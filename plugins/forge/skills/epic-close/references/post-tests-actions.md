# Post-tests actions — Step 5/6 hand-off shape

This file specifies the user prompt (Step 5) and the per-action **shape** (Step 6) that consume the classifier output from Step 4. Step 6's full implementation — sub-branch naming, recursion cap, merge-back flow — lives in [`step-6-execution.md`](step-6-execution.md). This file fixes the contract the orchestrator must honor; that file fixes how the orchestrator honors it.

## Step 5 — user prompt (3 actions)

Inputs available to the orchestrator at this point:

- `classifier.in_place_candidates[]` — fixes that fit on the current branch (≤ 30 lines, single file, no new abstraction).
- `classifier.sub_epic_candidates[]` — issues that need a new epic (cross-cutting, architectural, design-discussion-required).
- `classifier.totals` — `{ in_place: <N>, sub_epic: <N> }`.

If `totals.in_place == 0 && totals.sub_epic == 0` → skip Step 5 + Step 6 entirely and go straight to Step 7 (decision tree).

Otherwise present:

```
Класифікатор знайшов:
  in-place:  <N> (виправляються на цій же гілці)
  sub-epic:  <M> (потребують окремого епіка)

Дії:
  A. Все в sub-epic — defer everything до бекогу (нічого не правимо зараз).
  B. Виправити in-place зараз, sub-epic — у беког (deferred).
  C. Виправити in-place зараз + sub-epic СПАВНИТИ ЗАРАЗ (виконати негайно).

Вибір (A / B / C)?
```

No default. Wait for explicit response.

## Step 6 — hand-off contract per action

This is the **shape** the orchestrator must invoke. The execution details (sub-branch naming, recursion cap, merge-back, exit-vs-continue policy) live in [`step-6-execution.md`](step-6-execution.md).

### Action A — defer everything

1. Merge `classifier.in_place_candidates` into `classifier.sub_epic_candidates` (each becomes a sub-epic candidate).
2. Invoke `forge:create-epic` with `deferred=true` and the merged candidate list as input.
3. No code edits on the current branch. **Exit Step 6** without continuing to Step 7 — the original epic is not merged this run.

### Action B — fix-and-defer

1. For every `classifier.in_place_candidates` entry, apply the `fix_outline` on the current branch in this session (small, localized edits per the classifier's ≤ 30-lines / single-file guarantee).
2. Re-run Step 0b (tests-pass hard gate). Halt on fail.
3. Invoke `forge:create-epic` with `deferred=true` and `classifier.sub_epic_candidates` as input.
4. Continue to Step 7.

### Action C — fix-and-spawn-now

1. Apply every `classifier.in_place_candidates` `fix_outline` on the current branch (same as Action B step 1).
2. Re-run Step 0b. Halt on fail.
3. Invoke `forge:create-epic` with `deferred=false` and a `branch_hint` of `feature/<epic_ref>/postfix-<N>` (sub-branch naming convention).
4. Invoke `forge:execute-epic` on the new sub-epic. It runs on the postfix sub-branch.
5. On sub-epic completion, squash-merge the postfix branch back into the parent epic branch.
6. Re-run Step 0b on the parent branch. Continue to Step 7.

Recursion (Action C from a sub-epic's own epic-close) is allowed but capped at depth 2.

## Invariants (all three actions)

- The current epic branch is preserved except for the Action C child-branch round-trip.
- No commits except the Action C merge-back squash commit.
- The classifier output JSON is consumed read-only. The orchestrator does NOT re-call the classifier.
- If any action's in-place edit phase fails (Step 0b regression), halt with the failure snippet — do not advance to Step 7.

## What this file does NOT specify

- The exact sequence of git commands for Action C's sub-branch round-trip (lives in [`step-6-execution.md`](step-6-execution.md)).
- The `forge:create-epic` candidate-to-sub-issue mapping policy — owned by `forge:create-epic` itself.
- Re-classification policy if a fix introduces new findings (out of scope; the recursion cap is the safety valve).
