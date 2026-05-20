# Security — Backend

Backend-specific security KB. Builds on `00_general.md`. Covers API servers, databases, and infrastructure. Frontend concerns are in `01_web.md`.

OWASP reference: **OWASP API Security Top 10** (2023). https://owasp.org/www-project-api-security/

---

## OWASP API Security Top 10 Summary (2023)

| # | Risk | Notes |
|---|---|---|
| API1 | Broken Object Level Authorization (BOLA) | Every request must verify the caller owns the resource |
| API2 | Broken Authentication | Weak token validation, missing expiry checks |
| API3 | Broken Object Property Level Authorization | Mass assignment, over-exposed response fields |
| API4 | Unrestricted Resource Consumption | Missing rate limiting, unbounded queries |
| API5 | Broken Function Level Authorization | Admin endpoints accessible to regular users |
| API6 | Unrestricted Access to Sensitive Business Flows | Brute-force of OTP, purchase flows |
| API7 | Server-Side Request Forgery (SSRF) | URL-parameter-driven outbound requests |
| API8 | Security Misconfiguration | Debug endpoints, CORS misconfiguration, verbose errors |
| API9 | Improper Inventory Management | Shadow APIs, undocumented internal endpoints |
| API10 | Unsafe Consumption of APIs | Trusting third-party APIs without re-validation |

---

## Authentication

**What:** Verify the identity of callers before granting access to protected resources.

**Severity:** Critical — auth bypass is a direct path to full system compromise.

### Password Storage

- Never store plaintext passwords.
- Use **argon2id** (preferred) or bcrypt (min cost 12) or scrypt. Never MD5/SHA-1/SHA-256 alone.
- Always use a per-user random salt (built into argon2/bcrypt).
- Enforce minimum password complexity at the API level, not just the frontend.

### Session Tokens

- Generate session tokens using CSPRNG (min 128 bits).
- Store sessions server-side (Redis/DB); invalidate on logout.
- Set session cookie attributes: `HttpOnly`, `Secure`, `SameSite=Lax`, explicit `Max-Age`.

### JWT

- Sign with RS256 or EdDSA (asymmetric) for APIs consumed by third parties; HS256 is acceptable for internal services where key distribution is controlled.
- Validate: `exp` (expiry), `iss` (issuer), `aud` (audience), `nbf` (not before).
- Reject tokens with `alg: none`. Explicitly specify acceptable algorithms.
- Keep access token TTL short (15 min–1 hr). Use refresh token rotation with one-time use.
- Store signing keys in a secrets manager or KMS, not in source code.
- Revocation: for sensitive actions, maintain a short-lived deny-list or use opaque tokens with server-side session lookup.

---

## Authorization

**What:** Verify that an authenticated caller is permitted to perform the requested action on the requested resource.

**Severity:** Critical — missing authorization checks are BOLA (API1) / privilege escalation.

### Principle

- **AuthN ≠ AuthZ.** "You are who you say you are" does not mean "you can do what you're asking."
- Re-check authorization on every request, even for the same resource. Never cache authorization decisions across requests.

### RBAC vs ABAC

| Model | When to use |
|---|---|
| **RBAC** (Role-Based Access Control) | Clear user roles (admin/editor/viewer); permissions map to roles |
| **ABAC** (Attribute-Based Access Control) | Fine-grained policies based on resource attributes and context (e.g., "owner only", "same org only") |

In practice: RBAC for coarse-grained access (can access admin panel), ABAC/BOLA checks for row-level ("can modify this specific record").

### Row-Level Security (RLS)

- For databases that support it (Supabase/PostgreSQL), define RLS policies so the DB enforces access, not just application code.
- Test RLS policies explicitly — a missing `USING` clause can expose all rows.
- RLS is defense-in-depth; application-layer checks should still exist.

```sql
-- Example: users can only read their own rows
CREATE POLICY "users_own_data"
  ON game_saves FOR SELECT
  USING (auth.uid() = user_id);
```

---

## SQL Injection Prevention

