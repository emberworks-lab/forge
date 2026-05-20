# Decision Log

Autonomous-execution decisions made by Claude on behalf of @achontoroh
during overnight epic closure runs (Goal: close remaining epics F → B → C+D → G → H).

## When entries are written

Every time `forge:execute-epic` or `forge:epic-close` hits a contentious choice
(two or more reasonable options, no clear winner from project conventions),
an entry is appended to the per-epic file in this directory.

Routine choices already covered by `CLAUDE.md`, skill SKILL.md, or git
conventions are NOT logged — only genuine forks.

## Entry format

Each entry:

```markdown
## [TICKET] Short problem statement
**Epic:** EPIC X (#NN)
**Ticket:** #NN — title
**Context:** one sentence on what was being done
**Problem:** what was unclear or had multiple viable answers
**Options considered:**
- **A:** … — tradeoff
- **B:** … — tradeoff
- **C:** … — tradeoff
**Chosen:** B
**Why:** the deciding factor
**May need revisit if:** what would falsify this choice
```

## File layout

- `<YYYY-MM-DD>-epic-<letter>.md` — one file per epic
- This `README.md` — format spec only, no entries

## Baseline decisions (this run)

Recorded before any epic started:

| Decision | Choice | Why |
|---|---|---|
| Decision log location | `decision-log/` in repo root | Co-located with code, version-controlled, visible in PRs |
| Version bump scheme | Minor bump per epic close (0.2.0 → 0.3.0 → … → 0.7.0); **0.7.0 → 1.0.0 only on final README task** | Per-epic minor matches prior pattern (commit 02c42a7); user reserves major for completion-of-plugin milestone |
| Commit strategy | Per-ticket commit + push inside epic branch | `execute-epic` default; magic-word commits (`Refs #NN`) auto-link in GH |
| PR strategy | After `epic-close`: `forge:pr-create` → **auto-merge to `main`** (user authorized full trust, will revert if needed) | User explicit decision: don't wait on PR review overnight |
| Ultrareview | Skipped on every epic | Explicit user instruction in Goal |
| Blocker handling | No tests in this codebase (it's skill markdown, not code) — just record blockers in log + as ticket comments, continue to next epic | User explicit: "тестів скоріше за все не буде, пофіг" |
| Subagent depth | `execute-epic` default (per-ticket subagents); deeper only when a single ticket fans out naturally | Avoid context bloat; the skill already balances this |

## Final task (after all epics close)

Once F, B, C+D, G, H are merged, do one final commit on a fresh branch:

1. Write `README.md` (full plugin documentation: how to install, how each skill is used, useful tips, recipes — replace current short README at repo root)
2. Bump `plugins[0].version` in `.claude-plugin/marketplace.json`: `0.7.0 → 1.0.0`
3. Commit, push, PR, merge

This 1.0.0 milestone marks the plugin as complete and user-ready.
