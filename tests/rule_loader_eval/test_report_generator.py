"""Unit tests for report_generator.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_rules.rule_loader_eval.report_generator import (
    DurationStats,
    ModelResult,
    TurnStats,
    _build_effort_data,
    _build_effort_insights,
    _build_family_comparison,
    _build_fixtures_data,
    _build_overview_insights,
    _build_per_fixture_data,
    _build_vega_chart_data,
    _classify_family,
    _collect_per_fixture_effort,
    _compute_latency_pareto,
    _compute_metric_stats,
    _parse_ai_json_response,
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

_FIXTURE_PASS_WITH_TOKENS = {
    **_FIXTURE_PASS,
    "input_tokens": 10000,
    "output_tokens": 500,
}
_FIXTURE_FAIL_WITH_TOKENS = {
    **_FIXTURE_FAIL,
    "input_tokens": 15000,
    "output_tokens": 800,
}


def _make_run_dir(
    tmp_path: Path,
    model: str,
    runs: int = 3,
    ts: str = "20260718-120000",
    *,
    include_error: bool = False,
    include_tokens: bool = False,
) -> Path:
    """Create a minimal mock run directory structure."""
    run_dir = tmp_path / f"{model}_{runs}x_{ts}"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")

    pass_fx = _FIXTURE_PASS_WITH_TOKENS if include_tokens else _FIXTURE_PASS
    fail_fx = _FIXTURE_FAIL_WITH_TOKENS if include_tokens else _FIXTURE_FAIL

    # Create pass_1 and pass_2 subdirectories (plan-compatible structure)
    for pass_num in (1, 2):
        pass_dir = run_dir / f"pass_{pass_num}"
        pass_dir.mkdir()
        (pass_dir / "simple-sql-query.json").write_text(json.dumps(pass_fx), encoding="utf-8")
        (pass_dir / "complex-data-pipeline.json").write_text(json.dumps(fail_fx), encoding="utf-8")
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
    *,
    include_tokens: bool = False,
) -> Path:
    """Create a mock run directory using real run-0N/fixtures/ layout."""
    run_dir = tmp_path / f"{model}_{runs}x_{ts}"
    run_dir.mkdir()
    (run_dir / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")

    pass_fx = _FIXTURE_PASS_WITH_TOKENS if include_tokens else _FIXTURE_PASS
    fail_fx = _FIXTURE_FAIL_WITH_TOKENS if include_tokens else _FIXTURE_FAIL

    for run_num in range(1, runs + 1):
        fx_dir = run_dir / f"run-{run_num:02d}" / "fixtures"
        fx_dir.mkdir(parents=True)
        (fx_dir / "simple-sql-query.json").write_text(json.dumps(pass_fx), encoding="utf-8")
        (fx_dir / "complex-data-pipeline.json").write_text(json.dumps(fail_fx), encoding="utf-8")
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


def test_discover_results_accepts_single_run_dir(tmp_path: Path) -> None:
    """Pointing results_dir directly at one run directory returns that run."""
    run_dir = _make_run_dir(tmp_path, "my-model", ts="20260718-120000")
    result = discover_results(run_dir)
    assert result == {"my-model": run_dir}


def test_discover_results_single_run_dir_without_plugin_mode(tmp_path: Path) -> None:
    """A single run dir keeps its [no-plugin] display key from manifest.json."""
    run_dir = _make_run_dir(tmp_path, "my-model", ts="20260718-120000")
    (run_dir / "manifest.json").write_text(json.dumps({"mode": "without-plugin"}), encoding="utf-8")
    result = discover_results(run_dir)
    assert result == {"my-model [no-plugin]": run_dir}


def test_discover_results_single_run_dir_bad_name_returns_empty(tmp_path: Path) -> None:
    """A dir with summary.json but a non-run name is not treated as a run dir."""
    bad = tmp_path / "renamed-results"
    bad.mkdir()
    (bad / "summary.json").write_text(json.dumps(_SUMMARY_TEMPLATE), encoding="utf-8")
    assert discover_results(bad) == {}


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


def _make_model_result(
    model: str = "test-model",
    *,
    mode: str = "plugin",
    runs: int = 3,
    ts: str = "20260718-120000",
) -> ModelResult:
    return ModelResult(
        model=model,
        pass_rate=0.99,
        fixture_count=33,
        runs=runs,
        mode=mode,
        ts=ts,
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
    assert 'nav role="tablist"' in content
    assert "switchTab" in content
    assert 'id="overview"' in content
    assert 'id="protocol"' in content
    assert 'id="taxonomy"' in content
    assert 'id="results"' in content
    assert 'id="model-selection"' in content
    assert 'id="performance"' in content
    assert 'id="model-effort"' in content
    assert "--sf-blue" in content
    assert "vega-lite" in content.lower()
    # Alpine is inlined (vendored asset), never loaded from the CDN.
    assert "cdn.jsdelivr.net/npm/alpinejs" not in content
    assert "window.Alpine" in content


def test_generate_reports_writes_html_only(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    _make_run_dir(results_dir, "opus-4-6")
    output_dir = tmp_path / "reports"
    written = generate_reports(results_dir=results_dir, output_dir=output_dir)
    assert len(written) == 1
    assert written[0].name == "llm-protocol-compliance-report.html"
    assert written[0].exists()
    assert written[0].stat().st_size > 100
    # No markdown artifact is produced any more
    assert not list(output_dir.glob("*.md"))


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


# ---------------------------------------------------------------------------
# _compute_metric_stats
# ---------------------------------------------------------------------------


def test_compute_metric_stats_basic() -> None:
    result = _compute_metric_stats([10.0, 20.0, 30.0])
    assert result["min_val"] == pytest.approx(10.0)
    assert result["avg_val"] == pytest.approx(20.0)
    assert result["max_val"] == pytest.approx(30.0)


def test_compute_metric_stats_single() -> None:
    result = _compute_metric_stats([42.5])
    assert result["min_val"] == result["avg_val"] == result["max_val"] == pytest.approx(42.5)


def test_compute_metric_stats_empty() -> None:
    result = _compute_metric_stats([])
    assert result == {"min_val": 0.0, "avg_val": 0.0, "max_val": 0.0}


# ---------------------------------------------------------------------------
# _collect_per_fixture_effort
# ---------------------------------------------------------------------------


def test_collect_per_fixture_effort_basic(tmp_path: Path) -> None:
    run_dir = _make_real_run_dir(tmp_path, "token-model", runs=2, include_tokens=True)
    result = _collect_per_fixture_effort(run_dir)
    assert "simple-sql-query" in result
    assert "complex-data-pipeline" in result
    # 2 runs x input_tokens=10000 per pass fixture
    assert result["simple-sql-query"]["input_tokens"] == [10000.0, 10000.0]
    assert result["simple-sql-query"]["output_tokens"] == [500.0, 500.0]


def test_collect_per_fixture_effort_skips_error(tmp_path: Path) -> None:
    run_dir = _make_run_dir(tmp_path, "err-model", include_error=True, include_tokens=True)
    result = _collect_per_fixture_effort(run_dir)
    # error fixture has result='error' and same fixture_id: should not appear
    for vals in result.get("simple-sql-query", {}).get("input_tokens", []):
        assert vals > 0  # only non-error results included


def test_collect_per_fixture_effort_missing_tokens(tmp_path: Path) -> None:
    # Fixtures without input_tokens/output_tokens (original format)
    run_dir = _make_real_run_dir(tmp_path, "no-token-model", runs=2, include_tokens=False)
    result = _collect_per_fixture_effort(run_dir)
    assert "simple-sql-query" in result
    # input_tokens and output_tokens lists must be empty (fields absent)
    assert result["simple-sql-query"]["input_tokens"] == []
    assert result["simple-sql-query"]["output_tokens"] == []
    # But elapsed_s and turns ARE present
    assert len(result["simple-sql-query"]["elapsed_s"]) == 2
    assert len(result["simple-sql-query"]["turns"]) == 2


# ---------------------------------------------------------------------------
# _build_effort_data
# ---------------------------------------------------------------------------


def test_build_effort_data_no_connection(tmp_path: Path) -> None:
    run_dir = _make_real_run_dir(tmp_path, "m1", runs=2, include_tokens=True)
    r = extract_model_stats(run_dir)
    result = _build_effort_data([r], connection_name=None)
    assert result["insights"] is None
    assert result["insights_available"] is False


def test_build_effort_data_fixture_order(tmp_path: Path) -> None:
    run_dir = _make_real_run_dir(tmp_path, "order-model", runs=1, include_tokens=False)
    # Add a medium fixture to the run
    medium_fx = {**_FIXTURE_PASS, "fixture_id": "medium-extra", "duration_ms": 1000, "turns": 2}
    (run_dir / "run-01" / "fixtures" / "medium-extra.json").write_text(
        json.dumps(medium_fx), encoding="utf-8"
    )
    r = extract_model_stats(run_dir)
    result = _build_effort_data([r], connection_name=None)
    fixture_ids = result["fixtures"]
    # __aggregate__ first, then simple before complex
    assert fixture_ids[0] == "__aggregate__"
    complex_pos = next(i for i, f in enumerate(fixture_ids) if f.startswith("complex"))
    simple_pos = next(i for i, f in enumerate(fixture_ids) if f.startswith("simple"))
    assert simple_pos < complex_pos


def test_build_effort_data_aggregate_bucket(tmp_path: Path) -> None:
    run_dir = _make_real_run_dir(tmp_path, "agg-model", runs=2, include_tokens=True)
    r = extract_model_stats(run_dir)
    result = _build_effort_data([r], connection_name=None)
    assert "__aggregate__" in result["by_fixture"]
    agg = result["by_fixture"]["__aggregate__"]["agg-model"]
    assert agg["input_tokens"]["avg_val"] > 0


# ---------------------------------------------------------------------------
# render_report / generate_reports: effort tab
# ---------------------------------------------------------------------------


def test_render_html_includes_effort_tab(tmp_path: Path) -> None:
    results = [_make_model_result()]
    out = tmp_path / "effort.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert 'id="model-effort"' in content
    assert 'id="effort-table"' in content
    assert 'id="effort-fixture-select"' in content


def test_render_html_effort_no_insights(tmp_path: Path) -> None:
    results = [_make_model_result()]
    out = tmp_path / "no-insights.html"
    render_report(results, "compliance-report.html.j2", out, connection_name=None)
    content = out.read_text(encoding="utf-8")
    assert "AI insights not available" in content


def test_generate_reports_passes_connection(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    _make_run_dir(results_dir, "conn-model")
    output_dir = tmp_path / "reports"

    with patch(
        "ai_rules.rule_loader_eval.report_generator.render_report",
        wraps=render_report,
    ) as mock_render:
        generate_reports(
            results_dir=results_dir,
            output_dir=output_dir,
            connection_name="my-conn",
        )

    mock_render.assert_called_once()
    _args, kwargs = mock_render.call_args
    assert kwargs.get("connection_name") == "my-conn"


# ---------------------------------------------------------------------------
# _build_effort_insights: exception paths
# ---------------------------------------------------------------------------


def test_build_effort_insights_runtime_error() -> None:
    with patch("ai_rules.cortex.client.complete", side_effect=RuntimeError("boom")):
        result = _build_effort_insights({}, connection_name=None)
    assert result is None


def test_build_effort_insights_json_decode_error() -> None:
    from ai_rules.cortex.models import CortexResponse

    mock_response = CortexResponse(text="not-valid-json")
    with patch("ai_rules.cortex.client.complete", return_value=mock_response):
        result = _build_effort_insights({}, connection_name=None)
    assert result is None


# ---------------------------------------------------------------------------
# Latency-quality Pareto frontier
# ---------------------------------------------------------------------------


def _lat_result(model: str, pass_rate: float, mean_s: float, turns: float) -> ModelResult:
    r = _make_model_result(model)
    r.pass_rate = pass_rate
    r.duration_stats = DurationStats(
        mean_s=mean_s, median_s=mean_s, p95_s=mean_s * 1.5, total_s=mean_s * 100
    )
    r.turn_stats = TurnStats(mean=turns, median=turns, max=int(turns) + 1)
    return r


def test_latency_pareto_frontier_selection() -> None:
    """Non-dominated qualifying models are on the frontier; dominated ones are not."""
    results = [
        _lat_result("fast-ok", 0.909, 57.9, 4.6),  # cheapest time at its accuracy
        _lat_result("slow-best", 0.994, 62.3, 1.0),  # most accurate, slightly slower
        _lat_result("dominated", 0.943, 77.7, 3.0),  # slower AND less accurate
    ]
    pts = {p["model"]: p for p in _compute_latency_pareto(results)}
    assert pts["fast-ok"]["on_frontier"] is True
    assert pts["slow-best"]["on_frontier"] is True
    assert pts["dominated"]["on_frontier"] is False


def test_latency_pareto_excludes_below_threshold() -> None:
    """A sub-threshold model is never on the frontier, even when it is the fastest."""
    results = [
        _lat_result("skipper", 0.583, 38.4, 2.2),  # fastest overall, but 58.3%
        _lat_result("good", 0.994, 62.3, 1.0),
    ]
    pts = {p["model"]: p for p in _compute_latency_pareto(results)}
    assert pts["skipper"]["below_threshold"] is True
    assert pts["skipper"]["on_frontier"] is False
    assert pts["good"]["on_frontier"] is True


def test_latency_pareto_categories_mutually_exclusive() -> None:
    """Every model falls into exactly one of below / frontier / dominated."""
    results = [
        _lat_result("skipper", 0.583, 38.4, 2.2),
        _lat_result("fast-ok", 0.909, 57.9, 4.6),
        _lat_result("slow-best", 0.994, 62.3, 1.0),
        _lat_result("dominated", 0.943, 77.7, 3.0),
    ]
    for p in _compute_latency_pareto(results):
        below = p["below_threshold"]
        frontier = p["on_frontier"]
        assert not (below and frontier), f"{p['model']} is in two categories"


def test_latency_pareto_sorted_by_duration() -> None:
    results = [
        _lat_result("c", 0.99, 90.0, 2.0),
        _lat_result("a", 0.99, 40.0, 2.0),
        _lat_result("b", 0.99, 60.0, 2.0),
    ]
    durations = [p["avg_duration_s"] for p in _compute_latency_pareto(results)]
    assert durations == sorted(durations)


def test_latency_pareto_handles_missing_duration_stats() -> None:
    r = _make_model_result("no-timing")
    r.duration_stats = None
    r.turn_stats = None
    pts = _compute_latency_pareto([r])
    assert pts[0]["avg_duration_s"] == 0.0
    assert pts[0]["avg_turns"] == 0.0
    assert pts[0]["on_frontier"] is False


# ── Phase 6: discovery attribution ───────────────────────────────────────────

from ai_rules.rule_loader_eval.report_generator import (  # noqa: E402
    _build_discovery_attribution,
)


def _model_result(discovery: dict) -> ModelResult:
    return ModelResult(
        model="m",
        pass_rate=1.0,
        fixture_count=sum(discovery.values()),
        runs=1,
        flaky_fixtures=[],
        citation_drifts=0,
        duration_stats=None,
        turn_stats=None,
        result_dir="d",
        discovery=discovery,
    )


def test_build_discovery_attribution_buckets() -> None:
    row = _build_discovery_attribution(
        [
            _model_result(
                {
                    "pass": 3,
                    "signal-violation": 1,
                    "agent-miss": 1,
                    "matcher-miss": 1,
                    "empty-manifest": 1,
                    "recovery-only": 2,
                    "legacy": 1,
                    "error": 1,
                }
            )
        ]
    )[0]
    # Recalled = pass + agent-miss + signal-violation; not recalled = matcher-miss + empty-manifest.
    assert row["matcher_recall"] == {"recalled": 5, "not_recalled": 2}
    assert row["agent_compliance"] == {"complied": 4, "missed": 1}
    assert row["recovery_only"] == 2
    assert row["legacy"] == 1
    assert row["errors"] == 1


def test_build_discovery_attribution_empty_model() -> None:
    row = _build_discovery_attribution([_model_result({})])[0]
    assert row["matcher_recall"] == {"recalled": 0, "not_recalled": 0}
    assert row["recovery_only"] == 0


def _write_run_with_attribution(tmp_path: Path) -> Path:
    run_dir = tmp_path / "m_1x_20260803-000000"
    (run_dir / "run-01" / "fixtures").mkdir(parents=True)
    run_dir.joinpath("summary.json").write_text(
        json.dumps({"aggregate": {"mean_pass_rate": 1.0}, "fixture_count": 2, "runs": 1}),
        encoding="utf-8",
    )
    passing = {
        "result": "pass",
        "passed": True,
        "duration_ms": 100,
        "turns": 2,
        "manifest_recall": True,
        "agent_compliance": True,
        "manifest_empty": False,
        "out_of_manifest_recovery": {"count": 0, "rules": []},
    }
    recovery = {
        "result": "recovery-only",
        "passed": False,
        "duration_ms": 100,
        "turns": 2,
        "manifest_recall": False,
        "agent_compliance": True,
        "manifest_empty": False,
        "out_of_manifest_recovery": {"count": 1, "rules": ["rules/112-snowflake-snowcli.md"]},
    }
    fx = run_dir / "run-01" / "fixtures"
    fx.joinpath("a.json").write_text(json.dumps(passing), encoding="utf-8")
    fx.joinpath("b.json").write_text(json.dumps(recovery), encoding="utf-8")
    return run_dir


def test_load_model_result_tallies_discovery(tmp_path: Path) -> None:
    mr = extract_model_stats(_write_run_with_attribution(tmp_path))
    assert mr.discovery.get("pass") == 1
    assert mr.discovery.get("recovery-only") == 1
    row = _build_discovery_attribution([mr])[0]
    assert row["matcher_recall"] == {"recalled": 1, "not_recalled": 0}
    assert row["recovery_only"] == 1


def test_render_includes_discovery_section(tmp_path: Path) -> None:
    mr = extract_model_stats(_write_run_with_attribution(tmp_path))
    out = tmp_path / "report.html"
    render_report([mr], "compliance-report.html.j2", out)
    html = out.read_text(encoding="utf-8")
    assert "Discovery Attribution" in html
    assert "discovery-attribution-table" in html


# ---------------------------------------------------------------------------
# _parse_ai_json_response
# ---------------------------------------------------------------------------


def test_parse_ai_json_response_plain_json() -> None:
    """Plain JSON array is decoded correctly."""
    text = json.dumps(["a", "b", "c"])
    result = _parse_ai_json_response(text)
    assert result == ["a", "b", "c"]


def test_parse_ai_json_response_double_encoded() -> None:
    """Double-encoded string (outer JSON string literal containing JSON) is unwrapped."""
    inner = '["obs1", "obs2", "obs3"]'
    text = json.dumps(inner)  # outer encode
    result = _parse_ai_json_response(text)
    assert result == ["obs1", "obs2", "obs3"]


def test_parse_ai_json_response_code_fenced() -> None:
    """Code-fenced JSON inside a double-encoded string is decoded correctly."""
    inner = '```json\n["obs1", "obs2", "obs3"]\n```'
    text = json.dumps(inner)
    result = _parse_ai_json_response(text)
    assert result == ["obs1", "obs2", "obs3"]


def test_parse_ai_json_response_invalid_raises() -> None:
    """Invalid JSON raises a json.JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        _parse_ai_json_response("not-valid-json")


