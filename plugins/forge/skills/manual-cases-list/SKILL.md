---
name: manual-cases-list
description: Aggregate `## Manual test cases` comments from all sub-issues of an epic into one consolidated checklist on the epic.
type: hybrid
---

# Manual Cases List

Trigger: `/manual-cases-list EMB-247`, `/manual-cases-list FORGE-1`, "give me all manual cases for EMB-248", "зведи мануальні тест-кейси для FORGE-2".

On-demand counterpart to `forge:execute-epic` Step 7. Read-only on sub-issues; never generates new test cases.

## Core principles

- **Read-only on sub-issues.** Never modify sub-issues or their statuses.
- **Aggregation only.** Extract existing `## Manual test cases` blocks; never write new ones.
- **Idempotency warning.** Warn the user before posting if a prior aggregation comment exists on the epic.
- **Clean output.** Omit sub-issues with no test cases from the output.

## Inputs

`$ARGUMENTS` — required. Epic identifier (`EMB-247`, `FORGE-1`, etc.). Optional flags: `--post` (post aggregated comment on epic), `--save` (write to `manual-cases-<id>.md`).

## Steps

### 1. Parse and resolve epic ref

Split `$ARGUMENTS` on whitespace. Identify the epic ID token (`[A-Z]+-\d+` or `FORGE-\d+`). Collect flags.

No epic ID found → "Usage: /manual-cases-list <epic-id> [--post] [--save]" and stop.

`FORGE-N` alias: resolve via the backend recipe — **get_ticket** or project-list lookup for an issue whose title begins with `FORGE-<N> —`; use the resolved ref. Not found → tell user and stop.

### 2. Tracker bootstrap

Read `<project>/.claude/tracker.json` → `backend`. If missing, prompt `[linear | github | markdown]`, run `setup_interview`, write `tracker.json`, continue. Read `~/.claude/docs/tracker-backends/<backend>.md` for all recipe ops below.

### 3. Fetch epic + sub-issues

**get_ticket(epic_ref)** — extract `id`, `title`. Not found → tell user and stop.

**list_subissues(epic_ref)** → list of `ticket_ref`. Empty → "Epic has no sub-issues." and stop.

### 4. Collect test cases from each sub-issue

For each sub-issue: **get_ticket(ref)** for title; then scan comments (use the backend comment-read op). For each comment, extract the `## Manual test cases` block: find the heading (case-insensitive, allow trailing parenthetical), collect subsequent bullet lines (`- ` or `* `) until the next `##` heading or end-of-comment. Merge bullets from multiple comments on the same sub-issue; de-duplicate identical lines. Sub-issues with no matching bullets are silently omitted.

No sub-issue contributed any cases → "No `## Manual test cases` blocks found in any sub-issue of <id>." and stop.

### 5. Compose output

Match execute-epic Step 7 shape:

```
## Manual test cases (epic <EPIC-ID>)

### <SUB-REF> — <title>
- <case>

### <SUB-REF> — <title>
- <case>
```

Always print to chat.

### 6. Optional actions

**`--save`:** write to `<cwd>/manual-cases-<epic-id>.md`; confirm filename.

**`--post`:** check existing comments on epic for any body starting with `## Manual test cases (epic`; if found → warn "A prior aggregation comment exists on <id> (posted <createdAt>). Post another? (y/n)" and wait. On `n` → done. On `y` (or no prior comment) → **post_comment(epic_ref, body)** via backend recipe; confirm.

## Do NOT

- Change any tracker ticket status or body
- Post a comment on sub-issues — only on the epic (with `--post`)
- Generate new test cases not present in existing comments
- Post the aggregated comment twice without user confirmation
