---
name: flutter-fix-layout-issues
description: Resolve Flutter layout constraint violations — RenderFlex overflow, unbounded viewport/width, ParentData misuse — using a diagnostic-to-fix lookup. Use when a Flutter app throws a layout exception, shows the yellow/black overflow stripes, or surfaces the red error screen.
type: hybrid
inspired-by:
  - author: flutter
    repo: https://github.com/flutter/skills
    skill: flutter-fix-layout-issues
    relation: adapted
---

# Resolving Flutter layout errors

Flutter layout follows one rule: **constraints go down, sizes go up, parent sets position.** Layout exceptions occur when this negotiation breaks — usually unbounded parents or unconstrained children. Match the diagnostic to one of the five canonical signatures below, then apply the canonical fix.

## Contract

Given a Flutter app throwing a layout exception, produce:

1. The primary diagnostic identified (ignoring cascading "RenderBox was not laid out" follow-ups).
2. The matching fix applied at the right widget boundary.
3. Hot-reload confirmation that the red error screen / overflow stripes are gone, with no new layout exception introduced.

## Decision tree — which fix?

```
Read the *first* layout exception in the console; ignore "RenderBox was not laid out" follow-ups.

"Vertical viewport was given unbounded height"
└── Scrollable inside an unconstrained vertical parent (Column).
    Wrap the scrollable in Expanded (consume remaining space) OR SizedBox(height:) (absolute).

"An InputDecorator…cannot have an unbounded width"
└── TextField/TextFormField inside an unconstrained horizontal parent (Row).
    Wrap the field in Expanded or Flexible.

"RenderFlex overflowed"
└── A Row/Column child requests more space than the parent allocated.
    Wrap the offending child in Expanded (force fit) or Flexible (allow smaller).

"Incorrect use of ParentData widget"
└── ParentDataWidget is not a direct child of its required ancestor.
    Move Expanded/Flexible to be a direct child of Row/Column/Flex.
    Move Positioned to be a direct child of Stack.

"RenderBox was not laid out"
└── Cascading side-effect. Scroll *up* the stack trace for the primary unbounded error.
```

Full diagnostic table + examples: `references/diagnostic-table.md`.

## Workflow

Walk these steps in order:

1. **Run in debug mode** to capture the exact exception in the console.
2. **Identify the primary error** (skip "RenderBox was not laid out" follow-ups).
3. **Apply the fix** from the decision tree above.
4. **Hot reload** (`r` in `flutter run`, or via the Flutter MCP `hot_reload` tool).
5. **Verify** — the red error screen / yellow-and-black stripes are gone. If a new layout exception appeared, return to step 2 with the new diagnostic.

## Core principle

Constraints flow down (the parent tells the child the available box), sizes flow up (the child tells the parent how much of it it used), the parent positions the child. Errors come from breaking the contract: either the parent passes unbounded constraints into a widget that cannot interpret them (lists, text fields), or the child requests more space than the parent provided. Fixes pin one side of the contract — usually the child's space request — via `Expanded`, `Flexible`, or `SizedBox`.

## Examples

- `references/diagnostic-table.md` — full table of canonical diagnostics with one-paragraph cause + fix per entry.
- `references/fix-examples.md` — three worked code-pair examples (ListView-in-Column, TextField-in-Row, Row-overflow).

## Do not

- Do not chase the `RenderBox was not laid out` line — it's a cascading symptom, not the cause.
- Do not wrap *every* child in `Expanded` — overconstrained layouts hide real bugs and break legitimate intrinsic-size children.
- Do not stack `SizedBox` over `Expanded` to force a fit without understanding which one the parent expects.
- Do not skip hot reload after the fix — the layout pipeline is not re-run until the widget tree rebuilds.

## What this skill does not cover

- **Custom `RenderBox` / `RenderSliver` implementations** — when the issue is in a hand-rolled render object, escalate to `forge:diagnose-deep`.
- **Performance issues from over-deep widget trees** — orthogonal; check `DevTools` performance overlay separately.
- **Web / desktop platform-specific layout quirks** (mouse hover regions, system insets) — these have their own diagnostics; the rules above cover mobile-first layout.
