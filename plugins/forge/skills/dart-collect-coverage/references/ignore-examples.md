# Applying coverage:ignore directives

Three scopes: file, block, line. The format-time flag `--check-ignore` honors them when building LCOV.

```dart
// coverage:ignore-file
import 'package:meta/meta.dart';

class SystemConfig {
  final String env;

  SystemConfig(this.env);

  // coverage:ignore-start
  void legacyInit() {
    print('Deprecated initialization');
  }
  // coverage:ignore-end

  bool isProduction() {
    if (env == 'prod') return true;
    return false; // coverage:ignore-line
  }
}
```

## When to use which scope

| Scope | Good fit |
|---|---|
| `ignore-file` | Generated code, fixtures, throwaway scripts. |
| `ignore-start` / `ignore-end` | Deprecated section staying in tree, untestable platform-only branch. |
| `ignore-line` | A single defensive return / `assert(false)` / unreachable default. |

Prefer the narrowest scope that captures the intent. File-level ignores hide signal as much as noise.
