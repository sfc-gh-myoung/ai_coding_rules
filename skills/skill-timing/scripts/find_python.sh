#!/usr/bin/env bash
# Discover a suitable Python interpreter.
# Prints the absolute path (or command name) to stdout.
# Falls back through: uv run python -> python3 -> python
#
# Usage:
#   PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
#   $PYTHON skills/skill-timing/scripts/skill_timing.py start ...

if command -v uv &> /dev/null; then
    echo "uv run python"
    exit 0
fi

if command -v python3 &> /dev/null; then
    echo "python3"
    exit 0
fi

if command -v python &> /dev/null; then
    echo "python"
    exit 0
fi

echo "ERROR: No Python interpreter found. Install Python 3.10+ or uv." >&2
exit 1
