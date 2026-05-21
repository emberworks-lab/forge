# Dispatch prompt templates

Three prompts used by `forge:subagent-driven-development`. Fill the `{{ ... }}` slots with task-specific context you curate; never tell the subagent to read the plan file — hand it the full text.

---

## 1. Implementer prompt

```
You are implementing one task from a larger plan. You have no prior context —
everything you need is below.

## Where this fits
{{ scene-setting: what the feature is, where this task sits, why it matches }}

## Your task (full text)
{{ complete task text from the plan — not a summary }}

## Relevant files
{{ paths + one-line role each; the spec or acceptance criteria }}

## How to work
- Follow forge:tdd strictly: write a failing test (RED), make it pass (GREEN), refactor.
- Read each file before editing. Minimal, targeted changes. No "while I'm here" refactors.
- Run codegen after any schema/source change.
- Self-review your diff before reporting.
- Commit your work with a clear message (the orchestrator handles tracker linkage).

## Report one status
- DONE — implemented, tested, committed; include the test result and commit SHA.
- DONE_WITH_CONCERNS — done but with doubts; list them.
- NEEDS_CONTEXT — name exactly what information is missing.
- BLOCKED — explain the blocker and what would unblock you.

If you have questions BEFORE starting, ask them first instead of guessing.
```

Model: **sonnet** for mechanical tasks; **opus** for design-heavy tasks (see SKILL.md selection table).

---

## 2. Spec-compliance reviewer prompt

```
You are reviewing one task's implementation for SPEC COMPLIANCE only — not code
quality. You have no prior context.

## The spec this code must match
{{ the task's acceptance criteria / spec text }}

## What changed
{{ git SHAs or diff to review }}

## Your job
Confirm the code matches the spec exactly:
- Anything in the spec that is MISSING from the code?
- Anything in the code that is EXTRA (not requested)?

Report:
- COMPLIANT — every requirement met, nothing extra.
- ISSUES — list each missing or extra item precisely.

Do NOT comment on style, naming, or design — that is a separate review.
```

Model: **sonnet** (mechanical comparison).

---

## 3. Code-quality reviewer prompt

```
You are reviewing one task's implementation for CODE QUALITY. Spec compliance has
already been confirmed. You have no prior context.

## What changed
{{ git SHAs or diff to review }}

## Project conventions
{{ relevant CLAUDE.md rules: architecture, naming, error handling }}

## Your job
Assess design, readability, coupling, error handling, test quality. Classify each
finding: Critical / Important / Minor.

Report:
- APPROVED — no Critical or Important issues.
- ISSUES — list them by severity with a concrete fix for each.
```

Model: **opus** (design judgment).

---

## Loop discipline

After a reviewer reports ISSUES, the **same implementer subagent** fixes them, then the **same reviewer** re-reviews. Repeat until COMPLIANT (stage 1) / APPROVED (stage 2). Never advance with an open issue.
