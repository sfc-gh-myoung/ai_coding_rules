#!/usr/bin/env python3
"""Update release versions and lock metadata, restoring originals on failure."""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
README_BADGE_RE = re.compile(
    r"badge/version-([0-9]+\.[0-9]+\.[0-9]+(?:[.-][A-Za-z0-9]+)?)(?=-blue)"
)
VERSION_PATHS = ("pyproject.toml", "README.md", "uv.lock")


def atomic_write(path: Path, content: bytes) -> None:
    """Replace a file without exposing a partial write or changing its permissions."""
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        os.chmod(temporary, path.stat().st_mode)
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            Path(temporary).unlink()


def check_versions(root: Path, expected: str) -> None:
    """Require package, README, and editable lock entry to agree.

    ai_rules.__version__ is read from package metadata, so it is not checked here.
    """
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    lock = tomllib.loads((root / "uv.lock").read_text())
    entries = [entry for entry in lock["package"] if entry.get("source") == {"editable": "."}]
    badge = README_BADGE_RE.findall((root / "README.md").read_text())
    versions = [
        project["version"],
        *badge,
        *[entry["version"] for entry in entries],
    ]
    if len(badge) != 1 or len(entries) != 1 or any(value != expected for value in versions):
        raise ValueError(f"Version mismatch: expected {expected}, found {versions}")


def replace_one(pattern: str, replacement: str, text: str) -> str:
    """Replace exactly one authoritative version field."""
    result, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"Expected one version field, found {count}")
    return result


def bump(root: Path, version: str) -> None:
    """Update files, regenerate the lock, and roll back if any step fails."""
    originals = {name: (root / name).read_bytes() for name in VERSION_PATHS}
    project_text = originals["pyproject.toml"].decode()
    current = tomllib.loads(project_text)["project"]["version"]
    check_versions(root, current)
    if tuple(map(int, version.split("."))) <= tuple(map(int, current.split("."))):
        raise ValueError("New version must be greater than the current stable version")
    project_match = re.search(r"(?ms)^\[project\]\s*\n(.*?)(?=^\[|\Z)", project_text)
    if project_match is None:
        raise ValueError("Missing [project] section")
    project_section = replace_one(
        r'^version\s*=\s*"[^"\n]+"\s*$', f'version = "{version}"', project_match[1]
    )
    updates = {
        "pyproject.toml": project_text[: project_match.start(1)]
        + project_section
        + project_text[project_match.end(1) :],
        "README.md": README_BADGE_RE.sub(
            f"badge/version-{version}", originals["README.md"].decode()
        ),
    }
    try:
        for name, content in updates.items():
            atomic_write(root / name, content.encode())
        subprocess.run([os.environ.get("UV", "uv"), "lock"], cwd=root, check=True)
        check_versions(root, version)
    except (OSError, ValueError, subprocess.CalledProcessError):
        for name, content in originals.items():
            atomic_write(root / name, content)
        raise


def main() -> int:
    """Run a stable version bump or read-only consistency check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("version")
    arguments = parser.parse_args()
    if VERSION_RE.fullmatch(arguments.version) is None:
        parser.error("Expected a stable version X.Y.Z")
    try:
        if arguments.check:
            check_versions(Path.cwd(), arguments.version)
        else:
            bump(Path.cwd(), arguments.version)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Versions consistent at {arguments.version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
