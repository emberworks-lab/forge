# Methodology Stack — Linear flow + Superpowers

This doc explains how our two methodology layers compose.

## Layer 1 — Superpowers (universal methodology)

`superpowers` is an installed plugin (Anthropic's official marketplace, by Jesse Vincent / obra). 14 skills covering brainstorming → planning → execution → finishing.

Loaded skills (always available via Skill tool):
- `brainstorming` — pre-design exploration with HARD-GATE on implementation
- `writing-plans` — formal plan-document writer (TDD-structured tasks)
- `subagent-driven-development` — fresh subagent per task + 2-stage review
- `executing-plans` — fallback for platforms without subagents
- `using-git-worktrees` — isolated workspace setup
- `verification-before-completion` — Iron Law: evidence before claims
- `systematic-debugging` — 4-phase + architecture-question-after-3-fails
- `test-driven-development` — Iron Law: NO PRODUCTION CODE WITHOUT FAILING TEST
- `dispatching-parallel-agents` — 2+ independent tasks methodology
- `receiving-code-review` — handle review feedback rigorously
- `requesting-code-review` — request review at completion
- `writing-skills` — TDD applied to skill creation
- `finishing-a-development-branch` — generic merge/PR/cleanup decision tree
- `using-superpowers` — meta: how to find and use skills

## Layer 2 — Tracker flow (project tracking)

Our tracker skills are the project-tracking layer. They handle Linear epics, sub-issues, magic-word commits, manual cases comments, and PR creation. Tickets are the unit of work.

Skills:
- `/create-epic`, `/create-ticket` — drafting
- `/execute-epic`, `/execute-ticket` — orchestrated execution
- `/commit`, `/pr-create`, `/epic-close` — lifecycle
- `/manual-cases-list` — aggregate manual cases across an epic

Back-compat aliases (`/linear-create-epic`, `/linear-execute-epic`, etc.) remain available — they forward to the canonical names above. Aliases will be cleaned up post-FORGE-8.

## How they compose

```
                  Linear flow                    Superpowers
                  ===========                    ===========
Brief →           /create-epic →
                       drafts EMB-N + sub-issues

For a sub-issue (standard project work):
  /execute-ticket EMB-NN →
      Reads ticket body
      [delegates implementation to →]            superpowers:subagent-driven-development
                                                       Reads plan/ticket as plan
                                                       Per task:
                                                         - implementer subagent (TDD)
                                                         - spec compliance reviewer
                                                         - code quality reviewer
                                                       Returns DONE
      Runs linter-runner + test-runner agents
      Invokes superpowers:verification-before-completion (Iron Law gate)
      Posts manual cases comment
      Magic-word commit
      Returns DONE

For ad-hoc / non-Linear work:
  superpowers:brainstorming →
      Explores intent, design
      writes docs/superpowers/specs/<date>-<topic>-design.md
  superpowers:writing-plans →
      writes docs/superpowers/plans/<date>-<feature>.md
  superpowers:subagent-driven-development →
      Executes the plan
  superpowers:finishing-a-development-branch →
      Merge/PR/cleanup decision
```

## Decision tree — which to use

| Situation | Use |
|---|---|
| Tracked work in Embergard / FORGE / etc. (epic + sub-issues exist) | Linear flow (which embeds superpowers internally) |
| Ad-hoc feature exploration without Linear | `superpowers:brainstorming` → `writing-plans` → execution |
| Small one-off fix in existing codebase | `superpowers:test-driven-development` directly |
| Hard bug that's been resisting fixes (3+ attempts) | `superpowers:systematic-debugging` (heavier than `/diagnose`) |
| Quick bug investigation | `/diagnose` (lighter, 6-phase) |
| Solo experimentation in Embergard before formalizing as ticket | `superpowers:prototype` (mattpocock) or `superpowers:brainstorming` |

## Iron Law (universal)

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Applied via `superpowers:verification-before-completion`. Both `/execute-ticket` and `/execute-epic` invoke this gate before any DONE claim.

## Conflicts resolved (FORGE-2.9 / EMB-292, 2026-05-09)

- `~/.claude/commands/tdd.md` (mattpocock) — DELETED, superseded by `superpowers:test-driven-development`
- `~/.claude/commands/write-a-skill.md` (mattpocock) — DELETED, superseded by `superpowers:writing-skills`
- `~/.claude/commands/diagnose.md` (mattpocock) — KEPT alongside `superpowers:systematic-debugging`. Different weights.
- `/review` — built-in `/review` (PR review) shadowed by our local 5-domain orchestrator. Decision: keep as-is. (FORGE-2.3)

## Status

This methodology stack is in effect since 2026-05-09 (FORGE-2.9 / EMB-292). Future Embergard sessions should default to invoking superpowers skills as described above when triggered.
