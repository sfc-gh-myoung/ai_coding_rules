#!/usr/bin/env bash
set -euo pipefail

MODE=${1:?Expected cache, venv, or all}
FORCE=${FORCE:-0}
[[ "$FORCE" == 0 || "$FORCE" == 1 ]] || {
  printf 'FORCE must be 0 or 1.\n' >&2
  exit 1
}
case "$MODE" in cache | venv | all) ;; *)
  printf 'Expected cache, venv, or all.\n' >&2
  exit 1
  ;;
esac
[[ -f Taskfile.yml && -f pyproject.toml ]] || {
  printf 'Run from the project root.\n' >&2
  exit 1
}

if [[ "$MODE" != cache && "$FORCE" != 1 ]]; then
  [[ -t 0 ]] || {
    printf 'Refusing cleanup without confirmation. Pass FORCE=1.\n' >&2
    exit 1
  }
  printf 'Remove %s? [y/N] ' "$MODE"
  read -r answer
  case "$answer" in y | Y | yes | YES) ;; *)
    printf 'Aborted.\n'
    exit 1
    ;;
  esac
fi

if [[ "$MODE" != venv ]]; then
  for directory in src tests scripts skills; do
    [[ ! -L "$directory" ]] || {
      printf 'Refusing symlinked source directory: %s\n' "$directory" >&2
      exit 1
    }
    [[ -d "$directory" ]] || continue
    find "$directory" -type d \( -name .venv -o -name venv -o -name node_modules -o -name .git \) -prune -o \
      -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf -- {} +
    find "$directory" -type d \( -name .venv -o -name venv -o -name node_modules -o -name .git \) -prune -o \
      -type f -name '*.pyc' -exec rm -f -- {} +
  done
  rm -rf -- .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage .coverage.* .task
fi
if [[ "$MODE" != cache ]]; then
  rm -rf -- .venv
fi
printf 'Cleanup complete: %s\n' "$MODE"
