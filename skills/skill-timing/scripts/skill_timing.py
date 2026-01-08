#!/usr/bin/env python
"""Skill Timing CLI Module.

Provides timing instrumentation for Claude Code skills.
Uses only standard library modules for maximum portability.

Usage:
    python skill_timing.py start --skill NAME --target FILE --model MODEL
    python skill_timing.py checkpoint --run-id ID --name NAME
    python skill_timing.py end --run-id ID --output-file FILE --skill NAME
    python skill_timing.py analyze --skill NAME --days 30
    python skill_timing.py baseline set --skill NAME --mode MODE --model MODEL
    python skill_timing.py baseline compare --run-id ID
"""

import argparse
import glob
import hashlib
import json
import os
import re
import secrets
import sys
import tempfile
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
        "FULL": {"short": 120, "long": 720, "error": 60},
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


# ============================================================================
# Utility Functions
# ============================================================================


def get_temp_dir() -> Path:
    """Get cross-platform temp directory."""
    return Path(tempfile.gettempdir())


def get_timing_file(run_id: str) -> Path:
    """Get path to timing file for a run."""
    return get_temp_dir() / f"skill-timing-{run_id}.json"


def get_completed_file(run_id: str) -> Path:
    """Get path to completed timing file (saved to reviews/ for persistence)."""
    return Path("reviews/.timing-data") / f"skill-timing-{run_id}-complete.json"


