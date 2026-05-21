## Why

Playwright provides reliable, browser-native end-to-end testing across Chromium, Firefox, and WebKit. Adding it to a web project creates a fast-feedback loop for critical user flows — authentication, checkout, form submission — that unit tests cannot cover. The `forge:e2e-web` skill (`plugins/forge/skills/e2e-web/SKILL.md`) automates generating and running these tests; this template covers the one-time human setup required before that skill becomes active.

## Install

```bash
pnpm add -D @playwright/test
npx playwright install          # downloads Chromium, Firefox, WebKit binaries
npx playwright install-deps     # (Linux only) install OS-level browser deps
```

Add `playwright-report/` and `test-results/` to `.gitignore`.

## Config

Create `playwright.config.ts` at the project root:

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Directory where test files live
  testDir: './tests/e2e',

  // Match only *.e2e-web.spec.ts files (forge convention)
  testMatch: '**/*.e2e-web.spec.ts',

  // Run each test file in parallel; serial within a file
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,

  // Retry twice on CI; no retries locally
  retries: process.env.CI ? 2 : 0,

  // One worker on CI to avoid resource contention; auto locally
  workers: process.env.CI ? 1 : undefined,

  reporter: process.env.CI ? 'github' : 'html',

  use: {
    // Base URL — override via BASE_URL env var in CI
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',

    // Collect trace on first retry for debugging
    trace: 'on-first-retry',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox',  use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit',   use: { ...devices['Desktop Safari'] } },
  ],

  // Start the dev server automatically before running tests
  webServer: {
    command: 'pnpm dev',
    url: process.env.BASE_URL ?? 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

## First test

Create `tests/e2e/example.e2e-web.spec.ts`:

```ts
import { test, expect } from '@playwright/test';

test('home page loads and shows title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/<project_name>/i);
});

test('navigation links are visible', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('navigation')).toBeVisible();
});
```

Run locally:

```bash
npx playwright test            # headless, all browsers
npx playwright test --ui       # interactive UI mode
npx playwright show-report     # open last HTML report
```

## CI

Minimal GitHub Actions snippet (`.github/workflows/e2e.yml`):

```yaml
name: E2E

on:
  push:
    branches: [main]
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npx playwright test
        env:
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

For other CI providers (CircleCI, GitLab CI, Bitbucket Pipelines): the same four steps apply — install Node + pnpm, `pnpm install`, `npx playwright install --with-deps`, `npx playwright test`. Set `BASE_URL` to match the dev-server URL your pipeline starts.

## Conventions for the forge plugin

**File naming:** all Playwright specs must follow the pattern `*.e2e-web.spec.ts`. This is what `playwright.config.ts` above matches via `testMatch` and what `forge:e2e-web` scans when listing existing coverage.

**Opt-in marker:** create `<project-root>/.claude/e2e-web.json` to activate `forge:e2e-web` for this project:

```json
{
  "enabled": true,
  "baseURL": "http://localhost:3000",
  "testDir": "tests/e2e"
}
```

Without this file, `forge:e2e-web` will decline to run and prompt you to complete setup using this template.

**How `forge:e2e-web` uses these conventions:**

- Reads `.claude/e2e-web.json` to locate `testDir` and `baseURL`.
- Generates new spec files named `<feature>.e2e-web.spec.ts` inside `testDir`.
- Runs `npx playwright test --reporter=json` and surfaces failures inline.
- Never modifies `playwright.config.ts` — that file is owned by the human.

Cross-reference: `plugins/forge/skills/e2e-web/SKILL.md` (lands with issue #80).
