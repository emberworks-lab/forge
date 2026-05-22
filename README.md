# forge

**Claude Code plugin for AI-driven product engineering.** A curated set of slash commands, subagents, and skill-templates that cover the full development loop — tracker planning, epic orchestration, TDD execution, code review, multi-platform project bootstrap, design and e2e starters.

Built for solo developers and small teams who want deterministic, composable automation over free-form prompting.

---

## Install

```
/plugin install forge@emberworks-lab
```

Verify:

```
/forge:hello
```

Full setup walkthrough: [`docs/INSTALL.md`](docs/INSTALL.md).

---

## Quick start

Pick a scenario:

### Bootstrap a new project

```
/forge:project-init
```
Interview-driven scaffold. Picks tracker backend (Linear / GitHub personal / GitHub org / Markdown), single- vs multi-platform, per-platform framework, opt-in modules (Sentry, Playwright, etc.), and design system bootstrap. Writes `CLAUDE.md`, `.claude/tracker.json`, `docs/owner-overview.md`, and copies the appropriate skill-template(s).

### Plan and execute work as tracker epics

```
/forge:create-epic "Add OAuth login"          # brainstorm-gated; produces epic + sub-issues
/forge:execute-epic <EPIC-ID>                  # branch + dispatch subagents per ticket + commit per ticket
/forge:epic-close <EPIC-ID>                    # simplify → review → classifier → 3 actions → decision tree
```

### One-off fixes on a focused ticket

```
/forge:create-ticket "Fix flaky session timeout test"
/forge:execute-ticket <TICKET-ID>              # auto-injects e2e ack criteria if project opted in
```

### Diagnose a bug

```
/forge:diagnose         # 6-phase fast loop
/forge:diagnose-deep    # 4-phase rigorous loop (auto-invoked when needed)
```

### Iterate on a design

```
/forge:design-source              # 3-branch: co-create / external-generator prompt / 3 HTML variations
```

---

## Skill catalog

Full descriptions in each `plugins/forge/skills/<name>/SKILL.md`. The plugin ships **43 skills** organized below. Two families use a parent-router + per-flavor children shape: **e2e** (`forge:e2e` → web / backend / mobile) and **docs-sync** (`forge:update-docs` → meta / api / design).

### Tracker pipeline

| Skill | Use |
|---|---|
| [`create-epic`](plugins/forge/skills/create-epic/) | Draft an epic + sub-issues. Universal brainstorm gate; existing-ticket reference branch |
| [`create-ticket`](plugins/forge/skills/create-ticket/) | Create a single ticket from chat brief or doc. Auto-injects E2E ack-criteria when project is opted in (backend or web variant) |
| [`execute-epic`](plugins/forge/skills/execute-epic/) | Orchestrate epic execution. Manual-setup gate, branch, dependency-ordered subagent dispatch, per-ticket commits |
| [`execute-ticket`](plugins/forge/skills/execute-ticket/) | Execute a single ticket. Invokes `forge:tdd` for e2e RED→GREEN loop when ack criteria carry the E2E block (backend or web) |
| [`epic-close`](plugins/forge/skills/epic-close/) | Close a tracker epic. Steps 0-7: preflight → simplify → review → classifier → 3 actions (defer / inline+defer / inline+spawn-execute) → decision tree (merge / draft PR / cleanup) |
| [`commit`](plugins/forge/skills/commit/) | Magic-word commit linked to tracker; dispatches per `tracker.json.backend`. Invoked by execute-ticket/epic at commit time |
| [`pr-create`](plugins/forge/skills/pr-create/) | Open a draft PR linked to the epic with sub-issue summary |
| [`manual-cases-list`](plugins/forge/skills/manual-cases-list/) | On-demand aggregation of sub-issue `## Manual test cases` into one epic checklist (standalone counterpart to execute-epic Step 7) |

### Planning + ideation

| Skill | Use |
|---|---|
| [`brainstorm`](plugins/forge/skills/brainstorm/) | Stress-test a feature / design via guided dialectic before implementation |
| [`grill-me`](plugins/forge/skills/grill-me/) | Interview the user relentlessly about a plan until shared understanding |
| [`grill-with-docs`](plugins/forge/skills/grill-with-docs/) | Grilling that challenges plan against the project domain model + updates CONTEXT.md / ADRs inline |
| [`prototype`](plugins/forge/skills/prototype/) | Throwaway prototype to answer a design question — terminal logic app or UI variations |
| [`zoom-out`](plugins/forge/skills/zoom-out/) | Step back from the immediate task and re-derive priorities |
| [`to-prd`](plugins/forge/skills/to-prd/) | Synthesize the conversation + codebase into a PRD (no interview); backend-aware publish, output feeds create-ticket Mode A |

