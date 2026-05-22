#!/usr/bin/env bash
# run-fixture.sh — Fixture test: assert that forge:simplify removes known duplication.
#
# BILLING NOTICE: The live model-driven run (--live) calls `claude -p` with a real model.
# It is billable and slow (60-300 s). Gate it behind --live explicitly.
# Default (assertion-only) mode does NOT call Claude; it only asserts the
# result produced by a prior or injected run.
#
# Usage:
#   bash plugins/forge/tests/fixtures/simplify/run-fixture.sh [OPTIONS]
#
# Options:
#   --live           Run forge:simplify on the seed file in a real scratch repo (billable).
#   --result-dir     Point assertion at an existing result dir instead of running live.
#                    Mutually exclusive with --live.
#   --help           Show this help.
#
# Exit codes:
#   0   All assertions passed.
#   1   One or more assertions failed.
#   2   Bad arguments or setup error.
#
# Assertion list (derived from forge:simplify SKILL.md + ticket #114):
#   1. The simplified file exists in the result dir.
#   2. The KNOWN-duplicate function pair (formatFullName / buildFullName) no longer
#      both appear in the simplified file — deduplication is asserted by checking
#      that at most one of the two names remains.
#   3. The KNOWN-duplicate function pair (clampToHundred / normalizeToHundred) no
#      longer both appear in the simplified file.
#
# Seed file: plugins/forge/tests/fixtures/simplify/seed-duplicate.ts
#   Contains two pairs of identical functions as documented above.
#
# Related:
#   GitHub issue #114 — this fixture is the automated form of the simplify behavior check.

set -uo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
LIVE_RUN=false
RESULT_DIR=""

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --live)
      LIVE_RUN=true
      shift
      ;;
    --result-dir)
      RESULT_DIR="${2:-}"
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

if [ "$LIVE_RUN" = "true" ] && [ -n "$RESULT_DIR" ]; then
  printf 'ERROR: --live and --result-dir are mutually exclusive\n' >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../../.." && pwd)"
FORGE_PLUGIN_DIR="${REPO_ROOT}/plugins/forge"
SEED_FILE="${SCRIPT_DIR}/seed-duplicate.ts"

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
printf '=== Forge Fixture: simplify on known-duplicate ===\n'
printf 'Mode:       %s\n' "$([ "$LIVE_RUN" = "true" ] && echo "LIVE (billable)" || echo "assertion-only")"
if [ -n "$RESULT_DIR" ]; then
  printf 'Result dir: %s (pre-supplied)\n' "$RESULT_DIR"
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

# Assert that two function names do NOT both appear in a file.
# Passes when at most one of the two names is present (dedup happened).
assert_deduped() {
  local label="$1"
  local file="$2"
  local name_a="$3"
  local name_b="$4"
  local count_a count_b
  count_a="$(grep -c "function ${name_a}" "$file" 2>/dev/null; true)"
  count_b="$(grep -c "function ${name_b}" "$file" 2>/dev/null; true)"
  count_a="${count_a//[[:space:]]/}"
  count_b="${count_b//[[:space:]]/}"
  count_a="${count_a:-0}"
  count_b="${count_b:-0}"
  if [ "$count_a" -ge 1 ] && [ "$count_b" -ge 1 ]; then
    printf 'FAIL  %s  (both %s and %s still present — duplication not removed)\n' \
      "$label" "$name_a" "$name_b"
    FAIL=$((FAIL + 1))
    FAIL_MESSAGES+=("$label: both $name_a and $name_b still present in $file")
  else
    printf 'PASS  %s  (only one of %s / %s remains)\n' "$label" "$name_a" "$name_b"
    PASS=$((PASS + 1))
  fi
}

