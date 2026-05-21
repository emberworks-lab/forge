---
name: e2e
description: Run backend end-to-end tests against an isolated database (provision → migrate → run → teardown), gate epic-close on a green suite, and check setup on epic start. Use for any `*.e2e-spec.ts` work with DB isolation.
type: hybrid
---

# forge:e2e

Backend end-to-end testing for forge projects. Runs the project's e2e suite against a throwaway, isolated database so tests never touch dev or prod state. Mirrors `forge:e2e-web`; the web variant owns Playwright, this one owns DB isolation.

## Convention

| Thing | Value |
|---|---|
| Test file glob | `**/*.e2e-spec.ts` (project-defined) |
| Opt-in marker | `<project>/.claude/e2e.json` |
| Isolation recipe | `plugins/forge/docs/e2e-isolation/<db_isolation>.md` |
| Runner | project e2e command via existing `test-runner` agent (`sonnet`) |
| e2e command source | project `CLAUDE.md` "Essential commands" table (not `e2e.json`) |

### `.claude/e2e.json` shape + three-state model

```json
{ "db_isolation": "ephemeral-postgres" }
```

| Marker | `db_isolation` | Behaviour |
|---|---|---|
| Absent | — | Undecided. `--check` returns `needs-setup`; first `--init` writes the file. |
| Present | strategy name (e.g. `ephemeral-postgres`) | Opted in. `--run` loads the recipe and executes all four ops. |
| Present | `"none"` | Explicitly opted out. `--check` returns `not-applicable`; DB-isolation steps skipped. |

Full recipe contract (provision / migrate / run / teardown): `plugins/forge/docs/e2e-isolation/README.md`.

## Sub-modes

### `--check` (setup-check)

Invoked once per epic by `forge:execute-epic` Step 3.5 and `forge:epic-close` Step 0b. Return:

- `configured` — `e2e.json` present with a valid strategy + the recipe's prerequisites resolve (e.g. Docker available). Caller continues silently.
- `not-applicable` — no backend, OR `db_isolation: "none"`. Caller continues silently.
- `needs-setup` — backend project + marker missing OR a prerequisite (e.g. Docker) absent. Caller surfaces the fix and halts.

### `--run` (run)

Invoked by `forge:execute-ticket` (backend e2e TDD loop GREEN phase + regression run) and by `forge:epic-close` for the full-suite gate.

Inputs: `cwd`; optional `path_filter`; `mode` = `report` (default) | `fix`.

Procedure — load `plugins/forge/docs/e2e-isolation/<db_isolation>.md` and run its four ops in order:

1. **provision** — create the isolated DB; capture `DATABASE_URL`, `DIRECT_URL`, `handle`.
2. **migrate** — apply committed schema to the empty DB.
3. **run** — dispatch the existing `test-runner` agent (model: **sonnet**) with the project e2e command (from `CLAUDE.md`), the provisioned DB URLs injected inline, `mode`, and (if `mode=fix`) `max_fix_iterations=3`. The agent reports structured pass/fail.
4. **teardown** — destroy the DB by `handle`. **Always runs, even when migrate or run fails.**

Forward the agent's report to the caller. Never commit; never disable failing specs; never point at the real dev/prod DB.

### `--init` (init)

Invoked manually (`/forge:e2e --init`) or by `forge:project-init` when a backend project opts into DB-isolated e2e.

1. Prompt for a strategy (default `ephemeral-postgres`) and write `<project>/.claude/e2e.json`.
2. Surface the recipe's prerequisites (e.g. "Docker runtime required") — do not install anything silently.
3. Emit: `e2e initialised; run /forge:e2e --check to verify.`

## Trigger

- **Auto:** `forge:execute-epic` Step 3.5 (`--check`), `forge:execute-ticket` backend TDD loop (`--run`), `forge:epic-close` Step 0b gate (`--check` then `--run`), `forge:project-init` backend opt-in (`--init`).
- **Manual:** `/forge:e2e --check | --run [path] | --init`.

## Do not

- Do not run unit tests here — that is the `test-runner` agent's default path.
- Do not skip `teardown` — it MUST run even on failure (idempotent).
- Do not source the project's real `.env` — it points at the shared DB and defeats isolation.
- Do not delete or disable failing specs to make the gate pass.

## What this skill does not cover

- **Web e2e** — see `forge:e2e-web` (Playwright).
- **Authoring specs** — see `forge:tdd`; the backend TDD loop in `forge:execute-ticket` drives spec writing.
- **New isolation strategies** — add a recipe under `plugins/forge/docs/e2e-isolation/` per the README contract.
