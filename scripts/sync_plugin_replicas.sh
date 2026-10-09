#!/usr/bin/env bash
# Regenerate tracked plugin replicas from their primaries, then re-stage them.
#
# The plugin ships as a self-contained directory without src/, so the matcher
# necessarily exists twice: once as an importable module, once as the standalone
# script the plugin carries. The second copy is generated output.
#
# This hook exists because the copy previously had no writer at all. Drift was
# authored by hand and only caught by a CI step that runs on pushes to main, so a
# stale replica could sit committed on a feature branch indefinitely.
#
# Behaviour mirrors `ruff --fix`: fix the problem, stage the fix, then fail the
# commit so the author reviews what changed rather than having it slip in silently.
#
# Exit codes: 0 replicas already in sync; 1 replicas were regenerated (commit
# blocked for review) or the sync itself failed.

set -euo pipefail

if uv run ai-rules plugin sync --check >/dev/null 2>&1; then
    exit 0
fi

echo "Plugin replicas are out of sync with their primaries."
echo

if ! uv run ai-rules plugin sync; then
    echo
    echo "ERROR: 'ai-rules plugin sync' failed. Resolve the error above, then retry." >&2
    exit 1
fi

# Read the replica paths from the manifest rather than hardcoding them, so adding
# a replica to REPO_REPLICAS extends this hook automatically.
replicas="$(uv run python -c 'from ai_rules.plugin.replicas import REPO_REPLICAS
print("\n".join(r.replica for r in REPO_REPLICAS))')"

staged_any=0
while IFS= read -r replica; do
    [ -n "$replica" ] || continue
    if git add -- "$replica"; then
        echo "  staged: $replica"
        staged_any=1
    fi
done <<<"$replicas"

echo
if [ "$staged_any" -eq 1 ]; then
    echo "Replicas were regenerated and staged. Review the changes, then commit again."
else
    echo "Replicas were regenerated but could not be staged. Stage them manually." >&2
fi

exit 1
