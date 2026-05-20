#!/usr/bin/env bash
# scaffold-flutter.sh — Flutter project scaffolder entrypoint.
# FORGE-5.3 (EMB-288). Spec: plugins/forge/docs/tooling/ (tooling docs not migrated - deleted in EPIC E)
# Inventory: plugins/forge/docs/tooling/ (tooling docs not migrated - deleted in EPIC E)
#
# Usage:
#   scaffold-flutter.sh \
#     --answers <path/to/interview_answers.json> \
#     --target  <path/to/new/project> \
#     [--template <path/to/flutter-template>] \
#     [--dry-run] \
#     [--validate]
#
# This is a thin shell wrapper. The substitution / file-tree / generation logic
# lives in the sibling Python helper `_scaffold_flutter.py`. Bash here only:
#   1. Resolves the template source via template-source.json (mirror or git-cached).
#   2. Validates inputs minimally.
#   3. Hands off to the Python engine.
#   4. Optionally invokes `flutter pub get` + `flutter analyze` for sanity check.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PIN_FILE="${PLUGIN_DIR}/skill-templates/mobile-flutter/template-source.json"
PY_HELPER="${SCRIPT_DIR}/_scaffold_flutter.py"

# ---------- arg parsing ----------
ANSWERS=""
TARGET=""
TEMPLATE=""
DRY_RUN=0
VALIDATE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --answers)  ANSWERS="$2"; shift 2 ;;
    --target)   TARGET="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=1; shift ;;
    --validate) VALIDATE=1; shift ;;
    -h|--help)
      sed -n '2,20p' "$0"
      exit 0
      ;;
    *)
      echo "scaffold-flutter: unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$ANSWERS" || -z "$TARGET" ]]; then
  echo "scaffold-flutter: --answers and --target are required" >&2
  exit 2
fi

if [[ ! -f "$ANSWERS" ]]; then
  echo "scaffold-flutter: answers file not found: $ANSWERS" >&2
  exit 2
fi

# ---------- resolve template source ----------
if [[ -z "$TEMPLATE" ]]; then
  if [[ ! -f "$PIN_FILE" ]]; then
    echo "scaffold-flutter: pin file missing: $PIN_FILE" >&2
    exit 3
  fi
  # Prefer the local mirror path from the pin file. Tilde-expand.
  MIRROR="$(python3 -c "
import json, os, sys
with open(os.path.expanduser('$PIN_FILE')) as f:
    d = json.load(f)
print(os.path.expanduser(d['template']['local_mirror']))
")"
  if [[ -d "$MIRROR" ]]; then
    TEMPLATE="$MIRROR"
  else
    echo "scaffold-flutter: local mirror not found at $MIRROR" >&2
    echo "scaffold-flutter: clone the template manually first:" >&2
    echo "  git clone https://github.com/emberworks-lab/flutter-template $MIRROR" >&2
    exit 3
  fi
fi

if [[ ! -d "$TEMPLATE" ]]; then
  echo "scaffold-flutter: template dir not found: $TEMPLATE" >&2
  exit 3
fi
if [[ ! -f "$TEMPLATE/pubspec.yaml" ]]; then
  echo "scaffold-flutter: template dir does not look like a Flutter package: $TEMPLATE" >&2
  exit 3
fi

# ---------- locate python helper ----------
if [[ ! -f "$PY_HELPER" ]]; then
  echo "scaffold-flutter: python helper missing: $PY_HELPER" >&2
  exit 3
fi

# ---------- delegate to Python engine ----------
PY_ARGS=(
  --answers "$ANSWERS"
  --target  "$TARGET"
  --template "$TEMPLATE"
  --pin     "$PIN_FILE"
)
if [[ $DRY_RUN -eq 1 ]]; then PY_ARGS+=( --dry-run ); fi

python3 "$PY_HELPER" "${PY_ARGS[@]}"
PY_EXIT=$?
if [[ $PY_EXIT -ne 0 ]]; then
  echo "scaffold-flutter: python helper failed (exit $PY_EXIT)" >&2
  exit $PY_EXIT
fi

# ---------- optional: validate generated project ----------
# The Python helper now runs `flutter create` as step 0 (EMB-314), which itself
# triggers a pub get against the SDK-generated pubspec.yaml. Our overlay then
# REPLACES pubspec.yaml with the composed-deps version, so a final pub get is
# required to fetch the overlay's deps. Keep this AFTER the helper to avoid
# clashing with flutter-create's implicit pub get.
if [[ $VALIDATE -eq 1 && $DRY_RUN -eq 0 ]]; then
  if ! command -v flutter >/dev/null 2>&1; then
    echo "scaffold-flutter: --validate requested but flutter CLI not in PATH; skipping" >&2
  else
    echo "scaffold-flutter: running flutter pub get in $TARGET (overlay pubspec)"
    ( cd "$TARGET" && flutter pub get )
    echo "scaffold-flutter: running flutter analyze in $TARGET"
    ( cd "$TARGET" && flutter analyze ) || echo "scaffold-flutter: analyze reported issues (non-fatal at scaffold time)" >&2
  fi
fi

echo "scaffold-flutter: done"
