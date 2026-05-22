---
name: e2e-web
description: Web end-to-end testing child of forge:e2e — runs Playwright specs, gates epic-close on a green suite, and scaffolds the opt-in module on project init. Dispatched by forge:e2e for the web flavor. Use for any `*.e2e-web.spec.ts` work.
type: hybrid
---

# forge:e2e-web

The web platform child of `forge:e2e`. Runs Playwright specs (`**/*.e2e-web.spec.ts`) against the project, and is dispatched by the parent for the web flavor. The parent `forge:e2e` owns the universal lifecycle + opt-in model; this skill owns the Playwright specifics.

Sibling child `forge:e2e-backend` covers DB-isolated backend e2e. Playwright is an **external** dependency — this skill references its usage and surfaces the manual-setup template; it never vendors Playwright into the plugin.

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

Three-state model — the universal one defined by `forge:e2e` (sibling `forge:e2e-backend` uses `.claude/e2e.json`):

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

Invoked manually (`/forge:e2e-web --init`) or by `forge:e2e --init` / `forge:project-init` when a web platform is present.

Procedure:

1. **Ask the opt-in question first:** "This is a web platform. Do you want Playwright e2e tests here? (yes / no)". Playwright is an external dependency — installing it is the user's choice.
   - **No** → write `<project>/.claude/e2e-web.json` with `opted_in: false` and stop. The opt-out is recorded so e2e is never proposed for this platform again.
   - **Yes** → continue.
2. Write `<project>/.claude/e2e-web.json` with `opted_in: true` and the default `config` block above (browsers default to `["chromium"]`; can be widened later).
3. Scaffold `<project>/tests/e2e/` with a `.gitkeep` so the directory survives commits.
4. Write `<project>/playwright.config.ts` from the project-init opt-in module (#82 owns the template content — this skill only triggers the copy when invoked standalone; project-init handles its own copy directly).
5. If Playwright is not yet installed, surface the manual-setup template (do not run npm commands silently).
6. Emit a one-line summary: `e2e-web initialised; run /forge:e2e --check to verify.`

## Trigger

- **Auto:** dispatched by the `forge:e2e` parent for the `web` flavor (`--check` / `--run` / `--init`). Setup-time `--init` from `forge:project-init` is intended but not yet wired (tracked in #105).
- **Manual:** `/forge:e2e-web --check | --run [path] | --init` for direct web-only use.

## Do not

- Do not run unit tests from this skill — that's the `test-runner` agent's default path.
- Do not auto-install Playwright or its browsers — surface the manual-setup template (#81) and stop.
- Do not delete or disable failing specs to make the gate pass.
- Do not edit `playwright.config.ts` after init — the user owns it.
- Do not bypass the `--check` gate when invoked from `--run` inside epic-close; if check fails, halt.

## What this skill does not cover

- **Authoring the specs themselves** — see `forge:tdd` for the discipline; the web TDD loop (#84) drives spec writing.
- **DB isolation for e2e** — out of scope here; sibling `forge:e2e-backend` owns that contract (`plugins/forge/docs/e2e-isolation/`).
- **Universal rules + routing** — owned by the parent `forge:e2e`.
- **Mobile e2e** — separate research track (#86–#89).
- **CI integration** — orthogonal; each project wires Playwright into its own CI.
