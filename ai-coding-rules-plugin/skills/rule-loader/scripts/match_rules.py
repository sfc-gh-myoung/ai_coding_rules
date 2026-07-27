#!/usr/bin/env python3
"""Standalone deterministic rule matcher — stdlib-only, zero external deps.

Can be used two ways:
  1. CLI: python3 match_rules.py --prompt "Write a Streamlit app" --rules-dir ./rules
  2. Import: from ai_rules.match_rules import match_rules, load_rules_db, resolve_dependencies

Produces rule-loader-manifest/v2 JSON or full rule metadata JSON.
Exit codes: 0 = rules matched, 1 = no rules matched, 2 = fatal error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from fnmatch import fnmatch
from os.path import dirname
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Minimal YAML frontmatter parser (stdlib-only)
# Handles: scalars, string lists, one-level nested dicts, quoted strings
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^---\s*$")
_LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+)$")
_KEY_VALUE_RE = re.compile(r"^(\w[\w_]*):\s*(.*)$")
_QUOTED_RE = re.compile(r'^(["\'])(.*)(\1)$')


def _unquote(s: str) -> str:
    m = _QUOTED_RE.match(s.strip())
    return m.group(2) if m else s.strip()


def _parse_yaml_value(value_str: str) -> Any:
    """Parse a simple YAML scalar value."""
    v = value_str.strip()
    if not v or v == "~":
        return None
    if v in ("true", "True", "TRUE"):
        return True
    if v in ("false", "False", "FALSE"):
        return False
    if v == "{}":
        return {}
    if v == "[]":
        return []
    # Tilde-prefixed numbers (token_budget: ~2350)
    if v.startswith("~") and v[1:].isdigit():
        return v  # Keep as string, caller extracts the number
    # Plain integers
    if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
        return int(v)
    return _unquote(v)


def parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Parse YAML frontmatter from a markdown file's first --- fence pair."""
    lines = content.split("\n")
    if not lines or not _FENCE_RE.match(lines[0]):
        return None

    # Find closing fence
    end_idx = -1
    for idx in range(1, min(len(lines), 200)):
        if _FENCE_RE.match(lines[idx]):
            end_idx = idx
            break
    if end_idx < 0:
        return None

    # Parse the block between fences
    result: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    current_dict: dict[str, Any] | None = None
    dict_key: str | None = None

    for line in lines[1:end_idx]:
        # Empty line
        if not line.strip():
            continue

        # Check if this is a top-level list item (indented with -)
        # Only matches when NOT inside a nested dict (current_dict handles its own list items)
        list_match = _LIST_ITEM_RE.match(line)
        if list_match and current_key is not None and current_dict is None:
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            item = _unquote(list_match.group(1).strip())
            # Handle inline comment in list items
            if "  #" in item:
                item = item.split("  #")[0].strip()
            current_list.append(item)
            continue

        # Check if this is inside a nested dict (any indented line while current_dict is active)
        if current_dict is not None and (line.startswith("  ") or line.startswith("\t")):
            stripped = line.strip()
            # Nested list item under current dict_key
            if dict_key and stripped.startswith("- "):
                item = _unquote(stripped[2:].strip())
                if "  #" in item:
                    item = item.split("  #")[0].strip()
                current_dict.setdefault(dict_key, []).append(item)
                continue
            # Nested dict key
            nested_match = _KEY_VALUE_RE.match(stripped)
            if nested_match:
                nk, nv = nested_match.group(1), nested_match.group(2)
                if nv == "" or nv.startswith("["):
                    current_dict[nk] = []
                    dict_key = nk
                else:
                    current_dict[nk] = _parse_yaml_value(nv)
                    dict_key = None
                continue

        # Top-level key: value
        kv_match = _KEY_VALUE_RE.match(line)
        if kv_match:
            # Finalize previous dict if any
            if current_dict is not None and current_key:
                result[current_key] = current_dict

            current_key = kv_match.group(1)
            raw_value = kv_match.group(2).strip()
            current_list = None
            current_dict = None
            dict_key = None

            if raw_value == "" or raw_value == "|" or raw_value == ">":
                # Could be start of list, dict, or multiline — wait for next lines
                pass
            elif raw_value == "{}":
                result[current_key] = {}
            elif raw_value == "[]":
                result[current_key] = []
            else:
                result[current_key] = _parse_yaml_value(raw_value)
            continue

        # Indented content that starts a new dict (e.g., depends:\n  required:\n    - ...)
        if current_key and line.startswith("  ") and current_list is None and current_dict is None:
            nested_match = _KEY_VALUE_RE.match(line.strip())
            if nested_match:
                current_dict = {}
                nk, nv = nested_match.group(1), nested_match.group(2)
                if nv == "" or nv.startswith("["):
                    current_dict[nk] = []
                    dict_key = nk
                else:
                    current_dict[nk] = _parse_yaml_value(nv)

    # Finalize trailing dict
    if current_dict is not None and current_key:
        result[current_key] = current_dict

    return result


