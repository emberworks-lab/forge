# FORGE-N config-only ad-hoc subagent fallback

For **FORGE-N config-only tickets only** (tickets targeting `~/.claude/` infrastructure where TDD / lint / test commands are not applicable). Standard project tickets delegate to `forge:subagent-driven-development` (see `implement-delegation.md`) — they do NOT use this template.

When spawning the ad-hoc subagent for a FORGE-N config ticket, use the `sonnet` model (mechanical doc/skill edits) unless the work needs design judgement, in which case use `opus`. Never `haiku`.

Prompt:

```
Execute FORGE ticket <TICKET-ID>.

Context:
- Ticket title: <title>
- Ticket body: <full body>
- Target: ~/.claude/ infrastructure (NOT a git repo; no linter, no test runner, no commits)
- Verification gate: open each file you edited and confirm the change is present in the same turn

You MUST:
- Read the files you are editing before editing them
- Make targeted edits per the ticket's stated scope
- Verify changes are present by re-reading edited files in the same turn
- Return a structured result using one of these statuses:
  - `DONE — <summary of changes>`
  - `DONE_WITH_CONCERNS — <summary>; concerns: <…>`
  - `NEEDS_CONTEXT — missing: <what>` (the orchestrator will provide and re-dispatch)
  - `BLOCKED — reason: <context|reasoning|too-large|wrong-plan>; details: <…>`

You MUST NOT:
- Run git commands
- Run flutter/dart/lint/test commands
- Create branches or commit
- Modify tracker ticket status
```

## Subagent status enum

Same as Step 6b — the orchestrator handles `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED` per the table in SKILL.md.
