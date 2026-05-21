# CLAUDE.md — web-nextjs template

Next.js 15 + TypeScript + Tailwind 4 + ESLint 9 + pnpm project.

## Stack reminders

- **Router:** App Router only (`app/` directory). No Pages Router.
- **Data fetching:** Server Components by default. Use `"use client"` only when needed (event handlers, hooks, browser APIs).
- **Styling:** Tailwind utility classes. Global CSS lives in `app/globals.css`. No CSS modules unless added intentionally.
- **Package manager:** pnpm. Never use npm or yarn.
- **TypeScript:** Strict mode is on. No `any` unless absolutely unavoidable — prefer `unknown` + type narrowing.

## File conventions

- Pages: `app/<route>/page.tsx`
- Layouts: `app/<route>/layout.tsx`
- Server Actions: colocated in the page/component file, or `app/<route>/actions.ts`
- API routes: `app/api/<name>/route.ts`
- Shared components: `src/components/`
- Utilities: `src/lib/`
- Types: `src/types/`

## Opt-in modules

Before adding Supabase, Sentry, or other infrastructure, follow the relevant guide in
`plugins/forge/skill-templates/_common/manual-setup-templates/`.

## Forge plugin policy

Follows `plugins/forge/CLAUDE.md`. Kit skills land in `plugins/forge/skill-templates/web-nextjs/`
as the project matures.
