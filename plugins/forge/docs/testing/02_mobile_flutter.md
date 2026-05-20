# Testing — mobile (Flutter)

Augments `00_general.md` for Flutter+Dart projects. Assumes Bloc + Drift + Supabase but works for other Flutter stacks with minor adjustment.

## Stack mapping

| Layer | Tooling | Notes |
|---|---|---|
| Unit + widget | `flutter_test` (built-in) | Headless; no device needed |
| Bloc | `bloc_test` | `blocTest<B,S>(...)` matcher API |
| Mocking | `mocktail` | Use over `mockito` — null-safety friendly, no codegen |
| Property-based | `glados` | Universal generators + custom for domain types |
| Flame components | `flame_test` | `FlameTester`, `testWithFlameGame` |
| Drift schema/DAO | `drift_dev` test helpers | In-memory `NativeDatabase.memory()` |
| Golden | `flutter_test` (built-in `matchesGoldenFile`) | + `alchemist` for cross-platform stable goldens (optional) |
| Integration | `integration_test` (built-in) | Real device/emulator; we write but don't auto-run |
| HTTP/API mocking | `mocktail` against Supabase client interfaces | OR `http_mock_adapter` if using `dio` directly |

## Layer guidance

### Unit (pure Dart)

Files under `test/<domain>/` mirror `lib/<domain>/`. One `_test.dart` per source file.

```dart
void main() {
  group('CombatFormula.damageFor', () {
    test('returns 0 when attacker has 0 power', () {
      final result = CombatFormula.damageFor(power: 0, defense: 5);
      expect(result, 0);
    });

    test('caps at maxDamage when defense is 0', () {
      final result = CombatFormula.damageFor(power: 999, defense: 0);
      expect(result, lessThanOrEqualTo(CombatFormula.maxDamage));
    });
  });
}
```

### Bloc tests

Always use `bloc_test`. Verify state transitions, not Bloc internals.

```dart
blocTest<EnemyBloc, EnemyState>(
  'emits [Loading, Loaded] when LoadEnemies succeeds',
  build: () {
    when(() => mockRepository.loadAll()).thenAnswer(
      (_) async => const Result.ok(testEnemies),
    );
    return EnemyBloc(mockRepository);
  },
  act: (bloc) => bloc.add(const LoadEnemies()),
  expect: () => [
    const EnemiesLoading(),
    const EnemiesLoaded(testEnemies),
  ],
);
```

Cover at minimum: happy path + each error variant returned by the repository.

### Repository tests

Mock the DAO/API client with mocktail; verify:
- `Result.ok` shape on success path
- `Result.err` with the correct `AppException` subtype on each failure mode
- Boundary mapping (DTO → domain) is correct

```dart
test('loadAll wraps DAO exception as DriftFailure', () async {
  when(() => mockDao.all()).thenThrow(SqliteException(1, 'no such table'));
  final result = await repository.loadAll();
  expect(result.isErr, true);
  expect(result.err, isA<DriftFailure>());
});
```

### Widget tests

Test widget behavior, not widget tree shape. Pump with required providers (BlocProvider, MaterialApp).

```dart
testWidgets('shows error banner when bloc emits Error', (tester) async {
  await tester.pumpWidget(MaterialApp(
    home: BlocProvider<EnemyBloc>.value(
      value: enemyBloc,
      child: const EnemyListScreen(),
    ),
  ));
  enemyBloc.emit(const EnemiesError('network down'));
  await tester.pump();
  expect(find.text('network down'), findsOneWidget);
});
```

Query by:
1. `find.byKey(Key('combat-attack-button'))` — most stable
2. `find.byType(MaterialButton)` — type-based
3. `find.text('Attack')` — last resort, brittle to l10n

### Flame component tests

Use `flame_test`'s `testWithFlameGame` to spawn a game, add the component, simulate ticks.

```dart
testWithFlameGame('damage number floats up over 1s', (game) async {
  final dn = DamageNumberComponent(value: 42, position: Vector2(100, 100));
  await game.add(dn);
  await game.ready();

  final initialY = dn.position.y;
  game.update(1.0); // 1 second
  expect(dn.position.y, lessThan(initialY)); // floated up
});
```

Don't test `update(dt)` mutating Bloc state — Flame components should never write to Blocs.

### Drift tests

Use `NativeDatabase.memory()` for fast, isolated DB tests. Test schema migrations explicitly.

```dart
test('migration 0003 adds enemies.archetype column', () async {
  final db = AppDatabase.connect(NativeDatabase.memory());
  // Apply migration 0001 → 0002 → run migration 0003
  await migrations[2].up(db);
  final cols = await db.customSelect('PRAGMA table_info(enemies)').get();
  expect(cols.any((c) => c.read<String>('name') == 'archetype'), true);
});
```

### Property-based (glados)

Use for: combat formulas, RNG-driven systems given a seed (must be deterministic), drop table samplers, parsers.

```dart
Glados2(any.intInRange(1, 100), any.intInRange(0, 50)).test(
  'damage is non-negative and ≤ power',
  (power, defense) {
    final dmg = CombatFormula.damageFor(power: power, defense: defense);
    expect(dmg, greaterThanOrEqualTo(0));
    expect(dmg, lessThanOrEqualTo(power));
  },
);
```

### Golden tests

Limited to design-system widgets. Skip for full screens (too volatile).

```dart
testWidgets('PrimaryButton — disabled state', (tester) async {
  await tester.pumpWidget(_themed(const PrimaryButton(label: 'OK', onPressed: null)));
  await expectLater(
    find.byType(PrimaryButton),
    matchesGoldenFile('goldens/primary_button_disabled.png'),
  );
});
```

CI runs goldens; local update via `flutter test --update-goldens`. Cross-platform stability: consider `alchemist` package which normalizes font rendering.

### Integration tests

Live under `integration_test/`. **We write integration tests as code** for critical paths (save/sync, onboarding, complex multi-screen flows). **We do NOT auto-run them** — running on a real emulator is slow + flaky for orchestration.

User runs them manually via:
```bash
# iOS simulator
xcrun simctl boot <udid>
flutter test integration_test/save_sync_test.dart

# Android emulator
flutter emulators --launch <id>
flutter test integration_test/save_sync_test.dart
```

The `## Manual test cases` block in Linear may reference an integration test file the user can run.

## Test command outputs (for test-runner)

- `flutter test` — tap-style output; `--machine` flag for JSON-streamed events
- `flutter test --coverage` — generates `coverage/lcov.info`
- `flutter test test/<dir>/` — subset run; ~10x faster

The `test-runner` agent expects `flutter test` output by default; uses `--machine` when parsing structured failures.

## What "manual test cases" look like for Flutter mobile

```markdown
## Manual test cases (EMB-228)

- Run `flutter run --flavor dev -t lib/main_dev.dart`
- From main menu, navigate to Combat screen
- Tap "Attack" 3 times; expect damage events in the debug console (look for `[combat] dmg=...`)
- Verify HP bar visibly decreases on each hit
- Restart the app; expect combat state to reset (not persisted; bloc-only)
- On the Android emulator, rotate to landscape; expect HP bar layout to NOT overflow
- Optional: run `flutter test integration_test/combat_flow_test.dart` to verify the multi-turn flow end-to-end
```

## Common pitfalls

- **Forgetting `await tester.pump()`** after a state change — assertions race the rebuild
- **Testing `BuildContext.l10n` strings hardcoded** — l10n changes break tests; either use `Key`s or pin a locale in the test
- **Mocking Drift** — don't. Use `NativeDatabase.memory()`. Mocking generated code is fragile
- **Goldens checked in for screens** that change weekly — they'll get rubber-stamped on update. Restrict goldens to design-system primitives
- **Integration tests in CI without an emulator** — they'll hang. Either provision an emulator step or skip in CI

## Coverage discipline (Embergard reference targets, ADJUST per project)

Targets are descriptive, not enforced. Use them to spot gaps, not to fail PRs.

| Layer | Target | Reason |
|---|---|---|
| `lib/*/formulas/` | 90%+ | Pure functions; cheap to cover; high regression risk |
| `lib/core/` | 90%+ | Used everywhere; bugs propagate |
| `lib/*/blocs/` | 80%+ | State machines; happy + error paths |
| `lib/*/persistence/` | 80%+ | Boundary mapping; failure-mode coverage |
| `lib/*/ui/` | 50% | Widget tests on key states; not exhaustive layout |
| `lib/*/ui/flame/` | 50% | Component update + Bloc bridge |

## Skill integration

- `kit-create-feature` (project-local) scaffolds bloc + repository tests automatically
- `test-runner` agent runs tests on the orchestrator's behalf
- `execute-ticket` runs lint + relevant test subset; loops on failures (max 3)
- `execute-epic` adds a final full-suite pass before commit
