#!/usr/bin/env bash
# pull-all.sh — git pull the general repo and every platform repo of a polyrepo.
#
# Reads the project's .claude/tracker.json (platforms[].path) as the manifest.
# Run from the general/parent repo root. Requires: jq.
set -euo pipefail

cd "$(dirname "$0")/.."
cfg=".claude/tracker.json"

[ -f "$cfg" ] || { echo "error: $cfg not found — run from the general repo root" >&2; exit 1; }
command -v jq >/dev/null || { echo "error: jq not found" >&2; exit 1; }

echo "pull  . (general)"
git pull --ff-only || echo "  warn: general repo pull failed (resolve manually)"

jq -r '.platforms[]? | .path' "$cfg" |
while read -r path; do
  if [ -d "$path/.git" ]; then
    echo "pull  $path"
    git -C "$path" pull --ff-only || echo "  warn: $path pull failed (resolve manually)"
  else
    echo "skip  $path (not cloned — run clone-all.sh)"
  fi
done

echo "done."
