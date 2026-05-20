# mobile-native interview

For iOS (Swift) / Android (Kotlin) / Compose Multiplatform / React Native projects.

## Ask about

- **Target platform(s)** — iOS / Android / both / Compose Multiplatform.
- **State management** — SwiftUI + Observable / TCA / MVVM, Compose + ViewModel / MVI, Redux-style for RN.
- **Persistence** — SwiftData / Core Data / Room / SQLDelight / Realm.
- **Networking** — `URLSession` / Alamofire / Ktor / Retrofit / fetch.
- **Auth** — Sign-in-with-Apple / Google / custom / Firebase Auth / Supabase Auth.
- **Deployment** — App Store + TestFlight, Google Play, Firebase App Distribution.

## Generate

- `kit-create-screen.md` — screen + state + navigation entry.
- `kit-add-network-call.md` — typed client method + tests.
- `kit-add-persistence-entity.md` — model + migration.
- `kit-deploy-testflight.md` (iOS) or `kit-deploy-internal-track.md` (Android).

## Notes

- Cross-platform stacks (Compose Multiplatform, React Native) need a separate `kit-add-platform-channel.md` for native bridges — ask whether the project will use bridges.
- The user may not have a code signing / provisioning profile yet — that becomes a Mode M ticket under P0 Bootstrap if Linear automation is enabled.
