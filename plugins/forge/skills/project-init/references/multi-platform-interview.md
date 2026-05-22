# Multi-platform interview branch (Steps 2a–2e)

Drives the project-init flow when the user is building a project that spans more than one platform (e.g. backend + mobile, or web + backend). Replaces the single per-stack interview from `stack-interview-common.md` with a per-platform loop, and writes both `structure` and `platforms[]` into the tracker config per `plugins/forge/docs/conventions/tracker-json.md`.

This file owns Steps 2a–2e. After it completes, the main flow resumes at step 2.5 with `platforms[]` and `structure` recorded for downstream use (template routing, scaffolding, tracker setup).

## Step 2a — Project type

Ask the user (single-select, **default: `single-platform`**):

> "Project type?
> 1. **Single-platform** — one codebase, one stack (e.g. a Next.js app, a Flutter app, a Node backend).
> 2. **Multi-platform** — multiple platforms in the same repo (e.g. backend + mobile, web + backend)."

- `single-platform` → resume the main flow at step 2.5. Use the seven-question batch in `references/stack-interview-common.md` for the single stack. Record `platforms[]` as `[{ name: "<stack key>", path: "." }]` and `structure` as `"sub-folder"` (the default; not written to tracker.json — readers default to it).
- `multi-platform` → continue with Step 2b below.

## Step 2b — Which platforms (checkbox)

Ask the user (multi-select; user picks ≥ 2):

> "Which platforms? Check all that apply.
> - [ ] **mobile** — Flutter or React Native (cross-platform mobile).
> - [ ] **web** — browser frontend (React, Vue, Svelte, Next, Nuxt, Astro, etc.).
> - [ ] **backend** — server-side API or service (Node, Go, Python, Rust, etc.).
> - [ ] **mobile-native** — iOS Swift / Android Kotlin / Compose Multiplatform.
> - [ ] **mobile-flutter** — explicit Flutter (overrides `mobile` if both checked)."

Validation:

- If the user picks fewer than 2, prompt: "Multi-platform requires at least 2 platforms. Re-pick, or switch to single-platform?".
- If both `mobile` and `mobile-flutter` are checked, treat as `mobile-flutter` (more specific wins). Same for `mobile` + `mobile-native` — treat as `mobile-native`.

Record the chosen set as `selected_platforms` (e.g. `["backend", "mobile-flutter"]`).

## Step 2c — Layout

Ask the user (single-select, **default: `sub-folder`**):

> "Repo layout?
> 1. **sub-folder** — each platform lives in its own sub-folder of the repo root (e.g. `backend/`, `mobile/`). One repo. Stable, recommended. **(default)**
> 2. **monorepo** — one repo, nx / turborepo / melos workspace with shared tooling. **Experimental — many skills may behave imperfectly in this mode; expect to file bugs.**
> 3. **polyrepo** — a separate git repo per platform, plus a general/parent repo (the project folder) that owns shared `docs/` and the tracker. **Experimental.**"

Print the experimental warning **verbatim** when the user selects `monorepo`:

```
WARNING: monorepo layout is experimental. Many forge skills (kit-*, execute-ticket,
diagnose, simplify) currently assume sub-folder layout and may behave imperfectly.
File bugs against emberworks-lab/forge when you hit them.
Proceed with monorepo layout? (y/n)
```

Print this warning **verbatim** when the user selects `polyrepo`:

```
WARNING: polyrepo layout is experimental. project-init builds it (general repo +
one repo per platform + clone/pull scripts), but downstream skills (commit,
pr-create, epic-close) are not yet polyrepo-aware — see EPIC L #124.
Proceed with polyrepo layout? (y/n)
```

On `n` → fall back to `sub-folder`. On `y` → record the chosen `structure` and continue.

Record `structure` as `"sub-folder"`, `"monorepo"`, or `"polyrepo"`.

## Step 2d — Per-platform path

For each entry in `selected_platforms`, ask:

> "Path for **<platform>** (relative to repo root)? Press Enter for default `<default>`."

Defaults:

