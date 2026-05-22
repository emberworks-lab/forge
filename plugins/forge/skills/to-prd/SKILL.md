---
name: to-prd
description: Synthesize the current conversation context plus codebase understanding into a PRD, then publish it via the project's tracker backend.
type: hybrid
inspired-by:
  - author: mattpocock
    repo: github.com/mattpocock/skills
    skill: to-prd
    relation: adapted
---

# To PRD

Take everything already known — the current conversation, prior exploration,
any prototype output — and turn it into a PRD, then publish it. This skill
does NOT interview the user. It synthesizes what is already on the table. If a
decision is genuinely undecided, mark it open in the PRD rather than asking.

The output is shaped so `forge:create-ticket` Mode A (doc-backed) can consume
it directly.

## Contract

Given the current context, produce a PRD (problem / solution / user stories /
implementation decisions / testing decisions / out-of-scope) and publish it to
the project's tracker. Section template: `references/prd-template.md`. No
interview, no further triage.

## Steps

### 1. Ground in the codebase

If you have not already explored the repo this session, do so now — enough to
use the project's domain vocabulary and respect any ADRs in the area you are
touching. Read the project `CLAUDE.md` for conventions, prefix, and glossary.
Do not re-derive what the conversation already settled.

### 2. Sketch the modules

List the major modules to build or modify. Actively look for deep modules —
ones that encapsulate a lot of functionality behind a simple, testable
interface that rarely changes — and note which ones warrant isolated tests.
These feed the Implementation Decisions and Testing Decisions sections. See
`references/prd-template.md` for the deep-module heuristic.

### 3. Write the PRD

Fill in the template from `references/prd-template.md`. Use domain vocabulary
throughout. Keep the user-story list extensive. Keep file paths and code
snippets out of Implementation Decisions (they go stale) — the prototype-snippet
exception in the template is the only carve-out.

### 4. Publish via the tracker backend

Read `<project>/.claude/tracker.json` → `backend`, then execute the matching
recipe section from `plugins/forge/docs/tracker-backends/<backend>.md`. If
`tracker.json` is missing, run the first-use setup flow per
`forge:project-init --tracker-only`, then resume here.

- **`linear` / `github`** — call the backend's `create_ticket` op with
  `type: task`, `executor: exec:opus` (a PRD is an architectural artifact),
  `title` from the feature name, `body` = the full PRD. The issue body IS the
  PRD; `forge:create-ticket` Mode A later references the issue directly.
- **`markdown`** — do NOT create a tracker file. Write the PRD to the next
  `docs/0X_<slug>.md` (pick the lowest unused `0N` prefix). Prepend the
  Mode-A lead block (`## Goal`, `## Acceptance criteria`) above the PRD
  sections so `forge:create-ticket` Mode A can map them into a ticket. See
  the "Shaping for `forge:create-ticket` Mode A" section of
  `references/prd-template.md`.

### 5. Report

One line: the issue URL/ref (linear / github) or the `docs/0X_*.md` path
(markdown). Nothing else.

## Mode-A handoff

`forge:create-ticket` Mode A maps doc `## Goal` → ticket `## What` and doc
`## Acceptance criteria` → ticket `## Acceptance`. For the `markdown` backend
the lead block in Step 4 supplies both; the full PRD below stays as the
exhaustive plan the ticket's `## References` points at. For remote backends,
the published issue is the plan and `forge:create-ticket` references it
directly — no doc file is written.

## Do NOT

- Interview the user. Synthesize what is already known; mark open decisions
  as open.
- Hardcode a publish target. The backend is always resolved from
  `tracker.json` via the recipe.
- Set priority, cycle, or milestone on the published issue.
- Inline file paths or code snippets into Implementation Decisions (except the
  prototype-snippet carve-out in the template).
- Create a new tracker team. If undetected, ask which existing one to use.
