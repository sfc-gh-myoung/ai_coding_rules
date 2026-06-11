"""Extra branch-coverage tests for fixtures.py validation paths."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from ai_rules.rule_loader_eval.fixtures import (
    FixtureValidationError,
    TriggerEvidence,
    _coerce_str_tuple,
    _ext_pattern,
    _parse_fixture,
    _parse_trigger_evidence,
    load_fixtures,
    read_prompt,
    read_updated,
    validate_rendered_snippet,
)

# ---------------------------------------------------------------------------
# Minimal valid raw fixture dict helper
# ---------------------------------------------------------------------------

_VALID_TIMESTAMP = "2026-05-16T12:00:00-07:00"


def _valid_raw(*, id_val: str = "test-fixture") -> dict:
    return {
        "schema_version": 2,
        "updated": _VALID_TIMESTAMP,
        "id": id_val,
        "description": "test",
        "variant": "simple",
        "prompt": "Fix the bug in auth.py",
        "expected": {"required": []},
        "trigger_evidence": {"kw": ["python"]},
    }


_DUMMY_PATH = Path("dummy.yaml")


# ---------------------------------------------------------------------------
# TriggerEvidence.is_empty
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_trigger_evidence_is_empty_true() -> None:
    """is_empty returns True when all fields are empty tuples."""
    te = TriggerEvidence()
    assert te.is_empty() is True


@pytest.mark.unit
def test_trigger_evidence_is_empty_false_kw() -> None:
    """is_empty returns False when kw is non-empty."""
    te = TriggerEvidence(kw=("python",))
    assert te.is_empty() is False


# ---------------------------------------------------------------------------
# _ext_pattern
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_ext_pattern_without_leading_dot() -> None:
    """_ext_pattern normalizes ext without a leading dot."""
    pattern = _ext_pattern("py")
    assert pattern.search("script.py") is not None
    assert pattern.search("script.pyx") is None


# ---------------------------------------------------------------------------
# _coerce_str_tuple error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_coerce_str_tuple_non_list_raises() -> None:
    """_coerce_str_tuple raises when value is not a list."""
    with pytest.raises(FixtureValidationError, match="must be a list"):
        _coerce_str_tuple("not-a-list", key="expected.required", fixture_id="fx")


@pytest.mark.unit
def test_coerce_str_tuple_non_string_item_raises() -> None:
    """_coerce_str_tuple raises when a list item is not a string."""
    with pytest.raises(FixtureValidationError, match="must be strings"):
        _coerce_str_tuple([123], key="expected.required", fixture_id="fx")


@pytest.mark.unit
def test_coerce_str_tuple_tuple_input_normalised() -> None:
    """_coerce_str_tuple accepts a tuple by converting it to a list first."""
    result = _coerce_str_tuple(("a", "b"), key="k", fixture_id="fx")
    assert result == ("a", "b")


# ---------------------------------------------------------------------------
# _parse_trigger_evidence error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_trigger_evidence_none_defaults_to_empty() -> None:
    """None trigger_evidence yields empty TriggerEvidence."""
    result = _parse_trigger_evidence(None, "fx")
    assert result.is_empty()


@pytest.mark.unit
def test_parse_trigger_evidence_non_dict_raises() -> None:
    """Non-dict trigger_evidence raises FixtureValidationError."""
    with pytest.raises(FixtureValidationError, match="must be a mapping"):
        _parse_trigger_evidence("bad", "fx")


@pytest.mark.unit
def test_parse_trigger_evidence_unknown_kind_raises() -> None:
    """Unknown key in trigger_evidence raises FixtureValidationError."""
    with pytest.raises(FixtureValidationError, match="unknown kinds"):
        _parse_trigger_evidence({"xyz": ["foo"]}, "fx")


# ---------------------------------------------------------------------------
# _parse_fixture error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_parse_fixture_non_dict_raises() -> None:
    """Non-dict raw YAML raises FixtureValidationError."""
    with pytest.raises(FixtureValidationError, match="top-level YAML must be a mapping"):
        _parse_fixture(_DUMMY_PATH, "not a dict")


@pytest.mark.unit
def test_parse_fixture_empty_id_raises() -> None:
    """Empty id raises FixtureValidationError."""
    raw = _valid_raw()
    raw["id"] = ""
    with pytest.raises(FixtureValidationError, match="id must be a non-empty string"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_unsupported_schema_version_raises() -> None:
    """Unsupported schema_version raises FixtureValidationError."""
    raw = _valid_raw()
    raw["schema_version"] = 99
    with pytest.raises(FixtureValidationError, match="unsupported schema_version"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_naive_datetime_raises() -> None:
    """Naive datetime in updated (no tzinfo) raises FixtureValidationError."""
    raw = _valid_raw()
    raw["updated"] = datetime(2026, 5, 16, 12, 0, 0)  # naive — no tzinfo
    with pytest.raises(FixtureValidationError, match="missing a timezone offset"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_invalid_variant_raises() -> None:
    """Invalid variant raises FixtureValidationError."""
    raw = _valid_raw()
    raw["variant"] = "mega-complex"
    with pytest.raises(FixtureValidationError, match="variant must be one of"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_non_string_prompt_raises() -> None:
    """Non-string prompt raises FixtureValidationError."""
    raw = _valid_raw()
    raw["prompt"] = 42
    with pytest.raises(FixtureValidationError, match="prompt must be a non-empty string"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_non_dict_expected_raises() -> None:
    """Non-dict expected raises FixtureValidationError."""
    raw = _valid_raw()
    raw["expected"] = ["list", "not", "dict"]
    with pytest.raises(FixtureValidationError, match="expected must be a mapping"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_required_forbidden_overlap_raises() -> None:
    """Same rule in both required and forbidden raises FixtureValidationError."""
    raw = _valid_raw()
    raw["expected"]["required"] = ["rules/100-snowflake-core.md"]
    raw["expected"]["forbidden"] = ["rules/100-snowflake-core.md"]
    with pytest.raises(FixtureValidationError, match="both required and forbidden"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_dependencies_forbidden_overlap_raises() -> None:
    """Same rule in dependencies and forbidden raises FixtureValidationError."""
    raw = _valid_raw()
    raw["expected"]["dependencies"] = ["rules/100-snowflake-core.md"]
    raw["expected"]["forbidden"] = ["rules/100-snowflake-core.md"]
    with pytest.raises(FixtureValidationError, match="both dependencies and forbidden"):
        _parse_fixture(_DUMMY_PATH, raw)


@pytest.mark.unit
def test_parse_fixture_non_string_notes_raises() -> None:
    """Non-string notes raises FixtureValidationError."""
    raw = _valid_raw()
    raw["notes"] = 12345
    with pytest.raises(FixtureValidationError, match="notes must be a string"):
        _parse_fixture(_DUMMY_PATH, raw)


# ---------------------------------------------------------------------------
# read_prompt error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_read_prompt_missing_file_raises(tmp_path: Path) -> None:
    """read_prompt raises when file does not exist."""
    with pytest.raises(FixtureValidationError, match="not found"):
        read_prompt(tmp_path / "nonexistent.yaml")


@pytest.mark.unit
def test_read_prompt_invalid_yaml_raises(tmp_path: Path) -> None:
    """read_prompt raises on malformed YAML."""
    bad = tmp_path / "bad.yaml"
    bad.write_text("{not: valid: yaml: [[", encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="failed to parse"):
        read_prompt(bad)


@pytest.mark.unit
def test_read_prompt_non_dict_yaml_raises(tmp_path: Path) -> None:
    """read_prompt raises when YAML is not a mapping."""
    f = tmp_path / "f.yaml"
    f.write_text("- just a list\n", encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="must be a mapping"):
        read_prompt(f)


@pytest.mark.unit
def test_read_prompt_missing_prompt_key_raises(tmp_path: Path) -> None:
    """read_prompt raises when prompt key is missing."""
    f = tmp_path / "f.yaml"
    f.write_text("id: test\n", encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="missing a non-empty"):
        read_prompt(f)


# ---------------------------------------------------------------------------
# read_updated error paths
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_read_updated_missing_file_returns_none(tmp_path: Path) -> None:
    """read_updated returns None when file does not exist."""
    assert read_updated(tmp_path / "nonexistent.yaml") is None


@pytest.mark.unit
def test_read_updated_invalid_yaml_returns_none(tmp_path: Path) -> None:
    """read_updated returns None on malformed YAML."""
    f = tmp_path / "bad.yaml"
    f.write_text("{: invalid: [[", encoding="utf-8")
    assert read_updated(f) is None


@pytest.mark.unit
def test_read_updated_non_dict_yaml_returns_none(tmp_path: Path) -> None:
    """read_updated returns None when YAML is not a mapping."""
    f = tmp_path / "f.yaml"
    f.write_text("- just a list\n", encoding="utf-8")
    assert read_updated(f) is None


@pytest.mark.unit
def test_read_updated_naive_datetime_returns_none(tmp_path: Path) -> None:
    """read_updated returns None when datetime has no tzinfo."""
    f = tmp_path / "f.yaml"
    # PyYAML parses ISO 8601 without tz as naive datetime
    f.write_text("updated: 2026-05-16T12:00:00\n", encoding="utf-8")
    assert read_updated(f) is None


@pytest.mark.unit
def test_read_updated_valid_string_returns_stripped(tmp_path: Path) -> None:
    """read_updated returns the stripped timestamp string."""
    f = tmp_path / "f.yaml"
    f.write_text(f"updated: '{_VALID_TIMESTAMP}'\n", encoding="utf-8")
    result = read_updated(f)
    assert result == _VALID_TIMESTAMP


# ---------------------------------------------------------------------------
# validate_rendered_snippet schema error path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_rendered_snippet_schema_error_on_bad_fixture() -> None:
    """validate_rendered_snippet returns schema error for invalid fixture YAML."""
    # Valid YAML but missing required fields → schema error from _parse_fixture
    snippet = "schema_version: 2\nid: test\n"
    errors = validate_rendered_snippet(snippet, "test", {})
    assert any(e.startswith("schema:") for e in errors)


# ---------------------------------------------------------------------------
# load_fixtures rules=None with evidence error
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_load_fixtures_rules_none_raises_on_bad_evidence(tmp_path: Path) -> None:
    """load_fixtures raises when rules=None and prompt-level evidence is missing."""
    # kw evidence "python" declared but prompt doesn't contain "python"
    raw = _valid_raw()
    raw["prompt"] = "Fix the bug in auth.js"  # no "python" keyword
    raw["trigger_evidence"] = {"kw": ["python"]}
    content = yaml.dump(raw)
    (tmp_path / "test.yaml").write_text(content, encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="trigger-evidence invariant"):
        load_fixtures(tmp_path, rules=None)
