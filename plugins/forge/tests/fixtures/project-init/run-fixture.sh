#!/usr/bin/env bash
# run-fixture.sh — Fixture test: assert that project-init produces the expected scaffold.
#
# BILLING NOTICE: The live model-driven run (--live) calls `claude -p` with a real model.
# It is billable and slow (60-300 s). Gate it behind --live explicitly.
# Default (dry-run / assertion-only) mode does NOT call Claude; it only asserts
# the scaffold artifacts produced by a prior or injected run.
#
# Usage:
#   bash plugins/forge/tests/fixtures/project-init/run-fixture.sh [OPTIONS]
#
# Options:
#   --live           Run project-init in a real scratch repo (billable; on-demand / CI only).
#   --scaffold-dir   Point assertion at an existing scaffold dir instead of creating one.
#                    Mutually exclusive with --live.
#   --stack          Stack to use for the live run (default: mobile-flutter).
#   --help           Show this help.
#
# Exit codes:
#   0   All assertions passed.
#   1   One or more assertions failed.
#   2   Bad arguments or setup error.
#
# Assertion list (derived from project-init SKILL.md Contract + issue #62 procedure):
#   1. CLAUDE.md                  exists at scaffold root
#   2. .claude/settings.json      exists at scaffold root
#   3. .claude/tracker.json       exists at scaffold root
#   4. docs/owner-overview.md     exists at scaffold root
#   5. .claude/skills/kit-*.md    at least one kit-* skill file is present
#
# Related:
#   GitHub issue #62  — this fixture is the automated form of #62.
#   #62 closes after a green live fixture run; do NOT auto-close it here.

set -uo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
LIVE_RUN=false
SCAFFOLD_DIR=""
STACK="mobile-flutter"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --live)
      LIVE_RUN=true
      shift
      ;;
    --scaffold-dir)
      SCAFFOLD_DIR="${2:-}"
      shift 2
      ;;
    --stack)
      STACK="${2:-}"
      shift 2
      ;;
    --help|-h)
      grep '^#' "$0" | grep -v '#!/' | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

if [ "$LIVE_RUN" = "true" ] && [ -n "$SCAFFOLD_DIR" ]; then
  printf 'ERROR: --live and --scaffold-dir are mutually exclusive\n' >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
FORGE_PLUGIN_DIR="${REPO_ROOT}/plugins/forge"
SKILL_TEMPLATES_DIR="${FORGE_PLUGIN_DIR}/skill-templates"

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
printf '=== Forge Fixture: project-init scaffold ===\n'
printf 'Mode:         %s\n' "$([ "$LIVE_RUN" = "true" ] && echo "LIVE (billable)" || echo "assertion-only")"
printf 'Stack:        %s\n' "$STACK"
if [ -n "$SCAFFOLD_DIR" ]; then
  printf 'Scaffold dir: %s (pre-supplied)\n' "$SCAFFOLD_DIR"
fi
printf '\n'

# ---------------------------------------------------------------------------
# Assertion engine
# ---------------------------------------------------------------------------

PASS=0
FAIL=0
FAIL_MESSAGES=()

assert_file_exists() {
  local label="$1"
  local path="$2"
  if [ -f "$path" ]; then
    printf 'PASS  %s\n' "$label"
    PASS=$((PASS + 1))
  else
    printf 'FAIL  %s  (missing: %s)\n' "$label" "$path"
    FAIL=$((FAIL + 1))
    FAIL_MESSAGES+=("$label: missing $path")
  fi
}

assert_glob_exists() {
  local label="$1"
  local dir="$2"
  local pattern="$3"
  local matches
  # Use find to avoid glob expansion issues when no match exists
  matches="$(find "$dir" -maxdepth 1 -name "$pattern" -type f 2>/dev/null | head -1)"
  if [ -n "$matches" ]; then
    printf 'PASS  %s  (%s)\n' "$label" "$(basename "$matches")"
    PASS=$((PASS + 1))
  else
    printf 'FAIL  %s  (no file matching %s in %s)\n' "$label" "$pattern" "$dir"
    FAIL=$((FAIL + 1))
    FAIL_MESSAGES+=("$label: no $pattern in $dir")
  fi
}

run_assertions() {
  local root="$1"
  printf 'Asserting scaffold under: %s\n' "$root"
  printf '\n'

  assert_file_exists    "CLAUDE.md"             "${root}/CLAUDE.md"
  assert_file_exists    ".claude/settings.json" "${root}/.claude/settings.json"
  assert_file_exists    ".claude/tracker.json"  "${root}/.claude/tracker.json"
  assert_file_exists    "docs/owner-overview.md" "${root}/docs/owner-overview.md"
  assert_glob_exists    ".claude/skills/kit-*"  "${root}/.claude/skills" "kit-*.md"
}

