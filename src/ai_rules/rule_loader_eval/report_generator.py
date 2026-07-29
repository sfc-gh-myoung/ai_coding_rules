"""Report generation for rule-loader eval results.

Discovers latest run per model, extracts statistics from summary.json and
per-fixture JSONs, and renders HTML/Markdown reports via Jinja2 templates.
"""

from __future__ import annotations

import json
import logging
import os
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
REQUIRED_TABS = [
    "overview",
    "protocol",
    "taxonomy",
    "results",
    "recommendations",
    "performance",
    "model-effort",
]

# Models with pass_rate below this threshold are excluded from efficiency / consistency
# rankings — they are not comparable on efficiency because they skip too much of the protocol.
QUALITY_THRESHOLD: float = 85.0


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
        result_dir=str(run_dir),
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
        "latency_pareto": _compute_latency_pareto(results),
        "quality_threshold": QUALITY_THRESHOLD,
    }


def _compute_latency_pareto(results: Sequence[ModelResult]) -> list[dict[str, Any]]:
    """Build per-model data for the latency-quality Pareto frontier scatter chart.

    Cost axis is wall-clock duration rather than tokens, which tells a different
    story: a model can be token-expensive yet fast (one large response) or
    token-frugal yet slow.  Frontier eligibility is gated on QUALITY_THRESHOLD
    for the same reason as the token frontier -- a model that skips the protocol
    is not fast, it is incomplete.

    Args:
        results: Ordered list of ModelResult objects.

    Returns:
        List of dicts sorted by avg_duration_s ascending, each with: model,
        avg_duration_s, pass_rate, avg_turns, on_frontier, below_threshold.
    """
    points: list[dict[str, Any]] = []
    for r in results:
        pass_pct = round(r.pass_rate * 100, 1)
        points.append(
            {
                "model": r.model,
                "avg_duration_s": round(r.duration_stats.mean_s, 1) if r.duration_stats else 0.0,
                "pass_rate": pass_pct,
                "avg_turns": round(r.turn_stats.mean, 1) if r.turn_stats else 0.0,
                "on_frontier": False,
                "below_threshold": pass_pct < QUALITY_THRESHOLD,
            }
        )

    eligible = [p for p in points if p["avg_duration_s"] > 0 and not p["below_threshold"]]
    for candidate in eligible:
        dominated = any(
            other["pass_rate"] >= candidate["pass_rate"]
            and other["avg_duration_s"] <= candidate["avg_duration_s"]
            and other["model"] != candidate["model"]
            for other in eligible
        )
        if not dominated:
            candidate["on_frontier"] = True

    return sorted(points, key=lambda x: x["avg_duration_s"])


def _build_fixtures_data(results: Sequence[ModelResult]) -> list[dict[str, str]]:
    """Build an ordered list of {name, tier} for all known fixtures.

    Collects fixture IDs from per_fixture across all models, assigns tier from
    name prefix, and sorts by tier order then name.

    Args:
        results: Model results containing per_fixture mappings.

    Returns:
        List of dicts with ``name`` and ``tier`` keys, sorted tier-first.
    """
    seen: set[str] = set()
    for r in results:
        seen.update(r.per_fixture.keys())

    fixtures = [{"name": n, "tier": _fixture_tier(n)} for n in sorted(seen)]
    fixtures.sort(key=lambda f: (_TIER_ORDER.get(f["tier"], 99), f["name"]))
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


_FAILURE_MODES = [
    "FM-1 Declared-but-not-read",
    "FM-2 Hallucinated Metadata",
    "FM-3 Tool Substitution",
    "FM-4 Under-Matching",
    "FM-5 Stochastic Instability",
    "FM-6 Over-Eager Loading",
    "FM-7 Protocol Shape Divergence",
]


def _fixture_tier(name: str) -> str:
    """Return tier prefix (simple / medium / complex / new) for fixture sort ordering."""
    for prefix in ("simple", "medium", "complex"):
        if name.startswith(prefix + "-"):
            return prefix
    return "new"


_TIER_ORDER: dict[str, int] = {"simple": 0, "medium": 1, "complex": 2, "new": 3}


