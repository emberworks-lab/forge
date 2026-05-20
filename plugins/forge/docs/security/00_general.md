# Security — General Principles

Universal security foundation. Platform-specific files (`01_web.md`, `02_mobile_flutter.md`, `04_backend.md`) build on this.

---

## Defense in Depth

**What:** Layer multiple independent controls so no single failure compromises the system.

**Why:** Attackers chain weaknesses. A single-layer defense collapses once that layer is bypassed.

**Common mistakes:**
- Relying solely on perimeter firewalls with no internal controls.
- Trusting that a framework "handles security" without verifying which controls it actually provides.

**How:** Apply controls at network, transport, application, and data layers independently. Each layer should enforce its own checks, not assume an upstream layer already did.

---

## Least Privilege

**What:** Grant only the permissions needed for a task, for only as long as needed.

**Why:** Over-privileged components dramatically expand blast radius when compromised.

**Common mistakes:**
- Service accounts with admin roles because it was "easier to set up."
- Long-lived tokens with broad scopes.
- DB users with DDL rights when DML is all that's needed.

**How:** Scope tokens, roles, and API keys to the minimum required operation. Prefer short-lived credentials with refresh. Review permissions during code review.

---

## Secure Defaults

**What:** The system is secure out of the box; insecure options require explicit opt-in.

**Why:** Most deployments use defaults. Insecure defaults lead to mass exploitation.

**Common mistakes:**
- Shipping with debug endpoints enabled in production.
- Permissive CORS (`*`) as a default.
- No authentication on admin routes "temporarily."

**How:** Default to deny. Default to HTTPS. Default to strictest CSP/CORS. Require explicit configuration to loosen any restriction.

---

## Fail Closed (Fail Secure)

**What:** On error or ambiguous state, deny access rather than allow it.

**Severity:** High — fail-open conditions are a direct path to privilege escalation.

**Common mistakes:**
- Auth checks that return `true` on exception.
- Circuit breakers that bypass auth under load.
- Default branch in permission checks that grants access.

**How:**
```
// Bad — exception causes allow
try { return checkPermission(user, resource); }
catch (e) { return true; }

// Good — exception causes deny
try { return checkPermission(user, resource); }
catch (e) { return false; }
```

---

## Zero Trust Between Layers

**What:** Each internal layer authenticates and validates requests from upstream layers; no implicit trust because a call is internal.

**Why:** Lateral movement after an initial compromise can reach the entire system if internal traffic is trusted blindly.

**Common mistakes:**
- Backend services that skip authorization because "only our API gateway calls them."
- Microservices that accept any service-to-service call without mTLS or token verification.

**How:** Validate tokens/signatures at every service boundary. Use mTLS for service-to-service where feasible. Treat internal networks as hostile after initial breach.

---

## Secrets Management

**What:** Cryptographic keys, API tokens, passwords, and certificates must never appear in source code, logs, or unencrypted storage.

**Severity:** Critical — exposed secrets are an immediate compromise.

**Never:**
- Commit secrets to version control (even private repos — assume git history is semi-public).
- Store secrets in environment variables baked into Docker images or deployment artifacts.
- Log secrets at any level (debug included).

**How:**
- Development: `.env` files excluded by `.gitignore`; use `.env.example` with placeholder values.
- Production: use a secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, Doppler).
- Rotation cadence: rotate on suspected exposure immediately; rotate on a schedule (e.g., 90-day policy for long-lived tokens).
- Detect pre-commit via tools like `git-secrets`, `truffleHog`, `gitleaks`.

---

## Cryptography — Use Platform Primitives

**What:** Use OS/platform-provided or well-audited library implementations. Never implement crypto algorithms from scratch.

**Why:** Custom crypto is nearly always broken in subtle, exploitable ways. Even correct algorithms are easy to misuse (e.g., reusing IVs).

**Severity:** High for misuse of standard APIs; Critical for homebrew algorithms.

**Rules:**
- Symmetric encryption: AES-256-GCM (authenticated). Never ECB mode.
- Hashing (integrity): SHA-256 minimum. MD5/SHA-1 are broken for security use.
- Password hashing: argon2id (preferred), bcrypt (min cost 12), scrypt. Never SHA/MD5 for passwords.
- Random: use OS CSPRNG (`SecureRandom`, `crypto.getRandomValues`, `/dev/urandom`). Never `Math.random()` for security tokens.
- IVs/nonces: generate fresh per-encryption. Never reuse a nonce with the same key.
- Key derivation: PBKDF2 / HKDF / argon2 — never use raw passwords as keys.

---

## PII Handling & GDPR Basics

**What:** Personally Identifiable Information (PII) requires explicit handling controls beyond general data.