# ---------------------------------------------------------------------------
# _build_overview_insights
# ---------------------------------------------------------------------------

_FM_DATA = {
    "models": ["test-model"],
    "modes": ["FM-1", "FM-2"],
    "counts": [[3, 1]],
}


def _make_complete_response(payload: object):
    """Return a mock CortexResponse whose .text is a double-encoded JSON string."""
    from ai_rules.cortex.models import CortexResponse

    return CortexResponse(text=json.dumps(json.dumps(payload)))


def test_build_overview_insights_success() -> None:
    insights = ["obs1", "obs2", "obs3"]
    mock_response = _make_complete_response(insights)
    with patch("ai_rules.cortex.client.complete", return_value=mock_response) as mock_complete:
        result = _build_overview_insights([_make_model_result()], "test-conn", _FM_DATA)
    assert result == insights
    call_kwargs = mock_complete.call_args
    prompt = call_kwargs.args[0] if call_kwargs.args else call_kwargs.kwargs.get("prompt", "")
    assert "FM-1" in prompt
    assert mock_complete.call_args.kwargs.get("max_tokens") == 1500


def test_build_overview_insights_failure_raises() -> None:
    with patch("ai_rules.cortex.client.complete", side_effect=RuntimeError("boom")):
        result = _build_overview_insights([_make_model_result()], "test-conn", _FM_DATA)
    assert result is None


