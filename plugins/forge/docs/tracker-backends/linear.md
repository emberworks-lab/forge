# Linear backend recipe

**Backend:** `linear`
**Status:** Implemented by FORGE-8 Story 2 (EMB-329).
**MCP surface used:** `mcp__claude_ai_Linear__*` tools available in the Claude runtime.

This file is the Linear backend recipe. Skills read it at dispatch time:
1. Read `<project>/.claude/tracker.json` → verify `"backend": "linear"`.
2. Read this file.
3. Find the `## <op_name>` section.
4. Execute it step-by-step.

---

## setup_interview

### Inputs
None. Invoked when `tracker.json` is absent or `backend` is not yet set for this project.

### Recipe

**Step 1 — List existing teams.**

Call:
```
mcp__claude_ai_Linear__list_teams  { }
```
Present the team names to the user as a numbered list. Ask:
> "Which Linear team should this project use? (pick number or type team name)"

Wait for the user's selection. Match against the returned list — do NOT create a new team.

**Step 2 — Optionally attach a project.**

Call:
```
mcp__claude_ai_Linear__list_projects  { "team": "<selected-team-name>" }
```
Present the project names (may be empty). Ask:
> "Scope to a specific Linear project? (type name or press Enter to skip)"

If the user provides a project name, verify it appears in the list. Record it. If the user skips, omit `project` from `tracker.json`.

**Step 3 — Auto-detect the issue prefix.**

Call:
```
mcp__claude_ai_Linear__list_issues  {
  "team": "<selected-team-name>",
  "limit": 10,
  "orderBy": "updatedAt"
}
```
Extract identifiers from the returned issues (e.g. `EMB-42`). Parse the prefix as the uppercase alpha portion before the first `-`. If all recent issues share the same prefix — use it silently and tell the user: `"Detected prefix: EMB"`. If multiple prefixes appear, or if the list is empty, ask:
> "What is the ticket identifier prefix for this team? (e.g. EMB, ENG, IF)"

**Step 4 — Write `tracker.json`.**

Write (or update) `<project-root>/.claude/tracker.json`:
```json
{
  "backend": "linear",
  "linear": {
    "team": "<selected-team-name>",
    "project": "<selected-project-name-or-omit>",
    "prefix": "<detected-or-entered-prefix>"
  }
}
```
Omit the `"project"` key entirely if the user skipped Step 2.

### Output
`tracker.json` written. Skill continues to whatever triggered setup_interview.

### Edge cases / fallbacks
- If the user selects a name that doesn't match any team returned by `list_teams`, ask once more. If still no match, tell the user "No matching team found — check your Linear workspace access" and halt.
- If `list_teams` returns an empty list, the workspace is not accessible. Surface the error and halt.
- If `list_issues` returns no issues (new team), fall back to asking the user for the prefix explicitly.
- `project` is optional per §3.1 of the contract README. Leaving it absent is always valid.

---

## ensure_labels

### Inputs
- `team` — from `tracker.json` `linear.team`

### Recipe

**Step 1 — List existing labels for the team.**

Call:
```
mcp__claude_ai_Linear__list_issue_labels  { "team": "<team-name>", "limit": 250 }
```
Collect all returned label `name` values into a set.

**Step 2 — Determine which required labels are missing.**

Required labels (8 total):

| Label name | Axis |
|---|---|
| `epic` | type |
| `story` | type |
| `task` | type |
| `bug` | type |
| `exec:opus` | executor |
| `exec:sonnet` | executor |
| `exec:manual` | executor |

Cross-reference against the existing label set. Build a list of missing labels.

**Step 3 — Create each missing label.**

For each missing label, call:
```
mcp__claude_ai_Linear__create_issue_label  {
  "name": "<label-name>",
  "color": "<color>"
}
```
Use these colors by convention (hex):

| Label | Color |
|---|---|
| `epic` | `#7C3AED` (violet) |
| `story` | `#2563EB` (blue) |
| `task` | `#059669` (green) |
| `bug` | `#DC2626` (red) |
| `exec:opus` | `#D97706` (amber) |
| `exec:sonnet` | `#0891B2` (cyan) |
| `exec:manual` | `#6B7280` (gray) |

These colors are suggestions — if the workspace already has labels with the same name but different colors, they were found in Step 1 and will not be recreated. Skip silently.

**Step 4 — Done.**

No return value. All 8 labels now exist in the workspace.

### Output
All 8 required labels exist in the Linear workspace. Skill may proceed to `create_ticket`.

### Edge cases / fallbacks
- If a label already exists (found in Step 1), skip `create_issue_label` for it entirely — never attempt to create a duplicate.
- If `create_issue_label` returns an API error (e.g. duplicate race condition), treat it as a no-op and continue — the label exists.
- If `create_issue_label` returns a genuine API error (non-duplicate), surface the error and halt. The skill cannot create tickets without labels.
- `ensure_labels` is called once per session before the first `create_ticket`. Subsequent calls within the same session may skip the API round-trip if the agent knows labels were already ensured this session.

