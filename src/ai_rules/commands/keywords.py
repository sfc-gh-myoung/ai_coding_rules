"""Keyword generator command for ai-rules CLI.

This command analyzes rule files using claude-sonnet-4-5 via Snowflake Cortex to
summarize rule content into 5-20 contextually meaningful keywords for the
**Keywords:** metadata field. High-confidence heuristic signals (technology terms,
code languages) supplement the LLM output. Results are cached based on file
content hash to avoid redundant API calls.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import time
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from ai_rules._shared.console import (
    console,
    err_console,
    log_error,
    log_info,
    log_success,
    log_warning,
)

# Files to skip when processing directories
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "AGENTS_V2.md",
    "RULES_INDEX.md",
}

# Domain-specific technology terms (optional context for prompt enrichment)
TECHNOLOGY_TERMS = {
    # Snowflake ecosystem
    "snowflake",
    "cortex",
    "streamlit",
    "snowpark",
    "spcs",
    "snowpipe",
    "snowsight",
    "snowcli",
    # AI/ML
    "aisql",
    "ai_complete",
    "ai_classify",
    "ai_extract",
    "ai_sentiment",
    "ai_embed",
    "embeddings",
    "rag",
    "llm",
    # Python ecosystem
    "python",
    "pytest",
    "ruff",
    "pydantic",
    "fastapi",
    "flask",
    "typer",
    "htmx",
    "pandas",
    "faker",
    # Data patterns
    "cdc",
    "etl",
    "elt",
    "rbac",
    "scd",
    "dmf",
    "udf",
    "udtf",
    "sproc",
    # Infrastructure
    "docker",
    "taskfile",
    "ci/cd",
    "git",
    "bash",
    "zsh",
    # Other
    "sql",
    "yaml",
    "json",
    "markdown",
    "typescript",
    "javascript",
    "react",
    "golang",
}

# Terms to exclude (too generic or common in all rules)
STOP_TERMS = {
    # Generic programming terms
    "data",
    "code",
    "file",
    "files",
    "example",
    "function",
    "method",
    "class",
    "variable",
    "value",
    "type",
    "types",
    "string",
    "number",
    "list",
    "dict",
    "object",
    "array",
    "return",
    "import",
    "module",
    "package",
    "new",
    "name",
    "description",
    "text",
    "field",
    "fields",
    "required",
    "order",
    "structure",
    "standard",
    "default",
    "actual",
    # Generic document terms
    "section",
    "rule",
    "rules",
    "pattern",
    "patterns",
    "best",
    "practice",
    "practices",
    "guide",
    "guidelines",
    "documentation",
    "reference",
    "references",
    "note",
    "notes",
    "tip",
    "tips",
    "warning",
    "error",
    "errors",
    # Common verbs
    "use",
    "using",
    "create",
    "creating",
    "add",
    "adding",
    "update",
    "updating",
    "delete",
    "deleting",
    "get",
    "set",
    "run",
    "running",
    "check",
    "checking",
    "make",
    "making",
    "start",
    "stop",
    "fix",
    "apply",
    "load",
    "loaded",
    "loading",
    "validate",
    "detect",
    "detection",
    # Schema/metadata terms (present in all rules)
    "metadata",
    "schemaversion",
    "keywords",
    "tokenbudget",
    "contexttier",
    "depends",
    "purpose",
    "scope",
    "contract",
    "mandatory",
    "forbidden",
    "validation",
    # Common markdown terms
    "markdown",
    "heading",
    "table",
    "tables",
    "link",
    "image",
    # v3.2 schema section headings (appear in 100+ rules as boilerplate)
    "inputs",
    "prerequisites",
    "execution",
    "steps",
    "step",
    "dependencies",
    "context",
    "management",
    "protocol",
    "principles",
    "design",
    "task",
    "tasks",
    "priority",
    "critical",
    "scenario",
    "triggers",
    "trigger",
    "changes",
    "changed",
    "workflow",
    "related",
    "external",
    "information",
    "decision",
    "recommendations",
    "selection",
    "choice",
    "approach",
    "correct",
    "wrong",
    "good",
    "bad",
    "over",
    "words",
    "are",
    "explicit",
    "verbose",
    "violations",
    "missing",
    "instead",
    "right",
    "too",
    "generic",
    "specific",
    "common",
    "issues",
    "pitfall",
    "pitfalls",
    "progress",
    # Common rule section terms (appear in all rules)
    "anti-pattern",
    "anti-patterns",
    "antipattern",
    "antipatterns",
    "mode",
    "core",
    "configuration",
    "setup",
    "overview",
    "introduction",
    "summary",
    "checklist",
    "output",
    "outputs",
    "format",
    "examples",
    "quick",
    "handling",
    "implementation",
    "details",
    "testing",
    "naming",
    "convention",
    "conventions",
    "considerations",
    "strategies",
    "strategy",
    # Common English words that slip through
    "and",
    "the",
    "for",
    "with",
    "from",
    "that",
    "this",
    "when",
    "how",
    "why",
    "what",
    "where",
    "which",
    "should",
    "must",
    "can",
    "will",
    "may",
    "not",
    "all",
    "any",
    "each",
    "every",
    "both",
    "either",
    "neither",
    "only",
    "also",
    "just",
    "more",
    "most",
    "other",
    "same",
    "such",
    "than",
    "then",
    "very",
    "well",
    "even",
    "still",
    "already",
    "always",
    "never",
    "often",
    "usually",
    "sometimes",
    # Additional generic words observed in heuristic output
    "first",
    "second",
    "third",
    "command",
    "window",
    "tree",
    "preservation",
    "recognition",
    "definition",
    "session",
    "pollution",
    "template",
    "initialization",
    "choose",
    "guidance",
    "split",
    "detailed",
    "parallel",
    "investigation",
    "constraints",
    "success",
    "failure",
    "count",
    "fixes",
    "version",
    "total",
    "lines",
    "basic",
    "advanced",
    "simple",
    "complex",
    "large",
    "small",
    "existing",
    "available",
    "current",
    "major",
    "minor",
    "read",
    "write",
    "find",
    "determine",
    "process",
    "optional",
    "response",
    "request",
    "system",
    "model",
    "models",
    "result",
    "results",
    "general",
    "review",
    "ensure",
    "key",
    "point",
    "points",
    "level",
    "levels",
    "single",
    "multiple",
    "primary",
    "secondary",
    "full",
    "empty",
    "top",
    "bottom",
    "above",
    "below",
    "inside",
    "outside",
    "before",
    "after",
    "between",
    "through",
    "across",
    "within",
    "without",
    "during",
    "about",
    "like",
    "into",
    "down",
    "back",
    "next",
    "last",
    "end",
    "need",
    "needs",
    "different",
    "proper",
    "clear",
    "avoid",
    "include",
    "includes",
    "state",
    "based",
    "spec",
    "original",
    "correctly",
    "content",
    "automatically",
    "manual",
    "pair",
    "formula",
    "sections",
    "subsection",
    "commands",
    "options",
    "severity",
    "budget",
    "sizing",
    "size",
    "declaration",
    "techniques",
    "scenarios",
    "change",
    "automated",
    "script",
    "integration",
    "complexity",
    "curation",
    "compact",
    "tier",
    "responsibilities",
    "similar",
    "fill",
    "requirements",
    "estimation",
    "placement",
    "optimized",
    "buried",
    "tool",
    "tools",
    "parameter",
    "parameters",
    "parsing",
    "log",
    "recovery",
    "specialized",
    "tokens",
    "methods",
    "fundamentals",
    "boundaries",
    "specifications",
    "behaviors",
    "viable",
    "discoverability",
    "migration",
}

# Default cache file path
CACHE_FILENAME = ".keywords-cache.json"


# T4: Module-level map populated by ``_parse_keyword_response`` on every LLM
# response. Keys are keyword strings, values are the LLM-emitted one-sentence
# rationale (empty string when the LLM returned the legacy plain-string shape).
# Consumers must snapshot immediately after a parse call; the map is reset at
# the start of each ``_parse_keyword_response`` invocation.
_LAST_RATIONALE_MAP: dict[str, str] = {}


def get_last_rationale_map() -> dict[str, str]:
    """Return a snapshot of the rationale map captured by the last parse call.

    See ``_LAST_RATIONALE_MAP`` module attribute.
    """
    return dict(_LAST_RATIONALE_MAP)


# ---------------------------------------------------------------------------
# T5 — Stoplist and per-rule overrides for the heuristic supplement path
# ---------------------------------------------------------------------------

# Repo root discovered relative to this file: src/ai_rules/commands/keywords.py
# → parents[3] is the repo root.
_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_DEFAULT_STOPLIST_PATH: Path = _REPO_ROOT / ".workbench" / "config" / "keyword_stoplist.txt"
_DEFAULT_STOPLIST_OVERRIDES_PATH: Path = (
    _REPO_ROOT / ".workbench" / "config" / "keyword_stoplist_overrides.yml"
)

_STOPLIST_CACHE: set[str] | None = None
_STOPLIST_OVERRIDES_CACHE: dict[str, set[str]] | None = None


def load_keyword_stoplist(path: Path | None = None, *, refresh: bool = False) -> set[str]:
    """Load the newline-delimited keyword stop-list.

    Args:
        path: Optional override path (used in tests). When ``None`` the
            default workbench path is used and the result is cached.
        refresh: When True, bypass the cache and re-read from disk.

    Returns:
        Lower-cased set of tokens the heuristic supplement path must never
        emit unless a per-rule override permits it. Empty set when the file
        does not exist (soft-fail: T4 landed the parser but the file may be
        absent in some checkouts).
    """
    global _STOPLIST_CACHE
    if path is None and _STOPLIST_CACHE is not None and not refresh:
        return _STOPLIST_CACHE

    resolved = path or _DEFAULT_STOPLIST_PATH
    tokens: set[str] = set()
    if resolved.exists():
        for line in resolved.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                tokens.add(stripped.lower())

    if path is None:
        _STOPLIST_CACHE = tokens
    return tokens


def load_keyword_stoplist_overrides(
    path: Path | None = None, *, refresh: bool = False
) -> dict[str, set[str]]:
    """Load per-rule stop-list overrides from YAML.

    The YAML schema is::

        overrides:
          <rule filename>.md:
            override: [<token>, ...]
            justification: <text>
            co_occurring_discriminators: [<token>, ...]

    Args:
        path: Optional override path (used in tests). When ``None`` the
            default workbench path is used and the result is cached.
        refresh: When True, bypass the cache and re-read from disk.

    Returns:
        Mapping of rule filename → lower-cased set of override tokens
        that ARE permitted for that rule despite being on the stoplist.
        Empty dict when the file is absent.
    """
    global _STOPLIST_OVERRIDES_CACHE
    if path is None and _STOPLIST_OVERRIDES_CACHE is not None and not refresh:
        return _STOPLIST_OVERRIDES_CACHE

    resolved = path or _DEFAULT_STOPLIST_OVERRIDES_PATH
    result: dict[str, set[str]] = {}
    if resolved.exists():
        import yaml

        try:
            parsed = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            parsed = {}
        overrides_section = parsed.get("overrides", {}) if isinstance(parsed, dict) else {}
        if isinstance(overrides_section, dict):
            for rule_filename, entry in overrides_section.items():
                if not isinstance(entry, dict):
                    continue
                tokens_raw = entry.get("override", [])
                if isinstance(tokens_raw, list):
                    result[str(rule_filename)] = {
                        str(t).lower() for t in tokens_raw if isinstance(t, str)
                    }

    if path is None:
        _STOPLIST_OVERRIDES_CACHE = result
    return result


def _reset_stoplist_caches() -> None:
    """Clear cached stoplist state — test helper only."""
    global _STOPLIST_CACHE, _STOPLIST_OVERRIDES_CACHE
    _STOPLIST_CACHE = None
    _STOPLIST_OVERRIDES_CACHE = None


# ---------------------------------------------------------------------------
# T6 — Corpus-wide keyword collision map + post-filter
# ---------------------------------------------------------------------------

_DEFAULT_RULES_INDEX_PATH: Path = _REPO_ROOT / "rules" / "RULES_INDEX.md"
_DEFAULT_EXCLUDE_LIST_PATH: Path = _REPO_ROOT / ".workbench" / "config" / "exclude_list.txt"

# Line schema in RULES_INDEX.md (per its header comment):
#   <filename> tier=<T> [ext=..] [file=..] [dir=..] kw=<w1> <w2> ...
_RULES_INDEX_LINE = re.compile(r"^(?P<filename>\S+\.md)\s+tier=\S+.*?\bkw=(?P<kws>[^\r\n]+)$")


def _load_exclude_list(path: Path | None = None) -> set[str]:
    """Return the set of rule filenames to exclude from collision counts."""
    resolved = path or _DEFAULT_EXCLUDE_LIST_PATH
    excluded: set[str] = set()
    if resolved.exists():
        for line in resolved.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                excluded.add(stripped)
    return excluded


def build_keyword_collision_map(
    rules_index_path: Path | None = None,
    exclude_list_path: Path | None = None,
) -> dict[str, list[str]]:
    """Build an inverted index from RULES_INDEX.md: keyword → list of rule filenames.

    Args:
        rules_index_path: Path to RULES_INDEX.md (defaults to repo copy).
        exclude_list_path: Path to the exclude list (defaults to workbench copy).
            Filenames on the exclude list are dropped from the counts.

    Returns:
        Mapping from lower-cased keyword token to the sorted list of production
        rule filenames that declare it in their ``kw=`` field.
    """
    index_path = rules_index_path or _DEFAULT_RULES_INDEX_PATH
    excluded = _load_exclude_list(exclude_list_path)

    inverted: dict[str, set[str]] = {}
    if not index_path.exists():
        return {}

    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        m = _RULES_INDEX_LINE.match(line)
        if not m:
            continue
        filename = m.group("filename")
        if filename in excluded:
            continue
        kws_str = m.group("kws").strip()
        # Split on whitespace; keywords are single tokens using `-` for compounds
        for kw in kws_str.split():
            key = kw.lower()
            if not key:
                continue
            inverted.setdefault(key, set()).add(filename)

    return {kw: sorted(rules) for kw, rules in inverted.items()}


def find_collision_violations(
    collision_map: dict[str, list[str]],
    max_collision: int,
) -> dict[str, list[str]]:
    """Return the subset of the collision map that exceeds the threshold."""
    return {kw: rules for kw, rules in collision_map.items() if len(rules) > max_collision}


def apply_collision_postfilter(
    keywords: list[str],
    rationale_candidates: list[str],
    collision_map: dict[str, list[str]],
    max_collision: int,
    *,
    current_rule_filename: str | None = None,
) -> list[str]:
    """Reject over-threshold keywords, substituting next-best rationale candidates.

    Args:
        keywords: Post-merge candidate list, in preference order.
        rationale_candidates: Additional keywords the LLM ranked but the merge
            step did not select (typically ``get_last_rationale_map().keys()``).
        collision_map: Output of :func:`build_keyword_collision_map`.
        max_collision: Reject a keyword when it appears in strictly more than
            ``max_collision`` rules in the corpus.
        current_rule_filename: When set, the current rule is excluded from the
            collision count (so a keyword the current rule ALREADY carries does
            not falsely inflate its own count).

    Returns:
        Filtered keyword list with rejects replaced (in order) by the next
        eligible entry from ``rationale_candidates``. Length is bounded by the
        input length.
    """

    def _count_for(kw: str) -> int:
        rules = collision_map.get(kw.lower(), [])
        if current_rule_filename and current_rule_filename in rules:
            return len(rules) - 1
        return len(rules)

    accepted: list[str] = []
    seen_lower: set[str] = set()
    pool = list(rationale_candidates)

    def _try_add(candidate: str) -> bool:
        key = candidate.lower()
        if key in seen_lower:
            return False
        if _count_for(candidate) > max_collision:
            return False
        accepted.append(candidate)
        seen_lower.add(key)
        return True

    for kw in keywords:
        if _try_add(kw):
            continue
        # Rejected — try to substitute from the rationale pool
        substituted = False
        while pool:
            candidate = pool.pop(0)
            if _try_add(candidate):
                substituted = True
                break
        if not substituted:
            # No eligible substitute: keep the original slot empty by NOT
            # appending. Caller trims to `count`, so this is safe.
            continue

    return accepted


def load_snowflake_config(connection_name: str) -> dict[str, Any]:
    """Load connection config from ~/.snowflake/connections.toml or config.toml.

    Args:
        connection_name: Name of the connection in the config file.

    Returns:
        Dict with account, user, and authentication details.

    Raises:
        FileNotFoundError: If no config file exists.
        ValueError: If connection_name not found in config.
    """
    snowflake_dir = Path.home() / ".snowflake"
    connections_path = snowflake_dir / "connections.toml"
    config_path = snowflake_dir / "config.toml"

    config_file = None
    if connections_path.exists():
        config_file = connections_path
    elif config_path.exists():
        config_file = config_path
    else:
        raise FileNotFoundError(
            f"No Snowflake config found. Expected:\n  - {connections_path}\n  - {config_path}"
        )

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    if connection_name not in config:
        available = list(config.keys())
        raise ValueError(
            f"Connection '{connection_name}' not found in {config_file.name}. "
            f"Available: {available}"
        )

    return config[connection_name]


@dataclass
class KeywordCandidate:
    """A candidate keyword with scoring information."""

    term: str
    score: float
    source: str  # "llm", "header", "code_lang", "emphasis", "technology"

    def __hash__(self) -> int:
        """Hash by normalized term for deduplication."""
        return hash(self.term.lower())

    def __eq__(self, other: object) -> bool:
        """Equal if terms match (case-insensitive)."""
        if not isinstance(other, KeywordCandidate):
            return False
        return self.term.lower() == other.term.lower()


@dataclass
class ExtractionResult:
    """Result of keyword extraction for a rule file."""

    file_path: Path
    current_keywords: list[str] = field(default_factory=list)
    suggested_keywords: list[str] = field(default_factory=list)
    candidates: list[KeywordCandidate] = field(default_factory=list)
    # T7: Per-keyword rationale captured from the LLM response (empty when
    # heuristic fallback was used or the LLM returned the legacy string shape).
    rationale_map: dict[str, str] = field(default_factory=dict)

    @property
    def added(self) -> set[str]:
        """Keywords in suggested but not in current."""
        current_lower = {k.lower() for k in self.current_keywords}
        return {k for k in self.suggested_keywords if k.lower() not in current_lower}

    @property
    def removed(self) -> set[str]:
        """Keywords in current but not in suggested."""
        suggested_lower = {k.lower() for k in self.suggested_keywords}
        return {k for k in self.current_keywords if k.lower() not in suggested_lower}

    @property
    def kept(self) -> set[str]:
        """Keywords in both current and suggested."""
        suggested_lower = {k.lower() for k in self.suggested_keywords}
        return {k for k in self.current_keywords if k.lower() in suggested_lower}


def _deduplicate_across_rules(
    results: list[ExtractionResult],
    max_overlap: int = 2,
) -> None:
    """Remove over-shared keywords from rules where they're least relevant.

    For keywords appearing in more than *max_overlap* rules, keep the keyword
    only in the top *max_overlap* rules (ranked by how often the keyword term
    appears in the rule file content). Mutates ``suggested_keywords`` in place.

    Args:
        results: Extraction results to deduplicate across.
        max_overlap: Maximum number of rules that may share a keyword.
    """
    # Build frequency map: lowered keyword -> list of (result, body_count)
    keyword_owners: dict[str, list[tuple[ExtractionResult, int]]] = {}
    for result in results:
        content = result.file_path.read_text(encoding="utf-8").lower()
        for kw in result.suggested_keywords:
            key = kw.lower()
            body_count = content.count(key)
            keyword_owners.setdefault(key, []).append((result, body_count))

    # For keywords in too many rules, keep only the top-scoring ones
    for key, owners in keyword_owners.items():
        if len(owners) <= max_overlap:
            continue
        # Sort by body count descending; keep top max_overlap
        owners.sort(key=lambda x: x[1], reverse=True)
        keep_results = {id(r) for r, _ in owners[:max_overlap]}
        for result, _ in owners[max_overlap:]:
            if id(result) not in keep_results:
                result.suggested_keywords = [
                    kw for kw in result.suggested_keywords if kw.lower() != key
                ]


def _content_hash(content: str) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load_cache(cache_path: Path) -> dict:
    """Load keyword cache from disk."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    """Save keyword cache to disk."""
    with contextlib.suppress(OSError):
        cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _get_cached_keywords(cache: dict, file_key: str, content_hash: str) -> list[str] | None:
    """Get cached keywords if content hash matches."""
    entry = cache.get(file_key)
    if entry and entry.get("hash") == content_hash:
        return entry.get("keywords")
    return None


def _set_cached_keywords(cache: dict, file_key: str, content_hash: str, kws: list[str]) -> None:
    """Store keywords in cache with content hash."""
    cache[file_key] = {"hash": content_hash, "keywords": kws}


def _parse_cortex_sse_response(raw: str) -> str:
    """Parse a Cortex streaming SSE response into the full text.

    The Cortex inference API returns Server-Sent Events where each line
    is ``data: {JSON}``. Each JSON chunk contains a delta with partial
    content. This function concatenates all deltas into the complete text.
    """
    parts: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[len("data:") :].strip()
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    parts.append(content)
        except (json.JSONDecodeError, IndexError, KeyError):
            continue
    return "".join(parts)


def _call_cortex_complete(
    content: str,
    connection_name: str = "default",
    count: int = 15,
    debug: bool = False,
) -> list[str]:
    """Call Cortex REST API to generate keywords for rule content.

    Uses claude-sonnet-4-5 to summarize the rule into 5-20 contextually meaningful
    keywords and phrases for semantic discovery.

    Args:
        content: The rule file content.
        connection_name: Snowflake connection name from ~/.snowflake/connections.toml.
        count: Maximum number of keywords (LLM chooses 5-20 based on rule complexity).
        debug: Enable debug output.

    Returns:
        List of keyword strings from the LLM.

    Raises:
        RuntimeError: If API call fails after retries.
    """
    import requests

    config = load_snowflake_config(connection_name)
    account = config.get("account", config.get("accountname", ""))
    token = config.get("token") or config.get("password", "")

    if not account or not token:
        raise RuntimeError(
            f"Snowflake connection '{connection_name}' is missing 'account' or "
            f"'token'/'password'. Check ~/.snowflake/connections.toml."
        )

    stop_terms_list = ", ".join(sorted(STOP_TERMS))

    # T4: Enforce absolute 5-7 count regardless of `count` argument. The `count`
    # parameter now caps the upper bound but the LLM must never emit fewer than 5
    # nor more than 7. This aligns with §5.5 Improvement Design of the v5 plan.
    max_count = min(max(count, 5), 7)

    prompt = f"""You are a senior technical writer summarizing AI coding rule files into discovery keywords.

