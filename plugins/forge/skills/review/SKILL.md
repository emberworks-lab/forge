---
name: review
description: Local 3-agent code review focused on architecture, security, and testing. Read-only — emits structured findings for the EPIC B classifier (no auto-fix).
type: hybrid
---

# Review

Run a structured 3-agent code review across the current diff or branch. Each agent specialises in one domain (architecture, security, testing) and returns JSON findings. The skill itself never edits code — output feeds the downstream classifier.

## Phase 1 — Identify the scope

1. If invoked with `--branch`: resolve base via `git merge-base HEAD origin/main` and use `git diff <base>...HEAD` (see `references/scope-resolution.md` for full rules).
2. Otherwise default: `git diff HEAD`. If empty (clean tree), fall back to `git show HEAD` (review the last commit).
3. If still empty, print `review: nothing to review` and exit 0.
4. Capture the list of changed files via `git diff --name-only <range>` for path-based stack detection.

## Phase 2 — Load shared context

1. Read project root `CLAUDE.md`. If absent, fall back to `plugins/forge/CLAUDE.md`. This is passed verbatim to every agent.
2. Detect stack from the changed-file set (see `references/scope-resolution.md` for the detection table). Result is one of: `flutter`, `web`, `backend`, `general`.
3. Detect MCP availability: look for `.mcp.json` in CWD with a `code-review-graph` entry, AND `command -v code-review-graph` resolves. Record `mcp_available = true|false`. Agents key off this flag.

## Phase 3 — Dispatch three reviewer agents in parallel

Launch all three agents concurrently in a single message. Pass each: the diff, the changed-file list, the shared `CLAUDE.md` text, the detected stack, and `mcp_available`.

- **architecture-focus** — model: `opus`. Prompt blueprint: `references/architecture-focus.md`. KB: `plugins/forge/docs/architecture/`.
- **security-focus** — model: `opus`. Prompt blueprint: `references/security-focus.md`. KB: `plugins/forge/docs/security/`.
- **testing-focus** — model: `sonnet`. Prompt blueprint: `references/testing-focus.md`. KB: `plugins/forge/docs/testing/`.

Each agent MUST return ONLY the JSON object defined in `references/output-format.md` — no prose, no markdown wrapping.

## Phase 4 — Aggregate and report

1. Wait for all three agents. Parse each JSON payload; on parse failure record an empty findings array for that agent and a `parse_error` note.
2. Print one compact human-readable summary block per agent:

   ```
   <agent-name>: <N> high, <M> medium, <K> low
     - [HIGH] <area> · <file:line> — <title>
     - [MED]  <area> · <file:line> — <title>
   ```

3. Append a combined JSON blob (all three agents merged) fenced as `json` for the EPIC B classifier to consume.
4. Do NOT modify any files. Do NOT commit. Do NOT post comments.

## Do NOT

- Flag style, perf-micro, or lint nits — those are `forge:simplify`'s job.
- Block or halt on findings — this skill is advisory.
- Spawn more than the three declared agents per invocation.
