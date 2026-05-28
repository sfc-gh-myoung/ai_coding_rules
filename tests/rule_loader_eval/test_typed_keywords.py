"""Phase 3.5 tests for all four typed keyword categories.

Includes the mandatory test where ext:.py evidence is satisfied
without the literal word "python" in the prompt (plan requirement).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.rules_meta import parse_rule_metadata
from ai_rules.rule_loader_eval.suggestions import _evidence_for_rule, build_suggestions


def _meta(path: str, keywords: str, depends: str = "999-test-core.md"):
    """Helper: parse a minimal rule metadata block from typed Keywords."""
    content = f"**Keywords:** {keywords}\n**Depends:** {depends}\n"
    return parse_rule_metadata(Path(path), content)


@pytest.mark.unit
def test_ext_evidence_without_python_keyword() -> None:
    """ext:.py trigger fires when prompt contains a .py filename, even without 'python'."""
    prompt = "Review the module at utils/helper.py and update its imports."
    rules_meta = {
        "rules/999-test-core.md": _meta(
            "rules/999-test-core.md", keywords="kw:workflow", depends=""
        ),
        "rules/200-python-core.md": _meta(
            "rules/200-python-core.md",
            keywords="ext:.py, ext:.pyi, file:pyproject.toml, kw:uv, kw:ruff",
            depends="999-test-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/200-python-core.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/200-python-core.md" in sugg.required or (
        "rules/200-python-core.md" not in sugg.auto_demoted
    ), "ext:.py in prompt should satisfy the rule without the word 'python'"
    assert "rules/200-python-core.md" not in sugg.auto_demoted


@pytest.mark.unit
def test_file_evidence_matches_specific_filename() -> None:
    """file:Dockerfile trigger fires when prompt contains 'Dockerfile'."""
    prompt = "Update the Dockerfile to use a multi-stage build."
    rules_meta = {
        "rules/999-test-core.md": _meta(
            "rules/999-test-core.md", keywords="kw:workflow", depends=""
        ),
        "rules/300-docker-core.md": _meta(
            "rules/300-docker-core.md",
            keywords="file:Dockerfile, file:docker-compose.yml, kw:docker, kw:container",
            depends="999-test-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/300-docker-core.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/300-docker-core.md" not in sugg.auto_demoted


@pytest.mark.unit
def test_dir_evidence_matches_directory_path() -> None:
    """dir:skills/ trigger fires when prompt contains 'skills/' path."""
    prompt = "Add a new workflow file under skills/rule-loader/."
    rules_meta = {
        "rules/999-test-core.md": _meta(
            "rules/999-test-core.md", keywords="kw:workflow", depends=""
        ),
        "rules/002-rule-governance.md": _meta(
            "rules/002-rule-governance.md",
            keywords="dir:rules/, dir:skills/, kw:rule governance, kw:schema",
            depends="999-test-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/002-rule-governance.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/002-rule-governance.md" not in sugg.auto_demoted


@pytest.mark.unit
def test_kw_evidence_matches_prompt_phrase() -> None:
    """kw:stored-procedure trigger fires when prompt contains 'stored procedure'."""
    prompt = "Help me optimize my stored procedure for bulk inserts."
    rules_meta = {
        "rules/999-test-core.md": _meta(
            "rules/999-test-core.md", keywords="kw:workflow", depends=""
        ),
        "rules/102b-snowflake-sql-procedures.md": _meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="kw:stored-procedure, kw:create procedure, kw:sql",
            depends="102-snowflake-sql-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/102b-snowflake-sql-procedures.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/102b-snowflake-sql-procedures.md" not in sugg.auto_demoted


@pytest.mark.unit
def test_rule_with_no_trigger_evidence_auto_demoted() -> None:
    """A rule whose triggers don't match the prompt is auto-demoted to optional."""
    prompt = "Write a React component for a dropdown menu."
    rules_meta = {
        "rules/999-test-core.md": _meta(
            "rules/999-test-core.md", keywords="kw:workflow", depends=""
        ),
        "rules/200-python-core.md": _meta(
            "rules/200-python-core.md",
            keywords="ext:.py, kw:python, kw:uv, kw:ruff",
            depends="999-test-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/200-python-core.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/200-python-core.md" in sugg.optional
    assert "rules/200-python-core.md" in sugg.auto_demoted


@pytest.mark.unit
def test_typed_keywords_evidence_collected_by_kind() -> None:
    """trigger_evidence collects evidence for kw, ext, file, and dir kinds."""
    prompt = "Edit utils/parser.py and the Dockerfile to add Python 3.12 support."
    rules_meta = {
        "rules/200-python-core.md": _meta(
            "rules/200-python-core.md",
            keywords="kw:python, ext:.py, file:Dockerfile, dir:utils/",
            depends="999-test-core.md",
        ),
    }
    evidence = _evidence_for_rule("rules/200-python-core.md", rules_meta, prompt)

    assert any(e.lower() == "python" for e in evidence.get("kw", []))
    assert ".py" in evidence.get("ext", [])
    assert "dockerfile" in evidence.get("file", [])
