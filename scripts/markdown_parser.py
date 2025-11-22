#!/usr/bin/env python3
"""
Markdown-aware parser for rule validation.

Provides context-aware parsing of markdown files to distinguish actual
content from code examples, HTML comments, and template sections.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class CodeBlockRegion:
    """Represents a code block region in markdown."""

    start_line: int
    end_line: int
    language: str | None


@dataclass
class HtmlCommentRegion:
    """Represents an HTML comment region in markdown."""

    start_line: int
    end_line: int


@dataclass
class Section:
    """Represents a section in markdown with hierarchical context.

    Attributes:
        name: Section heading text (cleaned, no level markers)
        level: Header level (H2=2, H3=3, etc.)
        line_num: Line number where section starts (1-indexed)
        parent: Reference to parent section (None for root-level)
        children: List of child sections
        is_template: Whether this section is a template/example
        is_code_example: Whether this section is within a code block
    """

    name: str
    level: int
    line_num: int
    parent: Section | None = None
    children: list[Section] = field(default_factory=list)
    is_template: bool = False
    is_code_example: bool = False

    def add_child(self, child: Section) -> None:
        """Add a child section to this section.

        Args:
            child: Child section to add
        """
        self.children.append(child)
        child.parent = self

    def get_ancestors(self) -> list[Section]:
        """Get all ancestor sections from parent to root.

        Returns:
            List of ancestor sections in order from parent to root (excludes __root__)
        """
        ancestors = []
        current = self.parent
        while current is not None:
            # Skip __root__ sentinel
            if current.name != "__root__":
                ancestors.append(current)
            current = current.parent
        return ancestors

    def is_ancestor_template(self) -> bool:
        """Check if any ancestor section is a template section.

        Returns:
            True if any ancestor is marked as template
        """
        return any(ancestor.is_template for ancestor in self.get_ancestors())


class SectionHierarchy:
    """Builds and manages hierarchical section structure from markdown.

    Provides methods to:
    - Build section tree from flat header list
    - Filter out template/example sections
    - Query section relationships
    """

    def __init__(self, parser: MarkdownParser):
        """Initialize hierarchy builder with parser.

        Args:
            parser: MarkdownParser instance with parsed content
        """
        self.parser = parser
        self.root: Section | None = None
        self.sections: list[Section] = []
        self._template_keywords = [
            "template",
            "example",
            "structure",
            "boilerplate",
            "required rule structure",
            "rule creation template",
        ]

    def build(self) -> Section:
        """Build section hierarchy from parser's headers.

        Returns:
            Root section containing all top-level sections as children
        """
        # Create root section as container
        self.root = Section(name="__root__", level=0, line_num=0)
        headers = self.parser.get_actual_headers()

        # Track stack of sections by level for parent assignment
        section_stack: dict[int, Section] = {0: self.root}

        for line_num, heading, level in headers:
            # Determine if this is a template section
            is_template = self._is_template_section(heading, level, line_num)

            # Create section
            section = Section(name=heading, level=level, line_num=line_num, is_template=is_template)
            self.sections.append(section)

            # Find parent (closest section with lower level)
            parent_level = level - 1
            while parent_level >= 0:
                if parent_level in section_stack:
                    parent = section_stack[parent_level]
                    parent.add_child(section)
                    break
                parent_level -= 1

            # Update stack at this level
            section_stack[level] = section

            # Clear deeper levels
            levels_to_clear = [lv for lv in section_stack if lv > level]
            for lv in levels_to_clear:
                del section_stack[lv]

        return self.root

    def _is_template_section(self, heading: str, level: int, line_num: int) -> bool:
        """Check if section is a template/example section.

        IMPORTANT: This only checks if the section ITSELF contains template keywords.
        It does NOT mark children of template sections as templates.
        Use is_ancestor_template() to check if a section's parent is a template.

        Args:
            heading: Section heading text
            level: Header level (2=H2, 3=H3, etc.)
            line_num: Line number of header

        Returns:
            True if section heading contains template keywords
        """
        # Direct keyword match in heading ONLY
        # Do not propagate template status from parent
        return any(kw in heading.lower() for kw in self._template_keywords)

    def get_actual_rule_sections(self) -> list[Section]:
        """Get sections that are actual rule content (not templates/examples).

        Returns:
            List of sections excluding templates and their descendants
        """
        actual_sections = []

        for section in self.sections:
            # Skip if section itself is template
            if section.is_template:
                continue

            # Skip if any ancestor is template
            if section.is_ancestor_template():
                continue

            actual_sections.append(section)

        return actual_sections

    def get_h2_sections(self) -> list[Section]:
        """Get all H2 (##) sections.

        Returns:
            List of H2 sections
        """
        return [s for s in self.sections if s.level == 2]

    def get_actual_h2_sections(self) -> list[Section]:
        """Get H2 sections that are actual rule content (not templates).

        Returns:
            List of H2 sections excluding templates
        """
        return [s for s in self.get_actual_rule_sections() if s.level == 2]


class MarkdownParser:
    """Context-aware markdown parser for rule validation.

    Tracks code blocks (```), HTML comments (<!-- -->), and provides
    methods to query actual document structure excluding examples.
    """

    def __init__(self, content: str):
        """Initialize parser with markdown content.

        Args:
            content: Full markdown file content as string
        """
        self.content = content
        self.lines = content.split("\n")
        self._code_block_regions: list[CodeBlockRegion] | None = None
        self._html_comment_regions: list[HtmlCommentRegion] | None = None

    def _parse_code_blocks(self) -> list[CodeBlockRegion]:
        """Parse all code block regions from content.

        Returns:
            List of CodeBlockRegion objects representing all code blocks
        """
        if self._code_block_regions is not None:
            return self._code_block_regions

        regions = []
        in_code_block = False
        block_start = 0
        block_language = None

        for line_num, line in enumerate(self.lines, start=1):
            stripped = line.strip()

            if stripped.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    block_start = line_num
                    lang_match = re.match(r"```(\w+)", stripped)
                    block_language = lang_match.group(1) if lang_match else None
                else:
                    in_code_block = False
                    regions.append(
                        CodeBlockRegion(
                            start_line=block_start,
                            end_line=line_num,
                            language=block_language,
                        )
                    )
                    block_language = None

        if in_code_block:
            regions.append(
                CodeBlockRegion(
                    start_line=block_start,
                    end_line=len(self.lines),
                    language=block_language,
                )
            )

        self._code_block_regions = regions
        return regions

    def _parse_html_comments(self) -> list[HtmlCommentRegion]:
        """Parse all HTML comment regions from content.

        Returns:
            List of HtmlCommentRegion objects representing all HTML comments
        """
        if self._html_comment_regions is not None:
            return self._html_comment_regions

        regions = []
        in_comment = False
        comment_start = 0

        for line_num, line in enumerate(self.lines, start=1):
            if "<!--" in line and not in_comment:
                in_comment = True
                comment_start = line_num

            if "-->" in line and in_comment:
                in_comment = False
                regions.append(HtmlCommentRegion(start_line=comment_start, end_line=line_num))

        if in_comment:
            regions.append(HtmlCommentRegion(start_line=comment_start, end_line=len(self.lines)))

        self._html_comment_regions = regions
        return regions

    def is_in_code_block(self, line_num: int) -> bool:
        """Check if line is within a code block.

        Args:
            line_num: Line number (1-indexed)

        Returns:
            True if line is within ``` code block
        """
        regions = self._parse_code_blocks()
        return any(region.start_line <= line_num <= region.end_line for region in regions)

    def is_in_html_comment(self, line_num: int) -> bool:
        """Check if line is within HTML comment.

        Args:
            line_num: Line number (1-indexed)

        Returns:
            True if line is within <!-- --> comment
        """
        regions = self._parse_html_comments()
        return any(region.start_line <= line_num <= region.end_line for region in regions)

    def get_code_block_regions(self) -> list[CodeBlockRegion]:
        """Get all code block regions in document.

        Returns:
            List of CodeBlockRegion objects
        """
        return self._parse_code_blocks()

    def get_actual_headers(self) -> list[tuple[int, str, int]]:
        """Extract actual markdown headers excluding code blocks and comments.

        Returns:
            List of (line_num, header_text, level) tuples for actual headers
        """
        headers = []

        for line_num, line in enumerate(self.lines, start=1):
            if self.is_in_code_block(line_num):
                continue

            if self.is_in_html_comment(line_num):
                continue

            stripped = line.strip()
            header_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2).strip()
                headers.append((line_num, text, level))

        return headers

    def extract_context(self, line_num: int, context_lines: int = 3) -> list[tuple[int, str]]:
        """Extract surrounding lines for context around a specific line.

        Args:
            line_num: Line number (1-indexed) to extract context around
            context_lines: Number of lines before and after to include

        Returns:
            List of (line_num, line_content) tuples for context
        """
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.lines), line_num + context_lines)

        context = []
        for i in range(start, end):
            context.append((i + 1, self.lines[i]))

        return context

    def is_template_section(self, line_num: int, heading: str, level: int | None = None) -> bool:
        """Determine if header is within a template/example section.

        Checks for:
        1. Direct template keywords in heading
        2. Parent H2 section containing template keywords (only for H3+ headers)

        Args:
            line_num: Line number of the header
            heading: Header text to check
            level: Header level (H2=2, H3=3, etc.). If None, will be extracted from line.

        Returns:
            True if header is within template/example section
        """
        template_keywords = [
            "template",
            "example",
            "structure",
            "boilerplate",
            "required rule structure",
            "rule creation template",
        ]

        if any(kw in heading.lower() for kw in template_keywords):
            return True

        if level is None:
            line = self.lines[line_num - 1] if line_num > 0 else ""
            header_match = re.match(r"^(#{1,6})\s+", line)
            level = len(header_match.group(1)) if header_match else 2

        if level == 2:
            return False

        for i in range(line_num - 2, max(-1, line_num - 51), -1):
            if i < 0:
                break
            line = self.lines[i]
            if re.match(r"^##\s+", line):
                parent_heading = re.match(r"^##\s+(.+)$", line)
                if parent_heading:
                    parent_text = parent_heading.group(1)
                    if any(kw in parent_text.lower() for kw in template_keywords):
                        return True
                break

        return False
