# skill-templates / backend-nest

NestJS 10 backend template — core scaffold only.

## Stack

| Layer      | Library                    |
|------------|----------------------------|
| Framework  | NestJS 10 + Express        |
| ORM        | Prisma 5 (PostgreSQL)      |
| Language   | TypeScript 5 (strict)      |
| Testing    | Jest 29 + Supertest        |

## What's included

```
backend-nest/
├── src/
│   ├── main.ts                          # Bootstrap: global filter wired here
│   ├── app.module.ts                    # Root module — add feature modules here
│   ├── app.controller.ts / app.service.ts
│   └── exceptions/
│       ├── error-response.dto.ts        # RFC 7807 envelope type
│       └── all-exceptions.filter.ts     # Global HTTP exception → ErrorResponseDto
├── prisma/
│   └── schema.prisma                    # Minimal example schema (one model)
├── docs/api/
│   ├── endpoints.md   — auto-generated from @nestjs/swagger openapi.json
│   ├── errors.md      — hand-written RFC 7807 error catalog
│   └── websockets.md  — channel catalog (refers to asyncapi.yaml)
├── asyncapi.yaml                        # AsyncAPI 3 skeleton
├── nest-cli.json
├── tsconfig.json / tsconfig.build.json
└── package.json
```

## Doc conventions

- `docs/api/endpoints.md` — regenerate after adding/changing routes.
- `docs/api/errors.md` — add a row for every new error code.
- `docs/api/websockets.md` + `asyncapi.yaml` — update together when adding
  NestJS Gateways. See `CLAUDE.md` for the enforced rule.

## Opt-in additions (not in core)

The following are intentionally omitted; add when the project needs them:

| Feature          | Packages                              |
|------------------|---------------------------------------|
| Auth / JWT       | `@nestjs/jwt`, `@nestjs/passport`     |
| Validation (Zod) | `nestjs-zod`, `zod`                   |
| Structured logs  | `nestjs-pino`, `pino-http`            |
| Rate limiting    | `@nestjs/throttler`                   |
| Background jobs  | `@nestjs/bullmq`, `bullmq`, `ioredis` |
| OpenAPI / Swagger| `@nestjs/swagger`                     |
| WebSockets       | `@nestjs/websockets`, `@nestjs/platform-socket.io` |
| Deployment       | `Dockerfile`, `fly.toml` (project-specific) |

## Getting started

```bash
# 1. Copy template into your project
cp -r plugins/forge/skill-templates/backend-nest/ my-app/backend/

# 2. Rename package
#    Edit package.json → "name": "my-app-backend"

# 3. Install dependencies
npm install

# 4. Set DATABASE_URL in .env and run Prisma migration
npx prisma migrate dev --name init

# 5. Start dev server
npm run start:dev
```
