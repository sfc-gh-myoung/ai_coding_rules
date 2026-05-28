"""Tests for the trigger-evidence invariant validator and fixture schema."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.fixtures import (
    FixtureValidationError,
    current_updated_timestamp,
    load_fixture,
    load_fixtures,
    read_updated,
)
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata, load_rules_metadata


@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return the repo root."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


@pytest.fixture(scope="module")
def rules(project_root: Path) -> dict[str, RuleMetadata]:
    """Rule metadata for cross-checks."""
    return load_rules_metadata(project_root / "rules")


def _write_fixture(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "fixture.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_committed_fixtures_pass_invariant(
    project_root: Path, rules: dict[str, RuleMetadata]
) -> None:
    """Committed fixtures pass the trigger-evidence invariant."""
    fixtures = load_fixtures(project_root / "fixtures" / "rule_loader_eval", rules=rules)
    assert len(fixtures) >= 27
    assert any(f.variant == "simple" for f in fixtures)
    assert any(f.variant == "complex" for f in fixtures)


def test_kind_coverage_meets_minimum(project_root: Path, rules: dict[str, RuleMetadata]) -> None:
    """Each kind has >=3 simple and >=3 complex fixtures."""
    fixtures = load_fixtures(project_root / "fixtures" / "rule_loader_eval", rules=rules)
    counts = {("simple", k): 0 for k in ("kw", "ext", "file", "dir")}
    counts.update({("complex", k): 0 for k in ("kw", "ext", "file", "dir")})
    for f in fixtures:
        ev = f.trigger_evidence
        present = {
            "kw": bool(ev.kw),
            "ext": bool(ev.ext),
            "file": bool(ev.file),
            "dir": bool(ev.dir),
        }
        for kind, has in present.items():
            if has:
                counts[(f.variant, kind)] += 1
    for key, count in counts.items():
        assert count >= 3, f"insufficient {key} coverage: {count}"


@pytest.mark.unit
def test_dependencies_field_accepted(tmp_path: Path) -> None:
    """Schema accepts expected.dependencies."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: deps-ok
description: test
variant: simple
prompt: |
  Use streamlit dashboard please.
expected:
  required:
    - rules/999-test-core.md
    - rules/101-snowflake-streamlit-core.md
  dependencies:
    - rules/100-snowflake-core.md
trigger_evidence:
  kw: [streamlit, dashboard]
"""
    _write_fixture(tmp_path, body)
    fixtures = load_fixtures(tmp_path, rules={}, enforce_invariant=True)
    assert fixtures[0].dependencies == ("rules/100-snowflake-core.md",)


@pytest.mark.unit
def test_required_and_dependencies_must_not_overlap(tmp_path: Path) -> None:
    """A rule cannot appear in both required and dependencies."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: overlap
description: test
variant: simple
prompt: |
  streamlit dashboard
expected:
  required:
    - rules/999-test-core.md
    - rules/101-snowflake-streamlit-core.md
  dependencies:
    - rules/101-snowflake-streamlit-core.md
trigger_evidence:
  kw: [streamlit, dashboard]
"""
    _write_fixture(tmp_path, body)
    with pytest.raises(FixtureValidationError) as excinfo:
        load_fixtures(tmp_path, rules={}, enforce_invariant=True)
    assert "required and dependencies" in str(excinfo.value)


@pytest.mark.unit
def test_ext_evidence_must_appear_in_prompt(tmp_path: Path) -> None:
    """Ext evidence not in prompt fails fixture validation."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: bad-py
description: ext .py declared but no .py token in prompt
variant: simple
prompt: |
  Edit my python file to add a thing.
expected:
  required:
    - rules/999-test-core.md
trigger_evidence:
  ext: [.py]
"""
    _write_fixture(tmp_path, body)
    with pytest.raises(FixtureValidationError) as excinfo:
        load_fixtures(tmp_path, rules={}, enforce_invariant=True)
    assert ".py" in str(excinfo.value)


@pytest.mark.unit
def test_file_evidence_must_appear_in_prompt(tmp_path: Path) -> None:
    """File evidence not in prompt fails."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: bad-file
description: file evidence missing token
variant: simple
prompt: |
  Tell me about this configuration setup.
expected:
  required:
    - rules/999-test-core.md
trigger_evidence:
  file: [snowflake.yml]
"""
    _write_fixture(tmp_path, body)
    with pytest.raises(FixtureValidationError):
        load_fixtures(tmp_path, rules={}, enforce_invariant=True)


@pytest.mark.unit
def test_dir_evidence_must_appear_in_prompt(tmp_path: Path) -> None:
    """Dir evidence not in prompt fails."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: bad-dir
