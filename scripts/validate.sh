#!/usr/bin/env bash
set -euo pipefail

# Auto-detect UV
UV=$(command -v uv || echo "uv")
PYTHON="$UV run python"

# Auto-detect UVX
UVX=$(command -v uvx || echo "uvx")

echo "=== Step 1/5: Quality checks ==="
$UV run ruff check .
$UV run ruff format --check .
$UV run ty check .
$UVX pymarkdownlnt --config pymarkdown.rules.json scan rules/ templates/AGENTS_MODE.md.template templates/AGENTS_NO_MODE.md.template PROJECT.md
$UVX pymarkdownlnt --config pymarkdown.docs.json scan docs/ README.md CONTRIBUTING.md CHANGELOG.md

echo "=== Step 2/5: Tests ==="
$UV run pytest tests/ --tb=short

echo "=== Step 3/5: Rules validation ==="
$PYTHON scripts/schema_validator.py rules/

echo "=== Step 4/5: Examples validation ==="
$PYTHON scripts/schema_validator.py rules/examples/ --examples

echo "=== Step 5/5: Index check ==="
$PYTHON scripts/index_generator.py --check

echo ""
echo "All validation checks passed."
