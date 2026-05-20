# Classifier prompt — regression test snippets

Documentation only. NOT passed to the classifier subagent at runtime — the classifier-prompt.md file is the verbatim runtime payload; this sibling exists so prompt edits can be validated against expected behavior without bloating every call.

Each test fixes an `input` payload (the JSON the orchestrator would build from `review_findings` + `simplify_residuals`) and sketches the expected `output` JSON the classifier should produce. Use these to manually run the prompt + diff its output against the sketch when changing classifier-prompt.md.

## Test 1 — single architectural finding → 1 sub-epic, 0 in-place

Input:

```json
{
  "review_findings": [
    {
      "agent": "architecture-focus",
      "findings": [
        {
          "severity": "high",
          "area": "error-boundary",
          "file": "lib/app/app.dart:1-EOF",
          "title": "No error boundary anywhere in the app",
          "detail": "Uncaught exceptions in any screen crash the whole app. No ErrorWidget.builder, no zoned guard, no Crashlytics hookup.",
          "recommendation": "Introduce a top-level error boundary + zoned runZonedGuarded + Crashlytics surface."
        }
      ]
    }
  ],
  "simplify_residuals": []
}
```

Expected output sketch:

```json
{
  "in_place_candidates": [],
  "sub_epic_candidates": [
    {
      "id": "se-001",
      "severity": "high",
      "source": "review:architecture-focus",
      "title": "Introduce app-wide error boundary + crash reporting",
      "scope_outline": "Wire runZonedGuarded at app entry. Add ErrorWidget.builder. Route uncaught errors to Crashlytics with stage tags. Cover background isolates. Add smoke test that simulates an uncaught throw and asserts the surface.",
      "rationale": "Cross-cutting (touches app entry, every screen surface, build config). Architectural by definition; not a single-file fix."
    }
  ],
  "totals": { "in_place": 0, "sub_epic": 1 }
}
```

## Test 2 — single simplify reuse residual → 1 in-place, 0 sub-epic

Input:

```json
{
  "review_findings": [],
  "simplify_residuals": [
    {
      "agent": "reuse",
      "file": "lib/widgets/score_chip.dart:14-22",
      "title": "Duplicated /10 format helper",
      "detail": "score_chip.dart and signal_card.dart both inline the '/10' format. simplify could not extract because the two files are in different layers."
    }
  ]
}
```

Expected output sketch:

```json
{
  "in_place_candidates": [
    {
      "id": "ip-001",
      "severity": "low",
      "source": "simplify:reuse",
      "title": "Extract /10 score format helper",
      "file": "lib/widgets/score_chip.dart:14-22",
      "fix_outline": "Move the '/10' format into lib/core/formatters/score_format.dart. Update score_chip.dart and signal_card.dart to import it. No behavior change."
    }
  ],
  "sub_epic_candidates": [],
  "totals": { "in_place": 1, "sub_epic": 0 }
}
```

Note: severity absent in input → assigned `low` by ambiguous-case rule (small reuse residual).

## Test 3 — empty input → empty output

Input:

```json
{ "review_findings": [], "simplify_residuals": [] }
```

Expected output:

```json
{ "in_place_candidates": [], "sub_epic_candidates": [], "totals": { "in_place": 0, "sub_epic": 0 } }
```

## Test 4 — duplicate finding (review + simplify on same file:line) → single merged item

Input:

```json
{
  "review_findings": [
    {
      "agent": "testing-focus",
      "findings": [
        {
          "severity": "medium",
          "area": "missing-test",
          "file": "lib/auth/session.dart:42-58",
          "title": "Session expiry path has no test",
          "detail": "session.dart:42-58 implements expiry but no unit test exercises the expired branch.",
          "recommendation": "Add a unit test that fakes Clock and asserts expired-session behavior."
        }
      ]
    }
  ],
  "simplify_residuals": [
    {
      "agent": "quality",
      "file": "lib/auth/session.dart:42-58",
      "title": "Expiry branch lacks coverage",
      "detail": "simplify could not add the test in-line; needs a Clock fake."
    }
  ]
}
```

Expected output sketch:

```json
{
  "in_place_candidates": [
    {
      "id": "ip-001",
      "severity": "medium",
      "source": "review:testing-focus",
      "title": "Add unit test for session expiry branch",
      "file": "lib/auth/session.dart:42-58",
      "fix_outline": "Inject a fake Clock in test/auth/session_test.dart. Assert expired-session path returns the expected rejection. Simplify residual flagged the same gap."
    }
  ],
  "sub_epic_candidates": [],
  "totals": { "in_place": 1, "sub_epic": 0 }
}
```

Single merged item; `review` source preferred; simplify mentioned in `fix_outline`.

## Test 5 — three findings, exact-fidelity check

Input:

```json
{
  "review_findings": [
    {
      "agent": "security-focus",
      "findings": [
        {
          "severity": "high",
          "area": "secret-leak",
          "file": "src/config/stripe.ts:14",
          "title": "Hard-coded Stripe secret key in source",
          "detail": "Literal sk_live_… committed.",
          "recommendation": "Move to env."
        }
      ]
    },
    {
      "agent": "architecture-focus",
      "findings": [
        {
          "severity": "medium",
          "area": "layer-boundary",
          "file": "lib/ui/profile_page.dart:88-104",
          "title": "UI calls repository directly, bypassing controller",
          "detail": "profile_page.dart:88-104 imports UserRepo.",
          "recommendation": "Route via ProfileController."
        }
      ]
    },
    {
      "agent": "testing-focus",
      "findings": [
        {
          "severity": "low",
          "area": "flaky-test",
          "file": "test/widgets/card_test.dart:33",
          "title": "Pump duration depends on wall clock",
          "detail": "card_test.dart:33 uses Future.delayed.",
          "recommendation": "Use fakeAsync."
        }
      ]
    }
  ],
  "simplify_residuals": []
}
```

Expected behavior (sketch):

- Item 1 → `sub_epic` (secret rotation + env wiring is cross-cutting). File path copied verbatim: `src/config/stripe.ts:14`. Severity copied verbatim: `high`.
- Item 2 → `in_place` (single file, ≤ 30 lines, no new abstraction — just re-route the call). File path copied verbatim. Severity copied verbatim: `medium`.
- Item 3 → `in_place` (single line, trivial). File path copied verbatim. Severity copied verbatim: `low`.

No fabricated paths, no shifted severities, all three sources prefixed `review:<agent>`.
