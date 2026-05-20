# Credit attribution

If a skill is adapted from external work — `obra/superpowers`, `mattpocock/skills`, an Anthropic marketplace plugin, a blog post's checklist, any third-party source — the SKILL.md MUST carry attribution.

The forge plugin contains **no 1:1 copies**. Every adapted skill is rewritten in this plugin's voice with its own structure, examples, and decision criteria. Attribution acknowledges the seed; it does not grant license to skip the rewrite.

## Format

Attribution lives in the front-matter, under an `inspired-by` key. Multiple sources are allowed.

```yaml
---
name: brainstorm
description: Stress-test a feature or design via guided dialectic before implementation.
type: fundamental
inspired-by:
  - author: jesse-vincent/obra
    repo: github.com/obra/superpowers
    skill: brainstorming
    relation: adapted
---
```

## Required fields per entry

| Field | Meaning |
|---|---|
| `author` | Human-readable origin handle (`username` or `username/org`). |
| `repo` | Where the source skill lives (`github.com/...` or comparable URL stub). |
| `skill` | The source skill's name (or filename stem). |
| `relation` | How this skill relates to the source — one of `adapted`, `concept`, `structure`. |

All four are required. Missing any field fails the audit.

## `relation` values

### `adapted`

Derived from the source. Most structural patterns and step-shape are preserved; surface text is rewritten in this plugin's voice, examples are replaced, and integrations are re-wired to the forge ecosystem.

Use when: you started from the source, kept the bones, replaced the skin.

### `concept`

Borrowed a specific idea from the source — a checklist taxonomy, a single decision tree, a useful framing — and wrote the skill from scratch.

Use when: you read the source, took one insight, and built your own thing around it. Example: borrowing mattpocock's "10 types of feedback loop" categorization but writing an entirely fresh skill that consumes it.

### `structure`

Copied the organizational pattern only — Phase 1 / Phase 2 / Phase 3 scaffolding, or a header layout — but the content is unrelated.

Use when: only the file's skeleton resembles the source; the meat is independent.

## What is NOT acceptable

- **Verbatim copies** of someone else's SKILL.md, even with attribution. Attribution is not a license to skip the rewrite.
- **Silent borrowing** — adapting a skill without an `inspired-by` block. If a reviewer can trace the influence and there's no credit, the skill fails the audit.
- **Vague attribution** — "inspired by community patterns". Either you can name the source or you're not inspired by it; cite specifically.

## When attribution is NOT required

- Original skills authored fresh for the forge plugin (e.g. `forge:writing-skill` itself, `forge:epic-close` in its plugin form).
- Skills derived from this user's own prior `~/.claude/commands/` content (it's their own work moving into the plugin; no third-party credit needed).

Self-attribution is silent — no `inspired-by` block, just author the skill.

## Why this matters

Attribution serves three goals:

1. **Credit the upstream author** for their pattern, especially when the source is freely shared.
2. **Document the influence graph** so future maintainers know which skills are siblings and where to look for parallel updates upstream.
3. **Force the rewrite** — having to declare "this is adapted" makes you re-examine whether you actually rewrote, or just copied with light edits.
