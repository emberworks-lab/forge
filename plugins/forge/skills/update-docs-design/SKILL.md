---
name: update-docs-design
description: Design-doc drift detection child of forge:update-docs — checks whether the epic's code changes touched an area covered by a design spec or ADR, and flags any that may now be stale. Surfaces prompts; never rewrites human prose.
type: hybrid
---

# forge:update-docs-design

The design-and-ADR child of `forge:update-docs`. Rich prose specs (`docs/0X_<area>/*`, `docs/adr/*`) are human authorship — this skill does **not** rewrite them. It detects when code has drifted from a spec and **flags** it for the human, so a complex project's documentation (e.g. Embergard's) stays alive instead of silently rotting.

Markdown only; never writes HTML (format law lives in the parent).

## Why flag, not edit

Design specs encode intent and rationale — a synthesised rewrite would fabricate reasoning the author never gave. So the contract is: **find probable staleness, surface it, let the human decide.** This mirrors how `forge:update-docs-api` handles `errors.md` (hand-written, prompt-surfaced).

## Inputs

`--root`, `--platform <path>` (or root), `--epic`, `--dry-run`.

## Flow

### 1. Pre-analysis — is a pass even needed?

From the epic's diff + the `--epic` sub-issues, determine which code areas changed. Cross-reference against the spec inventory in `<root>/docs/00_meta/docs-workflow.md` (the routing cheat-sheet that maps areas → specs). If no changed area maps to any spec → report "no design docs need review" and exit. This is the cheap early-out.

### 2. Map changed areas → candidate stale specs

For each spec whose area was touched, gather a signal of probable drift:

- The spec references a symbol / module / endpoint that the diff renamed or removed.
- The spec describes a flow the diff materially changed (new branch, removed step).
- An ADR's decision was contradicted by the change (e.g. ADR says "use X", diff introduces Y).

### 3. Surface flags (do not edit)

For each candidate, emit a flag:

```
DRIFT? <spec path> — <one-line reason> (changed: <files>)
  Suggested: <review the section on … / log a superseding ADR / update the diagram>
```

Group by spec. Make no edits to spec prose. The only edits this child may make are mechanical and unambiguous: a renamed term inside a spec, when the rename is also being applied by `forge:update-docs-meta` to the glossary (kept consistent), and only inside an `<!-- auto -->` block if the spec has one.

### 4. Report

List the flags (or, in `--dry-run`, the same — this child is advisory by nature, so its output is identical with or without `--dry-run`).

## Do not

- Do not rewrite or "improve" design-spec or ADR prose — flag, never author.
- Do not write or edit HTML — MD only.
- Do not delete a spec because code changed — staleness is the human's call.
- Do not commit — the caller owns commit semantics.

## What this child does not cover

- **owner-overview / roadmap / glossary** — `forge:update-docs-meta`.
- **API reference** — `forge:update-docs-api`.
- **Authoring a new design doc** — that is design work, not a sync.