def test_build_overview_insights_malformed_short_list() -> None:
    mock_response = _make_complete_response(["only-two-items", "item2"])
    with patch("ai_rules.cortex.client.complete", return_value=mock_response):
        result = _build_overview_insights([_make_model_result()], "test-conn", _FM_DATA)
    assert result is None


def test_build_overview_insights_non_list() -> None:
    mock_response = _make_complete_response({"bad": "shape"})
    with patch("ai_rules.cortex.client.complete", return_value=mock_response):
        result = _build_overview_insights([_make_model_result()], "test-conn", _FM_DATA)
    assert result is None


# ---------------------------------------------------------------------------
# render_report: overview insights wiring
# ---------------------------------------------------------------------------


def test_render_html_static_observations_always_present(tmp_path: Path) -> None:
    out = tmp_path / "obs.html"
    render_report([_make_model_result()], "compliance-report.html.j2", out)
    html = out.read_text(encoding="utf-8")
    assert "Observations" in html
    assert "declared-but-not-read" in html


def test_render_html_this_report_present_when_insights_available(tmp_path: Path) -> None:
    insights = ["obs1", "obs2", "obs3"]
    mock_response = _make_complete_response(insights)
    out = tmp_path / "with_insights.html"
    with patch("ai_rules.cortex.client.complete", return_value=mock_response):
        render_report(
            [_make_model_result()], "compliance-report.html.j2", out, connection_name="conn"
        )
    html = out.read_text(encoding="utf-8")
    assert "This Report" in html
    assert "obs1" in html
    assert "obs2" in html
    assert "obs3" in html


