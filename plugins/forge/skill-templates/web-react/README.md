# skill-templates / web-react

Reusable web frontend skill skeletons (React / Next / Astro / Vite).

## Status: skeleton

No skill files yet. Templates land here as we ship web projects.

## Planned skills

When first web project starts, `/project-init` will prompt for these and create stubs:

| File | Purpose | When needed |
|---|---|---|
| `kit-create-feature.md` | Component + hook + types + tests scaffold | Always |
| `kit-add-route.md` | New page + loader/action + route registration | Next/Astro/Remix |
| `kit-add-api-route.md` | New `/api/*` handler + types + tests | Next/Hono on edge |
| `kit-add-migration.md` | Drizzle/Prisma migration + types regen | DB-backed projects |
| `kit-add-i18n.md` | Translation key + `next-intl` / `i18next` integration | i18n projects |
| `kit-deploy.md` | Build + deploy to Vercel/Cloudflare/etc. | Always |

## Linked global rules

- `~/.claude/docs/testing/00_general.md` + `01_web.md`
- `~/.claude/docs/linting/00_general.md` + `01_web.md`
- `~/.claude/docs/conventions/tracker-tickets.md`

## How to seed this folder

When the first web project is real, run `/project-init` in that project. The skill detects the empty templates folder and offers to write generic-first versions interactively, then commits them here for reuse.
