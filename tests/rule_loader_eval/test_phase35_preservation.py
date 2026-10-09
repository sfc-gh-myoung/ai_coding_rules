"""Phase 3.5 preservation test.

Asserts that the bucket-prefix fields on RuleMetadata and MatchResult
survive the Phase 3.5 typed-Keywords migration (non-removal clauses).
"""

from __future__ import annotations

import pytest

from ai_rules.rule_loader_eval.matcher import MatchResult
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


@pytest.mark.unit
def test_rule_metadata_has_depends_required() -> None:
    """RuleMetadata.depends_required field is present and accessible."""
    assert hasattr(RuleMetadata, "depends_required")
    meta = RuleMetadata(path=None)  # type: ignore[arg-type]
    assert meta.depends_required == ()


@pytest.mark.unit
def test_rule_metadata_has_depends_optional() -> None:
    """RuleMetadata.depends_optional field is present and accessible."""
    assert hasattr(RuleMetadata, "depends_optional")
    meta = RuleMetadata(path=None)  # type: ignore[arg-type]
    assert meta.depends_optional == ()


@pytest.mark.unit
def test_match_result_has_unloaded_optional() -> None:
    """MatchResult.unloaded_optional field is present (non-removal clause)."""
    assert hasattr(MatchResult, "unloaded_optional") or hasattr(
        MatchResult(
            missing_required=(),
            missing_dependencies=(),
            forbidden_present=(),
            optional_loaded=(),
        ),
        "unloaded_optional",
    )
    result = MatchResult(
        missing_required=(),
        missing_dependencies=(),
        forbidden_present=(),
        optional_loaded=(),
    )
    assert result.unloaded_optional == ()


@pytest.mark.unit
def test_rule_metadata_has_typed_kw() -> None:
    """RuleMetadata.typed_kw field is present (Phase 3.5 addition)."""
    assert hasattr(RuleMetadata, "typed_kw")
    meta = RuleMetadata(path=None)  # type: ignore[arg-type]
    assert meta.typed_kw == ()


@pytest.mark.unit
def test_rule_metadata_has_typed_ext() -> None:
    """RuleMetadata.typed_ext field is present (Phase 3.5 addition)."""
    assert hasattr(RuleMetadata, "typed_ext")


@pytest.mark.unit
def test_rule_metadata_has_typed_file() -> None:
    """RuleMetadata.typed_file field is present (Phase 3.5 addition)."""
    assert hasattr(RuleMetadata, "typed_file")


@pytest.mark.unit
def test_rule_metadata_has_typed_dir() -> None:
    """RuleMetadata.typed_dir field is present (Phase 3.5 addition)."""
    assert hasattr(RuleMetadata, "typed_dir")


@pytest.mark.unit
def test_typed_fields_populated_from_keywords() -> None:
    """All four typed-prefix fields are populated from a Keywords line."""
    from pathlib import Path

    from ai_rules.rule_loader_eval.rules_meta import parse_rule_metadata

    content = (
        "**Keywords:** kw:python, ext:.py, file:pyproject.toml, dir:tests/\n"
        "**Depends:** required:999-test-core.md\n"
    )
    meta = parse_rule_metadata(Path("rules/200-python-core.md"), content)

    assert "python" in meta.typed_kw
    assert ".py" in meta.typed_ext
    assert "pyproject.toml" in meta.typed_file
    assert "tests/" in meta.typed_dir


@pytest.mark.unit
def test_triggers_includes_all_four_kinds() -> None:
    """Triggers tuple contains entries for all four prefix kinds."""
    from pathlib import Path

    from ai_rules.rule_loader_eval.rules_meta import parse_rule_metadata

    content = (
        "**Keywords:** kw:python, ext:.py, file:Dockerfile, dir:tests/\n"
        "**Depends:** required:999-test-core.md\n"
    )
    meta = parse_rule_metadata(Path("rules/200-test.md"), content)

    kinds = {t.split(":", 1)[0] for t in meta.triggers if ":" in t}
    assert "kw" in kinds
    assert "ext" in kinds
    assert "file" in kinds
    assert "dir" in kinds