Your task: Read the rule file below, understand its core purpose and distinguishing concepts, then distill that understanding into EXACTLY 5 to {max_count} keywords or short phrases. Never return fewer than 5 or more than {max_count}.

These keywords populate the **Keywords:** metadata field used by AI agents to discover which rules to load via grep/search against a RULES_INDEX.md file.

Step 1 — Understand the rule:
- What specific technology, framework, or tool does this rule govern?
- What actions, patterns, or workflows does it prescribe?
- What distinguishes this rule from other rules in the same domain?
- Is this a sub-domain rule (e.g. a rule about pytest fixtures WITHIN the Python ecosystem, or a rule about masking policies WITHIN Snowflake)? If so, the bare parent technology name is FORBIDDEN as a keyword.

Step 2 — Generate keywords that:
- Capture the core concepts, technologies, and actionable patterns in this rule
- Prefer COMPOUND phrases (2+ tokens) over single tokens. At least 60% of keywords must be compound phrases.
- Include proper nouns with correct casing (e.g., "Snowflake", "FastAPI", "RBAC") ONLY when the rule is the top-level rule for that technology; sub-domain rules must use compound qualifications instead.
- Include compound phrases where meaningful (e.g., "cortex agent", "masking policy", "session state")
- Use lowercase for multi-word descriptive terms (e.g., "error handling", "dynamic table")
- Would help an AI agent searching for rules relevant to a specific task
- Are specific enough to distinguish THIS rule from other rules

