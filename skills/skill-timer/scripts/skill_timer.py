#!/usr/bin/env python
"""Skill Timing CLI Module.

Provides timing instrumentation for Claude Code skills.
Uses only standard library modules for maximum portability.

Usage:
    python skill_timer.py start --skill NAME --target FILE --model MODEL
    python skill_timer.py checkpoint --run-id ID --name NAME
    python skill_timer.py end --run-id ID --output-file FILE --skill NAME [--format human|json|markdown|quiet]
    python skill_timer.py analyze --skill NAME --days 30 [--format human|json|csv]
    python skill_timer.py baseline set --skill NAME --mode MODE --model MODEL
    python skill_timer.py baseline compare --run-id ID

Output Formats:
    human    - Human-readable terminal output (default)
    json     - Machine-readable JSON for CI/CD pipelines
    markdown - Markdown table for embedding in files
    quiet    - Exit code only, no output
    csv      - CSV format for spreadsheet analysis (analyze command only)

Exit Codes:
    0 - Success (within baseline or no baseline)
    1 - General error
    2 - Duration below error threshold (shortcut detected)
    3 - Duration significantly above baseline
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import secrets
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

# ============================================================================
# Configuration
# ============================================================================

ALERT_THRESHOLDS = {
    "rule-reviewer": {
        "FULL": {"short": 120, "long": 600, "error": 60},
        "FOCUSED": {"short": 60, "long": 360, "error": 30},
        "STALENESS": {"short": 30, "long": 240, "error": 15},
    },
    "plan-reviewer": {
        "FULL": {"short": 30, "long": 720, "error": 15},
    },
    "doc-reviewer": {
        "FULL": {"short": 90, "long": 480, "error": 45},
    },
    "rule-creator": {
        "default": {"short": 180, "long": 900, "error": 90},
    },
}

# Cost estimates per 1M tokens (update periodically as pricing changes)
# Last updated: 2026-04-05
# Sources: https://platform.claude.com/docs/en/about-claude/pricing
COST_PER_1M_TOKENS = {
    "claude-sonnet-45": {"input": 3.00, "output": 15.00},
    "claude-sonnet-46": {"input": 3.00, "output": 15.00},
    "claude-opus-45": {"input": 5.00, "output": 25.00},
    "claude-opus-46": {"input": 5.00, "output": 25.00},
    "claude-opus-4": {"input": 15.00, "output": 75.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "default": {"input": 5.00, "output": 15.00},
}

TTL_DAYS = 7
REGISTRY_STALE_HOURS = 24

VERSION = "2.0.0-rc1"

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_SHORTCUT_DETECTED = 2
EXIT_ABOVE_BASELINE = 3
EXIT_INSTRUMENTATION_FAILED = 4

PRICING_LAST_UPDATED = "2026-04-05"
PRICING_REVIEW_INTERVAL_DAYS = 90

# ============================================================================
# v2.0.0 Mode + Status enums + threshold/expected-dimension config
# ============================================================================

# Mode enum (full 10-value set introduced in v2.0.0).
# Each entry: counts_toward_total, allows_negative_duration, requires_positive_duration
# Modes that count toward total: their duration_seconds is summed into per-dimension total.
VALID_MODES: dict[str, dict[str, bool]] = {
    "checkpoint": {"counts": True, "neg_ok": False, "pos_required": True},
    "self-report": {"counts": True, "neg_ok": False, "pos_required": True},
    "self-report-flagged": {"counts": True, "neg_ok": False, "pos_required": True},
    "coordinator": {"counts": True, "neg_ok": False, "pos_required": True},
    "inline": {"counts": True, "neg_ok": False, "pos_required": True},
    "wrap": {"counts": True, "neg_ok": False, "pos_required": True},
    "failed": {"counts": False, "neg_ok": True, "pos_required": False},
    "validation-failed": {"counts": False, "neg_ok": True, "pos_required": False},
    "unavailable": {"counts": False, "neg_ok": True, "pos_required": False},
    "not-requested": {"counts": False, "neg_ok": True, "pos_required": False},
}

# Per-skill expected dimensions (warns if missing). Configurable via .timing-thresholds.json.
EXPECTED_DIMENSIONS: dict[str, list[str]] = {
    "plan-reviewer": [
        "executability",
        "completeness",
        "success_criteria",
        "scope",
        "dependencies",
        "decomposition",
        "context",
        "risk_awareness",
    ],
    "rule-reviewer": [
        "actionability",
        "rule_size",
        "parsability",
        "completeness",
        "consistency",
        "cross_agent",
    ],
    "doc-reviewer": [
        "accuracy",
        "clarity",
        "structure",
        "completeness",
        "consistency",
        "currency",
    ],
}

# Distribution-validator thresholds. Configurable via reviews/.timing-thresholds.json
# (loaded lazily in load_thresholds_config()).
DEFAULT_THRESHOLDS: dict[str, Any] = {
    "min_dim_seconds": {
        "plan-reviewer": 5.0,
        "rule-reviewer": 10.0,
        "doc-reviewer": 8.0,
        "_default": 5.0,
    },
    "uniformity_tolerance_pct": 0.05,  # ±5% across all dims triggers suspicion
    "uniformity_max_mean_seconds": 5.0,  # only triggers when mean dim < 5s
    "coverage_low_band": (0.10, 0.30),
    "coverage_severe_threshold": 0.10,
    "coverage_overrun_threshold": 1.20,
    "dim_total_short_seconds": 5.0,
    "dim_total_short_run_seconds": 60.0,
    "checkpoint_burst_seconds": 0.25,
    "post_review_gap_pct": 0.30,
    "clock_skew_seconds": 2.0,
    "min_evidence_bytes": 100,
}

_THRESHOLDS_CACHE: dict[str, Any] | None = None


def load_thresholds_config() -> dict[str, Any]:
    """Load distribution-validator thresholds.

    Precedence: in-memory cache > reviews/.timing-thresholds.json > DEFAULT_THRESHOLDS.
    """
    global _THRESHOLDS_CACHE
    if _THRESHOLDS_CACHE is not None:
        return _THRESHOLDS_CACHE
    cfg = json.loads(json.dumps(DEFAULT_THRESHOLDS))  # deep copy
    cfg_path = Path("reviews/.timing-thresholds.json")
    if cfg_path.exists():
        try:
            user = json.loads(cfg_path.read_text())
            if isinstance(user, dict):
                # Shallow merge top-level keys; nested dicts (min_dim_seconds) shallow-merge too.
                for k, v in user.items():
                    if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
        except Exception as e:
            print(
                f"WARNING: Could not parse reviews/.timing-thresholds.json: {e}; using defaults.",
                file=sys.stderr,
            )
    _THRESHOLDS_CACHE = cfg
    return cfg


# ============================================================================
# Utility Functions
# ============================================================================


TIMING_DATA_DIR = Path("reviews/.timing-data")


def get_timing_data_dir() -> Path:
    """Get timing data directory, creating it if needed."""
    TIMING_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return TIMING_DATA_DIR


def get_timing_file(run_id: str) -> Path:
    """Get path to in-progress timing file (project-local)."""
    return get_timing_data_dir() / f"skill-timer-{run_id}.json"


def get_completed_file(run_id: str) -> Path:
    """Get path to completed timing file."""
    return get_timing_data_dir() / f"skill-timer-{run_id}-complete.json"


def get_registry_file() -> Path:
    """Get path to agent recovery registry (project-local)."""
    return get_timing_data_dir() / "skill-timer-registry.json"


def get_baselines_file() -> Path:
    """Get path to baselines file."""
    return Path("reviews/.timing-baselines.json")


def write_timing_file(path: Path, data: dict):
    """Write timing file with optional secure permissions."""
    path.write_text(json.dumps(data, indent=2))
    # Optional: Restrict permissions for shared environments
    if os.environ.get("TIMING_SECURE_MODE") == "1":
        path.chmod(0o600)  # Owner read/write only


def generate_run_id(skill_name: str, target_file: str, model: str) -> str:
    """Generate collision-resistant run ID."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    pid = str(os.getpid())
    random_suffix = secrets.token_hex(4)
    payload = f"{skill_name}:{target_file}:{model}:{timestamp}:{pid}:{random_suffix}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration (Xm Ys)."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def format_duration_seconds(seconds: float) -> str:
    """Format seconds with 2 decimal places."""
    return f"{seconds:.2f}s"


def format_cost(cost_usd: float) -> str:
    """Format cost with 4 decimal places and $ prefix."""
    return f"${cost_usd:.4f}"


def format_tokens(count: int) -> str:
    """Format token count with thousands separator."""
    return f"{count:,}"


def format_baseline_delta(delta_percent: float) -> str:
    """Format baseline delta with sign and 1 decimal place."""
    sign = "+" if delta_percent >= 0 else ""
    return f"{sign}{delta_percent:.1f}%"


def format_checkpoint_elapsed(elapsed: float) -> str:
    """Format checkpoint elapsed time with 2 decimal places."""
    return f"{elapsed:.2f}s"


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> dict:
    """Calculate estimated cost for token usage."""
    costs = COST_PER_1M_TOKENS.get(model, COST_PER_1M_TOKENS["default"])
    estimated_cost = (input_tokens / 1_000_000) * costs["input"] + (
        output_tokens / 1_000_000
    ) * costs["output"]
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost_usd": round(estimated_cost, 4),
    }


def check_alerts(skill_name: str, mode: str, duration_sec: float) -> list:
    """Check for timing anomalies and return alerts."""
    alerts = []
    thresholds = ALERT_THRESHOLDS.get(skill_name, {}).get(
        mode, ALERT_THRESHOLDS.get(skill_name, {}).get("default", {})
    )

    if not thresholds:
        return alerts

    if duration_sec < thresholds.get("error", 0):
        alerts.append(
            {
                "type": "error_short_duration",
                "threshold_seconds": thresholds["error"],
                "actual_seconds": round(duration_sec, 2),
                "message": f"Duration {duration_sec:.1f}s is below error threshold ({thresholds['error']}s) - possible agent shortcut",
            }
        )
    elif duration_sec < thresholds.get("short", 0):
        alerts.append(
            {
                "type": "warning_short_duration",
                "threshold_seconds": thresholds["short"],
                "actual_seconds": round(duration_sec, 2),
                "message": f"Duration {duration_sec:.1f}s is below warning threshold ({thresholds['short']}s)",
            }
        )

    if duration_sec > thresholds.get("long", float("inf")):
        alerts.append(
            {
                "type": "warning_long_duration",
                "threshold_seconds": thresholds["long"],
                "actual_seconds": round(duration_sec, 2),
                "message": f"Duration {duration_sec:.1f}s exceeds warning threshold ({thresholds['long']}s)",
            }
        )

    return alerts


