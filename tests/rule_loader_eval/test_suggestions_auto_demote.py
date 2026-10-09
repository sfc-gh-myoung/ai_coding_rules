"""Unit tests for the auto-demote behavior in build_suggestions.

Auto-demote contract: a loaded rule with no typed-Keywords trigger evidence in the
prompt is moved to ``optional`` regardless of whether it would otherwise classify
as ``required`` or ``dependencies``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.rules_meta import RuleMetadata, parse_rule_metadata
from ai_rules.rule_loader_eval.suggestions import build_suggestions


def _make_meta(
    path: str,
    keywords: str = "",
    typed_keywords: str = "",
    depends: str = "999-test-core.md",
) -> RuleMetadata:
    """Helper: parse a minimal rule metadata block.

    v3.3: typed Keywords is the sole trigger evidence source. Already-prefixed
    ``typed_keywords`` entries are merged with bare ``keywords`` entries (wrapped
    as ``kw:``) into a single Keywords field.
    """
    parts: list[str] = []
    if typed_keywords:
        parts.extend(t.strip() for t in typed_keywords.split(",") if t.strip())
    if keywords:
        seen = {p.lower() for p in parts}
        for kw in keywords.split(","):
            kw = kw.strip()
            if not kw:
                continue
            typed = f"kw:{' '.join(kw.lower().split())}"
            if typed not in seen:
                parts.append(typed)
                seen.add(typed)
    typed_keywords = ", ".join(parts) if parts else "kw:rule"
    content = f"**Keywords:** {typed_keywords}\n**Depends:** {depends}\n"
    return parse_rule_metadata(Path(path), content)


@pytest.mark.unit
def test_auto_demote_top_level_rule_with_no_evidence() -> None:
    """A loaded rule with no kw/ext/file/dir match in the prompt goes to optional."""
    prompt = "Help me build a streamlit dashboard for our data team."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
        "rules/119-snowflake-warehouse-management.md": _make_meta(
            "rules/119-snowflake-warehouse-management.md",
            keywords="warehouse, virtual warehouse",
            typed_keywords="kw:warehouse, kw:virtual warehouse",
            depends="100-snowflake-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/119-snowflake-warehouse-management.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/119-snowflake-warehouse-management.md" in sugg.optional
    assert "rules/119-snowflake-warehouse-management.md" not in sugg.required
    assert "rules/119-snowflake-warehouse-management.md" in sugg.auto_demoted
    assert "rules/119-snowflake-warehouse-management.md" not in sugg.auto_demoted_was_dep
    reason = sugg.rule_reasons["rules/119-snowflake-warehouse-management.md"]
    assert "auto-demoted" in reason and "no trigger evidence" in reason


@pytest.mark.unit
def test_auto_demote_records_missing_triggers() -> None:
    """The missing_triggers map records the rule's declared typed-Keywords trigger tokens."""
    prompt = "Refactor my Python code."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
        "rules/202-markup-config-validation.md": _make_meta(
            "rules/202-markup-config-validation.md",
            keywords="markup",
            typed_keywords="file:Taskfile.yml",
            depends="",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/202-markup-config-validation.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    triggers = sugg.missing_triggers["rules/202-markup-config-validation.md"]
    assert triggers["file"] == ("Taskfile.yml",)
    assert triggers["kw"] == ("markup",)
    assert triggers["ext"] == ()
    assert triggers["dir"] == ()


@pytest.mark.unit
def test_rule_with_kw_evidence_stays_required() -> None:
    """A loaded rule whose kw matches the prompt stays in required."""
    prompt = "Set up a virtual warehouse for our analytics team."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
        "rules/119-snowflake-warehouse-management.md": _make_meta(
            "rules/119-snowflake-warehouse-management.md",
            keywords="warehouse, virtual warehouse",
            typed_keywords="kw:warehouse, kw:virtual warehouse",
            depends="100-snowflake-core.md",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/119-snowflake-warehouse-management.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/119-snowflake-warehouse-management.md" in sugg.required
    assert "rules/119-snowflake-warehouse-management.md" not in sugg.optional
    assert "rules/119-snowflake-warehouse-management.md" not in sugg.auto_demoted


@pytest.mark.unit
def test_operating_core_demotes_without_evidence() -> None:
    """The operating rule is not a foundation placeholder and needs trigger evidence."""
    prompt = "Just a plain prompt."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
    }
    loaded = ("rules/999-test-core.md",)
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert sugg.required == ()
    assert "rules/999-test-core.md" in sugg.auto_demoted
    assert sugg.optional == ("rules/999-test-core.md",)


@pytest.mark.unit
def test_dep_rule_with_no_evidence_demoted_to_optional() -> None:
    """A dependency rule with no own kw evidence is auto-demoted (was dep)."""
    prompt = "Help me with a stored procedure that runs nightly."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
        # Dep with no evidence: only matches via Depends from 102b
        "rules/100-snowflake-core.md": _make_meta(
            "rules/100-snowflake-core.md",
            keywords="warehouse, role, account",
            typed_keywords="kw:snowflake-account",
            depends="999-test-core.md",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure",
            typed_keywords="kw:stored procedure",
            depends="100-snowflake-core.md",
        ),
    }
    loaded = (
        "rules/999-test-core.md",
        "rules/100-snowflake-core.md",
        "rules/102b-snowflake-sql-procedures.md",
    )
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/102b-snowflake-sql-procedures.md" in sugg.required
    assert "rules/100-snowflake-core.md" in sugg.optional
    assert "rules/100-snowflake-core.md" in sugg.auto_demoted
    assert "rules/100-snowflake-core.md" in sugg.auto_demoted_was_dep
    reason = sugg.rule_reasons["rules/100-snowflake-core.md"]
    assert "(was dep)" in reason


