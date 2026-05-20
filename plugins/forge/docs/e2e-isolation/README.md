# E2E isolation — DB-isolation recipe contract

This directory holds DB-isolation recipes for the `/e2e` skill. Each recipe gives e2e tests a clean, isolated database so tests never share state with a development or production instance. The active recipe per project is chosen by the project's `.claude/e2e.json` file via its `db_isolation` field.

---

## 1. The `.claude/e2e.json` schema

Location: `<project-root>/.claude/e2e.json`

```json
{
  "db_isolation": "ephemeral-postgres"
}
```

| Field | Type | Meaning |
|---|---|---|
| `db_isolation` | string | The isolation strategy: a recipe filename in this directory (without `.md`), or `"none"` to explicitly opt out. |

### 1.1 Three-state model

| File state | `db_isolation` value | Behaviour |
|---|---|---|
| Absent | — | Undecided. The first `/execute-epic` or `/execute-ticket` run asks the user to pick a strategy, then writes `.claude/e2e.json`. |
| Present | Valid strategy name (e.g. `"ephemeral-postgres"`) | Opted in. The named recipe is loaded and all four ops are executed each run. Never prompts again. |
| Present | `"none"` | Explicitly opted out. DB-isolation steps are silently skipped. Never asks again. |

Note: `"none"` is a reserved value of `db_isolation` (the explicit opt-out), so a strategy recipe file may not be named `none`.

---

## 2. The recipe contract

Every recipe file (`<strategy>.md`) MUST implement exactly four operations, each as a `## <op>` section. Skills invoke them in order: `provision` → `migrate` → `run` → `teardown`. A recipe MAY include additional non-op sections (e.g. `## Prerequisites`) — the four ops are the required contract, not a cap on the file's sections.

## provision

**Purpose:** Create an isolated, empty database ready to receive the project schema.

**Inputs:**
- The project's Postgres major version (e.g. `15`, `16`).

**Outputs:**
- `DATABASE_URL` — a full Postgres connection string for the application/ORM (may be a pooled URL).
- `DIRECT_URL` — a direct (non-pooled) connection string for migrations.
- `handle` — an opaque value (container ID, branch name, schema name, etc.) passed to `teardown`. The recipe defines what this contains; the skill treats it as opaque.

**What the recipe must specify:**
- Exact commands to create the database resource (container, branch, schema).
- How to derive and format `DATABASE_URL`, `DIRECT_URL`, and `handle` from the created resource.
- Any prerequisites (e.g. Docker must be running, a CLI tool must be installed).

---

## migrate

**Purpose:** Apply the project's committed schema to the provisioned (empty) database, bringing it to the current migration state.

**Inputs:**
- `project_root` — absolute path to the project root.
- `DATABASE_URL` — connection string from `provision`.
- `DIRECT_URL` — direct connection string from `provision`.

**Outputs:** None (side-effect: database schema is fully applied).

**What the recipe must specify:**
- The exact command to run migrations (e.g. `prisma migrate deploy`, `supabase db push`).
- How to inject `DATABASE_URL` and `DIRECT_URL` as environment variables for that command.
- Expected success signal (exit code 0, specific stdout pattern, etc.).
- Failure behaviour: if migration fails, skill must call `teardown` before surfacing the error.

---

## run

**Purpose:** Execute the project's e2e test suite against the provisioned, migrated database.

**Inputs:**
- `DATABASE_URL` — connection string from `provision`.
- `DIRECT_URL` — direct connection string from `provision`.
- `e2e_command` — the project's e2e command string, supplied by the calling `/e2e` skill, which reads it from the project's `CLAUDE.md` "Essential commands" table (the same source the `test-runner` agent uses). It is NOT a field in `.claude/e2e.json` — the `e2e.json` schema has only `db_isolation`.

**Outputs:** Test results (pass/fail, counts, output text) forwarded to the calling skill.

**What the recipe must specify:**
- How to inject `DATABASE_URL` and `DIRECT_URL` into the test runner environment.
- How the recipe delegates execution to the `test-runner` agent (the shared sub-agent the `/e2e` skill uses to run a test command and report structured pass/fail results).
- How test output is captured and returned to the skill.
- Failure behaviour: if tests fail, skill MUST still call `teardown` before reporting results.

---

## teardown

**Purpose:** Destroy the isolated database created by `provision`, releasing all associated resources.

**Inputs:**
- `handle` — the opaque value returned by `provision`.

**Outputs:** None.

**What the recipe must specify:**
- Exact commands to destroy the resource identified by `handle`.
- Idempotency guarantee: `teardown` MUST be safe to call after a failed `provision`, `migrate`, or `run` — it must not error if the resource is already gone or was never fully created.

---

## 3. Strategy status

| Strategy | Status | Notes |
|---|---|---|
| `ephemeral-postgres` | implemented | Throwaway Docker Postgres container per run |
| `supabase-branch` | future | Needs Supabase Pro (branching is a paid feature) |
| `dedicated-schema` | future | Separate Postgres schema in an existing project |
