# kit-update-docs trigger map

Maps changed-file patterns to the docs they affect. Paths are relative to each platform's `path` (from `tracker.json.platforms[]`), or the repo root for root-scoped changes. The skill walks every platform plus root (see SKILL.md Step 1).

## Backend API docs (NestJS / OpenAPI projects)

Applies when the platform's template is `backend-nest` or the platform has a `docs/api/` directory.

| Changed file pattern | Doc to update | How |
|---|---|---|
| `src/controllers/**`, `src/**/*.controller.ts` | `docs/api/endpoints.md` | Run the project's OpenAPI generator (e.g. `pnpm openapi:gen`), then regenerate the endpoints doc from the new `openapi.json` diff. The doc is `<!-- auto -->`-guarded |
| `src/exceptions/**`, new error codes, `*ErrorResponseDto*` | `docs/api/errors.md` | Hand-written error catalog (RFC 7807). Surface a prompt listing the new/changed error codes; do not auto-write prose |
| `src/**/gateway*.ts`, `src/events/**`, `*.gateway.ts` | `docs/api/websockets.md` + `asyncapi.yaml` | Surface a prompt to update the websocket catalog + AsyncAPI skeleton; do not auto-write |

## Owner-facing docs

Applies when `docs/owner-overview.md` exists at repo root.

| Trigger | Section to refresh | How |
|---|---|---|
| Epic closed (invoked from `forge:epic-close`) | `Features.Shipped`, `Features.In-progress`, `Phases` | Move the just-closed epic's features from In-progress → Shipped; update the current/next phase. Only inside `<!-- auto:<key> -->` guards |
| Dependency added/removed (`package.json`, `pubspec.yaml`, `*.csproj` changed) | `Libraries & tools` | Refresh the active opt-in module / library list from the manifest |
| Milestone change (roadmap milestone status flips) | `Phases & Milestones` | Sync the milestone table with `docs/00_meta/roadmap.md` |

**Guard discipline:** never edit inside `<!-- manual --> … <!-- /manual -->`. Only regenerate `<!-- auto:<key> --> … <!-- /auto:<key> -->` blocks.

## Meta docs (universal — see docs-workflow.md mandatory cross-doc table)

| Trigger | Doc | How |
|---|---|---|
| A decision locked during the work | `docs/00_meta/decisions-log.md` | Append an entry (or defer to `/log-decision` if running interactively) |
| An item deferred | `docs/00_meta/roadmap.md` deferred section | Add with reason + re-eval trigger |
| A deferred item resolved | `roadmap.md` deferred + decisions-log + the spec | Drop from deferred, log, update spec |
| A new domain term introduced in any doc | `docs/00_meta/glossary.md` | Add an entry in the same sync |

## README / CLAUDE.md

| Changed file pattern | Doc | How |
|---|---|---|
| New top-level capability, new essential command | `<platform>/README.md`, `<platform>/CLAUDE.md` | Update the relevant section (Essential commands table, feature list); minimal edits |

## Multi-platform notes

- A single sync run covers every platform in `platforms[]` plus root in one pass.
- A file under `<platform.path>/` updates that platform's docs; root-level changes update root docs.
- Single-platform projects (`platforms: [{name, path: "."}]`) behave exactly as the legacy single-root sweep — no special case needed.
