# `/caveman` empirical pilot — execution template

**Status:** `DEFERRED — requires human-driven execution`
**Ticket:** [EPIC F] #1 (forge#40)
**Last touched:** 2026-05-21 (template only; no measured data yet)

This document is the **execution protocol** for the `/caveman` token-economy pilot. It was scaffolded autonomously and the per-session data tables are intentionally empty — they MUST be filled by a human running real Claude Code sessions, because:

- Token measurement requires reading the live UI counter or per-turn telemetry that an unattended agent cannot observe on its own conversation.
- Debug-clarity scoring is a third-party judgement on output quality — self-scoring is biased and not what the ticket asks for.

When a human runs the pilot, fill the tables below, replace the **Status** line with `COMPLETED — N=6 paired data points, YYYY-MM-DD`, and commit. Downstream artifacts (`docs/conventions/caveman-policy.md`) reference this file by path.

---

## Pilot design

Six representative paired sessions. Each session is run twice: once normally, once with `/caveman` toggled at the start and `/caveman off` at the end.

| Session type | Count | Why this type |
|---|---|---|
| `forge:execute-ticket` | 2 | Highest output volume; per-step narration is the main cost target |
| `forge:brainstorm` | 1 | Dialectic; output is mostly question-asking, low compression headroom expected |
| `forge:diagnose` | 1 | Mixed: hypothesis text + tool call results; medium headroom |
| `forge:create-epic` | 1 | Long structured output (epic body + sub-issue bodies); high headroom |
| Casual Q&A | 1 | Control: minimal context, short output; should show smallest economy |

## Measurement protocol

For each paired session:

1. Open a fresh Claude Code session.
2. Type the **same first prompt** in both runs (paste from a saved seed prompt).
3. Run baseline first, then caveman run. (Order matters: caveman-first biases the human into expecting brevity in the baseline.)
4. Record:
   - **Input tokens** (sum across turns) — read from telemetry log `~/.claude/telemetry/` or UI per-turn counter
   - **Output tokens** (sum across turns)
   - **Turn count** (number of model turns)
   - **Wall-clock duration** (start of first user prompt to last model response)
   - **Debug-clarity score** — `clear / acceptable / unclear`. Score immediately after the run, before reading the other run.
   - **Notable surprises** — any specific phrase the agent dropped that you wanted, any ambiguity that cost you a re-prompt
5. After both runs, compute:
   - **Output economy %** = `1 - (output_caveman / output_baseline)`
   - **Total economy %** = `1 - ((input_caveman + output_caveman) / (input_baseline + output_baseline))`
   - Note: input economy is typically zero — `/caveman` compresses output, not the system prompt or tool result re-injection.

## Per-session results

### Session 1 — `forge:execute-ticket` (run A)

| Field | Baseline | Caveman | Δ |
|---|---|---|---|
| Input tokens | _ | _ | _ |
| Output tokens | _ | _ | _ |
| Total tokens | _ | _ | _ |
| Output economy % | — | — | _ |
| Total economy % | — | — | _ |
| Turn count | _ | _ | _ |
| Wall-clock | _ | _ | _ |
| Debug-clarity | _ | _ | _ |

**Seed prompt:** _(paste exact text used)_

**Surprises:** _(anything that affected re-prompts or quality)_

---

### Session 2 — `forge:execute-ticket` (run B, different ticket)

_(same table shape — copy from Session 1)_

---

### Session 3 — `forge:brainstorm`

_(same table shape)_

---

### Session 4 — `forge:diagnose`

_(same table shape)_

---

### Session 5 — `forge:create-epic`

_(same table shape)_

---

### Session 6 — Casual Q&A

_(same table shape)_

---

## Roll-up

| Session type | Output economy % | Debug-clarity (baseline → caveman) |
|---|---|---|
| `forge:execute-ticket` (avg of 2) | _ | _ |
| `forge:brainstorm` | _ | _ |
| `forge:diagnose` | _ | _ |
| `forge:create-epic` | _ | _ |
| Casual Q&A | _ | _ |
| **Median across all 6** | _ | _ |

## Honest narrative

_(write 2-3 paragraphs once data is in: what surprised you, what the numbers actually say vs the `/caveman` source's `~75%` claim, what types of work benefit, what types don't, where `/caveman` made debugging harder)_

## Recalibration trigger

Re-run this pilot if any of the following happens:

- Base model output cost drops > 50% (caveman ROI shrinks proportionally)
- `/caveman` skill is materially rewritten (compression rules change)
- A new skill type ships that's >30% of monthly invocation (re-include in pilot)

## Downstream artifacts depending on this file

- `plugins/forge/docs/conventions/caveman-policy.md` — references the roll-up table for threshold calibration
- `plugins/forge/skills/writing-skill/references/caveman-opt-in-pattern.md` — references the policy file for "when to opt in"

If this file's status remains `DEFERRED`, both downstream files MUST flag their numbers / thresholds as `PROVISIONAL`.
