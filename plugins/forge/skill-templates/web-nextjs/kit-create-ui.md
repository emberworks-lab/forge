---
name: kit-create-ui
description: "Use when building a new UI page, feature component, or shared UI primitive in a Next.js App Router project. Covers component structure, Tailwind 4 conventions, the Widget Registry Rule, loading/empty states, and responsive layout patterns."
---

# kit-create-ui

## When to use

- Triggers: "add a UI component", "create a page", "build a feature screen", `/kit-create-ui`.
- The work adds or updates files under `app/` (pages/layouts) or `src/components/` (shared components).

Don't use for: API route handlers (`/kit-create-api`), Server Actions, or pure data-fetching utilities in `src/lib/`.

## What it produces

- `app/<route>/page.tsx` — a Server Component page (default)
- `src/components/features/<name>.tsx` — a feature-specific component
- `src/components/ui/<name>.tsx` — a shared UI primitive (if broadly reusable)

## Required inputs

- Component or page name (PascalCase, e.g. `ResourceCard`, `DashboardPage`)
- Whether it is a page, feature component, or shared UI primitive
- Data it displays (shape of the props or async fetch)
- Interactive behavior (if any — determines whether `"use client"` is needed)

## MANDATORY first step — Widget Registry Rule

Before writing any new component:

1. **CHECK** the project's component registry (see "Component registry" section below). Does a similar component already exist?
2. **REUSE** if found — import and compose; do not recreate.
3. **EVALUATE** reusability of the new component:
   - Used in 2+ places? → `src/components/ui/`
   - Feature-specific but non-trivial? → `src/components/features/`
   - One-off, simple? → inline in the page
4. **REGISTER** after adding to `src/components/ui/`: append the new component to the "Component registry" section in this file so future tasks know it exists.
5. **EXTRACT** when you notice duplication: if you copy-paste a UI pattern more than once, make it a component.

Never skip steps 1 and 4 — the registry is the shared memory for AI agents working on this project.

## Component template (example — replace with your domain)

The examples below use placeholder names (`ResourceCard`, `StatusBadge`, `FilterBar`). Replace them with the actual names for your project's domain.

```typescript
// src/components/features/resource-card.tsx  ← example: replace with your component
import { type FC } from 'react'

interface ResourceCardProps {
  title: string
  description?: string
  status?: string
  href?: string
}

// "use client"  ← uncomment only if this component needs event handlers or hooks

export const ResourceCard: FC<ResourceCardProps> = ({
  title,
  description,
  status,
  href,
}) => {
  return (
    <article className="rounded-lg border border-(--color-border) bg-(--color-surface) p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-base font-semibold text-(--color-text-primary)">{title}</h3>
        {status && <StatusBadge status={status} />}
      </div>
      {description && (
        <p className="text-sm text-(--color-text-secondary) mb-2">{description}</p>
      )}
      {href && (
        <a href={href} className="text-sm text-(--color-accent) hover:underline">
          View →
        </a>
      )}
    </article>
  )
}
```

```typescript
// src/components/ui/status-badge.tsx  ← example shared primitive
import { type FC } from 'react'

interface StatusBadgeProps {
  status: string
  // Add variant logic matching your project's status taxonomy
}

export const StatusBadge: FC<StatusBadgeProps> = ({ status }) => {
  return (
    <span className="rounded-full px-2 py-0.5 text-xs font-medium bg-(--color-badge-bg) text-(--color-badge-text)">
      {status}
    </span>
  )
}
```