description: dir evidence missing token
variant: simple
prompt: |
  Tell me about adding a thing.
expected:
  required:
    - rules/999-test-core.md
trigger_evidence:
  dir: [skills/]
"""
    _write_fixture(tmp_path, body)
    with pytest.raises(FixtureValidationError):
        load_fixtures(tmp_path, rules={}, enforce_invariant=True)


@pytest.mark.unit
def test_kw_evidence_word_boundary(tmp_path: Path) -> None:
    """kw:warehouse must NOT match warehouses (plural)."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: bad-plural
description: warehouse vs warehouses
variant: simple
prompt: |
  Investigate warehouses today.
expected:
  required:
    - rules/999-test-core.md
trigger_evidence:
  kw: [warehouse]
"""
    _write_fixture(tmp_path, body)
    with pytest.raises(FixtureValidationError):
        load_fixtures(tmp_path, rules={}, enforce_invariant=True)


@pytest.mark.unit
def test_ext_evidence_matches_filename(tmp_path: Path) -> None:
    """Ext .py matches a real .py filename."""
    body = """
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: ok-py
description: ext py with real filename
variant: simple
prompt: |
  Edit analytics/etl_pipeline.py to add a thing.
expected:
  required:
    - rules/999-test-core.md
trigger_evidence:
  ext: [.py]
"""
    _write_fixture(tmp_path, body)
    fixtures = load_fixtures(tmp_path, rules={}, enforce_invariant=True)
    assert len(fixtures) == 1


# ---------------------------------------------------------------------------
# load_fixture (singular)
# ---------------------------------------------------------------------------

_VALID_YAML = """\
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: target-fixture
description: a valid test fixture
variant: simple
prompt: |
  Set up a cortex-search service over our document corpus.
expected:
  required:
    - rules/999-test-core.md
    - rules/116-snowflake-cortex-search.md
  dependencies:
    - rules/100-snowflake-core.md
  forbidden: []
  optional: []
trigger_evidence:
  kw: [cortex-search]
"""

_BROKEN_YAML = """\
schema_version: 99
updated: 2026-05-16T12:00:00-07:00
id: broken-fixture
description: broken schema version
variant: simple
prompt: |
  Some prompt about broken things.
expected:
  required:
    - rules/999-test-core.md
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: [broken]
"""


@pytest.mark.unit
def test_load_fixture_fast_path(tmp_path: Path) -> None:
    """load_fixture finds a fixture when filename matches the id field (fast path)."""
    (tmp_path / "target-fixture.yaml").write_text(_VALID_YAML, encoding="utf-8")
    fixture = load_fixture(tmp_path, "target-fixture", rules=None, enforce_invariant=False)
    assert fixture.id == "target-fixture"
    assert fixture.description == "a valid test fixture"


@pytest.mark.unit
def test_load_fixture_fallback_scan(tmp_path: Path) -> None:
    """load_fixture scans all files when the filename doesn't match the id field."""
    (tmp_path / "other-name.yaml").write_text(_VALID_YAML, encoding="utf-8")
    fixture = load_fixture(tmp_path, "target-fixture", rules=None, enforce_invariant=False)
    assert fixture.id == "target-fixture"


@pytest.mark.unit
def test_load_fixture_not_found(tmp_path: Path) -> None:
    """load_fixture raises FixtureValidationError when no fixture matches the id."""
    (tmp_path / "target-fixture.yaml").write_text(_VALID_YAML, encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="not found"):
        load_fixture(tmp_path, "nonexistent-id", rules=None, enforce_invariant=False)


@pytest.mark.unit
def test_load_fixture_fast_path_id_differs_then_fallback(tmp_path: Path) -> None:
    """Fast path loads the file but id: field differs; fallback finds correct fixture."""
    different_id_yaml = _VALID_YAML.replace("id: target-fixture", "id: actual-id")
    (tmp_path / "target-fixture.yaml").write_text(different_id_yaml, encoding="utf-8")
    (tmp_path / "actual-id.yaml").write_text(
        different_id_yaml.replace("id: actual-id", "id: actual-id"), encoding="utf-8"
    )
    fixture = load_fixture(tmp_path, "actual-id", rules=None, enforce_invariant=False)
    assert fixture.id == "actual-id"


