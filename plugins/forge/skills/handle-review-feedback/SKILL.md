---
name: handle-review-feedback
description: Process PR or Linear code-review feedback by classifying each item as valid, needs-clarification, or push-back before implementing anything.
type: hybrid
---

# Handle Review Feedback

Trigger: user pastes PR feedback, code-review comments, Linear ticket critique, or says "ось ревʼю", "here's the feedback", `/handle-review-feedback`.

## Core principle

**Technical correctness over social comfort.** Verify before implementing. Ask before assuming. Push back when feedback is wrong. Never say "You're absolutely right!" or any performative agreement phrase — skip to the technical response.

## Step 1 — Locate the feedback

Three sources, in priority order:

1. **Inline in chat.** User pasted feedback as a chat message. Read it from the conversation.
2. **Linear ticket / comment.** User passed `EMB-NN` or a Linear URL. Use `list_comments` Linear MCP to fetch the latest comments; or parse the ticket body for `## Review` / `## Concerns`.
3. **GitHub PR.** User passed a PR number or URL. Run `gh pr view <num> --comments` to fetch.

If the source is ambiguous, ask once. Don't guess.

## Step 2 — Classify each suggestion

For each item in the feedback, assign one class:

| Class | Meaning | Action |
|---|---|---|
| **valid** | Technically correct, applies to this codebase, doesn't conflict with ADRs | Implement (Step 3) |
| **needs-clarification** | Ambiguous scope, unclear which file, missing context | Ask before touching code |
| **push-back** | Technically wrong, contradicts ADR, breaks behavior, or reviewer missed context | Respond with technical reasoning; do NOT implement |

Show the classified list before implementing anything and wait for confirmation:

```
Feedback classification:
1. <suggestion> → valid (will implement)
2. <suggestion> → needs-clarification (asking: <question>)
3. <suggestion> → push-back (reason: <…>)

OK to proceed with valid items + clarification questions? (y / edit / abort)
```

## Step 3 — Implement valid items, one at a time

For each `valid` item: read the affected file(s), apply the minimal targeted change, run the project's lint command on the touched files, run relevant tests if they cover the touched code. Move to the next item only after the previous passes. Do not batch.

## Step 4 — Push-back protocol

When pushing back: state the technical reason, cite the contradiction (ADR path, decisions-log entry, test, CLAUDE.md rule), and frame as a question: "I think this is wrong because <X>; want me to proceed anyway, or are we re-thinking <X>?"

## Step 5 — Output (do NOT auto-commit)

```
Feedback handled (<TICKET-ID> / PR <num>):
- valid (implemented): <count> items, files changed: <list>
- needs-clarification (waiting on user): <count> items
- push-back (reasoning sent): <count> items

Lint: clean / Tests: passed (X tests).
NO commit made — review diff with `git diff` then commit if good.
```

If feedback was attached to a Linear ticket, post a brief comment noting which items were applied / queried / pushed-back. Do NOT close the ticket.

## Edge cases and constraints

See `references/edge-cases.md`.
