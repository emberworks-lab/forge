---
name: pr-create
description: Create a draft PR for a tracker epic — reads the epic + branch, generates an epic-linked PR body from sub-issues and commits, opens the PR via gh CLI.
type: hybrid
---

# PR Create

Trigger: `/pr-create EMB-227`, "створи пр на епік EMB-227", or invoked from `forge:epic-close` after the user opts in.

At every tracker-touching step: read `<project>/.claude/tracker.json` → `backend`; execute the matching recipe section from `plugins/forge/docs/tracker-backends/<backend>.md`. Fallback: if `tracker.json` is missing, fall back to current Linear-MCP behavior — phased out in a future cleanup epic.

## Core principles

- **PR is created AFTER manual testing.** Don't bypass that gate. If invoked too early, ask for confirmation.
- **Draft by default.** PRs land as drafts; user marks ready-for-review when truly ready.
- **Body is generated, not authored.** Pull from epic + commits; user edits later if they want.
- **Auto-link via magic words.** Commits already carry the backend's magic-word phrase (e.g. `Implements EMB-NN`, `Closes #N`) — the tracker auto-closes on merge.

## Inputs

Epic ID (required, in the active backend's ref shape — `EMB-227` for Linear, `42` for GitHub, `forge-8` for markdown), or `--from-branch` to detect from the current branch.

Optional flags:

- `--ready` — open as ready-for-review instead of draft.
- `--base <branch>` — override base branch (default: `develop` if it exists, else `main`).
- `--no-confirm` — skip the manual-testing prompt (used when invoked from `forge:epic-close` with consent).

## Flow

### 1. Pre-flight

- `git rev-parse --abbrev-ref HEAD` — capture current branch.
- `gh auth status` — confirm gh CLI is authenticated; halt with a friendly message if not.
- Resolve `<base>`: `git rev-parse --verify develop 2>/dev/null` → `develop`, else `main`.
- Verify head is pushed: compare `git rev-parse HEAD` to `git rev-parse @{u}` (or check `git status` for "ahead by N"). If unpushed, ask: "branch has unpushed commits; running `git push -u origin <branch>` first — ok?" then push on `y`.
- Check for existing PR: `gh pr list --head <branch> --json number,url,state`. If an open PR exists → ask "PR exists at <url>. Update body? Skip? Close & reopen?"

### 2. Manual-test confirmation (unless `--no-confirm`)

> "PR створюється тільки після ручного тестування. Перевірив manual test cases в коментарі епіка <EPIC-REF>? (y / not yet)"

`not yet` → exit cleanly. `y` → continue.

### 3. Load epic + commits (parallel)

- **get_ticket via backend recipe** with `ref=<epic_ref>` (and `includeRelations` if supported).
- **list_subissues via backend recipe** with `epic_ref=<epic_ref>` — titles + refs.
- `git log <base>..HEAD --oneline` — commits on this branch.
- `git diff --stat <base>..HEAD` — stats.

### 4. Compose PR body

**commit_close_phrase via backend recipe** with `ref=<epic_ref>` and `kind=implements`. The recipe returns the magic-word phrase that auto-links and closes the epic on merge (e.g. `Implements EMB-227`, `Closes #42`, `Implements forge-8`).

PR body template + a worked example: see `references/pr-body-template.md`. The body always includes the magic-word phrase line at the top, a Summary section paraphrased from the epic's `## What`, a What's included list of commits, a Manual verification link to the epic comment, and a Stats line.

### 5. Compose PR title

Use the epic title verbatim (with phase prefix if any), e.g. `P1.1 — Combat foundation: simulator + replay`. If the epic title is too generic to stand on its own, prefix with the epic ref: `[EMB-227] <title>`.

### 6. Open the PR

```bash
gh pr create \
  --title "<computed title>" \
  --body "<computed body>" \
  --base <base-branch> \
  --head <current-branch> \
  --draft   # unless --ready was passed
```

Capture the returned URL.

### 7. Output

```
PR: <URL> (draft)
Epic: <epic URL or ref>
Base: <base-branch>
Commits: <N>
Files: <N>
```

That's it. Do NOT attach the PR to the tracker manually — the magic-word phrase in the body handles that automatically.

## Do NOT

- Skip manual-test confirmation unless `--no-confirm` was explicitly passed.
- Mark a PR ready-for-review unless the user passed `--ready`.
- Create a PR if commits aren't pushed. Push first (with confirm) or halt.
- Include code snippets in the PR body. Body is summary only; code lives in the diff.
- Set reviewers / labels / assignees unless the user asked.
- Modify the tracker epic description. That's `forge:epic-close`.
- Delete the branch after PR open. Branch lives until merge.

## Integration with `forge:epic-close`

When `forge:epic-close` finishes its work, it asks: "Створити draft PR? (y / n)". On `y` it invokes this skill with `--no-confirm` (manual testing was the user's pre-condition for closing the epic in the first place). On `n` the skill isn't called; the user invokes manually whenever they want.

## Configuration

Default behavior — draft (always); base = `develop` if it exists else `main`; title = epic title; body = generated from epic + commits + epic comment URL; no reviewers, no labels. Override only via flags. No project-level config file.

## Edge cases

See `references/edge-cases.md` for: branch never pushed, multiple PRs closing the same epic, gh CLI unavailable, no GitHub remote, empty diff, epic ID undetectable, `tracker.json` missing.
