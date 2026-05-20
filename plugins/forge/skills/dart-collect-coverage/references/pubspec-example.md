# pubspec.yaml — `coverage` under dev_dependencies

The `coverage` package is a dev tool; it must not appear under runtime `dependencies`.

```yaml
name: my_dart_app
environment:
  sdk: ^3.0.0

dependencies:
  path: ^1.8.0

dev_dependencies:
  test: ^1.24.0
  coverage: ^1.15.0
```

## Adding via CLI

The package manager places `coverage` under `dev_dependencies` automatically when you pass the `dev:` prefix:

- Dart project: `dart pub add dev:coverage`
- Flutter project: `flutter pub add dev:coverage`
