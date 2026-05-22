---
name: e2e
description: Universal end-to-end testing contract and router. Defines the opt-in model, RED→GREEN lifecycle, and validation discipline shared by all platforms, then dispatches to the per-platform child (web / backend / mobile) based on tracker.json platforms[] and the ticket's e2e flavor.
type: fundamental
---

# forge:e2e

The umbrella for end-to-end testing across every platform. This skill owns the **universal** rules — what an e2e test is, how it opts in, how it runs and validates — and **routes** each request to the right platform child. It does not run any tests itself; the children do.

```
forge:e2e  (this skill — universal rules + router)
├── forge:e2e-web        Playwright (external; not vendored)
├── forge:e2e-backend    DB-isolated API/HTTP suite
└── forge:e2e-mobile     framework + device-target router (future)
```

## What e2e means here

An e2e test exercises the system across its real boundaries — real HTTP, real browser, real device, real database — never mocked at the seam under test. It is the highest-fidelity, slowest tier; reserve it for the flows that matter, and let unit tests cover the rest.

## Universal opt-in model (three-state)

Every platform uses a per-platform marker file under `<platform.path>/.claude/`. The state machine is identical across platforms; only the marker name and payload differ.

| Marker | State | Behaviour |
|---|---|---|
| Absent | Undecided | `--check` returns `needs-setup`; `--init` writes the marker. |
| Present, opted in | Opted in | `--run` proceeds; `--check` returns `configured`. |
| Present, opted out (`opted_in:false` / `db_isolation:"none"`) | Opted out | `--check` returns `not-applicable`; never asks again. |

Per-platform marker + payload: `forge:e2e-web` → `.claude/e2e-web.json`; `forge:e2e-backend` → `.claude/e2e.json`; `forge:e2e-mobile` → `.claude/e2e-mobile.json`.

## Universal lifecycle

The same five-beat lifecycle applies to every flavor; the child fills in the platform mechanics.

1. **check** — is this platform opted in and are its prerequisites present?
2. **author (RED)** — generate spec files from the ticket's acceptance criteria via `forge:tdd`. Each spec MUST start RED for the right reason.
3. **implement** — production code (the caller's implementation phase) turns the specs GREEN.
4. **run (GREEN)** — execute the specs via the child until green; `mode=report` then `mode=fix` (max 3).
5. **gate** — `forge:epic-close` blocks the close on any red suite.

## Validation discipline (all flavors)

- A spec must be observed failing for the intended reason before it counts (no spec that never went red).
- Never delete, skip, or weaken a spec to make the suite pass.
- Always clean up provisioned resources (DB containers, browser contexts, emulators), even on failure.
- Report structured pass/fail to the caller; the caller owns commit and halt decisions — this skill and its children never commit.

## Routing

Resolve the flavor, then dispatch to the child for the requested sub-mode.

Flavor resolution:

1. Read `<project>/.claude/tracker.json` → `platforms[]` (reader algorithm: `plugins/forge/docs/conventions/tracker-json.md` §4).
2. If a ticket E2E qualifier is supplied (`required: web | backend | mobile`), that flavor is requested; if the project's `platforms[]` does not list it → halt `unsupported-e2e-flavor`.
3. `required: yes` → the project's default e2e-capable platform; if `platforms[]` is absent → default `backend` (single-repo back-compat).

Flavor → child:

| Flavor | Child | Marker |
|---|---|---|
| `web` | `forge:e2e-web` | `.claude/e2e-web.json` |
| `backend` | `forge:e2e-backend` | `.claude/e2e.json` |
| `mobile` | `forge:e2e-mobile` (future) | `.claude/e2e-mobile.json` |

## Sub-modes (each routes per platform)

- **`--check`** — walk every platform in `platforms[]`; dispatch each to its child's `--check`; aggregate. Any `needs-setup` on an opted-in-pending platform surfaces its fix and halts. `--check` is run once per epic by `forge:execute-epic` Step 3.5 and by `forge:epic-close` Step 0b.
- **`--run [--flavor <f>] [path_filter] [mode]`** — with `--flavor`, dispatch that one child's `--run`. Without it, walk every opted-in platform and run each child's full suite (the epic-close gate path). Forward the combined report.
- **`--init`** — for each platform, ask the user whether they want e2e there; on yes, dispatch the child's `--init` (which writes the marker and surfaces setup); on no, write the opted-out marker so it never asks again.

## Mobile branch (future)

`forge:e2e-mobile` is not yet built — mobile e2e is in research (`plugins/forge/docs/design-research/mobile-e2e-survey.md`, `mobile-e2e-matrix.md`). When implemented it is itself a router: it resolves the mobile framework (Flutter → Patrol, RN → Detox, KMP, native iOS/Android → XCUITest/Espresso) and the device target (iOS simulator vs Android emulator), then dispatches to `forge:e2e-mobile-<framework>`. Until those land, `--check`/`--run` for the `mobile` flavor return `not-applicable` with a pointer to the research docs.

## Trigger

- **Auto:** `forge:execute-epic` Step 3.5 (`--check`), `forge:execute-ticket` e2e TDD loop (`--run --flavor`), `forge:epic-close` Step 0b gate (`--check` then `--run`). Setup-time `--init` from `forge:project-init` is intended but not yet wired (tracked in #105).
- **Manual:** `/forge:e2e --check | --run [--flavor web|backend|mobile] | --init`.

## Do not

- Do not run tests directly here — always dispatch to a child.
- Do not bypass a child's `--check` before its `--run` inside the epic-close gate.
- Do not commit, and do not let any child commit — the caller owns that.

## What this skill does not cover

- **Platform mechanics** — owned by `forge:e2e-web` (Playwright), `forge:e2e-backend` (DB isolation), `forge:e2e-mobile` (future).
- **Spec authoring discipline** — `forge:tdd`.
- **Manual setup of tools** — surfaced by each child (e.g. the Playwright manual-setup template).
