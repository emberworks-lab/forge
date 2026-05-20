---
name: dart-fix-runtime-errors
description: Resolve Dart static-analysis errors (type system, null safety, override soundness) using `dart analyze` + `dart fix`, then verify via `dart test`. Use when the analyzer reports diagnostics or when CI fails on a type / null-safety / override issue.
type: hybrid
inspired-by:
  - author: dart-lang
    repo: https://github.com/dart-lang/skills
    skill: dart-fix-runtime-errors
    relation: adapted
---

# Resolving Dart static-analysis errors

A four-step loop: analyze → auto-fix → manual fix by category → verify. Most errors fall into three categories (null safety, type mismatch, invalid override); the decision tree below routes to the right resolution.

## Contract

Given a Dart or Flutter project with analyzer diagnostics, produce:

1. `dart analyze .` clean (no errors / fatal infos).
2. `dart test` green (no `TypeError` introduced by the fix).
3. Each manual fix follows the rule for its category (no blanket `?` / `!` / `dynamic` casts).

## Workflow

Walk the four steps in order. Use the checklist; do not skip the verification step.

### 1. Run the analyzer

```bash
dart analyze . --fatal-infos
```

### 2. Apply automated fixes

```bash
dart fix --dry-run    # preview
dart fix --apply      # apply
```

### 3. Resolve remaining errors by category

Decision tree:

```
Error mentions "nullable receiver" / "must be initialized" / "non-nullable"?
└── Null safety   → references/null-safety-fixes.md

Error mentions "can't be assigned" / "List<dynamic>" / "argument type"?
└── Type mismatch → references/type-mismatch-fixes.md

Error mentions "parameter type doesn't match" / "invalid override" / "covariant"?
└── Invalid override → references/override-fixes.md

None of the above
└── Re-read the diagnostic; treat it as a learning case, not a guess case.
```

Each reference file has the rule, a short rationale, and a worked example.

### 4. Verify (feedback loop)

```bash
dart analyze .
dart test
```

- `analyze` still reports errors → return to step 3.
- `test` fails with `TypeError` → an explicit cast (`as T`) or `late` access is wrong; locate the failure, correct the type or the initialization order.

## Core principles (one-paragraph each)

### Type system soundness

Sound return types are covariant, sound parameter types are contravariant. Never tighten a parameter type in a subclass override unless you mark it `covariant`. Annotate generics explicitly (`<int>[]`, `Map<K, V>`); never assign `List<dynamic>` to a typed list. Avoid implicit downcasts from `dynamic` — use explicit casts only when the underlying runtime type matches. Enable `strict-casts: true` under `analyzer.language` to catch implicit downcasts at compile time.

### Null safety

Use `?` for nullable types, `!` for null assertions (sparingly), `required` for non-nullable named parameters. Reach for `late` on non-nullable instance / top-level fields that the analyzer cannot prove are initialized, where you can guarantee init-before-use. Use the `_` wildcard (Dart 3.7+) for unused locals.

### Error handling

Catch `Exception` subtypes for recoverable failures. Never explicitly catch `Error` or its subtypes (`TypeError`, `ArgumentError`, etc.) — errors mark bugs and must be fixed, not caught. Use `rethrow` inside `catch` to propagate while preserving the stack trace. Enable `avoid_catching_errors` in the linter.

## Examples

- `references/null-safety-fixes.md` — fixes for "must be initialized" / "nullable receiver" diagnostics with `late`, `?`, `??`.
- `references/type-mismatch-fixes.md` — fixes for `List<dynamic>` inference + explicit generic annotations.
- `references/override-fixes.md` — fixes for parameter-tightening overrides using `covariant`.

## Do not

- Do not add `?` / `!` to silence diagnostics without thinking about nullability.
- Do not catch `Error` or its subtypes to suppress a `TypeError` — fix the cause.
- Do not stack hypotheses: if a manual fix doesn't resolve the diagnostic, re-read it before trying another approach.

## What this skill does not cover

- **Runtime exceptions during app execution** — fetch the stack via the Dart / Flutter MCP `get_runtime_errors`, locate the failing line, fix, and verify via `hot_reload`. That live-app loop is orthogonal to this analyzer-driven workflow.
- **Linter / format rules** — `dart format` and `dart analyze` lint output share the loop, but stylistic fixes belong with the lint runner.
- **Test design** — see `forge:tdd` for how to write the regression test that locks in a fix.
