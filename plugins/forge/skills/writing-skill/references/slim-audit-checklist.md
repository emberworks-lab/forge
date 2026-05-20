# Slim audit checklist

Walk these nine steps when authoring a new skill or refactoring an oversized one. The bundled `scripts/audit.sh` automates checks that can be mechanized; the others require the author's judgement.

Each step lists the question to ask, the action if the answer fails, and whether `scripts/audit.sh` covers it automatically.

## 1. Core contract test

**Ask:** What is the one-sentence promise this skill makes?

**Fail action:** If you need two sentences with "and" between distinct verbs, the skill is doing two jobs. Split it.

Automated? No — requires reading. Surfaces as ambiguous `description` front-matter; reviewer's job to flag.

## 2. Decision tree extraction

**Ask:** Does every "if X then Y" branch live in SKILL.md (visible flow), with rationale and edge cases in `references/`?

**Fail action:** Move rationale paragraphs out to `references/<topic>.md`. Leave the trigger condition + outcome in SKILL.md.

Automated? No — structural choice.

## 3. Anti-pattern list extraction

**Ask:** Are there ≥ 5 anti-pattern bullets in SKILL.md?

**Fail action:** Move them to `references/anti-patterns.md` and replace with a one-line summary + link.

Automated? No — count is a soft heuristic; reviewer's call.

## 4. Code / automation extraction

**Ask:** Is there a code block > 10 lines (bash, python, JSON template) inline?

**Fail action:** Move to `scripts/<name>.{sh,py}`, mark executable if a shell script, invoke from SKILL.md with the command line.

Automated? Partially — line-cap check (step 7) catches it indirectly.

## 5. Examples extraction

**Ask:** Are sample input/output blocks longer than 5 lines inline?

**Fail action:** Move to `examples/<scenario>.md` and reference. Keep examples small (≤ 30 lines each).

Automated? No — content choice.

## 6. Convention-doc deduplication

**Ask:** Does the SKILL.md repeat anything that already lives in `forge/docs/conventions/` or another canonical doc?

**Fail action:** Delete the duplicate from SKILL.md; replace with a reference link.

Automated? No — requires cross-reading.

## 7. Line-count target met

**Ask:** Does the skill fit its declared type's line cap (minimal ≤ 80, hybrid ≤ 120, fundamental ≤ 300)?

**Fail action:** Iterate — move more content to references, scripts, or examples; or change the declared type if the responsibilities genuinely warrant it.

Automated? **Yes** — `audit.sh` check 4.

## 8. Subagent model declarations present

**Ask:** Does the skill mention spawning a subagent? If yes, is a model named (`sonnet` or `opus`)? Is `haiku` absent from the body (outside backticks)?

**Fail action:** Add the model name inline where the spawn happens. Remove any bare mention of `haiku`. The audit allows `` `haiku` `` inside backticks (for documenting the rule); bare text fails.

Automated? **Yes** — `audit.sh` check 7.

## 9. Credit attribution present

**Ask:** If the skill is adapted from external work, does the front-matter carry an `inspired-by:` block with `author`, `repo`, `skill`, and `relation` (one of `adapted | concept | structure`)?

**Fail action:** Add the `inspired-by` block. If the skill is original, skip — `inspired-by` is omitted entirely (no empty block).

Automated? **Yes** — `audit.sh` check 5.

## Additional automated checks (no manual analogue)

The audit also enforces the following structural rules that don't map to authoring judgement:

- Front-matter present and well-formed (checks 1-2 in audit.sh).
- `type` value valid (check 3).
- No `superpowers:*` references in the body — must use `forge:*` or inline (check 6).
- Every `references/<file>.md` mentioned in the body resolves to an existing file (check 8).
- No empty sections — `## Heading` followed by another `## Heading` or EOF (check 9).

## Running the audit

```sh
bash plugins/forge/skills/writing-skill/scripts/audit.sh path/to/SKILL.md
```

Exit 0 = clean, exit 1 = violations printed to stderr. Iterate until clean before opening a PR.
