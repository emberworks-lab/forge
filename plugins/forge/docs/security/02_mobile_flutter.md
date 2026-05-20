# Security — Mobile (Flutter)

Flutter-specific security KB. Builds on `00_general.md`. Covers Android and iOS targets. References are platform-agnostic except where noted.

OWASP reference: **OWASP Mobile Top 10** (2024). https://owasp.org/www-project-mobile-top-10/

---

## OWASP Mobile Top 10 Summary (2024)

| # | Risk | Flutter relevance |
|---|---|---|
| M1 | Improper Credential Usage | Hardcoded keys, insecure storage |
| M2 | Inadequate Supply Chain Security | pub.dev package vetting |
| M3 | Insecure Authentication/Authorization | JWT misuse, missing server-side checks |
| M4 | Insufficient Input/Output Validation | Deep links, WebView URLs |
| M5 | Insecure Communication | Missing TLS, no cert pinning |
| M6 | Inadequate Privacy Controls | PII in logs, screenshots, backups |
| M7 | Insufficient Binary Protections | Debuggable release builds, no obfuscation |
| M8 | Security Misconfiguration | Permissive AndroidManifest, `NSAllowsArbitraryLoads` |
| M9 | Insecure Data Storage | SharedPreferences for secrets, unencrypted SQLite |
| M10 | Insufficient Cryptography | Weak algorithms, nonce reuse |

---

## Secure Storage

**What:** Sensitive values (auth tokens, session keys, user credentials) must use the platform secure enclave, not plain storage.

**Severity:** Critical — plaintext tokens in SharedPreferences are readable by rooted devices and some backup mechanisms.

**Use:**
- `flutter_secure_storage` — wraps iOS Keychain and Android EncryptedSharedPreferences/Keystore.
- iOS: Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` (does not migrate to new device).
- Android: EncryptedSharedPreferences backed by AndroidKeyStore for key material.

**Never use for sensitive values:**
- `SharedPreferences` / `NSUserDefaults` — plaintext on disk, included in device backups.
- `path_provider` + plain file write — filesystem accessible on rooted devices.
- Drift/SQLite without encryption (use SQLCipher via `drift` + `sqlcipher_flutter_libs` for sensitive databases).

**Pattern:**
```dart
final storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock_this_device),
);
await storage.write(key: 'auth_token', value: token);
final token = await storage.read(key: 'auth_token');
```

**Supabase / PostgREST:** Store the Supabase session (access + refresh token) via `flutter_secure_storage`, not `SharedPreferences`. If using the official `supabase_flutter` package, configure the custom storage adapter.

---

## TLS & Certificate Pinning

**What:** All network traffic must be encrypted (TLS 1.2+). Certificate pinning adds a layer against MITM with rogue CAs.

**Severity:** High for missing TLS; Medium for missing pinning (context-dependent).

**TLS rules:**
- Do not disable TLS verification in any build (including debug). Use a local proxy (Charles, mitmproxy) instead for debugging.
- Android: configure `network_security_config.xml` to `cleartextTrafficPermitted="false"`.
- iOS: do not add `NSAllowsArbitraryLoads` to `Info.plist`; never add domains to `NSExceptionDomains` in production.

**Certificate pinning:**
```dart
// Using http + SecurityContext, or a dedicated package
// Example with dio + pinning interceptor
final dio = Dio();
(dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
  final client = HttpClient();
  client.badCertificateCallback = (cert, host, port) {
    // Verify cert matches pinned SHA-256 fingerprint
    return false; // reject — never return true broadly
  };
  return client;
};
```
- Pin to leaf cert for tight control; pin to intermediate CA for operational flexibility (leaf cert can rotate without app update).
- Ship a backup pin to avoid lockout during cert rotation.
- **When to pin:** high-value apps (financial, medical). For most apps, strict TLS + correct hostname verification is sufficient.

---

## Permissions

**What:** Request only permissions the app genuinely needs, at the point of use.

**Severity:** Medium — over-permission erodes user trust and increases attack surface.

**Rules:**
- Declare minimum permissions in `AndroidManifest.xml` and `Info.plist`.
- Request runtime permissions at the moment the feature needs them, with a user-facing explanation.
- Handle permission denial gracefully — never crash; degrade feature, not entire app.
- Remove permissions that were added "for future features."
- iOS: every `NSUsageDescription` string must be honest and specific.

**Audit:** Run `flutter analyze` and review manifest manually before each release. There is no automated Flutter lint for over-permissioned manifests.

---

## Deep Links & URL Scheme Validation

**What:** Deep links (`yourapp://`, `https://yourapp.com/path`) can be forged by malicious apps or web pages.

