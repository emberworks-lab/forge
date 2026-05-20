# Anti-example: a skill that fails the audit

This file is intentionally broken to demonstrate the audit catching violations. Do NOT model real skills on it.

```yaml
---
name: do-everything
description: Diagnose, review, and commit code in one go.
type: gigantic
inspired-by:
  - author: someone
    repo: github.com/elsewhere
    skill: thing
    relation: forked
---
```

```markdown
# Do Everything

Step 1: run linter. Step 2: spawn a subagent to triage findings.
We use haiku for speed.

Check superpowers:brainstorming for the dialectic pattern.

## Empty section
## Another section

Refer to references/missing.md for details.
```

## What the audit will flag

- Check 3: `type: gigantic` — not in `minimal | fundamental | hybrid`.
- Check 5: `relation: forked` — not in `adapted | concept | structure`.
- Check 6: `superpowers:brainstorming` mentioned in body.
- Check 7: "subagent" mentioned but no `sonnet`/`opus`; also mentions `haiku`.
- Check 8: `references/missing.md` is a dangling link.
- Check 9: `## Empty section` is immediately followed by `## Another section`.

Bonus: the `description` uses "and" between distinct verbs (Diagnose, review, commit), violating step 1 of the slim audit checklist — a reviewer should reject this on single-responsibility grounds.