def get_registry_file() -> Path:
    """Get path to agent recovery registry."""
    return get_temp_dir() / "skill-timing-registry.json"


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
    """Format seconds as human-readable duration."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


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
    """Remove stale timing files older than TTL."""
    temp_dir = get_temp_dir()
    cutoff = time.time() - (TTL_DAYS * 24 * 60 * 60)

    # Only clean up temp directory files (not reviews/.timing-data/)
    for pattern in ["skill-timing-*.json"]:
        for filepath in glob.glob(str(temp_dir / pattern)):
            try:
                if Path(filepath).stat().st_mtime < cutoff:
                    Path(filepath).unlink()
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


def print_stdout_summary(
    data: dict, checkpoints: list, tokens: dict | None, baseline: dict | None, alerts: list
):
    """Print timing summary to STDOUT."""
    print()
    print("⏱️ Timing Summary")
    print(f"├── Duration: {data['duration_human']} ({data['duration_seconds']}s)")
    print(f"├── Started:  {data['start_iso'][:19].replace('T', ' ')} UTC")
    print(f"├── Ended:    {data['end_iso'][:19].replace('T', ' ')} UTC")
    print(f"├── Run ID:   {data['run_id']}")

    if tokens:
        print(
            f"├── Tokens:   {tokens['total_tokens']:,} ({tokens['input_tokens']:,} in / {tokens['output_tokens']:,} out) ~${tokens['estimated_cost_usd']:.2f}"
        )

    if baseline:
        sign = "+" if baseline["delta_percent"] >= 0 else ""
        print(
            f"└── Baseline: {sign}{baseline['delta_percent']}% vs avg ({baseline['status'].replace('_', ' ')})"
        )
    else:
        print("└── Baseline: N/A")
        # Helpful hint on first run
        print(
            "    Tip: Set baseline after 5+ runs with: baseline set --skill <name> --mode <mode> --model <model>"
        )

    if checkpoints:
        print()
        print("Checkpoints:")
        for i, cp in enumerate(checkpoints):
            prefix = "└──" if i == len(checkpoints) - 1 else "├──"
            pct = (cp["elapsed_seconds"] / data["duration_seconds"]) * 100
            print(f"{prefix} {cp['name']:<20} {cp['elapsed_seconds']:.1f}s ({pct:.1f}%)")

    if alerts:
        print()
        for alert in alerts:
            if "error" in alert["type"]:
                print(f"❌ TIMING ERROR: {alert['message']}")
            else:
                print(f"⚠️ TIMING WARNING: {alert['message']}")

    print()


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

    # Validate run_id format before attempting file operations
    if run_id != "none" and not re.match(r"^[a-f0-9]{16}$", run_id):
        print(f"WARNING: Invalid run_id format: {run_id}")
        print("Expected: 16-character hex string (e.g., a1b2c3d4e5f67890)")
        print("Attempting registry recovery...")
        run_id = "none"  # Trigger recovery path

    timing_file = get_timing_file(run_id)

    # Agent memory recovery
    if not timing_file.exists() or run_id == "none":
        recovered_id = recover_run_id(args.skill, agent_id)
        if recovered_id:
            timing_file = get_timing_file(recovered_id)
            run_id = recovered_id
            print(f"RECOVERED_RUN_ID={recovered_id}")

    if not timing_file.exists():
        print(f"WARNING: Timing file not found for run_id={run_id}")
        print("TIMING_STATUS=missing")
        return

    data = json.loads(timing_file.read_text())
    end_epoch = time.time()
    duration_sec = end_epoch - data["start_epoch"]

    # Validate timing data
    if duration_sec < 0:
        print(f"ERROR: Negative duration detected ({duration_sec}s) - clock skew")
        print("TIMING_STATUS=error")
        timing_file.unlink()
        return

    if duration_sec < 1:
        print(f"WARNING: Duration under 1 second ({duration_sec}s) - possible race condition")
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
    if args.output_file and not Path(args.output_file).exists():
        print(f"WARNING: Output file {args.output_file} does not exist yet")
        print("Note: Timing metadata must be appended after file write completes")

    # Token tracking (optional)
    tokens = None
    if args.input_tokens > 0 or args.output_tokens > 0:
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

    # Write completed file (ensure directory exists)
    completed_file = get_completed_file(data["run_id"])
    completed_file.parent.mkdir(parents=True, exist_ok=True)
    write_timing_file(completed_file, data)

    # Cleanup
    timing_file.unlink()
    remove_from_registry(args.skill, agent_id)
    cleanup_stale_files()

    # Output
    print(f"TIMING_DURATION={data['duration_human']} ({data['duration_seconds']}s)")
    print(f"TIMING_START={data['start_iso']}")
    print(f"TIMING_END={data['end_iso']}")
    print(f"TIMING_STATUS={data['status']}")

    # STDOUT summary
    print_stdout_summary(data, data.get("checkpoints", []), tokens, baseline, alerts)


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
        print("No timing data found matching criteria.")
        return

    durations = [r["duration_seconds"] for r in runs]
    durations.sort()

    avg = sum(durations) / len(durations)
    median = durations[len(durations) // 2]
    p95_idx = int(len(durations) * 0.95)
    p95 = durations[p95_idx] if p95_idx < len(durations) else durations[-1]

    result = {
        "count": len(runs),
        "total_seconds": round(sum(durations), 2),
        "avg_seconds": round(avg, 2),
        "median_seconds": round(median, 2),
        "min_seconds": round(min(durations), 2),
        "max_seconds": round(max(durations), 2),
        "p95_seconds": round(p95, 2),
        "filters": {"skill": args.skill, "model": args.model, "days": args.days},
    }

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"Analysis written to {args.output}")
    else:
        print(f"Timing Analysis ({len(runs)} runs):")
        print(f"  Average: {format_duration(avg)} ({avg:.1f}s)")
        print(f"  Median: {format_duration(median)} ({median:.1f}s)")
        print(f"  Min: {format_duration(min(durations))} ({min(durations):.1f}s)")
        print(f"  Max: {format_duration(max(durations))} ({max(durations):.1f}s)")
        print(f"  P95: {format_duration(p95)} ({p95:.1f}s)")


def cmd_aggregate(args):
    """Aggregate timing data from review files."""
    timing_pattern = re.compile(
        r"\|\s*Run ID\s*\|\s*`([a-f0-9]+)`\s*\|.*?"
        r"\|\s*Duration\s*\|\s*(\d+m \d+s)\s*\((\d+\.?\d*)s\)\s*\|",
        re.DOTALL,
    )

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
            print(f"Warning: Could not parse {filepath}: {e}")

    Path(args.output).write_text(json.dumps(results, indent=2))
    print(f"Aggregated {len(results)} timing records to {args.output}")


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

For detailed documentation, see skills/skill-timing/README.md
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
    analyze_parser.set_defaults(func=cmd_analyze)

    # aggregate command
    aggregate_parser = subparsers.add_parser(
        "aggregate", help="Aggregate timing data from review files"
    )
    aggregate_parser.add_argument("files", nargs="*", help="Review files to parse for timing data")
    aggregate_parser.add_argument("--output", required=True, help="Output file path (JSON format)")
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
