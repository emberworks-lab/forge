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
