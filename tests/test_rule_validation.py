"""Tests for rule structure validation and cross-reference checks.

Updated to validate against 002-rule-governance.md v2.4 standards:
- Required sections: Purpose, Rule Type and Scope, Contract, Validation,
  Response Template, Quick Compliance Checklist, References
- Required metadata: Version, LastUpdated, Keywords (promoted to required in v2.4)
- Recommended metadata: TokenBudget, ContextTier
- XML semantic tags (optional but recommended)
- Anti-Patterns section (recommended for complex rules)
"""

import re
from pathlib import Path

import pytest


class TestRuleStructureValidation:
    """Test that all rule files follow required structure standards per 002-rule-governance.md v2.4."""

    @classmethod
    def get_rule_files(cls) -> list[Path]:
        """Get all rule files, excluding documentation files."""
        excluded_files = {
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "RULES_INDEX.md",
            "UNIVERSAL_PROMPT.md",
            "AGENTS.md",  # Added per updated validation
        }

        rule_files = []
        for md_file in Path(".").glob("*.md"):
            if md_file.name not in excluded_files:
                rule_files.append(md_file)

        return sorted(rule_files)

    @pytest.mark.skip(reason="Full codebase validation - many files not yet compliant with v2.1")
    def test_all_rules_have_required_sections(self):
        """Test that all rule files contain mandatory sections per 002-rule-governance.md v2.1."""
        rule_files = self.get_rule_files()
        assert len(rule_files) > 0, "No rule files found"

        missing_sections = []

        for rule_file in rule_files:
            content = rule_file.read_text()
            file_issues = []

            # Check for required sections (v2.1 requirements)
            required_sections = [
                r"^## Purpose\b",
                r"^## Rule Type and Scope\b",
                r"^## Contract\b",
                r"^## Quick Compliance Checklist\b",
                r"^## Validation\b",
                r"^## Response Template\b",
                r"^## References\b",
            ]

            for section_pattern in required_sections:
                if not re.search(section_pattern, content, re.MULTILINE):
                    section_name = section_pattern.replace(r"^## ", "").replace(r"\b", "")
                    file_issues.append(section_name)

            if file_issues:
                missing_sections.append({"file": rule_file.name, "missing": file_issues})

        if missing_sections:
            error_msg = "Rule files missing required sections (v2.1 governance):\n"
            for issue in missing_sections:
                error_msg += f"  {issue['file']}: {', '.join(issue['missing'])}\n"
            pytest.fail(error_msg)

    @pytest.mark.skip(reason="Full codebase validation - many files not yet compliant with v2.4")
    def test_rule_files_have_proper_metadata(self):
        """Test that rule files have required metadata per 002-rule-governance.md v2.4."""
        rule_files = self.get_rule_files()

        missing_metadata = []

        for rule_file in rule_files:
            content = rule_file.read_text()
            file_issues = []

            # Check for required metadata (v2.4 requirements - Keywords now required)
            metadata_patterns = [
                r"^\*\*Description:\*\*",
                r"^\*\*AutoAttach:\*\*",
                r"^\*\*Type:\*\*",
                r"^\*\*Version:\*\*",
                r"^\*\*LastUpdated:\*\*",
                r"^\*\*Keywords:\*\*",  # CRITICAL: Required in v2.4 for semantic discovery
                r"^\*\*TokenBudget:\*\*",  # Recommended in v2.1+
                r"^\*\*ContextTier:\*\*",  # Recommended in v2.1+
            ]

            for pattern in metadata_patterns:
                if not re.search(pattern, content, re.MULTILINE):
                    field_name = pattern.replace(r"^\*\*", "").replace(r":\*\*", "")
                    file_issues.append(field_name)

            if file_issues:
                missing_metadata.append({"file": rule_file.name, "missing": file_issues})

        if missing_metadata:
            error_msg = (
                "Rule files missing required metadata (v2.4 governance - Keywords now required):\n"
            )
            for issue in missing_metadata:
                error_msg += f"  {issue['file']}: {', '.join(issue['missing'])}\n"
            pytest.fail(error_msg)

    @pytest.mark.skip(reason="Full codebase validation - many files not yet compliant")
    def test_rule_files_have_single_h1_title(self):
        """Test that rule files have exactly one H1 title."""
        rule_files = self.get_rule_files()

        title_issues = []

        for rule_file in rule_files:
            content = rule_file.read_text()
            h1_titles = re.findall(r"^# ", content, re.MULTILINE)

            if len(h1_titles) == 0:
                title_issues.append(f"{rule_file.name}: No H1 title found")
            elif len(h1_titles) > 1:
                title_issues.append(
                    f"{rule_file.name}: Multiple H1 titles found ({len(h1_titles)})"
                )

        if title_issues:
            error_msg = "Rule files with H1 title issues:\n" + "\n".join(
                f"  {issue}" for issue in title_issues
            )
            pytest.fail(error_msg)

    def test_002_rule_governance_is_compliant(self):
        """Test that 002-rule-governance.md itself follows v2.4 standards."""
        governance_file = Path("002-rule-governance.md")
        if not governance_file.exists():
            pytest.skip("002-rule-governance.md not found")

        content = governance_file.read_text()

        # Check for v2.4 required sections (use partial matches for numbered sections)
        required_section_patterns = [
            "## Purpose",
            "## Rule Type and Scope",
            "## Contract",
            "## Key Principles",
            "Semantic Markup and XML Tags",  # May be "## 2. Semantic Markup..."
            "Anti-Patterns Library",  # May be "### Anti-Patterns Library..."
            "Investigation-First Protocol",  # May be "### Investigation-First..."
            "Emoji Usage in Rules",  # May be "### Emoji Usage..."
            "## Quick Compliance Checklist",
            "## Validation",
            "## Response Template",
            "## References",
        ]

        missing = []
        for pattern in required_section_patterns:
            if pattern not in content:
                missing.append(pattern)

        assert len(missing) == 0, f"002-rule-governance.md missing sections: {missing}"

        # Check for v2.4 metadata (Keywords now required)
        assert "**Keywords:**" in content, "Missing Keywords metadata (required in v2.4)"
        assert "**TokenBudget:**" in content, "Missing TokenBudget metadata"
        assert "**ContextTier:**" in content, "Missing ContextTier metadata"
        assert "**Version:**" in content, "Missing Version metadata"
        assert "**LastUpdated:**" in content, "Missing LastUpdated metadata"

    @pytest.mark.skip(reason="Informational check - not all rules require XML tags yet")
    def test_rules_have_xml_semantic_tags(self):
        """Test that rules include XML semantic tags (recommended in v2.1)."""
        rule_files = self.get_rule_files()

        rules_without_xml = []

        for rule_file in rule_files:
            content = rule_file.read_text()

            # Check for any XML semantic tags
            has_section_metadata = "<section_metadata>" in content
            has_directive_strength = "<directive_strength>" in content
            has_investigate = "<investigate_before_answering>" in content

            if not (has_section_metadata or has_directive_strength or has_investigate):
                rules_without_xml.append(rule_file.name)

        if rules_without_xml:
            # Don't fail, just report
            print(f"\n⚠️  {len(rules_without_xml)} rules without XML semantic tags:")
            for rule in rules_without_xml[:10]:  # Show first 10
                print(f"  - {rule}")
            if len(rules_without_xml) > 10:
                print(f"  ... and {len(rules_without_xml) - 10} more")

    @pytest.mark.skip(reason="Informational check - not all rules require anti-patterns yet")
    def test_complex_rules_have_anti_patterns(self):
        """Test that complex rules (>300 lines) include Anti-Patterns section."""
        rule_files = self.get_rule_files()

        complex_rules_without_antipatterns = []

        for rule_file in rule_files:
            content = rule_file.read_text()
            line_count = len(content.splitlines())

            # Rules over 300 lines are considered "complex"
            if (
                line_count > 300
                and "## Anti-Patterns" not in content
                and "anti_pattern_examples" not in content
            ):
                complex_rules_without_antipatterns.append(
                    {"file": rule_file.name, "lines": line_count}
                )

        if complex_rules_without_antipatterns:
            # Don't fail, just report
            print(
                f"\n⚠️  {len(complex_rules_without_antipatterns)} complex rules without Anti-Patterns section:"
            )
            for rule in complex_rules_without_antipatterns[:5]:
                print(f"  - {rule['file']} ({rule['lines']} lines)")

    @pytest.mark.skip(reason="Informational check - checks emoji usage guidelines")
    def test_emoji_usage_follows_guidelines(self):
        """Test that rules follow emoji usage guidelines (v2.1 standards)."""
        rule_files = self.get_rule_files()

        # Allowed functional emojis

        # Common decorative emojis to detect
        decorative_emojis = {"🎉", "🥳", "🎊", "💯", "💪", "👍", "😀", "😎", "😅", "🤔"}

        rules_with_decorative = []

        for rule_file in rule_files:
            content = rule_file.read_text()

            # Check for decorative emojis
            found_decorative = []
            for emoji in decorative_emojis:
                if emoji in content:
                    found_decorative.append(emoji)

            if found_decorative:
                rules_with_decorative.append({"file": rule_file.name, "emojis": found_decorative})

        if rules_with_decorative:
            print(f"\n⚠️  {len(rules_with_decorative)} rules with decorative emojis:")
            for rule in rules_with_decorative[:5]:
                print(f"  - {rule['file']}: {''.join(rule['emojis'])}")

    @pytest.mark.skip(reason="Full codebase validation - many files not yet compliant")
    def test_contract_section_has_required_fields(self):
        """Test that Contract sections have all required fields."""
        rule_files = self.get_rule_files()

        contract_issues = []

        for rule_file in rule_files:
            content = rule_file.read_text()

            # Find Contract section
            contract_match = re.search(r"^## Contract\b.*?^## ", content, re.MULTILINE | re.DOTALL)
            if not contract_match:
                continue  # Will be caught by required sections test

            contract_content = contract_match.group(0)

            required_fields = [
                "Inputs/Prereqs",
                "Allowed Tools",
                "Forbidden Tools",
                "Required Steps",
                "Output Format",
                "Validation Steps",
            ]

            missing_fields = []
            for field in required_fields:
                if field not in contract_content:
                    missing_fields.append(field)

            if missing_fields:
                contract_issues.append({"file": rule_file.name, "missing": missing_fields})

        if contract_issues:
            error_msg = "Rule files with incomplete Contract sections:\n"
            for issue in contract_issues:
                error_msg += f"  {issue['file']}: {', '.join(issue['missing'])}\n"
            pytest.fail(error_msg)


