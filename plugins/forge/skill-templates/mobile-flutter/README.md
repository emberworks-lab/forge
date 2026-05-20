# skill-templates / mobile-flutter

Reusable Flutter skill skeletons. Copied to a new project by `/project-init` when stack=`mobile-flutter`.

## Inventory

| File | Purpose |
|---|---|
| `kit-create-feature.md` | Bloc + repository + DTO + UI + tests scaffold |
| `kit-add-drift-table.md` | Drift table + DAO + numbered migration + schemaVersion bump |
| `kit-add-localization.md` | ARB key + `flutter gen-l10n` + call-site swap |
| `kit-create-flame-component.md` | Flame component + flame_bloc bridge + test |
| `kit-deploy.md` | Build dev/prod APK + iOS artifacts |

## Origin + status

These were copied verbatim from the Embergard project. They contain Embergard-specific assumptions:

- `Result<T>` / `AppException` from `package:embergard/core/core.dart`
- Domain barrel pattern (`lib/<domain>/<domain>.dart`)
- `AppSpacing` / `AppRadius` / `AppTypography` theme tokens

When `/project-init` copies these into a new Flutter project, it should:

1. Replace `package:embergard/...` references with the new project's package name
2. Decide if the project uses `Result<T>` / sealed errors (most should — it's a good pattern); if not, generic-ify the error wrappers
3. Decide if the project uses domain barrels; if not, simplify the import section
4. Remove `kit-create-flame-component.md` if the project doesn't use Flame

## Generic-ifying roadmap

Not done yet. When the second Flutter project lands (Volatilance mobile?), we extract the shared parts into truly generic templates and keep Embergard-specific deltas as overrides in the project's `.claude/skills/`.

## What lives elsewhere

- `kit-add-content.md` (Embergard JSON content schema) — stays project-local; not generalizable
- `kit-update-docs.md` — global, in `~/.claude/commands/`
- tracker skills (`/create-epic`, `/execute-epic`, etc.) — global

## Linked global rules

Skills in this folder follow:
- `~/.claude/docs/testing/00_general.md` + `02_mobile_flutter.md` for test discipline
- `~/.claude/docs/linting/00_general.md` + `02_mobile_flutter.md` for lint
- `~/.claude/docs/conventions/tracker-tickets.md` for ticket bodies
