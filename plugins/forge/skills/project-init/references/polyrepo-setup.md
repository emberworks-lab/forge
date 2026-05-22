# Polyrepo repo creation (step 7.9, polyrepo only)

Runs **only** when the interview recorded `structure == "polyrepo"`. Turns the
on-disk multi-platform tree (built by `scaffolding-logic.md` exactly as for
`sub-folder`) into separate git repos, plus the general/parent repo.

**Placement:** last step before output (after 7.8). By now docs (6/6.5),
settings (7), tracker.json + GitHub Project (7.25), and the e2e / design / API
markers (7.6–7.8) are all written, so each repo's initial commit captures the
fully-scaffolded tree.

**Consent:** choosing `polyrepo` in interview step 2c is the explicit consent the
SKILL.md "do not `git init` without asking" rule requires. No extra prompt.

`gh` auth / name-conflict edge cases: handle exactly as
`references/flutter-scaffolder.md` 4A-flutter.5.2 (skip gracefully on
unauthenticated, ask the user on a repo-name conflict, continue on other errors).

## P1. General/parent repo

In the repo root (the project / parent folder):

```bash
# .gitignore: ignore every platform path so children stay independent
for p in <platforms[].path ...>; do printf '%s/\n' "$p" >> .gitignore; done
git init -b main
git add .
git commit -m "Initial commit: <project> general repo (docs + tracker)" \
  -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
gh repo create "<org>/<general-repo-name>" --private --source=. \
  --description="<project> — shared docs + tracker"
git push -u origin main
```

The `.gitignore` MUST list every `platforms[].path` (e.g. `backend/`, `mobile/`)
so the platform repos remain independent clones nested in the general repo's
working tree.

## P2. Per-platform repos

For each `p` in `platforms[]`, inside `<p.path>/` (already scaffolded):

```bash
cd "<p.path>"
git init -b main
git add .
git commit -m "Initial commit: <p.name> via /project-init" \
  -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
gh repo create "<org>/<p.repo>" --private --source=. \
  --description="<project> — <p.name>"
git push -u origin main
cd "<repo_root>"
```

The child `.claude/tracker.json` (`parent_path: "../"`) and per-platform
`CLAUDE.md` written during scaffolding are part of this initial commit.

## P3. Clone / pull scripts

Copy `plugins/forge/skill-templates/_common/scripts/{clone-all,pull-all}.sh` into
`<repo_root>/scripts/`, `chmod +x` both, and include them in the general repo's
commit (P1). They read the root `tracker.json` (`github.org` +
`platforms[].repo`) — there is **no separate manifest file**.

New-machine workflow:

```bash
gh repo clone <org>/<general-repo-name>
cd <general-repo-name>
./scripts/clone-all.sh
```

## P4. Link repos to the GitHub Project + labels

The GitHub Project was created at step 7.25 (it does not need a repo to exist).
Now that the repos exist, complete the wiring:

1. Link the general repo and every platform repo to the project via
   `linkProjectV2ToRepository` (see `plugins/forge/docs/tracker-backends/github.md`).
2. Run `ensure_labels` (github recipe) in the **general repo** (epics live there)
   and in **each platform repo** (sub-issues route there via area tags).

## Hard rules

- Run only when `structure == "polyrepo"`. Skip for single-platform,
  `sub-folder`, `monorepo`, and `--tracker-only`.
- The general repo's `.gitignore` MUST cover every `platforms[].path` before its
  initial commit — otherwise the platform clones get tracked by the parent.
- Never duplicate `docs/` into a platform repo. Shared docs live only in the
  general repo (`scaffolding-logic.md` already enforces this on disk).
- Do not mutate anything under `plugins/forge/skill-templates/` — copy the
  scripts, never edit the sources.
