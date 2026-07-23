"""Unit tests for frontmatter.py — parse_typed_keywords, parse_rule_file, load_rules_db."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_matcher.frontmatter import (
    TypedKeywords,
    _parse_raw_frontmatter,
    load_rules_db,
    parse_rule_file,
    parse_typed_keywords,
)

# ---------------------------------------------------------------------------
# parse_typed_keywords
# ---------------------------------------------------------------------------


class TestParseTypedKeywords:
    def test_kw_prefix(self):
        result = parse_typed_keywords(["kw:pytest fixtures"])
        assert result.kw == ["pytest fixtures"]
        assert result.ext == []

    def test_ext_prefix(self):
        result = parse_typed_keywords(["ext:.py"])
        assert result.ext == [".py"]

    def test_file_prefix(self):
        result = parse_typed_keywords(["file:auth.py"])
        assert result.file_patterns == ["auth.py"]

    def test_dir_prefix(self):
        result = parse_typed_keywords(["dir:tests/"])
        assert result.dir_patterns == ["tests/"]

    def test_bare_entry_treated_as_kw(self):
        result = parse_typed_keywords(["streamlit"])
        assert result.kw == ["streamlit"]

    def test_mixed_prefixes(self):
        raw = ["kw:pytest", "ext:.py", "file:conftest.py", "dir:tests/", "bare-kw"]
        result = parse_typed_keywords(raw)
        assert result.kw == ["pytest", "bare-kw"]
        assert result.ext == [".py"]
        assert result.file_patterns == ["conftest.py"]
        assert result.dir_patterns == ["tests/"]

    def test_empty_list(self):
        result = parse_typed_keywords([])
        assert result == TypedKeywords()

    def test_none_input(self):
        result = parse_typed_keywords(None)  # type: ignore[arg-type]
        assert result == TypedKeywords()

    def test_skips_blank_entries(self):
        result = parse_typed_keywords(["", "  ", "kw:valid"])
        assert result.kw == ["valid"]


# ---------------------------------------------------------------------------
# _parse_raw_frontmatter
# ---------------------------------------------------------------------------


class TestParseRawFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\nrule_version: v1.0\ncontext_tier: High\n---\n# Body"
        data = _parse_raw_frontmatter(content)
        assert data is not None
        assert data["rule_version"] == "v1.0"

    def test_no_frontmatter(self):
        content = "# Just a heading\nno frontmatter here"
        assert _parse_raw_frontmatter(content) is None

    def test_unclosed_frontmatter(self):
        content = "---\nrule_version: v1.0\n# no closing fence"
        assert _parse_raw_frontmatter(content) is None

    def test_multiple_fences_only_first_two_consumed(self):
        """Rules with >2 --- fences: only the first two delimit frontmatter."""
        content = "---\nrule_version: v2.0\n---\n# Body\n---\nMore content\n---"
        data = _parse_raw_frontmatter(content)
        assert data is not None
        assert data["rule_version"] == "v2.0"

    def test_invalid_yaml(self):
        content = "---\nkey: [unclosed\n---\n"
        assert _parse_raw_frontmatter(content) is None

    def test_non_mapping_yaml(self):
        content = "---\n- item1\n- item2\n---\n"
        assert _parse_raw_frontmatter(content) is None


# ---------------------------------------------------------------------------
# parse_rule_file
# ---------------------------------------------------------------------------

SAMPLE_FRONTMATTER = """\
---
schema_version: v3.5
rule_version: v2.0.0
last_updated: 2026-01-01
keywords:
  - kw:pytest fixtures
  - ext:.py
  - file:conftest.py
  - dir:tests/
token_budget: ~1500
context_tier: High
depends:
  required:
    - 000-global-core.md  # foundation
  optional:
    - 001-memory-bank.md
description: "Testing rule for Python pytest patterns."
---
# Rule Body
"""


def _make_rule_file(tmp_path: Path, content: str, name: str = "test-rule.md") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


class TestParseRuleFile:
    def test_full_parse(self, tmp_path):
        path = _make_rule_file(tmp_path, SAMPLE_FRONTMATTER)
        rule = parse_rule_file(path)
        assert rule is not None
        assert rule.filename == "test-rule.md"
        assert rule.rule_version == "v2.0.0"
        assert rule.context_tier == "High"
        assert rule.token_budget == 1500
        assert rule.typed_kw == ["pytest fixtures"]
        assert rule.typed_ext == [".py"]
        assert rule.file_patterns == ["conftest.py"]
        assert rule.dir_patterns == ["tests/"]
        assert rule.description == "Testing rule for Python pytest patterns."

    def test_required_dep_parsed(self, tmp_path):
        path = _make_rule_file(tmp_path, SAMPLE_FRONTMATTER)
        rule = parse_rule_file(path)
        assert rule is not None
        assert rule.depends is not None
        assert "000-global-core.md" in rule.depends["required"]

    def test_no_frontmatter_returns_none(self, tmp_path):
        path = _make_rule_file(tmp_path, "# No frontmatter\nJust content\n")
        assert parse_rule_file(path) is None

    def test_missing_optional_fields_use_defaults(self, tmp_path):
        minimal = "---\nrule_version: v1.0\n---\n# Minimal"
        path = _make_rule_file(tmp_path, minimal)
        rule = parse_rule_file(path)
        assert rule is not None
        assert rule.token_budget is None
        assert rule.depends is None
        assert rule.context_tier == "Low"
        assert rule.description == ""
        assert rule.typed_kw == []

    def test_unreadable_file_returns_none(self, tmp_path):
        path = tmp_path / "ghost.md"
        # File does not exist
        assert parse_rule_file(path) is None

    def test_token_budget_with_tilde(self, tmp_path):
        content = "---\nrule_version: v1.0\ntoken_budget: ~2550\n---\n"
        path = _make_rule_file(tmp_path, content)
        rule = parse_rule_file(path)
        assert rule is not None
        assert rule.token_budget == 2550


# ---------------------------------------------------------------------------
# load_rules_db
# ---------------------------------------------------------------------------


class TestLoadRulesDb:
    def test_loads_valid_files(self, tmp_path):
        _make_rule_file(tmp_path, SAMPLE_FRONTMATTER, "200-python-core.md")
        db = load_rules_db(tmp_path)
        assert "200-python-core.md" in db

    def test_skips_files_without_frontmatter(self, tmp_path):
        _make_rule_file(tmp_path, SAMPLE_FRONTMATTER, "200-valid.md")
        _make_rule_file(tmp_path, "# No frontmatter", "README.md")
        db = load_rules_db(tmp_path)
        assert "200-valid.md" in db
        assert "README.md" not in db

    def test_missing_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            load_rules_db(Path("/nonexistent/rules"))

    def test_multiple_fences_edge_case(self, tmp_path):
        """Rules with extra --- fences in body still parse correctly."""
        content = "---\nrule_version: v3.0\ncontext_tier: Medium\n---\n## Section\n---\nExtra\n---"
        _make_rule_file(tmp_path, content, "multi-fence.md")
        db = load_rules_db(tmp_path)
        assert "multi-fence.md" in db
        assert db["multi-fence.md"].rule_version == "v3.0"

    def test_no_keywords_field(self, tmp_path):
        content = "---\nrule_version: v1.0\ncontext_tier: Low\n---\n"
        _make_rule_file(tmp_path, content, "no-kw.md")
        db = load_rules_db(tmp_path)
        assert "no-kw.md" in db
        assert db["no-kw.md"].typed_kw == []
