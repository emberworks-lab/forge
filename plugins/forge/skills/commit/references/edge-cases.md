# Edge cases for `forge:commit`

## Ref-resolution failures

- **No ticket ID provided and detection fails.** Halt cleanly: "Couldn't detect a ticket reference. Tell me the ticket ID (e.g. `EMB-42`) or run `/create-ticket` first."
- **User-supplied ref shape doesn't match the backend.** E.g. `tracker.json` says `github` but user types `EMB-42`. Ask: "tracker.json says backend is `github`; that ref looks Linear-shaped. Use this ref against `linear`, or switch to github (numeric)?" Don't silently coerce.
- **Multiple prefix candidates in git log** (e.g. `EMB-` and `IF-` both recent). Show the candidates, ask which one applies.

## Mixed staged-and-unstaged state

- Show both `git diff --cached` and `git diff` in the summary so the user sees what's about to ship.
- If the user explicitly said "commit everything", confirm once before staging unstaged files.
- Never `git add -A` — always stage by path. Untracked files at the repo root are particularly risky.

## Secrets-shaped files

If any of these are in the staged or about-to-stage set, halt and ask:

- `.env`, `.env.*`, `*.secrets`, `secrets.*`
- `credentials.json`, `service-account*.json`
- `id_rsa`, `*.pem`, `*.key`
- Anything containing `BEGIN PRIVATE KEY` or `BEGIN OPENSSH PRIVATE KEY` in its diff

User opt-in is the only way to commit them. Default is no.

## Multi-ticket commits

A single commit that closes multiple tickets is allowed when the changes are genuinely cross-cutting. Format: `Implements EMB-42, EMB-43: <description>`. Mixing kinds in one subject (e.g. `Implements EMB-42, Refs EMB-43`) isn't supported by GitHub's keyword parser, so split into two commits instead.

## `tracker.json` malformed

If the file exists but doesn't parse, halt with the parse error and tell the user to fix it or delete it (the missing-file path is well-defined; the malformed path is not).

## Backend recipe missing

If `plugins/forge/docs/tracker-backends/<backend>.md` is missing or lacks the `## commit_close_phrase` section, halt with: "Backend recipe for `<backend>` not found at `<expected path>`. Migrate `tracker.json` to a supported backend or delete it to fall back to the legacy Linear path."

## Pre-commit hook fails

If the commit fails because a pre-commit hook rejected it, do NOT amend. Fix the underlying issue (the hook output tells you what); re-stage; create a NEW commit. Amending after a hook failure modifies the wrong commit (the previous one) and silently destroys work.

## User wants to skip hooks

Never pass `--no-verify` unless the user explicitly asks for it. If a hook is failing, investigate; don't bypass.
