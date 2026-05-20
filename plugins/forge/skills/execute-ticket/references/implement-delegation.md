# Step 6 — Implementation phase delegation

Step 6 of `forge:execute-ticket` chooses one of two execution patterns.

## 6a. Detect ticket type

- **FORGE-N config-only ticket** (markers: body mentions `~/.claude/`, "no git", "no lint", "no commits", or the ticket targets `~/.claude/` infrastructure directly): use the ad-hoc subagent pattern in `forge-config-fallback.md`. TDD is not applicable to config-only doc/skill edits.
- **Standard project ticket** (Flutter / backend / web — the default): delegate the implementation phase to `forge:subagent-driven-development`.

## 6b. Standard project ticket — delegate to `forge:subagent-driven-development`

1. **Determine plan source:**
   - Mode A → the referenced `docs/0X_*.md` IS the plan.
   - Mode B-a / B-b / B-c → the ticket body (after Step 4 prep) IS the plan.

2. **Invoke `forge:subagent-driven-development`** with the plan. That skill internally dispatches per-task subagents (the implementer following TDD: red → green → refactor; a spec compliance reviewer; a code quality reviewer). Those internal subagents run with **`opus`** or **`sonnet`** per the project's defaults; never `haiku`. The skill returns DONE when all tasks are complete and reviewed.

3. **The orchestrator (`forge:execute-ticket`) stays in charge of tracker, git, and commit semantics.** `forge:subagent-driven-development` handles code work and per-task review only. Do not delegate tracker comments, `commit_close_phrase`, or commit steps to it.

4. After it returns, continue to Step 7 (linter-runner + test-runner). These project-level checks complement the per-task verification.

## 6c. Architecture + editing rules (apply in both modes)

- Follow architecture rules from `CLAUDE.md > Mandatory rules` strictly. Don't bypass barrels, lint rules, test conventions.
- Read each file before editing it (Edit tool requirement).
- Make minimal, targeted changes. No "while I'm here" refactors.
- For codegen-dependent files (Drift, freezed, json_serializable, build_runner): run codegen after schema/source change.

If you're not sure mid-implementation:

- Mode B-b is the right move (interview); but if you're MID-implementation and uncertain → ask the user inline rather than guessing.
