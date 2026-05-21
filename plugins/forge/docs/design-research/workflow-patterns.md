# Design-First Workflow Patterns

Survey of mainstream design-first practices for frontend product engineering.
Covers: Figma → code handoff, design system governance, spec documentation,
and iteration cycles. Closes with a minimal viable workflow recommendation for
AI-driven solo-developer projects.

---

## 1. Figma → Code Handoff

### 1a. Dev Mode + Annotations (mainstream)

Figma Dev Mode gives every viewer access to inspect CSS/Swift/Android snippets,
component properties, and spacing values directly on any frame. Designers mark
frames as "Ready for development" to signal handoff state. Annotations layer
on top: designers embed callouts for motion specs, accessibility notes, and
edge-case states that raw inspection misses.

**Workflow cadence:**
1. Designer marks section "Ready for dev" on a dedicated handoff page.
2. Developer opens Dev Mode, inspects properties, reads annotation comments.
3. Mismatches are filed as Figma comments and resolved before closing the
   ticket.

**Fit:** Teams of 2+. Low tooling overhead. Breaks down when comments pile up
without resolution discipline.

### 1b. Code Connect (mainstream)

Figma Code Connect maps a Figma component to the real implementation in the
codebase. When a developer inspects a `Button` in Dev Mode, they see the actual
`<Button variant="primary" />` import from the project's component library
instead of generated CSS.

**Setup cost:** Medium. Requires a config file (`figma.config.json`) and a
CLI sync step. Pays off immediately on design system teams where component
reuse is high.

**Key benefit:** Eliminates the "generated code is not real code" problem.
Developers trust what they see; designers verify parity by looking at the same
component.

### 1c. AI-Assisted Handoff / Figma Make (emerging, less common)

Figma's own AI features (Figma Make, AI acceptance-criteria generator) and
third-party agents (AgentC2) can monitor a Figma file for frame changes,
extract specs, and create tracker tickets with design links and pre-filled
acceptance criteria within minutes.

**Interesting because:** For a solo developer + AI agent, this collapses the
handoff step entirely — the AI reads the frame and writes the ticket. Still
early: output quality depends on component naming discipline and token adoption.

---

## 2. Design System Governance

### 2a. Centralized Token Guardian (mainstream)

One person or a small design-system team owns the token source of truth,
typically stored in a JSON or YAML file that feeds both Figma variables and
the codebase via a build step (Style Dictionary, Theo, Supernova).

**Who owns tokens:** Design-system lead (often a hybrid designer/engineer).
**Sync mechanism:** Token file in version control → CI publishes to npm →
components import from package. Figma variables stay in sync via a plugin
(Token Studio, Supernova).

**Strength:** Single changelog, clear ownership. **Weakness:** Bottleneck
on a small team; PRs pile up.

### 2b. Federated / Contribution Model (mainstream, larger teams)

Core system team owns primitives (colors, spacing, typography). Product teams
own domain-specific patterns (e.g., dashboard widgets). Contributions flow
back to core via a defined proposal → review → publish process.

**Token ownership:** Split. Primitives = core team. Semantic / component tokens
= feature team proposes, core team reviews.

**Sync mechanism:** Automated compliance checks in CI (lint-tokens, visual
regression). Governance failures block PRs, not human reviews.

**Interesting quirk:** Teams that build compliance into CI rather than
relying on design review catch ~70% of token drift before production (Miro
governance report).

### 2c. Continuous Token Sync via Design Tokens W3C Format (less common, growing)

The W3C Design Tokens Community Group specification standardises token JSON,
enabling tool-agnostic pipelines. Figma variables export → DTCG JSON → Style
Dictionary → platform outputs. No proprietary lock-in.

**Interesting because:** An AI agent can parse DTCG JSON without bespoke
tooling and validate that a component's inline styles match declared tokens —
a natural forge automation hook.

---

## 3. Spec Documentation Patterns

### 3a. Spec Co-located in Figma (mainstream)

Annotations, component descriptions, and interaction notes live inside the
Figma file itself. FigJam pages hold context, user-story maps, and decision
logs adjacent to the design frames.

**Pros:** Single source of truth. Designers and developers look at the same
artefact. No doc drift. **Cons:** Specs are buried; no searchable text outside
Figma; hard to link from a tracker ticket.

### 3b. Linked PRD / Design Doc in Notion or Coda (mainstream)

A separate document (Notion page, Coda PRD, Confluence page) holds user
stories, acceptance criteria, and open decisions. The doc embeds or links to
Figma frames. Tracker tickets reference the doc section.

**Pattern:** `Ticket → PRD section → Figma frame → component story`.

**Strength:** Searchable, commentable, version-controlled in the doc tool.
**Weakness:** Doc diverges from Figma as designs iterate; requires discipline
to keep both updated.

### 3c. Design Acceptance Criteria in the Tracker Ticket (less common, recommended for AI workflows)

