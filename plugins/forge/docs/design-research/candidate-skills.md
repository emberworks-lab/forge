# Candidate forge:* Design Skills

_Synthesized: 2026-05-21. Refs #74._

Distillation of the EPIC G research artifacts (#70-#73) plus the two demo
skills already shipped (#75 `forge:design-bootstrap`, #76 `forge:design-source`).
Each candidate cites at least one source-research bullet; speculation beyond
the research is explicitly avoided.

Source artifacts referenced below:
- `existing-tools.md` (#70) — survey of mattpocock, superpowers, Anthropic
  marketplace, community design plugins.
- `external-generators.md` (#71) — Stitch, v0, Lovable, Galileo, Anima,
  Builder.io profiles and recommendation.
- `tokens-patterns.md` (#72) — Style Dictionary, Tokens Studio, Daisy UI,
  shadcn/ui token-model comparison.
- `workflow-patterns.md` (#73) — Figma → code handoff, governance, spec
  documentation, iteration patterns.
- `design-bootstrap/SKILL.md` (#75) — three-branch bootstrap demo.
- `design-source/SKILL.md` (#76) — three-branch design-source demo.

> TODO — fill once #69 lands. The user's article digest was deferred when no
> article list was provided. Re-evaluate priorities once that artifact exists;
> see "Calibration after #69" at the end of this document.

---

## P0 — next parking-lot epic

### 1. `forge:design-tokens-gen`

- **Purpose:** Scaffold a project-local design-token file (default: shadcn/ui
  CSS-variable model) and wire it into the build so generated UI code can
  reference real tokens instead of hardcoded values.
- **Effort:** M
- **Dependencies:** `forge:design-bootstrap` branch (c) (consumes the
  `design/tokens.json` stub it scaffolds); Tailwind or equivalent CSS pipeline
  present in the project.
- **Source signal:**
  - `tokens-patterns.md` §"Recommended Pattern for `forge:design-bootstrap`"
    explicitly recommends shadcn/ui as the default and lists Style
    Dictionary + Daisy UI as opt-in layers.
  - `existing-tools.md` G1 ("Design-system-aware code generation") names this
    exact gap: no surveyed tool reads the project's token file and generates
    UI that references those specific values.
  - `workflow-patterns.md` §5 Must-Haves: "Design tokens in version-controlled
    JSON" is a baseline requirement for AI execution.

### 2. `forge:design-source-v0` (wire v0 + Anima APIs into `forge:design-source`)

- **Purpose:** Promote branch 2 of `forge:design-source` from "freeform prompt
  + manual paste" to API-driven generation when `V0_API_KEY` or
  `ANIMA_API_KEY` is set, falling back to the existing copy-paste flow
  otherwise.
- **Effort:** M
- **Dependencies:** existing `forge:design-source` skill; optional env vars
  `V0_API_KEY`, `ANIMA_API_KEY`; account on Vercel ($20/mo Premium) or Anima
  for the API path.
- **Source signal:**
  - `external-generators.md` §"Recommendation" picks v0 + Anima as the two
    direct-wrap candidates and provides the exact dual-mode pattern
    (env-var-gated API call with manual fallback).
  - `design-source/SKILL.md` branch 2 includes a `TODO: once
    forge/docs/design-research/external-generators.md exists, replace the
    freeform ask with a generator-specific prompt template lookup` — this
    candidate closes that TODO.

### 3. `forge:design-a11y-brief`

- **Purpose:** Before UI code is written for a ticket, enumerate the
  accessibility requirements (semantic HTML, ARIA, focus, touch targets,
  reduced-motion, contrast) as a checklist appended to the ticket — gating
  implementation on the brief existing.
- **Effort:** S
- **Dependencies:** tracker backend (Linear / GitHub) for posting the brief;
  invoked from `forge:execute-ticket` for design-tagged tickets.
- **Source signal:**
  - `existing-tools.md` G6 ("Accessibility-first gating, not post-hoc
    auditing"): no existing skill gates implementation on a prior a11y brief
    — every surveyed tool audits after the fact.
  - `existing-tools.md` §2a confirms the underlying checklist (ARIA,
    focus, touch targets, reduced motion, semantic HTML, keyboard nav) is
    well-established in `obra/superpowers`' review flow — forge would
    promote it from a buried review step to an invokable gate.

---

## P1 — next-but-one

### 4. `forge:figma-implement` (forge wrapper around Code Connect + Dev Mode)

- **Purpose:** Translate a Figma frame URL into a project-local component
  using the project's design system, with Code Connect mappings consulted
  first so generated code uses real components instead of generated CSS.
- **Effort:** L
- **Dependencies:** Figma MCP plugin (already in forge); Code Connect config
  in the target project; `forge:design-tokens-gen` output for token
  validation.
- **Source signal:**
  - `existing-tools.md` §3c — the official Anthropic `figma` plugin already
    ships `/implement-design`, so forge should complement (deeper workflow,
    token discipline) rather than duplicate.
  - `workflow-patterns.md` §1b — Code Connect is the mainstream pattern that
    "eliminates the generated-code-is-not-real-code problem".
  - `existing-tools.md` §4c — `claude2figma`'s `figma-style-binding`
    enforcement loop (search → instance → bind → verify) is the most rigorous
    token-discipline pattern in the survey and is worth porting.

### 5. `forge:design-ac-extract`

- **Purpose:** Read a Figma frame URL + frame metadata and produce a
  ticket-ready acceptance-criteria checklist (states, breakpoints, tokens
  used, animation spec) in the format `forge:execute-ticket` already consumes.
- **Effort:** M
- **Dependencies:** Figma MCP plugin; tracker backend for ticket edits.
- **Source signal:**
  - `workflow-patterns.md` §3c — "Design Acceptance Criteria in the Tracker
    Ticket" is explicitly flagged as "less common, recommended for AI
    workflows" and the exact AC format is documented there.
  - `workflow-patterns.md` §1c — AI-assisted handoff (Figma Make / AgentC2)
    can already extract specs and pre-fill tickets; forge would close the
    loop into its own tracker.
  - `existing-tools.md` G3 — no existing tool wraps brief → AC → implement
    into a single ticket-driven workflow.

### 6. `forge:design-prototype-variants`

- **Purpose:** Replace generic prototype variation with a design-system-aware
  version: generate 3 structurally-different layout variants for the same
  screen using the project's tokens + components, expose via `?variant=`
  URL param, and capture the verdict on the tracker ticket before deletion.
- **Effort:** M
- **Dependencies:** existing `forge:prototype` skill; project design tokens
  (from `forge:design-tokens-gen`); tracker backend for capturing the
  decision.
- **Source signal:**
  - `existing-tools.md` §1a — `mattpocock/prototype` is the most complete
    AI-driven UI exploration pattern and forge's own `prototype` is already
    a derivative; the documented gap is "no design-token awareness, no
    accessibility check, no design-system integration".
  - `existing-tools.md` G5 ("Design-decision capture") — `mattpocock/prototype`
    mandates verdict capture before deletion; no other tool does. Forge can
    extend this into the tracker.

---

## P2 — later / opportunistic

### 7. `forge:design-critique`

- **Purpose:** Run a structured design critique pass on a frame or rendered
  page (usability heuristics, design-system consistency, microcopy quality)
  and post the findings to the tracker ticket.
- **Effort:** S
- **Dependencies:** Anthropic `design` plugin OR self-hosted critique
  prompts; tracker backend for posting.
- **Source signal:**
  - `existing-tools.md` §3a — the official Anthropic `design` plugin covers
    Design Critique + UX Writing + WCAG audit + Research Synthesis but
    "does not generate or modify code, so it's complementary".
  - `existing-tools.md` G2 ("Tracker-integrated design workflow") — no
    existing tool ties design decisions to a ticket system; forge can.

### 8. `forge:design-tokens-import-figma`

- **Purpose:** Pull design tokens out of a Figma file (variables) and write
  them into the project's `design/tokens.json` in W3C DTCG format.
- **Effort:** L
- **Dependencies:** Figma MCP plugin; Tokens Studio plugin in the source
  Figma file (or Figma Variables API); `forge:design-tokens-gen` for the
  downstream build.
- **Source signal:**
  - `tokens-patterns.md` §2 ("Tokens Studio") — documents the Figma → GitHub
    JSON → Style Dictionary pipeline that forge would automate.
  - `workflow-patterns.md` §2c ("Continuous Token Sync via DTCG") — the W3C
    format makes this a tool-agnostic pipeline, suitable for AI parsing.
  - `design-bootstrap/SKILL.md` §"What this skill does not cover" explicitly
    names this as a separate skill (`forge:design-source`, sibling). The
    sibling shipped but does not cover token import — this candidate fills
    the gap.

### 9. `forge:design-storybook-gen`

- **Purpose:** Generate a Storybook story scaffold for a component from a
  Figma frame + Code Connect mapping, so the component can be reviewed in
  isolation before full-app integration.
- **Effort:** M
- **Dependencies:** Storybook configured in the project; Figma MCP plugin;
  Code Connect config.
- **Source signal:**
  - `workflow-patterns.md` §4b ("Component-Driven Development / Storybook-
    First") — "AI can generate a story scaffold from a Figma frame + Code
    Connect mappings, then run Storybook CI to verify it renders" is stated
    as the explicit AI-agent fit.

### 10. `forge:design-flutter-theme`

- **Purpose:** Generate a Material 3-compliant `ThemeData` plus token map
  for a Flutter project, validate generated widgets against M3 guidelines,
  and surface platform-specific a11y findings.
- **Effort:** L
- **Dependencies:** `forge:design-tokens-gen` for the upstream token shape;
  existing forge Flutter skills (`dart-fix-runtime-errors`,
  `flutter-fix-layout-issues`).
- **Source signal:**
  - `existing-tools.md` G4 ("Flutter / cross-platform design discipline") —
    "All surveyed tools target web. None address Flutter theming, Material 3
    token structures, or platform-specific accessibility. A forge design
    skill that generates ThemeData-compliant components has no existing
    equivalent." Forge already operates in Flutter contexts.

---

## Next-up recommendation

The next parking-lot epic should pick up **candidates 1, 2, and 3** in that
order. Rationale:

- **#1 `forge:design-tokens-gen` first** — it's a blocker for #4, #6, #8,
  #10. It also closes the most cited gap (`existing-tools.md` G1) and turns
  the inert `design/tokens.json` stub that `forge:design-bootstrap` branch
  (c) leaves behind into a working build artifact. Without it, every
  downstream design skill has to either re-derive tokens or fall back to
  hardcoded values.
- **#2 `forge:design-source-v0` second** — closes an explicit TODO already
  written into the shipped `forge:design-source` skill (#76), uses the
  recommendation made in the `external-generators.md` survey verbatim, and
  is the lowest-risk way to validate that an API-driven generator path
  works inside forge's skill model. Effort is M because the fallback path
  already exists.
- **#3 `forge:design-a11y-brief` third** — small effort (S), no upstream
  dependencies, and addresses a gap (`existing-tools.md` G6) that no other
  surveyed tool covers. Posting the brief to the tracker also exercises
  `existing-tools.md` G2 (tracker integration) cheaply, derisking the
  pattern for #5 and #7 later.

Held back for a follow-up epic: #4 (`forge:figma-implement`) is high-value
but L-effort and overlaps the official Anthropic `figma` plugin — worth a
brainstorming gate before commitment. #5 and #6 depend on the tokens skill
landing first.

---

## Calibration after #69

> Placeholder — re-run this synthesis once `plugins/forge/docs/design-research/
> article-digest.md` (or equivalent) from #69 exists.

Expected recalibration angles when the user's article list lands:

- **Priority shifts.** The article digest may surface workflow patterns or
  pain points that bump a P2 candidate (e.g. #7 critique, #9 Storybook) up
  to P0/P1, or demote a current P0 if it solves a problem the user does not
  actually have.
- **New candidates.** Articles may name specific tools (Penpot, design-token-
  validator, visual-regression services) not covered by #70-#73. Add as #11,
  #12, ... under the appropriate priority tier with the article cite as
  source signal.
- **Effort recalibration.** First-hand reports of integration friction (e.g.
  "Code Connect setup is a half-day per project") may reshape S/M/L sizing.
- **Scope contraction.** If the article digest reveals strong preference for
  one stack (web only, Flutter only), Flutter-specific #10 may become P0 or
  may be removed entirely.

Update procedure: edit this file in place, bump the synthesis date, and
record the recalibration in the EPIC G epic body as a comment so the
decision trail is visible.
