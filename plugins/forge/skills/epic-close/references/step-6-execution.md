# Step 6 execution — three-action implementation

Detailed implementation for `forge:epic-close` Step 6. Consumes the classifier output from Step 4 and the user's A / B / C choice from Step 5 (prompt + hand-off shape: [`post-tests-actions.md`](post-tests-actions.md)). Returns control to the orchestrator at Step 7 (decision tree) — except Action A, which exits at Step 6.

## Inputs

- `classifier` — the Step 4 JSON object (`in_place_candidates[]`, `sub_epic_candidates[]`, `totals`).
- `epic_ref` — the current epic's tracker ref (e.g. `IF-136`, `gh#42`).
- `epic_branch` — the current branch (e.g. `feature/forge-44-tracker-pipeline-fixes`).
- `recursion_depth` — integer, defaults to `0`. Incremented when entering a spawned sub-epic via Action C. Cap: `2` (see "Recursion cap" below).

## Action A — defer everything to sub-epic

Promote all in-place candidates into the sub-epic candidate list, then spawn ONE sub-epic that captures the full residual set.

1. Build `merged_candidates = classifier.sub_epic_candidates + classifier.in_place_candidates`. Re-tag each promoted in-place entry as a `sub_epic`-shaped item (synthesize `scope_outline` from `fix_outline` if missing; `rationale = "promoted from in-place via Action A"`).
2. Invoke `forge:create-epic` with input:
   - `parent_epic_ref = <epic_ref>`
   - `parent_branch = <epic_branch>`
   - `seed_brief` — a short paragraph: "Post-close residuals from `<epic_ref>` — classifier deferred all findings via Action A." plus a bulleted dump of `merged_candidates[].title`.
   - `candidates = merged_candidates` (the skill uses these to propose sub-issue structure)
   - `deferred = true` (skill drafts the epic but does NOT auto-execute or branch).
3. Capture the new `sub_epic_ref` printed by `forge:create-epic`.
4. **Exit Step 6.** Do NOT continue to Step 7. The current epic is intentionally not merged — the user re-runs `forge:epic-close` after the sub-epic is executed and merged back.
5. Output for the transcript (one line): `Action A → sub-epic <sub_epic_ref> queued. epic-close exits without merge.`

## Action B — fix in-place now, defer rest

