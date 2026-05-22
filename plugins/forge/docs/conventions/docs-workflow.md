# Docs workflow (universal)

> Reference rulebook for documenting any project under `<project>/docs/`. Each project owns a `docs/00_meta/docs-workflow.md` that points back to this file and adds its own routing decisions on top.

This file describes the **shape** of a project's documentation tree, the **per-file conventions** that keep it consistent, and the **mandatory cross-doc updates** that prevent drift. Stack-agnostic — substitute the project's tech stack, ticket prefix, and domain vocabulary throughout.

---

## Purpose

Every non-trivial project accumulates four kinds of long-lived knowledge:

1. **Locked decisions** — choices that should not be re-litigated by a future contributor (human or agent) who lacks the original context.
2. **Strategic timeline** — what ships when, in what order, with what dependencies.
3. **Routing rules** — where new content goes when an agent isn't sure ("is this a decision? a spec? a deferred item?").
4. **Terminology** — the project's vocabulary, especially terms that would be ambiguous to a fresh reader.

Without an explicit home for each, this knowledge leaks into chat transcripts, ticket descriptions, or stale comments — and gets lost. The `docs/00_meta/` namespace exists to give each kind a single canonical file, with conventions strict enough that any agent can find and update them deterministically.

---

## Folder layout

The only **prescribed** layer is `docs/00_meta/`. Everything else is a project choice — pick what fits the domain.

```
<project>/docs/
  00_meta/
    decisions-log.md     ← append-only locked decisions (all kinds)
    roadmap.md           ← strategic timeline / phases / milestones
    docs-workflow.md     ← project-instance routing (extends this file)
    glossary.md          ← project-specific terminology
    idea-dump.md         ← (optional) un-groomed ideas with graduation path
  0X_<area>/             ← project-chosen design / spec folders
  adr/                   ← (optional) formal architecture decision records
```

A typical layout might add `01_design/`, `02_architecture/`, `03_reference/` (for product / spec / external prior-art content), or whatever the domain calls for. The numeric prefix (`00_`, `01_`, …) sorts the meta layer first in directory listings and signals reading order without enforcing it.

The `00_meta/` folder is the **routing layer** — agents check it first when they don't know where a piece of content goes.

---

## Per-file conventions

### `decisions-log.md`

Append-only registry of locked design / product / architectural decisions. One entry per decision. Once logged, do not revisit unless the entry is explicitly reopened.

**Format** (newest at top):

```markdown
## YYYY-MM-DD: <decision title>

**Status:** ✅ FINAL
**Decision:** <one sentence — what was chosen>
**Rationale:** <one paragraph — why this beats the alternatives>
**How to apply:** <where this decision shows up in code / specs / process>
**Linked:** [[0X_<area>/<spec>]], <ticket-prefix>-NNN (optional)
```

The rationale must outlive the chat. Its job is to keep a future contributor from re-opening the same question without new information.

**Status taxonomy** (canonical — projects may override but consistency across projects helps):

- 🟡 PROPOSED — drafted, not yet locked
- ✅ FINAL — locked, treat as constraint
- ❌ REJECTED — considered and declined; entry stays so the option isn't re-proposed
- 🔄 REOPENED — was FINAL, now under reconsideration with explicit reason
- 🚧 IN PROGRESS — execution-tracking variant for milestones / epics
- 📋 PLANNED — scheduled but not started

**Single-registry default.** One log covers design + product + architectural decisions. Projects with high-volume architecture decisions may split into a light `decisions-log.md` plus long-form entries under `adr/` — that's an advanced pattern; default to one log.

A copy-pasteable template lives at the **bottom** of the file so the format doesn't drift over time.

### `roadmap.md`

Strategic timeline — single source of truth for milestone scope, phase ordering, dependencies, and tactical deferred items. Read **first** when planning the next epic, milestone change, or scope decision.

Owns:

- Milestone status (current phase, next phase, completed phases)
- In-progress phase epics with links to per-epic specs / cheat sheets
- Sketches for future phases (loose; pre-design)
- Dependency graph between epics
- Deferred items per phase tag (with reason and re-evaluation trigger)

Acts as **veto** over any other doc making scope claims. If a feature spec implies "this ships in phase X" but the roadmap doesn't list it, the roadmap wins until the discrepancy is resolved.

End the file with a "What this file IS / IS NOT" section — explicit non-goals ("not a ticket tracker," "not a per-feature spec") that keep it from scope-creeping into adjacent docs.

### `docs-workflow.md` (project instance)

Each project's own copy. Contains:

- One-line link back to this universal file (`See [[~/.claude/docs/conventions/docs-workflow.md]]`)
- A "where does X go?" decision tree, parameterized for the project's folder layout
- Per-file cheat-sheet table: file → owns → "write here when…"
- Project-specific cross-doc rules layered on top of the universal ones below
- The chosen cross-link convention (see below)
- A "when this file is wrong" note — structure-on-disk wins; the doc gets corrected to match reality, not the other way around

This file is **not a skill** — it's the file every agent consults before writing or persisting anything in `docs/`.

### `glossary.md`

Project-specific terminology only. Don't define vocabulary that any reader (or LLM) already understands — define what's ambiguous within the project's domain.

Rules:

- Every term that appears in 2+ docs gets an entry.
- New term introduced anywhere → glossary entry mandatory in the same change.
- Renames → search-and-replace across all docs **and** keep the old entry with a `> Renamed YYYY-MM-DD → <new term>` note for one cycle, so dangling references resolve.
- Sorted alphabetically with a brief one-paragraph definition + optional links to canonical specs.

