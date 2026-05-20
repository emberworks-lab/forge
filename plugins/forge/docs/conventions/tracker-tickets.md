# Tracker tickets — modes, label model, conventions

Universal across projects and all tracker backends. Consumed by `/create-epic`, `/create-ticket`, `/execute-epic`, `/execute-ticket`.

For backend-specific recipe details (how to create, read, comment, and commit-link tickets in each system), see `~/.claude/docs/tracker-backends/` — start with `README.md` for the contract overview, then the backend recipe file that matches your project's `tracker.json`.

---

## Modes

A ticket body has exactly one of these shapes:

| Mode | When | Body sections |
|---|---|---|
| **A — doc-backed** | Plan exists at `docs/0X_*.md` (or similar) | `## What`, `## Acceptance`, `## References` (points at doc), `## Depends on?` |
| **B-a — inline** | Work fully scoped in chat, no separate doc | `## What`, `## Steps`, `## Acceptance`, `## Depends on?` |
| **B-b — interview** | Scope is partial; executor must ask user before coding | `## What`, `## Interview the user`, `## Acceptance` |
| **B-c — read-first** | Scope depends on existing code | `## What`, `## Read first`, `## Acceptance` |
| **M — manual-setup** | User-only manual prerequisite (no code work) | `## What`, `## User actions`, `## Acceptance` |

`## Tests` block — optional, only for tickets where testing scope is non-obvious (property-based, golden, integration, multi-mock). Default test discipline lives in `~/.claude/docs/testing/<platform>.md`.

These mode shapes are tracker-agnostic — they describe ticket structure, not tracker semantics. A Mode B-a ticket looks the same whether it lives in Linear, GitHub Issues, or a markdown file.

---

## Label model

Every ticket gets **exactly 2 labels — one from each axis**.

### Type axis

| Label | Meaning |
|---|---|
| `epic` | Parent container for a body of work; created by `/create-epic` |
| `story` | Sub-issue of an epic; default type for parent-linked tickets |
| `task` | Standalone ticket not under an epic; default for `/create-ticket` with no parent |
| `bug` | User-reported defect; not produced by automated flows |

### Executor axis

| Label | Meaning | Old label replaced |
|---|---|---|
| `exec:opus` | Run by Claude Opus via `/execute-ticket` or `/execute-epic` | `model:opus` |
| `exec:sonnet` | Run by Claude Sonnet via `/execute-ticket` or `/execute-epic` | `model:sonnet` |
| `exec:manual` | User must complete this manually; blocks `/execute-epic` until DONE | `manual-setup` |

### Mapping rules

- `/create-epic` — parent ticket gets `epic`; each sub-issue gets `story`; executor chosen per sub-issue at planning time.
- `/create-ticket` standalone (no `parent_ref`) — defaults to `task`.
- `/create-ticket` with `parent_ref` — defaults to `story`.
- `bug` is reserved for user-reported defects — not assigned by skill flows.
- Skills filter on `exec:manual` to gate `/execute-epic`: all `exec:manual` sub-issues must be DONE before automated sub-issues can be dispatched.

### Migration from old labels

`manual-setup`, `model:opus`, `model:sonnet` are replaced by this model starting FORGE-8 (EMB-327). Old labels on pre-existing tickets are left in place until natural ticket close or manual cleanup — they are not migrated in bulk.

During the transition period, skills recognize BOTH old and new labels (e.g. `manual-setup` OR `exec:manual` both trigger the manual gate in `/execute-epic`).

**Executor selection rubric:**

- `exec:opus` — new architecture, formula derivation, security-critical logic, design-heavy work, anything that benefits from extended thinking
- `exec:sonnet` — typical implementation by an existing plan, refactoring with clear scope, scaffold + tests, content additions, l10n, lint fixes

When uncertain, prefer `exec:sonnet` — Opus is reserved for genuinely thinking-heavy work.

### Backend-specific label storage

How labels are stored varies by backend — consult the recipe:
- **Linear:** labels are label entities in the team; `ensure_labels` creates them idempotently.
- **GitHub:** labels are repo-level GitHub labels; `ensure_labels` creates them via `gh label create`.
- **Markdown:** labels live in the ticket file's YAML frontmatter (`type:` and `executor:` fields); no global registry.

See `~/.claude/docs/tracker-backends/<backend>.md` for the full `ensure_labels` recipe per backend.

---

## Body shape templates

### Mode A — doc-backed

```markdown
## What
<1-2 sentences paraphrased from doc § Goal>

## Acceptance
<bullets copied verbatim from doc § Acceptance criteria>

## References
- docs/0X_<name>.md  ← exhaustive step-by-step plan; read fully before starting

## Depends on
- <ID>      (omit if none)
```

### Mode B-a — inline

```markdown
## What
<2-4 sentences — goal + why if non-obvious>

## Steps
1. ...
2. ...

## Acceptance
- 3-5 verifiable bullets

## Depends on   (only if true)
- <ID>
```