**Severity:** High — unvalidated deep links can trigger actions on behalf of the user or steal OAuth tokens from redirect URIs.

**Rules:**
- Use **App Links** (Android) and **Universal Links** (iOS) over custom URL schemes. These require server-side `assetlinks.json` / `apple-app-site-association` verification.
- Validate every parameter received via deep link before processing. Never trust incoming URL query parameters.
- OAuth redirect URIs: use Universal/App Links, not custom schemes, to prevent interception by other apps.
- After receiving an OAuth code via deep link, exchange it server-side or use PKCE — never log or expose the code.
- Prevent open redirects: validate that redirect targets are in an allowlist.

**Common mistakes:**
- Navigating directly to `uri.queryParameters['target']` without validation.
- Custom schemes like `myapp://action?token=xxx` — any installed app can register the same scheme.

---

## Build Flavors & Production Hardening

**What:** Release builds must not contain debug artifacts, and should be obfuscated.

**Severity:** High for debuggable release; Medium for missing obfuscation.

**Rules:**
- Never ship a build with `android:debuggable="true"` in `AndroidManifest.xml`. Flutter release builds set this correctly by default, but verify after plugin additions.
- Enable ProGuard/R8 obfuscation: in `android/app/build.gradle` set `minifyEnabled true` and `shrinkResources true` for release.
- Flutter obfuscation: `flutter build apk --obfuscate --split-debug-info=<output-dir>`. Store debug symbols securely for crash deobfuscation.
- Remove test code, debug flags, and mock data from production builds.
- Verify `flutter build apk --release` produces a signed, non-debuggable APK before store submission.
- iOS: disable debugging capabilities in the release provisioning profile.

**Flavor convention (e.g., dev/prod):**
```dart
// AppConfig.prod() should have:
// - No stub/mock data
// - No debug overlay
// - Supabase prod URL
// - Certificate pinning enabled
```

---

## WebView Hardening

**What:** Embedding a WebView introduces a browser-level attack surface inside your app.

**Severity:** High — misconfigured WebViews can expose native bridges or allow arbitrary code execution.

**Rules:**
- Enable JavaScript only if your content requires it. Explicitly set `javascriptMode: JavascriptMode.disabled` when not needed.
- Never enable `allowFileAccess` or `allowFileAccessFromFileURLs` — these allow access to the local filesystem.
- Never enable `addJavaScriptChannel` for arbitrary web content — only trusted first-party URLs.
- Validate the URL before loading: never load attacker-controlled URLs without allowlisting the scheme and host.
- Disable `setAllowContentAccess` (Android) to prevent access to content providers.
- Use `navigationDelegate` to intercept and validate navigation before it occurs.

```dart
WebView(
  javascriptMode: JavascriptMode.disabled, // or enabled only for known URLs
  navigationDelegate: (NavigationRequest req) {
    if (!req.url.startsWith('https://yourapp.com')) {
      return NavigationDecision.prevent;
    }
    return NavigationDecision.navigate;
  },
)
```

---

## Crash Logging & Telemetry

**What:** Crash and error reporting tools (Sentry, Firebase Crashlytics) can capture PII if not configured carefully.

**Severity:** Medium — PII in crash reports violates GDPR and user trust.

