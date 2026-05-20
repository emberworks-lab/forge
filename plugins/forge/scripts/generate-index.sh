#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PLUGIN_DIR}/../.." && pwd)"
INDEX="${REPO_ROOT}/docs/SKILL-INDEX.md"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found in PATH" >&2
    exit 1
fi

mkdir -p "$(dirname "${INDEX}")"

python3 "${SCRIPT_DIR}/_generate_index.py" "${PLUGIN_DIR}/skills" "${PLUGIN_DIR}/agents" > "${INDEX}"
echo "Generated: ${INDEX}"