1. **In-place loop.** For each `entry` in `classifier.in_place_candidates`, apply `entry.fix_outline` on `epic_branch` in this session — direct edits via Edit / Write. Localized (≤ 30 lines, single file per the classifier's guarantee). No subagent spawn — the orchestrator does the edits inline.
2. After all in-place edits land → re-run Step 0b (tests-pass hard gate: `linter-runner` + `test-runner` agents, both **`sonnet`**). On fail → halt with the failure snippet. Do NOT advance.
3. **Backlog the sub-epic candidates.** Invoke `forge:create-epic` once with input:
   - `parent_epic_ref = <epic_ref>`
   - `seed_brief` — "Post-close residuals from `<epic_ref>` — deferred via Action B."
   - `candidates = classifier.sub_epic_candidates`
   - `deferred = true` (drafted, not executed; user picks it up later).
4. Capture `sub_epic_ref`. Continue to Step 7.

If `classifier.sub_epic_candidates` is empty, skip step 3 — no sub-epic to spawn, just continue to Step 7.

## Action C — fix in-place now + spawn-execute sub-epic NOW

Action B steps 1–2, then spawn AND execute a sub-epic on a child branch, then merge it back into `epic_branch`, then resume at Step 7.

1. **In-place loop + Step 0b re-run** — identical to Action B steps 1–2. Halt on fail.
2. **Sub-epic creation.** Invoke `forge:create-epic` with input:
   - `parent_epic_ref = <epic_ref>`
   - `seed_brief` — "Post-close residuals from `<epic_ref>` — spawn-now via Action C."
   - `candidates = classifier.sub_epic_candidates`
   - `deferred = false`
   - `branch_hint = feature/<epic_ref>/postfix-<N>` where `<N>` is the next free integer (start at `1`; check `git branch --list 'feature/<epic_ref>/postfix-*'` for the highest existing suffix and increment).
3. Capture `sub_epic_ref`. `forge:create-epic` returns the sub-epic ref but does NOT switch branches itself.
4. **Sub-branch setup.** From `epic_branch`:
   ```
   git checkout -b feature/<epic_ref>/postfix-<N>
   ```
   This child branch starts from the current tip of `epic_branch` (which already contains the Action C in-place edits, uncommitted — see "Invariants" below).
5. **Execute sub-epic.** Invoke `forge:execute-epic <sub_epic_ref>` with `recursion_depth = current + 1`. The sub-epic runs its own dependency-ordered story loop, commits per ticket on the sub-branch, and finishes with its own final lint + test pass.
6. **Merge-back.** After sub-epic execution returns `done`:
   - `git checkout <epic_branch>`
   - `git merge --squash feature/<epic_ref>/postfix-<N>`
   - `git commit -m "Refs <epic_ref>: merge postfix-<N> sub-epic <sub_epic_ref>"`
   - Do NOT push — Step 7 / Path A push handles that, or Step 7 / Path B's PR flow.
   - Optionally delete the child branch: `git branch -D feature/<epic_ref>/postfix-<N>` (only after the squash commit lands).
7. **Re-run Step 0b** on `epic_branch` after the merge-back. Halt on regression.
8. **Resume.** Continue to Step 7.

If `classifier.sub_epic_candidates` is empty, Action C collapses to Action B steps 1–2 then continue to Step 7 — no child branch, no sub-epic spawn.

## Sub-branch naming convention

- Pattern: `feature/<epic_ref>/postfix-<N>`
- `<epic_ref>` — lowercased and `:` replaced with `-` (e.g. `if-136`, `gh-42`, `forge-44`).
- `<N>` — monotonically increasing integer starting at `1`. Always check existing branches before picking.
- This namespace (`/postfix-`) is reserved for Action C spawns. Do not reuse for unrelated work.

## Recursion cap

Action C can nest: the spawned sub-epic might itself surface bugs at its own `epic-close` time and ask the user for A / B / C. Allow recursion, but **cap depth at 2**.

- `recursion_depth = 0` — the original epic-close run.
- `recursion_depth = 1` — Action C spawned a sub-epic; the sub-epic's own epic-close runs.
- `recursion_depth = 2` — sub-sub-epic; this run still presents A / B / C, but **Action C is removed from the prompt**. Only A and B are offered. The user must defer rather than nest a third level.

The cap is enforced inside Step 5's prompt rendering when `recursion_depth >= 2` — strip the `C.` line and adjust the question text accordingly. The orchestrator passes `recursion_depth` to nested `forge:epic-close` invocations via the `forge:execute-epic` → final close hand-off.

## Invariants (all three actions)

- The current epic branch stays checked out at Step 6 entry. Action A and B never leave it. Action C briefly checks out a child branch, then returns.
- No commits on `epic_branch` during the in-place loop. The Action C merge-back commit is the only one Step 6 produces, and only on the parent branch after sub-epic execution completes.
- The classifier output JSON is consumed read-only. Do not re-call the classifier.
- Any in-place edit failure (Step 0b regression) halts Step 6. Do NOT advance to Step 7.
- A `forge:execute-epic` halt inside Action C bubbles up: `forge:epic-close` reports the halt reason and exits without merge-back. User resumes manually.

## Output (one line per action, into the transcript)

- A: `Action A → sub-epic <sub_epic_ref> queued. epic-close exits without merge.`
- B: `Action B → in-place fixes applied (<N>). Sub-epic <sub_epic_ref> queued (deferred). Continue to Step 7.`
- C: `Action C → in-place fixes applied (<N>). Sub-epic <sub_epic_ref> executed on feature/<epic_ref>/postfix-<N>, merged back. Continue to Step 7.`
