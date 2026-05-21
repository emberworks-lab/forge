---
name: execute-ticket
description: Execute a single tracker ticket — read it, plan, implement using project `/kit-*` skills if any, run linter + tests, generate manual test cases, post comment.
type: hybrid
---

# Execute Ticket

Trigger: `/execute-ticket EMB-228`, "виконай тікет EMB-228", or invoked from `forge:execute-epic` per sub-issue.

At every tracker-touching step: read `<project>/.claude/tracker.json` → `backend`; execute the matching recipe section from `plugins/forge/docs/tracker-backends/<backend>.md`. Fallback: if `tracker.json` is missing, fall back to current Linear-MCP behavior — phased out in a future cleanup epic.

## Core principles

- **The ticket body is the prompt.** Don't re-derive intent — read what's there.
- **Reuse existing patterns.** If the project has `/kit-*` skills, prefer them over inline scaffolding.
- **Lint + test before claiming done.** Halt if either fails after fix attempts.
- **Generate manual test cases as a tracker comment** so the user can verify by hand.
- **Don't auto-commit when invoked standalone.** When invoked by `forge:execute-epic`, that orchestrator handles commit.

## Inputs

Ticket ID (required). Optional flags: `--no-commit` (default standalone), `--commit` (default from execute-epic), `--branch <name>`.

## Flow

### Step 0 — Critical plan review (REQUIRED)

Read the body fully. Look for BLOCKERS: missing dependencies; conflicting requirements (Step 3 vs Acceptance); vague steps without code/exact paths; references to types/functions/modules not in any task and not in codebase; unverifiable acceptance ("make it better"); Mode B-a body without `## Files` or without bite-sized tasks. If clean → proceed. If concerns → halt with `EMB-X plan review — N concerns: 1. <concern> — <where>`, then "Resolve before I start, or tell me to proceed despite this."

For FORGE config-only tickets (target `~/.claude/`), the "code/exact paths" check becomes "exact text blocks + exact target file paths".

### 1. Load ticket + project context

In parallel: **get_ticket via backend recipe**; read repo `CLAUDE.md`; read `plugins/forge/docs/conventions/tracker-tickets.md` if body shape is unclear.

### 1.5. Mark ticket In Progress

After plan review, BEFORE first code change: **set_project_status via backend recipe** with `status="In Progress"`. Non-blocking; skip for markdown.

### 2. Detect mode + reject if not executable

Mode markers: A → `## References` with `docs/0X_*.md`; B-a → `## Steps` numbered list; B-b → `## Interview the user`; B-c → `## Read first`; M → `## User actions` + `exec:manual` label (or old `manual-setup`).

**Mode M tickets are NOT executable by an agent.** Tell user "Ticket <ref> is `exec:manual` — you must complete it manually. I'm waiting." Exit cleanly. Don't change status; don't commit.

### 3. Pre-flight git check

`git rev-parse --abbrev-ref HEAD`, `git status --short`. Resolve `feature/<prefix>-<epic_number>-<slug>`. If matches → proceed. If branch missing → STOP, tell user "Branch `<name>` not found. Create manually OR run `/execute-epic <epic>` to bootstrap." If branch exists but not checked out → ask "Switch to `<name>`?". If working tree dirty: from `forge:execute-epic` → halt; standalone → ask user "Commit, stash, or abort?"

### 3.5. E2E setup gate

Standalone only: invoke `forge:e2e`'s setup-check. `configured` / `not-applicable` → continue silently. `needs-setup` → show the prompt and act. From `forge:execute-epic` → skip entirely (the epic orchestrator ran this once at its start).

### 4. Mode-specific preparation

Mode A: read the referenced `docs/0X_*.md` fully (the doc IS the plan). Mode B-a: extract `## Steps`. Mode B-b: ask interview questions before any code work; wait for answers. Mode B-c: read all files in `## Read first`.

### 5. Determine which skills apply

Read project `CLAUDE.md > Skills`. Match the work against available `/kit-*` skills; use them when applicable. If the ticket spans multiple, use them in dependency order (drift table → feature scaffold → l10n strings).

### 6. Implement

Detect ticket type and delegate. For FORGE-N config-only tickets → ad-hoc subagent pattern in `references/forge-config-fallback.md` (no TDD, no lint, no test, no commits). For standard project tickets, first check Step 6.5 (e2e TDD opt-in). Then delegate the implementation phase to `forge:subagent-driven-development`, which dispatches **`opus`** or **`sonnet`** per-task implementer + reviewer subagents internally. Full delegation contract: see `references/implement-delegation.md`. The orchestrator stays in charge of tracker, git, and commit semantics. Architecture + editing rules apply in both modes — follow `CLAUDE.md > Mandatory rules` strictly; read each file before editing; minimal targeted changes; no "while I'm here" refactors; run codegen after schema/source change.

