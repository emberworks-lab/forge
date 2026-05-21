# External AI Design Generators — Survey

> Refs #71 — Last updated: 2026-05-21

Survey of six AI-driven UI/design generators for potential integration into
`forge:design-source`. Each profile covers what the tool does, how you feed
it, what comes out, pricing, best-fit use case, and a concrete integration
angle for the skill.

---

## 1. Google Stitch (`stitch.withgoogle.com`)

**What it does.**
Stitch is Google Labs' text-to-UI design platform. Users describe an
application in plain English (or upload a rough sketch / whiteboard photo),
and Stitch generates high-fidelity, multi-screen UI designs with a consistent
design system across all screens. The March 2026 update added "vibe design" —
a conversational canvas where the AI interviews you in real time — plus a
5-screen multi-flow generator and Voice Canvas. Galileo AI (formerly a
standalone competitor) was acquired by Google in May 2025 and its technology
was folded into Stitch; Galileo no longer operates as a separate product.

**Input modality.**
- Text prompt (natural language description)
- Image upload: napkin sketch, whiteboard photo, app screenshot
- Structured `design.md` brief

**Output.**
- Interactive multi-screen prototype (viewable in-browser)
- Figma-ready export (paste into Figma with editable layers)
- HTML/CSS front-end code download
- `.zip` project bundle
- MCP server integration (connect to Cursor, Blackbox, etc.)

**Pricing.**
Free — no subscription required. Credit-gated: 400 design credits + 15
redesign credits per day (~12 450/month). No paid tier to unlock more; credits
simply reset daily.

**Best-fit use case.**
Rapid MVP validation, early-stage prototyping where a product manager or solo
developer needs a polished wireframe before committing to Figma work. Also
useful for generating a visual brief that designers can refine.

**Integration angle for `forge:design-source`.**
No public API; UI-only. The wrapping pattern is a **prompt-recipe + manual
handoff**: the skill generates an optimised Stitch prompt from the ticket
context, instructs the user to paste it at `stitch.withgoogle.com`, then
guides them to export HTML/CSS or paste the Figma export back for the next
step. Because Stitch also exposes an MCP server, a future enhancement could
wire it into Claude Code's tool registry directly — worth monitoring.

---

## 2. v0 by Vercel (`v0.app`)

**What it does.**
v0 is Vercel's AI code-generation tool that converts natural language prompts
(and optionally Figma imports on paid tiers) into production-ready React /
Next.js components and full-stack pages. By 2026 it supports full Next.js
sandboxes including API Routes and Server Actions, a built-in Git panel, and
direct one-click deployment to Vercel. Used by 6 million+ developers.

**Input modality.**
- Text prompt
- Figma import (Premium tier and above)
- Image/screenshot (paste into the chat)

**Output.**
- React / Next.js components (shadcn/ui + Tailwind CSS by default)
- Full-stack Next.js app with API routes
- Live preview deployable to Vercel
- Shareable component links

**Pricing.**
| Plan | Price | Credits |
|------|-------|---------|
| Free | $0 | $5/month, 7 msg/day |
| Premium | $20/month | $20/month + Figma import + API access |
| Team | $30/user/month | $30/user/month |
| Business | $100/user/month | Training opt-out |
| Enterprise | Custom | SSO, data protection |

Token-based pricing: v0 Mini ($1/$5 per 1 M input/output), v0 Pro ($3/$15),
v0 Max ($5/$25), v0 Max Fast ($30/$150).

**Best-fit use case.**
Developer-centric UI generation where the output is immediately deployable
React code, especially for teams already on the Vercel/Next.js stack. Ideal
for component scaffolding and quick landing pages.

**Integration angle for `forge:design-source`.**
The **strongest candidate for direct API wrapping** (Premium tier unlocks API
access). Pattern: skill calls v0 API with a structured prompt built from
ticket title + acceptance criteria → receives React component code → writes
it into the project's `components/` directory. On the free tier, fall back to
prompt-recipe + manual handoff (user pastes prompt at v0.app, copies output
back). The skill can detect whether `V0_API_KEY` is set in the environment to
switch between modes automatically.

---

## 3. Lovable (`lovable.dev`)

