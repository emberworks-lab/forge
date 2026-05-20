## What

Generate a Linear API key (Personal API Key) for any project tooling that needs to talk to Linear outside the Claude Code MCP integration — e.g. CI scripts, custom dashboards, status webhooks. Bootstrapped via `/project-init` on `<date>`.

## User actions

1. Open https://linear.app and sign in.
2. Go to **Settings → Account → API → Personal API keys**.
3. Click **Create key**. Set:
   - **Label**: `<project_name> tooling` (so you can revoke it later without affecting other integrations)
   - **Workspace**: the workspace that owns the `<project_name>` Linear project
4. Copy the key value — it is shown ONCE. If you lose it, revoke and recreate.
5. Store the key in the project's secret layer — typical locations:
   - Local dev: 1Password / your password manager + a `.env.local` reference (gitignored)
   - CI: GitHub Actions secret named `LINEAR_API_KEY` (or equivalent for your CI provider)
   - Never commit the raw key to git.
6. (Optional) Smoke-test the key with a `curl`:
   ```bash
   curl -H "Authorization: $LINEAR_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"query":"{ viewer { id name } }"}' \
        https://api.linear.app/graphql
   ```
   You should get back your own user record.

## Acceptance

- A Personal API key labelled `<project_name> tooling` exists under your Linear account API settings.
- The key is stored in your password manager AND wired into the project's secret layer (env var or CI secret) — not in git.
- The smoke `curl` returns a 200 with your viewer info.
