# Edge cases for `forge:create-ticket`

- **Doc reference doesn't exist**: tell the user "`docs/0X_*.md` not found — switching to Mode B?" Ask before proceeding.
- **Doc exists but lacks `## Acceptance criteria`**: tell the user, ask whether to extract from doc body manually or write fresh.
- **No tracker team detected**: ask once which existing team to use. Don't guess. Never offer to create a new team.
- **Brief is too vague to even draft a body**: ask one short follow-up. If still unclear, exit and tell the user to flesh out the brief.
- **User asks for a manual-setup ticket without describing user actions**: ask "які саме кроки користувач має виконати? нумерований список 3-7 пунктів".
- **`tracker.json` missing**: the first-use hook at the top of `forge:create-ticket` triggers automatically — runs the same flow as `forge:project-init --tracker-only` and writes `tracker.json` before proceeding.
