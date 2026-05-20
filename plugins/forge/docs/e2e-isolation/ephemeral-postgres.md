Throwaway Docker Postgres container per run — spun up, migrated, tested, and removed in a single skill invocation.

## Prerequisites

Requires a running Docker-compatible runtime. On macOS without Docker Desktop, use Colima: `brew install colima docker` then `colima start`.

## provision

**Purpose:** Start a fresh Postgres container, wait for it to be ready, and emit the connection URLs and handle.

**Steps:**

1. **Preflight** — confirm Docker is available:
   ```bash
   docker info > /dev/null 2>&1
   ```
   On failure, **halt** the skill with this message:
   > Docker runtime not available. Install + start it: `brew install colima docker && colima start`. Then re-run.

2. **Pick a free host port:**
   ```bash
   PORT=$(node -e 'const s=require("net").createServer();s.listen(0,()=>{console.log(s.address().port);s.close()})')
   ```

3. **Generate a run ID:**
   ```bash
   RUNID=$(date +%s)-$RANDOM
   ```

4. **Start the container** (the Postgres major version is an input from the calling skill; the example below uses 17):
   ```bash
   docker run -d --rm --name "e2e-pg-$RUNID" \
     -e POSTGRES_PASSWORD=e2e -e POSTGRES_DB=e2e \
     -p "$PORT:5432" postgres:17
   ```

5. **Wait for readiness** — poll up to 30 × at 1 s intervals:
   ```bash
   READY=0
   for i in $(seq 1 30); do
     if docker exec "e2e-pg-$RUNID" pg_isready -U postgres -d e2e > /dev/null 2>&1; then
       READY=1
       break
     fi
     sleep 1
   done
   if [ "$READY" -ne 1 ]; then
     docker rm -f "e2e-pg-$RUNID" > /dev/null 2>&1 || true
     # halt: report "Postgres container did not become ready within 30s"
   fi
   ```
   On timeout the recipe halts (the e2e run does not proceed) and the container is removed first so nothing leaks.

6. **Outputs:**
   - `DATABASE_URL` = `postgresql://postgres:e2e@localhost:$PORT/e2e`
   - `DIRECT_URL`   = `postgresql://postgres:e2e@localhost:$PORT/e2e`
   - `handle`       = `e2e-pg-$RUNID` (the container name — carried to `teardown` as the shell variable `HANDLE`)

---

## migrate

**Purpose:** Apply the project's committed Prisma migrations to the empty container DB.

Run from the project root:
```bash
DATABASE_URL="$DATABASE_URL" DIRECT_URL="$DIRECT_URL" pnpm prisma migrate deploy
```

**Expected success signal:** exit code 0; Prisma prints `All migrations have been successfully applied.` (or `No pending migrations to apply.` if the migration set is empty — not expected in normal use).

**Failure behaviour:** if this command exits non-zero, the skill MUST call `teardown` before surfacing the error.

**Note on production rules:** this does NOT conflict with a project `CLAUDE.md` rule that says "`migrate deploy` runs only on Fly.io" — that rule governs the shared production DB; here the target is a disposable local container.

---

## run

**Purpose:** Execute the project's e2e test suite against the provisioned, migrated container.

Dispatch the `test-runner` agent with:
- The e2e command read from the project's `CLAUDE.md` "Essential commands" table (the calling skill supplies this — it is **not** a field in `.claude/e2e.json`).
- `DATABASE_URL` and `DIRECT_URL` set to the provisioned container URL, plus the minimal non-DB env the application's module evaluation genuinely requires.

**Environment assembly — finalised approach:**

Many NestJS apps load their env file (`.env.local` / `.env`) only via an import side-effect in `main.ts` (e.g. a `load-env.ts` module). An e2e spec imports `AppModule` directly, **not** `main.ts`, so that loader never runs — the jest process sees only the env the invoking shell exports. Therefore, **pass env inline on the e2e command invocation**; do not rely on the project's env file being auto-loaded.

Do **not** source the project's real `.env.local` — it points `DATABASE_URL` at the shared dev/prod database, which would defeat isolation. Instead, supply explicit test values inline and let the provisioned DB URLs win.

Determine the minimal env by inspecting what the app reads **at module-evaluation time** (constructors of eagerly-instantiated providers, `*.forRoot()` calls). A provider whose constructor throws on a missing/empty value will fail `AppModule` compilation before any test runs. Typically required:

| Var | Why it is needed at module-eval |
|---|---|
| `DATABASE_URL`, `DIRECT_URL` | Prisma datasource — point both at the provisioned container. |
| `JWT_SECRET`, `JWT_REFRESH_SECRET` | Auth token service reads secrets in its constructor and throws if absent. Use any non-empty test value. |
| `RESEND_API_KEY` (or equivalent 3rd-party SDK key) | An email/SDK provider constructed eagerly may throw on an empty key — supply a non-empty placeholder (e.g. `re_e2e_placeholder`), not `""`. |
| `REDIS_URL` | BullMQ / queue connections. A stub value is fine — the recipe does not provision Redis and the e2e endpoints under test do not exercise it. |
| `NODE_ENV=test` | Standard test-mode flag. |

This list is project-specific — derive it from the actual `AppModule` import graph each time; the table above is the pattern, not a fixed contract.

```bash
# Inline env on the e2e command. $DATABASE_URL / $DIRECT_URL are the provisioned
# container connection strings from `provision` (same vars `migrate` uses).
# --runInBand --forceExit are required here — see the caveat below.
NODE_ENV=test \
DATABASE_URL="$DATABASE_URL" DIRECT_URL="$DIRECT_URL" \
JWT_SECRET=e2e-test-access-secret JWT_REFRESH_SECRET=e2e-test-refresh-secret \
RESEND_API_KEY=re_e2e_placeholder \
REDIS_URL=redis://127.0.0.1:6379 \
<e2e_command> --runInBand --forceExit
```

**Open-handle / clean-exit caveat:** when `REDIS_URL` is a stub (no Redis provisioned), queue clients such as BullMQ + `ioredis` retry the connection in the background and keep socket handles open. Jest then hangs after the suite finishes instead of exiting. Run the e2e command with jest's `--forceExit` (and `--runInBand` for a deterministic single-DB run) so the process terminates once tests complete. The connection errors are logged but are harmless — the endpoints under test do not touch Redis.

**Failure behaviour:** if tests fail, the skill MUST still call `teardown` before reporting results. Test output (pass/fail, counts, stdout/stderr) is forwarded in full to the calling skill.

---

## teardown

**Purpose:** Destroy the container, releasing all resources.

```bash
docker rm -f "$HANDLE" > /dev/null 2>&1 || true
```

Where `$HANDLE` is the `handle` value from `provision`.

**Idempotency:** the `|| true` guard makes this safe to call after a failed `provision`, `migrate`, or `run` — it does not error if the container is already gone or was never fully created.

**Required:** teardown MUST run even when `run` fails.
