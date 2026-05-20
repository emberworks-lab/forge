## What

Authenticate the local GitHub CLI (`gh`) so `/project-init`, the `/pr-create` skill, and other repo-touching automations can create repos, open PRs, and push branches without manual prompts. Bootstrapped via `/project-init` on `<date>`.

## User actions

1. Verify the GitHub CLI is installed:
   ```bash
   gh --version
   ```
   If missing, install via `brew install gh` (macOS) / `apt install gh` (Debian) / `winget install GitHub.cli` (Windows) — see https://cli.github.com.
2. Run the auth flow:
   ```bash
   gh auth login
   ```
3. Pick:
   - **GitHub.com** (unless using GitHub Enterprise — then choose that)
   - **HTTPS** as the preferred protocol
   - **Yes** to authenticate Git with your GitHub credentials
   - **Login with a web browser** (recommended) — paste the one-time code shown into the browser
4. After completion, verify:
   ```bash
   gh auth status
   ```
   You should see `Logged in to github.com as <username>` with token scopes including `repo` and `read:org`.
5. (Optional) If you'll create repos under an org, ensure your token has `admin:org` scope:
   ```bash
   gh auth refresh -s admin:org,workflow
   ```

## Acceptance

- `gh auth status` exits 0 and reports an authenticated user.
- `gh repo list --limit 1` succeeds (returns at least one repo or an empty list — both indicate auth is working).
- Your GitHub username is the one expected for `<project_name>` work.
