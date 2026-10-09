"""Execute real Task commands with contained file operations and stubbed external tools."""

import json
import os
import shutil
import subprocess

import pytest
import yaml

from .conftest import ROOT, git

TASK = shutil.which("task")


def task(repo, *arguments, environment=None):
    assert TASK, "Install Task >=3.45.0 to run automation tests"
    return subprocess.run(
        [TASK, "--taskfile", str(repo / "Taskfile.yml"), *arguments],
        cwd=repo,
        env={**os.environ, **(environment or {})},
        input="",
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.mark.parametrize("invocation", [("FORCE=1",), ()])
def test_force_cli_and_environment_forms(repo, invocation):
    (repo / ".venv").mkdir()
    result = task(repo, "clean:venv", *invocation, environment={} if invocation else {"FORCE": "1"})
    assert result.returncode == 0, result.stderr
    assert not (repo / ".venv").exists()


def test_cleanup_refusal_precedes_all_deletions(repo):
    (repo / ".venv").mkdir()
    cache = repo / "src/__pycache__"
    cache.mkdir()
    (cache / "keep.pyc").write_text("cache")
    result = task(repo, "clean:all")
    assert result.returncode != 0
    assert (cache / "keep.pyc").exists()
    assert (repo / ".venv").exists()


def test_cleanup_scopes_caches_and_invalidates_task_fingerprints(repo):
    for relative in (
        "src/__pycache__",
        ".venv/__pycache__",
        "scripts/.venv/__pycache__",
        ".task",
        ".workbench/__pycache__",
    ):
        directory = repo / relative
        directory.mkdir(parents=True)
        (directory / "cache.pyc").write_text("cache")
    result = task(repo, "clean:cache")
    assert result.returncode == 0, result.stderr
    assert not (repo / "src/__pycache__").exists()
    assert not (repo / ".task").exists()
    for relative in (".venv/__pycache__", "scripts/.venv/__pycache__", ".workbench/__pycache__"):
        assert (repo / relative / "cache.pyc").exists()


def test_cleanup_invalid_force_fails_without_deletion(repo):
    (repo / ".venv").mkdir()
    result = task(repo, "clean:venv", "FORCE=yes")
    assert result.returncode != 0
    assert (repo / ".venv").exists()


def test_release_task_forwards_preview(repo, stubs):
    git(repo, "checkout", "-b", "release/v1.0.1")
    result = task(repo, "release:bump", "VERSION=1.0.1", "DRY_RUN=1")
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert git(repo, "status", "--porcelain") == ""
    calls = [json.loads(line) for line in stubs.read_text().splitlines()]
    assert all(call[0] == "git" for call in calls)


def test_release_task_requires_version(repo):
    result = task(repo, "--dry", "release:bump")
    assert result.returncode != 0
    assert "missing required variables" in result.stderr


def test_configured_uv_path_with_spaces(repo, stubs, tmp_path):
    executable = tmp_path / "uv with spaces"
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    result = task(repo, "quality:lint", f"UV={executable}")
    assert result.returncode == 0, result.stderr


def test_status_uses_configured_uv_path(repo, tmp_path):
    executable = tmp_path / "uv with spaces"
    executable.write_text(
        '#!/bin/sh\nif [ "$1" = "run" ]; then shift 5; exec python3 "$@"; fi\nprintf "custom uv\\n"\n'
    )
    executable.chmod(0o755)
    result = task(repo, "status:show", f"UV={executable}")
    assert result.returncode == 0, result.stderr
    assert "custom uv" in result.stdout


def test_ci_contract_and_no_task_fingerprints(repo, stubs):
    result = task(repo, "--dry", "ci")
    assert result.returncode == 0, result.stderr
    for command in (
        "--cov=src/ai_rules",
        "rule-loader validate",
        "audit --fail-on-miss",
        "validate-trigger-contract",
        "plugin-verify.sh",
        "ruff check",
        "ruff format --check",
    ):
        assert command in result.stderr
    definitions = yaml.safe_load((repo / "Taskfile.yml").read_text())["tasks"]
    assert "sources" not in definitions["quality:lint"]
    assert "sources" not in definitions["quality:format"]


def test_python_override_beats_inherited_environment(repo, tmp_path):
    executable = tmp_path / "uv-probe"
    executable.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    executable.chmod(0o755)
    result = task(
        repo,
        "test:run",
        f"UV={executable}",
        "PYTHON_VERSION=3.13",
        environment={"UV_PYTHON": "3.12"},
    )
    assert result.returncode == 0, result.stderr
    arguments = result.stdout.splitlines()
    assert arguments[arguments.index("--python") + 1] == "3.13"


def test_help_and_summaries_are_discoverable(repo):
    result = task(repo, "--list", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["tasks"]
    result = task(repo, "--summary", "release:merge")
    assert result.returncode == 0, result.stderr
    assert "DRY_RUN=1" in result.stdout


def test_hosted_ci_uses_shared_checks_and_python_matrix():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    test_job = workflow["jobs"]["test"]
    assert test_job["env"]["UV_PYTHON"] == "${{ matrix.python-version }}"
    steps = workflow["jobs"]["validate"]["steps"]
    commands = [step.get("run", "") for step in steps]
    assert "task validate:schemas" in commands
    assert "task validate:rule-loader" in commands
    assert "task plugin:verify" in commands
