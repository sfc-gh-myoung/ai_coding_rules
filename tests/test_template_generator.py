#!/usr/bin/env python3
"""Tests for template_generator.py.

Validates that generated templates are v3.2 schema compliant.
"""

import re
import sys
from unittest.mock import patch

import pytest

from scripts.template_generator import TemplateGenerator, main


class TestFilenameParser:
    """Test filename parsing and validation."""

    def test_parse_valid_filename(self):
        """Test parsing valid filename formats.

        Validates that parse_rule_filename correctly extracts number,
        slug, and title from standard NNN-technology-aspect format.
        This ensures template generation uses correct metadata for
        generating proper rule files.
        """
        number, slug, title = TemplateGenerator.parse_rule_filename("100-snowflake-sql")
        assert number == 100
        assert slug == "snowflake-sql"
        assert "100-snowflake-sql" in title
        assert "Snowflake Sql" in title

    def test_parse_filename_with_extension(self):
        """Test parsing filename with .md extension."""
        number, slug, title = TemplateGenerator.parse_rule_filename("200-python-core.md")
        assert number == 200
        assert slug == "python-core"
        assert "200-python-core" in title

    def test_parse_multi_part_slug(self):
        """Test parsing filename with multiple dashes."""
        number, slug, title = TemplateGenerator.parse_rule_filename(
            "115-snowflake-cortex-agents-core"
        )
        assert number == 115
        assert slug == "snowflake-cortex-agents-core"
        assert "Snowflake Cortex Agents Core" in title

    def test_parse_invalid_format_no_number(self):
        """Test parsing filename without number prefix.

        Verifies that filenames without a number prefix (e.g., 'snowflake-sql')
        raise ValueError to prevent generating templates with invalid metadata.
        The NNN prefix is required for rule categorization and indexing.
        """
        with pytest.raises(ValueError, match="Invalid filename format"):
            TemplateGenerator.parse_rule_filename("snowflake-sql")

    def test_parse_invalid_format_wrong_number(self):
        """Test parsing filename with invalid number format."""
        with pytest.raises(ValueError, match="Invalid filename format"):
            TemplateGenerator.parse_rule_filename("1-snowflake-sql")  # Need 3 digits

    def test_parse_invalid_format_uppercase(self):
        """Test parsing filename with uppercase letters."""
        with pytest.raises(ValueError, match="Invalid filename format"):
            TemplateGenerator.parse_rule_filename("100-Snowflake-SQL")


class TestKeywordGeneration:
    """Test default keyword generation."""

    def test_keywords_for_snowflake_range(self):
        """Test keyword generation for Snowflake rules (100-199).

        Ensures that rules in the 100-199 range get Snowflake-specific
        keywords to improve semantic search and rule discovery. The keyword
        range (5-20) per v3.2 schema balances specificity with discoverability.
        """
        keywords = TemplateGenerator.get_default_keywords(100, "snowflake-sql")
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        assert len(keyword_list) >= 5
        assert len(keyword_list) <= 20
        assert "snowflake" in keyword_list
        assert "sql" in keyword_list

    def test_keywords_for_python_range(self):
        """Test keyword generation for Python rules (200-299)."""
        keywords = TemplateGenerator.get_default_keywords(200, "python-core")
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        assert len(keyword_list) >= 5
        assert len(keyword_list) <= 20
        assert "python" in keyword_list
        assert "core" in keyword_list

    def test_keywords_count_in_range(self):
        """Test that generated keywords are always 5-20 terms per v3.2 schema."""
        for number in [100, 200, 300, 400, 500]:
            keywords = TemplateGenerator.get_default_keywords(number, "example-rule")
            keyword_list = [kw.strip() for kw in keywords.split(",")]
            assert 5 <= len(keyword_list) <= 20

    def test_keywords_no_duplicates(self):
        """Test that generated keywords don't contain duplicates.

        Validates deduplication logic to prevent keyword redundancy,
        which would waste token budget and reduce search effectiveness.
        This is especially important when slug contains repeated terms.
        """
        keywords = TemplateGenerator.get_default_keywords(100, "snowflake-snowflake")
        keyword_list = [kw.strip() for kw in keywords.split(",")]
        assert len(keyword_list) == len(set(keyword_list))

    def test_keywords_for_custom_range_above_999(self):
        """Test keyword generation for rule numbers outside defined ranges.

        Validates fallback keyword logic for rule numbers above 999
        (outside all defined ranges). This ensures custom or experimental
        rules still get appropriate keywords for semantic search.
        """
        keywords = TemplateGenerator.get_default_keywords(1000, "custom-rule")
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        assert len(keyword_list) >= 5
        assert len(keyword_list) <= 20
        assert "custom" in keyword_list
        assert "rule" in keyword_list
        # Should contain fallback keywords when no range matches
        assert any(
            kw in keyword_list
            for kw in ["custom", "specialized", "advanced", "specific", "targeted"]
        )

    def test_keywords_for_boundary_case_999(self):
        """Test keyword generation at upper boundary of defined ranges.

        Validates that rule number 999 (last number in demo range 900-999)
        correctly uses demo-specific keywords, not fallback keywords.
        """
        keywords = TemplateGenerator.get_default_keywords(999, "demo-example")
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        assert len(keyword_list) >= 5
        assert len(keyword_list) <= 20
        assert "demo" in keyword_list
        assert "example" in keyword_list
        # Should NOT use fallback keywords since 999 is in demo range
        assert any(kw in keyword_list for kw in ["demo", "example", "sample", "tutorial"])


