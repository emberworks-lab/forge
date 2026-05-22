---
name: update-docs-meta
description: Project-wide documentation child of forge:update-docs — refreshes the root-level owner-overview and 00_meta registries (roadmap, decisions-log, glossary) after an epic. Dispatched by forge:update-docs when features, decisions, dependencies, or milestones changed.
type: hybrid
---

# forge:update-docs-meta

The project-wide docs child of `forge:update-docs`. Owns the cross-cutting documents that always live in the resolved root `docs/`, never in a platform sub-folder. Markdown source only; never writes HTML (format law lives in the parent).

## Scope — the documents this child owns

| Doc | Location | What it holds |
|---|---|---|
| `docs/owner-overview.md` | root | Overview, Features (Shipped/In-progress/Planned), Phases, Tech stack, Libraries, Conventions |
| `docs/00_meta/roadmap.md` | root | Milestone status, phase ordering, deferred items |
| `docs/00_meta/decisions-log.md` | root | Append-only locked decisions |
| `docs/00_meta/glossary.md` | root | Project terminology |

## Inputs

`--root <path>` (resolved by the parent), `--epic <ref>` (the just-closed epic, to know which features/decisions to reconcile), `--dry-run`.

## Flow

### 1. owner-overview.md

Refresh only the `<!-- auto:<key> --> … <!-- /auto:<key> -->` blocks; never touch `<!-- manual -->` prose.

- **Features.Shipped / Features.In-progress** — using `--epic`, move the just-closed epic's features from In-progress → Shipped (read the epic + its sub-issues via the tracker backend recipe). Without `--epic`, reconcile against current tracker state.
- **Phases** — sync the current/next phase line with `roadmap.md`.
- **Tech stack** — refresh from the project's manifest(s) if the stack changed.
- **Libraries & tools** — refresh the active opt-in module list from the manifest.

If `owner-overview.md` is absent, skip it (single-file projects may not have one).

### 2. roadmap.md

- Deferred item added → append to the deferred section with reason + re-eval trigger.
- Deferred item resolved → drop it, ensure the decision is logged, note the spec update.
- Milestone status flipped → update the milestone table.

### 3. decisions-log.md

Append an entry for any decision locked during the epic (newest at top, per the `docs-workflow.md` format). If a session is interactive, prefer `/log-decision`; in an automated sweep, append directly.

### 4. glossary.md

Any new domain term introduced in the epic's docs → add an alphabetical entry. Renamed term → keep the old entry with a rename note for one cycle.

### 5. Report

List each doc touched (or, in `--dry-run`, would touch) with a one-line reason.

## Do not

- Do not touch `<!-- manual -->` content.
- Do not write or edit HTML — MD source only.
- Do not duplicate ticket bodies or chat output into docs.
- Do not commit — the caller owns commit semantics.

## What this child does not cover

- **API reference** — `forge:update-docs-api`.
- **Design specs / ADR** — `forge:update-docs-design`.
- **Scope analysis + routing** — the parent `forge:update-docs`.
