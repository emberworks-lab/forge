# Architectural escape hatch

After three failed fix attempts on the same bug, stop. The problem is no longer "we haven't found the right local change". The architecture is the bug.

## The trigger

Pattern indicators that say "this is architectural, not local":

- Each fix surfaces a new problem in a different part of the code.
- Each fix requires "just one more" refactor to land cleanly.
- Tests pass for the original failure but break elsewhere.
- The hypothesis-fix cycle keeps producing the same kind of failure with a new label.

If two of these are true after two fix attempts, treat the third attempt as your last; on the fourth, stop unconditionally.

## What to stop doing

- Don't propose fix #4.
- Don't bundle the failing fixes into a "comprehensive solution".
- Don't widen the scope of the current PR.

These all mask the architectural problem with more local damage.

## What to do instead

1. **Pause and surface the pattern.** Tell the user: "I've tried three fixes; each one reveals a new shared-state issue in a different place. I think the underlying abstraction is wrong, not the patches."
2. **State what the architecture currently assumes.** "This code assumes X is unique per request, but the new feature shares X across requests." Be specific.
3. **Offer two paths.**
   - A) Continue patching with the architectural debt acknowledged — log it, schedule the refactor.
   - B) Stop, redesign the abstraction, then implement once with a clean shape.
4. **Let the user decide.** Don't unilaterally start a refactor; don't unilaterally keep patching either. This is a scope decision that's theirs to make.

## Common architectural failure modes

- **Shared mutable state** masquerading as per-call data. Each fix discovers another place that mutates the shared instance.
- **Implicit ordering assumptions** between modules that the new feature breaks. Each fix patches one ordering; the next breaks another.
- **Conflated concerns** in one type (e.g., a class that's both a config and a runtime handle). Each fix splits one usage; the rest still conflate.
- **Wrong primary key / identifier** for a domain object. Fixes work in the happy path; edge cases keep producing duplicates or collisions.

Each of these is a wrong-abstraction signal. None of them are fixed by patch #4.

## How this differs from a failed hypothesis

A failed hypothesis is "I thought the cause was X, but the evidence shows it's Y; let me retry Phase 1 with the new evidence". That's normal; it's the loop working.

Three failed fixes means the loop is producing new problems faster than it solves them. That's not a hypothesis failure — that's a structural failure of the code being patched.

## What "discuss with the user" looks like

Concrete, not vague. Bring:

- A one-line summary of the bug.
- A one-line summary of each of the three failed fixes and what new problem each revealed.
- A one-sentence claim about what the architecture is doing wrong.
- The two paths above with a recommendation.

The user picks. Either way, you're out of the patch loop.
