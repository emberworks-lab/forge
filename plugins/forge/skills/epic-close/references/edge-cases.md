# Edge cases

Handled by `forge:epic-close`.

- **Incomplete sub-issues**: flag the IDs to the user; ask "закриваємо попри це / залишаємо / переносимо в наступний епік?" Do nothing until answered.
- **No branch found / epic not detected**: ask once, then exit cleanly.
- **Simplify pass fails or is noisy**: surface the issue, let the user decide. Don't push through.
- **User wants to close epic but `forge:execute-epic` was never run**: that's fine — manual-only execution path. Verify manual testing was done some other way before posting the close comment. Tests-pass gate (Step 0b) still applies.
- **Tests-pass gate fails at Step 0b**: exit immediately. Do NOT auto-fix at this level — failures here are integration-level and need human triage.
- **Path A merge command fails** (conflict with `<base>`, push rejected): halt with the git output. Do NOT retry. User resolves manually.
- **User picks Path C but tests are passing**: still allow it — manual testing or stakeholder feedback is its own veto, not visible to the test suite.
- **`tracker.json` missing**: fall back to legacy Linear-MCP behavior (see dispatch note in SKILL.md). Phased out in a future cleanup epic.
