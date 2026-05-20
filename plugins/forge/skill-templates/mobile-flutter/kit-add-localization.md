---
name: kit-add-localization
description: "Use when adding a new user-facing string. Edits lib/l10n/app_en.arb (and any sibling ARB files), runs flutter gen-l10n, and swaps any hardcoded call sites to context.l10n.<key>."
---

# kit-add-localization

## When to use

- Triggers: "додай рядок в l10n", "new copy string", "add UI text", `/kit-add-localization`.
- Any new user-visible string in a Flutter widget, dialog, snackbar, or error UI.
- A hardcoded string already in the codebase needs to be migrated to ARB.

Don't use when: adding internal log messages (those stay as plain English in `Logger` / `debugPrint` calls), or adding error `code` / `userMessage` defaults inside `AppException` leaves (those are fallbacks, real localized copy comes via `context.l10n` at the UI seam).

## What this skill produces

- Edits to `lib/l10n/app_en.arb` — new key + matching `@<key>` metadata block
- Edits to any other `lib/l10n/app_<locale>.arb` files, if present, with the translated value (placeholder when the user can't translate yet)
- Regenerated `lib/l10n/app_localizations*.dart` via `flutter gen-l10n`
- Edits to call sites that previously used a hardcoded string — replaced with `context.l10n.<key>` (using the `AppL10nContext` extension from `lib/l10n/build_context_l10n_extension.dart`)

## Required inputs

- Proposed key in camelCase (e.g. `profileSavedToast`, `dashboardEmptyState`)
- English value
- Short description for the `@<key>` metadata block (helps translators)
- Any placeholders / plurals / select forms — if so, the value uses ICU MessageFormat

## Steps

1. Open `lib/src/l10n/app_en.arb`. Confirm the proposed key doesn't already exist. If a similar key exists, prefer reusing it — duplicate copy is a smell.
2. Add the new key/value pair AND the `@<key>` block with at least a `description`. For ICU placeholders / plurals, add a `placeholders` map.
3. If sibling ARB files exist (e.g. `app_uk.arb`), add the same key. Use a placeholder translation if a real one isn't available — never leave the key out (that defaults to the English value at runtime, but skews translation tooling).
4. Run `flutter gen-l10n` (config in `l10n.yaml`). This regenerates `app_localizations.dart` and per-locale files.
5. At the call site, replace the hardcoded string with `context.l10n.<key>`. The extension is `import 'package:<project>/src/l10n/l10n.dart';`.
6. For interpolated strings, pass the placeholder value as a positional argument: `context.l10n.greetingUser('Alice')`.
7. Run `flutter analyze --fatal-warnings` (catches stale references) and `flutter test`.

## Conventions

- Keys are camelCase, descriptive, scoped by feature area (`profileDisplayName`, `settingsThemeLabel`, `dashboardWelcomeHeader`).
- `description` in the `@<key>` block is mandatory — translators see it as the only context.
- Placeholders use ICU syntax: `"You have {count} notifications"` with a `placeholders: { "count": { "type": "int" } }` block.
- Plurals use ICU `{count, plural, =0{...} one{...} other{...}}`.
- Selects use ICU `{gender, select, male{...} female{...} other{...}}`.

## Anti-patterns (don't do this)

- Adding a string only to `app_en.arb` when sibling locale files exist. Add to all of them in the same change.
- Inlining the string at the call site instead of using the ARB. Lint won't catch this — discipline does.
- Using `Intl.message(...)` directly. The project uses Flutter's gen-l10n pipeline; `Intl.message` is bypass.
- Renaming a shipped key without a migration. Keys are referenced from many call sites — rename via project-wide find/replace in one commit.
- Embedding HTML / Markdown in ARB values. UI styling belongs in widgets, not in the localization layer.
- Adding strings to `lib/src/l10n/` that are not user-facing (log messages, exception `userMessage` fallbacks). Those stay inline.

## Examples

Adding a simple key:

```jsonc
// lib/src/l10n/app_en.arb
{
  "homeWelcomeHeader": "Welcome",
  "@homeWelcomeHeader": {
    "description": "Heading shown on the home screen."
  },
  "profileSavedToast": "Profile saved",
  "@profileSavedToast": {
    "description": "Toast shown after the user saves their profile."
  }
}
```

Adding a key with a placeholder:

```jsonc
"uploadProgress": "Uploading {filename}…",
"@uploadProgress": {
  "description": "Progress label shown while a file upload is in flight.",
  "placeholders": {
    "filename": { "type": "String", "example": "avatar.png" }
  }
}
```

Call site:

```dart
Text(context.l10n.profileSavedToast)
Text(context.l10n.uploadProgress(file.name))
```

## References

- `lib/src/l10n/l10n.dart` (barrel — what to import)
- `lib/src/l10n/build_context_l10n_extension.dart` (`context.l10n` extension)
- `lib/src/l10n/app_en.arb` (existing keys for naming examples)
- `l10n.yaml` (gen-l10n configuration)
- Flutter docs on internationalization: <https://docs.flutter.dev/ui/accessibility-and-internationalization/internationalization>
