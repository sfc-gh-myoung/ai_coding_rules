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
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ai_rules._shared.console import log_warning
from ai_rules.rule_loader_eval.engine import NON_SCORED_RESULTS
from ai_rules.rule_loader_eval.results_schemas import classify_loaded_result

logger = logging.getLogger(__name__)

# Regex: <model>_<runs>x_<YYYYMMDD-HHMMSS>
_DIR_RE = re.compile(r"^(?P<model>.+?)_(?P<runs>\d+)x_(?P<ts>\d{8}-\d{6})$")

# Tab identifiers required in HTML output (AC-3 / AC-12)
REQUIRED_TABS = [
    "overview",
    "protocol",
    "taxonomy",
    "results",
    "fixtures",
    "performance",
    "model-effort",
    "model-selection",
]

# Models with pass_rate below this threshold are excluded from efficiency / consistency
# rankings: they are not comparable on efficiency because they skip too much of the protocol.
QUALITY_THRESHOLD: float = 85.0

# AI insight model used by both _build_effort_insights and _build_overview_insights.
_AI_INSIGHT_MODEL = "claude-sonnet-4-5"

# Tier thresholds (pass_rate %) used for tier labeling in AI prompt context and any inline logic.
_TIER_THRESHOLDS = {"compliant": 95, "partial": 90, "low": 85}


def _parse_ai_json_response(text: str) -> Any:
    """Double-decode the JSON string returned by AI_COMPLETE (no response_schema).

    AI_COMPLETE wraps the response in a JSON string literal, so the first
    json.loads() unwraps it to a Python str.  If code fences are present they
    are stripped, then the inner string is parsed as JSON.  Raises on any
    parse failure; callers catch via their broad except handler.
    """
    parsed: Any = json.loads(text)
    if isinstance(parsed, str):
        inner = parsed.strip()
        if inner.startswith("```"):
            inner = inner.split("```", 2)[1]
            if inner.startswith("json"):
                inner = inner[4:]
            inner = inner.strip()
        parsed = json.loads(inner)
    return parsed


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
    mode: str = "plugin"
    ts: str = ""
    """Run timestamp (``YYYYMMDD-HHMMSS``) parsed from the run directory name."""

    @property
    def run_date(self) -> str:
        """Run date as ``YYYY-MM-DD`` for provenance columns; empty when unknown."""
        if len(self.ts) >= 8 and self.ts[:8].isdigit():
            return f"{self.ts[:4]}-{self.ts[4:6]}-{self.ts[6:8]}"
        return ""

    @property
    def display_key(self) -> str:
        """Unique label distinguishing same model across modes."""
        if self.mode and self.mode != "plugin":
            return f"{self.model} [no-plugin]"
        return self.model

    @property
    def has_usable_data(self) -> bool:
        """True if this run has meaningful data for aggregation/ranking.

        Aborted or empty runs (0 tokens, no duration, trivial fixture count)
        should be excluded from statistical comparisons and rankings.
        """
        return self.duration_stats is not None or self.turn_stats is not None

    # raw per_fixture data for template use
    per_fixture: dict[str, Any] = field(default_factory=dict)
    # Phase 6: per-fixture-run discovery-attribution category counts, keyed by
    # the reader-side result string (classify_loaded_result). Empty for
    # snapshots/runs that predate the attribution fields (all counted legacy).
    discovery: dict[str, int] = field(default_factory=dict)


def _run_dir_entry(child: Path) -> tuple[str, str, str] | None:
    """Return ``(model, mode, ts)`` when ``child`` is a valid run directory.

    Valid means: name matches ``<model>_<N>x_<timestamp>``, a ``summary.json``
    is present, and the model is not the ``auto`` artifact. Mode is read from
    ``manifest.json`` (default ``"plugin"`` for legacy runs).
    """
    if not child.is_dir():
        return None
    m = _DIR_RE.match(child.name)
    if not m:
        return None
    if not (child / "summary.json").exists():
        return None
    model = m.group("model")
    # Skip 'auto' model artifacts: not a real model identifier
    if model == "auto":
        return None
    mode = "plugin"
    manifest_path = child / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            mode = manifest.get("mode") or "plugin"
        except (json.JSONDecodeError, OSError):
            pass
    return model, mode, m.group("ts")


def _display_key(model: str, mode: str) -> str:
    """Report display key: bare model name, suffixed for without-plugin runs."""
    return model if mode == "plugin" else f"{model} [no-plugin]"


