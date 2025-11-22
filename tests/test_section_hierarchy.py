#!/usr/bin/env python3
"""
Tests for section hierarchy building and template filtering.

Comprehensive test coverage for SectionHierarchy class including:
- Section tree building
- Parent-child relationships
- Template section detection
- Actual rule section filtering
"""

from __future__ import annotations

from scripts.markdown_parser import MarkdownParser, SectionHierarchy


class TestSectionTreeBuilding:
    """Test building section hierarchy from markdown."""

    def test_build_simple_hierarchy(self):
        content = """# Title
## Section 1
### Subsection 1.1
## Section 2"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        assert len(hierarchy.sections) == 4
        h2_sections = hierarchy.get_h2_sections()
        assert len(h2_sections) == 2
        assert h2_sections[0].name == "Section 1"
        assert h2_sections[1].name == "Section 2"

    def test_parent_child_relationships(self):
        content = """## Parent
### Child 1
### Child 2
## Another Parent"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        parent = hierarchy.sections[0]
        assert parent.name == "Parent"
        assert len(parent.children) == 2
        assert parent.children[0].name == "Child 1"
        assert parent.children[1].name == "Child 2"
        assert parent.children[0].parent == parent

    def test_nested_hierarchy(self):
        content = """# H1
## H2
### H3
#### H4
## H2 Again"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        h1 = hierarchy.sections[0]
        h2 = hierarchy.sections[1]
        h3 = hierarchy.sections[2]
        h4 = hierarchy.sections[3]

        assert h1.level == 1
        assert h2.level == 2
        assert h2.parent == h1
        assert h3.parent == h2
        assert h4.parent == h3

    def test_ancestor_chain(self):
        content = """# Root
## Level 2
### Level 3
#### Level 4"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        level4 = hierarchy.sections[3]
        ancestors = level4.get_ancestors()

        assert len(ancestors) == 3
        assert ancestors[0].name == "Level 3"
        assert ancestors[1].name == "Level 2"
        assert ancestors[2].name == "Root"


class TestTemplateSectionDetection:
    """Test template section identification in hierarchy."""

    def test_direct_template_keyword_marked(self):
        content = """## Template Example
### Subsection
## Real Section"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        template_section = hierarchy.sections[0]
        real_section = hierarchy.sections[2]

        assert template_section.is_template
        assert not real_section.is_template

    def test_template_children_detected(self):
        content = """## Required Rule Structure
### Purpose
### Contract
## Actual Purpose"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        parent = hierarchy.sections[0]
        child1 = hierarchy.sections[1]
        _child2 = hierarchy.sections[2]  # Not used but keep for documentation
        actual = hierarchy.sections[3]

        assert parent.is_template
        assert not child1.is_template  # Not directly template
        assert child1.is_ancestor_template()  # But ancestor is
        assert not actual.is_template

    def test_example_keyword_detection(self):
        content = """## Example Section
### Example Details
## Normal Section"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        example = hierarchy.sections[0]
        normal = hierarchy.sections[2]

        assert example.is_template
        assert not normal.is_template

    def test_boilerplate_keyword_detection(self):
        content = """## Boilerplate Structure
### Fields
## Actual Content"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        boilerplate = hierarchy.sections[0]
        actual = hierarchy.sections[2]

        assert boilerplate.is_template
        assert not actual.is_template


class TestActualSectionFiltering:
    """Test filtering to get actual rule sections."""

    def test_get_actual_rule_sections_excludes_templates(self):
        content = """## Template Section
### Template Child
## Real Section
### Real Child"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_sections = hierarchy.get_actual_rule_sections()

        assert len(actual_sections) == 2
        names = [s.name for s in actual_sections]
        assert "Real Section" in names
        assert "Real Child" in names
        assert "Template Section" not in names
        assert "Template Child" not in names

    def test_get_actual_h2_sections(self):
        content = """## Template Example
