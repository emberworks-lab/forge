---
name: update-docs
description: Sync a project's docs with the code after implementation — analyse the epic's scope, decide whether any docs need touching, then route to the per-type children (meta / api / design). Skips children whose domain the epic didn't touch. Invoked by epic-close and manually.
type: fundamental
inspired-by:
  - author: emberworks-lab
    repo: github.com/emberworks-lab/forge
    skill: kit-update-docs
    relation: structure
---

# forge:update-docs

The umbrella for documentation maintenance. This skill owns **scope analysis** (what did this epic actually change, and does any doc need updating at all?) and **routing** to the per-type children. It does not edit docs itself — the children do.

```
forge:update-docs  (this skill — scope analysis + router)
├── forge:update-docs-meta     project-wide root docs (owner-overview, roadmap, decisions-log, glossary)
├── forge:update-docs-api      backend API reference (Swagger/OpenAPI or hand-written MD)
└── forge:update-docs-design   design docs + ADR drift detection
```

Complements `/log-decision` (which captures a decision the moment it locks). This skill is the after-implementation sweep.

## Format law (applies to every child)

- **Source-of-truth is always Markdown** (plus `openapi.json` / `asyncapi.yaml` for API specs). MD is git-diffable, agent-readable, and safely editable in `<!-- auto:<key> -->` guard blocks.
- **HTML is a generated presentation layer, never hand-written.** No child ever writes or edits HTML. Polished views come from rendering MD/specs (Swagger UI, Redoc, AsyncAPI HTML, or an MD→site build) — those are build artifacts, not source.
- **Never touch content inside `<!-- manual --> … <!-- /manual -->` guards** — that is the user's prose.

## When invoked

- **Auto:** `forge:epic-close` docs-sync step (after a branch lands, before merge), and after a dependency or milestone change.
- **Manual:** `/forge:update-docs` when finishing a branch or after any stack-touching change.

## Inputs

Optional: `--epic <ref>` (the just-closed epic, so children know which features/decisions to reconcile), `--since <ref>` (diff base; default = merge-base with the default branch, or `HEAD~1`), `--dry-run` (report routing + proposed edits, apply nothing).

## Flow

### 1. Resolve project root + platform map

Read `<project>/.claude/tracker.json`. If it has `platforms[]` → this is the root. If it has `parent_path` → walk up to the root and read its `platforms[]`. This works whether the skill is invoked from the repo root or from inside a platform sub-folder (`mobile/`, `backend/`, `web/`). For a single-platform project (`platforms: [{name, path:"."}]`), root == the repo == the one platform — cross-cutting and platform docs both resolve to the repo-root `docs/` (nothing is misrouted into a sub-folder).

Doc taxonomy: **project-wide docs live in the resolved root `docs/`** (owner-overview, `00_meta/*`, cross-platform specs); **platform-specific docs live in `<platform>/docs/`** (API reference, platform design).

### 2. Read the project's docs routing authority

Read `<root>/docs/00_meta/docs-workflow.md` — the project-instance routing file (cheat-sheet: doc → owns → "update when…"). It is the source of truth for where each doc lives and what triggers its update. If absent, fall back to the universal conventions in `plugins/forge/docs/conventions/docs-workflow.md`.

### 3. Scope analysis — is a pass even needed?

Compute `git diff --name-only <since>...HEAD`, grouped by platform path. Classify the change surface:

- **Features / decisions / deps / milestones changed** → meta child is in scope.
- **Backend API surface changed** (controllers, exceptions, gateways/events) → api child is in scope, for the backend platform(s) only.
- **Code touched an area covered by a design spec / ADR** → design child is in scope.

If none of the above → report "no docs need updating" and exit. This is the cheap early-out: a mobile-only epic never triggers the api child; a pure-refactor epic with no doc-relevant surface does nothing.

### 4. Route to the in-scope children

Invoke only the children selected in Step 3, each with `--root <path>`, the relevant `--platform <path>` (api/design), `--epic <ref>`, and `--dry-run` if set:

- `forge:update-docs-meta` — once, for the resolved root.
- `forge:update-docs-api` — per backend platform whose API surface changed.
- `forge:update-docs-design` — per platform (and root) whose code touched a spec area.

Each child applies the format law and guard discipline. Collect their reports.

### 5. Report

List every doc each child touched (or, in `--dry-run`, would touch) with a one-line reason, grouped by child. Apply nothing in `--dry-run`.

## Do not

- Do not edit docs directly here — always route to a child.
- Do not invoke a child whose domain the epic didn't touch (Step 3 gates this).
- Do not commit — the caller (`forge:epic-close` or the user) owns commit semantics.
- Do not write HTML, and do not let any child write HTML (format law).

## What this skill does not cover

- **Editing mechanics per doc type** — owned by the children.
- **Capturing a fresh decision mid-session** — `/log-decision`.
- **Authoring a new design doc from scratch** — that is design work, not a sync.
