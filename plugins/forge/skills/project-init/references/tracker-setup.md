# Tracker setup (step 7.25, also reachable via `--tracker-only`)

Included in the full project-init flow between step 7 and step 7.5; also the exclusive target when invoked as `/project-init --tracker-only`.

**The full flow calls this section once; `--tracker-only` runs only this section.**

## T1. Check for existing tracker.json

Check whether `<project-root>/.claude/tracker.json` exists.

- **Does not exist** → proceed to T2.
- **Exists** and this is `--tracker-only`: ask "Overwrite existing tracker.json? (y/n)"
  - `n` → print "Keeping existing tracker.json unchanged." and exit.
  - `y` → proceed to T2.
- **Exists** and this is a full project-init run: proceed to T2 (the full flow owns the decision to overwrite; step 2.6 already asked about Linear setup).

## T2. Choose a backend

Ask the user:

> "Tracker for this repo? [linear | github | markdown | skip]"

Then branch:

### `linear`

Read `~/.claude/docs/tracker-backends/linear.md`, find the `## setup_interview` section, and execute it step-by-step. That recipe asks which team, which project (optional), and auto-detects the prefix — then writes `tracker.json`.

After `setup_interview` writes `tracker.json`, call `ensure_labels` via the linear recipe to create all required labels (idempotent).

### `github`

Read `~/.claude/docs/tracker-backends/github.md`, find the `## setup_interview` section, and execute it step-by-step. That recipe auto-detects org / repo and asks about a new vs existing GitHub Project — then writes `tracker.json`.

After `setup_interview` writes `tracker.json`, call `ensure_labels` via the github recipe to create all required labels (idempotent).

### `markdown`

Ask: "Where should markdown tickets live? (default: `docs/00_meta/manual-tracker`) — press Enter to accept." Capture the answer; if blank, use `docs/00_meta/manual-tracker`.

Write `<project-root>/.claude/tracker.json`:

```json
{
  "backend": "markdown",
  "markdown": {
    "directory": "<answer>"
  }
}
```

No `ensure_labels` call needed — markdown backend is a no-op for labels.

### `skip`

Write `<project-root>/.claude/tracker.json` silently with the markdown default:

```json
{
  "backend": "markdown",
  "markdown": {
    "directory": "docs/00_meta/manual-tracker"
  }
}
```

No further prompts. No `ensure_labels` call. Continue.

## T3. Confirm

Print to chat:

```
tracker.json created at <project-root>/.claude/tracker.json. Backend = <backend>.
```

If invoked via `--tracker-only`, the skill ends here. If invoked as part of the full project-init flow, return to the next step in the main flow (step 7.5 — Linear automation, or step 8 — Output if Linear was not requested).
