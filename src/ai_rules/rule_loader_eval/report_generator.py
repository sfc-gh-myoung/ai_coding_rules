"""Report generation for rule-loader eval results.

Discovers latest run per model, extracts statistics from summary.json and
per-fixture JSONs, and renders HTML/Markdown reports via Jinja2 templates.
"""

from __future__ import annotations

import json
import logging
import re
import statistics
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ai_rules._shared.console import log_warning

logger = logging.getLogger(__name__)

# Regex: <model>_<runs>x_<YYYYMMDD-HHMMSS>
_DIR_RE = re.compile(r"^(?P<model>.+?)_(?P<runs>\d+)x_(?P<ts>\d{8}-\d{6})$")

# Tab identifiers required in HTML output (AC-3 / AC-12)
REQUIRED_TABS = ["overview", "protocol", "taxonomy", "results", "recommendations", "performance"]


@dataclass
class DurationStats:
    """Duration statistics in seconds (converted from milliseconds)."""

    mean_s: float
    median_s: float
    p95_s: float
    total_s: float


@dataclass
class TurnStats:
    """Turn count statistics."""

    mean: float
    median: float
    max: int


@dataclass
class ModelResult:
    """Aggregated statistics for one model's latest run."""

    model: str
    pass_rate: float
    fixture_count: int
    runs: int
    flaky_fixtures: list[str]
    citation_drifts: int
    duration_stats: DurationStats | None
    turn_stats: TurnStats | None
    result_dir: str

    # raw per_fixture data for template use
    per_fixture: dict[str, Any] = field(default_factory=dict)


def discover_results(results_dir: Path) -> dict[str, Path]:
    """Find the latest run directory per model.

    Args:
        results_dir: Directory containing model run subdirectories.

    Returns:
        Mapping of model name to path of its latest run directory.
    """
    candidates: dict[str, tuple[str, Path]] = {}
    for child in sorted(results_dir.iterdir()):
        if not child.is_dir():
            continue
        m = _DIR_RE.match(child.name)
        if not m:
            continue
        summary = child / "summary.json"
        if not summary.exists():
            continue
        model = m.group("model")
        # Skip 'auto' model artifacts — not a real model identifier
        if model == "auto":
            continue
        ts = m.group("ts")
        existing = candidates.get(model)
        if existing is None or ts > existing[0]:
            candidates[model] = (ts, child)
    return {model: entry[1] for model, entry in candidates.items()}


def _collect_fixture_jsons(run_dir: Path) -> list[Path]:
    """Collect per-fixture JSON files from all passes within a run directory.

    Tries the real layout (run-0N/fixtures/*.json), then plan-compatible
    pass_*/*.json, then flat *.json as a last resort.

    Args:
        run_dir: Root of one model run (contains run-01/, run-02/, ...).

    Returns:
        List of fixture JSON file paths across all passes.
    """
    # Real layout: run-0N/fixtures/*.json
    real_pattern = list(run_dir.glob("run-*/fixtures/*.json"))
    if real_pattern:
        return real_pattern

    # Plan-compatible: pass_*/*.json
    pass_pattern = [p for p in run_dir.glob("pass_*/*.json") if p.name != "summary.json"]
    if pass_pattern:
        return pass_pattern

    # Flat fallback — exclude known metadata files
    _SKIP = {"summary.json", "manifest.json", "run_meta.json"}
    return [p for p in run_dir.glob("*.json") if p.name not in _SKIP]


