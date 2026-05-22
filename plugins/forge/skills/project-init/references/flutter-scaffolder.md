# Flutter scaffolder pipeline (step 4A-flutter)

When `stack == "mobile-flutter"`, the basic `4A` copy is replaced by the **Flutter scaffolder pipeline** (FORGE-5.3, EMB-288). The scaffolder both copies `kit-*` skills and generates the full project skeleton in one shot. The interview runs first; the scaffolder consumes its answers.

## Pipeline overview

1. Run the Flutter interview.
2. Persist answers to a temp JSON file.
3. Invoke `plugins/forge/scripts/scaffold-flutter.sh`.
4. After the scaffolder returns, perform post-scaffold remote setup.
5. Print final output.

## 4A-flutter.1 — Run the Flutter interview

Run the 26-question interview from the scaffolder spec (tooling docs not migrated — deleted in EPIC E; 8 phases). Each question uses `AskUserQuestion` for picks and free text for names / IDs. Skip conditional questions per the spec's "Conditional logic summary" table. Defaults are documented per question — they reflect current best practice, not the as-shipped flutter-template stack.

Default workspace target: `~/Development/emberworks_lab_projects/<project_snake_case>/` (per the global "Pet projects default to emberworks_lab_projects/" rule). Confirm with the user before scaffolding.

## 4A-flutter.2 — Persist interview answers to JSON

Write the resolved answers to a temp file using the `Q<phase>_<index>_<key>` schema from `plugins/forge/scripts/_scaffold_flutter.py:ANSWER_SCHEMA`:

```json
{
  "Q1_1_layout": "inline",
  "Q1_2_name": "<from interview>",
  "Q1_3_bundle_id": "<from interview>",
  "Q3_1_state_mgmt": "bloc",
  "Q4_1_backend": "supabase",
  "linear_prefix": "<derived from selected team's key, e.g. EMB>",
  "linear_team": "<from common interview step 2>",
  "tagline": "<from common interview step 5>",
  "credentials": {
    "supabase": {"mode": "defer"},
    "sentry":   {"mode": "defer"}
  }
}
```

The optional `credentials` block (FORGE-5.4 / EMB-289) carries the per-integration three-way decision collected via Q5.3 / Q7.4 / Q7.5: `provide` (with `values`), `defer` (default if omitted — emits stubs + Mode M ticket), or `skip`. <!-- TODO: linting docs not migrated, deleted in EPIC E; flutter-scaffolder-interview.md Credentials JSON serialization was in tooling/ which is out of scope -->

Save to `/tmp/scaffold-flutter-answers.json` (or any `mktemp -d` location).

## 4A-flutter.3 — Invoke the scaffolder

```bash
plugins/forge/scripts/scaffold-flutter.sh \
  --answers /tmp/scaffold-flutter-answers.json \
  --target  ~/Development/emberworks_lab_projects/<project_snake_case>/ \
  [--validate]   # optional: runs `flutter pub get` + `flutter analyze` post-scaffold
```

### What the scaffolder does

- **First step (EMB-314)**: `flutter create <target> --org <bundle-id-prefix> --project-name <name_snake> --platforms=android,ios --description "<desc>"` — the Flutter SDK owns the canonical project shell (`android/`, `ios/`, `.metadata`, base `test/widget_test.dart`). All subsequent steps overlay customisations.
- Reads `plugins/forge/skill-templates/mobile-flutter/template-source.json` to find the pinned `flutter-template@v0.1.0` source.
- Copies the template's `lib/src/**` into the new project (inline at `lib/core/` per Q1.1 default, OR as a local package at `packages/shared_core/`).
- Rewrites `package:shared_core/...` imports to the new package name (inline layout only).
- Drops directories for unselected features (e.g. `lib/core/network/websocket/` if Q4.5 = No, `lib/core/storage/hive/` if Q4.3 ≠ hive_ce, `keycloak_config.dart` + `auth_guard.dart` if Q5.1 = None).
- Generates `pubspec.yaml` with deps composed from interview answers (Bloc + go_router + Drift + Supabase by default; per-choice swaps + STUB markers for alternatives).
- Generates `analysis_options.yaml` (`very_good_analysis` by default).
- Generates `lib/config/app_config.dart` with `.dev()` / `.prod()` (and `.staging()` if Q8.1) factories backed by `--dart-define-from-file=.env.<flavor>`.
- Generates `lib/main_<flavor>.dart` per Q8.1 environments.
- Generates `.env.example` (committed, shape only) + `.env.<flavor>` files (gitignored). Per FORGE-5.4 (EMB-289), each integration the user selected has a per-block credentials decision (`provide` writes real values, `defer` writes workable offline stubs like `SUPABASE_URL=https://stub.supabase.co`, `skip` omits the keys).
- Generates IDE configs: `.vscode/launch.json` and / or `.idea/runConfigurations/<Flavor>_<Mode>.xml` per Q8.2.
- Generates `CLAUDE.md` from `plugins/forge/docs/conventions/claude-md-template.md`, populated with Flutter Essential commands, Mandatory rules (`Result<T>`, `AppException`, theme tokens, `/log-decision`), Documentation inventory, stack-aware Skills section.
- Copies stack-relevant `kit-*` skills from `plugins/forge/skill-templates/mobile-flutter/` into `<project>/.claude/skills/` (filtered by Q4.3 / Q6.3 / Q6.5).
- Generates `<project>/.claude/settings.json` with allowed Bash matching the Essential commands.
- Copies `docs/00_meta/{decisions-log,roadmap,docs-workflow,glossary}.md` from `plugins/forge/skill-templates/_common/docs/00_meta/` (resolves the docs-scaffold answer for mobile-flutter automatically).
- Generates `.gitignore`.
- Writes `.claude/scaffold-report.json` with Mode M tickets to surface to the user.

