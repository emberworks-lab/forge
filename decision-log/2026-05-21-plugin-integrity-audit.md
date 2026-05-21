# Plugin integrity audit — Phase 2 (Audits A + B)

Run: 2026-05-21, after the overnight epic execution
Method: git history of `~/.claude` (deleted local commands) + grep of all `forge:<name>` references across `plugins/`

---

## Audit A — Migration gap (local `~/.claude/commands/` → forge plugin)

Source of truth: `git -C ~/.claude log --all --diff-filter=D --name-only -- 'commands/*'`.
All legacy commands were deleted in commit `68fbefb chore: finalize EPIC A migration cleanup (#7)`. The cleanup assumed everything was migrated; several were not.

### Successfully migrated (no action)
`caveman, commit, create-epic, create-ticket, dart-collect-coverage, dart-fix-runtime-errors, diagnose, epic-close, execute-epic, execute-ticket, flutter-fix-layout-issues, grill-me, grill-with-docs, handle-review-feedback, handoff, pr-create, project-init, prototype, review, simplify-branch, zoom-out`

### Intentionally superseded (no action)
`linear-commit, linear-create-epic, linear-create-ticket, linear-epic-close, linear-execute-epic, linear-execute-ticket, linear-pr-create` — folded into the tracker-backend recipe model (`docs/tracker-backends/<backend>.md`). Correct to drop.

### GAPS — deleted but never migrated

| Command | Still referenced in plugin? | Severity | Notes |
|---|---|---|---|
| `e2e` | YES — execute-ticket ×2, execute-epic ×1 | **HIGH** | Backend e2e (ephemeral DB). Active phantom — see Audit B #2 |
| `kit-update-docs` | YES — 19 refs (epic-close, project-init, docs) | **HIGH** | Active phantom — see Audit B #1 |
| `improve-codebase-architecture` | YES — diagnose/phases.md ×1 | MED | Soft handoff target |
| `log-decision` | YES — docs-workflow.md, _scaffold_flutter.py | MED | Appends to `00_meta/decisions-log.md`. (Ironic: I built `decision-log/` by hand tonight not knowing this existed) |
| `manual-cases-list` | YES — 1 ref | LOW | Aggregates manual test cases |
| `memory-audit` | NO | LOW | Silent capability loss |
| `review-fix` | NO | LOW | Possibly superseded by `simplify` / `simplify-branch` — needs judgment |
| `to-issues` | NO | LOW | Silent capability loss |
| `to-prd` | NO | LOW | Silent capability loss |
| `triage` | NO | LOW | Silent capability loss |

**Decision needed per LOW item:** migrate, or formally retire (delete remaining references). Don't leave half-referenced.

---

## Audit B — Phantom references (`forge:X` invoked, X doesn't exist as a forge skill)

Existing skills cross-referenced against every `forge:<name>` token in `plugins/`.

### ACTIVE phantoms (real skill invokes nonexistent skill in an execution path — these are BUGS)

| # | Phantom | Invoked by | Fix |
|---|---|---|---|
| 1 | `forge:kit-update-docs` | `epic-close` Step (docs sync, line 161), `project-init` (line 136) | Build the skill (migration gap A) |
| 2 | `forge:e2e` (backend) | `execute-ticket` Step 3.5 (l53) + Step 8.5 (l85), `execute-epic` Step 3.5 (l45) | Build the skill (migration gap A), mirror `forge:e2e-web` |
| 3 | `forge:subagent-driven-development` | `execute-ticket` Step 6 (l65) + `implement-delegation.md` + `e2e-tdd-loop.md` | **Namespace bug** — exists as `superpowers:subagent-driven-development`. Rewrite ref, OR build a forge wrapper |
| 4 | `forge:verification-before-completion` | `execute-ticket` Step 10 (l93), `execute-epic` Step 6.5 (l72) | **Namespace bug** — exists as `superpowers:verification-before-completion`. Rewrite ref |
| 5 | `forge:improve-codebase-architecture` | `diagnose` references/phases.md (l62) | Build skill (gap A) or rewrite as a plain recommendation |
| 6 | `forge:log-decision` | `docs-workflow.md`, `_scaffold_flutter.py` (generated CLAUDE.md table) | Build skill (gap A) or repoint at the `decision-log/` convention |

**Most alarming: #3 and #4.** `execute-ticket` — the workhorse skill — delegates its ENTIRE implementation phase (#3) and its completion gate (#4) to skills that don't exist under the `forge:` namespace. They exist under `superpowers:`. This looks like the EPIC A migration over-eagerly rewrote `superpowers:* → forge:*` even for skills that legitimately stay in superpowers. **This means every `forge:execute-ticket` run is currently invoking phantom skills at its two most important steps.** (It likely "worked" tonight only because I ran subagents with generic prompts, not the real execute-ticket skill.)

### FUTURE sketches (referenced in design/research/candidate docs — NOT bugs, intentional forward-refs)

These appear only in `docs/design-research/` artifacts (#74 candidate-skills, #87 matrix, #88/#89 pilot docs) as "what a future skill would be named." No action; they're proposals.

- e2e family: `e2e-mobile-flutter`, `e2e-mobile-rn`, `e2e-mobile-cross`, `e2e-mobile-native`, `e2e-mobile-router`, `e2e-smoke-maestro`, `e2e-smoke-web-playwright`, `unit-web`
- design family: `design-tokens-gen`, `design-source-v0`, `design-a11y-brief`, `design-tokens-import-figma`, `design-storybook-gen`, `design-prototype-variants`, `design-flutter-theme`, `design-critique`, `design-ac-extract`, `figma-implement`

---

## Consolidated cleanup backlog (feeds Phase 3)

**P0 — execution-path bugs (the pipeline is silently broken):**
1. Fix `forge:subagent-driven-development` → `superpowers:subagent-driven-development` (execute-ticket core)
2. Fix `forge:verification-before-completion` → `superpowers:verification-before-completion` (execute-ticket + execute-epic)
3. Build `forge:e2e` (backend) + reconcile execute-ticket Steps 3.5/6.5/8.5 into one flow
4. Build `forge:kit-update-docs` → unblocks B#50, C+D#60, C+D#65

**P1 — referenced gaps:**
5. `forge:improve-codebase-architecture` — build or downgrade to plain recommendation
6. `forge:log-decision` — build or repoint at `decision-log/` convention
7. `manual-cases-list` — migrate or retire

**P2 — silent capability loss (decide migrate vs retire):**
8. `memory-audit`, `review-fix`, `to-issues`, `to-prd`, `triage`

**Still pending — Audit C (encapsulation):** not yet run. Will surface inline-logic-that-should-be-a-skill-call cases beyond the e2e one.

---

## Note on tonight's epic closures

The P0 #3/#4 namespace bugs mean `forge:execute-ticket` and `forge:execute-epic` were *already* referencing phantoms before tonight. Tonight's epics were executed via generic subagent prompts (not the real skills), so the phantom invocations were never actually hit — which is why the work completed. But anyone running `/forge:execute-ticket` for real today would hit them. This raises the priority of Phase 3 P0 fixes above the deferred content work.
