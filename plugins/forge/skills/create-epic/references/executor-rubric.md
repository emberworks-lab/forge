# Executor selection rubric

When deciding `[opus]` vs `[sonnet]` for a sub-issue:

## `[opus]` when

- Designing a NEW abstraction (sealed error hierarchy, sync conflict resolver, state machine for a new domain)
- Deriving formulas from a spec (combat damage, drop tables, pricing tiers)
- Security-critical paths (auth, RLS policies, token handling)
- Complex algorithm with non-obvious correctness (deterministic sampler given a seed, retry idempotency)
- Cross-cutting refactor that touches many domains and needs careful planning
- Anything where extended thinking earns its cost

## `[sonnet]` when

- Implementing a clearly-scoped feature by following an existing plan
- Adding a new Bloc + repository + UI by an established pattern (`/kit-create-feature`)
- Adding a Drift table + migration by an established pattern (`/kit-add-drift-table`)
- Writing tests against existing code with clear behaviors
- Refactoring with a clear before/after
- Content additions (new game items, translation strings, content schema entries)
- Lint fixes, formatting, barrel updates
- Anything where the task is well-defined and the implementation path is obvious

## Default

**Default `[sonnet]` if uncertain.** It's cheaper and `sonnet` is plenty capable; only promote to `opus` when you can articulate a specific reason this work needs extended thinking.
