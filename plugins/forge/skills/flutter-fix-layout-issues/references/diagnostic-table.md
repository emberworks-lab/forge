# Flutter layout diagnostic table

Match the *primary* diagnostic (not cascading follow-ups) to one row.

| Diagnostic | Cause | Canonical fix |
|---|---|---|
| `Vertical viewport was given unbounded height` | A scrollable (`ListView`, `GridView`) is inside a vertical parent that imposes no height (typically `Column`). The scrollable tries to expand infinitely. | Wrap the scrollable in `Expanded` (consume remaining `Column` space) **or** `SizedBox(height: …)` for an absolute height. |
| `An InputDecorator…cannot have an unbounded width` | A `TextField` / `TextFormField` is inside an unbounded horizontal parent (`Row`). The field cannot pick a width from infinite space. | Wrap the field in `Expanded` or `Flexible`. |
| `RenderFlex overflowed by N pixels` | A `Row` / `Column` child wants more space than the parent allocated. Visually: yellow-and-black warning stripes. | Wrap the offending child in `Expanded` (force-fit) or `Flexible` (allow smaller). Long text → `Expanded(child: Text(...))` so it wraps. |
| `Incorrect use of ParentData widget` | A `ParentDataWidget` (e.g. `Expanded`, `Flexible`, `Positioned`) is not a direct child of its required ancestor. | Move `Expanded` / `Flexible` to be a direct child of `Row` / `Column` / `Flex`. Move `Positioned` to be a direct child of `Stack`. |
| `RenderBox was not laid out` | A **cascading side-effect** from an earlier failure. Not the cause. | Scroll *up* in the stack trace; find and fix the upstream unbounded / overflow error. |

## Reading the stack trace

The Flutter engine prints multiple frames per exception. The **first** layout exception in the console (usually preceded by `══╡ EXCEPTION CAUGHT BY RENDERING LIBRARY ╞══`) is the primary one. Everything after it is collateral damage.

## When a fix breaks something else

Wrapping a child in `Expanded` removes its ability to size itself intrinsically. If the parent then complains about a different overflow, re-evaluate which side of the constraint contract you should pin:

- `Expanded(flex:)` — force a proportional share.
- `Flexible(fit: FlexFit.loose)` — allow the child to take less.
- `SizedBox(width: / height:)` — absolute pin (last resort; brittle across screen sizes).
- `ConstrainedBox(constraints: …)` — range pin (min/max).
