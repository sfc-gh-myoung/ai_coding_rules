#!/usr/bin/env python3
"""
Tests for markdown-aware parser.

Comprehensive test coverage for MarkdownParser class including:
- Basic header extraction
- Code block exclusion
- HTML comment exclusion
- Edge cases (unclosed blocks, nested structures, etc.)
"""

from __future__ import annotations

from scripts.markdown_parser import MarkdownParser


class TestBasicHeaderExtraction:
    """Test basic header extraction without exclusions."""

    def test_extract_single_h2_header(self):
        content = """# Title
## Real Header
Some content"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2
        assert headers[0] == (1, "Title", 1)
        assert headers[1] == (2, "Real Header", 2)

    def test_extract_multiple_header_levels(self):
        content = """# H1 Header
## H2 Header
### H3 Header
#### H4 Header"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 4
        assert headers[0][2] == 1
        assert headers[1][2] == 2
        assert headers[2][2] == 3
        assert headers[3][2] == 4

    def test_header_text_extraction(self):
        content = "## Purpose\n## Contract\n## Validation"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 3
        assert headers[0][1] == "Purpose"
        assert headers[1][1] == "Contract"
        assert headers[2][1] == "Validation"


class TestCodeBlockExclusion:
    """Test that headers in code blocks are excluded."""

    def test_header_in_code_block_excluded(self):
        content = """## Real Header
```markdown
## Fake Header
```"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert headers[0][1] == "Real Header"

    def test_header_in_python_code_block(self):
        content = """## Real Header
```python
# Not a header
## Also not a header
```
## Another Real Header"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2
        assert headers[0][1] == "Real Header"
        assert headers[1][1] == "Another Real Header"

    def test_multiple_code_blocks(self):
        content = """## Header 1
```
## Fake 1
```
## Header 2
```python
## Fake 2
```
## Header 3"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 3
        assert [h[1] for h in headers] == ["Header 1", "Header 2", "Header 3"]

    def test_unclosed_code_block(self):
        content = """## Header 1
