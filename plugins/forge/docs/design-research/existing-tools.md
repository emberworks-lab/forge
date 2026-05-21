# Design Ecosystem Survey — Existing Tools

_Surveyed: 2026-05-21. Refs #70._

Covers mattpocock/skills, obra/superpowers, the Anthropic official plugin
marketplace, and selected community repos. Goal: understand what already
exists before specifying what forge should build.

---

## 1. mattpocock/skills

Source: https://github.com/mattpocock/skills

Engineering-focused skill library. Matt Pocock runs Total TypeScript; the
skills reflect a TypeScript-first, clean-interface philosophy. Two skills
touch UI/design territory.

### 1a. `prototype` (engineering/prototype)

- **Link:** `skills/engineering/prototype/` — `SKILL.md` + `UI.md` + `LOGIC.md`
- **Summary:** Routes between two prototype shapes. The UI branch generates
  3–5 radically different layout variants on a single route, switchable via
  `?variant=` URL param and a floating bottom bar. Enforces "structurally
  different" variants (different layout hierarchy, not just colour tweaks).
  The logic branch builds a terminal app to stress-test a state machine.
  Both shapes are explicitly throwaway — the skill mandates deletion or
  absorption once the question is answered.
- **Relevance to forge:** HIGH. This is the most complete AI-driven UI
  exploration skill in the open ecosystem. The `?variant=` switcher pattern
  is practical and immediately usable. Forge's own `prototype` skill is a
  direct derivative. Gap: no design-token awareness, no accessibility check,
  no design-system integration.

### 1b. `design-an-interface` (deprecated)

- **Link:** `skills/deprecated/design-an-interface/SKILL.md`
- **Summary:** Spawns 3+ sub-agents, each with a different constraint
  ("minimize method count", "maximize flexibility", "optimize for common
  case"), to produce radically different API/module interface designs.
  Grounded in Ousterhout's "Design It Twice" principle. Purely about API
  shape — not visual UI.
- **Relevance to forge:** MED. Proves the multi-agent parallel-design
  pattern is battle-tested. The constraint-per-agent approach is worth
  borrowing for visual design exploration. The skill is deprecated upstream,
  suggesting the `prototype` skill absorbed its spirit.

---

## 2. obra/superpowers

Source: https://github.com/obra/superpowers

The largest community skill framework (40 k+ stars). Structures the full
dev lifecycle: brainstorm → plan → subagent execution → TDD → review.
Skill list (as of survey): brainstorming, dispatching-parallel-agents,
executing-plans, finishing-a-development-branch, receiving-code-review,
requesting-code-review, subagent-driven-development, systematic-debugging,
test-driven-development, using-git-worktrees, using-superpowers,
verification-before-completion, writing-plans, writing-skills.

**No dedicated design or UI skill exists in the core superpowers set.**

The framework does include a UI quality audit capability (mentioned in
release notes and community write-ups) that checks generated UI code
against 100+ rules covering ARIA attributes, visible focus states, touch
target sizes, reduced-motion support, semantic HTML, and keyboard
navigation. This surfaces as part of code review, not as a standalone
design skill.

### 2a. UI quality audit (embedded in code-review flow)

- **Link:** https://github.com/obra/superpowers (no dedicated skill file —
  bundled into review flow)
- **Summary:** When reviewing frontend code, superpowers checks against an
  internal checklist of accessibility and UX anti-patterns. Covers WCAG-
  adjacent rules: labelled inputs, heading hierarchy, ARIA roles, touch
  targets, focus management. Not user-invokable as a standalone command.
- **Relevance to forge:** MED. Confirms the accessibility-in-review pattern
  is valued by the community. Forge could surface this as an explicit,
  invokable skill rather than a buried review step.

---

## 3. Anthropic official plugin marketplace (claude-plugins-official)

Source: https://github.com/anthropics/claude-plugins-official
Browsable at: https://claude.com/plugins

