"""Tests for plugin closure: dangling references and new Phase 2-5 artifacts.

Guards that:
  1. All new Phase 2-5 artifacts declared in BUILD_COPIES are present after build.
  2. No relative Markdown link in a shipped skill file points to a missing target.
  3. The skills/rule-loader/references/ tree is emitted.
  4. skills/shared/runtime-capabilities.md is emitted.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.commands.plugin import plugin_app

REPO_ROOT = Path(__file__).resolve().parents[2]
runner = CliRunner()

_MD_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")


@pytest.fixture(scope="module")
def built_plugin(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("plugin_closure")
    result = runner.invoke(plugin_app, ["build", "--plugin-dir", str(out)])
    assert result.exit_code == 0, f"build failed: {result.output}"
    return out


# ── Phase 2-5 artifacts ───────────────────────────────────────────────────────


def test_rule_loader_references_dir_is_emitted(built_plugin: Path) -> None:
    """skills/rule-loader/references/ tree must be present after build."""
    ref_dir = built_plugin / "skills" / "rule-loader" / "references"
    assert ref_dir.is_dir(), "skills/rule-loader/references/ not in built plugin"


def test_rule_loader_manifest_schema_is_emitted(built_plugin: Path) -> None:
    """skills/rule-loader/references/manifest-schema.md must be in built plugin."""
    f = built_plugin / "skills" / "rule-loader" / "references" / "manifest-schema.md"
    assert f.is_file(), "manifest-schema.md missing from built plugin"
    # Byte parity with canonical source
    source = REPO_ROOT / "skills" / "rule-loader" / "references" / "manifest-schema.md"
    assert f.read_bytes() == source.read_bytes(), "manifest-schema.md byte-parity failure"


def test_shared_runtime_capabilities_is_emitted(built_plugin: Path) -> None:
    """skills/shared/runtime-capabilities.md must be in built plugin."""
    f = built_plugin / "skills" / "shared" / "runtime-capabilities.md"
    assert f.is_file(), "skills/shared/runtime-capabilities.md missing from built plugin"
    source = REPO_ROOT / "skills" / "shared" / "runtime-capabilities.md"
    assert f.read_bytes() == source.read_bytes(), "runtime-capabilities.md byte-parity failure"


# ── dangling-reference test ───────────────────────────────────────────────────


def test_no_dangling_markdown_links_in_shipped_skills(built_plugin: Path) -> None:
    """No relative Markdown link in a shipped skill file points to a missing target.

    Scans all *.md files under the built plugin's skills/ directory. For each
    relative link (no scheme, not anchored-only) resolves it against the file's
    own directory within the built plugin and asserts the target exists.

    External URLs (http/https/mailto) and anchor-only fragments (#...) are skipped.
    """
    dangling: list[str] = []

    skills_dir = built_plugin / "skills"
    for md_file in skills_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for match in _MD_LINK_RE.finditer(content):
            href = match.group(1)
            # Skip external URLs, anchors, and mail links
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Strip any anchor fragment
            path_part = href.split("#")[0]
            if not path_part:
                continue
            # Resolve relative to the file's own directory
            target = (md_file.parent / path_part).resolve()
            if not target.exists():
                rel_md = md_file.relative_to(built_plugin)
                dangling.append(f"{rel_md}: link target '{href}' does not exist")

    assert dangling == [], "Dangling links in built plugin:\n" + "\n".join(dangling)
