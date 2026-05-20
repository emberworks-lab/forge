# mobile-flutter interview

The Flutter path runs the 26-question scaffolder interview (tooling docs not migrated — deleted in EPIC E, 8 phases) rather than this short list. Use this file as a reference for the dimensions that interview covers; the actual question text lives in the scaffolder script.

## Dimensions covered

- **Project shape** — name, bundle id, description, layout (inline `lib/core/` vs `packages/shared_core/`).
- **State management** — Bloc / Riverpod / Provider / setState.
- **Persistence** — Drift / Isar / Hive / SharedPreferences only.
- **Backend / cloud** — Supabase / Firebase / custom REST / none.
- **Auth** — Keycloak / Supabase Auth / Firebase Auth / none.
- **DI** — `get_it` / `injectable` / manual.
- **Game / Flame** — yes / no (drives `kit-create-flame-component`).
- **Environments** — dev / staging / prod, IDE configs (`.vscode/launch.json`, `.idea/runConfigurations/<Flavor>_<Mode>.xml`).
- **Credentials** — per-integration `provide` / `defer` / `skip` (FORGE-5.4).

## Generated kit-* skills (filtered by interview answers)

- `kit-create-feature.md` (always)
- `kit-add-drift-table.md` (or stack equivalent based on persistence answer)
- `kit-add-localization.md` (always)
- `kit-create-flame-component.md` (only if Flame = yes)
- `kit-deploy.md` (always)

## Defaults (current best practice)

Bloc + go_router + Drift + Supabase + Keycloak auth + `get_it` + `very_good_analysis` lints. The scaffolder swaps these per the interview answers.

## See also

- `references/flutter-scaffolder.md` — the full pipeline orchestration.
<!-- TODO: linting docs not migrated, deleted in EPIC E; flutter-scaffolder-interview.md was in tooling/ which is out of scope -->
