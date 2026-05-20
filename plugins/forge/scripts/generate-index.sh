#!/usr/bin/env bash
set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
INDEX="${CLAUDE_DIR}/INDEX.md"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found in PATH" >&2
    exit 1
fi

python3 "${SCRIPT_DIR}/_generate_index.py" "${CLAUDE_DIR}/commands" "${CLAUDE_DIR}/agents" > "${INDEX}"
echo "Generated: ${INDEX}"
