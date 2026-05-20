---
name: prototype
description: Build a throwaway prototype to answer a design question before committing — routes to a terminal logic app or multiple UI variations depending on the question being asked.
type: hybrid
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → Build a tiny interactive terminal app that pushes the state machine through cases that are hard to reason about on paper.
- **"What should this look like?"** → Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules for both branches

See `references/prototype-rules.md` for the six rules that apply regardless of branch.

## When done

The *answer* is the only thing worth keeping. Capture it somewhere durable (commit message, ADR, issue, or a `NOTES.md` next to the prototype) along with the question it was answering. If the user is around, that capture is a quick conversation; if not, leave the placeholder so they can fill in the verdict before deleting the prototype.
