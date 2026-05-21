<!--
  Owner overview — high-level project snapshot for the human owner.

  Auto-update contract: scaffolded by `/forge:project-init`; refreshed by
  `/forge:kit-update-docs` on epic close, dependency changes, milestone
  changes. Sections OUTSIDE `<!-- manual -->` guards may be regenerated.
  Content INSIDE `<!-- manual --> ... <!-- /manual -->` is preserved
  verbatim across regeneration.

  Format spec: `plugins/forge/docs/conventions/owner-overview.md`.
  Cap: ≤ 300 lines total (auto-regen aborts if exceeded).
-->

# {{ project_name }} — Owner overview

> Single-page snapshot of what this project is, where it is, and where it's going. Skim before any planning conversation.

---

## 1. Overview

<!-- manual -->
{{ one_paragraph_elevator_pitch }}

_e.g. "An offline-first mobile RPG that turns daily habits into quest progression. Solo dev project; target audience is self-improvement gamers who want a calmer alternative to Habitica."_
<!-- /manual -->

---

## 2. Features

Three buckets. **Shipped** and **In progress** are auto-maintained by `/forge:kit-update-docs` from epic + ticket state. **Planned** is hand-curated.

### Shipped

<!-- auto:features.shipped -->
- {{ shipped_feature_1 }} — _shipped {{ YYYY-MM-DD }}_
- {{ shipped_feature_2 }} — _shipped {{ YYYY-MM-DD }}_
<!-- /auto:features.shipped -->

### In progress

<!-- auto:features.in_progress -->
- {{ in_progress_feature }} — _epic {{ TRACKER-NN }}, target {{ phase / milestone }}_
<!-- /auto:features.in_progress -->

### Planned

<!-- manual -->
- {{ planned_feature_1 }} — _priority: high / med / low_
- {{ planned_feature_2 }}
<!-- /manual -->

---

## 3. Phases & Milestones

Currently-active phase and what's next. Pulled from `docs/00_meta/roadmap.md`.

### Active phase

<!-- auto:phases.active -->
**{{ phase_name }}** — _started {{ YYYY-MM-DD }}, target {{ YYYY-MM-DD or "rolling" }}_

{{ one_line_phase_goal }}
<!-- /auto:phases.active -->

### Upcoming

<!-- auto:phases.upcoming -->
- **{{ next_phase_name }}** — _target {{ YYYY-MM-DD or "TBD" }}_ — {{ one_line_goal }}
<!-- /auto:phases.upcoming -->

### Milestones (optional)

<!-- manual -->
_Add named external-deadline milestones here (store release, demo day, conference). Solo-dev internal projects may leave empty._
<!-- /manual -->

---

## 4. Tech stack

Per-platform if multi-platform. Auto-maintained from `CLAUDE.md` essential-commands + project-init answers.

<!-- auto:tech_stack -->

### {{ platform_1_name }} _(e.g. mobile, web, backend)_

| Layer | Choice |
|---|---|
| Language / framework | {{ e.g. Flutter 3.24 + Dart }} |
| State management | {{ e.g. Bloc }} |
| Persistence | {{ e.g. Drift (SQLite) }} |
| Cloud / backend | {{ e.g. Supabase }} |
| Hosting | {{ e.g. App Store + Play Store }} |

### {{ platform_2_name }} _(omit for single-platform projects)_

| Layer | Choice |
|---|---|
| Language / framework | {{ ... }} |
| State management | {{ ... }} |
| Persistence | {{ ... }} |
| Cloud / backend | {{ ... }} |
| Hosting | {{ ... }} |

<!-- /auto:tech_stack -->

---

## 5. Libraries & tools

Opt-in modules currently active. One line each — what + why. Auto-detected from package manifests + `.mcp.json` + `.claude/settings.json`.

<!-- auto:libraries -->
- **{{ library_or_tool }}** — {{ one_line_why_this_choice }}
- **Sentry** _(if enabled)_ — error + performance monitoring; DSN in env, not VCS
- **Supabase** _(if enabled)_ — auth + Postgres + storage; project URL in env
- **Linear** _(if tracker = linear)_ — ticket + epic backlog; team {{ team_key }}
<!-- /auto:libraries -->

<!-- manual -->
_Add one-line "why we picked this" notes for non-obvious choices here. Survives regeneration._
<!-- /manual -->

---

## 6. Conventions cheatsheet

Quick-reference for read-only humans (PMs, designers, new contributors). Full rules live in `CLAUDE.md` + `plugins/forge/docs/conventions/`.

| Topic | Rule |
|---|---|
| Branch naming | `feature/{{ prefix }}-N-<slug>` — one branch per epic, sub-tickets commit on it |
| Commit magic words | `{{ commit_magic_word_example }}` — auto-links + auto-closes on PR merge |
| Tracker backend | `{{ tracker_backend }}` _(linear / github / markdown)_ |
| Ticket prefix | `{{ ticket_prefix }}` _(e.g. EMB, FORGE)_ |
| PR target | `main` (default) — never push directly without explicit instruction |
| Decisions | `/forge:log-decision` appends to `docs/00_meta/decisions-log.md` |
| Docs refresh | `/forge:kit-update-docs` after branch finish or stack-touching change |

---

## How this file stays fresh

- **Scaffolded by:** `/forge:project-init` (one-time, from this template).
- **Auto-updated by:** `/forge:kit-update-docs` on epic close, dependency changes, milestone changes.
- **Hand-edited zones:** anything inside `<!-- manual --> ... <!-- /manual -->` is preserved verbatim across regeneration. Auto-zones use `<!-- auto:<key> --> ... <!-- /auto:<key> -->`.
- **Cap:** ≤ 300 lines. Auto-regen aborts and asks the user to prune if exceeded.
- **Spec:** `plugins/forge/docs/conventions/owner-overview.md`.
