"""Tests for rule-loader eval output-contract handling (legacy AGENTS.md)."""

from __future__ import annotations

import pytest

from ai_rules.rule_loader_eval.agent_runner import (
    AgentRun,
    extract_contract_text,
    validate_output_shape,
)
from ai_rules.rule_loader_eval.diagnostics import SignalReport
from ai_rules.rule_loader_eval.engine import RunResult
from ai_rules.rule_loader_eval.matcher import MatchResult


@pytest.mark.unit
def test_validate_output_shape_accepts_legacy_rules_loaded_heading() -> None:
    text = """## Rules Loaded
- rules/000-global-core.md (foundation) — 350 lines
- rules/200-python-core.md (ext: .py) — 453 lines
"""
    assert validate_output_shape(text, loaded_count=2) == ()


@pytest.mark.unit
def test_validate_output_shape_accepts_bold_inline_rules_loaded() -> None:
    text = """**Rules Loaded**
- rules/200-python-core.md (ext:.py) — 453 lines
"""
    assert validate_output_shape(text, loaded_count=1) == ()


@pytest.mark.unit
def test_validate_output_shape_accepts_no_match_rules_loaded_body() -> None:
    text = """## Rules Loaded
(none — no domain rules matched)
"""
    assert validate_output_shape(text, loaded_count=0) == ()


@pytest.mark.unit
def test_validate_output_shape_rejects_missing_rules_loaded_section() -> None:
    text = """Some prose without a Rules Loaded section.

Just some response.
"""
    violations = validate_output_shape(text, loaded_count=0)
    assert "missing **Rules Loaded** section" in violations


@pytest.mark.unit
def test_validate_output_shape_requires_no_match_body_for_zero_loaded() -> None:
    text = """## Rules Loaded

Task Switch: FIRST
"""
    violations = validate_output_shape(text, loaded_count=0)
    assert "zero loaded rules must use explicit no-match Rules Loaded body" in violations


@pytest.mark.unit
def test_extract_contract_text_anchors_on_rules_loaded() -> None:
    text = """Scanning rules first.

## Rules Loaded
- rules/200-python-core.md (ext:.py) — 453 lines
"""
    assert extract_contract_text(text).startswith("## Rules Loaded")


@pytest.mark.unit
def test_extract_contract_text_anchors_on_legacy_bootstrap() -> None:
    text = """Scanning rules first.

**Bootstrap:** rule Keywords scanned (python) — 1 rules loaded, 0 failed.

**Rules Loaded**
- rules/200-python-core.md (ext:.py) — 453 lines

Task Switch: FIRST
"""
    extracted = extract_contract_text(text)
    assert extracted.startswith("**Bootstrap:**")


@pytest.mark.unit
def test_run_result_fails_on_output_contract_violation() -> None:
    run = AgentRun(
        fixture_id="bad-output",
        loaded=("rules/200-python-core.md",),
        loaded_via_reads=("rules/200-python-core.md",),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/200-python-core.md",),
        output_violations=("missing **Rules Loaded** section",),
    )
    result = RunResult(
        fixture_id="bad-output",
        run=run,
        match=MatchResult(
            missing_required=(),
            missing_dependencies=(),
            forbidden_present=(),
            optional_loaded=(),
            passed=True,
        ),
        signal_report=SignalReport(ok=True, disagreements=()),
        citation_drifts=(),
    )
    assert result.passed is False
