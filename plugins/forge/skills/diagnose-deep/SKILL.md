---
name: diagnose-deep
description: Rigorous four-phase debugging workflow for bugs that resist quick fixes. Invoked by forge:diagnose when a defect needs root-cause discipline rather than a guess-and-check loop.
type: fundamental
inspired-by:
  - author: obra
    repo: github.com/obra/superpowers
    skill: systematic-debugging
    relation: adapted
---

# Diagnose-deep

The disciplined variant of debugging. `forge:diagnose` (skill not yet migrated) routes hard cases here; this skill takes over until a root-cause fix is verified.

## Iron law

```
No fix proposal until Phase 1 produces evidence of the root cause.
```

If you have not finished Phase 1, you cannot propose a fix. Reading the stack trace and saying "probably X" is not evidence; reproducing, instrumenting, and observing is.

## When to use

Any technical defect where the cheap path has already failed or looks dangerous:

- Test failures after a change you thought was harmless.
- Bugs that recur after a previous fix.
- Unexplained behavior across components (CI → build → deploy, API → service → DB).
- Performance regressions with no obvious culprit.
- Build, integration, or environment failures you can't reproduce locally.

Use it especially when:

- Time pressure is high (rushing produces thrash, not progress).
- The "obvious" fix is so obvious you haven't verified it.
- You've already tried 2+ fixes and each one revealed a new symptom.

Don't skip on grounds of "simple bug". Simple bugs have root causes too, and the discipline is fast on simple ones.

## The four phases

Each phase has a gate. Don't move on until the gate is satisfied.

### Phase 1 — Root cause investigation

Gate: you can name the root cause and point at evidence (log line, diff, instrumented output).

1. **Read the error.** Don't skim. Stack trace, line numbers, error codes, exit status, the full failure message. Often the answer is already there.
2. **Reproduce consistently.** What are the exact steps? Does it happen every time? If not, gather more data before forming a theory.
3. **Check recent changes.** `git log`, `git diff`, dependency bumps, config changes, environment shifts. Bisect if needed.
4. **Instrument multi-component systems.** When the failure crosses boundaries (CI → build → signing, API → service → DB), add explicit logging at each boundary: what entered, what exited, environment state, config propagation. Run once, read the output, identify the failing layer, focus there. See `references/instrumentation.md` for the boundary-logging pattern with examples.
5. **Trace data flow backward.** When the error fires deep in the stack, find where the bad value originated, not where it surfaced. See `references/backward-tracing.md` for the technique.

### Phase 2 — Pattern analysis

Gate: you can name what's different between this case and a known-working analogue.

1. **Find a working example.** Similar code in the same codebase, the same pattern applied elsewhere, a reference implementation.
2. **Read the reference completely.** Don't skim; partial understanding is the source of most "I thought this worked like that" bugs.
3. **Enumerate differences.** Every difference between the working case and the broken one. Don't pre-filter for "that can't matter".
4. **Map dependencies.** What does this code need at runtime — environment, config, sibling services, ordering assumptions?

### Phase 3 — Hypothesis and test

Gate: you have a single hypothesis stated out loud, plus a minimal experiment that distinguishes "true" from "false".

1. **State one hypothesis.** "I think X is the root cause because Y." Specific, written down, falsifiable.
2. **Test minimally.** The smallest change that would distinguish true from false. One variable at a time. Don't fix; probe.
3. **Verify before moving on.** Confirmed → Phase 4. Refuted → form a new hypothesis with the new evidence. Never stack hypotheses on top of each other.
4. **Admit ignorance when stuck.** "I don't understand X" beats a confident-but-wrong theory. Re-read, ask, instrument further.

### Phase 4 — Fix and verify

Gate: a regression test exists, the test failed before the fix, passes after, and no other tests broke.

1. **Write a failing test first.** Simplest reproduction. Automated where possible; a one-off script otherwise. This invokes `forge:tdd` for non-trivial cases.
2. **Implement a single fix.** Address the root cause from Phase 1, not the symptom. One change. No bundled refactors, no "while I'm here" cleanups.
3. **Verify.** The new test passes. No other test regressed. The user-visible bug is gone.
4. **If three fixes have failed, stop and question the architecture.** Pattern: each fix exposes a new shared-state or coupling problem in a different place; each fix requires "massive refactoring". That's not a hypothesis failure — that's a wrong abstraction. Pause and discuss with the user before attempting fix #4. See `references/architectural-escape-hatch.md` for the full criteria.

## Red flags — stop, return to Phase 1

If you catch yourself thinking any of these, you have skipped a phase:

- "Quick fix for now, investigate later."
- "Let me just try changing X and see."
- "Multiple changes, run the tests, see what sticks."
- "Skip the test, I'll verify manually."
- "It's probably X, let me fix that."
- "I don't fully understand this, but this might work."
- "Here are the main problems: [list of fixes, no investigation]."
- "One more fix attempt" — when you've already tried two or more.
- Each fix reveals a new problem in a different place.

The rationalizations that produce these are catalogued in `references/rationalizations.md`.

## User signals you're doing it wrong

When the user says any of the below, stop and return to Phase 1:

- "Is that actually happening?" — you assumed without verifying.
- "Will that show us…?" — you should have added evidence-gathering.
- "Stop guessing." — proposing fixes without understanding.
- "Think harder about this." — question fundamentals, not just symptoms.
- "We're stuck?" (frustrated) — the current approach isn't working; change it.

## Quick reference

| Phase | Activity | Gate |
|---|---|---|
| 1. Root cause | Read errors, reproduce, instrument, trace | Evidence of the cause |
| 2. Pattern | Find working example, enumerate differences | Differences named |
| 3. Hypothesis | One theory, minimal probe | Confirmed or replaced |
| 4. Fix | Failing test, single fix, verify | Test green, no regressions |

## Outputs

When the workflow completes, return:

- The root cause in one sentence.
- The fix (file + commit reference) and the regression test that locks it in.
- Any defense-in-depth additions made along the way.

## What this skill does not cover

- **Quick triage** — that's `forge:diagnose` (skill not yet migrated). It decides whether to handle inline or escalate here.
- **Writing the actual regression test** — delegated to `forge:tdd`.
- **Performance profiling tooling** — this skill drives the *process*, not the specific profiler / sampler / tracer; pick the tool that fits the stack.
