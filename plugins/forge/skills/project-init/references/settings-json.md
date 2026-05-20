# settings.json defaults (step 7)

Create `<project>/.claude/settings.json`. The shape varies by stack but always includes an `permissions.allow` list of Bash commands and an `env` map for stack-specific defaults.

## Common shape

```json
{
  "permissions": {
    "allow": [
      "Bash(<stack-essential-1>)",
      "Bash(<stack-essential-2>)",
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ]
  }
}
```

## Per-stack essential commands

| Stack | Allow patterns to add |
|---|---|
| mobile-flutter | `Bash(flutter test:*)`, `Bash(flutter analyze:*)`, `Bash(dart format:*)`, `Bash(flutter pub get:*)`, `Bash(flutter pub add:*)`, `Bash(dart fix:*)`, `Bash(dart pub get:*)` |
| web-* (Node-based) | `Bash(pnpm test:*)`, `Bash(pnpm lint:*)`, `Bash(pnpm build:*)`, `Bash(pnpm dev:*)`, `Bash(pnpm typecheck:*)`. Swap `pnpm` for `npm` / `yarn` / `bun` per the user's preference. |
| backend-node | `Bash(pnpm test:*)`, `Bash(pnpm lint:*)`, `Bash(pnpm typecheck:*)`, `Bash(wrangler dev:*)` if Cloudflare. |
| backend-go | `Bash(go test:*)`, `Bash(go vet:*)`, `Bash(go build:*)`, `Bash(golangci-lint run:*)`. |
| backend-python | `Bash(pytest:*)`, `Bash(ruff check:*)`, `Bash(ruff format:*)`, `Bash(mypy:*)`. |
| backend-rust | `Bash(cargo test:*)`, `Bash(cargo clippy:*)`, `Bash(cargo fmt:*)`, `Bash(cargo build:*)`. |
| library-* | Stack-appropriate test / lint commands plus the publishing command. |

## MCP servers

If the user mentioned specific MCP integrations in step 2 (e.g. Supabase, Linear, Cloudflare), surface them by adding a comment line in the generated settings.json output pointing at `/update-config`.

## Read defaults

Settings.json may also include a sensible `permissions.deny` list for paths the user explicitly excluded (e.g. `.env*`, `secrets/`, `private/`). Ask before adding; defaults vary too much by team.

## Reminders

- Do not write secrets to `settings.json`. API keys / tokens belong in `.env.*` files (gitignored).
- The Flutter scaffolder owns its own settings.json — when this skill runs the Flutter path, this step is skipped.
- Suggest `/update-config` if the user wants finer-grained tuning (hooks, env vars, statusLine, etc.).
