#!/usr/bin/env bash
# run-test.sh — Triggering test tier: assert that a naive prompt causes Claude to invoke a forge skill.
#
# BILLING NOTICE: This runner calls `claude -p` with a real model. Each invocation is
# billable and slow (10-60 s). Run on-demand or in CI only — never in the inner dev loop.
#
# Usage:
#   bash plugins/forge/tests/triggering/run-test.sh <skill-name> <prompt-file> [max-turns]
#
# Arguments:
#   <skill-name>   Short name of the forge skill (e.g. "tdd", "brainstorm").
#                  The runner looks for a Skill tool-use whose name is "forge:<skill-name>".
#   <prompt-file>  Path to a plain-text file containing the naive prompt.
#                  The prompt must NOT mention the skill by name — it should describe
#                  a problem that naturally triggers the skill.
#   [max-turns]    Maximum Claude turns (default: 3).
#
# Exit codes:
#   0   The expected skill fired.
#   1   The skill did NOT fire (or claude exited non-zero).
#   2   Bad arguments or missing prompt file.
#
# How it works:
#   1. Invokes: claude -p "<prompt>" --plugin-dir <forge-plugin-dir>
#               --dangerously-skip-permissions --max-turns <N> --output-format stream-json
#   2. Captures stream-json to a timestamped log under /tmp/forge-triggering-tests/.
#   3. Scans the log for a Skill tool-use event whose "skill" field matches "forge:<skill-name>".
#   4. Prints a human-readable PASS / FAIL summary and exits accordingly.
#
# Adapted from superpowers/tests/skill-triggering/run-test.sh.
# Key differences: plugin dir points to the forge plugin; skill prefix is "forge:".

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument handling
# ---------------------------------------------------------------------------
SKILL_NAME="${1:-}"
PROMPT_FILE="${2:-}"
MAX_TURNS="${3:-3}"

if [ -z "$SKILL_NAME" ] || [ -z "$PROMPT_FILE" ]; then
    printf 'Usage: %s <skill-name> <prompt-file> [max-turns]\n' "$0" >&2
    printf 'Example: %s tdd ./prompts/tdd.txt\n' "$0" >&2
    exit 2
fi

if [ ! -f "$PROMPT_FILE" ]; then
    printf 'ERROR: prompt file not found: %s\n' "$PROMPT_FILE" >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

# SCRIPT_DIR: tests/triggering/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# FORGE_PLUGIN_DIR: plugins/forge/  (two levels up from tests/triggering)
FORGE_PLUGIN_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TIMESTAMP="$(date +%s)"
OUTPUT_DIR="/tmp/forge-triggering-tests/${TIMESTAMP}/${SKILL_NAME}"
mkdir -p "$OUTPUT_DIR"

PROMPT="$(cat "$PROMPT_FILE")"
LOG_FILE="${OUTPUT_DIR}/claude-output.json"

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
printf '=== Forge Skill Triggering Test ===\n'
printf 'Skill:        forge:%s\n' "$SKILL_NAME"
printf 'Prompt file:  %s\n' "$PROMPT_FILE"
printf 'Max turns:    %s\n' "$MAX_TURNS"
printf 'Plugin dir:   %s\n' "$FORGE_PLUGIN_DIR"
printf 'Log:          %s\n' "$LOG_FILE"
printf '\n'

# Preserve prompt for audit trail
cp "$PROMPT_FILE" "${OUTPUT_DIR}/prompt.txt"

# ---------------------------------------------------------------------------
# Run claude
# ---------------------------------------------------------------------------
printf 'Running claude -p (stream-json)...\n'
# `|| true` prevents set -e from aborting on non-zero claude exit; we evaluate
# the log ourselves.
#
# Three portability/correctness requirements, each learned the hard way:
#   1. `--verbose` is REQUIRED for `--print --output-format stream-json` to emit
#      streaming events. Without it the log is empty and every test FAILs.
#   2. GNU `timeout` is absent on stock macOS (so is `gtimeout` unless coreutils
#      is brew-installed). Use whichever exists; if neither, run without an outer
#      timeout — `--max-turns` still bounds the session.
#   3. Run from a throwaway cwd so a "doing" skill (commit / execute-ticket)
#      triggered headless cannot mutate the real working tree. We only need the
#      Skill tool-use event, which fires before the skill acts on anything.
CLAUDE_ARGS=(
    -p "$PROMPT"
    --plugin-dir "$FORGE_PLUGIN_DIR"
    --dangerously-skip-permissions
    --max-turns "$MAX_TURNS"
    --output-format stream-json
    --verbose
)
WORK_DIR="$(mktemp -d)"
if command -v timeout >/dev/null 2>&1; then
    ( cd "$WORK_DIR" && timeout 300 claude "${CLAUDE_ARGS[@]}" ) > "$LOG_FILE" 2>&1 || true
elif command -v gtimeout >/dev/null 2>&1; then
    ( cd "$WORK_DIR" && gtimeout 300 claude "${CLAUDE_ARGS[@]}" ) > "$LOG_FILE" 2>&1 || true
else
    ( cd "$WORK_DIR" && claude "${CLAUDE_ARGS[@]}" ) > "$LOG_FILE" 2>&1 || true
fi
rm -rf "$WORK_DIR"

printf '\n=== Results ===\n'

# ---------------------------------------------------------------------------
# Parse stream-json for Skill tool-use
# ---------------------------------------------------------------------------
# In stream-json output each line is a JSON event. A Skill invocation emits
# an event with:
#   "name": "Skill"          (the tool name)
#   "skill": "forge:<name>"  (the resolved skill identifier)
#
# We check for both independently in case event structure varies by claude version.
#
# SKILL_PATTERN matches:
#   "forge:tdd"           exact namespaced form
# We do NOT match a bare skill name to avoid false positives from assistant text.

EXPECTED_SKILL="forge:${SKILL_NAME}"
SKILL_PATTERN='"forge:'"${SKILL_NAME}"'"'

TRIGGERED=false
if grep -q '"name":"Skill"' "$LOG_FILE" 2>/dev/null && \
   grep -q "$SKILL_PATTERN"  "$LOG_FILE" 2>/dev/null; then
    TRIGGERED=true
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [ "$TRIGGERED" = "true" ]; then
    printf 'PASS: skill "%s" was triggered\n' "$EXPECTED_SKILL"
else
    printf 'FAIL: skill "%s" was NOT triggered\n' "$EXPECTED_SKILL"
    printf '\n'
    printf 'Skills seen in this run:\n'
    grep -o '"skill":"[^"]*"' "$LOG_FILE" 2>/dev/null | sort -u || printf '  (none)\n'
    printf '\n'
    printf 'First assistant text (<=500 chars):\n'
    # jq may not be present; fall back to grep
    if command -v jq >/dev/null 2>&1; then
        grep '"type":"assistant"' "$LOG_FILE" 2>/dev/null | head -1 \
            | jq -r '.message.content[0].text // .message.content // ""' 2>/dev/null \
            | head -c 500 || true
    else
        grep -o '"text":"[^"]*"' "$LOG_FILE" 2>/dev/null | head -1 || printf '  (could not extract)\n'
    fi
    printf '\n'
fi

printf '\nFull log: %s\n' "$LOG_FILE"
printf 'Timestamp: %s\n' "$TIMESTAMP"

if [ "$TRIGGERED" = "true" ]; then
    exit 0
else
    exit 1
fi
