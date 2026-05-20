# Multi-repo detection (GitHub backend only)

Before running the create-epic flow, peek at the resolved `tracker.json`:

- If `backend == github` AND `github.epics_repo` is **already set** → use it as the epic destination silently.
- If `backend == github` AND `github.epics_repo` is **not set**, run a one-time check:

  ```sh
  gh api graphql -f query='query($org:String!, $num:Int!) {
    organization(login:$org) {
      projectV2(number:$num) { repositories(first:10) { nodes { nameWithOwner } } }
    }
  }' -f org="$ORG" -F num="$PROJECT_NUMBER" --jq '[.data.organization.projectV2.repositories.nodes[].nameWithOwner]'
  ```

  If the project is linked to **2+ repos**, ask the user once:

  > "Project `$PROJECT_NUMBER` is linked to multiple repos. Recommend a separate `<product>-tracker` repo for epics so each code repo stays focused on actionable work. Create / use one now? [yes / no / use existing repo: name]"

  - `yes` → ask for tracker repo name (default `${PROJECT_NAME}-tracker`). Create via `gh repo create $ORG/<name> --private` if missing. Link to project via `linkProjectV2ToRepository`. Write `epics_repo` into the current `tracker.json` (and into sibling code repos' `tracker.json` if the user confirms they should share).
  - `no` → continue with epic in current `$REPO`. Do not re-ask in future invocations (absence of `epics_repo` is the answer).
  - `use existing repo: <name>` → verify the repo is in the project's linked list; write `epics_repo`.

See `~/.claude/docs/tracker-backends/README.md` §3.3 and `~/.claude/docs/tracker-backends/github.md` `## setup_interview` step 4 for the canonical flow.

## Multi-repo area routing

When multi-repo is in effect, each sub-issue carries an `[area-repo-short-name]` tag (e.g. `[backend]`, `[mobile]`, `[tracker]`). The short name maps to the actual repo via the project's `repositories` list. Cross-cutting prep tickets (provisioning, account setup) default to `[tracker]`. Single-repo projects omit the tag.

At ticket-creation time, pass `area=<area-repo-name>` to the `create_ticket` recipe; the recipe routes the `gh issue create` call to `$ORG/$AREA` instead of `$ORG/$REPO`. The recipe's `addSubIssue` works cross-repo against the parent in `epics_repo`.
