#!/usr/bin/env python3
"""Flutter project scaffolder engine — core logic for scaffold-flutter.sh.

FORGE-5.3 (EMB-288). Spec: plugins/forge/docs/tooling/ (tooling docs not migrated - deleted in EPIC E)
Inventory: plugins/forge/docs/tooling/ (tooling docs not migrated - deleted in EPIC E)

Reads interview answers JSON + base flutter-template, produces a new project
directory with substitutions applied, irrelevant code removed, CLAUDE.md /
.env files / kit-* skills generated.

Invoked by scaffold-flutter.sh — not intended for direct use, but works
standalone if you supply --template explicitly.

The "answers" JSON shape follows the question IDs in
flutter-scaffolder-interview.md (Q1.1, Q1.2, …). See ANSWER_SCHEMA below for
the canonical keys.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# Answer schema (documentation only — Python is duck-typed for this).
# Generator caller passes a dict matching these keys.
# ----------------------------------------------------------------------------
ANSWER_SCHEMA = {
    # Phase 1 — project identity
    "Q1_1_layout": "inline | local_package",  # default: inline
    "Q1_2_name": "free text -> snake_cased",
    "Q1_3_bundle_id": "free text e.g. com.embergard.app",
    "Q1_4_description": "free text (optional)",
    # Phase 2 — platform constraints
    "Q2_1_android_min_sdk": "24 | 26 | 28 | 30 | 33",
    "Q2_2_ios_min_version": "14.0 | 15.0 | 16.0 | 17.0",
    # Phase 3 — core architecture
    "Q3_1_state_mgmt": "bloc | riverpod | provider",
    "Q3_2_di": "get_it | get_it_injectable | none",
    "Q3_3_navigation": "go_router | auto_route",
    # Phase 4 — data layer
    "Q4_1_backend": "supabase | firebase | custom_rest | none",
    "Q4_2_http_client": "dio | http | none",
    "Q4_3_persistence": "drift | hive_ce | shared_prefs | none",
    "Q4_4_secure_storage": "yes | no",
    "Q4_5_websockets": "yes | no",
    # Phase 5 — auth
    "Q5_1_auth": "supabase_auth | firebase_auth | custom_rest_auth | "
                 "oauth_google | oauth_apple | oidc_sso | none",
    "Q5_2_oidc_idp": "free text (only if Q5_1=oidc_sso)",
    # Phase 6 — user-facing
    "Q6_1_theme": "material3 | material2 | cupertino",
    # Q6_2 channels (EMB-320): defaults | file | figma | brainstorm.
    # - "defaults": no overrides, keep flutter-template's base tokens.
    # - "file":     parse a tokens file (md|css|html|json) at `Q6_2_source`.
    # - "figma":    consume a pre-resolved IR dict at `Q6_2_tokens` (collected by
    #               the interview agent via mcp__plugin_figma_figma__get_variable_defs).
    # - "brainstorm": consume a pre-resolved IR dict at `Q6_2_tokens` (collected
    #               by the interview agent via superpowers:brainstorming).
    "Q6_2_theme_tokens": "defaults | file | figma | brainstorm",
    "Q6_2_source": "file path (only if Q6_2_theme_tokens=file)",
    "Q6_2_tokens": (
        "pre-resolved IR dict — see THEME_TOKEN_IR_SHAPE below "
        "(only if Q6_2_theme_tokens in {figma, brainstorm})"
    ),
    "Q6_3_l10n": "no | en | en_uk",
    "Q6_4_animations": "none | lottie | rive | both",
    "Q6_5_game": "none | flame",
    # Phase 7 — operations
    "Q7_1_error_tracking": "crashlytics_sentry | crashlytics | sentry | none",
    "Q7_2_analytics": "none | firebase | mixpanel | amplitude | posthog",
    "Q7_3_push": "none | fcm | onesignal",
    # Phase 8 — build & dev
    "Q8_1_environments": "dev | dev_prod | dev_staging_prod",
    "Q8_2_ide": "both | vscode | idea | none",
    "Q8_3_testing": "bloc_test_mocktail | flutter_test_only",
    "Q8_4_linting": "very_good_analysis | flutter_lints | embergard_custom",
    # Q8.5 — Fastlane (EMB-321). Defaults to "no". When "yes", scaffolder:
    #   - copies kit-add-fastlane.md into <project>/.claude/skills/
    #   - generates flutter_launcher_icons-<flavor>.yaml per flavor
    #   - adds flutter_launcher_icons dev_dependency to pubspec.yaml
    #   - emits a Mode M ticket "Set up Fastlane lanes for <project>"
    # Actual lane execution is deferred to FORGE-6.
    "Q8_5_fastlane": "yes | no",
    # Phase 9 — Workflow / task tracker (EMB-324).
    # Q9.1 — Which task tracker does this project use?
    # Options: linear (default) | github_projects | jira | other
    # Sub-fields populated per choice:
    #   linear:          Q9_workspace (Linear workspace name)
    #   github_projects: Q9_workspace (org/repo), Q9_project (project number/name)
    #   jira:            Q9_workspace (Jira host, e.g. myorg.atlassian.net),
    #                    Q9_project   (project key, e.g. PROJ)
    #   other:           Q9_workspace (free-text URL or description)
    # Skills currently DO NOT read tracker.json — FORGE-8 will add that.
    "Q9_1_tracker": "linear | github_projects | jira | other",
    "Q9_workspace": "workspace name / URL / org — depends on Q9_1_tracker",
    "Q9_project": "project name or ID (Linear / GitHub Projects / Jira only)",
    # Identity
    "linear_prefix": "EMB | …",
    "linear_team": "Emberworks | …",
    "tagline": "free text (optional)",
    # Phase 10 — credentials handling (per-integration mode + values).
    # Added by FORGE-5.4 (EMB-289). Each integration the user selected in
    # phases 4-7 has one of three modes:
    #   - "provide": user supplied real keys; write them to .env.<flavor>.
    #   - "defer":   user wants to start now with stubs; write workable
    #                offline stubs and emit a Mode M ticket so the user
    #                completes setup later.
    #   - "skip":    integration is not needed at all. (Equivalent to
    #                answering 'none' in phases 4-7 — a no-op here.)
    # Default if missing: "defer" for any selected integration.
    #
    # Shape:
    # "credentials": {
    #   "supabase":     {"mode": "provide",
    #                    "values": {"url": "...", "anon_key": "...",
    #                               "service_role": "..."}},
    #   "sentry":       {"mode": "defer"},
    #   "firebase":     {"mode": "defer"},  # values come from
    #                                       # google-services.json — never
    #                                       # via .env.
    #   "oauth_google": {"mode": "provide",
    #                    "values": {"ios": "...", "android": "..."}},
    #   "oidc":         {"mode": "provide",
    #                    "values": {"issuer": "...", "client_id": "...",
    #                               "redirect_uri": "...",
    #                               "scopes": "..."}},
    #   "analytics":    {"mode": "defer"},   # token kept under one key
    #                                        # since only one analytics is
    #                                        # selected at a time.
    #   "onesignal":    {"mode": "defer"},
    # }
    "credentials": "dict — see comment above",
    # Phase 11 — remote setup (FORGE-5.5 / EMB-290).
    # Collected AFTER the scaffolder generates the local project.
    # Both fields are optional; defaults to "skip" (local-only project).
    #
    # "gh_repo": one of:
    #   - "create_push"  → gh repo create + git push -u origin main
    #   - "create_only"  → gh repo create, no push
    #   - "skip"         → no GitHub repo (default)
    #
    # "linear_project": one of:
    #   - "create"       → call /project-init's Linear sub-flow (step 7.5)
    #                      to create project + P0 Bootstrap + P1 MVP
    #   - "skip"         → no Linear project (default)
    "gh_repo": "create_push | create_only | skip",
    "linear_project": "create | skip",
}

# Workable defer-mode stub values per env key. The app must boot with these
# without crashing — Supabase init wrapped in try/catch, empty Sentry DSN
# no-ops by SDK design.
DEFER_STUBS: dict[str, str] = {
    "SUPABASE_URL": "https://stub.supabase.co",
    "SUPABASE_ANON_KEY": "eyJ-stub-key",
    "SUPABASE_SERVICE_ROLE": "",
    "API_BASE_URL": "https://stub.example.com",
    "SENTRY_DSN": "",
    "ANALYTICS_TOKEN": "",
    "ONESIGNAL_APP_ID": "",
    "OIDC_ISSUER_URL": "https://stub-idp.example.com",
    "OIDC_CLIENT_ID": "stub-client-id",
    "OIDC_REDIRECT_URI": "com.example.app://oauth/callback",
    "OIDC_ADDITIONAL_SCOPES": "",
    "GOOGLE_OAUTH_CLIENT_ID": "stub-google-client-id.apps.googleusercontent.com",
}

# ----------------------------------------------------------------------------
# Theme token IR (EMB-320). All four Q6.2 channels converge on this dict
# before _generate_theme_overrides() writes <project>_theme.dart.
#
# Shape (every key optional — only supplied tokens override base classes):
#   {
#     "colors": {
#         # required keys when present; map to ColorScheme + AppColors usage:
#         "primary":   "#1565C0",
#         "secondary": "#FFA000",
#         "surface":   "#FFFFFF",
#         "background":"#F5F5F5",
#         "error":     "#D32F2F",
#         # optional extras — passed through verbatim as `Color(0xFF…)` consts:
#         "onPrimary": "#FFFFFF",
#         "outline":   "#9E9E9E",
#     },
#     "typography": {
#         "family": "Inter",          # google-fonts name; falls back to Inter.
#         # Optional per-style overrides; key names map to AppTypography getters:
#         "displayLarge":  {"size": 48, "weight": 700, "height": 1.1},
#         "headlineSmall": {"size": 24, "weight": 700},
#         "bodyMedium":    {"size": 16, "weight": 400},
#     },
#     "radius": {
#         # numeric values map to AppRadius semantic aliases:
#         "button":     8,
#         "card":       12,
#         "input":      8,
#         "dialog":     16,
#         "bottomSheet":16,
#     },
#   }
#
# Parsers in this file produce this shape from md / css|html / json input.
# Figma / brainstorm channels expect callers to supply a pre-resolved IR
# under `Q6_2_tokens` (the interview agent does the MCP call before invoking
# the scaffolder).
# ----------------------------------------------------------------------------
THEME_TOKEN_IR_SHAPE: dict[str, Any] = {
    "colors": {
        "primary": "str (#RRGGBB or #AARRGGBB)",
        "secondary": "str",
        "surface": "str",
        "background": "str",
        "error": "str",
    },
    "typography": {
        "family": "str (google-fonts name; default 'Inter')",
        "<textStyle>": {"size": "int", "weight": "int (100-900)", "height": "float"},
    },
    "radius": {"button": "int", "card": "int", "input": "int"},
}


# ----------------------------------------------------------------------------
# Defaults — applied if a given key is missing from the answers file.
# Mirror the spec's "press-enter" behaviour.
# ----------------------------------------------------------------------------
DEFAULTS: dict[str, Any] = {
    "Q1_1_layout": "inline",
    "Q1_4_description": "",
    "Q2_1_android_min_sdk": 24,
    "Q2_2_ios_min_version": "14.0",
    "Q3_1_state_mgmt": "bloc",
    "Q3_2_di": "get_it",
    "Q3_3_navigation": "go_router",
    "Q4_1_backend": "supabase",
    "Q4_2_http_client": None,  # auto-resolved from Q4_1
    "Q4_3_persistence": "drift",
    "Q4_4_secure_storage": None,  # auto-resolved from Q5_1
    "Q4_5_websockets": "yes",
    "Q5_1_auth": None,  # auto-resolved from Q4_1
    "Q5_2_oidc_idp": "",
    "Q6_1_theme": "material3",
    "Q6_2_theme_tokens": "defaults",
    "Q6_2_source": None,
    "Q6_2_tokens": None,
    "Q6_3_l10n": "en",
    "Q6_4_animations": "none",
    "Q6_5_game": "none",
    "Q7_1_error_tracking": "crashlytics_sentry",
    "Q7_2_analytics": "none",
    "Q7_3_push": "none",
    "Q8_1_environments": "dev_prod",
    "Q8_2_ide": "both",
    "Q8_3_testing": "bloc_test_mocktail",
    "Q8_4_linting": "very_good_analysis",
    "Q8_5_fastlane": "no",
    # Phase 9 — Workflow / task tracker (EMB-324)
    "Q9_1_tracker": "linear",
    "Q9_workspace": "",
    "Q9_project": "",
    "linear_prefix": "",
    "linear_team": "",
    "tagline": "",
    # Phase 10 — remote setup (FORGE-5.5 / EMB-290)
    "gh_repo": "skip",
    "linear_project": "skip",
}


# ----------------------------------------------------------------------------
# Substitution & rewrite helpers
# ----------------------------------------------------------------------------
NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
BUNDLE_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


def snake_case(value: str) -> str:
    """Best-effort snake_case conversion for a project display name."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    if s and s[0].isdigit():
        s = "p_" + s
    return s


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


# Root of the forge plugin (plugins/forge/). Resolved relative to this script
# so it works standalone without relying on ~/.claude/ being present.
_PLUGIN_ROOT = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------------
# Theme token parsers (EMB-320). Each consumes raw file text and returns the
# canonical THEME_TOKEN_IR_SHAPE dict. Unrecognised content is silently
# skipped so partial inputs (just colours, or just radii) still work.
# ----------------------------------------------------------------------------
_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
_CSS_VAR_RE = re.compile(
    r"--([a-zA-Z][\w-]*)\s*:\s*([^;\n]+);", re.MULTILINE
)
_TOKEN_KEY_RE = re.compile(r"^[a-zA-Z][\w-]*$")


def _canonical_color_key(raw: str) -> str | None:
    """Map a variety of token names to one of the canonical color slots.

    Returns None if the key doesn't match a known semantic role — caller
    skips it (we keep only the five base scheme slots + a few extras).
    """
    k = raw.lower().replace("-", "_").replace(".", "_")
    # strip common prefixes
    for prefix in ("color_", "colour_", "palette_", "brand_"):
        if k.startswith(prefix):
            k = k[len(prefix):]
    # canonical map — first match wins.
    mapping = {
        "primary": "primary",
        "brand": "primary",
        "accent": "secondary",
        "secondary": "secondary",
        "surface": "surface",
        "card": "surface",
        "background": "background",
        "bg": "background",
        "error": "error",
        "danger": "error",
        "destructive": "error",
        "on_primary": "onPrimary",
        "onprimary": "onPrimary",
        "outline": "outline",
        "border": "outline",
    }
    return mapping.get(k)


def _canonical_radius_key(raw: str) -> str | None:
    k = raw.lower().replace("-", "_").replace(".", "_")
    for prefix in ("radius_", "border_radius_", "corner_"):
        if k.startswith(prefix):
            k = k[len(prefix):]
    mapping = {
        "button": "button",
        "card": "card",
        "input": "input",
        "field": "input",
        "dialog": "dialog",
        "modal": "dialog",
        "bottom_sheet": "bottomSheet",
        "bottomsheet": "bottomSheet",
        "sheet": "bottomSheet",
    }
    return mapping.get(k)


def _normalize_hex(value: str) -> str | None:
    """Return canonical #RRGGBB or #AARRGGBB or None if not a valid hex."""
    v = value.strip().strip(";").strip()
    m = _HEX_RE.fullmatch(v) or _HEX_RE.match(v)
    if not m:
        return None
    hexpart = m.group(0)
    body = hexpart[1:]
    if len(body) == 3:
        body = "".join(c + c for c in body)
    if len(body) == 4:  # #RGBA -> AARRGGBB
        a = body[3] * 2
        rgb = "".join(c + c for c in body[:3])
        body = a + rgb
    return "#" + body.upper()


def _try_int(text: str) -> int | None:
    """Extract a leading int (e.g. '12px' -> 12, '8' -> 8)."""
    m = re.match(r"-?\d+", text.strip())
    return int(m.group(0)) if m else None


