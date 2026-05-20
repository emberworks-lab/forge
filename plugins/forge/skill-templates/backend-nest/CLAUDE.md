# NestJS backend — policy reminders

## Stack conventions

- **All errors** must use `AllExceptionsFilter` (registered globally in `main.ts`).
  Throw `HttpException` subclasses with a `{ code: "snake_case", message: "..." }` object
  response so `AllExceptionsFilter` surfaces a stable `code` to clients.
- **Prisma**: never call `PrismaClient` directly in controllers or services that are
  not `PrismaService`. Use the injectable `PrismaService` wrapper.
- **Validation**: use a validation pipe (NestJS built-in or `nestjs-zod`).
  Never accept raw untyped request bodies.
- **Secrets**: read exclusively from `process.env`. Never hard-code credentials.

## Doc-sync rule (enforced)

Every PR that changes a **controller**, **exception**, or **gateway** MUST also
update the corresponding `docs/api/*` file:

| Changed file type                       | Required doc update              |
|-----------------------------------------|----------------------------------|
| `src/**/*.controller.ts`                | `docs/api/endpoints.md`          |
| `src/exceptions/*.ts` or new error code | `docs/api/errors.md`             |
| `src/**/*.gateway.ts`                   | `docs/api/websockets.md` + `asyncapi.yaml` |

Reviewers reject PRs that add/change these files without updating docs.

## Plugin skills

Use `forge:execute-ticket` for standard feature tickets.
Run `forge:simplify-branch` before opening a PR.

## Testing

- Unit tests: `*.spec.ts` beside the source file.
- E2E tests: `test/` folder, `jest-e2e.json` config.
- Run `npm test` (unit) and `npm run test:e2e` before committing.
- Minimum 80% line coverage on new modules.

## What NOT to add here

- Deployment config (`Dockerfile`, `fly.toml`) — project-specific, not in template.
- Lock files (`pnpm-lock.yaml`, `package-lock.json`) — generated, not committed to template.
- `node_modules/`, `dist/`, `coverage/` — build artifacts.