def _build_failure_mode_data(results: Sequence[ModelResult]) -> dict[str, Any]:
    """Build failure mode heatmap data from per-fixture results.

    Scans fixture JSONs for each model to count occurrences of each failure mode.

    Returns:
        Dict with 'models' (list of model names), 'modes' (list of FM names),
        and 'counts' (model x mode matrix of occurrence counts).
    """
    models = [r.model for r in results]
    # model -> mode -> count
    mode_counts: dict[str, dict[str, int]] = {m: dict.fromkeys(_FAILURE_MODES, 0) for m in models}

    for r in results:
        # Track per-fixture pass/fail for stochastic instability detection
        fixture_outcomes: dict[str, list[bool]] = {}

        result_dir = Path(r.result_dir)
        if not result_dir.exists():
            result_dir = _find_result_dir(result_dir.name)
        if not result_dir:
            continue

        for fx_path in _collect_fixture_jsons(result_dir):
            try:
                fx = json.loads(fx_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            fixture_id = fx.get("fixture_id", fx_path.stem)
            passed = fx.get("passed", True)
            fixture_outcomes.setdefault(fixture_id, []).append(passed)

            sr = fx.get("signal_report", {})

            # FM-1: cited_without_read
            if sr.get("cited_without_read"):
                mode_counts[r.model][_FAILURE_MODES[0]] += 1

            # FM-2: citation drifts
            if fx.get("citation_drifts"):
                mode_counts[r.model][_FAILURE_MODES[1]] += 1

            # FM-3: tool substitution (bash reads detected but not read_file)
            notes = fx.get("notes", ())
            if isinstance(notes, (list, tuple)):
                bash_reads = [n for n in notes if isinstance(n, str) and "BashRead:" in n]
                if bash_reads:
                    mode_counts[r.model][_FAILURE_MODES[2]] += 1

            # FM-4: under-matching (missing required rules)
            match = fx.get("match", {})
            if match.get("missing_required") or match.get("missing_dependencies"):
                mode_counts[r.model][_FAILURE_MODES[3]] += 1

            # FM-6: over-eager loading
            if match.get("extra_loaded"):
                mode_counts[r.model][_FAILURE_MODES[5]] += 1

            # FM-7: protocol shape divergence
            if fx.get("output_violations"):
                mode_counts[r.model][_FAILURE_MODES[6]] += 1

        # FM-5: stochastic instability (fixture with mixed pass/fail across runs)
        for _fid, outcomes in fixture_outcomes.items():
            if len(outcomes) > 1 and any(outcomes) and not all(outcomes):
                mode_counts[r.model][_FAILURE_MODES[4]] += 1

    counts = [[mode_counts[m][fm] for fm in _FAILURE_MODES] for m in models]
    return {
        "models": models,
        "modes": _FAILURE_MODES,
        "counts": counts,
    }


def _compute_metric_stats(values: list[float]) -> dict[str, float]:
    """Return {"min_val": ..., "avg_val": ..., "max_val": ...}; all-zero when list is empty.

    Keys min_val / avg_val / max_val are accessed in JavaScript as stats.min_val etc.
    after Jinja2 tojson serialization.
    """
    if not values:
        return {"min_val": 0.0, "avg_val": 0.0, "max_val": 0.0}
    return {
        "min_val": round(min(values), 3),
        "avg_val": round(statistics.mean(values), 3),
        "max_val": round(max(values), 3),
    }


def _collect_per_fixture_effort(
    run_dir: Path,
) -> dict[str, dict[str, list[float]]]:
    """Collect raw metric values grouped by fixture_id across all passes.

    Skips fixtures with result='error'. Missing metric fields are silently
    omitted (treated as if the run produced no value for that metric).

    Returns:
        {fixture_id: {"input_tokens": [...], "output_tokens": [...],
                      "elapsed_s": [...], "turns": [...]}}
    """
    per_fixture: dict[str, dict[str, list[float]]] = {}

    for fx_path in _collect_fixture_jsons(run_dir):
        try:
            fx: dict[str, Any] = json.loads(fx_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log_warning(f"Could not read fixture file {fx_path}: {exc}")
            continue

        if fx.get("result") == "error":
            continue

        fixture_id: str = fx.get("fixture_id", fx_path.stem)
        if fixture_id not in per_fixture:
            per_fixture[fixture_id] = {
                "input_tokens": [],
                "output_tokens": [],
                "elapsed_s": [],
                "turns": [],
            }

        bucket = per_fixture[fixture_id]

        it = fx.get("input_tokens")
        if it is not None and float(it) > 0:
            bucket["input_tokens"].append(float(it))

        ot = fx.get("output_tokens")
        if ot is not None and float(ot) > 0:
            bucket["output_tokens"].append(float(ot))

        dur = fx.get("duration_ms")
        if dur is not None and float(dur) > 0:
            bucket["elapsed_s"].append(float(dur) / 1000.0)

        trn = fx.get("turns")
        if trn is not None and float(trn) > 0:
            bucket["turns"].append(float(trn))

    return per_fixture


def _compute_pareto_data(
    results: Sequence[ModelResult],
    aggregate_by_model: dict[str, dict[str, dict[str, float]]],
    pass_rates: dict[str, float],
) -> list[dict[str, Any]]:
    """Build per-model data for the cost-quality Pareto frontier scatter chart.

    Frontier eligibility is gated on QUALITY_THRESHOLD: a model that skips too
    much of the protocol is not a rational choice at any price, so it cannot be
    "Pareto optimal" for this benchmark.  Among eligible models, a model is on
    the frontier if no other eligible model has BOTH higher pass_rate AND lower
    avg_total_tokens.

    Returns:
        List of dicts sorted by avg_total_tokens ascending, each with:
        model, avg_total_tokens, accuracy_adjusted_tokens, pass_rate,
        on_frontier, below_threshold.
    """
    points: list[dict[str, Any]] = []
    for r in results:
        m = r.model
        it = aggregate_by_model.get(m, {}).get("input_tokens", {})
        ot = aggregate_by_model.get(m, {}).get("output_tokens", {})
        avg_total = (it.get("avg_val", 0) or 0) + (ot.get("avg_val", 0) or 0)
        pass_pct = pass_rates.get(m, 0.0)
        pass_frac = max(pass_pct / 100.0, 0.01)
        adjusted = round(avg_total / pass_frac) if avg_total else 0
        points.append(
            {
                "model": m,
                "avg_total_tokens": round(avg_total),
                "accuracy_adjusted_tokens": adjusted,
                "pass_rate": pass_pct,
                "on_frontier": False,
                "below_threshold": pass_pct < QUALITY_THRESHOLD,
            }
        )

    # Frontier is computed ONLY among models meeting the quality threshold.
    # Including a sub-threshold model would mark it "optimal" purely for being
    # cheap, contradicting the threshold-gating methodology.
    eligible = [p for p in points if p["avg_total_tokens"] > 0 and not p["below_threshold"]]
    for candidate in eligible:
        dominated = any(
            other["pass_rate"] >= candidate["pass_rate"]
            and other["avg_total_tokens"] <= candidate["avg_total_tokens"]
            and other["model"] != candidate["model"]
            for other in eligible
        )
        if not dominated:
            candidate["on_frontier"] = True

    return sorted(points, key=lambda x: x["avg_total_tokens"])


def _build_effort_insights(
    aggregate_by_model: dict[str, dict[str, dict[str, float]]],
    connection_name: str | None,
    pass_rates: dict[str, float] | None = None,
    pareto_data: list[dict[str, Any]] | None = None,
    reliability_data: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Call AI_COMPLETE (claude-sonnet-4-5) for model efficiency analysis.

    Efficiency rankings are accuracy-adjusted: a model with lower pass rate
    requires more re-runs to produce one correct result, so its effective cost
    is avg_total_tokens / pass_rate rather than raw token count.  Pareto
    frontier membership and stochastic reliability (token CV, flake rate) are
    included in the context so the AI can reflect them in observations.

    Returns a parsed dict carrying ``efficiency_ranking``, ``consistency_ranking``,
    ``most_efficient_model``, ``least_efficient_model``, ``most_consistent_model``,
    ``key_observations`` and ``summary``; or None on any failure — including
    Snowflake connector errors (DatabaseError, OperationalError, ProgrammingError)
    and JSON parse errors. No ``response_schema`` is sent: AI_COMPLETE returns NULL
    for a nested schema of this shape, so the response is validated after parsing
    instead. Failures are non-fatal: the report renders with the degradation
    callout instead of insights.
    """
    from ai_rules.cortex.client import complete  # local import; no circular dep risk

    _pass_rates = pass_rates or {}
    _pareto_map = {p["model"]: p for p in (pareto_data or [])}
    _rel_map = reliability_data or {}

    context_lines = []
    for model, metrics in aggregate_by_model.items():
        it = metrics.get("input_tokens", {})
        ot = metrics.get("output_tokens", {})
        el = metrics.get("elapsed_s", {})
        tu = metrics.get("turns", {})
        pass_pct = _pass_rates.get(model, 100.0)
        pass_frac = max(pass_pct / 100.0, 0.01)
        avg_total = (it.get("avg_val", 0) or 0) + (ot.get("avg_val", 0) or 0)
        adjusted = round(avg_total / pass_frac) if avg_total else 0
        on_frontier = _pareto_map.get(model, {}).get("on_frontier", False)
        rel = _rel_map.get(model, {})
        token_cv = rel.get("token_cv", 0.0)
        flake_rate = rel.get("flake_rate", 0.0)
        flaky_count = rel.get("flaky_count", 0)
        context_lines.append(
            f"  {model}: pass_rate={pass_pct:.1f}%, "
            f"accuracy_adjusted_tokens={adjusted}, "
            f"pareto_frontier={'YES' if on_frontier else 'no'}, "
            f"token_cv={token_cv:.3f} (run-to-run token predictability; lower=better), "
            f"flake_rate={flake_rate:.3f} (fraction of fixtures with inconsistent pass/fail; {flaky_count} fixtures), "
            f"input_tokens(avg={it.get('avg_val', 0):.0f}), "
            f"output_tokens(avg={ot.get('avg_val', 0):.0f}), "
            f"elapsed_s(avg={el.get('avg_val', 0):.1f}), "
            f"turns(avg={tu.get('avg_val', 0):.1f})"
        )

    prompt = (
        "You are analyzing the computational efficiency of AI models on a rule-loading protocol "
        "compliance benchmark. Each model processed the same test fixtures multiple times.\n\n"
        "METRIC DEFINITIONS:\n"
        "- accuracy_adjusted_tokens = avg_total_tokens / pass_rate: the real cost per successful run. "
        "A model at 60% pass rate needs ~1.67 attempts per success — rank by this, not raw tokens.\n"
        "- pareto_frontier=YES: no other model is BOTH cheaper AND more accurate. These are the only "
        "rational choices when optimizing for cost-quality trade-off.\n"
        "- token_cv (coefficient of variation): std_dev/mean of token usage across runs. "
        "CV < 0.1 = highly predictable, 0.1-0.25 = acceptable, > 0.25 = variable/unpredictable.\n"
        "- flake_rate: fraction of test fixtures where the model's pass/fail outcome varied across runs. "
        "High flake rate = unreliable protocol adherence even when the model 'mostly' passes.\n\n"
        "Per-model data:\n\n"
        + "\n".join(context_lines)
        + "\n\nRespond with ONLY a valid JSON object (no markdown, no explanation) using exactly these keys:\n"
        "{\n"
        '  "most_efficient_model": "<model with lowest accuracy_adjusted_tokens>",\n'
        '  "least_efficient_model": "<model with highest accuracy_adjusted_tokens>",\n'
        '  "most_consistent_model": "<model with lowest token_cv AND lowest flake_rate>",\n'
        '  "efficiency_ranking": ["<model>", ...],\n'
        '  "consistency_ranking": ["<model>", ...],\n'
        '  "key_observations": [{"model": "<name>", "observation": "<1-2 sentences>"}, ...],\n'
        '  "summary": "<2-3 sentences covering: which models are on the Pareto frontier and why, '
        'the accuracy-adjusted cost leaders, and which models have the most reliable/consistent behavior>"\n'
        "}\n\n"
        "efficiency_ranking: sort ascending by accuracy_adjusted_tokens (most efficient first). "
        "consistency_ranking: sort ascending by combined token_cv + flake_rate signal "
        "(most predictable behavior first — factor in BOTH token variability AND protocol flakiness). "
        "Include every model in both ranking arrays. "
        "In key_observations, mention pareto frontier status, token CV tier, and flake rate "
        "where notable. Flag any model where raw token efficiency is misleading due to low pass_rate."
    )

    try:
        response = complete(
            prompt,
            model="claude-sonnet-4-5",
            connection_name=connection_name,
            max_tokens=2000,
        )
        text = (response.text or "").strip()
        # Snowflake AI_COMPLETE (no response_schema) double-encodes the content:
        # the SQL column is a JSON-encoded string literal, so a first json.loads()
        # unwraps it to a Python str.  Strip code fences, then parse as JSON.
        parsed: Any = json.loads(text)
        if isinstance(parsed, str):
            inner = parsed.strip()
            if inner.startswith("```"):
                inner = inner.split("```", 2)[1]
                if inner.startswith("json"):
                    inner = inner[4:]
                inner = inner.strip()
            parsed = json.loads(inner)
        if not isinstance(parsed, dict):
            log_warning(f"AI_COMPLETE effort insights: expected dict, got {type(parsed).__name__}")
            return None
        if not parsed.get("efficiency_ranking") or not parsed.get("summary"):
            log_warning(
                "AI_COMPLETE effort insights: response missing required fields "
                f"(keys present: {list(parsed.keys())})"
            )
            return None
        return parsed
    except Exception as exc:  # broad catch: connector errors are non-critical for report generation
        log_warning(f"AI_COMPLETE effort insights failed: {exc}")
        return None


def _build_effort_data(
    results: Sequence[ModelResult],
    connection_name: str | None = None,
) -> dict[str, Any]:
    """Build the effort_data template variable for the Model Effort tab."""
    _METRICS = ("input_tokens", "output_tokens", "elapsed_s", "turns")

    raw: dict[str, dict[str, dict[str, list[float]]]] = {}
    all_fixture_ids: set[str] = set()

    for r in results:
        result_dir = Path(r.result_dir)
        if not result_dir.exists():
            resolved = _find_result_dir(result_dir.name)
            if resolved is None:
                log_warning(
                    f"Result directory not found for {r.model!r} "
                    f"({result_dir.name}); effort data for this model will be all-zero"
                )
            result_dir = resolved or result_dir
        per_fx = _collect_per_fixture_effort(result_dir)
        raw[r.model] = per_fx
        all_fixture_ids.update(per_fx.keys())

    sorted_fixture_ids = sorted(
        all_fixture_ids,
        key=lambda n: (_TIER_ORDER.get(_fixture_tier(n), 99), n),
    )

    agg_raw: dict[str, dict[str, list[float]]] = {
        r.model: {m: [] for m in _METRICS} for r in results
    }
    by_fixture: dict[str, dict[str, dict[str, dict[str, float]]]] = {}

    for fixture_id in sorted_fixture_ids:
        by_fixture[fixture_id] = {}
        for r in results:
            fx_data = raw.get(r.model, {}).get(fixture_id, {})
            model_entry: dict[str, dict[str, float]] = {}
            for metric in _METRICS:
                vals = fx_data.get(metric, [])
                model_entry[metric] = _compute_metric_stats(vals)
                agg_raw[r.model][metric].extend(vals)
            by_fixture[fixture_id][r.model] = model_entry

    aggregate_by_model: dict[str, dict[str, dict[str, float]]] = {}
    for r in results:
        aggregate_by_model[r.model] = {
            metric: _compute_metric_stats(agg_raw[r.model][metric]) for metric in _METRICS
        }
    by_fixture["__aggregate__"] = aggregate_by_model

    fixture_items: list[tuple[str, str]] = [("__aggregate__", "All Fixtures (Aggregate)")]
    fixture_items += [(fid, fid) for fid in sorted_fixture_ids]

    model_pass_rates = {r.model: round(r.pass_rate * 100, 1) for r in results}

    # ── Stochastic reliability: CV of total tokens + fixture flake rate ──────
    reliability_data: dict[str, dict[str, Any]] = {}
    for r in results:
        raw_m = agg_raw.get(r.model, {})
        in_vals = raw_m.get("input_tokens", [])
        out_vals = raw_m.get("output_tokens", [])
        paired_len = min(len(in_vals), len(out_vals))
        totals = [
            in_vals[i] + out_vals[i]
            for i in range(paired_len)
            if in_vals[i] > 0 and out_vals[i] > 0
        ]
        if len(totals) >= 2:
            mean_t = statistics.mean(totals)
            cv = round(statistics.stdev(totals) / mean_t, 3) if mean_t > 0 else 0.0
        else:
            cv = 0.0
        fixture_count = max(r.fixture_count, 1)
        flaky_count = len(r.flaky_fixtures)
        reliability_data[r.model] = {
            "token_cv": cv,
            "flaky_count": flaky_count,
            "flake_rate": round(flaky_count / fixture_count, 3),
        }

    # ── Pareto frontier ───────────────────────────────────────────────────────
    pareto_data = _compute_pareto_data(results, aggregate_by_model, model_pass_rates)

    # ── Quality threshold gating ──────────────────────────────────────────────
    above_threshold = [
        r.model for r in results if model_pass_rates.get(r.model, 0) >= QUALITY_THRESHOLD
    ]
    below_threshold = [
        r.model for r in results if model_pass_rates.get(r.model, 0) < QUALITY_THRESHOLD
    ]

    insights: dict[str, Any] | None = None
    if connection_name is not None or os.environ.get("SNOWFLAKE_CONNECTION_NAME"):
        insights = _build_effort_insights(
            aggregate_by_model,
            connection_name,
            pass_rates=model_pass_rates,
            pareto_data=pareto_data,
            reliability_data=reliability_data,
        )

    return {
        "fixtures": ["__aggregate__", *sorted_fixture_ids],
        "fixture_items": fixture_items,
        "models": [r.model for r in results],
        "pass_rates": model_pass_rates,
        "by_fixture": by_fixture,
        "pareto_data": pareto_data,
        "reliability_data": reliability_data,
        "quality_threshold": QUALITY_THRESHOLD,
        "above_threshold": above_threshold,
        "below_threshold": below_threshold,
        "insights": insights,
        "insights_available": insights is not None,
    }


def _find_result_dir(dir_name: str) -> Path | None:
    """Locate a result directory by name under the project results/ folder."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            candidate = parent / "results" / dir_name
            if candidate.exists():
                return candidate
            break
    return None


def _templates_dir() -> Path:
    """Locate the templates/reports directory relative to the package root."""
    # Walk up from this file to find pyproject.toml (project root)
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent / "templates" / "reports"
    raise FileNotFoundError("Cannot locate project root for templates")


def _load_personality_profiles(tmpl_dir: Path) -> dict[str, Any] | None:
    """Load static personality profiles from _personality_data.json if available."""
    data_path = tmpl_dir / "_personality_data.json"
    if not data_path.exists():
        return None
    try:
        return json.loads(data_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def render_report(
    results: Sequence[ModelResult],
    template_name: str,
    output_path: Path,
    *,
    connection_name: str | None = None,
) -> Path:
    """Render a single report from a Jinja2 template.

    Args:
        results: Model results to embed in the report.
        template_name: Filename of the template in templates/reports/.
        output_path: File path where the rendered report is written.
        connection_name: Snowflake connection name for AI_COMPLETE effort
            insights. ``None`` disables insights (degradation callout shown).

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
    failure_mode_data = _build_failure_mode_data(results)
    personality_profiles = _load_personality_profiles(tmpl_dir)
    effort_data = _build_effort_data(results, connection_name)
    rendered = template.render(
        results=results,
        chart_data=chart_data,
        fixtures_data=fixtures_data,
        per_fixture_data=per_fixture_data,
        failure_mode_data=failure_mode_data,
        personality_profiles=personality_profiles,
        effort_data=effort_data,
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
    *,
    connection_name: str | None = None,
) -> list[Path]:
    """Top-level orchestrator: discover, extract, render.

    Args:
        results_dir: Directory containing model run subdirectories.
        output_dir: Directory where generated reports are written.
        formats: List of formats to generate; valid values: "html", "md".
        connection_name: Snowflake connection name for AI_COMPLETE effort
            insights. ``None`` disables insights.

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
            written.append(
                render_report(model_results, tmpl_name, out_path, connection_name=connection_name)
            )
        except Exception as exc:
            log_warning(f"Failed to render {fmt!r} report: {exc}")

    return written
