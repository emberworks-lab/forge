# GitHub Projects v2 backend recipe

**Backend:** `github`
**Config key in `tracker.json`:** `github: { org, repo, epics_repo?, project_number }`
**CLI requirement:** `gh` (GitHub CLI) authenticated with at minimum the `repo` scope. Operations that touch GitHub Projects additionally require the `project` scope (`gh auth refresh -s project`).

**Repo routing (multi-repo projects).** When `epics_repo` is set in `tracker.json`, epics are created in `epics_repo` and sub-issues / standalone tickets stay in `repo`. Sub-issues link to parent epics via cross-repo `addSubIssue` (works org-wide on GitHub Cloud — confirmed via GraphQL introspection on `AddSubIssueInput`, which accepts `subIssueUrl` for cross-repo linkage). See `README.md` §3.3 for the full pattern.

Throughout this file: `$REPO` is the current repo from `tracker.json`. `$EPICS_REPO` is `tracker.json.github.epics_repo ?? $REPO`. Use `$REPO_FOR_TYPE` shorthand: `$EPICS_REPO` when `$TYPE == epic`, else `$REPO`.

**Platform requirement:** This recipe uses native **Issue Types** and native **Issue Relationships** (`addSubIssue` / `addBlockedBy`). These features require:
- GitHub Cloud (always available), **or**
- GitHub Enterprise Server 3.13+ with the Issue Types feature flag enabled at the org level.

For older GH Enterprise instances, each operation that uses these mutations documents a label/text-block fallback at the end of its section.

All 8 contract operations are implemented below using `gh` CLI and `gh api` (REST + GraphQL), plus one optional read op (`list_blocked_by`) used by `/execute-epic` for dependency-ordered dispatch. Variable names in ALLCAPS (e.g. `$ORG`, `$REPO`) come from `tracker.json` unless otherwise noted.

---

## setup_interview

**Inputs:** none (interactive — runs once per repo)

**Recipe:**

1. Auto-detect org and repo from the current directory:

   ```sh
   gh repo view --json owner,name --jq '"\(.owner.login) \(.name)"'
   ```

   This prints two space-separated values. Capture them:

   ```sh
   read ORG REPO <<< $(gh repo view --json owner,name --jq '"\(.owner.login) \(.name)"')
   ```

   If the command fails (not inside a git repo, or no GitHub remote), ask the user: "What is the GitHub org/username and repository name? (e.g. `emberworks-lab reddit-idea-forge`)"

2. Ask the user: "Create a new GitHub Project for this repo, or use an existing one? [new / existing]"

   **If `new`:**
   Ask for a project title (suggest repo name, e.g. `reddit-idea-forge`). Then:

   ```sh
   gh project create --owner "$ORG" --title "$PROJECT_TITLE" --format json
   ```

   Capture the project number from the JSON output:

   ```sh
   PROJECT_NUMBER=$(gh project create --owner "$ORG" --title "$PROJECT_TITLE" --format json --jq '.number')
   ```

   **If `existing`:**
   Ask: "What is the project number or URL?" (GitHub Projects have a numeric ID visible in the URL, e.g. `https://github.com/orgs/emberworks-lab/projects/1` → number `1`).

   If the user provides a URL, parse the trailing integer: `echo "$URL" | grep -oE '[0-9]+$'`.

   Verify the project exists and is accessible:

   ```sh
   gh project view "$PROJECT_NUMBER" --owner "$ORG" --format json --jq '.title'
   ```

   If this returns a title, the project is valid. If it errors, report: "Project `$PROJECT_NUMBER` not found or not accessible under `$ORG`. Check the project scope: `gh auth refresh -s project`."

3. Verify native Issue Types are enabled on the org and that `Epic`, `Task`, `Bug`, `Feature` exist:

   ```sh
   gh api graphql \
     -f query='query($org:String!) {
       organization(login: $org) {
         issueTypes(first: 20) { nodes { id name isEnabled } }
       }
     }' \
     -f org="$ORG" \
     --jq '.data.organization.issueTypes.nodes'
   ```

   Confirm the output contains entries for `Epic`, `Task`, `Bug`, `Feature` with `isEnabled: true`. If any are missing or disabled, instruct the user:

   > "Native Issue Types are required by this backend. Open https://github.com/organizations/$ORG/settings/issue-types and enable `Epic`, `Task`, `Bug`, `Feature`. Re-run setup when done."
   >
   > If the org is on a GitHub Enterprise version that does not support Issue Types at all, the backend will still function via label/text-block fallbacks documented in each op, but native UX (parent/sub-issue tree, "Blocked by" badges) will not appear.

   Do **not** persist anything from this query into `tracker.json` — type IDs are queried at runtime per call because they can change.

