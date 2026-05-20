# skill-templates routing

Map `(project_type, framework)` from the stack interview to a folder under `~/.claude/skill-templates/<stack>/`. The folder name is the **stack key** referenced throughout the rest of this skill.

## Routing table

| project_type | framework | Stack key | Folder |
|---|---|---|---|
| Web | React | `web-react` | `~/.claude/skill-templates/web-react/` |
| Web | Next.js | `web-nextjs` | `~/.claude/skill-templates/web-nextjs/` |
| Web | Vue | `web-vue` | `~/.claude/skill-templates/web-vue/` |
| Web | Svelte / SvelteKit | `web-svelte` | `~/.claude/skill-templates/web-svelte/` |
| Web | Astro | `web-astro` | `~/.claude/skill-templates/web-astro/` |
| Web | Solid | `web-solid` | `~/.claude/skill-templates/web-solid/` |
| Mobile | Flutter (any flavour) | `mobile-flutter` | `~/.claude/skill-templates/mobile-flutter/` |
| Mobile | iOS Swift | `mobile-ios` | `~/.claude/skill-templates/mobile-ios/` |
| Mobile | Android Kotlin | `mobile-android` | `~/.claude/skill-templates/mobile-android/` |
| Mobile | Compose Multiplatform | `mobile-cmp` | `~/.claude/skill-templates/mobile-cmp/` |
| Mobile | React Native | `mobile-rn` | `~/.claude/skill-templates/mobile-rn/` |
| Backend | Node + Hono | `backend-node` | `~/.claude/skill-templates/backend-node/` |
| Backend | Node + Nest | `backend-node-nest` | `~/.claude/skill-templates/backend-node-nest/` |
| Backend | Go | `backend-go` | `~/.claude/skill-templates/backend-go/` |
| Backend | Python (FastAPI / Django) | `backend-python` | `~/.claude/skill-templates/backend-python/` |
| Backend | Rust | `backend-rust` | `~/.claude/skill-templates/backend-rust/` |
| Backend | Elixir | `backend-elixir` | `~/.claude/skill-templates/backend-elixir/` |
| Backend | Java | `backend-java` | `~/.claude/skill-templates/backend-java/` |
| Backend | Ruby | `backend-ruby` | `~/.claude/skill-templates/backend-ruby/` |
| Library | npm | `library-npm` | `~/.claude/skill-templates/library-npm/` |
| Library | pub | `library-pub` | `~/.claude/skill-templates/library-pub/` |
| Library | pip | `library-pip` | `~/.claude/skill-templates/library-pip/` |
| Library | crates | `library-crates` | `~/.claude/skill-templates/library-crates/` |

## "Does the folder exist?" check

A folder counts as **existing** when:

- It has at least one `kit-*.md` file with real content (not just a placeholder README).

Otherwise treat it as missing and run the step 4B interview-scaffold flow.

## Shared assets

Stack-agnostic assets live under `~/.claude/skill-templates/_common/`:

- `_common/docs/00_meta/{decisions-log,roadmap,docs-workflow,glossary}.md` — used by step 6.
- `_common/manual-setup-templates/{supabase,firebase,sentry,github-auth,linear-keys}.md` — used by `references/linear-automation.md` step 7.5.3.
