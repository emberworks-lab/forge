# Interview-scaffold a new stack (step 4B)

Used when the resolved `~/.claude/skill-templates/<stack>/` folder is empty (or only has a placeholder README).

## Open the offer

Tell the user:

> "Stack `<X>` has no templates yet. Want to scaffold the basic kit-* skills now? It's a 5-10 minute interview; the result becomes reusable for future `<X>` projects."

If **no**: skip; the user can add skills later via `/init` or `/claude-md-management:claude-md-improver`. Generate a minimal CLAUDE.md anyway (step 5) — no skills section.

## If yes

For each "common" kit-skill (the list varies by stack — see the per-stack interview file under `stack-interviews/`):

1. Ask the user: "How do you typically scaffold a new `<feature / route / table / module>` in this kind of project? Walk me through the files you'd touch."
2. Compose a `SKILL.md` from the answers (use the writing-skill rules — `type: hybrid` unless the skill is genuinely one-shot).
3. Save the result to **two** places:
   - `~/.claude/skill-templates/<stack>/<kit-name>.md` — for future reuse.
   - `<project>/.claude/skills/<kit-name>.md` — for the current project.

## Stack-specific kit-* hint lists

See `stack-interviews/<stack>.md` for the recommended kit-* skill set per stack:

- `stack-interviews/web.md`
- `stack-interviews/backend-node.md`
- `stack-interviews/mobile-flutter.md` (not used in 4B — Flutter has its own scaffolder)
- `stack-interviews/mobile-native.md`
- `stack-interviews/library.md`

## Reminders

- Do not invent kit-* skills that the user did not describe — incomplete templates are worse than no templates.
- The composed SKILL.md must still pass `forge:writing-skill`'s `audit.sh`.
- After saving, mention the path in the project-init final output so the user knows where to evolve the templates.