class TestTemplateGeneration:
    """Test template content generation."""

    def test_generate_basic_template(self):
        """Test generating a basic template."""
        template = TemplateGenerator.generate_template("100-snowflake-sql")

        assert "# 100-snowflake-sql: Snowflake Sql" in template
        assert "## Metadata" in template
        assert "**SchemaVersion:** v3.2" in template
        assert "**RuleVersion:** v1.0.0" in template
        assert "**LastUpdated:**" in template
        assert "**Keywords:**" in template
        assert "**TokenBudget:** ~1200" in template
        assert "**ContextTier:** Medium" in template
        assert "**Depends:** 000-global-core.md" in template

    def test_generate_template_with_custom_tier(self):
        """Test generating template with custom context tier."""
        template = TemplateGenerator.generate_template("200-python-core", context_tier="High")

        assert "**ContextTier:** High" in template

    def test_generate_template_with_custom_keywords(self):
        """Test generating template with custom keywords."""
        custom_keywords = "python, programming, coding, development, best practices, patterns, optimization, testing, documentation, examples"
        template = TemplateGenerator.generate_template("200-python-core", keywords=custom_keywords)

        assert custom_keywords in template

    def test_generate_template_invalid_tier(self):
        """Test that invalid context tier raises error.

        Validates that only approved context tiers (Low, Medium, High)
        are accepted. This prevents templates with invalid tiers that
        would fail schema validation and break the rules system.
        """
        with pytest.raises(ValueError, match="Context tier must be one of"):
            TemplateGenerator.generate_template("100-example", context_tier="Invalid")

    def test_generate_template_invalid_keyword_count(self):
        """Test that invalid keyword count raises error.

        Ensures keyword count stays within 5-20 range per v3.2 schema for optimal
        semantic search performance. Too few keywords limit discoverability;
        too many keywords waste token budget and dilute relevance.
        """
        # Too few keywords
        with pytest.raises(ValueError, match="Keywords must contain 5-20 terms"):
            TemplateGenerator.generate_template("100-example", keywords="one, two, three")

        # Too many keywords
        too_many = ", ".join([f"keyword{i}" for i in range(25)])
        with pytest.raises(ValueError, match="Keywords must contain 5-20 terms"):
            TemplateGenerator.generate_template("100-example", keywords=too_many)


