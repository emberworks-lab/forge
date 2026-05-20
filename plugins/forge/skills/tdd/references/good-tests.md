# What makes a good test

A test you write under TDD has three jobs: prove the behavior is implemented, lock the behavior in against future regression, and document the API for future readers. All three depend on the test being good. Bad tests do none of these reliably.

## The three qualities

### Minimal

One behavior per test. If the test name contains "and" between two verbs, it's two tests pretending to be one — split it.

Why: when a multi-behavior test fails, you don't know which behavior broke. Diagnosis costs more than the time saved by bundling.

### Clear

The test name describes the behavior, not the mechanism.

Bad: `test_retry`, `test1`, `test_handler_works`.
Good: `retries failed operations three times before giving up`, `rejects empty email with a required-field error`.

A reader who hasn't seen the code should know what the system is supposed to do from the test name alone.

### Intent-revealing

The test body demonstrates the API the code should expose. It uses the real types and real call shapes. If the test is hard to read, the API is hard to use; that's a design signal, not a test problem.

## A concrete pair

### Good

```typescript
test('retries failed operations three times before giving up', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('transient failure');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

- Name describes the behavior.
- Operation is a real function with real failure semantics.
- Asserts both the outcome (succeeded) and the mechanism that matters (three attempts, not one or five).

### Bad

```typescript
test('retry works', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');

  await retryOperation(mock);

  expect(mock).toHaveBeenCalledTimes(3);
});
```

- Name is vague.
- Tests the mock's call count, not the operation's behavior. If `retryOperation` returns `undefined` because of a bug, this test still passes.
- The test will keep passing even if the production code does nothing meaningful with the mock's resolved value.

## Tests that show intent vs tests that obscure it

| Quality | Good | Bad |
|---|---|---|
| Minimal | One thing. If "and" appears in the name, split. | `test('validates email and domain and whitespace')` |
| Clear | Name describes behavior. | `test1`, `test_handler` |
| Intent-revealing | Shows the API readers will use. | Inscrutable mock plumbing |

## Real code over mocks

Default to using real types, real instances, real I/O against fixtures. Reach for a mock only when:

- The dependency is genuinely external and slow or unreliable (network, paid API, OS-level operation).
- The dependency has destructive side effects that aren't safe in a test.
- The dependency hasn't been built yet (TDD-on-collaborators).

A test that's 90% mock setup tests your understanding of the mock, not the behavior of the system. If you find yourself there, the design has too many tight couplings — fix the design, not the test.

## Naming style

Pick one convention per project, stick to it. The point is that the test name reads like a sentence describing the requirement.

- Behavior-as-sentence: `'returns 404 when user is not found'`.
- Should-prefix: `'should return 404 when user is not found'`.
- Given-when-then: `'given a missing user, when fetched, returns 404'`.

All three are fine. `test1`, `test_func`, `xyz` are not.

## Self-check

Before claiming the test is done:

- [ ] Name describes behavior in a sentence.
- [ ] Body shows the API consumers will use.
- [ ] Asserts the outcome that matters (not just call counts on mocks).
- [ ] One behavior, not several.
- [ ] You can hand the test to a stranger and they understand what the code is supposed to do.
