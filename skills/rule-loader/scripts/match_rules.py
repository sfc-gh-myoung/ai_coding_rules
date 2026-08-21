#!/usr/bin/env python3
"""Standalone deterministic rule matcher: stdlib-only, zero external deps.

Can be used two ways:
  1. CLI: python3 match_rules.py --prompt "Write a Streamlit app" --rules-dir ./rules
  2. Import: from ai_rules.match_rules import match_rules, load_rules_db, resolve_dependencies

Produces rule-loader-matcher/v1 JSON or full rule metadata JSON.
Exit codes: 0 = rules matched, 1 = no rules matched, 2 = fatal error.

THIS FILE IS THE PRIMARY. It is vendored verbatim to
``skills/rule-loader/scripts/match_rules.py`` by ``ai-rules plugin sync``, because
the plugin ships as a self-contained directory that deliberately excludes ``src/``
and a shipped skill therefore cannot import from here. Edit this file only; never
the vendored copy. The two must stay byte-identical, which is why this notice
lives in the primary rather than as a header on the copy alone.
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
                # Could be start of list, dict, or multiline: wait for next lines
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
        normalized = s.lower()
        if normalized.startswith("ext:"):
            ext.append(normalized[4:])
        elif normalized.startswith("file:"):
            file_pats.append(normalized[5:])
        elif normalized.startswith("dir:"):
            dir_pats.append(normalized[4:])
        else:
            kw.append(normalized[3:] if normalized.startswith("kw:") else normalized)
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

    # A multi-word user token is an n-gram phrase hypothesis: it scores only on
    # exact equality above. Partial credit (word-boundary / bigram-overlap /
    # word-level) is reserved for single-word tokens, so a long contiguous
    # n-gram like "raw landing table" cannot fuzzily inflate unrelated rules.
    if len(u.split()) >= 2:
        return 0

    if len(u) >= 3 and len(r) >= 3:
        u_wc = len(u.split())
        r_wc = len(r.split())
        shorter_wc = min(u_wc, r_wc)
        longer_wc = max(u_wc, r_wc)
        if ((u_wc == 1 and r_wc == 1) or (shorter_wc * 2 >= longer_wc)) and (
            _word_boundary_match(u, r) or _word_boundary_match(r, u)
        ):
            # A single user word found inside a MULTI-word rule keyword is a
            # partial signal, not an exact match. Awarding full credit here made
            # incidental hits indistinguishable from precise ones: e.g. generic
            # "deployment" scored 10 against "Gunicorn deployment", tying with an
            # exact "snowcli" == "snowcli" hit and pushing the correct rule out of
            # the entry cap. Score it like bigram overlap (5) instead.
            if u_wc == 1 and r_wc >= 2:
                return 5
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
                if fnmatch(path.lower(), pattern) or fnmatch(path.lower(), f"**/{pattern}"):
                    score += 5

        for path in file_context.paths:
            path_dir = dirname(path.lower())
            for pattern in rule.dir_patterns:
                clean_pattern = pattern.rstrip("/")
                if fnmatch(path_dir, clean_pattern) or fnmatch(path_dir, f"**/{clean_pattern}"):
                    score += 4  # RC3: exact dir clears the threshold alone

        if score >= score_threshold:
            scored.append(ScoredRule(rule=rule, score=score))

    # Filename is the stable final tiebreaker for equal score and tier, so rank
    # order cannot depend on rules-DB insertion order (RC/R11).
    scored.sort(key=lambda s: (-s.score, TIER_ORDER.get(s.rule.context_tier, 99), s.rule.filename))
    return scored


# ---------------------------------------------------------------------------
# Dependency resolution
# ---------------------------------------------------------------------------


def resolve_dependencies(
    matched: list[ScoredRule],
    rules_db: dict[str, RuleEntry],
    *,
    max_direct: int | None = None,
) -> tuple[list[RuleEntry], list[dict]]:
    """Walk the required dep graph transitively. Returns (resolved, warnings).

    Args:
        matched: Scored direct matches, highest score first.
        rules_db: Full rule database for dependency lookup.
        max_direct: When set, resolve dependencies for only the top ``max_direct``
            matches. ``build_manifest`` caps direct entries but appends every
            resolved dependency uncapped, so without this the manifest shipped
            dependencies belonging to matches it had already discarded.
    """
    from collections import OrderedDict

    if max_direct is not None:
        matched = matched[:max_direct]

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
    foundation: RuleEntry | None = None,
    max_entries: int = 3,
    max_tokens: int = 20_000,
) -> dict:
    """Build a rule-loader-matcher/v1 dict."""
    if matched_filenames is None:
        matched_filenames = {r.filename for r in resolved}

    def _to_entry(rule: RuleEntry, layer: str = "SOFT") -> dict:
        d: dict[str, Any] = {
            "rule_path": f"rules/{rule.filename}",
            "layer": layer,
            "context_tier": rule.context_tier,
            "description": rule.description,
        }
        if rule.token_budget is not None:
            d["token_budget"] = rule.token_budget
        return d

    if foundation is not None and all(rule.filename != foundation.filename for rule in resolved):
        resolved = [foundation, *resolved]

    candidate_rules = [
        _to_entry(
            r, "HARD" if (foundation is not None and r.filename == foundation.filename) else "SOFT"
        )
        for r in resolved
    ]
    deferred: list[dict] = []

    # Split into direct matches and deps
    foundation_entry: dict | None = None
    direct = []
    deps_only = []
    for rule in resolved:
        is_dep = rule.filename not in matched_filenames
        is_foundation = foundation is not None and rule.filename == foundation.filename
        layer = "HARD" if is_foundation else "SOFT"
        entry = _to_entry(rule, layer)
        if is_foundation:
            foundation_entry = entry
        elif is_dep:
            deps_only.append(entry)
        else:
            direct.append(entry)

    # Apply entry cap to direct matches
    capped_direct = direct[:max_entries]
    for entry in direct[max_entries:]:
        deferred.append({"rule_path": entry["rule_path"], "reason": "entry_cap"})

    # Order dependencies before dependents: emit each surviving direct match's
    # transitive required deps ahead of it. Foundation always leads (HARD).
    rule_by_path = {f"rules/{r.filename}": r for r in resolved}
    keep_entries = (
        ([foundation_entry] if foundation_entry is not None else []) + capped_direct + deps_only
    )
    entry_by_path = {e["rule_path"]: e for e in keep_entries}

    ordered: list[dict] = []
    emitted: set[str] = set()

    if foundation_entry is not None:
        ordered.append(foundation_entry)
        emitted.add(foundation_entry["rule_path"])

    def _emit_with_deps(path: str) -> None:
        # Mark before recursing so a dependency cycle terminates.
        if path in emitted or path not in entry_by_path:
            return
        emitted.add(path)
        rule = rule_by_path.get(path)
        if rule is not None:
            for dep_name in rule.depends_required:
                dep_clean = dep_name.split("#")[0].strip()
                if dep_clean:
                    _emit_with_deps(f"rules/{dep_clean}")
        ordered.append(entry_by_path[path])

    for entry in capped_direct:
        _emit_with_deps(entry["rule_path"])
    # Append any dependency-only rules no surviving match reached.
    for entry in deps_only:
        _emit_with_deps(entry["rule_path"])

    load_sequence = ordered
    deps_only_paths = {entry["rule_path"] for entry in deps_only}

    # Token budget enforcement
    def _total_tokens(seq: list[dict]) -> int:
        return sum(e.get("token_budget", 0) for e in seq)

    while _total_tokens(load_sequence) > max_tokens and len(load_sequence) > 1:
        removed_idx = None
        for i in range(len(load_sequence) - 1, -1, -1):
            entry = load_sequence[i]
            # Protect HARD foundation rules and dependency-only rules: evicting a
            # dependency would leave the rule that requires it loaded without its
            # dep. Direct matches are evicted first instead.
            if entry.get("layer") != "HARD" and entry["rule_path"] not in deps_only_paths:
                removed_idx = i
                break
        if removed_idx is None:
            break
        removed = load_sequence.pop(removed_idx)
        deferred.append({"rule_path": removed["rule_path"], "reason": "token_budget"})

    return {
        "schema_version": "rule-loader-matcher/v1",
        "load_sequence": load_sequence,
        "deferred_rules": deferred,
        "candidate_rules": candidate_rules,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Metadata mode: full rule database output
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
    """Extract keywords, extensions, and paths from prompt text.

    Delegates to :func:`extract_context` (bounded n-grams + bare-filename dual
    routing) and returns its three fields as a tuple for existing callers.
    """
    ctx = extract_context(prompt)
    return ctx.keywords, ctx.extensions, ctx.paths


# ---------------------------------------------------------------------------
# Canonical trigger semantics (matcher-owned public API)
#
# Single source of truth for typed-trigger parsing, prompt tokenization,
# count validation, and per-signal evidence. All peripheral subsystems import
# these from ``match_rules`` rather than reimplementing them (Decision D5).
#
# ``_extract_from_prompt`` delegates to ``extract_context`` and ``explain_match``
# mirrors ``match_rules`` scoring exactly, so the two paths cannot diverge.
# ---------------------------------------------------------------------------

# Matcher-owned exported stop-word constants (public aliases of the internal
# frozensets used by the scoring engine and the prompt tokenizer).
HARD_STOP_WORDS: frozenset[str] = _HARD_STOP_WORDS
SOFT_STOP_WORDS: frozenset[str] = _SOFT_STOP_WORDS
SHORT_TECH_ALLOWLIST: frozenset[str] = _SHORT_TECH_ALLOWLIST

# Canonical combined typed-trigger count contract (kw + ext + file + dir).
TRIGGER_COUNT_MIN: int = 5
TRIGGER_COUNT_MAX: int = 11

# Maximum contiguous n-gram length emitted by ``extract_context`` and the
# maximum word count permitted for a registered ``kw:`` phrase.
MAX_TRIGGER_NGRAM: int = 4

_BARE_FILENAME_RE = re.compile(r"^[\w-]+\.\w{1,5}$")
_FILENAME_ALIASES: dict[str, str] = {"readme.me": "readme.md"}


@dataclass(frozen=True)
class TypedTrigger:
    """A single parsed, lowercased typed trigger entry.

    Attributes:
        kind: One of ``kw``, ``ext``, ``file``, or ``dir``.
        value: The lowercased trigger value with its prefix removed.
    """

    kind: str
    value: str


@dataclass
class TriggerSet:
    """Typed triggers for one rule, split by kind."""

    kw: list[str] = field(default_factory=list)
    ext: list[str] = field(default_factory=list)
    file: list[str] = field(default_factory=list)
    dir: list[str] = field(default_factory=list)

    def total(self) -> int:
        """Return the combined count across all four typed-trigger kinds."""
        return len(self.kw) + len(self.ext) + len(self.file) + len(self.dir)


@dataclass
class PromptContext:
    """Signals extracted from a user prompt.

    ``PromptContext`` has exactly three consumed categories. A bare filename is
    routed into ``paths`` (for ``file:`` matching) and retained in ``keywords``
    (for semantic matching); there is no unconsumed fourth category.
    """

    keywords: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Violation:
    """A trigger-count contract violation."""

    code: str
    message: str
    count: int


@dataclass(frozen=True)
class SignalEvidence:
    """One scoring signal that contributed to a rule's match."""

    signal: str
    detail: str
    points: int


