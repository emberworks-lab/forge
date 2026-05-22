# PRD template

The PRD body uses these sections, in this order. Use the project's domain
glossary throughout, and respect any ADRs in the area you're touching. Skip a
section only when it is genuinely empty (e.g. nothing is out of scope).

```markdown
## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories, each in the format:

1. As an <actor>, I want a <feature>, so that <benefit>

Make this list extensive — cover every aspect of the feature.

## Implementation Decisions

The decisions that were made. May include:

- The modules that will be built or modified
- The interfaces of those modules
- Technical clarifications surfaced in the conversation
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include file paths or code snippets — they go stale fast.

Exception: if a prototype produced a snippet that encodes a decision more
precisely than prose can (state machine, reducer, schema, type shape), inline
it within the relevant decision and note it came from a prototype. Trim to the
decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

The testing decisions that were made. Include:

- What makes a good test here (test external behavior, not implementation
  details)
- Which modules will be tested
- Prior art — similar tests already in the codebase

## Out of Scope

What is deliberately not covered by this PRD.

## Further Notes

Any remaining notes about the feature.
```

## Deep modules

While drafting Implementation Decisions, sketch the major modules to build or
modify, and actively look for deep modules that can be tested in isolation. A
deep module encapsulates a lot of functionality behind a simple, testable
interface that rarely changes — the opposite of a shallow module whose
interface is nearly as large as its implementation. Surface these in the
Implementation Decisions section so the downstream ticket inherits the seams.

## Shaping for `forge:create-ticket` Mode A

Mode A reads a `docs/0X_*.md` plan and maps fixed headings into the ticket:

- doc `## Goal` → ticket `## What`
- doc `## Acceptance criteria` → ticket `## Acceptance`

When the publish target is the `markdown` backend (PRD written to a
`docs/0X_*.md` file), add a short lead block above the PRD sections so Mode A
can consume it directly:

```markdown
## Goal
<1-2 sentence paraphrase of Problem + Solution>

## Acceptance criteria
<bulleted, verifiable outcomes — derived from the User Stories>
```

Keep the full PRD sections below that lead block as the exhaustive plan Mode A
points the ticket's `## References` at. For remote backends (Linear / GitHub)
the PRD lives as the issue body; `forge:create-ticket` then references the issue
directly rather than a doc path.
