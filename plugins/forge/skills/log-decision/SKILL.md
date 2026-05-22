---
name: log-decision
description: Append a locked decision to docs/00_meta/decisions-log.md via a guided 30-second flow, optionally updating the design doc and glossary.
type: hybrid
---

# Log Decision

Guided flow for the moment a decision locks. First-class counterpart to `forge:update-docs` — `/log-decision` captures decisions interactively; `forge:update-docs` sweeps docs after implementation. Project-agnostic.

## Flow

### Step 1: Locate decisions-log

Search `<project>/docs/00_meta/decisions-log.md`. Fallback: `find . -name "decisions-log.md" 2>/dev/null` — if multiple hits, ask which one.

If none found: ask "No decisions-log found. Create at `docs/00_meta/decisions-log.md`? (y/n)". On y: init with minimal header. On n: abort.

### Step 2: Detect format

Read the first 120 lines of the file. Mirror the project's existing entry shape (heading separator style, field names, insert order). If the file is empty or a stub, default to the format from `docs/conventions/docs-workflow.md`:

```markdown
## YYYY-MM-DD: <title>

**Status:** ✅ FINAL
**Decision:** <one-line locked outcome>
**Rationale:** <one paragraph — why this beats alternatives>
**How to apply:** <practical guidance>
**Linked:** <ticket-id or doc ref> (optional)
```

Newest-at-top is the default insert order.

### Step 3: Interview (terse — 30-second flow)

Ask one at a time:

1. **Decision** (≤10 words): the locked outcome headline.
2. **Rationale** (1–2 sentences): why it must outlive this chat.
3. **How to apply** (1 line): practical guidance for future code/docs/work.
4. **Linear ticket?** (optional): paste ID or skip.
5. **Supersedes a prior entry?** (y/n): if y, list recent headers and ask which.
6. **New term for glossary?** (y/n): if y, ask term + one-line definition.
7. **Touches an existing design doc?** (y/n): if y, ask the path.

Today's date: read from `currentDate` system context, or `date +%Y-%m-%d` via shell.

Status emoji taxonomy from docs-workflow.md: 🟡 PROPOSED / ✅ FINAL / ❌ REJECTED / 🔄 REOPENED / 🚧 IN PROGRESS / 📋 PLANNED. Default for a locked decision: ✅ FINAL.

### Step 4: Compose and confirm

Show the entry in a fenced block. Ask: "Append this entry? (y / edit / cancel)"

### Step 5: Append to decisions-log

On y: detect insert point (newest-first → after header block, before first `## ` entry; oldest-first → end of file). Use `Edit` — never `Write`. Verify the first 30 lines after insertion.

### Step 6 (optional): Mark superseded entry

Show diff: will add `> **SUPERSEDED** by <new title> (<today>)` after the old entry's Status line. Ask confirm. On y: apply via `Edit`.

### Step 7 (optional): Update glossary

If new term provided: look for `docs/00_meta/glossary.md`. Show diff of term entry, ask confirm. If file absent: ask path or offer to create.

### Step 8 (optional): Add design-doc cross-reference

If design doc path provided: read first 60 lines to find the relevant section. Propose inserting:
`> Locked: <decision title> (decisions-log <YYYY-MM-DD>)`
Show proposed insertion, ask confirm.

### Step 9: Check project docs-workflow.md

If `docs/00_meta/docs-workflow.md` exists: read §3 (Mandatory cross-doc updates) for any additional required updates. Surface them in Step 10 summary under "Reminder per docs-workflow.md".

### Step 10: Output summary

```
Decision logged:
- decisions-log.md: + entry "<title>"
[if supersedes]  - decisions-log.md: old entry "<prior title>" marked SUPERSEDED
[if new term]    - glossary.md: + term "<term>"
[if design doc]  - <path>: cross-reference added
Reminder per docs-workflow.md: <additional steps, or "none">
```

## Constraints

- **Append-only** — never overwrite decisions-log.md. Old entries receive only the SUPERSEDED annotation.
- **Show diffs, ask confirm** before every write. No silent mutations.
- **Only touch** decisions-log.md, the chosen design doc (if any), glossary (if any), and the superseded annotation. Nothing else.
- **Project-agnostic** — detect format from existing entries; do not hardcode project-specific field names or date styles.
- On "cancel" or "n" at any prompt: stop cleanly and report what was and wasn't applied.
