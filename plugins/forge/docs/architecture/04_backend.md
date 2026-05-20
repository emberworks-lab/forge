# Architecture — Backend Services

Architecture patterns for backend HTTP services and APIs. Covers layering, transaction
management, DI, observability, and async patterns. Stack-agnostic where possible
(examples reference Node.js with Express/Fastify/Hono, but patterns apply broadly).
General principles are in `00_general.md`.

---

## Layer Model

```
HTTP layer          routes / controllers
    ↓  DTOs / validated input
Service layer       business logic, orchestration
    ↓  domain models
Repository layer    data access interface
    ↓
Data sources        DB (Drizzle / Prisma / raw SQL), external APIs, cache
```

**Routes / Controllers.** Parse and validate requests; call services; map results to
HTTP responses. No business logic. No direct DB calls. Thin wrappers.

**Service layer.** Orchestrates business rules, calls repositories, enforces invariants,
raises domain errors. Must be testable without HTTP infrastructure.

**Repository layer.** Abstracts data access behind an interface. Services depend on the
interface; the concrete implementation depends on the ORM or query builder.
Enables swapping persistence without touching services.

**Data sources.** ORM models, raw queries, external API clients. These are implementation
details hidden behind repositories.

---

## Request Validation and DTOs

Validate input at the boundary (route / controller) before it enters the service layer.
Use a schema library (Zod, Valibot, class-validator) and fail fast with structured errors.

```
Request JSON  →  Zod schema parse  →  typed DTO  →  service call
```

Never pass raw `req.body` into services. Domain models must never contain HTTP-specific
fields (headers, query strings, cookies).

---

## Transaction Scope

Transactions belong at the service layer, not the repository layer. A service method
that calls multiple repositories may need to wrap them in a single transaction to preserve
consistency.

```typescript
// Service method — owns the transaction boundary
async transferCredits(from: UserId, to: UserId, amount: number): Promise<void> {
  await db.transaction(async (tx) => {
    await creditRepo.debit(from, amount, tx);
    await creditRepo.credit(to, amount, tx);
  });
}
```

Repositories accept an optional transaction context parameter. They never start their own
transactions implicitly, as this prevents callers from composing atomic operations.

---

## Dependency Injection

**Request-scoped DI.** Most production Node.js apps wire dependencies per-request or
per-handler using factory functions. Suitable for stateless services.

**App-scoped (singleton) DI.** Long-lived objects (DB connection pools, caches, config)
are created once at app startup and injected via a container (tsyringe, awilix, manual).

Prefer explicit constructor injection over ambient singletons. A service that receives its
DB connection as a constructor argument is trivially testable; one that imports a global
pool is not.

---

## Idempotency

Any write operation that may be retried (payment, message send, job enqueue) must be
idempotent. Design for at-least-once delivery, implement for exactly-once semantics.

Strategies:
- **Idempotency key in request header.** Client generates a UUID; server stores it and
  returns the cached result on duplicate submission.
- **Natural key deduplication.** Upsert on a unique constraint rather than insert.
- **Event deduplication in queues.** Track processed event IDs in a seen-set.

---

## Health Checks and Observability

Every service exposes:
- `GET /healthz` (liveness) — returns 200 if the process is running.
- `GET /readyz` (readiness) — returns 200 only when the service can handle traffic
  (DB connected, warm-up done). Used by load balancers and orchestrators.

Structured logging:
- Emit JSON logs with `level`, `message`, `requestId`, `userId` (when available), and
  `durationMs` for every request.
- Use a request-scoped logger so all log lines for a request share the same `requestId`.

Metrics:
- Track request count, latency (p50/p95/p99), error rate, and queue depth.
- Emit spans for DB queries and external calls to enable distributed tracing.

---

## Async Patterns

**Synchronous (request-response).** Default for reads and most writes. Simple, debuggable,
easy to test. Use when the operation completes in < 1–2 seconds.

**Background jobs / queues.** Decouple slow or unreliable work from the HTTP request
lifecycle. The HTTP handler enqueues a job and returns immediately; a worker processes it.
Use for: emails, heavy computation, third-party API calls, bulk operations.

**Cron / scheduled tasks.** For periodic work (cleanup, aggregation, reminders).
Prefer a dedicated cron runner or a DB-backed job scheduler over `setInterval` in the
app process. The scheduler must be resilient to process restarts.

**Event-driven.** Services emit domain events (e.g., `order.placed`) to a message broker;
downstream services subscribe. Decouples teams and enables eventual consistency.
Complexity cost: harder to trace, requires idempotent consumers, eventual consistency
must be acceptable.

**Rule:** start with synchronous; introduce queues when you have a proven need for
decoupling or resilience. Do not add a message broker speculatively.

---

## Error Handling Strategy

Define a typed error hierarchy at the domain level:
- `DomainError` — business rule violations (not found, insufficient balance, forbidden).
  Maps to 4xx HTTP responses.
- `InfraError` — persistence, network, or external service failures.
  Maps to 5xx HTTP responses.

A central error-handling middleware translates typed errors to HTTP responses and logs
them with appropriate severity. Services throw typed errors; routes never inspect raw
`Error` objects.

---

## Security Basics (structural)

- Authenticate at the route level via middleware; never inside service methods.
- Authorise within the service layer where business context is available.
- Sanitise inputs at the boundary; never trust data from the client inside the service.
- Parameterise all queries; never interpolate user input into SQL strings.
- Store secrets in environment variables; never in source code or DB.

---

## Problem Signals

- Controllers contain if/else business logic — missing service layer.
- Services import ORM models directly instead of going through repositories — layer bypass.
- A repository starts its own transaction, preventing callers from composing operations.
- No input validation at route boundaries — raw `req.body` passed to services.
- Retryable operations have no idempotency mechanism — duplicate-write risk.
- `GET /healthz` queries the database — liveness and readiness are conflated.
- Background work runs inside the HTTP request lifecycle via `await` — blocks the server.
- Secrets hard-coded or committed to version control.
- Global singletons for DB connections passed implicitly — untestable services.
- Synchronous fan-out to multiple slow external services inside a single request — latency risk.
