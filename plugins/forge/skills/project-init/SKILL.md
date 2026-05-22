---
name: project-init
description: Bootstrap a new project's Claude Code setup — stack interview, CLAUDE.md from template, kit-* skills copied from `plugins/forge/skill-templates/<stack>/`, settings.json, tracker, optional Linear project. `--tracker-only` re-runs only the tracker setup on an existing project.
type: fundamental
---

# project-init

Interactive bootstrap for a fresh (or freshly-claudified) project. Triggers: `/project-init`, "налаштуй проект для Claude" at the project root. Flag: `/project-init --tracker-only` to run only `references/tracker-setup.md`.

## Core principles

- **Interactive, not magical.** Ask about the stack; don't infer from `package.json` alone — wrong guesses are expensive to undo.
- **Reuse global infrastructure.** CLAUDE.md references `plugins/forge/docs/`; the project setup is intentionally not self-sufficient.
- **Self-improving.** When a stack has no templates yet, interview the user and save the result to `plugins/forge/skill-templates/<stack>/` for future projects.
- **Idempotent re-runs.** If artifacts exist, ask "overwrite / merge / abort" before touching them.

## Contract

When the flow completes (full mode), the project has:

1. `CLAUDE.md` — single-platform: per-stack body. Multi-platform: short overview + table of per-platform CLAUDE.md links (written by step 4.5).
2. `.claude/skills/` — `kit-*` templates from `plugins/forge/skill-templates/<stack>/`. Single-platform at repo root; multi-platform under each `<path>/.claude/skills/`.
3. `.claude/settings.json` — allowed Bash list + stack-appropriate defaults.
4. `.claude/tracker.json` — backend declared (linear / github-personal / github-org / markdown), backend-specific fields populated per `plugins/forge/docs/conventions/tracker-json.md`. Multi-platform projects also write `structure` (if `monorepo`) and `platforms[]`, plus a minimal child `tracker.json` (`backend` + `parent_path: "../"`) per platform sub-folder.
5. `.mcp.json` — registers code-review-graph MCP server (if `code-review-graph` CLI is on PATH).
6. `docs/00_meta/` — if step 2.5 = Yes (scaffold the 4 meta files). Always at **repo root** (multi-platform projects never duplicate this per platform).
7. `docs/owner-overview.md` — always; scaffolded in step 6.5 from `plugins/forge/skill-templates/_common/owner-overview.md` with project-init answers substituted. Always at repo root.
8. Per-platform `<path>/CLAUDE.md` (multi-platform only) — per-stack body with the mandatory cross-ref block injected (see `references/scaffolding-logic.md` S2.3).
9. Linear project + P0/P1 epics — only if step 2.6 = `linear` and step 2.7 = Yes.
10. `.claude/e2e-*.json` — per-platform e2e opt-in / opt-out markers, written by `forge:e2e --init` (step 7.6).
11. Design posture — recorded by `forge:design-bootstrap` (step 7.7) when a frontend platform is present: one of a `design` block in `tracker.json`, a `## Design` block in CLAUDE.md, or a `design/` stub plus a parking-lot epic.
12. `.claude/api-docs.json` — API docs opt-in marker, written by `forge:update-docs-api --init` (step 7.8) when a backend platform is present: `{ "openapi": true }` or `{ "openapi": false }`.

`--tracker-only` mode produces only item 4 (and stops).

## Flow

### 0. Flag check

`--tracker-only` → jump straight to `references/tracker-setup.md`. Return when done.

### 1. Pre-flight

- `pwd` to confirm root.
- Detect existing `CLAUDE.md`, `.claude/`, `.git/`. If any exist, ask "Re-init? (overwrite / merge / abort)" before continuing.

### 2. Project type — single vs multi-platform

Ask first (single-select, **default: `single-platform`**):

> "Project type? 1. **Single-platform** — one codebase, one stack. 2. **Multi-platform** — multiple platforms in the same repo (backend + mobile, web + backend, …)."

- `single-platform` → continue to step 2.1 below.
- `multi-platform` → jump to `references/multi-platform-interview.md` (Steps 2a–2e). It produces `structure`, `platforms[]`, and `selected_stacks[]`; on return, skip step 2.1 and continue at step 2.5. The first entry in `platforms[]` is the primary stack used wherever a single `stack key` is required (step 3 / step 4A / step 5).

### 2.1. Stack interview (single-platform only)

Ask the seven-question batch in `references/stack-interview-common.md` (project type, framework, persistence, hosting, Linear team, design system, existing scaffolding). The selected `project_type + framework` resolves the stack key used by step 3. Record `platforms[]` as `[{ name: "<stack key>", path: "." }]` for the tracker writer in step 7.25; `structure` stays at the default `"sub-folder"` and is **not** written to tracker.json (readers default to it).

