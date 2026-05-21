# Branch 3 — three HTML variations pattern

Adapted concept: mattpocock's "variations" prototype pattern — three radically different takes on the same screen, switchable by route, user picks one.

## File layout

```
design-explorations/
  <epic-id>/                  # e.g. "forge-76" or "EMB-42"
    a/index.html              # variation A
    b/index.html              # variation B
    c/index.html              # variation C
    README.md                 # one-line note: epic title + question being answered
```

`<epic-id>` is the tracker prefix-N form (`forge-76`, `EMB-42`, `12` for markdown-backend slugs). When in doubt, ask the caller.

## Variation rules

- Three radically different directions — different information architecture, visual hierarchy, primary action emphasis, or layout pattern. Not three colour palettes of the same wireframe.
- Each `index.html` is standalone: no `<script src>` to external files, no build step. Inline `<style>` blocks. Use CSS only unless interaction is the question being answered.
- Same content across all three — the variation is in form, not data. Otherwise the comparison is meaningless.
- Mobile-first when the epic targets mobile; desktop-first otherwise. State the assumption at the top of each file in a comment.

## Iteration prompt

After all three files are written, present:

```
Open each in your browser:
  a → design-explorations/<epic-id>/a/index.html
  b → design-explorations/<epic-id>/b/index.html
  c → design-explorations/<epic-id>/c/index.html

Which works best?  a / b / c / none / iterate-<letter>
```

On `iterate-<letter>`: regenerate that file in place (overwrite). Cap iterations at three per letter; after that, prompt the user to switch branches.

On `a/b/c`: delete the two non-chosen variation directories. The remaining `index.html` is the artifact.

On `none`: delete the entire `design-explorations/<epic-id>/` directory. Fall back to branch 1 or 2.

## Output to the caller

When a variation is chosen, the design source block is:

```
## Design source
design-explorations/<epic-id>/<letter>/index.html  (preview locally)
```

The relative path is what the caller pastes into the epic body. The HTML file itself stays in the working tree until the epic closes; project-level `.gitignore` should include `design-explorations/` so explorations don't bloat the repo history.

## Project setup

One-time per project: add `design-explorations/` to `.gitignore`. The skill does not modify `.gitignore` itself — surface a one-line reminder if the path is currently tracked by git.

## Why this branch exists

When the visual direction is genuinely unclear, generating one careful design is slower than generating three rough ones and picking. The three-up forces choice; the choice surfaces the user's actual preference faster than any interview.
