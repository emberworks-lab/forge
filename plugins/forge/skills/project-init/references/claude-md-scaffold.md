# CLAUDE.md generation (step 5)

Read `plugins/forge/docs/conventions/claude-md-template.md`. Substitute placeholders below; write the result to `<project>/CLAUDE.md`.

## Placeholder substitution

| Placeholder | Source |
|---|---|
| `<Project name>` | `package.json` / `pubspec.yaml` `name` field, or ask the user. |
| `<tagline>` | Ask the user (1 line). |
| `<Stack>` | Composed from interview answers (e.g. "Next.js + tRPC + Drizzle + Postgres + Cloudflare Workers"). |
| Essential commands table | Stack-specific; populate from the per-stack examples in the template's "Per-stack populate examples" section (e.g. `flutter test`, `flutter analyze`, `dart format`). |
| Architecture | Short statement — either the stack default OR ask the user (1-2 paragraphs). |
| Mandatory rules | Stack defaults from `plugins/forge/skill-templates/<stack>/RULES.md` if present, else a minimal set; if step 2.5 = Yes, append the `/log-decision` row (see `references/docs-scaffold.md`). |
| Documentation inventory | If step 2.5 = Yes, inject the full inventory table (see `references/docs-scaffold.md`); otherwise leave the section empty with the note "Populate as docs/ grows". |
| Linear workflow | Prefix + team from the common interview. |
| Global references | Pre-filled paths to `plugins/forge/docs/testing/<platform>.md`, etc. <!-- TODO: linting docs not migrated, deleted in EPIC E --> |
| Skills (project-local) | List of copied `kit-*` skills under `<project>/.claude/skills/`. |
| Skills (global) | Standard list — `/create-epic`, `/execute-ticket`, etc. |

## After substitution

- If step 4C ran successfully (per-project SKILLS.md generated), add one pointer line under `## Skills`:

  > See `.claude/SKILLS.md` for the auto-generated, stack-filtered list of available global skills.

- If step 4C was skipped (e.g. mobile-flutter — scaffolder produced its own CLAUDE.md), the Skills section is owned by the scaffolder and this step is bypassed entirely (`references/flutter-scaffolder.md` step 4A-flutter.4.3).

## Reminders

- The template lives in `plugins/forge/docs/conventions/claude-md-template.md`. Read it fresh each run; it evolves.
- Do not inline content from the template's per-stack examples — keep CLAUDE.md concise; let the user evolve it.
- The "Architecture" paragraph is the hardest to auto-fill; default to asking the user unless the stack has a clear convention.