### Implementation

| Skill | Use |
|---|---|
| [`tdd`](plugins/forge/skills/tdd/) | Rigid red-green-refactor. Invoked by `execute-ticket` and `diagnose-deep` when production code is about to be written |
| [`subagent-driven-development`](plugins/forge/skills/subagent-driven-development/) | Execute a plan one fresh subagent per task, with two-stage review (spec then quality). Invoked by execute-ticket for the implementation phase |
| [`verification-before-completion`](plugins/forge/skills/verification-before-completion/) | The Iron Law gate — no completion claim without fresh verification evidence. Invoked before any DONE / commit / merge |
| [`project-init`](plugins/forge/skills/project-init/) | Interview-driven project bootstrap (see Quick start) |

### Diagnosis + debugging

| Skill | Use |
|---|---|
| [`diagnose`](plugins/forge/skills/diagnose/) | 6-phase fast diagnosis loop for bugs and perf regressions |
| [`diagnose-deep`](plugins/forge/skills/diagnose-deep/) | 4-phase rigorous workflow invoked by `diagnose` when defect resists quick fix |

### Review + simplification

| Skill | Use |
|---|---|
| [`review`](plugins/forge/skills/review/) | Local pre-PR review. Dispatches 3 parallel agents: architecture (opus), security (opus), testing (sonnet). Returns JSON, no edits |
| [`simplify`](plugins/forge/skills/simplify/) | Review the most recent code change for reuse / quality / efficiency, then fix |
| [`simplify-branch`](plugins/forge/skills/simplify-branch/) | Same as above but across all commits in current branch vs base |
| [`handle-review-feedback`](plugins/forge/skills/handle-review-feedback/) | Process PR / Linear feedback by classifying each item before implementing |
| [`improve-codebase-architecture`](plugins/forge/skills/improve-codebase-architecture/) | Surface architectural deepening opportunities (deep vs shallow modules) informed by CONTEXT.md + ADRs. Higher-level than simplify |
| [`graph-refresh`](plugins/forge/skills/graph-refresh/) | Thin wrapper around `code-review-graph build --incremental`. Idempotent; safe to call any time |

### Design

| Skill | Use |
|---|---|
| [`design-bootstrap`](plugins/forge/skills/design-bootstrap/) | Invoked by `project-init` on frontend platforms. 3-branch: ready / stack-defaults / will-create |
| [`design-source`](plugins/forge/skills/design-source/) | Invoked by `create-epic` for frontend epics without a design source. 3-branch: co-create / external-generator-prompt / 3 HTML variations |

### End-to-end testing

| Skill | Use |
|---|---|
| [`e2e`](plugins/forge/skills/e2e/) | Parent router — universal e2e contract (opt-in model, RED→GREEN lifecycle, validation discipline) + resolves flavor from `platforms[]` and dispatches to the child |
| [`e2e-web`](plugins/forge/skills/e2e-web/) | Playwright child. Convention `**/*.e2e-web.spec.ts` + `.claude/e2e-web.json` opt-in; Playwright is external (not vendored) |
| [`e2e-backend`](plugins/forge/skills/e2e-backend/) | DB-isolated child. provision → migrate → run → teardown via `docs/e2e-isolation/` recipes; `.claude/e2e.json` opt-in |
| `e2e-mobile` *(planned)* | Future child router → Patrol / Detox / native + device target. Documented in `forge:e2e`; built when mobile e2e leaves research |

### Documentation sync

| Skill | Use |
|---|---|
| [`update-docs`](plugins/forge/skills/update-docs/) | Parent router — analyses the epic's scope (is a pass even needed?) and dispatches only the in-scope children. MD source / generated-HTML format law |
| [`update-docs-meta`](plugins/forge/skills/update-docs-meta/) | Project-wide root docs: owner-overview, roadmap, decisions-log, glossary |
| [`update-docs-api`](plugins/forge/skills/update-docs-api/) | Backend API reference — Swagger/OpenAPI pipeline (opt-in) or hand-written MD fallback |
| [`update-docs-design`](plugins/forge/skills/update-docs-design/) | Design-doc + ADR drift detection — flags probable staleness, never rewrites prose |
| [`log-decision`](plugins/forge/skills/log-decision/) | Guided flow to append a locked decision to `docs/00_meta/decisions-log.md`. The decision-locks counterpart to update-docs |

