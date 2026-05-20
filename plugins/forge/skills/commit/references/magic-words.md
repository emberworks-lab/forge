# Magic words reference for `forge:commit`

## Per-backend phrase table

`commit_close_phrase(ref, kind)` returns:

| Backend | `implements` | `fixes` | `refs` |
|---|---|---|---|
| `linear` | `Implements <PREFIX>-<N>` | `Fixes <PREFIX>-<N>` | `Refs <PREFIX>-<N>` |
| `github` | `Closes #<N>` | `Fixes #<N>` | `Refs #<N>` |
| `markdown` | `Implements <slug>` | `Fixes <slug>` | `Refs <slug>` |

Notes:

- `implements` and `fixes` auto-close tickets on PR merge to the default branch (Linear and GitHub).
- `refs` links without changing status — use for WIP, partial work, docs, or ticket that spans multiple PRs.
- For the GitHub backend, `implements` maps to `Closes #N` — GitHub has no `Implements` keyword; `Closes` is the canonical auto-close word.
- Markdown has no remote state — the phrase shape is kept so `git log --grep` works across repos.

## Magic words effect

| Type | Words | Effect on merge to default branch |
|---|---|---|
| Auto-closing | `Implements`, `Fixes`, `Closes` | Links + moves ticket to "Done" (Linear) or closes the GitHub issue |
| Non-closing | `Refs` | Links only — no status change |

## Examples

```
Implements EMB-42: add Reddit API integration with rate limiting
Fixes EMB-123: resolve auth redirect loop on Vercel
Refs DES-5: update color tokens to match design system
Closes #88: add reddit feed ingestion
Refs #90: partial work on comment ranking
Implements forge-8/001-tracker-contract: add tracker pluggability README
Implements EMB-42, EMB-43: split combat simulator into engine + UI shell
```

## Rubric for choosing the kind

When the change is ambiguous, prefer `refs` over `implements` — leaving the ticket open is cheap; auto-closing a half-done ticket is annoying. The user can promote a `refs` commit to `implements` on the next commit if they discover the work is actually complete.
