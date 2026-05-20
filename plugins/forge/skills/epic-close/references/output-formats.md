# Output formats

Exact shapes for the DRY epic comment (Step 3c) and the final chat output (Step 4) of `forge:epic-close`.

## DRY epic comment (Step 3c)

Keep it short and factual:

- 3-6 bullets of what was actually delivered (human outcomes, not code changes).
- Note cross-cutting refactors if meaningful.
- For Path B: include `PR: <url>` at the bottom.
- For Path C: frame as "abandoned" / "deferred" with one-line reason.
- **No ticket IDs**, no links to sub-issues (the tracker UI shows them).
- No emojis, no "🎉 shipped!".

Good example (Path A):

```
- Editorial redesign of the dashboard feed rolled out
- Score display standardized on the /10 signal tokens
- Removed legacy per-user generation path
- Pipeline retries now surface to Sentry with stage tags
```

Good example (Path C):

```
Deferred. Manual testing surfaced cross-cutting issues with the new
ranking algorithm under historic-data corpora; revisit after data
backfill (next epic).
```

## Project status update body (Step 3d, optional)

Three short sections, each 2-4 bullets, no ticket IDs:

```
**Delivered**
- bullet
- bullet

**Cross-cutting**
- bullet

**Next**
- bullet
```

## Final chat output (Step 4)

Three or four lines, nothing more:

```
Path: <A merge | B draft PR | C cleanup>
Ultrareview: <ran | skipped | already-ran>
Epic comment: <comment URL if API returns one, else "posted">
Status update: <URL or "skipped">
Docs touched: file1, file2, ...
PR: <URL or "skipped" or "n/a">
Merge: <commit SHA or "n/a">
```

No summary, no celebration, no file-by-file diff.