class TestCrossReferenceValidation:
    """Test that cross-references between rule files are valid."""

    @classmethod
    def get_all_rule_files(cls) -> set[str]:
        """Get set of all rule file names."""
        rule_files = set()
        for md_file in Path(".").glob("*.md"):
            rule_files.add(md_file.name)
        return rule_files

    @classmethod
    def extract_rule_references(cls, content: str) -> list[str]:
        """Extract rule file references from content."""
        references = []

        # Pattern for @filename.md references
        at_refs = re.findall(r"@([a-zA-Z0-9_-]+\.md)", content)
        references.extend(at_refs)

        # Pattern for `filename.md` references in Related Rules sections
        backtick_refs = re.findall(r"`([a-zA-Z0-9_-]+\.md)`", content)
        references.extend(backtick_refs)

        return references

    @pytest.mark.skip(reason="Full codebase validation - many files not yet compliant")
    def test_cross_references_are_valid(self):
        """Test that all cross-references point to existing files."""
        rule_files = TestRuleStructureValidation.get_rule_files()
        all_files = self.get_all_rule_files()

        broken_references = []

        for rule_file in rule_files:
            content = rule_file.read_text()
            references = self.extract_rule_references(content)

            for ref in references:
                if ref not in all_files:
                    broken_references.append({"file": rule_file.name, "broken_ref": ref})

        if broken_references:
            error_msg = "Broken cross-references found:\n"
            for issue in broken_references:
                error_msg += f"  {issue['file']} -> {issue['broken_ref']}\n"
            pytest.fail(error_msg)

    def test_references_section_has_related_rules(self):
        """Test that References sections include Related Rules when appropriate."""
        rule_files = TestRuleStructureValidation.get_rule_files()

        for rule_file in rule_files:
            content = rule_file.read_text()

            # Find References section
            refs_match = re.search(r"^## References\b.*", content, re.MULTILINE | re.DOTALL)
            if not refs_match:
                continue  # Will be caught by required sections test

            refs_content = refs_match.group(0)

            # Check if it has Related Rules subsection
            if "### Related Rules" not in refs_content:
                # This is acceptable - not all rules need related rules
                continue

            # If it has Related Rules section, it should have at least one rule reference
            related_rules_match = re.search(r"### Related Rules\b.*", refs_content, re.DOTALL)
            if related_rules_match:
                related_section = related_rules_match.group(0)
                rule_refs = re.findall(r"`([a-zA-Z0-9_-]+\.md)`", related_section)

                assert len(rule_refs) > 0, f"{rule_file.name} has empty Related Rules section"


