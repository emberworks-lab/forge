---
name: epic-close
description: Close a tracker epic via 3-option decision tree (merge / draft PR / cleanup-only). Tests-pass hard gate + simplify + docs sync + DRY comment, with the path-specific follow-ups dispatched after the user picks. Does NOT change ticket statuses or rewrite epic descriptions.
type: fundamental
---

# Epic Close

Finalize a completed epic. Tests-pass hard gate first, then the user picks one of three paths (merge / PR / cleanup), and the skill executes that path with shared follow-ups (simplify, docs, DRY comment).

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

### Step 1 — Decision tree

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

Wait for user response. No default.

### Step 2 — Execute chosen path

Full per-path step list: see [`references/path-details.md`](references/path-details.md). Summary:

- **Path A** (Merge): simplify → graph-refresh → review → ultrareview → re-test → authorization gate → squash+merge → shared follow-ups.
- **Path B** (Draft PR): simplify → graph-refresh → review → ultrareview → re-test → shared follow-ups → `forge:pr-create <EPIC-ID> --no-confirm` → append PR URL → cloud code review (post-PR, optional).
- **Path C** (Cleanup): skip simplify + graph-refresh + review + merge/PR; shared follow-ups with "abandoned" framing.

### Step 3 — Shared follow-ups

#### 3a. Simplify (Path A, B)

> "Запускаю `forge:simplify-branch` — може змінювати код напряму. ОК? (y / skip / abort)"

`y` → invoke. After: "Продовжуємо? (y / щось ще поправити)". If files changed → re-run Step 0b before merge/PR.

#### 3a.3. Graph refresh (Path A, B)

Invoke `forge:graph-refresh` inline (no user prompt — quick, idempotent, < 5s typical). The skill self-skips when `code-review-graph` is not installed or `.mcp.json` is absent; in both cases it prints a one-line skip notice and exits 0. Relay its one-line summary (e.g. `graph-refresh: 2 files updated, 41 nodes, 87 edges (3.2s)`) into the epic-close transcript so the next step has fresh graph context. Do not halt on skip.

#### 3a.6. Local review (Path A, B)

> "Запускаю `forge:review --branch` — повний епік-branch vs base, read-only. (y / skip / abort)"

`y` → invoke `forge:review --branch`. The skill returns three reviewer-agent JSON payloads plus a combined JSON blob (schema documented in the `forge:review` skill's own output-format reference under `plugins/forge/skills/review/`). Print the per-agent summary count line (e.g. `architecture-focus: 1 high, 2 medium, 0 low`) into the transcript and keep the combined JSON for the downstream classifier. `skip` → continue without findings. `abort` → halt epic-close.

<!-- forge:review output (Step 3a.6) is the input to the classifier in references/classifier-prompt.md.
     Classifier invocation + user-prompt logic is wired by EPIC B #3 (sub-epic-from-bugs). -->

#### 3a.5. Optional /ultrareview cloud audit

AskUserQuestion: "Run `/ultrareview` before PR?" — Yes (user runs, billable) / No / Already ran. On Yes: print "Run `/ultrareview` in your chat input. Type `done` when finished." Wait. Ask "Any blockers?" — yes halts; no continues. Claude Code CANNOT invoke `/ultrareview` itself.

#### 3b. Gather context (minimal)

`git log --oneline <base>...HEAD`, `git diff --stat <base>...HEAD`. **get_ticket + list_subissues via backend recipe.** Don't pre-read the project, don't pull status updates, don't fetch docs.

#### 3c. DRY comment on epic

Compare delivered vs original `## Scope` / `## Sub-issues`. Scope unchanged → don't touch description. Scope shifted → append `## Scope changes` section, do NOT rewrite original.

**post_comment via backend recipe** with `ref=<epic_ref>` and the DRY body — 3-6 bullets of human outcomes (not code changes). Exact shape: [`references/output-formats.md`](references/output-formats.md).

#### 3d. Project status update (optional)

If closing a phase / milestone, use the backend's native status update (e.g., Linear `save_status_update`). Path A → `onTrack`. Path B → `onTrack` + "PR open". Path C → `atRisk` / `offTrack` + pivot note. Skip when the epic is one of many in an ongoing phase.

#### 3e. Sync docs

Invoke `forge:kit-update-docs` (same-session, inline). Move the epic line in `docs/FEATURES.md` `## In progress` → `## Delivered` (A/B) or `## Deferred` (C), if `FEATURES.md` exists.

### Step 4 — Output

See [`references/output-formats.md`](references/output-formats.md). 3-4 lines, no celebration.

## Do NOT

- Change ticket statuses in the tracker. They close on merge automatically.
- Rewrite the epic or project description.
- Commit changes (commits go via `forge:commit` or `forge:execute-epic`).
- Set priorities, labels, cycles, assignees.
- Print a full summary to chat — the epic comment is the summary.
- Skip Step 0b tests-pass hard gate, even if `forge:execute-epic` recently passed.
- Skip the manual-test confirmation gate.
- Auto-merge (Path A) without the explicit `y` authorization.

## Edge cases

See [`references/edge-cases.md`](references/edge-cases.md).