Do NOT include any of these generic terms (they appear in every rule and have no discovery value):
{stop_terms_list}

CRITICAL — Never use bare single-word domain terms. Always qualify with the specific aspect this rule covers:
- BAD:  "SQL", "testing", "performance", "validation", "security", "python", "snowflake", "docker", "react", "yaml", "json"
- GOOD: "SQL file formatting", "pytest fixtures", "query partition pruning", "schema compliance validation", "RBAC role grants"
Each keyword must be specific enough that an agent could identify THIS rule from the keyword alone, without needing the rule filename.

CRITICAL — Sub-domain rule prohibition: If this rule is a specialization within a broader technology domain (e.g. `206-python-pytest.md` within Python; `106a-snowflake-semantic-views-advanced.md` within Snowflake), you MUST NOT emit the bare parent technology token (`python`, `snowflake`, etc.) as a keyword. Emit qualified compounds instead.

CRITICAL — Rationale required: For EACH keyword, emit a one-sentence rationale explaining WHY this token uniquely identifies the rule (what distinguishes it from sibling rules in the same domain). Rationale must be non-empty.

Return ONLY a JSON array of 5 to {max_count} objects. Each object has this exact shape:
  {{"keyword": "<kw string>", "rationale": "<one-sentence justification>"}}
No explanation, no markdown, no other text outside the JSON array.

