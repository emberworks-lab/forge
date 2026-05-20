# Mode B — inline body shapes (a / b / c / d)

## Mode B clarifying questions (Step 2B)

Ask up to 5 in ONE batch, only on real gaps:

- What's the user-visible outcome / DoD?
- Which files/areas in scope, which explicitly out?
- Is the work fully scoped now, or does the executor need to interview the user / read existing code first?
- Anything blocking it (other tickets)?
- References to doc sections, Figma URLs, related issues?
- Are tests non-obvious for this ticket? (property-based, golden, integration — note in `## Tests`)

## Picking the flavour

Pick the body shape based on what came back:

- **Option (a) — full inline plan.** Work is fully scoped. Body has `## Files` + bite-sized `## Tasks` (writing-plans discipline).
- **Option (b) — interview-first.** Scope is partial; the executor needs more from the user. Body has `## Interview the user` listing exact questions.
- **Option (c) — read-first.** Scope depends on existing code. Body has `## Read first` listing exact files/docs the executor must read.
- **Option (d) — skill-authoring.** Ticket creates a new `~/.claude/commands/<name>.md` or agent. Body uses RED-GREEN-REFACTOR shape. Aligned with `forge:writing-skill`.

## Backend-conditional sections

- Native backends (`github`, `linear`) → skip `## Sub-issues` and `## Depends on` text blocks.
- Text-only backend (`markdown`) → keep them.

## Composed body — all four flavours share the same scaffold

```markdown
## What
<2-4 sentences — goal + why if non-obvious>

## Files      [option a — exact paths, no globs]
- Create: `exact/path/to/file.dart`
- Modify: `exact/path/to/existing.dart:123-145`
- Test: `test/exact/path/to/test.dart`

## Tasks      [option a — bite-sized 2-5 min each, TDD-shaped]
### Task 1: <Component>
- [ ] Write failing test  (code block with test)
- [ ] Run test, verify FAIL with expected message
- [ ] Minimal implementation  (code block)
- [ ] Run, verify PASS
### Task 2: …

## Interview the user      [option b only]
Before starting, ask:
- ...
- ...

## Read first      [option c only]
- <file path>
- <doc reference>

## Acceptance
- 3-5 verifiable bullets

## Tests   (only if testing scope is non-obvious — property-based, golden, integration)
- <e.g. "Add property-based glados test for damage formula given seed in [1, 1000]">

(## Depends on — added only for backends without native blocked-by; omitted for github / linear)
```

## Mode B-a — writing-plans discipline (full shape)

Each task is a bite-sized 2-5 minute unit with: failing test (code block, exact assertion), verify-FAIL step (exact command + expected error), minimal implementation (code block), verify-PASS step.

Example:

```markdown
### Task 1: Hit-rate clamp formula

- [ ] **Step 1: Write failing test**
  ```dart
  test('hit rate clamps at 0.95 when buff exceeds cap', () {
    expect(hitRate(base: 1.20, dexMult: 1.0), 0.95);
  });
  ```
- [ ] **Step 2: Run test, verify FAIL**
  Run: `flutter test test/combat/hit_rate_test.dart`
  Expected: FAIL — "hitRate not defined"
- [ ] **Step 3: Minimal implementation**
  ```dart
  double hitRate({required double base, required double dexMult}) {
    final raw = base * dexMult;
    return raw.clamp(0.05, 0.95);
  }
  ```
- [ ] **Step 4: Run, verify PASS**
  Run: `flutter test test/combat/hit_rate_test.dart`
  Expected: 1 test passed
```

Per-task `git commit` instructions are **not** included — commits are the orchestrator's job (one commit per ticket via `forge:execute-ticket` / `forge:execute-epic`).

### No-Placeholders enforcement

When drafting Mode B-a tickets, REJECT these in your own draft before showing it to the user:

- Phrases like "TBD", "implement later", "fill in", "see code"
- Vague step verbs like "add error handling" / "handle the edge case" without a code block
- File paths with `<placeholder>` / globs / "the relevant file"
- Type names referenced but never defined in any task block
- Test descriptions without expected assertion or expected failure mode
- Step counts without runnable verification ("verify it works" without a command)

If you catch a placeholder mid-draft, expand it inline OR tell the user: "Step N is too vague — what's the exact behavior? otherwise we should switch to Mode A and write a `docs/0X` spec first."

### Self-review pass (before showing the body)

After composing, scan once for:

- [ ] Every `## Files` entry has a Create / Modify / Test prefix and an exact path
- [ ] Every task has a failing-test + impl + verify-pass triple
- [ ] No placeholders (per above)
- [ ] Acceptance bullets are verifiable (concrete command, file path, or visible outcome)
- [ ] Type / function names referenced in one task are defined in an earlier task or already exist
- [ ] No git-workflow content

Fix any failure before moving to Step 3 (Confirm).

## Mode B-d — skill-authoring (RED-GREEN-REFACTOR)

Use when the ticket creates a new `~/.claude/commands/<name>.md`, `~/.claude/agents/<name>.md`, or substantively modifies an existing skill. Aligns with `forge:writing-skill` TDD-mapping.

```markdown
## Skill goal
<1-2 sentences — what behavior should this skill ensure when triggered?>

## Pressure scenarios (RED phase)
3+ concrete scenarios where an agent (without this skill) would skip the desired discipline:
- Trigger condition
- What the agent would naïvely do
- What this skill should make it do instead

Example:
- **Scenario 1: feedback contains both valid + questionable suggestions.** Naïve: implement all. Skill behavior: classify each, push back on questionable.
- **Scenario 2: feedback is from senior reviewer.** Naïve: rubber-stamp. Skill behavior: still verify technically.
- **Scenario 3: feedback contradicts ADR.** Naïve: implement and break ADR. Skill behavior: surface ADR conflict to user before changing.

## Skill body draft (GREEN phase)
The actual content of `~/.claude/commands/<name>.md` (or agent body). Include frontmatter (name, description, category) and full body.

Reminders:
- HTML comment with source/adoption-date goes AFTER the closing `---` of frontmatter.
- Description field is CSO compliant: "Use when..." trigger phrase only, no workflow summary.

## Anticipated rationalizations + counters
List 3-5 reasons an agent might rationalize skipping this skill, with the counter:
- "This is a simple case." → counter: skill applies regardless of perceived simplicity.
- "I already know this discipline." → counter: knowing the concept ≠ executing it under pressure.

## Description field
Final CSO-compliant `description:` line for the frontmatter.

## Acceptance
- Skill file exists at `~/.claude/commands/<name>.md` (or agents path)
- Frontmatter parses correctly (description visible in `/skill list` output, no `<!--` prefix)
- Surfaces in `INDEX.md` under correct category after `plugins/forge/scripts/generate-index.sh` run
- Manual smoke: invoke skill via trigger phrase from one of the pressure scenarios — agent follows skill body, not naïve path
```

Mode B-d cross-references `forge:writing-skill` for the full TDD-for-skills methodology.

## Quick reference — flavour scaffolds

### Mode B option (b) — interview-first

```markdown
## What
<2-4 sentences>

## Interview the user
Before starting, ask:
- ...
- ...

## Acceptance
- ...
```

### Mode B option (c) — read-first

```markdown
## What
<2-4 sentences>

## Read first
- <path>
- <path>

## Acceptance
- ...
```
