# Mode A — doc-backed body

## Backend-conditional sections

GitHub and Linear surface parent / dependency relations natively (Issue Types + sub-issue API + `blockedBy` / `blocks`). Adding text-block duplicates is noise. Markdown lacks native UI, so its bodies keep the relation blocks.

- Native backends (`github`, `linear`) → skip `## Sub-issues` and `## Depends on` text blocks.
- Text-only backend (`markdown`) → keep them.

## Template

```markdown
## What
<from doc § Goal — paraphrase to 1-2 sentences>

## Acceptance
<doc § Acceptance criteria bullets, copied verbatim>

## References
- docs/0X_<name>.md  ← exhaustive step-by-step plan; read this fully before starting

(## Depends on — added only for backends without native blocked-by; omitted for github / linear.
 For markdown: copy from doc front-matter or master plan story table.)
```

Skip empty sections.
