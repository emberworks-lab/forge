## What

Create a Firebase project for `<project_name>`, register the platform apps (iOS / Android / Web), and download the config files needed for SDK initialization. Project bootstrapped via `/project-init` on `<date>`.

## User actions

1. Open https://console.firebase.google.com and sign in.
2. Click **Add project**. Set:
   - **Project name**: `<project_name>`
   - **Google Analytics**: enable or skip per your preference
3. Wait for provisioning to complete.
4. For each platform the project targets:
   - **Android**: register an Android app with the package id (e.g. `com.example.<project_name>`), download `google-services.json`, drop it into `android/app/`.
   - **iOS**: register an iOS app with the bundle id, download `GoogleService-Info.plist`, drop it into `ios/Runner/` (Flutter) or the appropriate target group (native).
   - **Web**: register a web app, copy the SDK config object into the web bootstrap.
5. (Flutter only) Run `flutterfire configure` to generate `firebase_options.dart`.
6. Enable required Firebase products in the console: Auth, Firestore, Storage, Analytics, Crashlytics — only what you actually use.
7. Add the config files to `.gitignore` if they contain secrets you don't want public; otherwise commit them per the platform convention.

## Acceptance

- Firebase project exists in the console with name `<project_name>`.
- Each target platform's config file is in the correct repo location and the app builds without "missing Firebase config" errors.
- A smoke test (e.g. `Firebase.initializeApp()` then a no-op Firestore read) succeeds against the new project.
