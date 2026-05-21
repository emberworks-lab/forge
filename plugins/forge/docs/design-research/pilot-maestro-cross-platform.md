# Pilot Design — Maestro as Cross-Platform Smoke Tier

**Date:** 2026-05-21
**Ticket:** #89 (EPIC H)
**Inputs:** `plugins/forge/docs/design-research/mobile-e2e-survey.md` (#86), `plugins/forge/docs/design-research/mobile-e2e-matrix.md` (#87)
**Scope:** Design only — no Maestro install, no skill scaffolding. Output is a decision-grade plan for a future `forge:e2e-smoke-maestro` skill.

---

## 1. Why Maestro for This Niche

Per-stack frameworks (Patrol/Detox/XCUITest+Espresso) win on depth inside their own stack but cannot share a single test artifact across stacks. The #87 matrix recommends **Maestro as the cross-platform smoke tier** precisely because of this gap:

- **One YAML Flow runs on iOS, Android, RN, Flutter, and (beta) web** — no per-stack rewrite (survey §2 stack matrix).
- **No build step, no compiler, no test-runner config** — `maestro test flow.yaml` against a running emulator/simulator. Time-to-first-test ≈ 10–15 min (survey §2 setup).
- **Built-in auto-retry against the accessibility tree** removes manual `sleep()` discipline that Appium suites require (survey §2 speed/stability).
- **Mixed-estate fit** — a project with a Flutter app + an RN companion app + a marketing web target gets one suite covering the cross-cutting smoke flow (login → home → CTA) instead of three.

What stack-specific tools do **not** cover and Maestro does: cross-codebase smoke parity in one CI report, with one DSL the QA author can read.

What Maestro does **not** cover that stack-specific tools do: widget-tree assertions (Patrol), JS-thread idle signalling (Detox), Compose/SwiftUI internals (Espresso/XCUITest). This is the smoke-vs-full tradeoff in §7.

---

## 2. Setup Steps (Local)

Real commands a user would run, in order:

```bash
# 1. Install the Maestro CLI (macOS / Linux)
curl -Ls "https://get.maestro.mobile.dev" | bash

# 2. Verify
maestro --version          # → 2.5.1 or newer (per survey §2 — Apr 2026)

# 3. Prerequisites — at least one of:
#    a) Android emulator running (avdmanager / Android Studio)
#    b) iOS simulator running (xcrun simctl)
#    c) Physical device connected via adb / Xcode

# 4. (Optional) Maestro Studio — local GUI recorder
maestro studio

# 5. (Optional) Register the Maestro MCP server for LLM-driven flow generation
#    (Survey §2 — MCP server shipped 2025; enables Claude Code to author flows.)
maestro mcp install        # exact CLI flag confirmed during pilot execution
```

Homebrew alternative: `brew install maestro`. Windows is supported via WSL2.

---

## 3. Project Structure

Maestro flows live alongside source. Recommended layout for a Forge project:

```
<repo-root>/
├── maestro/
│   ├── flows/
│   │   ├── smoke-launch.yaml          # one cross-platform flow per critical path
│   │   ├── smoke-login.yaml
│   │   └── smoke-checkout.yaml
│   ├── config/
│   │   ├── android.yaml               # appId, env overrides for Android target
│   │   └── ios.yaml                   # appId, env overrides for iOS target
│   ├── helpers/
│   │   └── tap-cta.yaml               # reusable sub-flows (Maestro `runFlow:`)
│   └── README.md                      # local-run instructions for QA authors
└── .claude/
    └── e2e-smoke-maestro.json         # opt-in flag for forge:e2e-smoke-maestro
```

Notes:
- `flows/` is flat and named after the user journey, not the screen. One YAML per smoke path.
- `config/` holds the platform-specific bindings (`appId`, env vars). The flow itself stays platform-agnostic.
- `helpers/` exists only after a sub-flow has been reused twice (avoid premature extraction).
- `.claude/e2e-smoke-maestro.json` is the opt-in artifact `forge:e2e-smoke-maestro` reads, mirroring the `kit-*` opt-in pattern.

---

## 4. First Flow Example

A realistic smoke test: launch → home screen appears → tap CTA → confirm next screen renders.

```yaml
# maestro/flows/smoke-launch.yaml
appId: com.example.app
---
- launchApp:
    clearState: true
- assertVisible:
    id: "home-screen-title"
    text: "Welcome"
- assertVisible: "Get started"     # falls back to visible text
- tapOn:
    id: "cta-get-started"
- assertVisible:
    id: "onboarding-step-1"
- takeScreenshot: smoke-launch-onboarding-step-1
```

Run it:

```bash
maestro test maestro/flows/smoke-launch.yaml
maestro test maestro/flows/                 # whole directory
maestro test --include-tags=smoke maestro/  # tag-based selection
```

Cross-platform with the same YAML:

```bash
# iOS simulator currently booted
maestro --device "iPhone 15" test maestro/flows/smoke-launch.yaml

# Android emulator with a different appId override
maestro --config maestro/config/android.yaml test maestro/flows/smoke-launch.yaml
```

The flow file does **not** change between iOS and Android — only the config binding does. This is the core property the cross-platform skill leans on.

---

## 5. Forge Integration — `forge:e2e-smoke-maestro`

A future skill, parallel in shape to `forge:e2e-web` (#80) but **cross-platform by design** — unlike the per-stack skills (`forge:e2e-mobile-flutter`, `forge:e2e-mobile-rn`, `forge:e2e-mobile-native`) which each own one stack.

**Skill shape:**

- **Type:** `hybrid` (≤ 120 lines + `references/` + `manual-setup-templates/maestro.md`).
- **Trigger:** project has `<root>/.claude/e2e-smoke-maestro.json` AND a `maestro/` directory.
- **Inputs:** ticket acceptance criteria; existing flows under `maestro/flows/`.
- **Outputs:** new or updated `*.yaml` flow files; a `maestro test` invocation in CI; manual test cases scraped from the YAML.

**Responsibilities (what the skill wraps):**

1. **Scaffold** — on first run, write `maestro/` skeleton + `.claude/e2e-smoke-maestro.json` + per-platform configs.
2. **Author flows** — generate YAML flows from acceptance criteria. When the Maestro MCP server is registered, delegate flow drafting to it (survey §2 — MCP-driven authoring). Fall back to direct YAML emission otherwise.
3. **Run locally** — `maestro test maestro/flows/<flow>.yaml` against whichever simulator/emulator the user has booted; surface failure logs with screenshot artifacts.
4. **TDD hook** — red phase: write a failing flow that asserts the new behavior. Green phase: implement until `maestro test` passes. Refactor phase: extract reusable sub-flows into `helpers/` once a step appears in 2+ flows.
5. **Per-stack handoff** — when a flow needs widget-tree assertions, JS-thread idle, or Compose internals, the skill **stops** and recommends escalating that specific behavior to the per-stack skill (Patrol / Detox / XCUITest+Espresso). Smoke tier is not the place for depth.

**Parallel to `forge:e2e-web` (#80) but with one critical difference:**

| Axis | `forge:e2e-web` (#80) | `forge:e2e-smoke-maestro` (this) |
|---|---|---|
| Targets | One stack (web/Playwright) | Many stacks (iOS, Android, Flutter, RN, web-beta) from one YAML |
| Skill count | 1-to-1 with the stack | 1-to-many — replaces 4 hypothetical per-platform smoke skills |
| Depth | Full e2e for the web stack | Smoke only; escalates depth to per-stack skills |
| Composition rule | Owns its stack entirely | Composes **with** per-stack skills, does not replace them |

**Cross-cutting with the matrix:** the skill is the runtime for the §4 "Forge Plugin Implications → `forge:e2e-mobile-cross`" sketch in #87. The naming is normalised here to `forge:e2e-smoke-maestro` to make the smoke tier explicit and to leave room for a future `forge:e2e-smoke-web-playwright` should #80 acquire a smoke sibling.

---

## 6. CI Integration

Two paths, with different cost/coverage tradeoffs.

### 6a. Local CI runner (GitHub Actions / GitLab / self-hosted)

- macOS runner for iOS simulator; Linux runner with an Android emulator action for Android.
- No Maestro server fee.
- **Cost:** runner minutes only. macOS runners are ≈ 10× the cost of Linux on most providers — budget accordingly.
- **Coverage gap:** physical iOS device coverage of an App Store / TestFlight `.ipa` is **not possible locally** (survey §2 physical-device note).

```yaml
# .github/workflows/smoke-maestro.yml (sketch)
- uses: mobile-dev-inc/action-maestro-cloud@... # or local install
- run: maestro test maestro/flows/
```

### 6b. Maestro Cloud

- Hosted real-device farm; runs the same YAML in parallel across iOS/Android device matrices.
- Removes the physical-iOS-local limitation (survey §2 — Maestro Cloud unblocks `.ipa` testing).
- **Cost:** subscription tier; pricing is per parallel runner and per device-minute. Treat as a recurring OPEX line item — confirm the pricing page before recommending in a project's `kit-*` config.

### Recommendation pattern for `forge:project-init`

- Default: local runner for smoke. Cheap, deterministic, sufficient for the smoke tier's intent (does the app launch and reach the first CTA on each platform).
- Opt-in: Maestro Cloud, gated behind a `--smoke-cloud` flag at project init or a manual `.claude/e2e-smoke-maestro.json` config entry. The skill never silently enables a paid service.

### Device farm alternatives

Maestro flows can be executed on Firebase Test Lab, BrowserStack, LambdaTest, and AWS Device Farm via their respective Maestro integrations or CLI wrappers. These are documented as **escape hatches** in the manual-setup template; not the default. Pick one only when the team already pays for that farm for other test tiers.

---

## 7. Smoke-Tier vs Full-E2E Tradeoff

Per the #87 matrix — Maestro is the **smoke tier**, not a replacement for stack-specific frameworks.

| Question | Maestro suffices | Use stack-specific instead |
|---|---|---|
| Does the app launch on iOS and Android? | Yes | — |
| Does login succeed and reach the home screen? | Yes | — |
| Does the home screen's primary CTA navigate correctly? | Yes | — |
| Does a Flutter widget rebuild correctly after a state change? | No — black-box | **Patrol** (widget-tree access) |
| Does an RN screen wait for the network queue + animations correctly? | No — accessibility-tree heuristic only | **Detox** (JS-thread + animation idle) |
| Does a SwiftUI matched-geometry transition complete? | No — opaque to the accessibility tree | **XCUITest** |
| Does a complex branching flow (5+ conditionals on dynamic data) work? | Awkward — YAML ceiling (survey §2 known pitfalls) | Stack-specific framework with a real DSL |
| Does the app handle a system permission dialog? | Partially — depends on platform | **Patrol** (Flutter) or stack-native helpers |
| Cross-codebase smoke parity in one CI report? | **Yes — primary use case** | — |

Bottom line: Maestro answers "does it launch and reach the happy-path landmark on every platform?" — the smoke question. Stack-specific frameworks answer "does the behavior under this widget/component work correctly?" — the regression question. The two tiers compose; neither replaces the other. See #87 §2 cross-platform rationale and §3 "When to Break the Recommendation" for the explicit handoff triggers.

---

## 8. Risks

1. **YAML expressiveness ceiling.** Complex conditionals, loops, and dynamic data become verbose workarounds (survey §2 known pitfalls). The skill's escape hatch is to recommend a stack-specific framework once a flow exceeds ~50 lines of YAML or grows more than one nested `runFlow:`.
2. **Accessibility-tree dependency.** If the app under test lacks stable accessibility IDs, flows are flaky or unwritable (survey §2). Mitigation: `references/test-id-discipline.md` (already planned as a cross-cutting reference per #87 §4 cross-cutting notes).
3. **Web support is beta.** Maestro web is not production-grade as of mid-2026 (survey §2 stack matrix). For web smoke, prefer `forge:e2e-web` (#80) and treat Maestro-on-web as an experiment, not a recommendation.
4. **Physical iOS local gap.** Real `.ipa` builds can't be tested locally — only via Maestro Cloud (survey §2 physical-device note). Mitigation: explicit risk disclosure in the manual-setup template; do not promise local physical-iOS coverage.
5. **No IDE autocompletion / no type-checking on YAML.** Large suites become hard to refactor (survey §2 known pitfalls). The smoke tier is deliberately small (≤ ~10 flows), which keeps this risk bounded as long as the skill enforces tier discipline.
6. **MCP-server authoring is new.** The MCP-driven flow generation path (survey §2 — added 2025) is less battle-tested than hand-authored YAML. Pilot should evaluate flake rate of LLM-generated flows vs hand-written.
7. **Subscription drift.** Maestro Cloud pricing changes are a recurring vendor risk. Mitigation: never enable Cloud silently; project-init must surface the cost decision explicitly.

---

## 9. Pilot Success Criteria

Proceed if **all** of the following hold after running the pilot on one real project:

- **Setup time ≤ 30 min** from `curl` install to first green flow on at least one platform (iOS sim **or** Android emulator).
- **First flow runs cross-platform** — the same YAML file passes on both iOS and Android with only a config swap.
- **CI green on local runner** — at least one smoke flow runs to completion in GitHub Actions (or equivalent) within reasonable runner-minute budget; specific budget set during the pilot (rough target: ≤ 5 min per platform).
- **TDD loop closes** — red (failing flow) → green (passing flow) → refactor (helper extraction) all observed in a single ticket execution.
- **Handoff to per-stack skill demonstrated** — at least one case where a deeper-than-smoke check is correctly escalated to the per-stack framework (or documented as "would escalate" if the per-stack skill isn't yet implemented).
- **MCP authoring evaluated** — at least one flow generated via the Maestro MCP server, with flake rate compared against a hand-authored equivalent. Pass = either path is acceptable; fail = MCP path is materially flakier and is parked.

Abandon (or scope down to "documented but not skilled") if **any** of the following:

- Setup exceeds 2 h on a clean machine without external help.
- Cross-platform YAML reuse breaks — i.e. the team ends up maintaining two near-duplicate flows per platform.
- CI cost on the local-runner path exceeds the cost of one per-stack tier on its own (would invert the cost case).
- The smoke tier's flows become so YAML-complex they need a real DSL — at which point Appium-with-WebDriverIO becomes a fairer comparison and the smoke-tier framing collapses.

---

*Source-of-truth survey: `plugins/forge/docs/design-research/mobile-e2e-survey.md` (#86).*
*Matrix recommending Maestro for the cross-platform smoke tier: `plugins/forge/docs/design-research/mobile-e2e-matrix.md` (#87).*
*Sister Flutter+Patrol pilot: #88.*
