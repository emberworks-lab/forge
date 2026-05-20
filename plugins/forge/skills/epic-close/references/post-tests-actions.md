# Post-tests actions — Step 5/6 hand-off shape

This file specifies the user prompt (Step 5) and the hand-off contract (Step 6) that consume the classifier output from Step 4. Step 6's **detailed implementation** is reserved for EPIC B #3 / ticket #47 — this file fixes the **shape** of the hand-off so that ticket can land without re-negotiating boundaries.

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

This is the **shape** the orchestrator must invoke. The actual implementation (which subagent, which tracker call, which order) is owned by ticket #47.

### Action A — defer everything

1. Merge `classifier.in_place_candidates` into `classifier.sub_epic_candidates` (each becomes its own sub-epic candidate).
2. For every candidate now in the unified list, queue a backlog entry — implementation owned by #47 (likely `forge:create-epic` with `--draft` / `--deferred` semantics).
3. No code edits on the current branch. Continue to Step 7.

### Action B — fix-and-defer

1. For every `classifier.in_place_candidates` entry, apply the `fix_outline` on the current branch in this session. Each fix is a small, localized edit (≤ 30 lines, single file).
2. For every `classifier.sub_epic_candidates` entry, queue a backlog entry (deferred — no immediate spawn). Implementation owned by #47.
3. After in-place edits land → re-run Step 0b (tests-pass hard gate). Halt on fail.
4. Continue to Step 7.

### Action C — fix-and-spawn-now

1. Apply every `classifier.in_place_candidates` `fix_outline` on the current branch (same as Action B step 1).
2. Re-run Step 0b. Halt on fail.
3. For every `classifier.sub_epic_candidates` entry, spawn a new sub-epic **immediately** via `forge:create-epic` (one epic per candidate, or grouped — grouping policy owned by #47).
4. Execute spawned sub-epics? — that is a policy decision for #47 (likely user-prompt: "execute now / leave on backlog"). The shape here only commits to the **spawn**, not the execute.
5. Continue to Step 7.

## Invariants (all three actions)

- The current epic branch is preserved. No branching, no checkout.
- No commits. The user runs `forge:commit` after Step 7 (Path A merge / Path B PR) or leaves the changes uncommitted (Path C cleanup).
- The classifier output JSON is consumed read-only. The orchestrator does NOT re-call the classifier.
- If any action's in-place edit phase fails (Step 0b regression), halt with the failure snippet — do not advance to Step 7.

## What this file does NOT specify

- Which subagent applies the in-place fixes (could be one Sonnet agent per file, or a single batched pass — owned by #47).
- The exact `forge:create-epic` invocation flags for sub-epic spawn (owned by #47).
- Backlog-entry format for deferred sub-epics — depends on the tracker backend (owned by #47).
- Re-classification policy if a fix introduces new findings (out of scope for this round; future work).
