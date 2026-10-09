"""Real-corpus conformance: every operational rule satisfies the active schema.

Unit tests in ``tests/cli/test_validate.py`` cover synthetic negative controls
(wrong section order, empty Contract subsections). This module checks the
integration of those rules with the shipped corpus, so a rule that drifts out
of v4 conformance fails CI instead of passing silently.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ai_rules.commands import validate as validate_module

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RULE_PATHS = sorted((PROJECT_ROOT / "rules").glob("*.md"))


@pytest.fixture(scope="module")
def validator() -> validate_module.SchemaValidator:
    """Validator bound to the active schema shipped with the project."""
    return validate_module.SchemaValidator(project_root=PROJECT_ROOT)


@pytest.mark.characterization
def test_corpus_is_present() -> None:
    """Guard against a glob that silently matches nothing."""
    assert RULE_PATHS, "expected operational rules under rules/"


@pytest.mark.characterization
@pytest.mark.parametrize("rule_path", RULE_PATHS, ids=lambda p: p.name)
def test_rule_conforms_to_active_schema(
    validator: validate_module.SchemaValidator, rule_path: Path
) -> None:
    """Each rule validates without diagnostics and declares the v4.0 schema."""
    frontmatter = yaml.safe_load(rule_path.read_text(encoding="utf-8").split("---", 2)[1])
    assert str(frontmatter["schema_version"]).strip() == "v4.0"

    result = validator.validate_file(rule_path)

    assert not result.errors, [f"{e.severity}: {e.message}" for e in result.errors]
