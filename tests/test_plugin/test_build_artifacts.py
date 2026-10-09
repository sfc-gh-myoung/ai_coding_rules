"""Tests for the plugin build artifact contract.

Guards the contract defined by ``EXPECTED_ARTIFACTS`` and ``EXPECTED_TREES`` in
``ai_rules.commands.plugin``. The regression these tests exist to prevent: a
component is documented as shipped but no build step emits it, so it survives
only as a stray tracked file and vanishes on the next clean build.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.commands.plugin import (
    EXPECTED_ARTIFACTS,
    EXPECTED_TREES,
    REQUIRED_MANIFEST_KEYS,
    _check_copy_content,
    check_artifacts,
    check_manifest,
    plugin_app,
)
from ai_rules.plugin.replicas import BUILD_COPIES, REPO_REPLICAS

REPO_ROOT = Path(__file__).resolve().parents[2]

runner = CliRunner()


@pytest.fixture(scope="module")
def built_plugin(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the plugin once into a clean temp dir for the whole module.

    Args:
        tmp_path_factory: pytest factory for module-scoped temp dirs.

    Returns:
        Path to the freshly built plugin directory.
    """
    out = tmp_path_factory.mktemp("plugin_build")
    result = runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)])
    assert result.exit_code == 0, f"build failed: {result.output}"
    return out


def test_build_emits_show_rules(built_plugin: Path) -> None:
    """The build emits show-rules, matching the canonical source byte-for-byte."""
    emitted = built_plugin / "skills" / "show-rules" / "SKILL.md"
    source = REPO_ROOT / "skills" / "show-rules" / "SKILL.md"

    assert source.is_file(), "canonical source skills/show-rules/SKILL.md is missing"
    assert emitted.is_file(), "build did not emit skills/show-rules/SKILL.md"
    assert emitted.read_bytes() == source.read_bytes()


def test_expected_artifacts_all_present(built_plugin: Path) -> None:
    """Every declared artifact exists after a clean build (declared subset of emitted)."""
    missing = [rel for rel in EXPECTED_ARTIFACTS if not (built_plugin / rel).is_file()]
    assert missing == [], f"declared but not emitted: {missing}"

    missing_trees = [tree for tree in EXPECTED_TREES if not (built_plugin / tree).is_dir()]
    assert missing_trees == [], f"declared trees not emitted: {missing_trees}"


def test_no_undeclared_output(built_plugin: Path) -> None:
    """Every emitted file is accounted for (emitted subset of declared).

    This is the direction that catches a new copy step added to the build without
    a corresponding contract entry: the copy-map drift guard.
    """
    declared = set(EXPECTED_ARTIFACTS)
    undeclared = [
        p.relative_to(built_plugin).as_posix()
        for p in built_plugin.rglob("*")
        if p.is_file()
        and p.name != ".DS_Store"
        and p.relative_to(built_plugin).as_posix() not in declared
        and not any(
            p.relative_to(built_plugin).as_posix().startswith(f"{tree}/") for tree in EXPECTED_TREES
        )
    ]
    assert undeclared == [], f"emitted but not declared: {undeclared}"


def test_check_artifacts_passes_on_clean_build(built_plugin: Path) -> None:
    """The shared checker reports no problems for a clean build (positive control)."""
    assert check_artifacts(built_plugin) == []


def test_verify_command_succeeds_on_clean_build(built_plugin: Path) -> None:
    """`plugin verify` exits 0 on a clean build."""
    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(built_plugin)])
    assert result.exit_code == 0, result.output


def test_verify_fails_on_missing_artifact(tmp_path: Path) -> None:
    """`plugin verify` exits non-zero and names the artifact when one is removed."""
    out = tmp_path / "plugin"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    (out / "skills" / "show-rules" / "SKILL.md").unlink()

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert "skills/show-rules/SKILL.md" in result.output


def test_verify_fails_on_undeclared_output(tmp_path: Path) -> None:
    """`plugin verify` exits non-zero when the build tree gains an unregistered file."""
    out = tmp_path / "plugin"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    stray = out / "skills" / "retired-skill" / "SKILL.md"
    stray.parent.mkdir(parents=True, exist_ok=True)
    stray.write_text("stale\n", encoding="utf-8")

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert "undeclared output" in result.output
    assert "skills/retired-skill/SKILL.md" in result.output


