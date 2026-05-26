# forge skill routing rules

These rules **OVERRIDE** the superpowers `using-superpowers` "invoke at 1% chance"
instruction in any project where the forge plugin is installed.

## 1. Tie-break — MANDATORY

When a forge skill and a superpowers skill cover the same task, you **MUST**
invoke the forge one:

| Concern | Use | Not |
|---|---|---|
| Creative / design / behavior-change | `forge:brainstorm` | `superpowers:brainstorming` |
| TDD discipline | `forge:tdd` | `superpowers:test-driven-development` |
| Before completion claims | `forge:verification-before-completion` | `superpowers:verification-before-completion` |
| Bug / regression diagnosis | `forge:diagnose` (dispatches `forge:diagnose-deep`) | `superpowers:systematic-debugging` |
| Plan execution with subagents | `forge:subagent-driven-development` | `superpowers:subagent-driven-development` |

## 2. Calibration — OVERRIDES superpowers "1% MUST"

Heavy process skills (`forge:brainstorm`, `forge:tdd`,
`forge:verification-before-completion`, `forge:diagnose`) fire **only** when the
task genuinely modifies behavior or designs new functionality.

**SKIP** them for:

- trivial edits, config tweaks, doc / comment fixes
- single-file mechanical changes
- direct user requests like "edit X", "rename Y", "add this line"

The superpowers "1% chance → MUST invoke" rule does **NOT** apply to heavy
process skills in this project. Use forge skills deliberately, not reflexively.

## 3. Forge-first in forge-managed projects

In any project whose `.claude/tracker.json` exists (forge-managed), prefer
`forge:*` skills over `superpowers:*` for all overlapping concerns.
