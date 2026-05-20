# Path details

Full step-by-step for each path in Step 2 of `forge:epic-close`.

## Path A — Merge to `<base>` now

1. **Simplify** with explicit consent — see Step 3a.
2. **Re-run tests-pass gate** (Step 0b — simplify can introduce regressions). If fails → halt.
3. **Authorization gate** (REQUIRED before any merge command):

   > "Готовий мерджити `<branch>` → `<base>`. Це незворотно з UI цієї сесії. (y / abort)"

   Only `y` permits merge. Anything else → exit, leave branch as-is.

4. **Squash + merge** per `plugins/forge/docs/conventions/git-workflow.md` — typically:

   ```
   git checkout <base>
   git merge --squash <branch>
   git commit -m '<epic merge message>'
   git push
   ```

   Compose the merge message from the epic title. Do NOT include a long body — the epic comment in Step 3c is the body.

5. **Verify merge succeeded** — `git log -1 <base>` shows the squash commit. Capture commit SHA for Step 4 output.
6. Proceed to shared follow-ups (Step 3).

## Path B — Open draft PR

1. **Simplify** with consent (Step 3a).
2. **Re-run tests-pass gate** post-simplify. If fails → halt.
3. Proceed to shared follow-ups (Step 3) — but the DRY comment + status update reference the PR URL once it exists.
4. Invoke `forge:pr-create <EPIC-ID> --no-confirm` (manual-test confirmation already happened at Step 0c). Capture PR URL.
5. Append the PR URL to the DRY comment posted in Step 3c (or post a follow-up comment if Step 3c already ran).
6. **Cloud code review (post-PR).** Use the PR number from the URL printed by `forge:pr-create` (e.g. `https://github.com/.../pull/42` → PR number `42`).

   > Запустити `/code-review <PR-number>` у chat input? (y / skip)

   - `y` → ask the user to type `/code-review <PR-number>` in their chat input and press Enter. If the `code-review` plugin is installed, it will run 5 parallel Sonnet agents on the PR diff and post an inline comment on the GitHub PR within ~60 s. If the plugin is missing, the slash command returns an unknown-command error — the user should note this and continue.
   - `skip` → continue without cloud review.

   **This step is non-blocking.** If the `code-review` plugin is missing or fails, merge can still proceed. If the plugin posts a "blocker" finding, it appears as a PR comment — triage is the author's responsibility, not epic-close's.

## Path C — Cleanup only

1. **Skip simplify** — the branch is being abandoned; no point reshaping it.
2. **Skip merge / PR.**
3. Proceed to shared follow-ups (Step 3) with adjustments:
   - DRY comment frames as "abandoned" / "deferred", not "delivered".
   - Status update (if posted) marks `health: atRisk` or `health: offTrack` and explains the pivot.
   - Docs sync still runs — stale claims about in-progress work need correction even on cleanup.
