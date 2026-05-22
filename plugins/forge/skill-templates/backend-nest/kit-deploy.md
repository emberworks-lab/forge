---
name: kit-deploy
description: "Opt-in Fly.io deploy skill for the NestJS backend. Use when deploying to Fly.io, cutting a release, shipping to production, or diagnosing a boot crash."
---

# kit-deploy

> **Opt-in.** This skill is NOT a default step in every ticket. Invoke it explicitly when the project deploys to Fly.io and is ready to ship. If your project uses a different platform (Railway, Render, AWS, GCP, etc.), use this as a structural reference and adapt the platform-specific steps.

## When to use

- Triggers: "deploy", "ship to production", "release to fly", `/kit-deploy`.
- A deployed instance crashes on boot — usually a missing secret or an unapplied migration.

## What it produces

- A pre-flight verification (clean tree → lint → test → build → migration check)
- A Fly.io deploy of the current branch
- Applied database migrations (via the Fly release command)
- A post-deploy health + error-monitoring check

## Required inputs

- Fly app name (e.g. `<your-app>`) — set in `fly.toml`
- Fly region (e.g. `fra`, `iad`) — set in `fly.toml`
- Fly VM size (e.g. `shared-cpu-1x`) — set in `fly.toml`
- Health check URL (e.g. `https://<your-app>.fly.dev/health`)

## Steps

1. **Pre-flight gates** — abort if any fails:
   - `git status` — clean tree (the Docker image embeds whatever is on disk).
   - `npm run lint` — green.
   - `npm test` — green.
   - `npm run build` — compiles successfully (exit 0).
   - Migration check: confirm every `prisma/migrations/` directory is committed and `schema.prisma` is in sync.

2. **Secrets check** — for every new env var added since the last deploy, run:
   ```bash
   fly secrets set KEY=value --app <your-app>
   ```
   The Docker image contains **no `.env` file** — production config is entirely Fly secrets. A var the code reads but no secret provides causes a boot crash.
   Check currently set secrets (digest only, not values):
   ```bash
   fly secrets list --app <your-app>
   ```

3. **Migrations** — ensure every `prisma/migrations/` directory is committed alongside its `schema.prisma` change. Fly applies them automatically: the `[deploy] release_command` in `fly.toml` runs `npx prisma migrate deploy` in a pre-release VM **before** the new version serves traffic. This is the only place `migrate deploy` should run — never run it locally against production.

4. **Deploy:**
   ```bash
   fly deploy --app <your-app>
   ```
   Fly builds the multi-stage `Dockerfile`, pushes the image, and boots a VM in the configured region.

5. **Verify:**
   ```bash
   curl https://<your-app>.fly.dev/health
   # expect: { "status": "ok", "db": "ok" }
   fly logs --app <your-app>
   # expect: no boot errors
   ```
   Check your error-reporting dashboard (Sentry, Datadog, or equivalent) for any new release errors.

## Conventions

- Never deploy a dirty tree or with failing tests — the pre-flight gate is non-negotiable.
- `migrate deploy` is production-only (runs in the Fly release VM); `migrate dev` is local-only.
- New env var → add it to `.env.example` (documentation) **and** `fly secrets set` (runtime) in the same change.
- Deploy only from a clean, reviewed, merged commit on your default branch — not from feature branches.

## Anti-patterns

- Deploying from a feature branch with uncommitted work.
- Running `prisma migrate deploy` from your local machine against the production database.
- Adding an env var read in code without a matching Fly secret → the app crashes on boot.
- Skipping the health check and assuming green.
- Deploying with `npm test` red "because the failure looks unrelated".

## References

- `fly.toml` — app name, region, VM size, health check path (project-specific, not in template)
- `Dockerfile` — multi-stage build that Fly uses (project-specific)
- `.env.example` — documents every required env var
- `prisma/migrations/` — migration history; must be committed before deploy
- `src/main.ts` — health check endpoint registration
