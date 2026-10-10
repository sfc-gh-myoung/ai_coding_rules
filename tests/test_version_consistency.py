"""Release metadata must agree without pinning tests to a particular release."""

import importlib
import importlib.metadata
import tomllib
from pathlib import Path

import ai_rules
from scripts.bump_version import check_versions


def test_release_versions_are_consistent():
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    assert ai_rules.__version__ == project["version"]
    check_versions(root, project["version"])


def test_runtime_version_comes_from_package_metadata():
    assert ai_rules.__version__ == importlib.metadata.version("ai_coding_rules")


def test_missing_metadata_falls_back(monkeypatch):
    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    try:
        assert importlib.reload(ai_rules).__version__ == "0.0.0+unknown"
    finally:
        monkeypatch.undo()
        importlib.reload(ai_rules)
