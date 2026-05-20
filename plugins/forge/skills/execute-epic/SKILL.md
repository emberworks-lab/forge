---
name: execute-epic
description: Orchestrate execution of a tracker epic — branch setup, manual-setup gate, dependency-ordered story execution via subagents, per-ticket commits, aggregated manual test cases on the epic.
type: hybrid
---

# Execute Epic

Trigger: `/execute-epic EMB-227`, "виконай епік EMB-227", or implicit when on a feature branch with no arg (detect epic from branch name).

At every tracker-touching step: read `<project>/.claude/tracker.json` → `backend`; execute the matching recipe section from `plugins/forge/docs/tracker-backends/<backend>.md`. Fallback: if `tracker.json` is missing, fall back to current Linear-MCP behavior — phased out in a future cleanup epic.

## Core principles

- **Orchestration only.** Spawn subagents for code work; main session owns tracker, git, ordering.
- **Manual-setup tickets block execution.** Any unclosed `exec:manual` sub-issue halts the orchestrator. (Recognize both old `manual-setup` and new `exec:manual` during the transition.)
- **Per-ticket commit by default.** Invoking this skill = consent for auto-commit per ticket. Explicit exception to the "no auto-commit" rule.
- **Halt on failure.** Lint or test failure on any ticket halts the whole epic; user resumes manually.
- **Manual testing happens AFTER execution.** Don't create a PR; aggregate manual cases on the epic, let user verify, then `forge:pr-create`.

## Inputs

Epic ticket ID (or `--from-branch`). Optional flags: `--parallel`, `--dry-run`, `--start-from <ticket-id>`.

## Flow

### 1. Load epic + sub-issues

**get_ticket** for the epic (with relations). **list_subissues** for all sub-issues. In parallel: read repo `CLAUDE.md`. For each sub-issue extract `id`, `title`, `state`, `labels`, `body`. Detect mode (A / B-a / B-b / B-c / M) per `plugins/forge/docs/conventions/tracker-tickets.md`. Detect executor: `exec:opus` / `exec:sonnet` (recognize old `model:opus` / `model:sonnet`). Manual-setup: `exec:manual` (recognize old `manual-setup`).

### 1.5. Mark epic In Progress

**set_project_status via backend recipe** with `ref=<epic_ref>`, `status="In Progress"`. Non-blocking; skip for markdown. Per-sub-issue status updates happen inside `forge:execute-ticket`. Epic stays In Progress until `forge:epic-close` runs.

### 2. Manual-setup gate

Filter `exec:manual` (or old `manual-setup`) sub-issues in non-DONE state. List with title + URL; tell user "Виконай ці кроки вручну і закрий тікети в трекері. Скажи 'ready' коли готово." WAIT. On "ready", re-fetch each and verify DONE; if any still open, tell user "EMB-X still open; fix that first" and re-wait. If all done → continue. If none exist, skip.

### 3. Branch setup

Resolve `feature/<prefix>-<epic_number>-<slug>` (slug = lowercased+hyphenated epic title; strip phase prefix). `git rev-parse --abbrev-ref HEAD`. If matches → continue. If on `develop` / `main` / different feature branch, prompt and (on `y`) `git status --short` then `git checkout develop && git pull && git checkout -b <branch>`. If branch exists locally but not checked out, ask "Switch?".

### 3.5. E2E setup gate

Once, in the main session (NOT a subagent), invoke `forge:e2e`'s setup-check. `configured` / `not-applicable` → continue silently. `needs-setup` → show the prompt and act. This gate runs **once per epic**. Per-sub-issue `forge:execute-ticket` subagents MUST NOT re-run it.

### 3.6. Graph refresh (preflight)

Once, in the main session (NOT a subagent), invoke `forge:graph-refresh` (incremental). This ensures the code-review graph is fresh before the dispatch loop starts.

- Graceful skip if `code-review-graph` is not installed or no `.mcp.json` exists — the underlying skill handles this automatically.
- This step runs **once per epic**. Per-sub-issue `forge:execute-ticket` subagents MUST NOT re-run `forge:graph-refresh`.

### 4. Build execution plan

Topological sort by `## Depends on` blocks and `blockedBy` relations. Identify parallel groups via file-scope heuristics from `## What` / `## Steps` / `## Files`. When in doubt → sequential. **Parallel safety checklist** REQUIRED if `--parallel` — see `references/parallel-safety.md`. Print the plan compactly (see `references/output-formats.md` for exact shape). Ask "ОК, поїхали? або щось правимо?". If `--dry-run`, stop here.

### 5. Execute story by story

For each step, spawn one subagent per ticket via the Agent tool using the curated prompt (see `references/subagent-prompt.md`). Use **`opus`** or **`sonnet`** model per the ticket's executor label. Wait for result; expect `done | halted`. On `done`, verify commit with `git log -1`. On `halted`, print reason, STOP, tell user "EMB-X halted on <reason>. Resume with `/execute-epic <epic> --start-from <next-ticket>`."

For a parallel group: spawn N subagents in ONE Agent call block. Each gets its own curated prompt. Wait for ALL. Process commits in deterministic order (ticket ID ASC). Any halt → halt the whole epic.

### 6. Final lint + test pass

After all sub-issues done, in main session (NOT a subagent), spawn the `linter-runner` agent (`mode=report`, no path filter) and the `test-runner` agent (`mode=report`, full suite). Both run with **`sonnet`** model.

Read agent outputs in this turn (Iron Law: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE). If both pass → continue. If either fails — do NOT auto-fix at this level. Halt and tell user.

### 6.5. Verification gate before completion claim (REQUIRED)

Invoke `forge:verification-before-completion` (or apply its Iron Law inline): confirm fresh evidence of clean lint + pass tests before proceeding.

### 7. Aggregate manual test cases on epic

Fetch comments from each sub-issue (manual-cases blocks posted by `forge:execute-ticket`). Compose ONE block per the template in `references/output-formats.md`. **post_comment via backend recipe** with `ref=<epic_ref>`.

### 8. Output

Print the final summary to chat per `references/output-formats.md`.

## Do NOT

- Push at the orchestrator level after all tickets done. Per-ticket push during the dispatch loop is fine (and required by `execute-ticket` + the curated subagent prompt). Final PR push happens via `forge:pr-create`, not here.
- Call `forge:epic-close` automatically. User verifies manual cases first.
- Change tracker status of any ticket. Magic-word commits + merge handle this.
- Auto-fix integration failures in step 6.
- Skip the manual-setup gate if any such tickets are open.
- Parallelize without `--parallel`. Sequential by default.
- Have subagents re-run `forge:graph-refresh` — Step 3.6 already handled it once at the start of the epic.

## Edge cases + resumability

See `references/edge-cases.md`. Resumable at every ticket boundary. Halted ticket has no commit; user inspects/reverts. Resume via `--start-from <next-ticket-id>` or fix manually + `forge:commit` and resume.