### Mode B-b — interview

```markdown
## What
<2-4 sentences>

## Interview the user
Before starting, ask:
- ...
- ...

## Acceptance
- ...
```

### Mode B-c — read-first

```markdown
## What
<2-4 sentences>

## Read first
- <file path>
- <doc reference>

## Acceptance
- ...
```

### Mode M — manual-setup

```markdown
## What
<what the user must do manually before code work can begin>

## User actions
1. <e.g. Create Supabase project at https://supabase.com/dashboard>
2. <e.g. Generate anon key + service role key>
3. <e.g. Save SUPABASE_URL and SUPABASE_ANON_KEY into .env.dev>

## Acceptance
- <verifiable end state, e.g. ".env.dev contains SUPABASE_URL and SUPABASE_ANON_KEY">
- <e.g. "supabase login completed and CLI is authenticated">
```

Mode M tickets:
- Get `exec:manual` label (old `manual-setup` label also recognized during transition)
- Are placed FIRST in epic's `## Sub-issues` block
- Block `/execute-epic` until user marks them DONE in the tracker

---

## Sizing

- Sub-issues per epic: **3-8**
- More than 8 → propose splitting into two epics
- Exception: scaffold-style epic with pre-written `docs/0X_*.md` per sub-issue may grow to 13 (verify with user first)

---

## What NOT to put in tickets

- No git workflow content (branch names, `git checkout`, `git commit`, PR/merge instructions)
- No code snippets, architecture diagrams, skill references (`/kit-*`) — that lives in `CLAUDE.md`
- No "Test plan" or "How to test" sections — `## Acceptance` covers it
- No priority / labels / cycle / milestone / assignee unless user asked (label exception: type + executor labels — these ARE part of the convention)

---

## Workflow conventions

> **Conventions on cycles/milestones:** Solo-dev workflow is backlog-driven. Cycles and milestones are NOT proposed by default. Use them only if the project has external deadlines (store release, deploy windows) AND the user has explicitly set them up — and only where the tracker supports them.

> **Linear backend: skills MUST NEVER create new Linear teams.** Always work within an existing team — match by name or ask the user which existing team applies. Creating a team is a manual operation outside skill scope.

---

## Commit conventions

- Magic words: `Implements`, `Fixes`, `Refs` (capitalized)
- Format varies by backend:

| Backend | `implements` | `fixes` | `refs` |
|---|---|---|---|
| Linear | `Implements EMB-42: <desc>` | `Fixes EMB-42: <desc>` | `Refs EMB-42: <desc>` |
| GitHub | `Closes #123: <desc>` | `Fixes #123: <desc>` | `Refs #123: <desc>` |
| Markdown | `Implements forge-8/001-tracker-contract: <desc>` | `Fixes <slug>: <desc>` | `Refs <slug>: <desc>` |

- `Implements` / `Closes` / `Fixes` auto-close tickets on PR merge to the default branch (Linear and GitHub). Markdown has no remote state — the phrase is kept for grep consistency.
- One branch per epic (`feature/<prefix>-<N>-<slug>`); sub-tickets land as separate commits on that branch.
- Full `commit_close_phrase` recipes live in `~/.claude/docs/tracker-backends/<backend>.md`.

---

## Cross-references

- **Backend contract + recipe index:** `~/.claude/docs/tracker-backends/README.md`
- **Per-backend recipes:** `~/.claude/docs/tracker-backends/linear.md`, `github.md`, `markdown.md`
- **tracker.json schema:** `~/.claude/docs/tracker-backends/README.md` § 3
- **Git workflow:** `~/.claude/docs/conventions/git-workflow.md`

---

## Deprecation timeline — `/linear-*` aliases

The `/linear-*` skill aliases (`/linear-create-epic`, `/linear-create-ticket`, `/linear-execute-epic`, `/linear-execute-ticket`, `/linear-epic-close`, `/linear-pr-create`, `/linear-commit`) were deprecated as of **FORGE-8** (EMB-327, merged 2026-05-12).

- They remain fully callable for approximately **2 sprint cycles** after FORGE-8 merges, to ease the transition.
- A separate cleanup epic — referred to as the **"FORGE-8 cleanup"** epic (no Linear ID yet; will be created when scheduled) — will remove the alias files.
- Alias files live at `~/.claude/commands/linear-*.md`; each is a one-liner that redirects to the canonical skill.

**Migrate at your convenience:** replace any `/linear-*` invocations with the canonical names:

| Deprecated | Canonical |
|---|---|
| `/linear-create-epic` | `/create-epic` |
| `/linear-create-ticket` | `/create-ticket` |
| `/linear-execute-epic` | `/execute-epic` |
| `/linear-execute-ticket` | `/execute-ticket` |
| `/linear-epic-close` | `/epic-close` |
| `/linear-pr-create` | `/pr-create` |
| `/linear-commit` | `/commit` |