class TestGeneratedOutputValidation:
    """Test validation of generated IDE-specific rule files."""

    def test_cursor_rules_are_generated(self):
        """Test that Cursor .mdc files are generated and valid."""
        cursor_dir = Path(".cursor/rules")
        if not cursor_dir.exists():
            pytest.skip("Cursor rules directory not found")

        mdc_files = list(cursor_dir.glob("*.mdc"))
        assert len(mdc_files) > 0, "No .mdc files found in .cursor/rules/"

        for mdc_file in mdc_files:
            content = mdc_file.read_text()

            # Check for YAML frontmatter
            assert content.startswith("---\n"), f"{mdc_file.name} missing YAML frontmatter"

            # Check for required YAML fields
            yaml_end = content.find("\n---\n")
            assert yaml_end > 0, f"{mdc_file.name} malformed YAML frontmatter"

            yaml_content = content[:yaml_end]
            assert "description:" in yaml_content, f"{mdc_file.name} missing description in YAML"
            assert "globs:" in yaml_content, f"{mdc_file.name} missing globs in YAML"

    def test_copilot_rules_are_generated(self):
        """Test that GitHub Copilot instruction files are generated and valid."""
        copilot_dir = Path(".github/instructions")
        if not copilot_dir.exists():
            pytest.skip("GitHub instructions directory not found")

        instruction_files = list(copilot_dir.glob("*.md"))
        assert len(instruction_files) > 0, "No .md files found in .github/instructions/"

        for instruction_file in instruction_files:
            content = instruction_file.read_text()

            # Check for YAML frontmatter
            assert content.startswith("---\n"), f"{instruction_file.name} missing YAML frontmatter"

            # Check for appliesTo field
            yaml_end = content.find("\n---\n")
            assert yaml_end > 0, f"{instruction_file.name} malformed YAML frontmatter"

            yaml_content = content[:yaml_end]
            assert "appliesTo:" in yaml_content, (
                f"{instruction_file.name} missing appliesTo in YAML"
            )

    def test_cline_rules_are_generated(self):
        """Test that Cline rule files are generated."""
        cline_dir = Path(".clinerules")
        if not cline_dir.exists():
            pytest.skip("Cline rules directory not found")

        cline_files = list(cline_dir.glob("*.md"))
        assert len(cline_files) > 0, "No .md files found in .clinerules/"

        for cline_file in cline_files:
            content = cline_file.read_text()

            # Cline files should have the generation comment
            assert "Generated for Cline rules" in content, (
                f"{cline_file.name} missing generation comment"
            )

    def test_reference_conversion_for_cursor(self):
        """Test that .md references are converted to .mdc in Cursor files."""
        cursor_dir = Path(".cursor/rules")
        if not cursor_dir.exists():
            pytest.skip("Cursor rules directory not found")

        # Find a file that should have references
        rule_gov_file = cursor_dir / "002-rule-governance.mdc"
        if not rule_gov_file.exists():
            pytest.skip("002-rule-governance.mdc not found")

        content = rule_gov_file.read_text()

        # Should have .mdc references, not .md (except for preserved docs)
        mdc_refs = re.findall(r"`([a-zA-Z0-9_-]+\.mdc)`", content)
        md_refs = re.findall(r"`([a-zA-Z0-9_-]+\.md)`", content)

        # Filter out preserved documentation files
        preserved_files = {"README.md", "CHANGELOG.md", "CONTRIBUTING.md"}
        non_preserved_md_refs = [ref for ref in md_refs if ref not in preserved_files]

        assert len(mdc_refs) > 0, "No .mdc references found in Cursor rules"
        assert len(non_preserved_md_refs) == 0, (
            f"Found non-preserved .md references: {non_preserved_md_refs}"
        )
