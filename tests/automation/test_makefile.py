"""Execute real make targets with contained file operations and stubbed external tools.

No test here performs a real push, tag, release, or cleanup outside
the disposable repository built by the `repo` fixture.
"""

import json
import os
import re
import shutil
import subprocess

import pytest
import yaml

from .conftest import ROOT, git

# Resolved before the `stubs` fixture prepends its fake `make` to PATH.
MAKE = shutil.which("make")

VALIDATE_GATES = (
    "lock --check",
    "ruff check .",
    "ruff format --check .",
    "ty check .",
    "pymarkdownlnt",
    "shellcheck",
    "shfmt -d",
    "--cov=src/ai_rules",
    "ai-rules validate rules/",
    "ai-rules validate-skills skills/",
    "rule-loader validate",
    "audit --fail-on-miss",
    "validate-trigger-contract",
    "plugin-verify.sh optional",
)


def caller_environment():
    """The caller's environment minus exported shell functions (``BASH_FUNC_*``).

    An exported function such as ``cortex`` would satisfy ``command -v`` in make
    recipes and defeat missing-tool preflights, so the harness drops them itself.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith("BASH_FUNC_")}


def make(repo, *arguments, environment=None):
    assert MAKE, "GNU Make is required to run automation tests"
    return subprocess.run(
        [MAKE, *arguments],
        cwd=repo,
        env={**caller_environment(), **(environment or {})},
        input="",
        capture_output=True,
        text=True,
        timeout=60,
    )


def executable(tmp_path, name, body):
    path = tmp_path / name
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)
    return path


def argument_probe(tmp_path):
    """A uv stand-in that prints one received argument per line."""
    return executable(tmp_path, "uv probe", 'printf "%s\\n" "$@"\n')


def python_runner(tmp_path):
    """A uv stand-in that runs `uv run --locked --python X python ...` with python3."""
    return executable(
        tmp_path,
        "uv with spaces",
        'if [ "$1" = "run" ]; then shift 5; exec python3 "$@"; fi\nprintf "custom uv\\n"\n',
    )


def logged(stubs):
    return [json.loads(line) for line in stubs.read_text().splitlines()] if stubs.exists() else []


@pytest.mark.parametrize("invocation", [("FORCE=1",), ()])
def test_force_cli_and_environment_forms(repo, invocation):
    (repo / ".venv").mkdir()
    result = make(repo, "clean-venv", *invocation, environment={} if invocation else {"FORCE": "1"})
    assert result.returncode == 0, result.stderr
    assert not (repo / ".venv").exists()


def test_cleanup_refusal_precedes_all_deletions(repo):
    (repo / ".venv").mkdir()
    cache = repo / "src/__pycache__"
    cache.mkdir()
    (cache / "keep.pyc").write_text("cache")
    result = make(repo, "clean-all")
    assert result.returncode != 0
    assert "Refusing cleanup without confirmation" in result.stderr
    assert (cache / "keep.pyc").exists()
    assert (repo / ".venv").exists()


def test_cleanup_scopes_caches(repo):
    for relative in (
        "src/__pycache__",
        ".venv/__pycache__",
        "scripts/.venv/__pycache__",
        ".workbench/__pycache__",
    ):
        directory = repo / relative
        directory.mkdir(parents=True)
        (directory / "cache.pyc").write_text("cache")
    result = make(repo, "clean-cache")
    assert result.returncode == 0, result.stderr
    assert not (repo / "src/__pycache__").exists()
    for relative in (".venv/__pycache__", "scripts/.venv/__pycache__", ".workbench/__pycache__"):
        assert (repo / relative / "cache.pyc").exists()


def test_cleanup_invalid_force_fails_without_deletion(repo):
    (repo / ".venv").mkdir()
    result = make(repo, "clean-venv", "FORCE=yes")
    assert result.returncode != 0
    assert (repo / ".venv").exists()


@pytest.mark.parametrize("target", ["clean-all", "clean-venv", "clean-cache"])
def test_dry_run_never_deletes(repo, target):
    (repo / ".venv").mkdir()
    (repo / "src/__pycache__").mkdir()
    result = make(repo, "-n", target, "FORCE=1")
    assert result.returncode == 0, result.stderr
    assert (repo / ".venv").exists()
    assert (repo / "src/__pycache__").exists()


@pytest.mark.parametrize(
    ("target", "action"), [("release-bump", "bump"), ("release-merge", "merge")]
)
def test_release_targets_forward_preview(repo, stubs, target, action):
    git(repo, "checkout", "-b", "release/v1.0.1")
    before = git(repo, "rev-parse", "HEAD")
    result = make(repo, target, "VERSION=1.0.1", "DRY_RUN=1")
    assert result.returncode == 0, result.stderr
    assert f"DRY RUN: {action} v1.0.1" in result.stdout
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "status", "--porcelain") == ""
    calls = logged(stubs)
    assert all(call[0] == "git" for call in calls)
    assert not any(call[1] in ("fetch", "push", "commit", "tag") for call in calls)


@pytest.mark.parametrize("target", ["release-bump", "release-merge"])
@pytest.mark.parametrize("dry", [("-n",), ()])
def test_release_targets_require_version(repo, stubs, target, dry):
    result = make(repo, *dry, target)
    assert result.returncode != 0
    assert "VERSION is required" in result.stderr
    assert logged(stubs) == []


@pytest.mark.parametrize("target", ["release-bump", "release-merge"])
def test_make_dry_run_never_runs_release_script(repo, stubs, target):
    git(repo, "checkout", "-b", "release/v1.0.1")
    before = logged(stubs)
    result = make(repo, "-n", target, "VERSION=1.0.1")
    assert result.returncode == 0, result.stderr
    assert f"scripts/release.sh {target.split('-')[1]} '1.0.1'" in result.stdout
    assert logged(stubs) == before


def test_release_invalid_dry_run_value_fails(repo, stubs):
    git(repo, "checkout", "-b", "release/v1.0.1")
    result = make(repo, "release-bump", "VERSION=1.0.1", "DRY_RUN=yes")
    assert result.returncode != 0
    assert "DRY_RUN must be 0 or 1" in result.stderr
    assert not any(call[1] in ("push", "commit") for call in logged(stubs))


def test_configured_uv_path_with_spaces(repo, tmp_path):
    uv = executable(tmp_path, "uv with spaces", "exit 0\n")
    result = make(repo, "quality-lint", f"UV={uv}")
    assert result.returncode == 0, result.stderr


def test_status_uses_configured_uv_path(repo, tmp_path):
    result = make(repo, "status", f"UV={python_runner(tmp_path)}")
    assert result.returncode == 0, result.stderr
    assert "custom uv" in result.stdout
    assert "GNU Make" in result.stdout
    assert "Rules:" in result.stdout


def test_ci_alias_runs_validate_gates_in_order(repo):
    validate = make(repo, "-n", "validate")
    ci = make(repo, "-n", "ci")
    assert validate.returncode == 0, validate.stderr
    assert ci.returncode == 0, ci.stderr
    assert ci.stdout == validate.stdout
    positions = [validate.stdout.find(gate) for gate in VALIDATE_GATES]
    assert -1 not in positions, dict(zip(VALIDATE_GATES, positions, strict=True))
    assert positions == sorted(positions)


def test_validate_stops_at_first_failing_gate(repo, tmp_path):
    uv = executable(
        tmp_path, "uv-fails-lint", 'case "$*" in *"ruff check"*) exit 3;; esac\necho "ran: $*"\n'
    )
    result = make(repo, "validate", f"UV={uv}")
    assert result.returncode != 0
    assert "ran: lock --check" in result.stdout
    assert "ruff format" not in result.stdout
    assert "--cov" not in result.stdout


@pytest.mark.parametrize(
    ("arguments", "environment", "expected"),
    [
        ((), {}, "3.12"),
        ((), {"UV_PYTHON": "3.13"}, "3.13"),
        (("UV_PYTHON=3.13",), {}, "3.13"),
        (("PYTHON_VERSION=3.13",), {"UV_PYTHON": "3.12"}, "3.13"),
    ],
)
def test_python_version_overrides(repo, tmp_path, arguments, environment, expected):
    result = make(
        repo, "test-run", f"UV={argument_probe(tmp_path)}", *arguments, environment=environment
    )
    assert result.returncode == 0, result.stderr
    received = result.stdout.splitlines()
    assert received[received.index("--python") + 1] == expected


def test_cli_args_pass_through_to_pytest(repo, tmp_path):
    result = make(repo, "test-run", f"UV={argument_probe(tmp_path)}", "CLI_ARGS=-k version_bump -x")
    assert result.returncode == 0, result.stderr
    received = result.stdout.splitlines()
    assert received[received.index("--tb=short") + 1 :] == ["-k", "version_bump", "-x"]


def test_missing_uv_fails_before_running_anything(repo, tmp_path):
    result = make(repo, "quality-lint", f"UV={tmp_path / 'missing-uv'}")
    assert result.returncode != 0
    assert "uv not found" in result.stderr
    assert "ruff" not in result.stdout


@pytest.mark.parametrize(
    ("target", "message"),
    [
        ("quality-automation", "Install ShellCheck"),
        ("plugin-verify-strict", "Cortex CLI is required"),
    ],
)
def test_tool_preflights_fail_without_tools(repo, tmp_path, target, message):
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    uv = argument_probe(tmp_path)
    result = make(repo, target, f"UV={uv}", environment={"PATH": str(empty)})
    assert result.returncode != 0
    assert message in result.stderr
    assert "plugin-verify.sh" not in result.stdout


def test_exported_cortex_function_cannot_defeat_strict_preflight(repo, tmp_path, monkeypatch):
    sentinel = tmp_path / "cortex-function-ran"
    # Simulates `export -f cortex` in the caller; bash imports BASH_FUNC_<name>%%.
    monkeypatch.setenv("BASH_FUNC_cortex%%", f'() {{ /usr/bin/touch "{sentinel}"; }}')
    uv = argument_probe(tmp_path)
    result = make(repo, "plugin-verify-strict", f"UV={uv}", environment={"PATH": "/usr/bin:/bin"})
    assert result.returncode != 0
    assert "Cortex CLI is required" in result.stderr
    assert not sentinel.exists()


def plugin_verify(tmp_path, scratch_root, fail_step=None, extra_bin=None):
    """Run scripts/plugin-verify.sh with stub uv/cortex; return (result, logged calls).

    Each logged call is (step, plugin-dir) where step is the uv plugin subcommand
    or "validate" for `cortex plugin validate`.
    """
    stub_bin = tmp_path / "pv-bin"
    stub_bin.mkdir(exist_ok=True)
    log = tmp_path / "pv.log"
    uv = executable(
        stub_bin,
        "uv",
        'printf "%s\\t%s\\n" "$5" "$7" >>"$PV_LOG"\n'
        '[ "$5" = build ] && : >"$7/built"\n'
        '[ "$5" = "$PV_FAIL" ] && exit 3\nexit 0\n',
    )
    executable(stub_bin, "cortex", 'printf "validate\\t%s\\n" "$3" >>"$PV_LOG"\n')
    path = f"{stub_bin}:/usr/bin:/bin"
    if extra_bin:
        path = f"{extra_bin}:{path}"
    environment = {
        **caller_environment(),
        "PATH": path,
        "UV": str(uv),
        "TMPDIR": scratch_root,
        "PV_LOG": str(log),
        "PV_FAIL": fail_step or "",
    }
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "plugin-verify.sh"), "optional"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    calls = (
        [tuple(line.split("\t")) for line in log.read_text().splitlines()] if log.exists() else []
    )
    return result, calls


@pytest.mark.parametrize("suffix", ["", "/"])
def test_plugin_verify_builds_beneath_tmpdir_and_cleans_only_its_build(tmp_path, suffix):
    scratch = tmp_path / "scratch with spaces"
    scratch.mkdir()
    sentinel = scratch / "sibling-sentinel"
    sentinel.write_text("keep")
    result, calls = plugin_verify(tmp_path, f"{scratch}{suffix}")
    assert result.returncode == 0, result.stderr
    assert [step for step, _ in calls] == ["sync", "build", "verify", "validate"]
    build = {directory for step, directory in calls if step != "sync"}
    assert len(build) == 1
    build_dir = build.pop()
    assert os.path.dirname(build_dir) == str(scratch)
    assert os.path.basename(build_dir).startswith("plugin-verify.")
    assert not os.path.exists(build_dir)
    assert sentinel.read_text() == "keep"
    assert sorted(p.name for p in scratch.iterdir()) == ["sibling-sentinel"]


def test_plugin_verify_command_failure_removes_only_its_build(tmp_path):
    scratch = tmp_path / "scratch with spaces"
    scratch.mkdir()
    sentinel = scratch / "sibling-sentinel"
    sentinel.write_text("keep")
    result, calls = plugin_verify(tmp_path, str(scratch), fail_step="verify")
    assert result.returncode == 3
    assert [step for step, _ in calls] == ["sync", "build", "verify"]
    assert not os.path.exists(calls[1][1])
    assert sorted(p.name for p in scratch.iterdir()) == ["sibling-sentinel"]


def test_plugin_verify_allocation_failure_does_not_fall_back(tmp_path):
    missing = tmp_path / "scratch with spaces" / "absent"
    result, calls = plugin_verify(tmp_path, str(missing))
    assert result.returncode != 0
    assert [step for step, _ in calls] == ["sync"]
    assert not missing.exists()


def test_plugin_verify_passes_explicit_template_to_mktemp(tmp_path):
    # Controlled allocation stub: records arguments and allocates under scratch.
    scratch = tmp_path / "scratch with spaces"
    scratch.mkdir()
    fake = tmp_path / "fake-mktemp"
    fake.mkdir()
    record = tmp_path / "mktemp-args"
    executable(
        fake,
        "mktemp",
        f'printf "%s\\n" "$@" >"{record}"\n/usr/bin/mktemp -d "{scratch}/stub.XXXXXX"\n',
    )
    result, _ = plugin_verify(tmp_path, str(scratch), extra_bin=fake)
    assert result.returncode == 0, result.stderr
    assert record.read_text().splitlines() == ["-d", f"{scratch}/plugin-verify.XXXXXX"]


def test_status_preflight_requires_lockfile(repo, tmp_path):
    (repo / "uv.lock").unlink()
    result = make(repo, "status-preflight", f"UV={argument_probe(tmp_path)}")
    assert result.returncode != 0
    assert "pyproject.toml and uv.lock must exist" in result.stderr
    assert "--check" not in result.stdout


ESCAPE = "\x1b["


def test_default_goal_prints_plain_categorized_help_without_uv(repo, tmp_path):
    result = make(repo, f"UV={tmp_path / 'missing-uv'}", environment={"NO_COLOR": ""})
    assert result.returncode == 0, result.stderr
    assert ESCAPE not in result.stdout
    assert result.stdout.startswith("AI Coding Rules 1.0.0 (")
    for heading in ("Quickstart", "Environment", "Quality", "Testing", "Validation", "Release"):
        assert f"\n{heading}\n" in result.stdout
    documented = re.findall(
        r"^([a-z][a-z0-9-]*):[^=\n]*? ## ", (repo / "Makefile").read_text(), re.M
    )
    for target in documented:
        assert f"\n  {target} " in result.stdout
    assert "inputs: VERSION=X.Y.Z [DRY_RUN=1]" in result.stdout


@pytest.mark.parametrize(
    ("environment", "colored"),
    [
        ({}, False),
        ({"TERM": "dumb"}, False),
        ({"FORCE_COLOR": "1"}, True),
        ({"CLICOLOR_FORCE": "1"}, True),
        ({"FORCE_COLOR": "1", "NO_COLOR": "1"}, False),
    ],
)
def test_help_color_rules_when_piped(repo, environment, colored):
    result = make(repo, "help", environment={"NO_COLOR": "", **environment})
    assert result.returncode == 0, result.stderr
    assert (ESCAPE in result.stdout) is colored


def test_bare_make_changes_nothing_and_works_from_another_directory(repo, tmp_path):
    before = sorted(path.name for path in repo.iterdir())
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    for arguments in ((), ("-C", str(repo)), ("-f", str(repo / "Makefile"))):
        result = make(elsewhere if arguments else repo, *arguments, "help")
        assert result.returncode == 0, result.stderr
        assert "make validate" in result.stdout
    assert sorted(path.name for path in repo.iterdir()) == before
    assert list(elsewhere.iterdir()) == []


def test_error_messages_are_plain_when_piped_and_colored_when_forced(repo, tmp_path):
    arguments = ("status-preflight", f"UV={argument_probe(tmp_path)}")
    (repo / "uv.lock").unlink()
    plain = make(repo, *arguments, environment={"NO_COLOR": ""})
    forced = make(repo, *arguments, environment={"FORCE_COLOR": "1"})
    assert ESCAPE not in plain.stderr
    assert ESCAPE in forced.stderr
    missing = make(repo, "release-bump", environment={"FORCE_COLOR": "1"})
    assert "VERSION is required" in missing.stderr
    assert ESCAPE in missing.stderr


def test_quality_makefile_flags_undocumented_and_unphony_targets(repo):
    assert make(repo, "quality-makefile").returncode == 0
    with (repo / "Makefile").open("a") as handle:
        handle.write("\nstray:\n\t@true\n")
    result = make(repo, "quality-makefile")
    assert result.returncode != 0
    assert "No ## description: stray" in result.stdout
    assert "Missing from .PHONY: stray" in result.stdout


def test_no_target_installs_or_selects_python_311(repo):
    makefile = (ROOT / "Makefile").read_text()
    assert "3.11" not in makefile
    result = make(repo, "-n", "env-setup")
    assert result.returncode == 0, result.stderr
    assert "python install '3.12'" in result.stdout
    assert "3.11" not in result.stdout


def test_hosted_ci_uses_only_make_entry_points():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert workflow["jobs"]["test"]["env"]["UV_PYTHON"] == "${{ matrix.python-version }}"
    automation = workflow["jobs"]["automation"]["strategy"]["matrix"]
    assert set(automation["os"]) == {"ubuntu-latest", "macos-latest"}
    assert set(automation["python-version"]) == {"3.12", "3.13"}
    steps = [step for job in workflow["jobs"].values() for step in job["steps"]]
    assert not any("setup-task" in step.get("uses", "") for step in steps)
    commands = [step["run"] for step in steps if "run" in step]
    assert not any(re.search(r"\btask\b", command) for command in commands)
    validate = [step.get("run", "") for step in workflow["jobs"]["validate"]["steps"]]
    for command in ("make validate-schemas", "make validate-rule-loader", "make plugin-verify"):
        assert command in validate
