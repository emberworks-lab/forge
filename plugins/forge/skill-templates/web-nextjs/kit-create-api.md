---
name: kit-create-api
description: "Use when adding a new API route handler to a Next.js App Router project. Covers route-handler structure, request/response typing, error handling, Zod validation, and optional Supabase/auth opt-in seams."
---

# kit-create-api

## When to use

- Triggers: "add an API route", "create a route handler", "new server endpoint", `/kit-create-api`.
- The work adds or changes a file at `app/api/<name>/route.ts`.

Don't use for: Server Actions (colocate in the page or `actions.ts`), middleware (`middleware.ts`), or static data fetching in a Server Component.

## What it produces

- `app/api/<name>/route.ts` — exported handler(s) (`GET`, `POST`, `PATCH`, `DELETE`) using `NextRequest` / `NextResponse`
- Optional: Zod schema in `src/lib/schemas/<name>.schema.ts` when body validation is needed

## Required inputs

- Route name / path segment (e.g. `items`, `items/[id]`)
- HTTP verbs to implement
- Request input shape (query params and/or body fields)
- Success response shape
- Whether auth is required (yes / no / optional)

## Steps

1. Create `app/api/<name>/route.ts`. Start from the template below.
2. If the route accepts a body, add a Zod schema (see "Validation" section). Import it in the route handler.
3. For auth-protected routes, uncomment the Supabase auth seam (see "Optional seams" section) — only after running the Supabase opt-in guide.
4. Run `pnpm lint` and fix any warnings before reporting done.

## Route handler template

```typescript
// app/api/<name>/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // --- OPTIONAL: Supabase / auth seam (uncomment after opt-in) ---
    // import { createServerClient } from '@/lib/supabase/server'
    // const supabase = createServerClient()
    // const { data: { user } } = await supabase.auth.getUser()
    // if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // ---------------------------------------------------------------

    // Parse query params
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') ?? '1')

    // Business logic — replace with your data access
    const data: unknown[] = []

    return NextResponse.json({ data })
  } catch (error) {
    console.error('[API] <name> GET:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    // --- OPTIONAL: Supabase / auth seam (uncomment after opt-in) ---
    // const supabase = createServerClient()
    // const { data: { user } } = await supabase.auth.getUser()
    // if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    // ---------------------------------------------------------------

    const body: unknown = await request.json()

    // --- OPTIONAL: Zod validation (uncomment and replace schema) ---
    // import { NameSchema } from '@/lib/schemas/<name>.schema'
    // const parsed = NameSchema.safeParse(body)
    // if (!parsed.success) {
    //   return NextResponse.json({ error: parsed.error.flatten() }, { status: 422 })
    // }
    // const input = parsed.data
    // ---------------------------------------------------------------

    // Business logic — replace with your data access
    const result = body

    return NextResponse.json({ data: result }, { status: 201 })
  } catch (error) {
    console.error('[API] <name> POST:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

## Response format

All handlers use a consistent envelope:

```typescript
// Success
{ data: T }
{ data: T; meta: { page: number; total: number } }

// Error
{ error: string }
{ error: string; details?: unknown }
```

## Validation (optional, recommended for external input)

When a route accepts a body from untrusted callers, add a Zod schema:

```typescript
// src/lib/schemas/<name>.schema.ts
import { z } from 'zod'

export const NameSchema = z.object({
  title: z.string().min(1).max(255),
  // ...fields specific to your domain
})

export type NameInput = z.infer<typeof NameSchema>
```

Import and call `NameSchema.safeParse(body)` in the handler before business logic.

## Optional seams

These are **not included by default**. Enable them only after running the relevant opt-in guide in `plugins/forge/skill-templates/_common/manual-setup-templates/`.

| Seam | Opt-in guide | What to uncomment |
|---|---|---|
| Supabase data access | `supabase-setup.md` | `createServerClient()` import + query block |
| Auth (session check) | `supabase-auth-setup.md` | `supabase.auth.getUser()` + 401 guard |
| Sentry error capture | `sentry-setup.md` | `Sentry.captureException(error)` in catch |

## Conventions

- File path: `app/api/<name>/route.ts` (App Router convention). One file per resource.
- Use `NextRequest` / `NextResponse` — not the older `Request` / `Response` globals.
- Server-only secrets live in `process.env.VAR_NAME` — never expose them in `NEXT_PUBLIC_` vars.
- Prefer `unknown` over `any` for `body` and `error` — narrow explicitly.
- Authenticated routes must check identity inside the handler, not rely on middleware alone.

## Anti-patterns

- Putting business logic in multiple levels — keep each handler thin; extract a service function if logic exceeds ~20 lines.
- Returning a raw `Error` object in the JSON body — always map to `{ error: string }`.
- Hard-coding third-party API keys inline — read from `process.env`.
- Skipping the `try/catch` — uncaught errors produce unformatted 500 responses.
- Using `npm` — this template uses **pnpm**.

## References

- `app/api/` — route-handler file conventions (App Router docs)
- `plugins/forge/skill-templates/web-nextjs/CLAUDE.md` — stack reminders (pnpm, strict TS, App Router)
- `plugins/forge/skill-templates/_common/manual-setup-templates/` — Supabase / Sentry opt-in guides