def compare_to_baseline(
    skill_name: str,
    mode: str,
    model: str,
    duration_sec: float,
    dimension_timings: list | None = None,
) -> dict | None:
    """Compare duration against baseline if available."""
    baselines_file = get_baselines_file()
    if not baselines_file.exists():
        return None

    try:
        baselines = json.loads(baselines_file.read_text())
        baseline = baselines.get(skill_name, {}).get(mode, {}).get(model)
        if not baseline:
            return None

        avg = baseline["avg_seconds"]
        stddev = baseline.get("stddev_seconds", avg * 0.2)
        delta = duration_sec - avg
        delta_percent = (delta / avg) * 100

        if abs(delta) <= stddev:
            status = "within_normal"
        elif abs(delta) <= 2 * stddev:
            status = "slightly_outside"
        else:
            status = "significantly_outside"

        result = {
            "baseline_avg_seconds": avg,
            "baseline_stddev_seconds": stddev,
            "delta_seconds": round(delta, 2),
            "delta_percent": round(delta_percent, 1),
            "status": status,
        }

        if dimension_timings and "dimensions" in baseline:
            dim_comparisons = []
            for dt in dimension_timings:
                dim_name = dt.get("dimension", "")
                dim_dur = dt.get("duration_seconds", 0)
                if dim_dur < 0:
                    continue
                dim_bl = baseline["dimensions"].get(dim_name)
                if not dim_bl:
                    continue
                dim_avg = dim_bl["avg_seconds"]
                dim_stddev = dim_bl.get("stddev_seconds", dim_avg * 0.2)
                dim_delta = dim_dur - dim_avg
                dim_delta_pct = dim_delta / dim_avg * 100 if dim_avg > 0 else 0.0
                if abs(dim_delta) <= dim_stddev:
                    dim_status = "within_normal"
                elif abs(dim_delta) <= 2 * dim_stddev:
                    dim_status = "slightly_outside"
                else:
                    dim_status = "significantly_outside"
                dim_comparisons.append(
                    {
                        "dimension": dim_name,
                        "current_seconds": round(dim_dur, 2),
                        "baseline_avg_seconds": dim_avg,
                        "delta_seconds": round(dim_delta, 2),
                        "delta_percent": round(dim_delta_pct, 1),
                        "status": dim_status,
                    }
                )
            if dim_comparisons:
                result["dimension_comparisons"] = dim_comparisons

        return result
    except Exception:
        return None


def cleanup_stale_files():
    """Remove stale in-progress timing files older than TTL."""
    data_dir = get_timing_data_dir()
    cutoff = time.time() - (TTL_DAYS * 24 * 60 * 60)

    for filepath in glob.glob(str(data_dir / "skill-timer-*.json")):
        fp = Path(filepath)
        if fp.name.endswith("-complete.json"):
            continue
        if fp.name == "skill-timer-registry.json":
            continue
        try:
            if fp.stat().st_mtime < cutoff:
                fp.unlink()
        except Exception:
            pass


def update_registry(skill_name: str, agent_id: str, run_id: str, target_file: str):
    """Update agent recovery registry."""
    registry_file = get_registry_file()

    try:
        registry = json.loads(registry_file.read_text()) if registry_file.exists() else {}
    except Exception:
        registry = {}

    if skill_name not in registry:
        registry[skill_name] = {}

    registry[skill_name][agent_id] = {
        "run_id": run_id,
        "started_at": datetime.now(UTC).isoformat(),
        "target_file": target_file,
    }

    registry_file.write_text(json.dumps(registry, indent=2))


def remove_from_registry(skill_name: str, agent_id: str):
    """Remove entry from agent recovery registry."""
    registry_file = get_registry_file()

    try:
        if registry_file.exists():
            registry = json.loads(registry_file.read_text())
            if skill_name in registry and agent_id in registry[skill_name]:
                del registry[skill_name][agent_id]
                if not registry[skill_name]:
                    del registry[skill_name]
                registry_file.write_text(json.dumps(registry, indent=2))
    except Exception:
        pass


def recover_run_id(skill_name: str, agent_id: str) -> str | None:
    """Attempt to recover run_id from registry."""
    registry_file = get_registry_file()

    try:
        if registry_file.exists():
            registry = json.loads(registry_file.read_text())
            return registry.get(skill_name, {}).get(agent_id, {}).get("run_id")
    except Exception:
        pass

    return None


