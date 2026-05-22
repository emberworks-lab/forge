#!/usr/bin/env bash
# run-all.sh — Structural test tier: run audit.sh over every SKILL.md in the forge plugin.
#
# Usage:   bash plugins/forge/tests/structural/run-all.sh
# Exit:    0 = all skills pass, 1 = one or more skills failed, 2 = setup error.
#
# Discovery: plugins/forge/skills/*/SKILL.md (exactly one glob level deep).
# Audit:     plugins/forge/skills/writing-skill/scripts/audit.sh

set -u

# Resolve script location so the script is runnable from any working directory.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

SKILLS_DIR="${REPO_ROOT}/plugins/forge/skills"
AUDIT_SH="${SKILLS_DIR}/writing-skill/scripts/audit.sh"

# Verify prerequisites.
if [ ! -f "$AUDIT_SH" ]; then
  printf 'ERROR: audit.sh not found at %s\n' "$AUDIT_SH" >&2
  exit 2
fi

if [ ! -d "$SKILLS_DIR" ]; then
  printf 'ERROR: skills directory not found at %s\n' "$SKILLS_DIR" >&2
  exit 2
fi

# Collect all SKILL.md files (one level deep only).
skills=()
while IFS= read -r skill_file; do
  skills+=("$skill_file")
done < <(find "$SKILLS_DIR" -mindepth 2 -maxdepth 2 -name 'SKILL.md' | sort)

total=${#skills[@]}
if [ "$total" -eq 0 ]; then
  printf 'ERROR: no SKILL.md files found under %s\n' "$SKILLS_DIR" >&2
  exit 2
fi

pass=0
fail=0

for skill_file in "${skills[@]}"; do
  # Derive a short label: the skill directory name.
  skill_name="$(basename "$(dirname "$skill_file")")"

  # Run audit.sh; capture stderr (violations); suppress stdout.
  if bash "$AUDIT_SH" "$skill_file" 2>/dev/null; then
    printf 'PASS  %s\n' "$skill_name"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s\n' "$skill_name"
    # Re-run to surface violation details for the reader.
    bash "$AUDIT_SH" "$skill_file" 2>&1 >/dev/null | sed 's/^/      /'
    fail=$((fail + 1))
  fi
done

printf '\n--- Summary: %d passed, %d failed, %d total ---\n' "$pass" "$fail" "$total"

if [ "$fail" -gt 0 ]; then
  exit 1
fi

exit 0
