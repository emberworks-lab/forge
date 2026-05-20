---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree one question at a time.
type: minimal
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

> **Scope:** This skill is for structured design conversations without deep codebase access. If the conversation reveals that codebase cross-reference, domain-glossary challenges, or inline ADR/CONTEXT.md updates are needed, suggest escalating to `forge:grill-with-docs` — it adds those capabilities on top of the same grilling loop.