**What it does.**
Lovable is a full-stack AI app builder aimed at non-developers and rapid
prototypers. Users describe an app in plain English or drop in screenshots and
documents; Lovable generates a working React application, hosts it instantly
on a `lovable.app` subdomain, and supports real-time iteration via chat.
Natively integrates with Supabase (database), Stripe (payments), and third-
party APIs. Reached $200 M ARR and $6.6 B valuation (Series B, Dec 2025).

**Input modality.**
- Text prompt
- Screenshot / image upload
- Document upload (PDF, design brief)

**Output.**
- Hosted React application (deployed at `yourapp.lovable.app`)
- Editable source code (Pro tier)
- Custom domain deployment (Pro tier)

**Pricing.**
| Plan | Price | Credits |
|------|-------|---------|
| Free | $0 | 5 messages/day |
| Starter | $25/month | 100 generation credits |
| Pro | ~$50/month | More credits, custom domain, code editing |
| Enterprise | Custom | SSO, dedicated support, custom API |

Free workspaces receive $25 cloud credit + $1 AI credit/month through May 2026.

**Best-fit use case.**
Non-technical founders who need a working prototype fast, or developers
exploring a concept before writing any code. Not ideal when you need to merge
output into an existing codebase without manual cleanup.

**Integration angle for `forge:design-source`.**
UI-only; no public programmatic API for generation. Wrapping pattern is
**prompt-recipe + copy-paste**: skill produces a structured Lovable prompt
(app description + screen list + tech preferences) that the user runs at
lovable.dev, then pastes the exported code/URL back for downstream steps.
Lower priority than v0 for forge because output is a full hosted app, not
composable components.

---

## 4. Galileo AI (`usegalileo.ai`) — **Acquired; now Google Stitch**

**What it does.**
Galileo AI was a standalone text-to-UI design generator that produced
high-fidelity Figma frames from natural language prompts. Google acquired
Galileo in May 2025 and absorbed its technology into Stitch (Google Labs).
Galileo no longer operates as an independent product; existing users were
migrated to Stitch (conversation history importable as view-only).

**Input modality.** Text prompt, image reference (historical).

**Output.** Figma-ready designs, HTML/Tailwind CSS (historical; now via Stitch).

**Pricing.** Discontinued. Former plans: Standard $19/month (1 200 credits),
Pro $39/month (3 000 credits).

**Best-fit use case.** N/A — tool is sunset. See Stitch (§1).

**Integration angle for `forge:design-source`.**
None — do not wire Galileo. Reference Stitch instead. Keep this section for
historical context only; the survey ticket required profiling Galileo, but the
recommendation is to redirect to its successor.

---

## 5. Anima (`animaapp.com`)

**What it does.**
Anima is the leading Figma-to-code bridge, with 1.5 M users and native
integrations in Bolt.new and Replit. It converts Figma design files into
pixel-perfect React, HTML/CSS, Vue, or Tailwind CSS code, and also exposes a
UX co-pilot agent ("Buddy") that assists designers inside Figma. The Anima API
allows AI coding agents to request code generation from Figma URLs
programmatically, positioning it as "the design API for vibe coding platforms."

**Input modality.**
- Figma file URL (primary)
- Website URL (clone to code)
- Text prompt (via Buddy in-Figma agent)

**Output.**
- React, HTML/CSS, Vue, Tailwind CSS code packages
- LLM-friendly structured code output (optimised for agent consumption)
- Figma plugin exports (no Figma account needed on the API path)

**Pricing.**
| Plan | Price |
|------|-------|
| Free | 5 chat msg/day, 5 Figma imports/day, 5 code generations/day |
| Pro | $24/month (billed annually) |
| Enterprise | $500/month (SSO, SLA, compliance) |

SDK packages: `anima-sdk` (Node/server-side), `anima-sdk-react`.

**Best-fit use case.**
Teams with an existing Figma design system who want clean, framework-matched
code without manual translation. Perfect when designs are already finalised and
the gap is engineering time.

**Integration angle for `forge:design-source`.**
**Second-strongest candidate for direct API wrapping.** Pattern: if the user
supplies a Figma URL, the skill calls Anima API (`anima-sdk`) with the URL →
receives a code package in the target framework → writes files into the
project. API currently requires access request (not self-serve), so the skill
should gate this path on `ANIMA_API_KEY` being present and fall back to a
Figma-URL copy-paste recipe otherwise. Because Anima is already integrated
into Bolt.new and Replit, the pattern is proven.

---

## 6. Builder.io (`builder.io`)

