---
name: verification-before-completion
description: Enforce the Iron Law that no completion, fix, or pass claim may be made without fresh verification evidence gathered in the current turn. Invoked by execute-ticket and epic-close before any DONE claim, commit, or PR.
type: fundamental
inspired-by:
  - author: obra
    repo: github.com/obra/superpowers
    skill: verification-before-completion
    relation: adapted
---

# Verification before completion

Claiming work is done without verifying it is dishonesty, not efficiency. This skill is the gate every other forge skill passes through before it asserts success.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If the verification command was not run in the current turn, the claim cannot be made. A passing run from three messages ago is not evidence now — code, environment, or assumptions may have changed since.

Violating the letter of this rule is violating its spirit. Rephrasing a success claim to dodge the word "done" does not exempt it.

## The gate function

Before stating any status, expressing satisfaction, or moving on:

1. **Identify** — which exact command proves this claim?
2. **Run** — execute the full command, fresh and complete, in this turn.
3. **Read** — full output: exit code, failure count, not just the tail.
4. **Verify** — does the output actually confirm the claim?
   - No → state the real status with the evidence.
   - Yes → state the claim *with* the evidence attached.
5. **Only then** — make the claim.

Skipping any step is lying, not verifying.

## What counts as evidence

| Claim | Sufficient evidence | NOT sufficient |
|---|---|---|
| Tests pass | Test command output, 0 failures, this turn | Prior run; "should pass" |
| Linter clean | Linter output, 0 errors, this turn | Partial check; extrapolation |
| Build succeeds | Build command exit 0 | Linter passing; logs "look fine" |
| Bug fixed | Original symptom re-tested, now passes | Code changed, assumed fixed |
| Regression test works | Red→green cycle verified (fails without fix, passes with) | Test passes once |
| Delegated agent completed | VCS diff shows the actual changes | Delegated agent's "success" report |
| Requirements met | Line-by-line checklist against the spec | "Tests pass, so done" |

## Red flags — stop before claiming

- "should", "probably", "seems to", "looks correct"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- About to commit / push / open a PR without a fresh run
- Trusting a delegated agent's self-reported success without checking the diff
- Relying on a partial or scoped check to claim the whole thing passes
- "Just this once" / "I'm confident" / "I'm tired and want this over"
- Any wording that *implies* success without a run behind it

## Rationalization table

| Excuse | Reality |
|---|---|
| "Should work now" | Run the verification. |
| "I'm confident" | Confidence is not evidence. |
| "Just this once" | No exceptions — that is how trust breaks. |
| "Linter passed" | The linter does not compile or test. |
| "Delegated agent said success" | Verify independently via the diff. |
| "Partial check is enough" | Partial proves the part, not the whole. |
| "Different words, so the rule won't apply" | Spirit over letter. |

## Verification patterns

**Tests**
```
RIGHT: run test command → see 34/34 pass → "all tests pass (34/34)"
WRONG: "should pass now" / "looks correct"
```

**Regression test (red-green)**
```
RIGHT: write test → run (fails) → apply fix → run (passes) → "regression covered"
WRONG: "I wrote a regression test" with no red phase shown
```

**Build / typecheck**
```
RIGHT: run build → exit 0 → "build passes"
WRONG: "linter passed" (the linter does not check compilation)
```

**Requirements**
```
RIGHT: re-read the ticket acceptance → checklist each item → report gaps or completion
WRONG: "tests pass, so the ticket is done"
```

**Delegated work**
```
RIGHT: delegated agent reports DONE → read VCS diff → confirm the change is real → report actual state
WRONG: trust the delegated agent's report verbatim
```

## When to apply

Always, before:

- any success / completion / "fixed" / "passing" claim, in any phrasing
- any expression of satisfaction about the work state
- committing, pushing, or opening a PR
- marking a ticket or task done and moving to the next
- accepting a delegated agent's reported result

The rule applies to exact phrases, paraphrases, synonyms, and anything that implies success.

## How other skills invoke this

`forge:execute-ticket` invokes this skill at its verification gate (after lint + test, before commit). `forge:epic-close` and `forge:execute-epic` invoke it before any completion claim or merge. Invocation means: run the gate function above against the specific claim about to be made, and only proceed if the fresh output confirms it.

## The bottom line

Run the command. Read the output. Then claim the result. There are no shortcuts, and this is non-negotiable.
