# output-format — structured findings schema

This is the contract between each reviewer subagent and the `forge:review` orchestrator (and the downstream EPIC B classifier).

Every reviewer agent MUST return a single JSON object — no prose, no markdown fences, no leading/trailing commentary. The orchestrator parses it directly.

## Schema

```json
{
  "agent": "architecture-focus | security-focus | testing-focus",
  "stack": "flutter | web | backend | general",
  "mcp_used": true,
  "findings": [
    {
      "severity": "high | medium | low",
      "area": "<short kebab tag>",
      "file": "<path/from/repo/root.ext:start-end>",
      "title": "<one-line headline>",
      "detail": "<2-4 lines of explanation>",
      "recommendation": "<actionable fix>"
    }
  ]
}
```

### Field rules

- `agent` — one of the three exact strings above. Required.
- `stack` — what the orchestrator passed in; echoed back so the classifier can sort findings by platform without re-detecting.
- `mcp_used` — `true` if the agent invoked any `code-review-graph` MCP tool during its run, else `false`.
- `findings` — array. May be empty (`[]`). Empty is a valid, healthy result.

### Per-finding field rules

- `severity` — exactly one of `"high"`, `"medium"`, `"low"`. Match the agent's severity-guide section.
- `area` — short kebab-case tag, ≤ 24 chars. Examples: `auth`, `state-management`, `injection`, `flaky-test`, `layer-boundary`, `secret-leak`.
- `file` — repo-relative path with line range. Examples: `lib/auth/login.dart:42-58`, `src/api/users.ts:101`. For a single line use just `path:N`. For a whole-file finding use `path:1-EOF`.
- `title` — one line, ≤ 80 chars. Action-oriented headline. Examples: `"Hard-coded API key in source"`, `"New payment route ships without auth check"`.
- `detail` — 2–4 lines explaining the problem and why it matters. Cite the relevant principle from the KB doc you read (e.g. "violates layer-boundary rule in 02_mobile_flutter.md").
- `recommendation` — concrete, actionable fix. Not "consider refactoring" — write what to do. Examples: `"Move the secret to env var SUPABASE_KEY and read via dotenv at startup."`, `"Inject Clock and pass it via constructor; replace DateTime.now()."`.

## Examples

### Empty result (valid)

```json
{
  "agent": "security-focus",
  "stack": "flutter",
  "mcp_used": false,
  "findings": []
}
```

### One high-severity finding

```json
{
  "agent": "security-focus",
  "stack": "backend",
  "mcp_used": true,
  "findings": [
    {
      "severity": "high",
      "area": "secret-leak",
      "file": "src/config/stripe.ts:14",
      "title": "Hard-coded Stripe secret key in source",
      "detail": "stripe.ts line 14 embeds 'sk_live_…' directly. Per 00_general.md, secrets MUST come from environment. get_impact_radius shows this module is imported by 11 files, so the leak is broadly accessible.",
      "recommendation": "Remove the literal, load via process.env.STRIPE_SECRET_KEY, and add the key name to .env.example. Rotate the existing key — it is now considered compromised because it was committed."
    }
  ]
}
```

## Validation

The orchestrator parses each agent's output with a lenient JSON parser. On parse failure:

1. Record `findings: []` for that agent.
2. Note `parse_error: true` in the orchestrator's summary block.
3. Continue — one failed agent does not abort the run.

## Downstream — EPIC B classifier

The classifier prompt is defined in `plugins/forge/skills/epic-close/references/classifier-prompt.md` (EPIC E #34). It consumes the merged JSON of all three agents and produces:

- A deduped, severity-ranked actionable list.
- Per-finding "auto-fixable?" classification.
- Triage buckets (must-fix / nice-to-have / informational).

Classifier invocation + user-prompt logic is wired by EPIC B #3 (see `forge:epic-close` Step 3a.4 HTML comment). `forge:review` itself only emits the JSON.
