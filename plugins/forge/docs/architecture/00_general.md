# Architecture — General Principles

Universal architecture principles applicable across all platforms and stacks.
Platform-specific guidance lives in the sibling files.

---

## Core Principles

**1. Modularity.** Divide the system into cohesive modules with well-defined boundaries.
Each module can be understood, tested, and changed independently.

**2. Separation of concerns.** Each unit (function, class, module, service) has one focused
reason to change. Mixing UI, business logic, and I/O in the same unit creates rigid code.

**3. High cohesion, low coupling.** Keep related behaviour together; minimise dependencies
between modules. Coupling should flow through explicit, stable interfaces — never through
shared mutable state or internal implementation details.

**4. Dependencies inward.** Inner layers (domain, core) know nothing about outer layers
(infrastructure, UI, frameworks). Depend on abstractions, not concretions.

**5. Stable contracts.** Module boundaries are defined by interfaces or types, not
implementations. Contracts change infrequently and are versioned when they do.

**6. Explicit data flow.** State transitions and data movement are visible and traceable.
Avoid implicit side effects, ambient globals, and hidden channels.

**7. Composition over inheritance.** Prefer assembling behaviour from small, composable units
rather than deep inheritance hierarchies. Inheritance couples caller and callee tightly.

**8. Single source of truth.** Each piece of data has exactly one authoritative source.
Derived state is computed, not stored in parallel.

**9. Fail explicitly.** Errors are first-class values or typed exceptions. Never swallow
errors silently; callers must acknowledge failure paths.

**10. Testability by design.** Architecture that forces integration tests to verify domain
logic is a design problem. Pure functions and injected dependencies make unit tests cheap.

---

## Architecture Styles

Choose a style by context, not by habit.

### Layered (Presentation / Domain / Data)
Classic three-layer separation. Simple to understand. Works well for CRUD-heavy apps.
Risk: layers become pass-through scaffolding; business logic leaks into controllers.

### Hexagonal / Ports & Adapters
Domain is the centre; all external concerns (DB, network, UI) attach via ports (interfaces)
and adapters (implementations). Enables swapping infrastructure without touching domain.
Use when the domain is complex and testability is a priority.

### Clean Architecture
Extension of hexagonal with explicit dependency rule: source-code dependencies always
point inward. Entities → Use Cases → Interface Adapters → Frameworks & Drivers.
Suitable for large apps with long lifetimes and cross-cutting concerns.

### Event-Driven
Components communicate via events rather than direct calls. Decouples producers and
consumers; enables async pipelines and audit logs. Complexity cost: harder to trace flows.

### Microservices
Independent, separately deployable services with their own persistence.
Only reach for this when team/scale/deployment constraints justify the operational overhead.
Most apps do not need it.

---

## DRY, KISS, YAGNI

**DRY (Don't Repeat Yourself).** Duplicate knowledge, not code. Sharing code is fine
only when the abstraction is stable. Premature de-duplication creates coupling.

**KISS (Keep It Simple, Stupid).** The simplest design that correctly solves the problem
is almost always the right design. Complexity must be justified by concrete requirements.

**YAGNI (You Aren't Gonna Need It).** Don't build hooks, extension points, or features
before they are actually required. Speculative generality raises maintenance cost.

---

## Concurrency Patterns

**Producer–Consumer.** Decouple work production from processing via a queue or channel.
Absorbs bursts and decouples throughput.

**Thread Pool / Executor.** Reuse threads; control parallelism explicitly. Avoid unbounded
thread creation.

**Pipeline.** Process data through a linear chain of stages, each with clear input/output.
Compose stages independently and test each in isolation.

**Actor model.** Each actor owns its state and communicates via messages, eliminating
shared-state hazards. Suitable for high-concurrency scenarios.

**Futures / Promises / async-await.** Compose asynchronous work without blocking threads.
Prefer structured concurrency (bounded scopes) over fire-and-forget.

**Backpressure.** Slow consumers must be able to signal producers to slow down.
Without backpressure, queues grow unboundedly and memory is exhausted.

**Immutability.** Prefer immutable data structures. Shared mutable state is the primary
source of concurrency bugs.

---

## Reliability Patterns

**Timeouts.** Every external call must have a timeout. Unbounded waits cascade into
system-wide hangs.

**Retries with backoff.** Transient failures should be retried with exponential backoff
and jitter. Always bound the number of retries.

**Circuit breaker.** When a downstream dependency fails repeatedly, stop sending requests
and fail fast. Allows the dependency to recover without being overwhelmed.

**Bulkheads.** Isolate resource pools (thread pools, connection pools) by subsystem.
One subsystem exhausting its pool should not starve others.

**Idempotency.** Operations that may be retried must produce the same result on
repeated execution. Use idempotency keys for writes.

---

## Quality Attribute Trade-offs

**Performance vs simplicity.** Optimise only for proven bottlenecks with measurement.
Premature optimisation obscures intent and increases defect risk.

**Scalability vs consistency.** Distributed systems cannot have strong consistency and
high availability simultaneously (CAP). Choose explicitly and document the trade-off.

**Security vs usability.** Security controls add friction. Document security decisions,
their rationale, and accepted risks so they are not accidentally removed.

**Testability.** Small, pure components with injected dependencies are cheaply testable.
Architecture that requires end-to-end tests for unit-level validation is a design smell.

---

## Problem Signals

- UI code queries the database or calls network APIs directly.
- Domain models import framework types (HTTP request objects, ORM entities).
- A small change requires edits in many unrelated modules.
- Adding a new feature requires understanding the entire codebase.
- Unit tests require spinning up databases, network services, or full frameworks.
- A class has more than one clear reason to change.
- Shared mutable state is accessed without synchronisation.
- Error handling is missing, swallowed, or logged-and-ignored.
- Interfaces have a single implementation and no testability benefit — YAGNI violation.
- Build times grow proportionally with team size — missing module boundaries.