### Stack-specific helpers

| Skill | Use |
|---|---|
| [`dart-collect-coverage`](plugins/forge/skills/dart-collect-coverage/) | Dart/Flutter coverage via `coverage` package → LCOV |
| [`dart-fix-runtime-errors`](plugins/forge/skills/dart-fix-runtime-errors/) | `dart analyze` + `dart fix` → verify via `dart test` |
| [`flutter-fix-layout-issues`](plugins/forge/skills/flutter-fix-layout-issues/) | Diagnose-to-fix lookup for Flutter constraint violations |

### Meta

| Skill | Use |
|---|---|
| [`writing-skill`](plugins/forge/skills/writing-skill/) | Author / refactor a `forge:*` skill so it conforms to plugin policy. Ships `audit.sh` |
| [`handoff`](plugins/forge/skills/handoff/) | Compact the conversation into a handoff doc for another agent |
| [`caveman`](plugins/forge/skills/caveman/) | Switch to ultra-compressed output mode. Opt-in pattern documented in `writing-skill/references/caveman-opt-in-pattern.md` |
| [`hello`](plugins/forge/skills/hello/) | Smoke-test the install |

---

## Agents

| Agent | Model | Use |
|---|---|---|
| `linter-runner` | sonnet | Universal linter executor. Reads CLAUDE.md > Lint, runs, parses, reports |
| `test-runner` | sonnet | Universal test executor. Reads CLAUDE.md > Test, runs (optionally a subset), parses |

Both support `mode=report` (default) and `mode=fix` (auto-fixes + re-runs up to 3 times).

---

## Skill-templates

Drop-in project scaffolds copied by `forge:project-init`:

| Template | Stack | Source |
|---|---|---|
| `web-nextjs/` | Next.js 15 + TS + Tailwind + ESLint + pnpm | extracted from reddit-idea-forge |
| `backend-nest/` | NestJS 10 + Prisma + TS + Jest. Includes `docs/api/` skeleton, RFC 7807 `ErrorResponseDto`, `asyncapi.yaml` | extracted from PantryPal |
| `mobile-flutter/` | Flutter idiomatic project | original |
| `mobile-native/` | Native iOS / Android placeholder — framework choice pending mobile e2e research | placeholder |
| `web-react/` | React + TS placeholder | legacy |
| `backend-node/` | Node backend placeholder | legacy |
| `_common/` | Shared assets: `owner-overview.md` template, `manual-setup-templates/` (playwright + others) | — |

---

## Tracker backends

Skills that touch a tracker (`create-epic`, `create-ticket`, `execute-epic`, `epic-close`, `commit`, `pr-create`) read `<project>/.claude/tracker.json` and dispatch via `plugins/forge/docs/tracker-backends/<backend>.md`:

| Backend | Magic-word format | Auto-close on PR merge |
|---|---|---|
| `linear` | `Closes EMB-42:` / `Refs EMB-42:` | yes |
| `github` | `Closes #123:` / `Refs #123:` | yes |
| `markdown` | `Implements <slug>:` | n/a (no remote) |

Schema: [`docs/conventions/tracker-json.md`](plugins/forge/docs/conventions/tracker-json.md) — includes `structure` (sub-folder / monorepo) + `platforms[]` for multi-platform projects.

---

## Useful patterns + recipes

### Run the full pipeline on one feature

```
/forge:create-epic "Add OAuth login"
# brainstorm-gates, creates epic + sub-issues, returns IDs

/forge:execute-epic <EPIC-ID>
# branch, dispatch subagents (sonnet for mechanical, opus for creative), commit per ticket

# (verify manually if applicable)

/forge:epic-close <EPIC-ID>
# preflight gate → simplify → review → classifier → 3 actions → decision tree A/B/C
```

### Just one ticket, no epic

```
/forge:create-ticket "Fix flaky session test"
/forge:execute-ticket <TICKET-ID>
```

### Continue an interrupted epic

```
/forge:execute-epic <EPIC-ID> --start-from <NEXT-TICKET-ID>
```

### Open a draft PR for the current epic branch

```
/forge:pr-create <EPIC-ID>
```

### Multi-platform project

```
/forge:project-init
# pick "multi-platform" → pick platforms (web + backend, etc.)
# layout: "sub-folder" (default, stable) or "monorepo" (experimental — some skills may not handle it ideally)
# per-platform framework selection
# scaffolds: root CLAUDE.md + per-platform dirs each with their own CLAUDE.md + .claude/tracker.json with parent_path fallback
```

