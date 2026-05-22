---
name: simplify
description: Review a code change for reuse, quality, and efficiency, then fix every issue found. Default scope is the most recent change; forge:simplify-branch invokes this with whole-branch scope.
type: hybrid
---

# Simplify

Review a code change for reuse, quality, and efficiency, and fix every valid finding in place. This skill owns the reviewer procedure — `forge:simplify-branch` invokes it with a wider scope rather than duplicating it.

## Phase 1 — Identify the change (scope)

Pick the scope:

- **Default — most recent change:** run `git diff HEAD` (or `git diff --cached` if staged). If both are empty, run `git show HEAD`.
- **Branch scope — when invoked by `forge:simplify-branch`:** the caller supplies the resolved base. Run `git diff <base>...HEAD --stat` then `git diff <base>...HEAD`.

Read the full content of each changed file so the agents have complete context for finding reuse opportunities.

## Phase 2 — Dispatch three Sonnet reviewer agents in parallel

Launch all three agents concurrently in a single message, passing each the full diff and the changed-file contents.

**Agent 1: Reuse** — search for existing utilities, helpers, or patterns that could replace newly written code. Flag new functions that duplicate existing ones; flag inline logic that could use a shared utility (string manipulation, path handling, environment checks, type guards).

**Agent 2: Quality** — flag hacky patterns: redundant state, parameter sprawl, copy-paste with slight variation, leaky abstractions, stringly-typed code, unnecessary JSX nesting, and unnecessary comments (those explaining WHAT rather than WHY).

**Agent 3: Efficiency** — flag: unnecessary work (redundant computations, duplicate calls, N+1 patterns), missed concurrency (sequential independent operations), hot-path bloat, unconditional state updates in loops, unnecessary existence checks (TOCTOU anti-pattern), memory leaks, and overly broad reads.

## Phase 3 — Fix and summarise

Wait for all three Sonnet agents to complete. Aggregate findings; fix each valid issue directly. Skip false positives silently. When done, briefly summarise what was fixed, or confirm the code was already clean.
