#!/usr/bin/env python3
"""Timing data validation (v2.0.0+).

Thin wrapper around `skill_timer.py replay` that preserves the historical CLI
of the repo-root `scripts/validate_timing.py` (relocated into the skill in
v2.0.0). Accepts either a completed timing JSON fixture (preferred) or a
review markdown file path (legacy mode, kept for backward compatibility).

Usage:
    # Preferred: completed timing JSON fixture
    python validate_timing.py --fixture reviews/.timing-data/skill-timer-<id>-complete.json

    # Legacy: review markdown file (delegates to skill_timer.py replay using
    # the embedded timing-data/<id> path if discoverable; otherwise reports
    # the markdown file as not parseable in v2.0.0).
    python validate_timing.py reviews/rule-reviews/REVIEW_FILE.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_TIMER = SCRIPT_DIR / "skill_timer.py"


def _resolve_fixture_from_markdown(md: Path) -> Path | None:
    """Extract Run ID from review markdown and resolve to completed JSON path."""
    try:
        content = md.read_text()
    except OSError:
        return None
    m = re.search(r"\|\s*Run ID\s*\|\s*`([a-f0-9]{16})`\s*\|", content)
    if not m:
        return None
    run_id = m.group(1)
    candidate = Path("reviews/.timing-data") / f"skill-timer-{run_id}-complete.json"
    return candidate if candidate.exists() else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate timing data via skill_timer.py replay (v2.0.0+ wrapper)."
    )
    parser.add_argument(
        "--fixture",
        default=None,
        help="Path to completed timing JSON (preferred input).",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format passed through to replay.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional review markdown file(s) (legacy compat).",
    )
    args = parser.parse_args()

    targets: list[Path] = []
    if args.fixture:
        targets.append(Path(args.fixture))
    for f in args.files:
        p = Path(f)
        if p.suffix == ".json":
            targets.append(p)
            continue
        resolved = _resolve_fixture_from_markdown(p)
        if resolved is not None:
            targets.append(resolved)
        else:
            print(
                f"WARNING: {p} does not contain a discoverable Run ID or "
                f"completed JSON fixture; skipping (use --fixture for direct input).",
                file=sys.stderr,
            )

    if not targets:
        parser.print_help()
        return 1

    worst_exit = 0
    for fixture in targets:
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_TIMER),
                "replay",
                "--fixture",
                str(fixture),
                "--format",
                args.format,
            ],
            check=False,
        )
        if result.returncode > worst_exit:
            worst_exit = result.returncode
    return worst_exit


if __name__ == "__main__":
    sys.exit(main())
