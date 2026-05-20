# PR body template for `forge:pr-create`

The body is always the same shape. `<phrase>` is what `commit_close_phrase(ref, kind=implements)` returns for the active backend (e.g. `Implements EMB-227`, `Closes #42`, `Implements forge-8`).

```markdown
<phrase> (auto-linked via commits)

## Summary

<from epic ## What — paraphrased to 2-3 sentences>

## What's included

- `<SHA>` <commit subject line>
- `<SHA>` <commit subject line>
...

## Manual verification

See the epic comment for the QA checklist:
<URL of epic>

## Stats

<X> commits, <Y> files changed, <Z> insertions(+), <W> deletions(-)
```

Composition notes:

- **Phrase line first.** GitHub's keyword parser scans the body for `Closes #N` and similar; placing the phrase at the top makes the auto-close behavior unambiguous and easy to verify in the PR preview.
- **Summary is paraphrased, not copy-pasted.** The epic's `## What` may contain explanation aimed at the implementer; the PR summary should read for a reviewer. Two or three sentences max.
- **What's included is commit order.** Use `git log <base>..HEAD --oneline` output; one bullet per commit. Don't reorder by ticket; reviewers follow the diff in commit order.
- **Manual verification points at the epic comment.** Don't inline the checklist into the PR body — the comment is the single source of truth and the user already verified it.
- **Stats line is one line.** No emoji, no celebration. The Codex / Claude Code footer is the only branding.

## Worked example (Linear backend, EMB-227)

```markdown
Implements EMB-227 (auto-linked via commits)

## Summary

Editorial redesign of the dashboard feed: shift score display to the /10
signal tokens, remove the legacy per-user generation path, and surface
pipeline retries to Sentry with stage tags.

## What's included

- `a1b2c3d` Implements EMB-228: drop per-user generation hook
- `e4f5g6h` Implements EMB-229: switch dashboard tiles to /10 tokens
- `i7j8k9l` Implements EMB-230: tag Sentry events with pipeline stage
- `m1n2o3p` Refs EMB-227: tidy up imports after token swap

## Manual verification

See the epic comment for the QA checklist:
https://linear.app/example/issue/EMB-227

## Stats

4 commits, 17 files changed, 312 insertions(+), 198 deletions(-)
```

## Worked example (GitHub backend, #42)

```markdown
Closes #42 (auto-linked via commits)

## Summary

...
```

The only thing that changes between backends is the phrase line — the rest of the body is backend-agnostic.
