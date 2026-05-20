# Scope resolution

Rules the `forge:review` skill follows to decide what to review and which stack docs to load.

## Diff range

| Invocation              | Range                                                              |
| ----------------------- | ------------------------------------------------------------------ |
| `forge:review` (no arg) | `git diff HEAD` — uncommitted change. If empty: `git show HEAD`.   |
| `forge:review --branch` | `git diff $(git merge-base HEAD origin/main)...HEAD` — full branch.|

If both forms produce an empty diff, exit `0` with `review: nothing to review`.

When `origin/main` does not exist (rare — fresh clone, or non-GitHub remote), fall back in order:

1. `origin/develop` if present.
2. `main` (local).
3. `develop` (local).
4. `git rev-list --max-parents=0 HEAD | tail -1` (repo root commit) as a last resort.

## File list for stack detection

```bash
git diff --name-only <range>
```

Use this list (plus a `ls`-level sweep of repo root) to pick the right platform KB file.

## Stack detection table

Applied in order — first match wins. Used to pick the matching `02_*.md` / `01_*.md` / `04_*.md` file under `plugins/forge/docs/<domain>/`.

| Signal                                                                         | Stack value | KB file suffix          |
| ------------------------------------------------------------------------------ | ----------- | ----------------------- |
| `pubspec.yaml` in repo root                                                    | `flutter`   | `02_mobile_flutter.md`  |
| `package.json` with `react`, `vue`, `svelte`, `next`, `nuxt`, or `solid` dep   | `web`       | `01_web.md`             |
| `package.json` with `express`, `fastify`, `nestjs`, or `koa` dep               | `backend`   | `04_backend.md`         |
| Any `*.go`, `*.rs`, `*.py` (with `pyproject.toml` or `requirements.txt`), `*.rb`, `*.kt`, `*.java` file in changed set | `backend`   | `04_backend.md`         |
| None of the above                                                              | `general`   | (only `00_general.md`)  |

When the stack value is `general`, the agent reads only `00_general.md`. Otherwise it reads `00_general.md` PLUS the platform file.

## MCP detection

The `code-review-graph` MCP is "available" iff BOTH:

1. `.mcp.json` exists in the current working directory AND contains an entry whose key matches `code-review-graph` (substring match is fine).
2. `command -v code-review-graph` returns a path (the CLI is on `PATH`).

If only one signal is present, treat MCP as unavailable. Agents then fall back to direct `Read`/`Grep` against the changed-file list.

## Pass-through to agents

The orchestrator hands each agent:

```yaml
diff: <full unified diff text>
changed_files: [<list of paths>]
project_claude_md: <full text of project CLAUDE.md or plugin CLAUDE.md fallback>
stack: flutter | web | backend | general
mcp_available: true | false
```

Agents MUST treat these as the sole authoritative inputs. They may invoke `Read`/`Grep` only on files mentioned in `changed_files` (or, when MCP is available, those returned by `get_review_context` / `get_impact_radius`).