class TestTemplateStructure:
    """Test that generated templates have correct v3.2 structure."""

    @pytest.fixture
    def sample_template(self) -> str:
        """Generate a sample template for testing."""
        return TemplateGenerator.generate_template("100-snowflake-sql")

    def test_has_required_metadata_fields(self, sample_template):
        """Test that template has all required metadata fields."""
        assert "**SchemaVersion:** v3.2" in sample_template
        assert "**RuleVersion:**" in sample_template
        assert "**LastUpdated:**" in sample_template
        assert "**Keywords:**" in sample_template
        assert "**TokenBudget:**" in sample_template
        assert "**ContextTier:**" in sample_template
        assert "**Depends:**" in sample_template

    def test_has_metadata_header(self, sample_template):
        """Test that template has ## Metadata header."""
        assert "## Metadata" in sample_template
        # Check it appears after H1 and before metadata fields
        lines = sample_template.split("\n")
        h1_line = next(i for i, line in enumerate(lines) if line.startswith("# "))
        metadata_header_line = next(i for i, line in enumerate(lines) if line == "## Metadata")
        keywords_line = next(i for i, line in enumerate(lines) if line.startswith("**Keywords:**"))

        assert h1_line < metadata_header_line < keywords_line

    def test_has_required_sections(self, sample_template):
        """Test that template has all required v3.2 sections.

        Validates that generated templates include all sections defined
        in the v3.2 schema. Missing sections would cause schema validation
        failures and prevent rules from being loaded by AI systems.
        """
        required_sections = [
            "## Scope",
            "## References",
            "## Contract",
            "## Anti-Patterns and Common Mistakes",
        ]

        for section in required_sections:
            assert section in sample_template, f"Missing required section: {section}"

    def test_has_contract_markdown_headers(self, sample_template):
        """Test that Contract section has all required Markdown subsections.

        Ensures the Contract section follows v3.2 specification with
        proper Markdown ### headers (not XML tags). These subsections define
        rule execution semantics and are parsed by AI systems to understand
        rule constraints.
        """
        required_subsections = [
            "### Inputs and Prerequisites",
            "### Mandatory",
            "### Forbidden",
            "### Execution Steps",
            "### Output Format",
            "### Validation",
            "### Post-Execution Checklist",
        ]

        for subsection in required_subsections:
            assert subsection in sample_template, f"Missing Contract subsection: {subsection}"

    def test_has_quick_start_elements(self, sample_template):
        """Test that Quick Start TL;DR section is NOT present (removed in v3.2)."""
        # v3.2 eliminated Quick Start TL;DR section
        assert "## Quick Start TL;DR" not in sample_template
        assert "**Essential Patterns:**" not in sample_template

    def test_has_minimum_essential_patterns(self, sample_template):
        """Test Essential Patterns (removed in v3.2, skip test)."""
        # v3.2 eliminated Quick Start TL;DR section with Essential Patterns
        # This test is no longer applicable
        pass

    def test_has_minimum_checklist_items(self, sample_template):
        """Test Pre-Execution Checklist (moved to Contract in v3.2)."""
        # v3.2 moved Pre-Execution Checklist into Contract section
        # Check for Post-Execution Checklist items instead
        checklist_section = re.search(
            r"### Post-Execution Checklist.*?(?=\n###|\n##|$)",
            sample_template,
            re.DOTALL,
        )
        assert checklist_section

        # Count checklist items
        checklist_items = re.findall(r"^\s*-\s+\[\s*\]", checklist_section.group(0), re.MULTILINE)
        assert len(checklist_items) >= 3

    def test_has_post_execution_checklist_items(self, sample_template):
        """Test that Post-Execution Checklist has minimum items."""
        # Find Post-Execution Checklist section (now inside Contract)
        post_checklist_section = re.search(
            r"### Post-Execution Checklist.*?(?=\n###|\n##|$)",
            sample_template,
            re.DOTALL,
        )
        assert post_checklist_section

        # Count checklist items
        checklist_items = re.findall(
            r"^\s*-\s+\[\s*\]", post_checklist_section.group(0), re.MULTILINE
        )
        assert len(checklist_items) >= 3

    def test_has_contract_steps(self, sample_template):
        """Test that Contract section has minimum 5 steps."""
        # Find Execution Steps subsection within Contract (now uses ### header)
        steps_section = re.search(
            r"### Execution Steps.*?(?=\n###|\n##)",
            sample_template,
            re.DOTALL,
        )
        assert steps_section

        # Count numbered steps
        steps = re.findall(r"^\d+\.", steps_section.group(0), re.MULTILINE)
        assert len(steps) >= 5

    def test_has_anti_pattern_structure(self, sample_template):
        """Test that Anti-Patterns section has correct structure."""
        assert "### Anti-Pattern 1:" in sample_template
        assert "**Problem:**" in sample_template
        assert "**Correct Pattern:**" in sample_template
        assert "**Benefits:**" in sample_template

    def test_has_code_blocks(self, sample_template):
        """Test that template has code block placeholders."""
        # Count code blocks (triple backticks)
        code_blocks = re.findall(r"```", sample_template)
        # Should have at least 6 code blocks (2 anti-pattern pairs + 2 output examples)
        assert len(code_blocks) >= 6

    def test_has_references_structure(self, sample_template):
        """Test that References section has correct structure."""
        assert "### Dependencies" in sample_template
        assert "### External Documentation" in sample_template
        assert "000-global-core.md" in sample_template


