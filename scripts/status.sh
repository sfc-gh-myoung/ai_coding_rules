#!/usr/bin/env bash
set -euo pipefail

# Auto-detect UV
UV=$(command -v uv || echo "uv")

# Extract project version from pyproject.toml
PROJECT_VERSION=$(awk -F'"' '/^version = "/ {print $2; exit}' pyproject.toml 2>/dev/null || echo "unknown")

# Count rules and tests
RULES_COUNT=$(find rules -name '*.md' | wc -l | tr -d ' ')
TESTS_COUNT=$(find tests -name 'test_*.py' | wc -l | tr -d ' ')

# Print header
echo "AI Coding Rules v${PROJECT_VERSION} - Production-Ready Rules Architecture"
echo ""
echo "Rules: rules/ (${RULES_COUNT} files)"
echo "Tests: ${TESTS_COUNT} test files"
echo ""

# Check linting
if $UV run ruff check . >/dev/null 2>&1; then
    echo "✓ Linting passed"
else
    echo "✗ Linting issues (run: ./dev lint:fix)"
fi

# Check formatting
if $UV run ruff format --check . >/dev/null 2>&1; then
    echo "✓ Formatting passed"
else
    echo "✗ Formatting issues (run: ./dev format:fix)"
fi

# Check type checking
if $UV run ty check . >/dev/null 2>&1; then
    echo "✓ Type checking passed"
else
    echo "✗ Type checking issues (run: ./dev typecheck)"
fi
