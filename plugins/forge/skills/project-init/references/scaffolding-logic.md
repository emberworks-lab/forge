# Root + per-platform scaffolding (step 4.5)

Consumes the multi-platform interview output (`references/multi-platform-interview.md`) plus the resolved `selected_stacks`. Writes the right files in the right places per the layout choice. Runs after step 4 (`copy-templates.md` / scaffold-new-stack) so individual stack templates are already on disk for the root-or-only platform; this step handles the **placement** for multi-platform projects and the **root-overview wiring**.

For `mobile-flutter` paths the Flutter scaffolder owns its own platform layout (`references/flutter-scaffolder.md`). When the multi-platform list includes `mobile-flutter`, the Flutter scaffolder runs scoped to that platform's `<path>/` and this step writes only the cross-ref `CLAUDE.md` plus the minimal child `tracker.json` for it.

## When to run

- **Single-platform** (`platforms.length == 1` and `path == "."`) → skip this step entirely. Steps 4A / 4A-flutter / 4B already placed templates at repo root; `CLAUDE.md` is generated in step 5; `tracker.json` in step 7.25.
- **Multi-platform** (`platforms.length > 1`) → run all sub-sections below.

## S1. Root files

1. **Root `CLAUDE.md` (multi-platform overview).** Generate a short overview file at repo root that links to each platform's `CLAUDE.md`. Use this skeleton (substitute `{{ project_name }}` and the per-platform rows from `platforms[]`):

   ```markdown
   # {{ project_name }}

   Multi-platform project. Each platform has its own `CLAUDE.md` with stack-specific rules.

   ## Platforms

   | Platform | Path | CLAUDE.md |
   |---|---|---|
   | <name> | `<path>/` | [`<path>/CLAUDE.md`](<path>/CLAUDE.md) |
   <!-- one row per entry in platforms[], in order -->

   ## Shared

   - Roadmap, ADRs, glossary, docs-workflow: `docs/00_meta/`
   - Owner overview: `docs/owner-overview.md`
   - Tracker: `.claude/tracker.json` (root) — per-platform overrides under `<path>/.claude/tracker.json`

   ## Forge plugin policy

   Follows `plugins/forge/CLAUDE.md`. Per-platform skill kits live under `<path>/.claude/skills/`.
   ```

   Step 5's full per-stack `CLAUDE.md` is **not** written at repo root in the multi-platform case — that content lives under each `<path>/CLAUDE.md` (see S2 below).

2. **`docs/00_meta/`** — already scaffolded in step 6 when step 2.5 = Yes. No-op here; this section just records the contract that the root `docs/` directory is the shared location.

3. **`docs/owner-overview.md`** — already scaffolded in step 6.5 (single canonical owner overview, always at repo root for multi-platform projects). No-op here.

4. **Root `.claude/tracker.json`** — written by step 7.25 (`references/tracker-setup.md`). Includes `structure` (only if `monorepo`) and the full `platforms[]` array per the schema in `plugins/forge/docs/conventions/tracker-json.md §2.2`. No-op here.

## S2. Per-platform iteration

For each entry `p` in `platforms[]` (in the order recorded), perform these sub-steps. Skip the entry whose `path == "."` if any — the root layout is owned by single-platform flow and should not appear in multi-platform `platforms[]`.

### S2.1 Create the platform directory

`mkdir -p <p.path>/.claude/skills/`. Do not create deeper sub-folders — the stack template (if it provides scaffolding like `app/` or `src/`) handles that on its own.

### S2.2 Copy the skill-template into the platform

Run `references/copy-templates.md` scoped to `<p.path>/` instead of repo root. The template source is `plugins/forge/skill-templates/<p.name>/`. Same filter / placeholder rules apply; the target prefix is `<p.path>/.claude/skills/` instead of `.claude/skills/`.

Stack-specific exceptions:

