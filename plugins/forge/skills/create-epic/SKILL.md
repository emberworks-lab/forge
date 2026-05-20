---
name: create-epic
description: Draft a tracker epic plus its sub-issues from a chat brief; interview, propose structure, then create on confirmation with dependency links.
type: hybrid
---

# Create Epic

Trigger when the user says "let's create an epic", "давай створимо епік", `/create-epic`, or passes a description inline.

At every tracker-touching step: read `<project>/.claude/tracker.json` to resolve `backend`, then execute the matching recipe section from `~/.claude/docs/tracker-backends/<backend>.md`. If `tracker.json` is missing, run the first-use setup flow per `forge:project-init --tracker-only`. After it writes `tracker.json`, resume here.

For GitHub backend, run multi-repo detection once — see `references/multi-repo-detection.md`.

## Core principles

- **The user is the source of truth.** Skill guides and proposes; never invents scope.
- **Minimal chat output.** End with the epic URL only — no drafts the user already saw.
- **No priority / cycle / milestone games.** Don't set them. Tickets close on merge. Cycles and milestones are strictly opt-in.
- **Never create a tracker team.** Always work within an existing team. If unclear, ask the user which one.
- **Assignee = current user** for epic and sub-issues. User can reassign manually.
- **Tickets are high-level.** Implementation agents read CLAUDE.md and ask clarifying questions at exec time. Don't dump architecture into bodies.
- **Pre-populate execution metadata.** Each sub-issue gets `exec:opus` / `exec:sonnet`; manual-setup steps get `exec:manual`.

## Flow

### Step 0 — Brainstorming gate (REQUIRED for non-trivial epics)

For any epic that's NOT pure infra / docs / config, invoke `forge:brainstorm` first. The gate:

> Do NOT draft tracker tickets, write any code, or take any implementation action until the user has approved a design. Brainstorm output (the design spec) becomes the source for the epic body.

Skip the gate ONLY for documentation-only epics, pure renaming / cleanup, manual-setup epics (`exec:manual`), or FORGE-style infra/tooling targeting `~/.claude/`. If the user explicitly says "skip brainstorm" / "пропускаємо brainstorm" — respect that and proceed.

When invoking brainstorm: pass the brief as starting prompt. Spec lands at `<project>/docs/superpowers/specs/<date>-<topic>-design.md`. Use it as primary input to Step 3 + 4.

### 1. Load context (cheap, once)

Read `CLAUDE.md` first — project name, prefix, skills, conventions. Look for an explicit master/index doc pointer. If named, read that too. If silent, ask the user once: "Is there a master doc (FEATURES, roadmap, master plan)? Path?" Don't preload `docs/*.md` wholesale.

### 2. Absorb the brief

The user either pastes the description inline, has described it earlier, or says "let's create an epic" with nothing — then ask for a 2-3 sentence seed.

### 3. Ask clarifying questions — in batch, not drip

Ask ≤6 questions, all at once, only on real gaps. Typical gaps (project-type-agnostic):

- Visible outcome / behavior change?
- In scope vs explicitly out?
- Design or spec artifacts to attach? (Figma URL, mockup, `*.md`, ADR/RFC, sequence diagram — any combination, or none.)
- Anything shipped this extends / replaces?
- Rough size — 3 sub-issues or 8?
- Any manual user-only prerequisites? (Supabase project, API keys, OAuth app, DNS — anything the user must do by hand BEFORE code work.)

Skip questions the brief already answers. Don't force a UI frame if the work has no UI.

### 4. Propose the structure

Show in chat, ONE compact block — epic title, epic body (required: `## What`, `## Acceptance`; optional sections only when relevant), then a bulleted sub-issue list with mode + executor tags.

Body sections + sub-issue list format + numbering rule + executor tag rubric: see `references/proposal-shape.md`.

Size rule: **3–8 sub-issues.** More than 8 → propose splitting. (Exception: scaffold epic with pre-written `docs/0X_*.md` per sub-issue may grow to 13.)

### 5. Confirm

Ask once: "ОК, створюю? або що правимо?" If the user edits — apply, show only the delta, re-ask. Loop until "go" / "ок поїхали".

### 6. Create in tracker

Order of operations (minimize round-trips):

1. **ensure_labels via backend recipe** — once. Required labels: `epic`, `story`, `task`, `bug`, `exec:opus`, `exec:sonnet`, `exec:manual`.
2. **create_ticket via backend recipe** — create the epic (`type=epic`, `executor=exec:sonnet` typically, no `parent_ref`). Capture `epic_ref`.
3. For each sub-issue: compose body per `forge:create-ticket` mode conventions, then **create_ticket via backend recipe** with `type=story`, executor label, `parent_ref=<epic_ref>`, and (multi-repo only) `area=<area-repo-name>`. Titles already prefixed `E<N>.<idx>:` if the epic title matched the numbering pattern. Capture each `sub_ref`. Skip clarifying questions per sub-issue — the epic flow already gathered them.
4. After all sub-issues exist, silently **link_dependency via backend recipe** where you can clearly infer relations from ordering, content, or `## Depends on` blocks. **Only when confident** — never ask the user to confirm relations. Manual-setup tickets implicitly block all non-manual sub-issues; set this explicitly for the first non-manual sub-issue (chain follows).
5. If `backend == markdown`, write the `## Sub-issues` block back into the epic body with real refs (manual-setup first). For `github` and `linear`, skip — native UI surfaces sub-issues.

### 7. Output

Single line to chat:

```
Epic: <epic URL>
```

Nothing else. No summary, no file tree, no "here's what I did".

## Sub-issue body templates

See `references/sub-issue-templates.md` for Mode A / B-a / B-b / B-c / M body shapes and where design references attach.

## Executor selection rubric

See `references/executor-rubric.md` for the detailed `[opus]` vs `[sonnet]` decision. Default `[sonnet]` if uncertain.

## Do NOT

- Write a Claude Code prompt into the ticket. The ticket IS the prompt.
- Add "Test plan" / "How to test" sections — `## Acceptance` covers it.
- Dump code, architecture diagrams, or skill references (`/kit-create-ui`, etc.) into tickets. That lives in CLAUDE.md.
- Add ticket titles after the link in the sub-issues list. Just `- <ref>`.
- Create a git branch. That's the user's call (or `forge:execute-epic` at exec start).
- **Include any git workflow content in any ticket body** (epic or sub-issue): no branch names, no `git checkout -b`, no commits, no commit messages, no PR / merge / push steps.
- Set priority / cycle / milestone / estimate / assignees unless explicitly asked.
- Create a new tracker team. If unclear, ask which existing team to use.
- Set labels OTHER than `exec:manual`, `exec:opus`, `exec:sonnet`, `epic`, `story`.
- Re-read `docs/` wholesale.