def extract_model_stats(run_dir: Path) -> ModelResult:
    """Parse summary.json and fixture JSONs into a ModelResult.

    Args:
        run_dir: Path to a model's run directory (contains summary.json).

    Returns:
        Populated ModelResult with aggregate and per-fixture statistics.

    Raises:
        ValueError: If summary.json is missing or has unexpected schema.
    """
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        raise ValueError(f"Missing summary.json in {run_dir}")

    summary: dict[str, Any] = json.loads(summary_path.read_text(encoding="utf-8"))
    agg = summary.get("aggregate", {})

    model_name = run_dir.name
    m = _DIR_RE.match(run_dir.name)
    if m:
        model_name = m.group("model")

    pass_rate = float(agg.get("mean_pass_rate", 0.0))
    fixture_count = int(summary.get("fixture_count", 0))
    runs = int(summary.get("runs", 0))
    flaky_fixtures: list[str] = list(agg.get("flaky_fixtures", []))
    citation_drifts = int(agg.get("total_citation_drifts", 0))
    per_fixture: dict[str, Any] = dict(summary.get("per_fixture", {}))

    # Collect duration_ms and turns from fixture JSONs across all passes
    durations_ms: list[float] = []
    turns_list: list[int] = []

    for fx_path in _collect_fixture_jsons(run_dir):
        try:
            fx: dict[str, Any] = json.loads(fx_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log_warning(f"Could not read fixture file {fx_path}: {exc}")
            continue

        result = fx.get("result")
        if result == "error":
            log_warning(f"Skipping error result in {fx_path.name}")
            continue

        dur = fx.get("duration_ms")
        if dur is None or dur <= 0:
            log_warning(f"Missing/invalid duration_ms in {fx_path.name}")
        else:
            durations_ms.append(float(dur))

        trn = fx.get("turns")
        if trn is None or trn <= 0:
            log_warning(f"Missing/invalid turns in {fx_path.name}")
        else:
            turns_list.append(int(trn))

    duration_stats: DurationStats | None = None
    if len(durations_ms) >= 2:
        durations_s = [d / 1000.0 for d in durations_ms]
        sorted_s = sorted(durations_s)
        p95_idx = max(0, int(len(sorted_s) * 0.95) - 1)
        duration_stats = DurationStats(
            mean_s=round(statistics.mean(durations_s), 1),
            median_s=round(statistics.median(durations_s), 1),
            p95_s=round(sorted_s[p95_idx], 1),
            total_s=round(sum(durations_s), 1),
        )
    elif len(durations_ms) == 1:
        val = durations_ms[0] / 1000.0
        duration_stats = DurationStats(
            mean_s=round(val, 1),
            median_s=round(val, 1),
            p95_s=round(val, 1),
            total_s=round(val, 1),
        )

    turn_stats: TurnStats | None = None
    if turns_list:
        turn_stats = TurnStats(
            mean=round(statistics.mean(turns_list), 1),
            median=round(statistics.median(turns_list), 1),
            max=max(turns_list),
        )

    return ModelResult(
        model=model_name,
        pass_rate=pass_rate,
        fixture_count=fixture_count,
        runs=runs,
        flaky_fixtures=flaky_fixtures,
        citation_drifts=citation_drifts,
        duration_stats=duration_stats,
        turn_stats=turn_stats,
        result_dir=run_dir.name,
        per_fixture=per_fixture,
    )


def _build_chart_data(results: Sequence[ModelResult]) -> dict[str, Any]:
    """Build chart.js-compatible data dict from model results.

    Args:
        results: Ordered list of ModelResult objects.

    Returns:
        Dict with labels and dataset arrays for pass_rate and duration charts.
    """
    labels = [r.model for r in results]
    pass_rates = [round(r.pass_rate * 100, 1) for r in results]
    avg_durations = [r.duration_stats.mean_s if r.duration_stats else 0.0 for r in results]
    avg_turns = [r.turn_stats.mean if r.turn_stats else 0.0 for r in results]
    return {
        "labels": labels,
        "pass_rates": pass_rates,
        "avg_durations": avg_durations,
        "avg_turns": avg_turns,
    }


def _build_fixtures_data(results: Sequence[ModelResult]) -> list[dict[str, str]]:
    """Build an ordered list of {name, tier} for all known fixtures.

    Collects fixture IDs from per_fixture across all models, assigns tier from
    name prefix, and sorts by tier order then name.

    Args:
        results: Model results containing per_fixture mappings.

    Returns:
        List of dicts with ``name`` and ``tier`` keys, sorted tier-first.
    """
    tier_order = {"simple": 0, "medium": 1, "complex": 2, "new": 3}
    seen: set[str] = set()
    for r in results:
        seen.update(r.per_fixture.keys())

    def _tier(name: str) -> str:
        for prefix in ("simple", "medium", "complex"):
            if name.startswith(prefix + "-"):
                return prefix
        return "new"

    fixtures = [{"name": n, "tier": _tier(n)} for n in sorted(seen)]
    fixtures.sort(key=lambda f: (tier_order.get(f["tier"], 99), f["name"]))
    return fixtures


def _build_per_fixture_data(results: Sequence[ModelResult]) -> dict[str, dict[str, dict[str, int]]]:
    """Build per-model per-fixture pass data for the results heatmap.

    Args:
        results: Model results containing per_fixture mappings.

    Returns:
        Nested dict: ``{model: {fixture_id: {passes, n_runs}}}``.
    """
    out: dict[str, dict[str, dict[str, int]]] = {}
    for r in results:
        model_data: dict[str, dict[str, int]] = {}
        for fixture_id, agg in r.per_fixture.items():
            passes = int(agg.get("passes", 0))
            n_runs = int(agg.get("n_runs", r.runs or 3))
            model_data[fixture_id] = {"passes": passes, "n_runs": n_runs}
        out[r.model] = model_data
    return out


def _templates_dir() -> Path:
    """Locate the templates/reports directory relative to the package root."""
    # Walk up from this file to find pyproject.toml (project root)
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent / "templates" / "reports"
    raise FileNotFoundError("Cannot locate project root for templates")


def render_report(
    results: Sequence[ModelResult],
    template_name: str,
    output_path: Path,
) -> Path:
    """Render a single report from a Jinja2 template.

    Args:
        results: Model results to embed in the report.
        template_name: Filename of the template in templates/reports/.
        output_path: File path where the rendered report is written.

    Returns:
        The output_path that was written.

    Raises:
        jinja2.TemplateNotFound: If the template file does not exist.
    """
    tmpl_dir = _templates_dir()
    env = Environment(
        loader=FileSystemLoader(str(tmpl_dir)),
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
    )
    # Disable autoescape for .md templates
    if template_name.endswith(".md.j2"):
        env = Environment(
            loader=FileSystemLoader(str(tmpl_dir)),
            autoescape=False,
            keep_trailing_newline=True,
        )

    template = env.get_template(template_name)
    chart_data = _build_chart_data(results)
    fixtures_data = _build_fixtures_data(results)
    per_fixture_data = _build_per_fixture_data(results)
    rendered = template.render(
        results=results,
        chart_data=chart_data,
        fixtures_data=fixtures_data,
        per_fixture_data=per_fixture_data,
        total_models=len(results),
        required_tabs=REQUIRED_TABS,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def generate_reports(
    results_dir: Path,
    output_dir: Path,
    formats: list[str],
) -> list[Path]:
    """Top-level orchestrator: discover, extract, render.

    Args:
        results_dir: Directory containing model run subdirectories.
        output_dir: Directory where generated reports are written.
        formats: List of formats to generate; valid values: "html", "md".

    Returns:
        List of paths for files that were successfully written.
    """
    discovered = discover_results(results_dir)
    if not discovered:
        return []

    model_results: list[ModelResult] = []
    for model, run_dir in sorted(discovered.items()):
        try:
            mr = extract_model_stats(run_dir)
            model_results.append(mr)
        except Exception as exc:
            log_warning(f"Skipping model {model!r}: {exc}")

    if not model_results:
        return []

    # Sort by pass_rate descending for consistent report ordering
    model_results.sort(key=lambda r: r.pass_rate, reverse=True)

    written: list[Path] = []
    format_map = {
        "html": ("compliance-report.html.j2", "llm-protocol-compliance-report.html"),
        "md": ("compliance-report.md.j2", "llm-protocol-compliance-report.md"),
    }
    for fmt in formats:
        if fmt not in format_map:
            log_warning(f"Unknown format {fmt!r}; skipping")
            continue
        tmpl_name, out_name = format_map[fmt]
        out_path = output_dir / out_name
        try:
            written.append(render_report(model_results, tmpl_name, out_path))
        except Exception as exc:
            log_warning(f"Failed to render {fmt!r} report: {exc}")

    return written