def parse_tokens_from_json(text: str) -> dict[str, Any]:
    """Parse style-dictionary / w3c-style design-token JSON into the IR.

    Accepts two shapes:
      A) Flat-ish IR (already matches THEME_TOKEN_IR_SHAPE) — passed through
         after light normalisation.
      B) Nested w3c shape: `{"color": {"primary": {"value": "#abc"}}, ...}`
         or style-dictionary `{"color": {"primary": {"$value": "#abc"}}}`.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"theme tokens file is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("theme tokens JSON must be an object at the root")

    ir: dict[str, Any] = {"colors": {}, "typography": {}, "radius": {}}

    def _value_of(node: Any) -> Any:
        if isinstance(node, dict):
            for k in ("value", "$value"):
                if k in node:
                    return node[k]
        return node

    # Shape A — already-IR keys at root
    if "colors" in data and isinstance(data["colors"], dict):
        for k, v in data["colors"].items():
            normalized = _normalize_hex(str(_value_of(v)))
            canonical = _canonical_color_key(k)
            if normalized and canonical:
                ir["colors"][canonical] = normalized
    if "typography" in data and isinstance(data["typography"], dict):
        for k, v in data["typography"].items():
            if k == "family":
                ir["typography"]["family"] = str(v)
            elif isinstance(v, dict):
                style: dict[str, Any] = {}
                if "size" in v:
                    n = _try_int(str(v["size"]))
                    if n is not None:
                        style["size"] = n
                if "weight" in v:
                    n = _try_int(str(v["weight"]))
                    if n is not None:
                        style["weight"] = n
                if "height" in v:
                    try:
                        style["height"] = float(v["height"])
                    except (TypeError, ValueError):
                        pass
                if style:
                    ir["typography"][k] = style
    if "radius" in data and isinstance(data["radius"], dict):
        for k, v in data["radius"].items():
            canonical = _canonical_radius_key(k)
            n = _try_int(str(_value_of(v)))
            if canonical and n is not None:
                ir["radius"][canonical] = n

    # Shape B — `color` / `font` / `radius` top-level groups (w3c-ish).
    if "color" in data and isinstance(data["color"], dict):
        for k, v in data["color"].items():
            normalized = _normalize_hex(str(_value_of(v)))
            canonical = _canonical_color_key(k)
            if normalized and canonical:
                ir["colors"].setdefault(canonical, normalized)
    for group_key in ("borderRadius", "border-radius", "radii"):
        if group_key in data and isinstance(data[group_key], dict):
            for k, v in data[group_key].items():
                canonical = _canonical_radius_key(k)
                n = _try_int(str(_value_of(v)))
                if canonical and n is not None:
                    ir["radius"].setdefault(canonical, n)
    return ir


def parse_tokens_from_css(text: str) -> dict[str, Any]:
    """Parse CSS / HTML custom-property declarations (--token-name: value;).

    Color values must be hex (`#…`); other formats (rgb(), hsl()) are skipped.
    Radius values must end with `px` or be bare ints.
    """
    ir: dict[str, Any] = {"colors": {}, "typography": {}, "radius": {}}
    for match in _CSS_VAR_RE.finditer(text):
        name = match.group(1)
        raw_value = match.group(2).strip()
        # Try as color
        hex_val = _normalize_hex(raw_value)
        if hex_val:
            canonical = _canonical_color_key(name)
            if canonical:
                ir["colors"].setdefault(canonical, hex_val)
            continue
        # Try as radius / spacing int
        n = _try_int(raw_value)
        if n is not None:
            canonical = _canonical_radius_key(name)
            if canonical:
                ir["radius"].setdefault(canonical, n)
    return ir


def parse_tokens_from_markdown(text: str) -> dict[str, Any]:
    """Best-effort markdown parse.

    Looks for sections (e.g. `# Colors`, `## Typography`, `## Radius`) and
    extracts `- key: value` style entries underneath. Section names are
    case-insensitive; key matching uses the same canonical maps as the
    other parsers.
    """
    ir: dict[str, Any] = {"colors": {}, "typography": {}, "radius": {}}

    # Split into sections by markdown headings.
    section = ""
    bullet_re = re.compile(
        r"^\s*[-*]\s*`?([a-zA-Z][\w-]*)`?\s*[:=]\s*`?(.+?)`?\s*$"
    )
    heading_re = re.compile(r"^\s{0,3}#+\s+(.+?)\s*$")
    for line in text.splitlines():
        h = heading_re.match(line)
        if h:
            section = h.group(1).strip().lower()
            continue
        b = bullet_re.match(line)
        if not b:
            continue
        key, raw_value = b.group(1), b.group(2).strip()
        if any(kw in section for kw in ("color", "colour", "palette")):
            hex_val = _normalize_hex(raw_value)
            canonical = _canonical_color_key(key)
            if hex_val and canonical:
                ir["colors"].setdefault(canonical, hex_val)
        elif any(kw in section for kw in ("radius", "radii", "corner")):
            n = _try_int(raw_value)
            canonical = _canonical_radius_key(key)
            if n is not None and canonical:
                ir["radius"].setdefault(canonical, n)
        elif "typograph" in section or "font" in section:
            if key.lower() in ("family", "font", "font-family"):
                ir["typography"]["family"] = raw_value.strip('"').strip("'")
    return ir


def _google_fonts_method(family: str) -> str:
    """Convert a font family name to its google_fonts camelCase method.

    e.g. 'Inter' -> 'inter', 'Roboto Slab' -> 'robotoSlab', 'Open Sans' -> 'openSans'.
    Defaults to 'inter' on empty/invalid input.
    """
    parts = re.split(r"[\s_-]+", family.strip())
    parts = [p for p in parts if p]
    if not parts:
        return "inter"
    head = parts[0].lower()
    tail = "".join(p.capitalize() for p in parts[1:])
    return head + tail


def parse_tokens_from_file(path: Path) -> dict[str, Any]:
    """Dispatcher: pick parser based on file suffix.

    Supported: .json, .css, .html / .htm, .md / .markdown.
    Unknown suffixes raise ValueError with a clear hint.
    """
    if not path.is_file():
        raise FileNotFoundError(f"theme tokens file not found: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix in (".json",):
        return parse_tokens_from_json(text)
    if suffix in (".css", ".html", ".htm"):
        return parse_tokens_from_css(text)
    if suffix in (".md", ".markdown"):
        return parse_tokens_from_markdown(text)
    raise ValueError(
        f"theme tokens file '{path.name}' has unsupported suffix '{suffix}'. "
        "Supported: .json, .css, .html, .md"
    )


# ----------------------------------------------------------------------------
# Resolved answers — encapsulates derived defaults and validation.
# ----------------------------------------------------------------------------
@dataclass
class Answers:
    raw: dict[str, Any]

    # resolved
    layout: str = "inline"
    name: str = ""
    name_snake: str = ""
    bundle_id: str = ""
    description: str = ""
    android_min_sdk: int = 24
    ios_min_version: str = "14.0"
    state_mgmt: str = "bloc"
    di: str = "get_it"
    navigation: str = "go_router"
    backend: str = "supabase"
    http_client: str = "dio"
    persistence: str = "drift"
    secure_storage: bool = True
    websockets: bool = True
    auth: str = "none"
    oidc_idp: str = ""
    theme: str = "material3"
    theme_tokens: str = "defaults"
    # EMB-320: per-channel inputs.
    # - theme_tokens_source: filesystem path (only when theme_tokens == "file").
    # - theme_tokens_ir: pre-resolved IR dict (figma / brainstorm channels).
    theme_tokens_source: str = ""
    theme_tokens_ir: dict[str, Any] = field(default_factory=dict)
    l10n: str = "en"
    animations: str = "none"
    game: str = "none"
    error_tracking: str = "crashlytics_sentry"
    analytics: str = "none"
    push: str = "none"
    environments: str = "dev_prod"
    ide: str = "both"
    testing: str = "bloc_test_mocktail"
    linting: str = "very_good_analysis"
    # Q8.5 — Fastlane (EMB-321). Default False → no fastlane artifacts.
    fastlane: bool = False
    # Q9 — Workflow / task tracker (EMB-324).
    # tracker: which task-tracking backend was chosen at interview time.
    # tracker_workspace: workspace name / host URL / org-repo depending on backend.
    # tracker_project: project name or ID (meaningful for Linear/GitHub/Jira).
    # Skills DO NOT read tracker.json yet — that's FORGE-8.
    tracker: str = "linear"
    tracker_workspace: str = ""
    tracker_project: str = ""
    linear_prefix: str = ""
    linear_team: str = ""
    tagline: str = ""

    # remote setup (FORGE-5.5 / EMB-290).
    # Both default to "skip" — remote setup is opt-in.
    gh_repo: str = "skip"       # create_push | create_only | skip
    linear_project: str = "skip"  # create | skip

    # credentials handling (FORGE-5.4 / EMB-289).
    # Map of integration key -> {"mode": "provide|defer|skip", "values": {...}}.
    # Populated by from_dict; read by env / Mode M / AppConfig generation.
    credentials: dict[str, dict[str, Any]] = field(default_factory=dict)

    # tracking — what we'd ask Linear to create as Mode M tickets
    mode_m_tickets: list[dict[str, str]] = field(default_factory=list)

    # ---- credentials helpers (FORGE-5.4) ----
    def cred_mode(self, integration: str) -> str:
        """Return the mode for a given integration key.

        Default is "defer" — caller of the scaffolder should pass an explicit
        mode if they collected one during the interview. "skip" is reserved
        for callers who chose to strip the integration entirely (in practice
        that's redundant with the phase-4-7 "none" answers, but kept here so
        a caller can decline a credential prompt without unselecting the
        feature).
        """
        block = self.credentials.get(integration) or {}
        return block.get("mode") or "defer"

    def cred_values(self, integration: str) -> dict[str, str]:
        block = self.credentials.get(integration) or {}
        vals = block.get("values") or {}
        return {str(k): str(v) for k, v in vals.items() if v is not None}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Answers":
        # apply defaults
        merged: dict[str, Any] = {**DEFAULTS, **raw}
        a = cls(raw=raw)

        a.layout = merged.get("Q1_1_layout", "inline")

        name_input = (merged.get("Q1_2_name") or "").strip()
        if not name_input:
            raise ValueError("Q1_2_name is required (project display name)")
        a.name = name_input
        a.name_snake = snake_case(name_input)
        if not NAME_RE.match(a.name_snake):
            raise ValueError(
                f"Q1_2_name snake_cased to '{a.name_snake}' which does not match {NAME_RE.pattern}"
            )

        bid = (merged.get("Q1_3_bundle_id") or "").strip()
        if not bid:
            raise ValueError("Q1_3_bundle_id is required (e.g. com.example.app)")
        if not BUNDLE_RE.match(bid):
            raise ValueError(f"Q1_3_bundle_id '{bid}' does not match {BUNDLE_RE.pattern}")
        a.bundle_id = bid

        a.description = merged.get("Q1_4_description") or ""
        a.android_min_sdk = int(merged.get("Q2_1_android_min_sdk") or 24)
        a.ios_min_version = str(merged.get("Q2_2_ios_min_version") or "14.0")

        a.state_mgmt = merged.get("Q3_1_state_mgmt", "bloc")
        a.di = merged.get("Q3_2_di") or "get_it"
        if a.state_mgmt == "riverpod":
            a.di = "riverpod"  # Riverpod IS the DI
        a.navigation = merged.get("Q3_3_navigation", "go_router")

        a.backend = merged.get("Q4_1_backend", "supabase")

        # http_client resolution: skip if Supabase/Firebase
        http = merged.get("Q4_2_http_client")
        if a.backend in ("supabase", "firebase"):
            a.http_client = "none"  # SDK covers HTTP; no extra client
        else:
            a.http_client = http or ("dio" if a.backend == "custom_rest" else "none")

        a.persistence = merged.get("Q4_3_persistence", "drift")

        # auth resolution
        auth = merged.get("Q5_1_auth")
        if auth is None:
            auth_map = {
                "supabase": "supabase_auth",
                "firebase": "firebase_auth",
                "custom_rest": "custom_rest_auth",
                "none": "none",
            }
            auth = auth_map.get(a.backend, "none")
        a.auth = auth
        a.oidc_idp = merged.get("Q5_2_oidc_idp") or ""

        # secure storage default depends on auth
        ss = merged.get("Q4_4_secure_storage")
        if ss is None:
            a.secure_storage = a.auth != "none"
        else:
            a.secure_storage = ss == "yes" or ss is True

        a.websockets = (merged.get("Q4_5_websockets") or "yes") in ("yes", True)

        a.theme = merged.get("Q6_1_theme", "material3")
        a.theme_tokens = merged.get("Q6_2_theme_tokens", "defaults")
        if a.theme_tokens not in ("defaults", "file", "figma", "brainstorm"):
            raise ValueError(
                "Q6_2_theme_tokens must be one of "
                "defaults|file|figma|brainstorm "
                f"(got '{a.theme_tokens}')"
            )
        a.theme_tokens_source = str(merged.get("Q6_2_source") or "").strip()
        tokens_ir = merged.get("Q6_2_tokens") or {}
        if tokens_ir and not isinstance(tokens_ir, dict):
            raise ValueError("Q6_2_tokens, if provided, must be a dict (token IR)")
        a.theme_tokens_ir = dict(tokens_ir)
        if a.theme_tokens == "file" and not a.theme_tokens_source:
            raise ValueError(
                "Q6_2_theme_tokens=file requires Q6_2_source (path to tokens file)"
            )
        if a.theme_tokens in ("figma", "brainstorm") and not a.theme_tokens_ir:
            # Soft fallback: caller didn't supply IR — degrade to defaults so the
            # scaffolder still produces a working project. Mode M ticket records
            # the gap so the user can wire tokens later.
            a.theme_tokens = "defaults"
        a.l10n = merged.get("Q6_3_l10n", "en")
        a.animations = merged.get("Q6_4_animations", "none")
        a.game = merged.get("Q6_5_game", "none")
        a.error_tracking = merged.get("Q7_1_error_tracking", "crashlytics_sentry")
        a.analytics = merged.get("Q7_2_analytics", "none")
        a.push = merged.get("Q7_3_push", "none")
        a.environments = merged.get("Q8_1_environments", "dev_prod")
        a.ide = merged.get("Q8_2_ide", "both")
        a.testing = merged.get("Q8_3_testing", "bloc_test_mocktail")
        a.linting = merged.get("Q8_4_linting", "very_good_analysis")
        # Q8.5 — Fastlane (EMB-321)
        fastlane_raw = (merged.get("Q8_5_fastlane") or "no").strip().lower()
        a.fastlane = fastlane_raw in ("yes", "true")

        # Q9 — Workflow / task tracker (EMB-324)
        tracker_raw = (merged.get("Q9_1_tracker") or "linear").strip().lower()
        if tracker_raw not in ("linear", "github_projects", "jira", "other"):
            raise ValueError(
                "Q9_1_tracker must be one of linear|github_projects|jira|other "
                f"(got '{tracker_raw}')"
            )
        a.tracker = tracker_raw
        a.tracker_workspace = str(merged.get("Q9_workspace") or "").strip()
        a.tracker_project = str(merged.get("Q9_project") or "").strip()

        a.linear_prefix = merged.get("linear_prefix", "")
        a.linear_team = merged.get("linear_team", "")
        a.tagline = merged.get("tagline", "")

        # Remote setup (FORGE-5.5 / EMB-290).
        gh_repo = (merged.get("gh_repo") or "skip").strip()
        if gh_repo not in ("create_push", "create_only", "skip"):
            raise ValueError(
                f"gh_repo must be create_push|create_only|skip, got '{gh_repo}'"
            )
        a.gh_repo = gh_repo

        linear_project = (merged.get("linear_project") or "skip").strip()
        if linear_project not in ("create", "skip"):
            raise ValueError(
                f"linear_project must be create|skip, got '{linear_project}'"
            )
        a.linear_project = linear_project

        # Credentials (FORGE-5.4 / EMB-289). Caller passes a mapping under
        # the "credentials" key; we accept it as-is and validate per-entry
        # shape. Missing entries → mode defaults to "defer" via cred_mode().
        creds_raw = merged.get("credentials") or {}
        if not isinstance(creds_raw, dict):
            raise ValueError("credentials, if provided, must be a dict")
        sanitized: dict[str, dict[str, Any]] = {}
        for key, block in creds_raw.items():
            if not isinstance(block, dict):
                raise ValueError(
                    f"credentials.{key} must be a dict with 'mode' (and optional 'values')"
                )
            mode = (block.get("mode") or "").strip()
            if mode not in ("provide", "defer", "skip"):
                raise ValueError(
                    f"credentials.{key}.mode must be one of provide|defer|skip "
                    f"(got '{mode}')"
                )
            entry: dict[str, Any] = {"mode": mode}
            vals = block.get("values")
            if vals is not None:
                if not isinstance(vals, dict):
                    raise ValueError(
                        f"credentials.{key}.values must be a dict if present"
                    )
                entry["values"] = vals
            sanitized[key] = entry
        a.credentials = sanitized
        return a

    def stack_summary(self) -> str:
        bits = [
            f"Flutter + {self.state_mgmt}",
            self.persistence if self.persistence != "none" else None,
            self.backend if self.backend != "none" else None,
        ]
        return " + ".join(b for b in bits if b)


# ----------------------------------------------------------------------------
# Filesystem operations
# ----------------------------------------------------------------------------
class Scaffolder:
    """Encapsulates a single scaffold run.

    Public entry: `run()`. All side effects gated by `dry_run` — when True,
    operations log to stdout and target stays untouched.
    """

    # core_dir is relative to <target>/lib/ — varies by Q1_1 layout.
    # For inline: lib/core/<modules…>. For local pkg: packages/shared_core/lib/<modules…>.

    def __init__(
        self,
        answers: Answers,
        target: Path,
        template: Path,
        pin: Path,
        *,
        dry_run: bool = False,
    ) -> None:
        self.a = answers
        self.target = target
        self.template = template
        self.pin = pin
        self.dry_run = dry_run
        self.summary: list[str] = []  # human-readable log
        # EMB-318: separate list for files/dirs dropped during scaffold so the
        # user can see exactly what was removed and why in scaffold-report.json.
        self.dropped_files: list[dict[str, str]] = []

    # -- helpers -----------------------------------------------------------
    def _log(self, msg: str) -> None:
        self.summary.append(msg)
        print(f"[scaffold] {msg}")

    def _mkdir(self, p: Path) -> None:
        self._log(f"mkdir {p}")
        if not self.dry_run:
            p.mkdir(parents=True, exist_ok=True)

    def _write(self, p: Path, content: str) -> None:
        self._log(f"write {p} ({len(content)} bytes)")
        if not self.dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)

    def _copytree(self, src: Path, dst: Path) -> None:
        self._log(f"copytree {src} -> {dst}")
        if not self.dry_run:
            shutil.copytree(src, dst, dirs_exist_ok=True)

    def _rmtree(self, p: Path, reason: str = "") -> None:
        if not p.exists():
            return
        self._log(f"rmtree {p}" + (f" [{reason}]" if reason else ""))
        rel = str(p.relative_to(self.target)) if p.is_relative_to(self.target) else str(p)
        self.dropped_files.append({"path": rel, "kind": "dir", "reason": reason})
        if not self.dry_run:
            shutil.rmtree(p)

    def _rm(self, p: Path, reason: str = "") -> None:
        if not p.exists():
            return
        self._log(f"rm {p}" + (f" [{reason}]" if reason else ""))
        rel = str(p.relative_to(self.target)) if p.is_relative_to(self.target) else str(p)
        self.dropped_files.append({"path": rel, "kind": "file", "reason": reason})
        if not self.dry_run:
            p.unlink()

    def _add_mode_m(self, title: str, template_name: str | None = None) -> None:
        self.a.mode_m_tickets.append({"title": title, "template": template_name or ""})

    def _maybe_add_mode_m(
        self,
        integration: str,
        title: str,
        template_name: str | None = None,
    ) -> None:
        """Emit a Mode M ticket only when the integration's credentials are deferred.

        provide → user already supplied keys; setup is done.
        defer   → emit Mode M (current behavior).
        skip    → defensive: skip silently (caller likely shouldn't reach here).
        """
        mode = self.a.cred_mode(integration)
        if mode == "provide":
            self._log(
                f"credentials[{integration}]=provide → suppress Mode M ticket"
            )
            return
        if mode == "skip":
            self._log(
                f"credentials[{integration}]=skip → no Mode M ticket"
            )
            return
        self._add_mode_m(title, template_name=template_name)

    # -- core path resolution ---------------------------------------------
    @property
    def core_dir(self) -> Path:
        """Where flutter-template's lib/src/* lands in the target.

        EMB-315: inline layout now places core under lib/src/core/ (not lib/core/)
        to mirror the b2b-mobile-app reference structure where all project code
        lives under lib/src/.
        """
        if self.a.layout == "local_package":
            return self.target / "packages" / "shared_core" / "lib"
        return self.target / "lib" / "src" / "core"

    @property
    def core_pubspec(self) -> Path:
        if self.a.layout == "local_package":
            return self.target / "packages" / "shared_core" / "pubspec.yaml"
        return self.target / "pubspec.yaml"

    # -- top-level orchestration ------------------------------------------
    def run(self) -> int:
        self._log(f"scaffold start: target={self.target} template={self.template}")
        self._log(f"layout={self.a.layout} stack={self.a.stack_summary()}")

        if self.target.exists() and any(self.target.iterdir() if self.target.is_dir() else []):
            self._log(f"WARNING: target {self.target} already exists and is non-empty")

        self._mkdir(self.target)

        # Step 0: `flutter create` baseline — Flutter SDK generates the canonical
        # project shell (android/, ios/, .metadata, base test/widget_test.dart).
        # Our overlay logic below then replaces pubspec.yaml, lib/main.dart,
        # analysis_options.yaml, etc., on top of this shell. See EMB-314.
        self._run_flutter_create()

        self._copy_template_core()
        self._patch_template_bugs()
        self._apply_substitutions()
        self._drop_unselected_features()
        self._generate_app_skeleton()
        self._generate_pubspec()
        self._generate_analysis_options()
        self._generate_app_config()
        self._generate_env_files()
        self._generate_app_widget()
        self._generate_di_stub()
        self._generate_home_feature()
        self._generate_shared_user_feature()
        self._generate_main_entries()
        self._generate_ide_configs()
        self._generate_assets()
        self._generate_theme_overrides()
        self._generate_test_skeleton()
        self._generate_l10n_skeleton()
        self._generate_claude_md()
        self._copy_kit_skills()
        self._generate_settings_json()
        self._generate_tracker_json()
        self._generate_docs_meta()
        self._generate_gitignore()
        self._generate_launcher_icon_yamls()

        self._write_summary()
        return 0

    # -- step 0: `flutter create` baseline (EMB-314) -----------------------
    def _run_flutter_create(self) -> None:
        """Invoke `flutter create` so the Flutter SDK owns the project shell.

        Generates android/, ios/, .metadata, default lib/main.dart, base
        test/widget_test.dart, etc. Our subsequent overlay steps replace
        files we care about (pubspec.yaml, lib/main.dart, lib/src/**, env
        files, CLAUDE.md, .claude/, docs/00_meta/, IDE configs) while
        keeping the platform shells intact.

        Halts on non-zero exit so we don't proceed against a half-broken
        target directory. In `dry_run` mode we log the intended command
        and return without executing.
        """
        # bundle-id-prefix: everything except the last segment of bundle id.
        # e.g. com.emberworks.scaffold_test → com.emberworks
        bundle_parts = self.a.bundle_id.split(".")
        if len(bundle_parts) < 2:
            raise ValueError(
                f"bundle id '{self.a.bundle_id}' has no organisation prefix; "
                "expected at least two dot-separated segments"
            )
        org = ".".join(bundle_parts[:-1])

        description = (
            self.a.description
            or self.a.tagline
            or "A new Flutter project."
        )

        cmd = [
            "flutter", "create", str(self.target),
            "--org", org,
            "--project-name", self.a.name_snake,
            "--platforms=android,ios",
            "--description", description,
        ]

        self._log(f"flutter create: {' '.join(cmd)}")
        if self.dry_run:
            return

        if not shutil.which("flutter"):
            raise RuntimeError(
                "`flutter` CLI not found in PATH — scaffolder now requires "
                "the Flutter SDK to generate the project baseline (EMB-314). "
                "Install Flutter or add it to PATH, then re-run the scaffolder."
            )

        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:  # pragma: no cover — defensive
            raise RuntimeError(f"failed to invoke flutter create: {exc}") from exc

        if result.stdout:
            for line in result.stdout.splitlines():
                self._log(f"flutter create | {line}")
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                f"flutter create exited with code {result.returncode}: {stderr}"
            )

    # -- step 1: copy template to <target>/<core_dir> ---------------------
    def _copy_template_core(self) -> None:
        """Copy flutter-template's lib/src/** into the project core dir."""
        src_lib = self.template / "lib" / "src"
        if not src_lib.is_dir():
            raise FileNotFoundError(f"template missing lib/src/: {src_lib}")

        if self.a.layout == "local_package":
            # packages/shared_core/lib/<modules>
            dst = self.core_dir
            self._copytree(src_lib, dst)
            # Also copy the barrel file alongside.
            barrel = self.template / "lib" / "shared_core.dart"
            if barrel.is_file():
                self._copytree_file(barrel, self.core_dir / "shared_core.dart")
        else:
            # inline: project lib/core/<modules>
            dst = self.core_dir
            self._copytree(src_lib, dst)

    def _copytree_file(self, src: Path, dst: Path) -> None:
        self._log(f"cp {src} -> {dst}")
        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # -- step 1b: patch known template issues post-copy -------------------
    def _patch_template_bugs(self) -> None:
        """Apply in-place fixes for known issues in the copied template source.

        These are bugs in flutter-template that need remediation at scaffold
        time (template source is read-only from the scaffolder's perspective).
        Tracked separately so they can be cleaned up in a future template bump.
        """
        if self.dry_run:
            return

        # EMB-315: The template ships lib/src/config/app_config.dart which
        # imports lib/src/config/env_config.dart (containing the EnvConfig class
        # and Environment enum). Our scaffolder generates a replacement
        # env_config.dart (in the same dir) that uses a different design
        # (AppConfig + AppEnvConfigs enum, setEnvironment pattern). The
        # template's app_config.dart now references undefined types and must be
        # removed. Our generated env_config.dart is written after this step and
        # replaces the template copy. The template's keycloak_config.dart is
        # removed conditionally in _drop_unselected_features.
        # EMB-318: use _rm() so drops appear in dropped_files in scaffold-report.json.
        self._rm(
            self.core_dir / "config" / "app_config.dart",
            reason="template app_config.dart replaced by generated env_config.dart (EMB-315)",
        )
        # Also remove the template's env_config.dart that ships with it
        # (it defines EnvConfig / Environment which our design doesn't use).
        # The scaffolder will write a fresh env_config.dart after this step.
        self._rm(
            self.core_dir / "config" / "env_config.dart",
            reason="template env_config.dart replaced by generated env_config.dart (EMB-315)",
        )

        # country_service.dart: json.decode returns dynamic; explicit
        # Map<String, dynamic> annotation fails very_good_analysis strict mode.
        # Fix: add `as Map<String, dynamic>` cast on the decode call.
        cs = self.core_dir / "country" / "country_service.dart"
        if cs.is_file():
            text = cs.read_text()
            old = "    final Map<String, dynamic> jsonData = json.decode(jsonString);"
            new = "    final jsonData = json.decode(jsonString) as Map<String, dynamic>;"
            if old in text:
                text = text.replace(old, new)
                cs.write_text(text)
                self._log("patched country/country_service.dart: Map<String,dynamic> cast")

    # -- step 2: in-place substitutions on copied dart files --------------
    def _apply_substitutions(self) -> None:
        """Rewrite `package:shared_core/...` imports + project name placeholders."""
        if self.a.layout == "local_package":
            # imports stay as `package:shared_core/...` — local_package keeps that name
            self._log("layout=local_package: keeping package:shared_core/... imports")
            return

        # inline: rewrite `package:shared_core/...` -> `package:<name>/src/core/...`
        # EMB-315: prefix is now src/core/ because inline layout places core
        # under lib/src/core/ (all project code lives under lib/src/).
        new_pkg = self.a.name_snake
        for dart in self.core_dir.rglob("*.dart"):
            self._rewrite_imports(dart, "shared_core", new_pkg, "src/core/")

    def _rewrite_imports(self, file: Path, old_pkg: str, new_pkg: str, prefix: str) -> None:
        if not file.is_file():
            return
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            return
        new_text = re.sub(
            rf"package:{re.escape(old_pkg)}/",
            f"package:{new_pkg}/{prefix}",
            text,
        )
        if new_text != text:
            self._log(f"rewrite imports in {file.relative_to(self.target)}")
            if not self.dry_run:
                file.write_text(new_text)

    # -- step 3: drop directories for un-selected features ---------------
    def _drop_unselected_features(self) -> None:
        """Remove subtrees that don't apply to the user's stack choices."""
        # WebSockets
        if not self.a.websockets:
            self._rmtree(self.core_dir / "network" / "websocket")

        # HTTP client / Dio
        if self.a.http_client != "dio":
            self._rmtree(self.core_dir / "network" / "dio")
            self._rmtree(self.core_dir / "network" / "interceptors")
            self._rmtree(self.core_dir / "network" / "helpers")
            # api_client.dart is Dio-only; remove it when Dio is not selected.
            self._rm(self.core_dir / "network" / "api_client.dart")
            # result.dart imports package:dio — strip the Dio-specific bits.
            result_file = self.core_dir / "utils" / "result.dart"
            if result_file.is_file() and not self.dry_run:
                text = result_file.read_text()
                # Remove: import 'package:dio/dio.dart';
                text = re.sub(r"^import 'package:dio/dio\.dart';\n", "", text, flags=re.MULTILINE)
                # Remove the _unwrapError method that references DioException
                # (the entire method body from the doc comment to the closing brace)
                text = re.sub(
                    r"\n  /// Unwrap \[DioException\].*?^  }\n",
                    "\n",
                    text,
                    flags=re.DOTALL | re.MULTILINE,
                )
                # Simplify guard() to not call _unwrapError (just return failure directly)
                text = text.replace(
                    "      return Result.failure(_unwrapError(e), stack);",
                    "      return Result.failure(e, stack);",
                )
                result_file.write_text(text)
                self._log("patched utils/result.dart: removed Dio-specific imports and _unwrapError")
            # If WS also off, drop network/ entirely
            if not self.a.websockets and self.a.backend == "none":
                self._rmtree(self.core_dir / "network")

        # Persistence
        if self.a.persistence != "hive_ce":
            # Drop hive-specific code; keep migrations runner only if we have any storage
            self._rmtree(self.core_dir / "storage" / "hive")
        if self.a.persistence == "none":
            self._rmtree(self.core_dir / "storage")
            # theme_notifier.dart imports storage/preferences/preferences_service.dart.
            # When storage is removed the import becomes dangling — remove the
            # notifier too. ThemeMode is still wired via AppTheme in the root widget.
            self._rm(self.core_dir / "theme" / "theme_notifier.dart")
            # Also remove the re-export from theme.dart barrel so analyze is clean.
            theme_barrel = self.core_dir / "theme" / "theme.dart"
            if theme_barrel.is_file() and not self.dry_run:
                text = theme_barrel.read_text()
                text = re.sub(r"^export 'theme_notifier\.dart';\n", "", text, flags=re.MULTILINE)
                theme_barrel.write_text(text)
                self._log("patched theme/theme.dart: removed theme_notifier.dart export")

        # Secure storage: remove the service file if the feature is off.
        # The dep is pubspec-gated in _compose_deps; the source file must be
        # removed too so `flutter analyze` does not see an undefined import.
        if not self.a.secure_storage:
            self._rm(self.core_dir / "storage" / "secure_storage_service.dart")

        # Secure storage usage gating is enforced via pubspec deps (handled later).

        # Auth: drop Keycloak config when not OIDC; drop AuthGuard if no auth.
        # keycloak_config.dart is OIDC-specific — only oidc_sso needs it.
        # EMB-318: previously only dropped for auth==none; now covers all non-OIDC paths.
        if self.a.auth != "oidc_sso":
            self._rm(
                self.core_dir / "config" / "keycloak_config.dart",
                reason="auth != oidc_sso — Keycloak config not needed",
            )
        if self.a.auth == "none":
            self._rm(
                self.core_dir / "navigation" / "auth_guard.dart",
                reason="auth == none — no auth guard needed",
            )
            # If navigation dir becomes empty, drop it
            nav_dir = self.core_dir / "navigation"
            if nav_dir.is_dir() and not any(nav_dir.iterdir()):
                self._rmtree(nav_dir)

        # Error tracking
        if self.a.error_tracking == "none":
            self._rmtree(self.core_dir / "error_tracking")
            # error_handler.dart imports error_tracking — strip the import and
            # the ErrorTrackingService.captureException call when removed.
            eh = self.core_dir / "errors" / "error_handler.dart"
            if eh.is_file() and not self.dry_run:
                text = eh.read_text()
                # Remove the error_tracking import line
                text = re.sub(
                    r"^import '\.\./error_tracking/error_tracking\.dart';\n",
                    "",
                    text,
                    flags=re.MULTILINE,
                )
                # Remove the block that calls ErrorTrackingService.captureException
                text = re.sub(
                    r"\n\s+if \(reportToTracking && _shouldReport\(error\)\) \{[^}]+\}",
                    "",
                    text,
                    flags=re.DOTALL,
                )
                eh.write_text(text)
                self._log("patched errors/error_handler.dart: removed error_tracking import + call")
            # network/interceptors/error_interceptor.dart also imports sentry_flutter
            # and error_tracking — strip when Dio is kept but error tracking is off.
            ei = self.core_dir / "network" / "interceptors" / "error_interceptor.dart"
            if ei.is_file() and not self.dry_run:
                text = ei.read_text()
                # Remove sentry + error_tracking import lines
                text = re.sub(
                    r"^import 'package:sentry_flutter/sentry_flutter\.dart';\n",
                    "",
                    text,
                    flags=re.MULTILINE,
                )
                text = re.sub(
                    r"^import '\.\./\.\./error_tracking/error_tracking\.dart';\n",
                    "",
                    text,
                    flags=re.MULTILINE,
                )
                # Replace onRequest body: strip breadcrumb block, keep only handler.next
                text = re.sub(
                    r"(void onRequest\(RequestOptions options, RequestInterceptorHandler handler\) \{)"
                    r".*?"
                    r"(handler\.next\(options\);)",
                    r"\1\n    \2",
                    text,
                    flags=re.DOTALL,
                )
                # Remove _reportIfServerError call in onError
                text = text.replace(
                    "\n    _reportIfServerError(err, exception);\n",
                    "\n",
                )
                # Remove the entire _reportIfServerError method
                text = re.sub(
                    r"\n  void _reportIfServerError\(DioException err, AppException exception\) \{.*?\n  \}",
                    "",
                    text,
                    flags=re.DOTALL,
                )
                ei.write_text(text)
                self._log("patched network/interceptors/error_interceptor.dart: removed sentry/error_tracking refs")
        elif self.a.error_tracking == "crashlytics":
            # Keep the Sentry-shaped file but mark a Mode M ticket; user swaps later.
            self._add_mode_m(
                f"Replace Sentry adapter with Crashlytics-only in {self.a.name_snake}",
            )

        # Theme: Cupertino swap is heavy → STUB + Mode M
        if self.a.theme == "cupertino":
            self._add_mode_m(
                f"Implement Cupertino-only theme swap in {self.a.name_snake}",
            )

    # -- step 4: app skeleton README (android/, ios/ come from flutter create) -
    def _generate_app_skeleton(self) -> None:
        """Write a README; android/ + ios/ come from `flutter create` (step 0).

        Since EMB-314 the scaffolder runs `flutter create` first, which owns
        the Android/iOS platform shells, `.metadata`, base widget test, etc.
        This step now only emits a README documenting bootstrap from a fresh
        clone (`pub get` + `.env.<flavor>` + `flutter run`).
        """
        readme = self.target / "README.md"
        body = (
            f"# {self.a.name}\n\n"
            f"{self.a.tagline or self.a.description or ''}\n\n"
            "Scaffolded via `plugins/forge/scripts/scaffold-flutter.sh` "
            "(FORGE-5.3, EMB-288). Platform shells generated by "
            "`flutter create` at scaffold time (EMB-314).\n\n"
            "## Bootstrap\n\n"
            "1. Run `flutter pub get`.\n"
            "2. Configure `.env.dev` and `.env.prod` (see `.env.example`).\n"
            "3. Run `flutter run --flavor dev -t lib/main_dev.dart`.\n\n"
            "## Stack\n\n"
            f"- State mgmt: {self.a.state_mgmt}\n"
            f"- DI: {self.a.di}\n"
            f"- Navigation: {self.a.navigation}\n"
            f"- Backend: {self.a.backend}\n"
            f"- Persistence: {self.a.persistence}\n"
            f"- Auth: {self.a.auth}\n"
            f"- Error tracking: {self.a.error_tracking}\n"
            f"- Linting: {self.a.linting}\n"
            f"- Testing: {self.a.testing}\n"
        )
        self._write(readme, body)

    # -- step 5: pubspec.yaml ---------------------------------------------
    def _generate_pubspec(self) -> None:
        deps = self._compose_deps()
        dev_deps = self._compose_dev_deps()

        # description handling
        desc = self.a.description or self.a.tagline or "A new Flutter project."

        # base structure
        lines = [
            f"name: {self.a.name_snake}",
            f"description: {desc}",
            "publish_to: none",
            "version: 0.1.0+1",
            "",
            "environment:",
            "  sdk: ^3.10.4",
            "  flutter: \">=3.32.0\"",
            "",
            "dependencies:",
            "  flutter:",
            "    sdk: flutter",
        ]
        # l10n requires flutter_localizations from sdk
        if self.a.l10n in ("en", "en_uk"):
            lines += [
                "  flutter_localizations:",
                "    sdk: flutter",
            ]
        for name, version in deps.items():
            lines.append(f"  {name}: {version}")

        lines += ["", "dev_dependencies:", "  flutter_test:", "    sdk: flutter"]
        for name, version in dev_deps.items():
            lines.append(f"  {name}: {version}")

        # flutter section
        lines += ["", "flutter:", "  uses-material-design: true"]
        if self.a.l10n in ("en", "en_uk"):
            lines.append("  generate: true")

        # asset declarations — must list the folder prefix (with trailing slash)
        lines += [
            "  assets:",
            "    - assets/images/",
            "    - assets/icons/",
            "    - assets/animations/",
        ]

        self._write(self.core_pubspec, "\n".join(lines) + "\n")

    def _compose_deps(self) -> dict[str, str]:
        """Build runtime dependency map from interview answers."""
        d: dict[str, str] = {}

        # Always-present runtime utilities (mirrored from flutter-template)
        d["equatable"] = "^2.0.7"
        d["intl"] = "^0.20.2"
        d["logging"] = "^1.3.0"
        d["package_info_plus"] = "^9.0.0"
        d["google_fonts"] = "^6.2.1"
        d["connectivity_plus"] = "^6.1.4"

        # State mgmt
        if self.a.state_mgmt == "bloc":
            d["flutter_bloc"] = "^8.1.6"
            d["bloc"] = "^8.1.4"
        elif self.a.state_mgmt == "riverpod":
            d["flutter_riverpod"] = "^2.5.1"  # STUB — flagged by Mode M
            self._add_mode_m(
                f"Implement Riverpod swap in {self.a.name_snake}",
            )
        elif self.a.state_mgmt == "provider":
            d["provider"] = "^6.1.2"
            self._add_mode_m(
                f"Implement Provider swap in {self.a.name_snake}",
            )

        # DI
        if self.a.di == "get_it":
            d["get_it"] = "^7.7.0"
        elif self.a.di == "get_it_injectable":
            d["get_it"] = "^7.7.0"
            d["injectable"] = "^2.4.4"

        # Navigation
        if self.a.navigation == "go_router":
            d["go_router"] = "^14.2.0"
        elif self.a.navigation == "auto_route":
            d["auto_route"] = "^9.2.0"
            self._add_mode_m(
                f"Implement auto_route navigation swap in {self.a.name_snake}",
            )

        # Backend
        if self.a.backend == "supabase":
            d["supabase_flutter"] = "^2.5.6"
            self._maybe_add_mode_m(
                "supabase",
                f"Set up Supabase project + integrate {self.a.name_snake}",
                template_name="supabase.md",
            )
        elif self.a.backend == "firebase":
            d["firebase_core"] = "^3.4.0"
            self._maybe_add_mode_m(
                "firebase",
                f"Set up Firebase project for {self.a.name_snake}",
                template_name="firebase.md",
            )
        elif self.a.backend == "custom_rest":
            d["dio"] = "^5.4.1"

        # HTTP client (only when not auto-skipped)
        # Note: custom_rest already adds dio above; this covers the explicit
        # http_client=dio case when backend is not custom_rest (e.g. backend=none).
        if self.a.http_client == "dio" and "dio" not in d:
            d["dio"] = "^5.4.1"
        elif self.a.http_client == "http":
            d["http"] = "^1.2.2"
            self._add_mode_m(
                f"Implement http (lighter) swap in {self.a.name_snake}",
            )

        # Persistence
        if self.a.persistence == "drift":
            d["drift"] = "^2.20.0"
            d["sqlite3_flutter_libs"] = "^0.5.24"
            d["path_provider"] = "^2.1.4"
            d["path"] = "^1.9.0"
        elif self.a.persistence == "hive_ce":
            d["hive_ce"] = "^2.6.0"
            d["hive_ce_flutter"] = "^2.1.0"
        # shared_prefs is added below regardless
        d["shared_preferences"] = "^2.2.0"

        # Secure storage
        if self.a.secure_storage:
            d["flutter_secure_storage"] = "^9.2.4"

        # WebSockets
        if self.a.websockets:
            d["web_socket_channel"] = "^3.0.1"

        # Auth — wrappers / helpers
        if self.a.auth == "supabase_auth":
            # supabase_flutter already added by Q4_1; Mode M is keyed under
            # the same `supabase` credentials block — if the user provided
            # Supabase keys, no separate Auth Mode M is needed.
            self._maybe_add_mode_m(
                "supabase",
                f"Configure Supabase Auth flow in {self.a.name_snake}",
                template_name="supabase.md",
            )
        elif self.a.auth == "firebase_auth":
            d["firebase_auth"] = "^5.1.4"
            self._maybe_add_mode_m(
                "firebase",
                f"Configure Firebase Auth in {self.a.name_snake}",
                template_name="firebase.md",
            )
        elif self.a.auth in ("oauth_google",):
            d["google_sign_in"] = "^6.2.1"
            self._maybe_add_mode_m(
                "oauth_google",
                f"Configure Google Sign-In in {self.a.name_snake}",
            )
        elif self.a.auth == "oauth_apple":
            d["sign_in_with_apple"] = "^6.1.2"
            self._maybe_add_mode_m(
                "oauth_apple",
                f"Configure Sign in with Apple in {self.a.name_snake}",
            )
        elif self.a.auth == "oidc_sso":
            d["flutter_appauth"] = "^7.0.1"
            idp = self.a.oidc_idp or "OIDC"
            self._maybe_add_mode_m(
                "oidc",
                f"Configure flutter_appauth for {idp} in {self.a.name_snake}",
            )
        elif self.a.auth == "custom_rest_auth":
            # No external service to provision — the Mode M task here is
            # implementation-side, not credentials-side. Always emit.
            self._add_mode_m(
                f"Implement custom-REST email/password auth in {self.a.name_snake}",
            )

        # Animations
        if self.a.animations in ("lottie", "both"):
            d["lottie"] = "^3.1.2"
        if self.a.animations in ("rive", "both"):
            d["rive"] = "^0.13.13"

        # Game
        if self.a.game == "flame":
            d["flame"] = "^1.18.0"
            d["flame_audio"] = "^2.10.0"
            d["flame_bloc"] = "^1.11.0"

        # Error tracking
        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            d["sentry_flutter"] = "^8.12.0"
            # Sentry is gated on a DSN — emit the Mode M ticket unless the
            # user supplied one (in which case .env.<flavor> gets the real
            # value below in _generate_env_files).
            self._maybe_add_mode_m(
                "sentry",
                f"Set up Sentry project + DSN for {self.a.name_snake}",
                template_name="sentry.md",
            )
        if self.a.error_tracking in ("crashlytics", "crashlytics_sentry"):
            d["firebase_core"] = d.get("firebase_core", "^3.4.0")
            d["firebase_crashlytics"] = "^4.1.0"
            self._maybe_add_mode_m(
                "firebase",
                f"Set up Firebase Crashlytics for {self.a.name_snake}",
                template_name="firebase.md",
            )

        # Analytics
        if self.a.analytics == "firebase":
            d["firebase_analytics"] = "^11.3.0"
            d["firebase_core"] = d.get("firebase_core", "^3.4.0")
            # Firebase Analytics shares google-services.json with the rest
            # of Firebase — emit the Firebase Mode M unless provided.
            self._maybe_add_mode_m(
                "firebase",
                f"Set up Firebase Analytics for {self.a.name_snake}",
                template_name="firebase.md",
            )
        elif self.a.analytics == "mixpanel":
            d["mixpanel_flutter"] = "^2.3.1"
            self._maybe_add_mode_m("analytics", f"Set up Mixpanel for {self.a.name_snake}")
        elif self.a.analytics == "amplitude":
            d["amplitude_flutter"] = "^4.0.0"
            self._maybe_add_mode_m("analytics", f"Set up Amplitude for {self.a.name_snake}")
        elif self.a.analytics == "posthog":
            d["posthog_flutter"] = "^4.10.0"
            self._maybe_add_mode_m("analytics", f"Set up PostHog for {self.a.name_snake}")

        # Push
        if self.a.push == "fcm":
            d["firebase_messaging"] = "^15.1.0"
            d["firebase_core"] = d.get("firebase_core", "^3.4.0")
            self._maybe_add_mode_m(
                "firebase",
                f"Set up FCM + APNs cert for {self.a.name_snake}",
                template_name="firebase.md",
            )
        elif self.a.push == "onesignal":
            d["onesignal_flutter"] = "^5.2.4"
            self._maybe_add_mode_m("onesignal", f"Set up OneSignal for {self.a.name_snake}")

        return d

    def _compose_dev_deps(self) -> dict[str, str]:
        d: dict[str, str] = {}
        # Linting
        if self.a.linting == "very_good_analysis":
            d["very_good_analysis"] = "^6.0.0"
        elif self.a.linting == "flutter_lints":
            d["flutter_lints"] = "^4.0.0"
        # Testing
        if self.a.testing == "bloc_test_mocktail":
            d["bloc_test"] = "^9.1.7"
            d["mocktail"] = "^1.0.4"
        # Codegen
        if self.a.persistence == "drift":
            d["drift_dev"] = "^2.20.0"
            d["build_runner"] = "^2.4.13"
        if self.a.persistence == "hive_ce":
            d["hive_ce_generator"] = "^1.7.0"
            d["build_runner"] = d.get("build_runner", "^2.4.13")
        if self.a.di == "get_it_injectable":
            d["injectable_generator"] = "^2.6.2"
            d["build_runner"] = d.get("build_runner", "^2.4.13")
        # Fastlane / launcher icons (Q8.5, EMB-321)
        if self.a.fastlane:
            d["flutter_launcher_icons"] = "^0.14.3"
        return d

    # -- step 6: analysis_options.yaml ------------------------------------
    def _generate_analysis_options(self) -> None:
        if self.a.linting == "very_good_analysis":
            content = (
                "include: package:very_good_analysis/analysis_options.yaml\n\n"
                "analyzer:\n"
                "  exclude:\n"
                "    - \"**/*.g.dart\"\n"
                "    - \"**/*.freezed.dart\"\n"
            )
        elif self.a.linting == "flutter_lints":
            content = (
                "include: package:flutter_lints/flutter.yaml\n"
            )
        else:  # embergard_custom — punt to user; emit a minimal scaffold
            content = (
                "# Embergard-style custom rules. Copy from your reference project and tune.\n"
                "include: package:flutter_lints/flutter.yaml\n\n"
                "linter:\n"
                "  rules:\n"
                "    # add explicit rule overrides here\n"
            )
        self._write(self.target / "analysis_options.yaml", content)

    # -- step 7: AppConfig (env-aware) ------------------------------------
    def _generate_app_config(self) -> None:
        """Embergard-pattern AppConfig with .dev() / .prod() (and .staging() if asked).

        EMB-315: moved from lib/config/app_config.dart →
        lib/src/core/config/env_config.dart so it lives under lib/src/ alongside
        all other project code. Import path: package:<name>/src/core/config/env_config.dart.

        FORGE-5.4 (EMB-289): AppConfig surfaces stub-detection predicates so
        callers can branch (or silence init) when running with offline stubs.
        """
        flavors = self._flavors()

        # Choose which fields AppConfig exposes based on the user's stack.
        # Each entry: (dart field, env key, dart type — currently always String).
        cfg_fields: list[tuple[str, str]] = []
        if self.a.backend == "supabase":
            cfg_fields.append(("supabaseUrl", "SUPABASE_URL"))
            cfg_fields.append(("supabaseAnonKey", "SUPABASE_ANON_KEY"))
        if self.a.backend == "custom_rest":
            cfg_fields.append(("apiBaseUrl", "API_BASE_URL"))
        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            cfg_fields.append(("sentryDsn", "SENTRY_DSN"))
        if self.a.analytics in ("mixpanel", "amplitude", "posthog"):
            cfg_fields.append(("analyticsToken", "ANALYTICS_TOKEN"))
        if self.a.push == "onesignal":
            cfg_fields.append(("oneSignalAppId", "ONESIGNAL_APP_ID"))
        if self.a.auth == "oidc_sso":
            cfg_fields.append(("oidcIssuerUrl", "OIDC_ISSUER_URL"))
            cfg_fields.append(("oidcClientId", "OIDC_CLIENT_ID"))
            cfg_fields.append(("oidcRedirectUri", "OIDC_REDIRECT_URI"))
        if self.a.auth == "oauth_google":
            cfg_fields.append(("googleOauthClientId", "GOOGLE_OAUTH_CLIENT_ID"))

        # Compose the constructor params and field declarations.
        const_params = "    required this.flavor,\n" + "".join(
            f"    required this.{name},\n" for name, _ in cfg_fields
        )
        field_decls = "  final String flavor;\n" + "".join(
            f"  final String {name};\n" for name, _ in cfg_fields
        )

        # Stub predicates (FORGE-5.4): how the app detects offline-stub mode
        # so it can skip / soft-fail SDK initialisation. Each predicate lines
        # up with a DEFER_STUBS entry, so empty values OR the canned stub
        # both signal "not configured".
        stub_predicates: list[str] = []
        if self.a.backend == "supabase":
            stub_predicates.append(
                "  /// True when Supabase keys are unset OR set to the stub "
                "values\n  /// emitted by scaffold-flutter for offline dev. "
                "Wrap your\n  /// `Supabase.initialize` call in "
                "`if (!config.isSupabaseStub) { ... }`\n"
                "  /// (or a try/catch) to avoid network init failures.\n"
                "  bool get isSupabaseStub =>\n"
                "      supabaseUrl.isEmpty ||\n"
                "      supabaseUrl == 'https://stub.supabase.co' ||\n"
                "      supabaseAnonKey.isEmpty ||\n"
                "      supabaseAnonKey == 'eyJ-stub-key';"
            )
        if self.a.backend == "custom_rest":
            stub_predicates.append(
                "  bool get isApiStub =>\n"
                "      apiBaseUrl.isEmpty || apiBaseUrl == 'https://stub.example.com';"
            )
        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            stub_predicates.append(
                "  /// Empty DSN is a Sentry SDK no-op — feed the value in directly.\n"
                "  bool get isSentryStub => sentryDsn.isEmpty;"
            )
        if self.a.auth == "oidc_sso":
            stub_predicates.append(
                "  bool get isOidcStub =>\n"
                "      oidcIssuerUrl.isEmpty ||\n"
                "      oidcIssuerUrl == 'https://stub-idp.example.com' ||\n"
                "      oidcClientId.isEmpty ||\n"
                "      oidcClientId == 'stub-client-id';"
            )

        # Per-flavor factory bodies. AppConfig._ is const, fields are pulled
        # from --dart-define-from-file=.env.<flavor>.
        factory_lines: list[str] = []
        for f in flavors:
            inner = "    flavor: '" + f + "',\n"
            for name, env_key in cfg_fields:
                inner += (
                    f"    {name}: const String.fromEnvironment('{env_key}', "
                    "defaultValue: ''),\n"
                )
            factory_lines.append(
                f"  static AppConfig _{f}() => AppConfig._(\n{inner}  );"
            )

        predicates_block = "\n\n".join(stub_predicates)
        if predicates_block:
            predicates_block = "\n\n" + predicates_block

        # EMB-315: AppEnvConfigs enum + setEnvironment / isConfigured / current
        # pattern so thin main_<flavor>.dart shims can just call
        # AppConfig.setEnvironment(AppEnvConfigs.<flavor>) before delegating.
        flavor_enum_values = ", ".join(flavors)
        env_configs_enum = (
            "/// Supported application environments.\n"
            "enum AppEnvConfigs { " + flavor_enum_values + " }\n"
        )

        env_map_entries = "\n".join(
            f"    AppEnvConfigs.{f}: _{f}()," for f in flavors
        )
        set_env_method = (
            "  static AppConfig? _instance;\n\n"
            "  /// Set the active environment. Call once per process, from main_<flavor>.dart.\n"
            "  static void setEnvironment(AppEnvConfigs env) {\n"
            + "".join(
                (
                    "    if (env == AppEnvConfigs." + f + ") {\n"
                    "      _instance = _" + f + "();\n"
                    "      return;\n"
                    "    }\n"
                )
                for f in flavors
            )
            + "  }\n\n"
            "  /// True once [setEnvironment] has been called.\n"
            "  static bool get isConfigured => _instance != null;\n\n"
            "  /// The active [AppConfig]. Throws if [setEnvironment] was not called.\n"
            "  static AppConfig get current {\n"
            "    assert(_instance != null, 'Call AppConfig.setEnvironment() first.');\n"
            "    return _instance!;\n"
            "  }\n"
        )

        body = (
            f"// AppConfig — environment-aware configuration for {self.a.name}.\n"
            "// Generated by plugins/forge/scripts/scaffold-flutter.sh\n"
            "// (FORGE-5.3 / EMB-288 + FORGE-5.4 / EMB-289 + EMB-315).\n"
            "// Values pulled from --dart-define-from-file=.env.<flavor>.\n"
            "//\n"
            "// Usage:\n"
            "//   1. lib/main_<flavor>.dart calls AppConfig.setEnvironment(AppEnvConfigs.<flavor>)\n"
            "//   2. lib/main.dart (bootstrap) reads AppConfig.current\n"
            "//\n"
            "// Stub-mode awareness: when the scaffolder ran in defer mode for an\n"
            "// integration, the .env files contain workable offline stubs. The\n"
            "// `isXStub` predicates below let app init code skip remote setup\n"
            "// without crashing.\n\n"
            + env_configs_enum
            + "\n"
            "class AppConfig {\n"
            "  AppConfig._({\n"
            f"{const_params}"
            "  });\n\n"
            f"{field_decls}\n"
            + set_env_method
            + "\n"
            + "\n\n".join(factory_lines)
            + predicates_block
            + "\n}\n"
        )
        # EMB-315: lives under lib/src/core/config/ (was lib/config/)
        self._write(self.target / "lib" / "src" / "core" / "config" / "env_config.dart", body)

    # -- step 8: .env.example + .env.<flavor> -----------------------------
    def _generate_env_files(self) -> None:
        """Write .env.example (committed, shape only) and per-flavor .env files
        with real or stub values.

        FORGE-5.4 (EMB-289) — values flow:
        - mode=provide → user-supplied values land in every flavor
        - mode=defer   → workable offline stubs from DEFER_STUBS land in
                         every flavor; SDK init must be stub-tolerant
        - mode=skip    → key omitted entirely (matches phase-4-7 'none')
        """
        keys = self._env_keys()

        # .env.example — committed; shape only, no values, with section headers.
        example_lines = [
            "# Generated by scaffold-flutter (FORGE-5.3 / EMB-288).",
            "# Shape reference for .env.<flavor> files. Values intentionally blank.",
            "# Per-integration credential resolution status is captured in",
            "# .claude/scaffold-report.json under `credentials_resolution`.",
            "",
        ]
        for section, ks in keys.items():
            example_lines.append(f"# === {section} ===")
            for k, comment in ks:
                if comment:
                    example_lines.append(f"# {comment}")
                example_lines.append(f"{k}=")
            example_lines.append("")
        self._write(self.target / ".env.example", "\n".join(example_lines))

        # .env.<flavor> — gitignored. Real values when provided, stubs otherwise.
        for flavor in self._flavors():
            lines = [
                f"# .env.{flavor} — gitignored.",
                "# Generated by scaffold-flutter (FORGE-5.4 / EMB-289).",
                "# Edit values directly; .env.example holds the canonical shape.",
                "",
            ]
            for section, ks in keys.items():
                lines.append(f"# === {section} ===")
                for k, comment in ks:
                    integration = self._integration_for_env_key(k)
                    mode = self.a.cred_mode(integration) if integration else "defer"
                    value = self._resolved_value_for(k, integration, flavor)
                    suffix_bits: list[str] = []
                    if integration:
                        suffix_bits.append(f"creds={integration}:{mode}")
                    if comment:
                        suffix_bits.append(comment)
                    suffix = (
                        f"  # {' | '.join(suffix_bits)}" if suffix_bits else ""
                    )
                    lines.append(f"{k}={value}{suffix}")
                lines.append("")
            self._write(self.target / f".env.{flavor}", "\n".join(lines))

    # ---- credential helpers used by env / config generators ----
    # Map .env key -> credentials-block integration key.
    # Same key may be referenced by multiple integrations (e.g. SUPABASE_URL
    # is owned by the `supabase` block whether the user picked it for backend,
    # auth, or both — single block, single mode).
    _ENV_KEY_OWNER: dict[str, str] = {
        "SUPABASE_URL": "supabase",
        "SUPABASE_ANON_KEY": "supabase",
        "SUPABASE_SERVICE_ROLE": "supabase",
        "API_BASE_URL": "custom_rest",
        "SENTRY_DSN": "sentry",
        "ANALYTICS_TOKEN": "analytics",
        "ONESIGNAL_APP_ID": "onesignal",
        "OIDC_ISSUER_URL": "oidc",
        "OIDC_CLIENT_ID": "oidc",
        "OIDC_REDIRECT_URI": "oidc",
        "OIDC_ADDITIONAL_SCOPES": "oidc",
        "GOOGLE_OAUTH_CLIENT_ID": "oauth_google",
    }

    # Map .env key -> values dict sub-key under the integration's "values".
    # Lets `provide` mode populate a multi-key block from a single user input
    # form (e.g. supabase.values = {url, anon_key, service_role}).
    _ENV_KEY_VALUE_FIELD: dict[str, str] = {
        "SUPABASE_URL": "url",
        "SUPABASE_ANON_KEY": "anon_key",
        "SUPABASE_SERVICE_ROLE": "service_role",
        "API_BASE_URL": "url",
        "SENTRY_DSN": "dsn",
        "ANALYTICS_TOKEN": "token",
        "ONESIGNAL_APP_ID": "app_id",
        "OIDC_ISSUER_URL": "issuer",
        "OIDC_CLIENT_ID": "client_id",
        "OIDC_REDIRECT_URI": "redirect_uri",
        "OIDC_ADDITIONAL_SCOPES": "scopes",
        "GOOGLE_OAUTH_CLIENT_ID": "client_id",
    }

    def _integration_for_env_key(self, env_key: str) -> str:
        return self._ENV_KEY_OWNER.get(env_key, "")

    def _resolved_value_for(
        self,
        env_key: str,
        integration: str,
        flavor: str,
    ) -> str:
        """Resolve the value to write to .env.<flavor> for `env_key`.

        Order:
        1. If integration has mode=provide and the matching value field is
           supplied (with optional flavor-suffix override), use it.
        2. Otherwise fall back to DEFER_STUBS — workable offline stub.
        3. Otherwise empty string.
        """
        if integration:
            mode = self.a.cred_mode(integration)
            if mode == "provide":
                vals = self.a.cred_values(integration)
                field_name = self._ENV_KEY_VALUE_FIELD.get(env_key, "")
                # Allow per-flavor override: e.g. {"url_prod": "..."}.
                flavor_specific = (
                    vals.get(f"{field_name}_{flavor}") if field_name else None
                )
                if flavor_specific:
                    return flavor_specific
                if field_name and vals.get(field_name):
                    return vals[field_name]
                # User said "provide" but didn't supply this specific field —
                # fall through to stub. The Mode M suppression remains in
                # effect; the user is on the hook to fill the gap.
        return DEFER_STUBS.get(env_key, "")

    def _env_keys(self) -> dict[str, list[tuple[str, str]]]:
        """Return ordered map of section -> [(key, optional_comment), …]."""
        out: dict[str, list[tuple[str, str]]] = {}

        backend: list[tuple[str, str]] = []
        if self.a.backend == "supabase":
            backend.append(("SUPABASE_URL", ""))
            backend.append(("SUPABASE_ANON_KEY", ""))
            backend.append(("SUPABASE_SERVICE_ROLE", "for backend ops only — do NOT ship in mobile builds"))
        elif self.a.backend == "custom_rest":
            backend.append(("API_BASE_URL", ""))
        # Firebase intentionally omits .env entries — uses google-services.json
        if backend:
            out["Backend"] = backend

        auth: list[tuple[str, str]] = []
        if self.a.auth == "oidc_sso":
            idp = self.a.oidc_idp or "OIDC"
            auth.append(("OIDC_ISSUER_URL", f"IDP: {idp}"))
            auth.append(("OIDC_CLIENT_ID", ""))
            auth.append(("OIDC_REDIRECT_URI", ""))
            auth.append(("OIDC_ADDITIONAL_SCOPES", "space-separated, optional"))
        elif self.a.auth == "oauth_google":
            auth.append(("GOOGLE_OAUTH_CLIENT_ID", ""))
        if auth:
            out["Auth"] = auth

        obs: list[tuple[str, str]] = []
        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            obs.append(("SENTRY_DSN", ""))
        if self.a.analytics in ("mixpanel", "amplitude", "posthog"):
            obs.append(("ANALYTICS_TOKEN", f"for {self.a.analytics}"))
        if self.a.push == "onesignal":
            obs.append(("ONESIGNAL_APP_ID", ""))
        if obs:
            out["Observability"] = obs

        return out

    # -- step 8b: lib/src/app/<name>_app.dart (root widget) ---------------
    #    EMB-315: the root MaterialApp.router widget lives here, not inlined
    #    inside a main_<flavor>.dart. Keeps main.dart focused on bootstrap.
    # -------------------------------------------------------------------------
    def _generate_app_widget(self) -> None:
        """Write lib/src/app/<name>_app.dart — root MaterialApp.router widget.

        EMB-315: mirrors the b2b-mobile-app AddupApp pattern. The widget is a
        StatelessWidget (skeleton) — the dev adds BLoC providers, router wiring,
        theme, and l10n delegates as the project grows.
        """
        pkg = self.a.name_snake
        name_pascal = "".join(w.capitalize() for w in pkg.split("_"))

        imports = [
            "import 'package:flutter/material.dart';",
        ]
        if self.a.navigation == "go_router":
            imports.append("import 'package:go_router/go_router.dart';")
            # Import the real HomePage generated by _generate_home_feature.
            imports.append(
                f"import 'package:{pkg}/src/features/home/presentation/pages/home_page.dart';"
            )

        # Build the widget body.
        if self.a.navigation == "go_router":
            router_field = (
                "\n  /// Application router — initial route is /home (EMB-316).\n"
                "  static final _router = GoRouter(\n"
                "    initialLocation: '/home',\n"
                "    routes: [\n"
                "      GoRoute(\n"
                "        path: '/home',\n"
                f"        builder: (context, state) => const HomePage(),\n"
                "      ),\n"
                "    ],\n"
                "  );\n"
            )
            build_return = (
                f"    return MaterialApp.router(\n"
                f"      title: '{self.a.name}',\n"
                f"      theme: ThemeData(\n"
                f"        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),\n"
                f"        useMaterial3: {str(self.a.theme == 'material3').lower()},\n"
                f"      ),\n"
                f"      routerConfig: _router,\n"
                f"      debugShowCheckedModeBanner: false,\n"
                f"    );"
            )
        else:
            router_field = ""
            # Non-go_router path: import and use HomePage directly.
            imports.append(
                f"import 'package:{pkg}/src/features/home/presentation/pages/home_page.dart';"
            )
            build_return = (
                f"    return MaterialApp(\n"
                f"      title: '{self.a.name}',\n"
                f"      theme: ThemeData(\n"
                f"        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),\n"
                f"        useMaterial3: {str(self.a.theme == 'material3').lower()},\n"
                f"      ),\n"
                f"      home: const HomePage(),\n"
                f"      debugShowCheckedModeBanner: false,\n"
                f"    );"
            )

        body = (
            "\n".join(sorted(imports))
            + "\n\n"
            f"/// Root application widget for {self.a.name}.\n"
            "///\n"
            "/// Configures:\n"
            "/// - Theme (Material 3)\n"
            "/// - Navigation (router)\n"
            "/// Add BLoC providers, localization delegates, and auth guards here\n"
            "/// as the project grows.\n"
            f"class {name_pascal}App extends StatelessWidget {{\n"
            f"  const {name_pascal}App({{super.key}});\n"
            f"{router_field}\n"
            "  @override\n"
            "  Widget build(BuildContext context) {\n"
            f"{build_return}\n"
            "  }\n"
            "}\n"
        )

        path = self.target / "lib" / "src" / "app" / f"{pkg}_app.dart"
        self._write(path, body)

    # -- step 8c: lib/src/core/di/service_locator.dart stub ------------------
    #    EMB-315: main.dart bootstrap imports setupServiceLocator when get_it
    #    is selected. Generate a minimal stub so flutter analyze passes.
    # -------------------------------------------------------------------------
    def _generate_di_stub(self) -> None:
        """Write a minimal service_locator.dart stub under lib/src/core/di/.

        Only emitted when DI is get_it or get_it_injectable. The stub is a
        placeholder — dev fills in real registrations as features are added.
        The template's lib/src/ does not ship a service_locator.dart (it's
        project-specific), so we generate one here (EMB-315).
        """
        if self.a.di not in ("get_it", "get_it_injectable"):
            return

        pkg = self.a.name_snake
        body = (
            f"import 'package:get_it/get_it.dart';\n\n"
            f"import 'package:{pkg}/src/features/home/di/home_module.dart';\n"
            f"import 'package:{pkg}/src/shared/user/di/user_module.dart';\n\n"
            "/// Global service locator instance.\n"
            "final getIt = GetIt.instance;\n\n"
            "/// Register all dependencies.\n"
            "///\n"
            "/// Called once during app bootstrap in lib/main.dart before runApp.\n"
            "/// Each feature/shared module exposes a register*Module() function\n"
            "/// that is called here — add new modules as the project grows.\n"
            "Future<void> setupServiceLocator() async {\n"
            "  registerUserModule();\n"
            "  registerHomeModule();\n"
            "}\n"
        )
        self._write(
            self.target / "lib" / "src" / "core" / "di" / "service_locator.dart",
            body,
        )

    # -- step 8d: lib/src/features/home/ — regular feature skeleton (EMB-316) -
    #    Generates a BLoC-driven home feature following clean-arch layering:
    #      presentation/pages, presentation/bloc, domain/repositories,
    #      data/repositories, di.
    #    Guarded: only emitted when state_mgmt=bloc and di in (get_it,
    #    get_it_injectable). For other combos we emit a placeholder
    #    (no BLoC, no DI registration) so the project still compiles.
    # -------------------------------------------------------------------------
    def _generate_home_feature(self) -> None:  # noqa: PLR0912, PLR0915
        """Generate lib/src/features/home/ with clean-arch layers."""
        pkg = self.a.name_snake
        base = self.target / "lib" / "src" / "features" / "home"

        use_bloc = self.a.state_mgmt == "bloc"
        use_get_it = self.a.di in ("get_it", "get_it_injectable")

        # ---- domain/repositories/home_repository.dart ----------------------
        self._write(
            base / "domain" / "repositories" / "home_repository.dart",
            (
                f"import 'package:{pkg}/src/shared/user/domain/models/user.dart';\n\n"
                "/// Contract for the home feature's data operations.\n"
                "abstract class HomeRepository {\n"
                "  /// Returns a mock current user for display.\n"
                "  Future<User> getCurrentUser();\n"
                "}\n"
            ),
        )

        # ---- data/repositories/home_repository_impl.dart -------------------
        self._write(
            base / "data" / "repositories" / "home_repository_impl.dart",
            (
                f"import 'package:{pkg}/src/features/home/domain/repositories/home_repository.dart';\n"
                f"import 'package:{pkg}/src/shared/user/domain/models/user.dart';\n\n"
                "/// Default implementation of [HomeRepository].\n"
                "///\n"
                "/// Returns in-memory stub data. Replace with a real data\n"
                "/// source (Supabase, REST, local DB) as the project grows.\n"
                "class HomeRepositoryImpl implements HomeRepository {\n"
                "  const HomeRepositoryImpl();\n\n"
                "  @override\n"
                "  Future<User> getCurrentUser() async {\n"
                "    // Simulate an async fetch with a short delay.\n"
                "    await Future<void>.delayed(const Duration(milliseconds: 300));\n"
                "    return const User(\n"
                "      id: 'stub-id',\n"
                "      email: 'dev@example.com',\n"
                "      name: 'Dev User',\n"
                "    );\n"
                "  }\n"
                "}\n"
            ),
        )

        # ---- presentation/bloc/ --------------------------------------------
        if use_bloc:
            # home_event.dart
            self._write(
                base / "presentation" / "bloc" / "home_event.dart",
                (
                    "import 'package:equatable/equatable.dart';\n\n"
                    "/// Base class for all HomeBloc events.\n"
                    "sealed class HomeEvent extends Equatable {\n"
                    "  const HomeEvent();\n\n"
                    "  @override\n"
                    "  List<Object?> get props => [];\n"
                    "}\n\n"
                    "/// Triggered when the home screen is first opened.\n"
                    "final class HomeStarted extends HomeEvent {\n"
                    "  const HomeStarted();\n"
                    "}\n"
                ),
            )

            # home_state.dart
            self._write(
                base / "presentation" / "bloc" / "home_state.dart",
                (
                    "import 'package:equatable/equatable.dart';\n\n"
                    f"import 'package:{pkg}/src/shared/user/domain/models/user.dart';\n\n"
                    "/// Base class for all HomeBloc states.\n"
                    "sealed class HomeState extends Equatable {\n"
                    "  const HomeState();\n\n"
                    "  @override\n"
                    "  List<Object?> get props => [];\n"
                    "}\n\n"
                    "/// Initial loading state — shown while fetching the user.\n"
                    "final class HomeLoading extends HomeState {\n"
                    "  const HomeLoading();\n"
                    "}\n\n"
                    "/// Successfully loaded state — carries the current [user].\n"
                    "final class HomeLoaded extends HomeState {\n"
                    "  const HomeLoaded({required this.user});\n\n"
                    "  final User user;\n\n"
                    "  @override\n"
                    "  List<Object?> get props => [user];\n"
                    "}\n\n"
                    "/// Error state — carries a human-readable [message].\n"
                    "final class HomeError extends HomeState {\n"
                    "  const HomeError({required this.message});\n\n"
                    "  final String message;\n\n"
                    "  @override\n"
                    "  List<Object?> get props => [message];\n"
                    "}\n"
                ),
            )

            # home_bloc.dart
            self._write(
                base / "presentation" / "bloc" / "home_bloc.dart",
                (
                    "import 'package:flutter_bloc/flutter_bloc.dart';\n\n"
                    f"import 'package:{pkg}/src/features/home/domain/repositories/home_repository.dart';\n"
                    f"import 'package:{pkg}/src/features/home/presentation/bloc/home_event.dart';\n"
                    f"import 'package:{pkg}/src/features/home/presentation/bloc/home_state.dart';\n\n"
                    "/// BLoC for the home feature.\n"
                    "///\n"
                    "/// Handles [HomeStarted] → emits [HomeLoading] then [HomeLoaded]\n"
                    "/// (or [HomeError] on failure).\n"
                    "class HomeBloc extends Bloc<HomeEvent, HomeState> {\n"
                    "  HomeBloc({required HomeRepository repository})\n"
                    "      : _repository = repository,\n"
                    "        super(const HomeLoading()) {\n"
                    "    on<HomeStarted>(_onHomeStarted);\n"
                    "  }\n\n"
                    "  final HomeRepository _repository;\n\n"
                    "  Future<void> _onHomeStarted(\n"
                    "    HomeStarted event,\n"
                    "    Emitter<HomeState> emit,\n"
                    "  ) async {\n"
                    "    emit(const HomeLoading());\n"
                    "    try {\n"
                    "      final user = await _repository.getCurrentUser();\n"
                    "      emit(HomeLoaded(user: user));\n"
                    "    } catch (e) {\n"
                    "      emit(HomeError(message: e.toString()));\n"
                    "    }\n"
                    "  }\n"
                    "}\n"
                ),
            )

        # ---- presentation/pages/home_page.dart -----------------------------
        if use_bloc:
            home_page_body = (
                "import 'package:flutter/material.dart';\n"
                "import 'package:flutter_bloc/flutter_bloc.dart';\n\n"
                f"import 'package:{pkg}/src/core/di/service_locator.dart';\n"
                f"import 'package:{pkg}/src/features/home/presentation/bloc/home_bloc.dart';\n"
                f"import 'package:{pkg}/src/features/home/presentation/bloc/home_event.dart';\n"
                f"import 'package:{pkg}/src/features/home/presentation/bloc/home_state.dart';\n\n"
                "/// Home screen — entry point of the app after launch.\n"
                "///\n"
                "/// Creates a [HomeBloc] from the get_it service locator and\n"
                "/// dispatches [HomeStarted] immediately, triggering the\n"
                "/// loading → loaded/error state transition.\n"
                "class HomePage extends StatelessWidget {\n"
                "  const HomePage({super.key});\n\n"
                "  @override\n"
                "  Widget build(BuildContext context) {\n"
                "    return BlocProvider(\n"
                "      create: (_) => getIt<HomeBloc>()..add(const HomeStarted()),\n"
                "      child: const _HomeView(),\n"
                "    );\n"
                "  }\n"
                "}\n\n"
                "class _HomeView extends StatelessWidget {\n"
                "  const _HomeView();\n\n"
                "  @override\n"
                "  Widget build(BuildContext context) {\n"
                "    return Scaffold(\n"
                "      appBar: AppBar(title: const Text('Home')),\n"
                "      body: BlocBuilder<HomeBloc, HomeState>(\n"
                "        builder: (context, state) {\n"
                "          return switch (state) {\n"
                "            HomeLoading() => const Center(\n"
                "                child: CircularProgressIndicator(),\n"
                "              ),\n"
                "            HomeLoaded(:final user) => Center(\n"
                "                child: Column(\n"
                "                  mainAxisSize: MainAxisSize.min,\n"
                "                  children: [\n"
                "                    const Icon(Icons.home, size: 64),\n"
                "                    const SizedBox(height: 16),\n"
                "                    Text(\n"
                "                      'Hello, ${user.name}!',\n"
                "                      style: Theme.of(context).textTheme.headlineSmall,\n"
                "                    ),\n"
                "                    Text(user.email),\n"
                "                  ],\n"
                "                ),\n"
                "              ),\n"
                "            HomeError(:final message) => Center(\n"
                "                child: Text('Error: $message'),\n"
                "              ),\n"
                "          };\n"
                "        },\n"
                "      ),\n"
                "    );\n"
                "  }\n"
                "}\n"
            )
        else:
            # Minimal stateless placeholder for non-bloc stacks.
            home_page_body = (
                "import 'package:flutter/material.dart';\n\n"
                "/// Home screen — replace with your state management solution.\n"
                "class HomePage extends StatelessWidget {\n"
                "  const HomePage({super.key});\n\n"
                "  @override\n"
                "  Widget build(BuildContext context) {\n"
                "    return Scaffold(\n"
                "      appBar: AppBar(title: const Text('Home')),\n"
                "      body: const Center(child: Text('Welcome home!')),\n"
                "    );\n"
                "  }\n"
                "}\n"
            )
        self._write(
            base / "presentation" / "pages" / "home_page.dart",
            home_page_body,
        )

        # ---- di/home_module.dart -------------------------------------------
        if use_bloc and use_get_it:
            di_body = (
                "import 'package:get_it/get_it.dart';\n\n"
                f"import 'package:{pkg}/src/features/home/data/repositories/home_repository_impl.dart';\n"
                f"import 'package:{pkg}/src/features/home/domain/repositories/home_repository.dart';\n"
                f"import 'package:{pkg}/src/features/home/presentation/bloc/home_bloc.dart';\n\n"
                "final _getIt = GetIt.instance;\n\n"
                "/// Registers home feature dependencies.\n"
                "void registerHomeModule() {\n"
                "  _getIt\n"
                "    ..registerLazySingleton<HomeRepository>(\n"
                "      () => const HomeRepositoryImpl(),\n"
                "    )\n"
                "    ..registerFactory<HomeBloc>(\n"
                "      () => HomeBloc(repository: _getIt<HomeRepository>()),\n"
                "    );\n"
                "}\n"
            )
        else:
            di_body = (
                "/// Registers home feature dependencies.\n"
                "///\n"
                "/// This stub is emitted when DI is not get_it. Wire manually.\n"
                "void registerHomeModule() {\n"
                "  // No registrations — add your DI wiring here.\n"
                "}\n"
            )
        self._write(base / "di" / "home_module.dart", di_body)

    # -- step 8e: lib/src/shared/user/ — shared feature skeleton (EMB-316) ---
    #    data/domain only — no presentation layer (shared features don't ship UI).
    #    Ships always as proof of shared-vs-feature layering.
    # -------------------------------------------------------------------------
    def _generate_shared_user_feature(self) -> None:
        """Generate lib/src/shared/user/ with data and domain layers."""
        pkg = self.a.name_snake
        base = self.target / "lib" / "src" / "shared" / "user"

        use_get_it = self.a.di in ("get_it", "get_it_injectable")

        # ---- domain/models/user.dart ---------------------------------------
        self._write(
            base / "domain" / "models" / "user.dart",
            (
                "import 'package:equatable/equatable.dart';\n\n"
                "/// Domain model representing an authenticated user.\n"
                "///\n"
                "/// Pure business object — no serialization logic here.\n"
                "/// Serialization lives in the data layer (DTOs / mappers).\n"
                "class User extends Equatable {\n"
                "  const User({\n"
                "    required this.id,\n"
                "    required this.email,\n"
                "    required this.name,\n"
                "  });\n\n"
                "  final String id;\n"
                "  final String email;\n"
                "  final String name;\n\n"
                "  @override\n"
                "  List<Object?> get props => [id, email, name];\n"
                "}\n"
            ),
        )

        # ---- domain/repositories/user_repository.dart ----------------------
        self._write(
            base / "domain" / "repositories" / "user_repository.dart",
            (
                f"import 'package:{pkg}/src/shared/user/domain/models/user.dart';\n\n"
                "/// Contract for user data operations.\n"
                "///\n"
                "/// Implementations live in the data layer. The domain layer\n"
                "/// depends only on this interface — never on a concrete class.\n"
                "abstract class UserRepository {\n"
                "  /// Fetch the current authenticated user by [id].\n"
                "  Future<User> getUserById(String id);\n"
                "}\n"
            ),
        )

        # ---- data/repositories/user_repository_impl.dart -------------------
        self._write(
            base / "data" / "repositories" / "user_repository_impl.dart",
            (
                f"import 'package:{pkg}/src/shared/user/domain/models/user.dart';\n"
                f"import 'package:{pkg}/src/shared/user/domain/repositories/user_repository.dart';\n\n"
                "/// Default implementation of [UserRepository].\n"
                "///\n"
                "/// Stub: returns in-memory data. Replace with a real backend\n"
                "/// client (Supabase, REST, etc.) as the project grows.\n"
                "class UserRepositoryImpl implements UserRepository {\n"
                "  const UserRepositoryImpl();\n\n"
                "  @override\n"
                "  Future<User> getUserById(String id) async {\n"
                "    await Future<void>.delayed(const Duration(milliseconds: 100));\n"
                "    return User(id: id, email: 'stub@example.com', name: 'Stub User');\n"
                "  }\n"
                "}\n"
            ),
        )

        # ---- di/user_module.dart -------------------------------------------
        if use_get_it:
            di_body = (
                "import 'package:get_it/get_it.dart';\n\n"
                f"import 'package:{pkg}/src/shared/user/data/repositories/user_repository_impl.dart';\n"
                f"import 'package:{pkg}/src/shared/user/domain/repositories/user_repository.dart';\n\n"
                "final _getIt = GetIt.instance;\n\n"
                "/// Registers shared user dependencies.\n"
                "void registerUserModule() {\n"
                "  _getIt.registerLazySingleton<UserRepository>(\n"
                "    () => const UserRepositoryImpl(),\n"
                "  );\n"
                "}\n"
            )
        else:
            di_body = (
                "/// Registers shared user dependencies.\n"
                "///\n"
                "/// Stub for non-get_it stacks — wire manually.\n"
                "void registerUserModule() {\n"
                "  // No registrations — add your DI wiring here.\n"
                "}\n"
            )
        self._write(base / "di" / "user_module.dart", di_body)

    # -- step 9: lib/main.dart (real bootstrap) + lib/main_<flavor>.dart shims
    #    EMB-315: restructured so main.dart is the real entry point and
    #    main_<flavor>.dart files are thin ≤8-line shims that set the
    #    environment and delegate to app.main(). The root widget (<Name>App)
    #    lives in lib/src/app/<name>_app.dart (written by _generate_app_widget).
    # -------------------------------------------------------------------------
    def _generate_main_entries(self) -> None:
        # Thin flavor shims — each is ≤8 lines.
        for flavor in self._flavors():
            body = self._flavor_shim_body(flavor)
            self._write(self.target / "lib" / f"main_{flavor}.dart", body)

        # Real bootstrap — lib/main.dart.
        self._write(self.target / "lib" / "main.dart", self._main_bootstrap_body())

    def _flavor_shim_body(self, flavor: str) -> str:
        """Compose a thin lib/main_<flavor>.dart shim (EMB-315).

        Sets the environment via AppConfig.setEnvironment, then delegates to
        the shared app.main() defined in lib/main.dart. ≤8 lines by design.
        """
        pkg = self.a.name_snake
        # Sort imports alphabetically within the package: section.
        # main.dart (shorter path) must come before src/... alphabetically.
        return (
            f"import 'package:{pkg}/main.dart' as app;\n"
            f"import 'package:{pkg}/src/core/config/env_config.dart';\n"
            "\n"
            f"/// {flavor.capitalize()} environment entry point.\n"
            f"/// Run with: flutter run --flavor {flavor} -t lib/main_{flavor}.dart"
            f" --dart-define-from-file=.env.{flavor}\n"
            "void main() {\n"
            f"  AppConfig.setEnvironment(AppEnvConfigs.{flavor});\n"
            "  app.main();\n"
            "}\n"
        )

    def _main_bootstrap_body(self) -> str:
        """Compose lib/main.dart — the real bootstrap entry point (EMB-315).

        Contains: WidgetsFlutterBinding.ensureInitialized, logging setup,
        conditional SDK init (Supabase / Sentry) guarded by AppConfig stub
        predicates, get_it service locator init, then runApp(<Name>App).

        FORGE-5.4 (EMB-289): stub-tolerant — SDK init is skipped gracefully
        when running with deferred offline stubs in .env.<flavor>.
        """
        pkg = self.a.name_snake
        name_pascal = "".join(w.capitalize() for w in pkg.split("_"))

        # Collect all imports then sort alphabetically.
        # very_good_analysis's directives_ordering wants package: imports
        # sorted alphabetically within the package: section.
        raw_imports: list[str] = [
            "import 'package:flutter/material.dart';",
            "import 'package:logging/logging.dart';",
            f"import 'package:{pkg}/src/app/{pkg}_app.dart';",
            f"import 'package:{pkg}/src/core/config/env_config.dart';",
        ]
        if self.a.di in ("get_it", "get_it_injectable"):
            raw_imports.append(
                f"import 'package:{pkg}/src/core/di/service_locator.dart';"
            )
        if self.a.backend == "supabase":
            raw_imports.append("import 'package:supabase_flutter/supabase_flutter.dart';")
        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            raw_imports.append("import 'package:sentry_flutter/sentry_flutter.dart';")
        imports = sorted(raw_imports)

        # Build init body lines.
        init_lines: list[str] = [
            "  WidgetsFlutterBinding.ensureInitialized();",
            "",
            "  _setupLogging();",
            "",
            "  // Guard: flavor must be set by the entry-point shim before main() is called.",
            "  if (!AppConfig.isConfigured) {",
            "    AppConfig.setEnvironment(AppEnvConfigs.dev);",
            "  }",
            "  final config = AppConfig.current;",
        ]

        if self.a.backend == "supabase":
            init_lines += [
                "",
                "  if (config.isSupabaseStub) {",
                "    _log.warning(",
                "      'Supabase keys are stubs (defer mode). Skipping init; '",
                "      'app runs offline. Replace .env.<flavor> values to enable.',",
                "    );",
                "  } else {",
                "    try {",
                "      await Supabase.initialize(",
                "        url: config.supabaseUrl,",
                "        anonKey: config.supabaseAnonKey,",
                "      );",
                "    } catch (e, st) {",
                "      _log.severe(",
                "        'Supabase.initialize failed; continuing offline.',",
                "        e,",
                "        st,",
                "      );",
                "    }",
                "  }",
            ]

        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            init_lines += [
                "",
                "  if (config.isSentryStub) {",
                "    _log.info('Sentry DSN empty (defer mode); SDK no-ops.');",
                "  } else {",
                "    try {",
                "      await SentryFlutter.init(",
                "        (options) {",
                "          options",
                "            ..dsn = config.sentryDsn",
                "            ..environment = config.flavor;",
                "        },",
                "      );",
                "    } catch (e, st) {",
                "      _log.severe(",
                "        'SentryFlutter.init failed; continuing without Sentry.',",
                "        e,",
                "        st,",
                "      );",
                "    }",
                "  }",
            ]

        if self.a.di in ("get_it", "get_it_injectable"):
            init_lines += [
                "",
                "  await setupServiceLocator();",
            ]

        init_lines += [
            "",
            f"  runApp(const {name_pascal}App());",
        ]

        init_body = "\n".join(init_lines)

        return (
            "\n".join(imports)
            + "\n\n"
            "final _log = Logger('main');\n\n"
            "/// Application bootstrap.\n"
            "///\n"
            "/// Called by the flavor-specific entry-point shims\n"
            "/// (lib/main_<flavor>.dart) after AppConfig.setEnvironment.\n"
            "Future<void> main() async {\n"
            f"{init_body}\n"
            "}\n\n"
            "void _setupLogging() {\n"
            "  Logger.root\n"
            "    ..level = Level.ALL\n"
            "    ..onRecord.listen((record) {\n"
            "      // ignore: avoid_print\n"
            "      print(\n"
            "        '[${record.level.name}] '\n"
            "        '${record.loggerName}: '\n"
            "        '${record.message}',\n"
            "      );\n"
            "    });\n"
            "}\n"
        )

    def _flavors(self) -> list[str]:
        if self.a.environments == "dev":
            return ["dev"]
        if self.a.environments == "dev_staging_prod":
            return ["dev", "staging", "prod"]
        return ["dev", "prod"]

    # -- step 10: IDE configs ---------------------------------------------
    def _generate_ide_configs(self) -> None:
        if self.a.ide in ("none",):
            return
        if self.a.ide in ("both", "vscode"):
            self._generate_vscode_launch()
        if self.a.ide in ("both", "idea"):
            self._generate_idea_run_configs()

    def _generate_vscode_launch(self) -> None:
        configurations: list[dict[str, Any]] = []
        for flavor in self._flavors():
            for mode in ("debug", "release"):
                configurations.append({
                    "name": f"{flavor} ({mode})",
                    "request": "launch",
                    "type": "dart",
                    "program": f"lib/main_{flavor}.dart",
                    "args": [
                        "--flavor", flavor,
                        f"--dart-define-from-file=.env.{flavor}",
                        *(["--release"] if mode == "release" else []),
                    ],
                })
        body = json.dumps({"version": "0.2.0", "configurations": configurations}, indent=2)
        self._write(self.target / ".vscode" / "launch.json", body + "\n")

    def _generate_idea_run_configs(self) -> None:
        for flavor in self._flavors():
            for mode in ("Debug", "Release"):
                name = f"{flavor}_{mode}"
                xml = (
                    f'<component name="ProjectRunConfigurationManager">\n'
                    f'  <configuration default="false" name="{flavor} ({mode})" '
                    f'type="FlutterRunConfigurationType" factoryName="Flutter">\n'
                    f'    <option name="filePath" value="$PROJECT_DIR$/lib/main_{flavor}.dart" />\n'
                    f'    <option name="buildFlavor" value="{flavor}" />\n'
                    f'    <option name="additionalArgs" '
                    f'value="--dart-define-from-file=.env.{flavor}'
                    f'{" --release" if mode == "Release" else ""}" />\n'
                    f'    <method v="2" />\n'
                    f'  </configuration>\n'
                    f'</component>\n'
                )
                self._write(self.target / ".idea" / "runConfigurations" / f"{name}.xml", xml)

    # -- step 11: assets skeleton (EMB-317) ---------------------------------
    def _generate_assets(self) -> None:
        """Write asset folder skeletons and AppImages/AppIcons/AppAnimations constants.

        Creates:
          assets/images/.gitkeep
          assets/icons/.gitkeep
          assets/animations/.gitkeep
          lib/src/core/constants/app_assets.dart  (3 classes, 2-3 placeholders each)
        """
        # .gitkeep files so git tracks the otherwise-empty asset folders
        for subfolder in ("images", "icons", "animations"):
            self._write(self.target / "assets" / subfolder / ".gitkeep", "")

        dart = (
            "// Asset path constants. Use these instead of hardcoding paths in widgets.\n"
            "// Regenerated by scaffold — extend as needed.\n\n"
            "class AppImages {\n"
            "  AppImages._();\n\n"
            "  static const _prefix = 'assets/images';\n\n"
            "  static const logo = '$_prefix/logo.png';\n"
            "  static const placeholder = '$_prefix/placeholder.png';\n"
            "  static const onboardingHero = '$_prefix/onboarding_hero.png';\n"
            "}\n\n"
            "class AppIcons {\n"
            "  AppIcons._();\n\n"
            "  static const _prefix = 'assets/icons';\n\n"
            "  static const appIcon = '$_prefix/app_icon.svg';\n"
            "  static const home = '$_prefix/home.svg';\n"
            "  static const profile = '$_prefix/profile.svg';\n"
            "}\n\n"
            "class AppAnimations {\n"
            "  AppAnimations._();\n\n"
            "  static const _prefix = 'assets/animations';\n\n"
            "  static const loading = '$_prefix/loading.json';\n"
            "  static const success = '$_prefix/success.json';\n"
            "  static const empty = '$_prefix/empty.json';\n"
            "}\n"
        )
        self._write(
            self.target / "lib" / "src" / "core" / "constants" / "app_assets.dart",
            dart,
        )

    # -- step 11b: theme tokens override (EMB-320) ------------------------
    def _generate_theme_overrides(self) -> None:
        """Write `<core>/theme/<project>_theme.dart` from the resolved IR.

        Q6.2 channels (file / figma / brainstorm / defaults):
          - "defaults":  no-op; keep flutter-template base tokens only.
          - "file":      parse `a.theme_tokens_source` into the IR.
          - "figma":     consume `a.theme_tokens_ir` (interview agent supplied).
          - "brainstorm":consume `a.theme_tokens_ir` (interview agent supplied).

        The generated file imports the base AppSpacing / AppRadius /
        AppTypography classes that ship with flutter-template and provides
        a `<Name>Theme` class with `lightTheme`/`darkTheme` getters that
        override only the supplied tokens. Unset tokens fall back to the
        base classes (no values are duplicated).
        """
        if self.a.theme_tokens == "defaults":
            return
        # Cupertino swap is a STUB; skip override generation either way.
        if self.a.theme == "cupertino":
            return

        ir: dict[str, Any] = {}
        if self.a.theme_tokens == "file":
            try:
                ir = parse_tokens_from_file(Path(self.a.theme_tokens_source))
            except (FileNotFoundError, ValueError) as exc:
                # Graceful fallback: log + emit Mode M, keep scaffolding.
                self._log(
                    f"theme tokens parse failed ({exc}); falling back to defaults"
                )
                self._add_mode_m(
                    f"Wire theme tokens manually in {self.a.name_snake} "
                    f"(scaffolder could not parse {self.a.theme_tokens_source})",
                )
                return
        else:  # figma | brainstorm
            ir = self.a.theme_tokens_ir or {}

        # Skip generation if IR has no real overrides (caller passed empty dict).
        non_empty = any(
            isinstance(v, dict) and v for v in ir.values()
        )
        if not non_empty:
            self._log("theme tokens IR empty; keeping flutter-template defaults")
            return

        body = self._render_theme_dart(ir)
        path = self.core_dir / "theme" / f"{self.a.name_snake}_theme.dart"
        self._write(path, body)
        self._log(
            f"wrote {path.relative_to(self.target)} "
            f"(channel={self.a.theme_tokens}, "
            f"colors={len(ir.get('colors') or {})}, "
            f"radius={len(ir.get('radius') or {})}, "
            f"typography={len(ir.get('typography') or {})})"
        )

    def _render_theme_dart(self, ir: dict[str, Any]) -> str:
        """Render the override-style `<project>_theme.dart` body.

        The generated class is intentionally minimal — it exposes only the
        overrides the user actually supplied. Devs can extend it later.
        """
        pkg = self.a.name_snake
        name_pascal = "".join(w.capitalize() for w in pkg.split("_"))
        class_name = f"{name_pascal}Theme"

        colors: dict[str, str] = ir.get("colors") or {}
        radii: dict[str, int] = ir.get("radius") or {}
        typo: dict[str, Any] = ir.get("typography") or {}
        family = typo.get("family") if isinstance(typo, dict) else None
        # Trim family from typo iterator to avoid treating it as a textStyle.
        text_styles = {k: v for k, v in typo.items() if k != "family" and isinstance(v, dict)}

        def _hex_to_color(value: str, *, const_prefix: bool = True) -> str:
            """Render `#RRGGBB` / `#AARRGGBB` as a Dart Color literal.

            With `const_prefix=True` returns `const Color(0x…)` (for use inside
            expressions, e.g. argument lists). With False returns `Color(0x…)`
            (for use in a `const`-declared field where the outer `const`
            already applies — avoids prefer_const_constructors lint).
            """
            body = value.lstrip("#")
            if len(body) == 6:
                body = "FF" + body
            literal = f"Color(0x{body.upper()})"
            return f"const {literal}" if const_prefix else literal

        # Imports: material always; google_fonts only when typography family
        # override is supplied (otherwise the file would have an unused import
        # and trip very_good_analysis).
        imports = [
            "import 'package:flutter/material.dart';",
        ]
        if family:
            imports.append("import 'package:google_fonts/google_fonts.dart';")

        out: list[str] = []
        out.append("// GENERATED by scaffold-flutter.sh (EMB-320 theme tokens).")
        out.append(f"// Channel: {self.a.theme_tokens}")
        if self.a.theme_tokens == "file" and self.a.theme_tokens_source:
            out.append(f"// Source : {self.a.theme_tokens_source}")
        out.append("//")
        out.append("// Overrides the flutter-template base tokens; any field not set")
        out.append("// here falls back to AppRadius / AppTypography / Material defaults.")
        out.append("")
        out.extend(sorted(imports))
        out.append("")
        out.append(f"/// Project theme overrides for {self.a.name}.")
        out.append("///")
        out.append("/// Use `AppTheme` (flutter-template) for general Material theming;")
        out.append("/// this class exposes the specific tokens supplied at scaffold time.")
        out.append(f"abstract final class {class_name} {{")
        # Private constructor first (very_good_analysis: sort_constructors_first).
        out.append(f"  {class_name}._();")
        out.append("")

        # -- Color overrides
        if colors:
            out.append("  // -------- Colors --------")
            slot_order = [
                "primary", "secondary", "surface", "background",
                "error", "onPrimary", "outline",
            ]
            for slot in slot_order:
                if slot in colors:
                    out.append(f"  /// {slot} colour token (from scaffold input).")
                    out.append(
                        f"  static const Color {slot} = "
                        f"{_hex_to_color(colors[slot], const_prefix=False)};"
                    )
            out.append("")
            # ColorScheme constructor for light mode (devs override in app widget).
            seed = colors.get("primary", "#1565C0")
            out.append("  /// Convenience light ColorScheme derived from the overridden seed.")
            out.append(
                "  static ColorScheme get lightColorScheme => ColorScheme.fromSeed("
            )
            out.append(f"        seedColor: {_hex_to_color(seed)},")
            out.append("      );")
            out.append("")
            out.append("  /// Convenience dark ColorScheme derived from the overridden seed.")
            out.append(
                "  static ColorScheme get darkColorScheme => ColorScheme.fromSeed("
            )
            out.append(f"        seedColor: {_hex_to_color(seed)},")
            out.append("        brightness: Brightness.dark,")
            out.append("      );")
            out.append("")

        # -- Radius overrides (map onto AppRadius semantic aliases)
        if radii:
            out.append("  // -------- Radius --------")
            for slot, value in radii.items():
                out.append(
                    f"  /// {slot} BorderRadius (from scaffold input)."
                )
                out.append(
                    f"  static final BorderRadius {slot} = "
                    f"BorderRadius.circular({value});"
                )
            out.append("")

        # -- Typography overrides
        if family or text_styles:
            out.append("  // -------- Typography --------")
            if family:
                out.append(
                    f"  /// Font family override (google_fonts: {family})."
                )
                out.append(
                    f"  static TextTheme get textTheme => "
                    f"GoogleFonts.{_google_fonts_method(family)}TextTheme();"
                )
                out.append("")
            for style_name, spec in text_styles.items():
                size = spec.get("size")
                weight = spec.get("weight")
                height = spec.get("height")
                args: list[str] = []
                if size is not None:
                    args.append(f"fontSize: {size}")
                if weight is not None:
                    args.append(f"fontWeight: FontWeight.w{int(weight)}")
                if height is not None:
                    args.append(f"height: {float(height)}")
                out.append(
                    f"  /// {style_name} text style (from scaffold input)."
                )
                if not args:
                    out.append(
                        f"  static const TextStyle {style_name} = TextStyle();"
                    )
                elif len(args) <= 2:
                    out.append(
                        f"  static const TextStyle {style_name} = "
                        f"TextStyle({', '.join(args)});"
                    )
                else:
                    # Break long-arg TextStyle onto multiple lines.
                    out.append(
                        f"  static const TextStyle {style_name} = TextStyle("
                    )
                    for arg in args:
                        out.append(f"        {arg},")
                    out.append("      );")
            out.append("")

        out.append("}")
        # Trim trailing blank lines inside the class.
        while len(out) >= 2 and out[-2].strip() == "":
            del out[-2]
        return "\n".join(out) + "\n"

    # -- step 12: test skeleton ------------------------------------------
    def _generate_test_skeleton(self) -> None:
        # EMB-314: `flutter create` (step 0) produces test/widget_test.dart
        # that pumps the SDK's default `MyApp()` — which our overlay does
        # not provide. Always remove it; both testing branches below
        # replace it with our own placeholder.
        self._rm(self.target / "test" / "widget_test.dart")

        if self.a.testing == "bloc_test_mocktail":
            body = (
                "import 'package:flutter_test/flutter_test.dart';\n\n"
                "void main() {\n"
                "  test('placeholder', () {\n"
                "    expect(2 + 2, 4);\n"
                "  });\n"
                "}\n"
            )
            self._write(self.target / "test" / "smoke_test.dart", body)
        else:
            body = (
                "import 'package:flutter_test/flutter_test.dart';\n\n"
                "void main() {\n"
                "  test('placeholder', () {\n"
                "    expect(2 + 2, 4);\n"
                "  });\n"
                "}\n"
            )
            self._write(self.target / "test" / "widget_test.dart", body)

    # -- step 12: l10n skeleton -------------------------------------------
    def _generate_l10n_skeleton(self) -> None:
        if self.a.l10n == "no":
            return
        l10n_yaml = (
            "arb-dir: lib/l10n\n"
            "template-arb-file: app_en.arb\n"
            "output-localization-file: app_localizations.dart\n"
            "output-class: AppLocalizations\n"
            "output-dir: lib/l10n/generated\n"
            "# synthetic-package removed: deprecated in Flutter >=3.32\n"
        )
        self._write(self.target / "l10n.yaml", l10n_yaml)
        en = json.dumps(
            {
                "@@locale": "en",
                "appTitle": self.a.name,
                "@appTitle": {"description": "App title displayed in the top bar"},
                "welcomeMessage": "Welcome",
                "@welcomeMessage": {"description": "Greeting shown on the home screen"},
                "errorGeneric": "Something went wrong. Please try again.",
                "@errorGeneric": {"description": "Generic error message shown in snackbars"},
            },
            indent=2,
        )
        self._write(self.target / "lib" / "l10n" / "app_en.arb", en + "\n")
        if self.a.l10n == "en_uk":
            uk = json.dumps(
                {
                    "@@locale": "uk",
                    "appTitle": self.a.name,
                    "welcomeMessage": "Ласкаво просимо",
                    "errorGeneric": "Щось пішло не так. Будь ласка, спробуйте ще раз.",
                },
                indent=2, ensure_ascii=False,
            )
            self._write(self.target / "lib" / "l10n" / "app_uk.arb", uk + "\n")

    # -- step 13: CLAUDE.md ------------------------------------------------
    def _generate_claude_md(self) -> None:
        a = self.a
        # Build the "Skills (project-local)" list — populated AFTER kit-* copy
        # but generated as a placeholder list here based on selections.
        kits = self._kit_skill_list()
        kit_md_inline = ", ".join(f"`/{kit}`" for kit in kits) if kits else "(none)"

        # Mandatory rules table — Flutter defaults + log-decision
        rules_rows = [
            "| Use `Result<T>` for fallible operations from `core/` | Forces explicit error paths | manual review |",
            "| `AppException` hierarchy for errors; never throw raw `Exception` | Stable error model | manual review |",
            f"| Imports cross packages via `package:{a.name_snake}/src/core/...`, never relative | Stable refactor surface | lint custom rule |",
            "| Theme tokens via `AppSpacing` / `AppRadius` / `AppTypography`; never hard-code | Centralized design system | manual review |",
            "| Use `AppImages` / `AppIcons` / `AppAnimations` constants for asset paths; never hardcode strings in widgets | Single source of truth for asset paths | manual review |",
            "| Append to `docs/00_meta/decisions-log.md` for non-trivial design decisions | Decisions outlive chat | `/log-decision` |",
        ]
        if a.persistence == "drift":
            rules_rows.append(
                "| New tables go through Drift schema + migration; bump `schemaVersion` | Versioned migrations only | `/kit-add-drift-table` |"
            )
        if a.game == "flame":
            rules_rows.append(
                "| Flame components live under `lib/<game>/`; use `flame_bloc` bridge | Keeps game logic isolated | `/kit-create-flame-component` |"
            )

        rules_md = "\n".join(rules_rows)

        # Essential commands — flutter has no separate Typecheck row
        primary_flavor = self._flavors()[0]
        commands_md = (
            f"| Run dev | `flutter run --flavor {primary_flavor} -t lib/main_{primary_flavor}.dart "
            f"--dart-define-from-file=.env.{primary_flavor}` |\n"
            f"| Run prod | `flutter run --flavor prod -t lib/main_prod.dart "
            f"--dart-define-from-file=.env.prod --release` |\n"
            "| Format | `dart format .` |\n"
            "| Lint | `flutter analyze --fatal-warnings` |\n"
            "| Test | `flutter test` |\n"
            "| Test integration | `flutter test integration_test/` |\n"
            "| Codegen | `dart run build_runner build --delete-conflicting-outputs` |\n"
        )
        if a.l10n != "no":
            commands_md += "| L10n | `flutter gen-l10n` |\n"
        commands_md += (
            f"| Build APK | `flutter build apk --flavor {primary_flavor} -t "
            f"lib/main_{primary_flavor}.dart` |\n"
        )

        tagline = a.tagline or a.description or "A new Flutter project."
        commands_md_stripped = commands_md.rstrip("\n")
        body = f"""# {a.name}

{tagline}. Stack: {a.stack_summary()}.

## Essential commands

| What | How |
|---|---|
{commands_md_stripped}

## Architecture

Layered Flutter app. All project code lives under `lib/src/`. `lib/src/core/` ships the shared infrastructure copied from `flutter-template@v0.1.0` (network, storage, theme tokens, error handling, validation). Project-specific features live under `lib/src/features/` (see `lib/src/app/<name>_app.dart` for the root widget).

State management: {a.state_mgmt} | Persistence: {a.persistence} | Backend: {a.backend} | DI: {a.di} | Auth: {a.auth} | Error tracking: {a.error_tracking} | Theme: {a.theme}

See `plugins/forge/docs/architecture/02_mobile_flutter.md` for universal Flutter architecture rules.

## Mandatory rules

| Rule | Why | Skill / lint |
|---|---|---|
{rules_md}

## Documentation inventory

| Doc | When to read |
|---|---|
| `docs/00_meta/roadmap.md` | Planning a new epic or scope decision |
| `docs/00_meta/decisions-log.md` | Non-trivial design decisions (use `/log-decision`) |

## Credentials

See `docs/00_meta/runbooks/credentials.md` for env file conventions and credential workflows.

## Workflow

- Task tracker: {a.tracker} (see `.claude/tracker.json`).
- Project: {a.name}, prefix `{a.linear_prefix or '<set me>'}`, team `{a.linear_team or '<set me>'}`.
- Branches: `feature/<prefix>-N-<slug>`. **One branch per epic** — sub-tickets are commits.
- Magic-word commits: `Implements <PREFIX>-NN: <description>`.

## Global references

Global rules → `plugins/forge/docs/` (testing, linting, linear-tickets, git-workflow, architecture). Project-local overrides live in `docs/`.

## Skills

Project-local (in `.claude/skills/`): {kit_md_inline}. See `.claude/SKILLS.md` for the full filtered list.
Global: `/execute-epic`, `/execute-ticket`, `/commit`, `/epic-close`, `/pr-create`, `/kit-update-docs`, `/simplify-branch`. See `plugins/forge/skills/`.

## Environment

- Flavors: {", ".join(self._flavors())}
- Min Android SDK: {a.android_min_sdk} | Min iOS: {a.ios_min_version}
- Bundle id: `{a.bundle_id}`
- `.env.<flavor>` files: gitignored. `.env.example` is committed.
"""
        self._write(self.target / "CLAUDE.md", body)

    # -- step 14: copy kit-* skills ---------------------------------------
    def _kit_skill_list(self) -> list[str]:
        kits = ["kit-create-feature", "kit-deploy"]
        if self.a.persistence == "drift":
            kits.append("kit-add-drift-table")
        if self.a.l10n != "no":
            kits.append("kit-add-localization")
        if self.a.game == "flame":
            kits.append("kit-create-flame-component")
        # Q8.5 — Fastlane (EMB-321): copy stub skill when user opts in.
        if self.a.fastlane:
            kits.append("kit-add-fastlane")
        return kits

    def _copy_kit_skills(self) -> None:
        src_root = _PLUGIN_ROOT / "skill-templates" / "mobile-flutter"
        dst_root = self.target / ".claude" / "skills"
        for kit in self._kit_skill_list():
            src = src_root / f"{kit}.md"
            if not src.is_file():
                self._log(f"warning: kit template missing: {src} (skipping)")
                continue
            content = src.read_text()
            # placeholder replace: package:embergard/... -> package:<name>/src/core/...
            # EMB-315: inline layout uses lib/src/core/ (not lib/core/)
            content = re.sub(
                r"package:embergard/",
                f"package:{self.a.name_snake}/src/core/",
                content,
            )
            self._write(dst_root / f"{kit}.md", content)

    # -- step 15: settings.json -------------------------------------------
    def _generate_settings_json(self) -> None:
        allowed_bash = [
            "flutter analyze",
            "flutter analyze --fatal-warnings",
            "flutter test",
            "flutter pub get",
            "flutter pub run build_runner build",
            "dart format .",
            "dart run build_runner build --delete-conflicting-outputs",
            "git status",
            "git diff",
            "git log",
        ]
        body = json.dumps({
            "permissions": {
                "allow": [f"Bash({cmd}*)" for cmd in allowed_bash],
            },
        }, indent=2)
        self._write(self.target / ".claude" / "settings.json", body + "\n")

    # -- step 16: docs/00_meta scaffolding --------------------------------
    def _generate_docs_meta(self) -> None:
        src = _PLUGIN_ROOT / "skill-templates" / "_common" / "docs" / "00_meta"
        if not src.is_dir():
            self._log(f"warning: skill-templates/_common/docs/00_meta missing at {src}")
            return
        from datetime import date
        today = date.today().isoformat()
        for f in src.glob("*.md"):
            content = f.read_text()
            content = content.replace("<project_name>", self.a.name)
            content = content.replace("<date>", today)
            self._write(self.target / "docs" / "00_meta" / f.name, content)
        # Copy runbooks/ subdirectory (e.g. credentials.md — EMB-322)
        runbooks_src = src / "runbooks"
        if runbooks_src.is_dir():
            for f in runbooks_src.glob("*.md"):
                content = f.read_text()
                content = content.replace("<project_name>", self.a.name)
                content = content.replace("<date>", today)
                self._write(self.target / "docs" / "00_meta" / "runbooks" / f.name, content)

    # -- step 17: .gitignore ----------------------------------------------
    def _generate_gitignore(self) -> None:
        body = (
            "# Flutter / Dart\n"
            ".dart_tool/\n"
            ".packages\n"
            "build/\n"
            ".flutter-plugins\n"
            ".flutter-plugins-dependencies\n"
            "pubspec.lock\n\n"
            "# Generated\n"
            "*.g.dart\n"
            "*.freezed.dart\n"
            "lib/l10n/generated/\n\n"
            "# IDE\n"
            ".idea/workspace.xml\n"
            ".idea/tasks.xml\n"
            ".vscode/.last_run.json\n\n"
            "# Env files (gitignored — .env.example is committed)\n"
            ".env\n"
            ".env.dev\n"
            ".env.staging\n"
            ".env.prod\n\n"
            "# OS\n"
            ".DS_Store\n"
        )
        self._write(self.target / ".gitignore", body)

    # -- step 18: flutter_launcher_icons per flavor (Q8.5 / EMB-321) ------
    def _generate_launcher_icon_yamls(self) -> None:
        """Generate flutter_launcher_icons-<flavor>.yaml per flavor when Q8.5=yes.

        Each yaml mirrors the b2b-mobile-app pattern:
          flutter_launcher_icons:
            android: true
            ios: true
            image_path: "assets/icons/launcher_<flavor>.png"
            adaptive_icon_background: "#000000"
            adaptive_icon_foreground: "assets/icons/launcher_<flavor>.png"
            remove_alpha_ios: true

        The icon source images (`assets/icons/launcher_<flavor>.png`) are
        placeholders — the user replaces them with real artwork before running
        `dart run flutter_launcher_icons -f flutter_launcher_icons-<flavor>.yaml`.
        The Mode M ticket ("Set up Fastlane lanes for <project>") reminds the
        user to supply artwork + run the generator before Fastlane lane setup.
        """
        if not self.a.fastlane:
            return

        for flavor in self._flavors():
            content = (
                "flutter_launcher_icons:\n"
                "  android: true\n"
                "  ios: true\n"
                f"  image_path: \"assets/icons/launcher_{flavor}.png\"\n"
                "  adaptive_icon_background: \"#000000\"\n"
                f"  adaptive_icon_foreground: \"assets/icons/launcher_{flavor}.png\"\n"
                "  remove_alpha_ios: true\n"
            )
            self._write(
                self.target / f"flutter_launcher_icons-{flavor}.yaml",
                content,
            )

        # Emit Mode M ticket for Fastlane lane setup. This is always "defer"
        # (not credentials-gated) — lane execution is a FORGE-6 deliverable.
        self._add_mode_m(
            f"Set up Fastlane lanes for {self.a.name}",
            template_name="fastlane.md",
        )

        # Copy kit-add-fastlane skill (handled via _kit_skill_list() below).
        # The Mode M ticket body reminds the user to run /kit-add-fastlane
        # after Fastlane is wired up.

    # -- step 19: .claude/tracker.json (Q9 / EMB-324) ---------------------
    def _generate_tracker_json(self) -> None:
        """Write <project>/.claude/tracker.json with the chosen task-tracker config.

        Skills currently IGNORE this file. FORGE-8 will wire tracker-aware
        behaviour (e.g. /commit choosing Linear vs GitHub PRs vs Jira transitions).
        Schema version 1 — bump when the shape changes in FORGE-8+.
        """
        a = self.a
        payload: dict[str, Any] = {
            "backend": a.tracker,
            "version": 1,
            "note": "Read by /commit and other tracker-aware skills in FORGE-8",
        }
        if a.tracker_workspace:
            payload["workspace"] = a.tracker_workspace
        if a.tracker_project:
            payload["project"] = a.tracker_project
        self._write(
            self.target / ".claude" / "tracker.json",
            json.dumps(payload, indent=2) + "\n",
        )

    # -- summary file ------------------------------------------------------
    def _write_summary(self) -> None:
        # Build per-integration credentials resolution map (FORGE-5.4 / EMB-289).
        # Surfaces what the user supplied vs deferred vs skipped, so downstream
        # tooling (Linear automation, /project-init follow-up output) can act
        # on it without re-parsing the answers JSON.
        cred_resolution = self._credentials_resolution()

        report: dict[str, Any] = {
            "ticket": "EMB-288",
            "scaffolder_version": "1.7.0",  # bumped for EMB-324: Q9 tracker + .claude/tracker.json
            "answers_resolved": {
                "name": self.a.name,
                "name_snake": self.a.name_snake,
                "bundle_id": self.a.bundle_id,
                "stack": self.a.stack_summary(),
                "layout": self.a.layout,
                "flavors": self._flavors(),
            },
            "credentials_resolution": cred_resolution,
            "mode_m_tickets": self.a.mode_m_tickets,
            # Remote setup intent (FORGE-5.5 / EMB-290).
            # /project-init reads this after the scaffolder returns and drives
            # the gh-repo and Linear-project flows accordingly.  The scaffolder
            # records intent only — it does NOT call `gh` or the Linear MCP.
            "remote_setup": {
                "gh_repo": self.a.gh_repo,
                "linear_project": self.a.linear_project,
            },
            "kit_skills_copied": self._kit_skill_list(),
            # EMB-318: explicit list of files/dirs removed so the user can see
            # what was dropped and why without grepping through actions_log.
            "dropped_files": self.dropped_files,
            "actions_log": self.summary,
        }
        self._write(self.target / ".claude" / "scaffold-report.json",
                    json.dumps(report, indent=2) + "\n")

    def _credentials_resolution(self) -> dict[str, str]:
        """Resolve every integration the user selected to its credential mode.

        Output keys mirror the credentials block keys; values are
        provide|defer|skip. Integrations not in the user's stack are omitted.
        """
        out: dict[str, str] = {}
        if self.a.backend == "supabase" or self.a.auth == "supabase_auth":
            out["supabase"] = self.a.cred_mode("supabase")
        if (
            self.a.backend == "firebase"
            or self.a.auth == "firebase_auth"
            or self.a.error_tracking in ("crashlytics", "crashlytics_sentry")
            or self.a.analytics == "firebase"
            or self.a.push == "fcm"
        ):
            out["firebase"] = self.a.cred_mode("firebase")
        if self.a.backend == "custom_rest":
            out["custom_rest"] = self.a.cred_mode("custom_rest")
        if self.a.error_tracking in ("sentry", "crashlytics_sentry"):
            out["sentry"] = self.a.cred_mode("sentry")
        if self.a.auth == "oauth_google":
            out["oauth_google"] = self.a.cred_mode("oauth_google")
        if self.a.auth == "oauth_apple":
            out["oauth_apple"] = self.a.cred_mode("oauth_apple")
        if self.a.auth == "oidc_sso":
            out["oidc"] = self.a.cred_mode("oidc")
        if self.a.analytics in ("mixpanel", "amplitude", "posthog"):
            out["analytics"] = self.a.cred_mode("analytics")
        if self.a.push == "onesignal":
            out["onesignal"] = self.a.cred_mode("onesignal")
        return out


# ----------------------------------------------------------------------------
# CLI entry
# ----------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--pin", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    raw = json.loads(args.answers.read_text())
    answers = Answers.from_dict(raw)

    s = Scaffolder(
        answers=answers,
        target=args.target.resolve(),
        template=args.template.resolve(),
        pin=args.pin.resolve(),
        dry_run=args.dry_run,
    )
    return s.run()


if __name__ == "__main__":
    sys.exit(main())
