---
name: kit-add-drift-table
description: "Use when adding a new Drift table for persistent local state. Adds the table class, DAO with reactive queries, an append-only numbered migration, registers it in @DriftDatabase, bumps schemaVersion, and runs build_runner."
---

# kit-add-drift-table

## When to use

- Triggers: "нова таблиця", "add drift table", "new persisted entity", `/kit-add-drift-table`.
- The data is **persistent local state** (user profiles, settings snapshots, cached sessions, offline-capable records). NOT device-level preferences (locale, theme, debug flags) — those go in SharedPreferences. NOT secrets (handled by `supabase_flutter`'s SecureStorage).

## What this skill produces

- `lib/src/core/db/tables/<name>.dart` — `class <Name> extends Table { ... }`
- `lib/src/core/db/dao/<name>_dao.dart` — `@DriftAccessor` with companion-based writes and `watch*()` reactive queries
- `lib/src/core/db/migrations/00NN_<descriptor>.dart` — `Migration00NN<Descriptor>` extends `MigrationStep`
- Edits to `lib/src/core/db/migrations/migrations.dart` — append the new step to the const list (in version order)
- Edits to `lib/src/core/db/app_database.dart` — add the table to `@DriftDatabase(tables: [...], daos: [...])` and bump `schemaVersion`
- Edits to `lib/src/core/db/db.dart` barrel — export the new DAO if it's consumed outside `lib/src/core/db/`
- Generated `*.g.dart` files (re-run `build_runner`)

## Required inputs

- Table name in `UpperCamelCase` (singular Dart class) → SQL becomes snake_case (e.g. `UserProfiles` → `user_profiles`)
- Column list with types (per `docs/04_tech/04_drift-schema.md`)
- Whether the table needs FK indexes
- Migration descriptor (one-word kebab, e.g. `add_user_profiles`, `add_sessions`)

## Steps

1. Read `docs/04_tech/04_drift-schema.md` first — column types, naming, indexing rules are spelled out there.
2. Pick the next migration number: look at `lib/src/core/db/migrations/`, find the highest `00NN_` prefix, use `NN+1` zero-padded to 4 digits.
3. Create `lib/src/core/db/tables/<name>.dart` with the `Table` subclass. Use `IntColumn`, `TextColumn`, `DateTimeColumn`, etc. Foreign keys via `.references(OtherTable, #id)`. Defaults via `.withDefault(currentDateAndTime)` for timestamps.
4. Create `lib/src/core/db/dao/<name>_dao.dart` — `@DriftAccessor(tables: [<Name>])` class with `_$<Name>DaoMixin` mixin. Provide at least one `watch*()` Stream method for reactive UI consumers; one-shot methods (`get`, `insert`, `update`, `delete`) on top.
5. Create `lib/src/core/db/migrations/00NN_<descriptor>.dart` — class extends `MigrationStep`, `version` returns `NN`, `apply` calls `m.createTable(db.<tableName>)` (or `addColumn`, `renameTable`, etc. for later changes).
6. Edit `lib/src/core/db/migrations/migrations.dart` — append `const Migration00NN<Descriptor>()` to the list. **Order matters** — version N must sit at index N-1.
7. Edit `lib/src/core/db/app_database.dart` — add the table to `@DriftDatabase(tables: [..., <Name>], daos: [..., <Name>Dao])` and increment `int get schemaVersion` to `NN`.
8. Edit `lib/src/core/db/db.dart` barrel — export the DAO if any feature outside `lib/src/core/db/` will consume it.
9. Run `dart run build_runner build --delete-conflicting-outputs`. Verify `app_database.g.dart` and `<name>_dao.g.dart` are regenerated.
10. Run `flutter analyze --fatal-warnings` and `flutter test`.

## Conventions

- Class names: `UpperCamelCase` plural for table classes (`UserProfiles`, `Sessions`, `Settings`).
- SQL names: snake_case singular for columns. Drift derives table SQL name from the class name automatically.
- Timestamps: `DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();`
- Foreign keys: explicit `.references(...)` AND an index on the FK column for read-heavy joins.
- Repositories live in `lib/src/features/<feature>/data/`, not in `lib/src/core/db/`. The `db/` layer only owns table definitions, DAOs, and migrations.

## Anti-patterns (don't do this)

- **Editing an existing migration file.** Migrations are append-only. Need to fix a shipped table? Add a new migration that alters it.
- Forgetting to bump `schemaVersion`. The runner will silently skip the new step.
- Returning raw `<Name>Data` rows from DAOs to feature code. Map to domain types inside the feature's repository.
- Storing preferences (locale, theme mode, debug flags) in Drift. Those are device-level — use SharedPreferences. Account-level preferences that sync across devices may belong in Drift or Supabase.
- Using `Hive`, `Isar`, or `sqflite` directly. Drift is the only local persistence layer.
- Skipping `build_runner` and committing stale `*.g.dart` files. CI codegen-freshness gate will fail.

## Examples

Minimal table + DAO:

```dart
// lib/src/core/db/tables/user_profiles.dart
class UserProfiles extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get displayName => text().withLength(min: 1, max: 64)();
  TextColumn get email => text()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

// lib/src/core/db/dao/user_profiles_dao.dart
@DriftAccessor(tables: [UserProfiles])
class UserProfilesDao extends DatabaseAccessor<AppDatabase> with _$UserProfilesDaoMixin {
  UserProfilesDao(super.db);
  Stream<List<UserProfileData>> watchAll() => select(userProfiles).watch();
  Future<int> insertProfile(UserProfilesCompanion c) => into(userProfiles).insert(c);
}
```

Migration:

```dart
class Migration0002AddUserProfiles extends MigrationStep {
  const Migration0002AddUserProfiles();
  @override
  int get version => 2;
  @override
  Future<void> apply(AppDatabase db, Migrator m) async {
    await m.createTable(db.userProfiles);
  }
}
```

## References

- `docs/04_tech/04_drift-schema.md` (full DSL)
- `docs/04_tech/06_data-sync.md` (which fields sync to Supabase, which stay local)
- `lib/src/core/db/app_database.dart` (existing schema + migration wiring)
- `lib/src/core/db/migrations/migration_runner.dart` (how steps execute on upgrade)
