# Invalid override fixes

Common diagnostic:

- "The parameter type 'X' of overridden method 'Y' isn't a supertype of the parameter type 'Z'."

## Root cause

Sound parameter types are **contravariant**: a subclass override must accept *at least* what the superclass accepts. Tightening a parameter type narrows the contract, which a polymorphic caller can violate at runtime.

## Decision

Pick one:

- **Widen the parameter type to match the superclass.** The override now honors the interface; do internal narrowing (`if (a is Mouse)`) inside the body if needed.
- **Mark the parameter `covariant`.** Tightening becomes explicit and intentional; the caller must guarantee they pass the narrower type.

## Example: `covariant` when the domain genuinely requires the narrower type

```dart
// Fails: tightening parameter without covariant
class Animal {
  void chase(Animal a) {}
}

class Cat extends Animal {
  @override
  void chase(Mouse a) {}
}

// Passes: covariant makes the tightening explicit
class Animal {
  void chase(Animal a) {}
}

class Cat extends Animal {
  @override
  void chase(covariant Mouse a) {}
}
```

## When to widen vs use `covariant`

- Widen when callers polymorphically dispatch via the base type (`Animal a; a.chase(other);`) and might genuinely pass any `Animal`.
- Use `covariant` when the call sites that actually invoke this override always have a `Cat`, and the narrower type is part of the domain model (e.g. game / simulation logic). Accept that mis-typed callers will throw at runtime.

## Anti-patterns

- Marking everything `covariant` to silence the analyzer — every override now risks a runtime `TypeError`.
- Casting inside the body (`a as Mouse`) without `covariant` — analyzer is satisfied, runtime is not safer.