def discover_results(results_dir: Path) -> dict[str, Path]:
    """Find the latest run directory per model+mode combination.

    Args:
        results_dir: The results root whose children are
            ``<model>_<N>x_<timestamp>`` run directories. Pointing it directly
            at a single run directory is also accepted and returns that run
            alone.

    Returns:
        Mapping of display key (model or model[no-plugin]) to path of its
        latest run directory.
    """
    single = _run_dir_entry(results_dir)
    if single is not None:
        model, mode, _ts = single
        return {_display_key(model, mode): results_dir}

    # Key: (model, mode) -> (timestamp, path)
    candidates: dict[tuple[str, str], tuple[str, Path]] = {}
    for child in sorted(results_dir.iterdir()):
        entry = _run_dir_entry(child)
        if entry is None:
            continue
        model, mode, ts = entry
        key = (model, mode)
        existing = candidates.get(key)
        if existing is None or ts > existing[0]:
            candidates[key] = (ts, child)

    # Unique display keys: same model can appear twice if both modes exist
    return {_display_key(model, mode): path for (model, mode), (_, path) in candidates.items()}


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

    # Flat fallback: exclude known metadata files
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
    run_ts = ""
    m = _DIR_RE.match(run_dir.name)
    if m:
        model_name = m.group("model")
        run_ts = m.group("ts")

    pass_rate = float(agg.get("mean_pass_rate", 0.0))
    fixture_count = int(summary.get("fixture_count", 0))
    runs = int(summary.get("runs", 0))
    flaky_fixtures: list[str] = list(agg.get("flaky_fixtures", []))
    citation_drifts = int(agg.get("total_citation_drifts", 0))
    per_fixture: dict[str, Any] = dict(summary.get("per_fixture", {}))

    # Collect duration_ms and turns from fixture JSONs across all passes
    durations_ms: list[float] = []
    turns_list: list[int] = []
    discovery: Counter[str] = Counter()

    for fx_path in _collect_fixture_jsons(run_dir):
        try:
            fx: dict[str, Any] = json.loads(fx_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log_warning(f"Could not read fixture file {fx_path}: {exc}")
            continue

        # Phase 6 discovery attribution: tally every doc (including legacy/error)
        # by its reader-side result category before the error-skip below.
        discovery[classify_loaded_result(fx)] += 1

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

    # Read mode from manifest
    run_mode = "plugin"
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            run_mode = manifest_data.get("mode") or "plugin"
        except (json.JSONDecodeError, OSError):
            pass

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
        mode=run_mode,
        ts=run_ts,
        per_fixture=per_fixture,
        discovery=dict(discovery),
    )


# Result categories that mean the deterministic matcher DID recall the required
# set (manifest_recall True) vs. did NOT (Phase 6 discovery attribution).
# ``model-skipped-reads`` is recalled AND agent-compliant (the agent loaded the
# rules) - it only cited without reading, so it is model behavior, not a
# recall/compliance miss.
_RECALLED_CATEGORIES = frozenset({"pass", "agent-miss", "signal-violation", "model-skipped-reads"})
_NOT_RECALLED_CATEGORIES = frozenset({"matcher-miss", "empty-manifest"})


def _build_discovery_attribution(results: Sequence[ModelResult]) -> list[dict[str, Any]]:
    """Per-model discovery-attribution rows for the report's four sections.

    Buckets each model's fixture-run categories (from
    :func:`classify_loaded_result`) into (1) matcher recall, (2) agent
    compliance, (3) out-of-manifest recovery: labeled non-passing: and
    (4) legacy runs. Report-only: recovery-only is never credited as a pass,
    and legacy records stay out of the current pass/recall denominators.
    """
    rows: list[dict[str, Any]] = []
    for r in results:
        d = r.discovery
        recalled = sum(v for k, v in d.items() if k in _RECALLED_CATEGORIES)
        not_recalled = sum(v for k, v in d.items() if k in _NOT_RECALLED_CATEGORIES)
        rows.append(
            {
                "model": r.model,
                "mode": r.mode or "plugin",
                "total": sum(d.values()),
                "matcher_recall": {"recalled": recalled, "not_recalled": not_recalled},
                "agent_compliance": {
                    "complied": d.get("pass", 0)
                    + d.get("signal-violation", 0)
                    + d.get("model-skipped-reads", 0),
                    "missed": d.get("agent-miss", 0),
                },
                "recovery_only": d.get("recovery-only", 0),
                "model_skipped": d.get("model-skipped-reads", 0),
                "legacy": d.get("legacy", 0),
                "errors": d.get("error", 0),
            }
        )
    return rows


def _build_chart_data(results: Sequence[ModelResult]) -> dict[str, Any]:
    """Build chart.js-compatible data dict from model results.

    Args:
        results: Ordered list of ModelResult objects.

    Returns:
        Dict with labels and dataset arrays for pass_rate and duration charts.
    """
    labels = [r.display_key for r in results]
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
                "model": r.display_key,
                "mode": r.mode or "plugin",
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
            and (
                other["pass_rate"] > candidate["pass_rate"]
                or other["avg_duration_s"] < candidate["avg_duration_s"]
            )
            and other["model"] != candidate["model"]
            for other in eligible
        )
        if not dominated:
            candidate["on_frontier"] = True

    return sorted(points, key=lambda x: x["avg_duration_s"])


