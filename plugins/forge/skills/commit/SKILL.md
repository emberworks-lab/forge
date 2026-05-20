---
name: commit
description: Create a git commit linked to a tracker ticket via magic words; dispatches to the configured backend (linear/github/markdown) via tracker.json, with fallback to legacy Linear prefix detection.
type: hybrid
---

# Commit

Trigger: `/commit`, `/commit 42`, "закомить EMB-42", or invoked by `forge:execute-ticket` / `forge:execute-epic` at per-ticket commit time.

Create a git commit whose subject auto-links to a tracker ticket via the backend's magic-word phrase. Backend-aware: `linear`, `github`, `markdown`. Legacy fallback exists for repos that haven't been migrated to `tracker.json` yet.

## Core principles

- **One commit per ticket.** Magic word in subject → tracker auto-closes on PR merge to default.
- **Backend dispatches phrase shape.** Never hardcode `EMB-` or `#N` — read `tracker.json` once, then ask the backend recipe.
- **Stage explicitly.** Never `git add -A` blindly; skip anything that smells like a secret.
- **Co-author footer matches the running model.** Per `~/.claude/docs/conventions/git-workflow.md`.

## Dispatch — read tracker.json once

At the start of the flow, attempt to read `<project-root>/.claude/tracker.json` (the working repo's root, not `~/.claude/`).

- File present → parse, capture `backend` (`linear` | `github` | `markdown`) + the backend-specific config block. Use this through the rest of the flow.
- File missing → run the **first-use hook** (Step 0) before Step 1.

## Flow

### Step 0 — First-use hook (only if `tracker.json` missing)

Ask: "Set up `tracker.json` now? (y/n)"

- `y` → run the tracker setup flow from `forge:project-init --tracker-only`. After it writes `tracker.json`, resume from Step 1 (dispatched path) with the resolved backend.
- `n` → fall through to **legacy fallback** in Step 1 (detect Linear prefix from git log / CLAUDE.md; keep existing Linear repos working without disruption).

### 1. Determine tracker context

**If `tracker.json` is present** (dispatched path), branch on `backend`:

| Backend | Ref shape | Example |
|---|---|---|
| `linear` | `<PREFIX>-<N>` (prefix from `tracker.json` → `linear.prefix`) | `EMB-42` |
| `github` | plain issue number | `123` |
| `markdown` | slug | `forge-8/001-tracker-contract` |

**If `tracker.json` is missing** (legacy fallback): detect the project prefix in order — (1) prefix from a user-provided ticket ID; (2) recent git log (`git log --oneline -10`) for `IF-` / `ENG-` / `DES-` / `EMB-` / etc; (3) CLAUDE.md mention; (4) ask the user. The rest of the flow uses the same shape as the `linear` dispatched path.

### 2. Gather context (parallel)

- `git status` — what is staged vs unstaged.
- `git diff --cached` — staged changes.
- `git diff` — unstaged changes.
- `git log --oneline -5` — recent commits for style reference.

### 3. Ask for the ticket reference

If the user didn't provide a ref in the invocation, ask using the backend-aware question:

| Backend | Question |
|---|---|
| `linear` (dispatched) | "Which ticket number? (just the number, e.g. `42` — prefix `<prefix>` from tracker.json)" |
| `github` | "Which issue number? (e.g. `123`)" |
| `markdown` | "Which ticket slug? (e.g. `forge-8/001-tracker-contract`)" |
| legacy fallback | "Which ticket number? (e.g. `42`)" |

Also show a one-line summary of what will be committed (files changed + key modifications).

### 4. Determine the commit kind

Infer from the staged changes:

| Change nature | Kind |
|---|---|
| New feature / completing an implementation | `implements` |
| Bug fix (ticket is a defect / regression report) | `fixes` |
| Partial work, refactor, docs-only, leave ticket open | `refs` |

If unclear, ask. Rubric notes + per-backend mappings: see `references/magic-words.md`.

### 5. Compose the commit message via backend recipe

**If `tracker.json` is present:** read `~/.claude/docs/tracker-backends/<backend>.md`, locate `## commit_close_phrase`, apply it with the chosen `ref` and `kind`. The recipe returns the magic-word phrase string.

**Legacy fallback** (no `tracker.json`): build the phrase directly with the detected prefix — `Implements <PREFIX>-<N>` / `Fixes <PREFIX>-<N>` / `Refs <PREFIX>-<N>`.

Compose the subject:

```
<phrase>: <short description>
```

Rules:

- Magic word capitalized as shown.
- Description lowercase, concise, one line, no period.
- Multiple tickets → list them: `Implements EMB-42, EMB-43: description`.

Examples + per-backend phrase table: see `references/magic-words.md`.

### 6. Stage files and commit

Stage relevant files by path (never `git add -A`). Refuse anything that looks like a secret (`.env`, credentials, keys). Create the commit with the composed subject and the co-author footer matching the running model (per `~/.claude/docs/conventions/git-workflow.md`, format `Co-Authored-By: <Model name> <noreply@anthropic.com>`). Run `git status` after to verify.

## Do NOT

- Push the commit. That's `forge:pr-create` or the user.
- Skip the backend dispatch and hardcode `EMB-` or `#N` — `tracker.json` is the source of truth.
- Stage files that look like secrets even when the user asks "just commit everything".
- Invent a ticket reference. If detection fails and the user can't provide one, halt cleanly.
- Combine work that belongs to different tickets into one commit. One ticket per commit.

## Edge cases

See `references/edge-cases.md` for: ref-resolution failures, mixed staged-and-unstaged state, backend mismatch between `tracker.json` and the ref shape the user typed, multi-ticket commits.
