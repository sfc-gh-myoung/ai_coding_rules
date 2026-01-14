#!/usr/bin/env bash
# Portable Python invocation wrapper for skill-timing
# Falls back through: uv -> python3 -> python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMING_SCRIPT="$SCRIPT_DIR/skill_timing.py"

# Try uv first (preferred for dependency management)
if command -v uv &> /dev/null; then
    exec uv run python "$TIMING_SCRIPT" "$@"
fi

# Fall back to python3
if command -v python3 &> /dev/null; then
    exec python3 "$TIMING_SCRIPT" "$@"
fi

# Fall back to python
if command -v python &> /dev/null; then
    exec python "$TIMING_SCRIPT" "$@"
fi

echo "ERROR: No Python interpreter found. Install Python 3.8+ or uv." >&2
exit 1