@pytest.mark.unit
def test_dep_rule_with_own_evidence_stays_dep() -> None:
    """A dependency rule that ALSO has its own kw evidence stays in dependencies."""
    prompt = "Help me build a stored procedure on our snowflake-account."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
        "rules/100-snowflake-core.md": _make_meta(
            "rules/100-snowflake-core.md",
            keywords="snowflake-account, warehouse, role",
            typed_keywords="kw:snowflake-account",
            depends="999-test-core.md",
        ),
        "rules/102b-snowflake-sql-procedures.md": _make_meta(
            "rules/102b-snowflake-sql-procedures.md",
            keywords="stored procedure",
            typed_keywords="kw:stored procedure",
            depends="100-snowflake-core.md",
        ),
    }
    loaded = (
        "rules/999-test-core.md",
        "rules/100-snowflake-core.md",
        "rules/102b-snowflake-sql-procedures.md",
    )
    sugg = build_suggestions(loaded, prompt, rules_meta)

    assert "rules/100-snowflake-core.md" in sugg.dependencies
    assert "rules/100-snowflake-core.md" not in sugg.optional


@pytest.mark.unit
def test_ngram_suggestions_separated_from_kw_evidence() -> None:
    """N-gram phrases live in ngram_kw_suggestions, not in trigger_evidence['kw']."""
    prompt = "Refactor a fragile retry loop into a more resilient retry policy."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
    }
    loaded = ("rules/999-test-core.md",)
    sugg = build_suggestions(loaded, prompt, rules_meta)

    # No rules with kw triggers loaded → no rule-tied kw evidence.
    assert sugg.trigger_evidence.get("kw", ()) == ()
    # But n-gram suggestions ARE populated.
    assert len(sugg.ngram_kw_suggestions) > 0


@pytest.mark.unit
def test_auto_demoted_rule_has_optional_classification_only() -> None:
    """A demoted rule appears in optional only, not in required or dependencies."""
    prompt = "Generic prompt with nothing rule-specific."
    rules_meta = {
        "rules/999-test-core.md": _make_meta(
            "rules/999-test-core.md", typed_keywords="", depends=""
        ),
        "rules/126-snowflake-cortex-code-agent-sdk.md": _make_meta(
            "rules/126-snowflake-cortex-code-agent-sdk.md",
            keywords="agent-sdk",
            typed_keywords="kw:agent-sdk",
            depends="",
        ),
    }
    loaded = ("rules/999-test-core.md", "rules/126-snowflake-cortex-code-agent-sdk.md")
    sugg = build_suggestions(loaded, prompt, rules_meta)
    rule = "rules/126-snowflake-cortex-code-agent-sdk.md"
    assert rule in sugg.optional
    assert rule not in sugg.required
    assert rule not in sugg.dependencies