**What:** Attacker-controlled input interpreted as SQL commands.

**Severity:** Critical — can result in full data exfiltration, deletion, or auth bypass.

**Prevention:**
- Use **parameterized queries** or **prepared statements** in every database interaction. Never concatenate user input into SQL.
- ORMs (Prisma, SQLAlchemy, Hibernate, Drift) use parameterization by default — verify you're not bypassing it with raw query methods.
- If raw SQL is necessary, use the ORM's raw-but-parameterized API (`db.execute(sql, params)` not string interpolation).
- Principle of least privilege for DB users: the app DB user should have DML (SELECT/INSERT/UPDATE/DELETE) only — no DDL.

```typescript
// Bad
db.query(`SELECT * FROM users WHERE id = '${userId}'`);

// Good
db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

**Common mistakes:**
- ORM `.rawQuery()` or `.execute()` calls with string interpolation.
- Search/filter parameters passed directly into ORDER BY clauses (column names can't be parameterized — use an allowlist).
- Logging query text with embedded values.

---

## Input Validation at Request Boundary

**What:** Validate all incoming data (body, query params, path params, headers) before processing.

**Rules:**
- Validate type, length, format, range, and content at the API boundary. Reject early with a clear 400 error.
- Use a schema validation library (Zod, Joi, Yup, Pydantic, class-validator) — don't handroll.
- Prevent **mass assignment**: explicitly allowlist fields that can be set by the client. Never pass `req.body` directly to an ORM `create()` / `update()`.
- Strip unknown fields before processing; don't silently ignore them.

---

## Output Encoding

**What:** Encode data for its output context to prevent injection.

| Context | Encoding needed |
|---|---|
| HTML response | HTML-entity encode user data |
| SQL | Parameterized queries |
| Shell command | Avoid shell; if necessary, use argument arrays not strings |
| JSON | JSON serialization (no string interpolation) |
| File path | Normalize and validate; prevent path traversal |

**Path traversal:**
```python
# Bad
open(f"/uploads/{user_filename}")

# Good
safe_path = os.path.realpath(os.path.join('/uploads', filename))
if not safe_path.startswith('/uploads/'):
    raise ValueError('Invalid path')
