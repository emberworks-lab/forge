# forge plugin — policy

Plugin-level policy that all `forge:*` skills follow. The headline rules are summarized here for quick reference; the authoritative full content lives in `forge:writing-skill` and its references.

When writing or refactoring a skill in this plugin, invoke `forge:writing-skill` and run `bash plugins/forge/skills/writing-skill/scripts/audit.sh <path/to/SKILL.md>` before opening a PR. Exit 0 = ready.

## Composition principle

Skills follow code composition rules: single responsibility, master composes via explicit invocation (no inlining), low coupling, extract when reused (not before).

> Full details: [`skills/writing-skill/references/composition-principle.md`](skills/writing-skill/references/composition-principle.md).

## Type taxonomy

Every SKILL.md front-matter declares `type: minimal | fundamental | hybrid`:

- **minimal** — ≤ 80 lines, flexible one-shot, no decision tree, no `references/`
- **fundamental** — ≤ 300 lines + `references/`, rigid foundational workflow cited by other skills
- **hybrid** — ≤ 120 lines + supporting files (default)

> Full details: [`skills/writing-skill/references/type-taxonomy.md`](skills/writing-skill/references/type-taxonomy.md).

## Subagent model declaration

Skills that spawn subagents MUST name the model inline: `sonnet` (mechanical) or `opus` (creative/critical). The `haiku` model is not used in this plugin.

> Full details: [`skills/writing-skill/references/subagent-model-declaration.md`](skills/writing-skill/references/subagent-model-declaration.md).

## Credit attribution

Adapted skills carry an `inspired-by` front-matter block with `author`, `repo`, `skill`, and `relation` (one of `adapted | concept | structure`). No 1:1 copies — every adapted skill is rewritten in this plugin's voice.

> Full details: [`skills/writing-skill/references/credit-attribution.md`](skills/writing-skill/references/credit-attribution.md).

## Audit before PR

The slim audit checklist mechanizes structural checks (front-matter, line caps, dangling references, forbidden patterns) via `audit.sh`:

> Checklist: [`skills/writing-skill/references/slim-audit-checklist.md`](skills/writing-skill/references/slim-audit-checklist.md)
> Script: [`skills/writing-skill/scripts/audit.sh`](skills/writing-skill/scripts/audit.sh)

## Code review architecture

Two-axis review: **`forge:review`** (local, pre-PR) + **`code-review` plugin** (cloud, post-PR). Code-style and performance are covered by linter + `forge:simplify-branch` + the `code-simplifier` plugin — no dedicated reviewer.

### Axis 1 — `forge:review` (local, BEFORE PR)

- EPIC E #29 / `plugins/forge/skills/review/`
- Dispatches 3 parallel agents: **architecture-focus** (opus), **security-focus** (opus), **testing-focus** (sonnet).
- Each agent consults a domain KB under `plugins/forge/docs/<domain>/` and the project `CLAUDE.md`.
- Each agent returns a JSON payload (schema: `skills/review/references/output-format.md`). No file edits; no commits.
- Wired inside `forge:epic-close` Step 3a.4 (after `forge:simplify-branch` and `forge:graph-refresh`). Combined JSON feeds the Opus classifier in `skills/epic-close/references/classifier-prompt.md`.
- Can also be run standalone: `forge:review --branch`.

### Axis 2 — `code-review` plugin (Anthropic, AFTER PR)

- Upstream Anthropic plugin — separate from the removed forge reviewers (see Decision context below). Dispatches 5 parallel Sonnet agents on the GitHub PR diff; Haiku scores confidence per finding.
- Posts inline comments directly on the GitHub PR.
- Triggered by user typing `/code-review <PR#>` in the chat after `forge:pr-create` opens the PR.
- Wired in `forge:epic-close` Path B Step 6 (`skills/epic-close/references/path-details.md`).
- Non-blocking: if the plugin is absent or fails, merge can still proceed.

### `code-review-graph` MCP integration

- EPIC E #30 / `plugins/forge/skills/graph-refresh/`
- `forge:graph-refresh` is a thin wrapper around `code-review-graph build --incremental`. Safe to call anytime — idempotent.
- Invoked at the start of `forge:execute-epic` Step 3.6 (once per epic, before the dispatch loop).
- Invoked again inside `forge:epic-close` Step 3a.3 (before Step 3a.4 local review runs).
- Initial full graph is built by `forge:project-init` Step 7.1 alongside writing `.mcp.json` directly — **NOT** via `code-review-graph install --platform claude-code` (destructive; see `docs/INSTALL.md` warning).
- `forge:review` agents consult MCP tools (`get_review_context`, `get_impact_radius`, `detect_changes`) when `mcp_available = true`; fall back to direct file reading otherwise.
- Installation (once per machine): `pipx install code-review-graph` — see `docs/INSTALL.md`.

### Decision context (why 5-domain reviewers were removed)

- The previous setup had 6 skills: architecture-reviewer, security-reviewer, code-style-reviewer, performance-reviewer, testing-reviewer, review-aggregator. Recorded 0 invocations in 4 months.
- Code-style and performance are now covered by linter + `forge:simplify-branch` + `code-simplifier` plugin.
- Cleanup tracked in EPIC E #7 / GitHub issue #35.

### Cross-links

- `forge:epic-close` Steps 3a.3 / 3a.4 / classifier hand-off are being further redesigned by EPIC B #2 / #3 — see the GitHub issue tracker for current state. This section does not restate that plan.
