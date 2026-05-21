# Pilot Design — Flutter + Patrol on Embergard

**Date:** 2026-05-21
**Status:** Design only. No implementation in this doc.
**Inputs:** `mobile-e2e-survey.md` (#86) §1 Patrol, `mobile-e2e-matrix.md` (#87) §1/§2 Flutter row.
**Target project:** `~/Development/emberworks_lab_projects/embergard-rpg/embergard-mobile/` (Flutter 3.10+, flame, flame_bloc, supabase_flutter).
**Output of pilot:** a decision — proceed to a full `forge:e2e-mobile-flutter` skill or abandon the approach.

---

## 1. Why Patrol for this project

Three bullets, drawn from the #87 matrix Flutter row and #86 §1:

- **Grey-box widget + native access in one Dart test.** Patrol compiles into the Embergard binary and exposes both the Flutter widget tree and the host OS. A Maestro/Appium flow can only see the accessibility tree — it silently passes when accessibility IDs are missing (#86 §2 pitfall). Embergard already has bloc-driven onboarding, hub, combat, and supabase sync — many flows depend on permission dialogs (push, notifications), supabase OAuth deep links, and secure storage prompts. Patrol covers those without escaping to a second tool.
- **No WebDriver round-trip; fast inner loop.** Tests run in-process (#86 §1 speed). For an idle-RPG with frequent timer/ticker logic, the absence of HTTP overhead between every step matters; Patrol's hot-restart further compresses iteration during authoring.
- **Out-of-box CI compatibility.** Patrol ships compatible with Firebase Test Lab, BrowserStack, LambdaTest, AWS Device Farm, and emulator.wtf (#86 §1 setup). That keeps CI integration cost modest compared to Detox or Appium — relevant because Embergard currently has no mobile CI tier at all, so cheap onboarding matters.

---

## 2. Setup steps

All commands assume cwd is `~/Development/emberworks_lab_projects/embergard-rpg/embergard-mobile/`. Pin versions explicitly — see §7 Risks for the rationale.

```bash
# 1. Install the Patrol CLI (global Dart tool).
dart pub global activate patrol_cli 4.5.0

# 2. Add dev dependencies. Pin to 4.5.x to match the CLI.
flutter pub add --dev patrol:^4.5.0
flutter pub add --dev integration_test --sdk flutter

# 3. Scaffold Patrol's per-platform glue (writes
#    android/app/src/androidTest/.../MainActivityTest.kt and
#    ios/RunnerUITests/RunnerUITests.swift).
patrol bootstrap

# 4. Add the canonical first test (see §4).
mkdir -p integration_test
$EDITOR integration_test/onboarding_test.dart

# 5. Smoke-run against an iOS simulator and Android emulator.
patrol test -t integration_test/onboarding_test.dart --device "iPhone 16"
patrol test -t integration_test/onboarding_test.dart --device emulator-5554
```

Pre-reqs the developer must already have:
- Xcode 16.x + at least one iOS simulator booted
- Android Studio + an emulator AVD (API 34+ recommended)
- A working `flutter doctor` (no red entries for the target platforms)

---

## 3. Project structure changes

What Patrol adds to the Embergard repo (no files modified outside these paths):

```
embergard-mobile/
  integration_test/                  # NEW — Patrol test entry points
    onboarding_test.dart             # first spec (§4)
    hub_navigation_test.dart         # follow-up
    test_helpers/
      bootstrap.dart                 # shared setUp / app pumping
  android/app/src/androidTest/
    java/.../MainActivityTest.kt     # NEW — written by `patrol bootstrap`
  ios/RunnerUITests/
    RunnerUITests.swift              # NEW — written by `patrol bootstrap`
    Info.plist                       # NEW
  patrol.yaml                        # NEW — Patrol-level config (app id, bundle id, timeouts)
  pubspec.yaml                       # MODIFIED — adds patrol + integration_test to dev_deps
  android/app/build.gradle           # MODIFIED — adds androidTestImplementation block
  ios/Podfile                        # MODIFIED — adds Patrol pod target if iOS pods are vendored
```

No changes to `lib/`. No changes to the production build configuration. Patrol's footprint stays in test-only paths and platform manifests for the test runner.

---

## 4. First spec example

A Patrol test against Embergard's onboarding flow — the user pumps the dev entry point, taps through the welcome screen, picks a starting class, lands on the hub, and verifies the hub HUD is rendered. Uses real widget keys; uses `$.native` to dismiss an OS notification permission prompt that Embergard requests on first launch.

```dart
// integration_test/onboarding_test.dart
import 'package:flutter/material.dart';
import 'package:patrol/patrol.dart';
import 'package:embergard/main_dev.dart' as app;

void main() {
  patrolTest(
    'new player completes onboarding and lands on hub',
    ($) async {
      // Launch the dev variant (uses test supabase project + seeded data).
      await app.main();
      await $.pumpAndSettle();

      // Welcome screen.
      await $(#onboarding_welcome_continue).tap();

      // Native notification permission prompt — Patrol drives the OS dialog.
      if (await $.native.isPermissionDialogVisible()) {
        await $.native.grantPermissionWhenInUse();
      }

      // Class selection.
      await $(#onboarding_class_ember_warden).tap();
      await $(#onboarding_class_confirm).tap();

      // Name entry.
      await $(#onboarding_name_field).enterText('Pilot');
      await $(#onboarding_finish).tap();

      // Hub screen — verify HUD widgets pumped.
      await $(#hub_hud_root).waitUntilVisible();
      expect($(#hub_hud_currency_ember), findsOneWidget);
      expect($(#hub_hud_xp_bar), findsOneWidget);
    },
  );
}
```

Notes on the spec:
- Uses `main_dev.dart` (Embergard already separates dev/prod entry points) so the test hits the dev supabase project, not prod.
- Widget keys (`#onboarding_welcome_continue`, etc.) are aspirational — the pilot scope includes adding stable `Key('...')` props to those widgets if missing. This is the `testID`-discipline cost called out in the #87 matrix cross-cutting notes.
- `$.native` is the Patrol 4.0 redesigned API (#86 §1 known pitfalls — do not use deprecated `native`/`native2`).

---

## 5. Forge integration

How the future `forge:e2e-mobile-flutter` skill wraps the above. Pattern parallels `forge:e2e-web` (EPIC H #80) and the cross-cutting plugin notes in #87 §4.

- **Spec discovery.** Skill scans `integration_test/*_test.dart` for files containing `patrolTest(`. Mirrors how `forge:e2e-web` discovers `*.e2e.spec.ts` in `tests/e2e/`.
- **Config file.** Project opts in via `<project>/.claude/e2e-mobile.json` (parallel to `.claude/e2e.json` for web):
  ```json
  {
    "framework": "patrol",
    "entry_point": "lib/main_dev.dart",
    "android_device": "emulator-5554",
    "ios_device": "iPhone 16",
    "default_timeout_seconds": 120
  }
  ```
- **Runner subagent.** Sonnet, mechanical — invokes `patrol test -t <file> --device <device>` per spec, parses JSON output, reports pass/fail. Same model declaration as the web runner.
- **TDD integration.** When `forge:tdd` runs in a Flutter project with `e2e-mobile.json` present, the red phase writes a failing `patrolTest`, the green phase loops `patrol test` until pass. Build latency (see §6) means the loop is slower than widget-test TDD — skill warns the user to keep e2e specs coarse-grained and rely on widget tests for fine assertions.
- **Manual-setup module.** `plugins/forge/skills/<skill>/references/manual-setup-patrol.md` documents §2 setup as a one-shot the user runs during `forge:project-init`. Skill itself never runs `patrol bootstrap` (writes platform files — outside the autonomy envelope).
- **Template wiring.** The `flutter-app` kit gains an opt-in `patrol` module under `plugins/forge/skill-templates/flutter-app/opt-in/patrol/`, listed in that template's `OPT_IN_MODULES.md`. Mirrors the `web-nextjs` Playwright opt-in pattern already documented in `plugins/forge/skill-templates/web-nextjs/OPT_IN_MODULES.md`.
- **Deprecated-API detector.** Skill greps the project for `native2.` or `nativeAutomator.` (Patrol < 4.0 surfaces) and warns to migrate to `$.native` / `platform` — see #86 §1 known pitfalls.
- **`forge:epic-close` gate.** Treated identically to web e2e: epic close fails if any `*_test.dart` under `integration_test/` is failing or skipped without an explicit `@Skip('reason')` annotation.

---

## 6. CI integration

Patrol needs a real device or emulator — `flutter test` alone is not enough. Three viable shapes; pick one in the pilot.

| CI shape | Pros | Cons | Cost signal |
|---|---|---|---|
| **GitHub Actions self-hosted macOS + AVD** | Free-er than FTL once a runner exists; full control. | macOS runner uptime + AVD boot adds ~3–5 min per job; flakier than managed farms. | One-time runner setup; ongoing energy/maintenance. |
| **Firebase Test Lab** | Patrol ships FTL-compatible out of the box (#86 §1); real devices; parallelisation across device matrix. | Per-minute billing; iOS-on-FTL coverage shallower than Android. | Pay-per-minute; modest at pilot volume. |
| **emulator.wtf (Android-only)** | Fastest Android emulator CI in the ecosystem; Patrol-compatible per #86 §1. | Android-only; iOS still needs a separate path. | Pay-per-minute; cheaper than self-hosted for low volume. |

Recommended pilot shape: **FTL for iOS + emulator.wtf for Android**, with a smoke-only matrix (one device per platform). Cost-conscious; exercises both compatibility paths Patrol advertises.

Build-cache strategy is non-negotiable. Each Patrol run compiles a debug/profile APK + IPA (#86 §1 known pitfalls). Without caching, a smoke run is ~10–15 min cold. Pilot must measure cold-vs-warm to confirm caching pays off.

CI must run only the smoke tier on every PR (single onboarding spec ≤ 2 min on warm cache). Full regression runs nightly or on demand — Embergard's idle-RPG release cadence does not justify full-regression-per-PR cost.

---

## 7. Risks and unknowns

Concrete failure modes the pilot must measure or resolve.

- **Maintainer concentration.** Patrol is LeanCode-only — no second corporate sponsor. v4.5.0 March 2026 is the latest signal of life (#86 §1). If LeanCode pivots, the framework stalls. Mitigation: pin to a known-good 4.5.x patch range; keep `patrol_cli` upgrade gated behind explicit user action; document an exit ramp to Maestro (#87 §3 Flutter break-the-rec).
- **Version pinning needs.** Patrol couples CLI ↔ Dart package ↔ platform bootstrap files. Mismatch = silent breakage. Pilot must pin: `patrol_cli 4.5.0`, `patrol: ^4.5.0` in pubspec, and document the upgrade procedure (re-run `patrol bootstrap` after bumps).
- **Patrol 4.0 API churn.** The deprecated `native`/`native2` API was replaced by `platform` in 4.0 (#86 §1 known pitfalls). Embergard has no prior Patrol code, so this is not a migration cost here — but the `forge:e2e-mobile-flutter` detector (see §5) protects future projects that might.
- **Build latency vs. TDD cadence.** Patrol requires a debug binary per run. On a cold cache, a single onboarding spec is ~3–4 min on simulator, ~5–7 min on emulator. This is incompatible with sub-second red-green-refactor. The skill must steer e2e specs to coarse flows and rely on widget tests for fine-grained TDD — open question is how `forge:tdd` enforces or signals this.
- **Simulator/emulator strategy.** iOS Simulator is fine for most flows but cannot test real push notifications, real biometric prompts, or real WebView system dialogs in all variants. Android emulator behaves similarly. Pilot scope is simulator-only; real-device coverage is a follow-up (likely via FTL).
- **Flame engine + Patrol interaction.** Embergard uses `flame` and `flame_bloc`. Patrol's finder syntax targets Flutter widgets; Flame renders inside a `GameWidget`. Hub/HUD widgets surrounding the game canvas are testable, but in-game interactions (taps on Flame components) require Flame's own test harness or coordinate-based taps. Pilot scope: HUD/menu/onboarding flows only. Combat/world flows are out of scope until a Flame-aware approach exists.
- **Supabase auth + secure-storage prompts.** First-launch supabase init may trigger a keychain prompt on iOS. Patrol's `$.native` should handle it, but unverified for Embergard's specific auth flow. Pilot must confirm.
- **Patrol Web is not in scope.** Embergard has no web build target. If one is added later, the survey's caveat about early-stage Patrol Web (#86 §1) applies — re-evaluate then.

---

## 8. Pilot success criteria

How the user judges whether to proceed to a full `forge:e2e-mobile-flutter` skill. All criteria must hold; any single failure means re-scope or abandon.

1. **One spec, two platforms, green.** The §4 onboarding spec runs and passes on both iOS Simulator and Android emulator from a clean `patrol bootstrap`. Re-run 5 times consecutively — must pass 5/5.
2. **Cold-run time ≤ 10 min, warm-run time ≤ 3 min** for the §4 spec on a developer laptop (Apple Silicon, no CI). If warm runs exceed 3 min, the TDD integration story collapses and the recommendation flips toward widget-test-only for Embergard.
3. **Native permission prompt handled by Patrol.** The notification permission step in §4 must be driven by `$.native` without falling back to platform-specific Swift/Kotlin glue. If `$.native` cannot dismiss the prompt reliably, Patrol's primary advantage over `integration_test` is in doubt.
4. **CI shape proven on at least one platform.** Pilot ships either FTL iOS OR emulator.wtf Android with a passing build, including the cache strategy from §6. Cold-vs-warm measurement recorded.
5. **Flame canvas interaction documented as known limitation.** Pilot does not need to solve Flame-in-Patrol — but the limitation must be reproduced and documented so `forge:e2e-mobile-flutter` can route around it.
6. **Exit ramp validated.** The same `onboarding_test.dart` flow can be expressed as a Maestro YAML Flow of comparable size (the matrix's break-the-rec fallback). If Maestro proves dramatically simpler for this specific app, that is a signal to revisit the primary recommendation for Flame-heavy projects.

Decision rule: if 1–4 pass and 5–6 are documented, proceed to a full `forge:e2e-mobile-flutter` skill and ship it as a follow-up ticket under EPIC H. If 1 or 3 fail, reopen the #87 matrix Flutter row.

---

*Pilot doc only. No code in `lib/` is modified by this document. Follow-up ticket: `forge:e2e-mobile-flutter` skill spec (not yet filed).*
