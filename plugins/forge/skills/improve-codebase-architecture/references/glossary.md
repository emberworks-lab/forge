# Glossary and working principles

Use these terms exactly in every suggestion. Consistency is the point — the moment you swap in "component," "service," "API," or "boundary," the analysis loses its shared frame. Keep architecture vocabulary (this file) separate from domain vocabulary (the project's `CONTEXT.md`).

## Terms

- **Module** — anything with an interface and an implementation: a function, class, package, or slice.
- **Interface** — *everything a caller must know to use the module*: types, invariants, error modes, ordering constraints, configuration. Not merely the type signature.
- **Implementation** — the code inside the module.
- **Depth** — leverage at the interface: a lot of behaviour behind a small interface.
  - **Deep** = high leverage; small interface, large useful implementation.
  - **Shallow** = the interface is nearly as complex as the implementation. Suspect.
- **Seam** — where an interface lives; a place behaviour can be altered without editing in place. Use this word, not "boundary."
- **Adapter** — a concrete thing that satisfies an interface at a seam.
- **Leverage** — what callers gain from depth.
- **Locality** — what maintainers gain from depth: change, bugs, and knowledge concentrated in one place.

## Working principles

- **Deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through (shallow — not earning its keep). If complexity reappears, duplicated across N callers, it was earning its keep (deep). "Concentrates" is the signal worth surfacing.
- **The interface is the test surface.** A deep module is testable through its interface; a shallow one forces tests against its internals.
- **One adapter = hypothetical seam. Two adapters = real seam.** Do not introduce a seam for a single adapter — that is speculative generality. A second concrete adapter proves the seam is real.

## Stance toward the domain model

This skill is *informed* by the project's domain model, not driven by it:

- `CONTEXT.md` domain language gives names to good seams. A well-named domain concept is often exactly where a deep module wants to live.
- `docs/adr/` records decisions already made. Treat them as settled; reopen one only when the friction is load-bearing enough to justify revisiting the decision.
