---
name: simplify
description: Review the most recent code change for reuse, quality, and efficiency, then fix every issue found.
type: hybrid
---

# Simplify

Review the current uncommitted change (or the last commit if working tree is clean) for reuse, quality, and efficiency. Fix every valid finding in place.

## Phase 1 — Identify the change

1. Run `git diff HEAD` (or `git diff --cached` if staged). If both are empty, run `git show HEAD`.
2. Read the full content of each changed file so agents have complete context for finding reuse opportunities.

## Phase 2 — Dispatch three Sonnet reviewer agents in parallel

Launch all three agents concurrently in a single message, passing each the full diff and the full file content.

**Agent 1: Reuse** — search for existing utilities, helpers, or patterns that could replace newly written code. Flag new functions that duplicate existing ones; flag inline logic that could use a shared utility.

**Agent 2: Quality** — flag hacky patterns: redundant state, parameter sprawl, copy-paste with slight variation, leaky abstractions, stringly-typed code, unnecessary JSX nesting, and unnecessary comments (those explaining WHAT rather than WHY).

**Agent 3: Efficiency** — flag: unnecessary work (redundant computations, duplicate calls), missed concurrency (sequential independent operations), hot-path bloat, unconditional state updates in loops, unnecessary existence checks (TOCTOU anti-pattern), memory leaks, and overly broad reads.

## Phase 3 — Fix and summarise

Wait for all three Sonnet agents to complete. Aggregate findings; fix each valid issue directly. Skip false positives silently. When done, briefly summarise what was fixed, or confirm the code was already clean.
