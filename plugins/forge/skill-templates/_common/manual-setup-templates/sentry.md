## What

Create a Sentry organization (or reuse an existing one) and a Sentry project for `<project_name>`, then capture the DSN so error/crash reporting can be wired into the app. Project bootstrapped via `/project-init` on `<date>`.

## User actions

1. Open https://sentry.io and sign in (or create an account).
2. If you don't already have an organization, create one via **Create a new organization** during onboarding.
3. From the org sidebar, click **Projects → Create Project**.
4. Pick the platform that matches the app (Flutter / React / Node / Go / Swift / Kotlin / etc.). Sentry's wizard will pre-select an SDK.
5. Set:
   - **Project name**: `<project_name>` (or a flavour suffix, e.g. `<project_name>-dev`)
   - **Team**: your default team
   - **Alert frequency**: per your preference
6. After creation, copy the **DSN** from the project's onboarding screen (also available under **Settings → Projects → <name> → Client Keys (DSN)**).
7. Store the DSN in the project's secret/config layer — NOT committed to git unless your platform's convention allows it (DSNs are not strictly secret but treat them as config).
8. (Optional) Generate an **Auth Token** under **Settings → Account → Auth Tokens** if you plan to upload source maps / dSYMs / debug symbols from CI.
9. (Optional) Repeat steps 3-7 for a `<project_name>-prod` project so dev and prod errors stay separated.

## Acceptance

- Sentry project exists in the chosen org with name `<project_name>`.
- DSN is stored in the project's secret/config layer.
- A smoke test (e.g. throwing a test exception via `Sentry.captureException`) appears in the Sentry Issues feed within ~1 minute.
