---
name: kit-create-feature
description: "Use when adding a new feature (e.g. profile / dashboard / settings / notifications). Scaffolds Bloc + repository + DTO + UI + tests under lib/src/features/<feature>/, wired through the feature barrel."
---

# kit-create-feature

## When to use

- Triggers: "новий feature", "create feature for X", "add bloc for X", `/kit-create-feature`.
- The work introduces a new user-visible feature inside `lib/src/features/` (or `lib/src/shared/` for cross-cutting utilities).
- The feature needs persisted state (Drift) OR cloud-backed state (Supabase) OR pure in-memory state — this skill covers all three.

Don't use when: adding a new Drift table only (`/kit-add-drift-table`), adding a Flame component only (`/kit-create-flame-component`), or adding a top-level feature folder that requires scaffold-level decisions (talk to the user).

## What this skill produces

- `lib/src/features/<feature>/presentation/blocs/<name>_bloc.dart` — `Bloc` (events) or `Cubit` (commands) class
- `lib/src/features/<feature>/presentation/blocs/<name>_event.dart` — sealed event hierarchy (Bloc only)
- `lib/src/features/<feature>/presentation/blocs/<name>_state.dart` — sealed state hierarchy
- `lib/src/features/<feature>/data/<name>_repository.dart` — repository returning `Result<T>`
- `lib/src/features/<feature>/data/<name>_dto.dart` — Drift / Supabase row ↔ domain mapping (only if persistence touches the boundary)
- `lib/src/features/<feature>/presentation/<name>_screen.dart` — Flutter widget consuming the Bloc
- Update `lib/src/features/<feature>/<feature>.dart` barrel — export ONLY the public symbols (Bloc class, state types, screen widget). Do NOT export internal DTOs.
- Mirroring `test/features/<feature>/blocs/<name>_bloc_test.dart`, `test/features/<feature>/data/<name>_repository_test.dart`

## Required inputs

- Feature folder name in snake_case (e.g. `profile`, `dashboard`, `settings`)
- Feature name in snake_case (e.g. `user_summary`, `item_picker`)
- Persistence flavor: `drift` / `supabase` / `none`
- One-line description of what the feature does

## Steps

1. Confirm the feature folder exists under `lib/src/features/`. If not, create it (or ask the user if this should live under `lib/src/shared/` instead).
2. Create the bloc files (`<name>_bloc.dart`, `<name>_event.dart`, `<name>_state.dart`). Events are `UpperCamelCase` action verbs (e.g. `LoadItems`, `SelectEntry`). States are `UpperCamelCase` descriptive (e.g. `ItemsLoaded`, `ItemsLoadFailed`). State classes extend a sealed `<Name>State` base.
3. Create the repository. Public methods return `Future<Result<T>>` and use `Result.guard(... onError: (e, _) => <Typed>InfraException(...))` to wrap external calls. The repository depends on a Drift DAO (injected) or `SupabaseClient` (injected) — never on `get_it` directly.
4. If persistence crosses a boundary, add a DTO with `fromRow` / `toCompanion` (Drift) or `fromJson` / `toJson` (Supabase). Domain types stay free of `*Companion`, `*Data`, and `Map<String, dynamic>`.
5. Create the screen. UI uses `BlocBuilder` / `BlocListener`. Strings come from `context.l10n.<key>` — add new keys via `/kit-add-localization`. Spacing / radius / typography come from `AppSpacing`, `AppRadius`, `AppTypography`.
6. Update `lib/src/features/<feature>/<feature>.dart` to export the bloc class, state types, and screen. Internal DTOs and repository implementations stay unexported.
7. Wire DI in `lib/src/app/composition_root.dart` if the bloc needs to be a long-lived singleton; otherwise create per-screen with `BlocProvider(create: (_) => <Bloc>(sl<Repo>()))`.
8. Write bloc tests with `bloc_test` (verify state transitions for each event) and repository tests with `mocktail` (verify `Result` shape on success and failure).
9. Run `dart run build_runner build --delete-conflicting-outputs` if any generated DTO files are involved.
10. Run `flutter analyze --fatal-warnings` and `flutter test` — both must pass before reporting done.

## Conventions

- Bloc file imports use `package:<project>/...` absolute paths. Cross-feature imports go through the other feature's barrel (`package:<project>/src/features/<other>/<other>.dart`).
- One bloc per feature, not per screen. If two screens share state, share the bloc.
- Repository methods are verbs (`loadItems`, `saveProfile`), not nouns.
- DTOs live next to the repository in the `data/` layer, not in `core/`.
- Tests for a feature live under `test/features/<feature>/`, mirroring the `lib/src/features/<feature>/` shape.

## Anti-patterns (don't do this)

- Throwing exceptions out of repository methods. Always wrap with `Result.guard`.
- Importing another feature's internals directly (e.g. `import 'package:<project>/src/features/profile/data/...'` from another feature). Go through the feature's barrel.
- Exposing Drift `*Companion` or `*Data` types in repository return values. Map to domain types inside the repository.
- Calling `sl<...>()` (get_it) inside a Bloc body. Inject dependencies through the constructor.
- Adding a hardcoded user-facing string in the screen. Run `/kit-add-localization` first, then reference `context.l10n.<key>`.

## Examples

Skeleton repository (Drift-backed):

```dart
class ProfileRepository {
  ProfileRepository(this._dao);
  final ProfileDao _dao;

  Future<Result<List<Profile>>> loadAll() => Result.guard(
    () async => (await _dao.all()).map(Profile.fromRow).toList(),
    onError: (e, _) => DriftFailure(detail: 'profile.loadAll', cause: e),
  );
}
```

## References

- `docs/04_tech/01_stack-overview.md` §3 (layering rules)
- `docs/04_tech/02_project-structure.md` §2 (feature folder layout)
- `docs/04_tech/03_data-architecture.md` (cross-feature dataflow)
- `lib/src/core/result/result.dart` (Result + guard helpers)
- `lib/src/core/errors/app_exception.dart` (sealed error hierarchy)
