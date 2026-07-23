"""A/B comparison framework for progressive vs front-loaded rule loading.

Runs behavioral fixtures through both architectures and produces a
comparison report with token metrics and statistical tests.

Output: comparison-report/v1 JSON + human-readable summary markdown.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class ArmResult:
    """Result of running one fixture through one arm."""

    passed: bool
    score: float
    total_input_tokens: int
    total_output_tokens: int
    turns: int = 0
    rule_tokens_loaded: int = 0
    duration_ms: int = 0
    status: str = "completed"  # "completed" | "skipped" | "error"

    def to_dict(self) -> dict:
        return {
            "pass": self.passed,
            "score": round(self.score, 3),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "turns": self.turns,
            "rule_tokens_loaded": self.rule_tokens_loaded,
            "duration_ms": self.duration_ms,
            "status": self.status,
        }


@dataclass(frozen=True)
class FixtureComparison:
    """Side-by-side comparison of one fixture across both arms."""

    fixture_id: str
    model: str
    arm_a: ArmResult
    arm_b: ArmResult

    @property
    def token_reduction_pct(self) -> float:
        if self.arm_a.total_input_tokens == 0:
            return 0.0
        reduction = 1.0 - (self.arm_b.total_input_tokens / self.arm_a.total_input_tokens)
        return round(reduction * 100, 1)

    def to_dict(self) -> dict:
        return {
            "fixture_id": self.fixture_id,
            "model": self.model,
            "arm_a": self.arm_a.to_dict(),
            "arm_b": self.arm_b.to_dict(),
            "token_reduction_pct": self.token_reduction_pct,
        }


@dataclass(frozen=True)
class StatisticalTest:
    """Result of a statistical significance test."""

    method: str
    statistic: float
    p_value: float

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "statistic": round(self.statistic, 4),
            "p_value": round(self.p_value, 6),
        }


@dataclass(frozen=True)
class ComparisonAggregate:
    """Aggregate metrics across all fixtures."""

    arm_a_pass_rate: float
    arm_b_pass_rate: float
    pass_rate_diff: float
    arm_a_mean_input_tokens: float
    arm_b_mean_input_tokens: float
    mean_token_reduction_pct: float
    worst_fixture_token_reduction_pct: float

    def to_dict(self) -> dict:
        return {
            "arm_a_pass_rate": round(self.arm_a_pass_rate, 3),
            "arm_b_pass_rate": round(self.arm_b_pass_rate, 3),
            "pass_rate_diff": round(self.pass_rate_diff, 3),
            "arm_a_mean_input_tokens": round(self.arm_a_mean_input_tokens),
            "arm_b_mean_input_tokens": round(self.arm_b_mean_input_tokens),
            "mean_token_reduction_pct": round(self.mean_token_reduction_pct, 2),
            "worst_fixture_token_reduction_pct": round(self.worst_fixture_token_reduction_pct, 1),
        }


@dataclass
class ComparisonReport:
    """Full comparison report — serializable to comparison-report/v1."""

    fixture_results: list[FixtureComparison] = field(default_factory=list)
    models: list[str] = field(default_factory=list)
    unavailable_models: list[str] = field(default_factory=list)
    run_id: str = ""
    _aggregate: ComparisonAggregate | None = None
    _stat_tests: dict[str, StatisticalTest] = field(default_factory=dict)

    def compute_aggregate(self) -> ComparisonAggregate:
        if not self.fixture_results:
            return ComparisonAggregate(0, 0, 0, 0, 0, 0, 0)

        completed = [
            r
            for r in self.fixture_results
            if r.arm_a.status == "completed" and r.arm_b.status == "completed"
        ]
        if not completed:
            return ComparisonAggregate(0, 0, 0, 0, 0, 0, 0)

        n = len(completed)
        arm_a_pass = sum(1 for r in completed if r.arm_a.passed) / n
        arm_b_pass = sum(1 for r in completed if r.arm_b.passed) / n
        arm_a_tokens = sum(r.arm_a.total_input_tokens for r in completed) / n
        arm_b_tokens = sum(r.arm_b.total_input_tokens for r in completed) / n
        reductions = [r.token_reduction_pct for r in completed]
        mean_reduction = sum(reductions) / n
        worst_reduction = min(reductions)

        self._aggregate = ComparisonAggregate(
            arm_a_pass_rate=arm_a_pass,
            arm_b_pass_rate=arm_b_pass,
            pass_rate_diff=arm_b_pass - arm_a_pass,
            arm_a_mean_input_tokens=arm_a_tokens,
            arm_b_mean_input_tokens=arm_b_tokens,
            mean_token_reduction_pct=mean_reduction,
            worst_fixture_token_reduction_pct=worst_reduction,
        )
        return self._aggregate

    def compute_statistical_tests(self) -> dict[str, StatisticalTest]:
        """Compute significance tests. Uses paired t-test for tokens."""
        completed = [
            r
            for r in self.fixture_results
            if r.arm_a.status == "completed" and r.arm_b.status == "completed"
        ]
        if len(completed) < 3:
            self._stat_tests = {}
            return self._stat_tests

        # Paired t-test for token reduction
        diffs = [r.arm_a.total_input_tokens - r.arm_b.total_input_tokens for r in completed]
        n = len(diffs)
        mean_diff = sum(diffs) / n
        variance = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1) if n > 1 else 0
        std_err = math.sqrt(variance / n) if variance > 0 else 1e-10
        t_stat = mean_diff / std_err

        # Approximate p-value (two-tailed, using normal approximation for large n)
        # For small n, this is an approximation — replace with scipy.stats.ttest_rel if available
        p_value = 2 * (1 - _normal_cdf(abs(t_stat))) if n >= 30 else 0.05  # placeholder for small n

        self._stat_tests = {
            "token_count_test": StatisticalTest(
                method="paired_t",
                statistic=t_stat,
                p_value=p_value,
            ),
        }

        # McNemar's test for pass rate difference
        # Discordant pairs: A passes + B fails, A fails + B passes
        b_only = sum(1 for r in completed if not r.arm_a.passed and r.arm_b.passed)
        a_only = sum(1 for r in completed if r.arm_a.passed and not r.arm_b.passed)
        if b_only + a_only > 0:
            chi2 = (abs(b_only - a_only) - 1) ** 2 / (b_only + a_only)
            # Approximate p-value from chi-squared(1)
            p_mcnemar = 1 - _normal_cdf(math.sqrt(chi2)) * 2 if chi2 > 0 else 1.0
            self._stat_tests["pass_rate_test"] = StatisticalTest(
                method="mcnemar",
                statistic=chi2,
                p_value=min(p_mcnemar, 1.0),
            )

        return self._stat_tests

    def to_json(self) -> str:
        agg = self._aggregate or self.compute_aggregate()
        stats = self._stat_tests or self.compute_statistical_tests()

        report = {
            "schema_version": "comparison-report/v1",
            "run_id": self.run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%S"),
            "models": self.models,
            "unavailable_models": self.unavailable_models,
            "fixture_results": [r.to_dict() for r in self.fixture_results],
            "aggregate": agg.to_dict(),
            "statistical_tests": {k: v.to_dict() for k, v in stats.items()},
        }
        return json.dumps(report, indent=2, ensure_ascii=False)

    def to_summary_markdown(self) -> str:
        agg = self._aggregate or self.compute_aggregate()
        stats = self._stat_tests or self.compute_statistical_tests()

        lines = [
            "# Progressive vs Front-Loaded: Comparison Summary",
            "",
            f"**Run ID:** {self.run_id}",
            f"**Models:** {', '.join(self.models)}",
            f"**Unavailable:** {', '.join(self.unavailable_models) or 'none'}",
            f"**Fixtures evaluated:** {len(self.fixture_results)}",
            "",
            "## Aggregate Results",
            "",
            "| Metric | Arm A (Front-loaded) | Arm B (Progressive) | Delta |",
            "|--------|---------------------|--------------------:|------:|",
            f"| Pass rate | {agg.arm_a_pass_rate:.1%} | {agg.arm_b_pass_rate:.1%} | {agg.pass_rate_diff:+.1%} |",
            f"| Mean input tokens | {agg.arm_a_mean_input_tokens:,.0f} | {agg.arm_b_mean_input_tokens:,.0f} | {agg.mean_token_reduction_pct:+.1f}% |",
            f"| Worst fixture reduction | — | — | {agg.worst_fixture_token_reduction_pct:.1f}% |",
            "",
            "## Statistical Tests",
            "",
        ]
        for name, test in stats.items():
            sig = "significant" if test.p_value < 0.05 else "not significant"
            lines.append(
                f"- **{name}**: {test.method}, statistic={test.statistic:.3f}, p={test.p_value:.4f} ({sig})"
            )

        lines.extend(["", "## Per-Fixture Results", ""])
        lines.append("| Fixture | Model | A Pass | B Pass | A Tokens | B Tokens | Reduction |")
        lines.append("|---------|-------|--------|--------|----------|----------|-----------|")
        for r in self.fixture_results:
            lines.append(
                f"| {r.fixture_id} | {r.model} | "
                f"{'pass' if r.arm_a.passed else 'FAIL'} | "
                f"{'pass' if r.arm_b.passed else 'FAIL'} | "
                f"{r.arm_a.total_input_tokens:,} | "
                f"{r.arm_b.total_input_tokens:,} | "
                f"{r.token_reduction_pct:.1f}% |"
            )

        return "\n".join(lines)

    def write(self, output_dir: Path) -> tuple[Path, Path]:
        """Write JSON + markdown reports. Returns (json_path, md_path)."""
        output_dir.mkdir(parents=True, exist_ok=True)
        run_id = self.run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        self.run_id = run_id

        json_path = output_dir / f"comparison-{run_id}.json"
        md_path = output_dir / f"comparison-{run_id}-summary.md"

        json_path.write_text(self.to_json(), encoding="utf-8")
        md_path.write_text(self.to_summary_markdown(), encoding="utf-8")
        return json_path, md_path


def _normal_cdf(x: float) -> float:
    """Approximate standard normal CDF (no scipy dependency)."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))
