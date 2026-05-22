# Output summary (step 8)

Print this block to chat when the full project-init flow completes (non-Flutter path; Flutter has its own output in `references/flutter-scaffolder.md` step 4A-flutter.5.4).

```
Project initialized: <project name>

Created:
- CLAUDE.md
- .claude/skills/ (<N> kit-* templates copied)
- .claude/settings.json
- .claude/tracker.json (backend: <backend>)
- docs/00_meta/ (if requested)
- Linear project + P0/P1 epics (if requested — see step 7.5 summary above)

Stack: <stack summary>
Linear: <prefix> / <team>

Next:
1. Review CLAUDE.md and adjust Mandatory rules to your project.
2. Complete manual-setup tickets under P0 — Bootstrap (if Linear was set up).
3. Run /create-epic to draft your first real P1 epic.
4. Run /project-init again later if you want to add more kit-* skills.
```

## Variants

- **Linear skipped:** drop the Linear bullet from `Created:` and the corresponding `Next` step.
- **Docs scaffold skipped:** drop the `docs/00_meta/` bullet.
- **`--tracker-only` run:** do NOT print this block; tracker setup ends with its own confirmation line (`references/tracker-setup.md` T3).
- **Polyrepo (`structure == "polyrepo"`):** add a `Repos created:` section listing the general repo + each platform repo (`<org>/<name>`), and a clone hint:
  ```
  Repos created:
  - <org>/<general-repo>   (general — docs + tracker)
  - <org>/<platform-repo>  (<platform name>)
  ...

  New machine:
    gh repo clone <org>/<general-repo> && cd <general-repo> && ./scripts/clone-all.sh
  ```
