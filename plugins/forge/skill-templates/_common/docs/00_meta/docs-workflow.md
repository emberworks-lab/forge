# Docs Workflow (project instance)

Project-specific routing and rules for `docs/`.

See `~/.claude/docs/conventions/docs-workflow.md` for the universal pattern this project follows.

## Folder layout

- `00_meta/` — meta-docs (decisions-log, roadmap, this file, glossary)
- `0X_tech/` — technical / design docs per area (added as project grows)
- `0X_product/` — product docs (optional)

## Per-file conventions

*(Inherits universal conventions; add project-specific overrides here as they emerge.)*

## Mandatory cross-doc updates

- Locking a decision → append `decisions-log.md` entry; update related tech doc if applicable; update `glossary.md` if new term
- Changing roadmap scope → update `roadmap.md`; reflect in Linear if relevant

## What does NOT belong in `docs/`

- Code (lives in source tree)
- Active Linear tickets (Linear is the system of record)
- Session-only chat output
- Secrets / credentials

---

*Last updated: <date>*