def validate_timing_data(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate timing data against schema (runtime check)."""
    errors = []
    required_fields = [
        "run_id",
        "skill_name",
        "model",
        "start_iso",
        "end_iso",
        "duration_seconds",
        "status",
    ]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    if "run_id" in data and not re.match(r"^[a-f0-9]{16}$", data["run_id"]):
        errors.append(f"Invalid run_id format: {data['run_id']}")
    valid_statuses = [
        "completed",
        "warning",
        "error",
        "missing",
        "dimension_invalid",
        "instrumentation_failed",
    ]
    if data.get("status") not in valid_statuses:
        errors.append(f"Invalid status: {data.get('status')}")
    if "duration_seconds" in data and data["duration_seconds"] < 0:
        errors.append(f"Invalid duration: {data['duration_seconds']}")
    dim_timings = data.get("dimension_timings", [])
    if dim_timings:
        if not isinstance(dim_timings, list):
            errors.append("dimension_timings must be an array")
        else:
            for i, dt in enumerate(dim_timings):
                if not isinstance(dt, dict):
                    errors.append(f"dimension_timings[{i}] must be an object")
                    continue
                entry = cast(dict[str, Any], dt)
                if (
                    "dimension" not in entry
                    or "duration_seconds" not in entry
                    or "mode" not in entry
                ):
                    errors.append(
                        f"dimension_timings[{i}] missing required fields (need: dimension, duration_seconds, mode)"
                    )
                elif not isinstance(entry["duration_seconds"], (int, float)):
                    errors.append(f"dimension_timings[{i}] duration_seconds must be numeric")
                else:
                    mode = entry["mode"]
                    dur = entry["duration_seconds"]
                    mode_rules = VALID_MODES.get(mode)
                    if mode_rules is None:
                        errors.append(
                            f"dimension_timings[{i}] ({entry['dimension']}): "
                            f"unknown mode '{mode}' (valid: {sorted(VALID_MODES)})"
                        )
                    elif dur < -1:
                        errors.append(f"dimension_timings[{i}] has invalid duration ({dur}s)")
                    elif dur < 0 and not mode_rules["neg_ok"]:
                        errors.append(
                            f"dimension_timings[{i}] ({entry['dimension']}): "
                            f"negative duration not allowed for mode='{mode}'"
                        )
                    elif dur == 0 and mode_rules["pos_required"]:
                        errors.append(
                            f"dimension_timings[{i}] ({entry['dimension']}): "
                            "0s duration — timestamps likely fabricated or not captured"
                        )
                    if "start_epoch" in entry and "end_epoch" in entry:
                        if entry["end_epoch"] < entry["start_epoch"]:
                            errors.append(
                                f"dimension_timings[{i}] ({entry['dimension']}): "
                                "end_epoch < start_epoch"
                            )
                        elif entry["start_epoch"] == entry["end_epoch"] and dur != 0:
                            errors.append(
                                f"dimension_timings[{i}] ({entry['dimension']}): "
                                "start_epoch == end_epoch but duration_seconds != 0"
                            )
    return (len(errors) == 0, errors)


# ============================================================================
# v2.0.0 Distribution validator + work-window resolver
# ============================================================================


def _checkpoint_epoch(
    checkpoints: list[dict], name: str, start_epoch: float | None = None
) -> float | None:
    """Return wall-clock epoch of the last checkpoint with the given name, or None.

    Prefers explicit `epoch` field (v2.0.0+). Falls back to start_epoch +
    elapsed_seconds for legacy v1.5.0 fixtures lacking per-checkpoint epoch.
    """
    for cp in reversed(checkpoints):
        if cp.get("name") != name:
            continue
        if "epoch" in cp:
            try:
                return float(cp["epoch"])
            except (TypeError, ValueError):
                pass
        if start_epoch is not None and "elapsed_seconds" in cp:
            try:
                return float(start_epoch) + float(cp["elapsed_seconds"])
            except (TypeError, ValueError):
                pass
    return None


def resolve_work_window(data: dict[str, Any]) -> tuple[float, str]:
    """Compute the denominator for coverage / post-review-gap calculations.

    Falls back through (per source plan section 4.5):
      1. work_started -> work_complete
      2. skill_loaded -> finalize.pre_write (preferred)
      3. skill_loaded -> review_complete (legacy)
      4. start -> finalize.pre_write
      5. start -> review_complete
      6. start -> end
    Returns (seconds, source_label).
    """
    checkpoints = data.get("checkpoints", [])
    start_epoch = data.get("start_epoch")
    end_epoch = data.get("end_epoch")

    ws = _checkpoint_epoch(checkpoints, "work_started", start_epoch)
    wc = _checkpoint_epoch(checkpoints, "work_complete", start_epoch)
    if ws is not None and wc is not None and wc > ws:
        return (wc - ws, "work_started_to_work_complete")

    sl = _checkpoint_epoch(checkpoints, "skill_loaded", start_epoch)
    pre_write = data.get("finalize", {}).get("pre_write_epoch")
    rc = _checkpoint_epoch(checkpoints, "review_complete", start_epoch)

    if sl is not None and pre_write is not None and pre_write > sl:
        return (pre_write - sl, "skill_loaded_to_finalize_pre_write")
    if sl is not None and rc is not None and rc > sl:
        return (rc - sl, "skill_loaded_to_review_complete")
    if start_epoch is not None and pre_write is not None and pre_write > start_epoch:
        return (pre_write - start_epoch, "start_to_finalize_pre_write")
    if start_epoch is not None and rc is not None and rc > start_epoch:
        return (rc - start_epoch, "start_to_review_complete")
    if start_epoch is not None and end_epoch is not None and end_epoch > start_epoch:
        return (end_epoch - start_epoch, "start_to_end")
    return (0.0, "unavailable")


def _alert(alert_type: str, severity: str, message: str, **details: Any) -> dict[str, Any]:
    return {"type": alert_type, "severity": severity, "message": message, "details": details}


def validate_dimension_distribution(
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run the v2.0.0 distribution validator. Returns list of alert dicts.

    Honors TIMING_TEST_MODE=1 (skips floor/coverage/total/post-review checks)
    and TIMING_DISABLE_DISTRIBUTION_VALIDATOR=1 (returns []).
    """
    if os.environ.get("TIMING_DISABLE_DISTRIBUTION_VALIDATOR") == "1":
        return []

    test_mode = os.environ.get("TIMING_TEST_MODE") == "1"
    cfg = load_thresholds_config()
    alerts: list[dict[str, Any]] = []

    skill_name = data.get("skill_name", "")
    dim_timings = data.get("dimension_timings") or []
    run_total = float(data.get("duration_seconds") or 0.0)
    work_window, work_window_source = resolve_work_window(data)
    data["work_window_seconds"] = round(work_window, 2)
    data["work_window_source"] = work_window_source

    # Counted vs not-counted modes
    counted = [
        dt for dt in dim_timings if VALID_MODES.get(dt.get("mode", ""), {}).get("counts") is True
    ]
    counted_durations = [
        float(dt.get("duration_seconds", 0.0))
        for dt in counted
        if isinstance(dt.get("duration_seconds"), (int, float))
        and float(dt.get("duration_seconds", 0.0)) >= 0
    ]
    dim_total = sum(counted_durations) if counted_durations else 0.0

    # ---- duplicate_dim_checkpoints (always on) ----
    checkpoints = data.get("checkpoints", [])
    seen_dim_names: dict[str, int] = {}
    for cp in checkpoints:
        name = cp.get("name", "")
        if re.match(r"^dim_[a-z_]+_(start|end)$", name):
            seen_dim_names[name] = seen_dim_names.get(name, 0) + 1
    dups = [n for n, c in seen_dim_names.items() if c >= 2]
    if dups:
        alerts.append(
            _alert(
                "duplicate_dim_checkpoints",
                "warning",
                f"Duplicate dim_* checkpoint names: {sorted(dups)}",
                duplicates=sorted(dups),
            )
        )

    # ---- checkpoint_burst (always on) ----
    burst_threshold = float(cfg.get("checkpoint_burst_seconds", 0.25))
    burst_pairs: list[tuple[str, str, float]] = []
    last_dim_event: tuple[str, float] | None = None
    start_epoch_for_burst = data.get("start_epoch")
    for cp in checkpoints:
        name = cp.get("name", "")
        m = re.match(r"^dim_([a-z_]+)_(start|end)$", name)
        if not m:
            continue
        epoch = cp.get("epoch")
        if epoch is None and start_epoch_for_burst is not None and "elapsed_seconds" in cp:
            try:
                epoch = float(start_epoch_for_burst) + float(cp["elapsed_seconds"])
            except (TypeError, ValueError):
                epoch = None
        if epoch is None:
            continue
        try:
            ep = float(epoch)
        except (TypeError, ValueError):
            continue
        if last_dim_event is not None:
            prev_name, prev_epoch = last_dim_event
            delta = ep - prev_epoch
            if 0 <= delta < burst_threshold:
                burst_pairs.append((prev_name, name, round(delta, 4)))
        last_dim_event = (name, ep)
    if burst_pairs:
        alerts.append(
            _alert(
                "checkpoint_burst",
                "warning",
                f"{len(burst_pairs)} consecutive dim_* checkpoint(s) recorded "
                f"<{burst_threshold}s apart",
                burst_pairs=burst_pairs,
            )
        )

    # ---- missing_expected_dimension (always on) ----
    expected = (cfg.get("expected_dimensions") or {}).get(skill_name) or EXPECTED_DIMENSIONS.get(
        skill_name
    )
    if expected:
        present = {dt.get("dimension") for dt in dim_timings}
        missing = [d for d in expected if d not in present]
        if missing:
            alerts.append(
                _alert(
                    "missing_expected_dimension",
                    "warning",
                    f"Skill '{skill_name}' expected dimensions missing: {missing}",
                    missing=missing,
                    expected=expected,
                )
            )

    # ---- clock_skew (always on) ----
    skew_threshold = float(cfg.get("clock_skew_seconds", 2.0))
    if data.get("clock_source") == "monotonic":
        # Compare wall-clock end-start delta against monotonic delta if available.
        try:
            wall_delta = float(data["end_epoch"]) - float(data["start_epoch"])
            mono_delta = float(data.get("duration_seconds_monotonic", wall_delta))
            if abs(wall_delta - mono_delta) > skew_threshold:
                alerts.append(
                    _alert(
                        "clock_skew",
                        "warning",
                        f"Wall vs monotonic delta differ by "
                        f"{abs(wall_delta - mono_delta):.2f}s (>{skew_threshold}s)",
                        wall_delta=round(wall_delta, 4),
                        monotonic_delta=round(mono_delta, 4),
                    )
                )
        except (KeyError, TypeError, ValueError):
            pass

    # The remaining validators are silenced under TIMING_TEST_MODE=1.
    if test_mode or not counted_durations:
        return alerts

    # ---- dim_uniformity_suspect ----
    if len(counted_durations) >= 2:
        mean_dim = dim_total / len(counted_durations)
        if mean_dim > 0:
            uniformity_pct = float(cfg.get("uniformity_tolerance_pct", 0.05))
            uniformity_max_mean = float(cfg.get("uniformity_max_mean_seconds", 5.0))
            within = all(abs(d - mean_dim) / mean_dim <= uniformity_pct for d in counted_durations)
            if within and mean_dim < uniformity_max_mean:
                alerts.append(
                    _alert(
                        "dim_uniformity_suspect",
                        "warning",
                        f"All {len(counted_durations)} per-dimension durations are "
                        f"within \u00b1{uniformity_pct * 100:.0f}% of mean {mean_dim:.2f}s "
                        f"(< {uniformity_max_mean}s); pattern suggests batched "
                        f"checkpoint emission rather than real measurement.",
                        mean_seconds=round(mean_dim, 4),
                        tolerance_pct=uniformity_pct,
                    )
                )

    # ---- dim_floor_violation ----
    floor_map = cfg.get("min_dim_seconds", {})
    floor_default = float(floor_map.get("_default", 5.0))
    floor = float(floor_map.get(skill_name, floor_default))
    below_floor = [
        (dt.get("dimension"), float(dt.get("duration_seconds", 0.0)))
        for dt in counted
        if isinstance(dt.get("duration_seconds"), (int, float))
        and 0 <= float(dt.get("duration_seconds", 0.0)) < floor
    ]
    if below_floor:
        alerts.append(
            _alert(
                "dim_floor_violation",
                "warning",
                f"{len(below_floor)} dimension(s) below per-skill floor of "
                f"{floor:.1f}s for '{skill_name}'",
                below_floor=below_floor,
                floor_seconds=floor,
            )
        )

    # ---- coverage tiers + dim_total_short ----
    if work_window > 0 and dim_total >= 0:
        coverage = dim_total / work_window
        low_lo, low_hi = cfg.get("coverage_low_band", (0.10, 0.30))
        severe = float(cfg.get("coverage_severe_threshold", 0.10))
        overrun = float(cfg.get("coverage_overrun_threshold", 1.20))
        if coverage < severe:
            alerts.append(
                _alert(
                    "dim_coverage_severe",
                    "error",
                    f"Per-dimension total ({dim_total:.2f}s) covers only "
                    f"{coverage * 100:.1f}% of work window ({work_window:.2f}s) "
                    f"— below severe threshold {severe * 100:.0f}%",
                    coverage_ratio=round(coverage, 4),
                    work_window_seconds=round(work_window, 2),
                    dim_total_seconds=round(dim_total, 2),
                    work_window_source=work_window_source,
                )
            )
        elif low_lo <= coverage < low_hi:
            alerts.append(
                _alert(
                    "dim_coverage_low",
                    "warning",
                    f"Per-dimension total covers only {coverage * 100:.1f}% of work "
                    f"window ({work_window:.2f}s) — below recommended {low_hi * 100:.0f}%",
                    coverage_ratio=round(coverage, 4),
                    work_window_seconds=round(work_window, 2),
                )
            )
        elif coverage > overrun:
            alerts.append(
                _alert(
                    "dim_coverage_overrun",
                    "error",
                    f"Per-dimension total ({dim_total:.2f}s) exceeds work window "
                    f"({work_window:.2f}s) by {(coverage - 1) * 100:.1f}%",
                    coverage_ratio=round(coverage, 4),
                    work_window_seconds=round(work_window, 2),
                )
            )

    short_dim_total = float(cfg.get("dim_total_short_seconds", 5.0))
    short_run_total = float(cfg.get("dim_total_short_run_seconds", 60.0))
    if dim_total < short_dim_total and run_total > short_run_total:
        alerts.append(
            _alert(
                "dim_total_short",
                "warning",
                f"Per-dimension total ({dim_total:.2f}s) is below {short_dim_total:.0f}s "
                f"despite run_total={run_total:.2f}s",
                dim_total_seconds=round(dim_total, 2),
                run_total_seconds=round(run_total, 2),
            )
        )

    # ---- post_review_gap ----
    pre_write = data.get("finalize", {}).get("pre_write_epoch")
    rc = _checkpoint_epoch(checkpoints, "review_complete", data.get("start_epoch"))
    anchor = pre_write if pre_write is not None else rc
    end_epoch = data.get("end_epoch")
    if anchor is not None and end_epoch is not None and run_total > 0:
        try:
            gap = float(end_epoch) - float(anchor)
            gap_pct = gap / run_total
            limit = float(cfg.get("post_review_gap_pct", 0.30))
            if gap_pct > limit:
                alerts.append(
                    _alert(
                        "post_review_gap",
                        "warning",
                        f"{gap:.2f}s ({gap_pct * 100:.1f}% of run) elapsed after "
                        f"work-complete anchor — above {limit * 100:.0f}% limit; "
                        f"largest cost block is uninstrumented.",
                        gap_seconds=round(gap, 2),
                        gap_pct=round(gap_pct, 4),
                        anchor_source="finalize.pre_write"
                        if pre_write is not None
                        else "review_complete",
                    )
                )
        except (TypeError, ValueError):
            pass

    return alerts


def annotate_validation_status(data: dict[str, Any], alerts: list[dict[str, Any]]) -> None:
    """Stamp per-row validation_status onto each dimension_timings entry.

    valid     - mode counts and no per-row error
    warning   - mode counts but distribution alert references this dim, or self-report-flagged
    failed    - mode is failed/validation-failed
    not_requested - mode is not-requested
    unavailable   - mode is unavailable
    """
    flagged_dims: set[str] = set()
    for a in alerts:
        details = a.get("details") or {}
        for d in details.get("below_floor") or []:
            if isinstance(d, (list, tuple)) and d:
                flagged_dims.add(d[0])
        for n in details.get("missing") or []:
            flagged_dims.add(n)
    for dt in data.get("dimension_timings") or []:
        mode = dt.get("mode")
        if mode == "failed" or mode == "validation-failed":
            dt["validation_status"] = "failed"
        elif mode == "not-requested":
            dt["validation_status"] = "not_requested"
        elif mode == "unavailable":
            dt["validation_status"] = "unavailable"
        elif mode == "self-report-flagged" or dt.get("dimension") in flagged_dims:
            dt["validation_status"] = "warning"
        else:
            dt["validation_status"] = "valid"


def escalate_status(data: dict[str, Any], alerts: list[dict[str, Any]]) -> str:
    """Apply the v2.0.0 status-escalation matrix.

    completed / warning / dimension_invalid / instrumentation_failed / error
    """
    # Already-set error stays as error.
    if data.get("status") == "error":
        return "error"
    if data.get("validation_errors"):
        # Per-row schema rejection took place upstream.
        return "dimension_invalid"
    error_alerts = [a for a in alerts if a.get("severity") == "error"]
    warning_alerts = [a for a in alerts if a.get("severity") == "warning"]
    if error_alerts:
        return "instrumentation_failed"
    if len(warning_alerts) >= 3:
        return "instrumentation_failed"
    if 1 <= len(warning_alerts) <= 2:
        return "warning"
    return "completed"


def check_pricing_staleness():
    """Warn if token pricing data is stale."""
    try:
        last = datetime.strptime(PRICING_LAST_UPDATED, "%Y-%m-%d")
        if (datetime.now() - last).days > PRICING_REVIEW_INTERVAL_DAYS:
            print(
                f"WARNING: Token pricing data last updated {PRICING_LAST_UPDATED}. "
                "Consider updating COST_PER_1M_TOKENS.",
                file=sys.stderr,
            )
    except Exception:
        pass


def determine_exit_code(data: dict) -> int:
    """Determine appropriate exit code based on timing data."""
    if data.get("status") == "instrumentation_failed":
        return EXIT_INSTRUMENTATION_FAILED
    if data.get("status") == "dimension_invalid":
        return EXIT_INSTRUMENTATION_FAILED
    alerts = data.get("alerts", [])
    for alert in alerts:
        if alert.get("type") == "error_short_duration":
            return EXIT_SHORTCUT_DETECTED
        if alert.get("severity") == "error":
            return EXIT_INSTRUMENTATION_FAILED
    baseline = data.get("baseline_comparison")
    if (
        baseline
        and baseline.get("status") == "significantly_outside"
        and baseline.get("delta_percent", 0) > 0
    ):
        return EXIT_ABOVE_BASELINE
    return EXIT_SUCCESS


def print_stdout_summary(
    data: dict, checkpoints: list, tokens: dict | None, baseline: dict | None, alerts: list
):
    """Print timing summary to STDOUT in standardized human-readable format."""
    sep = "-" * 40
    print()
    print(f"TIMING: skill-timer v{VERSION}")
    print(sep)
    print(f"Run ID:      {data['run_id']}")
    print(f"Skill:       {data.get('skill_name', 'unknown')}")
    print(f"Target:      {data.get('target_file', 'unknown')}")
    print(f"Model:       {data.get('model', 'unknown')}")
    print(f"Agent:       {data.get('agent', 'unknown')}")
    print(sep)
    print(f"Start:       {data.get('start_iso', 'unknown')}")
    print(f"End:         {data.get('end_iso', 'unknown')}")
    print(
        f"Duration:    {data['duration_human']} ({format_duration_seconds(data['duration_seconds'])})"
    )
    print(f"Status:      {data.get('status', 'unknown')}")
    print(sep)

    if checkpoints:
        print("Checkpoints:")
        for cp in checkpoints:
            print(f"  {cp['name']}:  {format_checkpoint_elapsed(cp['elapsed_seconds'])}")
        print(sep)

    dim_timings = data.get("dimension_timings", [])
    if dim_timings:
        print("Per-Dimension Timing:")
        for dt in dim_timings:
            dur = dt.get("duration_seconds", 0)
            print(
                f"  {dt.get('dimension', 'unknown'):30s} {format_duration_seconds(dur):>10s}  ({dt.get('mode', '')})"
            )
        total = sum(
            d.get("duration_seconds", 0) for d in dim_timings if d.get("duration_seconds", 0) >= 0
        )
        print(f"  {'Total (dimension work)':30s} {format_duration_seconds(total):>10s}")
        print(sep)

    if tokens:
        print(
            f"Tokens:      {format_tokens(tokens['total_tokens'])} "
            f"({format_tokens(tokens['input_tokens'])} in / {format_tokens(tokens['output_tokens'])} out)"
        )
        print(f"Cost:        {format_cost(tokens['estimated_cost_usd'])}")
    else:
        print("Tokens:      N/A")
        print("Cost:        N/A")

    if baseline:
        print(
            f"Baseline:    {format_baseline_delta(baseline['delta_percent'])} vs avg "
            f"({baseline['status'].replace('_', ' ')})"
        )
    else:
        print("Baseline:    N/A")
        print(
            "    Tip: Set baseline after 5+ runs with: baseline set --skill <name> --mode <mode> --model <model>"
        )

    print(sep)

    if alerts:
        for alert in alerts:
            if "error" in alert["type"]:
                print(f"ERROR: {alert['message']}")
            else:
                print(f"WARNING: {alert['message']}")
        print(sep)

    print()


def generate_markdown_table(data: dict) -> str:
    """Generate standardized markdown timing table for file embedding."""
    checkpoints = data.get("checkpoints", [])
    tokens = data.get("tokens")
    baseline = data.get("baseline_comparison")

    cp_str = "N/A"
    if checkpoints:
        cp_parts = [
            f"{cp['name']}: {format_checkpoint_elapsed(cp['elapsed_seconds'])}"
            for cp in checkpoints
        ]
        cp_str = ", ".join(cp_parts)

    tokens_str = "N/A"
    cost_str = "N/A"
    if tokens:
        tokens_str = (
            f"{format_tokens(tokens['total_tokens'])} "
            f"({format_tokens(tokens['input_tokens'])} in / {format_tokens(tokens['output_tokens'])} out)"
        )
        cost_str = format_cost(tokens["estimated_cost_usd"])

    baseline_str = "N/A"
    if baseline:
        baseline_str = (
            f"{format_baseline_delta(baseline['delta_percent'])} vs avg "
            f"({baseline['status'].replace('_', ' ')})"
        )

    lines = [
        "## Timing Metadata",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Run ID | `{data['run_id']}` |",
        f"| Skill | {data.get('skill_name', 'unknown')} |",
        f"| Model | {data.get('model', 'unknown')} |",
        f"| Agent | {data.get('agent', 'unknown')} |",
        f"| Start (UTC) | {data.get('start_iso', 'unknown')} |",
        f"| End (UTC) | {data.get('end_iso', 'unknown')} |",
        f"| Duration | {data['duration_human']} ({format_duration_seconds(data['duration_seconds'])}) |",
        f"| Status | {data.get('status', 'unknown')} |",
        f"| Checkpoints | {cp_str} |",
        f"| Tokens | {tokens_str} |",
        f"| Cost | {cost_str} |",
        f"| Baseline | {baseline_str} |",
    ]

    dim_timings = data.get("dimension_timings", [])
    if dim_timings:
        lines.append("")
        lines.append("### Per-Dimension Timing")
        lines.append("")
        lines.append("| Dimension | Duration | Mode |")
        lines.append("|-----------|----------|------|")
        total_dim_time = 0
        for dt in dim_timings:
            dur = dt.get("duration_seconds", 0)
            if dur >= 0:
                total_dim_time += dur
            lines.append(
                f"| {dt.get('dimension', 'unknown')} "
                f"| {format_duration_seconds(dur)} "
                f"| {dt.get('mode', 'unknown')} |"
            )
        lines.append(
            f"| **Total (dimension work)** | **{format_duration_seconds(total_dim_time)}** | - |"
        )

    return "\n".join(lines)


def output_timing_data(data: dict, output_format: str) -> int:
    """Output timing data in specified format. Returns exit code."""
    exit_code = determine_exit_code(data)

    if output_format == "json":
        print(json.dumps(data, indent=2))
    elif output_format == "markdown":
        print(generate_markdown_table(data))
    elif output_format == "quiet":
        pass
    else:
        print_stdout_summary(
            data,
            data.get("checkpoints", []),
            data.get("tokens"),
            data.get("baseline_comparison"),
            data.get("alerts", []),
        )

    return exit_code


# ============================================================================
# CLI Commands
# ============================================================================


def cmd_start(args):
    """Start timing for a skill execution."""
    agent_name = args.agent or os.environ.get("CORTEX_AGENT_NAME", "unknown")
    pid = str(os.getpid())
    agent_id = f"{agent_name}-{pid}"

    run_id = generate_run_id(args.skill, args.target, args.model)
    timing_file = get_timing_file(run_id)

    timing_data = {
        "run_id": run_id,
        "skill_name": args.skill,
        "target_file": args.target,
        "model": args.model,
        "review_mode": args.mode,
        "start_epoch": time.time(),
        "start_monotonic": time.monotonic(),
        "start_iso": datetime.now(UTC).isoformat(),
        "pid": os.getpid(),
        "agent": agent_name,
        "checkpoints": [],
    }

    write_timing_file(timing_file, timing_data)
    update_registry(args.skill, agent_id, run_id, args.target)

    print(f"TIMING_RUN_ID={run_id}")
    print(f"TIMING_FILE={timing_file}")
    print(f"TIMING_AGENT_ID={agent_id}")


def cmd_checkpoint(args):
    """Record a timing checkpoint."""
    timing_file = get_timing_file(args.run_id)

    if not timing_file.exists():
        print(f"WARNING: Timing file not found for run_id={args.run_id}")
        print("CHECKPOINT_STATUS=missing")
        return

    data = json.loads(timing_file.read_text())
    now_epoch = time.time()
    elapsed_wall = now_epoch - data["start_epoch"]
    # Monotonic delta when start_monotonic was captured in same process. Falls
    # back to wall-clock elapsed when not present (e.g., cross-process resumes).
    if "start_monotonic" in data:
        try:
            elapsed_raw = time.monotonic() - float(data["start_monotonic"])
        except (TypeError, ValueError):
            elapsed_raw = elapsed_wall
    else:
        elapsed_raw = elapsed_wall

    data["checkpoints"].append(
        {
            "name": args.name,
            "elapsed_seconds": round(elapsed_raw, 2),
            "elapsed_seconds_raw": elapsed_raw,
            "epoch": now_epoch,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    write_timing_file(timing_file, data)

    print(f"CHECKPOINT_NAME={args.name}")
    print(f"CHECKPOINT_ELAPSED={elapsed_raw:.2f}s")
    print("CHECKPOINT_STATUS=recorded")


def derive_dimension_timings_from_checkpoints(
    checkpoints: list, start_epoch: float
) -> tuple[list[dict], list[str]]:
    """Derive dimension_timings from dim_{name}_start/dim_{name}_end checkpoint pairs.

    Returns (dimension_timings, warnings).
    Checkpoint names must match: ^dim_(?P<name>[a-z_]+)_(start|end)$
    Each checkpoint provides an elapsed_seconds field (relative to start_epoch).
    Duration is computed as end_elapsed - start_elapsed.
    """
    pattern = re.compile(r"^dim_(?P<name>[a-z_]+)_(?P<phase>start|end)$")
    pairs: dict[str, dict[str, float]] = {}
    warnings: list[str] = []

    for cp in checkpoints:
        name = cp.get("name", "")
        m = pattern.match(name)
        if not m:
            if name.startswith("dim_"):
                warnings.append(
                    f"Malformed dim_* checkpoint ignored: '{name}' "
                    "(expected dim_<name>_start or dim_<name>_end)"
                )
            continue
        dim_name = m.group("name")
        phase = m.group("phase")
        elapsed = float(cp.get("elapsed_seconds", 0))
        pairs.setdefault(dim_name, {})[phase] = elapsed

    dimension_timings: list[dict] = []
    for dim_name in sorted(pairs.keys()):
        phases = pairs[dim_name]
        if "start" not in phases or "end" not in phases:
            missing = "end" if "start" in phases else "start"
            warnings.append(f"Dimension '{dim_name}' missing {missing} checkpoint; skipped.")
            continue
        duration = round(phases["end"] - phases["start"], 2)
        dimension_timings.append(
            {
                "dimension": dim_name,
                "duration_seconds": duration,
                "mode": "checkpoint",
                "start_epoch": round(start_epoch + phases["start"], 6),
                "end_epoch": round(start_epoch + phases["end"], 6),
            }
        )

    return dimension_timings, warnings


def cmd_end(args):
    """End timing and compute duration."""
    agent_name = args.agent or os.environ.get("CORTEX_AGENT_NAME", "unknown")
    pid = str(os.getpid())
    agent_id = f"{agent_name}-{pid}"

    run_id = args.run_id
    output_format = getattr(args, "format", "human")
    ci_mode = getattr(args, "ci", False)

    if ci_mode:
        output_format = "json"

    # Validate run_id format before attempting file operations
    if run_id != "none" and not re.match(r"^[a-f0-9]{16}$", run_id):
        if output_format != "quiet":
            print(f"WARNING: Invalid run_id format: {run_id}", file=sys.stderr)
            print("Expected: 16-character hex string (e.g., a1b2c3d4e5f67890)", file=sys.stderr)
            print("Attempting registry recovery...", file=sys.stderr)
        run_id = "none"

    timing_file = get_timing_file(run_id)

    # Agent memory recovery
    if not timing_file.exists() or run_id == "none":
        recovered_id = recover_run_id(args.skill, agent_id)
        if recovered_id:
            timing_file = get_timing_file(recovered_id)
            run_id = recovered_id
            if output_format not in ("json", "quiet"):
                print(f"RECOVERED_RUN_ID={recovered_id}")

    if not timing_file.exists():
        completed_file = get_completed_file(run_id)
        if completed_file.exists():
            if output_format == "json":
                print(json.dumps(json.loads(completed_file.read_text())))
            elif output_format == "markdown":
                print(generate_markdown_table(json.loads(completed_file.read_text())))
            elif output_format != "quiet":
                print("TIMING_STATUS=already_completed")
                print(f"TIMING_COMPLETED_FILE={completed_file}")
            sys.exit(EXIT_SUCCESS)
        if output_format == "json":
            print(
                json.dumps(
                    {"error": "timing_file_not_found", "run_id": run_id, "status": "missing"}
                )
            )
        elif output_format != "quiet":
            print(f"WARNING: Timing file not found for run_id={run_id}")
            print("TIMING_STATUS=missing")
        sys.exit(EXIT_ERROR)

    data = json.loads(timing_file.read_text())
    end_epoch = time.time()
    end_monotonic = time.monotonic()
    duration_sec_wall = end_epoch - data["start_epoch"]
    # Prefer monotonic delta when both endpoints recorded in same process.
    if "start_monotonic" in data:
        try:
            duration_sec_monotonic = end_monotonic - float(data["start_monotonic"])
            duration_sec = duration_sec_monotonic
            data["duration_seconds_monotonic"] = round(duration_sec_monotonic, 6)
            data["end_monotonic"] = end_monotonic
            data["clock_source"] = "monotonic"
        except (TypeError, ValueError):
            duration_sec = duration_sec_wall
            data["clock_source"] = "wall"
    else:
        duration_sec = duration_sec_wall
        data["clock_source"] = "wall"

    # Validate timing data
    if duration_sec < 0:
        if output_format == "json":
            print(
                json.dumps(
                    {
                        "error": "negative_duration",
                        "duration_seconds": duration_sec,
                        "status": "error",
                    }
                )
            )
        elif output_format != "quiet":
            print(f"ERROR: Negative duration detected ({duration_sec}s) - clock skew")
            print("TIMING_STATUS=error")
        timing_file.unlink()
        sys.exit(EXIT_ERROR)

    if duration_sec < 1:
        if output_format not in ("json", "quiet"):
            print(
                f"WARNING: Duration under 1 second ({duration_sec}s) - possible race condition",
                file=sys.stderr,
            )
        data["status"] = "warning"
    else:
        data["status"] = "completed"

    # Update timing data
    data["end_epoch"] = end_epoch
    data["end_iso"] = datetime.now(UTC).isoformat()
    data["duration_seconds"] = round(duration_sec, 2)
    data["duration_human"] = format_duration(duration_sec)
    data["output_file"] = args.output_file

    # ------------------------------------------------------------------
    # Per-dimension timing resolution (explicit > auto-derive > missing)
    # ------------------------------------------------------------------
    checkpoints_for_scan = data.get("checkpoints", [])
    dim_checkpoints_present = any(
        re.match(r"^dim_[a-z_]+_(start|end)$", cp.get("name", "")) for cp in checkpoints_for_scan
    )
    auto_dim = getattr(args, "auto_dimension_timings", False)
    per_dimension_status = "missing"

    if args.dimension_timings:
        try:
            dim_timings = json.loads(args.dimension_timings)
            if isinstance(dim_timings, list):
                data["dimension_timings"] = dim_timings
                per_dimension_status = "present"
                if auto_dim:
                    print(
                        "WARNING: Both --dimension-timings and --auto-dimension-timings supplied; "
                        "explicit --dimension-timings wins.",
                        file=sys.stderr,
                    )
            else:
                print("VALIDATION ERROR: --dimension-timings must be a JSON array", file=sys.stderr)
        except (json.JSONDecodeError, TypeError) as e:
            print(
                f"VALIDATION ERROR: Could not parse --dimension-timings JSON: {e}", file=sys.stderr
            )
            print("Continuing with aggregate timing only (no per-dimension data).", file=sys.stderr)
    elif auto_dim:
        derived, derive_warnings = derive_dimension_timings_from_checkpoints(
            checkpoints_for_scan, start_epoch=data["start_epoch"]
        )
        for w in derive_warnings:
            print(f"WARNING: {w}", file=sys.stderr)
        if derived:
            data["dimension_timings"] = derived
            per_dimension_status = "derived"
        else:
            print(
                "WARNING: --auto-dimension-timings supplied but no dim_*_start/dim_*_end "
                "checkpoint pairs found; continuing with aggregate timing only.",
                file=sys.stderr,
            )
    elif dim_checkpoints_present:
        # Silent-omission protection: dim_* checkpoints exist but neither flag was passed.
        print(
            "WARNING: dim_* checkpoints found but --dimension-timings / "
            "--auto-dimension-timings not supplied; per-dimension data will be OMITTED. "
            "Pass --auto-dimension-timings to derive automatically.",
            file=sys.stderr,
        )

    data["per_dimension_status"] = per_dimension_status

    # Validate output file exists (for metadata embedding guidance)
    if (
        args.output_file
        and not Path(args.output_file).exists()
        and output_format not in ("json", "quiet")
    ):
        print(f"WARNING: Output file {args.output_file} does not exist yet", file=sys.stderr)
        print("Note: Timing metadata must be appended after file write completes", file=sys.stderr)

    # Token tracking (optional)
    if args.input_tokens > 0 or args.output_tokens > 0:
        check_pricing_staleness()
        tokens = calculate_cost(args.input_tokens, args.output_tokens, data["model"])
        data["tokens"] = tokens

    # Anomaly detection (legacy threshold-based alerts)
    alerts = check_alerts(data["skill_name"], data["review_mode"], duration_sec)

    # v2.0.0 distribution validator (additive). Fold into alerts list.
    distribution_alerts = validate_dimension_distribution(data)
    alerts.extend(distribution_alerts)
    data["alerts"] = alerts

    # Per-row validation_status + run-level status escalation.
    annotate_validation_status(data, distribution_alerts)
    new_status = escalate_status(data, distribution_alerts)
    if new_status != "completed" or data.get("status") not in ("warning",):
        data["status"] = new_status
    if data["status"] == "instrumentation_failed":
        # Strip the per-dimension array per source plan section 4.7 and emit banner.
        data["dimension_timings_rejected"] = data.pop("dimension_timings", [])
        if output_format not in ("json", "quiet"):
            triggered = sorted({a.get("type") for a in distribution_alerts})
            print(
                "INSTRUMENTATION_FAILED: per-dimension data rejected by skill-timer "
                f"v{VERSION} due to alerts: {triggered}",
                file=sys.stderr,
            )

    # Baseline comparison
    baseline = compare_to_baseline(
        data["skill_name"],
        data["review_mode"],
        data["model"],
        duration_sec,
        dimension_timings=data.get("dimension_timings"),
    )
    if baseline:
        data["baseline_comparison"] = baseline

    # Validate timing data before output
    is_valid, validation_errors = validate_timing_data(data)
    if not is_valid:
        data["validation_errors"] = validation_errors
        dim_errors = [e for e in validation_errors if e.startswith("dimension_timings")]
        if dim_errors:
            if output_format not in ("json", "quiet"):
                for err in dim_errors:
                    print(f"VALIDATION ERROR: {err}", file=sys.stderr)
                print(
                    "VALIDATION ERROR: Invalid dimension_timings rejected. "
                    "Re-run with --dimension-timings '[]' for aggregate timing only.",
                    file=sys.stderr,
                )
            data["dimension_timings"] = []
            data["validation_errors"] = dim_errors
        non_dim_errors = [e for e in validation_errors if not e.startswith("dimension_timings")]
        if non_dim_errors and output_format not in ("json", "quiet"):
            for err in non_dim_errors:
                print(f"VALIDATION WARNING: {err}", file=sys.stderr)

    # Write completed file (ensure directory exists)
    completed_file = get_completed_file(data["run_id"])
    completed_file.parent.mkdir(parents=True, exist_ok=True)
    write_timing_file(completed_file, data)

    # Cleanup
    timing_file.unlink()
    remove_from_registry(args.skill, agent_id)
    cleanup_stale_files()

    # Output based on format
    if output_format not in ("json", "markdown", "quiet"):
        print(
            f"TIMING_DURATION={data['duration_human']} ({format_duration_seconds(data['duration_seconds'])})"
        )
        print(f"TIMING_START={data['start_iso']}")
        print(f"TIMING_END={data['end_iso']}")
        print(f"TIMING_STATUS={data['status']}")
        print(f"PER_DIMENSION_STATUS={data.get('per_dimension_status', 'missing')}")

    exit_code = output_timing_data(data, output_format)
    sys.exit(exit_code)


def cmd_wrap(args):
    """v2.0.0 atomic per-dimension capture.

    Agent invokes `wrap` AFTER per-dimension analysis is materialized as
    --evidence (file path or stdin, >=100 bytes by default). skill-timer
    assigns the end_epoch server-side. The agent cannot collapse the duration
    by emitting two commands back-to-back.
    """
    timing_file = get_timing_file(args.run_id)
    if not timing_file.exists():
        print(f"ERROR: Timing file not found for run_id={args.run_id}", file=sys.stderr)
        print("WRAP_STATUS=missing")
        sys.exit(EXIT_ERROR)

    data = json.loads(timing_file.read_text())

    # --- Evidence ingestion + minimum-bytes gate ---
    cfg = load_thresholds_config()
    min_bytes = int(cfg.get("min_evidence_bytes", 100))
    if args.evidence == "-":
        evidence_bytes = sys.stdin.buffer.read()
        evidence_source = "<stdin>"
    else:
        evidence_path = Path(args.evidence)
        if not evidence_path.exists():
            print(f"ERROR: --evidence path not found: {evidence_path}", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        evidence_bytes = evidence_path.read_bytes()
        evidence_source = str(evidence_path)

    if len(evidence_bytes) < min_bytes:
        print(
            f"ERROR: --evidence too small ({len(evidence_bytes)}B < {min_bytes}B); "
            f"refusing to wrap dimension '{args.dimension}'.",
            file=sys.stderr,
        )
        print("WRAP_STATUS=evidence_too_small")
        sys.exit(EXIT_INSTRUMENTATION_FAILED)

    # --- Resolve start endpoint (explicit > previous wrap end > run start) ---
    existing_dims = data.setdefault("dimension_timings", [])
    prev_wrap_end_epoch = None
    prev_wrap_end_monotonic = None
    for dt in reversed(existing_dims):
        if dt.get("mode") == "wrap":
            prev_wrap_end_epoch = dt.get("end_epoch")
            prev_wrap_end_monotonic = dt.get("end_monotonic")
            break

    if args.start_epoch is not None:
        start_epoch = float(args.start_epoch)
    elif prev_wrap_end_epoch is not None:
        start_epoch = float(prev_wrap_end_epoch)
    else:
        start_epoch = float(data["start_epoch"])

    if args.start_monotonic is not None:
        start_monotonic: float | None = float(args.start_monotonic)
    elif prev_wrap_end_monotonic is not None:
        start_monotonic = float(prev_wrap_end_monotonic)
    elif "start_monotonic" in data:
        try:
            start_monotonic = float(data["start_monotonic"])
        except (TypeError, ValueError):
            start_monotonic = None
    else:
        start_monotonic = None

    # --- Server-side end timestamp ---
    end_epoch = time.time()
    end_monotonic = time.monotonic()

    if start_monotonic is not None:
        duration = end_monotonic - start_monotonic
    else:
        duration = end_epoch - start_epoch

    if duration < 0:
        print(
            f"ERROR: Negative duration ({duration:.4f}s) for dimension "
            f"'{args.dimension}'; clock skew suspected.",
            file=sys.stderr,
        )
        sys.exit(EXIT_ERROR)

    mode = args.mode or "wrap"
    if mode not in ("wrap", "inline"):
        print(f"ERROR: --mode must be 'wrap' or 'inline' (got: {mode})", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    dim_entry: dict[str, Any] = {
        "dimension": args.dimension,
        "duration_seconds": round(duration, 6),
        "mode": mode,
        "start_epoch": round(start_epoch, 6),
        "end_epoch": round(end_epoch, 6),
        "evidence_bytes": len(evidence_bytes),
        "evidence_source": evidence_source,
    }
    if start_monotonic is not None:
        dim_entry["start_monotonic"] = start_monotonic
        dim_entry["end_monotonic"] = end_monotonic
        dim_entry["clock_source"] = "monotonic"
    else:
        dim_entry["clock_source"] = "wall"

    existing_dims.append(dim_entry)
    write_timing_file(timing_file, data)

    print(f"WRAP_DIMENSION={args.dimension}")
    print(f"WRAP_DURATION={duration:.4f}s")
    print(f"WRAP_MODE={mode}")
    print(f"WRAP_EVIDENCE_BYTES={len(evidence_bytes)}")
    print("WRAP_STATUS=recorded")


def cmd_finalize(args):
    """v2.0.0 stage marker for work-complete semantics.

    --stage pre_write requires --review-artifact; records the moment after
    synthesized output exists but before file write.
    --stage post_write records the moment after the on-disk write.
    """
    timing_file = get_timing_file(args.run_id)
    if not timing_file.exists():
        print(f"ERROR: Timing file not found for run_id={args.run_id}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    data = json.loads(timing_file.read_text())

    if args.stage == "pre_write":
        if not args.review_artifact:
            print(
                "ERROR: --stage pre_write requires --review-artifact <path>",
                file=sys.stderr,
            )
            sys.exit(EXIT_ERROR)
        artifact = Path(args.review_artifact)
        # Artifact may not exist yet on disk if finalize is invoked just before
        # write; we record the path declaration regardless.
        finalize = data.setdefault("finalize", {})
        finalize["pre_write_epoch"] = time.time()
        finalize["pre_write_monotonic"] = time.monotonic()
        finalize["review_artifact"] = str(artifact)
    elif args.stage == "post_write":
        finalize = data.setdefault("finalize", {})
        finalize["post_write_epoch"] = time.time()
        finalize["post_write_monotonic"] = time.monotonic()
    else:
        print(
            f"ERROR: --stage must be 'pre_write' or 'post_write' (got: {args.stage})",
            file=sys.stderr,
        )
        sys.exit(EXIT_ERROR)

    write_timing_file(timing_file, data)

    print(f"FINALIZE_STAGE={args.stage}")
    print("FINALIZE_STATUS=recorded")


def cmd_replay(args):
    """Re-run the v2.0.0 distribution validator against a completed JSON.

    Useful for post-hoc validation of historical runs and CI gating.
    """
    fixture = Path(args.fixture)
    if not fixture.exists():
        print(f"ERROR: --fixture not found: {fixture}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    try:
        data = json.loads(fixture.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse fixture JSON: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    alerts = validate_dimension_distribution(data)
    annotate_validation_status(data, alerts)
    new_status = escalate_status(data, alerts)
    data["status"] = new_status
    data["alerts"] = (data.get("alerts") or []) + alerts

    output_format = getattr(args, "format", "human")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"REPLAY: {fixture}")
        print(f"  status:           {new_status}")
        print(
            f"  work_window:      {data.get('work_window_seconds'):>8} s "
            f"({data.get('work_window_source')})"
        )
        print(f"  alerts ({len(alerts)}):")
        for a in alerts:
            print(f"    [{a['severity']:7s}] {a['type']}: {a['message'][:200]}")

    sys.exit(determine_exit_code(data))


def cmd_baseline_set(args):
    """Set baseline from recent timing data."""
    timing_data_dir = Path("reviews/.timing-data")
    cutoff = time.time() - (args.days * 24 * 60 * 60)

    durations = []
    if timing_data_dir.exists():
        for filepath in glob.glob(str(timing_data_dir / "skill-timer-*-complete.json")):
            try:
                data = json.loads(Path(filepath).read_text())
                if (
                    data.get("skill_name") == args.skill
                    and data.get("review_mode") == args.mode
                    and data.get("model") == args.model
                    and data.get("end_epoch", 0) >= cutoff
                ):
                    durations.append(data["duration_seconds"])
            except Exception:
                pass

    min_required = getattr(args, "min_samples", 5)  # Configurable minimum samples

    if len(durations) < min_required:
        print(f"ERROR: Not enough data points ({len(durations)}). Need at least {min_required}.")
        print("Tip: Use --min-samples N to lower threshold for testing/debugging.")
        sys.exit(1)

    durations.sort()
    avg = sum(durations) / len(durations)
    median = durations[len(durations) // 2]
    p95_idx = int(len(durations) * 0.95)
    p95 = durations[p95_idx] if p95_idx < len(durations) else durations[-1]
    variance = sum((d - avg) ** 2 for d in durations) / len(durations)
    stddev = variance**0.5

    baselines_file = get_baselines_file()
    baselines_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        baselines = json.loads(baselines_file.read_text()) if baselines_file.exists() else {}
    except Exception:
        baselines = {}

    if args.skill not in baselines:
        baselines[args.skill] = {}
    if args.mode not in baselines[args.skill]:
        baselines[args.skill][args.mode] = {}

    baselines[args.skill][args.mode][args.model] = {
        "baseline_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        "sample_size": len(durations),
        "avg_seconds": round(avg, 2),
        "median_seconds": round(median, 2),
        "p95_seconds": round(p95, 2),
        "stddev_seconds": round(stddev, 2),
    }

    per_dimension = getattr(args, "per_dimension", False)
    if per_dimension:
        dim_data: dict[str, list[float]] = {}
        timing_data_dir_pd = Path("reviews/.timing-data")
        if timing_data_dir_pd.exists():
            for filepath in glob.glob(str(timing_data_dir_pd / "skill-timer-*-complete.json")):
                try:
                    data = json.loads(Path(filepath).read_text())
                    if (
                        data.get("skill_name") == args.skill
                        and data.get("review_mode") == args.mode
                        and data.get("model") == args.model
                        and data.get("end_epoch", 0) >= cutoff
                        and "dimension_timings" in data
                    ):
                        for dt in data["dimension_timings"]:
                            dim_name = dt.get("dimension", "unknown")
                            dur = dt.get("duration_seconds", 0)
                            if dur >= 0:
                                dim_data.setdefault(dim_name, []).append(dur)
                except Exception:
                    pass

        if dim_data:
            dimensions_bl = {}
            for dim_name, durs in dim_data.items():
                d_avg = sum(durs) / len(durs)
                d_var = sum((d - d_avg) ** 2 for d in durs) / len(durs)
                d_stddev = d_var**0.5
                dimensions_bl[dim_name] = {
                    "avg_seconds": round(d_avg, 2),
                    "stddev_seconds": round(d_stddev, 2),
                }
            baselines[args.skill][args.mode][args.model]["dimensions"] = dimensions_bl

    baselines_file.write_text(json.dumps(baselines, indent=2))

    print(f"Baseline set for {args.skill}/{args.mode}/{args.model}:")
    print(f"  Sample size: {len(durations)}")
    print(f"  Average: {format_duration(avg)} ({avg:.1f}s)")
    print(f"  Median: {format_duration(median)} ({median:.1f}s)")
    print(f"  P95: {format_duration(p95)} ({p95:.1f}s)")
    print(f"  Stddev: {stddev:.1f}s")


def cmd_baseline_compare(args):
    """Compare a run against baseline."""
    completed_file = get_completed_file(args.run_id)

    if not completed_file.exists():
        print(f"ERROR: Completed timing file not found for run_id={args.run_id}")
        sys.exit(1)

    data = json.loads(completed_file.read_text())
    comparison = compare_to_baseline(
        data["skill_name"],
        data["review_mode"],
        data["model"],
        data["duration_seconds"],
        dimension_timings=data.get("dimension_timings"),
    )

    if comparison is None:
        print(f"No baseline found for {data['skill_name']}/{data['review_mode']}/{data['model']}")
        sys.exit(1)

    # Type narrowing: comparison is now guaranteed to be non-None
    assert comparison is not None
    sign = "+" if comparison["delta_percent"] >= 0 else ""
    print(f"Baseline Comparison for {args.run_id}:")
    print(f"  Current: {format_duration(data['duration_seconds'])} ({data['duration_seconds']}s)")
    print(
        f"  Baseline: {format_duration(comparison['baseline_avg_seconds'])} ({comparison['baseline_avg_seconds']}s avg)"
    )
    print(f"  Delta: {sign}{comparison['delta_seconds']}s ({sign}{comparison['delta_percent']}%)")
    print(f"  Status: {comparison['status'].replace('_', ' ')}")

    dim_comparisons = comparison.get("dimension_comparisons", [])
    if dim_comparisons:
        print("")
        print("  Per-Dimension Comparison:")
        print(f"    {'Dimension':30s} {'Current':>10s} {'Baseline':>10s} {'Delta':>12s} {'Status'}")
        for dc in dim_comparisons:
            d_sign = "+" if dc["delta_percent"] >= 0 else ""
            print(
                f"    {dc['dimension']:30s} {format_duration_seconds(dc['current_seconds']):>10s}"
                f" {format_duration_seconds(dc['baseline_avg_seconds']):>10s}"
                f" {d_sign}{dc['delta_percent']:.1f}%{' ':>6s}"
                f" {dc['status'].replace('_', ' ')}"
            )
    elif data.get("dimension_timings"):
        print("")
        print("  NOTE: Baseline was set without --per-dimension. Per-dimension comparison skipped.")
        print("  Re-run `baseline set --per-dimension` to enable.")


def cmd_analyze(args):
    """Analyze timing data."""
    timing_data_dir = Path("reviews/.timing-data")
    cutoff = time.time() - (args.days * 24 * 60 * 60)
    output_format = getattr(args, "format", "human")

    runs = []
    if timing_data_dir.exists():
        for filepath in glob.glob(str(timing_data_dir / "skill-timer-*-complete.json")):
            try:
                data = json.loads(Path(filepath).read_text())
                if data.get("end_epoch", 0) < cutoff:
                    continue
                if args.skill and data.get("skill_name") != args.skill:
                    continue
                if args.model and data.get("model") != args.model:
                    continue
                runs.append(data)
            except Exception:
                pass

    if not runs:
        if output_format == "json":
            print(json.dumps({"count": 0, "runs": [], "error": "no_data"}))
        elif output_format == "csv":
            print("skill,model,run_id,duration_seconds,status")
        else:
            print("No timing data found matching criteria.")
        return

    durations = [r["duration_seconds"] for r in runs]
    durations.sort()

    avg = sum(durations) / len(durations)
    median = durations[len(durations) // 2]
    variance = sum((d - avg) ** 2 for d in durations) / len(durations)
    stddev = variance**0.5
    p5_idx = max(0, int(len(durations) * 0.05))
    p5 = durations[p5_idx]
    p50 = median
    p95_idx = min(len(durations) - 1, int(len(durations) * 0.95))
    p95 = durations[p95_idx]

    result = {
        "count": len(runs),
        "total_seconds": round(sum(durations), 2),
        "avg_seconds": round(avg, 2),
        "median_seconds": round(median, 2),
        "min_seconds": round(min(durations), 2),
        "max_seconds": round(max(durations), 2),
        "stddev_seconds": round(stddev, 2),
        "p5_seconds": round(p5, 2),
        "p50_seconds": round(p50, 2),
        "p95_seconds": round(p95, 2),
        "filters": {"skill": args.skill, "model": args.model, "days": args.days},
    }

    per_dimension = getattr(args, "per_dimension", False)
    dim_result = {}
    if per_dimension:
        dim_runs = [r for r in runs if "dimension_timings" in r]
        skipped = len(runs) - len(dim_runs)
        if skipped > 0:
            print(
                f"NOTE: {skipped} run(s) lack dimension_timings data and are excluded from per-dimension breakdown.",
                file=sys.stderr,
            )
        if dim_runs:
            dim_data_analyze: dict[str, list[float]] = {}
            for r in dim_runs:
                for dt in r.get("dimension_timings", []):
                    dim_name = dt.get("dimension", "unknown")
                    dur = dt.get("duration_seconds", 0)
                    if dur >= 0:
                        dim_data_analyze.setdefault(dim_name, []).append(dur)

            for dim_name, durs in sorted(dim_data_analyze.items()):
                durs.sort()
                d_avg = sum(durs) / len(durs)
                d_median = durs[len(durs) // 2]
                d_var = sum((d - d_avg) ** 2 for d in durs) / len(durs)
                d_stddev = d_var**0.5
                d_p5 = durs[max(0, int(len(durs) * 0.05))]
                d_p95 = durs[min(len(durs) - 1, int(len(durs) * 0.95))]
                dim_result[dim_name] = {
                    "count": len(durs),
                    "avg_seconds": round(d_avg, 2),
                    "median_seconds": round(d_median, 2),
                    "stddev_seconds": round(d_stddev, 2),
                    "p5_seconds": round(d_p5, 2),
                    "p95_seconds": round(d_p95, 2),
                }
            if dim_result:
                result["per_dimension"] = dim_result

    if output_format == "json":
        result["runs"] = [
            {
                "run_id": r.get("run_id"),
                "skill": r.get("skill_name"),
                "model": r.get("model"),
                "duration_seconds": r.get("duration_seconds"),
                "status": r.get("status"),
            }
            for r in runs
        ]
        print(json.dumps(result, indent=2))
    elif output_format == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["skill", "model", "run_id", "duration_seconds", "status"]
        )
        writer.writeheader()
        for r in runs:
            writer.writerow(
                {
                    "skill": r.get("skill_name", ""),
                    "model": r.get("model", ""),
                    "run_id": r.get("run_id", ""),
                    "duration_seconds": r.get("duration_seconds", 0),
                    "status": r.get("status", ""),
                }
            )
        print(output.getvalue(), end="")
    elif args.output:
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"Analysis written to {args.output}")
    else:
        sep = "-" * 40
        print(f"TIMING: Analysis v{VERSION}")
        print(sep)
        print(f"Count:       {len(runs)} runs")
        print(
            f"Filters:     skill={args.skill or 'all'}, model={args.model or 'all'}, days={args.days}"
        )
        print(sep)
        print(f"Average:     {format_duration(avg)} ({format_duration_seconds(avg)})")
        print(f"Median:      {format_duration(median)} ({format_duration_seconds(median)})")
        print(f"Stddev:      {format_duration_seconds(stddev)}")
        print(
            f"Min:         {format_duration(min(durations))} ({format_duration_seconds(min(durations))})"
        )
        print(
            f"Max:         {format_duration(max(durations))} ({format_duration_seconds(max(durations))})"
        )
        print(f"P5:          {format_duration(p5)} ({format_duration_seconds(p5)})")
        print(f"P50:         {format_duration(p50)} ({format_duration_seconds(p50)})")
        print(f"P95:         {format_duration(p95)} ({format_duration_seconds(p95)})")
        print(sep)

    if per_dimension and dim_result and output_format not in ("json", "csv") and not args.output:
        print("")
        print("Per-Dimension Breakdown:")
        print(f"  {'Dimension':30s} {'Avg':>10s} {'Median':>10s} {'Stddev':>10s} {'P95':>10s}")
        for dim_name, stats in dim_result.items():
            print(
                f"  {dim_name:30s} {format_duration_seconds(stats['avg_seconds']):>10s}"
                f" {format_duration_seconds(stats['median_seconds']):>10s}"
                f" {format_duration_seconds(stats['stddev_seconds']):>10s}"
                f" {format_duration_seconds(stats['p95_seconds']):>10s}"
            )
        print(sep)


def cmd_aggregate(args):
    """Aggregate timing data from review files."""
    timing_pattern = re.compile(
        r"\|\s*Run ID\s*\|\s*`([a-f0-9]+)`\s*\|.*?"
        r"\|\s*Duration\s*\|\s*(\d+m \d+s)\s*\((\d+\.?\d*)s\)\s*\|",
        re.DOTALL,
    )

    output_format = getattr(args, "format", "json")
    results = []

    for filepath in args.files:
        try:
            content = Path(filepath).read_text()
            match = timing_pattern.search(content)
            if match:
                results.append(
                    {
                        "file": str(filepath),
                        "run_id": match.group(1),
                        "duration_human": match.group(2),
                        "duration_seconds": float(match.group(3)),
                    }
                )
        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    if output_format == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["file", "run_id", "duration_human", "duration_seconds"]
        )
        writer.writeheader()
        for r in results:
            writer.writerow(r)
        if args.output:
            Path(args.output).write_text(output.getvalue())
            print(f"Aggregated {len(results)} timing records to {args.output}")
        else:
            print(output.getvalue(), end="")
    else:
        aggregate_data = {
            "count": len(results),
            "total_seconds": round(sum(r["duration_seconds"] for r in results), 2),
            "avg_seconds": round(sum(r["duration_seconds"] for r in results) / len(results), 2)
            if results
            else 0,
            "runs": results,
        }
        if args.output:
            Path(args.output).write_text(json.dumps(aggregate_data, indent=2))
            print(f"Aggregated {len(results)} timing records to {args.output}")
        else:
            print(json.dumps(aggregate_data, indent=2))


def main():
    """Main entry point with argparse CLI."""
    parser = argparse.ArgumentParser(
        description="Skill timing instrumentation CLI for measuring execution performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start timing a skill
  %(prog)s start --skill rule-reviewer --target rules/100.md --model claude-sonnet-45

  # Record a checkpoint
  %(prog)s checkpoint --run-id a1b2c3d4e5f67890 --name schema_validated

  # End timing with token counts
  %(prog)s end --run-id a1b2c3d4e5f67890 --output-file output.md --skill rule-reviewer \\
      --input-tokens 1000 --output-tokens 500

  # Set performance baseline
  %(prog)s baseline set --skill rule-reviewer --mode FULL --model claude-sonnet-45

  # Analyze recent timing data
  %(prog)s analyze --skill rule-reviewer --days 7

For detailed documentation, see docs/USING_SKILL_TIMER_SKILL.md
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # start command
    start_parser = subparsers.add_parser("start", help="Start timing for a skill execution")
    start_parser.add_argument("--skill", required=True, help="Skill name (e.g., rule-reviewer)")
    start_parser.add_argument("--target", required=True, help="Target file path")
    start_parser.add_argument("--model", required=True, help="Model slug (e.g., claude-sonnet-45)")
    start_parser.add_argument(
        "--mode", default="FULL", help="Review mode (FULL, FOCUSED, STALENESS)"
    )
    start_parser.add_argument(
        "--agent", default=None, help="Agent name (defaults to CORTEX_AGENT_NAME env var)"
    )
    start_parser.set_defaults(func=cmd_start)

    # checkpoint command
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Record a timing checkpoint")
    checkpoint_parser.add_argument("--run-id", required=True, help="Run ID from timing start")
    checkpoint_parser.add_argument(
        "--name", required=True, help="Checkpoint name (e.g., schema_validated)"
    )
    checkpoint_parser.set_defaults(func=cmd_checkpoint)

    # end command
    end_parser = subparsers.add_parser("end", help="End timing and compute duration")
    end_parser.add_argument(
        "--run-id", required=True, help='Run ID from timing start (or "none" for recovery)'
    )
    end_parser.add_argument("--output-file", required=True, help="Path to output file")
    end_parser.add_argument("--skill", required=True, help="Skill name (for recovery)")
    end_parser.add_argument(
        "--input-tokens", default=0, type=int, help="Input token count (optional)"
    )
    end_parser.add_argument(
        "--output-tokens", default=0, type=int, help="Output token count (optional)"
    )
    end_parser.add_argument("--agent", default=None, help="Agent name (for recovery)")
    end_parser.add_argument(
        "--format",
        choices=["human", "json", "markdown", "quiet"],
        default="human",
        help="Output format: human (default), json (machine-readable), markdown (file embed), quiet (exit code only)",
    )
    end_parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: JSON output to stdout, exit code based on baseline/thresholds",
    )
    end_parser.add_argument(
        "--dimension-timings",
        default=None,
        help='JSON array of per-dimension timing data. Format: [{"dimension":"name","duration_seconds":N,"mode":"checkpoint|self-report"}]',
    )
    end_parser.add_argument(
        "--auto-dimension-timings",
        action="store_true",
        help="Derive dimension_timings from dim_<name>_start / dim_<name>_end checkpoint pairs. "
        "Ignored (with WARNING) if --dimension-timings is also supplied.",
    )
    end_parser.set_defaults(func=cmd_end)

    # wrap command (v2.0.0): atomic per-dimension capture
    wrap_parser = subparsers.add_parser(
        "wrap",
        help="Atomically capture a per-dimension duration with server-side end timestamp (v2.0.0)",
    )
    wrap_parser.add_argument("--run-id", required=True, help="Run ID from timing start")
    wrap_parser.add_argument(
        "--dimension", required=True, help="Dimension name (e.g., executability)"
    )
    wrap_parser.add_argument(
        "--evidence",
        required=True,
        help="Path to per-dimension worksheet draft, or '-' for stdin (>=100 bytes)",
    )
    wrap_parser.add_argument(
        "--start-epoch", type=float, default=None, help="Optional explicit start (wall-clock epoch)"
    )
    wrap_parser.add_argument(
        "--start-monotonic",
        type=float,
        default=None,
        help="Optional explicit start (monotonic clock value)",
    )
    wrap_parser.add_argument(
        "--mode",
        choices=["wrap", "inline"],
        default="wrap",
        help="Capture mode (default: wrap)",
    )
    wrap_parser.set_defaults(func=cmd_wrap)

    # finalize command (v2.0.0): record work-complete semantics server-side
    finalize_parser = subparsers.add_parser(
        "finalize",
        help="Record work-complete stage (pre_write/post_write) for plausibility math (v2.0.0)",
    )
    finalize_parser.add_argument("--run-id", required=True, help="Run ID from timing start")
    finalize_parser.add_argument(
        "--stage",
        choices=["pre_write", "post_write"],
        required=True,
        help="Lifecycle stage to record",
    )
    finalize_parser.add_argument(
        "--review-artifact",
        default=None,
        help="Path to synthesized output (required when --stage pre_write)",
    )
    finalize_parser.set_defaults(func=cmd_finalize)

    # replay command (v2.0.0): re-run distribution validator against fixture
    replay_parser = subparsers.add_parser(
        "replay",
        help="Re-run distribution validator against a completed timing JSON (v2.0.0)",
    )
    replay_parser.add_argument("--fixture", required=True, help="Path to completed timing JSON")
    replay_parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format",
    )
    replay_parser.set_defaults(func=cmd_replay)

    # baseline command group
    baseline_parser = subparsers.add_parser("baseline", help="Manage timing baselines")
    baseline_subparsers = baseline_parser.add_subparsers(
        dest="baseline_command", help="Baseline commands"
    )

    # baseline set
    baseline_set_parser = baseline_subparsers.add_parser(
        "set", help="Set baseline from recent timing data"
    )
    baseline_set_parser.add_argument("--skill", required=True, help="Skill name")
    baseline_set_parser.add_argument("--mode", required=True, help="Review mode")
    baseline_set_parser.add_argument("--model", required=True, help="Model slug")
    baseline_set_parser.add_argument(
        "--days", default=30, type=int, help="Days of data to include (default: 30)"
    )
    baseline_set_parser.add_argument(
        "--min-samples",
        default=5,
        type=int,
        help="Minimum sample size required (default: 5, lower for testing)",
    )
    baseline_set_parser.set_defaults(func=cmd_baseline_set)
    baseline_set_parser.add_argument(
        "--per-dimension",
        action="store_true",
        help="Also set per-dimension baselines from dimension_timings data",
    )

    # baseline compare
    baseline_compare_parser = baseline_subparsers.add_parser(
        "compare", help="Compare a run against baseline"
    )
    baseline_compare_parser.add_argument("--run-id", required=True, help="Run ID to compare")
    baseline_compare_parser.set_defaults(func=cmd_baseline_compare)

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze timing data across runs")
    analyze_parser.add_argument("--skill", default=None, help="Filter by skill name")
    analyze_parser.add_argument("--model", default=None, help="Filter by model")
    analyze_parser.add_argument(
        "--days", default=7, type=int, help="Days of data to analyze (default: 7)"
    )
    analyze_parser.add_argument("--output", default=None, help="Output file path (JSON format)")
    analyze_parser.add_argument(
        "--format",
        choices=["human", "json", "csv"],
        default="human",
        help="Output format: human (default), json (machine-readable), csv (spreadsheet)",
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    analyze_parser.add_argument(
        "--per-dimension",
        action="store_true",
        help="Show per-dimension timing breakdown (requires dimension_timings in completed data)",
    )

    # aggregate command
    aggregate_parser = subparsers.add_parser(
        "aggregate", help="Aggregate timing data from review files"
    )
    aggregate_parser.add_argument("files", nargs="*", help="Review files to parse for timing data")
    aggregate_parser.add_argument(
        "--output", default=None, help="Output file path (optional, prints to stdout if omitted)"
    )
    aggregate_parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format: json (default), csv (spreadsheet)",
    )
    aggregate_parser.set_defaults(func=cmd_aggregate)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "baseline" and args.baseline_command is None:
        baseline_parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