Rule file content:
---
{content[:32000]}
---"""

    if ".snowflakecomputing.com" in account:
        url = f"https://{account}/api/v2/cortex/inference:complete"
    else:
        url = f"https://{account}.snowflakecomputing.com/api/v2/cortex/inference:complete"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    }
    payload = {
        "model": "claude-sonnet-4-5",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1,
    }

    # Retry with exponential backoff (per rule 118)
    max_retries = 3
    base_delay = 1.0

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                err_console.print(
                    f"[dim][DEBUG] Cortex API attempt {attempt + 1}/{max_retries}[/dim]"
                )

            resp = requests.post(url, headers=headers, json=payload, timeout=30)  # ty: ignore[invalid-argument-type]

            if resp.status_code == 200:
                text = _parse_cortex_sse_response(resp.text)

                if debug:
                    err_console.print(f"[dim][DEBUG] LLM response text: {text[:200]}[/dim]")

                return _parse_keyword_response(text, count)

            elif resp.status_code in (429, 503, 504):
                delay = base_delay * (2**attempt)
                if debug:
                    err_console.print(
                        f"[dim][DEBUG] Retryable error {resp.status_code}, "
                        f"waiting {delay:.1f}s[/dim]"
                    )
                time.sleep(delay)
                last_error = RuntimeError(
                    f"Cortex API returned {resp.status_code}: {resp.text[:200]}"
                )
            else:
                raise RuntimeError(f"Cortex API returned {resp.status_code}: {resp.text[:200]}")

        except requests.exceptions.RequestException as e:
            last_error = RuntimeError(f"Cortex API request failed: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)
                time.sleep(delay)

    raise last_error or RuntimeError("Cortex API call failed after retries")


def _parse_keyword_response(text: str, count: int) -> list[str]:
    """Parse LLM response text into a list of keyword strings.

    Accepts two LLM output shapes:

    1. NEW (T4): a JSON array of objects: ``[{"keyword": "...", "rationale": "..."}, ...]``
    2. LEGACY (backward compat): a JSON array of strings, comma-separated list,
       or newline-separated list.

    When the new object shape is detected, the per-keyword rationale is captured
    into the module-level ``_LAST_RATIONALE_MAP`` for downstream consumers
    (e.g. the ``--rationale`` flag added in Phase 0.5 Task 7). Legacy shapes
    populate an empty rationale for each keyword to keep the map complete.

    Args:
        text: Raw LLM response text.
        count: Upper bound on returned keywords.

    Returns:
        List of keyword strings (rationale metadata is written to
        ``_LAST_RATIONALE_MAP`` as a side effect).
    """
    text = text.strip()

    global _LAST_RATIONALE_MAP
    _LAST_RATIONALE_MAP = {}

    # Try JSON array first (both object shape and string shape live here)
    try:
        # Match the outer-most array. Use greedy match with DOTALL so nested
        # object braces do not truncate the capture.
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            if isinstance(parsed, list) and parsed:
                # NEW shape: list of dicts with keyword+rationale
                if all(isinstance(item, dict) and "keyword" in item for item in parsed):
                    keywords: list[str] = []
                    for item in parsed:
                        kw = str(item.get("keyword", "")).strip()
                        rationale = str(item.get("rationale", "")).strip()
                        if kw:
                            keywords.append(kw)
                            _LAST_RATIONALE_MAP[kw] = rationale
                    return keywords[:count]
                # LEGACY shape: list of strings
                if all(isinstance(k, str) for k in parsed):
                    keywords = [k.strip() for k in parsed if k.strip()][:count]
                    for kw in keywords:
                        _LAST_RATIONALE_MAP[kw] = ""
                    return keywords
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: try comma-separated
    if "," in text:
        keywords = [k.strip().strip('"').strip("'") for k in text.split(",")]
        keywords = [k for k in keywords if k and k.lower() not in STOP_TERMS]
        if keywords:
            keywords = keywords[:count]
            for kw in keywords:
                _LAST_RATIONALE_MAP[kw] = ""
            return keywords

    # Fallback: newline-separated (strip bullet markers)
    lines = text.strip().splitlines()
    keywords = []
    for line in lines:
        line = re.sub(r"^[\s\-*\d.]+", "", line).strip().strip('"').strip("'")
        if line and line.lower() not in STOP_TERMS:
            keywords.append(line)
    keywords = keywords[:count]
    for kw in keywords:
        _LAST_RATIONALE_MAP[kw] = ""
    return keywords


class KeywordExtractor:
    """Extract and rank keywords from rule files using Cortex LLM and heuristic signals."""

    def __init__(self, *, debug: bool = False, connection_name: str = "default"):
        """Initialize the keyword extractor.

        Args:
            debug: Enable debug output
            connection_name: Snowflake connection name for Cortex API calls.
        """
        self.debug = debug
        self.connection_name = connection_name

    def _debug(self, message: str) -> None:
        """Print debug message if debug mode enabled."""
        if self.debug:
            err_console.print(f"[dim][DEBUG] {message}[/dim]")

    def _extract_headers(self, content: str) -> list[KeywordCandidate]:
        """Extract keywords from H2 and H3 headers."""
        candidates = []

        # Match ## and ### headers
        header_pattern = r"^#{2,3}\s+(?:\d+\.\s+)?(.+)$"
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            header_text = match.group(1).strip()

            # Skip all v3.2 schema boilerplate section names
            if header_text.lower() in {
                "metadata",
                "purpose",
                "scope",
                "rule scope",
                "quick start",
                "quick start tl;dr",
                "contract",
                "inputs and prerequisites",
                "mandatory",
                "forbidden",
                "execution steps",
                "output format",
                "validation",
                "post-execution checklist",
                "anti-patterns and common mistakes",
                "output format examples",
                "references",
                "external documentation",
                "related rules",
                "dependencies",
                "design principles",
                "key principles",
                "implementation details",
                "performance optimization",
                "performance considerations",
                "performance and optimization",
                "troubleshooting",
                "validation checklist",
                "rules loaded",
                "unreleased",
                "fixed",
                "added",
                "changed",
                "deprecated",
                "quantification standards",
                "related examples",
            }:
                continue

            # Keep the full header text as a compound phrase if it's
            # domain-specific (not just boilerplate words)
            # Strip inline markdown formatting (bold, italic, backticks)
            clean_header = re.sub(r"[*_`]", "", header_text).strip()
            # Strip common numbered prefixes like "Step 1:", "Scenario 4:", "Anti-Pattern 1:"
            clean_header = re.sub(
                r"^(?:Step \d+|Scenario \d+|Anti-Pattern \d+|Priority \d+|Phase \d+|Option \d+|Example \d+)\s*[:—–-]\s*",
                "",
                clean_header,
            ).strip()
            # Strip trailing parenthetical qualifiers like "(CRITICAL - Must Pass)"
            clean_header = re.sub(r"\s*\([^)]*\)\s*$", "", clean_header).strip()
            # Strip "Error N:" prefixes
            clean_header = re.sub(r"^Error \d+\s*:\s*", "", clean_header).strip()
            # Strip any remaining leading/trailing colons or markdown artifacts
            clean_header = clean_header.strip(":").strip()
            # Skip question-form headers ("What is...?", "How to...?")
            if clean_header.endswith("?"):
                continue
            # Skip headers with special characters (≤, >, ~, =, ---) — usually not keywords
            if re.search(r"[≤≥<>=~]|^---$", clean_header):
                continue
            # Skip headers that are too long (>45 chars) — not useful as keywords
            if len(clean_header) > 45:
                continue
            # Skip if cleaned header is empty
            if not clean_header:
                continue

            header_words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b", clean_header)
            non_stop_words = [w for w in header_words if w.lower() not in STOP_TERMS]

            # If the header has 2+ meaningful words, keep as compound phrase
            if len(non_stop_words) >= 2:
                candidates.append(KeywordCandidate(term=clean_header, score=0.9, source="header"))
            elif len(non_stop_words) == 1:
                word = non_stop_words[0]
                # Only keep single words that look like proper nouns or tech terms
                if word[0].isupper() or word.lower() in TECHNOLOGY_TERMS:
                    candidates.append(KeywordCandidate(term=word, score=0.8, source="header"))

        return candidates

    def _extract_code_languages(self, content: str) -> list[KeywordCandidate]:
        """Extract programming language identifiers from code blocks."""
        candidates = []

        # Match ```language
        lang_pattern = r"```(\w+)"
        languages = set(re.findall(lang_pattern, content))

        # Map common language identifiers
        lang_map = {
            "python": "Python",
            "py": "Python",
            "sql": "SQL",
            "bash": "Bash",
            "sh": "shell",
            "shell": "shell",
            "zsh": "Zsh",
            "javascript": "JavaScript",
            "js": "JavaScript",
            "typescript": "TypeScript",
            "ts": "TypeScript",
            "yaml": "YAML",
            "yml": "YAML",
            "json": "JSON",
            "toml": "TOML",
            "markdown": "Markdown",
            "md": "Markdown",
            "go": "Go",
            "golang": "Go",
            "dockerfile": "Docker",
            "html": "HTML",
            "css": "CSS",
        }

        for lang in languages:
            normalized = lang_map.get(lang.lower(), lang)
            if normalized.lower() not in STOP_TERMS:
                candidates.append(KeywordCandidate(term=normalized, score=0.6, source="code_lang"))

        return candidates

    def _extract_emphasized_terms(self, content: str) -> list[KeywordCandidate]:
        """Extract terms from bold and backtick emphasis."""
        candidates = []

        # Bold terms: **term** or __term__
        bold_pattern = r"\*\*([^*]+)\*\*|__([^_]+)__"
        for match in re.finditer(bold_pattern, content):
            term = match.group(1) or match.group(2)
            # Skip if it looks like a label (ends with :)
            if term.endswith(":"):
                continue
            # Skip common schema metadata field names
            if term.lower() in {
                "schemaversion",
                "ruleversion",
                "lastupdated",
                "keywords",
                "tokenbudget",
                "contexttier",
                "depends",
                "what this rule covers",
                "when to load this rule",
                "must load first",
                "note",
                "critical",
                "always",
                "never",
            }:
                continue
            # Extract words and check if the term is meaningful
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b", term)
            non_stop_words = [w for w in words if w.lower() not in STOP_TERMS]
            # Keep compound phrases with 2+ meaningful words (cap length)
            if len(non_stop_words) >= 2 and len(term) <= 50:
                candidates.append(KeywordCandidate(term=term, score=0.6, source="emphasis"))
            elif len(non_stop_words) == 1:
                word = non_stop_words[0]
                # Only keep single words that look like proper nouns or tech terms
                if word[0].isupper() or word.lower() in TECHNOLOGY_TERMS:
                    candidates.append(KeywordCandidate(term=word, score=0.5, source="emphasis"))

        # Backtick terms: `term`
        backtick_pattern = r"`([^`]+)`"
        for match in re.finditer(backtick_pattern, content):
            term = match.group(1)
            # Skip multi-line matches (from code blocks) and markdown artifacts
            if "\n" in term or "*" in term:
                continue
            # Skip if it looks like code/command (has spaces, paths, function calls)
            if " " in term or "/" in term or "(" in term:
                continue
            # Skip CLI flags like --json, --schema
            if term.startswith("-"):
                continue
            # Skip file paths and extensions
            if "." in term and term.split(".")[-1] in {
                "py",
                "md",
                "sql",
                "yml",
                "yaml",
                "toml",
                "json",
            }:
                continue
            if term.lower() not in STOP_TERMS and len(term) > 2:
                candidates.append(KeywordCandidate(term=term, score=0.4, source="emphasis"))

        return candidates

    def _extract_technology_terms(self, content: str) -> list[KeywordCandidate]:
        """Extract known technology terms from content."""
        candidates = []
        content_lower = content.lower()

        for tech in TECHNOLOGY_TERMS:
            # Check if term appears in content
            if re.search(rf"\b{re.escape(tech)}\b", content_lower):
                # Use original casing for display
                candidates.append(KeywordCandidate(term=tech, score=0.7, source="technology"))

        return candidates

    def _extract_current_keywords(self, content: str) -> list[str]:
        """Extract current keywords from the **Keywords:** metadata field."""
        pattern = r"\*\*Keywords:\*\*\s*(.+)"
        match = re.search(pattern, content)
        if match:
            keywords_str = match.group(1).strip()
            return [k.strip() for k in keywords_str.split(",") if k.strip()]
        return []

    def _collect_heuristic_candidates(self, content: str) -> list[KeywordCandidate]:
        """Collect keyword candidates from all heuristic signals."""
        candidates = []
        candidates.extend(self._extract_headers(content))
        candidates.extend(self._extract_code_languages(content))
        candidates.extend(self._extract_emphasized_terms(content))
        candidates.extend(self._extract_technology_terms(content))
        return candidates

    def _rank_heuristic_keywords(
        self, candidates: list[KeywordCandidate], count: int = 12
    ) -> list[str]:
        """Rank and deduplicate heuristic candidates (fallback when no API)."""
        term_scores: dict[str, float] = {}
        term_display: dict[str, str] = {}

        for candidate in candidates:
            key = candidate.term.lower()
            if key in STOP_TERMS:
                continue
            if key not in term_scores:
                term_scores[key] = 0.0
                term_display[key] = candidate.term
            term_scores[key] += candidate.score
            if candidate.term[0].isupper() and not term_display[key][0].isupper():
                term_display[key] = candidate.term

        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        return [term_display[key] for key, _score in sorted_terms[:count]]

    @staticmethod
    def _merge_llm_with_heuristics(
        llm_keywords: list[str],
        heuristic_candidates: list[KeywordCandidate],
        count: int,
        rule_filename: str | None = None,
    ) -> list[str]:
        """Merge LLM keywords with high-confidence heuristic candidates.

        The LLM output is the primary set. High-confidence heuristic terms
        (technology matches, code languages) that the LLM missed are appended
        up to the count limit.

        T5: Heuristic supplements are additionally filtered against the
        workbench keyword stop-list. Tokens on the stop-list are dropped
        unless the rule's filename appears in the per-rule overrides file
        (``.workbench/config/keyword_stoplist_overrides.yml``).

        Args:
            llm_keywords: Keywords from the LLM.
            heuristic_candidates: Pre-extracted heuristic candidates.
            count: Maximum number of keywords.
            rule_filename: Optional rule filename (``file_path.name``) used
                to consult per-rule stop-list overrides. When ``None``, no
                overrides apply and every stop-list token is dropped.

        Returns:
            Merged keyword list, LLM terms first.
        """
        result = list(llm_keywords)
        result_lower = {k.lower() for k in result}

        stoplist = load_keyword_stoplist()
        overrides_map = load_keyword_stoplist_overrides()
        permitted_overrides = overrides_map.get(rule_filename or "", set())

        # Only supplement with high-confidence signals the LLM missed
        high_confidence_sources = {"technology", "code_lang"}
        supplements = {}
        for c in heuristic_candidates:
            if c.source in high_confidence_sources and c.term.lower() not in result_lower:
                key = c.term.lower()
                if key in STOP_TERMS:
                    continue
                # T5: workbench stop-list filter (with per-rule override escape)
                if key in stoplist and key not in permitted_overrides:
                    continue
                if key not in supplements:
                    supplements[key] = c.term

        # Sort supplements by term for deterministic output
        for term in sorted(supplements.values()):
            if len(result) >= count:
                break
            result.append(term)

        return result

    def suggest_keywords(
        self,
        file_path: Path,
        count: int = 15,
        *,
        use_api: bool = True,
        cache: dict | None = None,
        force: bool = False,
        max_collision: int | None = None,
        collision_map: dict[str, list[str]] | None = None,
    ) -> ExtractionResult:
        """Analyze a rule file and suggest keywords.

        Args:
            file_path: Path to rule file
            count: Maximum number of keywords (LLM chooses 5-20 based on complexity)
            use_api: Whether to use Cortex API (False = heuristic-only fallback)
            cache: Optional keyword cache dict
            force: Bypass cache even if hash matches
            max_collision: When set, apply the T6 collision post-filter with
                this threshold. Keywords appearing in strictly more than
                ``max_collision`` corpus rules are dropped and substituted
                from the LLM rationale pool where possible.
            collision_map: Pre-computed collision map. When ``None`` and
                ``max_collision`` is set, the map is built lazily from the
                default RULES_INDEX.md path.

        Returns:
            ExtractionResult with current and suggested keywords
        """
        content = file_path.read_text(encoding="utf-8")
        current = self._extract_current_keywords(content)
        heuristic_candidates = self._collect_heuristic_candidates(content)

        # Check cache
        if cache is not None and not force:
            file_key = str(file_path.resolve())
            ch = _content_hash(content)
            cached = _get_cached_keywords(cache, file_key, ch)
            if cached is not None:
                self._debug(f"Cache hit for {file_path.name}")
                return ExtractionResult(
                    file_path=file_path,
                    current_keywords=current,
                    suggested_keywords=cached,
                    candidates=heuristic_candidates,
                )

        # Try Cortex API
        suggested = []
        if use_api:
            try:
                suggested = _call_cortex_complete(
                    content, connection_name=self.connection_name, count=count, debug=self.debug
                )
            except RuntimeError as e:
                self._debug(f"Cortex API failed, falling back to heuristic: {e}")
                log_warning(f"Cortex API unavailable, using heuristic fallback: {e}")

        # Snapshot the LLM rationale pool BEFORE merge/postfilter — the merge
        # step never mutates the module-level rationale map but subsequent
        # extractor calls would clear it. Preserved for T6 substitution and
        # T7 rationale emission.
        rationale_pool = list(get_last_rationale_map().keys())

        # Fallback to heuristic ranking if API didn't produce results
        if not suggested:
            suggested = self._rank_heuristic_keywords(heuristic_candidates, count)
        else:
            # Merge LLM output with high-confidence heuristic terms
            suggested = self._merge_llm_with_heuristics(
                suggested, heuristic_candidates, count, rule_filename=file_path.name
            )

        # Filter stop terms from LLM output as post-processing
        suggested = [k for k in suggested if k.lower() not in STOP_TERMS][:count]

        # T6 collision post-filter: reject keywords that already collide in
        # >max_collision production rules, substituting from the LLM rationale
        # pool (LLM emitted this rule's "next-best" candidates in a single call).
        if max_collision is not None:
            resolved_map = (
                collision_map if collision_map is not None else build_keyword_collision_map()
            )
            suggested = apply_collision_postfilter(
                suggested,
                rationale_pool,
                resolved_map,
                max_collision,
                current_rule_filename=file_path.name,
            )[:count]

        # Update cache
        if cache is not None:
            file_key = str(file_path.resolve())
            ch = _content_hash(content)
            _set_cached_keywords(cache, file_key, ch, suggested)

        return ExtractionResult(
            file_path=file_path,
            current_keywords=current,
            suggested_keywords=suggested,
            candidates=heuristic_candidates,
            rationale_map={kw: get_last_rationale_map().get(kw, "") for kw in suggested},
        )


def format_keywords_line(keywords: list[str]) -> str:
    """Format keywords as a metadata line."""
    return f"**Keywords:** {', '.join(keywords)}"


def update_keywords_in_file(file_path: Path, new_keywords: list[str]) -> bool:
    """Update the Keywords field in a rule file.

    Args:
        file_path: Path to rule file
        new_keywords: New keywords to set

    Returns:
        True if updated, False if no change needed
    """
    content = file_path.read_text(encoding="utf-8")

    # Find and replace Keywords line
    pattern = r"(\*\*Keywords:\*\*\s*)(.+)"
    new_line = format_keywords_line(new_keywords)

    new_content, count = re.subn(pattern, new_line, content, count=1)

    if count == 0:
        log_warning(f"No **Keywords:** field found in {file_path}")
        return False

    if new_content == content:
        return False

    file_path.write_text(new_content, encoding="utf-8")
    return True


def print_diff_rich(result: ExtractionResult) -> None:
    """Print a rich diff between current and suggested keywords."""
    # Create side-by-side panels
    current_lines = []
    suggested_lines = []

    # Mark keywords with colors
    current_lower = {k.lower() for k in result.current_keywords}
    suggested_lower = {k.lower() for k in result.suggested_keywords}

    for kw in result.current_keywords:
        if kw.lower() in suggested_lower:
            current_lines.append(f"[dim]{kw}[/dim]")  # Kept
        else:
            current_lines.append(f"[red strikethrough]{kw}[/red strikethrough]")  # Removed

    for kw in result.suggested_keywords:
        if kw.lower() in current_lower:
            suggested_lines.append(f"[dim]{kw}[/dim]")  # Kept
        else:
            suggested_lines.append(f"[green bold]{kw}[/green bold]")  # Added

    current_panel = Panel(
        "\n".join(current_lines) if current_lines else "[dim]No keywords[/dim]",
        title=f"[bold]Current ({len(result.current_keywords)})[/bold]",
        border_style="red",
    )

    suggested_panel = Panel(
        "\n".join(suggested_lines) if suggested_lines else "[dim]No keywords[/dim]",
        title=f"[bold]Suggested ({len(result.suggested_keywords)})[/bold]",
        border_style="green",
    )

    console.print()
    console.print(f"[bold cyan]{result.file_path.name}[/bold cyan]")
    console.print(Columns([current_panel, suggested_panel], equal=True, expand=True))

    # Summary
    if result.removed:
        console.print(
            f"  [red]- Removed ({len(result.removed)}):[/red] {', '.join(sorted(result.removed))}"
        )
    if result.added:
        console.print(
            f"  [green]+ Added ({len(result.added)}):[/green] {', '.join(sorted(result.added))}"
        )
    if result.kept:
        console.print(f"  [dim]= Kept ({len(result.kept)}):[/dim] {', '.join(sorted(result.kept))}")


def print_suggestions_table(results: list[ExtractionResult]) -> None:
    """Print keyword suggestions as a Rich table."""
    table = Table(title="Keyword Suggestions", show_lines=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Current", style="yellow")
    table.add_column("Suggested", style="green")

    for result in results:
        table.add_row(
            result.file_path.name,
            ", ".join(result.current_keywords) if result.current_keywords else "[dim]None[/dim]",
            ", ".join(result.suggested_keywords)
            if result.suggested_keywords
            else "[dim]None[/dim]",
        )

    console.print(table)


def _emit_rationale_jsonl(results: list[ExtractionResult], output_path: Path) -> int:
    """Append per-keyword rationale JSONL entries to ``output_path``.

    T7: one JSON line per (rule, keyword) pair. Schema:
    ``{rule_path, keyword, rationale, timestamp}``. Rationale is the string
    captured by the T4 LLM parser; when the parser produced no rationale
    (heuristic fallback, cache hit, or legacy string-shape LLM output) the
    entry is skipped so the ``rationale`` field is guaranteed non-empty.

    Args:
        results: Extraction results in the order they were produced.
        output_path: Destination JSONL file (created with parent dirs).

    Returns:
        Number of JSONL lines actually appended.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).isoformat()
    emitted = 0
    with output_path.open("a", encoding="utf-8") as fh:
        for result in results:
            for kw in result.suggested_keywords:
                rationale_text = (result.rationale_map or {}).get(kw, "")
                if not rationale_text:
                    continue
                entry = {
                    "rule_path": str(result.file_path),
                    "keyword": kw,
                    "rationale": rationale_text,
                    "timestamp": timestamp,
                }
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
                emitted += 1
    return emitted


