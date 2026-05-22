---
name: simplify-branch
description: Review and fix reuse, quality, and efficiency across all commits in the current branch versus its base — the whole-branch entry point that delegates the reviewer procedure to forge:simplify.
type: minimal
---

# Simplify Branch

Whole-branch counterpart to `forge:simplify`: reviews every commit in the branch versus its base, not just the most recent change. The reviewer + fix procedure is owned by `forge:simplify` — this skill only resolves the branch scope and delegates, so the two never drift.

## Flow

1. Resolve the base branch: if `develop` exists (`git rev-parse --verify develop`), use it; otherwise `main`.
2. Invoke `forge:simplify` with branch scope — pass the resolved base so its Phase 1 runs `git diff <base>...HEAD`. `forge:simplify` then dispatches its three Sonnet reviewer agents (reuse / quality / efficiency) and applies fixes.
3. Relay its summary. If files changed, the caller (e.g. `forge:epic-close`) re-runs its tests-pass gate.