### 6.5. E2E TDD loop (if ack opts in)

Detect: ticket body has `## E2E coverage` with `required: yes | web | backend | mobile`. Absent / `required: no` → skip. Resolve flavor against `<project>/.claude/tracker.json` `platforms[]` (default `backend` when absent). RED phase: spawn `forge:tdd` with model **`opus`** to author e2e spec files from the ack block (web → `tests/e2e/<slug>.e2e-web.spec.ts`). Implementation (Step 6 delegate) makes them GREEN. After Step 6 returns, GREEN loop dispatches per flavor: **web** → `forge:e2e-web --run` (which dispatches `test-runner` sonnet with `type=e2e-web`); **backend** → raw `test-runner` agent **`sonnet`**. Both: `mode=report` then `mode=fix` (max 3). Still failing → halt; do NOT proceed to Step 7. Full contract + interaction with Step 8.5: see `references/e2e-tdd-loop.md`.

### 7. Run linter

Spawn `linter-runner` agent with **`sonnet`** model, `mode=fix`, `path_filter` = touched files. If clean → continue. If still errors after auto-fix, apply manual fixes (max 2 attempts). Still failing → halt + report; do NOT commit.

### 7.5. Run typecheck / build (if defined)

Read `CLAUDE.md > ## Essential commands`. Look for `Typecheck` row (preferred) or `Build`. Neither → skip. If found, run via Bash. Pass → continue. Fail → halt; do NOT run tests; do NOT commit. No auto-fix iteration here.

### 8. Run tests

Spawn `test-runner` agent with **`sonnet`** model, `mode=report` first, `path_filter` = relevant test dir. Pass → continue. Fail → spawn again with `mode=fix`, `max_fix_iterations=3`; then one more `mode=report`. Still failing → halt + report; do NOT commit.

### 8.5. Run e2e (if opted in)

If `<project>/.claude/e2e.json` exists with `db_isolation` other than `"none"`: invoke `forge:e2e <ticket-ref>`. On success → continue. On halt → halt `forge:execute-ticket`; do NOT commit; do NOT mark done.

### 9. Generate manual test cases

Compose a `## Manual test cases` tracker comment: 3-5 bullets, action-oriented, runnable in 5-10 minutes by a human. **post_comment via backend recipe**. Template + trailing automated summary line: see `references/output-formats.md`.

### 10. Verification gate (REQUIRED)

Invoke `forge:verification-before-completion` against the about-to-claim DONE state — it owns the Iron Law gate (fresh lint + test evidence gathered in this turn). Proceed to commit and DONE only on confirmed-clean. For FORGE config-only tickets the gate narrows to: open the file you just edited and confirm the change is present in this turn.

### 11. Commit (if `--commit`)

Default NO COMMIT when standalone. When invoked from `forge:execute-epic` (`--commit` implied): stage + commit. **commit_close_phrase via backend recipe** with `kind=implements`. Message: `<phrase>: <ticket title lowercase>` then `Co-Authored-By: <model footer per plugins/forge/docs/conventions/git-workflow.md>`. Push the branch (first push of a new branch needs `--set-upstream`): `git push -u origin "$(git rev-parse --abbrev-ref HEAD)" 2>&1 | tail -1`. If push fails, warn and continue.

### 11.5. Mark ticket Done

**set_project_status via backend recipe** with `status="Done"`. Non-blocking; skip for markdown. GitHub auto-closes the issue on PR merge anyway.

### 12. Output

See `references/output-formats.md` for DONE / NO-COMMIT / HALTED summaries.

## Subagent status handling

Expect one of: `DONE`, `DONE_WITH_CONCERNS` (correctness → address; else note in manual cases), `NEEDS_CONTEXT` (provide + re-dispatch), `BLOCKED` (triage: context / reasoning / too-large / wrong-plan).

## Do NOT

- Commit or push without `--commit` (that's `forge:pr-create` or the user); never change ticket status via API — magic-word commit + merge does it.
- Run the FULL test suite every time. Use `path_filter`. Full-suite is for `forge:execute-epic`'s final pass.
- Interpret an `exec:manual` (or old `manual-setup`) ticket as executable.
- Edit files outside the ticket's scope (mention tangential issues in manual cases); never invent acceptance criteria — ask if `## Acceptance` is missing.

## Edge cases + loop integration

See `references/edge-cases.md`.