| selected_platform | Default path |
|---|---|
| `backend` | `backend/` |
| `web` | `web/` |
| `mobile` (generic) | `mobile/` |
| `mobile-flutter` | `mobile/` |
| `mobile-native` | `mobile-native/` |

Strip any trailing slash. Validate that the paths are distinct across platforms.

### Polyrepo only — repo names

When `structure == "polyrepo"`, also ask:

1. **General/parent repo name** (once):
   > "Name for the general/parent repo (holds shared `docs/` + tracker)? Press Enter for default `<project>`."
2. **Per-platform repo name**, for each entry in `selected_platforms`:
   > "GitHub repo name for **<platform>**? Press Enter for default `<project>-<platform-short>` (e.g. `<project>-mobile`)."

`<platform-short>` is `backend` / `web` / `mobile` derived from the platform key.
Record the general repo name for tracker-setup (step 7.25) and store each
per-platform repo name on the matching `platforms[]` entry as `repo`.

## Step 2e — Per-platform framework / runtime

Loop through `selected_platforms` in the order the user picked them. For each, ask the **framework / runtime** question from `references/stack-interview-common.md §2` scoped to that platform.

| Platform | What to ask |
|---|---|
| `backend` | Which language + framework (Node + Hono, Node + Nest, Go, Python FastAPI / Django, Rust, Elixir, Java, Ruby). |
| `web` | Which framework + bundler (Next.js, Nuxt, SvelteKit, Astro, plain React + Vite, plain Vue + Vite, Solid, …). |
| `mobile-flutter` | Pure Flutter or Flame-based; targets (iOS / Android / Web / Desktop). |
| `mobile-native` | Which platform(s): iOS Swift / Android Kotlin / Compose Multiplatform / React Native. |
| `mobile` | Resolve to one of `mobile-flutter` / `mobile-native` based on the answer here. |

For each answered platform, resolve the **stack key** via `references/skill-templates-routing.md` (same lookup used by single-platform). Build a `platforms[]` entry:

```jsonc
{ "name": "<stack key>", "path": "<answer from 2d>" }
// polyrepo: also add "repo": "<repo name from 2d>"
```

Example after a backend + Flutter multi-platform interview:

```json
[
  { "name": "backend-node-nest", "path": "backend" },
  { "name": "mobile-flutter",    "path": "mobile" }
]
```

The first entry is the primary / orchestrator platform (use the order the user picked).

## Result — what gets recorded

The multi-platform branch produces three artefacts for downstream steps:

1. **`structure`** — `"sub-folder"`, `"monorepo"`, or `"polyrepo"`.
2. **`platforms[]`** — list of `{ name, path }` entries (plus `repo` when `polyrepo`).
3. **`selected_stacks`** — same as `platforms[].name`, used by step 3 to resolve template paths for each platform.

These flow into:

- **Step 3 / 4 (templates)** — step 3 runs `references/skill-templates-routing.md` per entry in `selected_stacks`; step 4 copies templates per platform into `<path>/.claude/skills/`. *(Implementation in #56.)*
- **Step 7.25 (tracker setup)** — writes `structure` and `platforms[]` into the root `<project>/.claude/tracker.json` per the schema in `plugins/forge/docs/conventions/tracker-json.md`. Per-platform child tracker.json files (with `parent_path: "../"`) are also created when `selected_platforms.length > 1`.
- **Step 8 (output)** — the summary block lists each platform name + path.

## Hard rules

- Never silently default the user past the experimental-monorepo **or polyrepo** warning — always print it verbatim and require explicit `y`.
- Polyrepo records a general/parent repo name (once) plus a `repo` on every `platforms[]` entry — both are required for tracker-setup and the clone scripts.
- Never combine `mobile` and `mobile-flutter` (or `mobile` and `mobile-native`) as separate entries — the more specific choice wins.
- Never write `structure: "sub-folder"` to tracker.json explicitly when the default would do — readers default to `sub-folder` when the field is absent. Only write it when the user picked `monorepo`.
- Single-platform projects do not pass through this file at all; they use the existing `stack-interview-common.md` batch.
