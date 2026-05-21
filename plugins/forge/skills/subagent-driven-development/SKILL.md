---
name: subagent-driven-development
description: Execute an implementation plan by dispatching one fresh subagent per task, each followed by two-stage review (spec compliance, then code quality). Invoked by execute-ticket for standard project tickets to keep the orchestrator's context clean while each task runs in isolation.
type: fundamental
inspired-by:
  - author: obra
    repo: github.com/obra/superpowers
    skill: subagent-driven-development
    relation: adapted
---

# Subagent-driven development

Execute a plan by dispatching a fresh subagent per task, with a two-stage review after each: spec compliance first, then code quality. The orchestrator never writes code itself — it curates context, dispatches, reviews, and loops.

**Core principle:** fresh subagent per task + two-stage review = high quality with a clean orchestrator context.

**Why subagents:** each task runs in isolated context you construct precisely — the subagent never inherits your session history. This keeps focus tight and preserves your own context for coordination.

**Continuous execution:** do not pause to check in between tasks. Run every task in the plan. Stop only for an unresolvable BLOCKED status, genuine ambiguity, or all-tasks-complete. "Should I continue?" prompts waste the caller's time.

## When to use

Invoked by `forge:execute-ticket` (Step 6) once a standard project ticket has a task breakdown. Use it when:

- there is an implementation plan or task list,
- the tasks are mostly independent,
- the work stays in this session.

Tightly-coupled tasks with no clean boundaries → execute manually instead. Config-only FORGE tickets → use the ad-hoc fallback in `forge:execute-ticket`, not this skill.

## The per-task loop

For each task, in order:

1. **Dispatch the implementer subagent.** Provide the full task text + scene-setting context (where it fits, relevant files, the spec). Never make the subagent read the plan file — hand it exactly what it needs. Model per the selection table below. The implementer follows `forge:tdd` (red → green → refactor), tests, self-reviews, and commits.
2. **If the implementer asks questions** before starting, answer completely, then re-dispatch. Do not rush it into code.
3. **Dispatch the spec-compliance reviewer** (model: **sonnet** — mechanical check of code against the spec). It confirms the code matches the spec: nothing missing, nothing extra. Issues → the same implementer subagent fixes them → re-review. Loop until clean.
4. **Dispatch the code-quality reviewer** (model: **opus** — judgment on design, naming, coupling). Only after spec compliance is clean. Issues → implementer fixes → re-review. Loop until approved.
5. **Mark the task complete** in your task tracker. Move to the next.

After all tasks: dispatch one final code-quality reviewer (model: **opus**) over the whole implementation, then hand control back to the caller (`forge:execute-ticket` owns commit/tracker semantics).

## Model selection

Use the least powerful model that can do the job. In this plugin only `sonnet` and `opus` are used.

| Task signal | Implementer model |
|---|---|
| 1-2 files, complete spec, mechanical | **sonnet** |
| Multi-file integration, pattern matching, debugging | **sonnet** (escalate to opus if it returns BLOCKED on reasoning) |
| Design judgment, architecture, broad codebase understanding | **opus** |

Reviewers: spec-compliance reviewer is **sonnet** (mechanical); code-quality reviewer is **opus** (judgment).

## Handling implementer status

The implementer subagent reports one of four statuses:

- **DONE** → proceed to spec-compliance review.
- **DONE_WITH_CONCERNS** → read the concerns first. Correctness or scope concerns → resolve before review. Observations ("this file is getting large") → note and proceed.
- **NEEDS_CONTEXT** → provide the missing information and re-dispatch.
- **BLOCKED** → diagnose: context problem → add context, re-dispatch same model; needs more reasoning → re-dispatch with **opus**; task too large → split it; plan itself wrong → escalate to the human.

Never ignore an escalation, and never force the same model to retry unchanged. If the subagent is stuck, something must change.

## Prompt templates

The three dispatch prompts (implementer, spec-compliance reviewer, code-quality reviewer) live in `references/prompts.md`. Construct each from the template plus the task-specific context you curate.

## Verification

Before marking the whole plan complete, apply `forge:verification-before-completion`: confirm via the actual VCS diff that each subagent's reported work is real, and that the final review passed in this turn.

## Red flags

- Starting implementation on `main` / `master` without explicit consent.
- Skipping either review stage, or starting code-quality review before spec compliance is clean.
- Dispatching multiple implementer subagents in parallel for overlapping files (conflicts).
- Making a subagent read the plan file instead of handing it the full task text.
- Trusting a subagent's "success" without checking the diff (that is what the verification gate is for).
- Accepting "close enough" on spec compliance, or moving to the next task with an open review issue.

## Do NOT

- Delegate tracker comments, commit, or push to the subagents — the caller owns those.
- Let the implementer's self-review replace the two review stages; both are still required.
- Skip the re-review loop after a reviewer finds issues.
