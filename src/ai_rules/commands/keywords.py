"""src/ai_rules/commands/keywords.py — SHIM: re-exports from canonical location.

Do not add logic here. Remove after deprecated alias period ends.

Primary CLI path: ``ai-rules rule-loader keywords``
Deprecated path:  ``ai-rules keywords`` (this shim)
"""

from __future__ import annotations

from typing import Any

from ai_rules.commands.rule_loader.keywords import (  # noqa: F401
    CortexClient,
    ExtractionResult,
    KeywordCandidate,
    KeywordExtractor,
    ParseResult,
    _call_cortex_complete,
    _content_hash,
    _deduplicate_across_rules,
    _emit_rationale_jsonl,
    _get_cached_keywords,
    _KeywordsGroup,
    _load_cache,
    _parse_frontmatter_block,
    _parse_keyword_response,
    _reset_stoplist_caches,
    _save_cache,
    _set_cached_keywords,
    apply_collision_postfilter,
    build_keyword_collision_map,
    find_collision_violations,
    format_keywords_line,
    keywords_app,
    load_keyword_stoplist,
    load_keyword_stoplist_overrides,
    load_snowflake_config,
    update_keywords_in_file,
)
from ai_rules.commands.rule_loader.keywords.stoplist import (  # noqa: F401
    CACHE_FILENAME,
    SKIP_FILES,
    STOP_TERMS,
    TECHNOLOGY_TERMS,
)

# ---------------------------------------------------------------------------
# Backward-compat path constants (lazy via module __getattr__)
# Accessing these triggers find_project_root() at access time, not import
# time, so importing this shim from a non-repo CWD remains safe.
# ---------------------------------------------------------------------------


def __getattr__(name: str) -> Any:
    if name == "_DEFAULT_STOPLIST_PATH":
        from ai_rules.commands.rule_loader.keywords.stoplist import _get_repo_root

        return _get_repo_root() / ".workbench" / "config" / "keyword_stoplist.txt"
    if name == "_DEFAULT_STOPLIST_OVERRIDES_PATH":
        from ai_rules.commands.rule_loader.keywords.stoplist import _get_repo_root

        return _get_repo_root() / ".workbench" / "config" / "keyword_stoplist_overrides.yml"
    if name == "_DEFAULT_EXCLUDE_LIST_PATH":
        from ai_rules.commands.rule_loader.keywords.collision import _get_default_exclude_list_path

        return _get_default_exclude_list_path()
    raise AttributeError(f"module 'ai_rules.commands.keywords' has no attribute {name!r}")
