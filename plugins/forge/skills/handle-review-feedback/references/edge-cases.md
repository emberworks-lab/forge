# Edge cases and constraints for handle-review-feedback

## Edge cases

- **Feedback contradicts an ADR**: classify as push-back. Reference the ADR by path (`docs/04_tech/adr/<n>_*.md`) in the response.
- **Feedback is rude or dismissive**: ignore the tone. Extract the technical content and respond technically. Technical correctness first.
- **Feedback contradicts itself** (item 2 reverses item 1): ask the reviewer to clarify priority before implementing either.
- **Feedback is already implemented in main** (reviewer hadn't pulled): note it, ask "should I rebase + show the diff, or do you want to update your reviewer first?"
- **Feedback is too large** (>10 items, would need its own ticket): suggest creating a follow-up ticket via `/create-ticket` rather than absorbing it inline.
- **Reviewer is the user themselves and they want it applied immediately**: still classify, still verify. The user can override push-back ("I know about the ADR, do it anyway") but the verification step protects against accidental misreads.

## Constraints (do NOT)

- Say "You're absolutely right!" or any performative agreement phrase.
- Implement before classifying. Classification + user confirmation comes first.
- Batch-apply without per-item verification. One change → one lint/test pass → next change.
- Auto-commit. User invokes the commit step after reviewing.
- Silently push back — if skipping an item, the user must see the reasoning.
- Modify files outside the feedback's stated scope. If a tangential issue appears, mention it; don't fix it inline.
