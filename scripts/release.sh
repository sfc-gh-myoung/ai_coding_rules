#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/maintainer-common.sh"

[[ $# == 2 ]] || fail "Usage: bash scripts/release.sh bump|merge X.Y.Z"
ACTION=$1
VERSION=$2
UV=${UV:-uv}
TASK_BIN=${TASK_BIN:-task}
DRY_RUN=${DRY_RUN:-0}
require_boolean DRY_RUN "$DRY_RUN"
require_version "$VERSION"
[[ "$ACTION" == bump || "$ACTION" == merge ]] || fail "Expected bump or merge."
require_tool git
require_root
BRANCH="release/v$VERSION"
[[ $(git branch --show-current) == "$BRANCH" ]] || fail "Run from $BRANCH."
require_clean
PUSH_URL=$(require_single_push_url origin)
[[ $(git remote get-url origin) == "$PUSH_URL" ]] || fail "origin fetch and push URLs must match."
if git show-ref --verify --quiet "refs/tags/v$VERSION"; then
  fail "Tag v$VERSION already exists. Inspect the previous release before retrying."
fi

if [[ "$DRY_RUN" == 1 ]]; then
  printf 'DRY RUN: %s v%s on %s\n' "$ACTION" "$VERSION" "$BRANCH"
  if [[ "$ACTION" == bump ]]; then
    printf '%s\n' 'Update pyproject.toml, runtime version, README badge, and uv.lock.'
    printf '%s\n' 'Run uncached CI validation, create a signed commit, then push the release branch.'
  else
    printf '%s\n' 'Fetch origin, check source/version, squash in an isolated worktree without conflict overrides.'
    printf '%s\n' 'Run uncached CI, sign commit and tag, atomically push main and tag, create a draft release.'
  fi
  exit 0
fi

require_tool "$UV"
require_tool "$TASK_BIN"
if [[ "$ACTION" == merge ]]; then
  require_tool gh
  gh auth status
fi
REMOTE_TAG=$(git ls-remote --tags "$PUSH_URL" "refs/tags/v$VERSION")
[[ -z "$REMOTE_TAG" ]] || fail "Remote tag v$VERSION already exists."

if [[ "$ACTION" == bump ]]; then
  "$UV" run --locked python scripts/bump_version.py "$VERSION"
  "$TASK_BIN" --force ci
  while IFS= read -r changed; do
    case "$changed" in
      pyproject.toml | README.md | src/ai_rules/__init__.py | uv.lock) ;;
      *) fail "Unexpected changed file after validation: $changed. Review before committing." ;;
    esac
  done < <(git diff --name-only HEAD)
  [[ -z $(git ls-files --others --exclude-standard) ]] || fail "Unexpected untracked files after validation."
  git add -- pyproject.toml README.md src/ai_rules/__init__.py uv.lock
  git commit -S -m "chore: bump version to $VERSION"
  git push "$PUSH_URL" "HEAD:refs/heads/$BRANCH"
  printf 'Version bumped. Next: task release:merge VERSION=%s\n' "$VERSION"
  exit 0
fi

git fetch --no-tags origin main "$BRANCH"
git merge-base --is-ancestor main origin/main || fail "Local main has diverged from origin/main."
[[ $(git rev-parse HEAD) == "$(git rev-parse "origin/$BRANCH")" ]] || fail "Release branch differs from origin/$BRANCH."
"$UV" run --locked python scripts/bump_version.py --check "$VERSION"
SOURCE=$(git rev-parse HEAD)
TEMP_DIR=$(mktemp -d)
WORKTREE="$TEMP_DIR/release"
git worktree add --detach "$WORKTREE" origin/main
cleanup() {
  local result=$?
  if [[ "$result" == 0 ]]; then
    git worktree remove "$WORKTREE"
    rmdir "$TEMP_DIR"
  else
    printf 'Release stopped. Inspect retained worktree: %s\nSee docs/USING_DEV_CLI.md for recovery.\n' "$WORKTREE" >&2
  fi
}
trap cleanup EXIT
git -C "$WORKTREE" merge --squash "$SOURCE"
(
  cd -- "$WORKTREE"
  "$UV" run --locked python scripts/bump_version.py --check "$VERSION"
  "$TASK_BIN" --force ci
  git diff --quiet || fail "Validation changed tracked files. Review the retained worktree."
  [[ -z $(git ls-files --others --exclude-standard) ]] || fail "Validation created untracked files."
  git commit -S -m "chore: squash merge $BRANCH into main"
  git tag -s "v$VERSION" -m "Release $VERSION"
  git push --atomic "$PUSH_URL" HEAD:refs/heads/main "refs/tags/v$VERSION"
  gh release create "v$VERSION" --verify-tag --title "v$VERSION" --draft --generate-notes
)
printf 'Release v%s pushed; draft created. Local main and your checkout were not changed.\n' "$VERSION"
