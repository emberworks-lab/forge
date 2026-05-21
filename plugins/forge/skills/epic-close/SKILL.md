---
name: epic-close
description: Close a tracker epic via simplify → residuals → review → classifier → 3 actions → decision tree. Tests-pass hard gate + simplify + review run BEFORE the merge/PR/cleanup decision. Does NOT change ticket statuses or rewrite epic descriptions.
type: fundamental
---

# Epic Close

Finalize a completed epic. Tests-pass hard gate first, then simplify + review run on the clean branch, a classifier sorts findings into in-place vs sub-epic, the user picks one of 3 actions on those findings, and only then does the user pick the merge / PR / cleanup path. Path-specific follow-ups (DRY comment, docs, PR creation) execute last.

At every tracker-touching step: read `<project>/.claude/tracker.json` → `backend`; execute the matching recipe section from `plugins/forge/docs/tracker-backends/<backend>.md`. Fallback: if `tracker.json` is missing, fall back to legacy Linear-MCP behavior — phased out in a future cleanup epic.

## Trigger & epic detection

`/epic-close IF-136` (ID or URL), or "закриваємо епік" with detect-from-branch-name (`feature/if-XX-name` → `IF-XX`). Ask once if both fail.

## Flow

### Step 0 — Preflight (halt on first failure)

#### 0a. Git state

`git rev-parse --abbrev-ref HEAD` (confirm on epic branch). Resolve `<base>` (`develop` if local, else `main`). `git status --short` — on a dirty tree, prompt "Незакомічені зміни: <list>. (commit / stash / abort)" and wait. Do NOT proceed dirty.

#### 0b. Tests-pass hard gate (REQUIRED)

Iron Law: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE. Re-run, don't trust prior runs.

- Spawn `linter-runner` agent (`mode=report`, no path filter) — model **`sonnet`**.
- Spawn `test-runner` agent (`mode=report`, full suite) — model **`sonnet`**.

Read agent outputs in this turn. If either fails:

> "EMB-X tests-pass gate FAILED. Lint: <count> / Tests: <count>. Snippet: <first failure>. No close actions until clean. Fix and re-run, OR `/execute-epic --start-from <ticket>`."

Halt. If both pass → continue.

#### 0c. Manual-test confirmation

> "Manual test cases для епіка `<EPIC-ID>` пройдені вручну? (y / not yet)"

`not yet` → exit cleanly. `y` → continue.

### Step 1 — Simplify branch

Simplify BEFORE review so reviewers see the cleaner code.

> "Запускаю `forge:simplify-branch` — може змінювати код напряму. ОК? (y / skip / abort)"

`y` → invoke `forge:simplify-branch`. After: "Продовжуємо? (y / щось ще поправити)". If files changed → re-run Step 0b before continuing. `skip` → continue without simplify. `abort` → halt epic-close.

Capture the simplify-residuals list (issues simplify could not apply inline) for Step 4.

### Step 2 — Residuals prompt

If Step 1 returned simplify residuals (issues simplify flagged but did not auto-apply), present them:

```
Simplify лишив <N> residuals:
  1. <file:line> — <one-line title>
  2. ...

Виправити? (all / none / per-item)
```

- `all` → apply every residual inline now. After edits → re-run Step 0b. Halt on fail.
- `none` → keep residuals; they flow into Step 4 classifier input as `simplify_residuals[]`.
- `per-item` → walk the list one by one, asking `fix / skip / abort` for each. Unfixed items flow into Step 4.

If Step 1 was `skip` or returned no residuals → skip Step 2 silently.

### Step 3 — Graph refresh + review + optional ultrareview

#### 3a. Graph refresh

Invoke `forge:graph-refresh` inline (no user prompt — quick, idempotent, < 5s typical). The skill self-skips when `code-review-graph` is not installed or `.mcp.json` is absent; in both cases it prints a one-line skip notice and exits 0. Relay its one-line summary into the transcript so review has fresh context. Do not halt on skip.

#### 3b. Local review (3 agents)

> "Запускаю `forge:review --branch` — повний епік-branch vs base, read-only. (y / skip / abort)"

