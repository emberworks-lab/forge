# Design Tokens Patterns Research

_Surveyed: Style Dictionary, Tokens Studio, Daisy UI, shadcn/ui_
_Date: 2026-05-21 | Refs: #72_

---

## 1. Style Dictionary (Amazon)

**Format**
JSON, JSONC, JSON5, or ESM. Supports both legacy Style Dictionary format
(`value`, `type`, `comment`) and the W3C Design Token Community Group (DTCG)
spec (`$value`, `$type`, `$description`). Tokens are organized via a
Category/Type/Item (CTI) hierarchy (e.g. `color.background.primary`), though
the hierarchy is a convention, not an enforcement.

**Source of truth**
Code-side JSON files committed to the repo. No dependency on Figma or any
design tool. Multiple token files are deep-merged at build time via glob
patterns.

**Output platforms**
CSS custom properties, SCSS variables, JavaScript/TypeScript modules, Android
XML, iOS Swift/Objective-C, JSON. Any custom format can be registered
programmatically.

**Workflow shape**
```
token JSON files → sd.build() → platform-specific outputs
```
1. Author tokens in JSON (primitives → semantic → component tiers).
2. Configure `style-dictionary.config.json` with `source` globs and platform
   targets.
3. Run `sd build` in CI; outputs land in each platform's source tree.
4. Transforms are non-destructive and composable (hex→rgb, px→rem, etc.).
5. Post-build actions can copy assets or invoke other scripts.

**Token philosophy**
Tier-based / alias model. Primitives (`color.blue.500`) are referenced by
semantic tokens (`color.background.interactive`), which components then
consume. References use `{path.to.token}` dot-notation. This separation means
rebrand = change one layer, not every component.

**AI-agent friendliness**
High. Declarative JSON input, deterministic build pipeline, well-typed config
schema. An LLM can generate or mutate token files reliably.

---

## 2. Tokens Studio (Figma plugin + platform)

**Format**
W3C DTCG-compliant JSON. Single-file (`tokens.json`) or multi-file per token
set. Ships with a Style Dictionary integration for downstream builds.

**Source of truth**
Figma is the editing surface; a Git remote (GitHub/GitLab) is the canonical
store. Two-way sync: designers push from the Figma plugin to a branch; CI
pulls and runs Style Dictionary to produce CSS/SCSS/platform outputs.

**Output platforms**
Anything Style Dictionary supports (CSS, SCSS, Android, iOS, JS). Token export
also targets Supernova, Framer, and VS Code extensions.

**Workflow shape**
```
Figma (plugin) ←→ GitHub JSON ← → Style Dictionary → platform outputs
```
1. Designer edits tokens in the Tokens Studio Figma plugin.
2. Plugin pushes `tokens.json` diff to a feature branch, optionally auto-opens
   a GitHub PR.
3. CI runs Style Dictionary transforms; outputs go to the consuming app repos.
4. Developer pulls outputs or consumes them via package.

**Token philosophy**
Figma-first. Tokens are born in the design tool; code is a consumer of the
design graph. Supports token sets, themes (light/dark), and multi-brand via
set composition.

**AI-agent friendliness**
Medium. The Figma plugin side is human-driven; however, the JSON and CI
pipeline are fully scriptable. An LLM can manipulate `tokens.json` directly
and push via the GitHub API without touching the Figma plugin.

---

## 3. Daisy UI (Tailwind plugin)

**Format**
CSS custom properties in `oklch()` color space, declared inside
`@plugin "daisyui/theme" {}` blocks. Variable names follow a flat semantic
convention: `--color-primary`, `--color-base-100`, `--radius-box`.

**Source of truth**
`app.css` (or global stylesheet). The library ships 35 built-in themes as
canonical defaults; custom themes extend them by overriding variables.

**Output platforms**
Web only (CSS + Tailwind utilities). No native mobile export. Themes activate
via `data-theme="<name>"` HTML attribute, enabling scoped, nestable theming.

**Workflow shape**
```
app.css theme definition → Tailwind build → HTML data-theme attribute
```
1. Add `@plugin "daisyui"` to Tailwind config.
2. Define themes in `app.css`; list enabled themes with `--default` /
   `--prefersdark` flags.
3. Apply `data-theme` to any element; child elements inherit it.
4. Use daisyUI component classes (`btn`, `card`, etc.) which map to token
   variables automatically.

**Token philosophy**
Theme-based (not tier-based). Tokens are flat semantic values per named theme;
there are no primitive aliases. Rebrand = swap the active theme or override
variables in the theme block. Component library is tightly coupled to the
token set.

