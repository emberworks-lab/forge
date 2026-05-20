# Edge cases for `forge:execute-ticket`

## When to stop and ask

STOP and raise to user when:

- Hit a blocker (missing dependency, test fails repeatedly, instruction unclear)
- Plan has critical gaps preventing progress (placeholder paths, undefined types, contradictory steps)
- You don't understand an instruction — and the ticket lacks an interview/read-first hint
- Verification fails after 3 attempts (lint/test won't go green; verification gate keeps rejecting)
- Subagent returns BLOCKED status
- Mid-implementation, you discover the ticket's scope was wrong (e.g. existing code already does what the ticket asks)
- A change requires editing files outside the ticket's stated scope to make sense

Don't force through blockers — stop and ask. The user prefers a halted ticket with a clear question over a half-finished commit.

## Edge cases list

- **Ticket body is empty / placeholder**: tell user "ticket body is empty; can't execute. Run `/create-ticket` to flesh it out, or pass scope inline."
- **Multiple `/kit-*` skills conflict**: pick the most specific. If still ambiguous, ask the user.
- **Codegen produces unexpected diff**: if `dart run build_runner build` produces changes, inspect them; that may be the actual fix the ticket wants. Include in commit.
- **Tests pass locally but you suspect flakiness**: re-run once. If still passes, trust them. If passes once and fails once, halt and tell user "flaky test detected: <name>; investigate before committing."
- **Linter wants to remove an import you just added**: probably a mistake on your end (you added something but didn't use it). Re-check the implementation.
- **`tracker.json` missing** — fall back to current Linear-MCP behavior (see dispatch note at top of SKILL.md). This fallback exists for legacy repos without `tracker.json`.

## Loop integration

This skill is the unit `forge:execute-epic` calls per sub-issue. It MUST:

- Halt cleanly on any failure (don't half-finish)
- Return a structured status to the orchestrator (done / halted)
- Leave the working tree in a recoverable state (no half-applied changes from a failed Edit)

Standalone use is also valid: solo dev picks up one-off ticket, runs `/execute-ticket EMB-X`, reviews the diff, runs `/commit X` if happy.
