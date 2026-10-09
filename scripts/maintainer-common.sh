#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_tool() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

require_clean() {
  local state
  state=$(git status --porcelain --untracked-files=normal)
  [[ -z "$state" ]] || fail "Uncommitted or untracked files detected. Commit or move them before release."
}

require_boolean() {
  [[ "$2" == 0 || "$2" == 1 ]] || fail "$1 must be 0 or 1."
}

require_version() {
  [[ "$1" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || fail "Expected a stable version X.Y.Z."
}

require_root() {
  local root
  root=$(git rev-parse --show-toplevel)
  [[ "$PWD" == "$root" ]] || fail "Run from the repository root."
}

require_single_push_url() {
  local urls
  urls=$(git remote get-url --push --all "$1") || fail "Remote '$1' is not configured."
  [[ -n "$urls" && "$urls" != *$'\n'* ]] || fail "Remote '$1' must have exactly one push URL."
  printf '%s\n' "$urls"
}
