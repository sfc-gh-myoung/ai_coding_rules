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
    check_artifacts,
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
