---
name: bad-subagent-spawn-example
description: Intentionally broken fixture — spawn without model name.
type: minimal
---

# Bad Subagent Spawn Example

This fixture is intentionally broken to verify that `audit.sh` check 10 fires
when a SKILL.md spawns a subagent without naming the model.

## Step 1 — Do the work

Spawn `linter-runner` agent with `mode=fix` on the changed files.

In parallel, spawn `test-runner` agent with `mode=report`.

## What the audit will flag

- Check 10: both spawn lines lack a model name (sonnet|opus).