@dataclass
class MatchEvidence:
    """Per-signal score attribution for a single rule against a context."""

    rule_filename: str
    total: int
    signals: list[SignalEvidence] = field(default_factory=list)


def normalize_trigger(raw: str) -> TypedTrigger:
    """Parse and lowercase a single typed trigger entry.

    An entry with no recognized prefix is treated as a ``kw`` trigger. Values
    are lowercased so downstream matching is case-insensitive.

    Args:
        raw: A trigger string such as ``kw:cortex search``, ``ext:.sql``,
            ``file:snowflake.yml``, ``dir:skills/``, or a bare ``cortex search``.

    Returns:
        The parsed :class:`TypedTrigger`.
    """
    s = raw.strip()
    for kind in ("ext", "file", "dir", "kw"):
        prefix = f"{kind}:"
        if s.startswith(prefix):
            return TypedTrigger(kind=kind, value=s[len(prefix) :].strip().lower())
    return TypedTrigger(kind="kw", value=s.lower())


def parse_typed_triggers(entries: list[str]) -> TriggerSet:
    """Split raw typed-trigger entries into a :class:`TriggerSet` by kind.

    Args:
        entries: Raw trigger strings (typically a rule's ``keywords`` list).

    Returns:
        A :class:`TriggerSet` grouping values under ``kw``/``ext``/``file``/``dir``.
    """
    result = TriggerSet()
    for entry in entries or []:
        if not str(entry).strip():
            continue
        trig = normalize_trigger(str(entry))
        getattr(result, trig.kind).append(trig.value)
    return result


