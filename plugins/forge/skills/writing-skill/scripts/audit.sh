#!/usr/bin/env bash
# audit.sh — verify a SKILL.md against forge:writing-skill rules.
#
# Usage:   bash audit.sh <path/to/SKILL.md>
# Exit:    0 = clean, 1 = violations (printed to stderr), 2 = usage error.
#
# Checks (mirrors references/slim-audit-checklist.md):
#   1. Front-matter present (between '---' fences at top).
#   2. Front-matter has 'name', 'description', 'type' fields.
#   3. 'type' value is one of: minimal | fundamental | hybrid.
#   4. Line count respects type cap:
#        minimal     <=  80
#        hybrid      <= 120
#        fundamental <= 300   (SKILL.md only; references/ uncapped)
#   5. If 'inspired-by:' present, each entry has author, repo, skill, relation,
#      and 'relation' is one of: adapted | concept | structure.
#   6. No 'superpowers:*' references anywhere in the body.
#   7. If body mentions the word 'subagent' it MUST also name a model
#      ('sonnet' or 'opus'); body MUST NOT mention 'haiku' as a model.
#      ('haiku' inside backticks is allowed — that's referring to the rule,
#      not declaring use.)
#   8. Every 'references/<file>.md' mentioned in the body resolves to a real
#      file relative to SKILL.md.
#   9. No empty sections (a '## Heading' line directly followed by another
#      '## Heading' or by EOF, ignoring blank lines).
#
# Portable: POSIX bash + awk + grep + sed. No GNU-specific flags.

set -u

if [ $# -ne 1 ]; then
  printf 'usage: %s <path/to/SKILL.md>\n' "$0" >&2
  exit 2
fi

file=$1
if [ ! -f "$file" ]; then
  printf 'audit: file not found: %s\n' "$file" >&2
  exit 2
fi

# Counter lives in a tmp file so subshell pipelines can increment it.
v_file="${TMPDIR:-/tmp}/.audit.$$.violations"
: > "$v_file"
trap 'rm -f "$v_file" "${TMPDIR:-/tmp}/.audit.$$.ib" "${TMPDIR:-/tmp}/.audit.$$.v8"' EXIT
report() {
  printf 'VIOLATION [%s] %s\n' "$1" "$2" >&2
  echo x >> "$v_file"
}

# --- Extract front-matter block (between the first two '---' fences) ---
fm=$(awk 'BEGIN{fence=0}
  /^---[[:space:]]*$/ {
    fence++;
    if (fence == 1) next;
    if (fence == 2) exit;
  }
  fence == 1 { print }
' "$file")

# Check 1: front-matter present
fence_count=$(grep -c '^---[[:space:]]*$' "$file" || true)
if [ "$fence_count" -lt 2 ]; then
  report 1 "front-matter block missing or unterminated (need two '---' fences)"
  # Without front-matter, downstream front-matter checks are meaningless.
  fm=""
fi

# Check 2: required fields
for field in name description type; do
  if [ -n "$fm" ] && ! printf '%s\n' "$fm" | grep -Eq "^${field}:[[:space:]]+.+"; then
    report 2 "front-matter missing required field: ${field}"
  fi
done

# Check 3: type value
type_val=$(printf '%s\n' "$fm" | awk -F': *' '/^type:/ {print $2; exit}' | tr -d '[:space:]')
case "$type_val" in
  minimal|fundamental|hybrid) : ;;
  "") [ -n "$fm" ] && report 3 "type field missing or empty" ;;
  *) report 3 "type must be one of minimal|fundamental|hybrid (got: ${type_val})" ;;
esac

# Check 4: line count cap
total_lines=$(awk 'END{print NR}' "$file")
case "$type_val" in
  minimal)     cap=80 ;;
  hybrid)      cap=120 ;;
  fundamental) cap=300 ;;
  *)           cap=0 ;;
esac
if [ "$cap" -gt 0 ] && [ "$total_lines" -gt "$cap" ]; then
  report 4 "line count ${total_lines} exceeds cap ${cap} for type ${type_val}"
fi

