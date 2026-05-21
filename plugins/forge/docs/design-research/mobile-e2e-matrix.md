# Mobile E2E Decision Matrix per Stack

**Date:** 2026-05-21
**Input:** `plugins/forge/docs/design-research/mobile-e2e-survey.md` (#86)
**Purpose:** Per-stack recommendation derived from the survey. Feeds pilot design docs (#88 Flutter+Patrol, #89 Maestro).

All evidence citations refer to the survey above unless noted.

---

## 1. Stack Matrix

| Stack | Primary | Secondary fallback | Why this over alternatives | Setup cost | Maintenance cost |
|---|---|---|---|---|---|
| **Flutter** | Patrol | Maestro | Patrol is Flutter-first, runs in-process (grey-box) with Dart, and bridges native OS interactions (permissions, push, biometrics) that `integration_test` cannot reach. Cross-platform tools (Maestro/Appium) treat Flutter as a black box, losing widget-tree access. | Medium — `patrol_cli`, Gradle/Xcode adjustments; FTL/BrowserStack work out of the box | Low — single Dart codebase; minor friction from the `platform` API redesign in 4.0 |
| **React Native** | Detox | Maestro | Detox's grey-box JS-thread / UI-thread / network synchronisation drives flakiness below 2% on well-maintained suites — significantly better than Appium's 15–25% and ahead of YAML-only Maestro for assertion sophistication. RN-only focus matches RN-only stacks. | High — compiled `.app`/`.apk` per run, `.detoxrc.json`, macOS runner, RN version coupling | Mid — RN/Expo upgrades can block on Detox compatibility; `testID` discipline required |
| **Native iOS + Android (separate codebases)** | XCUITest (iOS) + Espresso (Android) | Maestro (for shared smoke tier) | First-party frameworks, in-process, deterministic synchronisation, bundled with Xcode/Android Studio. Survey reports XCUITest "strong reliability with minimal flaky behavior" and Espresso's idling-resource model eliminating common async flakiness. No cross-platform tool beats native depth on its own platform. | Low per platform inside the IDE; high if team is unfamiliar with native tooling | Low — frameworks ship with platform SDKs and are effectively permanent |
| **Cross-platform single-codebase smoke / RN+Flutter mixed estate** | Maestro | Appium | Maestro covers iOS, Android, RN, Flutter from one YAML Flow with ~10–15 min time-to-first-test, auto-retry, and an MCP server for LLM-generated tests. Appium spans the same matrix but is the slowest framework with the highest maintenance burden (30–50% of QA time in enterprise). | Low — single CLI install, no build step | Low for simple flows; rises as YAML hits its ceiling on complex conditional logic |

---

## 2. Per-Stack Rationale

### Flutter → Patrol

Patrol's grey-box model compiles tests into the app binary and exposes both the Flutter widget tree and the host OS simultaneously, which lets one test assert on a widget AND drive a permission dialog or push notification — the survey (§1) explicitly calls this out as the gap `integration_test` cannot close: "permission dialogs, system notifications, Wi-Fi toggling, WebViews, and device settings that `integration_test` cannot reach". Maestro and Appium can drive a Flutter app, but only through the accessibility tree, which loses widget-level assertions and silently passes when accessibility IDs are missing (survey §2 known pitfall: "tests can silently pass if accessibility IDs are ambiguous or missing"). Patrol ships with FTL/BrowserStack/LambdaTest/AWS Device Farm/emulator.wtf compatibility out of the box (survey §1 setup), so CI integration cost stays modest compared to Appium or Detox. Speed is favourable because tests run in-process — "no WebDriver round-trip" per survey §1. Maintainer activity is healthy (v4.5.0 ~March 2026, 285k monthly pub.dev downloads, LeanCode actively shipping; adopters Tide, Sennheiser, easyJet). The 4.0 `platform` API redesign is a one-time migration cost (survey §1 known pitfalls) rather than a recurring tax.

### React Native → Detox

Detox is the only framework in the survey that hooks the RN JS thread, UI thread, network queue, AND animation engine (survey §3), giving deterministic "app is idle" signalling. The survey cites flakiness below 2% on well-maintained Detox suites versus Appium's 15–25% on RN (survey §3 stability and §4 stability), and CISIN benchmarks reporting up to 80% flakiness reduction vs. black-box tools. Detox is also New Architecture (Fabric/JSI) compatible from RN 0.77 onwards, which matters for any 2026-era RN codebase. Maestro is viable for RN but is YAML-only and accessibility-tree-bound, so complex branching logic and dynamic data become verbose workarounds (survey §2 known pitfall: "Limited support for complex test logic (conditionals, loops, dynamic data) without workarounds"). The trade-off is real: Detox demands a compiled binary per run, a macOS CI runner for iOS, and breaks on RN/Expo upgrades until a compatible Detox release lands (survey §3 known pitfalls) — so the recommendation assumes the team has macOS CI capacity and `testID` discipline (or will adopt them). Maintainer signal is strong: v20.51.1 May 2026, 400 total releases, Wix runs "thousands of Detox tests in production".

### Native iOS + Android (separate codebases) → XCUITest + Espresso

When the codebase is already split per platform, the first-party tools are the only ones with direct thread-level synchronisation on each side. The survey (§5) notes both are bundled with their IDEs (Xcode, Android Studio) — "no separate installation. Creating a new test target or test class is a few clicks". XCUITest has "strong reliability with minimal flaky behavior" thanks to Apple's accessibility tree synchronisation; Espresso's automatic idling-resource management "eliminates the most common sources of flakiness (async operations, animations)" and runs at near-unit-test speed. Both are used as the underlying driver layer by other frameworks (Appium delegates to the XCUITest driver), confirming they sit at the bottom of the abstraction stack. The known limitation — neither crosses the app boundary into system UI without help — matches the reality of native-team workflow, where cross-app scenarios are rare and usually solved by UIAutomator2 (Android) or accessibility-tree access (iOS). The survey's idiomatic-use note explicitly endorses the 2026 pattern of "Espresso for the fast Android regression layer + XCUITest for the fast iOS regression layer + Maestro/Appium for cross-cutting smoke" — which informs the cross-platform tier recommendation below and the secondary fallback here. Maintainer risk is effectively zero: both ship with their platform SDKs and "will be maintained as long as the platforms exist".

### Cross-platform single-codebase smoke / mixed estate → Maestro

For a single YAML Flow that runs against iOS, Android, RN, and Flutter targets, Maestro is the only framework in the survey that does this without per-platform configuration (survey §2 stack matrix). Survey evidence: 10–15 min time-to-first-test (§2 setup), ~15–20s typical login flow (§2 speed), built-in auto-retry eliminating manual `sleep()` calls, 14.1k stars, 138 releases, v2.5.1 April 2026, adopters Microsoft/Meta/DoorDash (§2 maintainer activity), MCP server for LLM-driven test generation added 2025. The September 2025 Jupiter (fintech) case study cited in §2 — choosing Maestro over Detox after Detox succeeded only 2 of 10 physical-device runs — is direct field evidence that Maestro's cross-platform model survives real-device variance better than the more sophisticated alternatives. Appium is the only alternative with comparable breadth but is reported as the slowest framework (§4 speed: "3–5× slower than Maestro") and consumes 30–50% of enterprise QA time in maintenance (§4 known pitfalls). Detox is RN-only, Patrol is Flutter-only, XCUITest+Espresso are per-platform — none fit a cross-codebase smoke tier.

---

## 3. When to Break the Recommendation

### Flutter — pick Maestro over Patrol when:
- The Flutter app is a thin shell over a WebView (limited widget-tree value, accessibility tree is enough).
- Team has zero Dart appetite for tests and QA is non-engineering (Maestro's YAML is approachable; Patrol requires Dart fluency — survey §1 notes Dart-only with no separate DSL).
- The same suite must cover a parallel RN or native app — single Maestro repo is cheaper than two test stacks.
- Existing test-suite uses the deprecated Patrol `native`/`native2` API and the team would rather migrate to Maestro than to the new Patrol `platform` API (survey §1 known pitfalls).

### React Native — pick Maestro over Detox when:
- The team has been bitten by Detox version-coupling on the upgrade path (RN/Expo bumps blocked by Detox compatibility, per survey known pitfall).
- Physical-device coverage matters and you don't run a macOS CI fleet — survey notes Detox's 2/10 physical-device success rate in one 2025 case study (Jupiter), versus Maestro winning the contract.
- Test authors are non-engineers or QA-only; YAML beats JS/TS for hand-off.

### React Native — pick Appium over Detox when:
- The team already runs Java/Python WebDriver tooling and Sauce Labs/BrowserStack contracts (survey §4 idiomatic use); reusing that infra beats Detox's setup cost.
- The RN app must share an E2E suite with a non-RN sibling app (e.g., a native iOS or Xamarin twin) where Detox cannot reach — Appium's universal driver model handles all of them.
- The team has no macOS CI capacity and cannot add one — Detox requires macOS for iOS builds (survey §3 known pitfalls); Appium tests can run against a remote device farm without local macOS.

### Native iOS+Android — pick Maestro over XCUITest+Espresso when:
- The team is small enough that maintaining two test codebases dominates the budget — a single Maestro suite covers both at the cost of native depth.
- Cross-platform CI parity (one pipeline, one report) matters more than per-platform reliability.
- The native team is unfamiliar with the platform tools — survey §5 notes "for teams unfamiliar with the native platform (e.g., Flutter or RN developers), the learning curve for Xcode project structure or Gradle test configurations can be steep". Maestro sidesteps this.

### Cross-platform single-codebase — pick Appium over Maestro when:
- Tests require complex conditional logic, dynamic data, or loops that YAML expresses awkwardly (survey known pitfall §2).
- The app is not RN or Flutter (e.g., Xamarin, .NET MAUI, native hybrid) — Appium's driver model still covers it.
- Existing Sauce Labs / BrowserStack / Kobiton enterprise contracts already centre on Appium.

### Flutter Web — pick Maestro over Patrol when:
- Survey notes Patrol 4.0 Web is early-stage with no hot restart in develop mode and a pending unresolved technical issue (§1 stability and known pitfalls). For web-heavy Flutter targets, Maestro's web beta or a Playwright-side approach (via the EPIC H web pilot) may be more pragmatic until Patrol Web matures.

### Any stack — pick the native first-party tool over the recommendation when:
- The team is shipping a single-platform-only app and wants the longest-horizon maintainer guarantee. Survey §5 makes the point: XCUITest and Espresso "will be maintained as long as the platforms exist" — a property no third-party framework can match.
- A specific flow requires deterministic synchronisation with Compose UI or SwiftUI internals beyond what an accessibility-tree-based tool can reach.

---

## 4. Forge Plugin Implications

For each recommendation, what the corresponding `forge:e2e-mobile-<stack>` skill would look like (sketches; not implementations).

### `forge:e2e-mobile-flutter` (Patrol primary)

- **Pattern:** mirror `forge:e2e` (backend) and `forge:e2e-web` (Playwright pilot from EPIC H web tier) — `*.e2e-mobile.dart` files under `integration_test/`, opt-in via `<project>/.claude/e2e-mobile.json`, test-runner subagent (sonnet, mechanical).
- **Setup module:** `manual-setup-templates/patrol.md` — `dart pub global activate patrol_cli`, `patrol bootstrap`, Gradle/Xcode entries, FTL/BrowserStack CI snippet, emulator.wtf hint.
- **Template wiring:** `flutter-app` template gets opt-in `patrol` module (parallel to web-nextjs Playwright opt-in pattern already in `plugins/forge/skill-templates/web-nextjs/OPT_IN_MODULES.md`).
- **TDD integration:** `forge:tdd` red phase writes a failing Patrol test, green phase runs `patrol test` until pass.
- **4.0 migration note:** skill detects deprecated `native`/`native2` API usage and warns to migrate to the redesigned `platform` API.
- **Pilot doc:** #88.

### `forge:e2e-mobile-rn` (Detox primary)

- **Pattern:** same skeleton; `*.e2e-mobile.spec.ts` files under `e2e/`, Jest runner, Detox config in `.detoxrc.json`, test-runner subagent (sonnet, mechanical).
- **Setup module:** `manual-setup-templates/detox.md` — macOS CI gate, `detox build`, `detox test`, `testID` lint rule recommendation (eslint-plugin), pre-built binary caching strategy for CI.
- **Template wiring:** `mobile-rn` template (if/when scaffolded) gets opt-in `detox` module.
- **Escape hatch hook:** skill detects `package.json` Expo managed workflow and warns user about EAS Build prerequisite (survey §3 known pitfall); also checks RN version against Detox compatibility matrix and flags upgrade-blocked scenarios.
- **Sister skill:** `forge:e2e-mobile-cross` (Maestro) for teams electing the secondary fallback or running mixed Detox+Maestro tiers.
- **New Architecture check:** skill confirms RN ≥ 0.77 before recommending Detox for Fabric/JSI projects.

### `forge:e2e-mobile-native` (XCUITest + Espresso primary)

- **Pattern:** two-headed — `e2e-mobile-ios` uses XCUITest test target in Xcode, `e2e-mobile-android` uses Espresso test APK. Opt-in flags per platform in `.claude/e2e-mobile.json`.
- **Setup module:** `manual-setup-templates/xcuitest-espresso.md` — Xcode Test Navigator setup, AndroidX Test Gradle deps, Compose UI test interop note (per survey §5 — Espresso updated for Compose UI 1.7.x in 2025).
- **Template wiring:** `native-ios` and `native-android` templates each ship the respective opt-in module.
- **Test-runner subagent:** sonnet, mechanical; dispatches per-platform.
- **Cross-app guardrail:** skill documents when a flow requires UIAutomator2 (Android) or system-alert accessibility access (iOS), so teams know when to escalate to Maestro for that specific flow.

### `forge:e2e-mobile-cross` (Maestro primary for cross-platform tier)

- **Pattern:** `*.flow.yaml` files under `tests/maestro/`, opt-in via `.claude/e2e-mobile-cross.json`, runner subagent invokes `maestro test`.
- **Setup module:** `manual-setup-templates/maestro.md` — `brew install maestro`, emulator/simulator prerequisites, MCP server registration for LLM-generated flows.
- **Template wiring:** opt-in module available to `flutter-app`, `mobile-rn`, `native-ios`, `native-android` templates as a smoke-tier add-on.
- **Pilot doc:** #89.
- **LLM-authoring hook:** skill leverages Maestro MCP server to scaffold initial Flows from natural-language descriptions (survey §2 — MCP server added 2025).

### Cross-cutting plugin notes

- All four skills share a `references/test-id-discipline.md` (importance of stable accessibility IDs across frameworks — relevant because Maestro, Detox, and Appium all fail silently or noisily when IDs are missing per survey §2/§3/§4).
- All four register a `forge:tdd` integration the same way the web pilot does, so red-green-refactor extends to mobile e2e.
- A single `forge:e2e-mobile-router` is **not** recommended — per EPIC H composition principle, each stack-specific skill owns its own decision tree; the master skill (likely the project's `forge:execute-ticket`) routes based on `kit-*` config.
- All setup modules document a CI build-caching strategy because the three primary-recommendation frameworks (Patrol, Detox, XCUITest+Espresso) all require app compilation before tests run (survey notes Patrol §1, Detox §3, native §5 each as "compiled binary per run" or equivalent).

---

## 5. Synthesis: Why These Five and Not Others

The survey deliberately scoped to five frameworks; this matrix recommends only from within that scope. Notable absences (Calabash, Earl Grey, Cavy, Bitbar, Kobiton-as-framework) are out of scope here. If a future ticket re-opens the framework set, the matrix axes (primary / secondary / setup / maintenance / break-the-rec triggers) should be reused so the comparison stays apples-to-apples.

Two patterns hold across all four stack recommendations:

1. **Primary = closest-to-the-app framework that the stack supports.** Patrol compiles into the Flutter binary; Detox hooks the RN runtime; XCUITest/Espresso are first-party. The further the framework sits from the app process, the more flakiness and maintenance it accrues — survey evidence converges on this across §1, §3, §4, and §5.
2. **Secondary = Maestro almost everywhere.** Maestro's accessibility-tree model is a ceiling but also a floor: it works on every stack and lets a team replace any primary recommendation with a uniform fallback if the primary's setup/maintenance cost exceeds budget. This is exactly why it's also the primary for the cross-platform-single-codebase tier.

Appium does not appear as primary for any stack in this matrix. The survey is unambiguous on why: it is the slowest of the five (§4 speed — 3–5× slower than Maestro), has the highest maintenance burden (§4 known pitfalls — 30–50% of QA time in enterprise), and its 15–25% out-of-the-box flakiness on RN is bested by Detox (sub-2%), Maestro, and the native tools on their respective platforms. Its strength — language-agnostic, every-stack coverage including Xamarin/MAUI and mobile web — is rare in the projects this plugin targets. Where it does win (existing WebDriver tooling + Sauce Labs contracts), the break-the-rec sections call it out explicitly.

---

## 6. Open Questions for Pilot Design Docs

The following questions are surfaced here rather than answered, because they belong in the pilot designs (#88, #89), not in this matrix:

- **Patrol pilot (#88):** what's the minimum acceptable build-cache strategy on FTL vs. local emulator? How does `forge:tdd` reconcile Patrol's binary-build latency with red-green-refactor cadence?
- **Maestro pilot (#89):** does the MCP-server-driven Flow generation flow through `forge:tdd` cleanly, or does it sit as a separate skill? How are real-device gaps (iOS local) documented when Maestro Cloud is not in scope?
- **Detox (deferred):** would a `forge:e2e-mobile-rn` skill ship in EPIC H or land in the parking-lot epic alongside an RN template? Matrix recommends Detox; whether to pilot now is an EPIC-H scoping decision, not a matrix decision.

---

*Source-of-truth survey: `plugins/forge/docs/design-research/mobile-e2e-survey.md` (#86).*
*Inputs for #88 (Flutter + Patrol pilot design) and #89 (Maestro pilot design).*