### 2.5. Docs scaffold question

Ask: "Scaffold `docs/00_meta/`? (decisions-log + roadmap + docs-workflow + glossary). Recommended." Options: **Yes** / **No** / **Skip — decide later**. Record; apply in step 6.

### 2.6. Tracker backend question

Ask: "Tracker backend for this repo?" Single-select, **default: `github-personal`**.

1. **Linear** — Linear team + project, MCP-driven
2. **GitHub personal** — issues + Projects v2 on your personal account (default)
3. **GitHub org** — issues + Projects v2 on an organization
4. **Markdown** — local files under `docs/00_meta/manual-tracker`

Record the choice; the actual backend setup (interview + writing `tracker.json`) runs in step 7.25 via `references/tracker-setup.md`. The `tracker.json` schema and backend-specific fields are defined in `plugins/forge/docs/conventions/tracker-json.md` and `plugins/forge/docs/tracker-backends/<backend>.md`.

Inherited hard rules (see `plugins/forge/docs/conventions/tracker-tickets.md`): never offer team creation; never propose cycles or milestones by default; never set priority.

### 2.7. Linear automation question (only if 2.6 = Linear)

If 2.6 selected `linear`, ask: "Create a Linear project for backlog tracking?" Options: **Yes (Recommended)** / **No** / **Skip — I'll add later**. Record; apply in step 7.5. Skip entirely if 2.6 selected any other backend.

### 3. Resolve template path

Map `(project_type, framework)` → `plugins/forge/skill-templates/<stack>/` via the table in `references/skill-templates-routing.md`. Check whether the resolved folder exists and contains real `kit-*.md` files.

### 4A. Templates exist — copy them (non-Flutter)

For stacks **other than `mobile-flutter`**, follow `references/copy-templates.md`: create `.claude/skills/`, copy each relevant `kit-*.md` (filter by frontmatter `description`), rewrite placeholder package names, ask before applying stack-specific convention assumptions, then create `.claude/settings.json` (see `references/settings-json.md`).

### 4A-flutter. Stack = mobile-flutter — run the scaffolder

The Flutter path replaces the basic copy with the **Flutter scaffolder pipeline** (interview → JSON → `plugins/forge/scripts/scaffold-flutter.sh` → post-scaffold remote setup). The scaffolder owns CLAUDE.md, `.claude/skills/`, `.claude/settings.json`, `docs/00_meta/`, git init, GitHub repo, and the hand-off to step 7.5.

Full pipeline: `references/flutter-scaffolder.md`. If this branch runs, steps 4C / 5 / 6 / 7 are **skipped** (the scaffolder produced them); jump to step 7.25.

### 4B. Templates do not exist — interview-scaffold

Per `references/scaffold-new-stack.md`: ask the user to walk through their typical workflow for `kit-create-feature`, `kit-add-route` (or equivalent), compose SKILL.md files from the answers, save to `plugins/forge/skill-templates/<stack>/` for future reuse, and also drop a copy in `<project>/.claude/skills/`.

### 4.5. Root + per-platform scaffolding (multi-platform only)

If `platforms.length > 1` (recorded by `references/multi-platform-interview.md`), follow `references/scaffolding-logic.md` to:

- Write the **root multi-platform `CLAUDE.md`** (short overview + table of per-platform CLAUDE.md links + pointer to shared `docs/`).
- Iterate `platforms[]`: `mkdir -p <path>/.claude/skills/`, copy the resolved `plugins/forge/skill-templates/<name>/` into `<path>/`, write `<path>/CLAUDE.md` (per-stack body with the mandatory cross-ref block `> Roadmap, ADRs, owner overview live at \`../docs/\`. See \`../CLAUDE.md\` for the project-wide overview.` injected after the H1), write a minimal `<path>/.claude/tracker.json` (`backend` + `parent_path: "../"`).
- Skip `<path>/docs/` scaffolding — shared `docs/` lives only at repo root.

Single-platform projects skip this step entirely (root layout handled by steps 4 → 5 → 6 → 7.25 as before).

### 4C. Generate per-project SKILLS.md

Run `plugins/forge/scripts/generate-project-skills.sh <stack> <project>/.claude/SKILLS.md` to emit a stack-filtered skills index. Add one pointer line to CLAUDE.md `## Skills`: "See `.claude/SKILLS.md` for the auto-generated, stack-filtered list."

### 5. Generate CLAUDE.md

