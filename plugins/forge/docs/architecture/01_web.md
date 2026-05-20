# Architecture — Web Frontend

Principles for web frontend applications (React, Vue, Angular, and similar SPA frameworks).
General principles are in `00_general.md`; this file covers web-specific concerns.

---

## Layering

```
UI Components
    ↓  events / callbacks
State / Hooks layer (ViewModels, stores, composables)
    ↓  async calls
Data / Query layer (API clients, caches, adapters)
    ↓
Network / Storage
```

Components should know nothing about fetch mechanics. The data layer should know nothing
about rendering. Hooks/composables are the seam between the two.

---

## State Management

Choose the smallest tool that solves the problem. Escalate only when you hit its limits.

**Local component state** (`useState` / `ref`). For UI-only state that does not leave the
component: form field focus, toggle visibility, accordion open/closed. Default choice.

**Lifted state.** When two siblings share state, lift to their nearest common ancestor.
Avoid lifting past the point of actual sharing.

**Context + `useReducer`.** For low-frequency global state (auth user, theme, locale).
Not optimised for high-frequency updates — context re-renders all consumers.

**Zustand.** Lightweight, subscription-based, outside the React tree. Good for
cross-cutting state (UI layout, notifications) that does not need React context.
Simpler API than Redux; add it when lifting/context becomes unwieldy.

**Redux Toolkit.** Structured, predictable global state with strict unidirectional flow.
Best for large apps with complex shared state, extensive devtools, or normalised entity
caches. The boilerplate cost is real — only justified at scale.

**Jotai / Recoil.** Atomic state: compose small atoms, derive others from them.
Good when you have many independent pieces of UI state that occasionally intersect.
Fine-grained subscriptions avoid unnecessary re-renders.

**Rule of thumb:** most apps never need Redux. Start local → lift → context/Zustand → Redux.

---

## Data Fetching Layer

**TanStack Query (React Query).** First choice for server-state management. Handles
caching, background refetch, stale-while-revalidate, optimistic updates, pagination,
and request deduplication. Separates server state from UI state clearly.

**SWR.** Simpler alternative to TanStack Query. Good default for smaller apps.
Less feature-rich for complex invalidation or mutation workflows.

**RTK Query.** Use when already using Redux Toolkit. Co-locates API definitions with
the Redux store; auto-generates hooks. Avoids adding a second caching layer.

**Native `fetch` / `axios`.** Only for simple, fire-and-forget calls with no caching
requirements. Wrapping in a data-layer module (not calling from components directly) is
mandatory regardless.

**Rule:** server state (remote data) belongs in a query layer, not in component-local
`useState`. Never store API responses in Redux unless you have a specific normalisation need.

---

## Routing

**SPA routing (React Router / TanStack Router / Vue Router).** Client-side navigation.
All routes render on the client; the server returns a single HTML shell.
Simple DX, no server required, but initial bundle size and SEO need attention.

**File-based routing (Next.js App Router / Nuxt / Remix).** Routes defined by
file-system structure. Reduces routing boilerplate; enables per-route code splitting
automatically. Standard choice for new React/Vue projects today.

**Server-Side Rendering (SSR).** HTML is rendered on the server per request.
Best for SEO-critical content, auth-gated pages with personalised content, or
performance on slow devices. Adds server infrastructure and hydration complexity.

**Static Generation (SSG).** Pages rendered at build time. Best for content that
changes infrequently. Zero runtime server cost; CDN-friendly.

**Pattern:** pass IDs, not objects, through route params. Reconstruct data from the
query layer on the destination page. Avoids serialisation edge cases and stale state.

---

## Component Composition

**Container / Presentational split.** Containers handle data fetching and state;
presentational components receive props and emit events. Keeps components testable in
isolation. Modern hooks partially collapse this — apply the principle, not the rigid split.

**Hooks-first.** Extract stateful logic into custom hooks. A hook can be unit-tested
without rendering. Components become thin wrappers that connect hooks to JSX.

**Compound components / Slots.** For complex reusable UI (tabs, modals, selects),
expose subcomponents that share implicit context. Gives callers layout control without
prop-drilling. Prefer explicit context passing over implicit global context.

**Render props.** Useful when a component needs to delegate rendering to its caller.
Largely replaced by hooks for logic sharing; still valid for flexible render delegation.

---

## Code Splitting and Lazy Loading

Split at route boundaries by default. Each route loads only its own bundle.
Use `React.lazy` / dynamic `import()` for heavy below-the-fold components
(rich text editors, chart libraries, data tables).

Avoid splitting below the route level prematurely — bundle analysis before splitting.
Prefetch critical routes on hover or on idle to eliminate perceived latency.

---

## Error Boundaries and Suspense

**Error boundaries.** Wrap subtrees that may fail with error boundaries so a single
component crash does not unmount the entire app. Provide useful fallback UI.
Log caught errors to an error tracker at the boundary.

**Suspense.** Suspend component trees during async operations (lazy loading, data fetching
with Suspense-enabled libraries). Place `<Suspense>` boundaries at meaningful UX points,
not wrapping every leaf component.

---

## SSR vs SPA Trade-offs

| Concern | SPA | SSR |
|---|---|---|
| Initial load performance | Slower TTFB on slow connections | Faster first meaningful paint |
| SEO | Requires extra work | Natural |
| Infrastructure | Static files / CDN | Server runtime required |
| Auth integration | Simple; entirely client-side | Requires server session handling |
| Hydration complexity | None | Can mismatch; needs care |

Default to SSR/file-based routing for new projects unless the app is auth-gated and SEO
is irrelevant (then a pure SPA is simpler).

---

## Accessibility as Architecture

Accessibility is not a post-hoc feature — it is a structural concern.

- Use semantic HTML elements (`<button>`, `<nav>`, `<main>`, `<header>`) rather than
  `<div onClick>`. Screen readers and keyboard users depend on semantics.
- Manage focus explicitly after route transitions and modal opens/closes.
- ARIA attributes (`aria-label`, `aria-live`, `role`) supplement, not replace, semantics.
- Colour contrast and font sizing are design system concerns; enforce them via tokens,
  not inline values.

---

## Problem Signals

- Components call `fetch` or `axios` directly — missing data layer.
- Server state stored in Redux next to UI state — conflating two different state types.
- Props drilled more than two levels — candidate for context or composition redesign.
- A single React component over 300 lines — needs decomposition.
- Business logic (calculations, validation rules) inside JSX render functions.
- `useEffect` with complex dependency arrays used for data fetching — use a query library.
- No error boundaries — a single component failure crashes the whole screen.
- All routes in one bundle — missing code splitting.
- Inline styles or raw pixel values instead of design tokens — theme drift.
- State initialised from a prop and then managed locally — stale-prop anti-pattern.
