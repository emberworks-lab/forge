---
name: kit-update-docs
description: Sync a project's docs/ with recent code changes — discover docs across all platforms, map changed files to the docs they affect, and apply targeted edits (API docs, owner-overview, roadmap, glossary) per the docs-workflow rules. Invoked by epic-close and on stack-touching changes.
type: hybrid
---

# forge:kit-update-docs

Catch project documentation up to the code after implementation. Analyses the diff, finds stale docs across every platform, and applies targeted edits — respecting the conventions in `plugins/forge/docs/conventions/docs-workflow.md` and the `<!-- manual -->` / `<!-- auto:<key> -->` guards in generated files.

Complements `/log-decision` (which captures a decision the moment it locks). This skill is the after-implementation sweep.

## When invoked

- **Auto:** `forge:epic-close` docs-sync step (after a branch lands), and after a dependency or milestone change.
- **Manual:** `/forge:kit-update-docs` when finishing a branch or after any stack-touching change.

## Inputs

Optional: `--since <ref>` (diff base; default = the branch's merge-base with the default branch, or `HEAD~1` for a single-commit sync), `--dry-run` (list proposed edits without applying).

## Flow

### 1. Resolve discovery scope (multi-platform)

Read `<project>/.claude/tracker.json` → `platforms[]` per the reader algorithm in `plugins/forge/docs/conventions/tracker-json.md` §4. For each platform `path`, plus the repo root, the doc surface is:

- `<path>/docs/**`
- `<path>/README.md`
- `<path>/CLAUDE.md`

Plus always, at repo root: `docs/owner-overview.md`, `docs/00_meta/*`. If `platforms[]` is absent, treat the repo root as the single platform (`path: "."`) — identical to legacy single-root behaviour.

### 2. Compute the diff

`git diff --name-only <since>...HEAD`. Group changed files by platform path (a file under `<platform.path>/` belongs to that platform; everything else is root-scoped).

### 3. Apply the trigger map

For each changed file, look up the docs it affects in `references/trigger-map.md` (API docs, owner-overview, roadmap, glossary, README). Build the set of docs to touch. When unsure where content goes, consult the project's `docs/00_meta/docs-workflow.md` routing tree first.

### 4. Apply targeted edits

For each doc in the set:

- **Generated/guarded sections** (`<!-- auto:<key> --> … <!-- /auto:<key> -->`): regenerate the block content from current state. **Never** touch content inside `<!-- manual --> … <!-- /manual -->` guards.
- **owner-overview.md**: refresh `Features.Shipped`, `Features.In-progress`, and `Phases` from the just-closed epic / current tracker state; preserve all manual-guarded prose.
- **API docs** (`docs/api/*`): per the trigger map — regenerate `endpoints.md` from `openapi.json` (run the project's openapi gen first), hand-edit prompts for `errors.md` / `websockets.md` are surfaced, not auto-written.
- **decisions-log / roadmap / glossary**: follow the mandatory cross-doc table in `docs-workflow.md` (append decisions, update deferred items, add new-term entries).

Make minimal, targeted edits. Read each file before editing. Do not rewrite docs wholesale.

### 5. Report

List every doc touched (or, in `--dry-run`, every doc that *would* be touched) with a one-line reason each. In `--dry-run`, apply nothing.

## Do not

- Do not touch content inside `<!-- manual -->` guards — that is the user's prose.
- Do not invent doc content not supported by the diff or current state.
- Do not duplicate ticket bodies or chat output into docs (see `docs-workflow.md` § What does NOT belong).
- Do not commit — the caller (`forge:epic-close` or the user) owns commit semantics.

## What this skill does not cover

- **Capturing a fresh decision** — use `/log-decision` at the moment it locks.
- **Authoring a new design doc from scratch** — that is design work, not a sync.
- **Generating the owner-overview template** — `forge:project-init` scaffolds it; this skill only refreshes its auto sections.
