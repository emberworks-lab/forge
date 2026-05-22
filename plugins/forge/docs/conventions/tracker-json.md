# tracker.json — full schema reference

**Status:** Extended by EPIC C+D (#52) Story 1 (#53). Additive to the base contract in `docs/tracker-backends/README.md §3`.

This document describes the **complete** `tracker.json` schema, including the new `structure` and `platforms[]` fields introduced for multi-platform project support.

---

## 1. Full schema

Location: `<project-root>/.claude/tracker.json`

```jsonc
{
  // ── Core (required) ──────────────────────────────────────────────
  "backend": "linear" | "github" | "markdown",

  // ── Project layout (optional; defaults shown) ────────────────────
  "structure": "sub-folder" | "monorepo" | "polyrepo",
  // Default: "sub-folder"
  //   sub-folder  — one or more platforms live in sub-folders of the
  //                 same repo root (e.g. backend/, mobile/).
  //   monorepo    — nx/turborepo/melos style; build tooling manages
  //                 the workspace. Same resolution rules as sub-folder;
  //                 the distinction is advisory for humans and tooling
  //                 that needs to pick a package-manager strategy.
  //   polyrepo    — each platform is its OWN git repo, nested in and
  //                 .gitignore'd by a general/parent repo that owns the
  //                 shared docs/ and the tracker. Same on-disk resolution
  //                 rules as sub-folder; each platforms[] entry carries a
  //                 `repo` field and github.epics_repo = the general repo.
  //                 Experimental.

  "platforms": [
    {
      "name": "<platform identifier>",  // e.g. "backend-nest", "mobile-flutter"
      "path": "<relative path from repo root>",
                                        // "." for single-platform projects
      "repo": "<github repo name>"      // polyrepo only — the platform's own repo
    }
    // ... additional platforms
  ],
  // Default: [{ "name": "<inferred from backend config>", "path": "." }]
  // Skills treat a missing platforms[] as [{ "name": "default", "path": "." }].

  // ── Backend config (conditional on "backend" value) ───────────────
  "linear": { ... },   // see tracker-backends/README.md §3.1
  "github": { ... },
  "markdown": { ... },

  // ── Per-platform only (minimal child tracker.json) ────────────────
  "parent_path": "../"
  // Present ONLY in a per-platform tracker.json nested inside a
  // platform sub-folder. Points to the directory containing the root
  // tracker.json. Slash-terminated. Skills use this to walk up and
  // merge config (see §4 Reader algorithm).
}
```

**Required:** `backend`. All other fields are optional or conditional.

**Single-platform projects** SHOULD include `platforms` with a single entry (`path: "."`) so tooling has a uniform shape to iterate over. Omitting `platforms` is valid; skills default to `[{ "name": "default", "path": "." }]`.

---

## 2. New fields — detail

### 2.1 `structure`

| Value | Meaning |
|---|---|
| `"sub-folder"` | Platforms are sub-folders of the same repo root. No special build tooling required. **Default.** |
| `"monorepo"` | Build tooling (nx, turborepo, melos, etc.) manages the workspace. Skills may use this to pick a package-manager aware command (e.g. `melos run test` vs `flutter test`). |
| `"polyrepo"` | Each platform is its own git repo, nested in and `.gitignore`d by a general/parent repo that owns the shared `docs/` and the tracker. On-disk identical to `sub-folder`; the difference is git topology (separate repos + remotes). `github.epics_repo` = the general repo; each `platforms[]` entry carries its own `repo`. **Experimental** (downstream skills not yet polyrepo-aware — see EPIC L #124). |

**Not used for routing.** `structure` is advisory metadata. The `platforms[]` array drives all actual path resolution.

### 2.2 `platforms[]`

Each entry is an object with two keys:

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Human-readable platform identifier. Used in skill output labels and log messages. |
| `path` | string | yes | Relative path from repo root to the platform's code root. `"."` for single-platform. No trailing slash. |
| `repo` | string | polyrepo only | GitHub repo name for this platform's code. Required when `structure == "polyrepo"`; absent otherwise. Used by `scripts/clone-all.sh` and area routing. |

**Order** is significant: skills that iterate platforms process them in array order (top to bottom). List the primary/orchestrator platform first.

### 2.3 `parent_path`

Present **only** in a per-platform `tracker.json` that lives inside a platform sub-folder. Its value is a relative path (slash-terminated) pointing to the directory that contains the root `tracker.json`.

```json
{
  "backend": "linear",
  "parent_path": "../"
}
```

The per-platform file is intentionally minimal: it carries `backend` (so skills can read it stand-alone) and `parent_path` (so they can merge full config from the root). Any field present in the per-platform file **overrides** the corresponding field in the root.

---

## 3. Worked examples

### 3.1 Single-platform project

A Node.js API, repo root is also the platform root.

**`.claude/tracker.json`**
```json
{
  "backend": "github",
  "github": {
    "org": "emberworks-lab",
    "repo": "pantrypal-api",
    "project_number": 3
  },
  "platforms": [
    { "name": "backend-nest", "path": "." }
  ]
}
```

No `structure` field (defaults to `"sub-folder"`). No `parent_path` (root file).

---

### 3.2 Multi-platform sub-folder layout

A monorepo with a NestJS backend in `backend/` and a Flutter mobile app in `mobile/`. Shared tracker on GitHub Projects v2.

**Root `.claude/tracker.json`**
```json
{
  "backend": "github",
  "structure": "sub-folder",
  "github": {
    "org": "emberworks-lab",
    "repo": "pantrypal",
    "epics_repo": "pantrypal-tracker",
    "project_number": 1
  },
  "platforms": [
    { "name": "backend-nest", "path": "backend" },
    { "name": "mobile-flutter", "path": "mobile" }
  ]
}
```

**`backend/.claude/tracker.json`** *(per-platform, minimal)*
```json
{
  "backend": "github",
  "parent_path": "../"
}
```

**`mobile/.claude/tracker.json`** *(per-platform, minimal)*
```json
{
  "backend": "github",
  "parent_path": "../"
}
```

A skill invoked from within `backend/` reads `backend/.claude/tracker.json`, finds `parent_path: "../"`, walks up to `.claude/tracker.json`, and merges the full config. It then knows:
- Backend: `github` with full `github` config block.
- Platform context: it is `backend-nest` at `backend/`.
- Sibling platforms: `mobile-flutter` at `mobile/`.

---

### 3.3 Multi-platform polyrepo layout

A `petripal` project with a NestJS backend and a Flutter app as **separate
repos**, plus a `petripal-general` repo (the parent folder) holding shared docs
and the tracker.

**General repo `.claude/tracker.json`** *(in the parent folder)*
```json
{
  "backend": "github",
  "structure": "polyrepo",
  "github": {
    "org": "emberworks-lab",
    "repo": "petripal-general",
    "epics_repo": "petripal-general",
    "project_number": 7
  },
  "platforms": [
    { "name": "backend-nest", "path": "backend", "repo": "petripal-backend" },
    { "name": "mobile-flutter", "path": "mobile", "repo": "petripal-mobile" }
  ]
}
```

`backend/` and `mobile/` are independent clones nested in the general repo's
working tree and `.gitignore`d by it. Each carries the same minimal child
`tracker.json` (`{ "backend": "github", "parent_path": "../" }`) as the
sub-folder layout, so the reader algorithm resolves docs + root config
identically. `scripts/clone-all.sh` rebuilds the working tree on a new machine
from `github.org` + `platforms[].repo`.

---

## 4. Reader algorithm

Skills that need tracker config follow this resolution order:

```
function read_tracker_config(cwd):
  local_path  = find(".claude/tracker.json", starting_at=cwd, walk_up=false)
  if local_path exists:
    config = parse(local_path)
    if config has "parent_path":
      parent_config = parse(cwd / config.parent_path / ".claude/tracker.json")
      # Merge: parent is base, local overrides individual keys
      config = deep_merge(base=parent_config, overrides=config)
    return config
  else:
    # No local tracker.json — check repo root directly
    root_path = git_root(cwd) + "/.claude/tracker.json"
    if root_path exists:
      return parse(root_path)
    else:
      return null  # trigger first-use setup flow (see tracker-backends/README.md §7)
```

**Merge semantics:**
- `deep_merge` replaces top-level keys, not nested keys. If the per-platform file sets `"github": { "repo": "mobile-repo" }`, it replaces the entire `github` object in the root.
- `parent_path` is consumed during resolution and **not** included in the merged config returned to the skill.
- `platforms[]` from the root is always preserved in the merged result unless the per-platform file explicitly overrides it.

**Platform identity:** after merging, the skill can determine which platform it is operating in by matching `cwd` against `platforms[].path` entries.

---

## 5. Loader pseudocode (contract for skill implementors)

The following pseudocode defines the full contract. Future skill code that calls `read_tracker_config()` can rely on these guarantees:

```python
# tracker_loader.py  (pseudocode — not a runnable module)

class TrackerConfig:
    backend: str                       # "linear" | "github" | "markdown"
    structure: str                     # "sub-folder" | "monorepo"  (default: "sub-folder")
    platforms: list[Platform]          # always populated (min 1 entry)
    linear: dict | None
    github: dict | None
    markdown: dict | None

class Platform:
    name: str
    path: str                          # relative to repo root

def read_tracker_config(cwd: Path) -> TrackerConfig | None:
    """
    Resolve tracker.json for the given working directory.

    Resolution order:
      1. <cwd>/.claude/tracker.json  (local / per-platform)
         → if has parent_path: merge with parent
      2. <git_root>/.claude/tracker.json  (repo root)
      3. None  (caller should trigger setup_interview)

    Merge rule: local overrides root, key-by-key at top level.
    parent_path is stripped from the returned config.
    platforms[] from root is preserved unless local explicitly overrides.
    """
    ...

def current_platform(config: TrackerConfig, cwd: Path) -> Platform | None:
    """
    Return the Platform entry whose path matches cwd relative to git root.
    Returns None if cwd is the repo root or no match found.
    """
    rel = cwd.relative_to(git_root(cwd))
    for p in config.platforms:
        if Path(p.path) == rel:
            return p
    return None
```

**Guarantees the loader must uphold:**
1. Returned `TrackerConfig` always has `backend` set.
2. `platforms` is never empty; missing field defaults to `[Platform(name="default", path=".")]`.
3. `structure` defaults to `"sub-folder"` when absent.
4. `parent_path` is never present in the returned config (consumed during resolution).
5. Returning `None` is the only signal to trigger first-use setup — the caller must not swallow it.

---

## 6. Relationship to existing schema (tracker-backends/README.md §3)

This document **extends** — not replaces — the schema in `docs/tracker-backends/README.md §3`.

| Field | Defined in |
|---|---|
| `backend` | `tracker-backends/README.md §3.1` |
| `linear`, `github`, `markdown` | `tracker-backends/README.md §3.1–3.3` |
| `structure` | **this document §2.1** |
| `platforms[]` | **this document §2.2** |
| `parent_path` | **this document §2.3** |

The `tracker-backends/README.md` dispatch mechanism (§7) is unchanged. Skills that only use backend operations and don't care about multi-platform layout can continue reading `tracker.json` exactly as before — `structure` and `platforms[]` are additive optional fields.