Acceptance criteria are written directly on the tracker ticket as a checklist
derived from the Figma frame: states, breakpoints, tokens used, animation
spec. A Figma frame URL is attached to the ticket.

**Format example:**
```
AC:
- [ ] Button renders with primary token bg (#design-token: color.action.primary)
- [ ] Disabled state reduces opacity to 0.4
- [ ] Touch target ≥ 44 × 44 pt on mobile
- [ ] Matches Figma frame: <url>#node=<id>
```

**Interesting because:** This is what forge's execute-ticket already reads to
generate implementation plans. When designers write ACs in this format, the
AI can verify them against code without a separate spec step.

---

## 4. Iteration Patterns (Sketch → High-Fi → Handoff)

### 4a. Linear Fidelity Progression (mainstream)

1. **Sketch / wireframe** — structure and flow only (Balsamiq, FigJam, paper).
2. **Mid-fi mockup** — layout, spacing, component placeholders (Figma, no
   real tokens applied).
3. **High-fi design** — real tokens, variants, interaction states.
4. **Handoff** — Dev Mode annotation + "Ready for dev" mark.
5. **Commit** — developer implements, screenshots compared to Figma in PR.

**Gate between high-fi and handoff:** Designer review + stakeholder sign-off.
Commits only happen in the handoff phase.

### 4b. Component-Driven Development / Storybook-First (mainstream)

Components are built in isolation in Storybook *during* development, not after
design completes. Stories are the first deliverable, not the last. The
workflow:

1. Design defines the component API (props, variants) in Figma.
2. Developer writes a Storybook story for each variant before implementing.
3. Designer reviews the story in isolation — no full-app context needed.
4. Template- and page-level stories compose atoms into screens.

**Brad Frost's framing:** Storybook is the "workshop" where all UI code is
built; the design system is the product, not a side-effect. Stories become the
living spec. Commits happen story-by-story.

**Fit for AI agents:** AI can generate a story scaffold from a Figma frame +
Code Connect mappings, then run Storybook CI to verify it renders.

### 4c. Continuous Design — Commits Tied to Figma Version History (less common)

Some teams treat Figma version history as the design changelog and tie it to
Git commits. A Figma plugin (Figma Tokens, Supernova) triggers a CI pipeline
that updates token files and opens a PR when a designer publishes a library
update.

**Interesting because:** Design commits and code commits share a causal link.
Designers don't hand off; they trigger handoff. The iteration loop becomes:
design change → automated PR → developer reviews diff → merge.

---

## 5. Minimal Viable Design Workflow for AI-Driven Product Engineering

This is the baseline forge should expect from any frontend project that wants
AI-assisted implementation to work reliably.

### Must-Haves

| Requirement | Why it matters for AI execution |
|---|---|
| **Figma file with component naming matching codebase** | Code Connect and frame-to-ticket extraction only work if names match. |
| **Design tokens in version-controlled JSON** | AI can validate inline styles against declared tokens; catches drift without manual review. |
| **One Figma URL per tracker ticket** | forge's execute-ticket reads the frame to generate an implementation plan and acceptance criteria. |
| **Acceptance criteria written on the ticket** | The AI's primary spec input. Checklist format preferred (state, token, dimension, URL). |
| **"Ready for dev" marker on frames** | Prevents AI agents from implementing in-progress designs. |

### Recommended (not required)

- **Code Connect config** — developers see real component code in Dev Mode.
- **Storybook stories** — AI can verify component renders in isolation before
  full integration.
- **DTCG token format** — future-proofs against tooling changes; enables
  programmatic validation.

### What to Skip for Solo-Dev / AI Workflows

- **Federated contribution governance** — only relevant at 5+ engineer teams.
- **Separate PRD documents** — the ticket + Figma frame is sufficient; a
  parallel doc creates sync debt with no one to maintain it.
- **Linear fidelity progression gates** — a solo developer with AI assistance
  can jump from mid-fi Figma frame to a Story scaffold without a formal
  sign-off step; the AI PR review substitutes.

---

## Sources

- Figma — [Guide to developer handoff](https://www.figma.com/best-practices/guide-to-developer-handoff/)
- Figma — [Guide to Dev Mode](https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode)
- Miro — [Design System Governance](https://miro.com/research-and-design/design-system-governance/)
- Brad Frost — [Atomic Design and Storybook](https://bradfrost.com/blog/post/atomic-design-and-storybook/)
- DOOR3 — [Establishing Effective Design Token Governance](https://www.door3.com/blog/design-token-governance)
- Figma — [AI Acceptance Criteria Generator](https://www.figma.com/solutions/ai-acceptance-criteria-generator/)
- AgentC2 — [Figma AI Agent: From Design to Dev Ticket](https://agentc2.ai/blog/figma-ai-agent-design-handoff)
- Supernova — [Design Tokens 2024 insights](https://www.supernova.io/blog/navigating-the-future-of-design-tokens-insights-from-supernovas-2024-webinar)
