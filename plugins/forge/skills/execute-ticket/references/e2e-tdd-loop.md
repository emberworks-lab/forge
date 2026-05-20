# Step 6.5 — E2E TDD loop (when ack opts in)

Activated when the ticket body (fetched in Step 1) contains an `## E2E coverage` block whose `required:` value is `yes`, `web`, `backend`, or `mobile`. Absent or `required: no` → skip the whole step.

## Detection

Parse the ack section. The line shape is:

```markdown
## E2E coverage
required: <yes | web | backend | mobile>
scope: <prose>
```

- `required: yes` → use the project's **default** e2e flavor (see qualifier resolution below).
- `required: web` → web e2e flavor (Playwright / etc — wired by EPIC H).
- `required: backend` → backend HTTP / API e2e flavor.
- `required: mobile` → mobile e2e flavor (research; may halt as "no consumer wired yet").

## Qualifier resolution

Read `<project>/.claude/tracker.json` → `platforms[]`. Match the ticket's stated flavor against what the project supports:

1. If `required: yes`: pick the first entry in `platforms[]` that is e2e-capable. If `platforms[]` is missing or empty → default to `backend`.
2. If `required: web | backend | mobile`: that exact flavor is requested. If the project's `platforms[]` does NOT list it → halt with `unsupported-e2e-flavor: <flavor> requested but not in tracker.json platforms[]`.
3. If `platforms[]` is missing entirely → default to `backend` (backwards-compatible with single-platform repos).

The chosen flavor is the **e2e-flavor** used for the rest of this step.

## Flow

### 6.5.1 — RED: generate e2e spec files via `forge:tdd`

Spawn `forge:tdd` with model **`opus`** (creative — generates test cases from prose acceptance criteria). Pass:

- The ack criteria block (full `## Acceptance` + `## E2E coverage` from the ticket body).
- The resolved e2e-flavor (`backend` | `web` | `mobile`).
- The touched-file scope hint from the plan (Mode A doc, Mode B-a `## Files`, or inferred from `## Steps`).

Expected return: one or more spec files written under the project's e2e test directory (per the flavor's conventions). Each spec MUST start in RED — assertions for behavior that does not yet exist. The skill itself enforces "watch it fail for the right reason" before returning.

If `forge:tdd` returns `BLOCKED` or `NEEDS_CONTEXT` → relay to the user with the original message; halt.

### 6.5.2 — Implementation phase

Continue with Step 6 as documented (delegate to `forge:subagent-driven-development`). The subagents now have a clear definition of done: the new RED specs must turn GREEN. The orchestrator notes that the RED specs from 6.5.1 ARE the contract for this implementation phase, and forwards them as plan context.

### 6.5.3 — GREEN: loop e2e tests via `test-runner` agent

After the implementation phase returns DONE, spawn `test-runner` agent with model **`sonnet`** (mechanical):

- `mode=report` first, `path_filter` = the e2e spec dir for the resolved flavor.
- Pass → continue to Step 7 (lint).
- Fail → spawn `test-runner` again with `mode=fix`, `max_fix_iterations=3`. Then one more `mode=report` to confirm GREEN.
- Still failing → halt with `e2e-tdd-loop-failed: <flavor> specs did not reach GREEN after fix iterations`; do NOT continue to Step 7; do NOT commit.

## Interaction with Step 8.5 (existing e2e runner)

Step 6.5 is the **TDD authoring + green-loop** for the ack-derived behavior. Step 8.5 is the **DB-isolated e2e run** (config-driven by `.claude/e2e.json`) that validates the full e2e suite against the implementation. They are complementary:

- 6.5 writes new specs and confirms they GREEN against the just-written code.
- 8.5 runs the entire e2e suite (including the new specs) under DB isolation as a final regression pass.

If the project has `e2e.json` present, both run. If `e2e.json` is absent but `## E2E coverage required:` is present in the ticket, 6.5 still runs (it does not depend on `e2e.json`); 8.5 is skipped per its existing precondition.

## When NOT to run Step 6.5

- Ticket body has no `## E2E coverage` block at all.
- `## E2E coverage` block says `required: no`.
- FORGE config-only ticket (Step 6 routes to `forge-config-fallback.md`; no test loop applies).
- Mode M ticket (already rejected in Step 2).
