"""Version changes are complete or rolled back, never silently partial."""

import subprocess
import sys

from scripts.bump_version import VERSION_PATHS, check_versions


def test_bump_updates_all_versions(repo, stubs):
    package_init = (repo / "src/ai_rules/__init__.py").read_bytes()
    subprocess.run(
        [sys.executable, str(repo / "scripts/bump_version.py"), "1.0.1"], cwd=repo, check=True
    )
    check_versions(repo, "1.0.1")
    assert (repo / "src/ai_rules/__init__.py").read_bytes() == package_init


def test_failed_lock_restores_every_file(repo, stubs, monkeypatch):
    originals = {name: (repo / name).read_bytes() for name in VERSION_PATHS}
    monkeypatch.setenv("FAIL_LOCK", "1")
    result = subprocess.run(
        [sys.executable, str(repo / "scripts/bump_version.py"), "1.0.1"], cwd=repo
    )
    assert result.returncode != 0
    assert originals == {name: (repo / name).read_bytes() for name in VERSION_PATHS}


def test_invalid_badge_prevents_writes(repo, stubs):
    (repo / "README.md").write_text("Missing badge")
    originals = {name: (repo / name).read_bytes() for name in VERSION_PATHS}
    result = subprocess.run(
        [sys.executable, str(repo / "scripts/bump_version.py"), "1.0.1"], cwd=repo
    )
    assert result.returncode != 0
    assert originals == {name: (repo / name).read_bytes() for name in VERSION_PATHS}
