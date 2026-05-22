# Curated subagent prompt template

**Curation rule (REQUIRED, especially in parallel groups):** the controller (this skill, in main session) MUST curate the prompt per subagent. NEVER pass a list of tickets and let the subagent pick. NEVER inherit context from a sibling subagent. Each subagent starts fresh with:

- Its specific ticket ID + body
- Its specific mode + executor assignment
- Pointers to globals it might need (`CLAUDE.md`, conventions docs)

If you find yourself thinking "I'll let one subagent decide which of these to work on" — that's the anti-pattern. Make the decision in the controller, then dispatch with a curated prompt.

When spawning a subagent for a sub-issue, use the model named on the ticket's executor label (`opus` or `sonnet` — never `haiku` in this plugin) and this prompt structure:

```
Execute tracker ticket <TICKET-ID> as a sub-issue of epic <EPIC-ID>.

Use the forge:execute-ticket skill. Pass `--commit` so this work lands as a magic-word commit on the current branch.

Context:
- Ticket title: <title>
- Mode: <A | B-a | B-b | B-c>
- Executor assigned: <opus | sonnet>
- Project: read CLAUDE.md at the project root for full context (essential commands, mandatory rules, skill routing)
- Branch: you're already on <branch-name>; do not create a new branch

Globals to consult as needed:
- plugins/forge/docs/conventions/tracker-tickets.md
- plugins/forge/docs/conventions/git-workflow.md
- plugins/forge/docs/testing/00_general.md + the platform-specific testing doc
<!-- TODO: linting docs not migrated, deleted in EPIC E -->
- (linting docs not available; use project CLAUDE.md linter commands instead)

You MUST:
- Run linter via linter-runner agent (mode=fix)
- Run tests via test-runner agent (mode=report; mode=fix if failures, max 3 iters)
- Halt cleanly if lint or tests still fail after fix attempts. Do NOT commit a broken state.
- Generate manual test cases as a tracker comment on this ticket
- Commit + push are handled by `forge:execute-ticket` Step 11 because you passed `--commit`: it invokes `forge:commit` (backend magic-word phrase + co-author footer + safe staging), then pushes the branch. If push fails (network, auth, branch-protection), it warns and continues — do NOT halt the ticket. Per-ticket push gives visibility + resilience; auto-close still requires PR merge to default branch.

You MUST NOT:
- Modify other tickets
- Create branches
- Change tracker ticket status manually (commits do that on merge)
- Edit files outside this ticket's scope
- Re-run the e2e setup gate (forge:execute-ticket Step 3.5) — the epic orchestrator already ran it once before dispatching you; skip it entirely. The opted-in e2e run step (forge:execute-ticket Step 8.5) still applies normally.
- Push to default (`main` / `develop`) — only push the feature branch.

Return final status as one of:
- DONE — committed; <SHA>; <files changed>; <tests passed>
- HALTED — reason: <lint|test|other>; details: <…>
```
