---
name: design-bootstrap
description: Interview a fresh project for its design-system posture (ready / stack-defaults / will-create) and record the answer in tracker.json, CLAUDE.md, or a scaffolded mini design-system + parking-lot epic.
type: hybrid
---

# design-bootstrap

Determine and record how a new project relates to a design system, so downstream UI work has a known source of truth (or an explicit "no system yet" decision).

## Trigger

Invoked by `/forge:project-init` once a **frontend platform** is detected in the stack interview (any `platforms[]` entry whose stack key is web-frontend, mobile-flutter, mobile-native, etc.). Standalone invocation `/forge:design-bootstrap` is also valid on an existing project to retroactively record the decision.

> Wiring: `/forge:project-init` SHOULD call this skill as a sub-step right after the per-platform CLAUDE.md is written (step 4.5 in multi-platform mode, or after step 5 in single-platform mode). The actual wiring lives in a separate ticket — this skill's contract below tells the wirer what to invoke and what artifacts to expect.

## Contract

After running, the project has exactly one of:

- **(a) Ready** — `design.figma_file_url` written to the project's `tracker.json`.
- **(b) Stack defaults** — a `## Design` block added to `CLAUDE.md` naming the default stack (Tailwind / Material / Cupertino / etc.).
- **(c) Will create** — a mini design-system skeleton (`design/tokens.json` + `design/README.md`) committed under `<platform-path>/`, plus a parking-lot epic "design system creation for <project>" created via `forge:create-epic`.

Exactly one branch runs per invocation. The skill writes nothing else.

## Flow

### 1. Prompt the user

Single question, three options:

> Design system for this project?
> a) **Ready** — already have one (Figma URL or library reference).
> b) **Stack defaults** — use the framework's defaults (Tailwind / Material / Cupertino / shadcn / native).
> c) **Will create** — none yet, plan to build one. I'll scaffold a stub and open a parking-lot epic.

Wait for the user's letter. No multi-select.

### 2. Branch (a) — Ready

1. Ask: "Figma file URL (or other source-of-truth URL)?" Accept any URL or "no URL, just a name" (then ask for the name).
2. Read `<project>/.claude/tracker.json` (resolve per `plugins/forge/docs/conventions/tracker-json.md` — walk `parent_path` if present).
3. Add a `design` block at the top level of the root tracker.json:
   ```json
   "design": {
     "source": "figma" | "library" | "other",
     "figma_file_url": "<URL or null>",
     "library_name": "<name or null>"
   }
   ```
4. Print one line: `tracker.json: design.figma_file_url recorded`.

### 3. Branch (b) — Stack defaults

1. Ask: "Which default stack — Tailwind / Material / Cupertino / shadcn / native / other?" Accept one short token.
2. Append a `## Design` block to the **per-platform CLAUDE.md** (or root CLAUDE.md in single-platform mode):
   ```markdown
   ## Design

   Using **<stack>** defaults. No custom design system. UI work should
   reach for <stack> components first; only diverge with a clear reason
   captured in an ADR.
   ```
3. Print one line: `CLAUDE.md: design block added (stack: <stack>)`.

### 4. Branch (c) — Will create

1. Resolve `<platform-path>` from the active platform (root `.` for single-platform; the platform's `path` in multi-platform).
2. `mkdir -p <platform-path>/design/`.
3. Write `<platform-path>/design/tokens.json` with the minimal stub:
   ```json
   {
     "color": { "_comment": "fill on first design pass" },
     "spacing": { "_comment": "fill on first design pass" },
     "typography": { "_comment": "fill on first design pass" }
   }
   ```
4. Write `<platform-path>/design/README.md` with one paragraph: "Design system stub. Token shape is illustrative — replace with the team's chosen schema (W3C DTCG, Style Dictionary, etc.) once decided. Parking-lot epic tracks the build-out."
5. Invoke `forge:create-epic` with the inline brief: `"design system creation for <project_name> — build out tokens, components, and library hand-off. Parking lot — scope to be refined when prioritized."` Let `forge:create-epic` handle brainstorming-gate, interview, and creation.
6. Print one line: `design/ scaffolded; parking-lot epic: <epic URL>`.

## Do not

- Do not write to multiple branches' artifacts in one run — exactly one of (a) / (b) / (c).
- Do not invent a Figma URL the user did not supply (branch a). Leave `figma_file_url: null` if the source is a non-Figma library.
- Do not pre-populate `tokens.json` with real values (branch c). The stub is a placeholder for the future build-out, not a starting palette.
- Do not skip the `forge:create-epic` invocation in branch (c). The parking-lot epic is the whole point — a `design/` folder with no tracking attached gets forgotten.
- Do not modify `forge:project-init` from here. Wiring is a separate ticket.

## What this skill does not cover

- **Building the design system itself.** Branch (c) only scaffolds a stub + opens an epic. The actual build-out is whatever the epic resolves to.
- **Token format choice.** The `tokens.json` stub is shape-illustrative; the parking-lot epic decides on DTCG / Style Dictionary / Tailwind config / etc.
- **Importing tokens from an existing Figma file.** Branch (a) records the URL; pulling variables out of Figma is a separate skill (`forge:design-source`, sibling in EPIC G).