4. **Multi-repo detection (only when `$PROJECT_NUMBER` is reused).** Query the project's linked repos:

   ```sh
   gh api graphql -f query='query($org:String!, $num:Int!) {
     organization(login:$org) {
       projectV2(number:$num) {
         repositories(first:10) { nodes { nameWithOwner } }
       }
     }
   }' -f org="$ORG" -F num="$PROJECT_NUMBER" --jq '[.data.organization.projectV2.repositories.nodes[].nameWithOwner]'
   ```

   If the project is linked to **2+ repos** (including this one), ask the user:

   > "Project `$PROJECT_NUMBER` is linked to multiple repos: A, B, …. Where should epics live?
   > a) **separate tracker repo** (recommended for multi-repo projects — creates / uses a dedicated `<product>-tracker` repo so epics don't clutter any code repo)
   > b) **this repo** (`$REPO`) — epics and code coexist in the same repo
   > c) **another existing repo** in the project — pick from the list above"

   - **(a) separate tracker repo:** ask for the tracker repo name (default suggestion: `${PROJECT_NAME}-tracker` lowercased). If the repo doesn't exist, offer to create it via `gh repo create $ORG/$TRACKER --private`. Link it to the project via `linkProjectV2ToRepository` (see step 5). Set `EPICS_REPO=$TRACKER`. Create the `exec:opus`, `exec:sonnet`, `exec:manual` labels in the tracker repo too (see `ensure_labels`).
   - **(b) this repo:** do not write `epics_repo`. Omit the field — single-repo default.
   - **(c) another repo:** prompt for which one; set `EPICS_REPO=<that-repo>`. Verify that repo is in the project's linked list.

   If the project is linked to only one repo, skip this step entirely.

5. Write `tracker.json` at `<project-root>/.claude/tracker.json`:

   **Single-repo (or `epics_repo == repo`):**
   ```json
   {
     "backend": "github",
     "github": {
       "org": "<ORG>",
       "repo": "<REPO>",
       "project_number": <PROJECT_NUMBER>
     }
   }
   ```

   **Multi-repo with separate tracker repo:**
   ```json
   {
     "backend": "github",
     "github": {
       "org": "<ORG>",
       "repo": "<REPO>",
       "epics_repo": "<TRACKER_REPO>",
       "project_number": <PROJECT_NUMBER>
     }
   }
   ```

   Rule: omit `epics_repo` when it equals `repo`. The tracker repo's own `tracker.json` therefore has no `epics_repo` field.

**Output:** `tracker.json` written with `backend`, `org`, `repo`, optional `epics_repo`, `project_number`. Issue Types verified enabled on the org. Tracker repo (if chosen) exists and is linked to the project.

**Edge cases / fallbacks:**
- If `gh repo view` fails because there are multiple remotes, `gh` will use the `origin` remote by default. Confirm with the user if the detected repo looks wrong.
- `gh project create` requires the `project` scope; if it fails with a scope error, instruct the user to run `gh auth refresh -s project` and retry.
- If the user is an individual (not an org), `--owner` takes their GitHub username; `gh project list --owner "@me"` can help enumerate personal projects. Note: native Issue Types are an **organization-level** feature — personal accounts cannot enable them. The backend will fall back to label-based types for personal repos.

---

## ensure_labels

**Inputs:** `$ORG`, `$REPO` from `tracker.json`. For multi-repo setups (when `$EPICS_REPO` is set), run this op once per repo: `$REPO`, `$EPICS_REPO`, and any other code repos that may host sub-issues. Pass the target repo as `$TARGET_REPO` per call.

> **Note:** Ticket *type* (`epic` / `story` / `task` / `bug`) is now expressed via the **native GitHub Issue Type** field, not labels. Only executor labels remain here because GitHub has no first-class executor concept — `exec:opus` / `exec:sonnet` / `exec:manual` are how skills route work to the right runtime.

**Recipe:**

1. Fetch all existing label names in `$TARGET_REPO`:

   ```sh
   EXISTING=$(gh label list --repo "$ORG/$TARGET_REPO" --json name --jq '.[].name')
   ```

2. Define the required labels with their colors and descriptions:

   | Label | Color | Description |
   |---|---|---|
   | `exec:opus` | `#E4B429` (gold) | Run by Claude Opus |
   | `exec:sonnet` | `#F9A825` (amber) | Run by Claude Sonnet |
   | `exec:manual` | `#BDBDBD` (grey) | User must complete manually |

3. For each required label, check if it already exists. If not, create it:

   ```sh
   declare -A LABEL_COLORS=(
     ["exec:opus"]="E4B429"
     ["exec:sonnet"]="F9A825"
     ["exec:manual"]="BDBDBD"
   )
   declare -A LABEL_DESCS=(
     ["exec:opus"]="Run by Claude Opus"
     ["exec:sonnet"]="Run by Claude Sonnet"
     ["exec:manual"]="User must complete manually; blocks /execute-epic until DONE"
   )

   EXISTING=$(gh label list --repo "$ORG/$TARGET_REPO" --json name --jq '.[].name')

   for LABEL in exec:opus exec:sonnet exec:manual; do
     if ! echo "$EXISTING" | grep -qx "$LABEL"; then
       gh label create "$LABEL" \
         --repo "$ORG/$TARGET_REPO" \
         --color "${LABEL_COLORS[$LABEL]}" \
         --description "${LABEL_DESCS[$LABEL]}"
     fi
   done
   ```

