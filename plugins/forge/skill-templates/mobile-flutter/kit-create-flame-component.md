---
name: kit-create-flame-component
description: "Use when adding a new Flame component or FlameGame. Wires the component through flame_bloc to a Bloc/Cubit, places files under lib/src/features/<feature>/presentation/flame/, and adds a flame_test."
---

# kit-create-flame-component

## When to use

- Triggers: "новий flame component", "create scene", "new flame game", `/kit-create-flame-component`.
- Adding visual / interactive canvas content: animated game scenes, sprite-based overlays, canvas-rendered UI elements.
- The component needs to react to Bloc state (the typical case — Flame is the renderer, Bloc is the source of truth).

Don't use when: adding plain Flutter widgets (use `/kit-create-feature`), or adding pre-computed simulation logic (that's pure-Dart `core/` work, not Flame — see `docs/04_tech/adr/0005`).

## What this skill produces

- `lib/src/features/<feature>/presentation/flame/<name>_component.dart` — `PositionComponent` (or appropriate superclass) with `FlameBlocListenable` mixin
- `lib/src/features/<feature>/presentation/flame/<name>_game.dart` — `FlameGame` subclass (only if a new game container is needed; reuse existing games when possible)
- `test/features/<feature>/presentation/flame/<name>_component_test.dart` — `flame_test` verifying the component reacts to bloc state changes

## Required inputs

- Feature folder (e.g. `dashboard`, `profile`, `map_view`, ...)
- Component name in snake_case (e.g. `progress_bar`, `avatar_sprite`)
- Bloc / Cubit type that drives the component's state
- Whether the component is added to an existing FlameGame or needs its own

## Steps

1. Read `docs/04_tech/01_stack-overview.md` §8 (Flame discipline) before starting. Key invariant: `update(dt)` is for cosmetic animation only — never mutate Drift / Bloc / domain state inside it.
2. Locate (or create) the FlameGame that will host the component. If creating a new game, place it next to the component (`<name>_game.dart`).
3. Create the component file. Component class extends the right Flame superclass (`PositionComponent`, `SpriteComponent`, `TextComponent`, etc.) and mixes in `FlameBlocListenable<TheBloc, TheState>` so `onNewState(state)` fires on every bloc change.
4. Place the component inside a `FlameBlocProvider<TheBloc, TheState>.value(value: bloc, children: [component])` (when injecting an existing bloc) or `FlameBlocProvider(create: () => TheBloc(...))` (when the bloc lives only as long as the game).
5. Document the component's coordinate space at the top of the file: world-space vs screen-space, anchor, what the position represents.
6. Add a `flame_test` that pumps the game, dispatches a bloc event, and asserts the component's visual state changed (e.g. text content, position, sprite frame).
7. Run `flutter analyze --fatal-warnings` and `flutter test`.

## Conventions

- File layout: every Flame asset lives under `lib/src/features/<feature>/presentation/flame/`. Plain Flutter widgets go in `lib/src/features/<feature>/presentation/` (sibling).
- Constructor injection only. Components receive their dependencies as constructor args — no `sl<...>()` lookups inside the component.
- Text rendering: use Flame's `TextPaint` + `TextStyle` from `package:flutter/painting.dart`. Don't pull `package:flutter/material.dart` into Flame files.
- Components consuming bloc state mix in `FlameBlocListenable` (passive listener) or `FlameBlocReader` (one-shot read in `onLoad`). Never `BlocProvider.of(context)` — there's no `BuildContext` inside Flame.
- A FlameGame should expose its dependencies via constructor — `DashboardGame({required this.counterCubit})` is the reference pattern (see `lib/src/features/dashboard/presentation/flame/dashboard_game.dart`).

## Anti-patterns (don't do this)

- Mutating Bloc state from `update(dt)`. The render loop is read-only against application state.
- Reading from `get_it` inside the component. Inject through the constructor (or via `FlameBlocProvider` for blocs).
- Using Flutter `material.dart` types (`TextStyle` from material, `ThemeData`, etc.) inside Flame components. Material is for the widget tree.
- Placing a Flame component outside `lib/src/features/<feature>/presentation/flame/`. Layering rules require the engine code to live in the presentation layer of its owning feature.
- Hardcoding canvas / screen dimensions. Read from `game.size` or accept dimensions via constructor.

## Examples

Bloc-listening text component:

```dart
class ScoreTextComponent extends TextComponent
    with FlameBlocListenable<DashboardBloc, DashboardState> {
  ScoreTextComponent()
    : super(text: '—', anchor: Anchor.topLeft, textRenderer: _renderer);

  static final _renderer = TextPaint(
    style: const TextStyle(fontSize: 24, color: Color(0xFFFFFFFF)),
  );

  @override
  void onNewState(DashboardState state) {
    if (state is DashboardLoaded) text = '${state.score}';
  }
}
```

Wiring inside a FlameGame:

```dart
@override
Future<void> onLoad() async {
  await add(
    FlameBlocProvider<DashboardBloc, DashboardState>.value(
      value: dashboardBloc,
      children: [ScoreTextComponent()..position = Vector2(8, 8)],
    ),
  );
}
```

## References

- `docs/04_tech/01_stack-overview.md` §8 (Flame discipline + render-loop invariant)
- `docs/04_tech/adr/0005` (pre-computed simulation, not realtime tick)
- `lib/src/features/dashboard/presentation/flame/dashboard_game.dart` (reference FlameGame)
- `lib/src/features/dashboard/presentation/flame/score_text_component.dart` (reference `FlameBlocListenable` use)
- flame_bloc docs: <https://pub.dev/packages/flame_bloc>
