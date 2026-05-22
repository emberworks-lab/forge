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
| 3 | `forge:subagent-driven-development` | `execute-ticket` Step 6 (l65) + `implement-delegation.md` + `e2e-tdd-loop.md` | **RESOLVED** — built as a forge skill (adapted from superpowers, `inspired-by`). NOT repointed at `superpowers:` — that is forbidden by audit check 6 and breaks standalone install |
| 4 | `forge:verification-before-completion` | `execute-ticket` Step 10 (l93), `execute-epic` Step 6.5 (l72) | **RESOLVED** — built as a forge skill (adapted, `inspired-by`); consumers now invoke it, inline Iron Law duplication removed |
| 5 | `forge:improve-codebase-architecture` | `diagnose` references/phases.md (l62) | Build skill (gap A) or rewrite as a plain recommendation |
| 6 | `forge:log-decision` | `docs-workflow.md`, `_scaffold_flutter.py` (generated CLAUDE.md table) | Build skill (gap A) or repoint at the `decision-log/` convention |

**#3 and #4 — resolution note.** `execute-ticket` delegated its implementation phase (#3) and completion gate (#4) to `forge:*` skills that were never built — the EPIC A migration left the invocations but never created the skills (and the behavior had no `superpowers:` equivalent it was allowed to point at, since check 6 forbids that). Fix taken: **build both as proper forge skills** adapted from the superpowers originals (with `inspired-by` credit), then point the consumers at them and delete the inline duplication. This preserves the plugin's encapsulation + reusability rule rather than inlining. Done on branch `feature/forge-105-plugin-integrity`.

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

## Resolution log (Phase 3 — 2026-05-22)

**P0 — all resolved.** #1/#2 built as forge skills (not repointed at superpowers — forbidden by audit check 6); #3 e2e built then split into parent+children; #4 kit-update-docs built then split into update-docs parent+children.

**P1 — all migrated (user decision: migrate all three):**
- `forge:improve-codebase-architecture` — migrated (adapted from mattpocock, `inspired-by`). Resolves the diagnose handoff phantom.
- `forge:log-decision` — migrated (original; matches docs-workflow decisions-log format). Resolves the docs-workflow + scaffold phantom.
- `forge:manual-cases-list` — migrated as the on-demand counterpart to execute-epic Step 7; backend-aware via tracker recipe.

**P2 — user decision: migrate `to-prd`, retire the rest:**
- `forge:to-prd` — migrated (adapted from mattpocock); backend-agnostic publish (markdown → `docs/0X_*.md`); output feeds create-ticket Mode A.
- `triage` — **retired** (user: "не потрібен"). Was Linear-coupled inbox triage; not core to the execution pipeline.
- `review-fix` — **retired**: superseded by `forge:review` (JSON) + epic-close classifier + Step 6 action execution.
- `to-issues` — **retired**: covered by `forge:create-epic` / `forge:create-ticket`.
- `memory-audit` — **retired from the plugin**: personal-infra (`~/.claude-memory/`), not product-engineering; doesn't belong in a distributable plugin. Recreate as a personal `~/.claude/commands/` command if wanted.

All four retired commands had zero remaining references in the plugin (verified) — pure capability removal, no dangling links.

**Audit C — encapsulation: 1 violation found + fixed.**
- `forge:execute-ticket` Step 11 + `forge:execute-epic` `references/subagent-prompt.md` inlined the commit recipe (phrase + message + footer + staging) instead of invoking `forge:commit` — whose own description already claimed to be invoked by them. Fixed: Step 11 now invokes `forge:commit` (`kind=implements`) then pushes (commit doesn't push); the subagent prompt now points at Step 11 instead of restating the recipe.
- Everything else composes correctly. The only unresolved `forge:*` references are intentional `forge:e2e-mobile*` future-skill sketches (documented as not-yet-built).

**Net plugin state:** 43 skills, all pass `audit.sh`. No active phantom references remain.

---

## E2E architecture — parent/child split (user decision)

Initial P0 fix built `forge:e2e` as the backend skill (sibling of `forge:e2e-web`). User pushed back: that's the wrong shape for a system that will grow web + backend + mobile (and mobile further into flutter/rn/kmp/native + device target). Restructured to a composition hierarchy:

```
forge:e2e            fundamental — universal rules (opt-in model, RED→GREEN lifecycle,
                     validation discipline) + router (resolve flavor → dispatch child)
├── forge:e2e-web        Playwright (external; not vendored; init asks opt-in)
├── forge:e2e-backend    DB-isolated suite (renamed from the first forge:e2e)
└── forge:e2e-mobile     future router → flutter/rn/kmp/native + iOS-sim/Android-emu
```

**Why:** matches the plugin's composition principle — each level owns one responsibility and the parent composes by dispatch, not by inlining. Consumers (execute-ticket / execute-epic / epic-close) now call the single entry point `forge:e2e`; routing lives in one place instead of being duplicated as per-platform bullets across three skills.

**Mobile:** documented in the parent as a future branch; the `forge:e2e-mobile` child + its framework sub-children are built when mobile e2e leaves research (#86-89).

**Known follow-up (tracked in #105):** `forge:project-init` does not yet invoke `forge:e2e --init` at setup time — the wiring was never added (epic H #82 only shipped the template). Surfaced honestly in the e2e skills' trigger sections rather than claimed.

---

## Note on tonight's epic closures

The P0 #3/#4 namespace bugs mean `forge:execute-ticket` and `forge:execute-epic` were *already* referencing phantoms before tonight. Tonight's epics were executed via generic subagent prompts (not the real skills), so the phantom invocations were never actually hit — which is why the work completed. But anyone running `/forge:execute-ticket` for real today would hit them. This raises the priority of Phase 3 P0 fixes above the deferred content work.
