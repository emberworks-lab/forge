#!/usr/bin/env bash
# clone-all.sh — clone every platform repo of a polyrepo project.
#
# Manifest is the project's own .claude/tracker.json (no separate file):
#   github.org           — the GitHub owner
#   platforms[].path     — where each platform lives, relative to this repo
#   platforms[].repo     — the GitHub repo name for that platform
#
# Run from the general/parent repo root after `gh repo clone <org>/<general>`.
# Requires: gh (authenticated), jq.
set -euo pipefail

cd "$(dirname "$0")/.."
cfg=".claude/tracker.json"

[ -f "$cfg" ] || { echo "error: $cfg not found — run from the general repo root" >&2; exit 1; }
command -v gh >/dev/null || { echo "error: gh not found — https://cli.github.com/" >&2; exit 1; }
command -v jq >/dev/null || { echo "error: jq not found" >&2; exit 1; }

org=$(jq -r '.github.org // empty' "$cfg")
[ -n "$org" ] || { echo "error: github.org missing in $cfg" >&2; exit 1; }

jq -r '.platforms[]? | select(.repo) | "\(.path)\t\(.repo)"' "$cfg" |
while IFS=$'\t' read -r path repo; do
  if [ -d "$path/.git" ]; then
    echo "skip  $path (already a git repo)"
    continue
  fi
  echo "clone $org/$repo -> $path"
  gh repo clone "$org/$repo" "$path"
done

echo "done."
