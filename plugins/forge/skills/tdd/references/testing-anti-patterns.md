# Testing anti-patterns

When you reach for a mock, a fixture helper, or a "just-for-tests" hook, scan this list first. Each pattern below is a way to make a test pass while making the test useless.

## 1. Testing the mock, not the code

You wire up a mock with an elaborate expectation, the test passes, you ship.

```typescript
const mock = jest.fn().mockResolvedValue({ id: 1 });
service.userRepo = mock;
await service.fetchUser(1);
expect(mock).toHaveBeenCalledWith(1);
```

What's tested: that `service.fetchUser(1)` calls its dependency with `1`. What's not tested: that `service.fetchUser` returns the right thing, handles a missing user, propagates errors, or does anything useful.

If a refactor changes `fetchUser` to silently return `undefined`, this test still passes. The mock is the entire surface; the production code's behavior is invisible.

**Fix:** assert on the *output* of the unit under test, not the call shape of its collaborators. Mocks are for substituting expensive dependencies, not for becoming the test target.

## 2. Adding test-only methods to production code

```typescript
class Cache {
  // ...
  _resetForTests() { this.store.clear(); }
  _getInternalState() { return { ...this.store }; }
}
```

These methods are now part of the public API. Other code will discover them and call them in production. Worse, they encode an assumption that the test needs internal access — usually a sign that the code's collaborators are too tightly coupled to let you test from the outside.

**Fix:** if a test needs to reset state, expose a real reset method that's safe in production, or construct a fresh instance per test. If it needs internal state, expose a real query method, or test through the observable behavior that *uses* the state.

## 3. Mocking without understanding the dependency

You don't fully know what `s3.putObject` does, so you mock it with `mockResolvedValue({})`. The test passes. Six months later, in production, `putObject` is failing with an auth error and the test never exercised that path because the mock didn't know it could fail.

**Fix:** read the real dependency's signature and failure modes. Reproduce at least one failure path in a test. If the dependency is too complex to model, that's a design signal — wrap it in a thin adapter you control and test the adapter against the real thing in an integration test.

## 4. Fixture spaghetti

A test starts with 80 lines of fixture setup. The actual assertion is two lines. You can't tell from reading the test what behavior is being tested.

**Fix:** extract fixture builders with intention-revealing names (`anActiveUserWithUnpaidInvoice()`). If a single test needs more than a screenful of setup, the unit under test is doing too much — split it.

## 5. Tests that change when the implementation changes

The test checks call counts, internal field values, the order of an internal queue, or the contents of a private cache. Every implementation change requires updating the test.

**Fix:** test the contract, not the implementation. If a behavior is "after three failures, the operation gives up", assert that the operation gave up after three failures, not that an internal counter equals three.

## 6. The "happy path only" test suite

Every test exercises the success case. No test exercises errors, edge inputs, empty collections, concurrent writes, partial failures.

**Fix:** for each new behavior, write at least one test for the obvious failure mode. Empty input, missing dependency, error from a collaborator, concurrent access — pick the one that's most likely to bite and lock it in.

## 7. Brittle async timing

```typescript
await sleep(100);
expect(state.loaded).toBe(true);
```

`sleep(100)` works on your machine, fails on CI, fails on a slow day. The test is flaky and gets retried into oblivion.

**Fix:** poll for the condition (`waitFor`, `untilTrue`, framework helpers) with a generous timeout and a clear failure message. Never assume wall-clock time is the same on every machine.

## 8. One test that asserts everything

A single test sets up a workflow, runs it, then asserts on twelve different aspects of the final state. When it fails, you don't know which behavior broke.

**Fix:** split into one test per behavior. The setup is shared via fixture builders; the assertions are not.

## When to use mocks

Mocks earn their place when:

- The dependency is genuinely external and slow / paid / unreliable.
- The dependency has destructive side effects (DELETE FROM production, billing.charge(...)).
- The dependency doesn't exist yet (you're TDDing the collaborator).

Outside these, default to real code. The test is more truthful and the design pressure is more honest.
