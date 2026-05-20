# Type taxonomy

Every SKILL.md in the forge plugin MUST declare a `type` in its front-matter. The type signals the skill's structural shape and bounds its line count.

```yaml
---
name: <skill-name>
description: <one-sentence trigger description>
type: minimal | fundamental | hybrid
---
```

## The three types

### `minimal` — ≤ 80 lines, no `references/`

A one-shot flexible instruction. No decision tree, no scripts, no supporting files. The whole skill fits on one screen.

When to choose:

- The instruction is short — one paragraph plus 2-3 bullets.
- There is no branching: the skill does the same thing every time.
- No state crosses turn boundaries; no automation is invoked.

Examples (planned): `forge:caveman`, `forge:handoff`, `forge:hello`.

Constraint: if a `minimal` skill creeps past 80 lines, it has outgrown the type. Either trim ruthlessly back under 80, or promote to `hybrid`.

### `hybrid` — 50-120 lines + supporting files (the default)

The everyday shape. Core contract, decision tree, and checklist live in SKILL.md; long anti-pattern lists, prior-art notes, and edge cases live in `references/*.md`; automation lives in `scripts/`; sample inputs/outputs live in `examples/`.

When to choose:

- The skill has a non-trivial decision tree or checklist.
- There are anti-patterns or rationale worth recording but not worth blocking the main flow.
- One or two scripts assist the workflow.

Examples (planned): `forge:epic-close`, `forge:create-epic`, `forge:review`, `forge:execute-ticket`.

This is the default. If you're unsure which type to pick, pick `hybrid`.

### `fundamental` — up to ~300 lines + `references/` + `scripts/`

A rigid foundational workflow that **downstream skills cite as authoritative**. These skills carry discipline that the whole plugin depends on; their length is justified because their rules govern many other artifacts.

When to choose:

- Another skill will reference this one as the source of truth for behavior.
- The skill encodes policy or a long discipline (TDD, deep diagnosis, the audit rules in `forge:writing-skill` itself).
- The 80-line and 120-line caps would force harmful compression.

Examples (planned): `forge:writing-skill` (this skill), `forge:tdd`, `forge:diagnose-deep`.

Cap: 300 lines for SKILL.md alone. Content in `references/` is uncapped — extract liberally.

## Decision tree

Use this in order:

1. **Will another skill cite this skill as authoritative for some behavior?** → `fundamental`.
2. **Is the entire instruction one short paragraph plus 2-3 bullets, with no branching?** → `minimal`.
3. **Otherwise** → `hybrid`.

## Line caps enforced by audit

`scripts/audit.sh` reads the declared `type` and rejects files that exceed the cap:

| Type | Cap (SKILL.md only) |
|---|---|
| minimal | 80 |
| hybrid | 120 |
| fundamental | 300 |

`references/`, `scripts/`, and `examples/` files are uncapped — extract aggressively when SKILL.md gets long.

## A note on growth

A `minimal` skill that grows over time is not a sign of failure of the type; it's a sign that the skill's responsibilities have expanded. Promote it to `hybrid` deliberately, restructure the body into core + references, and update the front-matter.

Avoid the opposite anti-pattern: a `fundamental` skill that turns out to never be cited by anyone. If after a few months no other skill references it, demote to `hybrid` and trim.
