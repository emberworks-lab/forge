# Stack interview — common batch

Ask the user this seven-question batch. Batch all picks via `AskUserQuestion`; use free text only for names / IDs.

## 1. Project type (single-select)

- Web frontend (React / Vue / Svelte / Astro / Next / Nuxt / Solid / etc.)
- Mobile — Flutter
- Mobile — native (iOS Swift / Android Kotlin / Compose Multiplatform / React Native)
- Backend (Node / Go / Python / Rust / Elixir / Java / Ruby)
- Library / package (npm / pub / pip / crates)
- Other (specify)

## 2. Specific framework / runtime (depends on type)

- **Web** — which framework + bundler.
- **Mobile-Flutter** — pure Flutter or Flame-based.
- **Mobile-native** — which platform(s).
- **Backend** — which language + framework.
- **Library** — target ecosystem.

## 3. Persistence

- Database: Postgres / MySQL / SQLite / Mongo / Redis / None.
- ORM / driver: relevant set per DB.
- Cloud: Supabase / Firebase / AWS / Cloudflare / Self-hosted / None.

## 4. Cloud / hosting

Vercel / Cloudflare Workers / Cloudflare Pages / AWS / Fly / Render / Railway / Netlify / Self-hosted / None.

## 5. Linear team

Team name (e.g. `Emberworks`). The prefix (`team.key`) is derived automatically from the selected team via Linear MCP — no separate prefix question.

## 6. Design system / Figma (optional)

- Figma file URL if any.
- Design tokens managed where.

## 7. Existing scaffolding

- Newly created (empty repo) or already has code?
- If has code, scan `package.json` / `pubspec.yaml` / `go.mod` / `Cargo.toml` to corroborate the user's framework answer.

## Per-stack deepening

After the common batch, for the chosen stack open the per-stack interview:

- `stack-interviews/mobile-flutter.md`
- `stack-interviews/web.md`
- `stack-interviews/backend-node.md`
- `stack-interviews/mobile-native.md`
- `stack-interviews/library.md`
