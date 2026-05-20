# Copy templates flow (step 4A, non-Flutter stacks)

Used when the resolved `plugins/forge/skill-templates/<stack>/` folder exists and has real `kit-*.md` files. Flutter has its own path (see `references/flutter-scaffolder.md`).

## Steps

1. **Create `<project>/.claude/skills/`** if it does not exist.
2. **For each `kit-*.md` template in the stack folder:**
   1. Read the template's frontmatter `description`.
   2. Decide whether the skill is relevant to the project's chosen integrations (e.g. skip `kit-add-drift-table.md` if the user picked a different ORM).
   3. Copy the template to `<project>/.claude/skills/<name>.md`.
   4. Replace placeholder package names — e.g. `package:embergard/...` → `package:<this_project>/...`. For npm packages, swap `@org/template-pkg` with the actual scope.
   5. If the template has stack-specific assumptions (e.g. `Result<T>`, `AppException`, barrel pattern, repository pattern), ask the user: "Your project will use these conventions? y/n." On `y` keep as-is; on `n` either adjust or annotate the copied skill with "verify before use".
3. **Create `<project>/.claude/settings.json`** per `references/settings-json.md`.

## What to skip

- Templates whose required dependency is not in the user's selected stack.
- Templates whose frontmatter has a `stacks:` field that does not include the resolved stack key.

## Reminders

- Do not overwrite an existing `<project>/.claude/skills/<name>.md` silently. Ask the user "overwrite / merge / skip" per file.
- The placeholder rewrite is mechanical — verify the resulting files compile / parse before declaring the step done.