# ---------------------------------------------------------------------------
# Rule data model
# ---------------------------------------------------------------------------

_TOKEN_BUDGET_RE = re.compile(r"~?(\d+)")

TIER_ORDER: dict[str, int] = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

_EXT_ALIASES: dict[str, str] = {".yml": ".yaml", ".yaml": ".yaml"}


@dataclass
class RuleEntry:
    """Parsed rule frontmatter."""

    filename: str
    path: Path
    context_tier: str
    token_budget: int | None
    depends_required: list[str]
    depends_optional: list[str]
    typed_kw: list[str]
    typed_ext: list[str]
    file_patterns: list[str]
    dir_patterns: list[str]
    rule_version: str
    description: str
    line_count: int
    last_updated: str
    schema_version: str
    keywords_raw: list[str]


def _parse_token_budget(value: Any) -> int | None:
    if value is None:
        return None
    m = _TOKEN_BUDGET_RE.search(str(value))
    return int(m.group(1)) if m else None


def _parse_depends(value: Any) -> tuple[list[str], list[str]]:
    """Return (required, optional) dependency filename lists."""
    if not value:
        return [], []
    if isinstance(value, dict):
        req = [str(v).split("#")[0].strip() for v in (value.get("required") or []) if v]
        opt = [str(v).split("#")[0].strip() for v in (value.get("optional") or []) if v]
        return req, opt
    if isinstance(value, list):
        req, opt = [], []
        for item in value:
            s = str(item).strip()
            if s.startswith("optional:"):
                opt.append(s[9:].strip())
            else:
                req.append(s[9:].strip() if s.startswith("required:") else s)
        return req, opt
    return [], []


