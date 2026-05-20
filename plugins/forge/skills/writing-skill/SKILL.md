---
name: writing-skill
description: Author or refactor a forge plugin skill so it conforms to plugin-wide policy. Use when creating a new SKILL.md, splitting an oversized skill, migrating a legacy command into the plugin, or verifying a skill before opening a PR.
type: fundamental
---

# Writing skills for the forge plugin

This skill is the canonical guide for authoring every other skill in the plugin. It encodes five enforced rule-sets — composition, type taxonomy, credit attribution, subagent model declaration, and the slim audit checklist — and ships a bash audit script that mechanizes the structural checks.

Treat the rules below as policy. The `forge/CLAUDE.md` plugin-level file mirrors the headline rules; this skill carries the full content and is the authoritative source if the two ever drift.

## Contract

Given a skill to author or refactor, produce a SKILL.md that:

1. Declares one of the three valid types in front-matter and stays within that type's line cap.
2. Has a single, declarable responsibility (one-sentence `description`).
3. Composes by invocation, not inlining, when it needs another skill's behavior.
4. Names subagent models explicitly when spawning them; never mentions `haiku`.
5. Carries `inspired-by` front-matter if adapted from external work, with `author`, `repo`, `skill`, `relation` (`adapted | concept | structure`).
6. Passes `scripts/audit.sh` cleanly (exit 0).

## When to invoke

- Creating a new `forge:<skill>` from scratch.
- Migrating an existing `~/.claude/commands/<name>.md` into the plugin.
- Splitting a SKILL.md that has grown past its type's line cap.
- Verifying a skill before commit (run the audit; iterate until clean).

## The five rule-sets

Headline summaries below. For full details, follow the linked references.

### 1. Composition principle

Skills follow code composition rules: single responsibility, master composes via explicit invocation (never by inlining sub-skill content), low coupling, extract when reused (not before). A master skill that reads the body of another skill's file instead of invoking the skill via the Skill tool is broken.

Full details: `references/composition-principle.md`.

### 2. Type taxonomy

Every SKILL.md declares `type: minimal | fundamental | hybrid` in front-matter:

| Type | SKILL.md cap | When |
|---|---|---|
| `minimal` | ≤ 80 lines | One-shot, flexible, no decision tree, no `references/`. |
| `hybrid` | ≤ 120 lines | Default. Core + decision tree in SKILL.md, edge cases in `references/`. |
| `fundamental` | ≤ 300 lines | Foundational. Cited as authoritative by other skills. |

Decision order: if other skills will cite this one as authoritative → `fundamental`; if the whole instruction is a paragraph plus a few bullets → `minimal`; otherwise → `hybrid`.

Full details: `references/type-taxonomy.md`.

### 3. Credit attribution

If a skill is adapted from external work (obra/superpowers, mattpocock/skills, any third-party source), the front-matter MUST include:

```yaml
inspired-by:
  - author: <handle-or-org>
    repo: <url>
    skill: <source-skill-name>
    relation: adapted | concept | structure
```

`adapted` = derived, structure preserved; `concept` = borrowed one idea; `structure` = copied scaffolding only. No 1:1 copies — every adapted skill is rewritten in this plugin's voice. Original skills omit the block entirely.

Full details: `references/credit-attribution.md`.

### 4. Subagent model declaration

Any SKILL.md that spawns a subagent MUST name the model inline:

- `sonnet` — mechanical (parsing, formatting, applying patterns, lint-style checks).
- `opus` — creative / critical / nuanced (severity classification, architecture review, security analysis, ambiguous trade-off rulings).

Only `sonnet` and `opus` are used in this plugin. The reference file enumerates the model that is forbidden and explains why.

Example phrasing: "Step 4: spawn **Opus** classifier-agent to split findings into in-place vs sub-epic groups."

Composition via the Skill tool (one skill invoking another) is NOT subagent spawning and does not require a model declaration.

Full details: `references/subagent-model-declaration.md`.

### 5. Slim audit checklist

Nine steps to walk when authoring or refactoring:

1. Core contract test — one-sentence promise, no "and".
2. Decision tree extraction — branches in SKILL.md, rationale in `references/`.
3. Anti-pattern lists ≥ 5 items → extract to a dedicated reference file.
4. Code blocks > 10 lines → `scripts/<name>.{sh,py}`.
5. Sample input/output blocks > 5 lines → `examples/`.
6. Convention-doc duplicates → delete, replace with reference link.
7. Line-count target met for declared type.
8. Subagent declarations present where required.
9. Credit attribution present where required.

Steps 7-9 plus front-matter shape, dangling `references/` links, `superpowers:*` references, and empty sections are mechanized by `scripts/audit.sh`.

Full details: `references/slim-audit-checklist.md`.

## Decision tree — which type should this skill be?

```
Will another skill cite this one as authoritative for some behavior?
├── Yes  → type: fundamental   (cap 300; needs references/)
└── No
    ├── Is the whole instruction one paragraph + 2-3 bullets, no branching?
    │   └── Yes → type: minimal   (cap 80; no references/)
    └── Otherwise   → type: hybrid   (cap 120; references/ as needed)
```

When unsure, choose `hybrid`. Promoting `minimal → hybrid` or demoting `fundamental → hybrid` later is a small refactor.

## Authoring checklist

Walk in order; do not skip:

1. Draft a one-sentence `description`. Reject "and" between two distinct verbs.
2. Choose a `type` via the decision tree above.
3. Write the body. Lift long content (rationale, anti-patterns, samples) into `references/`, `scripts/`, `examples/`.
4. If adapted from external work, add `inspired-by` front-matter with all four required fields.
5. If the skill spawns subagents, name the model (`sonnet` or `opus`) inline at each spawn. Search the body for `haiku` and remove any reference.
6. Replace any `superpowers:*` reference with the corresponding `forge:*` skill, or inline the needed behavior.
7. Verify every `references/<file>.md` you cite exists.
8. Run `bash plugins/forge/skills/writing-skill/scripts/audit.sh <path/to/SKILL.md>`. Iterate until exit 0.
9. Open the PR with the skill plus its supporting files.

## Running the audit

```sh
bash plugins/forge/skills/writing-skill/scripts/audit.sh path/to/SKILL.md
```

Exit 0 = clean. Exit 1 = violations printed to stderr; fix and re-run. Exit 2 = usage error (bad path).

The audit's nine checks are listed at the top of `scripts/audit.sh` and detailed in `references/slim-audit-checklist.md`.

## Examples

- `examples/good-skill.md` — a compact, well-formed `minimal` skill annotated with why it passes.
- `examples/bad-skill.md` — an anti-pattern collection that the audit catches; useful for verifying the audit script.

## What this skill does not cover

- **What a skill should do** — that's the skill author's design problem; this skill is about *how* to express the skill once you know.
- **When to write a new skill vs extend an existing one** — composition-principle rule 4 (extract when reused, not before) is the heuristic; product judgement decides.
- **Skill discovery and routing** — see `~/.claude/INDEX.md` (auto-generated) and the harness's own routing, not this skill.