# Check 5: inspired-by structure (if present)
if printf '%s\n' "$fm" | grep -q '^inspired-by:'; then
  # Extract the inspired-by block: lines under 'inspired-by:' until next top-level key.
  ib=$(printf '%s\n' "$fm" | awk '
    /^inspired-by:/ {flag=1; next}
    /^[A-Za-z]/ && flag {flag=0}
    flag {print}
  ')
  # Use a tmp file to collect problems (avoids subshell counter issues).
  ib_tmp="${TMPDIR:-/tmp}/.audit.$$.ib"
  : > "$ib_tmp"
  # Parse entries: each entry starts with a line matching '- key:'; the entry's
  # block extends to (but not including) the next such line.
  printf '%s\n' "$ib" | awk -v out="$ib_tmp" '
    function flush() {
      if (entry_started) {
        need_author = !seen_author;
        need_repo   = !seen_repo;
        need_skill  = !seen_skill;
        need_relation = !seen_relation;
        missing = "";
        if (need_author)   missing = missing " author";
        if (need_repo)     missing = missing " repo";
        if (need_skill)    missing = missing " skill";
        if (need_relation) missing = missing " relation";
        if (missing != "") print "MISSING:" missing >> out;
        if (seen_relation && relation_val != "adapted" && relation_val != "concept" && relation_val != "structure") {
          print "BADREL:" relation_val >> out;
        }
      }
      entry_started = 0;
      seen_author = seen_repo = seen_skill = seen_relation = 0;
      relation_val = "";
    }
    /^[[:space:]]*-[[:space:]]/ {
      flush();
      entry_started = 1;
      line = $0;
      # Strip leading "- " and any whitespace
      sub(/^[[:space:]]*-[[:space:]]*/, "", line);
      handle_kv(line);
      next;
    }
    /^[[:space:]]+[A-Za-z_-]+:/ {
      if (entry_started) {
        line = $0;
        sub(/^[[:space:]]+/, "", line);
        handle_kv(line);
      }
      next;
    }
    END { flush() }
    function handle_kv(s,   key, val) {
      if (match(s, /^[A-Za-z_-]+:/)) {
        key = substr(s, 1, RLENGTH - 1);
        val = substr(s, RLENGTH + 1);
        sub(/^[[:space:]]*/, "", val);
        sub(/[[:space:]]*$/, "", val);
        if (key == "author")   { seen_author = 1 }
        if (key == "repo")     { seen_repo = 1 }
        if (key == "skill")    { seen_skill = 1 }
        if (key == "relation") { seen_relation = 1; relation_val = val }
      }
    }
  '
  if [ ! -s "$ib_tmp" ]; then
    # Also catch the case where the block is empty (no entries at all).
    entry_count=$(printf '%s\n' "$ib" | grep -c '^[[:space:]]*-[[:space:]]')
    if [ "$entry_count" -eq 0 ]; then
      report 5 "inspired-by declared but contains no entries"
    fi
  fi
  while IFS= read -r problem; do
    case "$problem" in
      MISSING:*) report 5 "inspired-by entry missing required field(s):${problem#MISSING:}" ;;
      BADREL:*)  report 5 "inspired-by relation must be adapted|concept|structure (got: ${problem#BADREL:})" ;;
    esac
  done < "$ib_tmp"
  rm -f "$ib_tmp"
fi

# Body = everything after the closing front-matter fence.
body=$(awk 'BEGIN{fence=0}
  /^---[[:space:]]*$/ { fence++; next }
  fence >= 2 { print }
' "$file")
# If no front-matter, audit the whole file as body.
if [ -z "$fm" ]; then
  body=$(cat "$file")
fi

# Check 6: no superpowers:* references in body
if printf '%s\n' "$body" | grep -Eq 'superpowers:[A-Za-z0-9_-]+'; then
  offenders=$(printf '%s\n' "$body" | grep -E 'superpowers:[A-Za-z0-9_-]+' | head -3 | tr '\n' '|')
  report 6 "forbidden superpowers:* reference(s) in body: ${offenders%|}"
fi

# Check 7: subagent model rule
if printf '%s\n' "$body" | grep -qi 'subagent'; then
  if ! printf '%s\n' "$body" | grep -Eqi '\b(sonnet|opus)\b'; then
    report 7 "body mentions 'subagent' but does not name a model (sonnet|opus)"
  fi
fi
# haiku must never appear as a model name in this plugin.
# Allow occurrences inside backticks (`haiku`) — those are referring to the
# rule itself (e.g. in writing-skill or its reference docs), not declaring use.
haiku_body=$(printf '%s\n' "$body" | sed -E 's/`[^`]*`/ /g')
if printf '%s\n' "$haiku_body" | grep -Eqi '\bhaiku\b'; then
  report 7 "body mentions 'haiku' outside backticks — not used as a subagent model in this plugin"
fi

# Check 8: references/<file>.md links resolve
skill_dir=$(dirname "$file")
# Match references/<name>.md anywhere in body.
printf '%s\n' "$body" | grep -Eo 'references/[A-Za-z0-9_.-]+\.md' | sort -u | while IFS= read -r ref; do
  [ -z "$ref" ] && continue
  if [ ! -f "${skill_dir}/${ref}" ]; then
    report 8 "dangling reference: ${ref} (resolved as ${skill_dir}/${ref})"
  fi
done

# Check 9: empty sections (## Heading followed by another ## or EOF, skipping blank lines)
empties=$(printf '%s\n' "$body" | awk '
  /^##[[:space:]]/ {
    if (pending != "") {
      print pending;
    }
    pending = $0;
    next;
  }
  /^[^[:space:]]/ { pending = "" }
  END { if (pending != "") print pending }
')
if [ -n "$empties" ]; then
  printf '%s\n' "$empties" | while IFS= read -r heading; do
    [ -z "$heading" ] && continue
    report 9 "empty section: ${heading}"
  done
fi

violations=$(wc -l < "$v_file" | tr -d ' ')
if [ "$violations" -gt 0 ]; then
  printf '\naudit: %d violation(s) in %s\n' "$violations" "$file" >&2
  exit 1
fi

exit 0