**Output:** All 3 required executor labels exist in `$ORG/$REPO`. Silent on no-ops.

**Edge cases / fallbacks:**
- If `gh label create` fails with "already exists", it is safe to ignore (the `grep -qx` check should prevent this, but race conditions are possible). Use `--force` on `gh label create` to update color/description if the label exists with different metadata.
- The `project` scope is not required for label operations; only `repo` scope is needed.
- Color values in `gh label create --color` must be 6-character hex WITHOUT the leading `#`.
- **Type-label fallback (GH Enterprise without Issue Types):** if the org could not enable Issue Types (verified during `setup_interview`), also create `epic` / `story` / `task` / `bug` labels here. Detect this case by querying `organization(login:$org).issueTypes` and checking for an empty list. The fallback mirrors the pre-native scheme: `epic` `#0052CC`, `story` `#5319E7`, `task` `#1D76DB`, `bug` `#D93F0B`.

---

## create_ticket

**Inputs:**
- `$TYPE` — one of `epic | story | task | bug` (skill contract)
- `$EXECUTOR` — one of `exec:opus | exec:sonnet | exec:manual`
- `$TITLE` — string
- `$BODY` — markdown string
- `$PARENT_NUMBER` — optional GitHub issue number of the parent (integer, e.g. `42`). For multi-repo setups, may be qualified as `<org>/<repo>#<N>`.
- `$AREA` — optional, multi-repo only — explicit destination code repo for a sub-issue (e.g. `pantrypal-mobile`). When set, overrides `$REPO`. Required when sub-issues span multiple code repos (see `/create-epic` Step 4 sub-issue tagging).
- `$ORG`, `$REPO`, `$EPICS_REPO` (optional), `$PROJECT_NUMBER` from `tracker.json`

**Repo resolution.** Compute `$TARGET_REPO` before any API call:

```sh
if [ "$TYPE" = "epic" ] && [ -n "$EPICS_REPO" ]; then
  TARGET_REPO="$EPICS_REPO"
elif [ -n "$AREA" ]; then
  TARGET_REPO="$AREA"
else
  TARGET_REPO="$REPO"
fi
```

All subsequent steps use `$ORG/$TARGET_REPO` in place of `$ORG/$REPO`.

### Type mapping (skill contract → GitHub Issue Type)

| Skill `$TYPE` | GitHub Issue Type |
|---|---|
| `epic` | `Epic` |
| `story` | `Task` (GitHub has no native `Story` — `Task` is the closest fit for sub-issues of epics) |
| `task` | `Task` |
| `bug` | `Bug` |

> Note the asymmetry: `story` and `task` both map onto GitHub's `Task` type. When reading back via `get_ticket`, the skill contract distinguishes them only by whether the issue has a parent (sub-issue of an epic → caller may treat as `story`; standalone → `task`). Callers MUST treat `task` as the generic sub-issue type and not assume `story`.

### Recipe

1. **Resolve the GitHub Issue Type ID** for `$TYPE`. Query the org once per session and cache; the type IDs are stable per org but stable across runs only if no admin recreates them:

   ```sh
   # Map skill type → GitHub Issue Type name
   case "$TYPE" in
     epic)  GH_TYPE_NAME="Epic" ;;
     story) GH_TYPE_NAME="Task" ;;
     task)  GH_TYPE_NAME="Task" ;;
     bug)   GH_TYPE_NAME="Bug"  ;;
   esac

   ISSUE_TYPE_ID=$(gh api graphql \
     -f query='query($org:String!) {
       organization(login: $org) {
         issueTypes(first: 20) { nodes { id name } }
       }
     }' \
     -f org="$ORG" \
     --jq ".data.organization.issueTypes.nodes[] | select(.name == \"$GH_TYPE_NAME\") | .id")
   ```

   `$ISSUE_TYPE_ID` is a GraphQL node ID like `IT_kwDOEMKCbc4B-zeB`.

2. **Create the issue with the executor label** (no type label):

   ```sh
   ISSUE_JSON=$(gh issue create \
     --repo "$ORG/$TARGET_REPO" \
     --title "$TITLE" \
     --body "$BODY" \
     --label "$EXECUTOR" \
     --assignee "@me" \
     --json number,url)

   ISSUE_NUMBER=$(echo "$ISSUE_JSON" | jq -r '.number')
   ISSUE_URL=$(echo "$ISSUE_JSON"    | jq -r '.url')
   ```

3. **Resolve the child issue's GraphQL node ID** (distinct from the REST integer ID):

   ```sh
   CHILD_NODE_ID=$(gh api graphql \
     -f query='query($owner:String!, $repo:String!, $number:Int!) {
       repository(owner:$owner, name:$repo) {
         issue(number:$number) { id }
       }
     }' \
     -f owner="$ORG" \
     -f repo="$TARGET_REPO" \
     -F number="$ISSUE_NUMBER" \
     --jq '.data.repository.issue.id')
   ```

   `$CHILD_NODE_ID` looks like `I_kwDOEMKCbc7K1234`. **Important:** `gh issue view --json id` returns the REST integer ID, which is NOT the same value and is not accepted by GraphQL mutations. Always use the GraphQL `repository.issue.id` query above to get the right ID.

