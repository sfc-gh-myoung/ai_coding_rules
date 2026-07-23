"""Integration tests for the A/B comparison framework."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_rules.progressive_eval.compare import (
    ArmResult,
    ComparisonReport,
    FixtureComparison,
)
from ai_rules.progressive_eval.runner import (
    load_behavioral_fixtures,
    run_comparison,
)

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "progressive_eval"
RULES_DIR = Path(__file__).parent.parent.parent / "rules"
RULES_INDEX = RULES_DIR / "RULES_INDEX.md"


class TestBehavioralFixtureLoading:
    def test_loads_all_fixtures(self):
        if not FIXTURES_DIR.exists():
            pytest.skip("fixtures/progressive_eval not found")
        fixtures = load_behavioral_fixtures(FIXTURES_DIR)
        assert len(fixtures) == 12

    def test_fixture_has_checks(self):
        if not FIXTURES_DIR.exists():
            pytest.skip("fixtures/progressive_eval not found")
        fixtures = load_behavioral_fixtures(FIXTURES_DIR)
        for f in fixtures:
            assert len(f.behavioral_checks) > 0, f"Fixture {f.id} has no checks"

    def test_fixture_has_required_rules(self):
        if not FIXTURES_DIR.exists():
            pytest.skip("fixtures/progressive_eval not found")
        fixtures = load_behavioral_fixtures(FIXTURES_DIR)
        for f in fixtures:
            assert len(f.required_rules) > 0, f"Fixture {f.id} has no required rules"


class TestComparisonReport:
    def test_report_serialization(self):
        report = ComparisonReport(models=["test-model"], run_id="20260718T120000")
        report.fixture_results.append(
            FixtureComparison(
                fixture_id="test-1",
                model="test-model",
                arm_a=ArmResult(
                    passed=True, score=1.0, total_input_tokens=5000, total_output_tokens=1000
                ),
                arm_b=ArmResult(
                    passed=True, score=0.95, total_input_tokens=2000, total_output_tokens=900
                ),
            )
        )
        report.fixture_results.append(
            FixtureComparison(
                fixture_id="test-2",
                model="test-model",
                arm_a=ArmResult(
                    passed=True, score=1.0, total_input_tokens=8000, total_output_tokens=1500
                ),
                arm_b=ArmResult(
                    passed=False, score=0.5, total_input_tokens=3000, total_output_tokens=1200
                ),
            )
        )
        report.compute_aggregate()

        # JSON output
        json_str = report.to_json()
        data = json.loads(json_str)
        assert data["schema_version"] == "comparison-report/v1"
        assert data["run_id"] == "20260718T120000"
        assert len(data["fixture_results"]) == 2
        assert data["aggregate"]["arm_a_pass_rate"] == 1.0
        assert data["aggregate"]["arm_b_pass_rate"] == 0.5

    def test_token_reduction_calculation(self):
        comp = FixtureComparison(
            fixture_id="test",
            model="m",
            arm_a=ArmResult(
                passed=True, score=1.0, total_input_tokens=10000, total_output_tokens=0
            ),
            arm_b=ArmResult(passed=True, score=1.0, total_input_tokens=4000, total_output_tokens=0),
        )
        assert comp.token_reduction_pct == 60.0

    def test_report_write(self, tmp_path):
        report = ComparisonReport(models=["test"], run_id="20260718T120000")
        report.fixture_results.append(
            FixtureComparison(
                fixture_id="f1",
                model="test",
                arm_a=ArmResult(
                    passed=True, score=1.0, total_input_tokens=5000, total_output_tokens=500
                ),
                arm_b=ArmResult(
                    passed=True, score=0.9, total_input_tokens=2000, total_output_tokens=400
                ),
            )
        )
        report.compute_aggregate()
        json_path, md_path = report.write(tmp_path)
        assert json_path.exists()
        assert md_path.exists()
        assert "comparison-report/v1" in json_path.read_text()
        assert "Progressive vs Front-Loaded" in md_path.read_text()

    def test_markdown_summary_content(self):
        report = ComparisonReport(models=["claude-opus-4-6"], run_id="test")
        report.fixture_results.append(
            FixtureComparison(
                fixture_id="sql-dedup",
                model="claude-opus-4-6",
                arm_a=ArmResult(
                    passed=True, score=1.0, total_input_tokens=6000, total_output_tokens=800
                ),
                arm_b=ArmResult(
                    passed=True, score=1.0, total_input_tokens=2500, total_output_tokens=700
                ),
            )
        )
        report.compute_aggregate()
        md = report.to_summary_markdown()
        assert "sql-dedup" in md
        assert "claude-opus-4-6" in md
        assert "Arm A" in md


class TestComparisonRunner:
    def test_simulation_mode(self):
        if not FIXTURES_DIR.exists() or not RULES_INDEX.exists():
            pytest.skip("fixtures or rules not found")
        report = run_comparison(
            FIXTURES_DIR,
            RULES_DIR,
            RULES_INDEX,
            models=["claude-opus-4-6"],
        )
        assert len(report.fixture_results) == 12
        assert report.models == ["claude-opus-4-6"]

        agg = report.compute_aggregate()
        # In simulation mode, both arms "pass" (assumed)
        assert agg.arm_a_pass_rate == 1.0
        assert agg.arm_b_pass_rate == 1.0
        # Progressive should always have fewer tokens than front-loaded
        assert agg.mean_token_reduction_pct > 0

    def test_token_reduction_is_significant(self):
        if not FIXTURES_DIR.exists() or not RULES_INDEX.exists():
            pytest.skip("fixtures or rules not found")
        report = run_comparison(
            FIXTURES_DIR,
            RULES_DIR,
            RULES_INDEX,
            models=["claude-opus-4-6"],
        )
        agg = report.compute_aggregate()
        # The progressive architecture should show meaningful reduction
        # (micro-kernel + manifest ≪ full rules upfront)
        assert agg.mean_token_reduction_pct >= 30, (
            f"Expected ≥30% token reduction, got {agg.mean_token_reduction_pct:.1f}%"
        )

    def test_full_pipeline_write(self, tmp_path):
        if not FIXTURES_DIR.exists() or not RULES_INDEX.exists():
            pytest.skip("fixtures or rules not found")
        report = run_comparison(
            FIXTURES_DIR,
            RULES_DIR,
            RULES_INDEX,
            models=["claude-opus-4-6"],
        )
        json_path, md_path = report.write(tmp_path)
        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert data["schema_version"] == "comparison-report/v1"
        assert len(data["fixture_results"]) == 12
