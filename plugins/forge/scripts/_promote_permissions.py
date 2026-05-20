#!/usr/bin/env python3
"""
_promote_permissions.py — promote stable permissions from local to global settings.

Usage:
    python3 _promote_permissions.py <global_path> <local_path> [--dry-run]

In dry-run mode: prints diff entries only, no prompts, no writes.
Interactive mode: prompts y/n/skip-all/quit per diff entry.

Rules:
- NEVER deletes entries from global; only adds.
- Creates backups (<path>.bak.<unix-timestamp>) before any write.
- Validates JSON after edit before writing.
- Handles missing `permissions` key gracefully (treated as empty).
"""

import json
import os
import sys
import time
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_indent(path: str) -> int:
    """Detect the indentation level used in the JSON file (default 2)."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.lstrip()
            if stripped and line != stripped:
                return len(line) - len(stripped)
    return 2


def save_json(path: str, data: dict, indent: int) -> None:
    serialized = json.dumps(data, indent=indent, ensure_ascii=False)
    # Validate round-trip
    json.loads(serialized)
    with open(path, "w", encoding="utf-8") as f:
        f.write(serialized)
        f.write("\n")


def backup(path: str, ts: int) -> str:
    backup_path = f"{path}.bak.{ts}"
    with open(path, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    return backup_path


def compute_diff(global_data: dict, local_data: dict) -> dict:
    """
    Returns entries present in local permissions but absent in global, per sub-key.
    Only considers `allow` and `deny`.
    """
    diff = {}
    global_perms = global_data.get("permissions", {})
    local_perms = local_data.get("permissions", {})

    for key in ("allow", "deny"):
        global_entries = set(global_perms.get(key, []))
        local_entries = local_perms.get(key, [])
        missing = [e for e in local_entries if e not in global_entries]
        if missing:
            diff[key] = missing

    return diff


def main() -> int:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    positional = [a for a in args if not a.startswith("--")]

    if len(positional) < 2:
        print(f"Usage: {sys.argv[0]} <global_path> <local_path> [--dry-run]", file=sys.stderr)
        return 1

    global_path, local_path = positional[0], positional[1]

    if not os.path.exists(local_path):
        print(f"Error: local settings not found: {local_path}", file=sys.stderr)
        return 1

    if not os.path.exists(global_path):
        print(f"Error: global settings not found: {global_path}", file=sys.stderr)
        return 1

    global_data = load_json(global_path)
    local_data = load_json(local_path)

    diff = compute_diff(global_data, local_data)

    if not diff:
        print("No permissions to promote. Local and global are in sync.")
        return 0

    total_diff = sum(len(v) for v in diff.values())

    if dry_run:
        print(f"Dry-run: {total_diff} permission(s) in local not present in global:")
        for key, entries in diff.items():
            for entry in entries:
                print(f"  [{key}] {entry}")
        return 0

    # Interactive mode — take backups first
    ts = int(time.time())
    global_indent = detect_indent(global_path)
    local_indent = detect_indent(local_path)

    global_backup = backup(global_path, ts)
    local_backup = backup(local_path, ts)

    promoted = []
    left_local = []
    aborted = False

    # Work on mutable copies
    working_global = load_json(global_path)
    working_local = load_json(local_path)

    try:
        for key, entries in diff.items():
            for entry in entries:
                answer = input(f"Promote `{entry}` from local [{key}] → global? [y/n/skip-all/quit]: ").strip().lower()
                if answer == "y":
                    # Ensure the key exists in global permissions
                    if "permissions" not in working_global:
                        working_global["permissions"] = {}
                    if key not in working_global["permissions"]:
                        working_global["permissions"][key] = []
                    working_global["permissions"][key].append(entry)
                    # Remove from local
                    working_local["permissions"][key].remove(entry)
                    # Clean up empty list (keep key but empty list is fine)
                    promoted.append(f"[{key}] {entry}")
                elif answer == "n":
                    left_local.append(f"[{key}] {entry}")
                elif answer in ("skip-all", "quit"):
                    left_local.append(f"[{key}] {entry}")
                    # Mark remaining as left
                    remaining_idx = entries.index(entry) + 1
                    left_local.extend(f"[{key}] {e}" for e in entries[remaining_idx:])
                    aborted = True
                    break
                else:
                    print(f"Unrecognised input '{answer}', treating as 'n'.")
                    left_local.append(f"[{key}] {entry}")
            if aborted:
                break

        # Write changes
        save_json(global_path, working_global, global_indent)
        save_json(local_path, working_local, local_indent)

    except Exception as exc:
        print(f"\nError during write: {exc}", file=sys.stderr)
        print(f"Restoring from backups: {global_backup}, {local_backup}", file=sys.stderr)
        try:
            import shutil
            shutil.copy2(global_backup, global_path)
            shutil.copy2(local_backup, local_path)
            print("Restored successfully.")
        except Exception as restore_exc:
            print(f"Restore failed: {restore_exc}", file=sys.stderr)
        return 1

    print(f"\nPromoted {len(promoted)} permission(s) to global. Left {len(left_local)} as local-only.")
    print(f"Backups: {global_backup}, {local_backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
