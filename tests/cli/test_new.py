"""Tests for the ai-rules new command.

Validates that the CLI command creates v3.2 schema compliant rule templates.
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner(env={"NO_COLOR": "1"})


class TestNewCommandHelp:
    """Test help output."""

    def test_help_output(self):
        """Test --help output shows correct information."""
        result = runner.invoke(app, ["new", "--help"])

        assert result.exit_code == 0
        assert "Create a new rule file" in result.output
        assert "--output-dir" in result.output
        assert "--context-tier" in result.output
        assert "--keywords" in result.output
        assert "--force" in result.output


class TestNewCommandHappyPath:
    """Test successful rule file creation."""

    def test_create_basic_rule_file(self, tmp_path: Path):
        """Test creating a basic rule file."""
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0

        # Verify file created
        output_path = tmp_path / "100-test-rule.md"
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "# 100-test-rule" in content
        assert "## Metadata" in content
        assert "**SchemaVersion:** v3.2" in content
        assert "**ContextTier:** Medium" in content  # Default tier

    def test_create_rule_with_letter_suffix(self, tmp_path: Path):
        """Test creating a rule file with letter suffix (e.g., 111a-example)."""
        result = runner.invoke(
            app, ["new", "111a-snowflake-feature", "--output-dir", str(tmp_path)]
        )

        assert result.exit_code == 0

        output_path = tmp_path / "111a-snowflake-feature.md"
        assert output_path.exists()

        content = output_path.read_text()
        assert "# 111a-snowflake-feature" in content

    def test_create_rule_with_md_extension(self, tmp_path: Path):
        """Test creating a rule file when filename includes .md extension."""
        result = runner.invoke(app, ["new", "100-test-rule.md", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0

        # Should not double the extension
        output_path = tmp_path / "100-test-rule.md"
        assert output_path.exists()
        assert not (tmp_path / "100-test-rule.md.md").exists()


class TestNewCommandContextTier:
    """Test --context-tier flag."""

    @pytest.mark.parametrize("tier", ["Critical", "High", "Medium", "Low"])
    def test_create_rule_with_context_tier(self, tmp_path: Path, tier: str):
        """Test creating rule files with each context tier."""
        result = runner.invoke(
            app,
            ["new", "200-test-rule", "--output-dir", str(tmp_path), "--context-tier", tier],
        )

        assert result.exit_code == 0

        content = (tmp_path / "200-test-rule.md").read_text()
        assert f"**ContextTier:** {tier}" in content

    def test_invalid_context_tier_error(self, tmp_path: Path):
        """Test error with invalid context tier."""
        result = runner.invoke(
            app,
            [
                "new",
                "100-test-rule",
                "--output-dir",
                str(tmp_path),
                "--context-tier",
                "InvalidTier",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid context tier" in result.output or "invalid" in result.output.lower()


class TestNewCommandKeywords:
    """Test --keywords flag."""

    def test_create_rule_with_custom_keywords(self, tmp_path: Path):
        """Test creating a rule file with custom keywords."""
        custom_keywords = "test, example, demo, sample, validation, verification, template, placeholder, prototype, reference"
        result = runner.invoke(
            app,
            ["new", "300-test-rule", "--output-dir", str(tmp_path), "--keywords", custom_keywords],
        )

        assert result.exit_code == 0

        content = (tmp_path / "300-test-rule.md").read_text()
        assert custom_keywords in content

    def test_invalid_keyword_count_too_few(self, tmp_path: Path):
        """Test error with too few keywords."""
        too_few_keywords = "one, two, three"
        result = runner.invoke(
            app,
            ["new", "100-test-rule", "--output-dir", str(tmp_path), "--keywords", too_few_keywords],
        )

        assert result.exit_code == 1
        assert "5-20" in result.output or "Keywords must contain" in result.output

    def test_invalid_keyword_count_too_many(self, tmp_path: Path):
        """Test error with too many keywords."""
        too_many_keywords = ", ".join([f"keyword{i}" for i in range(25)])
        result = runner.invoke(
            app,
            [
                "new",
                "100-test-rule",
                "--output-dir",
                str(tmp_path),
                "--keywords",
                too_many_keywords,
            ],
        )

        assert result.exit_code == 1
        assert "5-20" in result.output or "Keywords must contain" in result.output


class TestNewCommandForce:
    """Test --force flag."""

    def test_overwrite_existing_file_with_force(self, tmp_path: Path):
        """Test that --force overwrites existing file."""
        # Create file first time
        result1 = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])
        assert result1.exit_code == 0

        first_content = (tmp_path / "100-test-rule.md").read_text()

        # Overwrite with different tier using --force
        result2 = runner.invoke(
            app,
            [
                "new",
                "100-test-rule",
                "--output-dir",
                str(tmp_path),
                "--context-tier",
                "Critical",
                "--force",
            ],
        )
        assert result2.exit_code == 0

        second_content = (tmp_path / "100-test-rule.md").read_text()

        assert first_content != second_content
        assert "**ContextTier:** Critical" in second_content

    def test_file_exists_error_without_force(self, tmp_path: Path):
        """Test error when file exists without --force."""
        # Create file first time
        result1 = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])
        assert result1.exit_code == 0

        # Try to create again without --force
        result2 = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result2.exit_code == 1
        assert "already exists" in result2.output


class TestNewCommandErrors:
    """Test error handling."""

    def test_invalid_filename_no_number(self, tmp_path: Path):
        """Test error with invalid filename (no number prefix)."""
        result = runner.invoke(app, ["new", "invalid-filename", "--output-dir", str(tmp_path)])

        assert result.exit_code == 1
        assert "Invalid filename format" in result.output

    def test_invalid_filename_wrong_number_format(self, tmp_path: Path):
        """Test error with invalid filename (wrong number format)."""
        result = runner.invoke(app, ["new", "1-snowflake-sql", "--output-dir", str(tmp_path)])

        assert result.exit_code == 1
        assert "Invalid filename format" in result.output

    def test_invalid_filename_uppercase(self, tmp_path: Path):
        """Test error with invalid filename (uppercase letters)."""
        result = runner.invoke(app, ["new", "100-Snowflake-SQL", "--output-dir", str(tmp_path)])

        assert result.exit_code == 1
        assert "Invalid filename format" in result.output


class TestNewCommandOutputDirectory:
    """Test output directory handling."""

    def test_creates_nested_directory(self, tmp_path: Path):
        """Test that nested output directories are created."""
        nested_dir = tmp_path / "custom" / "nested" / "path"
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(nested_dir)])

        assert result.exit_code == 0
        assert nested_dir.exists()
        assert (nested_dir / "100-test-rule.md").exists()

    def test_default_output_dir_message(self, tmp_path: Path):
        """Test that success message shows correct output path."""
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0
        # The path may be wrapped by Rich console, so check for filename
        assert "100-test-rule.md" in result.output


class TestNewCommandOutput:
    """Test CLI output formatting."""

    def test_success_output_contains_next_steps(self, tmp_path: Path):
        """Test that success output contains next steps."""
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "Next steps" in result.output
        assert "Validate" in result.output or "validate" in result.output

    def test_success_output_shows_summary(self, tmp_path: Path):
        """Test that success output shows summary panel."""
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0
        # Check for key summary elements
        assert "100-test-rule" in result.output
        assert "Medium" in result.output  # Default context tier


class TestNewCommandTemplateContent:
    """Test generated template content."""

    def test_template_has_required_sections(self, tmp_path: Path):
        """Test that generated template has all required v3.2 sections."""
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0

        content = (tmp_path / "100-test-rule.md").read_text()

        required_sections = [
            "## Metadata",
            "## Scope",
            "## References",
            "## Contract",
            "## Anti-Patterns and Common Mistakes",
        ]

        for section in required_sections:
            assert section in content, f"Missing required section: {section}"

    def test_template_has_contract_subsections(self, tmp_path: Path):
        """Test that Contract section has all required subsections."""
        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0

        content = (tmp_path / "100-test-rule.md").read_text()

        contract_subsections = [
            "### Inputs and Prerequisites",
            "### Mandatory",
            "### Forbidden",
            "### Execution Steps",
            "### Output Format",
            "### Validation",
            "### Post-Execution Checklist",
        ]

        for subsection in contract_subsections:
            assert subsection in content, f"Missing Contract subsection: {subsection}"

    def test_template_keyword_count(self, tmp_path: Path):
        """Test that auto-generated keywords meet 5-20 count requirement."""
        import re

        result = runner.invoke(app, ["new", "200-test-keywords", "--output-dir", str(tmp_path)])

        assert result.exit_code == 0

        content = (tmp_path / "200-test-keywords.md").read_text()

        # Extract keywords line
        keywords_match = re.search(r"\*\*Keywords:\*\*\s+(.+)", content)
        assert keywords_match

        keywords = keywords_match.group(1)
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        assert 5 <= len(keyword_list) <= 20


class TestTemplateGeneratorDirect:
    """Test TemplateGenerator methods directly for uncovered branches."""

    def test_get_default_keywords_out_of_range(self):
        """Test fallback keywords for number outside all RANGE_KEYWORDS ranges."""
        from ai_rules.commands.new import TemplateGenerator

        # Number > 999 is outside all defined ranges
        keywords = TemplateGenerator.get_default_keywords(1500, "custom-tool")
        assert "custom" in keywords
        assert "specialized" in keywords

    def test_get_default_keywords_few_keywords_gets_fillers(self, monkeypatch: pytest.MonkeyPatch):
        """Test that filler keywords are added when combined count < 5 (lines 294-301)."""
        from ai_rules.commands.new import TemplateGenerator

        # Override RANGE_KEYWORDS so matching range returns very few keywords,
        # ensuring combined deduped list has < 5 items and fillers are triggered.
        monkeypatch.setattr(
            TemplateGenerator,
            "RANGE_KEYWORDS",
            {(0, 99): "core"},
        )

        keywords = TemplateGenerator.get_default_keywords(50, "x")
        keyword_list = [kw.strip() for kw in keywords.split(",")]
        assert len(keyword_list) >= 5
        # Should include fillers
        assert any(
            filler in keyword_list
            for filler in [
                "implementation",
                "best practices",
                "patterns",
                "guidelines",
                "optimization",
            ]
        )

    def test_generate_template_invalid_context_tier(self):
        """Test ValueError for invalid context tier in generate_template."""
        from ai_rules.commands.new import TemplateGenerator

        with pytest.raises(ValueError, match="Context tier must be one of"):
            TemplateGenerator.generate_template("100-test-rule", context_tier="Invalid")

    def test_format_success_message(self):
        """Test format_success_message returns expected content."""
        from ai_rules.commands.new import TemplateGenerator

        msg = TemplateGenerator.format_success_message(Path("/tmp/100-test-rule.md"))
        assert "Created rule template" in msg
        assert "Next steps" in msg
        assert "100-test-rule.md" in msg

    def test_format_error_message(self):
        """Test format_error_message returns expected content."""
        from ai_rules.commands.new import TemplateGenerator

        msg = TemplateGenerator.format_error_message(ValueError("something broke"))
        assert "Error" in msg
        assert "something broke" in msg


class TestNewCLIEdgeCases:
    """Test CLI edge cases for uncovered branches in the new() function."""

    def test_parse_failure_in_summary_fallback(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that ValueError during summary parse_rule_filename falls back gracefully.

        Lines 510-511: When create_rule_file succeeds but the summary
        parse_rule_filename call raises ValueError, it falls back to
        'auto-generated' keywords.
        """
        from ai_rules.commands.new import TemplateGenerator

        # We need create_rule_file to succeed, then the summary parse to fail.
        # Use monkeypatch to make parse_rule_filename fail only on the second call.
        original_parse = TemplateGenerator.parse_rule_filename
        call_count = [0]

        @staticmethod
        def patched_parse(filename):
            call_count[0] += 1
            if call_count[0] > 1:
                raise ValueError("parse failed on summary")
            return original_parse(filename)

        monkeypatch.setattr(TemplateGenerator, "parse_rule_filename", patched_parse)

        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])
        assert result.exit_code == 0

    def test_unexpected_exception_handler(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test that unexpected exceptions are caught and exit with code 1.

        Lines 535-537: generic Exception handler in new() CLI function.
        """
        from ai_rules.commands.new import TemplateGenerator

        monkeypatch.setattr(
            TemplateGenerator,
            "create_rule_file",
            staticmethod(lambda **kwargs: (_ for _ in ()).throw(RuntimeError("disk on fire"))),
        )

        result = runner.invoke(app, ["new", "100-test-rule", "--output-dir", str(tmp_path)])
        assert result.exit_code == 1
        assert "Unexpected error" in result.output or "disk on fire" in result.output