def test_render_html_no_this_report_on_degradation(tmp_path: Path) -> None:
    out = tmp_path / "no_conn.html"
    render_report([_make_model_result()], "compliance-report.html.j2", out, connection_name=None)
    html = out.read_text(encoding="utf-8")
    assert "Observations" in html
    assert "This Report" not in html


def test_render_html_env_connection_routing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SNOWFLAKE_CONNECTION_NAME env var is forwarded to the overview insights call."""
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "test-conn")
    insights = ["obs1", "obs2", "obs3"]
    mock_response = _make_complete_response(insights)
    out = tmp_path / "env_conn.html"

    with patch("ai_rules.cortex.client.complete", return_value=mock_response) as mock_complete:
        with patch(
            "ai_rules.rule_loader_eval.report_generator._build_effort_insights",
            return_value=None,
        ):
            render_report(
                [_make_model_result()], "compliance-report.html.j2", out, connection_name=None
            )

    # Find the overview-context call and assert connection_name="test-conn"
    overview_calls = [
        c
        for c in mock_complete.call_args_list
        if "concise report-specific observations"
        in (c.args[0] if c.args else c.kwargs.get("prompt", ""))
    ]
    assert len(overview_calls) == 1
    assert overview_calls[0].kwargs.get("connection_name") == "test-conn"


# ---------------------------------------------------------------------------
# has_usable_data property
# ---------------------------------------------------------------------------


class TestHasUsableData:
    """Tests for ModelResult.has_usable_data property."""

    def test_has_usable_data_with_duration(self):
        r = ModelResult(
            model="test-model",
            pass_rate=0.95,
            fixture_count=35,
            runs=5,
            flaky_fixtures=[],
            citation_drifts=0,
            duration_stats=DurationStats(mean_s=10.0, median_s=9.5, p95_s=15.0, total_s=50.0),
            turn_stats=None,
            result_dir="/tmp/test",
        )
        assert r.has_usable_data is True

    def test_has_usable_data_with_turns(self):
        r = ModelResult(
            model="test-model",
            pass_rate=0.5,
            fixture_count=1,
            runs=1,
            flaky_fixtures=[],
            citation_drifts=0,
            duration_stats=None,
            turn_stats=TurnStats(mean=2.0, median=2.0, max=3),
            result_dir="/tmp/test",
        )
        assert r.has_usable_data is True

    def test_no_usable_data_aborted(self):
        r = ModelResult(
            model="aborted-model",
            pass_rate=0.0,
            fixture_count=1,
            runs=5,
            flaky_fixtures=[],
            citation_drifts=0,
            duration_stats=None,
            turn_stats=None,
            result_dir="/tmp/test",
        )
        assert r.has_usable_data is False


# ---------------------------------------------------------------------------
# _classify_family
# ---------------------------------------------------------------------------


class TestClassifyFamily:
    """Tests for _classify_family."""

    @pytest.mark.parametrize(
        "model,expected",
        [
            ("claude-opus-4-6", "Anthropic"),
            ("claude-sonnet-4-5", "Anthropic"),
            ("gpt-4o", "OpenAI"),
            ("o1-preview", "OpenAI"),
            ("o3-mini", "OpenAI"),
            ("gemini-3.1-pro", "Google"),
            ("glm-4-plus", "Zhipu"),
            ("unknown-model-x", "Other"),
        ],
    )
    def test_family_classification(self, model, expected):
        assert _classify_family(model) == expected


# ---------------------------------------------------------------------------
# _build_family_comparison
# ---------------------------------------------------------------------------


class TestBuildFamilyComparison:
    """Tests for _build_family_comparison."""

    def _make_result(self, model, pass_rate, has_data=True):
        return ModelResult(
            model=model,
            pass_rate=pass_rate,
            fixture_count=35,
            runs=5,
            flaky_fixtures=["fx-a"] if pass_rate < 1.0 else [],
            citation_drifts=0,
            duration_stats=DurationStats(10.0, 9.0, 15.0, 50.0) if has_data else None,
            turn_stats=TurnStats(mean=2.0, median=2.0, max=3) if has_data else None,
            result_dir="/tmp/test",
        )

    def test_groups_by_family(self):
        results = [
            self._make_result("claude-opus-4-6", 0.98),
            self._make_result("claude-sonnet-4-5", 0.99),
            self._make_result("gpt-4o", 0.99),
        ]
        agg = {
            r.display_key: {
                "turns": {"avg_val": 2.0, "min_val": 1.0, "max_val": 3.0},
                "input_tokens": {"avg_val": 100000, "min_val": 80000, "max_val": 120000},
                "elapsed_s": {"avg_val": 45.0, "min_val": 30.0, "max_val": 60.0},
            }
            for r in results
        }
        families = _build_family_comparison(results, agg)
        family_names = [f["family"] for f in families]
        assert "Anthropic" in family_names
        assert "OpenAI" in family_names

    def test_excludes_no_data_models(self):
        results = [
            self._make_result("claude-opus-4-6", 0.98, has_data=True),
            self._make_result("gemini-3.1-pro", 0.0, has_data=False),
        ]
        agg = {
            "claude-opus-4-6": {
                "turns": {"avg_val": 3.0, "min_val": 2.0, "max_val": 4.0},
                "input_tokens": {"avg_val": 200000, "min_val": 150000, "max_val": 250000},
                "elapsed_s": {"avg_val": 55.0, "min_val": 40.0, "max_val": 70.0},
            },
        }
        families = _build_family_comparison(results, agg)
        family_names = [f["family"] for f in families]
        assert "Google" not in family_names
        assert "Anthropic" in family_names


# ---------------------------------------------------------------------------
# _build_vega_chart_data
# ---------------------------------------------------------------------------


def test_build_vega_chart_data_structure() -> None:
    """Verify flat record list has correct shape and derived fields."""
    plugin_result = ModelResult(
        model="test-model",
        pass_rate=0.99,
        fixture_count=10,
        runs=3,
        flaky_fixtures=[],
        citation_drifts=0,
        duration_stats=DurationStats(mean_s=40.0, median_s=38.0, p95_s=60.0, total_s=1200.0),
        turn_stats=TurnStats(mean=2.5, median=2.0, max=5),
        result_dir="test-model_3x_20260718-120000",
        mode="plugin",
    )
    noplugin_result = ModelResult(
        model="test-model",
        pass_rate=0.80,
        fixture_count=10,
        runs=3,
        flaky_fixtures=["f1"],
        citation_drifts=2,
        duration_stats=DurationStats(mean_s=70.0, median_s=65.0, p95_s=100.0, total_s=2100.0),
        turn_stats=TurnStats(mean=3.5, median=3.0, max=8),
        result_dir="test-model_3x_20260719-120000",
        mode="without-plugin",
    )
    results = [plugin_result, noplugin_result]
    latency_pareto = _compute_latency_pareto(results)
    cost_pareto = [
        {
            "model": "test-model",
            "avg_total_tokens": 50000,
            "on_frontier": True,
            "below_threshold": False,
        },
        {
            "model": "test-model [no-plugin]",
            "avg_total_tokens": 80000,
            "on_frontier": False,
            "below_threshold": True,
        },
    ]

    data = _build_vega_chart_data(results, latency_pareto, cost_pareto)

    assert isinstance(data, list)
    assert len(data) == 2

    required_keys = {
        "model",
        "model_short",
        "mode",
        "pass_rate",
        "avg_duration_s",
        "avg_turns",
        "avg_total_tokens",
        "below_threshold_latency",
        "below_threshold_cost",
        "on_frontier_latency",
        "on_frontier_cost",
        "category_latency",
        "category_cost",
    }
    for record in data:
        assert required_keys <= set(record.keys()), (
            f"Missing keys: {required_keys - set(record.keys())}"
        )

    # Plugin model has no * suffix
    plugin_rec = next(r for r in data if r["mode"] == "plugin")
    assert not plugin_rec["model_short"].endswith("*")

    # No-plugin model has * suffix
    np_rec = next(r for r in data if r["mode"] == "without-plugin")
    assert np_rec["model_short"].endswith("*")

    # Category values are constrained
    valid_cats = {"Below threshold", "On frontier", "Off frontier"}
    for r in data:
        assert r["category_latency"] in valid_cats
        assert r["category_cost"] in valid_cats

    # Numeric fields are present and reasonable
    assert plugin_rec["pass_rate"] == 99.0
    assert plugin_rec["avg_duration_s"] == 40.0
    assert plugin_rec["avg_turns"] == 2.5


# ---------------------------------------------------------------------------
# Regression tests: Vega-Lite Alpine migration gap remediation
# ---------------------------------------------------------------------------


def test_alpine_root_wraps_plugin_filter(tmp_path: Path) -> None:
    """Plugin status bar must be inside the Alpine reportApp() root."""
    import re

    results = [_make_model_result()]
    # Add a without-plugin result to trigger has_noplugin rendering
    np_result = _make_model_result(model="test-model-np")
    np_result.mode = "without-plugin"
    results.append(np_result)
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    # Structural check: the div with x-data appears before the div with class plugin-status-bar
    root_match = re.search(r'<div\s+x-data="reportApp\(\)"', content)
    filter_match = re.search(r'<div\s+class="plugin-status-bar"', content)
    assert root_match is not None, "Alpine root div not found"
    assert filter_match is not None, "Plugin status bar div not found"
    assert root_match.start() < filter_match.start(), (
        "Alpine root div must appear before plugin-status-bar div in DOM order"
    )


def test_hash_links_activate_matching_tab_panels(tmp_path: Path) -> None:
    """In-page hash links must update Alpine tab state after initial load."""
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert "window.addEventListener('hashchange'" in content
    assert "applyHash(location.hash.slice(1))" in content
    assert "switchTab('model-selection')" in content
    assert 'id="model-selection"' in content


def test_merged_model_selection_tab_replaces_three_tabs(tmp_path: Path) -> None:
    """Model Selection is one panel with three sub-panels; the old three are gone."""
    import re

    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")

    assert 'id="model-selection"' in content
    assert ">Model Selection</a>" in content
    for pid in ("selection-guidance", "selection-families", "selection-ai-analysis"):
        assert f'id="{pid}"' in content, f"missing sub-panel {pid}"

    # Retired panels are gone. The predicate is the panel id attribute only: the same
    # strings are required inside the legacy alias map (see the alias test below).
    for old in ("sovereignty", "recommendations", "ai-insights"):
        assert not re.search(rf'<section[^>]*id="{old}"', content), (
            f"retired panel id={old} still present as a section"
        )

    # Nav collapsed from 10 links to 8
    assert len(re.findall(r'<a href="#[^"]+" role="tab"', content)) == 8


def test_legacy_hashes_alias_to_merged_subpanels(tmp_path: Path) -> None:
    """Old permalinks must resolve to the merged tab and the right sub-panel."""
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert "_TAB_ALIASES" in content
    assert "'sovereignty':     ['model-selection', 'families']" in content
    assert "'recommendations': ['model-selection', 'guidance']" in content
    assert "'ai-insights':     ['model-selection', 'ai-analysis']" in content
    assert "selectionTab: 'guidance'" in content


def test_model_selection_sections_are_filter_aware(tmp_path: Path) -> None:
    """The provider-family block renders all three filter modes.

    Guidance holds no per-mode content: the Compliance Tiers block that used to live
    there was removed, leaving only authored prose that is mode-independent.
    """
    import re

    plugin = _make_model_result()
    np_result = _make_model_result(model="test-model-np")
    np_result.mode = "without-plugin"
    out = tmp_path / "test.html"
    render_report([plugin, np_result], "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    panel = _panel(content, "model-selection")

    def _sub(pid: str) -> str:
        seg = panel[panel.index(f'id="{pid}"') :]
        nxt = seg.find('id="selection-', 5)
        return seg[:nxt] if nxt > 0 else seg

    modes = re.findall(r"\$store\.filter\.mode === '([a-z-]+)'", _sub("selection-families"))
    assert set(modes) == {"all", "plugin", "without-plugin"}, f"families modes: {modes}"

    # Compliance Tiers are gone from Guidance, and the remaining sections are renumbered.
    guidance = _sub("selection-guidance")
    assert "Compliance Tiers" not in guidance
    assert "<h4>Compliant (95%+)</h4>" not in guidance
    assert "<h3>1. Practical Implications</h3>" in guidance
    assert "<h3>2. Scope &amp; Limitations</h3>" in guidance


def test_excluded_list_follows_filter(tmp_path: Path) -> None:
    """The AI Analysis Excluded list is per-mode, not all-models."""
    import re

    below = _make_model_result(model="weak-model")
    below.pass_rate = 0.10
    below.mode = "without-plugin"
    results = [_make_model_result(), below]

    data = _build_effort_data(results, None)
    by_mode = data["below_threshold_by_mode"]
    assert set(by_mode) == {"all", "plugin", "without-plugin"}
    # The failing model is a without-plugin run, so it must not appear in the plugin slice
    assert "weak-model [no-plugin]" in by_mode["without-plugin"]
    assert "weak-model [no-plugin]" not in by_mode["plugin"]
    assert by_mode["all"] == data["below_threshold"]

    mock_response = _make_complete_response(
        {
            "summary": "s",
            "efficiency_ranking": ["a"],
            "consistency_ranking": ["a"],
            "key_observations": [{"model": "a", "observation": "o"}],
        }
    )
    out = tmp_path / "insights.html"
    with patch("ai_rules.cortex.client.complete", return_value=mock_response):
        render_report(results, "compliance-report.html.j2", out, connection_name="conn")
    content = out.read_text(encoding="utf-8")
    panel = _panel(content, "model-selection")
    # With insights available, all three mode blocks render inside AI Analysis
    seg = panel[panel.index('id="selection-ai-analysis"') :]
    modes = re.findall(r"\$store\.filter\.mode === '([a-z-]+)'", seg)
    assert set(modes) == {"all", "plugin", "without-plugin"}, f"ai-analysis modes: {modes}"


def test_family_comparison_ordering_is_deterministic() -> None:
    """Default order is Avg Pass % desc, n<=1 last, name as tie-break.

    Order must not depend on input sequence (dict insertion), because the table
    renders in this order — no client-side initial sort runs on load.
    """
    strong = _make_model_result(model="openai-gpt-x")
    weak = _make_model_result(model="claude-y")
    weak.pass_rate = 0.50
    forward = _build_family_comparison([strong, weak], {})
    reverse = _build_family_comparison([weak, strong], {})
    assert [f["family"] for f in forward] == [f["family"] for f in reverse]

    # Both families are n=1 here, so they tie on the n<=1 flag and order by pass rate desc
    assert [f["avg_pass"] for f in forward] == sorted(
        (f["avg_pass"] for f in forward), reverse=True
    )

    # A multi-model family with a lower pass rate still outranks a single-run family
    a1 = _make_model_result(model="claude-a")
    a2 = _make_model_result(model="claude-b")
    a1.pass_rate = a2.pass_rate = 0.60
    solo = _make_model_result(model="gemini-solo")
    solo.pass_rate = 0.99
    ranked = _build_family_comparison([a1, a2, solo], {})
    assert [f["family"] for f in ranked] == ["Anthropic", "Google"]
    assert ranked[-1]["n"] == 1


def test_subtabs_use_alpine_click_handlers(tmp_path: Path) -> None:
    """Sub-tabs must use Alpine @click.prevent, not legacy data-subtab."""
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert '@click.prevent="subTab' in content
    assert "data-subtab=" not in content


def test_sortable_tables_use_delegated_init(tmp_path: Path) -> None:
    """Sortable tables use initSortableTable with guard, not Alpine.data('sortableTable')."""
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert "initSortableTable" in content
    assert "sortableInitialized" in content
    assert "Alpine.data('sortableTable'" not in content


def test_sort_engine_consumes_fallback_chain(tmp_path: Path) -> None:
    """Every declared data-sort-fallback chain must be read by the sort engine.

    The attribute and its CSS shipped without the engine half, so the chains were
    inert. Guard the wiring, not just the declarations.
    """
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")

    # Tables still declare chains.
    assert 'data-sort-fallback="' in content
    # The engine parses them and applies them as tie-breakers.
    assert "dataset.sortFallback" in content
    assert "_parseSortChain" in content
    assert "_resolveSortSteps" in content
    # Tie-breaker ranks are emitted so the subscript-arrow CSS can match.
    assert "data-sort-rank" in content
    assert "_SORT_RANK_MAX" in content


def test_sort_engine_normalizes_number_type_token(tmp_path: Path) -> None:
    """Numeric columns declare data-sort-type="number"; the engine must treat it as numeric.

    The engine previously compared only against 'num', so every "number" column
    fell through to the string collator and defaulted to ascending.
    """
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")

    assert 'data-sort-type="number"' in content
    assert "_normSortType" in content
    # Both spellings normalize to the numeric path.
    assert "'num' || raw === 'number'" in content
    # The raw token is no longer compared directly against 'num'.
    assert "th.dataset.sortType || 'num'" not in content


def test_insight_blocks_use_alpine_xshow(tmp_path: Path) -> None:
    """AI insight blocks must NOT use inline display:none; template uses x-show."""
    results = [_make_model_result()]
    np_result = _make_model_result(model="test-model-np")
    np_result.mode = "without-plugin"
    results.append(np_result)
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    # Old pattern must not appear
    assert 'data-insights-mode="plugin" style="display:none;"' not in content
    assert 'data-insights-mode="without-plugin" style="display:none;"' not in content
    assert "data-insights-mode=" not in content


def test_print_css_includes_vega_embed(tmp_path: Path) -> None:
    """Print CSS must target .vega-embed selectors."""
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    # Check that the print media query contains .vega-embed
    # The @media print block spans multiple lines; find the last occurrence
    # (styles are included early in the file)
    last_print_idx = content.rfind("@media print")
    assert last_print_idx != -1, "@media print not found"
    print_section = content[last_print_idx : last_print_idx + 3000]
    assert ".vega-embed" in print_section, ".vega-embed not found in @media print section"


def test_subtabs_have_aria_attributes(tmp_path: Path) -> None:
    """Sub-tab links must have role=tab and aria-selected bindings."""
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert 'role="tab"' in content
    assert ":aria-selected" in content
    assert ":tabindex" in content


def test_panel_visibility_not_blocked_by_legacy_css(tmp_path: Path) -> None:
    """Alpine x-show owns panel visibility; legacy display rules must be gone.

    The legacy `.tab-panel { display: none }` / `.tab-panel.active` pair kept every
    non-Overview panel hidden because x-show only clears its own inline style.
    """
    results = [_make_model_result()]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert ".tab-panel { display: none;" not in content
    assert ".tab-panel.active { display: block; }" not in content
    assert ".sub-panel { display: none;" not in content
    assert ".sub-panel.active { display: block; }" not in content
    # Panels are still declaratively bound and cloaked against pre-init flash
    assert "x-show=\"tab==='taxonomy'\"" in content
    assert "[x-cloak] { display: none !important; }" in content


def _visible_text(html: str) -> str:
    """Strip script payloads and attribute values, leaving rendered text."""
    import re

    stripped = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    return re.sub(r'[\w:@.-]+="[^"]*"', "", stripped)


def _panel(html: str, panel_id: str) -> str:
    start = html.index(f'id="{panel_id}"')
    return html[start : html.index("</section>", start)]


def test_no_plugin_labels_use_pill_not_bracket_text(tmp_path: Path) -> None:
    """Converted labels render the no-plugin pill, never `[no-plugin]` text.

    Scoped to the panels that were migrated to the pill. Script payloads and
    `data-*` attributes keep the full `display_key` on purpose because JS uses
    it as a lookup key, and the taxonomy failure-mode chips still carry the
    bracket suffix (tracked separately).
    """
    results = [_make_model_result()]
    np_result = _make_model_result(model="test-model-np")
    np_result.mode = "without-plugin"
    results.append(np_result)
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")
    assert ">no-plugin</span>" in content

    for panel_id in ("overview", "results", "performance", "model-selection", "model-effort"):
        visible = _visible_text(_panel(content, panel_id))
        assert "[no-plugin]" not in visible, f"bracket suffix still rendered in #{panel_id}"


def test_charts_span_text_width_consistently(tmp_path: Path) -> None:
    """Every chart wrapper spans the text column; none is pixel-capped.

    `.chart-container` previously capped at 820px and the scatter wrapper added
    its own 760px cap, so charts were narrower than the surrounding prose and
    inconsistent with each other.
    """
    import re

    # Two models: single-model reports intentionally omit the ranking chart.
    results = [_make_model_result(), _make_model_result("other-model")]
    out = tmp_path / "test.html"
    render_report(results, "compliance-report.html.j2", out)
    content = out.read_text(encoding="utf-8")

    # The shared class no longer caps chart width
    assert ".chart-container { margin: 2rem 0; position: relative; }" in content
    assert "max-width: 820px" not in content

    # Each chart lives in a .chart-container wrapper with no pixel max-width
    for chart_id in ("passRateChart", "scatter-chart", "effort-pareto-chart"):
        wrapper = re.search(
            r'<div class="chart-container"([^>]*)>\s*<div id="' + re.escape(chart_id),
            content,
        )
        assert wrapper is not None, f"{chart_id} is not inside a .chart-container"
        assert not re.search(r"max-width:\s*\d+px", wrapper.group(1)), (
            f"{chart_id} wrapper is pixel-capped"
        )


def test_chart_model_short_drops_bracket_suffix() -> None:
    """Chart labels use the `*` marker only, not `[no-plugin]*`."""
    plugin = _make_model_result()
    np_result = _make_model_result(model="test-model-np")
    np_result.mode = "without-plugin"
    data = _build_vega_chart_data([plugin, np_result], [], [])
    np_rec = next(r for r in data if r["mode"] == "without-plugin")
    assert np_rec["model_short"].endswith("*")
    assert "[no-plugin]" not in np_rec["model_short"]


# ---------------------------------------------------------------------------
# UX remediation: resilience, provenance, comparability, single-model, a11y
# ---------------------------------------------------------------------------


def test_model_result_run_date_parses_ts() -> None:
    r = _make_model_result(ts="20260825-040112")
    assert r.run_date == "2026-08-25"


def test_model_result_run_date_empty_when_no_ts() -> None:
    r = _make_model_result(ts="")
    assert r.run_date == ""


def test_extract_model_stats_captures_run_timestamp(tmp_path: Path) -> None:
    run_dir = _make_real_run_dir(tmp_path, "my-model", ts="20260825-040112")
    mr = extract_model_stats(run_dir)
    assert mr.ts == "20260825-040112"
    assert mr.run_date == "2026-08-25"


def _render(results, tmp_path: Path) -> str:
    out = tmp_path / "out.html"
    render_report(results, "compliance-report.html.j2", out)
    return out.read_text(encoding="utf-8")


def test_render_resilience_markers(tmp_path: Path) -> None:
    """Vega load failure degrades per-chart; noscript stacks all panels."""
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert "__vegaLoadFailed" in content
    assert "chart-fallback" in content
    assert "<noscript>" in content
    # Vega stays on the CDN with onerror detection
    assert 'onerror="window.__vegaLoadFailed = true"' in content


def test_render_provenance_run_date_columns(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert "Run Date" in content
    assert "2026-07-18" in content


def test_render_faceted_chart_when_both_modes(tmp_path: Path) -> None:
    results = [
        _make_model_result("model-a"),
        _make_model_result("model-b", mode="without-plugin"),
    ]
    content = _render(results, tmp_path)
    assert "const _hasBothModes = true" in content
    assert "mode_label" in content
    assert "Partitioned by evaluation mode" in content


def test_render_no_facet_single_mode(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert "const _hasBothModes = false" in content
    assert "Partitioned by evaluation mode" not in content


def test_render_runs_range_in_meta_strip(tmp_path: Path) -> None:
    results = [_make_model_result("model-a", runs=3), _make_model_result("model-b", runs=5)]
    content = _render(results, tmp_path)
    assert "runs per model: 3&ndash;5" in content


def test_render_single_run_honesty(tmp_path: Path) -> None:
    """runs=1 must never be captioned as stochastic verification."""
    results = [_make_model_result("model-a", runs=1), _make_model_result("model-b", runs=1)]
    content = _render(results, tmp_path)
    assert "single pass &mdash; no variance data" in content
    assert "Stochastic stability verification" not in content


def test_render_findings_first_kpis_and_verdict(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert "Best Compliance" in content
    assert "Worst Compliance" in content
    assert "FM-1 Fabrications" in content
    assert "Verdict" in content


def test_render_single_model_adaptation(tmp_path: Path) -> None:
    """Single-model reports drop the ranking chart and cross-model analysis."""
    content = _render([_make_model_result()], tmp_path)
    assert 'id="passRateChart"' not in content
    assert "Single-model report." in content
    assert "Cross-model comparisons are omitted" in content


def test_render_results_matrix_scroll_wrapper(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert 'class="table-wrap table-wrap--scroll"' in content
    assert ".table-wrap--scroll { max-height: 75vh; overflow: auto; }" in content
    # Print must undo the scroll cage so the full matrix paginates.
    assert ".table-wrap--scroll { max-height: none; overflow: visible; }" in content


def test_render_reduced_motion_guard(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert "prefers-reduced-motion" in content


def test_render_observations_ordered_list(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    assert '<ol class="observations-list">' in content


def test_render_nav_groups(tmp_path: Path) -> None:
    content = _render([_make_model_result(), _make_model_result("other-model")], tmp_path)
    for label in ("Findings", "Method", "Operations"):
        assert f'<span class="nav-group-label">{label}</span>' in content


def test_render_filter_mode_hash_wiring(tmp_path: Path) -> None:
    """Plugin filter pills route through setMode so the mode lands in the hash."""
    content = _render(
        [_make_model_result(), _make_model_result("other-model", mode="without-plugin")],
        tmp_path,
    )
    assert "setMode('plugin')" in content
    assert "writeHash()" in content
