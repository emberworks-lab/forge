# Security — Web Frontend

Web-specific security KB. Builds on `00_general.md`. Covers frontend and browser-side concerns; backend controls are in `04_backend.md`.

OWASP reference: **OWASP Top 10** (current edition: 2021). https://owasp.org/Top10/

---

## OWASP Top 10 Summary (2021)

| # | Risk | Frontend relevance |
|---|---|---|
| A01 | Broken Access Control | Client-side route guards are UI only — enforce server-side |
| A02 | Cryptographic Failures | Avoid storing sensitive data in localStorage; enforce HTTPS |
| A03 | Injection | XSS (HTML injection), template injection |
| A04 | Insecure Design | Threat-model before building auth/payment flows |
| A05 | Security Misconfiguration | Permissive CORS, missing CSP, exposed stack traces |
| A06 | Vulnerable & Outdated Components | npm dependency audits |
| A07 | Identification & Authentication Failures | JWT misuse, insecure session management |
| A08 | Software & Data Integrity Failures | Supply-chain attacks, missing Subresource Integrity |
| A09 | Security Logging & Monitoring Failures | Client-side error telemetry leaking PII |
| A10 | Server-Side Request Forgery (SSRF) | URL-parameter-driven fetch calls |

---

## XSS (Cross-Site Scripting)

**What:** Attacker-controlled HTML/JS injected into the page, executing in the victim's browser session.

**Severity:** High — can steal cookies, tokens, perform actions as the victim.

**Types:**
- **Reflected:** payload in URL, reflected in response.
- **Stored:** payload persisted to DB, rendered for other users.
- **DOM-based:** JavaScript reads from URL/storage and writes to the DOM unsafely.

**Prevention:**
- Use frameworks that auto-escape by default (React, Vue, Angular). Avoid `dangerouslySetInnerHTML` / `v-html` / `[innerHTML]` unless content is explicitly sanitized.
- Sanitize any user-generated HTML before rendering: use `DOMPurify` (browser) or `sanitize-html` (server-side).
- CSP as a secondary control (see below) — limits damage if XSS occurs.
- Never construct HTML via string concatenation.

**Common mistakes:**
- `element.innerHTML = userInput` — always use `textContent` for text.
- Trusting sanitization of rich text without allowlisting tags.
- Bypassing framework escaping to "render HTML from the server."

---

## Content Security Policy (CSP)

**What:** HTTP response header instructing the browser which sources of scripts, styles, and other resources are trusted.

**Why:** Mitigates XSS by blocking inline scripts and unauthorized external script sources.

**Recommended starting policy:**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.yourservice.com;
  font-src 'self';
  object-src 'none';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

**Rules:**
- Avoid `'unsafe-inline'` for scripts — use nonces or hashes instead.
- Avoid `'unsafe-eval'` — disallows eval/Function constructor.
- Add `report-uri` / `report-to` to surface violations in prod.
- Test with `Content-Security-Policy-Report-Only` before enforcing.

---

## CSRF (Cross-Site Request Forgery)

**What:** Malicious site triggers authenticated requests to your API using the victim's cookies.

**Severity:** High — can perform state-changing actions (password change, funds transfer).

**Prevention:**
- **SameSite cookies:** set `SameSite=Strict` or `SameSite=Lax` on session cookies. `Lax` is the browser default now but don't rely on it.
- **CSRF tokens:** for form submissions, embed a secret token validated server-side.
- **Double-submit cookie pattern:** if stateless, match a cookie value with a header value.
- APIs that use `Authorization: Bearer` headers (not cookies) are inherently CSRF-safe — cross-site requests can't set custom headers.

**Common mistakes:**
- `SameSite=None; Secure` without understanding the CSRF implication.
- Not including CSRF token validation for state-changing GET endpoints.
- Relying on `Origin` header checking alone without a CSRF token fallback.

---

## CORS Configuration

**What:** Browser mechanism controlling which origins can make cross-origin requests to your API.

**Severity:** High if misconfigured — can expose API to any web page.

**Rules:**
- Never use `Access-Control-Allow-Origin: *` for endpoints that handle authenticated data.
- Allowlist specific origins explicitly; fail closed for unlisted origins.
- Do not reflect `Origin` header back without validation.
- Restrict allowed methods and headers to the minimum required.
- `Access-Control-Allow-Credentials: true` must never be paired with `*` origin.

**Common mistakes:**
- Blanket wildcard origin for "convenience during development" that ships to production.
- Reflecting any `Origin` value back unconditionally.

---

## Authentication Flows — OAuth & OIDC

**What:** Delegated authorization (OAuth 2.0) and identity (OIDC) patterns for web clients.

**Rules:**
- Use **Authorization Code Flow + PKCE** for SPAs and mobile. Never Implicit Flow (tokens in URL fragment).
- Validate `state` parameter to prevent CSRF on the callback.
- Validate `nonce` in ID token to prevent replay.
- Use short-lived access tokens (15 min–1 hr) with refresh token rotation.
- Store tokens in memory (JS variable) when possible; use httpOnly cookies as a fallback (see below).
- Never store tokens in `localStorage` — accessible to any XSS payload.

---

## Token & Session Storage

**What:** Where to keep auth tokens in the browser.

**Severity:** High — wrong choice exposes tokens to XSS or CSRF.

| Option | XSS risk | CSRF risk | Recommended? |
|---|---|---|---|
| `localStorage` | High (any script reads it) | Low | No for sensitive tokens |
| `sessionStorage` | High | Low | No for sensitive tokens |
| In-memory (JS var) | Low (lost on refresh) | Low | Yes for access tokens |
| `httpOnly` cookie | Low (JS can't read) | Medium (use SameSite) | Yes for refresh tokens |

**Pattern:** store access token in memory, refresh token in `httpOnly; SameSite=Lax; Secure` cookie. Refresh silently via a `/refresh` endpoint on page load.

---

## JWT Pitfalls

**What:** JSON Web Tokens are widely used but easy to misuse.

**Severity:** Critical for the `alg: none` attack; High for others.

| Pitfall | Severity | Fix |
|---|---|---|
| Accepting `alg: none` | Critical | Explicitly specify expected algorithm; reject `none` |
| Accepting RS256 when you sign HS256 | Critical | Validate `alg` header before processing |
| Storing full JWT in localStorage | High | Use memory + httpOnly refresh token |
| Not validating `exp` / `iss` / `aud` | High | Validate all standard claims |
| Very long expiry (days/weeks) | Medium | Use 15-min access tokens + refresh rotation |
| Sensitive data in payload | Medium | JWT is base64, not encrypted — use opaque tokens for PII |

---

## Subresource Integrity (SRI)

**What:** Browser verifies that external scripts/styles match a known hash before executing.

**Why:** Prevents supply-chain compromise via CDN tampering.

**How:**
```html
<script
  src="https://cdn.example.com/lib.js"
  integrity="sha384-<base64-hash>"
  crossorigin="anonymous">
</script>
```

**Rules:**
- Add `integrity` attribute to all third-party `<script>` and `<link>` tags loaded from CDNs.
- Pin the hash in your codebase; update deliberately on version upgrades.
- Self-hosted scripts don't need SRI but should be versioned/immutable.

---

## Dependency & Supply-Chain Security

**What:** Third-party npm packages are a significant attack surface (typosquatting, malicious maintainer takeover, transitive vulnerabilities).

**Rules:**
- Run `npm audit` (or `pnpm audit`) in CI; fail on high/critical severity.
- Use `npm ci` in CI — installs from lockfile exactly, no floating resolutions.
- Enable Dependabot or Renovate for automated PR-based upgrades.
- Pin exact versions or ranges conservatively in `package.json`.
- Review package owners and download counts before adding new dependencies.
- Never `npm install` from URLs or local paths in production packages.
- Use `socket.dev` or similar for supply-chain scanning on large projects.

**Common mistakes:**
- `"*"` or `"^latest"` version pins.
- Adding packages without checking their transitive dependencies.
- Not auditing after a major dependency upgrade.

---

## Secure Cookie Attributes

| Attribute | Purpose |
|---|---|
| `HttpOnly` | Prevents JS access — mitigates XSS token theft |
| `Secure` | Cookie only sent over HTTPS |
| `SameSite=Lax` | Blocks cross-site POST — CSRF mitigation (use `Strict` for stricter) |
| `Path` | Scope cookie to specific path |
| `Max-Age` / `Expires` | Explicit expiry; absence = session cookie |

Always set `HttpOnly`, `Secure`, and `SameSite` on auth cookies. Never set `SameSite=None` without a documented reason.

---

## Client-Side Error Telemetry

**What:** Frontend error tracking (Sentry, Datadog, Rollbar) can inadvertently capture PII or secrets.

**Rules:**
- Configure `beforeSend` hooks to scrub sensitive fields before transmission.
- Exclude `Authorization` headers, request bodies from auth endpoints, and form values.
- Set `sendDefaultPii: false` (Sentry default) and opt in only for needed fields.
- Review what the SDK captures automatically — many capture full request/response bodies by default.

---

## Common Pitfalls

| Pitfall | Severity | Fix |
|---|---|---|
| `dangerouslySetInnerHTML` with user content | High | DOMPurify + allowlist |
| `localStorage` for access tokens | High | In-memory storage |
| CORS `*` on authenticated endpoints | High | Explicit origin allowlist |
| No CSP header | Medium | Add CSP; start in report-only mode |
| Missing `HttpOnly` on session cookie | High | Always set on auth cookies |
| JWT `alg: none` accepted | Critical | Validate algorithm explicitly |
| No `state` param in OAuth callback | High | Generate + validate `state` |
| CDN scripts without SRI | Medium | Add `integrity` attribute |
| npm dependencies not audited in CI | Medium | `npm audit --audit-level=high` in pipeline |
| Logging `req.body` / response on auth endpoints | High | Log only path + status code |
