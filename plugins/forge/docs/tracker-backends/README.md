# Tracker backends — pluggability contract

**Status:** Established by FORGE-8 Story 1 (EMB-328). Authoritative reference for Stories 2–4 (backend recipes) and Story 5 (skill refactor).

This document defines everything a backend recipe must implement. Future backend implementors (Jira, Notion, etc.) only need to:
1. Create `docs/tracker-backends/<backend>.md` with all 8 `## <op>` sections.
2. Add the backend enum value to the `tracker.json` schema (§3).
3. Update any skill enum lookups if they list backends explicitly (§5).

No other files change.

---

## 1. The 8-operation contract

Every backend recipe implements exactly these 8 operations, each as a `## <op>` section in its recipe file. Skills call them indirectly: read `tracker.json` → resolve backend → read `~/.claude/docs/tracker-backends/<backend>.md` → find the `## <op_name>` section → execute it.

### 1.1 `setup_interview()`

**Purpose:** Collect backend-specific configuration from the user and write it into the project's `tracker.json`.

**Invoked by:** `/project-init --tracker-only`; also the first-use prompt triggered when a tracker-touching skill runs in a repo without `tracker.json`.

**What the recipe must specify:**
- Which questions to ask the user (backend-specific: team name, org/repo, directory, etc.)
- How to validate or auto-detect values where possible (e.g., detect prefix from recent commits)
- Exactly which keys to write into `tracker.json` under the backend's top-level object

**Success:** `tracker.json` exists and contains a valid `backend` key plus the matching backend config section. Skill continues after this op.

**Failure:** User answers indicate this backend is not applicable. Recipe must tell the skill to fall back to the tracker selection prompt.

---

### 1.2 `ensure_labels()`

**Purpose:** Idempotently create all required type and executor labels in the tracker if they are missing. Prevents `create_ticket` failures due to missing label references.

**Invoked by:** Skills that call `create_ticket` — once per session before the first ticket creation.

**Required labels to ensure (both axes, §2):**
- Type axis: `epic`, `story`, `task`, `bug`
- Executor axis: `exec:opus`, `exec:sonnet`, `exec:manual`

**What the recipe must specify:**
- How to list existing labels in this backend
- How to create a missing label (name, optional color/description if the backend supports it)
- The idempotency rule: if label already exists, skip silently; never fail on duplicate