### Opt in to web e2e

```
# 1. Copy the manual-setup template into your project
cp plugins/forge/skill-templates/_common/manual-setup-templates/playwright.md docs/setup/
# 2. Follow it (install, config, first test)
# 3. Create <project>/.claude/e2e-web.json with {"opted_in": true}
# 4. From now on, forge:create-ticket auto-injects "E2E coverage required: web" on web tickets
# 5. forge:execute-ticket invokes forge:e2e-web --run; forge:epic-close gates on web e2e pass
```

### Author a new skill

```
# Read the rules
cat plugins/forge/skills/writing-skill/SKILL.md

# Draft your SKILL.md and run the audit
bash plugins/forge/skills/writing-skill/scripts/audit.sh plugins/forge/skills/your-skill/SKILL.md

# Exit 0 = ready. Exit 1 = violations printed to stderr; fix and re-run.
```

---

## Plugin policy

Authoritative source: [`plugins/forge/skills/writing-skill/`](plugins/forge/skills/writing-skill/). Headline rules:

1. **Composition principle** — single responsibility; master composes via explicit invocation, never inlining
2. **Type taxonomy** — `minimal` (≤80) / `hybrid` (≤120, default) / `fundamental` (≤300, cited by others)
3. **Credit attribution** — adapted skills carry `inspired-by` front-matter (`adapted | concept | structure`); no 1:1 copies
4. **Subagent model declaration** — spawning subagents MUST name `sonnet` (mechanical) or `opus` (creative/critical); `haiku` is not used. Enforced by `audit.sh` check 10
5. **Slim audit checklist** — 9 steps mechanized by `audit.sh` (front-matter shape, line caps, dangling refs, forbidden patterns)

---

## Code review architecture

Two-axis review:

- **`forge:review` (local, pre-PR)** — 3 parallel agents (architecture / security / testing), no edits, JSON output. Wired into `epic-close` after `simplify-branch` and `graph-refresh`
- **`code-review` plugin (cloud, post-PR)** — upstream Anthropic plugin, posts inline comments on the GitHub PR. Triggered by `/code-review <PR#>` after merge candidate is ready

`code-review-graph` MCP integration: `forge:graph-refresh` keeps the graph fresh; `forge:review` agents consult it via MCP tools when available.

---

## Decision log

Major decisions taken during epic execution land in [`decision-log/`](decision-log/) — one file per epic (e.g. `2026-05-21-epic-F.md`). Format: problem statement, options considered, choice + rationale, "may need revisit if" trigger. See [`decision-log/README.md`](decision-log/README.md) for the full spec.

The log is committed to the repo so PR reviewers can see *why*, not just *what*.

---

## Status

**v1.1.0** — Production-ready. Core tracker pipeline, multi-platform init, code review, design ecosystem, e2e (web + backend + mobile-research), docs-sync, and plugin authoring all functional. The v1.1.0 plugin-integrity pass (#105) built the previously-missing skills (`forge:e2e` family, `forge:update-docs` family, `verification-before-completion`, `subagent-driven-development`) and removed all phantom skill references.

Known follow-ups (open tickets):
- `forge:e2e-mobile` — parent documents the branch; framework children (Patrol / Detox / native) built when mobile e2e leaves research (#86-89)
- Runtime verification of the new docs-sync + e2e skills on a real repo (incl. the `project-init` → `forge:e2e --init` / `forge:design-bootstrap` wiring)
- F.1 caveman pilot — protocol scaffolded, awaiting human-driven measurement
- G.1 articles digest — awaiting user-provided article list
- C+D.10 + .15 multi-platform pilots — human sandbox + Embergard/PantryPal fill

See [open issues](https://github.com/emberworks-lab/forge/issues) for the live backlog.

---

## Credits

- [`forge:brainstorm`](plugins/forge/skills/brainstorm/), [`forge:tdd`](plugins/forge/skills/tdd/), [`forge:diagnose-deep`](plugins/forge/skills/diagnose-deep/) — adapted from obra/[superpowers](https://github.com/obra/superpowers)
- [`forge:caveman`](plugins/forge/skills/caveman/) — adapted from mattpocock/[skills](https://github.com/mattpocock/skills)

Adapted skills are rewritten in forge's voice; each carries `inspired-by` front-matter with the source.

---

## License

MIT — see [`LICENSE`](LICENSE).