- **`mobile-flutter`** — run the Flutter scaffolder pipeline (`references/flutter-scaffolder.md`) with its workspace target set to `<repo_root>/<p.path>/` instead of `~/Development/emberworks_lab_projects/<project>/`. The scaffolder's own `git init` / GitHub repo creation steps are **skipped** when running inside an existing multi-platform repo (the root already owns `.git`).
- **`mobile-native`** / other placeholder stacks — if `plugins/forge/skill-templates/<p.name>/` has only a `README.md` and no `kit-*.md` files, copy the README into `<p.path>/.claude/skills/README.md` and stop. The scaffold-new-stack interview is **not** triggered automatically per platform during multi-platform init (would explode interview length); leave kit-* discovery for the user's first real ticket.

### S2.3 Write `<p.path>/CLAUDE.md`

Generate a per-platform `CLAUDE.md` populated from the stack template, exactly as step 5 / `references/claude-md-scaffold.md` would for a single-platform project — same placeholders, same per-stack content. The only difference: **prepend** the mandatory cross-ref block (verbatim) right after the H1 title:

```markdown
> Roadmap, ADRs, owner overview live at `../docs/`. See `../CLAUDE.md` for the project-wide overview.
```

If the skill-template ships its own `CLAUDE.md` (e.g. `plugins/forge/skill-templates/web-nextjs/CLAUDE.md`, `plugins/forge/skill-templates/backend-nest/CLAUDE.md`), prefer it as the body and inject the cross-ref block immediately after its first heading. Otherwise fall back to generating from `plugins/forge/docs/conventions/claude-md-template.md`.

### S2.4 Write `<p.path>/.claude/tracker.json` (minimal child)

Per `plugins/forge/docs/conventions/tracker-json.md §2.3`:

```json
{
  "backend": "<same backend as root>",
  "parent_path": "../"
}
```

No backend-config block (the reader merges the root). `parent_path` is always `"../"` for the default sub-folder layout. For deeper nesting (e.g. `apps/backend/`) compute the path back to repo root and slash-terminate (`../../`).

### S2.5 Do not write per-platform `docs/` automatically

Each `<p.path>/docs/` is for **platform-specific implementation docs only** (architecture notes, runbooks). Do not scaffold it during init — the user creates files there organically. Roadmap / ADRs / glossary / owner-overview live exclusively at `<repo_root>/docs/`.

## S3. Idempotency / overwrite

- If `<p.path>/` already exists with files, ask "overwrite / merge / abort" once per platform.
- If the root multi-platform `CLAUDE.md` already exists and is non-empty, prompt before overwriting (full-init mode usually proceeds; merge-mode preserves manual edits).
- The minimal child `tracker.json` is always safe to write (no user content); overwrite without prompting in the full-init flow.

## S4. Cross-references with downstream steps

| Downstream step | What it expects from S1/S2 |
|---|---|
| Step 5 (CLAUDE.md scaffold) | Multi-platform mode: skip the root `CLAUDE.md` per-stack body (S1.1 already wrote the overview). Single-platform mode: unchanged. |
| Step 6 (docs/00_meta/) | Always writes to **`<repo_root>/docs/00_meta/`**, never per-platform. |
| Step 6.5 (owner-overview.md) | Always writes to **`<repo_root>/docs/owner-overview.md`**. |
| Step 7 (settings.json) | Multi-platform: one `<repo_root>/.claude/settings.json` covering the union of allowed-Bash commands across platforms, **plus** per-platform `<p.path>/.claude/settings.json` for stack-specific overrides (e.g. mobile needs `flutter`, backend needs `pnpm`). |
| Step 7.25 (tracker setup) | Writes the root `tracker.json` with full backend config + `platforms[]`. This step S2.4 wrote the minimal children. |

## Hard rules

- Never write a per-platform `docs/` during init — the shared `docs/` at repo root is the only documentation tree this skill scaffolds.
- Never duplicate the owner-overview into each platform; it always lives at `<repo_root>/docs/owner-overview.md`.
- The mandatory cross-ref block in S2.3 is required in every per-platform `CLAUDE.md` — its absence is a downstream-skill assumption violation.
- Single-platform projects never enter this step. If `platforms.length == 1`, bail at the top without modifying anything.
- Do not mutate any file under `plugins/forge/skill-templates/` — those are sources, copy only.
