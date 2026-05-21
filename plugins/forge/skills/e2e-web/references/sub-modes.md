# `forge:e2e-web` sub-mode contracts

The three sub-modes — `--check`, `--run`, `--init` — share the same flag interface but have different inputs, outputs, and callers. This reference fills in the detail that the SKILL.md summary intentionally leaves out.

---

## `--check` (setup-check)

### Callers

- `forge:execute-epic` Step 3.5 — once per epic, in the main session, BEFORE the dispatch loop. Subagents MUST NOT re-run.
- `forge:epic-close` web gate (#85) — before the full-suite `--run` is invoked, to short-circuit if the project never opted in.

### Inputs

- `cwd` — project root (defaults to current working directory).

### Outputs

Exactly one of:

- `configured` — marker present (`opted_in: true`), `@playwright/test` resolves from `node_modules`, `npx playwright --version` exits 0. Caller continues silently.
- `not-applicable` — not a web project, OR marker present with `opted_in: false`. Caller continues silently. Never asks again.
- `needs-setup` — web project AND (marker absent OR Playwright not installed). Caller surfaces the manual-setup template (`plugins/forge/skill-templates/_common/manual-setup-templates/playwright.md`) and halts the current operation. After the user completes manual setup, they re-trigger the caller (e.g. re-run `/forge:execute-epic <ID>`).

### Detection rules

- **Web project** — `package.json` exists at `cwd` AND its `dependencies` or `devDependencies` includes one of `next`, `react`, `vite`, `astro`. If you see only a backend stack (Express, NestJS, plain Node), return `not-applicable`.
- **Playwright installed** — `node_modules/@playwright/test/package.json` exists AND `npx playwright --version` exits 0. If `@playwright/test` is in `package.json` but `node_modules/` is missing it (fresh clone), treat as `needs-setup`.

### Output format

One line, machine-parsable:

```
e2e-web check: <configured|not-applicable|needs-setup>
```

On `needs-setup`, append a second line with the template path:

```
e2e-web check: needs-setup
template: plugins/forge/skill-templates/_common/manual-setup-templates/playwright.md
```

---

## `--run` (run)

### Callers

- `forge:execute-ticket` web TDD loop (#84) — invoked on each red-green-refactor turn. Typically passes `path_filter` to scope to the spec under test.
- `forge:epic-close` web gate (#85) — invoked once with no `path_filter` for the full-suite green gate.

### Inputs

- `cwd` — project root.
- `path_filter` (optional) — single spec path or directory to scope the run (e.g. `tests/e2e/checkout.e2e-web.spec.ts`, `tests/e2e/auth/`).
- `mode` — `report` (default) | `fix`.
- `max_fix_iterations` (optional, mode=fix) — default 3.

### Procedure

1. Read `<cwd>/.claude/e2e-web.json` to resolve `playwright_config` and `test_dir` (fall back to defaults if either is missing).
2. Build the test command:
   - Base: `npx playwright test`
   - Add `--config <playwright_config>` if non-default.
   - Add `<path_filter>` if provided.
   - Add `--reporter=json` so the `test-runner` agent can parse machine output.
3. Dispatch the existing `test-runner` agent (model: **sonnet**) with:
   - `cwd`, `mode`, `max_fix_iterations` (if `mode=fix`)
   - `type=e2e-web` — discriminator the agent uses to switch its Playwright parser path on
   - The resolved command as `extra_args` (or as `command_override` if the agent supports it; otherwise the agent uses the `type` to pick the right base command and append `path_filter` itself).
4. Forward the agent's structured report to the caller verbatim.

### `test-runner` agent contract (web variant)

The `test-runner` agent reads `type=e2e-web` and parses Playwright's JSON reporter format:

- `passed_count`, `failed_count`, `skipped_count`, `duration_ms` from the top-level summary.
- `failures[]` from any `tests[].results[].status == 'failed'` entry — each with spec file, test title, error message (truncated ~500 chars), and the top app-code stack frames.

`mode=fix` semantics are unchanged from the default unit-test path: the agent edits the spec OR the source minimally, re-runs the single failing spec via `path_filter`, and loops up to `max_fix_iterations`. The same prohibitions apply (no commits, no `.skip` to silence, no disabling of failing tests).

---

## `--init` (init)

### Callers

- Manual: user types `/forge:e2e-web --init` inside a web project.
- Programmatic: `forge:project-init` when the user opts into the web-nextjs Playwright module (#82) — though project-init may copy the template files directly and only call this skill to write the marker.

### Inputs

- `cwd` — project root.
- `browsers` (optional) — list, default `["chromium"]`. Widen later by editing `e2e-web.json`.
- `base_url` (optional) — default `http://localhost:3000`.

### Procedure

1. **Write the marker** — `<cwd>/.claude/e2e-web.json`:
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
2. **Scaffold the test directory** — `mkdir -p <cwd>/tests/e2e/` and write a `.gitkeep` so the directory survives commits before the first spec is authored.
3. **Write `playwright.config.ts`** — the project-init opt-in module (#82) owns the template content; this skill copies it from there when invoked standalone. If invoked from project-init itself, project-init handles the copy directly and only delegates the marker write to this skill.
4. **Check installation** — run `--check`. If it returns `needs-setup` (Playwright not installed), surface the manual-setup template and stop. Do NOT auto-install `@playwright/test` or its browsers — that's manual-setup territory.
5. **Emit summary**:
   ```
   e2e-web initialised at <cwd>.
   Run /forge:e2e-web --check to verify, then author specs in tests/e2e/<name>.e2e-web.spec.ts.
   ```

### Idempotency

- If `.claude/e2e-web.json` already exists with `opted_in: true`, report `already initialised` and skip steps 1–3 (still run step 4 to re-verify install state).
- If it exists with `opted_in: false`, ask the user before overwriting — they explicitly opted out.
- `tests/e2e/` is created with `mkdir -p`; existing contents are never touched.
