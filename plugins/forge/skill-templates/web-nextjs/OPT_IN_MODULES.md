# Opt-in modules — web-nextjs template

These modules are **not** included in the core template. Follow the linked guide to add each one.

| Module | Guide | Runtime skill |
|---|---|---|
| End-to-end testing (Playwright) | `_common/manual-setup-templates/playwright.md` | `forge:e2e-web` |
| Error monitoring | `_common/manual-setup-templates/sentry.md` | — |
| Database / auth | `_common/manual-setup-templates/supabase.md` | — |
| Auth providers | `_common/manual-setup-templates/github-auth.md` | — |

## How to opt in

1. Read the guide for your chosen module.
2. Run the install commands it specifies.
3. Copy the relevant `.template` files from this directory (if any) to their final locations.
4. Activate the corresponding `forge:*` skill by creating the marker file described in the guide.

## Playwright quick-start

The Playwright module ships sample config and a first-test template in this directory:

- `playwright.config.ts.template` — copy to `playwright.config.ts` at the project root.
- `tests/e2e/example.e2e-web.spec.ts.template` — copy to `tests/e2e/example.e2e-web.spec.ts`.

Full setup instructions: `plugins/forge/skill-templates/_common/manual-setup-templates/playwright.md`.
Runtime invocation: `forge:e2e-web` (`plugins/forge/skills/e2e-web/SKILL.md`, lands with issue #80).
