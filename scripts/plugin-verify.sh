#!/usr/bin/env bash
set -euo pipefail

UV=${UV:-uv}
MODE=${1:-optional}
case "$MODE" in optional | required) ;; *)
  printf 'Expected optional or required.\n' >&2
  exit 1
  ;;
esac
if [[ "$MODE" == required ]]; then
  command -v cortex >/dev/null 2>&1 || {
    printf 'cortex is required for strict plugin verification.\n' >&2
    exit 1
  }
fi
"$UV" run --locked ai-rules plugin sync --check
BUILD_DIR=$(mktemp -d)
trap 'rm -rf -- "$BUILD_DIR"' EXIT
"$UV" run --locked ai-rules plugin build --plugin-dir "$BUILD_DIR"
"$UV" run --locked ai-rules plugin verify --plugin-dir "$BUILD_DIR"
if command -v cortex >/dev/null 2>&1; then
  cortex plugin validate "$BUILD_DIR"
else
  printf 'SKIPPED: Cortex loader validation. Use plugin:verify:strict to require it.\n'
fi