# ---------------------------------------------------------------------------
# Mode: LIVE (billable)
# ---------------------------------------------------------------------------
if [ "$LIVE_RUN" = "true" ]; then
  printf '*** BILLING NOTICE: running a real claude -p invocation — this is billable ***\n'
  printf '*** Suitable for on-demand manual testing or CI; never for the inner dev loop ***\n\n'

  # Validate stack has kit-* templates before even spinning up Claude
  KIT_COUNT="$(find "${SKILL_TEMPLATES_DIR}/${STACK}" -maxdepth 1 -name 'kit-*.md' -type f 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$KIT_COUNT" -eq 0 ]; then
    printf 'WARNING: no kit-*.md found in %s/%s — kit-* assertion will likely fail\n' \
      "$SKILL_TEMPLATES_DIR" "$STACK" >&2
  else
    printf 'INFO: found %s kit-*.md file(s) in %s/%s\n\n' "$KIT_COUNT" "$SKILL_TEMPLATES_DIR" "$STACK"
  fi

  TIMESTAMP="$(date +%s)"
  SCRATCH_DIR="/tmp/forge-fixture-project-init-${TIMESTAMP}"
  mkdir -p "$SCRATCH_DIR"
  printf 'Scratch repo: %s\n' "$SCRATCH_DIR"

  # Init a bare git repo so project-init doesn't complain about missing .git
  git -C "$SCRATCH_DIR" init --quiet

  # Create a non-interactive prompt that drives project-init for the chosen stack.
  # project-init is interactive by design; this prompt steers it deterministically.
  PROMPT_FILE="${SCRATCH_DIR}/prompt.txt"
  cat > "$PROMPT_FILE" <<PROMPT
You are running inside a throwaway scratch repository at ${SCRATCH_DIR}.
Run /forge:project-init with the following answers:
- Project type: single-platform
- Stack: ${STACK}
- Project name: fixture-test-project
- Elevator pitch: A throwaway repo for fixture testing of the project-init skill.
- Docs scaffold: No
- Tracker backend: markdown
- Do NOT create any Linear project.
Proceed without pausing for confirmation. Use all defaults for remaining questions.
PROMPT

  LOG_FILE="${SCRATCH_DIR}/claude-output.json"

  # Run the skill headless INSIDE the scratch repo.
  #   - cd into SCRATCH_DIR so the skill operates on the scratch repo, NOT the real
  #     working tree — prompt text alone does NOT change claude's cwd, and
  #     project-init scaffolds whatever `pwd` returns.
  #   - --verbose is required for --print --output-format stream-json to emit events.
  #   - GNU timeout/gtimeout are absent on stock macOS; use whichever exists, else none
  #     (--max-turns still bounds the run).
  CLAUDE_ARGS=(
    -p "$(cat "$PROMPT_FILE")"
    --plugin-dir "$FORGE_PLUGIN_DIR"
    --dangerously-skip-permissions
    --max-turns 20
    --output-format stream-json
    --verbose
  )
  if command -v timeout >/dev/null 2>&1; then
    ( cd "$SCRATCH_DIR" && timeout 600 claude "${CLAUDE_ARGS[@]}" ) > "$LOG_FILE" 2>&1 || true
  elif command -v gtimeout >/dev/null 2>&1; then
    ( cd "$SCRATCH_DIR" && gtimeout 600 claude "${CLAUDE_ARGS[@]}" ) > "$LOG_FILE" 2>&1 || true
  else
    ( cd "$SCRATCH_DIR" && claude "${CLAUDE_ARGS[@]}" ) > "$LOG_FILE" 2>&1 || true
  fi

  printf 'Claude run complete. Log: %s\n\n' "$LOG_FILE"

  SCAFFOLD_DIR="$SCRATCH_DIR"
fi

# ---------------------------------------------------------------------------
# Mode: assertion-only (SCAFFOLD_DIR must be set, either by --live or --scaffold-dir)
# ---------------------------------------------------------------------------
if [ -z "$SCAFFOLD_DIR" ]; then
  printf 'ERROR: no scaffold dir available.\n' >&2
  printf '  Supply --scaffold-dir <path>  to assert an existing scaffold, OR\n' >&2
  printf '  pass --live                   to run project-init in a fresh scratch repo.\n' >&2
  exit 2
fi

if [ ! -d "$SCAFFOLD_DIR" ]; then
  printf 'ERROR: scaffold dir does not exist: %s\n' "$SCAFFOLD_DIR" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Run assertions
# ---------------------------------------------------------------------------
run_assertions "$SCAFFOLD_DIR"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
printf '\nSummary: %d passed, %d failed\n' "$PASS" "$FAIL"

if [ "${#FAIL_MESSAGES[@]}" -gt 0 ]; then
  printf '\nFailed assertions:\n'
  for msg in "${FAIL_MESSAGES[@]}"; do
    printf '  - %s\n' "$msg"
  done
fi

# Clean up scratch dir only when this script created it (--live mode)
if [ "$LIVE_RUN" = "true" ] && [ -n "${SCRATCH_DIR:-}" ] && [ -d "${SCRATCH_DIR:-}" ]; then
  printf '\nCleaning up scratch dir: %s\n' "$SCRATCH_DIR"
  rm -rf "$SCRATCH_DIR"
fi

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi

exit 0
