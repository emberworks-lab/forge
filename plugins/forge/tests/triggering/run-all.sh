#!/usr/bin/env bash
# run-all.sh — Run all forge skill triggering tests.
#
# BILLING NOTICE: Each case invokes `claude -p` via run-test.sh.
# Run on-demand or in CI only — never in the inner dev loop.
#
# Usage:
#   bash plugins/forge/tests/triggering/run-all.sh
#
# Each row in CASES is "<skill-name> <prompt-file>" relative to SCRIPT_DIR.
# Adapted from superpowers/tests/skill-triggering/run-all.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="${SCRIPT_DIR}/prompts"

# ---------------------------------------------------------------------------
# Case table: (skill-name, prompt-file)
# ---------------------------------------------------------------------------
SKILLS=(
    "epic-close"
    "execute-ticket"
    "e2e"
    "commit"
    "diagnose"
    "update-docs"
)

printf '=== Forge Skill Triggering Tests ===\n\n'

PASSED=0
FAILED=0
RESULTS=()

for skill in "${SKILLS[@]}"; do
    prompt_file="${PROMPTS_DIR}/${skill}.txt"

    if [ ! -f "$prompt_file" ]; then
        printf '⚠️  SKIP: No prompt file for %s\n' "$skill"
        continue
    fi

    printf 'Testing: %s\n' "$skill"

    if "${SCRIPT_DIR}/run-test.sh" "$skill" "$prompt_file" 3 2>&1 | tee "/tmp/forge-skill-test-${skill}.log"; then
        PASSED=$((PASSED + 1))
        RESULTS+=("PASS  $skill")
    else
        FAILED=$((FAILED + 1))
        RESULTS+=("FAIL  $skill")
    fi

    printf '\n---\n\n'
done

printf '\n=== Summary ===\n'
for result in "${RESULTS[@]}"; do
    printf '  %s\n' "$result"
done
printf '\nPassed: %s\n' "$PASSED"
printf 'Failed: %s\n' "$FAILED"
printf '\n'

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi
