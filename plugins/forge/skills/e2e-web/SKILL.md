---
name: e2e-web
description: Run Playwright end-to-end tests for web projects, gate epic-close on a green suite, and scaffold the opt-in module on project init. Use for any `*.e2e-web.spec.ts` work.
type: hybrid
---

# forge:e2e-web

Web-side end-to-end testing for forge projects. Runs Playwright specs (`**/*.e2e-web.spec.ts`) against the project, gates `forge:epic-close`, and is the auto-installer when `forge:project-init` selects the web-nextjs Playwright module.

Its sibling `forge:e2e` (backend) mirrors this shape so the two stay symmetric.

## Convention

| Thing | Value |
|---|---|
| Test file glob | `**/*.e2e-web.spec.ts` |
| Default test dir | `<project>/tests/e2e/` |
| Opt-in marker | `<project>/.claude/e2e-web.json` |
| Runner | Playwright via existing `test-runner` agent (`sonnet`), invoked with `type=e2e-web` |
| Setup template | `plugins/forge/skill-templates/_common/manual-setup-templates/playwright.md` (provided by ticket #81) |

### `.claude/e2e-web.json` shape

```json
{
  "opted_in": true,
  "config": {
    "test_dir": "tests/e2e",
    "base_url": "http://localhost:3000",
    "browsers": ["chromium"],
    "playwright_config": "playwright.config.ts"
  }
}
```

Three-state model — same pattern as `forge:e2e` backend / `.claude/e2e.json`:

| Marker | `opted_in` | Behaviour |
|---|---|---|
| Absent | — | Undecided. `setup-check` returns `needs-setup` on web projects; `not-applicable` on non-web. |
| Present | `true` | Opted in. `run` proceeds; `setup-check` returns `configured`. |
| Present | `false` | Explicitly opted out. `setup-check` returns `not-applicable`. Never asks again. |

## Sub-modes

Three sub-modes, each with a distinct caller. Full inputs / outputs / exit shapes in `references/sub-modes.md`.

### `--check` (setup-check)

Invoked once per epic by `forge:execute-epic` Step 3.5 and `forge:epic-close` web gate (#85). Detect mode, return one of:

- `configured` — marker present + Playwright resolves + browsers installed. Caller continues silently.
- `not-applicable` — not a web project, OR marker says `opted_in: false`. Caller continues silently.
- `needs-setup` — web project + marker missing OR Playwright not installed. Caller surfaces the manual-setup template (path above) and halts.

Detection: web project = `package.json` exists AND has `next` / `react` / `vite` / `astro` in dependencies. Playwright installed = `@playwright/test` resolves from `node_modules` AND `npx playwright --version` exits 0.

### `--run` (run)

Invoked by `forge:execute-ticket` web TDD loop (#84) on each red-green-refactor turn, and by `forge:epic-close` web gate (#85) for the full-suite green gate.

Inputs: `cwd` (project root); optional `path_filter` (a single spec path or directory to scope the run); `mode` = `report` (default) | `fix`.

Procedure:

1. Resolve the test command: `npx playwright test [--config <playwright_config>] [<path_filter>] [--reporter=json]`.
2. Dispatch the existing `test-runner` agent (model: **sonnet**) with `type=e2e-web`, the resolved command, `cwd`, `mode`, and (if `mode=fix`) `max_fix_iterations=3`. The agent parses Playwright JSON output and reports pass/fail with structured failures — same contract as its default unit-test path.
3. Forward the agent's structured report to the caller. Never commit, never disable failing specs.

Failure surfacing is the caller's job: the TDD loop reads it on every turn; the epic-close gate halts the close on red.

### `--init` (init)

Invoked manually (`/forge:e2e-web --init`) or by `forge:project-init` when the user opts into the web-nextjs Playwright module (#82).

Procedure:

1. Write `<project>/.claude/e2e-web.json` with `opted_in: true` and the default `config` block above (browsers default to `["chromium"]`; can be widened later).
2. Scaffold `<project>/tests/e2e/` with a `.gitkeep` so the directory survives commits.
3. Write `<project>/playwright.config.ts` from the project-init opt-in module (#82 owns the template content — this skill only triggers the copy when invoked standalone; project-init handles its own copy directly).
4. If Playwright is not yet installed, surface the manual-setup template (do not run npm commands silently).
5. Emit a one-line summary: `e2e-web initialised; run /forge:e2e-web --check to verify.`

## Trigger

- **Auto:** `forge:execute-epic` Step 3.5 (`--check`), `forge:execute-ticket` web TDD loop #84 (`--run`), `forge:epic-close` web gate #85 (`--check` then `--run`), `forge:project-init` web opt-in module #82 (`--init`).
- **Manual:** `/forge:e2e-web --check | --run [path] | --init`.

## Do not

- Do not run unit tests from this skill — that's the `test-runner` agent's default path.
- Do not auto-install Playwright or its browsers — surface the manual-setup template (#81) and stop.
- Do not delete or disable failing specs to make the gate pass.
- Do not edit `playwright.config.ts` after init — the user owns it.
- Do not bypass the `--check` gate when invoked from `--run` inside epic-close; if check fails, halt.

## What this skill does not cover

- **Authoring the specs themselves** — see `forge:tdd` for the discipline; the web TDD loop (#84) drives spec writing.
- **DB isolation for e2e** — out of scope here; backend `forge:e2e` owns that contract (`plugins/forge/docs/e2e-isolation/`).
- **Mobile e2e** — separate research track (#86–#89).
- **CI integration** — orthogonal; each project wires Playwright into its own CI.