def _build_fixture_catalog() -> list[dict[str, Any]]:
    """Load fixture YAML files and return a catalog for the Fixtures tab.

    Returns a list of dicts with keys: id, description, variant, prompt,
    required, forbidden, optional, triggers (dict with kw/ext/file/dir lists).
    Sorted by variant tier then id.
    """
    import yaml

    fixtures_dir = (
        Path(__file__).resolve().parent.parent.parent.parent / "fixtures" / "rule_loader_eval"
    )
    if not fixtures_dir.is_dir():
        return []

    catalog: list[dict[str, Any]] = []
    for yaml_path in sorted(fixtures_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or "id" not in data:
            continue

        expected = data.get("expected", {}) or {}
        trigger_ev = data.get("trigger_evidence", {}) or {}
        catalog.append(
            {
                "id": data["id"],
                "description": data.get("description") or "",
                "variant": data.get("variant", "simple"),
                "prompt": (data.get("prompt") or "").strip(),
                "required": [r.split("#")[0].strip() for r in (expected.get("required") or [])],
                "forbidden": [r.split("#")[0].strip() for r in (expected.get("forbidden") or [])],
                "optional": [r.split("#")[0].strip() for r in (expected.get("optional") or [])],
                "triggers": {
                    "kw": trigger_ev.get("kw") or [],
                    "ext": trigger_ev.get("ext") or [],
                    "file": trigger_ev.get("file") or [],
                    "dir": trigger_ev.get("dir") or [],
                },
            }
        )

    tier_order = {"simple": 0, "medium": 1, "complex": 2}
    catalog.sort(key=lambda f: (tier_order.get(f["variant"], 99), f["id"]))
    return catalog


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
        out[r.display_key] = model_data
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


# Fixture complexity tiers in presentation order: (id, label, description).
# Single source of truth -- sort order, display labels, and the prose that
# describes each tier all derive from this, so no template can claim a tier the
# fixture set does not contain. "medium" stays registered even though the current
# fixture set has none, so a medium-* fixture sorts and renders correctly if added.
_FIXTURE_TIERS: tuple[tuple[str, str, str], ...] = (
    (
        "simple",
        "Simple",
        "Single-domain prompts that should trigger exactly one or two rules. "
        "Low ambiguity, high determinism.",
    ),
    (
        "medium",
        "Medium",
        "Multi-domain prompts where the correct rule set is non-obvious. "
        "Tests classification accuracy without over-loading.",
    ),
    (
        "complex",
        "Complex",
        "Multi-step tasks spanning several domains with dependent rules, forbidden "
        "exclusions, and structured output requirements. Most closely reflect "
        "real-world agentic workloads.",
    ),
    (
        "new",
        "Unclassified",
        "Fixtures that do not follow the <tier>-<name> naming convention.",
    ),
)

_TIER_ORDER: dict[str, int] = {tier: idx for idx, (tier, _, _) in enumerate(_FIXTURE_TIERS)}
_TIER_LABELS: dict[str, str] = {tier: label for tier, label, _ in _FIXTURE_TIERS}
_TIER_DESCRIPTIONS: dict[str, str] = {tier: desc for tier, _, desc in _FIXTURE_TIERS}


def _build_fixture_tiers(items: Sequence[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    """Return only the tiers actually represented in ``items``, in presentation order.

    Args:
        items: Fixture records to tally.
        key: Field on each record holding the tier id (``tier`` or ``variant``).

    Returns:
        List of dicts with ``id``, ``label``, ``count``, and ``description``.
        Tiers with no fixtures are omitted so templates cannot describe them.
    """
    counts = Counter(str(item.get(key, "new")) for item in items)
    return [
        {
            "id": tier,
            "label": _TIER_LABELS[tier],
            "count": counts[tier],
            "description": _TIER_DESCRIPTIONS[tier],
        }
        for tier, _, _ in _FIXTURE_TIERS
        if counts.get(tier)
    ]


def _build_failure_mode_data(results: Sequence[ModelResult]) -> dict[str, Any]:
    """Build failure mode heatmap data from per-fixture results.

    Scans fixture JSONs for each model to count occurrences of each failure mode.

    Returns:
        Dict with 'models' (list of model names), 'model_modes' (parallel list of modes),
        'modes' (list of FM names), and 'counts' (model x mode matrix of occurrence counts).
    """
    # Use index-based tracking to handle duplicate model names across modes
    model_labels = [r.display_key for r in results]
    model_modes_local = [r.mode or "plugin" for r in results]
    # Per-index counts
    index_counts: list[dict[str, int]] = [dict.fromkeys(_FAILURE_MODES, 0) for _ in results]

    for idx, r in enumerate(results):
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
            # Exclude non-scored rows (infra errors, model-skipped-reads) from the
            # per-fixture pass/flakiness aggregation: they are neither pass nor fail.
            if fx.get("result", "") not in NON_SCORED_RESULTS:
                fixture_outcomes.setdefault(fixture_id, []).append(passed)

            sr = fx.get("signal_report", {})

            # FM-1: cited_without_read
            if sr.get("cited_without_read"):
                index_counts[idx][_FAILURE_MODES[0]] += 1

            # FM-2: citation drifts
            if fx.get("citation_drifts"):
                index_counts[idx][_FAILURE_MODES[1]] += 1

            # FM-3: tool substitution (bash reads detected but not read_file)
            notes = fx.get("notes", ())
            if isinstance(notes, (list, tuple)):
                bash_reads = [n for n in notes if isinstance(n, str) and "BashRead:" in n]
                if bash_reads:
                    index_counts[idx][_FAILURE_MODES[2]] += 1

            # FM-4: under-matching (missing required rules)
            match = fx.get("match", {})
            if match.get("missing_required") or match.get("missing_dependencies"):
                index_counts[idx][_FAILURE_MODES[3]] += 1

            # FM-6: over-eager loading
            if match.get("extra_loaded"):
                index_counts[idx][_FAILURE_MODES[5]] += 1

            # FM-7: protocol shape divergence
            if fx.get("output_violations"):
                index_counts[idx][_FAILURE_MODES[6]] += 1

        # FM-5: stochastic instability (fixture with mixed pass/fail across runs)
        for _fid, outcomes in fixture_outcomes.items():
            if len(outcomes) > 1 and any(outcomes) and not all(outcomes):
                index_counts[idx][_FAILURE_MODES[4]] += 1

    counts = [[index_counts[i][fm] for fm in _FAILURE_MODES] for i in range(len(results))]
    return {
        "models": model_labels,
        "model_modes": model_modes_local,
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
                "cache_creation_input_tokens": [],
                "cache_read_input_tokens": [],
                "output_tokens": [],
                "elapsed_s": [],
                "turns": [],
            }

        bucket = per_fixture[fixture_id]

        it = fx.get("input_tokens")
        if it is not None and float(it) > 0:
            bucket["input_tokens"].append(float(it))

        ccit = fx.get("cache_creation_input_tokens")
        if ccit is not None and float(ccit) > 0:
            bucket["cache_creation_input_tokens"].append(float(ccit))

        crit = fx.get("cache_read_input_tokens")
        if crit is not None and float(crit) > 0:
            bucket["cache_read_input_tokens"].append(float(crit))

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
        m = r.display_key
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
            and (
                other["pass_rate"] > candidate["pass_rate"]
                or other["avg_total_tokens"] < candidate["avg_total_tokens"]
            )
            and other["model"] != candidate["model"]
            for other in eligible
        )
        if not dominated:
            candidate["on_frontier"] = True

    return sorted(points, key=lambda x: x["avg_total_tokens"])


def _build_vega_chart_data(
    results: Sequence[ModelResult],
    latency_pareto: list[dict[str, Any]],
    cost_pareto: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Flat per-model records for Vega-Lite chart specs.

    One record per model/mode combination. All three charts consume this
    same dataset with different field references.
    """
    latency_lookup = {p["model"]: p for p in latency_pareto}
    cost_lookup = {p["model"]: p for p in cost_pareto}

    records = []
    for r in results:
        m = r.display_key
        # Charts cannot render the HTML no-plugin badge, so they use a trailing
        # asterisk instead of the bracketed suffix carried by display_key.
        short = m.replace(" [no-plugin]", "").replace("claude-", "").replace("openai-", "")
        if r.mode != "plugin":
            short += "*"
        lp = latency_lookup.get(m, {})
        cp = cost_lookup.get(m, {})
        below_latency = lp.get("below_threshold", False)
        below_cost = cp.get("below_threshold", False)
        records.append(
            {
                "model": m,
                "model_short": short,
                "mode": "without-plugin" if r.mode != "plugin" else "plugin",
                "run_date": r.run_date,
                "runs": r.runs,
                "pass_rate": round(r.pass_rate * 100, 1),
                "avg_duration_s": round(r.duration_stats.mean_s, 1) if r.duration_stats else 0.0,
                "avg_turns": round(r.turn_stats.mean, 1) if r.turn_stats else 0.0,
                "avg_total_tokens": cp.get("avg_total_tokens", 0),
                "below_threshold_latency": below_latency,
                "below_threshold_cost": below_cost,
                "on_frontier_latency": lp.get("on_frontier", False),
                "on_frontier_cost": cp.get("on_frontier", False),
                "category_latency": (
                    "Below threshold"
                    if below_latency
                    else "On frontier"
                    if lp.get("on_frontier")
                    else "Off frontier"
                ),
                "category_cost": (
                    "Below threshold"
                    if below_cost
                    else "On frontier"
                    if cp.get("on_frontier")
                    else "Off frontier"
                ),
            }
        )
    return records


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
    ``key_observations`` and ``summary``; or None on any failure: including
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
        "A model at 60% pass rate needs ~1.67 attempts per success: rank by this, not raw tokens.\n"
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
        "(most predictable behavior first: factor in BOTH token variability AND protocol flakiness). "
        "Include every model in both ranking arrays. "
        "In key_observations, mention pareto frontier status, token CV tier, and flake rate "
        "where notable. Flag any model where raw token efficiency is misleading due to low pass_rate."
    )

    try:
        response = complete(
            prompt,
            model=_AI_INSIGHT_MODEL,
            connection_name=connection_name,
            max_tokens=2000,
        )
        text = (response.text or "").strip()
        parsed: Any = _parse_ai_json_response(text)
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


def _build_overview_insights(
    results: Sequence[ModelResult],
    connection_name: str | None,
    failure_mode_data: dict[str, Any],
) -> list[str] | None:
    """Call AI_COMPLETE for three run-specific insight strings about the current report.

    Returns a list of exactly 3 strings on success, or None on any failure.
    Failures are non-fatal: the static "Observations" block renders without the
    "This Report" block.
    """
    from ai_rules.cortex.client import complete  # local import; no circular dep risk

    # Build compact per-model context using pass rates and tier labels.
    context_lines = []
    for r in results:
        pass_pct = r.pass_rate * 100
        if pass_pct >= _TIER_THRESHOLDS["compliant"]:
            tier = "Compliant"
        elif pass_pct >= _TIER_THRESHOLDS["partial"]:
            tier = "Partial"
        elif pass_pct >= _TIER_THRESHOLDS["low"]:
            tier = "Low"
        else:
            tier = "Non-Compliant"
        context_lines.append(
            f"  {r.model}: pass_rate={pass_pct:.1f}%, tier={tier}, "
            f"flaky_fixtures={len(r.flaky_fixtures)}"
        )

    # Append failure-mode distribution from the pre-computed failure_mode_data dict.
    # failure_mode_data["counts"] is a model-by-mode matrix; traverse with zip.
    fm_models = failure_mode_data.get("models", [])
    fm_modes = failure_mode_data.get("modes", [])
    fm_counts = failure_mode_data.get("counts", [])
    fm_lines = []
    for model, row in zip(fm_models, fm_counts, strict=False):
        mode_parts = [f"{fm_modes[i]}={row[i]}" for i in range(len(fm_modes))]
        fm_lines.append(f"  {model}: {', '.join(mode_parts)}")

    run_count = results[0].runs if results else 0
    prompt = (
        "You are analyzing a protocol compliance benchmark run. "
        f"Each model processed the same test fixtures {run_count} times.\n\n"
        "Per-model compliance summary:\n"
        + "\n".join(context_lines)
        + "\n\nFailure-mode distribution (counts per model per failure mode):\n"
        + "\n".join(fm_lines)
        + "\n\nChoose exactly three concise report-specific observations. "
        "Each may synthesize one or more signals. "
        "Focus on: current-run tier distribution, current-run outliers, "
        "and failure-mode concentration. "
        "Do NOT restate general methodology truths (e.g. variance-is-a-dimension, "
        "FM-1 danger, multiple-runs necessity). "
        "Do NOT make temporal comparisons (e.g. 'improved', 'declined', 'shifted') "
        "since no historical baseline is available.\n\n"
        "Respond with ONLY a valid JSON array of exactly 3 strings "
        "(no markdown, no explanation):\n"
        '["<observation 1>", "<observation 2>", "<observation 3>"]'
    )

    try:
        response = complete(
            prompt,
            model=_AI_INSIGHT_MODEL,
            connection_name=connection_name,
            max_tokens=1500,
        )
        text = (response.text or "").strip()
        parsed: Any = _parse_ai_json_response(text)
        if (
            not isinstance(parsed, list)
            or len(parsed) != 3
            or not all(isinstance(s, str) for s in parsed)
        ):
            log_warning(
                f"AI_COMPLETE overview insights: expected list of 3 strings, got {type(parsed).__name__}"
                f" len={len(parsed) if isinstance(parsed, list) else 'n/a'}"
            )
            return None
        return parsed
    except Exception as exc:  # broad catch: connector errors are non-critical for report generation
        log_warning(f"AI_COMPLETE overview insights failed: {exc}")
        return None


def _build_effort_data(
    results: Sequence[ModelResult],
    connection_name: str | None = None,
) -> dict[str, Any]:
    """Build the effort_data template variable for the Model Effort tab."""
    _METRICS = (
        "input_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
        "output_tokens",
        "elapsed_s",
        "turns",
    )

    raw: dict[str, dict[str, dict[str, list[float]]]] = {}
    all_fixture_ids: set[str] = set()

    for r in results:
        result_dir = Path(r.result_dir)
        if not result_dir.exists():
            resolved = _find_result_dir(result_dir.name)
            if resolved is None:
                log_warning(
                    f"Result directory not found for {r.display_key!r} "
                    f"({result_dir.name}); effort data for this model will be all-zero"
                )
            result_dir = resolved or result_dir
        per_fx = _collect_per_fixture_effort(result_dir)
        raw[r.display_key] = per_fx
        all_fixture_ids.update(per_fx.keys())

    sorted_fixture_ids = sorted(
        all_fixture_ids,
        key=lambda n: (_TIER_ORDER.get(_fixture_tier(n), 99), n),
    )

    agg_raw: dict[str, dict[str, list[float]]] = {
        r.display_key: {m: [] for m in _METRICS} for r in results
    }
    by_fixture: dict[str, dict[str, dict[str, dict[str, float]]]] = {}

    for fixture_id in sorted_fixture_ids:
        by_fixture[fixture_id] = {}
        for r in results:
            fx_data = raw.get(r.display_key, {}).get(fixture_id, {})
            model_entry: dict[str, dict[str, float]] = {}
            for metric in _METRICS:
                vals = fx_data.get(metric, [])
                model_entry[metric] = _compute_metric_stats(vals)
                agg_raw[r.display_key][metric].extend(vals)
            by_fixture[fixture_id][r.display_key] = model_entry

    aggregate_by_model: dict[str, dict[str, dict[str, float]]] = {}
    for r in results:
        aggregate_by_model[r.display_key] = {
            metric: _compute_metric_stats(agg_raw[r.display_key][metric]) for metric in _METRICS
        }
    by_fixture["__aggregate__"] = aggregate_by_model

    fixture_items: list[tuple[str, str]] = [("__aggregate__", "All Fixtures (Aggregate)")]
    fixture_items += [(fid, fid) for fid in sorted_fixture_ids]

    model_pass_rates = {r.display_key: round(r.pass_rate * 100, 1) for r in results}

    # ── Stochastic reliability: CV of total tokens + fixture flake rate ──────
    reliability_data: dict[str, dict[str, Any]] = {}
    for r in results:
        raw_m = agg_raw.get(r.display_key, {})
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
        reliability_data[r.display_key] = {
            "token_cv": cv,
            "flaky_count": flaky_count,
            "flake_rate": round(flaky_count / fixture_count, 3),
        }

    # ── Pareto frontier ───────────────────────────────────────────────────────
    pareto_data = _compute_pareto_data(results, aggregate_by_model, model_pass_rates)

    # ── Quality threshold gating ──────────────────────────────────────────────
    above_threshold = [
        r.display_key
        for r in results
        if model_pass_rates.get(r.display_key, 0) >= QUALITY_THRESHOLD and r.has_usable_data
    ]
    below_threshold = [
        r.display_key
        for r in results
        if model_pass_rates.get(r.display_key, 0) < QUALITY_THRESHOLD and r.has_usable_data
    ]
    nodata_models = [r.display_key for r in results if not r.has_usable_data]

    # Per-mode below-threshold slices so the AI Analysis "Excluded" list can follow the
    # active plugin filter. The unsuffixed below_threshold stays all-models for the Model
    # Effort tab, which is not filter-scoped.
    def _below_for(mode_results: Sequence[ModelResult]) -> list[str]:
        keys = {r.display_key for r in mode_results}
        return [k for k in below_threshold if k in keys]

    below_threshold_by_mode = {
        "all": below_threshold,
        "plugin": _below_for([r for r in results if r.mode == "plugin"]),
        "without-plugin": _below_for([r for r in results if r.mode != "plugin"]),
    }

    # ── AI Insights: 3 filtered calls (all, plugin-only, without-plugin-only) ──
    insights_all: dict[str, Any] | None = None
    insights_plugin: dict[str, Any] | None = None
    insights_noplugin: dict[str, Any] | None = None

    effective_conn = connection_name or os.environ.get("SNOWFLAKE_CONNECTION_NAME")
    if effective_conn:
        # All models
        insights_all = _build_effort_insights(
            aggregate_by_model,
            effective_conn,
            pass_rates=model_pass_rates,
            pareto_data=pareto_data,
            reliability_data=reliability_data,
        )

        # Plugin-only slice
        plugin_keys = {r.display_key for r in results if r.mode == "plugin" and r.has_usable_data}
        if len(plugin_keys) >= 2:
            insights_plugin = _build_effort_insights(
                {k: v for k, v in aggregate_by_model.items() if k in plugin_keys},
                effective_conn,
                pass_rates={k: v for k, v in model_pass_rates.items() if k in plugin_keys},
                pareto_data=[p for p in pareto_data if p["model"] in plugin_keys],
                reliability_data={k: v for k, v in reliability_data.items() if k in plugin_keys},
            )

        # Without-plugin slice
        noplugin_keys = {r.display_key for r in results if r.mode != "plugin" and r.has_usable_data}
        if len(noplugin_keys) >= 2:
            insights_noplugin = _build_effort_insights(
                {k: v for k, v in aggregate_by_model.items() if k in noplugin_keys},
                effective_conn,
                pass_rates={k: v for k, v in model_pass_rates.items() if k in noplugin_keys},
                pareto_data=[p for p in pareto_data if p["model"] in noplugin_keys],
                reliability_data={k: v for k, v in reliability_data.items() if k in noplugin_keys},
            )

    return {
        "fixtures": ["__aggregate__", *sorted_fixture_ids],
        "fixture_items": fixture_items,
        "models": [r.display_key for r in results],
        "pass_rates": model_pass_rates,
        "by_fixture": by_fixture,
        "pareto_data": pareto_data,
        "reliability_data": reliability_data,
        "quality_threshold": QUALITY_THRESHOLD,
        "above_threshold": above_threshold,
        "below_threshold": below_threshold,
        "below_threshold_by_mode": below_threshold_by_mode,
        "nodata_models": nodata_models,
        "insights": insights_all,
        "insights_all": insights_all,
        "insights_plugin": insights_plugin,
        "insights_noplugin": insights_noplugin,
        "insights_available": insights_all is not None,
    }


def _build_sovereignty_insight(
    family_comparison: list[dict[str, Any]],
    connection_name: str | None,
) -> str | None:
    """Generate a one-paragraph AI interpretation of the family comparison data.

    Returns None if no connection or on any error. The insight is labeled as
    model-generated in the template; all numbers come from Python.
    """
    if not connection_name or len(family_comparison) < 2:
        return None
    try:
        from ai_rules.cortex.client import complete

        context = "\n".join(
            f"- {f['family']}: n={f['n']}, pass={f['avg_pass']}%, "
            f"turns={f['turn_mean']} (range {f['turn_range'][0]}-{f['turn_range'][1]}), "
            f"avg_tokens={f['avg_input_tokens']}, elapsed={f['avg_elapsed_s']}s, "
            f"flaky={f['avg_flaky']}"
            for f in family_comparison
        )
        prompt = (
            "You are analyzing LLM protocol compliance benchmark results grouped by provider family. "
            "Below are the per-family aggregate statistics. Write ONE paragraph (3-4 sentences) "
            "interpreting what these numbers mean for model selection decisions. "
            "Focus on the strategic trade-off between iteration strategy and cost, "
            "NOT on declaring winners. All numbers are pre-computed; do not invent new ones.\n\n"
            f"{context}"
        )
        result = complete(prompt, model=_AI_INSIGHT_MODEL, connection_name=connection_name)
        return result.text.strip() if result else None
    except Exception:
        return None


def _classify_family(model_name: str) -> str:
    """Classify a model display_key into its provider family."""
    lower = model_name.lower()
    if "claude" in lower or "anthropic" in lower:
        return "Anthropic"
    if "gpt" in lower or "openai" in lower or "o1" in lower or "o3" in lower or "o4" in lower:
        return "OpenAI"
    if "gemini" in lower or "google" in lower:
        return "Google"
    if "glm" in lower or "zhipu" in lower:
        return "Zhipu"
    return "Other"


def _build_family_comparison(
    results: Sequence[ModelResult],
    effort_agg: dict[str, dict[str, dict[str, float]]],
) -> list[dict[str, Any]]:
    """Build per-family aggregate statistics for the Model Sovereignty tab.

    Groups models by provider family and computes deterministic stats:
    model count, avg pass rate, turn range/mean, avg input tokens, avg elapsed,
    avg flaky fixture count.
    """
    from collections import defaultdict

    families: dict[str, list[ModelResult]] = defaultdict(list)
    for r in results:
        if not r.has_usable_data:
            continue
        families[_classify_family(r.display_key)].append(r)

    family_stats: list[dict[str, Any]] = []
    # Iterate in a stable order; the final ordering is applied after the loop.
    for family, members in sorted(families.items(), key=lambda x: x[0]):
        pass_rates = [r.pass_rate * 100 for r in members]
        avg_pass = round(statistics.mean(pass_rates), 1) if pass_rates else 0.0

        # Turn stats from effort aggregate
        turn_means: list[float] = []
        input_token_means: list[float] = []
        elapsed_means: list[float] = []
        for r in members:
            agg = effort_agg.get(r.display_key, {})
            turns_data = agg.get("turns", {})
            if turns_data.get("avg_val", 0) > 0:
                turn_means.append(turns_data["avg_val"])
            inp_data = agg.get("input_tokens", {})
            if inp_data.get("avg_val", 0) > 0:
                input_token_means.append(inp_data["avg_val"])
            ela_data = agg.get("elapsed_s", {})
            if ela_data.get("avg_val", 0) > 0:
                elapsed_means.append(ela_data["avg_val"])

        flaky_counts = [len(r.flaky_fixtures) for r in members]

        family_stats.append(
            {
                "family": family,
                "n": len(members),
                "avg_pass": avg_pass,
                "turn_range": (
                    round(min(turn_means), 2) if turn_means else 0,
                    round(max(turn_means), 2) if turn_means else 0,
                ),
                "turn_mean": round(statistics.mean(turn_means), 2) if turn_means else 0,
                "avg_input_tokens": round(statistics.mean(input_token_means))
                if input_token_means
                else 0,
                "avg_elapsed_s": round(statistics.mean(elapsed_means), 1) if elapsed_means else 0,
                "avg_flaky": round(statistics.mean(flaky_counts), 1) if flaky_counts else 0,
                "models": [r.display_key for r in members],
            }
        )

    # Default order matches the table's declared sort: Avg Pass % descending. Families with
    # n<=1 are forced last because the template greys them out and says they sort last, and a
    # single run cannot characterize a provider. Family name is the final tie-break so the
    # order is deterministic rather than dependent on dict insertion.
    family_stats.sort(key=lambda f: (f["n"] <= 1, -f["avg_pass"], f["family"]))
    return family_stats


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

    template = env.get_template(template_name)

    # Inlined into the HTML so tabs/filters/tables work with no network access
    # (the Vega chart libs stay on the CDN and degrade gracefully). Vendored
    # copy documented in templates/reports/assets/README.md.
    alpine_js = (tmpl_dir / "assets" / "alpinejs-3.14.8.min.js").read_text(encoding="utf-8")

    chart_data = _build_chart_data(results)
    fixtures_data = _build_fixtures_data(results)
    # Effort data needed before vega_chart_data (pareto_data comes from effort)
    # — moved effort_data computation earlier so vega_chart_data can reference it.
    fixture_catalog = _build_fixture_catalog()
    per_fixture_data = _build_per_fixture_data(results)
    failure_mode_data = _build_failure_mode_data(results)
    effort_data = _build_effort_data(results, connection_name)

    # Split results by eval mode before per-mode aggregation depends on it.
    plugin_results = [r for r in results if r.mode == "plugin"]
    noplugin_results = [r for r in results if r.mode != "plugin"]
    has_noplugin = len(noplugin_results) > 0

    _effort_agg = effort_data.get("by_fixture", {}).get("__aggregate__", {})
    family_comparison = _build_family_comparison(results, _effort_agg)
    # Per-mode variants so the merged Model Selection tab can follow the plugin filter.
    # Keys match $store.filter.mode values exactly, so templates need no translation.
    family_comparisons = {
        "all": family_comparison,
        "plugin": _build_family_comparison(plugin_results, _effort_agg),
        "without-plugin": _build_family_comparison(noplugin_results, _effort_agg),
    }

    _sov_conn = connection_name or os.environ.get("SNOWFLAKE_CONNECTION_NAME")
    _all_keys = {r.display_key for r in results}
    sovereignty_insights: dict[str, str | None] = {"all": None}
    sovereignty_insights["all"] = _build_sovereignty_insight(family_comparison, _sov_conn)
    for _mode, _slice in (("plugin", plugin_results), ("without-plugin", noplugin_results)):
        # Model-set equality (order-independent) means the slice would produce the same
        # narrative as "all", so reuse it rather than paying for a second Cortex call.
        if {r.display_key for r in _slice} == _all_keys:
            sovereignty_insights[_mode] = sovereignty_insights["all"]
        else:
            sovereignty_insights[_mode] = _build_sovereignty_insight(
                family_comparisons[_mode], _sov_conn
            )

    discovery_attribution = _build_discovery_attribution(results)

    # Vega-Lite chart data: denormalized per-model records for all 3 chart specs.
    vega_chart_data = _build_vega_chart_data(
        results, chart_data["latency_pareto"], effort_data.get("pareto_data", [])
    )

    # Resolve effective connection for env-only configuration.
    effective_connection_name = connection_name or os.environ.get("SNOWFLAKE_CONNECTION_NAME")

    # HTML renders are intentionally non-reproducible (live AI call per render);
    # markdown renders are static-only.
    if template_name == "compliance-report.html.j2" and effective_connection_name:
        overview_insights = _build_overview_insights(
            results, effective_connection_name, failure_mode_data
        )
    else:
        overview_insights = None

    # Model-to-mode mapping for JS-side filtering of charts and tables.
    # Parallel array (same order as chart_data labels) so each index maps to its mode.
    model_modes_list = [r.mode or "plugin" for r in results]
    # Dict form still needed for table/row filtering by model name.
    # Use 'without-plugin' as canonical non-plugin mode value.
    model_modes = {
        r.display_key: ("without-plugin" if r.mode != "plugin" else "plugin") for r in results
    }
    # Provenance for tables keyed by display_key (effort table rows are
    # model-keyed, not ModelResult-keyed).
    model_run_dates = {r.display_key: r.run_date for r in results}

    # "Models" means distinct model identities, not model x plugin-mode runs. A model
    # evaluated both with and without the plugin is one model and two runs.
    total_models = len({r.model for r in results})

    # Rule-library size for the architecture diagram label. Falls back to 0 when the
    # rules directory is absent (e.g. rendering from a results-only checkout).
    rules_dir = tmpl_dir.parent.parent / "rules"
    total_rules = len(list(rules_dir.glob("*.md"))) if rules_dir.is_dir() else 0

    rendered = template.render(
        alpine_js=alpine_js,
        results=results,
        plugin_results=plugin_results,
        noplugin_results=noplugin_results,
        has_noplugin=has_noplugin,
        model_modes=model_modes,
        model_modes_list=model_modes_list,
        model_run_dates=model_run_dates,
        chart_data=chart_data,
        fixtures_data=fixtures_data,
        fixture_catalog=fixture_catalog,
        per_fixture_data=per_fixture_data,
        failure_mode_data=failure_mode_data,
        effort_data=effort_data,
        family_comparison=family_comparison,
        family_comparisons=family_comparisons,
        sovereignty_insights=sovereignty_insights,
        discovery_attribution=discovery_attribution,
        vega_chart_data=vega_chart_data,
        total_models=total_models,
        total_model_runs=len(results),
        total_rules=total_rules,
        report_date=datetime.now(UTC).strftime("%B %Y"),
        required_tabs=REQUIRED_TABS,
        overview_insights=overview_insights,
        overview_insights_available=overview_insights is not None,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def generate_reports(
    results_dir: Path,
    output_dir: Path,
    *,
    connection_name: str | None = None,
) -> list[Path]:
    """Top-level orchestrator: discover, extract, render the HTML report.

    Args:
        results_dir: Directory containing model run subdirectories.
        output_dir: Directory where the generated report is written.
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

    out_path = output_dir / "llm-protocol-compliance-report.html"
    try:
        return [
            render_report(
                model_results,
                "compliance-report.html.j2",
                out_path,
                connection_name=connection_name,
            )
        ]
    except Exception as exc:
        log_warning(f"Failed to render HTML report: {exc}")
        return []