def keywords(
    ctx: typer.Context,
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to rule file or directory.",
            show_default=False,
        ),
    ] = None,
    connection: Annotated[
        str,
        typer.Option(
            "-c",
            "--connection",
            help="Snowflake connection name from ~/.snowflake/connections.toml.",
        ),
    ] = "default",
    update: Annotated[
        bool,
        typer.Option(
            "--update",
            "-u",
            help="Update the Keywords field in-place.",
        ),
    ] = False,
    diff: Annotated[
        bool,
        typer.Option(
            "--diff",
            "-d",
            help="Show diff between current and suggested keywords.",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Bypass cache and re-generate keywords.",
        ),
    ] = False,
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Maximum number of keywords (LLM chooses 5 to this limit).",
        ),
    ] = 15,
    deduplicate: Annotated[
        bool,
        typer.Option(
            "--deduplicate",
            "-D",
            help="Remove over-shared keywords across rules (directory only).",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug output.",
        ),
    ] = False,
    rationale: Annotated[
        bool,
        typer.Option(
            "--rationale",
            help="Append per-keyword rationale to .workbench/audit/keyword_rationale.jsonl.",
        ),
    ] = False,
    rationale_output: Annotated[
        Path | None,
        typer.Option(
            "--rationale-output",
            help="Override the rationale JSONL destination (default: "
            ".workbench/audit/keyword_rationale.jsonl).",
        ),
    ] = None,
) -> None:
    """Generate semantically relevant keywords for AI coding rule files.

    Uses claude-sonnet-4-5 via Snowflake Cortex to summarize rule content into
    contextually meaningful keywords. High-confidence heuristic signals
    (technology terms, code languages) supplement LLM output.
    Results are cached based on file content hash.

    Reads Snowflake credentials from ~/.snowflake/connections.toml using the
    'default' connection. Override with -c/--connection. Falls back to
    heuristic extraction when credentials are not available.

    Examples:
        # Suggest keywords for a single file
        ai-rules keywords rules/100-snowflake-core.md

        # Use a specific Snowflake connection
        ai-rules keywords rules/ -c my_connection

        # Update the Keywords field in-place
        ai-rules keywords rules/100-snowflake-core.md --update

        # Show diff between current and suggested keywords
        ai-rules keywords rules/100-snowflake-core.md --diff

        # Bypass cache and re-generate
        ai-rules keywords rules/100-snowflake-core.md --force

        # Analyze all rules in a directory
        ai-rules keywords rules/
    """
    if path is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Validate path
    if not path.exists():
        log_error(f"Path does not exist: {path}")
        raise typer.Exit(1)

    # Initialize extractor
    extractor = KeywordExtractor(debug=debug, connection_name=connection)

    # Determine if API is available by checking for valid connection config
    use_api = True
    try:
        config = load_snowflake_config(connection)
        account = config.get("account", config.get("accountname", ""))
        token = config.get("token") or config.get("password", "")
        if not account or not token:
            use_api = False
            log_info(
                f"Connection '{connection}' missing account or token; using heuristic fallback"
            )
    except (FileNotFoundError, ValueError) as e:
        use_api = False
        log_info(f"Snowflake connection not available; using heuristic fallback: {e}")

    # Load cache
    cache_dir = path if path.is_dir() else path.parent
    cache_path = cache_dir / CACHE_FILENAME
    cache = _load_cache(cache_path)

    # Process file(s)
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.glob("*.md"))
        files = [f for f in files if f.name not in SKIP_FILES]

    if not files:
        log_error(f"No rule files found in {path}")
        raise typer.Exit(1)

    results: list[ExtractionResult] = []
    updated_count = 0
    unchanged_count = 0

    for file_path in files:
        try:
            result = extractor.suggest_keywords(
                file_path,
                count=count,
                use_api=use_api,
                cache=cache,
                force=force,
            )
            results.append(result)

        except Exception as e:
            log_error(f"Error processing {file_path}: {e}")
            if debug:
                raise

    # Cross-rule deduplication (directory mode only)
    if deduplicate and len(results) > 1:
        _deduplicate_across_rules(results)

    # Output results
    for result in results:
        if diff:
            print_diff_rich(result)
        elif update:
            if update_keywords_in_file(result.file_path, result.suggested_keywords):
                log_success(f"Updated: {result.file_path.name}")
                updated_count += 1
            else:
                log_info(f"No change: {result.file_path.name}")
                unchanged_count += 1

    # Save cache after processing
    _save_cache(cache_path, cache)

    # T7: emit per-keyword rationale JSONL for downstream audit tooling.
    if rationale:
        target = rationale_output or (
            _REPO_ROOT / ".workbench" / "audit" / "keyword_rationale.jsonl"
        )
        emitted = _emit_rationale_jsonl(results, target)
        log_success(f"Appended {emitted} rationale entries to {target} (rules={len(results)})")

    # Print summary for non-diff, non-update mode
    if not diff and not update:
        print_suggestions_table(results)

    # Print final summary for update mode
    if update:
        console.print()
        if updated_count > 0:
            log_success(f"Updated {updated_count} file(s)")
        if unchanged_count > 0:
            log_info(f"Unchanged: {unchanged_count} file(s)")