def _parse_typed_keywords(
    raw_keywords: list[Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Split keywords by prefix: (kw, ext, file, dir)."""
    kw, ext, file_pats, dir_pats = [], [], [], []
    for item in raw_keywords or []:
        s = str(item).strip()
        if not s:
            continue
        if s.startswith("ext:"):
            ext.append(s[4:])
        elif s.startswith("file:"):
            file_pats.append(s[5:])
        elif s.startswith("dir:"):
            dir_pats.append(s[4:])
        else:
            kw.append(s[3:] if s.startswith("kw:") else s)
    return kw, ext, file_pats, dir_pats


def parse_rule_file(path: Path) -> RuleEntry | None:
    """Parse a single rule .md file and return a RuleEntry."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    data = parse_frontmatter(content)
    if data is None:
        return None

    raw_kw = data.get("keywords") or []
    if not isinstance(raw_kw, list):
        raw_kw = []
    typed_kw, typed_ext, file_pats, dir_pats = _parse_typed_keywords(raw_kw)
    req, opt = _parse_depends(data.get("depends"))
    line_count = content.count("\n") + (0 if content.endswith("\n") else 1)

    return RuleEntry(
        filename=path.name,
        path=path,
        context_tier=str(data.get("context_tier") or "Low"),
        token_budget=_parse_token_budget(data.get("token_budget")),
        depends_required=req,
        depends_optional=opt,
        typed_kw=typed_kw,
        typed_ext=typed_ext,
        file_patterns=file_pats,
        dir_patterns=dir_pats,
        rule_version=str(data.get("rule_version") or ""),
        description=str(data.get("description") or ""),
        line_count=line_count,
        last_updated=str(data.get("last_updated") or ""),
        schema_version=str(data.get("schema_version") or ""),
        keywords_raw=[str(k) for k in raw_kw],
    )


def load_rules_db(rules_dir: Path) -> dict[str, RuleEntry]:
    """Scan rules_dir for *.md files and return a filename-keyed dict."""
    if not rules_dir.is_dir():
        raise FileNotFoundError(f"rules-dir not found: {rules_dir}")
    db: dict[str, RuleEntry] = {}
    for md_path in sorted(rules_dir.glob("*.md")):
        if md_path.name == "README.md":
            continue
        rule = parse_rule_file(md_path)
        if rule is not None:
            db[md_path.name] = rule
    return db


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------


@dataclass
class FileContext:
    """File context extracted from a user prompt (extensions, paths)."""

    extensions: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)


@dataclass
class ScoredRule:
    """A rule entry with its aggregate match score."""

    rule: RuleEntry
    score: int


def _word_boundary_match(needle: str, haystack: str) -> bool:
    pattern = r"(?:^|\s)" + re.escape(needle) + r"(?:\s|$)"
    return bool(re.search(pattern, haystack))


def _score_kw(user_kw: str, rule_kw: str) -> int:
    """Score one user keyword against one rule keyword."""
    u = user_kw.lower().replace("-", " ").replace("_", " ").strip()
    r = rule_kw.lower().replace("-", " ").replace("_", " ").strip()

    if u == r:
        return 10

    if len(u) >= 3 and len(r) >= 3:
        u_wc = len(u.split())
        r_wc = len(r.split())
        shorter_wc = min(u_wc, r_wc)
        longer_wc = max(u_wc, r_wc)
        if ((u_wc == 1 and r_wc == 1) or (shorter_wc * 2 >= longer_wc)) and (
            _word_boundary_match(u, r) or _word_boundary_match(r, u)
        ):
            return 10

    r_words = r.split()
    u_words = u.split()

    # Bigram overlap
    if len(r_words) >= 2 and len(u_words) >= 2:
        bigrams_r = {f"{r_words[i]} {r_words[i + 1]}" for i in range(len(r_words) - 1)}
        bigrams_u = {f"{u_words[i]} {u_words[i + 1]}" for i in range(len(u_words) - 1)}
        if bigrams_r & bigrams_u:
            return 5

    # Word-level match (>= 3 chars)
    r_word_set = set(r_words)
    for uw in u_words:
        if len(uw) >= 3 and uw in r_word_set:
            return 1

    return 0


def _normalize_ext(ext: str) -> str:
    return _EXT_ALIASES.get(ext.lower(), ext.lower())


# Stop-word sets used by both _extract_from_prompt and match_rules
_HARD_STOP_WORDS = frozenset(
    [
        "the",
        "and",
        "for",
        "are",
        "but",
        "not",
        "you",
        "all",
        "can",
        "had",
        "was",
        "has",
        "have",
        "been",
        "they",
        "that",
        "this",
        "with",
        "from",
        "were",
        "will",
        "what",
        "when",
        "make",
        "like",
        "time",
        "just",
        "know",
        "take",
        "into",
        "your",
        "some",
        "them",
        "than",
        "then",
        "would",
        "about",
        "more",
        "much",
        "need",
        "want",
        "help",
        "think",
        "use",
        "how",
        "find",
        "could",
        "also",
        "back",
        "after",
        "any",
        "get",
        "come",
        "made",
        "may",
        "should",
        "might",
        "each",
        "other",
        "which",
        "before",
        "through",
        "its",
        "where",
        "must",
        "new",
        "now",
        "see",
        "only",
        "here",
        "those",
        "while",
        "never",
        "many",
        "end",
        "being",
        "because",
        "both",
        "using",
        "create",
        "write",
        "build",
        "implement",
        "add",
        "update",
        "change",
        "modify",
        "fix",
        "show",
        "display",
        "handle",
        "process",
        "check",
        "ensure",
        "please",
        "best",
        "practices",
        "following",
        "current",
        "existing",
        "specific",
    ]
)

_SOFT_STOP_WORDS = frozenset(
    [
        "data",
        "code",
        "file",
        "function",
        "method",
        "class",
        "application",
        "project",
        "system",
        "service",
        "query",
        "table",
        "view",
        "model",
        "config",
        "configuration",
        "setup",
        "deploy",
        "test",
        "error",
        "output",
        "input",
        "result",
        "value",
        "type",
        "name",
        "path",
        "task",
        "work",
        "feature",
        "issue",
    ]
)

_SHORT_TECH_ALLOWLIST = frozenset(
    [
        "sql",
        "dbt",
        "mcp",
        "rag",
        "llm",
        "api",
        "cdc",
        "cte",
        "ddl",
        "udf",
        "sdk",
        "cli",
        "etl",
        "jwt",
        "sse",
        "dmf",
        "orm",
        "zsh",
        "tsx",
        "dml",
        "iac",
        "gcp",
        "aws",
        "k8s",
        "css",
        "csv",
        "dag",
        "env",
        "gpu",
        "oci",
    ]
)


def match_rules(
    keywords: list[str],
    file_context: FileContext,
    rules: list[RuleEntry],
    *,
    score_threshold: int = 4,
    soft_stop_words: frozenset[str] = _SOFT_STOP_WORDS,
) -> list[ScoredRule]:
    """Score and rank rules against keywords and file_context."""
    scored: list[ScoredRule] = []

    for rule in rules:
        score = 0

        for user_kw in keywords:
            best_kw_score = 0
            for rule_kw in rule.typed_kw:
                s = _score_kw(user_kw, rule_kw)
                if s > best_kw_score:
                    best_kw_score = s
            # Cap soft-stop keywords to word-level contribution (max 1)
            if user_kw in soft_stop_words and best_kw_score > 1:
                best_kw_score = 1
            score += best_kw_score

        rule_exts = {_normalize_ext(e) for e in rule.typed_ext}
        for ext in file_context.extensions:
            if _normalize_ext(ext) in rule_exts:
                score += 4

        for path in file_context.paths:
            for pattern in rule.file_patterns:
                if fnmatch(path, pattern) or fnmatch(path, f"**/{pattern}"):
                    score += 5

        for path in file_context.paths:
            path_dir = dirname(path)
            for pattern in rule.dir_patterns:
                clean_pattern = pattern.rstrip("/")
                if fnmatch(path_dir, clean_pattern) or fnmatch(path_dir, f"**/{clean_pattern}"):
                    score += 3

        if score >= score_threshold:
            scored.append(ScoredRule(rule=rule, score=score))

    scored.sort(key=lambda s: (-s.score, TIER_ORDER.get(s.rule.context_tier, 99)))
    return scored


# ---------------------------------------------------------------------------
# Dependency resolution
# ---------------------------------------------------------------------------


def resolve_dependencies(
    matched: list[ScoredRule],
    rules_db: dict[str, RuleEntry],
) -> tuple[list[RuleEntry], list[dict]]:
    """Walk the required dep graph transitively. Returns (resolved, warnings)."""
    from collections import OrderedDict

    to_load: OrderedDict[str, RuleEntry] = OrderedDict()
    warnings: list[dict] = []
    visited: set[str] = set()
    queue: list[RuleEntry] = [sr.rule for sr in matched]

    while queue:
        rule = queue.pop(0)
        if rule.filename in visited:
            continue
        visited.add(rule.filename)
        to_load[rule.filename] = rule

        for dep_name in rule.depends_required:
            dep_clean = dep_name.split("#")[0].strip()
            if not dep_clean or dep_clean in visited:
                continue
            if dep_clean not in rules_db:
                warnings.append({"rule": rule.filename, "missing_dep": dep_clean})
                continue
            queue.append(rules_db[dep_clean])

    return list(to_load.values()), warnings


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------


def build_manifest(
    resolved: list[RuleEntry],
    warnings: list[dict],
    *,
    matched_filenames: set[str] | None = None,
    max_entries: int = 3,
    max_tokens: int = 20_000,
) -> dict:
    """Build a rule-loader-manifest/v2 dict."""
    if matched_filenames is None:
        matched_filenames = {r.filename for r in resolved}

    def _to_entry(rule: RuleEntry, is_dep: bool = False) -> dict:
        d: dict[str, Any] = {
            "filename": rule.filename,
            "rule_path": f"rules/{rule.filename}",
            "context_tier": rule.context_tier,
            "rule_version": rule.rule_version,
            "description": rule.description,
        }
        if rule.token_budget is not None:
            d["token_budget"] = rule.token_budget
        if is_dep:
            d["is_dependency_only"] = True
        return d

    candidate_rules = [_to_entry(r) for r in resolved]
    deferred: list[dict] = []

    # Split into direct matches and deps
    direct = []
    deps_only = []
    for rule in resolved:
        is_dep = rule.filename not in matched_filenames
        entry = _to_entry(rule, is_dep)
        if is_dep:
            deps_only.append(entry)
        else:
            direct.append(entry)

    # Apply entry cap to direct matches
    capped_direct = direct[:max_entries]
    for entry in direct[max_entries:]:
        deferred.append({"filename": entry["filename"], "reason": "entry_cap"})

    load_sequence = capped_direct + deps_only

    # Token budget enforcement
    def _total_tokens(seq: list[dict]) -> int:
        return sum(e.get("token_budget", 0) for e in seq)

    while _total_tokens(load_sequence) > max_tokens and len(load_sequence) > 1:
        removed_idx = None
        for i in range(len(load_sequence) - 1, -1, -1):
            entry = load_sequence[i]
            is_foundation = entry["filename"].startswith("000-")
            if not is_foundation and not entry.get("is_dependency_only"):
                removed_idx = i
                break
        if removed_idx is None:
            break
        removed = load_sequence.pop(removed_idx)
        deferred.append({"filename": removed["filename"], "reason": "token_budget"})

    return {
        "schema_version": "rule-loader-manifest/v2",
        "load_sequence": load_sequence,
        "deferred_rules": deferred,
        "candidate_rules": candidate_rules,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Metadata mode — full rule database output
# ---------------------------------------------------------------------------


def build_metadata(rules_db: dict[str, RuleEntry]) -> dict:
    """Build full metadata JSON for all rules (used by eval harness)."""
    rules_out: dict[str, dict] = {}
    for filename, rule in rules_db.items():
        path_str = f"rules/{filename}"
        rules_out[path_str] = {
            "path": path_str,
            "filename": filename,
            "keywords": rule.keywords_raw,
            "typed_kw": rule.typed_kw,
            "typed_ext": rule.typed_ext,
            "typed_file": rule.file_patterns,
            "typed_dir": rule.dir_patterns,
            "context_tier": rule.context_tier,
            "token_budget": rule.token_budget,
            "depends_required": [
                f"rules/{d}" if not d.startswith("rules/") else d for d in rule.depends_required
            ],
            "depends_optional": [
                f"rules/{d}" if not d.startswith("rules/") else d for d in rule.depends_optional
            ],
            "rule_version": rule.rule_version,
            "description": rule.description,
            "line_count": rule.line_count,
            "last_updated": rule.last_updated,
            "schema_version": rule.schema_version,
        }
    return {"rules": rules_out}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _extract_from_prompt(prompt: str) -> tuple[list[str], list[str], list[str]]:
    """Extract keywords, extensions, and paths from prompt text."""
    words = re.split(r"[^\w./-]+", prompt.lower())
    keywords = []
    extensions = []
    paths = []
    for word in words:
        if word.startswith(".") and len(word) > 1:
            extensions.append(word)
        elif "/" in word:
            paths.append(word)
            # Also extract extension from path (e.g., ".py" from "src/foo.py")
            ext_match = re.search(r"(\.\w{1,5})$", word)
            if ext_match:
                extensions.append(ext_match.group(1))
        elif word in _HARD_STOP_WORDS:
            continue  # fully filtered
        elif len(word) >= 4:
            keywords.append(word)
        elif word.upper() == word and len(word) >= 2:
            keywords.append(word)  # acronym (SQL, MCP, API)
        elif word in _SHORT_TECH_ALLOWLIST:
            keywords.append(word)  # known short tech term
        # else: word is <4 chars, not uppercase, not in allowlist → skip
    return keywords, extensions, paths


def main(argv: list[str] | None = None) -> int:  # noqa: D103
    parser = argparse.ArgumentParser(description="Deterministic rule matcher (stdlib-only)")
    parser.add_argument("--mode", choices=["match", "metadata"], default="match")
    parser.add_argument(
        "--prompt", default="", help="User prompt (auto-extracts keywords/extensions/paths)"
    )
    parser.add_argument("--keywords", default="", help="Comma-separated keywords")
    parser.add_argument("--extensions", default="", help="Comma-separated file extensions")
    parser.add_argument("--paths", default="", help="Comma-separated file paths")
    parser.add_argument(
        "--rules-dir", type=Path, default=Path("rules"), help="Path to rules directory"
    )
    parser.add_argument("--max-entries", type=int, default=3, help="Max direct-match entries")
    parser.add_argument("--max-tokens", type=int, default=20_000, help="Token budget ceiling")
    args = parser.parse_args(argv)

    # Load rules
    try:
        db = load_rules_db(args.rules_dir)
    except FileNotFoundError as exc:
        print(json.dumps({"error": str(exc), "load_sequence": []}), file=sys.stderr)
        return 2

    # Metadata mode: dump full DB and exit
    if args.mode == "metadata":
        print(json.dumps(build_metadata(db), indent=2))
        return 0

    # Match mode
    kw_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
    ext_list = [e.strip() for e in args.extensions.split(",") if e.strip()]
    path_list = [p.strip() for p in args.paths.split(",") if p.strip()]

    if args.prompt:
        p_kw, p_ext, p_paths = _extract_from_prompt(args.prompt)
        kw_list.extend(w for w in p_kw if w not in kw_list)
        ext_list.extend(e for e in p_ext if e not in ext_list)
        path_list.extend(p for p in p_paths if p not in path_list)

    file_ctx = FileContext(extensions=ext_list, paths=path_list)
    scored = match_rules(kw_list, file_ctx, list(db.values()))
    matched_filenames = {sr.rule.filename for sr in scored}

    resolved, warnings = resolve_dependencies(scored, db)
    manifest = build_manifest(
        resolved,
        warnings,
        matched_filenames=matched_filenames,
        max_entries=args.max_entries,
        max_tokens=args.max_tokens,
    )

    print(json.dumps(manifest, indent=2))
    return 0 if manifest["load_sequence"] else 1


if __name__ == "__main__":
    sys.exit(main())