---

## create_ticket

### Inputs
- `type` — one of `epic | story | task | bug`
- `executor` — one of `exec:opus | exec:sonnet | exec:manual`
- `title` — string
- `body` — markdown string
- `parent_ref` — optional; Linear identifier of the parent issue (e.g. `EMB-27`)

### Recipe

**Step 1 — Resolve label IDs.**

Call:
```
mcp__claude_ai_Linear__list_issue_labels  { "team": "<team-from-tracker.json>", "limit": 250 }
```
Find the label objects whose `name` matches `type` and `executor`. Extract their `id` values. If either label is missing — run `ensure_labels` first, then retry.

**Step 2 — Resolve parent issue ID (if `parent_ref` provided).**

If `parent_ref` is set, call:
```
mcp__claude_ai_Linear__get_issue  { "id": "<parent_ref>" }
```
Extract the internal `id` field (UUID). This is the `parentId` for the next step.

**Step 3 — Create the issue.**

Call:
```
mcp__claude_ai_Linear__save_issue  {
  "team": "<team-from-tracker.json>",
  "title": "<title>",
  "description": "<body>",
  "assignee": "me",
  "labels": ["<type-label-name>", "<executor-label-name>"],
  "parentId": "<parent-uuid-or-omit>"
}
```
Omit `parentId` entirely if `parent_ref` was not provided.

Do NOT set: `priority`, `cycle`, `milestone`, `estimate`, `dueDate`.

**Step 4 — Extract the returned identifier.**

The response contains an `id` (UUID) and an `identifier` field (e.g. `EMB-42`). Return the `identifier` as the `ticket_ref`.

### Output
`ticket_ref` — Linear identifier string, e.g. `EMB-42`.

### Edge cases / fallbacks
- If `save_issue` returns an API error, surface it and halt. Do not retry silently.
- If `list_issue_labels` returns a label whose name matches case-insensitively but not exactly — use the exact name from Linear's response, not the input string.
- If the team has a `project` configured in `tracker.json`, pass `"project": "<project-name>"` in the `save_issue` call so the ticket is scoped to that project.
- Assignee is always `"me"`. Linear's UI auto-assign setting does not apply to MCP-created issues — the field must be set explicitly.

---

## link_dependency

### Inputs
- `blocker_ref` — Linear identifier of the upstream (blocking) ticket, e.g. `EMB-27`
- `blocked_ref` — Linear identifier of the downstream (blocked) ticket, e.g. `EMB-28`

### Recipe

**Linear MCP exposes a native relation API.** The `save_issue` tool accepts `blockedBy` (append-only array of identifiers). Use it directly.

**Step 1 — Record the blocking relation on the blocked ticket.**

Call:
```
mcp__claude_ai_Linear__save_issue  {
  "id": "<blocked_ref>",
  "blockedBy": ["<blocker_ref>"]
}
```
This appends `blocker_ref` as a blocker of `blocked_ref`. Linear renders this as a "blocked by" relation in the UI.

The relation is append-only — existing relations on the ticket are preserved.

### Output
Blocking relation recorded in Linear. No return value.

### Edge cases / fallbacks
- `blockedBy` is append-only — calling this multiple times for the same pair is idempotent in effect (Linear deduplicates relations).
- If `save_issue` returns an API error, surface it with a single warning in chat and continue. Dependency tracking is advisory — skill execution is not blocked by a failed relation write.
- If the caller needs to record the inverse (`blocker_ref` blocks `blocked_ref`) and prefers to express it from the blocker's side, use `"blocks": ["<blocked_ref>"]` on the blocker ticket instead. Both forms are equivalent in Linear.
- No text-annotation fallback is needed for Linear — the native API is available.

---

## get_ticket

### Inputs
- `ref` — Linear identifier, e.g. `EMB-42`

### Recipe

**Step 1 — Fetch the issue.**

Call:
```
mcp__claude_ai_Linear__get_issue  { "id": "<ref>" }
```

**Step 2 — Map fields.**

From the response, extract:

| Contract field | Source field | Derivation |
|---|---|---|
| `title` | `title` | Direct |
| `body` | `description` | Direct (markdown string) |
| `type` | `labels` array | Find label whose `name` is one of `epic \| story \| task \| bug`; return that name |
| `executor` | `labels` array | Find label whose `name` starts with `exec:`; return that name (`exec:opus`, `exec:sonnet`, or `exec:manual`) |
| `status` | `status` (or `statusType`) | Return the backend-native status name as-is (e.g. `"Backlog"`, `"In Progress"`, `"Done"`) |
| `parent_ref` | `parentId` | If non-null: call `get_issue` on `parentId` to resolve its `identifier`; return that identifier string. If null: return `null` |

**Step 3 — Return structured object.**

```
{
  title:      "<string>",
  body:       "<markdown string>",
  type:       "epic" | "story" | "task" | "bug" | null,
  executor:   "exec:opus" | "exec:sonnet" | "exec:manual" | null,
  status:     "<backend-native status string>",
  parent_ref: "<EMB-N>" | null
}
```

