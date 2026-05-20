---
name: diagnose
description: Disciplined 6-phase diagnosis loop for bugs and performance regressions — builds a fast feedback loop first, then reproduces, hypothesises, instruments, fixes, and regresses-tests.
type: hybrid
---

# Diagnose

A discipline for hard bugs. Skip phases only when explicitly justified.

> **Escalation:** for bugs where 3+ fixes have already failed or the root cause is genuinely mysterious, invoke `forge:diagnose-deep` — it applies a 4-phase Iron Law protocol with stronger gates. `/diagnose` is the lighter 6-phase variant optimised for a fast feedback loop; pick the heavy version when the cheap path has already failed.

When exploring the codebase, use the project's domain glossary to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a fast, deterministic, agent-runnable pass/fail signal, you will find the cause. If you don't, no amount of staring at code will save you.

Spend disproportionate effort here. **Be aggressive. Be creative. Refuse to give up.**

Try in roughly this order: failing test → curl/HTTP script → CLI invocation with fixture → headless browser script → replay captured trace → throwaway harness → property/fuzz loop → bisection harness → differential loop → HITL bash script.

Once you have a loop, iterate: make it faster, sharpen the signal, make it deterministic. A 2-second deterministic loop is a debugging superpower; a 30-second flaky one is barely better than none.

Do not proceed to Phase 2 until you have a loop you believe in.

## Phases 2–6

Full checklists for Reproduce, Hypothesise, Instrument, Fix + regression test, and Cleanup + post-mortem are in `references/phases.md`.
