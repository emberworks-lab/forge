# Markdown backend recipe

**Backend:** `markdown`
**Status:** Implemented (FORGE-8 Story 4 / EMB-331)
**Dispatch key:** `tracker.json` → `"backend": "markdown"`

This is the fallback backend for projects without a structured tracker (no Linear, no GitHub Projects). All state lives in local `.md` files with YAML frontmatter. There is no remote state — no auto-close, no label registry, no API calls.

---

## File layout

```
<directory>/                          # default: docs/00_meta/manual-tracker
  <epic-slug>/
    epic.md                           # epic file
    001-<sub-slug>.md                 # sub-issues, NNN sequential for ordering
    002-<sub-slug>.md
    ...
  <standalone-task-slug>.md           # tickets without a parent live flat at root
```

`<directory>` is read from `tracker.json` → `markdown.directory` (relative to project root).

---

## Frontmatter schema

All ticket files use this YAML frontmatter block at the top:

```yaml
---
id: <slug>                            # epic slug, OR <epic-slug>/<NNN>-<sub-slug>
type: epic | story | task | bug
executor: opus | sonnet | manual
parent: <epic-slug>                   # only for sub-issues; omit for epics and standalones
status: backlog                       # backlog | in-progress | done — NOT updated by skills
depends_on: []                        # array of ticket ids (same format as id field)
---
```

**Important:** Skills never write to the `status` field. The user manages status manually (edit frontmatter, archive folder, or delete file when done). See the "No auto-close" edge case in `commit_close_phrase` below.

---

## setup_interview

**Inputs:**
- None required. One optional question: `directory`.

**Recipe:**

1. Ask the user:
   ```
   Where should markdown tickets live? (default: docs/00_meta/manual-tracker)
   Press Enter to accept the default.
   ```
2. Capture the answer. If blank, use `docs/00_meta/manual-tracker`.
3. Write (or update) `.claude/tracker.json` in the project root:
   ```json
   {
     "backend": "markdown",
     "markdown": {
       "directory": "<answer>"
     }
   }
   ```
   If `tracker.json` already exists and has other backend sections (e.g. `linear`), preserve them — only set `backend` and `markdown` keys.

**Output:** `tracker.json` written. Skill continues.

**Edge cases / fallbacks:**
- If the user types a path with a leading `/` (absolute), accept it as-is — this is unusual but not invalid.
- If `tracker.json` already has `"backend": "markdown"` with a different directory, overwrite with the new answer.
- The directory does not need to exist at setup time. `create_ticket` creates it on first use.

---

## ensure_labels

**This operation is a NO-OP for the markdown backend.**

Labels live in the `type` and `executor` frontmatter fields of each ticket file. There is no global label registry to create or verify.

**Recipe:**

Return success immediately. Do not create any files or prompt the user.

**Output:** Success. Skill continues without any action.

**Note:** The label model (type axis + executor axis) is still enforced at write time — `create_ticket` always writes `type` and `executor` into frontmatter. This op is simply not needed to pre-populate anything.

---

## create_ticket

**Inputs:**
- `type` — `epic | story | task | bug`
- `executor` — `exec:opus | exec:sonnet | exec:manual` (stored in frontmatter as `opus | sonnet | manual`, stripping the `exec:` prefix)
- `title` — string
- `body` — markdown string (ticket description, placed after frontmatter)
- `parent_ref` — optional slug string (e.g. `forge-8`)

**Recipe:**

**Step 1 — Compute slug:**
```
slug = title.downcase()
     .replace(/[^a-z0-9]+/g, '-')   # replace non-alphanumeric runs with -
     .replace(/^-+|-+$/g, '')        # strip leading/trailing -
```
Example: `"Tracker Contract (Draft)"` → `tracker-contract-draft`

**Step 2 — Resolve directory:**
Read `tracker.json` → `markdown.directory`. All paths below are relative to project root.

**Step 3a — Epic (type=`epic`, no parent_ref):**
```bash
mkdir -p <directory>/<slug>/
```
Write `<directory>/<slug>/epic.md`:
```markdown
---
id: <slug>
type: epic
executor: <opus|sonnet|manual>
status: backlog
depends_on: []
---

# <title>

<body>
```
Return ref: `<slug>`

