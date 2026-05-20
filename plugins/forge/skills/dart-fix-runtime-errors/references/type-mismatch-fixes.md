# Type-mismatch fixes

Common diagnostic:

- "The argument type 'List\<dynamic\>' can't be assigned to the parameter type 'List\<int\>'."

## Root cause

Dart infers `List<dynamic>` for empty literals (`[]`) and for collections built from heterogeneous-looking sources. The downstream consumer expects a typed list and rejects the implicit downcast (especially under `strict-casts: true`).

## Fix

Add explicit generic annotations at the instantiation site.

```dart
// Fails static analysis: inferred List<dynamic>
void main() {
  final list = [];
  list.add(1);
  list.add(2);
  printInts(list); // Error: List<dynamic> can't be assigned to List<int>
}

// Passes static analysis: explicit type at instantiation
void main() {
  final list = <int>[];
  list.add(1);
  list.add(2);
  printInts(list);
}
```

## Variations

- Map literals: `<String, int>{}` instead of `{}`.
- `.cast<T>()` is acceptable when the source genuinely is `dynamic` (e.g. decoded JSON) — the runtime cast then catches a type drift early.
- Function arguments: pass `<T>[]` rather than relying on inference from a typed parameter.

## Anti-patterns

- `as List<T>` to silence the analyzer when the underlying list really is `List<dynamic>` — defers the crash to runtime, where it becomes `TypeError`.
- Widening the consumer's signature to `List<dynamic>` to make the error go away — loses type safety on every other caller.
