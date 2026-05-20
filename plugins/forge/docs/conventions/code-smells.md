# Code Smells

Language-agnostic reference for code review agents. No platform-specific syntax. Each entry: what it is, why it matters, how to recognize it, how to fix it.

---

## General

**Long Method.** A function does too much — multiple levels of abstraction mixed together. Hard to name, test, and reuse. Split into smaller, well-named helpers, each doing one thing.

**God Object.** A class or module that controls too much and knows about too many others. Every change touches it; it can't be tested in isolation. Split by responsibility; delegate to smaller collaborators.

**Feature Envy.** A method reaches into another module's internals more than it uses its own. Sign that the logic belongs in the other module. Move the method or extract a shared abstraction.

**Shotgun Surgery.** One conceptual change requires edits scattered across many files. Indicates missing abstraction or wrong ownership. Centralize the varying behavior.

**Divergent Change.** A single module changes for many unrelated reasons. Violates single-responsibility. Split into focused modules, one reason to change each.

**Duplicate Code.** The same logic exists in multiple places. Any fix must be applied everywhere, and one copy will eventually diverge. Extract a shared function or abstraction.

**Primitive Obsession.** Domain concepts modeled as raw strings, integers, or booleans instead of named types. Ambiguous, error-prone, and hard to validate. Introduce value types or domain objects.

**Inappropriate Intimacy.** Two modules know too much about each other's internals. Changes in one break the other. Add a clear interface boundary; hide implementation details.

**Lazy Class.** A class exists but doesn't carry its weight — too little behavior to justify its existence. Inline it into the caller or merge with a related class.

**Data Clumps.** The same group of fields or parameters always appear together. They're asking to be a named type. Introduce a value object or record.

**Long Parameter List.** A function takes more than 3–4 arguments. Hard to call correctly and hard to test. Group related parameters into an object; use named options.

**Magic Numbers / Strings.** Hardcoded literal values with no explanation. Break at any rename, and the meaning is invisible at the call site. Replace with named constants.

**Deep Nesting.** Multiple levels of if/else, loops, or callbacks stacked inside each other. Hides the happy path and makes error handling hard to follow. Return early; extract inner blocks into functions.

**Dead Code.** Functions, branches, or variables that are never reached or used. Misleads readers and increases maintenance burden. Delete it; version control has the history.

**Unsafe Casts.** Forcing a value to a more specific type without a runtime check. Causes crashes on unexpected input. Validate before casting; prefer pattern-matching or typed alternatives.

**Overly Clever Expressions.** Dense chains or one-liners that exploit language tricks. Impresses no one and confuses everyone at 9 AM. Prefer clarity over brevity; add intermediate variables.

---

## Frontend (web + mobile UI)

**Context / Scope Leaks.** A UI component or callback holds a reference to a context, view, or scope that has already been destroyed. Causes crashes or memory leaks. Tie object lifetimes to the component lifecycle; use weak references where appropriate.

**Business Logic in UI Layer.** Domain rules (validation, calculations, state transitions) live inside a view, component, or template. Untestable and duplicated whenever the UI changes. Move logic to domain or service layer; UI should only render and dispatch events.

**Prop Drilling.** Data or callbacks passed through many layers of components that don't use them — only forward them. Makes refactoring painful. Use a shared state container or event bus at the appropriate level.

**Stale Closures.** A callback captures a variable by reference but the reference becomes outdated by the time the callback runs. Produces subtle, intermittent bugs. Capture the value explicitly or re-subscribe when dependencies change.

**Missed or Unstable List Keys.** Collections rendered without stable identity markers, causing the framework to destroy and re-create items unnecessarily. Degrades performance and can cause flickering. Use stable, unique identifiers — never array indices for reorderable lists.

**Excessive Recomposition / Re-render.** A parent component re-renders causing all children to re-render, even unchanged ones. Creates jank on large trees. Stabilize references (memoize objects and callbacks); push state down to where it's consumed.

**Heavy Work in Render / Build.** Expensive computation (parsing, filtering, network calls) triggered directly inside the render cycle. Blocks the UI thread. Move heavy work to background tasks; cache results; compute only on input change.

**Missing Error Boundary / Error State.** A component can fail but has no visual fallback — the whole screen crashes or shows nothing. Add explicit loading, error, and empty states at every async boundary.

---

## Backend

**Blocking I/O on the Main Thread.** Synchronous database or network calls on a thread that must stay responsive. Starves the thread pool under load. Use async primitives and dedicated I/O executors.

**Anemic Domain Model.** Domain objects are pure data containers; all business logic lives in service classes that manipulate them. Leads to scattered, duplicated rules. Move behavior into the domain objects that own the data.

**Transactional Sprawl.** Business operations that should be atomic are spread across multiple independent transactions. Leaves data partially updated on failure. Wrap related writes in a single transaction; use saga patterns for cross-service operations.

**N+1 Queries.** A list is loaded, then each item triggers an additional query. Latency grows linearly with result size. Use batch loading, joins, or eager-load strategies at the query boundary.

**Missing Idempotency.** An endpoint that mutates state can be called multiple times with different results (e.g., duplicate charges, double sends). Make write operations safe to retry by checking preconditions or using idempotency keys.

**Premature Optimization.** Complex caching, denormalization, or micro-optimizations added before a bottleneck is measured. Adds complexity and bugs with no proven benefit. Profile first; optimize the measured hot path.

---

## Refactoring Signals

These patterns indicate it's time to refactor — not just clean up:

- Tests require heavy mocking or are brittle; changing one thing breaks unrelated tests.
- A new feature requires touching more than 3 unrelated files.
- A module has more than 10 public functions without a clear unifying theme.
- Reviewers consistently need to ask "what does this do?" for names or logic.
- The same bug fix has been applied in multiple places.
- Onboarding a new contributor to a module takes longer than an hour.
- A component or service accumulates unrelated responsibilities over successive PRs.

When you see 2+ signals in one area, treat refactoring as a prerequisite, not a nice-to-have.
