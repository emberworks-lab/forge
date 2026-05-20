# Owner-overview format spec

> Authoritative spec for `docs/owner-overview.md` — the single-page project snapshot every project gets. Defines section order, guard semantics, update lifecycle, and the contract between `/forge:project-init` (scaffolds) and `/forge:kit-update-docs` (refreshes).
>
> Canonical template: [`plugins/forge/skill-templates/_common/owner-overview.md`](../../skill-templates/_common/owner-overview.md).

---

## Purpose

`owner-overview.md` exists so a returning owner — or any new contributor — can answer four questions in under two minutes:

1. **What is this project?** — one-paragraph elevator pitch.
2. **What's shipped, what's cooking, what's planned?**
3. **Where in the roadmap are we right now?**
4. **What stack, what libraries, what conventions apply?**

It is **not** a replacement for `README.md` (user-facing install/run instructions), `CLAUDE.md` (agent routing), or `docs/00_meta/roadmap.md` (strategic timeline source-of-truth). It's a curated digest that pulls from those three.

---

## File location

| Project shape | Location |
|---|---|
| Single-platform | `<project>/docs/owner-overview.md` |
| Multi-platform monorepo | `<repo-root>/docs/owner-overview.md` (one file, with per-platform sub-sections under "Tech stack" and "Libraries & tools") |

Never per-platform copies. The owner reads one file.

---

## Line cap

**≤ 300 lines total**, including placeholders, guards, and blank lines.

Why a hard cap: this is a digest, not a spec. If a section grows past its slot, the content belongs in `docs/00_meta/` or a per-feature spec instead. `/forge:kit-update-docs` aborts regeneration and asks the user to prune if the rendered output exceeds 300 lines.

---

## Section order (canonical)

| # | Section | Owner | Source of truth |
|---|---|---|---|
| 1 | Overview | Manual | One-paragraph elevator pitch — never auto-generated |
| 2 | Features (Shipped / In progress / Planned) | Auto + Manual | Shipped + In progress: tracker (epics + tickets). Planned: manual list. |
| 3 | Phases & Milestones (Active + Upcoming) | Auto | `docs/00_meta/roadmap.md` |
| 4 | Tech stack (per-platform if multi) | Auto | `CLAUDE.md` essential-commands + project-init answers |
| 5 | Libraries & tools | Auto + Manual | Package manifests + `.mcp.json` + `.claude/settings.json`; manual "why" notes preserved |
| 6 | Conventions cheatsheet | Auto | `CLAUDE.md` + `.claude/tracker.json` + `plugins/forge/docs/conventions/` |

Sections must appear in this order. `/forge:kit-update-docs` re-emits them in order; out-of-order sections in the existing file are reordered.

---

## Guard semantics

Two guard types delimit regions in the file:

### `<!-- manual --> ... <!-- /manual -->`

User-owned. `/forge:kit-update-docs` **never** overwrites content between these guards. If the surrounding section is regenerated, the manual block is lifted out, the rest is rewritten, then the manual block is reinserted at the same relative position.

Used for:

- Section 1 (Overview) — the entire paragraph
- Section 2 (Planned features) — hand-curated list
- Section 3 (Milestones) — optional external-deadline list
- Section 5 — optional "why we picked this" prose notes
- Anywhere the user adds a freeform note worth keeping

### `<!-- auto:<key> --> ... <!-- /auto:<key> -->`

Agent-owned. `/forge:kit-update-docs` replaces the entire block on every run. The `<key>` is a stable identifier (`features.shipped`, `phases.active`, `tech_stack`, `libraries`, etc.) so the updater can target specific blocks without re-parsing the whole file.

Used for:

- Section 2 (Shipped / In progress)
- Section 3 (Active phase / Upcoming)
- Section 4 (Tech stack tables)
- Section 5 (auto-detected library list)
- Section 6 is rendered as a single auto-block (no key — whole-section replacement)

### Nesting rule

Manual guards may appear inside an auto-section (e.g. a free-form note inside `## 5. Libraries & tools`). Auto-guards may **not** appear inside manual guards. If the updater encounters this, it logs a warning and treats the whole region as manual.

---

## Update lifecycle

| Event | Action | Skill |
|---|---|---|
| Project bootstrap | File scaffolded from canonical template with placeholders filled from project-init answers | `/forge:project-init` |
| Epic closed | Sections 2 (Shipped + In progress) + 3 (Active phase) refreshed from tracker state | `/forge:kit-update-docs` (invoked by `/forge:epic-close`) |
| Dependency added / removed | Section 4 (Tech stack) + Section 5 (Libraries) refreshed | `/forge:kit-update-docs` (invoked manually or by post-install hook) |
| Milestone changed | Section 3 (Active + Upcoming) refreshed from `roadmap.md` | `/forge:kit-update-docs` |
| Manual edit | User edits anything (typically inside `<!-- manual -->` guards) | n/a — guards preserve it |

`/forge:kit-update-docs` is the single entry point for non-manual updates. It is idempotent — running it twice with no source changes produces no diff.

---

## Placeholder convention

The template uses `{{ snake_case_placeholder }}` for values populated at scaffold time. `/forge:project-init` substitutes from the stack interview answers:

| Placeholder | Source |
|---|---|
| `{{ project_name }}` | project-init Q1 |
| `{{ prefix }}` | `.claude/tracker.json` `prefix` field |
| `{{ ticket_prefix }}` | same as above |
| `{{ tracker_backend }}` | `.claude/tracker.json` `backend` field |
| `{{ commit_magic_word_example }}` | derived from backend (see `plugins/forge/docs/tracker-backends/<backend>.md`) |
| `{{ platform_1_name }}` etc. | project-init Q2 (project type) |
| Other `{{ ... }}` | populated by `/forge:kit-update-docs` from tracker / repo state |

Unsubstituted placeholders are a smell — `/forge:kit-update-docs` flags any `{{ ... }}` that remains after a refresh as a TODO.

---

## What this file IS / IS NOT

**IS:**

- A single-page owner-facing digest.
- The deliverable that answers "where are we?" without opening the tracker.
- A template that survives across project lifetime via guards + auto-keys.

**IS NOT:**

- A ticket tracker (tracker is the tracker).
- A per-feature spec (those live in `docs/0X_<area>/`).
- A changelog (use `CHANGELOG.md` if the project ships releases).
- A replacement for `README.md` or `CLAUDE.md`.

---

## Reference implementations

_Add entries here as projects adopt the template._

- _(none yet — first projects land via `/forge:project-init` after EPIC C+D ticket #64 wires the scaffold step.)_