**Principles:**
- **Data minimization:** collect only what you need for a declared purpose.
- **Purpose limitation:** don't repurpose data beyond what users consented to.
- **Storage limitation:** delete data when purpose is fulfilled or user requests it.
- **Right to erasure:** system must be able to delete a user's data on request (including backups/logs).

**Common mistakes:**
- Logging user IDs + email + actions together (creates a behavior profile in logs).
- Storing IP addresses indefinitely without a legal basis.
- Not having a documented data retention policy.

**How:**
- Classify fields as PII at schema design time. Mark in code comments / schema annotations.
- Never log PII. Log opaque user IDs if needed for debugging.
- Pseudonymize analytics data.
- Document the legal basis for each PII collection.

---

## Logging Discipline

**What:** Logs must be useful for incident response without being a secondary data breach vector.

**Rules:**
- **Never log:** passwords, tokens, API keys, credit card numbers, SSNs, full PII (email, phone, address).
- **Sanitize:** stack traces may contain variable values — scrub before logging.
- **Redact:** log `user_id` not `email`; log request shape not request body when it may contain credentials.
- **Severity levels:** use consistently — CRITICAL for production incidents, ERROR for unexpected failures, WARN for recoverable anomalies, INFO for significant business events, DEBUG never in prod.

**Common mistakes:**
- `console.log(req.body)` / `print(request)` on auth endpoints.
- Exception messages that include SQL query text with embedded values.
- Logging the full JWT (includes user claims).

---

## Input Validation at Trust Boundaries

**What:** Validate all data at every point where it crosses a trust boundary (network → application, client → server, service → service).

**Why:** Downstream operations (SQL, HTML rendering, shell, file access) interpret input literally — attacker-controlled input becomes attacker-controlled behavior.

**Rules:**
- Validate type, length, format, and range before processing.
- Reject-then-allow (allowlist), not allow-then-reject (denylist).
- Re-validate after deserialization — data can be mutated in transit.
- Never pass raw user input to SQL, shell, HTML renderers, file paths, or eval.

---

## SDLC Integration

**What:** Security controls integrated throughout the development lifecycle, not bolted on at release.

**Checklist:**
- [ ] Threat model new features before implementation (at least informally: "what could go wrong?")
- [ ] Security review for auth, payment, PII, or crypto-touching PRs
- [ ] Dependency audit in CI (`npm audit`, `pip-audit`, `flutter pub audit`)
- [ ] Secret scanning in CI (gitleaks, truffleHog, GitHub secret scanning)
- [ ] SAST in CI for high-severity patterns
- [ ] Manual penetration test or security review before first public launch

---

## Severity Scale

Used consistently across all platform KB files:

| Severity | Meaning |
|---|---|
| **Critical** | Direct path to system compromise, data exfiltration, or authentication bypass. Fix before merge. |
| **High** | Significant security impact; exploitable by motivated attacker. Fix in current sprint. |
| **Medium** | Exploitable under specific conditions or with attacker assistance. Fix before next release. |
| **Low** | Defense-in-depth improvement; no direct exploit path known. Fix opportunistically. |

---

## Common Pitfalls

| Pitfall | Severity | Fix |
|---|---|---|
| Secrets committed to git | Critical | Remove from history (`git filter-branch` / BFG); rotate immediately |
| Debug endpoints in production | High | Feature-flag behind env check; blocked in production build |
| Auth check that returns true on exception | High | Fail closed — catch → return false |
| Logging `request.body` on auth routes | High | Log request path + method only |
| Using `Math.random()` for CSRF tokens | High | Use CSPRNG |
| MD5/SHA-1 for password hashing | Critical | Migrate to argon2id/bcrypt |
| Re-using AES-GCM nonces | Critical | Generate fresh nonce per encryption |
| Trusting internal network calls without verification | Medium | Add service-to-service auth |
| Over-privileged DB user | Medium | Create read-only / limited-scope DB users per service |
| No data retention policy for PII | Medium | Define and automate retention/deletion |

---

## OWASP References

These principles map directly to the OWASP frameworks used in platform-specific files:

- **OWASP Top 10** (web — 2021): https://owasp.org/Top10/ — the general principles here address A01–A10 at the foundational layer.
- **OWASP API Security Top 10** (2023): https://owasp.org/www-project-api-security/ — zero trust, least privilege, fail closed, and input validation all apply.
- **OWASP Mobile Top 10** (2024): https://owasp.org/www-project-mobile-top-10/ — secure defaults, secrets management, and crypto principles underpin M1–M10.
- **OWASP WSTG** (Web Security Testing Guide): https://owasp.org/www-project-web-security-testing-guide/ — reference for security review test cases.
- **OWASP MASTG** (Mobile Application Security Testing Guide): https://mas.owasp.org/ — reference for mobile security review.
