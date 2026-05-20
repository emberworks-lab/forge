---
name: dart-collect-coverage
description: Collect Dart/Flutter test coverage with the `coverage` package and produce an LCOV report. Use when a Dart or Flutter project needs a coverage run, an LCOV artifact, or branch/function-level metrics.
type: hybrid
inspired-by:
  - author: dart-lang
    repo: https://github.com/dart-lang/skills
    skill: dart-collect-coverage
    relation: adapted
---

# Dart / Flutter test coverage

Generate an LCOV report for a Dart or Flutter project using the `coverage` package. The default path uses the bundled `test_with_coverage` script; the manual path is reserved for VM-service / branch / function coverage needs.

## Contract

Given a Dart or Flutter project, produce:

1. `coverage/coverage.json` — raw VM coverage data.
2. `coverage/lcov.info` — LCOV-formatted report.
3. `coverage` declared under `dev_dependencies` in `pubspec.yaml`.

## Decision tree — which workflow?

```
Need branch coverage, function coverage, or custom VM-service control?
├── Yes → Manual VM-service workflow (see references/manual-vm-service.md)
└── No  → Default `test_with_coverage` workflow (below)
```

## Default workflow — `test_with_coverage`

Walk these steps in order:

1. **Add the dev dependency.**
   - Dart project: `dart pub add dev:coverage`
   - Flutter project: `flutter pub add dev:coverage`
2. **Run the bundled script.**
   ```bash
   dart run coverage:test_with_coverage
   ```
   In a Dart workspace / monorepo, specify test dirs explicitly:
   `dart run coverage:test_with_coverage -- pkgs/foo/test pkgs/bar/test`
3. **Validate output.** Confirm `coverage/coverage.json` and `coverage/lcov.info` exist.
4. **Tune ignores.** Missing files → either import them from tests, or annotate (see § Coverage directives).

## Coverage directives

Inline comments exclude code from the report. Pass `--check-ignore` when formatting to enforce them.

| Directive | Scope |
|---|---|
| `// coverage:ignore-line` | one line |
| `// coverage:ignore-start` / `// coverage:ignore-end` | a block |
| `// coverage:ignore-file` | the whole file |

## Testing fundamentals (one paragraph)

Use `package:test` for pure Dart, `flutter_test` for Flutter. Unit tests cover functions/classes, widget tests cover component layout + interaction (often with `package:mockito`), integration tests cover full app flows on simulated / real devices. Coverage is read on the aggregate; tune ignores rather than chasing 100%.

## When to use the manual workflow

The default `test_with_coverage` script is sufficient for line coverage. Reach for the manual workflow only when the task explicitly requires:

- Branch coverage (`--branch-coverage`, Dart VM 2.17.0+).
- Function coverage (`--function-coverage`).
- Custom isolate-pause / resume control.
- VM-service port pinning for an external collector.

Full recipe: `references/manual-vm-service.md`.

## Examples

- `references/pubspec-example.md` — `pubspec.yaml` shape with `coverage` under `dev_dependencies`.
- `references/ignore-examples.md` — applied directive examples (file / block / line).

## Do not

- Do not move `coverage` into runtime `dependencies` — it is a dev tool.
- Do not chase 100% coverage by adding meaningless tests; prefer `coverage:ignore-*` for generated code, unreachable branches, or trivial passthroughs.
- Do not delete the `coverage/` directory between runs without committing the LCOV elsewhere — CI consumers expect it at a stable path.

## What this skill does not cover

- **Authoring the tests themselves** — see `forge:tdd` for the discipline; this skill assumes tests already exist.
- **Publishing LCOV to a service** (Codecov / Coveralls) — orthogonal; configure per your CI runner.
- **Mutation testing or coverage-quality scoring** — out of scope.
