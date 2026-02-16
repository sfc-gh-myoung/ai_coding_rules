#!/usr/bin/env bash
set -euo pipefail

clean_cache() {
    echo "Removing Python cache files..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    rm -f .coverage
}

clean_venv() {
    echo "Removing virtual environment..."
    rm -rf .venv
}

clean_all() {
    echo "Removing all generated files..."
    clean_cache
    clean_venv
    rm -rf htmlcov dist
}

show_help() {
    echo "Usage: ./dev clean:{cache|venv|all}"
}

case "${1:-}" in
    cache)
        clean_cache
        ;;
    venv)
        clean_venv
        ;;
    all)
        clean_all
        ;;
    help|-h|--help|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