**Step 3b — Sub-issue (parent_ref is set):**
1. List existing files matching `<directory>/<parent_ref>/[0-9][0-9][0-9]-*.md` (exclude `epic.md`).
2. Extract the NNN prefix from each filename (e.g. `001`, `002`). Take the highest and add 1. If none exist, NNN = `001`.
3. Zero-pad to 3 digits.
4. Ensure the parent directory exists: `mkdir -p <directory>/<parent_ref>/`
5. Write `<directory>/<parent_ref>/<NNN>-<slug>.md`:
```markdown
---
id: <parent_ref>/<NNN>-<slug>
type: <story|task|bug>
executor: <opus|sonnet|manual>
parent: <parent_ref>
status: backlog
depends_on: []
---

# <title>

<body>
```
Return ref: `<parent_ref>/<NNN>-<slug>`

**Step 3c — Standalone task/bug (no parent_ref, type=`task` or `bug`):**
```bash
mkdir -p <directory>/
```
Write `<directory>/<slug>.md`:
```markdown
---
id: <slug>
type: <task|bug>
executor: <opus|sonnet|manual>
status: backlog
depends_on: []
---

# <title>

<body>
```
Return ref: `<slug>`

**Output:** `ticket_ref` string — one of:
- `<slug>` for epics and standalone tasks/bugs
- `<parent_ref>/<NNN>-<slug>` for sub-issues

**Edge cases / fallbacks:**
- If a file at the computed path already exists, do NOT overwrite. Surface the conflict: `"Ticket file already exists: <path>. Chose a different title or rename the existing file."` Halt this op.
- Slug collision on standalone tickets: same as above — surface conflict.
- `executor` value arrives as `exec:opus` / `exec:sonnet` / `exec:manual` from the skill — strip the `exec:` prefix before writing to frontmatter.
- If `parent_ref` is set but `<directory>/<parent_ref>/epic.md` does not exist, write a warning in chat (`"Parent epic '<parent_ref>' has no epic.md — creating sub-issue anyway"`) but continue.

---

## link_dependency

**Inputs:**
- `blocker_ref` — ticket id of the upstream ticket (e.g. `forge-8`, `forge-8/001-tracker-contract`)
- `blocked_ref` — ticket id of the downstream ticket

**Recipe:**

1. Resolve the file path for `blocked_ref`:
   - If `blocked_ref` contains `/` → it is a sub-issue: `<directory>/<blocked_ref>.md`
   - Otherwise check: if `<directory>/<blocked_ref>/epic.md` exists → path = `<directory>/<blocked_ref>/epic.md`; else path = `<directory>/<blocked_ref>.md`
2. Read the file using the Read tool.
3. Parse the YAML frontmatter. Find the `depends_on` array.
4. Check if `blocker_ref` is already in `depends_on`. If yes, return success immediately (idempotent).
5. Append `blocker_ref` to the `depends_on` array.
6. Write the updated frontmatter back to the file using the Edit tool — replace only the `depends_on:` line (or the full YAML block if needed to preserve formatting).

**Output:** File updated. `depends_on` array now includes `blocker_ref`.

**Edge cases / fallbacks:**
- `blocked_ref` file not found: surface error `"Cannot link dependency — ticket file not found: <path>"`. Halt.
- `blocker_ref` file not found: do NOT halt. The blocker may not yet exist in the filesystem. Write the ref to `depends_on` anyway and emit a warning: `"Blocker '<blocker_ref>' file not found — dependency recorded as text reference."`.
- Malformed frontmatter: surface error and halt.

---

## get_ticket

**Inputs:**
- `ref` — ticket id string (e.g. `forge-8`, `forge-8/001-tracker-contract`, `my-bug`)

**Recipe:**

1. Resolve the file path for `ref`:
   - If `ref` contains `/` → sub-issue: path = `<directory>/<ref>.md`
   - Otherwise check if `<directory>/<ref>/epic.md` exists:
     - Yes → path = `<directory>/<ref>/epic.md`
     - No → path = `<directory>/<ref>.md`
2. Read the file using the Read tool.
3. Split on the second `---` to separate YAML frontmatter from body.
4. Parse frontmatter fields:
   - `type` → returned as-is (`epic | story | task | bug`)
   - `executor` → prefix with `exec:` when returning to caller (stored as `opus/sonnet/manual`, returned as `exec:opus/exec:sonnet/exec:manual`)
   - `status` → returned as-is
   - `parent` → returned as `parent_ref` (or `null` if field absent)
5. Body = all content after the closing `---`, trimmed.
6. Title = first `# Heading` line in the body, stripped of `# `.

**Output:**
```
{
  title:      string,
  body:       string (full markdown body including the # heading),
  type:       "epic" | "story" | "task" | "bug",
  executor:   "exec:opus" | "exec:sonnet" | "exec:manual",
  status:     string,
  parent_ref: string | null
}
```

**Edge cases / fallbacks:**
- File not found: surface error `"Ticket not found: <path>"`.
- `type` or `executor` missing from frontmatter (pre-dates label model): return `null` for that field. Calling skills should treat `null` as unknown and not crash — they should warn the user.
- Body has no `# Heading`: return `title: null` and the full body as-is.

