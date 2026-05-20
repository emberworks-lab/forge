# skill-templates / backend-node

Reusable Node backend skill skeletons (Hono / Express / Fastify / NestJS).

## Status: skeleton

No skill files yet. Templates land here as we ship backend projects.

## Planned skills

| File | Purpose | When needed |
|---|---|---|
| `kit-create-route.md` | Route handler + DTO + service + tests | Always |
| `kit-add-migration.md` | Drizzle/Prisma migration + apply | DB-backed projects |
| `kit-add-job.md` | Background job + scheduler hook | If using BullMQ / Inngest / queue |
| `kit-add-mcp-tool.md` | MCP tool definition + handler + tests | If exposing MCP server |
| `kit-deploy.md` | Build + deploy to Cloudflare Workers / Vercel / Fly | Always |

## Linked global rules

- `~/.claude/docs/testing/00_general.md` + `04_backend.md`
- `~/.claude/docs/linting/00_general.md` + `04_backend.md`
- `~/.claude/docs/conventions/tracker-tickets.md`

## How to seed this folder

When the first Node backend project is real, run `/project-init` there. Generic-first templates get written interactively and committed here.

## Other backend stacks

This is `backend-node` only. Sibling folders for `backend-go`, `backend-python`, `backend-rust`, `backend-elixir` will be added when those stacks become real.
