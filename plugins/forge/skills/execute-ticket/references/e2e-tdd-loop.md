# Step 6.5 — E2E TDD loop (when ack opts in)

Activated when the ticket body (fetched in Step 1) contains an `## E2E coverage` block whose `required:` value is `yes`, `web`, `backend`, or `mobile`. Absent or `required: no` → skip the whole step.

## Detection

Parse the ack section. The line shape is:

```markdown
## E2E coverage
required: <yes | web | backend | mobile>
scope: <prose>
```

- `required: yes` → use the project's **default** e2e flavor (see qualifier resolution below). Alias for `backend` when `platforms[]` is missing.
- `required: web` → web e2e flavor (Playwright). Specs go to `tests/e2e/<feature-slug>.e2e-web.spec.ts`; GREEN loop runs via `forge:e2e-web --run`.
- `required: backend` → backend HTTP / API e2e flavor. Explicit alias for `yes` on backend-only projects. GREEN loop runs via `forge:e2e --run` (DB-isolated wrapper around the `test-runner` agent).
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

Per-flavor spec target:

- `backend` → project's backend e2e test dir (per `.claude/e2e.json` or framework default).
- `web` → `tests/e2e/<feature-slug>.e2e-web.spec.ts` (Playwright). Feature-slug derives from the ticket title (kebab-case).
- `mobile` → halt; no consumer wired yet.

Expected return: one or more spec files written under the resolved path. Each spec MUST start in RED — assertions for behavior that does not yet exist. The skill itself enforces "watch it fail for the right reason" before returning.

If `forge:tdd` returns `BLOCKED` or `NEEDS_CONTEXT` → relay to the user with the original message; halt.

### 6.5.2 — Implementation phase

Continue with Step 6 as documented (delegate to `forge:subagent-driven-development`). The subagents now have a clear definition of done: the new RED specs must turn GREEN. The orchestrator notes that the RED specs from 6.5.1 ARE the contract for this implementation phase, and forwards them as plan context.

### 6.5.3 — GREEN: loop e2e tests (per-flavor consumer)

After the implementation phase returns DONE, dispatch the GREEN loop based on resolved flavor.

**Web flavor** (`required: web`): invoke `forge:e2e-web --run` with `cwd` = project root, `path_filter` = the spec dir / file(s) written in 6.5.1, `mode=report` first. The skill dispatches `test-runner` (model: **`sonnet`**) with `type=e2e-web` internally.

- Pass → continue to Step 7 (lint).
- Fail → invoke `forge:e2e-web --run` again with `mode=fix` (skill caps `max_fix_iterations=3`). Then one more `mode=report` to confirm GREEN.
- Still failing → halt with `e2e-tdd-loop-failed: web specs did not reach GREEN after fix iterations`; do NOT continue to Step 7; do NOT commit.

**Backend flavor** (`required: backend` or `yes`-resolved-to-backend): invoke `forge:e2e --run` with `cwd` = project root, `path_filter` = the e2e spec dir/file(s) written in 6.5.1, `mode=report` first. The skill provisions a throwaway DB, dispatches `test-runner` (model: **`sonnet`**) against it, and tears down.

- Pass → continue to Step 7 (lint).
- Fail → invoke `forge:e2e --run` again with `mode=fix` (skill caps `max_fix_iterations=3`). Then one more `mode=report` to confirm GREEN.
- Still failing → halt with `e2e-tdd-loop-failed: backend specs did not reach GREEN after fix iterations`; do NOT continue to Step 7; do NOT commit.

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
