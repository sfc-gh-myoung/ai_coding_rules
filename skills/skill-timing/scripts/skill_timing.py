#!/usr/bin/env python
"""Skill Timing CLI Module.

Provides timing instrumentation for Claude Code skills.
Uses only standard library modules for maximum portability.

Usage:
    python skill_timing.py start --skill NAME --target FILE --model MODEL
    python skill_timing.py checkpoint --run-id ID --name NAME
    python skill_timing.py end --run-id ID --output-file FILE --skill NAME [--format human|json|markdown|quiet]
    python skill_timing.py analyze --skill NAME --days 30 [--format human|json|csv]
    python skill_timing.py baseline set --skill NAME --mode MODE --model MODEL
    python skill_timing.py baseline compare --run-id ID

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
# Last updated: 2026-01-06
# Sources: https://www.anthropic.com/pricing, https://openai.com/pricing
COST_PER_1M_TOKENS = {
    "claude-sonnet-45": {"input": 3.00, "output": 15.00},
    "claude-opus-45": {"input": 15.00, "output": 75.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "default": {"input": 5.00, "output": 15.00},
}

TTL_DAYS = 7
REGISTRY_STALE_HOURS = 24

VERSION = "1.3.0"

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_SHORTCUT_DETECTED = 2
EXIT_ABOVE_BASELINE = 3

PRICING_LAST_UPDATED = "2026-01-06"
PRICING_REVIEW_INTERVAL_DAYS = 90


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
    return get_timing_data_dir() / f"skill-timing-{run_id}.json"


def get_completed_file(run_id: str) -> Path:
    """Get path to completed timing file."""
    return get_timing_data_dir() / f"skill-timing-{run_id}-complete.json"


def get_registry_file() -> Path:
    """Get path to agent recovery registry (project-local)."""
    return get_timing_data_dir() / "skill-timing-registry.json"


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


def compare_to_baseline(skill_name: str, mode: str, model: str, duration_sec: float) -> dict | None:
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

        return {
            "baseline_avg_seconds": avg,
            "baseline_stddev_seconds": stddev,
            "delta_seconds": round(delta, 2),
            "delta_percent": round(delta_percent, 1),
            "status": status,
        }
    except Exception:
        return None


def cleanup_stale_files():
    """Remove stale in-progress timing files older than TTL."""
    data_dir = get_timing_data_dir()
    cutoff = time.time() - (TTL_DAYS * 24 * 60 * 60)

    for filepath in glob.glob(str(data_dir / "skill-timing-*.json")):
        fp = Path(filepath)
        if fp.name.endswith("-complete.json"):
            continue
        if fp.name == "skill-timing-registry.json":
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


def validate_timing_data(data: dict) -> tuple[bool, list[str]]:
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
    valid_statuses = ["completed", "warning", "error", "missing"]
    if data.get("status") not in valid_statuses:
        errors.append(f"Invalid status: {data.get('status')}")
    if "duration_seconds" in data and data["duration_seconds"] < 0:
        errors.append(f"Invalid duration: {data['duration_seconds']}")
    return (len(errors) == 0, errors)


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
    alerts = data.get("alerts", [])
    for alert in alerts:
        if alert.get("type") == "error_short_duration":
            return EXIT_SHORTCUT_DETECTED
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
    print(f"TIMING: skill-timing v{VERSION}")
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
    elapsed = time.time() - data["start_epoch"]

    data["checkpoints"].append(
        {
            "name": args.name,
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    write_timing_file(timing_file, data)

    print(f"CHECKPOINT_NAME={args.name}")
    print(f"CHECKPOINT_ELAPSED={elapsed:.2f}s")
    print("CHECKPOINT_STATUS=recorded")


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
                print(f"TIMING_STATUS=already_completed")
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
    duration_sec = end_epoch - data["start_epoch"]

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

    # Anomaly detection
    alerts = check_alerts(data["skill_name"], data["review_mode"], duration_sec)
    data["alerts"] = alerts

    # Baseline comparison
    baseline = compare_to_baseline(
        data["skill_name"], data["review_mode"], data["model"], duration_sec
    )
    if baseline:
        data["baseline_comparison"] = baseline

    # Validate timing data before output
    is_valid, validation_errors = validate_timing_data(data)
    if not is_valid:
        data["validation_errors"] = validation_errors
        if output_format not in ("json", "quiet"):
            for err in validation_errors:
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

    exit_code = output_timing_data(data, output_format)
    sys.exit(exit_code)


def cmd_baseline_set(args):
    """Set baseline from recent timing data."""
    timing_data_dir = Path("reviews/.timing-data")
    cutoff = time.time() - (args.days * 24 * 60 * 60)

    durations = []
    if timing_data_dir.exists():
        for filepath in glob.glob(str(timing_data_dir / "skill-timing-*-complete.json")):
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
        data["skill_name"], data["review_mode"], data["model"], data["duration_seconds"]
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


def cmd_analyze(args):
    """Analyze timing data."""
    timing_data_dir = Path("reviews/.timing-data")
    cutoff = time.time() - (args.days * 24 * 60 * 60)
    output_format = getattr(args, "format", "human")

    runs = []
    if timing_data_dir.exists():
        for filepath in glob.glob(str(timing_data_dir / "skill-timing-*-complete.json")):
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

For detailed documentation, see docs/USING_SKILL_TIMING_SKILL.md
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
    end_parser.set_defaults(func=cmd_end)

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
