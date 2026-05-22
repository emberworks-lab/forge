# Candidate suggestion template

Each deepening opportunity in the Step 2 numbered list follows this shape. Keep it tight — this is a menu for the user to pick from, not a design doc.

```
N. <short title in glossary + domain vocabulary>

   Files     — the files/modules involved (paths).
   Problem   — why the current architecture causes friction. Name the
               shallowness, the leaked seam, or the missing locality
               explicitly. Use the deletion test if it applies.
   Solution  — plain-English description of what would change. Describe the
               deepened module's shape; do NOT propose the interface yet.
   Benefits  — framed in locality and leverage, AND in how tests improve
               (what becomes testable through the interface).
```

## Vocabulary rules

- Domain nouns come from `CONTEXT.md`: "the Order intake module," "the Ledger reconciler."
- Architecture nouns come from `references/glossary.md`: shallow, deep, seam, adapter, locality, leverage.
- Never mix the wrong register: not "the FooBarHandler" (raw code name), not "the Order service" (drifted architecture word).

## Worked example

```
2. Deepen the Order intake module behind a single seam

   Files     — src/orders/parse.ts, src/orders/validate.ts,
               src/orders/normalize.ts, 6 call sites in src/api/*.ts
   Problem   — Three shallow modules each expose an interface nearly as
               wide as their implementation. The real bugs live in how the
               six call sites chain them in the wrong order — there is no
               locality. Deleting any one moves complexity to the callers
               rather than concentrating it (failed deletion test).
   Solution  — Fold parse/validate/normalize into one deep Order intake
               module with a single seam taking raw input and returning a
               validated Order. The ordering invariant lives inside.
   Benefits  — Leverage: callers stop sequencing three steps. Locality:
               the ordering bug has one home. Tests: the intake interface
               becomes the test surface — drive raw input, assert the
               Order, instead of testing three internals in isolation.
```

## ADR-conflict marking

If a candidate contradicts an ADR, only include it when the friction warrants reopening the decision, and mark it inline:

```
4. <title>  — contradicts ADR-0007, but worth reopening because the seam
   it forbids is exactly where the recurring reconciliation bug lands.
```