def test_build_cleans_stale_undeclared_output(tmp_path: Path) -> None:
    """A rebuild removes files that are no longer declared by the artifact contract."""
    out = tmp_path / "plugin"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    stale = out / "docs" / "plugin-rule-path-contract.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale\n", encoding="utf-8")
    assert any("undeclared output" in p for p in check_artifacts(out))

    result = runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)])

    assert result.exit_code == 0, result.output
    assert not stale.exists()
    assert check_artifacts(out) == []


@pytest.mark.parametrize("manifest_dir", [".cortex-plugin", ".claude-plugin"])
def test_verify_fails_on_invalid_manifest(tmp_path: Path, manifest_dir: str) -> None:
    """`plugin verify` exits non-zero when a generated manifest is not valid JSON."""
    out = tmp_path / "plugin"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    (out / manifest_dir / "plugin.json").write_text("{ not json", encoding="utf-8")

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert f"invalid {manifest_dir}/plugin.json" in result.output


def test_generated_manifest_is_valid_json(built_plugin: Path) -> None:
    """The generated cortex manifest parses and declares the skills directory."""
    manifest = json.loads(
        (built_plugin / ".cortex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "ai-coding-rules"
    assert "./skills" in manifest["skills"]


def test_generated_claude_manifest_is_valid_json(built_plugin: Path) -> None:
    """The generated claude manifest parses and carries identity keys only.

    Claude Code auto-discovers skills/ and hooks/hooks.json, so declaring either
    in the manifest is at best redundant and at worst a second source of truth.
    """
    manifest = json.loads(
        (built_plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "ai-coding-rules"
    assert "skills" not in manifest
    assert "hooks" not in manifest


def test_rules_tree_matches_source(built_plugin: Path) -> None:
    """Built rules match source by filename set and by content, not merely by count."""
    source_rules = {p.name: p for p in (REPO_ROOT / "rules").glob("*.md")}
    built_rules = {p.name: p for p in (built_plugin / "rules").glob("*.md")}

    assert set(built_rules) == set(source_rules), "rule filename sets differ"

    differing = [
        name
        for name in source_rules
        if built_rules[name].read_bytes() != source_rules[name].read_bytes()
    ]
    assert differing == [], f"rule content differs from source: {differing}"


def test_build_is_deterministic(tmp_path: Path) -> None:
    """Two independent builds from identical source produce identical file sets and bytes."""
    first = tmp_path / "a"
    second = tmp_path / "b"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(first)]).exit_code == 0
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(second)]).exit_code == 0

    def _files(root: Path) -> dict[str, bytes]:
        return {
            p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and p.name != ".DS_Store"
        }

    assert _files(first) == _files(second)


def test_vendored_matcher_matches_canonical_source(built_plugin: Path) -> None:
    """The vendored matcher is byte-identical to src/ai_rules/match_rules.py."""
    vendored = built_plugin / "skills" / "rule-loader" / "scripts" / "match_rules.py"
    canonical = REPO_ROOT / "src" / "ai_rules" / "match_rules.py"
    assert vendored.read_bytes() == canonical.read_bytes()


# ---------------------------------------------------------------------------
# Manifest contract (check_manifest)
#
# The Cortex CLI has no `plugin validate` subcommand, so a malformed manifest
# would otherwise surface only at install time on a consumer's machine. Every
# test below pairs a clean-build assertion with a positive control that breaks
# the manifest deliberately -- a validator that cannot fail gates nothing.
# ---------------------------------------------------------------------------


def _manifest_path(plugin_dir: Path) -> Path:
    return plugin_dir / ".cortex-plugin" / "plugin.json"


def _rewrite_manifest(plugin_dir: Path, mutate) -> None:
    """Load, mutate, and write back the manifest in place."""
    path = _manifest_path(plugin_dir)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _hooks_path(plugin_dir: Path) -> Path:
    """Return the plugin's single hook declaration."""
    return plugin_dir / "hooks" / "hooks.json"


