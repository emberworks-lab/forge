# Path details

Full step-by-step for each path in Step 7 of `forge:epic-close`.

**Note:** `forge:simplify-branch`, `forge:graph-refresh`, and `forge:review` already ran in Steps 1–3 BEFORE the user reached Step 7. The classifier-driven in-place edits from Step 6 may also have just landed. Each path below therefore picks up on a clean, simplified, reviewed branch. If Step 6 applied in-place edits, Step 0b was re-run at the end of Step 6 — paths below assume tests are green at entry.

## Path A — Merge to `<base>` now

1. **Authorization gate** (REQUIRED before any merge command):

   > "Готовий мерджити `<branch>` → `<base>`. Це незворотно з UI цієї сесії. (y / abort)"

   Only `y` permits merge. Anything else → exit, leave branch as-is.

2. **Squash + merge** per `plugins/forge/docs/conventions/git-workflow.md` — typically:

   ```
   git checkout <base>
   git merge --squash <branch>
   git commit -m '<epic merge message>'
   git push
   ```

   Compose the merge message from the epic title. Do NOT include a long body — the epic comment in Step 8b is the body.

3. **Verify merge succeeded** — `git log -1 <base>` shows the squash commit. Capture commit SHA for Step 9 output.
4. Proceed to shared follow-ups (Step 8).

## Path B — Open draft PR

1. Proceed to shared follow-ups (Step 8) — but the DRY comment + status update reference the PR URL once it exists.
2. Invoke `forge:pr-create <EPIC-ID> --no-confirm` (manual-test confirmation already happened at Step 0c). Capture PR URL.
3. Append the PR URL to the DRY comment posted in Step 8b (or post a follow-up comment if Step 8b already ran).
4. **Cloud code review (post-PR).** Use the PR number from the URL printed by `forge:pr-create` (e.g. `https://github.com/.../pull/42` → PR number `42`).

   > Запустити `/code-review <PR-number>` у chat input? (y / skip)

   - `y` → ask the user to type `/code-review <PR-number>` in their chat input and press Enter. If the `code-review` plugin is installed, it will run 5 parallel Sonnet agents on the PR diff and post an inline comment on the GitHub PR within ~60 s. If the plugin is missing, the slash command returns an unknown-command error — the user should note this and continue.
   - `skip` → continue without cloud review.

   **This step is non-blocking.** If the `code-review` plugin is missing or fails, merge can still proceed. If the plugin posts a "blocker" finding, it appears as a PR comment — triage is the author's responsibility, not epic-close's.

## Path C — Cleanup only

1. **Skip merge / PR.**
2. Proceed to shared follow-ups (Step 8) with adjustments:
   - DRY comment frames as "abandoned" / "deferred", not "delivered".
   - Status update (if posted) marks `health: atRisk` or `health: offTrack` and explains the pivot.
   - Docs sync still runs — stale claims about in-progress work need correction even on cleanup.

Note: simplify/review ran in Steps 1–3 even for Path C. If the user knew at Step 0c they were going to cleanup-only, they should have answered `not yet` to the manual-test prompt and exited early. Once past Step 0c, Steps 1–6 run regardless of path — the cleanup framing only applies to the follow-ups.