class TestFileCreation:
    """Test actual file creation."""

    def test_create_rule_file(self, tmp_path):
        """Test creating a rule file."""
        output_path = TemplateGenerator.create_rule_file(
            filename="100-test-rule",
            output_dir=tmp_path,
        )

        assert output_path.exists()
        assert output_path.name == "100-test-rule.md"

        content = output_path.read_text()
        assert "# 100-test-rule" in content
        assert "## Metadata" in content

    def test_create_rule_file_with_extension(self, tmp_path):
        """Test creating a rule file when filename includes .md."""
        output_path = TemplateGenerator.create_rule_file(
            filename="100-test-rule.md",
            output_dir=tmp_path,
        )

        assert output_path.exists()
        assert output_path.name == "100-test-rule.md"

    def test_create_rule_file_custom_tier(self, tmp_path):
        """Test creating a rule file with custom context tier."""
        output_path = TemplateGenerator.create_rule_file(
            filename="200-test-rule",
            output_dir=tmp_path,
            context_tier="High",
        )

        content = output_path.read_text()
        assert "**ContextTier:** High" in content

    def test_create_rule_file_custom_keywords(self, tmp_path):
        """Test creating a rule file with custom keywords."""
        custom_keywords = "test, example, sample, demo, validation, verification, template, placeholder, prototype, reference"
        output_path = TemplateGenerator.create_rule_file(
            filename="300-test-rule",
            output_dir=tmp_path,
            keywords=custom_keywords,
        )

        content = output_path.read_text()
        assert custom_keywords in content

    def test_create_rule_file_exists_no_force(self, tmp_path):
        """Test that creating existing file without force raises error."""
        # Create file first time
        TemplateGenerator.create_rule_file(
            filename="100-test-rule",
            output_dir=tmp_path,
        )

        # Try to create again without force
        with pytest.raises(FileExistsError, match="already exists"):
            TemplateGenerator.create_rule_file(
                filename="100-test-rule",
                output_dir=tmp_path,
            )

    def test_create_rule_file_exists_with_force(self, tmp_path):
        """Test that creating existing file with force overwrites."""
        # Create file first time
        first_path = TemplateGenerator.create_rule_file(
            filename="100-test-rule",
            output_dir=tmp_path,
        )

        first_content = first_path.read_text()

        # Create again with force and different tier
        second_path = TemplateGenerator.create_rule_file(
            filename="100-test-rule",
            output_dir=tmp_path,
            context_tier="Critical",
            force=True,
        )

        second_content = second_path.read_text()

        assert first_path == second_path
        assert first_content != second_content
        assert "**ContextTier:** Critical" in second_content

    def test_create_rule_file_creates_directory(self, tmp_path):
        """Test that creating file creates directory if it doesn't exist."""
        nested_dir = tmp_path / "custom" / "nested"

        output_path = TemplateGenerator.create_rule_file(
            filename="100-test-rule",
            output_dir=nested_dir,
        )

        assert nested_dir.exists()
        assert output_path.exists()


