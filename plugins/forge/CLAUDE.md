# forge plugin — policy

Plugin-level policy that all `forge:*` skills follow. The headline rules are summarized here for quick reference; the authoritative full content lives in `forge:writing-skill` and its references.

When writing or refactoring a skill in this plugin, invoke `forge:writing-skill` and run `bash plugins/forge/skills/writing-skill/scripts/audit.sh <path/to/SKILL.md>` before opening a PR. Exit 0 = ready.

## Composition principle

Skills follow code composition rules: single responsibility, master composes via explicit invocation (no inlining), low coupling, extract when reused (not before).

> Full details: [`skills/writing-skill/references/composition-principle.md`](skills/writing-skill/references/composition-principle.md).

## Type taxonomy

Every SKILL.md front-matter declares `type: minimal | fundamental | hybrid`:

- **minimal** — ≤ 80 lines, flexible one-shot, no decision tree, no `references/`
- **fundamental** — ≤ 300 lines + `references/`, rigid foundational workflow cited by other skills
- **hybrid** — ≤ 120 lines + supporting files (default)

> Full details: [`skills/writing-skill/references/type-taxonomy.md`](skills/writing-skill/references/type-taxonomy.md).

## Subagent model declaration

Skills that spawn subagents MUST name the model inline: `sonnet` (mechanical) or `opus` (creative/critical). The `haiku` model is not used in this plugin.

> Full details: [`skills/writing-skill/references/subagent-model-declaration.md`](skills/writing-skill/references/subagent-model-declaration.md).

## Credit attribution

Adapted skills carry an `inspired-by` front-matter block with `author`, `repo`, `skill`, and `relation` (one of `adapted | concept | structure`). No 1:1 copies — every adapted skill is rewritten in this plugin's voice.

> Full details: [`skills/writing-skill/references/credit-attribution.md`](skills/writing-skill/references/credit-attribution.md).

## Audit before PR

The slim audit checklist mechanizes structural checks (front-matter, line caps, dangling references, forbidden patterns) via `audit.sh`:

> Checklist: [`skills/writing-skill/references/slim-audit-checklist.md`](skills/writing-skill/references/slim-audit-checklist.md)
> Script: [`skills/writing-skill/scripts/audit.sh`](skills/writing-skill/scripts/audit.sh)
