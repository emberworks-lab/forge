<!-- Owned by EPIC E (#34) and consumed by EPIC B (#3). -->

# Classifier prompt — review + simplify → in-place / sub-epic groups

This file is **not** a stand-alone subagent definition. It is a prompt template that the `forge:epic-close` orchestrator (Step 3 → Step 4 transition) passes verbatim to a single Opus subagent. The subagent classifies combined findings from `forge:review` and `forge:simplify-branch` residuals into two actionable groups and returns one JSON object.

Model: **opus** (creative, judgement-heavy classification).

## Input contract

The orchestrator merges all reviewer-agent JSON outputs (per `plugins/forge/skills/review/references/output-format.md`) and simplify residuals into a single object:

```json
{
  "review_findings": [
    {
      "agent": "architecture-focus | security-focus | testing-focus",
      "findings": [
        {
          "severity": "high | medium | low",
          "area": "<kebab tag>",
          "file": "<path:start-end>",
          "title": "<one line>",
          "detail": "<2-4 lines>",
          "recommendation": "<actionable fix>"
        }
      ]
    }
  ],
  "simplify_residuals": [
    {
      "agent": "reuse | quality | efficiency",
      "file": "<path:start-end>",
      "title": "<one line>",
      "detail": "<short reason simplify could not apply the change in-line>"
    }
  ]
}
```

- Either array may be empty. Both empty → return empty groups (totals zero).
- The orchestrator guarantees this structure. Do not validate beyond using the fields below; if a field is missing, treat it as absent (not an error).

## Classification rules

For every finding, sort into exactly one of two buckets.

### `in_place` — fix on the current epic branch before close

A finding is `in_place` when **all** of these hold:

- Localized to a single file (or 2–3 lines spanning ≤ 2 adjacent files).
- ≤ 30 lines of expected change.
- No breaking-change implications (no public API rename, no contract change).
- No new abstraction or module (no new interface, no new layer, no new service).
- The fix can be described in 2–3 lines of guidance.

Examples: missing null check, missing test case for a covered file, stale comment, dead import, unused branch, simplify residual that needs a tiny manual touch, mis-named variable, single-line off-by-one.

### `sub_epic` — spawn a new epic (or defer to a future one)

A finding is `sub_epic` when **any** of these hold:

- Cross-cutting (touches > 3 files, or spans multiple layers / packages).
- Architectural in nature (introduces or changes a layer boundary, ownership, or contract).
- Requires design discussion before a fix is safe.
- Introduces a new abstraction (new interface, new module, new service, new build step).
- Touches a public API or wire-format and requires migration.
- Fix scope is too large to write a 2–3 line outline for.

Examples: "no error boundary anywhere in the app", "auth flow allows session-token leak across tabs", "no integration tests for the payment path", "logging library is not pluggable", "DI container is bypassed in 7 modules".

### Ambiguous cases

If a finding fits neither bucket cleanly:

- `severity == "low"` → default to `in_place`.
- `severity == "high"` → default to `sub_epic`.
- `severity == "medium"` → re-apply the rules above; tie-break toward `in_place` if a 2–3 line fix outline can be written, else `sub_epic`.

## Output contract

Return **a single JSON object, nothing else**. No prose. No markdown code fences. No leading/trailing whitespace beyond the JSON itself.

```json
{
  "in_place_candidates": [
    {
      "id": "ip-001",
      "severity": "high | medium | low",
      "source": "review:architecture-focus | review:security-focus | review:testing-focus | simplify:reuse | simplify:quality | simplify:efficiency",
      "title": "<one line, ≤ 80 chars>",
      "file": "<path:start-end>",
      "fix_outline": "<2-3 lines, actionable, names symbols / files to touch>"
    }
  ],
  "sub_epic_candidates": [
    {
      "id": "se-001",
      "severity": "high | medium | low",
      "source": "review:architecture-focus | review:security-focus | review:testing-focus | simplify:reuse | simplify:quality | simplify:efficiency",
      "title": "<short, epic-worthy headline>",
      "scope_outline": "<3-5 lines: what an epic covering this would deliver>",
      "rationale": "<1-2 lines: why this is sub-epic-worthy, not in-place>"
    }
  ],
  "totals": { "in_place": <N>, "sub_epic": <N> }
}
```

Field rules:

- `id` — sequential, zero-padded to 3 digits, prefix `ip-` or `se-`. Number in the order items appear in the output array.
- `severity` — copy from the input finding. If the input lacks `severity`, assign by the ambiguous-case rule above and record the assigned value.
- `source` — exactly one of the six strings shown. Derive from input `agent` field with the appropriate `review:` or `simplify:` prefix.
- `file` — for `in_place` items, copy from the input verbatim. For `sub_epic` items, copy if the finding is anchored to a file; omit the field entirely if the issue is genuinely cross-cutting and no single anchor file applies.
- `fix_outline` — 2–3 lines, actionable. Names the function / symbol / file area. Not "consider refactoring".
- `scope_outline` — 3–5 lines describing what a new epic would deliver. Not the fix itself — the **boundary** of the work.
- `rationale` — why this cannot be done in-place. Cite one or two of the `sub_epic` rules above.
- `totals` — integer counts. MUST equal the lengths of the two arrays.

## Hand-off contract

This JSON is consumed by EPIC B #3 logic, which presents the user with a 3-action prompt:

1. **all sub-epic** — promote every `in_place_candidates` entry into `sub_epic_candidates` and queue all for `forge:create-epic`.
2. **fix-and-defer** — keep `in_place_candidates` for in-line fix on the current branch; mark `sub_epic_candidates` as deferred (no new epic this round).
3. **fix-and-spawn-now** — fix `in_place_candidates` inline on the current branch; spawn one new sub-epic per `sub_epic_candidates` entry via `forge:create-epic`.

The classifier output must therefore be **stable, deterministic, and self-contained**. Downstream logic does not re-read the source findings.

## Anti-hallucination guards

These are hard rules. Violating any of them is a defect.

- **Do not invent file paths.** Use `file` from the input verbatim. Do not normalize, shorten, or "fix" a path.
- **Do not fabricate severities.** Use the input severity. If absent, assign per the ambiguous-case rule and record the assigned value (do not silently default).
- **Do not duplicate findings.** If the same issue appears in both `review_findings` and `simplify_residuals` (same `file` and overlapping line range, or same `title` ± 10 characters of edit distance), merge into a single output item. Prefer the `review:*` source; mention the simplify residual once in `fix_outline` if it adds detail.
- **Do not import outside knowledge.** Classify only what is in the input. Do not infer issues "likely also affected" — that is a separate review run.
- **Output JSON only.** No leading prose. No trailing commentary. No ```json fences. No `// comments`. A single parseable JSON object.
- **Empty input → empty output.** If both `review_findings` and `simplify_residuals` are empty (or contain only empty `findings` arrays), return both candidate arrays empty and `totals: { "in_place": 0, "sub_epic": 0 }`.

## Test-case snippets

Documentation only — not runtime. Use these to validate that an edit to this prompt preserves behavior.

### Test 1 — single architectural finding → 1 sub-epic, 0 in-place

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

### Test 2 — single simplify reuse residual → 1 in-place, 0 sub-epic

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

### Test 3 — empty input → empty output

Input:

```json
{ "review_findings": [], "simplify_residuals": [] }
```

Expected output:

```json
{ "in_place_candidates": [], "sub_epic_candidates": [], "totals": { "in_place": 0, "sub_epic": 0 } }
```

### Test 4 — duplicate finding (review + simplify on same file:line) → single merged item

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

### Test 5 — three findings, exact-fidelity check

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

## What this prompt does NOT do

- Does not fix anything. Classification only.
- Does not call `forge:create-epic`. Hand-off to EPIC B #3 owns that.
- Does not modify `forge:epic-close` Step 4 wiring. That is EPIC B #3.
- Does not re-read source files. Classifies the input as given.
