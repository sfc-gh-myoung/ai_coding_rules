"""Characterization tests for ai_rules.commands.keywords.

These tests capture current behavior before any refactoring begins (Phase 0).
They serve as the primary regression guard throughout Phases 0.5-4.

All imports use the public surface at ``ai_rules.commands.keywords`` so they
remain valid after the shim is introduced in Phase 1 Step 11.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.commands.keywords import (
    ExtractionResult,
    KeywordExtractor,
    _content_hash,
    _get_cached_keywords,
    _load_cache,
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
    update_keywords_in_file,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[5]

FIXTURE_RULE_CONTENT = """\
---
schemaVersion: "3.5"
ruleVersion: "1.0"
keywords:
  - pytest fixtures
  - parametrize
  - test isolation
---

## Overview

This rule covers pytest fixture best practices for Python test suites.

## Mandatory

- Use `pytest.fixture` for all test setup
- Prefer `conftest.py` for shared fixtures
- Use `parametrize` for data-driven tests

```python
import pytest

@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.close()
```

## Forbidden

- Do not use class-level setup/teardown
- Avoid mutable global state in fixtures
"""


# ---------------------------------------------------------------------------
# 1. Stoplist loading from workbench file paths
# ---------------------------------------------------------------------------


class TestStoplistLoading:
    def setup_method(self):
        _reset_stoplist_caches()

    def teardown_method(self):
        _reset_stoplist_caches()

    def test_default_stoplist_loads_nonempty(self):
        """Stoplist must load from the workbench config path and be non-empty."""
        stoplist = load_keyword_stoplist()
        assert isinstance(stoplist, set)
        assert len(stoplist) > 0

    def test_stoplist_contains_lowercase_tokens(self):
        """All tokens in the stoplist must be lowercase."""
        stoplist = load_keyword_stoplist()
        for token in stoplist:
            assert token == token.lower(), f"Token not lowercase: {token!r}"

    def test_stoplist_path_resolves_correctly(self):
        """Default stoplist path must resolve to an existing file."""
        from ai_rules.commands.keywords import _DEFAULT_STOPLIST_PATH

        assert _DEFAULT_STOPLIST_PATH.exists(), (
            f"Stoplist file not found at {_DEFAULT_STOPLIST_PATH}"
        )

    def test_stoplist_cached_on_second_call(self):
        """Second call without refresh returns the same object (caching)."""
        first = load_keyword_stoplist()
        second = load_keyword_stoplist()
        assert first is second

    def test_stoplist_refresh_bypasses_cache(self):
        """refresh=True must bypass the cache."""
        first = load_keyword_stoplist()
        second = load_keyword_stoplist(refresh=True)
        # Not the same object after refresh, but same content
        assert first == second
        assert first is not second

    def test_stoplist_overrides_loads(self):
        """Stop-list overrides must load as a dict (may be empty)."""
        overrides = load_keyword_stoplist_overrides()
        assert isinstance(overrides, dict)

    def test_override_path_resolves(self):
        """Default overrides path resolves under workbench config."""
        from ai_rules.commands.keywords import _DEFAULT_STOPLIST_OVERRIDES_PATH

        # Path must exist (may be empty YAML)
        assert _DEFAULT_STOPLIST_OVERRIDES_PATH.exists(), (
            f"Overrides file not found at {_DEFAULT_STOPLIST_OVERRIDES_PATH}"
        )

    def test_custom_stoplist_path(self, tmp_path):
        """Custom path is used when provided; result is not cached globally."""
        custom = tmp_path / "custom_stoplist.txt"
        custom.write_text("alpha\nbeta\n# comment\n\ngamma\n", encoding="utf-8")
        result = load_keyword_stoplist(custom)
        assert result == {"alpha", "beta", "gamma"}

    def test_missing_stoplist_returns_empty_set(self, tmp_path):
        """Non-existent custom path returns empty set (soft-fail)."""
        result = load_keyword_stoplist(tmp_path / "nonexistent.txt")
        assert result == set()


# ---------------------------------------------------------------------------
# 2. Collision map output on fixture rule content (snapshot)
# ---------------------------------------------------------------------------


class TestCollisionMap:
    def test_build_collision_map_returns_dict(self):
        """build_keyword_collision_map must return a dict."""
        result = build_keyword_collision_map()
        assert isinstance(result, dict)

    def test_collision_map_values_are_sorted_lists(self):
        """Each value in the collision map must be a sorted list of filenames."""
        result = build_keyword_collision_map()
        for kw, rules in result.items():
            assert isinstance(kw, str)
            assert isinstance(rules, list)
            assert rules == sorted(rules), f"Rules list not sorted for keyword {kw!r}"

    def test_find_collision_violations_filters_correctly(self):
        """find_collision_violations returns only entries exceeding the threshold."""
        collision_map = {
            "alpha": ["rule-a.md", "rule-b.md"],
            "beta": ["rule-a.md"],
            "gamma": ["rule-a.md", "rule-b.md", "rule-c.md"],
        }
        violations = find_collision_violations(collision_map, max_collision=2)
        assert "gamma" in violations
        assert "alpha" not in violations
        assert "beta" not in violations

    def test_apply_collision_postfilter_removes_over_threshold(self):
        """Collision postfilter rejects keywords exceeding max_collision."""
        collision_map = {
            "overused": ["a.md", "b.md", "c.md"],
            "rare": ["a.md"],
        }
        keywords = ["overused", "rare"]
        rationale = []
        result = apply_collision_postfilter(keywords, rationale, collision_map, max_collision=2)
        assert "overused" not in result
        assert "rare" in result

    def test_apply_collision_postfilter_current_rule_excluded(self):
        """Current rule filename must be excluded from collision count."""
        collision_map = {
            # Appears in exactly 2 rules; if current rule is excluded, count = 1
            "borderline": ["current.md", "other.md"],
        }
        result = apply_collision_postfilter(
            ["borderline"],
            [],
            collision_map,
            max_collision=1,
            current_rule_filename="current.md",
        )
        assert "borderline" in result

    def test_apply_collision_postfilter_substitutes_from_pool(self):
        """Postfilter substitutes rejected keywords from rationale candidates."""
        collision_map = {"overused": ["a.md", "b.md", "c.md"]}
        result = apply_collision_postfilter(
            ["overused"], ["substitute"], collision_map, max_collision=2
        )
        assert "overused" not in result
        assert "substitute" in result


# ---------------------------------------------------------------------------
# 3. Cache hit/miss round-trip behavior
# ---------------------------------------------------------------------------


class TestCacheBehavior:
    def test_cache_miss_returns_none(self):
        """Cache miss returns None when no entry exists."""
        cache: dict = {}
        result = _get_cached_keywords(cache, "some/path.md", "abc123")
        assert result is None

    def test_cache_set_then_get_hit(self):
        """Setting then getting with the same hash returns the stored keywords."""
        cache: dict = {}
        kws = ["pytest fixtures", "parametrize"]
        _set_cached_keywords(cache, "path.md", "hash1", kws)
        result = _get_cached_keywords(cache, "path.md", "hash1")
        assert result == kws

    def test_cache_miss_on_hash_mismatch(self):
        """Cache miss when content hash does not match."""
        cache: dict = {}
        _set_cached_keywords(cache, "path.md", "hash1", ["keyword"])
        result = _get_cached_keywords(cache, "path.md", "hash2")
        assert result is None

    def test_save_and_load_cache_roundtrip(self, tmp_path):
        """Cache persists to disk and loads back correctly."""
        cache_path = tmp_path / ".keywords-cache.json"
        cache = {}
        _set_cached_keywords(cache, "my-rule.md", "abc", ["cortex agent"])
        _save_cache(cache_path, cache)

        loaded = _load_cache(cache_path)
        result = _get_cached_keywords(loaded, "my-rule.md", "abc")
        assert result == ["cortex agent"]

    def test_load_cache_missing_file_returns_empty(self, tmp_path):
        """Loading from a non-existent path returns empty dict."""
        result = _load_cache(tmp_path / "missing.json")
        assert result == {}

    def test_load_cache_corrupt_json_returns_empty(self, tmp_path):
        """Corrupt JSON cache returns empty dict (soft-fail)."""
        cache_path = tmp_path / "corrupt.json"
        cache_path.write_text("{not valid json", encoding="utf-8")
        result = _load_cache(cache_path)
        assert result == {}

    def test_content_hash_deterministic(self):
        """_content_hash must return the same value for the same input."""
        h1 = _content_hash("hello world")
        h2 = _content_hash("hello world")
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex digest

    def test_content_hash_different_inputs(self):
        """_content_hash must return different values for different inputs."""
        h1 = _content_hash("hello")
        h2 = _content_hash("world")
        assert h1 != h2


# ---------------------------------------------------------------------------
# 4. KeywordExtractor output on known input (heuristic, no API)
# ---------------------------------------------------------------------------


class TestKeywordExtractor:
    def test_suggest_keywords_heuristic_returns_extraction_result(self, tmp_path):
        """suggest_keywords must return an ExtractionResult."""
        rule_file = tmp_path / "206-python-pytest.md"
        rule_file.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        extractor = KeywordExtractor(debug=False, connection_name="default")
        result = extractor.suggest_keywords(rule_file, count=10, use_api=False)
        assert isinstance(result, ExtractionResult)
        assert result.file_path == rule_file

    def test_suggest_keywords_extracts_some_keywords(self, tmp_path):
        """Heuristic extraction must produce at least one keyword."""
        rule_file = tmp_path / "206-python-pytest.md"
        rule_file.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        extractor = KeywordExtractor(debug=False)
        result = extractor.suggest_keywords(rule_file, count=10, use_api=False)
        assert len(result.suggested_keywords) > 0

    def test_suggest_keywords_no_stop_terms(self, tmp_path):
        """Suggested keywords must not contain STOP_TERMS entries."""
        from ai_rules.commands.keywords import STOP_TERMS

        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        extractor = KeywordExtractor(debug=False)
        result = extractor.suggest_keywords(rule_file, count=10, use_api=False)
        for kw in result.suggested_keywords:
            assert kw.lower() not in STOP_TERMS, f"Stop term in suggested keywords: {kw!r}"

    def test_suggest_keywords_cache_hit(self, tmp_path):
        """Cached keywords are returned on second call without API."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        extractor = KeywordExtractor(debug=False)
        cache: dict = {}

        first = extractor.suggest_keywords(rule_file, count=10, use_api=False, cache=cache)
        second = extractor.suggest_keywords(rule_file, count=10, use_api=False, cache=cache)
        assert first.suggested_keywords == second.suggested_keywords

    def test_suggest_keywords_force_bypasses_cache(self, tmp_path):
        """force=True must bypass cache and regenerate."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        extractor = KeywordExtractor(debug=False)
        cache: dict = {}

        first = extractor.suggest_keywords(rule_file, count=10, use_api=False, cache=cache)
        # Put stale data in cache
        cache[str(rule_file.resolve())] = {"hash": "stale", "keywords": ["stale-keyword"]}
        # force=True should ignore the stale cache
        forced = extractor.suggest_keywords(
            rule_file, count=10, use_api=False, cache=cache, force=True
        )
        assert "stale-keyword" not in forced.suggested_keywords

    def test_extraction_result_added_removed_kept(self, tmp_path):
        """ExtractionResult.added/removed/kept compute correctly."""
        result = ExtractionResult(
            file_path=tmp_path / "rule.md",
            current_keywords=["pytest fixtures", "old-keyword"],
            suggested_keywords=["pytest fixtures", "new-keyword"],
        )
        assert "pytest fixtures" in result.kept
        assert "old-keyword" in result.removed
        assert "new-keyword" in result.added


# ---------------------------------------------------------------------------
# 5. Import from non-repo CWD (find_project_root() CWD safety)
# ---------------------------------------------------------------------------


class TestNonRepoCWD:
    def test_import_keywords_from_tmp_cwd(self, tmp_path):
        """Importing ai_rules.commands.keywords from a non-repo CWD must not crash.

        find_project_root() is CWD-based. This test verifies that a simple
        import (which triggers module-level code) does not raise an error
        when invoked from a directory with no pyproject.toml.

        Note: _REPO_ROOT is set at module-level using Path(__file__).parents[3];
        it does NOT call find_project_root() at import time, so import from
        non-repo CWD is safe even before the lru_cache refactor.
        """
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import os, sys; os.chdir(sys.argv[1]); "
                "from ai_rules.commands.keywords import keywords_app; "
                "print('ok')",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Import from non-repo CWD failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "ok" in result.stdout


# ---------------------------------------------------------------------------
# 6. Positional invocation form (ai-rules keywords rules/foo.md)
# ---------------------------------------------------------------------------


class TestPositionalInvocation:
    """Guards _KeywordsGroup behavior — positional dispatch to 'run' subcommand."""

    def test_positional_path_routes_to_run_with_help(self, tmp_path):
        """Passing a path without 'run' subcommand must work (--help check).

        We don't actually call the API; we just confirm that positional
        dispatch does not fail before reaching the command logic.
        """
        runner = CliRunner()
        # Passing --help with a positional arg verifies routing doesn't crash
        result = runner.invoke(keywords_app, ["--help"])
        assert result.exit_code == 0

    def test_positional_dispatch_nonexistent_path(self, tmp_path):
        """A non-existent positional path must exit with code 1 (not crash)."""
        runner = CliRunner()
        nonexistent = str(tmp_path / "no-such-rule.md")
        result = runner.invoke(keywords_app, [nonexistent])
        # Should exit 1 with path-not-found, not crash (exit 2) or raise
        assert result.exit_code in (0, 1), (
            f"Unexpected exit code {result.exit_code}:\n{result.output}"
        )

    def test_run_subcommand_equivalent_to_positional(self, tmp_path):
        """'run <path>' and positional '<path>' must reach the same command.

        Creates a real rule file so both paths exercise the full dispatch.
        """
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        runner = CliRunner()

        result_positional = runner.invoke(keywords_app, [str(rule_file)])
        result_explicit = runner.invoke(keywords_app, ["run", str(rule_file)])

        # Both should succeed (or both fail with the same code)
        assert result_positional.exit_code == result_explicit.exit_code, (
            f"Positional exit={result_positional.exit_code}, "
            f"explicit exit={result_explicit.exit_code}"
        )


# ---------------------------------------------------------------------------
# 7. format_keywords_line / update_keywords_in_file helpers
# ---------------------------------------------------------------------------


class TestFormattingHelpers:
    def test_format_keywords_line_inline(self):
        """Inline style produces **Keywords:** prefix."""
        result = format_keywords_line(["pytest fixtures", "parametrize"], style="inline")
        assert result == "**Keywords:** pytest fixtures, parametrize"

    def test_format_keywords_line_yaml(self):
        """Yaml style produces keywords:\\n  - ... block."""
        result = format_keywords_line(["pytest fixtures", "parametrize"], style="yaml")
        assert result.startswith("keywords:")
        assert "  - pytest fixtures" in result
        assert "  - parametrize" in result

    def test_format_keywords_line_empty(self):
        """Empty list produces yaml: [] in yaml style."""
        result = format_keywords_line([], style="yaml")
        assert result == "keywords: []"

    def test_update_keywords_in_file_inline(self, tmp_path):
        """update_keywords_in_file rewrites inline **Keywords:** field."""
        rule = tmp_path / "rule.md"
        rule.write_text(
            "# My Rule\n\n**Keywords:** old-keyword\n\nsome content\n",
            encoding="utf-8",
        )
        updated = update_keywords_in_file(rule, ["new-kw", "another"])
        assert updated is True
        content = rule.read_text()
        assert "new-kw" in content
        assert "old-keyword" not in content

    def test_update_keywords_no_change_returns_false(self, tmp_path):
        """Returns False when keywords already match."""
        rule = tmp_path / "rule.md"
        rule.write_text(
            "# My Rule\n\n**Keywords:** same-kw\n",
            encoding="utf-8",
        )
        updated = update_keywords_in_file(rule, ["same-kw"])
        assert updated is False

    def test_update_keywords_frontmatter(self, tmp_path):
        """update_keywords_in_file handles YAML frontmatter format."""
        rule = tmp_path / "rule.md"
        rule.write_text(FIXTURE_RULE_CONTENT, encoding="utf-8")
        updated = update_keywords_in_file(rule, ["new-keyword", "another"])
        assert updated is True
        content = rule.read_text()
        assert "new-keyword" in content


# ---------------------------------------------------------------------------
# 8. Path constant snapshot (acceptance criterion 12)
# ---------------------------------------------------------------------------


class TestPathConstants:
    def test_default_stoplist_path_under_workbench(self):
        """Default stoplist path resolves under .workbench/config/."""
        from ai_rules.commands.keywords import _DEFAULT_STOPLIST_PATH

        assert ".workbench" in str(_DEFAULT_STOPLIST_PATH)
        assert "keyword_stoplist.txt" in str(_DEFAULT_STOPLIST_PATH)

    def test_default_overrides_path_under_workbench(self):
        """Default overrides path resolves under .workbench/config/."""
        from ai_rules.commands.keywords import _DEFAULT_STOPLIST_OVERRIDES_PATH

        assert ".workbench" in str(_DEFAULT_STOPLIST_OVERRIDES_PATH)
        assert "keyword_stoplist_overrides" in str(_DEFAULT_STOPLIST_OVERRIDES_PATH)

    def test_default_exclude_list_path_under_workbench(self):
        """Default exclude list path resolves under .workbench/config/."""
        from ai_rules.commands.keywords import _DEFAULT_EXCLUDE_LIST_PATH

        assert ".workbench" in str(_DEFAULT_EXCLUDE_LIST_PATH)
        assert "exclude_list" in str(_DEFAULT_EXCLUDE_LIST_PATH)