# ---------------------------------------------------------------------------
# T6 — Corpus collision reporter CLI command
# ---------------------------------------------------------------------------
#
# The plan's contract is ``ai-rules keywords collisions``. Click's group +
# callback + positional-argument routing forces callers to put options BEFORE
# the positional arg, which breaks the 24 existing tests + the T7 success
# signal ``ai-rules keywords rules/000-global-core.md --count 7 --rationale``.
#
# We therefore ship the reporter as a sibling top-level command
# ``ai-rules keywords-collisions`` and keep the historical ``keywords``
# command shape unchanged. The internal library entry points
# (:func:`build_keyword_collision_map`, :func:`find_collision_violations`,
# :func:`apply_collision_postfilter`) are the primary integration surface;
# the CLI wraps them.


def collisions_command(
    rules_dir: Annotated[
        Path,
        typer.Option(
            "--rules-dir",
            help="Directory containing RULES_INDEX.md.",
        ),
    ] = Path("rules"),
    max_collision: Annotated[
        int,
        typer.Option(
            "--max-collision",
            help="Report tokens appearing in strictly more than this many production rules.",
        ),
    ] = 3,
    exclude_list: Annotated[
        Path | None,
        typer.Option(
            "--exclude-list",
            help="Path to the exclude list of rule filenames to omit from counts.",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            help="Write JSON collision report to this path (stdout when omitted).",
        ),
    ] = None,
) -> None:
    """Emit a JSON collision map for keywords across production rules.

    Reads ``RULES_INDEX.md`` from ``<rules_dir>`` and produces the map
    ``{keyword: [<rule filenames>...]}``. ``--max-collision`` also surfaces
    the violating subset in the JSON payload.
    """
    index_path = rules_dir / "RULES_INDEX.md"
    if not index_path.exists():
        log_error(f"RULES_INDEX.md not found at {index_path}")
        raise typer.Exit(1)

    collision_map = build_keyword_collision_map(
        rules_index_path=index_path,
        exclude_list_path=exclude_list,
    )
    violations = find_collision_violations(collision_map, max_collision)

    report = {
        "rules_index_path": str(index_path),
        "max_collision": max_collision,
        "total_keywords": len(collision_map),
        "violation_count": len(violations),
        "collision_map": collision_map,
        "violations": violations,
    }

    payload = json.dumps(report, indent=2, sort_keys=True)

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
        log_success(
            f"Wrote collision report to {output} "
            f"(keywords={len(collision_map)}, violations={len(violations)})"
        )
    else:
        console.print(payload)
