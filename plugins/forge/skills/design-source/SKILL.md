---
name: design-source
description: Produce a design source for a frontend epic via one of three branches — co-create with Claude, generate an external-tool prompt, or render three HTML variations for the user to pick.
type: hybrid
inspired-by:
  - author: mattpocock
    repo: github.com/mattpocock/skills
    skill: variations
    relation: concept
---

# design-source

When a frontend-related epic is missing a design source, this skill produces one. The output is a single artifact (textual mock, external-tool URL, or selected HTML route) ready to embed in the epic body under `## Design source`.

## When invoked

Designed to be invoked by `forge:create-epic` when the draft epic touches a UI platform (web/mobile) AND no design source is detected (no Figma URL, no HTML mockup, no screenshot, no component reference). Wiring into `forge:create-epic` is a follow-up — track under the same future wiring epic as `forge:design-bootstrap` (or the next EPIC G follow-up). The skill is also callable standalone for ad-hoc design exploration.

## Contract

Given an epic draft (title + goal + UI surface), interview once for the branch choice, then run the chosen branch to produce a design artifact. The artifact is returned to the caller as text ready to paste under `## Design source` in the epic body.

## Decision tree

Ask the user once, with these three branches as multiple choice. Recommend branch 1 for simple flows, branch 2 when the user already pays for a generator, branch 3 when the visual direction is genuinely unclear.

```
Branch 1: Co-create with Claude (textual mock + ASCII wireframe)
Branch 2: External generator prompt (Stitch / v0.dev / Lovable / Galileo / ...)
Branch 3: Three HTML variations (mattpocock-style), user picks one
```

### Branch 1 — co-create with Claude

1. Draft a textual mock: page title, key sections, primary actions, empty/error states.
2. Render an ASCII wireframe (monospace box-drawing) for the main screen.
3. Iterate with the user — `keep / change <section> / restart`. Cap iterations at five; if not converged, suggest branch 2 or 3.
4. Emit the final mock as the artifact. No files written.

### Branch 2 — external generator prompt

1. Choose the target generator. Until the `#71` survey lands, ask the user which they prefer (Stitch, v0.dev, Lovable, Galileo, or other) and forward as-is. TODO: once `forge/docs/design-research/external-generators.md` exists, replace the freeform ask with a generator-specific prompt template lookup.
2. Generate a prompt the user runs externally. Required slots: product domain, page purpose, primary user, must-have sections, brand/style cue, output format (URL, HTML, Figma link).
3. Wait for the user to paste back the generator's output (URL or HTML/Figma link).
4. Emit that artifact unchanged as the design source. No files written.

### Branch 3 — three HTML variations

1. Generate three radically different prototypes for the same screen (different IA, different visual direction).
2. File layout — each variation is a standalone `index.html` under `design-explorations/<epic-id>/{a,b,c}/index.html`. No framework, no build, inline CSS, no JS unless interaction is the question.
3. Ask the user to open each, then prompt: `which works best? a / b / c / none / iterate-X` (where X is one of a/b/c).
4. On `iterate-X`, regenerate that variant in place (overwrite same file) and re-ask.
5. On `a/b/c`, delete the two non-chosen variants and keep the chosen one. The chosen `index.html` path is the design artifact (referenced as a relative path in the epic body).
6. On `none`, delete the entire `design-explorations/<epic-id>/` directory and fall back to branch 1 or 2.

Full layout and prompt details — `references/branch-3-variations-pattern.md`.

## Output contract

The skill returns a single block formatted for direct paste:

```
## Design source
<branch-1 textual mock | branch-2 URL/HTML/Figma link | branch-3 relative path>
```

No commits, no epic edits — the caller (`forge:create-epic` or the user) places the block.

## What this skill does not cover

- Detecting whether an epic needs a design source — that's the caller's job.
- Editing the epic body — caller responsibility.
- Production-grade design tokens, component libraries, or Figma authoring — see `forge:design-bootstrap` (when it lands) and the figma plugin skills.
- Persisting branch-3 explorations long-term — by design they live under `design-explorations/` and are gitignored at the project level (configure once per project).
