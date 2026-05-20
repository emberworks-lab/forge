# Edge cases for `forge:pr-create`

- **Branch never pushed.** Confirm with the user, then `git push -u origin <branch>`. If user declines, halt cleanly — no PR without commits on the remote.
- **Multiple PRs would close the same epic.** The tracker handles multiple magic-word references gracefully (only the first merging to default closes the issue). Warn the user: "you already have an open PR for this epic at <url>. Proceed anyway, update body, or stop?"
- **gh CLI not installed / not authenticated.** Halt with a pointed message: "install `gh` (https://cli.github.com) and run `gh auth login`."
- **Repo has no GitHub remote.** Halt: "this repo has no `origin` GitHub remote; can't create a GitHub PR. Configure the remote first."
- **Empty diff between base and HEAD.** Halt: "no commits between `<base>` and `HEAD`; nothing to PR. Either `git pull` if base moved, or check you're on the right branch."
- **Epic ID can't be detected from branch and was not provided.** Ask once: "Which epic? Pass the ref (e.g. `EMB-227`) or `--from-branch` from a branch named `feature/<prefix>-<N>-<slug>`."
- **`tracker.json` missing.** Fall back to current Linear-MCP behavior (the dispatch note at the top of `SKILL.md` covers this). The fallback exists for legacy repos.
- **Base branch out of date locally.** Don't auto-pull. If `git log --oneline <base>..origin/<base>` shows new commits on the remote base, warn the user — base is what GitHub will diff against, not your local copy.
- **Title looks generic** (e.g. just "tidy up", "wip"). Prefix with the epic ref: `[EMB-227] <title>`. The PR list page becomes browsable.
- **User passes `--ready` for a half-done epic.** Trust the user, but the manual-test confirmation gate still applies unless they also pass `--no-confirm`.
- **Existing PR on this branch.** `gh pr list --head <branch>` already detected it in Step 1. Ask once: "Update the existing PR body, skip, or close & reopen?" Don't silently overwrite.
- **PR body composition fails** (e.g. epic body has no `## What`). Fall back to a one-line summary: "See epic <ref> for context." Don't halt for missing optional sections — the magic-word phrase is what matters for auto-close.
