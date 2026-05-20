# forge

forge is a Claude Code plugin for AI-driven product engineering workflows. It ships a curated set of slash commands and subagents that cover the full development loop: ticket planning, epic orchestration, test-driven implementation, code review, and project bootstrap — designed for solo developers and small teams who want deterministic, composable automation over free-form prompting.

## Install

```
/plugin install forge@emberworks-lab
```

Verify the install:

```
/forge:hello
```

Full step-by-step setup: [docs/INSTALL.md](docs/INSTALL.md)

## Skill catalog

Full catalog with descriptions: [docs/SKILL-INDEX.md](docs/SKILL-INDEX.md)

| Group | Skills |
|---|---|
| Tracker pipeline | `create-epic`, `create-ticket`, `execute-epic`, `execute-ticket`, `epic-close`, `commit`, `pr-create` |
| Planning | `brainstorm`, `diagnose`, `grill-me`, `grill-with-docs`, `prototype`, `zoom-out` |
| Review | `simplify`, `simplify-branch`, `handle-review-feedback` |
| Debugging | `tdd`, `diagnose-deep` |
| Project init + Flutter | `project-init`, `dart-collect-coverage`, `dart-fix-runtime-errors`, `flutter-fix-layout-issues` |
| Runner agents | `linter-runner`, `test-runner` |
| Meta | `writing-skill`, `handoff`, `caveman`, `hello` |

## Philosophy

- **Slim, composable skills.** Each skill has a single responsibility. The [`writing-skill`](plugins/forge/skills/writing-skill/) meta-skill encodes the policy that all other skills follow.
- **One branch per epic.** Sub-issues commit to the epic branch; per-issue branches are not created.
- **Magic-word commits.** Commits link to tracker tickets via prefixes (`Closes #N:`, `Refs #N:`), enabling auto-close on PR merge.

## Credits

- [`forge:brainstorm`](plugins/forge/skills/brainstorm/), [`forge:tdd`](plugins/forge/skills/tdd/), [`forge:diagnose-deep`](plugins/forge/skills/diagnose-deep/) — adapted from obra's [superpowers](https://github.com/obra/superpowers) plugin.
- [`forge:caveman`](plugins/forge/skills/caveman/) — adapted from mattpocock's [skills](https://github.com/mattpocock/skills) repo.

Adapted skills are rewritten in forge's voice; no 1:1 copies. Each carries an `inspired-by` block in its frontmatter.

## Status

Alpha / bootstrap phase. Core tracker pipeline and review skills are functional. See [open issues](https://github.com/emberworks-lab/forge/issues) for planned work.
