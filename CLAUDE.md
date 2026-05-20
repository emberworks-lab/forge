# forge plugin — policy

Plugin-level policy that all `forge:*` skills follow. **Bootstrap phase** — content lands progressively across EPIC A sub-issues. Authoritative rules are encoded in `forge:writing-skill` (sub-issue #16); this file mirrors the headline rules for quick reference.

## Composition principle

Skills follow code composition rules: single responsibility, master composes via explicit invocation (no inlining), low coupling, extract when reused (not before).

> Full details: `forge:writing-skill` → `references/composition-principle.md` (lands in #16).

## Type taxonomy

Every SKILL.md front-matter declares `type: minimal | fundamental | hybrid`:

- **minimal** — 30-80 lines, flexible one-shot, no decision tree
- **fundamental** — 200+ lines + `references/`, rigid foundational workflow
- **hybrid** — 50-120 lines + supporting files (default)

> Full details: `forge:writing-skill` → `references/type-taxonomy.md` (lands in #16).

## Subagent model declaration

Skills that spawn subagents MUST name the model inline: `sonnet` (mechanical) or `opus` (creative/critical). `haiku` is not used in this plugin.

> Full details: `forge:writing-skill` → `references/subagent-model-declaration.md` (lands in #16).

## Credit attribution

Adapted skills carry `inspired-by` front-matter with `author`/`repo`/`skill`/`relation: adapted | concept | structure`. No 1:1 copies.

> Full details: `forge:writing-skill` → `references/credit-attribution.md` (lands in #16).
