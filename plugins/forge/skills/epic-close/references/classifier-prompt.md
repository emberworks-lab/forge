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

<!-- Regression test snippets: see plugins/forge/skills/epic-close/references/classifier-prompt-tests.md.
     They are intentionally NOT in this file so the orchestrator does not pay ~800 tokens per
     classifier call to ship documentation that the runtime subagent never executes. -->

## What this prompt does NOT do

- Does not fix anything. Classification only.
- Does not call `forge:create-epic`. Hand-off to EPIC B #3 owns that.
- Does not modify `forge:epic-close` Step 4 wiring. That is EPIC B #3.
- Does not re-read source files. Classifies the input as given.
