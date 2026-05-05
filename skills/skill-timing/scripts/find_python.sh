#!/usr/bin/env bash
# Discover a suitable Python interpreter and (optionally) run it.
#
# Two modes:
#
# 1) Runner mode (RECOMMENDED) — pass args; they are forwarded to Python:
#      bash skills/skill-timing/scripts/find_python.sh script.py --flag value
#
#    This works in both bash and zsh and correctly handles the
#    multi-word `uv run python` case.
#
# 2) Print mode (legacy) — no args; prints an eval-safe command string:
#      CMD=$(bash skills/skill-timing/scripts/find_python.sh)
#      eval "$CMD script.py --flag value"
#
#    NOTE: Do NOT use `$CMD script.py` directly in zsh — zsh does not
#    word-split unquoted variables, so `uv run python` would be treated
#    as a single command name. Always use `eval`.
#
# Resolution order: python3 -> python -> uv run python
#
# Single-word commands are preferred so legacy callers that assign the
# output to a variable and expand it unquoted (e.g. `$PYTHON script.py`)
# work correctly in zsh, which does not word-split unquoted variables.
# `uv run python` is kept only as a last-resort fallback for environments
# without a standalone python; callers that need it should use runner
# mode (pass args to this script) to avoid shell-splitting issues.

set -e

resolve() {
    if command -v python3 &> /dev/null; then
        echo "python3"
        return 0
    fi
    if command -v python &> /dev/null; then
        echo "python"
        return 0
    fi
    if command -v uv &> /dev/null; then
        echo "uv run python"
        return 0
    fi
    echo "ERROR: No Python interpreter found. Install Python 3.10+ or uv." >&2
    return 1
}

CMD=$(resolve)

# Runner mode: args provided -> exec with forwarded args
if [ "$#" -gt 0 ]; then
    # shellcheck disable=SC2086
    exec $CMD "$@"
fi

# Print mode: no args -> emit command string for eval
echo "$CMD"