```
## Fake Header (unclosed)
## Also Fake"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert headers[0][1] == "Header 1"

    def test_code_block_with_language_specifier(self):
        content = """## Real
```sql
## Fake SQL Header
```
## Real 2"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2
        regions = parser.get_code_block_regions()
        assert len(regions) == 1
        assert regions[0].language == "sql"


class TestHtmlCommentExclusion:
    """Test that headers in HTML comments are excluded."""

    def test_header_in_html_comment_excluded(self):
        content = """## Real Header
<!--
## Fake Header
-->"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert headers[0][1] == "Real Header"

    def test_multiline_html_comment(self):
        content = """## Header 1
<!--
This is a comment
## Fake Header 1
More comment text
## Fake Header 2
-->
## Header 2"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2
        assert headers[0][1] == "Header 1"
        assert headers[1][1] == "Header 2"

    def test_inline_html_comment(self):
        content = """## Real Header
<!-- ## Fake Header -->
## Another Real Header"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2

    def test_unclosed_html_comment(self):
        content = """## Header 1
<!--
## Fake Header (unclosed)
## Also Fake"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert headers[0][1] == "Header 1"


class TestCodeBlockDetection:
    """Test is_in_code_block method."""

    def test_line_in_code_block_returns_true(self):
        content = """Line 1
```
Line 3 (in block)
Line 4 (in block)
```
Line 6"""
        parser = MarkdownParser(content)

        assert not parser.is_in_code_block(1)
        assert parser.is_in_code_block(2)
        assert parser.is_in_code_block(3)
        assert parser.is_in_code_block(4)
        assert parser.is_in_code_block(5)
        assert not parser.is_in_code_block(6)

    def test_multiple_code_blocks_detection(self):
        content = """Line 1
```
Block 1
```
Line 5
```
Block 2
```
Line 9"""
        parser = MarkdownParser(content)

        assert not parser.is_in_code_block(1)
        assert parser.is_in_code_block(2)
        assert parser.is_in_code_block(3)
        assert not parser.is_in_code_block(5)
        assert parser.is_in_code_block(6)
        assert parser.is_in_code_block(7)
        assert not parser.is_in_code_block(9)


class TestHtmlCommentDetection:
    """Test is_in_html_comment method."""

    def test_line_in_html_comment_returns_true(self):
        content = """Line 1
<!--
Line 3 (in comment)
-->
Line 5"""
        parser = MarkdownParser(content)

        assert not parser.is_in_html_comment(1)
        assert parser.is_in_html_comment(2)
        assert parser.is_in_html_comment(3)
        assert parser.is_in_html_comment(4)
        assert not parser.is_in_html_comment(5)

    def test_multiple_html_comments(self):
        content = """Line 1
<!-- Comment 1 -->
Line 3
<!-- Comment 2 -->
Line 5"""
        parser = MarkdownParser(content)

        assert not parser.is_in_html_comment(1)
        assert parser.is_in_html_comment(2)
        assert not parser.is_in_html_comment(3)
        assert parser.is_in_html_comment(4)
        assert not parser.is_in_html_comment(5)


class TestContextExtraction:
    """Test extract_context method."""

    def test_extract_context_middle_of_file(self):
        content = """Line 1
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7"""
        parser = MarkdownParser(content)
        context = parser.extract_context(4, context_lines=1)

        assert len(context) == 3
        assert context[0] == (3, "Line 3")
        assert context[1] == (4, "Line 4")
        assert context[2] == (5, "Line 5")

    def test_extract_context_at_file_start(self):
        content = """Line 1
Line 2
Line 3"""
        parser = MarkdownParser(content)
        context = parser.extract_context(1, context_lines=3)

        assert context[0][0] == 1
        assert len(context) <= 4

    def test_extract_context_at_file_end(self):
        content = """Line 1
Line 2
Line 3"""
        parser = MarkdownParser(content)
        context = parser.extract_context(3, context_lines=3)

        assert context[-1][0] == 3


class TestTemplateSectionDetection:
    """Test is_template_section method."""

    def test_direct_template_keyword_in_heading(self):
        content = "## Template Example\n## Real Section"
        parser = MarkdownParser(content)

        headers = parser.get_actual_headers()
        assert len(headers) == 2
        assert parser.is_template_section(headers[0][0], headers[0][1], headers[0][2])
        assert not parser.is_template_section(headers[1][0], headers[1][1], headers[1][2])

    def test_parent_section_with_template_keyword(self):
        content = """## Required Rule Structure
Some text
### Purpose
More text
### Contract"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        parent_line, parent_text, parent_level = headers[0]
        child_line, child_text, child_level = headers[1]

        assert parser.is_template_section(parent_line, parent_text, parent_level)
        assert parser.is_template_section(child_line, child_text, child_level)

    def test_example_keyword_detection(self):
        content = "## Example Section\n## Normal Section"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert parser.is_template_section(headers[0][0], headers[0][1], headers[0][2])
        assert not parser.is_template_section(headers[1][0], headers[1][1], headers[1][2])

    def test_boilerplate_keyword_detection(self):
        content = "## Boilerplate Structure\n## Actual Content"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert parser.is_template_section(headers[0][0], headers[0][1], headers[0][2])
        assert not parser.is_template_section(headers[1][0], headers[1][1], headers[1][2])


class TestComplexScenarios:
    """Test complex mixed scenarios."""

    def test_code_block_inside_html_comment(self):
        content = """## Real Header
<!--
```
## Fake in code in comment
```
-->
## Another Real Header"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2
        assert headers[0][1] == "Real Header"
        assert headers[1][1] == "Another Real Header"

    def test_html_comment_inside_code_block(self):
        content = """## Real Header
```
<!--
## Fake in comment in code
-->
```
## Another Real Header"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 2

    def test_real_world_rule_file_structure(self):
        content = """**Keywords:** test, example
**TokenBudget:** ~500

# Rule Title

## Purpose
Purpose text

## Contract
Contract text

## Response Template
```markdown
## Example Output
This is template code
```

## Validation
<!--
## Old Validation Approach (deprecated)
Don't use this
-->

## References
References text"""
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        header_names = [h[1] for h in headers]
        assert "Rule Title" in header_names
        assert "Purpose" in header_names
        assert "Contract" in header_names
        assert "Response Template" in header_names
        assert "Validation" in header_names
        assert "References" in header_names
        assert "Example Output" not in header_names
        assert "Old Validation Approach (deprecated)" not in header_names


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_content(self):
        parser = MarkdownParser("")
        headers = parser.get_actual_headers()
        assert len(headers) == 0

    def test_no_headers(self):
        content = "Just plain text\nNo headers here"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()
        assert len(headers) == 0

    def test_inline_code_not_treated_as_block(self):
        content = "## Header with `inline code`"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert "Header with `inline code`" in headers[0][1]

    def test_header_with_special_characters(self):
        content = "## Purpose: Define Core Patterns"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert "Purpose: Define Core Patterns" in headers[0][1]

    def test_header_with_markdown_formatting(self):
        content = "## **Bold** and *italic* header"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1

    def test_false_header_without_space(self):
        content = "##NoSpace\n## Real Header"
        parser = MarkdownParser(content)
        headers = parser.get_actual_headers()

        assert len(headers) == 1
        assert headers[0][1] == "Real Header"
