---
name: tdd
description: Rigid red-green-refactor discipline for any feature, bug fix, or behavior change. Invoked by forge:execute-ticket and forge:diagnose-deep when production code is about to be written.
type: fundamental
inspired-by:
  - author: obra
    repo: github.com/obra/superpowers
    skill: test-driven-development
    relation: adapted
---

# TDD

Write the failing test first. Watch it fail for the right reason. Write the minimum code to pass. Refactor with the test as a fence. Repeat.

The whole skill exists to force one observation: **if you didn't watch the test fail, you don't know that it tests the right thing.**

## Iron law

```
No production code without a failing test that ran first.
```

Wrote code before the test? Delete it. Start over with the test.

No "keep it as reference". No "let me adapt it while I write the tests". No "I'll just look at it". Delete means delete. Implement fresh from the test you just watched fail.

## When to use

Always, for:

- New features.
- Bug fixes (the failing test reproduces the bug).
- Refactors (the existing tests are your fence; if there aren't any, add them before changing behavior).
- Any behavior change.

The only exceptions, which require explicit user permission:

- Throwaway prototypes — `forge:prototype` territory, not this skill.
- Generated code — already exercised by the generator's own tests.
- Config files — declarative; tests are usually integration-level.

"Skip TDD just this once" is a rationalization. The skill catches it; see `references/rationalizations.md`.

## The cycle

```
RED  →  verify RED  →  GREEN  →  verify GREEN  →  REFACTOR  →  verify GREEN  →  next
```

### RED — write the failing test

One test. One behavior. Real code under test (no mocks unless the dependency is genuinely unavoidable). Clear name describing the behavior, not the mechanism.

See `references/good-tests.md` for what a good test looks like, what a bad one looks like, and why.

### Verify RED — watch it fail

**Mandatory.** Run the test and observe the failure.

```
<your test command for the file>
```

Confirm:

- The test fails — not errors out from a typo or import bug.
- The failure message is the one you'd expect from the missing behavior.
- The test fails because the feature doesn't exist yet, not because the test itself is broken.

If the test passes immediately, you're testing existing behavior — fix the test to actually demand the new behavior.

If the test errors out (import error, syntax error, fixture missing), fix the error, re-run, keep going until you see a clean fail.

### GREEN — minimum code to pass

Write the smallest change that turns the test green. Resist:

- Adding options the test didn't ask for.
- Refactoring unrelated code.
- Generalizing "for future use".

The contract is exactly "make this test pass". Future tests are written by future you.

### Verify GREEN — watch it pass

**Mandatory.** Run the test and the surrounding suite.

Confirm:

- The new test passes.
- No other test regressed.
- Output is pristine: no warnings, deprecation notices, or stray prints. If there are warnings, fix them or explicitly accept them — never ignore them.

If the new test fails, the code is wrong — fix the code, not the test.

If a sibling test broke, fix that now, not later.

### REFACTOR — clean up, stay green

Only after green. Remove duplication, improve names, extract helpers, simplify shapes. Run the tests after each meaningful change. The moment they turn red, stop and revert or fix; you've changed behavior, not just structure.

Don't add new behavior here. New behavior gets a new RED test.

### Repeat

Next failing test for the next slice of behavior.

## Good tests

Three minimum qualities. Full discussion in `references/good-tests.md`.

| Quality | What it means |
|---|---|
| Minimal | One behavior per test. If "and" appears in the test name, split it. |
| Clear | The name describes the behavior, not the implementation. `test1` is malpractice. |
| Intent-revealing | The test shows how the code should be called and what it should do. Reading the test should teach the API. |

## Order matters — why test-after isn't TDD

The complete catalogue of "but tests-after is the same" rationalizations and the responses is in `references/rationalizations.md`. The core failure mode in one sentence:

> Tests written after the code pass immediately, and passing immediately is not evidence.

A test you never saw fail might test the wrong thing, might test the implementation rather than the behavior, might miss the edge cases you forgot, might be coupled to a mock that's coupled to a bug. The only way to know the test tests something is to see it fail for the right reason and then see it pass for the right reason.

Tests-after answer "what does this code do?" Tests-first answer "what should this code do?" The second question is the one that designs the API.

## Red flags — stop, start over

Each of these means the discipline has cracked; delete, restart with TDD:

- Code written before a test.
- Test written after the code passes immediately.
- "Can't explain why the test failed."
- "I'll add the tests later."
- "Already manually tested it."
- "Tests-after achieves the same goal."
- "Keep this as reference and write tests around it."
- "Already invested X hours; deleting is wasteful." (Sunk cost.)
- "TDD is dogmatic; I'm being pragmatic."
- "This case is different because…"

All of these end the same way: delete the code, write the test, watch it fail, write the code fresh.

## Verification checklist

Before claiming work complete:

- [ ] Every new function/method has a test.
- [ ] You watched each test fail before implementing.
- [ ] Each test failed for the expected reason (feature missing, not a typo).
- [ ] You wrote the minimum code to pass each test.
- [ ] All tests pass now.
- [ ] Output is pristine: no warnings, no stray prints.
- [ ] Tests use real code; mocks only where unavoidable.
- [ ] Edge cases and error paths are covered.

Can't check all boxes? You skipped TDD. Restart.

## When stuck

| Symptom | Move |
|---|---|
| "I don't know how to test this." | Write the API you wish existed. The test reveals it. |
| "The test is too complicated." | The design is too complicated. Simplify the interface, then test. |
| "I have to mock everything." | The code is too coupled. Use dependency injection or split the unit. |
| "Test setup is huge." | Extract test helpers. If it's still huge, the design is wrong. |

## Bug fixes

A bug means: there exists a behavior the system promised but didn't deliver. Write the failing test that reproduces the bug, watch it fail, fix the code, watch the test pass. Now the bug is locked out — it has a guard.

Never fix a bug without first writing the failing test that proves the fix.

## Testing anti-patterns

When you reach for a mock or a test helper, scan `references/testing-anti-patterns.md` first. The list covers testing-the-mock-not-the-code, adding test-only methods to production classes, and "mocking without understanding the dependency".

## Final rule

```
Production code → a test exists, and it failed first.
Otherwise → not TDD.
```

No exceptions without explicit user permission.