---

## list_subissues

**Inputs:**
- `epic_ref` — slug of the epic (e.g. `forge-8`)

**Recipe:**

1. Resolve directory: `<directory>/<epic_ref>/`.
2. Check if the directory exists. If not, return `[]`.
3. Glob pattern: `<directory>/<epic_ref>/[0-9][0-9][0-9]-*.md`
   - The pattern `[0-9][0-9][0-9]-` explicitly targets only NNN-prefixed files.
   - `epic.md` does NOT match this pattern and is excluded automatically.
   - Other non-NNN files (if any) are also excluded.
4. Sort results by filename (lexicographic = numeric order due to zero-padded NNN).
5. For each matched path, extract the basename without extension and return as: `<epic_ref>/<basename>`.
   - Example: `docs/00_meta/manual-tracker/forge-8/001-tracker-contract.md` → ref = `forge-8/001-tracker-contract`

**Output:** Array of `ticket_ref` strings, sorted by filename. Empty array `[]` if no sub-issues exist.

**Edge cases / fallbacks:**
- Epic directory does not exist: return `[]` (not an error — the epic may have just been created with no sub-issues yet).
- Directory exists but contains only `epic.md` (or files not matching the glob): return `[]`.
- Glob returns files in arbitrary OS order: always sort by filename before returning to guarantee stable ordering.

---

## post_comment

**Inputs:**
- `ref` — ticket id string
- `body` — markdown string to append as a comment

**Recipe:**

1. Resolve the file path using the same logic as `get_ticket` step 1.
2. Get the current UTC timestamp:
   ```bash
   date -u +"%Y-%m-%d %H:%M"
   ```
3. Read the file using the Read tool.
4. Check if the file contains a `## Comments` section (search for `\n## Comments\n` or `\n## Comments` at end of file).
5a. If `## Comments` section exists: append the new comment block after the last existing comment (at the end of the file):
   ```markdown

   ### YYYY-MM-DD HH:MM
   <body>
   ```
5b. If `## Comments` section does not exist: append to the end of the file:
   ```markdown

   ## Comments

   ### YYYY-MM-DD HH:MM
   <body>
   ```
6. Write the updated file using the Edit tool.

**Output:** File updated. Comment is visible at the bottom of the ticket file.

**Edge cases / fallbacks:**
- File not found: surface error `"Cannot post comment — ticket file not found: <path>"`. The skill should warn but not hard-fail (the test cases output can be pasted manually).
- `body` is empty string: still append the timestamp header (creates a blank comment entry). This is acceptable behaviour.
- Multiple `## Comments` sections (malformed file): append after the last occurrence.

---

## commit_close_phrase

**Inputs:**
- `ref` — ticket id string (e.g. `forge-8`, `forge-8/001-tracker-contract`)
- `kind` — `implements | fixes | refs`

**Recipe:**

| kind | Output string |
|---|---|
| `implements` | `Implements <ref>` |
| `fixes` | `Fixes <ref>` |
| `refs` | `Refs <ref>` |

**Examples:**
- `commit_close_phrase("forge-8", "implements")` → `Implements forge-8`
- `commit_close_phrase("forge-8/001-tracker-contract", "implements")` → `Implements forge-8/001-tracker-contract`
- `commit_close_phrase("my-bug", "fixes")` → `Fixes my-bug`

The calling skill appends `: <short description>` and the co-author line to produce the full commit message subject line.

**Output:** A string. This op is pure string formatting — no failure mode. Always returns a string.

**Edge cases / fallbacks:**
- No failure case. If `ref` is empty string, return `Implements ` (callers should validate ref before calling).
- `kind` not one of the three known values: default to `Refs <ref>` and emit a warning.

---

### No auto-close edge case

**Markdown has no remote state.** Using `Implements <ref>` or `Fixes <ref>` in a commit message does NOT update the ticket's `status` field. Skills never write to the `status` frontmatter field — the user manages ticket lifecycle manually.

The phrase format is kept identical to other backends for two reasons:
1. **Grep consistency** — `git log --grep "Implements forge-8"` works the same way regardless of backend.
2. **Future tooling** — a future script or skill could scan commit history and auto-update frontmatter based on these phrases without changing the phrase format.

**User's options for "closing" a markdown ticket:**
- Edit the `status` field in frontmatter to `done` manually.
- Move/archive the file to a `_done/` subdirectory.
- Delete the file when the work is fully complete and no audit trail is needed.
- Leave the status as `backlog` indefinitely — skills do not depend on it.