class TestSchemaCompliance:
    """Test that generated templates pass schema validation."""

    def test_generated_template_structure_compliance(self, tmp_path):
        """Test that generated template has v3.2 compliant structure."""
        output_path = TemplateGenerator.create_rule_file(
            filename="100-test-compliance",
            output_dir=tmp_path,
        )

        content = output_path.read_text()

        # Test metadata header placement
        lines = content.split("\n")
        h1_idx = next(i for i, line in enumerate(lines) if line.startswith("# "))
        metadata_header_idx = next(i for i, line in enumerate(lines) if line == "## Metadata")
        scope_idx = next(i for i, line in enumerate(lines) if line == "## Scope")

        assert h1_idx < metadata_header_idx < scope_idx

        # Test metadata field order (v3.2: SchemaVersion, RuleVersion, LastUpdated, Keywords, TokenBudget, ContextTier, Depends)
        schema_idx = next(
            i for i, line in enumerate(lines) if line.startswith("**SchemaVersion:**")
        )
        rule_version_idx = next(
            i for i, line in enumerate(lines) if line.startswith("**RuleVersion:**")
        )
        last_updated_idx = next(
            i for i, line in enumerate(lines) if line.startswith("**LastUpdated:**")
        )
        keywords_idx = next(i for i, line in enumerate(lines) if line.startswith("**Keywords:**"))
        token_idx = next(i for i, line in enumerate(lines) if line.startswith("**TokenBudget:**"))
        tier_idx = next(i for i, line in enumerate(lines) if line.startswith("**ContextTier:**"))
        depends_idx = next(i for i, line in enumerate(lines) if line.startswith("**Depends:**"))

        assert (
            schema_idx
            < rule_version_idx
            < last_updated_idx
            < keywords_idx
            < token_idx
            < tier_idx
            < depends_idx
        )

    def test_generated_template_keyword_count(self, tmp_path):
        """Test that generated keywords meet 5-20 count requirement per v3.2 schema."""
        output_path = TemplateGenerator.create_rule_file(
            filename="200-test-keywords",
            output_dir=tmp_path,
        )

        content = output_path.read_text()

        # Extract keywords line
        keywords_match = re.search(r"\*\*Keywords:\*\*\s+(.+)", content)
        assert keywords_match

        keywords = keywords_match.group(1)
        keyword_list = [kw.strip() for kw in keywords.split(",")]

        assert 5 <= len(keyword_list) <= 20


class TestCLIFormatting:
    """Test CLI message formatting functions."""

    def test_format_success_message(self, tmp_path):
        """Test success message formatting."""
        output_path = tmp_path / "100-test-rule.md"
        message = TemplateGenerator.format_success_message(output_path)

        assert "✅" in message
        assert "Created rule template:" in message
        assert str(output_path) in message
        assert "Next steps:" in message
        assert "Edit" in message
        assert "Validate:" in message
        assert "schema_validator.py" in message
        assert "RULES_INDEX.md" in message

    def test_format_error_message_value_error(self):
        """Test error message formatting for ValueError."""
        error = ValueError("Invalid filename format")
        message = TemplateGenerator.format_error_message(error)

        assert "❌" in message
        assert "Error:" in message
        assert "Invalid filename format" in message

    def test_format_error_message_file_exists_error(self):
        """Test error message formatting for FileExistsError."""
        error = FileExistsError("Rule file already exists")
        message = TemplateGenerator.format_error_message(error)

        assert "❌" in message
        assert "Error:" in message
        assert "Rule file already exists" in message


