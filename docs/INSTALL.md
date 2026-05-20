# forge — Installation

## Prerequisites

- Claude Code CLI (latest stable; plugin marketplace support required)
- GitHub CLI (`gh`) — required by tracker-pipeline skills
- `git` — required for branch and commit skills
- `python3` — required to regenerate `docs/SKILL-INDEX.md`

## 1. Add the plugin

```
/plugin marketplace add emberworks-lab/forge
```

## 2. Install the plugin

```
/plugin install forge@emberworks-lab
```

## 3. Verify

```
/forge:hello
```

Expected output: a short confirmation that the forge plugin is installed and reachable.

## 4. Per-project setup (optional)

Run `forge:project-init` at the root of any project to scaffold `CLAUDE.md`, copy stack-specific `kit-*` skills, configure `tracker.json`, and optionally set up a Linear project.

```
/forge:project-init
```

Note: `forge:project-init` is available in the plugin but the `--tracker-only` flag assumes a tracker backend is already chosen. The skill will interview you on first run.

## code-review-graph MCP

`code-review-graph` is an **optional** dependency that builds a persistent knowledge graph for code reviews. Skills that use it check whether the MCP is available before invoking its tools; if it is absent, they fall back to direct file reading.

### Install

```
pipx install code-review-graph
```

Requires `pipx` (install via Homebrew: `brew install pipx && pipx ensurepath`).

### Register with Claude Code

Run from any project root where you want graph-aware reviews:

```
code-review-graph install --platform claude-code
```

This writes a project-local `.mcp.json` that registers the MCP server, injects usage instructions into `CLAUDE.md`, installs four project skills (`debug-issue`, `explore-codebase`, `refactor-safely`, `review-changes`), and adds a `.claude/settings.json` hook that keeps the graph up to date after every file edit.

### MCP tools provided

| Tool | Purpose |
| ---- | ------- |
| `detect_changes` | Risk-scored analysis of a diff |
| `get_review_context` | Token-efficient source snippets for review |
| `get_impact_radius` | Blast-radius of a change (dependents, callers) |
| `get_affected_flows` | Execution paths impacted by a change |
| `query_graph` | Trace callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Find functions/classes by name or keyword |
| `get_architecture_overview` | High-level codebase structure |
| `list_communities` | Logical modules detected by community analysis |

### Build the graph (first run)

```
code-review-graph build
```

After the initial build, the `PostToolUse` hook keeps the graph incrementally updated on every edit.

### Verify

Restart Claude Code after install. The `code-review-graph` server should appear in the MCP tool listing. Smoke-test with:

```
code-review-graph status
```

## Troubleshooting

**Plugin not visible after install**
- Restart the Claude Code session (close and reopen the terminal).
- Run `/plugin list` and confirm `forge` appears.

**Skills not resolving (`forge:hello` returns unknown command)**
- Confirm the install step completed without errors.
- Run `/plugin install forge@emberworks-lab` again; installs are idempotent.

**Hooks not firing**
- Skills that rely on hooks (e.g., pre-commit linting) require `settings.json` entries. Run `/forge:project-init` to configure them for the current project.
- Check `.claude/settings.json` in the project root for a `hooks` block.

**`gh` auth errors from tracker skills**
- Run `gh auth login` and complete GitHub authentication.
- Confirm with `gh auth status`.

For other issues, open a ticket at [github.com/emberworks-lab/forge/issues](https://github.com/emberworks-lab/forge/issues).
