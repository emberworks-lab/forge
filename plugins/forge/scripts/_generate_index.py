#!/usr/bin/env python3
"""Generate INDEX.md from frontmatter of plugins/forge/{skills,agents}/*.md"""

import re
import sys
from datetime import date
from pathlib import Path
from collections import defaultdict

# Hardcoded category map — avoids requiring category: in every SKILL.md.
# Key: skill/agent name, Value: category label.
CATEGORY_MAP = {
    # tracker pipeline
    "commit": "tracker pipeline",
    "create-epic": "tracker pipeline",
    "create-ticket": "tracker pipeline",
    "execute-epic": "tracker pipeline",
    "execute-ticket": "tracker pipeline",
    "epic-close": "tracker pipeline",
    "pr-create": "tracker pipeline",
    # planning
    "brainstorm": "planning",
    "diagnose": "planning",
    "grill-me": "planning",
    "grill-with-docs": "planning",
    "prototype": "planning",
    "zoom-out": "planning",
    # review
    "handle-review-feedback": "review",
    "simplify": "review",
    "simplify-branch": "review",
    # debugging
    "diagnose-deep": "debugging",
    "tdd": "debugging",
    # project init + flutter
    "dart-collect-coverage": "flutter + project init",
    "dart-fix-runtime-errors": "flutter + project init",
    "flutter-fix-layout-issues": "flutter + project init",
    "project-init": "flutter + project init",
    # meta
    "caveman": "meta",
    "handoff": "meta",
    "hello": "meta",
    "writing-skill": "meta",
    # agents
    "linter-runner": "runner agents",
    "test-runner": "runner agents",
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    out = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()

            # Handle YAML block scalars: > (folded) or | (literal)
            if v in (">", "|"):
                scalar_lines = []
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                    scalar_lines.append(lines[i].strip())
                    i += 1
                # Folded (>) joins with spaces; literal (|) joins with newlines
                if v == ">":
                    out[k] = " ".join(scalar_lines)
                else:
                    out[k] = "\n".join(scalar_lines)
                continue
            else:
                # Strip surrounding quotes if present
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                out[k] = v
        i += 1
    return out


def collect(dir_path: Path) -> list:
    items = []
    if not dir_path.exists():
        return items
    # Support both flat *.md (agents) and subdirectory */SKILL.md (skills) layouts
    candidates = sorted(dir_path.glob("*.md")) + sorted(dir_path.glob("*/SKILL.md"))
    seen = set()
    for md in candidates:
        if md in seen:
            continue
        seen.add(md)
        # skip README / index / docs by name
        if md.name.lower() in {"readme.md", "index.md"}:
            continue
        fm = parse_frontmatter(md.read_text())
        # fallback to parent dir name for SKILL.md, else stem
        default_name = md.parent.name if md.name == "SKILL.md" else md.stem
        name = fm.get("name", "").strip() or default_name
        # Category: prefer frontmatter, then hardcoded map, then "uncategorized"
        category = fm.get("category", "").strip() or CATEGORY_MAP.get(name, "uncategorized")
        items.append({
            "name": name,
            "description": fm.get("description", "").strip() or "(no description)",
            "category": category,
            "path": str(md),
        })
    return items


def render_section(heading: str, items_by_cat: dict, prefix: str = "") -> str:
    out = [f"## {heading}\n"]
    # alphabetize categories, but put 'uncategorized' last
    cats = sorted(items_by_cat.keys(), key=lambda c: (c == "uncategorized", c))
    for cat in cats:
        out.append(f"### {cat}\n")
        for it in sorted(items_by_cat[cat], key=lambda i: i["name"]):
            out.append(f"- `{prefix}{it['name']}` — {it['description']}")
        out.append("")
    return "\n".join(out)


def main(commands_dir: str, agents_dir: str) -> int:
    cmd_items = collect(Path(commands_dir))
    agent_items = collect(Path(agents_dir))

    cmd_by_cat = defaultdict(list)
    for it in cmd_items:
        cmd_by_cat[it["category"]].append(it)
    agent_by_cat = defaultdict(list)
    for it in agent_items:
        agent_by_cat[it["category"]].append(it)

    today = date.today().isoformat()
    sys.stdout.write(f"# Skills & Agents Index (auto-generated)\n\nLast regenerated: {today}\n\n")
    sys.stdout.write("> This file is generated by `plugins/forge/scripts/generate-index.sh`. Do not edit manually.\n")
    sys.stdout.write("> To regenerate: `plugins/forge/scripts/generate-index.sh`\n\n")

    sys.stdout.write(render_section("Skills (slash commands)", cmd_by_cat, prefix="/"))
    sys.stdout.write("\n")
    sys.stdout.write(render_section("Agents (Task subagents)", agent_by_cat, prefix=""))

    # Warnings to stderr if any uncategorized
    uncats = [it for it in cmd_items + agent_items if it["category"] == "uncategorized"]
    if uncats:
        sys.stderr.write(f"WARN: {len(uncats)} files missing category:\n")
        for it in uncats:
            sys.stderr.write(f"  - {it['path']}\n")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: _generate_index.py <commands_dir> <agents_dir>\n")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