Anthropic maintains an official, curated directory of high-quality plugins.
Three design-adjacent entries are directly relevant.

### 3a. `design` plugin

- **Link:** https://claude.com/plugins/design
- **Summary:** Accelerates design-team workflows. Four capabilities:
  (1) Design Critique — reviews mockups for usability and design-system
  consistency; (2) UX Writing — generates microcopy for interface elements;
  (3) Accessibility Audit — evaluates against WCAG 2.1 AA; (4) Research
  Synthesis — transforms user interview findings into actionable insights.
  Intended for product/design teams, not necessarily developers. No code
  generation.
- **Relevance to forge:** MED. Covers the design-review and research side
  well. Does not generate or modify code, so it's complementary rather than
  competitive with a developer-facing forge skill.

### 3b. `frontend-design` plugin

- **Link:** https://claude.com/plugins/frontend-design — 760 k+ installs
- **Summary:** Activates when users request frontend work. Establishes an
  aesthetic framework (brutalist / maximalist / retro-futuristic / luxury /
  playful, etc.) before writing code. Focuses on typography (unexpected font
  pairings), motion (scroll-triggered effects), spatial composition
  (asymmetry, grid-breaking), and visual depth (gradients, textures).
  Explicitly avoids "generic AI aesthetics" — purple gradients, system
  fonts, cookie-cutter components. Supports React, Vue, Svelte, vanilla
  HTML/CSS.
- **Relevance to forge:** HIGH. Most popular design-adjacent plugin in the
  marketplace. Sets the baseline expectation users have. Forge's UI skill
  needs to either integrate with this aesthetic layer or offer a
  design-system-first alternative. Gap: no Figma integration, no design
  token enforcement, no accessibility pass.

### 3c. `figma` plugin (official, Anthropic-verified)

- **Link:** https://claude.com/plugins/figma — 128 k installs
- **Summary:** Bridges Figma and code. Three commands:
  `/implement-design` (translates Figma frames to code using the project's
  design system), `/create-design-system-rules` (generates team conventions
  from a Figma file), `/code-connect-components` (links Figma components to
  codebase components). Uses Code Connect. Supports cloud and desktop Figma.
- **Relevance to forge:** HIGH. Forge ships the Figma MCP server and
  figma-related skills. This official plugin represents Anthropic's own
  answer; forge skills should complement (deeper workflow, more opinionated
  process) rather than duplicate these three commands.

---

## 4. Community: selected notable repos

These are not from mattpocock or obra but appeared consistently in search
results and represent the community baseline.

### 4a. `phazurlabs/ux-ui-mastery`

- **Link:** https://github.com/phazurlabs/ux-ui-mastery
- **Summary:** 19 skill domains, 55 reference docs, 10 commands, 310 k+
  words of theory. Commands include `/ux-audit` (Nielsen heuristics),
  `/accessibility-check` (WCAG 2.2/3.0), `/generate-design-tokens` (W3C
  token format), `/ai-ux-audit` (trust/safety for AI features), and
  `/figma-to-code`. Covers emerging topics: agentic UX, spatial design,
  ambient / zero UI. Activated progressively by user query.
- **Relevance to forge:** MED. Encyclopedic rather than opinionated. The
  breadth (310 k words) is a liability in token-constrained sessions. Forge
  should be narrower and more actionable per session. Notable: `/ai-ux-audit`
  for trust and safety in AI feature UX has no equivalent elsewhere — worth
  borrowing as a concept.

### 4b. `nextlevelbuilder/ui-ux-pro-max-skill`

- **Link:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Summary:** Design System Generator. Runs 5 parallel queries (products,
  styles, palettes, patterns, typography) against a built-in corpus of 67
  UI styles, 161 color palettes, 57 font pairings, and 161 industry-specific
  rules. Outputs a complete, customized design system for the described
  product. CLI-installable (`npm install -g uipro-cli`). Slash command
  `/ui-ux-pro-max`.