## Purpose
### Details
## Contract
## Another Template"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_h2 = hierarchy.get_actual_h2_sections()

        assert len(actual_h2) == 2
        names = [s.name for s in actual_h2]
        assert "Purpose" in names
        assert "Contract" in names
        assert "Template Example" not in names
        assert "Another Template" not in names

    def test_nested_template_exclusion(self):
        content = """## Template Section
### Level 3 Template Child
#### Level 4 Template Grandchild
## Real Section
### Real Child"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_sections = hierarchy.get_actual_rule_sections()

        # Only real section and its child should be included
        assert len(actual_sections) == 2
        assert all(not s.is_ancestor_template() for s in actual_sections)


class TestComplexHierarchies:
    """Test complex real-world scenarios."""

    def test_rule_file_with_template_sections(self):
        content = """**Keywords:** test, example

# Rule Title

## Purpose
Purpose content

## Required Rule Structure
This section shows the template:

### Purpose
Template purpose

### Contract
Template contract

## Contract
Actual contract content

## Validation
Validation content"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_h2 = hierarchy.get_actual_h2_sections()
        names = [s.name for s in actual_h2]

        # Should have: Purpose, Contract, Validation (H2 sections only)
        # Should NOT have: Required Rule Structure (template)
        # Note: "Rule Title" is H1, not H2, so not included here
        assert "Purpose" in names
        assert "Contract" in names
        assert "Validation" in names
        assert "Required Rule Structure" not in names
        assert len(names) == 3  # Exactly 3 H2 sections

        # Check template children are excluded from actual
        all_actual = hierarchy.get_actual_rule_sections()
        # Template children should not appear in actual sections
        template_children = [s for s in hierarchy.sections if s.parent and s.parent.is_template]
        for child in template_children:
            # The specific child object should not be in all_actual
            # (even if there's another section with the same name)
            assert child not in all_actual

    def test_mixed_levels_with_templates(self):
        content = """# H1 Title
## Purpose
## Example Structure
### Example H3
#### Example H4
## Contract
### Contract Details
## Validation"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_sections = hierarchy.get_actual_rule_sections()

        # Count actual sections (not under Example Structure)
        actual_names = [s.name for s in actual_sections]
        assert "Purpose" in actual_names
        assert "Contract" in actual_names
        assert "Contract Details" in actual_names
        assert "Validation" in actual_names
        assert "Example Structure" not in actual_names
        assert "Example H3" not in actual_names
        assert "Example H4" not in actual_names

    def test_governance_file_structure(self):
        """Test 002-rule-governance.md style structure."""
        content = """# Rule Governance

## Purpose
Governance purpose

## Required Rule Structure
Template showing structure:

### Purpose
Template purpose

### Contract
Template contract

### Validation
Template validation

## Validation
Actual validation

## References"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_h2 = hierarchy.get_actual_h2_sections()
        names = [s.name for s in actual_h2]

        # Should include actual sections
        assert "Purpose" in names
        assert "Validation" in names
        assert "References" in names

        # Should exclude template section
        assert "Required Rule Structure" not in names

        # Template children should be excluded
        all_actual = hierarchy.get_actual_rule_sections()

        # There are two "Purpose" sections - one template, one real
        # But get_actual_rule_sections should only return non-template ones
        purpose_sections = [s for s in hierarchy.sections if s.name == "Purpose"]
        assert len(purpose_sections) == 2

        actual_purpose_sections = [s for s in all_actual if s.name == "Purpose" and s.level == 2]
        # Only the actual Purpose (not under Required Rule Structure) should be included
        assert len(actual_purpose_sections) == 1
        assert not actual_purpose_sections[0].is_ancestor_template()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_content(self):
        parser = MarkdownParser("")
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        assert len(hierarchy.sections) == 0
        assert len(hierarchy.get_actual_rule_sections()) == 0

    def test_only_template_sections(self):
        content = """## Template Only
### Template Child"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual = hierarchy.get_actual_rule_sections()
        assert len(actual) == 0

    def test_no_template_sections(self):
        content = """## Purpose
## Contract
## Validation"""
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        actual_h2 = hierarchy.get_actual_h2_sections()
        assert len(actual_h2) == 3

    def test_h1_only(self):
        content = "# Title Only"
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        assert len(hierarchy.sections) == 1
        assert hierarchy.sections[0].level == 1