**Multi-platform** (`platforms.length > 1`): step 4.5 already wrote the root overview `CLAUDE.md` and per-platform `<path>/CLAUDE.md` files. This step is a **no-op** in that mode.

**Single-platform**: read `plugins/forge/docs/conventions/claude-md-template.md` and substitute placeholders per `references/claude-md-scaffold.md` (project name, tagline, stack, Essential commands, Architecture, Mandatory rules, Documentation inventory, Linear workflow, Global references, Skills). Write to `<project>/CLAUDE.md`.

### 6. Initialize project docs structure

If step 2.5 answer was **Yes**, copy `plugins/forge/skill-templates/_common/docs/00_meta/{decisions-log,roadmap,docs-workflow,glossary}.md` into `<project>/docs/00_meta/`, substitute `<date>` / `<project_name>`, and inject the **Documentation inventory** table + the `/log-decision` row into CLAUDE.md. Full substitution spec: `references/docs-scaffold.md`.

### 6.5. Scaffold owner-overview.md

Copy `plugins/forge/skill-templates/_common/owner-overview.md` to `<project>/docs/owner-overview.md` (single-platform) or `<repo-root>/docs/owner-overview.md` (multi-platform monorepo). Substitute `{{ placeholders }}` from interview data:

| Placeholder | Source |
|---|---|
| `{{ project_name }}` | project name from step 2 |
| `{{ one_paragraph_elevator_pitch }}` | elevator-pitch answer collected during the interview; if not asked, prompt now: "One-sentence elevator pitch for this project?" |
| `{{ platform_1_name }}` / `{{ platform_2_name }}` | project type / platforms from step 2 |
| `{{ prefix }}` / `{{ ticket_prefix }}` | from `tracker.json` `prefix` field (written in step 7.25) — substitute after step 7.25 or leave the literal placeholder if tracker step has not run yet; the next `update-docs` run fills it |
| `{{ tracker_backend }}` | from `tracker.json` `backend` field (same timing note) |
| `{{ commit_magic_word_example }}` | derived from backend (`Refs PREFIX-N:` for Linear, `Refs #N:` for GitHub, `Refs <slug>:` for Markdown) |

Sections inside `<!-- manual --> ... <!-- /manual -->` guards: replace the inner example-italics placeholder text with an empty line so the user sees a clean prompt area, but keep the guard tags themselves in place.

Sections inside `<!-- auto:<key> --> ... <!-- /auto:<key> -->` guards: leave the placeholder stub lines untouched — `/forge:update-docs` replaces those blocks on first epic close.

Create `<project>/docs/` if it does not exist. Do not overwrite an existing `owner-overview.md` without explicit user confirmation.

### 7. Settings.json defaults

Create `<project>/.claude/settings.json` per `references/settings-json.md` — allowed Bash matching the stack's essential commands, MCP servers the user named in step 2, sensible read defaults. Suggest `/update-config` for further tuning.

### 7.1. Code-review-graph wiring

> Skip entirely if `--tracker-only` was passed.

1. **Check tool availability.** Run `command -v code-review-graph`. If the command is not found, print:
   ```
   code-review-graph not on PATH; skipping graph setup. Install per docs/INSTALL.md
   ```
   Skip the rest of this step.

2. **Check existing `.mcp.json`.** If `<project>/.mcp.json` exists and is non-empty, prompt:
   > `.mcp.json` вже існує. Що робимо? (merge / overwrite / skip)
   - `skip` → skip the rest of this step.
   - `merge` → ensure a `mcpServers.code-review-graph` key exists alongside any existing servers; do not remove other entries.
   - `overwrite` → replace the file entirely with the template below.

3. **Write `.mcp.json`.** Write the following 10-line template to `<project>/.mcp.json`:
   ```json
   {
     "mcpServers": {
       "code-review-graph": {
         "command": "uvx",
         "args": ["code-review-graph", "serve"],
         "type": "stdio"
       }
     }
   }
   ```
   > **WARNING: Do NOT run `code-review-graph install --platform claude-code`.** That command is destructive — it overwrites CLAUDE.md, injects upstream skills into `.claude/skills/`, and adds auto-update hooks to `.claude/settings.json` that conflict with everything this skill writes. Always write `.mcp.json` directly from the template above.

4. **Run initial full build.** Execute `code-review-graph build` from the project root. This may take 30s–2min. Capture output.

5. **Print summary.** Parse node/edge count from output if available. Format:
   ```
   graph-refresh: <N> nodes, <N> edges built
   ```
   Fall back to raw output if unparseable.

### 7.25. Tracker setup

