# Sub-issue body templates

Used by Step 6.3 of `forge:create-epic` to compose each sub-issue body before calling `create_ticket` via backend recipe. Simpler than the epic. Required: `## What`, `## Acceptance`. Optional: include only when relevant.

```
## What                    (required)
1-2 sentences.

## Steps                   (Mode B-a only)
1. ...
2. ...

## User actions            (Mode M only — exec:manual ticket)
1. ...
2. ...

## Interview the user      (Mode B-b only)
- ...

## Read first              (Mode B-c only)
- <path>

## Acceptance              (required)
- 3-5 verifiable bullets.

## References              (Mode A — points at the plan doc)
- docs/0X_<name>.md

## Design                  (optional — only if THIS sub-issue has its own design artifact)
- Figma: <url>
- HTML mockup: <path or url>
- Description: <md path>

(## Depends on — added only for backends without native blocked-by; omitted for github / linear)
```

## Mode-specific bodies

- **`[A]`** — minimal body, points at the doc. Auto-extract `## Acceptance` bullets from the doc's `## Acceptance criteria` section.
- **`[B-a]`** — full inline plan with `## Steps`.
- **`[B-b]`** — body has `## Interview the user` block with the questions.
- **`[B-c]`** — body has `## Read first` block with file paths.
- **`[M]`** — body has `## User actions` block with the manual steps.

## Where to attach design references

- If a design artifact spans the **whole epic** → put it in the epic's `## Design`.
- If a design artifact is specific to **one sub-issue** → put it in that sub-issue's `## Design`.
- If a sub-issue has no UI / no design at all → omit `## Design` entirely.
