---
name: kit-deploy
description: "Use when running a build for distribution. Stub for the scaffold — runs flutter build apk / ios for the requested flavor and surfaces the artifact path. Real signing + store upload lands in a post-scaffold ticket."
---

# kit-deploy

## When to use

- Triggers: "deploy", "build prod", "make a release build", `/kit-deploy`.
- The user wants a release-mode build artifact (APK or IPA) for the dev or prod flavor.
- This is a stub — there's no signing, no fastlane, no store upload until the post-scaffold deployment epic. Do NOT invent these steps.

## What this skill produces

- A pre-flight verification: clean tree, analyzer green, tests green, codegen fresh.
- A flavored release build: `flutter build apk --flavor <dev|prod> -t lib/main_<flavor>.dart` and/or `flutter build ios --flavor <dev|prod> -t lib/main_<flavor>.dart --no-codesign` (until signing infra exists).
- A printed artifact path so the user can collect the binary from `build/app/outputs/...`.

## Required inputs

- Flavor: `dev` or `prod`
- Target platform: `android`, `ios`, or `both`
- Whether to bump the version in `pubspec.yaml` first (default: ask the user)

## Steps

1. **Pre-flight gates** (abort if any fail):
   - `git status` reports a clean tree (no uncommitted changes).
   - `flutter analyze --fatal-warnings` is green.
   - `flutter test` is green.
   - `dart run build_runner build --delete-conflicting-outputs` produces no diff (codegen is fresh).
   - `dart format --set-exit-if-changed .` is clean.
2. Confirm the version in `pubspec.yaml`. If a bump is needed, ask the user for the new version + build number; update `pubspec.yaml` and `CHANGELOG.md` (when present); commit before building.
3. Run the matching build command:
   - Android: `flutter build apk --flavor <flavor> -t lib/main_<flavor>.dart` (or `appbundle` for Play Store, when signing exists).
   - iOS: `flutter build ios --flavor <flavor> -t lib/main_<flavor>.dart --no-codesign` until signing certs are wired up.
4. Print the artifact path:
   - APK: `build/app/outputs/flutter-apk/app-<flavor>-release.apk`
   - iOS: `build/ios/iphoneos/Runner.app` (unsigned during scaffold era)
5. Stop. Do NOT push to a store, do NOT invoke fastlane, do NOT upload to TestFlight — those steps land in the post-scaffold deployment epic.

## Conventions

- Never deploy from a dirty tree. The pre-flight gate is non-negotiable.
- Never build the `dev` flavor for distribution to non-developers. Dev shows debug overlays and points at stub Supabase keys.
- `pubspec.yaml` `version: X.Y.Z+B` — semver before `+`, monotonic build number after.
- The build command writes to `build/`. That folder is gitignored.

## Anti-patterns (don't do this)

- Running `flutter build` without the pre-flight gates passing.
- Building the `dev` flavor and shipping it to users.
- Skipping `flutter analyze --fatal-warnings` because "it's a small change".
- Inventing a signing flow, a fastlane config, or a store upload step. Those are explicitly out of scope until the post-scaffold deployment epic.
- Running `flutter build` from a feature branch with uncommitted work — the build embeds whatever's on disk.
- Bumping the version after the build instead of before. The build embeds the version at compile time.

## TODO: real implementation when signing infrastructure is ready

Tracked separately. The follow-up will add: signing keys (Android keystore + iOS provisioning), a fastlane config under `android/fastlane/` and `ios/fastlane/`, store metadata, beta-channel automation, and a CI release pipeline. Until then, this skill remains a thin wrapper around `flutter build`.

## Examples

Building Android prod (current scaffold-era flow):

```bash
git status                               # must be clean
flutter analyze --fatal-warnings         # must be green
flutter test                             # must pass
dart run build_runner build --delete-conflicting-outputs
git diff --quiet                         # codegen must be fresh
flutter build apk --flavor prod -t lib/main_prod.dart
ls build/app/outputs/flutter-apk/app-prod-release.apk
```

## References

- `pubspec.yaml` (version + flavor wiring)
- `lib/main_dev.dart`, `lib/main_prod.dart` (entry points consumed by `-t`)
- Android flavor wiring: `android/app/build.gradle`
- iOS flavor wiring: `ios/Runner.xcodeproj/`
