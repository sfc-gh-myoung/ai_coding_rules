"""Extra tests for validate.py covering null-byte paths and --templates CLI mode.

Covers:
- validate CLI with no PATH (prints help, exits 0) — lines 1862-1864
- validate CLI --templates with empty dir — lines 1949-1951, 1955-1957
- validate CLI --templates with real template file — lines 1937-1996
- SchemaValidator._get_null_byte_locations long-line preview — lines 280-282
- ExampleValidator._get_null_byte_locations positions — lines 1549-1576
- ExampleValidator._validate_file_integrity verbose=True/False — lines 1594, 1597-1621
- SchemaValidator._validate_ascii_patterns RULES_INDEX table exemption
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.validate import (
    ExampleValidator,
    SchemaValidator,
    ValidationResult,
)

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# validate CLI — no-path branch (lines 1862-1864)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_validate_no_path_shows_help_exits_zero() -> None:
    """Validate with no PATH argument prints help and exits 0."""
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# SchemaValidator._get_null_byte_locations — long-line preview (lines 280-282)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_schema_validator_null_byte_long_line_preview_truncated() -> None:
    """Lines >60 chars get a '...' suffix in the null-byte location preview."""
    sv = SchemaValidator(project_root=PROJECT_ROOT)
    # Null byte embedded in a line that is >60 characters
    long_prefix = "x" * 65
    content = long_prefix + "\x00" + "y" * 10
    null_pos = len(long_prefix)
    locations = sv._get_null_byte_locations(content, [null_pos])
    assert len(locations) == 1
    assert locations[0]["preview"].endswith("...")


@pytest.mark.unit
def test_schema_validator_null_byte_short_line_no_ellipsis() -> None:
    """Lines <=60 chars do NOT get '...' suffix."""
    sv = SchemaValidator(project_root=PROJECT_ROOT)
    content = "short\x00line"
    locations = sv._get_null_byte_locations(content, [5])
    assert len(locations) == 1
    assert not locations[0]["preview"].endswith("...")


# ---------------------------------------------------------------------------
# ExampleValidator._get_null_byte_locations (lines 1549-1576)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_example_validator_null_byte_locations_basic() -> None:
    """_get_null_byte_locations returns correct line, column, offset."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    content = "abcde\x00fgh"
    locations = ev._get_null_byte_locations(content, [5])
    assert len(locations) == 1
    assert locations[0]["line"] == 1
    assert locations[0]["column"] == 6
    assert locations[0]["offset"] == 5


@pytest.mark.unit
def test_example_validator_null_byte_second_line() -> None:
    """Null byte on second line reports correct line number."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    content = "line1\nab\x00cd"
    null_pos = content.index("\x00")
    locations = ev._get_null_byte_locations(content, [null_pos])
    assert locations[0]["line"] == 2
    assert locations[0]["column"] == 3


@pytest.mark.unit
def test_example_validator_null_byte_long_line_preview_truncated() -> None:
    """Lines >60 chars get '...' suffix in ExampleValidator locations."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    long_prefix = "a" * 65
    content = long_prefix + "\x00" + "b"
    pos = len(long_prefix)
    locations = ev._get_null_byte_locations(content, [pos])
    assert locations[0]["preview"].endswith("...")


@pytest.mark.unit
def test_example_validator_null_byte_multiple_positions() -> None:
    """Multiple null bytes produce multiple location entries."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    content = "a\x00b\x00c"
    locations = ev._get_null_byte_locations(content, [1, 3])
    assert len(locations) == 2


# ---------------------------------------------------------------------------
# ExampleValidator._validate_file_integrity (lines 1594, 1597-1621)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_example_validator_file_integrity_verbose_true_individual_errors() -> None:
    """verbose=True emits one error per null byte with location detail."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    content = "good content\x00more content"
    result = ValidationResult(file_path=Path("fake.md"))
    is_clean = ev._validate_file_integrity(content, result, verbose=True)
    assert not is_clean
    assert any("Null byte at line" in e.message for e in result.errors)


@pytest.mark.unit
def test_example_validator_file_integrity_verbose_false_summary_error() -> None:
    """verbose=False emits a single summary error for all null bytes."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    content = "abc\x00def"
    result = ValidationResult(file_path=Path("fake.md"))
    is_clean = ev._validate_file_integrity(content, result, verbose=False)
    assert not is_clean
    # Summary error mentions count or 'null byte'
    assert any("null byte" in e.message.lower() for e in result.errors)


@pytest.mark.unit
def test_example_validator_file_integrity_clean_content() -> None:
    """Content with no null bytes returns True."""
    ev = ExampleValidator(project_root=PROJECT_ROOT)
    content = "completely clean content without null bytes"
    result = ValidationResult(file_path=Path("fake.md"))
    is_clean = ev._validate_file_integrity(content, result, verbose=False)
    assert is_clean
    assert len(result.errors) == 0


# ---------------------------------------------------------------------------
# validate CLI --templates mode (lines 1937-1996)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_validate_templates_mode_nonexistent_dir(tmp_path: Path) -> None:
    """--templates with a nonexistent directory exits 0 (no-templates-dir branch)."""
    missing = tmp_path / "does-not-exist"
    result = runner.invoke(app, ["validate", str(missing), "--templates"])
    assert result.exit_code == 0


@pytest.mark.integration
def test_validate_templates_mode_empty_dir(tmp_path: Path) -> None:
    """--templates with empty directory exits 0 (no-template-files branch)."""
    result = runner.invoke(app, ["validate", str(tmp_path), "--templates"])
    assert result.exit_code == 0


@pytest.mark.integration
def test_validate_templates_mode_with_real_template(tmp_path: Path) -> None:
    """--templates with a real template file produces a summary table."""
    real_template = PROJECT_ROOT / "templates" / "AGENTS_NO_MODE.md.template"
    if not real_template.exists():
        pytest.skip("AGENTS_NO_MODE.md.template not present in templates/")
    templates_sub = tmp_path / "templates"
    templates_sub.mkdir()
    (templates_sub / "AGENTS_NO_MODE.md.template").write_bytes(real_template.read_bytes())
    result = runner.invoke(app, ["validate", str(tmp_path), "--templates"])
    # 0 = all valid, 1 = some invalid — both are expected depending on content
    assert result.exit_code in (0, 1)
    assert "Template Validation Summary" in result.output


# ---------------------------------------------------------------------------
# SchemaValidator._validate_ascii_patterns — non-index exemption check
# ---------------------------------------------------------------------------

TABLE_CONTENT = "| Rule | Tier |\n|---------|------|\n| foo.md | High |\n"


@pytest.mark.unit
def test_non_rules_index_table_is_still_flagged(tmp_path: Path) -> None:
    """ASCII table in any other file name must still be flagged (exemption is narrow)."""
    other_file = tmp_path / "OTHER_INDEX.md"
    other_file.write_text(TABLE_CONTENT)
    validator = SchemaValidator(project_root=PROJECT_ROOT)
    result = validator.validate_agents_md(other_file)
    table_errors = [e for e in result.errors if "ASCII table" in e.message]
    assert table_errors, "Non-RULES_INDEX file with |---| should still fail validation"
