"""Unit tests for match_rules.py — parse_frontmatter, parse_rule_file, load_rules_db."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.match_rules import (
    _parse_typed_keywords,
    load_rules_db,
    parse_frontmatter,
    parse_rule_file,
)

# ---------------------------------------------------------------------------
# _parse_typed_keywords
# ---------------------------------------------------------------------------


class TestParseTypedKeywords:
    def test_kw_prefix(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(["kw:pytest fixtures"])
        assert kw == ["pytest fixtures"]
        assert ext == []

    def test_ext_prefix(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(["ext:.py"])
        assert ext == [".py"]

    def test_file_prefix(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(["file:auth.py"])
        assert file_pats == ["auth.py"]

    def test_dir_prefix(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(["dir:tests/"])
        assert dir_pats == ["tests/"]

    def test_bare_entry_treated_as_kw(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(["streamlit"])
        assert kw == ["streamlit"]

    def test_mixed_prefixes(self):
        raw = ["kw:pytest", "ext:.py", "file:conftest.py", "dir:tests/", "bare-kw"]
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(raw)
        assert kw == ["pytest", "bare-kw"]
        assert ext == [".py"]
        assert file_pats == ["conftest.py"]
        assert dir_pats == ["tests/"]

    def test_empty_list(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords([])
        assert kw == []
        assert ext == []

    def test_none_input(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(None)  # type: ignore[arg-type]
        assert kw == []

    def test_skips_blank_entries(self):
        kw, ext, file_pats, dir_pats = _parse_typed_keywords(["", "  ", "kw:valid"])
        assert kw == ["valid"]


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\nrule_version: v1.0\ncontext_tier: High\n---\n# Body"
        data = parse_frontmatter(content)
        assert data is not None
        assert data["rule_version"] == "v1.0"

    def test_no_frontmatter(self):
        content = "# Just a heading\nno frontmatter here"
        assert parse_frontmatter(content) is None

    def test_unclosed_frontmatter(self):
        content = "---\nrule_version: v1.0\n# no closing fence"
        assert parse_frontmatter(content) is None

    def test_multiple_fences_only_first_two_consumed(self):
        content = "---\nrule_version: v2.0\n---\n# Body\n---\nMore content\n---"
        data = parse_frontmatter(content)
        assert data is not None
        assert data["rule_version"] == "v2.0"


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
        assert "000-global-core.md" in rule.depends_required

    def test_optional_dep_parsed(self, tmp_path):
        path = _make_rule_file(tmp_path, SAMPLE_FRONTMATTER)
        rule = parse_rule_file(path)
        assert rule is not None
        assert "001-memory-bank.md" in rule.depends_optional

    def test_no_frontmatter_returns_none(self, tmp_path):
        path = _make_rule_file(tmp_path, "# No frontmatter\nJust content\n")
        assert parse_rule_file(path) is None

    def test_missing_optional_fields_use_defaults(self, tmp_path):
        minimal = "---\nrule_version: v1.0\n---\n# Minimal"
        path = _make_rule_file(tmp_path, minimal)
        rule = parse_rule_file(path)
        assert rule is not None
        assert rule.token_budget is None
        assert rule.depends_required == []
        assert rule.context_tier == "Low"
        assert rule.description == ""
        assert rule.typed_kw == []

    def test_unreadable_file_returns_none(self, tmp_path):
        path = tmp_path / "ghost.md"
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
        _make_rule_file(tmp_path, "# No frontmatter", "no-fm.md")
        db = load_rules_db(tmp_path)
        assert "200-valid.md" in db
        assert "no-fm.md" not in db

    def test_skips_readme(self, tmp_path):
        _make_rule_file(tmp_path, SAMPLE_FRONTMATTER, "README.md")
        db = load_rules_db(tmp_path)
        assert "README.md" not in db

    def test_missing_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            load_rules_db(Path("/nonexistent/rules"))

    def test_multiple_fences_edge_case(self, tmp_path):
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
