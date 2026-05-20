---
name: simplify-branch
description: Run reuse, quality, and efficiency review across all commits in the current branch versus its base, then fix every issue found.
type: hybrid
---

# Simplify Branch

Review and simplify all code changes in the current branch compared to its base. Covers every commit in the branch — not just the last one.

## Phase 1 — Identify the diff

1. Determine the base branch: check if `develop` exists (`git rev-parse --verify develop`). If yes, use `develop`; otherwise use `main`.
2. Run `git diff <base>...HEAD --stat` to see which files changed.
3. Run `git diff <base>...HEAD` to get the full diff.
4. Read the full content of each changed file so agents have complete context for finding reuse opportunities.

## Phase 2 — Dispatch three Sonnet reviewer agents in parallel

Launch all three agents concurrently in a single message. Pass each agent the full diff.

**Agent 1: Reuse** — for each change, search for existing utilities and helpers that could replace newly written code. Flag new functions that duplicate existing ones; flag inline logic that could use a shared utility (string manipulation, path handling, environment checks, type guards).

**Agent 2: Quality** — flag hacky patterns: redundant state, parameter sprawl, copy-paste with slight variation, leaky abstractions, stringly-typed code, unnecessary JSX nesting, and unnecessary comments (those explaining WHAT rather than WHY).

**Agent 3: Efficiency** — flag: unnecessary work (redundant computations, duplicate calls, N+1 patterns), missed concurrency (sequential independent operations), hot-path bloat, unconditional state updates in loops, unnecessary existence checks (TOCTOU anti-pattern), memory leaks, and overly broad reads.

## Phase 3 — Fix and summarise

Wait for all three Sonnet agents to complete. Aggregate findings; fix each valid issue directly. If a finding is a false positive, note it and move on. When done, briefly summarise what was fixed, or confirm the code was already clean.
