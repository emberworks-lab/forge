# Credentials runbook — <project_name>

Env files, stub lifecycle, and per-flavor key management.

## .env policy

The scaffolder writes one `.env.<flavor>` per flavor (gitignored) and one
`.env.example` (committed, shape only). At runtime, values land in `AppConfig`
via `--dart-define-from-file=.env.<flavor>`.

## Stub-first credentials

Each integration has three lifecycle states, captured per-key in
`.claude/scaffold-report.json` under `credentials_resolution`:

| Mode      | What scaffolder did                                | What you do next                                            |
|-----------|----------------------------------------------------|-------------------------------------------------------------|
| `provide` | Wrote real values to `.env.<flavor>`               | Nothing — integration is live                               |
| `defer`   | Wrote workable stubs; emitted Mode M ticket        | Complete the Mode M ticket; replace stub values in `.env`   |
| `skip`    | Removed integration's deps/code from the project   | Nothing — integration is not part of this app               |

`AppConfig.isXStub` predicates (e.g. `isSupabaseStub`, `isSentryStub`) detect
defer mode at runtime. `lib/main_<flavor>.dart` already gates SDK init behind
those predicates and wraps remote calls in try/catch, so `flutter run` succeeds
out-of-the-box even before any keys are filled in.

## Replacing stub values

1. Locate the Mode M ticket for the integration in your task tracker backlog (P0 — Bootstrap).
2. Follow its `## User actions` to provision the service and capture credentials.
3. Edit `.env.<flavor>` — replace the stub value with the real one.
4. Restart `flutter run` — `AppConfig.isXStub` will return `false` and SDK init kicks in.
5. Close the Mode M ticket.

## Per-flavor key overrides

If dev and prod need different values for the same integration (e.g. separate
Supabase projects), edit `.env.dev` and `.env.prod` directly — the same key,
two different values, AppConfig pulls per-flavor automatically.