## 4A-flutter.4 — After the scaffolder returns

Platform shells (`android/`, `ios/`, `.metadata`) are now generated by the scaffolder itself via `flutter create` (EMB-314). No manual `flutter create` invocation is required afterwards.

1. **Read** `<project>/.claude/scaffold-report.json` — pull `mode_m_tickets` and `credentials_resolution` (FORGE-5.4 / EMB-289). The latter is a flat `{integration: provide|defer|skip}` map. If the user opted into Linear automation (step 2.6 = Yes), pass `mode_m_tickets` through to the Linear flow instead of re-detecting in step 7.5.3 — the scaffolder's list is canonical because it already accounts for credential mode (`provide` → no ticket emitted).
2. **Skip step 4C** — the scaffolder already produced `.claude/skills/`. SKILLS.md generation can still run as a follow-up if `plugins/forge/scripts/generate-project-skills.sh` is available; otherwise add a TODO note to the chat output.
3. **Skip step 5** (Generate CLAUDE.md) — the scaffolder produced it.
4. **Skip step 6** (Initialize docs/00_meta/) — the scaffolder already copied it.
5. **Skip step 7** (settings.json) — the scaffolder produced it.
6. **Continue at step 7.25** (Tracker setup) → **step 7.5** (Linear automation) if the user opted in; pass the report's `mode_m_tickets` as the canonical source.

If the scaffolder fails (non-zero exit), surface the error and **HALT** — do not proceed with a broken target dir.

## 4A-flutter.5 — Phase 4: gh repo + Linear project (FORGE-5.5 / EMB-290)

Run after the scaffolder returns successfully.

> **Multi-platform note.** This whole phase (git init + `gh repo create`) is for
> single-platform Flutter projects. In any multi-platform run it is **skipped**:
> `sub-folder` / `monorepo` keep one root repo, and `polyrepo` does per-repo git
> setup uniformly for every platform at step 7.9 (`references/polyrepo-setup.md`).
> See `references/scaffolding-logic.md` S2.2.

### 4A-flutter.5.1 — Git init

```bash
cd <target>
git init -b main
git add .
git commit -m "Initial commit: Flutter scaffold via /project-init" \
  -m "Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

Use the Co-Authored-By footer matching the model that ran the scaffolder; see `plugins/forge/docs/conventions/git-workflow.md`.

### 4A-flutter.5.2 — Ask about GitHub repo

Ask via `AskUserQuestion`:

```
Q: "Create a GitHub repo for this project?"
A — Yes — create + push initial commit
B — Yes — create only (no push)
C — No — local only (skip)
```

**A (create_push) or B (create_only):**

1. Check `gh auth status`. If unauthenticated:
   > "GitHub CLI is not authenticated. Run `gh auth login` first, then re-run `/project-init` or run `gh repo create <name> --private --source=. --description="<desc>"` manually."
   Skip the GitHub step and continue.
2. Check for an existing repo named `<project_name_snake>`. On conflict, ask: "A GitHub repo named `<name>` already exists under your account. Rename the project, use that existing repo, or skip GitHub?" Wait for an answer.
3. Run:
   ```bash
   gh repo create <project_name_snake> --private \
     --source=. \
     --description="<Q1_4_description from interview, or empty>"
   ```
   `--source=.` automatically adds the `origin` remote.
4. If A: also run `git push -u origin main`.
5. Capture the repo URL via `gh repo view <name> --json url -q .url`.

**C (skip):** nothing to do.

Record the outcome in `remote_setup.gh_repo` of the scaffold report.

Edge cases:

- `gh` not installed → print "GitHub CLI (`gh`) not found. Install from https://cli.github.com/ or create the repo manually." Skip gracefully.
- Non-zero exit from `gh repo create` (other than auth / conflict) → print the error, skip push, continue.

### 4A-flutter.5.3 — Ask about Linear project

Use the same flow as the regular step 7.5 — but with the scaffold report's `mode_m_tickets` as the canonical input (do not re-detect). See `references/linear-automation.md`.

If the Linear MCP is unavailable, print: "Linear automation skipped — no MCP connection. Set up the Linear MCP and re-run `/project-init --linear-only` if you want the project created later." Skip; continue to final output.

### 4A-flutter.5.4 — Final output

```
Flutter project scaffolded: <name>
Local: <target dir>
GitHub: <repo URL> (or "skipped")
Linear: <project URL> (or "skipped")

Next steps:
1. cd <target dir>
2. flutter run --flavor dev
3. Complete any manual-setup tickets in Linear (credentials) — see P0 — Bootstrap epic
```

If the user skipped both GitHub and Linear:

```
Flutter project scaffolded: <name>
Local: <target dir>
GitHub: skipped
Linear: skipped

Next steps:
1. cd <target dir>
2. flutter run --flavor dev
3. When ready: gh repo create <name_snake> --private --source=. --description="..."
4. When ready: re-run /project-init --linear-only to create a Linear project
```
