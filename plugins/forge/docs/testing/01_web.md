# Testing — web

Augments `00_general.md` for web frontend stacks (React / Vue / Svelte / SolidJS / Astro / Next / Nuxt / SvelteKit).

## Stack mapping

| Layer | Tooling (recommended) | Alternative |
|---|---|---|
| Unit + component | **Vitest** | Jest (only if monorepo already on Jest) |
| Component (React) | **React Testing Library** + Vitest | Enzyme is dead, don't pick it |
| Component (Vue) | **Vue Test Utils** + Vitest | — |
| Component (Svelte) | **@testing-library/svelte** + Vitest | — |
| API mocking | **MSW (Mock Service Worker)** | nock (Node-only) |
| E2E | **Playwright** | Cypress (only if team experience demands) |
| Visual regression | **Chromatic** (with Storybook) | Percy, Loki |
| Property-based | **fast-check** | — |
| Performance | Lighthouse CI; web-vitals | — |

Default for new projects: Vitest + RTL + MSW + Playwright + fast-check (when applicable).

## Layer guidance

### Unit (`*.test.ts` next to source OR `__tests__/`)

- Pure functions: hash, format, parse, derive, compute
- Custom React/Vue hooks via `@testing-library/react-hooks` or `renderHook`
- Server-side utilities (Node), reducers, state machines

Use `vi.fn()` for spies. Use real implementations whenever possible.

### Component

- One file per component
- Render via `render()` helper from RTL/Vue Test Utils
- Query by accessible role first (`getByRole('button', { name: /submit/i })`), then text, then label, then test-id
- Interact via `userEvent` (not `fireEvent` — userEvent simulates real input timing)
- Assertions: `toBeInTheDocument`, `toHaveAttribute`, etc. (jest-dom or chai equivalents)

```ts
test('submits form when valid', async () => {
  const onSubmit = vi.fn();
  const user = userEvent.setup();
  render(<LoginForm onSubmit={onSubmit} />);
  
  await user.type(screen.getByLabelText(/email/i), 'a@b.com');
  await user.type(screen.getByLabelText(/password/i), 'secret');
  await user.click(screen.getByRole('button', { name: /sign in/i }));
  
  expect(onSubmit).toHaveBeenCalledWith({ email: 'a@b.com', password: 'secret' });
});
```

### Integration

- Test multiple modules together with mocked I/O at the network boundary (MSW)
- Cover: form submit → API call → state update → UI reflects new state
- Mock at HTTP level, not at module-import level — closer to reality, less brittle

### E2E (Playwright)

- Run on real browsers (Chromium baseline, Firefox + WebKit if multi-browser matters)
- One spec per critical user journey: signup, checkout, primary feature flow
- Use `page.locator(role)` queries; avoid CSS selectors
- Use `expect(...).toHaveScreenshot()` for visual regression on critical surfaces
- Run against a deployed preview, not localhost — CI starts the dev server, then Playwright

## Test command outputs (for test-runner parsing)

- **Vitest**: structured TAP-like output; `--reporter=verbose` for detail; `--reporter=json` for machine parsing
- **Playwright**: HTML report on failure; `--reporter=list,github` good for CI logs
- **Jest**: similar to Vitest but slower; if forced to use, prefer `--silent` + `--ci`

## What "manual test cases" look like for web

```markdown
## Manual test cases (TICKET-12)

- Run `npm run dev`; open http://localhost:3000/dashboard
- Click "New project" → modal opens; cancel → modal closes
- Submit project name "Test"; see new card appear, no full-page reload
- Refresh the page; the card persists (verify Postgres write)
- Open DevTools → Network tab; create another project; expect ONE POST /api/projects, no duplicates
```

## Common pitfalls

- **Snapshot tests of full pages** — they break on every minor change. Use Chromatic on Storybook instead.
- **Testing implementation details** (component state, internal hooks) — refactor-fragile. Test through the public API.
- **Forgetting `await user.click()`** — userEvent is async; non-awaited clicks cause race-y assertions.
- **Mocking `fetch` at module level** — use MSW; it's stack-agnostic and survives bundler changes.
- **Running E2E on localhost in CI** without proper teardown — leaks ports, breaks parallel runs.

## Coverage commands

- Vitest: `vitest --coverage` (uses v8 by default; istanbul also supported)
- Playwright: not coverage-based; use trace artifacts for failure analysis instead

## Visual regression

For design-system components only. Set up Storybook + Chromatic; CI publishes a Chromatic build per PR; review visual diffs in Chromatic dashboard before approving.

For app-level pages, prefer manual test cases (see `00_general.md`) over visual regression — pages change too often.
