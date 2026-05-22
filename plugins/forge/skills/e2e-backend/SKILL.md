---
name: e2e-backend
description: Backend end-to-end testing child of forge:e2e — runs the project's e2e suite against an isolated database (provision → migrate → run → teardown). Dispatched by forge:e2e for the backend flavor; owns the DB-isolation contract.
type: hybrid
---

# forge:e2e-backend

The backend platform child of `forge:e2e`. Runs the project's e2e suite against a throwaway, isolated database so tests never touch dev or prod state. The parent `forge:e2e` owns the universal lifecycle + opt-in model; this skill owns the backend specifics — DB isolation.

## Convention

| Thing | Value |
|---|---|
| Test file glob | `**/*.e2e-spec.ts` (project-defined) |
| Opt-in marker | `<project>/.claude/e2e.json` |
| Isolation recipe | `plugins/forge/docs/e2e-isolation/<db_isolation>.md` |
| Runner | project e2e command via existing `test-runner` agent (`sonnet`) |
| e2e command source | project `CLAUDE.md` "Essential commands" table (not `e2e.json`) |

### `.claude/e2e.json` shape

```json
{ "db_isolation": "ephemeral-postgres" }
```

The three-state opt-in model (absent / strategy-name / `"none"`) is the universal one defined by `forge:e2e`. Here the opted-in value is the isolation strategy. Full recipe contract (provision / migrate / run / teardown): `plugins/forge/docs/e2e-isolation/README.md`.

## Sub-modes

Same `--check` / `--run` / `--init` shape the parent dispatches into.

### `--check`

- `configured` — `e2e.json` present with a valid strategy + the recipe's prerequisites resolve (e.g. Docker available).
- `not-applicable` — no backend, OR `db_isolation: "none"`.
- `needs-setup` — backend project + marker missing OR a prerequisite (e.g. Docker) absent. Surface the fix and halt.

### `--run`

Inputs: `cwd`; optional `path_filter`; `mode` = `report` (default) | `fix`.

Load `plugins/forge/docs/e2e-isolation/<db_isolation>.md` and run its four ops in order:

1. **provision** — create the isolated DB; capture `DATABASE_URL`, `DIRECT_URL`, `handle`.
2. **migrate** — apply committed schema to the empty DB.
3. **run** — dispatch the existing `test-runner` agent (model: **sonnet**) with the project e2e command (from `CLAUDE.md`), the provisioned DB URLs injected inline, `mode`, and (if `mode=fix`) `max_fix_iterations=3`.
4. **teardown** — destroy the DB by `handle`. **Always runs, even when migrate or run fails.**

Forward the agent's report to the caller. Never commit; never disable failing specs; never point at the real dev/prod DB.

### `--init`

Invoked by `forge:e2e --init` (parent) when the user opts a backend platform into DB-isolated e2e.

1. Prompt for a strategy (default `ephemeral-postgres`) and write `<project>/.claude/e2e.json`.
2. Surface the recipe's prerequisites (e.g. "Docker runtime required") — do not install anything silently.
3. Emit: `e2e-backend initialised; run /forge:e2e --check to verify.`

## Trigger

- **Auto:** dispatched by `forge:e2e` (`--check` / `--run` / `--init`) when the resolved flavor is `backend`.
- **Manual:** `/forge:e2e-backend --check | --run [path] | --init` for direct backend-only use.

## Do not

- Do not run unit tests here — that is the `test-runner` agent's default path.
- Do not skip `teardown` — it MUST run even on failure (idempotent).
- Do not source the project's real `.env` — it points at the shared DB and defeats isolation.
- Do not delete or disable failing specs to make the gate pass.

## What this skill does not cover

- **Universal e2e rules + routing** — owned by the parent `forge:e2e`.
- **Web / mobile flavors** — sibling children `forge:e2e-web` / `forge:e2e-mobile`.
- **Authoring specs** — see `forge:tdd`; the parent's TDD loop drives spec writing.
- **New isolation strategies** — add a recipe under `plugins/forge/docs/e2e-isolation/` per the README contract.
