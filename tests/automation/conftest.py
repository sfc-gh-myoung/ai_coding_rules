"""Isolated repositories and command stubs for maintainer automation tests."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo with spaces"
    root.mkdir()
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Automation Test")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "automation@example.invalid")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Automation Test")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "automation@example.invalid")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", os.devnull)
    for variable in ("DRY_RUN", "FORCE", "UV", "TASK_BIN", "GIT_INDEX_FILE"):
        monkeypatch.delenv(variable, raising=False)
    for relative in ("Taskfile.yml", "scripts"):
        source = ROOT / relative
        if source.is_dir():
            shutil.copytree(source, root / relative, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(source, root / relative)
    (root / "pyproject.toml").write_text('[project]\nname = "sample"\nversion = "1.0.0"\n')
    (root / "README.md").write_text("badge/version-1.0.0-blue\n")
    (root / "src/ai_rules").mkdir(parents=True)
    (root / "src/ai_rules/__init__.py").write_text('__version__ = "1.0.0"\n')
    (root / "uv.lock").write_text(
        'version = 1\n[[package]]\nname = "sample"\nversion = "1.0.0"\n'
        'source = { editable = "." }\n'
    )
    (root / ".gitignore").write_text(".venv/\n.task/\n__pycache__/\n.pytest_cache/\n")
    git(root, "init", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-m", "Initial tree")
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "--bare", str(origin))
    git(root, "remote", "add", "origin", str(origin))
    git(root, "push", "origin", "main")
    return root


def git(root, *arguments):
    return subprocess.run(
        ["git", *arguments], cwd=root, text=True, capture_output=True, check=True
    ).stdout.strip()


@pytest.fixture
def stubs(tmp_path, monkeypatch):
    binaries = tmp_path / "bin"
    binaries.mkdir()
    log = tmp_path / "commands.jsonl"
    real_git = shutil.which("git")
    monkeypatch.setenv("AUTOMATION_LOG", str(log))
    monkeypatch.setenv("REAL_GIT", real_git)
    script = """#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys
command = pathlib.Path(sys.argv[0]).name
arguments = sys.argv[1:]
with open(os.environ["AUTOMATION_LOG"], "a") as stream:
    stream.write(json.dumps([command, *arguments]) + "\\n")
if command == "git":
    if os.environ.get("FAIL_PUSH") == "1" and "push" in arguments:
        sys.exit(1)
    arguments = [argument for argument in arguments if argument not in ("-S", "-s")]
    sys.exit(subprocess.call([os.environ["REAL_GIT"], *arguments]))
if command == "task":
    sys.exit(int(os.environ.get("FAIL_VALIDATION", "0")))
if command == "uv":
    if "python" in arguments:
        start = arguments.index("python") + 1
        sys.exit(subprocess.call([sys.executable, *arguments[start:]]))
    if "lock" in arguments:
        if os.environ.get("FAIL_LOCK") == "1":
            sys.exit(1)
        import tomllib
        version = tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["version"]
        lock = pathlib.Path("uv.lock")
        lock.write_text('version = 1\\n[[package]]\\nname = "sample"\\nversion = "' + version + '"\\nsource = { editable = "." }\\n')
sys.exit(0)
"""
    for name in ("git", "uv", "task", "gh", "cortex"):
        binary = binaries / name
        binary.write_text(script)
        binary.chmod(0o755)
    monkeypatch.setenv("PATH", str(binaries) + os.pathsep + os.environ["PATH"])
    return log
