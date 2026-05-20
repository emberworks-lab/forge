# Composition principle

Skills follow code composition rules. A skill is a reusable unit of behavior; the same engineering instincts that keep code maintainable keep skill libraries navigable.

## The four rules

### 1. Single responsibility

One skill = one concern. The skill's `description` field is the test: if you cannot describe what the skill does in one declarative sentence without using "and" between two verbs, the skill is doing too much. Split it.

A SKILL.md outline that reads as two distinct chapters ("first we do X, then a completely different Y") is two skills in a trench coat.

### 2. Master composes via explicit invocation

When a skill needs another skill's behavior, it **invokes** that skill — it does not inline its content.

- Good: `/forge:epic-close` says "Step 1: invoke `forge:simplify-branch`. Step 2: invoke `forge:review`."
- Bad: `/forge:epic-close` copies the simplify checklist into its own body "for convenience".

Inlining defeats reuse: when the sub-skill evolves, every inlining copy drifts. Inlining also hides the dependency graph — readers of the master cannot tell which downstream skills they implicitly rely on.

The forbidden anti-pattern: a master skill that reads the **body** of `~/.claude/commands/<sub>.md` or `plugins/forge/skills/<sub>/SKILL.md` programmatically, instead of invoking `/<sub>`. If you find yourself wanting to do this, you are bypassing the Skill tool — stop and invoke instead.

### 3. Low coupling

Sub-skills know nothing about which master called them. Inputs are explicit at the boundary (passed as arguments or read from a well-known file like `tracker.json`); outputs are explicit (return text, write a known artifact path, exit code).

Concretely:

- A sub-skill does not branch on "if my caller is `/forge:epic-close` then do X else Y". It does its one job.
- A master does not rely on a sub-skill's internal scratch files. If state needs to flow back, the sub-skill returns it explicitly.

### 4. Extract when reused, not before (YAGNI)

If logic is needed in only one skill, keep it inline. Premature extraction — pulling a sub-skill out before there is a second caller — creates a maintenance liability for hypothetical reuse that may never come.

When a **second** skill needs the same logic, extract. Now the abstraction has a real shape pinned by two concrete use cases, and the cost of moving it is justified.

## Practical signals it's time to split

- Two different prompts (mechanical vs creative) reach for the same checklist mid-flow.
- A skill's "Phase 2" section is longer than its "Phase 1" and changes for unrelated reasons.
- You're tempted to write `if mode == 'A'` branching in the SKILL.md body.

In each case, the underlying problem is mixed responsibility; extraction restores clarity.

## Practical signals it's NOT time to split

- The logic appears in exactly one place and you imagine "someone might want this later".
- The two sub-blocks always run together and never independently.
- Splitting would add a layer of indirection without changing the call surface.

When in doubt: leave it inline. The bar for extraction is **a real second caller**, not a hypothetical one.