run_assertions() {
  local root="$1"
  local simplified_file="${root}/seed-duplicate.ts"
  printf 'Asserting simplified output under: %s\n' "$root"
  printf '\n'

  assert_file_exists "simplified file exists" "$simplified_file"

  if [ -f "$simplified_file" ]; then
    assert_deduped \
      "name-pair deduped (formatFullName / buildFullName)" \
      "$simplified_file" \
      "formatFullName" \
      "buildFullName"

    assert_deduped \
      "clamp-pair deduped (clampToHundred / normalizeToHundred)" \
      "$simplified_file" \
      "clampToHundred" \
      "normalizeToHundred"
  else
    printf 'SKIP  dedup assertions (file missing)\n'
    FAIL=$((FAIL + 2))
    FAIL_MESSAGES+=("dedup assertions skipped: simplified file missing")
  fi
}

# ---------------------------------------------------------------------------
# Mode: LIVE (billable)
# ---------------------------------------------------------------------------
if [ "$LIVE_RUN" = "true" ]; then
  printf '*** BILLING NOTICE: running a real claude -p invocation — this is billable ***\n'
  printf '*** Suitable for on-demand manual testing or CI; never for the inner dev loop ***\n\n'

  if [ ! -f "$SEED_FILE" ]; then
    printf 'ERROR: seed file not found: %s\n' "$SEED_FILE" >&2
    exit 2
  fi

  TIMESTAMP="$(date +%s)"
  SCRATCH_DIR="/tmp/forge-fixture-simplify-${TIMESTAMP}"
  mkdir -p "$SCRATCH_DIR"
  printf 'Scratch dir: %s\n' "$SCRATCH_DIR"

  # Copy the seed file into the scratch dir
  cp "$SEED_FILE" "${SCRATCH_DIR}/seed-duplicate.ts"

  # Init a bare git repo so forge:simplify can run git diff
  git -C "$SCRATCH_DIR" init --quiet
  git -C "$SCRATCH_DIR" add .
  git -C "$SCRATCH_DIR" -c user.email="fixture@forge" -c user.name="Fixture" \
    commit -m "seed: known-duplicate file" --quiet

  # Prompt that drives forge:simplify over the seed file.
  # forge:simplify scopes to the most recent diff; we need the file to look
  # "changed" relative to HEAD — so we stage a trivial comment addition first,
  # then ask simplify to review.
  printf '// fixture-trigger\n' >> "${SCRATCH_DIR}/seed-duplicate.ts"
  git -C "$SCRATCH_DIR" add .

  PROMPT_FILE="${SCRATCH_DIR}/prompt.txt"
  cat > "$PROMPT_FILE" <<PROMPT
You are running inside a throwaway scratch repository at ${SCRATCH_DIR}.
The file seed-duplicate.ts has two pairs of obviously duplicated functions:
  - formatFullName and buildFullName (identical bodies)
  - clampToHundred and normalizeToHundred (identical bodies)
Run /forge:simplify to identify and fix all duplication in the staged diff.
Merge each duplicate pair into a single shared function and update all call
sites. Commit the result with message "simplify: remove duplicate functions".
PROMPT

  LOG_FILE="${SCRATCH_DIR}/claude-output.json"

  # Run the skill headless INSIDE the scratch repo (see project-init fixture for
  # the full rationale): cd into SCRATCH_DIR so forge:simplify operates on the
  # scratch diff, not the real tree; --verbose for stream-json; portable timeout.
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

  RESULT_DIR="$SCRATCH_DIR"
fi

# ---------------------------------------------------------------------------
# Mode: assertion-only (RESULT_DIR must be set)
# ---------------------------------------------------------------------------
if [ -z "$RESULT_DIR" ]; then
  printf 'ERROR: no result dir available.\n' >&2
  printf '  Supply --result-dir <path>  to assert an existing result, OR\n' >&2
  printf '  pass --live                 to run forge:simplify in a fresh scratch dir.\n' >&2
  exit 2
fi

if [ ! -d "$RESULT_DIR" ]; then
  printf 'ERROR: result dir does not exist: %s\n' "$RESULT_DIR" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Run assertions
# ---------------------------------------------------------------------------
run_assertions "$RESULT_DIR"

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