open(safe_path)
```

---

## Rate Limiting & Brute-Force Protection

**What:** Limit request frequency to prevent credential stuffing, brute force, and resource abuse.

**Severity:** High for auth endpoints; Medium for general API.

**Rules:**
- Rate-limit all auth endpoints (`/login`, `/register`, `/forgot-password`, `/verify-otp`) by IP and by account.
- Implement exponential backoff or account lockout after N consecutive failures (be careful with lockout — it can be abused for DoS; prefer slow-down over hard lockout).
- Limit expensive or abusable endpoints (search, bulk operations, AI inference).
- Apply rate limiting at the edge (CDN/load balancer) and as defense-in-depth in the application layer.
- Return 429 Too Many Requests with `Retry-After` header.

**Supabase:** Use Supabase Auth's built-in rate limiting for auth operations. For custom API routes (Edge Functions), implement rate limiting via Upstash Redis or similar.

---

## Secrets Management

**What:** Backend services depend on secrets (DB passwords, API keys, signing keys) that must not appear in source code or unencrypted config.

**Rules:**
- Load secrets from environment variables injected at runtime; never commit `.env` files with real secrets.
- In production: use a secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, Doppler).
- Rotate secrets on a schedule (90 days for API keys; immediately on suspected exposure).
- Audit secret access: secrets managers log every read — alert on unusual access patterns.
- CI/CD: use CI platform secret storage (GitHub Actions secrets, CircleCI contexts) — never plaintext in workflow files.
- Never log secrets; ensure error messages don't include DB connection strings or API keys.

---

## mTLS (Mutual TLS) for Service-to-Service

**What:** Both sides of a connection present certificates, providing cryptographic identity for service-to-service calls.

**When:** Microservice architectures where internal services should verify each other's identity. Zero-trust internal networks.

**Rules:**
- Issue short-lived certs via internal CA (SPIFFE/SPIRE, cert-manager on Kubernetes).
- Rotate certificates before expiry; automate rotation.
- Fail closed if peer certificate is invalid or expired.

---

## Audit Logging

**What:** Immutable log of who performed what action on which resource at what time.

**Severity:** Medium — absence is a compliance and incident-response failure.

**What to log:**
- Authentication events: login, logout, failed attempts, password changes, MFA events.
- Authorization decisions for sensitive resources.
- Data access on high-sensitivity records (PII, financial).
- Admin actions: config changes, user management, role changes.
- System events: deployments, secret rotations, schema migrations.

**What NOT to log:**
- Passwords, tokens, API keys (even in "redacted" form — strip completely).
- Full request/response bodies on auth endpoints.
- PII beyond necessary identifiers (use user ID, not email).

**Format:**
```json
{
  "timestamp": "2026-01-15T10:23:00Z",
  "event": "auth.login_success",
  "actor_id": "usr_abc123",
  "ip": "1.2.3.4",
  "resource": null,
  "outcome": "success"
}
```

**Storage:** Write audit logs to append-only storage (immutable S3 bucket, dedicated audit log table with insert-only policy). Never allow application code to delete audit logs.

---

## Error Handling

**What:** Error responses must not leak internal implementation details.

**Severity:** Medium — verbose errors accelerate attacker reconnaissance.

**Rules:**
- Return generic error messages to clients: "An error occurred" not stack traces.
- Log the full error (with stack trace) internally; return only an error code + correlation ID to the client.
- Use consistent error shapes across your API.
- Do not differentiate "user not found" from "wrong password" on login endpoints — merge into "invalid credentials."
- Remove debug middleware / stack trace rendering from production deployments.

---

## Dependency & Supply-Chain Security

**What:** Backend packages are a significant and frequently exploited attack surface.

**Rules:**
- Pin dependencies with lockfiles (`package-lock.json`, `poetry.lock`, `Cargo.lock`). Never floating versions in production.
- Run `npm audit` / `pip-audit` / `cargo audit` in CI; fail on high/critical.
- Automate dependency updates via Dependabot or Renovate with automatic merging for patch-level updates.
- Review changelogs for major version upgrades.
- Vet new dependencies: check maintainer identity, download count, last commit date, open security issues.

---

## Idempotent & Replay-Safe Endpoints

**What:** State-changing endpoints (payment, purchase, state mutation) must handle duplicate requests safely.

**Severity:** High for financial operations; Medium for others.

**Rules:**
- Accept an idempotency key from the client (UUID per request attempt).
- Store the result of the first execution; return the stored result for subsequent identical requests.
- Validate the idempotency key is scoped to the authenticated user — prevent cross-user replay.
- Use database transactions to ensure atomicity of the idempotency check + operation.

---

## Common Pitfalls

| Pitfall | Severity | Fix |
|---|---|---|
| No BOLA check (fetching any record by ID) | Critical | Verify `owner_id = current_user_id` on every row fetch |
| `alg: none` JWT accepted | Critical | Explicitly validate algorithm |
| Password hashed with SHA-256 (no salt, no KDF) | Critical | Migrate to argon2id with re-hash on next login |
| Raw SQL with string interpolation | Critical | Parameterized queries everywhere |
| Mass assignment via `req.body` to ORM | High | Explicit field allowlist |
| No rate limiting on login endpoint | High | Add per-IP + per-account rate limiting |
| Stack traces in 500 responses | Medium | Generic error + correlation ID |
| Secrets in environment variables baked into Docker image | High | Runtime injection via secrets manager |
| Audit logs deletable by app | High | Append-only storage policy |
| ORDER BY from user input without allowlist | High | Allowlist column names before interpolation |
| DB user has DDL rights | Medium | Principle of least privilege — DML only |
| No `exp` / `iss` / `aud` JWT validation | High | Validate all standard claims on every request |
| Supabase `service_role` key exposed to clients | Critical | Server-side only; never in mobile/web app |