**Rules:**
- Never include user email, phone, or other PII in breadcrumbs or custom keys sent to crash reporters.
- Use opaque user IDs (UUID, hashed identifier) in `setUserId` — not emails.
- Scrub `Exception` messages before sending if they may contain user-entered data.
- Disable crash reporting in dev/test builds unless explicitly needed.
- Review what the crash SDK captures automatically (stack frames, device metadata, request bodies in some configurations).

```dart
// Good
Sentry.configureScope((scope) {
  scope.setUser(SentryUser(id: user.id)); // opaque ID only
});

// Bad
scope.setUser(SentryUser(id: user.email)); // PII
```

---

## Screenshot Prevention

**What:** On sensitive screens (auth, payment, PII display), prevent OS-level screenshots and screen recording.

**Severity:** Medium — screenshots can be captured by malicious apps on Android.

**Android:** Set `FLAG_SECURE` on the window:
```kotlin
// In MainActivity.kt
window.setFlags(WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE)
```
Or use `flutter_windowmanager` plugin.

**iOS:** The OS prevents screenshot capture on secure screens when `isProtected` is set via secure text field or screen recording notification. Use `UITextField.isSecureTextEntry` where applicable. Consider using `AppLifecycleState.inactive` hook to overlay a blur/placeholder when the app is backgrounded.

---

## Authentication Tokens (Supabase / OAuth)

**What:** Access and refresh tokens must be treated as secrets throughout their lifecycle.

**Rules:**
- Store tokens in `flutter_secure_storage`, not `SharedPreferences`.
- Refresh tokens should be rotated on use (Supabase does this by default).
- On logout, invalidate server-side and delete local token storage.
- Never embed service keys (`service_role` key in Supabase) in the mobile app — these bypass RLS. Use only `anon` key + RLS.
- Validate that Supabase RLS policies are correct server-side; never rely on client-side filtering as the authorization boundary.
- JWT expiry: access tokens should be short-lived (Supabase default 1 hr); refresh silently.

---

## In-App Purchase Receipt Validation

**What:** IAP receipts must be validated server-side, not client-side.

**Severity:** High — client-side validation is trivially bypassed.

**Rules:**
- Send the receipt/purchase token to your backend for server-side validation against Apple/Google APIs.
- Never unlock features based solely on a client-reported purchase status.
- Idempotently record purchases server-side; replay the validation on app launch to catch reversals.

---

## Supply Chain (pub.dev)

**What:** Flutter packages are an attack surface.

**Rules:**
- Prefer packages with pub.dev "verified" badge and high pub points.
- Check publisher identity (e.g., `dart.dev`, `flutter.dev`) for official packages.
- Run `flutter pub audit` in CI when available; check for known CVEs.
- Review `CHANGELOG` and commits before major version upgrades.
- Minimize transitive dependencies.

---

## Common Pitfalls

| Pitfall | Severity | Fix |
|---|---|---|
| Supabase `service_role` key in app bundle | Critical | Use `anon` key + RLS |
| Auth token in `SharedPreferences` | High | Migrate to `flutter_secure_storage` |
| `NSAllowsArbitraryLoads: true` in `Info.plist` | High | Remove; fix individual domain exceptions |
| Debuggable release APK | High | Verify `android:debuggable` is false in release build |
| Deep link with no parameter validation | High | Allowlist + validate all incoming URL params |
| WebView loading arbitrary URLs with JS enabled | High | Allowlist hosts; disable JS when not needed |
| User email as crash reporter user ID | Medium | Use opaque UUID |
| PII in log statements | High | Log user ID only; never email/phone/address |
| Missing obfuscation in release builds | Medium | `--obfuscate --split-debug-info` |
| Screenshot not blocked on payment screen | Medium | `FLAG_SECURE` on Android |
| JWT accepted without `exp` / `iss` validation | High | Validate all standard claims |
| No cert pinning on financial app | Medium | Pin to intermediate CA with backup pin |
