"""Behavioral checks against real temporary Git repositories, never external remotes."""

import json
import os
import subprocess

import pytest

from .conftest import git


def run_script(repo, script, *arguments, **environment):
    return subprocess.run(
        ["bash", str(repo / "scripts" / script), *arguments],
        cwd=repo,
        env={**os.environ, **environment},
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_release_rejects_wrong_branch(repo, stubs):
    result = run_script(repo, "release.sh", "bump", "1.0.1", DRY_RUN="1")
    assert result.returncode != 0
    assert "Run from release/v1.0.1" in result.stderr
    assert git(repo, "status", "--porcelain") == ""


@pytest.mark.parametrize("version", ["", "1.0", "01.0.0", "1.0.0 beta", "1.0.0\n"])
def test_release_rejects_invalid_version(repo, version):
    result = run_script(repo, "release.sh", "bump", version, DRY_RUN="1")
    assert result.returncode != 0
    assert "Expected a stable version" in result.stderr


def test_release_preview_does_not_call_tools_or_change_files(repo, stubs):
    git(repo, "checkout", "-b", "release/v1.0.1")
    before = git(repo, "rev-parse", "HEAD")
    result = run_script(repo, "release.sh", "bump", "1.0.1", DRY_RUN="1")
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    calls = [json.loads(line) for line in stubs.read_text().splitlines()]
    assert not any(call[0] in ("uv", "gh", "make") for call in calls)
    assert not any(call[1] in ("fetch", "push", "commit") for call in calls)
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "status", "--porcelain") == ""


def test_release_refuses_untracked_files(repo, stubs):
    git(repo, "checkout", "-b", "release/v1.0.1")
    (repo / "new.txt").write_text("Uncommitted work")
    result = run_script(repo, "release.sh", "bump", "1.0.1", DRY_RUN="1")
    assert result.returncode != 0
    assert "Uncommitted or untracked" in result.stderr


def test_mirror_uses_main_not_current_branch(repo, stubs, tmp_path):
    destination = tmp_path / "mirror.git"
    git(tmp_path, "init", "--bare", str(destination))
    git(repo, "remote", "add", "gitlab", str(destination))
    main_tree = git(repo, "rev-parse", "main^{tree}")
    git(repo, "checkout", "-b", "feature")
    (repo / "feature.txt").write_text("Not for the mirror")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Feature work")
    before = git(repo, "rev-parse", "HEAD")
    result = run_script(repo, "mirror.sh")
    assert result.returncode == 0, result.stderr
    assert git(destination, "rev-parse", "main^{tree}") == main_tree
    assert git(destination, "rev-list", "--count", "main") == "1"
    assert git(repo, "branch", "--show-current") == "feature"
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "status", "--porcelain") == ""
    calls = [json.loads(line) for line in stubs.read_text().splitlines()]
    assert any(call[1:3] == ["commit-tree", "-S"] for call in calls)
    assert any(
        argument.startswith("--force-with-lease=refs/heads/main:")
        for call in calls
        for argument in call
    )


def test_mirror_failure_preserves_checkout(repo, stubs, tmp_path):
    destination = tmp_path / "mirror.git"
    git(tmp_path, "init", "--bare", str(destination))
    git(repo, "remote", "add", "gitlab", str(destination))
    before = git(repo, "rev-parse", "HEAD")
    result = run_script(repo, "mirror.sh", FAIL_PUSH="1")
    assert result.returncode != 0
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "status", "--porcelain") == ""


def test_mirror_requires_exact_remote_name(repo):
    git(repo, "remote", "add", "not-gitlab", "/unused")
    result = run_script(repo, "mirror.sh", DRY_RUN="1")
    assert result.returncode != 0
    assert "not configured" in result.stderr


def test_bump_validates_before_signed_commit_and_push(repo, stubs):
    git(repo, "checkout", "-b", "release/v1.0.1")
    result = run_script(repo, "release.sh", "bump", "1.0.1")
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in stubs.read_text().splitlines()]
    validation = calls.index(["make", "ci"])
    commit = next(index for index, call in enumerate(calls) if call[1:3] == ["commit", "-S"])
    push = next(index for index, call in enumerate(calls) if call[1:2] == ["push"])
    assert validation < commit < push


def test_failed_bump_validation_never_commits(repo, stubs):
    git(repo, "checkout", "-b", "release/v1.0.1")
    before = git(repo, "rev-parse", "HEAD")
    result = run_script(repo, "release.sh", "bump", "1.0.1", FAIL_VALIDATION="1")
    assert result.returncode != 0
    assert git(repo, "rev-parse", "HEAD") == before


def prepare_release(repo):
    git(repo, "checkout", "-b", "release/v1.0.0")
    (repo / "release.txt").write_text("Ready for release")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Release contents")
    git(repo, "push", "origin", "HEAD")


def test_merge_uses_isolated_worktree_and_atomic_push(repo, stubs):
    prepare_release(repo)
    before = git(repo, "rev-parse", "HEAD")
    local_main = git(repo, "rev-parse", "main")
    result = run_script(repo, "release.sh", "merge", "1.0.0")
    assert result.returncode == 0, result.stderr
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "rev-parse", "main") == local_main
    assert git(repo, "branch", "--show-current") == "release/v1.0.0"
    assert git(repo, "status", "--porcelain") == ""
    assert git(repo, "worktree", "list", "--porcelain").count("worktree ") == 1
    calls = [json.loads(line) for line in stubs.read_text().splitlines()]
    assert any(call[1:3] == ["push", "--atomic"] for call in calls)
    assert any(call[1:3] == ["tag", "-s"] for call in calls)


def test_merge_failure_retains_recovery_worktree(repo, stubs):
    prepare_release(repo)
    before = git(repo, "rev-parse", "HEAD")
    result = run_script(repo, "release.sh", "merge", "1.0.0", FAIL_VALIDATION="1")
    assert result.returncode != 0
    assert "retained worktree" in result.stderr
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "worktree", "list", "--porcelain").count("worktree ") == 2