```typescript
// src/components/features/filter-bar.tsx  ← example filter primitive
import { type FC } from 'react'

interface FilterBarProps {
  options: string[]
  selected: string
  onChange: (value: string) => void
}

// "use client" — this component needs event handlers
export const FilterBar: FC<FilterBarProps> = ({ options, selected, onChange }) => {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={`rounded-full px-3 py-1 text-sm transition-colors ${
            selected === opt
              ? 'bg-(--color-primary) text-white'
              : 'bg-(--color-surface) border border-(--color-border) text-(--color-text-secondary) hover:border-(--color-border-hover)'
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  )
}
```

## Page layout template

```typescript
// app/<route>/page.tsx — Server Component by default
export default async function ExamplePage() {
  // Fetch data here (Server Component — no useEffect needed)
  const items: Item[] = [] // replace with your data fetch

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-bold text-(--color-text-primary) mb-6">
        Page title
      </h1>

      {/* Filter — extract to FilterBar if interactive */}

      {items.length === 0 ? (
        <p className="text-center py-8 text-(--color-text-muted)">No items yet.</p>
      ) : (
        <div className="mt-6 flex flex-col gap-4">
          {items.map((item) => (
            <ResourceCard key={item.id} title={item.title} />
          ))}
        </div>
      )}
    </main>
  )
}
```

## Tailwind 4 — CSS-variable theming

This template uses **Tailwind 4** with CSS-variable-based theming. Color and spacing tokens are defined in `app/globals.css` and referenced via `(--token-name)` in class strings.

```css
/* app/globals.css — define your project's theme tokens here */
:root {
  --color-primary: oklch(55% 0.22 265);   /* override per project */
  --color-surface: oklch(99% 0 0);
  --color-border: oklch(90% 0 0);
  --color-text-primary: oklch(20% 0 0);
  --color-text-secondary: oklch(45% 0 0);
  --color-text-muted: oklch(65% 0 0);
  --color-accent: oklch(55% 0.22 265);
  /* add badge, status, and other semantic tokens as your domain requires */
}
```

Usage in components:

```typescript
// CSS-variable token in Tailwind 4 class
className="text-(--color-text-primary) bg-(--color-surface)"
```

**Defaults are placeholders — override per project.** Do not hard-code specific color values (e.g. `indigo-600`, `gray-200`) in new components; use semantic tokens instead so theming stays centralized.

## Loading and empty states

Every component or page that fetches data must handle all three states:

```typescript
// Loading skeleton (prefer Suspense + skeleton over client-side loading flags)
// In a Server Component, wrap in <Suspense fallback={<LoadingSkeleton />}>

// Error state
if (error) {
  return <p className="text-center py-8 text-red-600">Something went wrong.</p>
}

// Empty state
if (!items.length) {
  return <p className="text-center py-8 text-(--color-text-muted)">No items yet.</p>
}
```

## Server vs Client Components

| Needs | Use |
|---|---|
| Data fetch, no interactivity | Server Component (default — no directive) |
| Event handlers, `useState`, `useEffect` | `"use client"` at top of file |
| Third-party lib that uses browser APIs | `"use client"` wrapper component |

Minimize `"use client"` scope — push it as deep as possible (leaf components, not pages).

## Component registry

Track your project's component inventory here. Update this list whenever you add a component to `src/components/ui/`.

```
// src/components/ui/ — shared primitives (add yours here)
// Button       — primary / secondary / ghost / danger variants
// Card         — surface container with border and padding
// Badge        — small colored label
// Input        — text input with label and error state
```

After adding a new `ui/` component, append it to the list above so future agents know it exists without scanning the filesystem.

## Conventions

- File names: `kebab-case.tsx`. Component names: `PascalCase`.
- Server Components are the default — no directive needed.
- Client Components add `"use client"` as the first line.
- Shared components go in `src/components/ui/`; feature-scoped in `src/components/features/`.
- Import paths use `@/` alias (`@/components/ui/button`).
- Package manager: **pnpm**.

## Anti-patterns

- Creating a new component without checking the registry first — always check step 1 of the Widget Registry Rule.
- Adding `"use client"` to a page or layout — push it to the smallest leaf that needs it.
- Hard-coding color values (`text-gray-900`, `bg-indigo-600`) instead of CSS-variable tokens — breaks theming.
- Importing project-specific config modules (e.g. `@/config/categories`) in a template — use prop-driven APIs.
- Forgetting to update the component registry after adding to `src/components/ui/`.

## References

- `plugins/forge/skill-templates/web-nextjs/CLAUDE.md` — stack reminders (pnpm, strict TS, Tailwind 4, App Router)
- `src/components/ui/` — shared component inventory (check before creating)
- `app/globals.css` — CSS-variable theme tokens
- `plugins/forge/skill-templates/_common/manual-setup-templates/` — Supabase / auth / Sentry opt-in guides
