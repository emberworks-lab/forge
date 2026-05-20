# Subagent model declaration

Any SKILL.md that spawns a subagent — via the Agent tool, a `subagent_type` parameter, or parallel agent dispatch — MUST explicitly name the model the subagent runs on. This is a policy rule of the forge plugin, enforced by `scripts/audit.sh`.

## The two models

### `sonnet` — mechanical work

Use for tasks where the answer is structural and the criterion for "correct" is local:

- Parsing structured input (JSON, YAML, regex).
- Formatting and reformatting (lint fixes, prettier-style passes, doc-comment normalization).
- Lint-style or rule-based checks (does this file follow X convention?).
- Applying a known pattern across many files (rename, replace, scaffold).
- Reading and summarizing a defined section.

### `opus` — creative / critical / nuanced work

Use for tasks where the criterion for "correct" requires judgement, weighing trade-offs, or holding multi-step ambiguity:

- Severity classification (is this finding in-place fix or sub-epic?).
- Architecture review (does this design have coupling problems?).
- Security analysis (what attack surface does this expose?).
- Ambiguous trade-off rulings (should we extract or inline?).
- Generating skill content, ticket bodies, or design docs from a brief.
- Translating intent into concrete plans where multiple plans are valid.

## `haiku` is not used in this plugin

The forge plugin does not use `haiku` as a subagent model. The quality floor for `sonnet` is high enough that mechanical work doesn't justify `haiku`'s lower capability. Mentioning `haiku` as a model name in a SKILL.md body fails the audit.

Rationale: in this plugin's experience, `haiku`'s cost savings haven't justified the increase in retry rate or the inconsistency in following step-by-step instructions. If a future skill genuinely benefits from `haiku` (e.g. confidence-scoring at high volume), this rule can be revisited via an ADR — but the default is no `haiku`.

Authoring note: the audit allows `` `haiku` `` (backticked) in skill bodies, because the rule itself has to be expressible in prose without tripping its own check. Bare `haiku` outside backticks fails.

## Declaration format inline

Name the model where the spawn happens. Recommended phrasings:

> Step 4: spawn **Opus** classifier-agent to split findings into in-place vs sub-epic groups.

> Step 6.b: spawn **Sonnet** linter-runner with `mode=fix`.

> In parallel, dispatch three Opus reviewer agents — architecture, security, testing.

The audit looks for the literal words `sonnet` or `opus` near any mention of `subagent`, so the model name must appear in the body text, not just in a config file.

## What counts as "spawning a subagent"?

- Invoking the Agent tool with a `subagent_type` parameter.
- Calling another skill that is documented as agent-based (e.g. `linter-runner`, `test-runner`).
- Dispatching parallel agents for fan-out review or analysis.

A skill that merely **invokes another skill** (without the Agent tool) is composing — that's the composition principle, not subagent spawning, and does not require a model declaration. The model used by the master is unchanged.

## What to do when the model choice is conditional

If a skill spawns one kind of subagent for mechanical work and another for creative work, name both:

> If `mode=fix`, spawn **Sonnet** linter-runner. If `mode=triage`, spawn **Opus** linter-runner to interpret ambiguous warnings.

The audit is satisfied as long as `sonnet` and/or `opus` appear in the body and `haiku` does not.

## Why this rule exists

Without an explicit declaration, the model defaults to whatever the runtime picks. That makes:

- Cost unpredictable across sessions.
- Quality regressions invisible (a skill that silently downgrades looks the same in code review).
- Debugging hard ("why is this agent flaky?" — because it's running on the wrong model).

Forcing every spawn to name its model surfaces these decisions in code review and audit, where they belong.