@pytest.mark.unit
def test_load_fixture_enforces_invariant(tmp_path: Path) -> None:
    """load_fixture raises on invariant violations even in single-fixture mode."""
    bad_evidence_yaml = _VALID_YAML.replace(
        "kw: [cortex-search]",
        "kw: [this-token-is-not-in-the-prompt]",
    )
    (tmp_path / "target-fixture.yaml").write_text(bad_evidence_yaml, encoding="utf-8")
    with pytest.raises(FixtureValidationError, match="trigger-evidence"):
        load_fixture(tmp_path, "target-fixture", rules=None, enforce_invariant=True)


@pytest.mark.unit
def test_load_fixture_isolation_from_broken_sibling(tmp_path: Path) -> None:
    """load_fixture succeeds when an unrelated sibling fixture has an invalid schema."""
    (tmp_path / "target-fixture.yaml").write_text(_VALID_YAML, encoding="utf-8")
    (tmp_path / "broken-fixture.yaml").write_text(_BROKEN_YAML, encoding="utf-8")
    fixture = load_fixture(tmp_path, "target-fixture", rules=None, enforce_invariant=False)
    assert fixture.id == "target-fixture"


# ---------------------------------------------------------------------------
# updated: field validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_updated_field_required(tmp_path: Path) -> None:
    """Missing updated: raises FixtureValidationError."""
    body = _VALID_YAML.replace("updated: 2026-05-16T12:00:00-07:00\n", "")
    _write_fixture(tmp_path, body)
    with pytest.raises(FixtureValidationError, match="updated"):
        load_fixtures(tmp_path, rules={}, enforce_invariant=False)


@pytest.mark.unit
def test_updated_field_must_be_iso8601_with_offset(tmp_path: Path) -> None:
    """Non-ISO8601 or offset-less updated: values are rejected."""
    bad_values = [
        "2026-05-16",
        "2026-05-16 12:00:00",
        "2026-05-16T12:00:00",  # no offset
        "not-a-date",
        "",
    ]
    for bad in bad_values:
        body = _VALID_YAML.replace(
            "updated: 2026-05-16T12:00:00-07:00",
            f"updated: '{bad}'" if bad else "updated: ''",
        )
        _write_fixture(tmp_path, body)
        with pytest.raises(FixtureValidationError, match="updated"):
            load_fixtures(tmp_path, rules={}, enforce_invariant=False)


@pytest.mark.unit
def test_updated_field_accepts_z_offset(tmp_path: Path) -> None:
    """ISO 8601 with 'Z' UTC offset is accepted (canonicalized to +00:00)."""
    body = _VALID_YAML.replace(
        "updated: 2026-05-16T12:00:00-07:00",
        "updated: 2026-05-16T19:00:00Z",
    )
    _write_fixture(tmp_path, body)
    fixtures = load_fixtures(tmp_path, rules={}, enforce_invariant=False)
    # PyYAML parses ISO timestamps as datetimes; the parser canonicalizes
    # the offset, so 'Z' becomes '+00:00' (still valid per the schema regex).
    assert fixtures[0].updated in {"2026-05-16T19:00:00Z", "2026-05-16T19:00:00+00:00"}


@pytest.mark.unit
def test_updated_field_accepts_positive_offset(tmp_path: Path) -> None:
    """ISO 8601 with positive timezone offset is accepted."""
    body = _VALID_YAML.replace(
        "updated: 2026-05-16T12:00:00-07:00",
        "updated: 2026-05-16T20:00:00+01:00",
    )
    _write_fixture(tmp_path, body)
    fixtures = load_fixtures(tmp_path, rules={}, enforce_invariant=False)
    assert fixtures[0].updated == "2026-05-16T20:00:00+01:00"


@pytest.mark.unit
def test_current_updated_timestamp_format() -> None:
    """current_updated_timestamp returns a value that passes schema validation."""
    import re

    ts = current_updated_timestamp()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$", ts), (
        f"got {ts!r}"
    )


@pytest.mark.unit
def test_read_updated_returns_value(tmp_path: Path) -> None:
    """read_updated returns the on-disk value when present."""
    p = _write_fixture(tmp_path, _VALID_YAML)
    assert read_updated(p) == "2026-05-16T12:00:00-07:00"


@pytest.mark.unit
def test_read_updated_returns_none_when_missing(tmp_path: Path) -> None:
    """read_updated returns None when the field is missing or unreadable."""
    body = _VALID_YAML.replace("updated: 2026-05-16T12:00:00-07:00\n", "")
    p = _write_fixture(tmp_path, body)
    assert read_updated(p) is None
    assert read_updated(tmp_path / "does-not-exist.yaml") is None
