"""Contract checks for the `$show-rules` skill instructions."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_FILE = REPO_ROOT / "skills" / "show-rules" / "SKILL.md"


def test_show_rules_uses_explicit_absolute_path_trigger() -> None:
    """Absolute paths are used only when the injected absolute-path list is non-empty."""
    text = SKILL_FILE.read_text(encoding="utf-8")
    assert "when the injected absolute-path list is non-empty" in text
    assert "or are otherwise available" not in text


def test_show_rules_requires_filename_keyed_reason_join() -> None:
    """Reasons must join to rendered paths by filename, not list position."""
    text = SKILL_FILE.read_text(encoding="utf-8")
    assert "Join match reasons to paths by filename" in text
    assert "not by list position" in text


def test_show_rules_documents_relative_fallback() -> None:
    """Repo-root workflows keep a relative fallback path form."""
    text = SKILL_FILE.read_text(encoding="utf-8")
    assert "rules/<name>.md" in text
    assert "when no injected absolute path exists" in text


def test_show_rules_documents_escape_vocabulary_inline() -> None:
    """The durable markdown escape vocabulary lives in the skill, not an artifact doc."""
    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    for token in ("backslash", "`|`", "`*`", "`_`", "`[`", "`]`", "backtick"):
        assert token in skill_text
    assert "docs/plugin-rule-path-contract.md" not in skill_text
