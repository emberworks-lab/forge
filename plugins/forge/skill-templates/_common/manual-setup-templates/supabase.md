## What

Create a Supabase project for `<project_name>` and capture the connection credentials so the app can authenticate, persist data, and (optionally) sync saves. Project bootstrapped via `/project-init` on `<date>`.

## User actions

1. Open https://supabase.com/dashboard and sign in (or create an account).
2. Click **New project**. Set:
   - **Name**: `<project_name>` (or a flavour suffix, e.g. `<project_name>-dev`)
   - **Database password**: generate + store in your password manager
   - **Region**: closest to your primary user base
   - **Pricing plan**: Free tier is fine for bootstrap
3. Wait ~2 minutes for the project to provision.
4. Go to **Project Settings → API** and copy:
   - `Project URL`
   - `anon` public key
   - `service_role` secret key (handle with care — never commit)
5. (If two flavours / envs are needed) Repeat steps 2-4 for `<project_name>-prod`.
6. Store the values in the project's secret/config layer (`.env.local`, `--dart-define`, GitHub Actions secrets, etc.) — NOT committed to git.
7. Run a smoke connection test (e.g. `supabase status` after `supabase link`, or a one-shot client query).

## Acceptance

- Supabase project exists in your Supabase dashboard with name `<project_name>`.
- `Project URL` + `anon` key + `service_role` key are stored in the project's secret layer (not committed).
- A smoke test confirms the app can reach the Supabase API (e.g. anonymous SELECT or auth ping returns 200).
