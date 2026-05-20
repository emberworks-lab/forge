# Edge cases for `forge:execute-epic`

- **Epic has no sub-issues** — exit with "epic has no sub-issues; create them via /create-epic first"
- **Epic is already DONE** — ask user "epic seems closed already; re-run? (y/n)"
- **All sub-issues already DONE** — tell user "all sub-issues done; epic ready for /epic-close"
- **Subagent spawn fails (rate limit / quota)** — wait + retry once; if still fails, halt and report
- **User starts manual-setup gate but never responds** — that's fine; this skill is paused waiting; the user can resume by saying "ready" later
- **Branch has uncommitted work when entering** — refuse to start; tell user to commit/stash first
- **Sub-issue's `## Depends on` references a ticket NOT in this epic** — log a warning but don't block execution; treat as if the dependency is resolved externally
- **A sub-issue is in DOING / IN PROGRESS state in the tracker (not DONE, not TODO)** — ask user "EMB-X is IN PROGRESS — work in flight elsewhere? skip / re-execute / abort?"
- **`tracker.json` missing** — fall back to current Linear-MCP behavior (see dispatch note at top of SKILL.md). This fallback exists for legacy repos without `tracker.json`.