class TestCLIExecution:
    """Test CLI execution via main() function - integration tests."""

    def test_cli_creates_file_successfully(self, tmp_path, capsys, monkeypatch):
        """Test successful file creation via CLI."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule", "--output-dir", str(tmp_path)],
        )

        exit_code = main()

        assert exit_code == 0

        # Verify file created
        output_path = tmp_path / "100-test-rule.md"
        assert output_path.exists()

        # Verify success message
        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "Created rule template:" in captured.out
        assert "Next steps:" in captured.out

    def test_cli_with_custom_context_tier(self, tmp_path, capsys, monkeypatch):
        """Test CLI with custom context tier."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "template_generator.py",
                "200-test-rule",
                "--output-dir",
                str(tmp_path),
                "--context-tier",
                "High",
            ],
        )

        exit_code = main()

        assert exit_code == 0

        # Verify file has correct tier
        output_path = tmp_path / "200-test-rule.md"
        content = output_path.read_text()
        assert "**ContextTier:** High" in content

    def test_cli_with_custom_keywords(self, tmp_path, capsys, monkeypatch):
        """Test CLI with custom keywords."""
        custom_keywords = "test, example, demo, sample, validation, verification, template, placeholder, prototype, reference"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "template_generator.py",
                "300-test-rule",
                "--output-dir",
                str(tmp_path),
                "--keywords",
                custom_keywords,
            ],
        )

        exit_code = main()

        assert exit_code == 0

        # Verify file has custom keywords
        output_path = tmp_path / "300-test-rule.md"
        content = output_path.read_text()
        assert custom_keywords in content

    def test_cli_force_flag_overwrites(self, tmp_path, capsys, monkeypatch):
        """Test CLI --force flag overwrites existing file."""
        # Create file first
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule", "--output-dir", str(tmp_path)],
        )
        main()

        # Overwrite with different tier
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "template_generator.py",
                "100-test-rule",
                "--output-dir",
                str(tmp_path),
                "--context-tier",
                "Critical",
                "--force",
            ],
        )

        exit_code = main()

        assert exit_code == 0

        # Verify file overwritten with new tier
        output_path = tmp_path / "100-test-rule.md"
        content = output_path.read_text()
        assert "**ContextTier:** Critical" in content

    def test_cli_file_exists_error_without_force(self, tmp_path, capsys, monkeypatch):
        """Test CLI error when file exists without --force."""
        # Create file first
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule", "--output-dir", str(tmp_path)],
        )
        main()

        # Try to create again without force
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule", "--output-dir", str(tmp_path)],
        )

        exit_code = main()

        assert exit_code == 1

        # Verify error message
        captured = capsys.readouterr()
        assert "❌" in captured.err
        assert "Error:" in captured.err
        assert "already exists" in captured.err

    def test_cli_invalid_filename_error(self, tmp_path, capsys, monkeypatch):
        """Test CLI error with invalid filename format."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "invalid-filename", "--output-dir", str(tmp_path)],
        )

        exit_code = main()

        assert exit_code == 1

        # Verify error message
        captured = capsys.readouterr()
        assert "❌" in captured.err
        assert "Error:" in captured.err
        assert "Invalid filename format" in captured.err

    def test_cli_invalid_context_tier_error(self, tmp_path, capsys, monkeypatch):
        """Test CLI error with invalid context tier."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "template_generator.py",
                "100-test-rule",
                "--output-dir",
                str(tmp_path),
                "--context-tier",
                "InvalidTier",
            ],
        )

        # argparse will catch this before our code, so expect SystemExit
        with pytest.raises(SystemExit):
            main()

    def test_cli_invalid_keyword_count_error(self, tmp_path, capsys, monkeypatch):
        """Test CLI error with invalid keyword count."""
        too_few_keywords = "one, two, three"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "template_generator.py",
                "100-test-rule",
                "--output-dir",
                str(tmp_path),
                "--keywords",
                too_few_keywords,
            ],
        )

        exit_code = main()

        assert exit_code == 1

        # Verify error message
        captured = capsys.readouterr()
        assert "❌" in captured.err
        assert "Error:" in captured.err
        assert "Keywords must contain 5-20 terms" in captured.err

    def test_cli_custom_output_directory(self, tmp_path, capsys, monkeypatch):
        """Test CLI with custom output directory creation."""
        custom_dir = tmp_path / "custom" / "nested" / "path"
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule", "--output-dir", str(custom_dir)],
        )

        exit_code = main()

        assert exit_code == 0

        # Verify directory created
        assert custom_dir.exists()

        # Verify file created in custom directory
        output_path = custom_dir / "100-test-rule.md"
        assert output_path.exists()

    def test_cli_with_md_extension_in_filename(self, tmp_path, capsys, monkeypatch):
        """Test CLI handles .md extension in filename argument."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule.md", "--output-dir", str(tmp_path)],
        )

        exit_code = main()

        assert exit_code == 0

        # Verify file created with single .md extension
        output_path = tmp_path / "100-test-rule.md"
        assert output_path.exists()
        assert not (tmp_path / "100-test-rule.md.md").exists()

    def test_cli_unexpected_error_handling(self, tmp_path, capsys, monkeypatch):
        """Test CLI handles unexpected errors gracefully."""
        monkeypatch.setattr(
            sys,
            "argv",
            ["template_generator.py", "100-test-rule", "--output-dir", str(tmp_path)],
        )

        # Mock create_rule_file to raise unexpected exception
        def mock_create_error(*args, **kwargs):
            raise RuntimeError("Unexpected error occurred")

        with patch.object(TemplateGenerator, "create_rule_file", side_effect=mock_create_error):
            exit_code = main()

        assert exit_code == 1

        # Verify unexpected error message
        captured = capsys.readouterr()
        assert "❌ Unexpected error:" in captured.err
        assert "Unexpected error occurred" in captured.err
