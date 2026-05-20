# Docs scaffold (step 6)

Triggered when step 2.5 answer was **Yes (Recommended)** or **Yes**.

## Actions

1. `mkdir -p <project>/docs/00_meta/`.
2. Copy the 4 skeleton files from `plugins/forge/skill-templates/_common/docs/00_meta/`:
   - `decisions-log.md`
   - `roadmap.md`
   - `docs-workflow.md`
   - `glossary.md`
3. In each copied file, substitute placeholders:
   - `<date>` → today's date in ISO format (`date +%Y-%m-%d`).
   - `<project_name>` → the project name from the interview.

## CLAUDE.md injections

Append a `## Documentation inventory` section to `<project>/CLAUDE.md`:

```markdown
## Documentation inventory

Skills load these on demand — don't preload them.

| Doc | When to read |
|---|---|
| `docs/00_meta/roadmap.md` | Strategic timeline; read FIRST when planning a new epic, milestone change, or scope decision |
| `docs/00_meta/docs-workflow.md` | Before recording / persisting / deferring anything in docs/ |
| `docs/00_meta/decisions-log.md` | When making a non-trivial design / architectural decision (use `/log-decision`) |
| `docs/00_meta/glossary.md` | When introducing or referencing project-specific terminology |
| `plugins/forge/docs/conventions/docs-workflow.md` | Universal pattern (this is what `00_meta/docs-workflow.md` is an instance of) |
```

Insert this row into `## Mandatory rules` (preserve existing rows):

```markdown
| Append to docs/00_meta/decisions-log.md when making non-trivial design decisions; use /log-decision skill | Decisions outlive chat | /log-decision |
```

## If the answer was No / Skip

Do nothing here. The `## Documentation inventory` section in CLAUDE.md is left empty with the note "Populate as docs/ grows" (handled in `references/claude-md-scaffold.md`).

## Note for the Flutter path

The Flutter scaffolder already copies `docs/00_meta/` and injects these sections (it auto-resolves the 2.5 answer for `mobile-flutter`). This file applies only to non-Flutter stacks.
