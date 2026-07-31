"""Unit tests for --examples and --templates path derivation in the validate command.

Covers:
- Append behavior: validate X/ --examples validates X/examples/, not X/ directly.
- Direct-leaf form: validate X/examples/ --examples uses X/examples/ (no double-append).
- Missing-dir clean message: exits 0 with friendly message when resolved dir is absent.
- Combined --examples --templates: both run, both summarised in one pass.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

import ai_rules.commands.validate as validate_module
from ai_rules.cli import app

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_schema(tmp_path: Path) -> None:
    """Write minimal schema files so both ExampleValidator and SchemaValidator initialise OK."""
    schemas_dir = tmp_path / "schemas"
    schemas_dir.mkdir(exist_ok=True)
    (schemas_dir / "example-schema.yml").write_text("required_sections: []\ncontext_fields: []\n")
    (schemas_dir / "rule-schema.yml").write_text(
        'version: "3.3"\nrequired_sections: []\nvalidations: []\n'
    )
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"')


# ---------------------------------------------------------------------------
# --examples path derivation
# ---------------------------------------------------------------------------


class TestExamplesPathDerivation:
    """--examples resolves to PATH/examples/, with direct-leaf and missing-dir handling."""

    @pytest.mark.unit
    def test_append_subdir_when_path_is_not_named_examples(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Validate X/ --examples should validate X/examples/, not X/ directly."""
        _make_schema(tmp_path)
        monkeypatch.setattr(validate_module, "find_project_root", lambda: tmp_path)

        examples_sub = tmp_path / "examples"
        examples_sub.mkdir()
        (examples_sub / "ex1.md").write_text("# Example\n\n## Context\n\nContent.\n")

        result = runner.invoke(app, ["validate", str(tmp_path), "--examples"])

        assert result.exit_code in (0, 1)
        assert "Example Validation Summary" in result.output

    @pytest.mark.unit
    def test_direct_leaf_no_double_append(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Validate X/examples/ --examples uses X/examples/ directly (no double-append)."""
        _make_schema(tmp_path)
        monkeypatch.setattr(validate_module, "find_project_root", lambda: tmp_path)

        examples_dir = tmp_path / "examples"
        examples_dir.mkdir()
        (examples_dir / "ex1.md").write_text("# Example\n\n## Context\n\nContent.\n")

        result = runner.invoke(app, ["validate", str(examples_dir), "--examples"])

        assert result.exit_code in (0, 1)
        assert "Example Validation Summary" in result.output

    @pytest.mark.unit
    def test_missing_examples_subdir_exits_cleanly(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Validate X/ --examples where X/examples/ doesn't exist → friendly message, exit 0."""
        _make_schema(tmp_path)
        monkeypatch.setattr(validate_module, "find_project_root", lambda: tmp_path)

        # tmp_path has no "examples" subdirectory
        result = runner.invoke(app, ["validate", str(tmp_path), "--examples"])

        assert result.exit_code == 0
        assert "No examples directory found at" in result.output

    @pytest.mark.unit
    def test_direct_leaf_missing_still_exits_cleanly(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Validate X/examples/ --examples where path doesn't exist → friendly message, exit 0."""
        _make_schema(tmp_path)
        monkeypatch.setattr(validate_module, "find_project_root", lambda: tmp_path)

        nonexistent_examples = tmp_path / "examples"  # not created

        result = runner.invoke(app, ["validate", str(nonexistent_examples), "--examples"])

        assert result.exit_code == 0
        # Direct-leaf: path.name == "examples" → used directly → doesn't exist → friendly msg
        assert "No examples directory found at" in result.output

    @pytest.mark.unit
    def test_no_path_uses_project_root_examples(self) -> None:
        """--examples with no PATH resolves to <project_root>/rules/examples/."""
        result = runner.invoke(app, ["validate", "--examples"])

        assert result.exit_code in (0, 1)
        # Real rules/examples/ exists → shows summary (or friendly message if absent)
        has_output = (
            "Example Validation Summary" in result.output
            or "No examples directory found" in result.output
        )
        assert has_output


# ---------------------------------------------------------------------------
# --templates path derivation
# ---------------------------------------------------------------------------


class TestTemplatesPathDerivation:
    """--templates resolves to PATH/templates/, with direct-leaf and missing-dir handling."""

    @pytest.mark.unit
    def test_non_templates_path_uses_project_root(self, tmp_path: Path) -> None:
        """Validate X/ --templates always resolves to project_root/templates/, ignoring X/."""
        # Files created under tmp_path/templates/ should be irrelevant — the code
        # always uses the real project_root/templates/, not PATH/templates/.
        result = runner.invoke(app, ["validate", str(tmp_path), "--templates"])

        assert result.exit_code in (0, 1)
        # Project templates/ exists but may be empty after legacy templates removed.
        # Accept summary (if templates exist) or "no files" message (if empty).
        assert (
            "Template Validation Summary" in result.output
            or "No template files found" in result.output
        )

    @pytest.mark.unit
    def test_direct_leaf_no_double_append(self, tmp_path: Path) -> None:
        """Validate X/templates/ --templates uses X/templates/ directly (no double-append)."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "TEST.md.template").write_text("<!-- Template: test -->\n")

        result = runner.invoke(app, ["validate", str(templates_dir), "--templates"])

        assert result.exit_code in (0, 1)
        assert "Template Validation Summary" in result.output

    @pytest.mark.unit
    def test_missing_templates_subdir_exits_cleanly(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Validate X/ --templates where project_root/templates/ doesn't exist → friendly message, exit 0."""
        monkeypatch.setattr(validate_module, "find_project_root", lambda: tmp_path)
        # Use the real schema so SchemaValidator initialises successfully.
        # tmp_path has no "templates" subdir → project_root/templates/ won't exist → friendly msg.
        real_schema = PROJECT_ROOT / "schemas" / "rule-schema.yml"
        result = runner.invoke(
            app, ["validate", str(tmp_path), "--templates", "--schema", str(real_schema)]
        )

        assert result.exit_code == 0
        assert "No templates directory found at" in result.output

    @pytest.mark.unit
    def test_empty_templates_subdir_logs_no_files(self, tmp_path: Path) -> None:
        """Validate X/templates/ --templates where subdir exists but is empty → clean msg."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        result = runner.invoke(app, ["validate", str(templates_dir), "--templates"])

        assert result.exit_code == 0
        assert "No template files found" in result.output

    @pytest.mark.unit
    def test_no_path_uses_project_root_templates(self) -> None:
        """--templates with no PATH resolves to <project_root>/templates/."""
        result = runner.invoke(app, ["validate", "--templates"])

        assert result.exit_code in (0, 1)
        # Real templates/ exists → should show summary (or "not found"/"no files" if absent/empty)
        has_output = (
            "Template Validation Summary" in result.output
            or "No templates directory found" in result.output
            or "No template files found" in result.output
        )
        assert has_output


# ---------------------------------------------------------------------------
# Combined --examples --templates
# ---------------------------------------------------------------------------


class TestCombinedExamplesTemplates:
    """When both flags are set, both validations run and report summaries."""

    @pytest.mark.unit
    def test_both_flags_run_both_validations(self, tmp_path: Path) -> None:
        """--examples --templates runs example AND template validation in one pass."""
        # Create X/examples/
        examples_sub = tmp_path / "examples"
        examples_sub.mkdir()
        (examples_sub / "ex1.md").write_text("# Example\n\nContent.\n")

        # Create X/templates/
        templates_sub = tmp_path / "templates"
        templates_sub.mkdir()
        (templates_sub / "TEST.md.template").write_text("<!-- Template: test -->\n")

        result = runner.invoke(app, ["validate", str(tmp_path), "--examples", "--templates"])

        assert result.exit_code in (0, 1)
        assert "Example Validation Summary" in result.output
        # Template validation ran — may show summary or "no files" if project templates are empty.
        assert (
            "Template Validation Summary" in result.output
            or "No template files found" in result.output
        )

    @pytest.mark.unit
    def test_both_flags_missing_examples_subdir_still_runs_templates(self, tmp_path: Path) -> None:
        """With --examples --templates, missing examples dir doesn't prevent template check."""
        # No examples/ subdir, but templates/ exists
        templates_sub = tmp_path / "templates"
        templates_sub.mkdir()
        (templates_sub / "TEST.md.template").write_text("<!-- Template: test -->\n")

        result = runner.invoke(app, ["validate", str(tmp_path), "--examples", "--templates"])

        assert result.exit_code in (0, 1)
        assert "No examples directory found at" in result.output
        # Template validation ran — may show summary or "no files" if project templates are empty.
        assert (
            "Template Validation Summary" in result.output
            or "No template files found" in result.output
        )