**AI-agent friendliness**
High for web. daisyUI ships an official MCP server ("Blueprint") for LLM code
generation. Structured variable naming and simple plugin syntax are easily
parseable. Not suitable for multi-platform (mobile) output.

---

## 4. shadcn/ui (Radix + Tailwind)

**Format**
CSS custom properties in OKLCH color space under `:root` and `.dark` selectors.
Semantic naming with foreground pairs: `--primary`, `--primary-foreground`,
`--background`, `--foreground`. A single `--radius` generates a derived scale
(sm → 3xl) via calculated multipliers.

**Source of truth**
`globals.css` (or equivalent global stylesheet). Tokens are copy-pasted into
the project; there is no upstream package to update. The `shadcn/create` CLI
tool generates theme scaffolds visually.

**Output platforms**
Web only (Tailwind CSS utilities). Components auto-map tokens via
`@theme inline` declarations. No native platform output.

**Workflow shape**
```
globals.css (:root / .dark) → @theme inline → Tailwind utilities → components
```
1. Generate token scaffold via `npx shadcn add` or `shadcn/create` UI.
2. Paste `:root` / `.dark` blocks into `globals.css`.
3. Components reference Tailwind utilities (`bg-primary`, `text-foreground`).
4. Dark mode: override the same token names inside `.dark` — no separate
   theme system needed.

**Token philosophy**
Semantic-flat / theme-based. No primitive tier; tokens are direct semantic
values. Philosophy is "own your code" — tokens live in your repo, not a
library. Thin abstraction layer; very readable output.

**AI-agent friendliness**
Very high. Full default scaffold is copy-paste ready; semantic naming is
unambiguous; Tailwind utility mapping is explicit. LLMs can generate, mutate,
and extend themes without special tooling.

---

## Token Philosophy Comparison

| Dimension            | Style Dictionary       | Tokens Studio          | Daisy UI               | shadcn/ui              |
|----------------------|------------------------|------------------------|------------------------|------------------------|
| Paradigm             | Tier-based / alias     | Figma-first            | Theme-based (flat)     | Semantic-flat / owned  |
| Source of truth      | Code JSON              | Figma → Git JSON       | `app.css`              | `globals.css`          |
| Primitive tier       | Yes (required)         | Yes (in sets)          | No                     | No                     |
| Multi-platform       | Yes (CSS/iOS/Android)  | Via Style Dictionary   | Web only               | Web only               |
| Figma integration    | Manual / plugin bridge | Native (core feature)  | None                   | None                   |
| Token format         | JSON / DTCG            | DTCG JSON              | CSS variables          | CSS variables          |
| Rebrand mechanism    | Swap semantic tier     | Swap token set/theme   | Swap `data-theme`      | Edit `:root` block     |
| Learning curve       | Medium–High            | Medium (Figma users)   | Low                    | Very Low               |
| LLM generation ease  | High                   | Medium                 | High                   | Very High              |

---

## Recommended Pattern for `forge:design-bootstrap`

### Default: **shadcn/ui token model**

**Rationale:**
- `forge:design-bootstrap` targets LLM-generated code. shadcn's semantic CSS
  variable model is the easiest for an LLM to generate correctly with zero
  ambiguity — the full scaffold fits in ~30 lines, semantic names map 1:1 to
  Tailwind utilities, and the copy-paste ownership model means no package
  version drift.
- The OKLCH color space and foreground-pair convention produce accessible,
  consistent themes by construction.
- Dark mode is a first-class citizen (`:root` / `.dark`) with no extra
  infrastructure.
- Most Next.js / React / Expo Web projects that `forge:design-bootstrap` will
  target already use Tailwind, making adoption frictionless.

**When to deviate:**
- **Multi-platform (web + iOS + Android):** Layer in Style Dictionary on top.
  Use shadcn tokens as the semantic tier in `globals.css`; feed the same
  semantic values into a Style Dictionary config to produce Swift/Kotlin
  constants from the same source.
- **Large design-team / Figma-heavy workflow:** Add Tokens Studio as the
  authoring layer. The DTCG JSON it produces feeds directly into Style
  Dictionary; shadcn tokens can be generated as one of the platform outputs.
- **Rapid internal tools / admin panels with no Figma workflow:** Daisy UI is
  the fastest path — a single `@plugin` line and a theme block produce a
  complete, accessible UI in minutes. Recommend as an explicit opt-in flag
  (`--preset daisy`) rather than the default.

**Summary recommendation:**
> Default to the **shadcn/ui CSS variable model**. Add Style Dictionary as an
> opt-in layer when multi-platform output is required. Offer Daisy UI as a
> preset for utility-first projects. Tokens Studio is not a default concern —
> it activates only when a team has an existing Figma-to-code pipeline.
