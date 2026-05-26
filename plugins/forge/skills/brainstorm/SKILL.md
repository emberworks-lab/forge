---
name: brainstorm
description: Forge's design-exploration entry point — use BEFORE any feature, design, or behavior-change work when modifying existing systems, adding functionality, or starting new components. Guided dialectic that stress-tests intent, surfaces hidden assumptions, and produces an approved design spec. Prefer over superpowers:brainstorming in any forge-managed project. Skip for trivial edits, config tweaks, single-file mechanical changes.
type: hybrid
inspired-by:
  - author: obra
    repo: github.com/obra/superpowers
    skill: brainstorming
    relation: adapted
---

# Brainstorm

Turn an idea into a reviewed design before code is written. The output is a committed spec document and explicit user approval to plan implementation. Nothing else is produced here.

## Hard gate

Do NOT call any implementation skill, scaffold a project, edit code, or write tests until the user has approved a design produced by this skill. Applies to every project, including ones that look "too simple to design".

## Contract

Given a fresh idea and the current project context, walk the user through the steps below. The terminal state is a committed `docs/specs/YYYY-MM-DD-<topic>-design.md` plus user approval to move on. No other deliverable.

## Steps

Walk in order. Do not skip.

1. **Survey project context** — recent commits, top-level docs, existing patterns. One pass, no questions yet.
2. **Scope check** — if the idea is actually several independent subsystems, surface that first. Help the user decompose into separately-spec'd sub-projects before continuing. Each sub-project gets its own brainstorm run.
3. **Clarify, one question at a time** — purpose, constraints, success criteria. Multiple choice when possible; one question per message. See `references/question-craft.md` for technique.
4. **Propose 2-3 approaches** — each one-line description plus one-line tradeoff, recommend one, explain why.
5. **Present the design in sections** — architecture, components, data flow, error handling, testing. Scale each section to its complexity (a sentence is fine for trivial parts). After each section, ask "does this look right so far?".
6. **Write the spec** — save to `docs/specs/YYYY-MM-DD-<topic>-design.md` (or project-local override if the user has one). Commit it.
7. **Self-review the spec** — scan for TBDs, contradictions, ambiguity, scope creep. Fix inline. No second pass.
8. **User reviews the spec** — surface the path, ask the user to read it, wait for approval. Loop back to step 6 on requested changes.
9. **Hand off to planning** — once approved, invoke the planning skill (skill not yet migrated; until then, return the spec path and stop here).

## Design discipline

- **Isolation and clarity** — break the system into units with one job each, well-defined interfaces, independently testable. For each unit you should be able to answer: what does it do, how do you call it, what does it depend on?
- **Follow existing patterns** — when working in an existing codebase, explore the structure first; propose changes that fit the established shape.
- **Targeted improvement, not gold-plating** — if the surrounding code has a problem that affects the work, fix it as part of the design. Don't propose unrelated refactors.
- **YAGNI** — remove features the user didn't ask for. Adjacent variants, "while we're here" extras, and consistency-for-consistency-sake all out.

See `references/anti-patterns.md` for the rationalizations this skill is designed to block ("too simple to design", "I'll add the spec later", and friends).

## Key principles

- One question per message.
- Multiple choice when possible.
- Lead with your recommendation, then alternatives.
- Incremental approval — section by section, not big-bang.
- Be ready to back up when something doesn't add up.

## What this skill does not cover

- **Implementation planning** — out of scope. Handed off to the planning skill once the spec is approved.
- **Coding** — never starts here, by design (see Hard gate).
- **Visual mockups / interactive companion** — deferred; not part of this skill.