Acts as the foundation for any future internal or public wiki.

### `idea-dump.md` (optional)

Half-formed thoughts that aren't ready for a design doc but shouldn't be lost in chat. Recommended for projects without a separate capture surface; skip it if the project uses an issue tracker for this.

Each idea has a clear graduation path: it leaves the file only when (a) locked into a doc + decisions-log entry, or (b) explicitly dropped with a one-line reason.

---

## Mandatory cross-doc updates

When a triggering event happens, the listed files **all** get updated in the same change. The table is the enforcement mechanism — without it, individual rules get forgotten.

| When you do this | You MUST also update |
|---|---|
| Lock a decision | `decisions-log.md` entry + the relevant design / spec doc + `glossary.md` if it introduces a new term |
| Defer an item | `roadmap.md` deferred section + the source doc's open-questions section |
| Resolve a deferred item | Drop from `roadmap.md` deferred + log the decision + update the spec |
| Rename a term | `glossary.md` (with rename note) + search-and-replace across all docs |
| Catch a contradiction between docs | Pick the canonical version, fix the wrong one, log the resolution if non-obvious |
| Introduce a new term | `glossary.md` entry in the same change as the doc that introduces it |
| Reopen a FINAL decision | Mark old entry 🔄 REOPENED + write a new entry capturing what changed |

> Currently agent-discipline only — relies on whoever writes the doc to follow the table. A future enhancement (candidate for tooling work) is a hook or skill that machine-checks "did you log this decision and update the spec?" before allowing the change to land. Not yet shipped.

---

## What does NOT belong in docs/

- **Code** — lives in the project's source tree (`src/`, `lib/`, equivalent). Docs may reference snippets but should not host implementation.
- **Tickets / stories** — live in the issue tracker (Linear, GitHub Issues, Jira). Docs may link to ticket IDs but should not duplicate ticket bodies.
- **Session-only chat output** — exploratory conversation, ad-hoc Q&A. If a chat produces a locked decision, the **decision** goes in `decisions-log.md`; the chat itself does not.
- **Secrets / credentials** — never commit secrets to docs. Use the project's secret-management mechanism.
- **Generated artefacts** — build output, generated schemas, screenshots intended for one-time review. Source-of-truth specs only.
- **Scratch notes for an in-flight task** — keep these in the working branch's PR description or a tracker comment; promote to docs only when the work locks.

---

## Source format: Markdown is canonical, HTML is generated

- **Source-of-truth docs are always Markdown** (plus `openapi.json` / `asyncapi.yaml` for API specs). MD is git-diffable for PR review, readable by AI agents as context, and safely editable in `<!-- auto:<key> -->` guard blocks.
- **HTML is a generated presentation layer, never authored or edited by hand.** Polished/interactive views are rendered from MD or specs — Swagger UI / Redoc from `openapi.json`, AsyncAPI HTML from `asyncapi.yaml`, or an MD→site build (MkDocs / Docusaurus) for prose. Those outputs are build artifacts, not committed source-of-truth.
- The `forge:update-docs` skills never write HTML.

## How `/log-decision` and `forge:update-docs` interact

- **`/log-decision`** appends an entry to `00_meta/decisions-log.md` via a guided 30-second flow. It optionally updates the relevant design doc and `glossary.md` in the same step when the decision introduces a new term or supersedes a prior choice. Use it whenever a non-trivial decision crystallises during a session — the rationale must outlive the chat.
- **`forge:update-docs`** is the after-implementation sweep — a router that analyses the epic's scope and dispatches to per-type children: `update-docs-meta` (owner-overview + this `00_meta/` registry set), `update-docs-api` (backend API reference), `update-docs-design` (design / ADR drift detection). It runs nothing whose domain the epic didn't touch. Children respect the rules in this file — append to `decisions-log.md`, update `roadmap.md` deferred entries, refresh `glossary.md`.

Both are entry points into the same workflow. `/log-decision` is for the moment a decision locks; `forge:update-docs` is for catching up docs after implementation.

---

## Project instance pattern

Every project should have a `docs/00_meta/docs-workflow.md` that:

1. Opens with a one-line pointer back to this universal file (e.g. `See [[~/.claude/docs/conventions/docs-workflow.md]] for the universal rulebook this extends.`).
2. Specifies the project's chosen **cross-link convention**. Recommended default: Obsidian wikilinks (`[[0X_<area>/<doc>]]`) — they survive moves better than relative paths and render in both Obsidian and most markdown viewers. Projects published primarily through plain GitHub may prefer relative markdown paths; the universal layer doesn't enforce, but every project should pick **one** and apply it everywhere.
3. Lists the project's actual folder layout (which `0X_*` folders exist and what each owns).
4. Contains a "where does X go?" decision tree parameterised for the project — same shape across projects, leaf destinations vary.
5. Adds project-specific cross-doc rules on top of the universal table above (e.g. "when changing the schema, also update the schema reference in `0X_tech/`").
6. Documents the project's chosen ticket prefix and how decisions link to tickets.

Treat the project instance as the **per-project override layer**, not a replacement for this file. When the two conflict, the project instance wins for that project; the universal file is updated only when a pattern proves itself across multiple projects.

---

## Reference implementations

Existing project-instance examples to crib from when authoring a new project's `docs-workflow.md`:

- `embergard-mobile/docs/00_meta/docs-workflow.md` — Flutter mobile RPG. Uses Obsidian wikilinks, single decisions-log, ADRs nested under tech docs, idea-dump active.

(Add new entries here as future projects adopt this structure.)
