#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/maintainer-common.sh"

DRY_RUN=${DRY_RUN:-0}
require_boolean DRY_RUN "$DRY_RUN"
require_tool git
require_root
PUSH_URL=$(require_single_push_url gitlab)
SOURCE=$(git rev-parse --verify 'refs/heads/main^{commit}')
TREE=$(git rev-parse "$SOURCE^{tree}")

if [[ "$DRY_RUN" == 1 ]]; then
  printf 'DRY RUN: mirror main commit %s, tree %s\n' "$SOURCE" "$TREE"
  printf '%s\n' 'Use a temporary index, sign a parentless commit, push gitlab/main with an explicit lease.'
  exit 0
fi

REMOTE_REF=$(git ls-remote --heads "$PUSH_URL" refs/heads/main)
EXPECTED=${REMOTE_REF%%$'\t'*}
TEMP_DIR=$(mktemp -d)
cleanup() {
  rm -rf -- "$TEMP_DIR"
}
trap cleanup EXIT
export GIT_INDEX_FILE="$TEMP_DIR/index"
git read-tree "$SOURCE"
[[ $(git write-tree) == "$TREE" ]] || fail "Mirror tree differs from selected main commit."
COMMIT=$(git commit-tree -S "$TREE" -m "mirror: main $SOURCE")
git push --force-with-lease="refs/heads/main:$EXPECTED" "$PUSH_URL" "$COMMIT:refs/heads/main"
printf 'Mirrored main %s as %s. Active checkout unchanged.\n' "$SOURCE" "$COMMIT"