`y` → invoke `forge:review --branch`. The skill returns three reviewer-agent JSON payloads plus a combined JSON blob (schema documented in the `forge:review` skill's own output-format reference under `plugins/forge/skills/review/`). Print the per-agent summary count line (e.g. `architecture-focus: 1 high, 2 medium, 0 low`) into the transcript and keep the combined JSON for Step 4. `skip` → continue without findings (classifier input will be empty for review). `abort` → halt epic-close.

#### 3c. Optional /ultrareview cloud audit

AskUserQuestion: "Run `/ultrareview` before merge/PR?" — Yes (user runs, billable) / No / Already ran. On Yes: print "Run `/ultrareview` in your chat input. Type `done` when finished." Wait. Ask "Any blockers?" — yes halts; no continues. Claude Code CANNOT invoke `/ultrareview` itself. If ultrareview findings exist, merge them into Step 4 classifier input under `review_findings` (treat as an extra `agent` source).

### Step 4 — Opus classifier hand-off

Merge the Step 3b combined review JSON and the Step 2 unfixed simplify residuals into the classifier input object (schema: [`references/classifier-prompt.md`](references/classifier-prompt.md) input contract). Spawn one **opus** subagent with the verbatim prompt from [`references/classifier-prompt.md`](references/classifier-prompt.md). Capture its single-JSON-object output.

Validate: output parses as JSON, `totals.in_place` and `totals.sub_epic` equal the lengths of their arrays. If validation fails → re-spawn once with the same input; if it fails again → halt with the raw output for debug.

If `totals.in_place == 0 && totals.sub_epic == 0` → skip Steps 5 and 6, jump straight to Step 7.

<!-- This hand-off shape is defined here in #46. Step 5/6 detailed implementation
     lives in this skill, contributed by EPIC B #3 / ticket #47. -->

### Step 5 — 3-action user prompt

Present the user with three actions over the classifier output. Exact prompt copy and decision matrix: [`references/post-tests-actions.md`](references/post-tests-actions.md).

```
A. Все в sub-epic (defer everything to backlog)
B. Виправити in-place зараз, sub-epic — у backlog (deferred)
C. Виправити in-place зараз + sub-epic СПАВНИТИ ЗАРАЗ (виконати негайно)
```

No default. Wait for explicit `A` / `B` / `C`.

### Step 6 — Execute selected action

Full implementation, sub-branch naming, and recursion cap: [`references/step-6-execution.md`](references/step-6-execution.md). Per-action hand-off shape (Step 5 prompt contract): [`references/post-tests-actions.md`](references/post-tests-actions.md).

- **Action A** — promote all `in_place_candidates` into `sub_epic_candidates`, invoke `forge:create-epic` with `deferred=true`, then **exit Step 6** (no merge, skip Step 7).
- **Action B** — apply `in_place_candidates` fixes inline, re-run Step 0b, invoke `forge:create-epic` with `deferred=true` for `sub_epic_candidates`, continue to Step 7.
- **Action C** — apply `in_place_candidates` fixes inline, re-run Step 0b, invoke `forge:create-epic` with `deferred=false` + `branch_hint=feature/<epic_ref>/postfix-<N>`, invoke `forge:execute-epic` on the new sub-epic, squash-merge the postfix branch back into the epic branch, re-run Step 0b, continue to Step 7.

Invariants: stay on the epic branch except for the Action C child-branch round-trip; no commits except the Action C merge-back; halt on any Step 0b regression. Recursion (Action C spawning a sub-epic that itself triggers Action C) is capped at depth 2 — the third level strips `C` from the Step 5 prompt.

### Step 7 — Decision tree (merge / draft PR / cleanup)

**get_ticket via backend recipe** + **list_subissues via backend recipe** for current state. Present:

```
Epic <EPIC-ID> ready to close. Pick a path:
  A. Merge to <base> (squash + merge, requires authorization)
  B. Open draft PR (preferred for review-needing changes)
  C. Cleanup only (abandon — leave branch for later revisit)

Pick A / B / C.
```

| Option | When |
|---|---|
| **A** | Tests pass, manual ✓, no PR review, low-risk |
| **B** | Want review / CI / delay merge, risky/large/cross-cutting |
| **C** | Manual testing or stakeholder review revealed issues — abandon |

Wait for user response. No default. Per-path step list: [`references/path-details.md`](references/path-details.md).

### Step 8 — Shared follow-ups

#### 8a. Gather context (minimal)

`git log --oneline <base>...HEAD`, `git diff --stat <base>...HEAD`. **get_ticket + list_subissues via backend recipe.** Don't pre-read the project, don't pull status updates, don't fetch docs.

#### 8b. DRY comment on epic

Compare delivered vs original `## Scope` / `## Sub-issues`. Scope unchanged → don't touch description. Scope shifted → append `## Scope changes` section, do NOT rewrite original.

**post_comment via backend recipe** with `ref=<epic_ref>` and the DRY body — 3-6 bullets of human outcomes (not code changes). Exact shape: [`references/output-formats.md`](references/output-formats.md).

#### 8c. Project status update (optional)

If closing a phase / milestone, use the backend's native status update (e.g., Linear `save_status_update`). Path A → `onTrack`. Path B → `onTrack` + "PR open". Path C → `atRisk` / `offTrack` + pivot note. Skip when the epic is one of many in an ongoing phase.

#### 8d. Sync docs

Invoke `forge:kit-update-docs` (same-session, inline). Move the epic line in `docs/FEATURES.md` `## In progress` → `## Delivered` (A/B) or `## Deferred` (C), if `FEATURES.md` exists. If `docs/owner-overview.md` exists, `forge:kit-update-docs` MUST also refresh Features.Shipped, Features.In-progress, and Phases — see policy in `plugins/forge/CLAUDE.md § Owner overview update on epic close`.

### Step 9 — Output

See [`references/output-formats.md`](references/output-formats.md). 3-4 lines, no celebration.

## Do NOT

- Change ticket statuses in the tracker. They close on merge automatically.
- Rewrite the epic or project description.
- Commit changes (commits go via `forge:commit` or `forge:execute-epic`).
- Set priorities, labels, cycles, assignees.
- Print a full summary to chat — the epic comment is the summary.
- Skip Step 0b tests-pass hard gate, even if `forge:execute-epic` recently passed.
- Skip the manual-test confirmation gate.
- Run simplify or review AFTER the merge/PR decision — both run BEFORE (Steps 1, 3).
- Auto-merge (Step 7 Path A) without the explicit `y` authorization.

## Edge cases

See [`references/edge-cases.md`](references/edge-cases.md).
