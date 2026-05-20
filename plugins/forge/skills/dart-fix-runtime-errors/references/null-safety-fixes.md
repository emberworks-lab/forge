# Null-safety fixes

Common diagnostics:

- "Property cannot be accessed on a nullable receiver."
- "Non-nullable instance field 'X' must be initialized."
- "The non-nullable variable 'X' must be assigned before it can be used."

## Decision

Ask one question: **can this variable logically be null at this point?**

- **Yes** — model the nullability:
  - Use optional chaining: `obj?.method()`.
  - Provide a fallback: `obj ?? defaultValue`.
  - Make the type nullable: `String?`.
- **No, but the analyzer can't prove init order** — mark `late`:
  - Use for non-nullable instance / top-level fields whose initialization happens before any read.
  - Accept the runtime trade-off: an uninitialized read throws `LateInitializationError`.
- **No, value is always provided by the caller** — make the parameter `required` (named) or non-optional (positional).

## Example: `late` for deferred initialization

```dart
class Thermometer {
  late String temperature; // analyzer cannot prove init order; we can

  void read() {
    temperature = '20C';
  }
}
```

## Anti-patterns

- Slapping `!` on every diagnostic — silences the analyzer, defers the crash to runtime.
- Making every field nullable to "fix" the build — the API now lies about which values are required.
- `late` on a field that has no guaranteed init path — guaranteed `LateInitializationError`.
