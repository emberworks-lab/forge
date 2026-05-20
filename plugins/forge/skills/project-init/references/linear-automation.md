# Linear automation (step 7.5)

Runs only if step 2.6 was **Yes (Recommended)**. If **No** or **Skip**, jump straight to step 8 — make NO Linear MCP calls.

## Hard rules

Inherited from FORGE-3.5 (see `plugins/forge/docs/conventions/tracker-tickets.md`):

- **NEVER create a Linear team.** Always work within an existing team. If `list_teams` returns zero teams, exit gracefully: "No Linear teams found. Create one manually in Linear, then re-run." Continue the rest of the project-init flow.
- **NEVER set cycle or milestone** on the created project, P0 Bootstrap epic, P1 MVP epic, or any sub-issue. Cycles / milestones are strictly opt-in and the user did not opt in here.
- **NEVER set priority** on the created issues.

## 7.5.1. Resolve team

1. Call `mcp__claude_ai_Linear__list_teams`.
2. Zero teams → print the "no teams" message above; skip to step 8.
3. Exactly one team → use it as the default and confirm with the user (single-press Yes).
4. Multiple teams → present the list and ask "Which Linear team?" — default to **Emberworks** if present (the user's home team), otherwise no default.
5. **Do NOT offer team creation.** If the user wants a team that doesn't exist, instruct them to create it in Linear manually and re-run.
6. Capture `team.key` as the `linear_prefix` (e.g. `EMB`). Write to the answers JSON as `"linear_prefix"`. No separate prompt — prefix is derived automatically.

## 7.5.2. Create the Linear project

Call `mcp__claude_ai_Linear__save_project` with:

- `name` = project name from the interview.
- `team` = chosen team ID.
- `description` = `"Project bootstrapped via /project-init on <today's ISO date>. Stack: <stack summary>."`
- **Do NOT set** `targetDate`, `startDate`, `lead`, or any cycle / milestone-adjacent field unless the user volunteered it.

Capture `project.id`, `project.url`, and `project.slug` (or equivalent) from the response. On failure, print the error and skip to step 8.

## 7.5.3. Detect credentials needs

Scan the answers from step 2 (Persistence + Cloud + Existing scaffolding). For each match, queue one Mode M sub-ticket; the body comes from the matching template under `plugins/forge/skill-templates/_common/manual-setup-templates/`:

| Detected during interview | Template file | Sub-ticket title |
|---|---|---|
| Cloud = Supabase | `supabase.md` | `Set up Supabase project` |
| Cloud = Firebase | `firebase.md` | `Set up Firebase project` |
| Observability = Sentry (or user mentioned it) | `sentry.md` | `Set up Sentry project + DSN` |
| GitHub repo requested but `gh auth status` fails | `github-auth.md` | `GitHub CLI auth` |
| Tooling needs a Linear API key | `linear-keys.md` | `Linear API key` |

If no integrations match, P0 Bootstrap is still created with the body note: "No manual prerequisites detected — close this epic to proceed".

**Flutter path note:** when invoked from `references/flutter-scaffolder.md` step 4A-flutter.5.3, use the scaffold report's `mode_m_tickets` as canonical input instead of re-detecting here. The scaffolder already accounts for credential mode (`provide` → no ticket emitted).

## 7.5.4. Create the P0 — Bootstrap epic

Call `mcp__claude_ai_Linear__save_issue` with:

- `team` = chosen team ID.
- `project` = newly created project ID.
- `title` = `"P0 — Bootstrap"`.
- `labelIds` = `["Epic"]` (resolve via `list_issue_labels`; create via `create_issue_label` if missing).
- `description`:
  ```markdown
  Bootstrap epic created by /project-init. Holds manual-setup tickets the user must complete by hand before development begins.

  ## Prerequisites detected
  - <list each detected integration as a bullet, e.g. "Supabase project + keys">
  - <...>

  ## Next
  Run `/execute-epic <P0 epic ID>` once every manual-setup ticket below is closed by you.
  ```
- **Do NOT set** `cycle`, `milestone`, `priority`, `dueDate`, `estimate`, or `assignee`.

Capture the epic ID.

## 7.5.5. Create one Mode M sub-issue per detected integration

For each entry from 7.5.3:

1. Read the template at `plugins/forge/skill-templates/_common/manual-setup-templates/<service>.md`.
2. Substitute placeholders: `<project_name>`, `<date>`.
3. Call `mcp__claude_ai_Linear__save_issue` with:
   - `team` = chosen team ID.
   - `project` = newly created project ID.
   - `parentId` = P0 epic ID.
   - `title` = sub-ticket title from the table.
   - `labelIds` = `["Story", "manual-setup"]` (resolve / create as needed).
   - `description` = the substituted template body (must contain `## What`, `## User actions`, `## Acceptance`).
   - **Do NOT set** `cycle`, `milestone`, `priority`, `dueDate`, `estimate`, or `assignee`.

## 7.5.6. Create the P1 — MVP placeholder epic

Call `mcp__claude_ai_Linear__save_issue` with:

- `team` = chosen team ID.
- `project` = newly created project ID.
- `title` = `"P1 — MVP"`.
- `labelIds` = `["Epic"]`.
- `description`:
  ```markdown
  Placeholder epic for the MVP phase. Use `/create-epic <prefix>` to draft real P1 epics with detailed scope.
  ```
- **Do NOT set** `cycle`, `milestone`, `priority`, `dueDate`, `estimate`, or `assignee`.

Capture the epic URL.

## 7.5.7. Print summary

```
Linear project created: <name>
URL: <project URL>

Epics:
- P0 — Bootstrap (<N> manual-setup tickets) — <P0 epic URL>
- P1 — MVP (placeholder) — <P1 epic URL>

Next steps:
1. Complete the manual-setup tickets in P0 (each has step-by-step instructions in the body).
2. Once P0 is fully closed, run /execute-epic <P1 epic ID> to begin work — but first, draft real P1 epics via /create-epic <prefix>.
```
