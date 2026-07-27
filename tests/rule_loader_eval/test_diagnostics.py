"""Unit/integration tests for rule_loader_eval/diagnostics.py — all public functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.agent_runner import AgentRun, TurnEvent
from ai_rules.rule_loader_eval.diagnostics import (
    SignalReport,
    format_citation_drift_warning,
    format_debug,
    format_disagreement_warning,
    format_timing_lines,
    load_rule_meta_for_project,
    signal_disagreement,
)
from ai_rules.rule_loader_eval.matcher import CitationDrift

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_run(
    reads: tuple[str, ...] = (),
    section: tuple[str, ...] = (),
    reads_performed: tuple[str, ...] = (),
    citations_rules_loaded: dict | None = None,
    citations_reads_performed: dict | None = None,
    **kwargs,
) -> AgentRun:
    """Construct a minimal AgentRun for testing."""
    return AgentRun(
        fixture_id="test-fixture",
        loaded=tuple(sorted(set(reads) | set(section) | set(reads_performed))),
        loaded_via_reads=reads,
        loaded_via_reads_performed=reads_performed,
        loaded_via_section=section,
        citations_rules_loaded=citations_rules_loaded or {},
        citations_reads_performed=citations_reads_performed or {},
        **kwargs,
    )


# ---------------------------------------------------------------------------
# signal_disagreement
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_signal_disagreement_ok_when_sets_agree() -> None:
    run = _make_run(reads=("rules/a.md",), section=("rules/a.md",))
    report = signal_disagreement(run)
    assert report.ok is True
    assert report.cited_without_read == ()
    assert report.read_without_cite_unexpected == ()


@pytest.mark.unit
def test_signal_disagreement_fabrication_cited_without_read() -> None:
    run = _make_run(reads=(), section=("rules/a.md",))
    report = signal_disagreement(run)
    assert report.ok is False
    assert "rules/a.md" in report.cited_without_read


@pytest.mark.unit
def test_signal_disagreement_read_without_cite_unexpected() -> None:
    run = _make_run(reads=("rules/a.md",), section=())
    report = signal_disagreement(run)
    assert report.ok is True
    assert "rules/a.md" in report.read_without_cite_unexpected
    assert report.cited_without_read == ()


@pytest.mark.unit
def test_signal_disagreement_read_tolerated_when_in_optional() -> None:
    run = _make_run(reads=("rules/a.md",), section=())
    report = signal_disagreement(run, fixture_optional=["rules/a.md"])
    assert report.ok is True
    assert "rules/a.md" in report.read_without_cite_tolerated
    assert report.read_without_cite_unexpected == ()


@pytest.mark.unit
def test_signal_disagreement_discovery_artifacts_filtered() -> None:
    run = _make_run(reads=("AGENTS.md", "rules/x.md"), section=("AGENTS.md", "rules/x.md"))
    report = signal_disagreement(run)
    assert report.ok is True
    assert "AGENTS.md" not in report.cited_without_read
    assert "AGENTS.md" not in report.read_without_cite_unexpected


@pytest.mark.unit
def test_signal_disagreement_empty_run_all_ok() -> None:
    report = signal_disagreement(_make_run())
    assert report.ok is True
    assert report.cited_without_read == ()
    assert report.read_without_cite_unexpected == ()
    assert report.read_without_cite_tolerated == ()


# ---------------------------------------------------------------------------
# format_disagreement_warning
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_disagreement_warning_cited_without_read() -> None:
    run = _make_run(reads=(), section=("rules/a.md",))
    report = SignalReport(ok=False, disagreements=(), cited_without_read=("rules/a.md",))
    out = format_disagreement_warning(run, signal_report=report)
    assert "cited_without_read" in out
    assert "FAIL" in out
    assert "rules/a.md" in out


@pytest.mark.unit
def test_format_disagreement_warning_read_without_cite_unexpected() -> None:
    run = _make_run(reads=("rules/a.md",), section=())
    report = SignalReport(ok=True, disagreements=(), read_without_cite_unexpected=("rules/a.md",))
    out = format_disagreement_warning(run, signal_report=report)
    assert "read_without_cite_unexpected" in out
    assert "rules/a.md" in out


@pytest.mark.unit
def test_format_disagreement_warning_tolerated() -> None:
    run = _make_run(reads=("rules/a.md",), section=())
    report = SignalReport(ok=True, disagreements=(), read_without_cite_tolerated=("rules/a.md",))
    out = format_disagreement_warning(run, signal_report=report)
    assert "INFO" in out
    assert "tolerated" in out
    assert "rules/a.md" in out


@pytest.mark.unit
def test_format_disagreement_warning_legacy_two_signal_no_report() -> None:
    run = _make_run(reads=("rules/a.md",), section=("rules/b.md",))
    out = format_disagreement_warning(run, signal_report=None)
    assert "mismatch" in out.lower()
    assert "Rules Loaded" in out


@pytest.mark.unit
def test_format_disagreement_warning_legacy_three_signal() -> None:
    run = _make_run(
        reads=("rules/a.md",),
        section=("rules/b.md",),
        reads_performed=("rules/c.md",),
    )
    out = format_disagreement_warning(run, signal_report=None)
    assert "3-signal" in out
    assert "Reads Performed" in out


@pytest.mark.unit
def test_format_disagreement_warning_all_empty_signal_report_falls_to_legacy() -> None:
    run = _make_run(reads=("rules/a.md",), section=("rules/b.md",))
    report = SignalReport(ok=True, disagreements=())
    out = format_disagreement_warning(run, signal_report=report)
    assert "mismatch" in out.lower()


# ---------------------------------------------------------------------------
# format_citation_drift_warning
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_citation_drift_warning_empty_returns_none() -> None:
    assert format_citation_drift_warning(()) is None


@pytest.mark.unit
def test_format_citation_drift_warning_single_drift() -> None:
    d = CitationDrift(
        rule_path="rules/a.md",
        field="line_count",
        declared="50",
        actual="200",
        section="Rules Loaded",
    )
    out = format_citation_drift_warning((d,))
    assert out is not None
    assert "Citation drift" in out
    assert "rules/a.md" in out
    assert "line_count" in out
    assert "50" in out
    assert "200" in out


# ---------------------------------------------------------------------------
# format_debug
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_debug_header_footer() -> None:
    run = _make_run(reads=("rules/a.md",), section=("rules/a.md",), final_text="hello")
    lines = format_debug(run)
    assert lines[0] == "--- diagnostics debug ---"
    assert lines[-1] == "--- end diagnostics debug ---"


@pytest.mark.unit
def test_format_debug_empty_final_text_renders_placeholder() -> None:
    run = _make_run(final_text="")
    assert "(empty)" in format_debug(run)


@pytest.mark.unit
def test_format_debug_includes_reads_and_section_paths() -> None:
    run = _make_run(reads=("rules/a.md",), section=("rules/b.md",))
    combined = "\n".join(format_debug(run))
    assert "rules/a.md" in combined
    assert "rules/b.md" in combined


@pytest.mark.unit
def test_format_debug_reads_performed_section_when_non_empty() -> None:
    run = _make_run(reads_performed=("rules/c.md",))
    combined = "\n".join(format_debug(run))
    assert "reads_performed" in combined
    assert "rules/c.md" in combined


@pytest.mark.unit
def test_format_debug_notes_included_when_present() -> None:
    run = _make_run(notes=("note-alpha", "note-beta"))
    combined = "\n".join(format_debug(run))
    assert "note-alpha" in combined
    assert "note-beta" in combined


# ---------------------------------------------------------------------------
# format_timing_lines
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_format_timing_lines_empty_events() -> None:
    run = _make_run(duration_ms=5000, turns=2, model="test-model")
    lines = format_timing_lines(run, effort="low", model="test-model")
    assert lines[0] == "--- diagnostics timing ---"
    assert "5_000" in lines[1]
    assert "test-model" in lines[1]
    assert "[start]" in lines[2]
    assert lines[-1] == "--- end diagnostics timing ---"


@pytest.mark.unit
def test_format_timing_lines_event_rendered() -> None:
    ev = TurnEvent(t_ms=300, kind="tool_use", detail="Read file_path=rules/x.md")
    run = _make_run(duration_ms=300, turns=1, events=(ev,))
    lines = format_timing_lines(run, effort="high", model="auto")
    event_line = next(ln for ln in lines if "tool_use" in ln)
    assert "Read file_path=rules/x.md" in event_line


# ---------------------------------------------------------------------------
# load_rule_meta_for_project
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_load_rule_meta_for_project_empty_dir(tmp_path: Path) -> None:
    (tmp_path / "rules").mkdir()
    assert load_rule_meta_for_project(tmp_path) == {}


@pytest.mark.integration
def test_load_rule_meta_for_project_single_rule(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "999-test.md").write_text(
        "**Keywords:** kw:test\n**ContextTier:** High\n**Depends:** None\n# Test\n",
        encoding="utf-8",
    )
    result = load_rule_meta_for_project(tmp_path)
    assert "rules/999-test.md" in result


@pytest.mark.integration
def test_load_rule_meta_for_project_skips_readme(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "README.md").write_text("# Readme\n", encoding="utf-8")
    (rules_dir / "001-test.md").write_text("# Test\n", encoding="utf-8")
    result = load_rule_meta_for_project(tmp_path)
    assert "rules/README.md" not in result
    assert "rules/001-test.md" in result


# ---------------------------------------------------------------------------
# Task 6.4: _DISCOVERY_ARTIFACTS reference-file exclusion
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_discovery_artifacts_includes_rules_index() -> None:
    """_DISCOVERY_ARTIFACTS in diagnostics.py includes rules/RULES_INDEX.md."""
    from ai_rules.rule_loader_eval.diagnostics import _DISCOVERY_ARTIFACTS

    assert "rules/RULES_INDEX.md" in _DISCOVERY_ARTIFACTS
    assert "AGENTS.md" in _DISCOVERY_ARTIFACTS


@pytest.mark.unit
def test_rules_index_read_no_cite_excluded_from_signals() -> None:
    """Reading rules/RULES_INDEX.md without citing it produces no signal contribution."""
    run = _make_run(
        reads=("rules/000-global-core.md", "rules/RULES_INDEX.md"),
        section=("rules/000-global-core.md",),
    )
    report = signal_disagreement(run)
    assert "rules/RULES_INDEX.md" not in report.read_without_cite_unexpected
    assert "rules/RULES_INDEX.md" not in report.read_without_cite_tolerated
    assert "rules/RULES_INDEX.md" not in report.cited_without_read
    assert all("RULES_INDEX" not in d for d in report.disagreements)


@pytest.mark.unit
def test_rule_file_read_without_cite_still_reported() -> None:
    """Excluding RULES_INDEX.md must not suppress legitimate read_without_cite signals for rule files."""
    run = _make_run(
        reads=("rules/000-global-core.md", "rules/100-snowflake-core.md"),
        section=("rules/000-global-core.md",),
    )
    report = signal_disagreement(run)
    # 100-snowflake-core.md read but not cited: must still appear as read_without_cite
    assert "rules/100-snowflake-core.md" in (
        report.read_without_cite_unexpected + report.read_without_cite_tolerated
    )