def _rewrite_hooks(plugin_dir: Path, mutate) -> None:
    """Load, mutate, and write back hooks/hooks.json in place."""
    path = _hooks_path(plugin_dir)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_manifest_is_valid_on_clean_build(built_plugin: Path) -> None:
    """A freshly built manifest satisfies the contract."""
    assert check_manifest(built_plugin) == []


@pytest.mark.parametrize("key", REQUIRED_MANIFEST_KEYS)
def test_manifest_missing_required_key_is_flagged(tmp_path: Path, key: str) -> None:
    """Each required key is genuinely required, not merely documented."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_manifest(out, lambda d: d.pop(key))

    problems = check_manifest(out)
    assert any(key in p for p in problems), problems


def test_manifest_empty_required_key_is_flagged(tmp_path: Path) -> None:
    """A present-but-empty key is as broken as a missing one."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_manifest(out, lambda d: d.update(name=""))

    assert any("empty" in p and "name" in p for p in check_manifest(out))


def test_manifest_unknown_hook_event_is_flagged(tmp_path: Path) -> None:
    """A typo'd event name is silently ignored at runtime, so catch it here."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    def mutate(d: dict) -> None:
        d["hooks"] = {"UserPromptSubmitt": d["hooks"]["UserPromptSubmit"]}

    _rewrite_hooks(out, mutate)

    assert any("unknown hook event" in p for p in check_manifest(out))


def test_manifest_missing_hook_command_is_flagged(tmp_path: Path) -> None:
    """A manifest pointing at a script the build never emitted must fail.

    This is the check that catches a renamed or unshipped hook.
    """
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    def mutate(d: dict) -> None:
        d["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] = (
            "${CLAUDE_PLUGIN_ROOT}/hooks/does-not-exist"
        )

    _rewrite_hooks(out, mutate)

    assert any("does not exist in the build" in p for p in check_manifest(out))


def test_manifest_relative_hook_command_is_flagged(tmp_path: Path) -> None:
    """A bare relative hook command must fail the build.

    Plugin hosts run hooks with cwd set to the user's workspace, not the plugin root.
    'hooks/user-prompt-submit' therefore exits 127 in most projects -- and in a project
    that happens to contain a same-named script, silently runs the wrong one. The file
    exists inside the build, so a validator that resolved it against the plugin root
    would report a pass for a command that cannot work.
    """
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    def mutate(d: dict) -> None:
        d["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] = "hooks/user-prompt-submit"

    _rewrite_hooks(out, mutate)

    # Guard the premise: the target really is present and executable in the build,
    # so the failure below is about the path form, not a missing file.
    shipped = out / "hooks" / "user-prompt-submit"
    assert shipped.is_file() and shipped.stat().st_mode & 0o111

    assert any("must be absolute or start with" in p for p in check_manifest(out))


def test_built_hook_command_is_not_relative(tmp_path: Path) -> None:
    """The build's own emitted command must satisfy the rule above."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    hooks = json.loads(_hooks_path(out).read_text(encoding="utf-8"))
    command = hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]

    assert command == "${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit"
    assert check_manifest(out) == []


def test_manifest_non_executable_hook_command_is_flagged(tmp_path: Path) -> None:
    """A hook that ships without the execute bit would fail at runtime."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    hook = out / "hooks" / "user-prompt-submit"
    hook.chmod(0o644)

    assert any("not executable" in p for p in check_manifest(out))


def test_manifest_bad_hook_entry_type_is_flagged(tmp_path: Path) -> None:
    """Hook entries must declare type 'command'."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    def mutate(d: dict) -> None:
        d["hooks"]["UserPromptSubmit"][0]["hooks"][0]["type"] = "inline"

    _rewrite_hooks(out, mutate)

    assert any("type must be 'command'" in p for p in check_manifest(out))


def test_manifest_wrong_types_are_flagged(tmp_path: Path) -> None:
    """The skills key must be a list and hooks must be an object."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_manifest(out, lambda d: d.update(skills="./skills"))

    assert any("'skills' must be a list" in p for p in check_manifest(out))


def test_manifest_inline_hooks_key_is_rejected(tmp_path: Path) -> None:
    """Declaring hooks inline reintroduces the two-source divergence.

    Desktop read the inline key and ignored hooks/hooks.json while the CLI read
    hooks/hooks.json, so a fix applied to one silently did nothing on the other.
    """
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    hooks = json.loads(_hooks_path(out).read_text(encoding="utf-8"))
    _rewrite_manifest(out, lambda d: d.update(hooks=hooks["hooks"]))

    assert any("must not declare 'hooks' inline" in p for p in check_manifest(out))


def test_missing_hooks_file_is_flagged(tmp_path: Path) -> None:
    """hooks/hooks.json is the only hook declaration, so its absence must fail."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _hooks_path(out).unlink()

    assert any("missing hooks/hooks.json" in p for p in check_manifest(out))


