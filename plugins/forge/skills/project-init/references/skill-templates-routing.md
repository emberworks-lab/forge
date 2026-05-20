# skill-templates routing

Map `(project_type, framework)` from the stack interview to a folder under `plugins/forge/skill-templates/<stack>/`. The folder name is the **stack key** referenced throughout the rest of this skill.

## Routing table

| project_type | framework | Stack key | Folder |
|---|---|---|---|
| Web | React | `web-react` | `plugins/forge/skill-templates/web-react/` |
| Web | Next.js | `web-nextjs` | `plugins/forge/skill-templates/web-nextjs/` |
| Web | Vue | `web-vue` | `plugins/forge/skill-templates/web-vue/` |
| Web | Svelte / SvelteKit | `web-svelte` | `plugins/forge/skill-templates/web-svelte/` |
| Web | Astro | `web-astro` | `plugins/forge/skill-templates/web-astro/` |
| Web | Solid | `web-solid` | `plugins/forge/skill-templates/web-solid/` |
| Mobile | Flutter (any flavour) | `mobile-flutter` | `plugins/forge/skill-templates/mobile-flutter/` |
| Mobile | iOS Swift | `mobile-ios` | `plugins/forge/skill-templates/mobile-ios/` |
| Mobile | Android Kotlin | `mobile-android` | `plugins/forge/skill-templates/mobile-android/` |
| Mobile | Compose Multiplatform | `mobile-cmp` | `plugins/forge/skill-templates/mobile-cmp/` |
| Mobile | React Native | `mobile-rn` | `plugins/forge/skill-templates/mobile-rn/` |
| Backend | Node + Hono | `backend-node` | `plugins/forge/skill-templates/backend-node/` |
| Backend | Node + Nest | `backend-node-nest` | `plugins/forge/skill-templates/backend-node-nest/` |
| Backend | Go | `backend-go` | `plugins/forge/skill-templates/backend-go/` |
| Backend | Python (FastAPI / Django) | `backend-python` | `plugins/forge/skill-templates/backend-python/` |
| Backend | Rust | `backend-rust` | `plugins/forge/skill-templates/backend-rust/` |
| Backend | Elixir | `backend-elixir` | `plugins/forge/skill-templates/backend-elixir/` |
| Backend | Java | `backend-java` | `plugins/forge/skill-templates/backend-java/` |
| Backend | Ruby | `backend-ruby` | `plugins/forge/skill-templates/backend-ruby/` |
| Library | npm | `library-npm` | `plugins/forge/skill-templates/library-npm/` |
| Library | pub | `library-pub` | `plugins/forge/skill-templates/library-pub/` |
| Library | pip | `library-pip` | `plugins/forge/skill-templates/library-pip/` |
| Library | crates | `library-crates` | `plugins/forge/skill-templates/library-crates/` |

## "Does the folder exist?" check

A folder counts as **existing** when:

- It has at least one `kit-*.md` file with real content (not just a placeholder README).

Otherwise treat it as missing and run the step 4B interview-scaffold flow.

## Shared assets

Stack-agnostic assets live under `plugins/forge/skill-templates/_common/`:

- `_common/docs/00_meta/{decisions-log,roadmap,docs-workflow,glossary}.md` — used by step 6.
- `_common/manual-setup-templates/{supabase,firebase,sentry,github-auth,linear-keys}.md` — used by `references/linear-automation.md` step 7.5.3.
