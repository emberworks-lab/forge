# `/caveman` opt-in policy

**Status:** `PROVISIONAL — calibrate after pilot completes`
**Ticket:** [EPIC F] #2 (forge#41)
**Source data:** [`../caveman-pilot-2026-05.md`](../caveman-pilot-2026-05.md) (currently `DEFERRED`)

This document is the decision policy for whether a forge skill should opt in to `/caveman`. All numeric thresholds are placeholders drawn from first-principles reasoning and the `/caveman` source's published claims — they MUST be recalibrated once the pilot in `caveman-pilot-2026-05.md` returns measured data.

## What `/caveman` does (one-liner)

Switches the model to ultra-compressed output. Drops filler, preserves technical content. Compresses **output only** — input tokens (system prompt, tool result re-injection, prior turns) are unaffected.

Published claim: `~75%` output reduction. Realistic on real workloads: **7-22%** total economy (because output is typically 20-40% of total tokens in a tool-using session).

## Decision matrix

A skill should opt in to `/caveman` only if **both** thresholds clear:

| Axis | Threshold (PROVISIONAL) |
|---|---|
| Output economy | ≥ 15% |
| Debug-clarity (post-caveman) | ≥ `acceptable` |

If economy ≥ 40% AND clarity = `clear`, the skill may force auto-on at start + auto-off at end without user prompt. Otherwise, opt-in is **propose-only**: skill suggests `/caveman` to the user as Step 0, user types `yes` to enable.

## Per-skill recommendation (PROVISIONAL)

Based on expected output volume + debuggability cost, before pilot data:

| Skill | Recommendation | Reasoning (until calibrated) |
|---|---|---|
| `forge:execute-epic` | **Most likely opt-in** | Long per-ticket summaries dominate output; debuggability cost is low because per-ticket commits preserve the substance |
| `forge:create-epic` | Likely opt-in | Structured output (epic body + sub-issue bodies) is verbose; compression unlikely to lose required structure |
| `forge:execute-ticket` | Maybe opt-in | Output is mid-volume but heavily inspected; debuggability cost may be high |
| `forge:diagnose` | Skip | Hypothesis text needs to be readable for the user to validate; compression risks losing chains of reasoning |
| `forge:brainstorm` | Skip | Output is mostly questions; nothing to compress |
| `forge:simplify` / `forge:simplify-branch` | Skip | Output is specific cited changes; precision > brevity |
| `forge:review` | Skip | Reviewer findings need to be persuasive; compression hurts |
| `forge:project-init` | Skip | One-shot interview; output is structured prompts |
| Casual Q&A (no skill) | User choice | Out of policy scope |

## When NOT to opt in

Hard rules — never auto-enable `/caveman` for skills that:

- Produce content shown to **third parties** (PR descriptions, ticket comments visible to reviewers, public docs). Compressed caveman-style text reads as terse and unprofessional outside a developer chat.
- Generate code (caveman-mode does not apply to code output, but tool-use surrounding text loses context for debugging).
- Run inside `forge:writing-skill` itself (recursion: cannot author readable SKILL.md with caveman compression).

## Caveman opt-in pattern (the technical shape)

When a skill opts in:

1. **Step 0** (before any heavy loop): propose `/caveman` to the user. Show the published claim + the per-pilot economy number for this skill type. Wait for explicit `yes` / `no` / `skip`.
2. **On `yes`**: emit `/caveman on` as the first user-facing line of work. Continue the skill body normally.
3. **At skill completion** (success path AND error path): emit `/caveman off` before final output. Auto-restore is non-negotiable; leaving caveman on poisons subsequent unrelated work in the same session.
4. **Audit**: a future audit rule may check that any SKILL.md containing `/caveman on` also contains `/caveman off`. Not enforced today.

Authored skill examples reference: `plugins/forge/skills/writing-skill/references/caveman-opt-in-pattern.md`.

## How to recalibrate

When the pilot in `caveman-pilot-2026-05.md` completes:

1. Replace **Status** at the top of this file with `CALIBRATED — YYYY-MM-DD, from N=6 pilot`.
2. Update the thresholds table with the measured 25th-percentile economy across all skill types that produce useful work (typically lowers the `≥ 15%` floor).
3. Update the per-skill recommendation table: `Most likely opt-in` becomes concrete `OPT IN` or `SKIP` based on each skill's measured economy + clarity.
4. Open EPIC F #3 (forge#42) if any skill flips to `OPT IN` — that ticket lands the actual patches.

## Recalibration trigger

Re-run the pilot if any of the following holds:

- The `/caveman` skill is materially rewritten.
- Base model output cost drops > 50% (caveman ROI shrinks proportionally).
- A new skill ships that's > 30% of monthly invocation and was not in the pilot.

## Linked artifacts

- Source pilot: [`../caveman-pilot-2026-05.md`](../caveman-pilot-2026-05.md)
- Pattern reference: [`../../skills/writing-skill/references/caveman-opt-in-pattern.md`](../../skills/writing-skill/references/caveman-opt-in-pattern.md)
- Decision rationale: [`/decision-log/2026-05-21-epic-F.md`](../../../../decision-log/2026-05-21-epic-F.md)
