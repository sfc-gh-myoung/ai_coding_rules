"""Unit tests for version-based citation drift detection.

Covers:
- CITATION_RE_VERSION regex matching
- extract_citations() version field population
- validate_version_citations() drift logic
- version_citation_drift() orchestrator
- format_citation_drift_warning() with field="version"
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.agent_runner import (
    CITATION_RE_VERSION,
    Citation,
    extract_citations,
)
from ai_rules.rule_loader_eval.diagnostics import (
    format_citation_drift_warning,
    version_citation_drift,
)
from ai_rules.rule_loader_eval.matcher import CitationDrift, validate_version_citations
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_meta(path: str, rule_version: str = "", line_count: int = 100) -> dict[str, RuleMetadata]:
    return {path: RuleMetadata(path=Path(path), line_count=line_count, rule_version=rule_version)}


def _make_run(citations_rules_loaded: dict | None = None):
    from ai_rules.rule_loader_eval.agent_runner import AgentRun

    return AgentRun(
        fixture_id="test-fixture",
        loaded=(),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
        citations_rules_loaded=citations_rules_loaded or {},
        citations_reads_performed={},
    )


# ---------------------------------------------------------------------------
# CITATION_RE_VERSION — regex matching
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_version_regex_em_dash_prefix() -> None:
    m = CITATION_RE_VERSION.search("rules/000-global-core.md (foundation) — v4.0.0")
    assert m is not None
    assert m.group("version") == "4.0.0"


@pytest.mark.unit
def test_version_regex_hyphen_prefix() -> None:
    m = CITATION_RE_VERSION.search("rules/100-snowflake-core.md (snowflake) - v2.1.3")
    assert m is not None
    assert m.group("version") == "2.1.3"


@pytest.mark.unit
def test_version_regex_two_part_version() -> None:
    m = CITATION_RE_VERSION.search("rules/100-snowflake-core.md — v1.0")
    assert m is not None
    assert m.group("version") == "1.0"


@pytest.mark.unit
def test_version_regex_prerelease_beta() -> None:
    m = CITATION_RE_VERSION.search("rules/100-snowflake-core.md — v1.0.0-beta")
    assert m is not None
    assert m.group("version") == "1.0.0-beta"


@pytest.mark.unit
def test_version_regex_prerelease_rc() -> None:
    m = CITATION_RE_VERSION.search("rules/100-snowflake-core.md — v2.1.0-rc.1")
    assert m is not None
    assert m.group("version") == "2.1.0-rc.1"


@pytest.mark.unit
def test_version_regex_no_match_line_count_only() -> None:
    m = CITATION_RE_VERSION.search("rules/100-snowflake-core.md — 275 lines")
    assert m is None


@pytest.mark.unit
def test_version_regex_no_match_no_suffix() -> None:
    m = CITATION_RE_VERSION.search("rules/100-snowflake-core.md (snowflake)")
    assert m is None


# ---------------------------------------------------------------------------
# extract_citations — version field population
# ---------------------------------------------------------------------------

_PROGRESSIVE_SECTION = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — v4.0.0
- [x] Gate 2: Rule discovery via rule-loader skill
- [x] Gate 3: +1 domain rule(s):
  - [x] rules/100-snowflake-core.md (snowflake) — v3.1.0

Task Switch: FIRST
"""


@pytest.mark.unit
def test_extract_citations_version_from_gate3_subbullet() -> None:
    result = extract_citations(_PROGRESSIVE_SECTION, "Rules Loaded")
    assert "rules/100-snowflake-core.md" in result
    c = result["rules/100-snowflake-core.md"]
    assert c.version == "3.1.0"
    assert c.line_count is None


@pytest.mark.unit
def test_extract_citations_version_from_gate1_foundation() -> None:
    result = extract_citations(_PROGRESSIVE_SECTION, "Rules Loaded")
    assert "rules/000-global-core.md" in result
    c = result["rules/000-global-core.md"]
    assert c.version == "4.0.0"
    assert c.line_count is None


@pytest.mark.unit
def test_extract_citations_mixed_suffix_both_fields_populated() -> None:
    """A line with — vX.Y.Z populates the version field; line-count suffix is ignored."""
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md
- [x] Gate 3: +1 domain rule(s):
  - [x] rules/100-snowflake-core.md (snowflake) — v4.0.1

Task Switch: FIRST
"""
    result = extract_citations(text, "Rules Loaded")
    c = result["rules/100-snowflake-core.md"]
    assert c.version == "4.0.1"
    assert c.line_count is None


@pytest.mark.unit
def test_extract_citations_prerelease_version() -> None:
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md
- [x] Gate 3: +1 domain rule(s):
  - [x] rules/200-python-core.md (python) — v1.0.0-beta

Task Switch: FIRST
"""
    result = extract_citations(text, "Rules Loaded")
    assert result["rules/200-python-core.md"].version == "1.0.0-beta"