**Success:** All 8 required labels exist in the tracker (or are no-ops for backends that don't have a label registry, e.g. markdown).

**Failure:** API error creating a label. Recipe must surface the error and halt; the skill cannot proceed without labels.

---

### 1.3 `create_ticket(type, executor, title, body, parent_ref?) → ticket_ref`

**Purpose:** Create a single work item in the tracker with exactly two labels (one type, one executor) and optional parent linkage.

**Parameters:**
- `type` — one of `epic | story | task | bug`
- `executor` — one of `exec:opus | exec:sonnet | exec:manual`
- `title` — string
- `body` — markdown string (ticket description)
- `parent_ref` — optional; backend-native reference to an existing ticket (e.g. Linear identifier `EMB-42`, GH issue number `123`, markdown slug `forge-8`). When set, the new ticket is linked as a sub-issue.

**Returns:** `ticket_ref` — the backend-native reference used in all subsequent ops (e.g. `EMB-42`, `123`, `forge-8/001-tracker-contract`).

**What the recipe must specify:**
- The exact API call or file-write to create the ticket
- How to attach both labels
- How to set the parent relationship when `parent_ref` is provided
- The format of the returned `ticket_ref`

**Success:** Ticket exists in the backend; `ticket_ref` is returned to the skill.

**Failure:** API error or file-write error. Recipe must surface the error; skill halts and reports the ref that failed.

---

### 1.4 `link_dependency(blocker_ref, blocked_ref)`

**Purpose:** Record that `blocked_ref` cannot start until `blocker_ref` is complete.

**Parameters:**
- `blocker_ref` — backend-native reference to the upstream ticket
- `blocked_ref` — backend-native reference to the downstream ticket

**What the recipe must specify:**
- Whether the backend has a native relation primitive (e.g. issue relations in Linear, `## Depends on` text block in GH/markdown)
- Exact API call or text mutation
- If no native primitive exists: fall back to prepending a `## Depends on\n- <blocker_ref>` block to `blocked_ref`'s body; document the limitation

**Success:** Dependency is recorded in the backend (natively or as text annotation).

**Failure / no-op:** If the backend has no relation API and the text fallback also fails, recipe must emit a single warning in chat and continue. Skills that parse dependencies (e.g. `/execute-epic`) always read `## Depends on` blocks in ticket bodies regardless of backend — the text fallback is always sufficient for skill dispatch.

---

### 1.5 `get_ticket(ref) → { title, body, type, executor, status, parent_ref }`

**Purpose:** Read a ticket and return its structured fields.

**Parameters:**
- `ref` — backend-native reference

**Returns:**
```
{
  title:      string,
  body:       string (full markdown body),
  type:       "epic" | "story" | "task" | "bug",
  executor:   "exec:opus" | "exec:sonnet" | "exec:manual",
  status:     string (backend-native status name — not normalized),
  parent_ref: string | null
}
```

**What the recipe must specify:**
- The exact API call or file-read
- How to derive `type` and `executor` from the backend's representation (labels, frontmatter, etc.)
- How to extract `parent_ref` (or `null` if the ticket has no parent)

**Success:** All fields populated. `type`/`executor` may be `null` if the ticket pre-dates the label model — recipe must document whether `null` is possible and how calling skills should handle it.

**Failure:** Ticket not found or API error. Recipe must surface the error.

---

### 1.6 `list_subissues(epic_ref) → [ticket_ref]`

**Purpose:** Return an ordered list of child ticket references for an epic.

**Parameters:**
- `epic_ref` — backend-native reference to the parent epic

**Returns:** Array of `ticket_ref` strings, ordered by creation order or file-system order (backend-dependent).

**What the recipe must specify:**
- The exact API call or file-glob
- Sort/order guarantee (or lack thereof)
- What to return when the epic has no children: empty array `[]`

**Success:** Array returned (may be empty).

**Failure:** Epic not found or API error. Recipe must surface the error.

---

### 1.7 `post_comment(ref, body)`

**Purpose:** Append a comment to an existing ticket. Used by `/execute-ticket` to post the `## Manual test cases` block after execution.

**Parameters:**
- `ref` — backend-native reference
- `body` — markdown string

**What the recipe must specify:**
- The exact API call or file-append operation
- How the comment is attributed (user, timestamp, or anonymous — backend-dependent)

**Success:** Comment is visible on the ticket in the tracker.

**Failure:** API error or file-write error. Recipe must surface the error; the skill should warn but not hard-fail (test cases output can be pasted manually).

---

### 1.8 `commit_close_phrase(ref, kind: implements|fixes|refs) → str`

**Purpose:** Format the magic-word prefix for a git commit message that links the commit to the tracker ticket.

**Parameters:**
- `ref` — backend-native reference
- `kind` — `implements` | `fixes` | `refs`

**Returns:** A string that starts the commit message subject line, e.g. `Implements EMB-42`, `Closes #123`, `Refs forge-8/001-tracker-contract`.

**Mapping:**

| kind | Linear | GitHub | Markdown |
|---|---|---|---|
| `implements` | `Implements <PREFIX>-<N>` | `Closes #<N>` | `Implements <slug>` |
| `fixes` | `Fixes <PREFIX>-<N>` | `Fixes #<N>` | `Fixes <slug>` |
| `refs` | `Refs <PREFIX>-<N>` | `Refs #<N>` | `Refs <slug>` |

**Note on auto-close:** `implements` and `fixes` auto-close tickets on PR merge for Linear and GitHub. Markdown has no remote state — the phrase is kept for grep consistency but does not change any file.

**What the recipe must specify:**
- The exact string format
- How the prefix/number/slug is derived from the `ref` and the backend config in `tracker.json`

**Success:** String returned; calling skill appends `: <short description>` and the co-author line.

**Failure:** This op is pure string formatting — no failure mode. Recipe must always return a string.

---

## 2. Label model

Every ticket gets **exactly 2 labels — one from each axis**.

### 2.1 Type axis

| Label | Meaning |
|---|---|
| `epic` | Parent container for a body of work; created by `/create-epic` |
| `story` | Sub-issue of an epic; default type for parent-linked tickets |
| `task` | Standalone ticket not under an epic; default for `/create-ticket` with no parent |
| `bug` | User-reported defect; not produced by automated flows |

### 2.2 Executor axis

| Label | Meaning | Old label replaced |
|---|---|---|
| `exec:opus` | Run by Claude Opus via `/execute-ticket` or `/execute-epic` | `model:opus` |
| `exec:sonnet` | Run by Claude Sonnet via `/execute-ticket` or `/execute-epic` | `model:sonnet` |
| `exec:manual` | User must complete this manually; blocks `/execute-epic` until DONE | `manual-setup` |

### 2.3 Mapping rules

- `/create-epic` — parent ticket gets `epic`; each sub-issue gets `story`; executor chosen per sub-issue at planning time.
- `/create-ticket` standalone (no `parent_ref`) — defaults to `task`.
- `/create-ticket` with `parent_ref` — defaults to `story`.
- `bug` is reserved for user-reported defects. Not assigned by skill flows.
- Skills filter on `exec:manual` to gate `/execute-epic`: all `exec:manual` sub-issues must be `DONE` before automated sub-issues can be dispatched.

### 2.4 Migration from old labels

`manual-setup`, `model:opus`, `model:sonnet` are replaced by this model starting FORGE-8 Story 5. Old labels on pre-existing tickets are left in place until natural ticket close or manual cleanup — they are not migrated in bulk.

---

## 3. `tracker.json` schema

Location: `<project-root>/.claude/tracker.json`

### 3.1 Full schema

```json
{
  "backend": "linear" | "github" | "markdown",

  "linear": {
    "team": "<Linear team name>",
    "project": "<Linear project name>",
    "prefix": "<ticket identifier prefix, e.g. EMB>"
  },

  "github": {
    "org": "<GitHub org or username>",
    "repo": "<repository name>",
    "epics_repo": "<repository name>",   // OPTIONAL — multi-repo setups; see §3.3
    "project_number": <integer>
  },

  "markdown": {
    "directory": "<relative path from project root, e.g. docs/00_meta/manual-tracker>"
  }
}
```

**Required:** `backend`. All other top-level keys are conditional on `backend` value.

**Validation rule:** Only the section matching the active `backend` value is read and validated. Other backend sections are ignored — a user may keep dormant backend config in the file when switching backends without causing errors.

**`linear.project`** is optional. Omit when work is not scoped to a specific Linear project.

**`linear.prefix`** should match the team's issue identifier prefix (e.g. `EMB` for identifiers like `EMB-42`). Auto-detected during `setup_interview` from recent issue identifiers; falls back to asking the user.

### 3.2 Full examples

**Linear backend:**
```json
{
  "backend": "linear",
  "linear": {
    "team": "Emberworks",
    "project": "Forge",
    "prefix": "EMB"
  }
}
```

**GitHub Projects v2 backend:**
```json
{
  "backend": "github",
  "github": {
    "org": "emberworks-lab",
    "repo": "reddit-idea-forge",
    "project_number": 1
  }
}
```

**Markdown backend:**
```json
{
  "backend": "markdown",
  "markdown": {
    "directory": "docs/00_meta/manual-tracker"
  }
}
```

**Switching example (dormant linear config retained):**
```json
{
  "backend": "markdown",
  "linear": {
    "team": "Emberworks",
    "prefix": "EMB"
  },
  "markdown": {
    "directory": "docs/00_meta/manual-tracker"
  }
}
```

### 3.3 Multi-repo GitHub Projects

A "multi-repo project" is a GitHub Project v2 linked to two or more repos in the same org — typical when a product has separate backend and mobile (or web + worker, etc.) repos sharing one tracker board.

GitHub does not let an issue exist without a repo — every issue lives in exactly one repo. Two patterns are supported:

**Pattern A — code-repo-as-tracker (default).** Each repo's `tracker.json` points at its own `repo` with no `epics_repo`. Epics live in whichever repo the user runs `/create-epic` from; sub-issues live in the same repo. Cross-repo sub-issues are possible (the `addSubIssue` GraphQL mutation works across repos in the same org) but require manually setting `parent_ref` to an issue in a different repo. The user must remember which code repo "owns" each epic.

**Pattern B — dedicated tracker repo (recommended for ≥ 2 code repos).** A third repo (e.g. `<product>-tracker`) is created with the sole purpose of hosting epics. Each code repo's `tracker.json` sets:

```json
{
  "backend": "github",
  "github": {
    "org": "<org>",
    "repo": "<this code repo>",
    "epics_repo": "<tracker repo>",
    "project_number": <integer>
  }
}
```

The tracker repo also gets a `tracker.json` (with `repo == epics_repo`, so the field is just omitted — see normalisation rule below).

**Routing rules when `epics_repo` is set:**
- `create_ticket type=epic` → creates in `epics_repo`.
- `create_ticket type=story|task|bug` → creates in `repo`. Sub-issues link to a parent epic in `epics_repo` via the cross-repo `addSubIssue` mutation.
- `get_ticket`, `list_subissues`, `post_comment` → take a repo-qualified ref; if the ref omits the repo, try `repo` first, then `epics_repo`.
- `list_subissues` returns cross-repo refs natively (`subIssues.nodes[].repository.nameWithOwner` from the GraphQL query). The skill must preserve the per-sub-issue repo, not assume `repo`.
- `commit_close_phrase` always uses the short `#N` form when the ticket is in the **same repo as the commit**, and the cross-repo form `<org>/<repo>#N` otherwise (e.g. `Closes emberworks-lab/pantrypal-tracker#42`).

**Normalisation:** when `epics_repo == repo`, omit `epics_repo`. The tracker repo itself follows this rule.

**Why a separate tracker repo:** keeps each code repo's `gh issue list` focused on actionable work for that repo; sub-issues + native GitHub UI handle cross-repo linkage; the user can run `/execute-epic` from any code repo without epic-vs-code ambiguity.

---

## 4. Backend recipe structure

Each backend is a single file: `~/.claude/docs/tracker-backends/<backend>.md`.

The file must contain exactly 8 sections, one per operation, using this heading format:

```markdown
## setup_interview
...recipe...

## ensure_labels
...recipe...

## create_ticket
...recipe...

## link_dependency
...recipe...

## get_ticket
...recipe...

## list_subissues
...recipe...

## post_comment
...recipe...

## commit_close_phrase
...recipe...
```

Each section must be concrete enough that an agent can execute it without additional context — specify exact API calls, CLI commands, file paths, and expected outputs.

---

## 5. How to add a new backend

To add a backend (e.g. Jira, Notion) without modifying anything outside this README:

### Step 1 — Write the recipe file

Create `~/.claude/docs/tracker-backends/<backend>.md` with all 8 `## <op>` sections (§4). Each section must:
- Be self-contained (link to external docs if needed, but do not require reading them to execute the recipe)
- Cover the success path fully
- Document any no-op or text-fallback cases (e.g. `link_dependency` with no native primitive)

**Jira** and **Notion** are the anticipated future candidates (explicitly out of FORGE-8 scope). When adding either, consult the relevant API docs for issue creation, label management, and comment APIs.

### Step 2 — Add the enum value to this README

Update the `tracker.json` schema (§3.1) to include the new backend value in the `backend` enum:

```json
"backend": "linear" | "github" | "markdown" | "jira"
```

Also add a full `tracker.json` example for the new backend under §3.2.

### Step 3 — Update skill enum lookups

Search `~/.claude/commands/` for any skill that enumerates backends explicitly (e.g. in a prompt that lists choices). Add the new backend value. As of FORGE-8, skills are intended to be backend-agnostic — they read `tracker.json` and dispatch to the recipe. If a skill has hardcoded backend names in user-facing text (e.g. the first-use setup prompt `"[linear | github | markdown | skip]"`), update that prompt.

### Step 4 — Smoke-test all 8 ops

Verify the new backend works end-to-end:
1. `setup_interview` — run `/project-init --tracker-only` in a test repo, pick the new backend, confirm `tracker.json` is written correctly.
2. `ensure_labels` — confirm all 8 required labels exist after the call.
3. `create_ticket` — create an epic and a story under it; confirm `ticket_ref` is returned.
4. `link_dependency` — confirm dependency is recorded (natively or as text).
5. `get_ticket` — read back the created tickets; confirm all fields are populated.
6. `list_subissues` — list children of the created epic; confirm the story appears.
7. `post_comment` — post a comment on the story; confirm it appears on the ticket.
8. `commit_close_phrase` — confirm the returned string matches the expected format for all 3 `kind` values.

---

## 6. Operations NOT in the contract

The following are deliberately excluded. Skills must not attempt to perform them via backend recipes:

| Operation | Reason excluded |
|---|---|
| `update_status` | Handled automatically by magic-word commits + PR merge into default branch |
| `assign` | Assignee is always the authenticated user; set at creation time |
| `set_priority` | Not set by skill flows |
| `set_cycle` / `set_milestone` | Solo-dev workflow is backlog-driven; no cycles/milestones by default |
| Dependency-graph traversal | `/execute-epic` reads `## Depends on` blocks in ticket bodies directly; not a backend concern |

---

## 7. Dispatch mechanism (how skills use this)

When a skill reaches a tracker-touching step:

1. Read `<project>/.claude/tracker.json` → resolve `backend`.
2. If `tracker.json` is missing → run first-use setup flow (ask `[linear | github | markdown | skip]` → invoke the selected backend's `setup_interview` → write `tracker.json` → continue).
3. Read `~/.claude/docs/tracker-backends/<backend>.md`.
4. Locate the `## <op_name>` section.
5. Execute the recipe in that section.

**Why documentation-based dispatch (not a Python module):** Linear MCP tools live in Claude's runtime environment — they cannot be called from a subprocess. GitHub CLI (`gh`) can be called from a subprocess but keeping all three backends in the same doc-based pattern avoids a split dispatch mechanism. The agent reads the relevant section and executes it directly.

---

## 8. Current backends

| Backend | Recipe file | Status |
|---|---|---|
| `linear` | `linear.md` | Implemented (FORGE-8 Story 2 / EMB-329) |
| `github` | `github.md` | Implemented (FORGE-8 Story 3 / EMB-330) |
| `markdown` | `markdown.md` | Implemented (FORGE-8 Story 4 / EMB-331) |
| `jira` | `jira.md` | Future — out of FORGE-8 scope |
| `notion` | `notion.md` | Future — out of FORGE-8 scope |
