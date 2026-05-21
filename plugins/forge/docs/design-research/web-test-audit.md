# Web Project Test Infrastructure Audit

**Date:** 2026-05-21
**Branch:** feature/forge-78-manual-testing-automation
**Ticket:** #79 — Audit existing web projects (current test setup)

---

## Projects Audited

### 1. reddit-idea-forge

| Attribute      | Value |
|----------------|-------|
| Stack          | Next.js 16 / React 19 / TypeScript / Tailwind 4 |
| Package manager | pnpm |
| Unit test runner | **none** |
| E2E tool       | **none** |
| Test config files | none found |
| Test directories | none found (`src/` has `app/`, `components/`, `lib/`, `hooks/` — no `__tests__/` or `e2e/`) |
| Coverage tooling | none |
| CI pipeline    | `.github/workflows/cron-pipeline.yml` — cron-triggered HTTP hits only; **no test step** |

**Gaps:**
- No unit tests whatsoever
- No E2E coverage
- No `test` script in `package.json` (only `dev`, `build`, `start`, `lint`)
- CI pipeline exists but only for scheduled cron jobs — no test gating on PR or push
- No `@playwright/test`, `jest`, `vitest`, or `@testing-library/*` in dependencies

---

### 2. scaffold-tryout

| Attribute      | Value |
|----------------|-------|
| Stack          | Flutter (Dart) — `pubspec.yaml` only; no web layer |
| Unit test runner | Flutter test (`widget_test.dart`, `smoke_test.dart` found in `test/`) |
| E2E tool       | none |
| CI pipeline    | none found |

**Note:** This is a pure Flutter project — out of scope for the `forge:e2e-web` opt-in. Included here for completeness. The Flutter test infra will be handled by the separate Flutter testing path.

---

### 3. VolatiLens

| Attribute      | Value |
|----------------|-------|
| Top-level structure | `volatilens-backend/` (NestJS + Supabase), `volatilens-mobile/` (Flutter) |
| Web layer      | NestJS API only (no dedicated frontend project) |
| Unit test runner | `volatilens-backend/` has no `package.json` — contains only a `supabase/` directory and `README.md`; mobile layer is Flutter |
| E2E tool       | none |
| CI pipeline    | none found |

**Note:** No standalone frontend/web app exists here. The backend is Supabase-managed; there is no application server to E2E test with a browser driver. Excluded from `forge:e2e-web` scope.

---

### 4. PantryPal

| Attribute      | Value |
|----------------|-------|
| Top-level structure | `pantrypal-backend/` (NestJS), `pantrypal-mobile/` (Flutter) |
| Web layer      | NestJS REST API (no browser frontend) |
| Package manager | pnpm |
| Unit test runner | **Jest** (via `ts-jest`) — configured in `package.json` `jest` block |
| Unit test pattern | `src/**/*.spec.ts` (rootDir: `src`) |
| Unit test files | 10+ `.spec.ts` files across controllers, services, repositories, filters, processors |
| E2E test runner | Jest via `test/jest-e2e.json` (still Jest, not a browser driver) |
| E2E test files | `test/app.e2e-spec.ts`, `test/recipes.e2e-spec.ts`, `test/pantry-scans.e2e-spec.ts` |
| Coverage tooling | `jest --coverage`; `coverageDirectory: ../coverage`; collects from all `.ts` in `src/` |
| CI pipeline    | none found (no `.github/workflows/` at project root) |
| Test scripts   | `test`, `test:watch`, `test:cov`, `test:debug`, `test:e2e` |

**Gaps:**
- No CI test gate (tests exist but are only run manually)
- "E2E" here is HTTP-level integration (supertest against NestJS app) — not browser E2E
- No `@playwright/test` or Cypress

---

## Cross-Cutting Findings

### Who needs Playwright
| Project | Verdict |
|---------|---------|
| reddit-idea-forge | **Yes** — primary Next.js web app; user flows (auth, AI generation, browsing) require browser E2E |
| scaffold-tryout | No — Flutter only |
| VolatiLens | No — no browser frontend |
| PantryPal | No — API only; existing Jest supertest e2e is appropriate |

### Who needs basic unit test setup
| Project | Verdict |
|---------|---------|
| reddit-idea-forge | **Yes** — zero test infrastructure; needs Vitest (aligns with Next.js 14+ community standard) or Jest |
| scaffold-tryout | Has Flutter tests; out of scope |
| VolatiLens | N/A |
| PantryPal | Already has Jest; coverage configured |

### Common patterns observed
- NestJS projects default to Jest + ts-jest (NestJS CLI scaffolds this)
- Flutter projects default to `flutter test` widget tests
- Next.js project has no test tooling at all — a common "start fast, test later" gap
- pnpm is the package manager across all JS projects
- No project has a CI test gate on PRs (only reddit-idea-forge has CI at all, but it's cron-only)

---

## Recommendation: forge:e2e-web opt-in defaults

**Target:** Next.js / React web projects (primary use case: reddit-idea-forge)

**Recommended defaults:**

| Layer | Tool | Rationale |
|-------|------|-----------|
| E2E runner | `@playwright/test` | De-facto standard; first-party TS support; no separate config package needed; excellent Next.js integration via `webServer` option |
| Config file | `playwright.config.ts` | TypeScript config; ts-node not required — Playwright resolves `.ts` config natively via esbuild |
| Test directory | `e2e/` at project root | Keeps E2E separate from `src/`; matches Playwright docs convention |
| Base URL | `http://localhost:3000` | Next.js dev server default |
| Browsers | Chromium only (default install) | Minimal install footprint for a solo-dev setup; user can opt in to webkit/firefox |
| CI command | `pnpm exec playwright test` | Matches pnpm workspace convention seen across projects |
| Reporters | `list` (dev), `html` (CI) | Minimal noise locally; rich report in CI |
| `webServer` block | yes, `pnpm dev`, port 3000, `reuseExistingServer: !process.env.CI` | Lets dev run against the live dev server; CI always starts fresh |

**Opt-in script additions to `package.json`:**
```json
{
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui"
}
```

**What forge:e2e-web should NOT install by default:**
- `cypress` (heavier; not needed when Playwright covers the same ground)
- `ts-node` (Playwright handles TS config natively)
- `@playwright/experimental-ct-react` (component testing — separate concern)
- Multiple browser engines (Chromium only by default)

**Future: unit test opt-in (separate from e2e-web)**
- reddit-idea-forge also needs a unit test opt-in (`vitest` + `@testing-library/react` + `@testing-library/jest-dom`)
- That should be a separate `forge:unit-web` or built into `forge:e2e-web` as an independent toggle

---

## Summary Table

| Project | Stack | Unit runner | E2E tool | CI test cmd | Priority |
|---------|-------|-------------|----------|-------------|----------|
| reddit-idea-forge | Next.js 16 / TS | none | none | none | HIGH — needs both |
| scaffold-tryout | Flutter | flutter test | none | none | Out of scope |
| VolatiLens | Supabase + Flutter | none | none | none | Out of scope (no web app) |
| PantryPal/backend | NestJS / Jest | Jest + ts-jest | Jest supertest | none | Medium — add CI gate |
