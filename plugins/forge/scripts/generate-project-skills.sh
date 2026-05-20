#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <stack> <output-path>" >&2
    echo "Example: $0 mobile-flutter ./project/.claude/SKILLS.md" >&2
    exit 1
fi

STACK="$1"
OUTPUT="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found in PATH" >&2
    exit 1
fi

mkdir -p "$(dirname "${OUTPUT}")"
python3 "${SCRIPT_DIR}/_generate_project_skills.py" "${STACK}" > "${OUTPUT}"
echo "Generated: ${OUTPUT}"
