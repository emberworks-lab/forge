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

1. `CLAUDE.md` — generated from `plugins/forge/docs/conventions/claude-md-template.md`, populated for the chosen stack.
2. `.claude/skills/` — `kit-*` templates copied from `plugins/forge/skill-templates/<stack>/`.
3. `.claude/settings.json` — allowed Bash list + stack-appropriate defaults.
4. `.claude/tracker.json` — backend declared (linear / github / markdown / skip).
5. `.mcp.json` — registers code-review-graph MCP server (if `code-review-graph` CLI is on PATH).
6. `docs/00_meta/` — if step 2.5 = Yes (scaffold the 4 meta files).
7. Linear project + P0/P1 epics — if step 2.6 = Yes.

`--tracker-only` mode produces only item 4 (and stops).

## Flow

### 0. Flag check

`--tracker-only` → jump straight to `references/tracker-setup.md`. Return when done.

### 1. Pre-flight

- `pwd` to confirm root.
- Detect existing `CLAUDE.md`, `.claude/`, `.git/`. If any exist, ask "Re-init? (overwrite / merge / abort)" before continuing.

### 2. Stack interview

Ask the seven-question batch in `references/stack-interview-common.md` (project type, framework, persistence, hosting, Linear team, design system, existing scaffolding). The selected `project_type + framework` resolves the stack key used by step 3.

### 2.5. Docs scaffold question

Ask: "Scaffold `docs/00_meta/`? (decisions-log + roadmap + docs-workflow + glossary). Recommended." Options: **Yes** / **No** / **Skip — decide later**. Record; apply in step 6.

### 2.6. Linear automation question

Ask: "Create a Linear project for backlog tracking?" Options: **Yes (Recommended)** / **No** / **Skip — I'll add later**. Record; apply in step 7.5.

Inherited hard rules (see `plugins/forge/docs/conventions/tracker-tickets.md`): never offer team creation; never propose cycles or milestones by default; never set priority.

### 3. Resolve template path

Map `(project_type, framework)` → `plugins/forge/skill-templates/<stack>/` via the table in `references/skill-templates-routing.md`. Check whether the resolved folder exists and contains real `kit-*.md` files.

### 4A. Templates exist — copy them (non-Flutter)

For stacks **other than `mobile-flutter`**, follow `references/copy-templates.md`: create `.claude/skills/`, copy each relevant `kit-*.md` (filter by frontmatter `description`), rewrite placeholder package names, ask before applying stack-specific convention assumptions, then create `.claude/settings.json` (see `references/settings-json.md`).

### 4A-flutter. Stack = mobile-flutter — run the scaffolder

The Flutter path replaces the basic copy with the **Flutter scaffolder pipeline** (interview → JSON → `plugins/forge/scripts/scaffold-flutter.sh` → post-scaffold remote setup). The scaffolder owns CLAUDE.md, `.claude/skills/`, `.claude/settings.json`, `docs/00_meta/`, git init, GitHub repo, and the hand-off to step 7.5.

Full pipeline: `references/flutter-scaffolder.md`. If this branch runs, steps 4C / 5 / 6 / 7 are **skipped** (the scaffolder produced them); jump to step 7.25.

### 4B. Templates do not exist — interview-scaffold

Per `references/scaffold-new-stack.md`: ask the user to walk through their typical workflow for `kit-create-feature`, `kit-add-route` (or equivalent), compose SKILL.md files from the answers, save to `plugins/forge/skill-templates/<stack>/` for future reuse, and also drop a copy in `<project>/.claude/skills/`.

### 4C. Generate per-project SKILLS.md

Run `plugins/forge/scripts/generate-project-skills.sh <stack> <project>/.claude/SKILLS.md` to emit a stack-filtered skills index. Add one pointer line to CLAUDE.md `## Skills`: "See `.claude/SKILLS.md` for the auto-generated, stack-filtered list."

### 5. Generate CLAUDE.md

Read `plugins/forge/docs/conventions/claude-md-template.md` and substitute placeholders per `references/claude-md-scaffold.md` (project name, tagline, stack, Essential commands, Architecture, Mandatory rules, Documentation inventory, Linear workflow, Global references, Skills).

### 6. Initialize project docs structure

If step 2.5 answer was **Yes**, copy `plugins/forge/skill-templates/_common/docs/00_meta/{decisions-log,roadmap,docs-workflow,glossary}.md` into `<project>/docs/00_meta/`, substitute `<date>` / `<project_name>`, and inject the **Documentation inventory** table + the `/log-decision` row into CLAUDE.md. Full substitution spec: `references/docs-scaffold.md`.

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

Run `references/tracker-setup.md`. Writes `<project>/.claude/tracker.json`. In the full flow, no overwrite-confirmation prompt (the project is being initialized fresh). If the user picks `linear`, step 7.5 reuses that team — no second team prompt.

### 7.5. Linear automation

If step 2.6 = **Yes**, follow `references/linear-automation.md`: resolve team → create project → detect credential needs → create P0 Bootstrap epic + Mode M sub-issues + P1 MVP placeholder → print summary. If **No** / **Skip**, make zero Linear MCP calls; jump to step 8.

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
