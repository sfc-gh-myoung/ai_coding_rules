"""Unit tests for report_generator.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.report_generator import (
    DurationStats,
    ModelResult,
    TurnStats,
    _build_fixtures_data,
    _build_per_fixture_data,
    discover_results,
    extract_model_stats,
    generate_reports,
    render_report,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_SUMMARY_TEMPLATE = {
    "schema_version": "ai-rules-eval-aggregate/v1",
    "runs": 3,
    "fixture_count": 2,
    "per_fixture": {
        "simple-sql-query": {
            "n_runs": 3,
            "passes": 3,
            "fails": 0,
            "flake_score": 0.0,
            "pass_rate": 1.0,
        },
        "complex-data-pipeline": {
            "n_runs": 3,
            "passes": 2,
            "fails": 1,
            "flake_score": 0.33,
            "pass_rate": 0.67,
        },
    },
    "aggregate": {
        "mean_pass_rate": 0.833,
        "flaky_fixtures": ["complex-data-pipeline"],
        "total_cost_usd": 0.1,
        "total_input_tokens": 1000,
        "total_output_tokens": 500,
        "total_duration_ms": 120000,
        "total_signal_disagreements": 0,
        "total_citation_drifts": 1,
    },
}

_FIXTURE_PASS = {
    "schema_version": "ai-rules-eval-fixture/v1",
    "fixture_id": "simple-sql-query",
    "run_number": 1,
    "result": "pass",
    "passed": True,
    "duration_ms": 2000,
    "turns": 4,
}

_FIXTURE_FAIL = {
    "schema_version": "ai-rules-eval-fixture/v1",
    "fixture_id": "complex-data-pipeline",
    "run_number": 1,
    "result": "fail",
    "passed": False,
    "duration_ms": 3000,
    "turns": 5,
}

_FIXTURE_ERROR = {
    "schema_version": "ai-rules-eval-fixture/v1",
    "fixture_id": "simple-sql-query",
    "run_number": 2,
    "result": "error",
    "passed": False,
    "duration_ms": 500,
    "turns": 1,
}


def _make_run_dir(
    tmp_path: Path,
    model: str,
    runs: int = 3,
    ts: str = "20260718-120000",
    *,
    include_error: bool = False,
) -> Path:
    """Create a minimal mock run directory structure."""
    run_dir = tmp_path / f"{model}_{runs}x_{ts}"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")

    # Create pass_1 and pass_2 subdirectories (plan-compatible structure)
    for pass_num in (1, 2):
        pass_dir = run_dir / f"pass_{pass_num}"
        pass_dir.mkdir()
        (pass_dir / "simple-sql-query.json").write_text(json.dumps(_FIXTURE_PASS), encoding="utf-8")
        (pass_dir / "complex-data-pipeline.json").write_text(
            json.dumps(_FIXTURE_FAIL), encoding="utf-8"
        )
        if include_error:
            (pass_dir / "error-fixture.json").write_text(
                json.dumps(_FIXTURE_ERROR), encoding="utf-8"
            )
    return run_dir


def _make_real_run_dir(
    tmp_path: Path,
    model: str,
    runs: int = 3,
    ts: str = "20260718-120000",
) -> Path:
    """Create a mock run directory using real run-0N/fixtures/ layout."""
    run_dir = tmp_path / f"{model}_{runs}x_{ts}"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")

    for run_num in range(1, runs + 1):
        fx_dir = run_dir / f"run-{run_num:02d}" / "fixtures"
        fx_dir.mkdir(parents=True)
        (fx_dir / "simple-sql-query.json").write_text(json.dumps(_FIXTURE_PASS), encoding="utf-8")
        (fx_dir / "complex-data-pipeline.json").write_text(
            json.dumps(_FIXTURE_FAIL), encoding="utf-8"
        )
    return run_dir


# ---------------------------------------------------------------------------
# discover_results
# ---------------------------------------------------------------------------


def test_discover_results_selects_latest(tmp_path: Path) -> None:
    _make_run_dir(tmp_path, "my-model", ts="20260710-000000")
    latest = _make_run_dir(tmp_path, "my-model", ts="20260718-120000")
    result = discover_results(tmp_path)
    assert result == {"my-model": latest}


def test_discover_results_multiple_models(tmp_path: Path) -> None:
    a = _make_run_dir(tmp_path, "model-a", ts="20260718-120000")
    b = _make_run_dir(tmp_path, "model-b", ts="20260718-130000")
    result = discover_results(tmp_path)
    assert result == {"model-a": a, "model-b": b}


def test_discover_empty_dir(tmp_path: Path) -> None:
    result = discover_results(tmp_path)
    assert result == {}


def test_dirname_regex_edge_cases(tmp_path: Path) -> None:
    # Model name with hyphens and dots
    run_dir = _make_run_dir(tmp_path, "openai-gpt-5.2", ts="20260718-150000")
    result = discover_results(tmp_path)
    assert "openai-gpt-5.2" in result
    assert result["openai-gpt-5.2"] == run_dir


# ---------------------------------------------------------------------------
# extract_model_stats
# ---------------------------------------------------------------------------


def test_extract_model_stats_valid(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path, "test-model")
    result = extract_model_stats(run_dir)
    assert result.model == "test-model"
    assert result.fixture_count == 2
    assert result.runs == 3
    assert abs(result.pass_rate - 0.833) < 0.01
    assert result.flaky_fixtures == ["complex-data-pipeline"]
    assert result.citation_drifts == 1


def test_extract_duration_stats(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path, "perf-model")
    result = extract_model_stats(run_dir)
    assert result.duration_stats is not None
    # pass fixtures have 2000ms, fail fixtures have 3000ms; 4 total across 2 passes
    # expected mean = (2000 + 3000 + 2000 + 3000) / 4 / 1000 = 2.5s
    assert result.duration_stats.mean_s == pytest.approx(2.5, abs=0.1)


def test_duration_ms_to_seconds_conversion(tmp_path: Path) -> None:
    # Single pass, single fixture with duration_ms=1500
    run_dir = tmp_path / "conv-model_1x_20260718-000000"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")
    pass_dir = run_dir / "pass_1"
    pass_dir.mkdir()
    fx = {**_FIXTURE_PASS, "duration_ms": 1500}
    (pass_dir / "simple-sql-query.json").write_text(json.dumps(fx), encoding="utf-8")
    result = extract_model_stats(run_dir)
    assert result.duration_stats is not None
    assert result.duration_stats.mean_s == pytest.approx(1.5, abs=0.01)


def test_extract_turn_stats(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path, "turns-model")
    result = extract_model_stats(run_dir)
    assert result.turn_stats is not None
    # turns: 4 (pass) and 5 (fail) x 2 passes = [4, 5, 4, 5]
    assert result.turn_stats.mean == pytest.approx(4.5, abs=0.01)
    assert result.turn_stats.max == 5


def test_extract_skips_error_results(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path, "err-model", include_error=True)
    result = extract_model_stats(run_dir)
    # error fixture has duration_ms=500 but must be excluded
    # remaining fixtures have 2000 and 3000 each across 2 passes
    assert result.duration_stats is not None
    assert result.duration_stats.mean_s == pytest.approx(2.5, abs=0.1)


def test_extract_skips_missing_duration(tmp_path: Path) -> None:
    run_dir = tmp_path / "nodur-model_3x_20260718-000000"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")
    pass_dir = run_dir / "pass_1"
    pass_dir.mkdir()
    # No duration_ms field
    fx = {"fixture_id": "x", "result": "pass", "turns": 3}
    (pass_dir / "x.json").write_text(json.dumps(fx), encoding="utf-8")
    result = extract_model_stats(run_dir)
    # Should not crash; duration_stats may be None since only 1 record at most
    # but the record has no duration_ms so duration_stats is None
    # turns_list has [3] so turn_stats is populated
    assert result.turn_stats is not None
    assert result.turn_stats.mean == 3.0


def test_extract_aggregates_across_passes(tmp_path: Path) -> None:
    # Two pass dirs with different durations to confirm cross-pass aggregation
    run_dir = tmp_path / "multi-model_2x_20260718-000000"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")
    for pass_num, dur in enumerate([1000, 5000], start=1):
        pass_dir = run_dir / f"pass_{pass_num}"
        pass_dir.mkdir()
        fx = {**_FIXTURE_PASS, "duration_ms": dur}
        (pass_dir / "fx.json").write_text(json.dumps(fx), encoding="utf-8")
    result = extract_model_stats(run_dir)
    assert result.duration_stats is not None
    # mean = (1.0 + 5.0) / 2 = 3.0s
    assert result.duration_stats.mean_s == pytest.approx(3.0, abs=0.01)


# ---------------------------------------------------------------------------
# render_report
# ---------------------------------------------------------------------------


def _make_model_result(model: str = "test-model") -> ModelResult:
    return ModelResult(
        model=model,
        pass_rate=0.99,
        fixture_count=33,
        runs=3,
        flaky_fixtures=["complex-data-pipeline"],
        citation_drifts=1,
        duration_stats=DurationStats(mean_s=55.0, median_s=52.0, p95_s=90.0, total_s=5445.0),
        turn_stats=TurnStats(mean=5.5, median=5.0, max=12),
        result_dir=f"{model}_3x_20260718-120000",
        per_fixture={
            "simple-sql-query": {
                "n_runs": 3,
                "passes": 3,
                "fails": 0,
                "flake_score": 0.0,
                "pass_rate": 1.0,
            },
            "complex-data-pipeline": {
                "n_runs": 3,
                "passes": 2,
                "fails": 1,
                "flake_score": 0.33,
                "pass_rate": 0.67,
            },
        },
    )


def test_render_html(tmp_path: Path) -> None:
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    rendered_path = render_report(results, "compliance-report.html.j2", out)
    assert rendered_path == out
    content = out.read_text(encoding="utf-8")
    assert "<html" in content
    assert "</html>" in content
    assert 'nav[role="tablist"]' in content or 'nav role="tablist"' in content
    assert 'data-tab="overview"' in content
    assert 'data-tab="protocol"' in content
    assert 'data-tab="taxonomy"' in content
    assert 'data-tab="results"' in content
    assert 'data-tab="recommendations"' in content
    assert 'data-tab="performance"' in content
    assert "--sf-blue" in content
    assert "chart.js" in content.lower() or "Chart.js" in content


def test_render_markdown(tmp_path: Path) -> None:
    results = [_make_model_result()]
    out = tmp_path / "test.md"
    rendered_path = render_report(results, "compliance-report.md.j2", out)
    assert rendered_path == out
    content = out.read_text(encoding="utf-8")
    assert "# LLM Protocol Compliance" in content
    assert "## Overview" in content
    assert "## Performance" in content
    assert "Methodology Notes" in content
    assert "test-model" in content


def test_generate_reports_both(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    _make_run_dir(results_dir, "opus-4-6")
    output_dir = tmp_path / "reports"
    written = generate_reports(
        results_dir=results_dir, output_dir=output_dir, formats=["html", "md"]
    )
    assert len(written) == 2
    names = {p.name for p in written}
    assert "llm-protocol-compliance-report.html" in names
    assert "llm-protocol-compliance-report.md" in names
    for p in written:
        assert p.exists()
        assert p.stat().st_size > 100


# ---------------------------------------------------------------------------
# _build_fixtures_data / _build_per_fixture_data
# ---------------------------------------------------------------------------


def test_build_fixtures_data_ordering() -> None:
    r = _make_model_result()
    # Add a medium fixture so we get ordering across tiers
    r.per_fixture["medium-cortex-search"] = {
        "n_runs": 3,
        "passes": 3,
        "fails": 0,
        "flake_score": 0.0,
        "pass_rate": 1.0,
    }
    fixtures = _build_fixtures_data([r])
    tiers = [f["tier"] for f in fixtures]
    # simple comes before medium, medium before complex
    simple_idx = next(i for i, f in enumerate(fixtures) if f["tier"] == "simple")
    medium_idx = next(i for i, f in enumerate(fixtures) if f["tier"] == "medium")
    complex_idx = next(i for i, f in enumerate(fixtures) if f["tier"] == "complex")
    assert simple_idx < medium_idx < complex_idx


def test_build_per_fixture_data() -> None:
    r = _make_model_result("model-x")
    data = _build_per_fixture_data([r])
    assert "model-x" in data
    assert data["model-x"]["simple-sql-query"]["passes"] == 3
    assert data["model-x"]["complex-data-pipeline"]["passes"] == 2
