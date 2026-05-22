# Tracker setup (step 7.25, also reachable via `--tracker-only`)

Included in the full project-init flow between step 7 and step 7.5; also the exclusive target when invoked as `/project-init --tracker-only`.

**The full flow calls this section once; `--tracker-only` runs only this section.**

## T1. Check for existing tracker.json

Check whether `<project-root>/.claude/tracker.json` exists.

- **Does not exist** → proceed to T2.
- **Exists** and this is `--tracker-only`: ask "Overwrite existing tracker.json? (y/n)"
  - `n` → print "Keeping existing tracker.json unchanged." and exit.
  - `y` → proceed to T2.
- **Exists** and this is a full project-init run: proceed to T2 (the full flow owns the decision to overwrite; step 2.6 already asked about Linear setup).

## T2. Choose a backend

Ask the user (single-select, **default: `github-personal`**):

> "Tracker backend for this repo?
> 1. **Linear** — Linear team + project, MCP-driven
> 2. **GitHub personal** — issues + Projects v2 on your personal account (default)
> 3. **GitHub org** — issues + Projects v2 on an organization
> 4. **Markdown** — local files under `docs/00_meta/manual-tracker`"

Pressing Enter selects `github-personal`. Then branch:

### `linear`

Read `plugins/forge/docs/tracker-backends/linear.md`, find the `## setup_interview` section, and execute it step-by-step. That recipe asks which team (writes `team_id` / `team` name), which project (optional), and auto-detects the prefix — then writes `tracker.json`.

After `setup_interview` writes `tracker.json`, call `ensure_labels` via the linear recipe to create all required labels (idempotent).

### `github-personal`

1. Auto-detect the GitHub user from the current directory:
   ```sh
   gh repo view --json owner,name --jq '"\(.owner.login) \(.name)"'
   ```
   If detection fails (no remote or not in a repo), ask the user: "GitHub username + repo name? (e.g. `achontoroh my-project`)".

2. Confirm with the user: "Use `<user>/<repo>` as the personal-account tracker? (y / change)". On `change`, prompt for replacement values.

3. Continue with the rest of `plugins/forge/docs/tracker-backends/github.md` `## setup_interview` (new vs existing GitHub Project, project number, multi-repo detection). The recipe writes `tracker.json` with:
   ```json
   {
     "backend": "github",
     "github": {
       "org": "<user>",
       "repo": "<repo>",
       "project_number": <N>
     }
   }
   ```
   Personal accounts cannot enable native Issue Types — the github recipe automatically falls back to label-based types in that case (see github.md `setup_interview` step 3).

4. Call `ensure_labels` via the github recipe.

### `github-org`

1. Ask the user: "GitHub org name?" — free text (e.g. `emberworks-lab`).
2. Ask: "Use a dedicated **epics_repo** for tracker issues, or keep everything in the code repo? [dedicated / same-repo]". If `dedicated`, prompt for the epics repo name (default suggestion: `<repo>-tracker`).
3. Continue with `plugins/forge/docs/tracker-backends/github.md` `## setup_interview` (org / repo detection — the recipe's auto-detect uses the answers above; multi-repo detection runs to confirm the `epics_repo` decision).
4. The recipe writes `tracker.json` with:
   ```json
   {
     "backend": "github",
     "github": {
       "org": "<org>",
       "repo": "<repo>",
       "epics_repo": "<tracker-repo>",   // only when dedicated
       "project_number": <N>
     }
   }
   ```
5. Call `ensure_labels` via the github recipe — once per repo when `epics_repo` is set.

### Polyrepo wiring (when `structure == "polyrepo"`)

Applies **on top of** `github-personal` / `github-org`. The general/parent repo
is the tracker home. At this step (7.25) the repos do not exist yet — they are
created in step 7.9 (`references/polyrepo-setup.md`) — so do GitHub-side repo
work there, not here.

1. **Skip `gh repo view` auto-detection.** The repo names come from interview
   step 2d: the general repo name and each `platforms[].repo`.
2. **Create the GitHub Project** (`gh project create`) — Projects v2 do not need a
   repo to exist. Capture `project_number`.
3. **Write the root `tracker.json`** with:
   ```jsonc
   {
     "backend": "github",
     "structure": "polyrepo",
     "github": {
       "org": "<org or user>",
       "repo": "<general-repo-name>",
       "epics_repo": "<general-repo-name>",
       "project_number": <N>
     },
     "platforms": [ { "name": "...", "path": "...", "repo": "<platform repo>" } ]
   }
   ```
4. **Defer to step 7.9:** repo creation + push, `linkProjectV2ToRepository` for
   the general repo and every platform repo, and `ensure_labels` per repo. Do
   **not** call `ensure_labels` here (no repos exist yet).

### `markdown`

Ask: "Where should markdown tickets live? (default: `docs/00_meta/manual-tracker`) — press Enter to accept." Capture the answer; if blank, use `docs/00_meta/manual-tracker`.

Write `<project-root>/.claude/tracker.json`:

```json
{
  "backend": "markdown",
  "markdown": {
    "directory": "<answer>"
  }
}
```

No `ensure_labels` call needed — markdown backend is a no-op for labels.

## T3. Confirm

Print to chat:

```
tracker.json created at <project-root>/.claude/tracker.json. Backend = <backend>.
```

If invoked via `--tracker-only`, the skill ends here. If invoked as part of the full project-init flow, return to the next step in the main flow (step 7.5 — Linear automation, or step 8 — Output if Linear was not requested).
