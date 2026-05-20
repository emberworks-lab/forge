# Testing — mobile native

Augments `00_general.md` for native mobile stacks. **Skeleton — fill in detail when first project on each stack starts.**

## Android (Kotlin / Jetpack Compose)

| Layer | Tooling |
|---|---|
| Unit | JUnit 5 (or 4 if legacy) + Kotlin's `kotlin.test` |
| Mocking | MockK (Kotlin-idiomatic, beats Mockito for Kotlin code) |
| Coroutines | `kotlinx-coroutines-test` (`runTest`, `TestDispatcher`) |
| Compose UI | `androidx.compose.ui:ui-test-junit4` (`composeTestRule`) |
| Instrumented | Espresso (still relevant for non-Compose), `AndroidJUnitRunner` |
| Snapshot | Paparazzi (JVM-only — no emulator) OR Showkase + screenshot tests |
| E2E | UI Automator (cross-app), Maestro (declarative YAML) |
| Property-based | Kotest's property module |

Default for new projects: JUnit 5 + MockK + Compose UI Test + Paparazzi for design system. Maestro for E2E.

Test command: `./gradlew test` (unit) + `./gradlew connectedAndroidTest` (instrumented; needs device).

## iOS (Swift / SwiftUI)

| Layer | Tooling |
|---|---|
| Unit + UI | XCTest (built-in) |
| Mocking | Hand-rolled (no Mockito for Swift); use protocols + test doubles |
| SwiftUI views | `ViewInspector` (third-party but mature) |
| Snapshot | `swift-snapshot-testing` (Pointfree) |
| E2E | XCUITest |

Default: XCTest + ViewInspector + swift-snapshot-testing.

Test command: `xcodebuild test -scheme <App> -destination 'platform=iOS Simulator,name=iPhone 15'`.

Output is verbose; pipe through `xcbeautify` or `xcpretty` for human-readable parsing.

## Compose Multiplatform (KMP)

| Layer | Tooling |
|---|---|
| Common unit | `kotlin.test` (multiplatform) |
| JVM unit | JUnit 5 + MockK |
| iOS unit | Run via Kotlin/Native test target |
| Common UI | `compose-ui-test` (still maturing on iOS at time of writing) |
| Android UI | Standard Compose UI Test |
| iOS UI | XCUITest from Swift bridge |

Test command varies — typically `./gradlew commonTest` + per-platform targets.

## React Native

If picked: see also `01_web.md` for component testing patterns.

| Layer | Tooling |
|---|---|
| Unit + component | Jest + `@testing-library/react-native` |
| E2E | Detox (iOS + Android) OR Maestro (declarative, simpler) |
| Snapshot | jest snapshot (limited utility) OR Detox screenshots |

## Common across native mobile

- **Run unit tests on JVM/JS where possible.** Instrumented tests are slow and flaky.
- **Snapshot tests on JVM (Paparazzi for Android, swift-snapshot for iOS) are GOLD** — fast, deterministic, no device.
- **E2E on real device or emulator.** Maestro is the easiest cross-platform option in the agentic-skill era.
- **Manual test cases for ALL native flows.** Native runtime quirks (push notifications, deep links, in-app purchases) are best verified by the user, not by the agent.
