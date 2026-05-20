---
name: create-ticket
description: Create a single tracker ticket from a chat brief or `docs/0X_*.md` plan; routes between three modes — A (doc-backed), B (inline, four flavours), or M (manual-setup).
type: hybrid
---

# Create Ticket

Trigger when the user says "create a ticket", "давай створимо тікет", `/create-ticket`, or passes a brief inline. Also invoked indirectly by `forge:create-epic` for each sub-issue.

At every tracker-touching step: read `<project>/.claude/tracker.json` to resolve `backend`, then execute the matching recipe section from `~/.claude/docs/tracker-backends/<backend>.md`. If `tracker.json` is missing, run the first-use setup flow per `forge:project-init --tracker-only`. After it writes `tracker.json`, resume here.

## Core principles

- **Tickets are prompts.** Whoever picks up the ticket must start work cold — using only the body + project `CLAUDE.md`.
- **Three modes, one skill.** Detect doc-backed vs inline vs manual-setup.
- **No priority / cycle / milestone by default.** Tickets close on merge.
- **Never create a tracker team.** Work within an existing team; ask if unclear.
- **Assignee = user.** Always assign to the current user.
- **Minimal tracker calls.** One `create_ticket`. Optional `ensure_labels` if needed. No follow-up reads.

## Mode detection

Pick exactly one at the start:

- **Mode A — doc-backed.** User passes a doc path, a story ID mapping to `docs/0N_*.md`, or a doc reference inline.
- **Mode B — inline.** No doc reference; user describes the work in chat. Four flavours: B-a (full inline plan, writing-plans discipline), B-b (interview-first), B-c (read-first), B-d (skill-authoring, RED-GREEN-REFACTOR).
- **Mode M — manual-setup.** The USER must do it by hand (Supabase project, OAuth app, API keys, DNS, etc.). No code work; agent waits until the user marks DONE.

Ambiguous A vs B → ask once: "Doc-backed (point at `docs/0X_*.md`) or inline (describe here)?" Mode M is usually obvious; ask if unclear.

## Flow

### 1. Load minimal context

In parallel: read repo `CLAUDE.md` (project name, prefix, conventions). If absent, infer prefix from `git log --oneline -10`. For Mode A only, also read the referenced `docs/0X_*.md` fully. For B / M, skip doc reading.

### 2A. Mode A — extract from the doc

Doc structure is fixed (per `docs/00_implementation-plan.md` §8.1): `## Goal` → ticket `## What`; `## Acceptance criteria` → ticket `## Acceptance`. No `## Steps` in the ticket — the doc IS the steps.

Body shape + backend-conditional `## Depends on`: see `references/mode-a-body.md`.

### 2B. Mode B — interview if needed, then compose

Ask up to 5 clarifying questions in ONE batch, only on real gaps. Skip questions the brief already answers. Pick the right flavour (a / b / c / d) based on what came back.

Body shapes per flavour (with templates and the writing-plans discipline for B-a, plus B-d's RED-GREEN-REFACTOR shape and rationalization counters): see `references/mode-b-bodies.md`.

If a B-a body grows past ~60 lines: stop. Tell the user "ticket body getting large — better to write `docs/<name>.md` first and switch to Mode A". Ask. If they agree, exit cleanly without creating.

### 2C. Mode M — manual-setup

Body shape with `## User actions` + `## Acceptance`: see `references/mode-m-body.md`. Mode M tickets ALWAYS get `exec:manual` label, are placed FIRST in the parent epic, get no opus/sonnet label, and block `forge:execute-epic` until DONE.

### 3. Confirm

Show the composed body in chat (one block). Ask: "ОК, створюю? або що правимо?" If the user edits — apply, show only the delta, re-ask. Loop until "ок" / "go" / "поїхали".

### 4. Ensure labels exist

**ensure_labels via backend recipe** — no-op for markdown backend. Skip this step if invoked by `forge:create-epic` (the epic flow already called `ensure_labels` once).

### 5. Create in tracker

**create_ticket via backend recipe** with:

- `type`: `task` for standalone with no `parent_ref` (default for `/create-ticket` standalone); `story` when called by `forge:create-epic` with a `parent_ref`.
- `executor`: Mode M → `exec:manual`; Mode A/B standalone → `exec:sonnet` by default unless user specified; Mode A/B from create-epic → per its classification.
- `title` — from brief.
- `body` — composed body.
- `parent_ref` — if given.

Leave status as default (Backlog/Todo). Do NOT set priority / cycle / milestone.

### 6. Output

One line:

```
Ticket: <ticket URL or ref>
```

Nothing else.

## When called by `forge:create-epic`

The parent skill passes `parent_ref`, `title`, `mode` (A / B-a / B-b / B-c / B-d / M), `executor`, plus per-mode payload (doc ref, brief, user actions list). Skip clarifying questions — the epic flow already gathered them. Compose body in the appropriate mode and create. Don't print intermediate confirmations.

## Workflow assumption (don't duplicate in tickets)

The user's git model: one branch per epic, sub-tickets land as separate commits on it, the user reviews each ticket's diff and invokes `forge:commit` OR `forge:execute-ticket` runs executor + commit pipeline. Manual testing happens after epic execution; PR creation is `forge:pr-create`. Merge to main happens at the end of the epic after `forge:epic-close` + manual verification. Ticket bodies describe **what to build**, never **how to git-handle it**.

## Do NOT

- Dump architecture diagrams, code snippets, or skill references (`/kit-create-ui`, etc.) into the body.
- Add "Test plan" / "How to test" sections. `## Acceptance` covers it (and `## Tests` exists for non-obvious test scope).
- Pre-fill priority / cycle / milestone / assignee.
- Pre-fill labels OTHER than `exec:manual` / `exec:opus` / `exec:sonnet` / `task` / `story`.
- Create a new tracker team. If undetected, ask the user which existing team to use — never offer to create one.
- Re-read `docs/` wholesale. Only the one referenced doc, if any.
- Write the ticket as a "to-do for the user" UNLESS it's Mode M.
- **Include any git workflow content in the body**: no `git checkout -b`, no branch names, no commits / commit messages, no merge / PR / push.

## Edge cases

See `references/edge-cases.md` for: doc reference missing, doc lacks `## Acceptance criteria`, no tracker team detected, brief too vague, Mode M without user-action list, `tracker.json` missing.