@pytest.mark.unit
def test_extract_citations_no_version_yields_none() -> None:
    """A line with only — N lines suffix has version=None and line_count=None (line-count removed)."""
    text = """\
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md
- [x] Gate 3: +1 domain rule(s):
  - [x] rules/100-snowflake-core.md (snowflake) — 275 lines

Task Switch: FIRST
"""
    result = extract_citations(text, "Rules Loaded")
    assert result["rules/100-snowflake-core.md"].version is None
    assert result["rules/100-snowflake-core.md"].line_count is None


# ---------------------------------------------------------------------------
# validate_version_citations
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_version_citations_matching_versions_no_drift() -> None:
    citations = {"rules/a.md": Citation(version="4.0.0")}
    meta = _make_meta("rules/a.md", rule_version="4.0.0")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert result == ()


@pytest.mark.unit
def test_validate_version_citations_mismatch_produces_drift() -> None:
    citations = {"rules/a.md": Citation(version="4.0.0")}
    meta = _make_meta("rules/a.md", rule_version="4.0.1")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert len(result) == 1
    d = result[0]
    assert d.field == "version"
    assert d.declared == "4.0.0"
    assert d.actual == "4.0.1"
    assert d.section == "Rules Loaded"
    assert d.rule_path == "rules/a.md"


@pytest.mark.unit
def test_validate_version_citations_none_version_skipped() -> None:
    citations = {"rules/a.md": Citation(version=None)}
    meta = _make_meta("rules/a.md", rule_version="4.0.0")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert result == ()


@pytest.mark.unit
def test_validate_version_citations_rule_no_frontmatter_version_skipped() -> None:
    citations = {"rules/a.md": Citation(version="4.0.0")}
    meta = _make_meta("rules/a.md", rule_version="")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert result == ()


@pytest.mark.unit
def test_validate_version_citations_unknown_path_produces_path_drift() -> None:
    citations = {"rules/999-fake.md": Citation(version="1.0.0")}
    result = validate_version_citations(citations=citations, rules_meta={}, section="Rules Loaded")
    assert len(result) == 1
    assert result[0].field == "path"
    assert result[0].actual == "<rule file not in snapshot>"


@pytest.mark.unit
def test_validate_version_citations_failed_citation_skipped() -> None:
    citations = {"rules/a.md": Citation(failed=True, version="4.0.0")}
    meta = _make_meta("rules/a.md", rule_version="1.0.0")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert result == ()


@pytest.mark.unit
def test_validate_version_citations_prerelease_mismatch() -> None:
    citations = {"rules/a.md": Citation(version="1.0.0-beta")}
    meta = _make_meta("rules/a.md", rule_version="1.0.0")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert len(result) == 1
    assert result[0].field == "version"
    assert result[0].declared == "1.0.0-beta"
    assert result[0].actual == "1.0.0"


@pytest.mark.unit
def test_validate_version_citations_prerelease_match() -> None:
    citations = {"rules/a.md": Citation(version="1.0.0-beta")}
    meta = _make_meta("rules/a.md", rule_version="1.0.0-beta")
    result = validate_version_citations(
        citations=citations, rules_meta=meta, section="Rules Loaded"
    )
    assert result == ()


# ---------------------------------------------------------------------------
# version_citation_drift orchestrator
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_version_citation_drift_produces_drifts() -> None:
    run = _make_run(citations_rules_loaded={"rules/a.md": Citation(version="3.0.0")})
    meta = _make_meta("rules/a.md", rule_version="4.0.0")
    drifts = version_citation_drift(run, meta)
    assert len(drifts) == 1
    assert drifts[0].field == "version"
    assert drifts[0].declared == "3.0.0"


@pytest.mark.unit
def test_version_citation_drift_no_version_no_drift() -> None:
    run = _make_run(citations_rules_loaded={"rules/a.md": Citation(line_count=100)})
    meta = _make_meta("rules/a.md", rule_version="4.0.0")
    drifts = version_citation_drift(run, meta)
    assert drifts == ()


@pytest.mark.unit
def test_version_citation_drift_empty_run_empty_result() -> None:
    assert version_citation_drift(_make_run(), {}) == ()


# ---------------------------------------------------------------------------
# format_citation_drift_warning — generic intro text
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_citation_drift_warning_returns_none_on_empty() -> None:
    assert format_citation_drift_warning(()) is None


@pytest.mark.unit
def test_format_citation_drift_warning_version_drift_rendered() -> None:
    drift = CitationDrift(
        rule_path="rules/a.md",
        field="version",
        declared="4.0.0",
        actual="4.0.1",
        section="Rules Loaded",
    )
    result = format_citation_drift_warning((drift,))
    assert result is not None
    assert "fabrication signal" in result
    assert "line counts" not in result  # generic text, not line-count-specific
    assert "rules/a.md" in result
    assert "version" in result
    assert "declared='4.0.0'" in result
    assert "actual='4.0.1'" in result


@pytest.mark.unit
def test_format_citation_drift_warning_line_count_drift_still_works() -> None:
    """Regression: line_count drift must still render after intro text change."""
    drift = CitationDrift(
        rule_path="rules/a.md",
        field="line_count",
        declared="100",
        actual="200",
        section="Rules Loaded",
    )
    result = format_citation_drift_warning((drift,))
    assert result is not None
    assert "fabrication signal" in result
    assert "line_count" in result