**What it does.**
Builder.io is a visual development platform combining two products: **Fusion**
(AI-driven full-stack code generation) and **Publish** (visual CMS for
content teams). Visual Copilot converts Figma designs, text prompts, or
existing codebases into production-ready code that respects the project's
existing framework, design tokens, and component library. It integrates
natively with GitHub, GitLab, VS Code, Slack, and Jira, and uses Claude
Sonnet 4 as its default model (with GPT and Gemini available).

**Input modality.**
- Figma design import
- Text prompt
- Existing codebase (for refactoring / extension)

**Output.**
- Framework-matched production code (React, Angular, Vue, Next.js, Qwik, etc.)
- Visual CMS content blocks (Publish product)
- Code committed directly to repo via GitHub integration

**Pricing.**
| Plan | Price | AI Credits |
|------|-------|------------|
| Free | $0 | 75 agent credits/month |
| Pro (Fusion) | $30/user/month | 500 credits/user/month |
| Pro (full platform) | $49/user/month | 500 credits/user/month |
| Enterprise | Custom | Custom |

**Best-fit use case.**
Established product teams that need AI-assisted development within an existing
codebase, with governance over which AI models are used and where code lands.
Strong fit for content-heavy apps needing a CMS layer alongside generated UI.

**Integration angle for `forge:design-source`.**
Builder.io has an SDK and GitHub-native workflow but no simple one-shot API
suitable for forge's `design-source` skill. Its strength is platform-level
integration (whole-repo context) rather than component-level generation.
Wrapping pattern would be **environment setup + CLI-driven generation**, which
requires persistent project configuration beyond what a skill invocation can
set up cleanly. Lower priority for forge.

---

## Comparison Table

| Tool | Input | Output | API? | Free tier | Best for |
|------|-------|--------|------|-----------|----------|
| **Stitch** (Google) | Prompt, sketch, image, design.md | Figma export, HTML/CSS, prototype | MCP server (no REST API) | Yes (400 credits/day) | Early prototyping, MVP briefs |
| **v0** (Vercel) | Prompt, Figma (paid), image | React/Next.js, live preview | Yes (Premium+) | Yes ($5 credits/month) | Component & page scaffolding |
| **Lovable** | Prompt, screenshot, doc | Hosted React app | No (UI-only) | Yes (5 msg/day) | Full-app prototyping, non-dev founders |
| **Galileo AI** | Prompt, image | Figma, HTML/Tailwind | Discontinued | Discontinued | See Stitch |
| **Anima** | Figma URL, website URL, prompt | React/HTML/Vue/Tailwind pkg | Yes (`anima-sdk`) | Yes (5/day limits) | Figma-to-code, design-system teams |
| **Builder.io** | Figma, prompt, codebase | Framework-matched code, CMS blocks | SDK/GitHub (no simple REST) | Yes (75 agent credits/month) | Enterprise, content-heavy apps |

---

## Recommendation

### Wire into `forge:design-source`: **v0 + Anima**

**v0 (Vercel)** — primary integration, covers the "generate from prompt"
path. The REST API (available on the $20/month Premium tier) accepts a text
prompt and returns React/Next.js code. The skill pattern:

1. Build a structured prompt from the ticket title, acceptance criteria, and
   tech-stack context in `CLAUDE.md`.
2. If `V0_API_KEY` is set: POST to v0 API → write files to `components/`.
3. If not set: emit a formatted prompt the user pastes at `v0.app`, then
   ingest the copy-pasted code.

**Anima** — secondary integration, covers the "generate from Figma" path.
The `anima-sdk` package converts a Figma URL into a framework-specific code
package. The skill pattern:

1. Detect a Figma URL in the ticket or user input.
2. If `ANIMA_API_KEY` is set: call `anima-sdk` → unpack the code package into
   the project.
3. If not set: emit the Figma URL + framework preference so the user runs the
   Anima Figma plugin and pastes back generated code.

**Why not the others:**
- Stitch: no REST API; MCP server is promising but not stable enough for
  automated wrapping yet. Keep on watch list for MCP-native integration.
- Lovable: outputs a full hosted app, not composable components; doesn't fit
  forge's per-ticket code-generation model.
- Galileo: discontinued.
- Builder.io: platform-level tool, not a single API call; overhead exceeds
  benefit for per-ticket design tasks.
