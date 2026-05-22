---
name: kit-create-endpoint
description: "Use when adding or changing an HTTP API endpoint, route, or controller method in the NestJS backend (POST/GET/PATCH/DELETE handlers in any feature module), or when a client reports a generic 500 / 'unexpected error' from an endpoint."
---

# kit-create-endpoint

## When to use

- Triggers: "add an endpoint", "create an API route", "new controller method", `/kit-create-endpoint`.
- A client receives `code: "internal_server_error"` / "unexpected error" — almost always an expected failure thrown as a raw `Error`.

Don't use for: a background job (`/kit-add-queue`), a WebSocket message (`/kit-create-ws-gateway`), or a pure schema change (`/kit-add-prisma-model`).

## What it produces

- A DTO class in `src/modules/<feature>/<feature>.schemas.ts` (Zod + `createZodDto`, or plain class-validator class)
- A controller method (HTTP shape only — no business logic)
- A service method (all business logic; throws typed exceptions)
- A `*.spec.ts` covering the success path and every failure path

## Required inputs

- Feature module name (snake_case, e.g. `orders`)
- HTTP verb + path (e.g. `POST /orders`)
- Request body / query shape
- Success status code
- Expected failure codes

## Steps

1. **Check `.claude/api-docs.json`** — branch on `openapi` flag (see below).
2. **DTO first.** In `src/modules/<feature>/<feature>.schemas.ts` add a Zod schema + `createZodDto` class (or a plain `class` with `class-validator` decorators if Zod is not installed). This is the single source of truth for runtime validation and TypeScript types.
3. **Controller method.** Add the handler to the module's controller. Bind the DTO with `@Body(new ValidationPipe()) body: <Name>Dto` (or `@Query(...)`). Set the HTTP status with `@HttpCode(HttpStatus.X)`. Apply guards at controller or handler level. The controller only translates HTTP ↔ service call; no business logic here.
4. **Service method.** Implement the behavior in the service. On any expected failure throw a typed `HttpException` subclass with a `{ code: "snake_case" }` object — never let a raw `Error` represent an expected failure.
5. **Tests.** Write `*.spec.ts` for the service. Assert the success result and, for each failure path, the thrown exception type **and its `code``.
6. **Doc-sync.** See "Doc-sync by `openapi` flag" below.
7. Run `npm run lint && npm test && npm run build` — all must pass before reporting done.

## The error convention

`AllExceptionsFilter` (`src/exceptions/all-exceptions.filter.ts`) normalizes every thrown value into `{ code, message, requestId }`. How you throw determines what the client sees:

| You throw | Client gets |
|---|---|
| `new NotFoundException({ code: "entity_not_found" })` | `404`, `code: "entity_not_found"` ✅ |
| `throw new Error("not found")` | `500`, `code: "internal_server_error"` ❌ |

**Rule: every expected failure is `throw new <Http>Exception({ code: "snake_case_code" })`.** The `code` is a stable API contract. A raw `Error` is reserved for genuine bugs (→ 500).

Standard mappings:

| Exception | Status | Use for |
|---|---|---|
| `BadRequestException` | 400 | malformed but schema-valid input |
| `UnauthorizedException` | 401 | missing / invalid credentials |
| `ForbiddenException` | 403 | authenticated but not allowed |
| `NotFoundException` | 404 | entity does not exist |
| `ConflictException` | 409 | duplicate / state conflict |

Validation pipe failures (`422 validation_error`) are handled automatically — no extra code needed.

## Doc-sync by `openapi` flag

Read `.claude/api-docs.json` in the project root:

### `openapi: true` — Swagger pipeline

Add `@nestjs/swagger` decorators to every new/changed route and DTO:

```ts
// Controller
@ApiTags('<feature>')
@Controller('<resource>')
export class <Feature>Controller {

  @Post()
  @ApiOperation({ summary: 'Create a <Entity>' })
  @ApiResponse({ status: 201, description: 'Created', type: <Name>ResponseDto })
  @ApiResponse({ status: 409, description: 'Conflict — entity_already_exists' })
  create(@Body() body: Create<Entity>Dto): Promise<<Name>ResponseDto> { ... }
}

// DTO
export class Create<Entity>Dto {
  @ApiProperty({ description: 'Human-readable name', example: 'My entity' })
  name: string;
}
```

After adding decorators run `npm run docs:api` to regenerate `docs/api/endpoints.md` from `openapi.json`. Do NOT hand-edit the generated block — fix the decorators and re-run.

### `openapi: false` — hand-written docs

No `@nestjs/swagger` decorators needed. Instead, after implementing the endpoint manually update `docs/api/endpoints.md` with the new route, request/response shape, and error codes.

## Conventions

- Controller = HTTP shape; service = logic; repository = persistence. Keep them separate.
- `code` values are lowercase `snake_case`, descriptive, stable (`entity_not_found`, not `err1`).
- Service methods are named for verbs (`create<Entity>`, `get<Entity>`), returning typed results.
- Authenticated routes read caller identity via `req.user?.id` behind an auth guard.

## Anti-patterns

- `throw new Error("not found")` for an expected failure → becomes a generic `500`. Use `NotFoundException({ code: "..." })`.
- Putting business logic in the controller.
- Relying on the exception class name as the client-facing code — always pass an explicit `{ code }`.
- Shipping an endpoint whose `*.spec.ts` covers only the happy path.
- Hand-editing the generated `<!-- auto -->` block in `endpoints.md` when `openapi: true`.

## Example

```ts
// <feature>.service.ts
async get<Entity>(id: string, requesterId: string): Promise<Get<Entity>Result> {
  const item = await this.<entity>Repository.findById(id);
  if (item === null || item.ownerId !== requesterId) {
    throw new NotFoundException({ code: '<entity>_not_found' });
  }
  return this.toResult(item);
}
```

## References

- `src/exceptions/all-exceptions.filter.ts` — error envelope + `code` handling
- `src/exceptions/error-response.dto.ts` — `{ code, message, requestId }` shape
- `src/modules/<feature>/` — controller / service / schemas triplet layout
- `.claude/api-docs.json` — `{ "openapi": true|false }` opt-in marker
- `docs/api/endpoints.md` — hand-maintained when `openapi: false`; generated when `openapi: true`
