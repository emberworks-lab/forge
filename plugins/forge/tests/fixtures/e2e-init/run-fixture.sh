#!/usr/bin/env bash
# run-fixture.sh — Fixture test: assert that forge:e2e --init scaffolds opt-in markers.
#
# BILLING NOTICE: The live model-driven run (--live) calls `claude -p` with a real model.
# It is billable and slow (60-300 s). Gate it behind --live explicitly.
# Default (assertion-only) mode does NOT call Claude; it only asserts the
# marker files produced by a prior or injected run.
#
# Usage:
#   bash plugins/forge/tests/fixtures/e2e-init/run-fixture.sh [OPTIONS]
#
# Options:
#   --live           Run forge:e2e --init in a real scratch repo (billable; on-demand / CI only).
#   --scaffold-dir   Point assertion at an existing scaffold dir instead of creating one.
#                    Mutually exclusive with --live.
#   --flavor         e2e flavor to opt in to: web | backend (default: backend).
#   --help           Show this help.
#
# Exit codes:
#   0   All assertions passed.
#   1   One or more assertions failed.
#   2   Bad arguments or setup error.
#
# Assertion list (derived from forge:e2e + child SKILL.md contracts):
#
#   Flavor "backend":
#     1. .claude/e2e.json            exists and contains a db_isolation key
#
#   Flavor "web":
#     1. .claude/e2e-web.json        exists and contains an opted_in key
#     2. tests/e2e/.gitkeep          exists (Playwright test dir scaffolded)
#
# Related:
#   GitHub issue #114 — this fixture is the automated form of the e2e --init behavior check.
#   forge:e2e-backend SKILL.md — --init writes .claude/e2e.json with a db_isolation key.
#   forge:e2e-web SKILL.md    — --init writes .claude/e2e-web.json + tests/e2e/.gitkeep.

set -uo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
LIVE_RUN=false
SCAFFOLD_DIR=""
FLAVOR="backend"

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
    --flavor)
      FLAVOR="${2:-}"
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

case "$FLAVOR" in
  web|backend) ;;
  *)
    printf 'ERROR: unknown flavor "%s". Use: web | backend\n' "$FLAVOR" >&2
    exit 2
    ;;
esac

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
FORGE_PLUGIN_DIR="${REPO_ROOT}/plugins/forge"

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
printf '=== Forge Fixture: e2e --init scaffold ===\n'
printf 'Mode:   %s\n' "$([ "$LIVE_RUN" = "true" ] && echo "LIVE (billable)" || echo "assertion-only")"
printf 'Flavor: %s\n' "$FLAVOR"
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

assert_json_key() {
  local label="$1"
  local file="$2"
  local key="$3"
  if grep -q "\"${key}\"" "$file" 2>/dev/null; then
    printf 'PASS  %s  (key "%s" found)\n' "$label" "$key"
    PASS=$((PASS + 1))
  else
    printf 'FAIL  %s  (key "%s" not found in %s)\n' "$label" "$key" "$file"
    FAIL=$((FAIL + 1))
    FAIL_MESSAGES+=("$label: key \"$key\" missing in $file")
  fi
}

run_assertions_backend() {
  local root="$1"
  local marker="${root}/.claude/e2e.json"
  printf 'Asserting e2e-backend scaffold under: %s\n' "$root"
  printf '\n'

  assert_file_exists ".claude/e2e.json exists"          "$marker"

  if [ -f "$marker" ]; then
    assert_json_key   ".claude/e2e.json has db_isolation" "$marker" "db_isolation"
  else
    printf 'SKIP  db_isolation key check (marker missing)\n'
    FAIL=$((FAIL + 1))
    FAIL_MESSAGES+=("db_isolation check skipped: marker missing")
  fi
}

run_assertions_web() {
  local root="$1"
  local marker="${root}/.claude/e2e-web.json"
  printf 'Asserting e2e-web scaffold under: %s\n' "$root"
  printf '\n'

  assert_file_exists ".claude/e2e-web.json exists"          "$marker"

  if [ -f "$marker" ]; then
    assert_json_key   ".claude/e2e-web.json has opted_in"   "$marker" "opted_in"
  else
    printf 'SKIP  opted_in key check (marker missing)\n'
    FAIL=$((FAIL + 1))
    FAIL_MESSAGES+=("opted_in check skipped: marker missing")
  fi

  assert_file_exists "tests/e2e/.gitkeep exists" "${root}/tests/e2e/.gitkeep"
}

run_assertions() {
  local root="$1"
  case "$FLAVOR" in
    backend) run_assertions_backend "$root" ;;
    web)     run_assertions_web     "$root" ;;
  esac
}

# ---------------------------------------------------------------------------
# Mode: LIVE (billable)
# ---------------------------------------------------------------------------
if [ "$LIVE_RUN" = "true" ]; then
  printf '*** BILLING NOTICE: running a real claude -p invocation — this is billable ***\n'
  printf '*** Suitable for on-demand manual testing or CI; never for the inner dev loop ***\n\n'

  TIMESTAMP="$(date +%s)"
  SCRATCH_DIR="/tmp/forge-fixture-e2e-init-${TIMESTAMP}"
  mkdir -p "${SCRATCH_DIR}/.claude"
  printf 'Scratch repo: %s\n' "$SCRATCH_DIR"

  # Minimal tracker.json so forge:e2e can resolve the platform
  if [ "$FLAVOR" = "web" ]; then
    cat > "${SCRATCH_DIR}/.claude/tracker.json" <<JSON
{
  "backend": "markdown",
  "platforms": ["web"]
}
JSON
  else
    cat > "${SCRATCH_DIR}/.claude/tracker.json" <<JSON
{
  "backend": "markdown",
  "platforms": ["backend"]
}
JSON
  fi

  # Init a bare git repo
  git -C "$SCRATCH_DIR" init --quiet

  PROMPT_FILE="${SCRATCH_DIR}/prompt.txt"
  cat > "$PROMPT_FILE" <<PROMPT
You are running inside a throwaway scratch repository at ${SCRATCH_DIR}.
Run /forge:e2e --init for the ${FLAVOR} flavor.
When asked whether to opt in, answer YES.
When asked for a strategy, accept the default (ephemeral-postgres for backend, chromium for web).
Do NOT run any actual tests; only write the marker file(s) and scaffold files.
Proceed without pausing for further confirmation.
PROMPT

  LOG_FILE="${SCRATCH_DIR}/claude-output.json"

  timeout 600 claude \
    -p "$(cat "$PROMPT_FILE")" \
    --plugin-dir "$FORGE_PLUGIN_DIR" \
    --dangerously-skip-permissions \
    --max-turns 20 \
    --output-format stream-json \
    > "$LOG_FILE" 2>&1 || true

  printf 'Claude run complete. Log: %s\n\n' "$LOG_FILE"

  SCAFFOLD_DIR="$SCRATCH_DIR"
fi

# ---------------------------------------------------------------------------
# Mode: assertion-only (SCAFFOLD_DIR must be set)
# ---------------------------------------------------------------------------
if [ -z "$SCAFFOLD_DIR" ]; then
  printf 'ERROR: no scaffold dir available.\n' >&2
  printf '  Supply --scaffold-dir <path>  to assert an existing scaffold, OR\n' >&2
  printf '  pass --live                   to run forge:e2e --init in a fresh scratch repo.\n' >&2
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