4. **Set the Issue Type** via `updateIssueIssueType`:

   ```sh
   gh api graphql \
     -f query='mutation($issueId:ID!, $issueTypeId:ID) {
       updateIssueIssueType(input: {issueId:$issueId, issueTypeId:$issueTypeId}) {
         issue { number issueType { name } }
       }
     }' \
     -f issueId="$CHILD_NODE_ID" \
     -f issueTypeId="$ISSUE_TYPE_ID"
   ```

5. **If `$PARENT_NUMBER` is provided**, link this issue as a native sub-issue of the parent.

   In multi-repo setups, the parent typically lives in `$EPICS_REPO`. Resolve `$PARENT_REPO`:

   ```sh
   if [ -n "$PARENT_REPO" ]; then
     :  # caller supplied it explicitly (rare)
   elif [ -n "$EPICS_REPO" ]; then
     PARENT_REPO="$EPICS_REPO"
   else
     PARENT_REPO="$REPO"
   fi
   ```

   a. Resolve the parent's GraphQL node ID (same query as step 3, but in `$PARENT_REPO`):

      ```sh
      PARENT_NODE_ID=$(gh api graphql \
        -f query='query($owner:String!, $repo:String!, $number:Int!) {
          repository(owner:$owner, name:$repo) {
            issue(number:$number) { id }
          }
        }' \
        -f owner="$ORG" \
        -f repo="$PARENT_REPO" \
        -F number="$PARENT_NUMBER" \
        --jq '.data.repository.issue.id')
      ```

   b. Call `addSubIssue`. `issueId` is the **parent**, `subIssueId` is the **child**:

      ```sh
      gh api graphql \
        -f query='mutation($parentId:ID!, $childId:ID!) {
          addSubIssue(input: {issueId:$parentId, subIssueId:$childId}) {
            issue { number }
            subIssue { number }
          }
        }' \
        -f parentId="$PARENT_NODE_ID" \
        -f childId="$CHILD_NODE_ID"
      ```

      On success, the sub-issue relationship appears immediately in the GitHub UI under the parent issue's "Sub-issues" panel. On failure, surface the GraphQL error.

6. **Add the issue to the GitHub Project**:

   ```sh
   gh project item-add "$PROJECT_NUMBER" \
     --owner "$ORG" \
     --url "$ISSUE_URL"
   ```

> **One-shot alternative (advanced):** `CreateIssueInput` also accepts `issueTypeId` and `parentIssueId` directly, so steps 2–5 could collapse into a single `createIssue` GraphQL mutation. This recipe keeps `gh issue create` (REST) for portability — `gh` handles label resolution, repo defaults, and editor flow for free. Use the GraphQL one-shot only if optimising round-trips matters.

**Output:** `$ISSUE_NUMBER` (integer) — the human-readable GitHub issue number. This is the `ticket_ref` used in all subsequent ops.

