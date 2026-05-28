"""Unit tests for snippet rendering under the valid-by-construction contract.

Covers:
- N-gram phrases render as inline ``# n-gram (no rule):`` comments under ``kw:``,
  not as YAML kw values.
- Auto-demoted rules render under ``optional:`` with ``# auto-demoted`` and a
  per-rule ``# missing:`` hint.
- ``# suspicious`` comments no longer appear (vocabulary replaced).
- ``# preserve`` annotations survive a round-trip through the renderer.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.snippet import format_fixture_snippet


@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return the repo root."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


def _make_run(loaded: tuple[str, ...], fixture_id: str = "test") -> AgentRun:
    """Build a minimal AgentRun for snippet tests."""
    return AgentRun(
        fixture_id=fixture_id,
        loaded=loaded,
        loaded_via_reads=loaded,
        loaded_via_reads_performed=(),
        loaded_via_section=loaded,
    )


def test_ngram_phrases_render_as_inline_comments(project_root: Path) -> None:
    """High-signal prompt phrases appear as ``# n-gram (no rule):`` comments."""
    prompt = "Refactor a fragile retry loop into a more resilient retry policy."
    run = _make_run(("rules/999-test-core.md",))
    snippet = format_fixture_snippet(
        run, prompt, "test-ngram", "simple", project_root, "2026-05-16T12:00:00-07:00"
    )
    assert "# n-gram (no rule):" in snippet
    # The phrase appears inside a comment, not as a YAML kw value.
    assert "kw: []" in snippet


def test_no_suspicious_comment_in_output(project_root: Path) -> None:
    """The retired ``# suspicious`` vocabulary does not appear."""
    prompt = "Generic prompt."
    run = _make_run(("rules/999-test-core.md", "rules/200-python-core.md"))
    snippet = format_fixture_snippet(
        run, prompt, "test", "simple", project_root, "2026-05-16T12:00:00-07:00"
    )
    assert "# suspicious" not in snippet


def test_auto_demoted_rule_renders_under_optional(project_root: Path) -> None:
    """A loaded rule with no typed Keywords evidence in the prompt appears under optional."""
    prompt = "Walk me through deploying a streamlit dashboard."
    run = _make_run(("rules/999-test-core.md", "rules/200-python-core.md"))
    snippet = format_fixture_snippet(
        run, prompt, "test", "simple", project_root, "2026-05-16T12:00:00-07:00"
    )
    assert "  optional:" in snippet
    assert "rules/200-python-core.md" in snippet
    # And the # auto-demoted reason appears.
    assert "# auto-demoted" in snippet


def test_auto_demoted_rule_emits_missing_hint(project_root: Path) -> None:
    """Auto-demoted lines include a ``# missing:`` hint with the rule's triggers.

    v3.3: triggers are derived from typed Keywords entries (ext:, file:, dir:, kw:).
    """
    prompt = "Walk me through deploying a streamlit dashboard."
    run = _make_run(("rules/999-test-core.md", "rules/200-python-core.md"))
    snippet = format_fixture_snippet(
        run, prompt, "test", "simple", project_root, "2026-05-16T12:00:00-07:00"
    )
    assert "# missing:" in snippet
    # The hint should mention the rule's actual typed Keywords trigger kinds.
    # 200-python-core has ext:.py, ext:.pyi, file:pyproject.toml (from typed Keywords).
    assert "pyproject.toml" in snippet or ".py" in snippet or "ext" in snippet


def test_preserve_annotation_pins_rule_in_optional(project_root: Path) -> None:
    """A ``# preserve`` map entry pins the rule to its preserved section."""
    prompt = "Help me with a streamlit dashboard for warehouse usage."
    # Loaded set includes streamlit-core which would normally land in required.
    run = _make_run(("rules/999-test-core.md", "rules/101-snowflake-streamlit-core.md"))
    preserved = {"rules/101-snowflake-streamlit-core.md": "optional"}
    snippet = format_fixture_snippet(
        run,
        prompt,
        "test",
        "simple",
        project_root,
        "2026-05-16T12:00:00-07:00",
        preserved=preserved,
    )
    # Rule is in optional, not required (other than foundation).
    optional_section = snippet.split("  optional:")[1].split("trigger_evidence:")[0]
    assert "rules/101-snowflake-streamlit-core.md" in optional_section
    assert "# preserve" in optional_section


def test_preserve_annotation_pins_rule_in_required(project_root: Path) -> None:
    """A preserved required pin keeps the rule in required even if no evidence."""
    prompt = "Walk me through deploying a streamlit dashboard."
    run = _make_run(("rules/999-test-core.md", "rules/200-python-core.md"))
    preserved = {"rules/200-python-core.md": "required"}
    snippet = format_fixture_snippet(
        run,
        prompt,
        "test",
        "simple",
        project_root,
        "2026-05-16T12:00:00-07:00",
        preserved=preserved,
    )
    required_section = snippet.split("  required:")[1].split("  dependencies:")[0]
    assert "rules/200-python-core.md" in required_section
    assert "# preserve" in required_section
    # And NOT under optional.
    optional_section = snippet.split("  optional:")[1].split("trigger_evidence:")[0]
    assert "rules/200-python-core.md" not in optional_section


def test_stale_preserve_emits_warning(project_root: Path) -> None:
    """A preserved rule not loaded by the live agent renders with a stale warning."""
    prompt = "Help me with streamlit."
    run = _make_run(("rules/999-test-core.md",))
    preserved = {"rules/999-not-loaded.md": "optional"}
    snippet = format_fixture_snippet(
        run,
        prompt,
        "test",
        "simple",
        project_root,
        "2026-05-16T12:00:00-07:00",
        preserved=preserved,
    )
    assert "rules/999-not-loaded.md" in snippet
    assert "stale" in snippet.lower()
