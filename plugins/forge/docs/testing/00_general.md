# Testing — universal principles

These rules apply to ALL stacks. Stack-specific guidance lives in sibling files (`01_web.md`, `02_mobile_flutter.md`, etc.) and **adds to**, never overrides, this file.

## Core principle: tests as a tool, not a goal

We don't write tests for coverage. We write them when they earn their cost.

**Write a test when AT LEAST ONE is true:**

- It documents intended behavior that a human reader would otherwise re-derive from code (Bloc state machines, formula edge cases, parser branches)
- It guards a fragile invariant (sort stability, timezone handling, retry idempotency)
- It will run in CI and catch a class of regression you've actually hit before
- It gives a deterministic harness for an algorithm where eyeballing fails (combat damage, drop tables, scheduling)
- It encodes a contract between layers (repository ↔ DAO, API client ↔ server)

**Skip a test when:**

- It tests framework code (Flutter SDK, Express middleware, React's `useState`)
- It tests generated code (Drift `.g.dart`, freezed, json_serializable, Prisma client)
- It's a trivial getter/setter without logic
- It exists only to bump coverage % with no failure mode it would catch
- It mocks so much that it tests the mock more than the code

## Test pyramid (universal)

```
         ┌──────────────┐
         │     E2E      │   1-5%   slow, brittle, real environment
         ├──────────────┤
         │ Integration  │  10-25%  multiple modules, real I/O scoped
         ├──────────────┤
         │     Unit     │  70-85%  one function/class, mocked I/O
         └──────────────┘
```

Names per stack vary (widget tests in Flutter, component tests in React, etc.) — fit them into one of the three layers.

## Naming + layout

- **Test files mirror source layout.** `lib/foo/bar.dart` → `test/foo/bar_test.dart`. `src/components/Button.tsx` → `src/components/Button.test.tsx` (or `__tests__/Button.test.tsx`, per stack convention).
- **Test name = behavior described.** `it('returns Result.err when DB times out')` not `it('test1')`.
- **Group by subject, not by setup.** `describe('UserRepository.findById')` then nested `it('...')`.

## Property-based testing

Use property-based tests for:

- Deterministic algorithms with a state space (RNG given a seed, hashing, parsers)
- Invariants over a domain (sorted list stays sorted after insert; serialization roundtrips)
- Combinatoric formulas (combat damage scaling, pricing tiers)

Tools per stack: glados (Dart), fast-check (JS/TS), Hypothesis (Python), QuickCheck (Go via gopter).

Skip property-based for: UI rendering, I/O, anything stochastic where the property itself is fuzzy.

## Manual test cases — output artifact

After implementing a ticket, the executor (`/execute-ticket`) generates a `## Manual test cases` block as a Linear comment on the ticket. After all tickets in an epic are implemented, `/execute-epic` aggregates them as a single comment on the epic.

A test case is:
- A user-observable verification step ("open screen X → see Y")
- 3-5 bullets per ticket — not exhaustive QA, just the path to confirm the work landed
- Phrased as actions, not assertions — the human running them does the assertion

Example block:
```markdown
## Manual test cases (EMB-228)

- Run `flutter run --flavor dev`; from main menu open the combat screen
- Tap "attack" 3 times; expect damage events in the console (look for `[combat] dmg=...`)
- Restart the app; expect combat state to NOT persist (in-memory bloc only)
- On Android emulator, rotate to landscape; expect HP bar layout to not overflow
```

## Test loop in skills

`/execute-ticket` and `/execute-epic` follow this loop:

1. Run lint command (from `CLAUDE.md > Essential commands > Lint`)
2. If lint fails: fix loop, max 2 attempts; if still failing → halt + report
3. Run test command (relevant subset, not full suite)
4. If tests fail: spawn `test-runner` agent to analyze + propose fix; apply; re-run; max 3 iterations
5. If still failing → halt + report to user; do NOT commit

`/execute-epic` adds a final pass: full lint + full test suite from main session, after all tickets land.

## Coverage

- Coverage is **information**, not a gate. We don't fail PRs on coverage drops.
- Use coverage tooling (`flutter test --coverage`, `vitest --coverage`, `pytest --cov`) to spot gaps in critical modules — formulas, sync logic, parsers.
- Don't write a test purely to bump a number.

## Snapshot / golden tests

Use sparingly:
- For design-system primitives that should not change accidentally (Button variants, Card states)
- For pixel-stable UI of high-traffic screens (home, checkout)

Skip for:
- Volatile UI (still being designed)
- Anything that depends on platform fonts, animations, or randomized data
- Whole-screen snapshots — they trigger constantly and get rubber-stamped

Update tooling per stack (`flutter test --update-goldens`, `vitest -u`, etc.) is acceptable when the change is intended; reviewer must look at the diff.

## What test-runner agent expects

The `test-runner` agent (`~/.claude/agents/test-runner.md`) is universal. It:
1. Reads `CLAUDE.md > Essential commands` to find the test command
2. Optionally takes a path filter (run only `test/combat/`)
3. Runs the command, parses output (stack-specific parsers — see per-platform doc)
4. Returns: pass count, fail count, failure summaries (file:line + assertion + actual vs expected)
5. On failure, can propose a fix if invoked with `mode=fix`

Do not call test-runner from inside a test. Test-runner is for orchestration layer only.

## What NOT to do

- **No "let me just add a test for everything I touched"** — that's coverage-chasing
- **No tests that mock the System Under Test itself** — you end up testing the mock
- **No flaky tests left in.** A flaky test is a broken test. Either make it deterministic or delete it
- **No tests that depend on wall-clock time, network, or external services** — wrap them
- **No commits with broken tests** — `/execute-ticket` halts before commit if tests fail
