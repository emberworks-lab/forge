---
name: grill-with-docs
description: Grilling session that challenges a plan against the project's domain model, sharpens terminology, and updates CONTEXT.md and ADRs inline as decisions crystallise.
type: hybrid
---

# Grill with docs

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

> **See also:** for ideation without codebase access (pure design conversations, before code exists), use `forge:grill-me`. This skill adds codebase cross-reference + glossary discipline + inline ADR/CONTEXT.md updates on top of the same loop — pick this one when the project already has a domain model to challenge against.

## During the session

**Challenge against the glossary.** When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

**Sharpen fuzzy language.** When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean Customer or User? Those are different things."

**Discuss concrete scenarios.** When domain relationships are discussed, stress-test with edge-case scenarios that force precision about boundaries between concepts.

**Cross-reference with code.** When the user states how something works, check whether the code agrees. Surface contradictions: "Your code cancels entire Orders, but you said partial cancellation is possible — which is right?"

**Update CONTEXT.md inline.** When a term is resolved, update it immediately — don't batch. Keep `CONTEXT.md` free of implementation details; only terms meaningful to domain experts belong there.

**Offer ADRs sparingly.** Create an ADR only when all three are true: hard to reverse, surprising without context, result of a real trade-off with genuine alternatives. See `references/adr-criteria.md`.

## File structure

See `references/domain-file-structure.md` for how to locate `CONTEXT.md` and `docs/adr/` in single-context and multi-context repos.