Run `references/tracker-setup.md` with the backend chosen in step 2.6. Writes `<project>/.claude/tracker.json` per the schema in `plugins/forge/docs/conventions/tracker-json.md`. The writer also persists the multi-platform interview output (when step 2 = multi-platform): `structure` (only if `monorepo`) and `platforms[]` (always, including single-platform's `[{ name, path: "." }]`). When `platforms.length > 1`, write a minimal child `tracker.json` (`{ "backend": "<same>", "parent_path": "../" }`) into each `<path>/.claude/tracker.json`. In the full flow, no overwrite-confirmation prompt (the project is being initialized fresh). If the user picked `linear`, step 7.5 reuses that team — no second team prompt.

### 7.5. Linear automation

If step 2.6 = `linear` **and** step 2.7 = **Yes**, follow `references/linear-automation.md`: resolve team → create project → detect credential needs → create P0 Bootstrap epic + Mode M sub-issues + P1 MVP placeholder → print summary. Otherwise (any non-Linear backend, or Linear with **No** / **Skip**), make zero Linear MCP calls; jump to step 7.6.

### 7.6. E2E opt-in

> Skip entirely if `--tracker-only` was passed.

Invoke `forge:e2e --init`. It walks `platforms[]` from the now-written `tracker.json`, asks the user per platform whether they want e2e there, and writes the opt-in / opt-out marker (`.claude/e2e-*.json`) so the question is never re-asked. project-init does not ask the e2e question itself — `forge:e2e --init` owns the per-platform prompt and child dispatch (web → Playwright, backend → DB isolation; mobile is a future child and returns `not-applicable`).

### 7.7. Design posture (frontend platforms only)

> Skip entirely if `--tracker-only` was passed, or if no `platforms[]` entry is a frontend stack (web-frontend / mobile-flutter / mobile-native).

Invoke `forge:design-bootstrap`, passing any Figma URL / tokens answer captured during the stack interview (step 2.1 question 6) so its branch (a) does not re-ask. The skill records exactly one outcome per its own contract: a `design` block in `tracker.json`, a `## Design` block in CLAUDE.md, or a `design/` stub plus a parking-lot epic via `forge:create-epic`. Placed here — after CLAUDE.md (step 5 / 4.5) and `tracker.json` (step 7.25) both exist — so every branch has the artifact it writes to.

### 7.8. API docs opt-in (backend platforms only)

> Skip entirely if `--tracker-only` was passed, or if no `platforms[]` entry is a backend stack (backend-node / backend-nest / any backend framework).

Invoke `forge:update-docs-api --init`. It asks the user once whether to generate API docs from Swagger/OpenAPI or hand-write Markdown, then writes `.claude/api-docs.json` so the question is never re-asked. project-init does not ask the API docs question itself — `forge:update-docs-api --init` owns the prompt and marker write.

### 8. Output

Print the summary block from `references/output-summary.md` — what was created, the stack summary, Linear prefix/team, and next steps.

## Do not

- Do not overwrite existing files without explicit user confirmation.
- Do not commit anything; the user reviews and commits when ready.
- Do not configure secrets — that is a user responsibility, normally surfaced via a `manual-setup` Mode M ticket.
- Do not assume stack from filenames alone; ask.
- Do not run `git init` unless the user explicitly asked (the Flutter scaffolder branch is the only exception, and it's gated).
- Do not auto-install dependencies; that is the user's environmental commitment.
- Do not modify `plugins/forge/docs/` or `plugins/forge/skills/` during init. This skill writes to `plugins/forge/skill-templates/<stack>/` only with consent in step 4B.
- Do not run `code-review-graph install --platform claude-code` — it is destructive (overwrites CLAUDE.md, injects upstream skills, adds hooks). Always write `.mcp.json` directly from the template in step 7.1.
- Do not create a Linear team. Always work within an existing one (FORGE-3.5).
- Do not set cycle, milestone, priority, dueDate, estimate, or assignee on any Linear project / epic / sub-issue.

## Edge cases

`references/edge-cases.md` covers: existing non-claude CLAUDE.md (merge vs replace), Linear team detection failure, zero Linear teams, save-project / save-issue MCP failures, no-internet upstream-skills fetch, exotic stacks, and user refusing the interview-scaffold.

## What this skill does not cover

- **Per-stack interview question lists** — see `references/stack-interviews/<stack>.md`.
- **The Flutter scaffolder script itself** — owned by `plugins/forge/scripts/scaffold-flutter.sh`; this skill drives the user-facing flow only.
- **Existing-project audit** — that is `/claude-md-management:claude-md-improver`.
