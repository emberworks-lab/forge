# Caveman opt-in pattern

Reference for skill authors who want to opt their skill in to `/caveman` ultra-compressed output mode.

The policy file governs **whether** a skill should opt in. This file documents **how** to opt in safely once that decision is made.

> **Policy source:** [`forge/docs/conventions/caveman-policy.md`](../../../docs/conventions/caveman-policy.md)

## When to consider opting in

Use the policy file's decision matrix. Quick filter — do NOT consider opt-in if your skill:

- Produces content shown to third parties (PR descriptions, public docs, ticket comments)
- Generates code (the surrounding tool-use narration loses context for debugging)
- IS `forge:writing-skill` (recursion: cannot author a readable SKILL.md under caveman compression)
- Has output volume < ~30% of its total tokens — economy will be invisible

If you pass that filter, consult the per-skill recommendation table in the policy file.

## The pattern

Three-step structure, all three steps are required. Skipping any step makes the opt-in unsafe.

### Step 0 — propose, never force

Before any heavy loop, the skill emits a single user-facing prompt:

```
This skill produces verbose summaries. `/caveman` would compress output by
~X% (per pilot data) while preserving technical content. Want me to enable
it for this run? (yes / no / skip)
```

Wait for explicit `yes` before continuing. Default to `no` on any other input (including no answer).

The economy number `X` MUST come from the policy file's per-skill recommendation table, not from the source `/caveman`'s `~75%` claim — that number is across the wrong workload.

### Step 1 — emit `/caveman on` as the first work line

If user said `yes`, the very first line the skill emits when starting its loop body is `/caveman on`. Not in a comment, not buried inside a tool call — visible to the user so they know what's active.

### Step 2 — auto-restore at the end

Before the skill's final user-facing output (whether success path or error path), emit `/caveman off`. **This is non-negotiable**: leaving caveman mode on poisons subsequent unrelated work in the same Claude Code session.

Use a `finally`-equivalent pattern in your skill's flow control. If the skill has multiple exit branches (success / halt / dry-run), every branch must hit the off switch.

## The anti-pattern (do not do this)

Three failure modes the pattern exists to prevent:

### Force-on without user notice

```markdown
## Step 0: enable compression
Emit `/caveman on` to reduce output noise.
```

User had no say. If the workload doesn't fit caveman's compression sweet spot, the user just lost readable output for no economy gain. Always propose, always wait for `yes`.

### Conditional `/caveman off` that can be skipped

```markdown
## Step N
If summary was generated successfully, emit `/caveman off`.
```

Skill halts before this step on any error path → caveman stays on. The user's *next* session topic now reads as if dictated by a caveman. The off switch must be unconditional and in every exit branch.

### Mention `/caveman` without opting in

A SKILL.md that *talks about* `/caveman` (e.g. in a "see also" section) but never emits `/caveman on` is fine. A SKILL.md that emits `/caveman on` without a matching `/caveman off` is broken. A future audit rule may check for this balance — for now it's manual review.

## Example flow (illustrative)

A hypothetical opt-in inside `forge:execute-epic`:

```markdown
### Step 0 — caveman gate

Before dispatching subagents for the per-ticket loop:

> "This epic has N tickets. Per-ticket summaries are the largest output
> source. `/caveman` would compress them ~30% based on pilot data while
> preserving commit-quality content. Enable for this run? (yes/no)"

On `yes`: emit `/caveman on`. Continue.
On anything else: continue without compression.

### Step 7.5 — caveman restore

Before printing the final epic summary in step 8, emit `/caveman off`
unconditionally. Add the same emit to the halt branch in step 5.
```

## Cross-links

- Policy + thresholds: [`forge/docs/conventions/caveman-policy.md`](../../../docs/conventions/caveman-policy.md)
- Pilot template + raw data: [`forge/docs/caveman-pilot-2026-05.md`](../../../docs/caveman-pilot-2026-05.md)
- The `/caveman` skill itself: `forge:caveman`
