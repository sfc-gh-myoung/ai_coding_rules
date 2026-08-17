#!/usr/bin/env python3
"""Atomic version bump for pyproject.toml and README.md badge.

Usage: uv run python scripts/bump_version.py <VERSION>

Extracted from src/ai_rules/commands/dev/release.py for cross-platform
use from Taskfile.yml. Uses tempfile + os.replace for atomic writes.
"""

from __future__ import annotations

import contextlib
import os
import re
import sys
import tempfile
from pathlib import Path

VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)?$")
PYPROJECT_VERSION_LINE_RE = re.compile(r'^version = "[^"]*"$', re.MULTILINE)
README_BADGE_RE = re.compile(r"badge/version-[0-9]+\.[0-9]+\.[0-9]+(?:[.-][A-Za-z0-9]+)?")


def _atomic_write(path: Path, text: str) -> None:
    """Write text to path atomically via tempfile + os.replace."""
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(directory))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _replace_pyproject_version(path: Path, version: str) -> str:
    """Return new pyproject.toml text with version replaced."""
    if not path.is_file():
        return f"ERROR: {path} not found"
    text = path.read_text(encoding="utf-8")
    matches = PYPROJECT_VERSION_LINE_RE.findall(text)
    if len(matches) != 1:
        return (
            f"ERROR: expected exactly one 'version = \"...\"' line in {path}, found {len(matches)}"
        )
    new_text = PYPROJECT_VERSION_LINE_RE.sub(f'version = "{version}"', text, count=1)
    if new_text == text:
        return f"ERROR: failed to replace version in {path}"
    return new_text


def _replace_readme_badge(path: Path, version: str) -> tuple[str | None, str | None]:
    """Return (new_text, message). new_text is None if no badge present."""
    if not path.is_file():
        return None, f"WARNING: {path} not found; skipping README badge update"
    text = path.read_text(encoding="utf-8")
    matches = README_BADGE_RE.findall(text)
    if not matches:
        return None, f"WARNING: no version badge found in {path}; skipping"
    if len(matches) > 1:
        return None, f"ERROR: expected one badge token in {path}, found {len(matches)}"
    new_text = README_BADGE_RE.sub(f"badge/version-{version}", text, count=1)
    return new_text, None


def main() -> int:
    """Bump version in pyproject.toml and README.md."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <VERSION>", file=sys.stderr)
        return 1

    version = sys.argv[1]
    if not VERSION_RE.match(version):
        print(f"ERROR: Invalid version format: {version!r}. Expected X.Y.Z", file=sys.stderr)
        return 1

    root = Path.cwd()
    pyproject = root / "pyproject.toml"
    readme = root / "README.md"

    pyproject_result = _replace_pyproject_version(pyproject, version)
    if pyproject_result.startswith("ERROR:"):
        print(pyproject_result, file=sys.stderr)
        return 1

    readme_new, readme_msg = _replace_readme_badge(readme, version)
    if readme_msg and readme_msg.startswith("ERROR:"):
        print(readme_msg, file=sys.stderr)
        return 1

    try:
        _atomic_write(pyproject, pyproject_result)
        if readme_new is not None:
            _atomic_write(readme, readme_new)
    except OSError as exc:
        print(f"ERROR: write failed: {exc}", file=sys.stderr)
        return 1

    if readme_msg:
        print(readme_msg, file=sys.stderr)
    print(f"Bumped version to {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
