# Testing — backend

Augments `00_general.md` for backend services (Node / Go / Python / Rust / Elixir).

## Stack mapping

| Stack | Unit | HTTP | DB | Property | E2E |
|---|---|---|---|---|---|
| **Node** (Hono / Express / Fastify / NestJS) | Vitest | supertest OR Hono's `app.request()` | testcontainers + drizzle-kit/prisma | fast-check | Playwright (against deployed preview) |
| **Go** | testing + testify | `httptest.NewServer` | testcontainers-go | gopter | k6 / vegeta (load) |
| **Python** (FastAPI / Django) | pytest | TestClient (FastAPI), `Client` (Django) | pytest-postgresql / testcontainers | Hypothesis | Locust |
| **Rust** (Axum / Actix) | built-in `#[test]` | `axum::Router::oneshot` | testcontainers | proptest | drill |
| **Elixir** (Phoenix) | ExUnit | Phoenix.ConnTest | Ecto.Sandbox (built-in!) | StreamData | — |

Default for new Node projects: **Vitest + supertest + testcontainers (Postgres) + fast-check + Playwright for cross-service E2E**.

## Layer guidance

### Unit

Pure functions: validators, transformers, parsers, business rules.

Mock: nothing. Use real implementations. If a function is hard to test pure, it's doing too much — refactor.

### Service / handler

The unit of "do work" — typically receives input (validated DTO), calls repos, returns output.

```ts
test('createOrder rejects when total < min', async () => {
  const repo = { save: vi.fn() };
  const service = new OrderService(repo);
  
  const result = await service.create({ items: [], total: 0 });
  
  expect(result.ok).toBe(false);
  expect(result.error).toBe('TOTAL_TOO_LOW');
  expect(repo.save).not.toHaveBeenCalled();
});
```

Mock the repository (boundary), not other services in the same layer.

### Route / endpoint (HTTP integration)

Spin up the actual app, hit it via supertest / TestClient / equivalent. Stub external deps (other services, payment, email) at the network level.

```ts
test('POST /orders returns 201 + Location header on success', async () => {
  const res = await request(app).post('/orders').send({...validOrder});
  expect(res.status).toBe(201);
  expect(res.headers.location).toMatch(/^\/orders\/\w+$/);
});
```

### Database integration

Use testcontainers (or equivalent) to spin up a real DB instance per test suite. **Don't mock the DB.** Mocking SQL is harder than running it.

```ts
import { GenericContainer } from 'testcontainers';

beforeAll(async () => {
  pgContainer = await new GenericContainer('postgres:16')
    .withEnvironment({ POSTGRES_PASSWORD: 'test' })
    .withExposedPorts(5432)
    .start();
  // ... apply migrations
});

afterAll(() => pgContainer.stop());
```

For RLS-enabled stacks (Supabase, custom Postgres RLS): test policies explicitly. Spin up DB, apply RLS migration, set role, run query, assert allowed/denied. **RLS bugs are silent — they MUST be tested.**

### E2E

For backend, E2E means: client (Playwright or curl scripts) → deployed preview → real DB. Cover:
- Auth flows (signup, login, refresh, logout)
- Critical writes that span multiple services
- Idempotency keys (replay same request, same outcome)

Skip for: every CRUD endpoint. That's what HTTP integration covers.

## Property-based — high value for backend

Backend has many invariant-style properties:

- Idempotency: `f(f(x)) == f(x)`
- Retry safety: same input twice = same output once
- Serialization round-trip: `parse(stringify(x)) == x`
- Sort stability: same input + same sort = same output

```ts
// fast-check example
fc.assert(
  fc.property(fc.array(fc.record({ id: fc.uuid(), n: fc.integer() })), (xs) => {
    const a = sortByN(xs);
    const b = sortByN(sortByN(xs));
    expect(a).toEqual(b);
  })
);
```

## Auth / RLS / multi-tenant testing

Critical for SaaS. Always test:

1. Anonymous user cannot read others' data
2. User A cannot read/write User B's data
3. Service-role bypass works for admin endpoints
4. Token expiry rejects requests
5. RLS on Postgres applies BEFORE app-layer checks (defense in depth)

This is its own test file (`auth_isolation_test.ts` / similar). Don't bury it in unit tests.

## Test command outputs (for test-runner)

- **Vitest**: structured TAP/JSON; `--reporter=json` for parsing
- **Go test**: `-json` flag emits one JSON object per event
- **pytest**: `pytest --json-report` (pytest-json-report plugin) OR parse stdout
- **cargo test**: `--message-format=json` for structured output

Test-runner agent picks parser based on `CLAUDE.md > Stack` line.

## What "manual test cases" look like for backend

```markdown
## Manual test cases (BE-12)

- Run `npm run dev`; verify server starts on :3000
- POST /api/orders with valid body → 201 + body.id present
- POST same body again with same idempotency key → 201, SAME body.id (idempotent)
- POST without auth header → 401
- POST as user A; GET /api/orders/<id> as user B → 404 (not 403; don't leak existence)
- Check Postgres: `SELECT * FROM orders WHERE id = '<id>';` matches the response
- Tail logs; expect ONE order_created event, no duplicates
```

## Common pitfalls

- **Mocking the DB** — don't. Use testcontainers. The slight CI overhead is worth real DB behavior.
- **In-memory SQLite as Postgres substitute** — different SQL dialect; missed bugs. Use real Postgres.
- **Forgetting to test RLS** — silent privilege escalation. Always have an `auth_isolation_test`.
- **Time-based assertions** (`createdAt should be now()`) — use clock injection or `expect(x).toBeWithin(now ± 1s)`.
- **Shared state between tests** — DB rows, Redis keys, global singletons. Reset in `beforeEach` OR isolate via per-test schemas.
- **Testing through the wrong layer** — unit tests for HTTP routing logic, E2E tests for pure functions.

## Coverage targets (descriptive)

| Layer | Target |
|---|---|
| `services/`, `domain/` (pure logic) | 90%+ |
| `handlers/`, `routes/` (HTTP boundary) | 80%+ |
| `repos/`, `dao/` | 80%+ via integration tests |
| `db/migrations/` | 100% applied (each migration has at least one test) |
| `infra/`, `config/` | not tested |
