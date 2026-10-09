"""Release metadata must agree without pinning tests to a particular release."""

import tomllib
from pathlib import Path

import ai_rules
from scripts.bump_version import check_versions


def test_release_versions_are_consistent():
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    assert ai_rules.__version__ == project["version"]
    check_versions(root, project["version"])
