# backend-node interview

## Ask about

- **Framework** — Hono / Express / Fastify / NestJS.
- **Database** — Postgres + ORM choice (Drizzle / Prisma / Kysely / raw).
- **Auth** — custom / Clerk / Supabase / Auth.js / better-auth.
- **Deployment target** — Cloudflare Workers / Vercel / Fly / Render / Railway / AWS.

## Generate

- `kit-create-route.md` — handler + types + tests.
- `kit-add-migration.md` — schema migration via the chosen ORM.
- `kit-add-job.md` — background job (queue / cron).
- `kit-deploy.md` — build + deploy for the chosen target.

## Notes

- Cloudflare Workers deployment skills should call out the `wrangler.toml` shape and the bindings the user configured.
- NestJS scaffolds typically need a separate `kit-create-module.md` — ask whether to include it.