def extract_context(prompt: str, max_ngram: int = MAX_TRIGGER_NGRAM) -> PromptContext:
    """Extract keywords, extensions, and paths from a user prompt.

    Emits contiguous n-grams of length 1 through ``max_ngram`` (capped at
    :data:`MAX_TRIGGER_NGRAM`) as keywords. Unigram keywords are stop-word
    filtered as in the legacy extractor; multi-word n-grams are contiguous spans
    over the raw token stream so registered 2-4 word phrases become reachable.
    A bare filename (``name.ext`` with no slash) is routed into ``paths`` and
    also retained as a keyword, without being double-counted within a class.

    Args:
        prompt: The raw user prompt text.
        max_ngram: Maximum contiguous n-gram length to emit (1-4).

    Returns:
        The populated :class:`PromptContext`.
    """
    max_n = max(1, min(max_ngram, MAX_TRIGGER_NGRAM))
    raw_words = re.split(r"[^\w./-]+", prompt.lower())

    extensions: list[str] = []
    paths: list[str] = []
    span_tokens: list[str] = []  # contiguous stream for multi-word n-grams
    unigrams: list[str] = []

    for raw_word in raw_words:
        word = raw_word.rstrip(".,;:!?")
        if not word:
            continue
        word = _FILENAME_ALIASES.get(word, word)
        if word.startswith(".") and len(word) > 1:
            extensions.append(word)
            continue
        if "/" in word:
            paths.append(word)
            ext_match = re.search(r"(\.\w{1,5})$", word)
            if ext_match:
                extensions.append(ext_match.group(1))
            continue
        if _BARE_FILENAME_RE.match(word):
            # RC2 fix: dual-route the bare filename to file context and keep the
            # lexical token for semantic matching. No extension is emitted here
            # so the file signal is not double-counted against the ext signal.
            paths.append(word)
            span_tokens.append(word)
            unigrams.append(word)
            continue
        # Plain word: always part of the contiguous n-gram stream.
        span_tokens.append(word)
        if word in _HARD_STOP_WORDS:
            continue
        if len(word) >= 4:
            unigrams.append(word)
        elif word.upper() == word and len(word) >= 2:
            unigrams.append(word)  # acronym (SQL, MCP, API)
        elif word in _SHORT_TECH_ALLOWLIST:
            unigrams.append(word)

    keywords: list[str] = list(unigrams)
    for n in range(2, max_n + 1):
        for i in range(len(span_tokens) - n + 1):
            keywords.append(" ".join(span_tokens[i : i + n]))

    return PromptContext(keywords=keywords, extensions=extensions, paths=paths)