### Output
Structured object with all 6 fields populated (some may be `null` — see edge cases).

### Edge cases / fallbacks
- `type` may be `null` if the ticket predates the label model (no type-axis label present). Callers (e.g. `/execute-epic`) must tolerate `null` type and fall back to treating the ticket as `task`.
- `executor` may be `null` for the same reason (pre-FORGE-8 ticket). Callers must tolerate `null` and fall back to displaying the ticket as unclassified; `/execute-epic` should not auto-execute a ticket with `null` executor — surface to user.
- `parent_ref` resolution requires a second `get_issue` call if the parent UUID is present. This is unavoidable — Linear's `list_issues` and `get_issue` return the internal UUID for `parentId`, not the human-readable identifier.
- If `get_issue` returns a 404 / not-found, surface the error and halt.

---

## list_subissues

### Inputs
- `epic_ref` — Linear identifier of the parent epic, e.g. `EMB-27`

### Recipe

**Step 1 — Fetch child issues.**

Call:
```
mcp__claude_ai_Linear__list_issues  {
  "parentId": "<epic_ref>",
  "limit": 250,
  "orderBy": "createdAt"
}
```

**Step 2 — Extract identifiers.**

From the response, collect the `identifier` field of each returned issue (e.g. `EMB-28`, `EMB-29`, …). Return as an ordered array.

Order guarantee: `createdAt` ascending — this matches the order in which sub-issues were created by `/create-epic`, which corresponds to their intended execution order.

### Output
Array of `ticket_ref` strings ordered by creation time, e.g. `["EMB-28", "EMB-29", "EMB-30"]`.
Returns `[]` if the epic has no children.

### Edge cases / fallbacks
- If the epic does not exist, `list_issues` may return an empty array or an API error. If the array is empty and the caller expects sub-issues, surface a warning: "No sub-issues found for `<epic_ref>` — verify the epic identifier."
- If the epic has more than 250 sub-issues (extremely unlikely), paginate using the `cursor` field from the response. In practice this limit will never be hit for single-project epics.
- Archived sub-issues: `list_issues` defaults `includeArchived: true` — archived sub-issues will appear. If the caller wants to exclude archived issues, pass `"includeArchived": false`. For `/execute-epic`, include archived to avoid skipping tickets that were accidentally archived.

---

## post_comment

### Inputs
- `ref` — Linear identifier, e.g. `EMB-42`
- `body` — markdown string (the comment content)

### Recipe

**Step 1 — Post the comment.**

Call:
```
mcp__claude_ai_Linear__save_comment  {
  "issueId": "<ref>",
  "body": "<body>"
}
```

The comment is attributed to the authenticated Linear user (the user whose API token is active in the Claude runtime). No timestamp manipulation is needed — Linear records `createdAt` automatically.

### Output
Comment posted. No return value.

### Edge cases / fallbacks
- If `save_comment` returns an API error, surface it with a warning in chat but do NOT hard-fail the calling skill. Manual test cases output can be pasted into Linear by the user manually if the comment post fails.
- Do not use `parentId` (reply) — all comments from skills are top-level thread entries on the issue.
- There is no deduplication — calling `post_comment` twice with the same body creates two comments. The calling skill is responsible for not double-posting.

---

## commit_close_phrase

### Inputs
- `ref` — Linear identifier, e.g. `EMB-42`
- `kind` — one of `implements | fixes | refs`

### Recipe

**Step 1 — Derive prefix and number from `ref`.**

Split `ref` on the first `-`: prefix = portion before `-` (e.g. `EMB`), number = portion after `-` (e.g. `42`).

Alternatively, the prefix is available directly from `tracker.json` at `linear.prefix`. Either source is equivalent — use whichever is already in scope.

**Step 2 — Format the phrase.**

| `kind` | Output format | Auto-close on merge? |
|---|---|---|
| `implements` | `Implements <PREFIX>-<N>` | Yes — moves ticket to Done |
| `fixes` | `Fixes <PREFIX>-<N>` | Yes — moves ticket to Done |
| `refs` | `Refs <PREFIX>-<N>` | No — links only |

Examples for `ref = "EMB-42"`:
- `implements` → `Implements EMB-42`
- `fixes` → `Fixes EMB-42`
- `refs` → `Refs EMB-42`

The calling skill appends `: <short description>` and the co-author line to produce the full commit message:
```
Implements EMB-42: add reddit feed

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

### Output
String — e.g. `Implements EMB-42`.

### Edge cases / fallbacks
- This op is pure string formatting — no API calls, no failure modes. Always returns a string.
- `implements` is the default kind for new feature work. Use `fixes` only when the ticket is a bug report. Use `refs` for partial work, docs-only changes, or when the ticket should remain open after merge.
- Both `implements` and `fixes` trigger Linear's auto-close integration when the PR merges to the default branch. `refs` does not.
- If `ref` is malformed (e.g. no `-`), fall back to `Implements <ref>` verbatim and warn the caller to verify the identifier format.