- **Relevance to forge:** MED. Good pattern: parallel search over a curated
  corpus before generating tokens. The corpus itself is static/hardcoded,
  not connected to the project's existing design system. Forge's design-init
  skill could improve on this by reading the project's existing tokens first.

### 4c. `senlindesign/claude2figma`

- **Link:** https://github.com/senlindesign/claude2figma
- **Summary:** Four skills that enforce design system compliance when writing
  to Figma: `figma-preflight` (MCP health check), `component-rules`
  (library-first lookup, Auto Layout enforcement), `figma-style-binding`
  (every color/font/spacing must reference a Variable or Style, not a
  hardcoded value), `reference-interpreter` (converts screenshots/URLs/
  descriptions to a structured design brief before construction). Best for
  building pages inside an existing design system, not for greenfield.
- **Relevance to forge:** HIGH. The `figma-style-binding` enforcement loop
  (search → instance → bind → verify) is the most rigorous token-discipline
  skill found in the survey. Directly relevant to any forge figma skill that
  writes back to Figma. The `reference-interpreter` pattern (brief before
  action) maps well to forge's own grill-me / brainstorm gating.

---

## Gap Analysis

Based on the survey, the following areas are NOT adequately covered by
existing tools — these represent what forge could uniquely provide:

### G1. Design-system-aware code generation (project-local tokens)
`frontend-design` and `ui-ux-pro-max` generate visually polished UIs but
ignore the project's existing design system. `claude2figma` enforces token
binding inside Figma but not in generated application code. No existing
skill reads the project's token file (e.g. `design-tokens.json`,
`tailwind.config.ts`, CSS custom properties) and generates UI that references
those specific values. Forge should fill this with a design-init / design-
codegen skill that opens the token file first.

### G2. Tracker-integrated design workflow
No existing tool ties design decisions to a ticket system. Forge's execute-
ticket + execute-epic infrastructure means design exploration (prototype
variants, accessibility pass, design-critique results) can be attached to
Linear issues as comments, closing the loop between design decisions and
tracked work. This is uniquely possible within forge's architecture.

### G3. Opinionated end-to-end design-to-code flow
The Anthropic `figma` plugin offers three discrete commands. `phazurlabs/
ux-ui-mastery` offers 10 separate commands. Neither provides a guided,
sequential workflow: brief → token audit → prototype variants → pick →
implement → accessibility check → commit. Forge can wrap these steps into a
single `execute-ticket` path for design tickets, the same way it does for
engineering tickets.

### G4. Flutter / cross-platform design discipline
All surveyed tools target web (React/Vue/Svelte) or Figma. None address
Flutter theming, Material 3 token structures, or platform-specific
accessibility (iOS/Android). Forge operates in a Flutter context (dart-fix,
flutter-fix-layout-issues skills exist). A forge design skill that generates
ThemeData-compliant components and validates against Material 3 guidelines
has no existing equivalent.

### G5. Design-decision capture (ADR/NOTES pattern)
`mattpocock/prototype` mandates capturing the design verdict before deletion.
No other tool does this. Forge's forge:commit and handoff patterns could
extend this discipline to every design decision — writing a lightweight
design ADR or updating the Linear ticket with the rationale, not just the
implementation.

### G6. Accessibility-first gating (not post-hoc auditing)
Existing tools audit accessibility after the fact (`/accessibility-check`,
superpowers review checklist). No skill gates implementation on a prior
accessibility brief: "before writing any UI code, enumerate the a11y
requirements for this component." Forge could introduce an
`accessibility-brief` step as a required gate inside design ticket execution,
catching issues at design time rather than review time.

---

_Sources consulted:_
- https://github.com/mattpocock/skills
- https://github.com/obra/superpowers
- https://github.com/anthropics/claude-plugins-official
- https://claude.com/plugins/design
- https://claude.com/plugins/frontend-design
- https://claude.com/plugins/figma
- https://github.com/phazurlabs/ux-ui-mastery
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- https://github.com/senlindesign/claude2figma
