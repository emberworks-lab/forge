# mobile-native/ skill-template (placeholder)

This directory marks the future location for native iOS / Android project scaffolding.
No template files exist here yet.

## Why no scaffolding yet

The framework choice for native mobile e2e testing is pending resolution of EPIC H
research outputs:

- **#86** — iOS e2e research (XCUITest vs Detox on native)
- **#87** — Android e2e research (Espresso vs Detox on native)

Until those tickets land, the correct per-platform CLAUDE.md hooks, test-runner
configs, and CI steps cannot be finalised. Shipping a template now would require
changing it again once the decision is made.

## What this template will contain

Once EPIC H research is resolved, this directory will mirror the shape of
`mobile-flutter/` and include:

- `README.md` — this file, updated with full usage instructions
- `template-source.json` — metadata (platform targets, min SDK versions, dependencies)
- `CLAUDE.md` — per-project standing instructions for a native iOS/Android project
- `.claude/tracker.json` — tracker backend wiring
- Basic iOS scaffolding (`ios/` Xcode project layout, `Podfile` stub)
- Basic Android scaffolding (`android/` Gradle project layout, `build.gradle` stub)
- `kit-*.md` skills matching the native workflow (create-feature, add-fastlane,
  deploy, add-localization, etc.)

## Reference shape

Use `plugins/forge/skill-templates/mobile-flutter/` as the canonical example of what
a finished mobile skill-template looks like:

```
mobile-flutter/
  README.md
  template-source.json
  kit-add-drift-table.md
  kit-add-fastlane.md
  kit-add-localization.md
  kit-create-feature.md
  kit-create-flame-component.md
  kit-deploy.md
```

When implementing this template, replicate that structure with native-specific
equivalents and update this README with real usage instructions.