**Edge cases / fallbacks:**
- If `$EXECUTOR` label does not exist, `gh issue create` will fail with an error referencing the missing label. Always run `ensure_labels` before the first `create_ticket` call in a session.
- The `--json number,url` flag on `gh issue create` requires `gh` ≥ 2.x. Older versions may need `gh issue create ... | tail -1` to parse the URL from stdout and derive the number from the URL.
- `addSubIssue` works **across repos in the same org** on GitHub Cloud. The `AddSubIssueInput` schema accepts either `subIssueId` (any issue's GraphQL node ID in the same org) or `subIssueUrl` (the full HTML URL of the child issue) — confirmed via GraphQL introspection. The same applies in reverse: a child issue in one repo can be linked under a parent epic in `$EPICS_REPO`. For GH Enterprise without cross-repo sub-issue support, fall back to the `_Parent:_` text annotation.
- `gh project item-add` requires the `project` scope. If it fails, report the scope error and instruct the user to run `gh auth refresh -s project`.
- **Issue Types fallback (GH Enterprise without native support):** if step 1's query returns no matching type (org has no Issue Types configured), skip step 4 and instead add the legacy type label to step 2's `gh issue create`: `--label "$TYPE,$EXECUTOR"`. Requires the type labels created by the `ensure_labels` fallback path.
- **Sub-issue fallback (GH Enterprise without native support):** if `addSubIssue` errors with "not enabled" or "field not found", append `\n\n_Parent: #$PARENT_NUMBER_` to the issue body via `gh issue edit "$ISSUE_NUMBER" --body-file -` and emit a warning. `get_ticket` and `list_subissues` handle this text fallback.

---

## link_dependency

**Inputs:**
- `$BLOCKER_NUMBER` — GitHub issue number of the upstream (blocker) ticket
- `$BLOCKED_NUMBER` — GitHub issue number of the downstream (blocked) ticket
- `$BLOCKER_REPO`, `$BLOCKED_REPO` — repos for each side. Default to `$REPO`. In multi-repo setups the caller resolves these from `list_subissues` output or from the area tag on the source ticket.
- `$ORG`, `$REPO`, optional `$EPICS_REPO` from `tracker.json`

**Recipe:**

GitHub now has native **Issue Relationships** with a dedicated `addBlockedBy` GraphQL mutation. The resulting "Blocked by" relationship is visible in the GitHub UI under the blocked issue and is queryable via the `Issue.blockedBy` / `Issue.blocking` connection fields (used by `/execute-epic` for dependency-ordered dispatch — see `list_blocked_by` below).

1. Resolve the GraphQL node IDs for both issues:

   ```sh
   : "${BLOCKER_REPO:=$REPO}"
   : "${BLOCKED_REPO:=$REPO}"

   BLOCKER_NODE_ID=$(gh api graphql \
     -f query='query($owner:String!, $repo:String!, $number:Int!) {
       repository(owner:$owner, name:$repo) {
         issue(number:$number) { id }
       }
     }' \
     -f owner="$ORG" \
     -f repo="$BLOCKER_REPO" \
     -F number="$BLOCKER_NUMBER" \
     --jq '.data.repository.issue.id')

   BLOCKED_NODE_ID=$(gh api graphql \
     -f query='query($owner:String!, $repo:String!, $number:Int!) {
       repository(owner:$owner, name:$repo) {
         issue(number:$number) { id }
       }
     }' \
     -f owner="$ORG" \
     -f repo="$BLOCKED_REPO" \
     -F number="$BLOCKED_NUMBER" \
     --jq '.data.repository.issue.id')
   ```

2. Call `addBlockedBy`. The input field names follow the schema: `issueId` is the **blocked** issue (the dependent one), `blockingIssueId` is the **blocker**:

   ```sh
   gh api graphql \
     -f query='mutation($blockedId:ID!, $blockerId:ID!) {
       addBlockedBy(input: {issueId:$blockedId, blockingIssueId:$blockerId}) {
         issue { number }
       }
     }' \
     -f blockedId="$BLOCKED_NODE_ID" \
     -f blockerId="$BLOCKER_NODE_ID"
   ```

   On success, the relationship is created and visible in the GitHub UI as "Blocked by #$BLOCKER_NUMBER" on the blocked issue.

**Output:** Native "Blocked by" relationship recorded. No issue body is mutated.

**Edge cases / fallbacks:**
- **Fallback (GH Enterprise without Issue Relationships):** if `addBlockedBy` fails with a "field not found" or "feature not enabled" error, fall back to the legacy text-block annotation — append a `## Depends on\n- #$BLOCKER_NUMBER` block to the blocked issue body via `gh issue edit ... --body-file -`. The fallback exists solely so `/execute-epic` (which scans `## Depends on` blocks as a universal cross-backend signal) can still order work.
- If `addBlockedBy` returns "already exists" (the same blocker is already registered), treat as idempotent success — do not halt.
- Cross-repo blockers: `addBlockedBy` accepts issues from a different repo (as long as the GraphQL node IDs are valid). The relationship will display the full `owner/repo#N` reference in the UI.

---

## get_ticket

**Inputs:**
- `$REF` — GitHub issue number (integer, e.g. `42`)
- `$REF_REPO` — repo where the issue lives. Defaults to `$REPO`. For epics in `$EPICS_REPO` or cross-repo sub-issue refs, the caller passes the resolved value (e.g. discovered via `list_subissues` GraphQL form).
- `$ORG`, `$REPO`, optional `$EPICS_REPO` from `tracker.json`

**Recipe:**

1. Fetch the issue with type, parent, labels, and state in a single GraphQL call:

   ```sh
   ISSUE=$(gh api graphql \
     -f query='query($owner:String!, $repo:String!, $number:Int!) {
       repository(owner:$owner, name:$repo) {
         issue(number:$number) {
           title
           body
           state
           issueType { name }
           parent { number }
           labels(first: 50) { nodes { name } }
         }
       }
     }' \
     -f owner="$ORG" \
     -f repo="${REF_REPO:-$REPO}" \
     -F number="$REF" \
     --jq '.data.repository.issue')
   ```

   The `parent` field also returns the parent's repo via `parent { number repository { nameWithOwner } }` when needed for cross-repo follow-ups — extend the query if the caller needs `parent_repo` alongside `parent_ref`.

2. Extract individual fields:

   ```sh
   TITLE=$(echo  "$ISSUE" | jq -r '.title')
   BODY=$(echo   "$ISSUE" | jq -r '.body')
   STATUS=$(echo "$ISSUE" | jq -r '.state')                                # "OPEN" or "CLOSED"
   GH_TYPE=$(echo "$ISSUE" | jq -r '.issueType.name // empty')             # "Epic" | "Task" | "Bug" | "Feature" | empty
   PARENT_REF=$(echo "$ISSUE" | jq -r '.parent.number // empty')           # integer or empty
   LABELS=$(echo "$ISSUE" | jq '[.labels.nodes[].name]')                   # JSON array of label names
   ```

3. Map the GitHub Issue Type back to the skill contract's `type`:

   | GitHub `issueType.name` | Skill `type` |
   |---|---|
   | `Epic` | `epic` |
   | `Task` (with parent) | `task` (callers may treat as `story` when they need to distinguish — see note below) |
   | `Task` (no parent) | `task` |
   | `Bug` | `bug` |
   | `Feature` | `feature` (out of the four-type contract; callers should treat as `task`) |
   | _empty_ | fall back to label scan (see fallbacks) |

   ```sh
   case "$GH_TYPE" in
     Epic)    TYPE="epic" ;;
     Task)    TYPE="task" ;;
     Bug)     TYPE="bug"  ;;
     Feature) TYPE="task" ;;  # outside skill-contract 4-type set; downgraded to task
     "")      TYPE=$(echo "$LABELS" | jq -r '.[] | select(. == "epic" or . == "story" or . == "task" or . == "bug")' | head -1) ;;
   esac
   ```

   > The skill contract distinguishes `task` vs `story` only by the presence of a parent (a `story` is a sub-issue of an epic). GitHub does not preserve that distinction — both round-trip as `Task`. Callers that need it should check `parent_ref`: if non-null and the parent is an epic, treat as `story`; otherwise `task`.

4. Derive `executor` from labels:

   ```sh
   EXECUTOR=$(echo "$LABELS" | jq -r '.[] | select(startswith("exec:"))' | head -1)
   ```

**Output:** Structured ticket object:

```
{
  title:      $TITLE,
  body:       $BODY,
  type:       $TYPE,       // null if no Issue Type and no matching label
  executor:   $EXECUTOR,   // null if no exec:* label
  status:     $STATUS,     // "OPEN" or "CLOSED" (GraphQL state mirrors REST)
  parent_ref: $PARENT_REF  // integer issue number, or null
}
```

**Edge cases / fallbacks:**
- `type` and `executor` may be `null` for tickets that pre-date the contract (no Issue Type set, no executor label). Calling skills must handle `null` gracefully — do not assume `task` or `exec:manual`.
- If the org has no Issue Types enabled, `issueType` will be `null` on every issue; the fallback label scan in step 3's empty-string branch handles this.
- If the GraphQL query fails entirely (very old GH Enterprise), fall back to `gh issue view --json number,title,body,state,labels,id` and scan labels for both `type` and a `_Parent: #(\d+)_` text marker (the legacy text fallback written by `create_ticket`).
- `STATUS` is uppercased (`OPEN`/`CLOSED`) — calling skills should do case-insensitive comparisons.

---

## list_subissues

**Inputs:**
- `$EPIC_REF` — GitHub issue number of the parent epic (integer, e.g. `10`)
- `$REF_REPO` — repo where the epic lives. Defaults to `$REPO`; for epics living in `$EPICS_REPO`, the caller passes that instead.
- `$ORG`, `$REPO`, optional `$EPICS_REPO` from `tracker.json`

**Recipe:**

Use the native GitHub sub-issues REST API endpoint (GA as of mid-2026). This endpoint returns sub-issues regardless of whether they were linked via the REST `POST /sub_issues` route or via the GraphQL `addSubIssue` mutation used by `create_ticket` — both write into the same backing relationship.

```sh
gh api \
  "/repos/$ORG/$REF_REPO/issues/$EPIC_REF/sub_issues" \
  --jq '.[].number'
```

This prints one issue number per line. To capture as an array — **and preserve the cross-repo origin of each sub-issue**, prefer the GraphQL form (the REST endpoint returns only numbers):

```sh
SUBISSUES=$(gh api graphql \
  -f query='query($owner:String!, $repo:String!, $number:Int!) {
    repository(owner:$owner, name:$repo) {
      issue(number:$number) {
        subIssues(first:50) { nodes { number repository { nameWithOwner } } }
      }
    }
  }' \
  -f owner="$ORG" -f repo="$REF_REPO" -F number="$EPIC_REF" \
  --jq '[.data.repository.issue.subIssues.nodes[] | {number, repo: .repository.nameWithOwner}]')
```

`$SUBISSUES` is then a JSON array like `[{"number":11,"repo":"emberworks-lab/pantrypal-backend"},{"number":1,"repo":"emberworks-lab/pantrypal-mobile"}]`. Callers in single-repo setups can ignore the `repo` field; in multi-repo setups (`$EPICS_REPO` set), the field is required for any follow-up op that takes a `$REF` — pass it through as `$REF_REPO` to `get_ticket`, `post_comment`, etc.

**Output:** JSON array of `{number, repo}` objects (GraphQL form) or integers (REST form), in the order sub-issues were linked. Returns `[]` if the epic has no children.

**Edge cases / fallbacks:**
- If the epic issue number does not exist, `gh api` returns a 404. Surface the error: "Issue #$EPIC_REF not found in $ORG/$REF_REPO."
- Pagination: the REST endpoint returns up to 30 items per page by default; the GraphQL form above takes 50. For epics with more sub-issues, paginate the REST endpoint:

  ```sh
  gh api \
    "/repos/$ORG/$REF_REPO/issues/$EPIC_REF/sub_issues" \
    --paginate \
    --jq '.[].number'
  ```

- Order guarantee: results are in the order sub-issues were linked, not creation order. This is sufficient for `/execute-epic` dispatch.
- If the endpoint returns a 404 with "Not Found" (rather than an issue-not-found message), the sub-issues feature may not be enabled on this GH Enterprise instance. Fall back to scanning all open issues for a `_Parent: #$EPIC_REF_` text annotation in their body (the fallback written by `create_ticket`):

  ```sh
  gh issue list --repo "$ORG/$REF_REPO" \
    --search "\"_Parent: #${EPIC_REF}_\"" \
    --json number \
    --jq '[.[].number]'
  ```

---

## list_blocked_by (optional)

**Inputs:**
- `$REF` — GitHub issue number (integer)
- `$REF_REPO` — repo where the issue lives. Defaults to `$REPO`.
- `$ORG`, `$REPO`, optional `$EPICS_REPO` from `tracker.json`

**Purpose:** Read the native "Blocked by" dependencies written by `link_dependency`. Used by `/execute-epic` to compute dependency-ordered dispatch.

**Recipe:**

```sh
gh api graphql \
  -f query='query($owner:String!, $repo:String!, $number:Int!) {
    repository(owner:$owner, name:$repo) {
      issue(number:$number) {
        blockedBy(first: 50) { nodes { number repository { nameWithOwner } } }
      }
    }
  }' \
  -f owner="$ORG" \
  -f repo="${REF_REPO:-$REPO}" \
  -F number="$REF" \
  --jq '[.data.repository.issue.blockedBy.nodes | map({number, repo: .repository.nameWithOwner})]'
```

The dual `Issue.blocking` connection lists what this issue blocks (the inverse direction). Confirmed via GraphQL introspection: `blockedBy` and `blocking` are fully readable connection fields on `Issue` — no preview API or feature flag required on GitHub Cloud.

**Output:** JSON array of issue numbers (e.g. `[10, 12]`) representing the issues that block `$REF`. Empty array `[]` if none.

**Edge cases / fallbacks:**
- For repos using the legacy `## Depends on` text-block fallback (written by `link_dependency` when `addBlockedBy` is unavailable), parse the body instead:

  ```sh
  gh issue view "$REF" --repo "$ORG/$REF_REPO" --json body --jq '.body' \
    | awk '/^## Depends on/{f=1;next} f && /^## /{f=0} f && /^- #/{gsub(/[^0-9]/,""); print}'
  ```

- Cross-repo blockers will appear in `repository.nameWithOwner` distinct from `$ORG/$REPO`. The skill contract treats only same-repo blockers as orderable dependencies; cross-repo entries should be surfaced to the user but not gate dispatch.

---

## post_comment

**Inputs:**
- `$REF` — GitHub issue number (integer, e.g. `42`)
- `$REF_REPO` — repo where the issue lives. Defaults to `$REPO`. For comments on epics in `$EPICS_REPO` or on sub-issues in a sibling code repo, the caller passes the resolved value.
- `$BODY` — markdown string (comment content)
- `$ORG`, `$REPO`, optional `$EPICS_REPO` from `tracker.json`

**Recipe:**

For short, inline bodies:

```sh
gh issue comment "$REF" \
  --repo "$ORG/$REF_REPO" \
  --body "$BODY"
```

For multi-line bodies (e.g. the `## Manual test cases` block from `/execute-ticket`), pass via stdin to avoid shell escaping issues:

```sh
printf '%s' "$BODY" | gh issue comment "$REF" \
  --repo "$ORG/$REF_REPO" \
  --body-file -
```

**Output:** Comment is posted to issue `#$REF` and visible on GitHub. The comment is attributed to the authenticated `gh` user. No return value needed.

**Edge cases / fallbacks:**
- If `gh issue comment` fails (e.g. issue is locked, or repo has comments disabled), emit a warning: "Could not post comment to #$REF — paste the output manually." Do not halt the skill; test case output can always be pasted manually.
- `--body-file -` reads from stdin. Ensure `$BODY` is passed via `printf '%s'` rather than `echo` to avoid a trailing newline mutation.
- Comment length limit on GitHub is 65,536 characters. If the body exceeds this, split into multiple comments and add a `(continued)` header to each continuation.

---

## commit_close_phrase

**Inputs:**
- `$REF` — GitHub issue number (integer, e.g. `42`)
- `$REF_REPO` — repo where the ticket lives. Defaults to `$REPO`.
- `$COMMIT_REPO` — repo the commit will land in. Defaults to `$REPO` (the repo the skill is invoked from).
- `$KIND` — one of `implements | fixes | refs`

**Recipe:**

Pure string formatting — no API call required.

| `$KIND` | Output (same repo: `$REF_REPO == $COMMIT_REPO`) | Output (cross repo) |
|---|---|---|
| `implements` | `Closes #<REF>` | `Closes <ORG>/<REF_REPO>#<REF>` |
| `fixes` | `Fixes #<REF>` | `Fixes <ORG>/<REF_REPO>#<REF>` |
| `refs` | `Refs #<REF>` | `Refs <ORG>/<REF_REPO>#<REF>` |

Shell mapping:

```sh
: "${REF_REPO:=$REPO}"
: "${COMMIT_REPO:=$REPO}"

if [ "$REF_REPO" = "$COMMIT_REPO" ]; then
  REF_FORM="#${REF}"
else
  REF_FORM="${ORG}/${REF_REPO}#${REF}"
fi

case "$KIND" in
  implements) PHRASE="Closes ${REF_FORM}" ;;
  fixes)      PHRASE="Fixes ${REF_FORM}" ;;
  refs)       PHRASE="Refs ${REF_FORM}" ;;
esac
```

**Why cross-repo form matters here:** in multi-repo setups, a commit in `pantrypal-mobile` that references an epic in `pantrypal-tracker` (or a sub-issue tracked in `pantrypal-backend`) must use the qualified form — GitHub only auto-closes/auto-links if the qualifier resolves the cross-repo reference. The bare `#N` form is silently ignored when no issue `#N` exists in the commit's repo.

**Output:** A string such as `Closes #42`. The calling skill appends `: <short description>` and the co-author line to form the full commit message subject, e.g.:

```
Closes #42: add reddit feed ingestion

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**Auto-close behavior:**
- `Closes #N` and `Fixes #N` auto-close issue `#N` when the PR containing the commit is merged into the default branch (GitHub default behavior).
- `Refs #N` links the commit to the issue in the timeline without changing its open/closed state.
- GitHub recognizes these keywords case-insensitively: `closes`, `Closes`, `CLOSES` all work. Use the casing shown above for readability.

**Edge cases / fallbacks:**
- This op is pure string formatting — it cannot fail. If `$KIND` is unrecognized, default to `Refs ${REF_FORM}` (safest — no unintended auto-close).
- The issue number in commits is matched against issues in the **same repository** by default. For cross-repo references, GitHub requires the full form `Closes owner/repo#N` — handled automatically by the `$REF_REPO != $COMMIT_REPO` branch above.

---

## set_project_status

**Purpose:** Update the GitHub Projects v2 `Status` field for an issue (Todo / In Progress / Done). Used by `/execute-ticket` and `/execute-epic` to surface live progress on the project board.

**Inputs:**
- `$TICKET_REF` — GitHub issue number (integer)
- `$STATUS_NAME` — one of `Todo | "In Progress" | Done` (must match an existing option in the project's Status field, case-insensitive)
- `$REF_REPO` — repo where the ticket lives. Defaults to `$REPO`.
- `$ORG`, `$PROJECT_NUMBER` from `tracker.json`

**Recipe:**

> **Important:** Do NOT hold `gh project ... --format json` output in a bash variable, then re-pipe. Project item bodies can contain control chars that break jq parsing on the second pass. Always pipe `gh project ...` directly into `jq` in the same command. The `--jq` flag on `gh project ...` is also unreliable with multi-arg `jq --arg ...` queries — use plain pipe.

1. Resolve the project node ID + Status field metadata once per session (cache the small scalar results, NOT the full JSON):

   ```sh
   PROJECT_NODE_ID=$(gh api graphql -f query='query($org:String!,$num:Int!){organization(login:$org){projectV2(number:$num){id}}}' -f org="$ORG" -F num="$PROJECT_NUMBER" --jq '.data.organization.projectV2.id')
   STATUS_FIELD_ID=$(gh project field-list "$PROJECT_NUMBER" --owner "$ORG" --format json | jq -r '.fields[] | select(.name=="Status") | .id')
   OPTION_ID=$(gh project field-list "$PROJECT_NUMBER" --owner "$ORG" --format json | jq -r --arg n "$STATUS_NAME" '.fields[] | select(.name=="Status") | .options[] | select((.name | ascii_downcase) == ($n | ascii_downcase)) | .id')
   ```

   If `$OPTION_ID` is empty, exit with warning ("status `$STATUS_NAME` not in project Status field — skipping"). Do NOT halt the parent skill.

2. Find the project item ID for `$TICKET_REF` — pipe `gh ...` directly into `jq` (no intermediate variable):

   ```sh
   ITEM_ID=$(gh project item-list "$PROJECT_NUMBER" --owner "$ORG" --limit 200 --format json \
     | jq -r ".items[] | select(.content.number == $TICKET_REF) | .id")
   ```

   If empty (issue not in project), exit cleanly with warning. Do NOT add it here — `create_ticket` adds issues to the project.

3. Update the field:

   ```sh
   gh project item-edit \
     --project-id "$PROJECT_NODE_ID" \
     --id "$ITEM_ID" \
     --field-id "$STATUS_FIELD_ID" \
     --single-select-option-id "$OPTION_ID" \
     > /dev/null
   ```

**Output:** Status updated on the project board; visible in the project UI under `Status` column. No issue body change.

**Edge cases / fallbacks:**
- If `gh project field-list` fails with scope error, instruct user: `gh auth refresh -s project`.
- If the project has no `Status` field (custom-removed by user), skip silently with warning.
- If `$STATUS_NAME` doesn't match any option, skip silently — do NOT pick a near-match.
- This op is **non-blocking** — failures should warn-and-continue, never halt the parent skill. Progress visibility is a nice-to-have, not a correctness gate.
