# Example: a well-formed `minimal` skill

A compact, single-responsibility skill that passes the audit. Shown here as a SKILL.md body annotated.

```yaml
---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
type: minimal
---
```

```markdown
# Handoff

Produce a single markdown document summarizing the active task so a fresh
agent can continue without context loss.

## Output sections (in order)

1. **Goal** — one sentence: what the user is trying to achieve.
2. **State** — what is done, what is in progress, what is blocked.
3. **Files of interest** — absolute paths with one-line purpose each.
4. **Next action** — the single concrete next step.

Write to `handoff-<YYYY-MM-DD>.md` in the project root. Do not commit.
```

## Why this passes

- Front-matter has `name`, `description`, `type`.
- `type: minimal` and the body is well under 80 lines.
- One responsibility, named clearly in `description`.
- Does not invoke any agent — no model declaration needed.
- No `superpowers:*` references.
- No empty sections; no dangling `references/` links.
- Original work — no `inspired-by` block.