def test_verify_command_fails_on_broken_manifest(tmp_path: Path) -> None:
    """check_manifest is wired into verify, not merely available."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_manifest(out, lambda d: d.pop("name"))

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert "name" in result.output


def test_verify_command_fails_on_broken_hooks_file(tmp_path: Path) -> None:
    """check_hooks_file is wired into verify too, not merely available."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_hooks(out, lambda d: d.update(hooks={}))

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert "hooks.json" in result.output


# ---------------------------------------------------------------------------
# Replica parity
# ---------------------------------------------------------------------------


@pytest.mark.characterization
@pytest.mark.parametrize("replica", REPO_REPLICAS, ids=lambda r: r.replica)
def test_tracked_replica_matches_primary(replica) -> None:
    """A tracked replica must be byte-identical to its primary, with no build involved.

    This is the assertion that was missing. `test_vendored_matcher_matches_canonical_source`
    compares a freshly built copy against the source `shutil.copy2` produced it from
    moments earlier, so it verifies copy fidelity rather than staleness and cannot
    fail for a stale tracked file. Reading the committed bytes directly is what
    catches drift.

    Regenerate with `ai-rules plugin sync` when this fails.
    """
    primary = REPO_ROOT / replica.primary
    tracked = REPO_ROOT / replica.replica

    assert primary.is_file(), f"missing primary: {replica.primary}"
    assert tracked.is_file(), f"missing replica: {replica.replica}"
    assert tracked.read_bytes() == primary.read_bytes(), (
        f"{replica.replica} has drifted from {replica.primary}. "
        "Run `ai-rules plugin sync` to regenerate."
    )


@pytest.mark.parametrize("copy", BUILD_COPIES, ids=lambda c: c.dest)
def test_build_copy_matches_primary(copy, built_plugin: Path) -> None:
    """Every emitted artifact is byte-identical to the primary it came from."""
    problems = _check_copy_content(copy, built_plugin)
    assert problems == [], f"content mismatch: {problems}"


def test_content_check_detects_a_stale_file(built_plugin: Path, tmp_path: Path) -> None:
    """Negative control: a perturbed file copy must be reported as stale.

    Without this, a content check that silently no-ops would read as protection
    while providing none.
    """
    staged = tmp_path / "staged"
    shutil.copytree(built_plugin, staged)

    target = staged / "skills" / "rule-loader" / "scripts" / "match_rules.py"
    target.write_bytes(target.read_bytes() + b"\n# tampered\n")

    problems = check_artifacts(staged)
    assert any("stale artifact" in p for p in problems), (
        f"stale file not detected; problems were: {problems}"
    )


def test_content_check_detects_a_stale_tree_file(built_plugin: Path, tmp_path: Path) -> None:
    """Negative control for trees: a perturbed rules/ file must be reported as stale."""
    staged = tmp_path / "staged_tree"
    shutil.copytree(built_plugin, staged)

    target = next(iter(sorted((staged / "rules").glob("*.md"))))
    target.write_bytes(target.read_bytes() + b"\n")

    problems = check_artifacts(staged)
    assert any("stale artifact" in p for p in problems), (
        f"stale tree file not detected; problems were: {problems}"
    )


def test_agents_and_commands_are_not_shipped() -> None:
    """The manifest declares no agents/ or commands/ tree.

    Both are supported plugin components this plugin intentionally does not ship.
    Pinning the decision means adding one later must go through the manifest --
    otherwise `check_artifacts` rejects it as undeclared output rather than
    shipping it unverified.
    """
    dests = {c.dest for c in BUILD_COPIES}
    assert not any(d == "agents" or d.startswith("agents/") for d in dests)
    assert not any(d == "commands" or d.startswith("commands/") for d in dests)
