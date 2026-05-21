# skill-templates / web-nextjs

Generic Next.js 15 starter extracted from reddit-idea-forge. Scaffolded by `/project-init`.

## What's included (core)

| File | Purpose |
|---|---|
| `package.json` | Next.js 15 + React 19 + TypeScript + Tailwind 4 + ESLint 9 + pnpm |
| `tsconfig.json` | Strict TypeScript, `@/*` path alias pointing to `src/` |
| `next.config.ts` | Minimal — no project-specific config |
| `postcss.config.mjs` | `@tailwindcss/postcss` plugin |
| `eslint.config.mjs` | `eslint-config-next` core-web-vitals + typescript |
| `app/layout.tsx` | Root layout with Inter font + `{{ project_name }}` metadata placeholder |
| `app/globals.css` | Tailwind import + global antialiasing resets |
| `app/page.tsx` | Minimal placeholder home page |

## What's NOT included (opt-in)

These are available as ready-to-follow guides in `_common/manual-setup-templates/`:

| Feature | Guide |
|---|---|
| Error monitoring | `sentry.md` |
| Database / auth | `supabase.md` |
| Auth providers | `github-auth.md` |
| Analytics / events | *(add your own)* |
| i18n | *(add your own)* |

## Opt-in modules

See `OPT_IN_MODULES.md` for the full list. Quick reference:

### Playwright (end-to-end testing)

Full setup guide: `plugins/forge/skill-templates/_common/manual-setup-templates/playwright.md`

1. Install: `pnpm add -D @playwright/test && npx playwright install`
2. Copy `playwright.config.ts.template` → `playwright.config.ts` (webServer points at `pnpm dev`, Chromium-only by default per the #79 audit recommendation)
3. Copy `tests/e2e/example.e2e-web.spec.ts.template` → `tests/e2e/example.e2e-web.spec.ts`
4. Add to `package.json` scripts: `"test:e2e": "playwright test"`, `"test:e2e:ui": "playwright test --ui"`
5. Add to `.gitignore`: `playwright-report/`, `test-results/`
6. Create `.claude/e2e-web.json` opt-in marker (see guide) to activate `forge:e2e-web`

Runtime invocation once set up: `forge:e2e-web` (`plugins/forge/skills/e2e-web/SKILL.md`, issue #80)

## Quick start

```bash
# 1. Replace all {{ project_name }} / {{ project_description }} placeholders
# 2. Install dependencies
pnpm install

# 3. Start dev server
pnpm dev
```

## Planned kit skills

When the first feature is added, `/project-init` will offer to write these stubs:

| Skill | Purpose |
|---|---|
| `kit-create-feature.md` | Component + hook + types scaffold |
| `kit-add-route.md` | New app-router page + layout |
| `kit-add-api-route.md` | New `/api/*` route handler |
| `kit-deploy.md` | Build + deploy to Vercel / Cloudflare |

## Source

Extracted from `reddit-idea-forge` (emberworks_lab_projects). Project-specific dependencies
(Supabase, Sentry, custom AI SDKs, design tokens) were stripped. Structure and config patterns kept.
