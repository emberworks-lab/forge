---
name: improve-codebase-architecture
description: Surface architectural deepening opportunities — refactors that turn shallow modules into deep ones — informed by the project's CONTEXT.md domain language and docs/adr/ decisions.
type: hybrid
inspired-by:
  - author: mattpocock
    repo: github.com/mattpocock/skills
    skill: improve-codebase-architecture
    relation: adapted
---

# Improve Codebase Architecture

Find **deepening opportunities**: refactors that trade a wide, leaky interface for a deep one — high leverage behind a small surface. The payoff is testability (the interface becomes the test surface) and AI-navigability (complexity concentrates in one place a navigator can reason about).

This is the higher-level counterpart to `forge:simplify-branch`. That skill cleans the diff you just wrote (reuse, quality, efficiency — local, mechanical). This skill steps back from the diff and asks whether a module's *shape* is wrong. Run `forge:simplify-branch` to tidy a branch; run this when modules feel shallow, tangled, or untestable through their current interface. They do not overlap.

## Glossary discipline

Every suggestion uses the glossary terms **exactly**: module, interface, implementation, depth, deep/shallow, seam, adapter, leverage, locality. Do not drift into "component," "service," "API," or "boundary" — consistent language is the leverage. Full definitions plus the three working principles (deletion test, interface-as-test-surface, one-adapter-vs-two): `references/glossary.md`.

Two vocabularies, never mixed: **CONTEXT.md vocabulary** names the domain ("the Order intake module"); **glossary vocabulary** names the architecture ("a shallow module leaking across its seam"). Never "the FooBarHandler," never "the Order service."

## Process

### 1. Explore

Read the project's `CONTEXT.md` domain glossary and any relevant `docs/adr/` files **first** — the domain language gives names to good seams, and ADRs record decisions this skill must not re-litigate.

Then walk the codebase. If the area is large, spawn an **opus** explorer-agent (architectural friction is a nuanced read, not a mechanical scan); for a small surface, walk it inline. Do not chase rigid heuristics — explore organically and note friction:

- Understanding one concept requires bouncing between many small modules.
- A module is **shallow** — its interface is nearly as complex as its implementation.
- Pure functions extracted only for testability, while the real bugs hide in how they are called (no **locality**).
- Tightly-coupled modules leaking across their seams.
- Code that is untested or hard to test through its current interface.

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity (it earns its keep) or just move it around (it is a pass-through)? "Concentrates" is the signal worth surfacing.

### 2. Present candidates

Emit a numbered list of deepening opportunities. Per candidate, follow the template in `references/suggestion-template.md`: Files, Problem, Solution (plain English), Benefits (framed in locality, leverage, and how tests improve).

**ADR conflicts:** only surface a candidate that contradicts an existing ADR when the friction is real enough to warrant reopening that ADR. Mark it explicitly — *"contradicts ADR-0007, but worth reopening because…"*. Do not list every theoretical refactor an ADR forbids.

Do **not** propose interfaces yet. Close with: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation (the discipline of `forge:grill-me`): walk the design tree one branch at a time — constraints, dependencies, the shape of the deepened module, what sits behind the seam, which tests survive.

Side effects land inline as decisions crystallize:

- **Naming a deepened module after a concept absent from `CONTEXT.md`** → add the term to `CONTEXT.md`. Create the file lazily if it does not exist.
- **Sharpening a fuzzy term mid-conversation** → update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason** → offer an ADR: *"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"* Only offer when the reason would actually stop a future explorer from re-suggesting the same thing. Skip ephemeral reasons ("not worth it right now") and self-evident ones.

## What this skill does not do

- It does not edit code or open PRs — it surfaces opportunities and grills the chosen one toward a design.
- It does not clean a diff for reuse/quality/efficiency — that is `forge:simplify-branch`.
- It does not re-litigate settled ADRs — only reopens one when friction is load-bearing.
