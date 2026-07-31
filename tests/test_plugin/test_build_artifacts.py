"""Tests for the plugin build artifact contract.

Guards the contract defined by ``EXPECTED_ARTIFACTS`` and ``EXPECTED_TREES`` in
``ai_rules.commands.plugin``. The regression these tests exist to prevent: a
component is documented as shipped but no build step emits it, so it survives
only as a stray tracked file and vanishes on the next clean build.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.commands.plugin import (
    EXPECTED_ARTIFACTS,
    EXPECTED_TREES,
    REQUIRED_MANIFEST_KEYS,
    check_artifacts,
    check_manifest,
    plugin_app,
)

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
    a corresponding contract entry — the copy-map drift guard.
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


def test_verify_fails_on_invalid_manifest(tmp_path: Path) -> None:
    """`plugin verify` exits non-zero when the generated manifest is not valid JSON."""
    out = tmp_path / "plugin"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    (out / ".cortex-plugin" / "plugin.json").write_text("{ not json", encoding="utf-8")

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert "invalid plugin.json" in result.output


def test_generated_manifest_is_valid_json(built_plugin: Path) -> None:
    """The generated manifest parses and declares the skills directory."""
    manifest = json.loads(
        (built_plugin / ".cortex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "ai-coding-rules"
    assert "./skills" in manifest["skills"]


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

    _rewrite_manifest(out, mutate)

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

    _rewrite_manifest(out, mutate)

    assert any("does not exist in the build" in p for p in check_manifest(out))


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

    _rewrite_manifest(out, mutate)

    assert any("type must be 'command'" in p for p in check_manifest(out))


def test_manifest_wrong_types_are_flagged(tmp_path: Path) -> None:
    """The skills key must be a list and hooks must be an object."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_manifest(out, lambda d: d.update(skills="./skills"))

    assert any("'skills' must be a list" in p for p in check_manifest(out))


def test_verify_command_fails_on_broken_manifest(tmp_path: Path) -> None:
    """check_manifest is wired into verify, not merely available."""
    out = tmp_path / "p"
    assert runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)]).exit_code == 0

    _rewrite_manifest(out, lambda d: d.pop("hooks"))

    result = runner.invoke(plugin_app, ["verify", "--plugin-dir", str(out)])
    assert result.exit_code == 1
    assert "hooks" in result.output
