#!/usr/bin/env bash
# promote-permissions.sh — promote stable per-machine permissions from local to global.
#
# Usage:
#   promote-permissions.sh [--dry-run]
#
# Dry-run: prints diff entries without prompting or writing anything.
# Interactive: prompts y/n/skip-all/quit per diff entry.

set -euo pipefail

GLOBAL_SETTINGS="$HOME/.claude/settings.json"
LOCAL_SETTINGS="$HOME/.claude/settings.local.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_HELPER="$SCRIPT_DIR/_promote_permissions.py"

if [[ ! -f "$LOCAL_SETTINGS" ]]; then
  echo "Error: $LOCAL_SETTINGS does not exist. Nothing to promote." >&2
  exit 1
fi

if [[ ! -f "$GLOBAL_SETTINGS" ]]; then
  echo "Error: $GLOBAL_SETTINGS does not exist." >&2
  exit 1
fi

if [[ ! -f "$PYTHON_HELPER" ]]; then
  echo "Error: Python helper not found at $PYTHON_HELPER" >&2
  exit 1
fi

exec /usr/bin/env python3 "$PYTHON_HELPER" "$GLOBAL_SETTINGS" "$LOCAL_SETTINGS" "$@"
