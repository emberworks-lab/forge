# Architecture — Mobile Flutter

Architecture patterns for Flutter applications. Covers state management, layering,
persistence, game engine integration, and dependency injection.
General principles are in `00_general.md`.

---

## Layer Model

```
UI layer         lib/<domain>/ui/
    ↓  events (BlocProvider / BlocBuilder)
BLoC / Cubit     lib/<domain>/blocs/
    ↓  calls
Repository       lib/<domain>/persistence/  (interface in core/)
    ↓
Data sources     Drift DAOs / Supabase / HTTP
```

**Core layer** (`lib/core/`) is the shared infrastructure layer: `Result<T>`,
`AppException`, error tracking, theme tokens, shared utilities. It depends only on
`dart:core` and third-party pure-Dart packages. No Flutter widgets, no platform plugins.

**Domain core** (`lib/<domain>/core/`) holds pure Dart domain models, formulas,
and value objects. No persistence types, no framework types.

**Direction:** `ui` imports from `blocs`; `blocs` imports from `core` and `persistence`
interfaces; `persistence` implements the interface. Nothing points outward.

---

## Domain Barrel Rule

Every domain exposes a single barrel file: `lib/<domain>/<domain>.dart`.

```dart
// lib/quest/quest.dart  — the only public surface of the quest domain
export 'core/quest.dart';
export 'core/quest_status.dart';
export 'blocs/quest_bloc.dart';
```

Cross-domain imports MUST go through the barrel:
```dart
// Good
import 'package:myapp/quest/quest.dart';

// Bad — reaches into another domain's internals
import 'package:myapp/quest/core/quest_status.dart';
```

This rule is lint-enforced (`implementation_imports: error` in `analysis_options.yaml`).
Barrel files define the contract; implementation files are private details.

Within a domain, subdirectory imports are fine:
```dart
// Inside lib/quest/blocs/ — reaching into lib/quest/core/ is OK
import '../core/quest.dart';
```

---

## State Management

**`flutter_bloc` (BLoC / Cubit) — default.** State is emitted as an immutable stream.
Cubits for simple state; full BLoC with `Events` for complex, testable workflows.

```
BlocProvider  →  BlocBuilder / BlocListener / BlocConsumer
```

- One Bloc/Cubit per distinct screen or feature area.
- Blocs must not hold `BuildContext`. UI concerns are the caller's problem.
- Use `BlocListener` for one-shot side effects (navigation, snackbars).
- Use `BlocBuilder` for reactive UI rebuilds.

**Riverpod** is a valid alternative for apps leaning heavily on computed/derived state
and fine-grained rebuild control. Do not mix both in the same app.

**`setState`** is appropriate for purely local UI state (toggle, animation controller)
that does not leave the widget. Escalate to Cubit only when the state needs to survive
widget rebuilds or be shared.

---

## Error Handling: Result and AppException

All fallible operations across layer boundaries return `Result<T>`:

```dart
// core/result/result.dart
sealed class Result<T> {
  const Result();
}
class Ok<T>  extends Result<T> { final T value;  const Ok(this.value); }
class Err<T> extends Result<T> { final AppException error; const Err(this.error); }
```

**Never throw across layer boundaries.** Repositories return `Result<T>`.
BLoCs pattern-match on `Ok` / `Err` and emit the appropriate state.

All errors extend `AppException`:
- `DomainException` — business rule violations (validation, invariant failures).
- `InfraException` — infrastructure failures (network, DB, auth).

This gives a single error-handling path in the BLoC and a single entry point for
error tracking (`ErrorTracker.capture(e)`).

---

## Persistence

**Drift** — reactive SQLite ORM. Use for persistent game state (entities, progress,
inventory, history). All Drift types are confined to `lib/<domain>/persistence/`
and `lib/db/`. The domain BLoC talks to a repository interface, not to DAOs directly.

**SharedPreferences** — device-level settings only: locale, theme, feature flags.
Never store game state in SharedPreferences.

**SecureStorage** — authentication tokens and secrets managed by the auth layer.

**Drift migration rules:**
- Migrations are append-only. Never edit a shipped migration file.
- Bump `schemaVersion` and add a new `00NN_*.dart` file for each change.
- Use `step-by-step` migrations with explicit `Migrator` calls; avoid `createAll`.

---

## Dependency Injection

Use `get_it` as the service locator, wired at the composition root
(`lib/app/di/` or equivalent). DI setup runs before `runApp`.

```dart
// Composition root — register once
sl.registerLazySingleton<QuestRepository>(() => DriftQuestRepository(sl()));
sl.registerFactory<QuestBloc>(() => QuestBloc(sl()));
```

**Never call `GetIt.instance` inside a Flame component or a widget.** Pass dependencies
through constructors or BlocProvider. Flame components get state through `flame_bloc`
mixins — see below.

---

## Flame Integration

Flame components live in `lib/<domain>/ui/flame/`.

**State bridge:** Flame components consume Bloc state via `flame_bloc` mixins
(`HasGameBloc`, `HasGameRef`). They do **not** call `get_it` directly.

```dart
class HeroComponent extends PositionComponent
    with HasGameBloc<HeroBloc, HeroState> {
  @override
  void onNewState(HeroState state) {
    // React to state change
  }
}
```

**Direction:** Flame components are UI. They read state from Blocs and call Bloc `add()`
to push events. Business logic lives in BLoC and domain core, not in components.

Keep `FlameGame` subclasses thin: wiring and component lifecycle only.
Heavy computation (pathfinding, simulation) belongs in isolates or domain services.

---

## Localization

Use generated `AppLocalizations` (`context.l10n.<key>`). Never hardcode user-facing strings.

Run `flutter gen-l10n` after editing `.arb` files. The generated class is the only
contract between the UI and translations — no raw string keys in widget code.

---

## Theme Tokens

All spacing, typography, and radii come from design-system constants
(`AppSpacing`, `AppTypography`, `AppRadius`). Never use raw numeric literals in widget
layout. This enforces visual consistency and makes theme changes a single-file operation.

---

## Problem Signals

- A widget calls a repository or DAO directly — missing BLoC layer.
- `BuildContext` is stored in a Bloc or passed to a service — inverted dependency.
- A domain model imports a Drift table type or a Flutter widget — layer violation.
- Cross-domain import bypasses the barrel file — `implementation_imports` violation.
- `throw` used across layer boundaries instead of `Result<T>` — untyped error propagation.
- `get_it` called inside a Flame component — breaks the flame_bloc contract.
- Persistent game state stored in SharedPreferences — wrong storage tier.
- A migration file is edited after shipping — schema corruption risk.
- Business logic in widget `build()` methods — untestable and hard to change.
- A single Bloc manages multiple unrelated feature areas — cohesion violation.
