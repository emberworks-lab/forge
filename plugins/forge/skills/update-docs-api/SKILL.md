---
name: update-docs-api
description: Backend API documentation child of forge:update-docs — keeps endpoints, errors, and websocket docs in sync with the code, via the Swagger/OpenAPI pipeline when opted in or hand-written Markdown when not. Dispatched by forge:update-docs when the backend API surface changed.
type: hybrid
---

# forge:update-docs-api

The backend API-reference child of `forge:update-docs`. Keeps `docs/api/*` in sync with controllers, exceptions, and gateways. Markdown source only; any HTML view (Swagger UI / Redoc / AsyncAPI HTML) is generated from specs, never hand-written (format law lives in the parent).

## Opt-in: Swagger vs hand-written

Read `<platform>/.claude/api-docs.json`:

```json
{ "openapi": true }
```

| State | Meaning | endpoints.md source |
|---|---|---|
| `openapi: true` | Swagger pipeline | Generated from `openapi.json` via the project's `docs:api` command |
| `openapi: false` | Hand-written | `endpoints.md` is hand-maintained Markdown; no generator runs |
| Absent | Undecided | `--init` asks the user (see below); default proposes `true` |

`errors.md` and `websockets.md` are hand-written Markdown regardless of the Swagger choice — there is no auto-generator for an RFC 7807 error catalog, and websocket docs are sourced from `asyncapi.yaml`.

## Inputs

`--root`, `--platform <path>` (the backend platform), `--epic`, `--dry-run`. `--init` to set up the opt-in marker.

## Flow

### `--init`

Ask: "Generate API docs from Swagger/OpenAPI? It needs `@nestjs/swagger` + a Markdown renderer. (yes / no)".

- **Yes** → write `api-docs.json` `{ "openapi": true }`. Surface the manual-setup: install `@nestjs/swagger` + a renderer (e.g. `widdershins` / `redocly`), and add a `docs:api` command to the project's `CLAUDE.md` Essential commands that renders `openapi.json` → `docs/api/endpoints.md`.
- **No** → write `{ "openapi": false }`. API docs will be hand-written Markdown. Never asks again.

### `--run` (sync)

For each changed file in the backend platform:

| Changed | Doc | Action |
|---|---|---|
| `src/**/*.controller.ts` | `docs/api/endpoints.md` | **openapi:true** → run the project's `docs:api` command (regenerates the `<!-- auto -->` block from `openapi.json`); also surface a reminder: annotate new endpoints/DTOs with `@nestjs/swagger` decorators so the spec is complete. **openapi:false** → surface a prompt listing the changed endpoints to hand-edit |
| `src/exceptions/**`, new error codes, `*ErrorResponseDto*` | `docs/api/errors.md` | Surface a prompt with the new/changed error codes (RFC 7807). Hand-written; do not auto-write prose |
| `src/**/gateway*.ts`, `src/events/**` | `docs/api/websockets.md` + `asyncapi.yaml` | Surface a prompt to update the AsyncAPI skeleton + the catalog. AsyncAPI HTML, if wanted, is generated from `asyncapi.yaml` |

### Report

List each doc touched / prompt surfaced with a one-line reason.

## Do not

- Do not write or edit HTML — MD source + specs only; HTML is generated (Swagger UI / Redoc / AsyncAPI HTML).
- Do not hand-edit a generated `endpoints.md` `<!-- auto -->` block — fix the decorators + re-run `docs:api`.
- Do not invent error or event semantics — surface a prompt for the human.
- Do not commit — the caller owns commit semantics.

## What this child does not cover

- **owner-overview / roadmap / glossary** — `forge:update-docs-meta`.
- **Design specs / ADR** — `forge:update-docs-design`.
- **The renderer itself** — shipped by the `backend-nest` template's `docs:api` command, not by this skill.