def validate_trigger_counts(
    triggers: TriggerSet,
    *,
    min_count: int = TRIGGER_COUNT_MIN,
    max_count: int = TRIGGER_COUNT_MAX,
) -> list[Violation]:
    """Validate the combined typed-trigger count against the 5-11 contract.

    Args:
        triggers: The rule's parsed :class:`TriggerSet`.
        min_count: Minimum combined typed-trigger count (default 5).
        max_count: Maximum combined typed-trigger count (default 11).

    Returns:
        A list of :class:`Violation` (empty when the count is within bounds).
    """
    total = triggers.total()
    if total < min_count:
        return [
            Violation(
                code="too_few",
                message=f"combined typed-trigger count {total} is below minimum {min_count}",
                count=total,
            )
        ]
    if total > max_count:
        return [
            Violation(
                code="too_many",
                message=f"combined typed-trigger count {total} exceeds maximum {max_count}",
                count=total,
            )
        ]
    return []


def explain_match(
    rule: RuleEntry,
    context: PromptContext,
    *,
    soft_stop_words: frozenset[str] = _SOFT_STOP_WORDS,
) -> MatchEvidence:
    """Attribute a rule's match score to individual signals.

    Mirrors :func:`match_rules` scoring exactly so the aggregate ``total`` equals
    the score :func:`match_rules` would assign for the same rule and context.

    Args:
        rule: The rule to score.
        context: The extracted :class:`PromptContext`.
        soft_stop_words: Soft stop-word set (capped to 1 point), matching
            :func:`match_rules`.

    Returns:
        A :class:`MatchEvidence` with per-signal contributions and the total.
    """
    signals: list[SignalEvidence] = []

    for user_kw in context.keywords:
        best_kw_score = 0
        best_rule_kw = ""
        for rule_kw in rule.typed_kw:
            s = _score_kw(user_kw, rule_kw)
            if s > best_kw_score:
                best_kw_score = s
                best_rule_kw = rule_kw
        if user_kw in soft_stop_words and best_kw_score > 1:
            best_kw_score = 1
        if best_kw_score > 0:
            signals.append(
                SignalEvidence(
                    signal="kw",
                    detail=f"{user_kw!r} ~ {best_rule_kw!r}",
                    points=best_kw_score,
                )
            )

    rule_exts = {_normalize_ext(e) for e in rule.typed_ext}
    for ext in context.extensions:
        if _normalize_ext(ext) in rule_exts:
            signals.append(SignalEvidence(signal="ext", detail=ext, points=4))

    for path in context.paths:
        for pattern in rule.file_patterns:
            if fnmatch(path.lower(), pattern) or fnmatch(path.lower(), f"**/{pattern}"):
                signals.append(
                    SignalEvidence(signal="file", detail=f"{path} ~ {pattern}", points=5)
                )

    for path in context.paths:
        path_dir = dirname(path.lower())
        for pattern in rule.dir_patterns:
            clean_pattern = pattern.rstrip("/")
            if fnmatch(path_dir, clean_pattern) or fnmatch(path_dir, f"**/{clean_pattern}"):
                signals.append(
                    SignalEvidence(signal="dir", detail=f"{path_dir} ~ {pattern}", points=4)
                )

    return MatchEvidence(
        rule_filename=rule.filename,
        total=sum(s.points for s in signals),
        signals=signals,
    )


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

    # ``--keywords`` is the low-level interface for a comma-delimited list of
    # normalized terms. Recover when a caller sends a raw sentence instead.
    if len(kw_list) == 1 and len(kw_list[0].split()) > MAX_TRIGGER_NGRAM:
        p_kw, p_ext, p_paths = _extract_from_prompt(kw_list[0])
        kw_list = p_kw
        ext_list.extend(e for e in p_ext if e not in ext_list)
        path_list.extend(p for p in p_paths if p not in path_list)

    if args.prompt:
        p_kw, p_ext, p_paths = _extract_from_prompt(args.prompt)
        kw_list.extend(w for w in p_kw if w not in kw_list)
        ext_list.extend(e for e in p_ext if e not in ext_list)
        path_list.extend(p for p in p_paths if p not in path_list)

    file_ctx = FileContext(extensions=ext_list, paths=path_list)
    scored = match_rules(kw_list, file_ctx, list(db.values()))
    matched_filenames = {sr.rule.filename for sr in scored[: args.max_entries]}

    resolved, warnings = resolve_dependencies(scored, db, max_direct=args.max_entries)
    manifest = build_manifest(
        resolved,
        warnings,
        matched_filenames=matched_filenames,
        foundation=db.get("000-global-core.md"),
        max_entries=args.max_entries,
        max_tokens=args.max_tokens,
    )

    print(json.dumps(manifest, indent=2))
    return 0 if manifest["load_sequence"] else 1


if __name__ == "__main__":
    sys.exit(main())
