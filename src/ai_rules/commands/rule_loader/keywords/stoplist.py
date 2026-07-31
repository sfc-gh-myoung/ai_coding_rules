"""Stop-terms constants and workbench stop-list loading utilities."""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

from ai_rules._shared.paths import find_project_root

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Files to skip when processing directories.
# AGENTS.md / AGENTS_V2.md are retained deliberately: this project no longer uses a
# bootstrap entry-point file, but these are still valid filenames to encounter in a
# consumer repo, and skipping them keeps extracted keywords free of boilerplate.
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "AGENTS_V2.md",
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

# ---------------------------------------------------------------------------
# Lazy repo root (call-time, not import-time)
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=1)
def _get_repo_root() -> Path:
    """Return the project root; cached after first call."""
    return find_project_root()


# ---------------------------------------------------------------------------
# Stoplist loading
# ---------------------------------------------------------------------------

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
        does not exist (soft-fail).
    """
    global _STOPLIST_CACHE
    if path is None and _STOPLIST_CACHE is not None and not refresh:
        return _STOPLIST_CACHE

    resolved = path or (_get_repo_root() / ".workbench" / "config" / "keyword_stoplist.txt")
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

    Returns:
        Mapping of rule filename → lower-cased set of override tokens.
    """
    global _STOPLIST_OVERRIDES_CACHE
    if path is None and _STOPLIST_OVERRIDES_CACHE is not None and not refresh:
        return _STOPLIST_OVERRIDES_CACHE

    resolved = path or (
        _get_repo_root() / ".workbench" / "config" / "keyword_stoplist_overrides.yml"
    )
    result: dict[str, set[str]] = {}
    if resolved.exists():
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
