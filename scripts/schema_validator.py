#!/usr/bin/env python3
"""Schema-based validator for AI coding rules.

This validator uses YAML schema definitions to validate rule files against
002-rule-governance.md v3.0 standards. It replaces regex-based validation
with a declarative, maintainable schema approach.

Usage:
    python scripts/schema_validator.py rules/100-snowflake-core.md
    python scripts/schema_validator.py rules/
    python scripts/schema_validator.py rules/ --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@dataclass
class ValidationError:
    """Represents a validation error with context and fix suggestions."""

    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "INFO"]
    message: str
    error_group: str
    line_num: int | None = None
    fix_suggestion: str | None = None
    docs_reference: str | None = None
    context: str | None = None

    # Enhanced debugging fields
    actual_value: Any | None = None
    expected_value: Any | None = None
    matched_items: list[str] | None = None
    line_preview: str | None = None

    def format_detailed(self) -> str:
        """Format error for detailed console output with enhanced context."""
        output = [f"[{self.error_group}] {self.message}"]

        if self.line_num:
            output.append(f"  Line: {self.line_num}")
            if self.line_preview:
                preview = self.line_preview[:100]
                if len(self.line_preview) > 100:
                    preview += "..."
                output.append(f"  Content: {preview}")

        if self.actual_value is not None and self.expected_value is not None:
            output.append(f"  Expected: {self.expected_value}")
            output.append(f"  Actual:   {self.actual_value}")

        if self.matched_items:
            output.append(f"  Found {len(self.matched_items)} items:")
            for item in self.matched_items[:5]:
                output.append(f"    - {item}")
            if len(self.matched_items) > 5:
                output.append(f"    ... and {len(self.matched_items) - 5} more")

        if self.fix_suggestion:
            output.append(f"  Fix: {self.fix_suggestion}")

        if self.docs_reference:
            output.append(f"  Reference: {self.docs_reference}")

        return "\n".join(output)


@dataclass
class ValidationResult:
    """Result of validating a single rule file."""

    file_path: Path
    errors: list[ValidationError] = field(default_factory=list)
    passed_checks: int = 0

    @property
    def critical_count(self) -> int:
        """Count of CRITICAL severity errors."""
        return sum(1 for e in self.errors if e.severity == "CRITICAL")

    @property
    def high_count(self) -> int:
        """Count of HIGH severity errors."""
        return sum(1 for e in self.errors if e.severity == "HIGH")

    @property
    def medium_count(self) -> int:
        """Count of MEDIUM severity errors."""
        return sum(1 for e in self.errors if e.severity == "MEDIUM")

    @property
    def info_count(self) -> int:
        """Count of INFO severity errors."""
        return sum(1 for e in self.errors if e.severity == "INFO")

    @property
    def has_critical_or_high(self) -> bool:
        """Check if result has any CRITICAL or HIGH severity errors."""
        return self.critical_count > 0 or self.high_count > 0

    @property
    def is_clean(self) -> bool:
        """Check if result has no errors."""
        return len(self.errors) == 0

    @property
    def is_valid(self) -> bool:
        """Check if result is valid (no errors)."""
        return len(self.errors) == 0

    def get_grouped_errors(self) -> dict[str, list[ValidationError]]:
        """Group errors by error_group."""
        grouped: dict[str, list[ValidationError]] = {}
        for error in self.errors:
            if error.error_group not in grouped:
                grouped[error.error_group] = []
            grouped[error.error_group].append(error)
        return grouped


class CodeBlockTracker:
    """Track code block and contextual state while parsing markdown.

    Enhanced to handle:
    - Both ``` and ~~~ fence styles (3+ characters)
    - Variable-length fences (e.g., ```` for nesting)
    - Indented code blocks (within lists, blockquotes)
    - Proper fence matching by type, length, and indentation level
    """

    def __init__(self):
        """Initialize code block tracker with default state."""
        self.in_code_block = False
        self.code_block_language: str | None = None
        self.fence_char: str | None = None  # Track ` vs ~
        self.fence_length: int = 0  # Track fence length (3, 4, etc.)
        self.fence_indent: int = 0
        self.in_blockquote = False
        self.current_section: str | None = None

    def update(self, line: str) -> None:
        """Update state based on current line with robust fence detection."""
        stripped = line.strip()

        # Detect fence type, length, and language (supports ```, ~~~, ````, etc.)
        fence_match = re.match(r"^(\s*)(`{3,}|~{3,})(\w*)", line)
        if fence_match:
            indent_str, fence, lang = fence_match.groups()
            indent_level = len(indent_str)
            fence_char = fence[0]  # ` or ~
            fence_len = len(fence)

            if not self.in_code_block:
                # Opening fence
                self.in_code_block = True
                self.fence_char = fence_char
                self.fence_length = fence_len
                self.fence_indent = indent_level
                self.code_block_language = lang if lang else None
            elif (
                fence_char == self.fence_char
                and fence_len >= self.fence_length
                and indent_level == self.fence_indent
            ):
                # Closing fence (must match char type, be at least as long, and match indent)
                self.in_code_block = False
                self.fence_char = None
                self.fence_length = 0
                self.fence_indent = 0
                self.code_block_language = None

        # Blockquote detection
        self.in_blockquote = stripped.startswith(">")

        # Section detection (only outside code blocks)
        if not self.in_code_block and stripped.startswith("## "):
            self.current_section = stripped[3:].strip()

    def should_skip_validation(self, validation_type: str) -> bool:
        """Determine if validation should be skipped based on context."""
        if validation_type == "emoji":
            # Skip emoji checks in code blocks
            return self.in_code_block
        elif validation_type == "section_header":
            # Only detect real section headers outside code blocks
            return self.in_code_block
        return False


class SchemaValidator:
    """Validates rule files against YAML schema definitions."""

    def __init__(self, schema_path: Path | None = None, debug: bool = False):
        """Initialize validator with schema.

        Args:
            schema_path: Path to YAML schema file. Defaults to schemas/rule-schema.yml
            debug: Enable debug logging
        """
        if schema_path is None:
            schema_path = project_root / "schemas" / "rule-schema.yml"

        self.schema_path = schema_path
        self.debug = debug
        self.schema = self._load_schema()

    def _load_schema(self) -> dict[str, Any]:
        """Load and validate YAML schema file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path) as f:
            schema = yaml.safe_load(f)

        # Basic schema validation
        required_keys = ["version", "metadata", "structure", "content_rules"]
        for key in required_keys:
            if key not in schema:
                raise ValueError(f"Schema missing required key: {key}")

        return schema

    def _debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log debug message if debug mode enabled."""
        if not self.debug:
            return

        print(f"[DEBUG] {message}", file=sys.stderr)
        if context:
            for key, value in context.items():
                print(f"  {key}: {value}", file=sys.stderr)

    def _normalize_section_name(self, section_text: str) -> str:
        """Normalize section name for flexible matching.

        - Remove parentheticals: (anything in parens)
        - Remove numbering: ## 1. Section -> Section
        - Strip whitespace
        - Lowercase for case-insensitive match
        """
        # Remove parentheticals
        text = re.sub(r"\s*\([^)]*\)", "", section_text)
        # Remove numbering prefix
        text = re.sub(r"^\d+\.\s+", "", text)
        # Normalize whitespace
        text = " ".join(text.split())
        return text.strip().lower()

    def _extract_section(
        self,
        lines: list[str],
        section_name_pattern: str | re.Pattern,
        track_code_blocks: bool = True,
    ) -> tuple[int | None, int | None, str]:
        """Extract section content by name pattern.

        Args:
            lines: File lines
            section_name_pattern: Regex pattern or string to match section name
            track_code_blocks: If True, ignore ## inside ``` blocks

        Returns:
            (section_start_line, section_end_line, section_content)
        """
        section_start = None
        section_end = None
        tracker = CodeBlockTracker() if track_code_blocks else None

        # Compile pattern if string
        if isinstance(section_name_pattern, str):
            # Support both exact match and flexible pattern
            pattern = re.compile(re.escape(section_name_pattern), re.IGNORECASE)
        else:
            pattern = section_name_pattern

        for i, line in enumerate(lines):
            if tracker:
                tracker.update(line)

            # Skip section detection inside code blocks
            if tracker and tracker.in_code_block:
                continue

            if section_start is None and re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line):
                match = re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line)
                if match is None:  # Guard for type checker (already validated above)
                    continue
                section_text = match.group(1).strip()
                normalized = self._normalize_section_name(section_text)

                # Try pattern match on both original and normalized
                if pattern.search(section_text) or pattern.search(normalized):
                    section_start = i
                    self._debug("Found section start", {"line": i + 1, "name": section_text})
            elif section_start is not None and re.match(r"^##\s+", line):
                section_end = i
                self._debug("Found section end", {"line": i + 1})
                break

        if section_start is None:
            return None, None, ""

        section_end = section_end or len(lines)
        section_content = "\n".join(lines[section_start:section_end])

        return section_start, section_end, section_content

    def _find_all_sections(self, lines: list[str]) -> dict[str, int]:
        """Find all H2 sections with code block awareness.

        Uses CodeBlockTracker to ignore section headers inside code fences.
        This ensures consistent section detection across all validation methods.

        Args:
            lines: File lines to parse

        Returns:
            Dictionary mapping normalized section names to line numbers (1-indexed)
        """
        sections = {}
        tracker = CodeBlockTracker()

        for i, line in enumerate(lines, 1):
            tracker.update(line)

            # Skip section detection inside code blocks
            if tracker.in_code_block:
                continue

            # Match ## SectionName or ## N. SectionName
            match = re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line)
            if match:
                section_text = match.group(1).strip()
                normalized = self._normalize_section_name(section_text)
                sections[normalized] = i

        return sections

    def _find_h1_titles(self, lines: list[str]) -> list[int]:
        """Find all H1 titles with code block awareness.

        Args:
            lines: File lines to parse

        Returns:
            List of line numbers (1-indexed) where H1 titles are found
        """
        h1_lines = []
        tracker = CodeBlockTracker()

        for i, line in enumerate(lines, 1):
            tracker.update(line)

            if tracker.in_code_block:
                continue

            if re.match(r"^#\s+.+$", line):
                h1_lines.append(i)

        return h1_lines

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single rule file against the schema.

        Args:
            file_path: Path to rule file to validate

        Returns:
            ValidationResult with errors and passed checks
        """
        result = ValidationResult(file_path=file_path)

        # Read file content
        try:
            with open(file_path) as f:
                content = f.read()
        except Exception as e:
            result.errors.append(
                ValidationError(
                    severity="CRITICAL",
                    message=f"Failed to read file: {e}",
                    error_group="File",
                )
            )
            return result

        # Parse markdown structure
        lines = content.split("\n")

        # Run validation phases
        self._validate_metadata(content, lines, result)
        self._validate_structure(content, lines, result)
        self._validate_content(content, lines, result)
        self._validate_restrictions(content, lines, result)
        self._validate_links(content, lines, result)

        return result

    def _validate_metadata(self, content: str, lines: list[str], result: ValidationResult) -> None:
        """Validate metadata fields per schema."""
        metadata_config = self.schema["metadata"]

        # Check for ## Metadata header (v3.0 requirement)
        if "header" in metadata_config:
            header_config = metadata_config["header"]
            if header_config.get("required", False):
                metadata_header_pattern = r"^## Metadata\s*$"
                if not re.search(metadata_header_pattern, content, re.MULTILINE):
                    result.errors.append(
                        ValidationError(
                            severity=header_config.get("severity", "HIGH"),
                            message=header_config["error_message"],
                            error_group="Metadata",
                            line_num=1,  # Metadata header should be near top
                            fix_suggestion=header_config.get("fix_suggestion"),
                            docs_reference=header_config.get("docs_reference"),
                        )
                    )
                else:
                    result.passed_checks += 1

        # Extract metadata from content
        metadata = {}
        for field_config in metadata_config["required_fields"]:
            field_name = field_config["name"]
            field_format = field_config["format"]
            pattern = re.escape(field_format) + r"\s*(.+)"

            match = re.search(pattern, content, re.MULTILINE)
            if match:
                metadata[field_name] = match.group(1).strip()
                line_num = content[: match.start()].count("\n") + 1
                metadata[f"{field_name}_line"] = line_num
            else:
                # Missing required field
                result.errors.append(
                    ValidationError(
                        severity=field_config["severity"],
                        message=field_config["error_message"],
                        error_group="Metadata",
                        line_num=1,  # Metadata should be at top of file
                        fix_suggestion=field_config.get("fix_suggestion"),
                        docs_reference=field_config.get("docs_reference"),
                    )
                )
                continue

        # Validate Keywords count
        if "Keywords" in metadata:
            keywords = [k.strip() for k in metadata["Keywords"].split(",")]
            keywords_config = next(
                f for f in metadata_config["required_fields"] if f["name"] == "Keywords"
            )
            min_items = keywords_config["min_items"]
            max_items = keywords_config["max_items"]

            if not (min_items <= len(keywords) <= max_items):
                needed = min_items - len(keywords) if len(keywords) < min_items else 0
                fix_msg = keywords_config["fix_suggestion"].format(needed=needed)
                result.errors.append(
                    ValidationError(
                        severity=keywords_config["severity"],
                        message=f"Keywords count: {len(keywords)} (expected {min_items}-{max_items})",
                        error_group="Metadata",
                        line_num=metadata.get("Keywords_line"),
                        fix_suggestion=fix_msg,
                        docs_reference=keywords_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

        # Validate TokenBudget format
        if "TokenBudget" in metadata:
            token_budget = metadata["TokenBudget"]
            tb_config = next(
                f for f in metadata_config["required_fields"] if f["name"] == "TokenBudget"
            )
            pattern = tb_config["pattern"]

            if not re.match(pattern, token_budget):
                result.errors.append(
                    ValidationError(
                        severity=tb_config["severity"],
                        message=tb_config["error_message"],
                        error_group="Metadata",
                        line_num=metadata.get("TokenBudget_line"),
                        fix_suggestion=tb_config.get("fix_suggestion", "").format(
                            calculated_value="~" + str(len(content.split()) * 1.3)[:4]
                        ),
                        docs_reference=tb_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

        # Validate ContextTier
        if "ContextTier" in metadata:
            tier = metadata["ContextTier"]
            tier_config = next(
                f for f in metadata_config["required_fields"] if f["name"] == "ContextTier"
            )
            allowed = tier_config["allowed_values"]

            if tier not in allowed:
                result.errors.append(
                    ValidationError(
                        severity=tier_config["severity"],
                        message=tier_config["error_message"],
                        error_group="Metadata",
                        line_num=metadata.get("ContextTier_line"),
                        fix_suggestion=tier_config.get("fix_suggestion"),
                        docs_reference=tier_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

        # Validate Depends
        if "Depends" in metadata:
            depends = metadata["Depends"]
            if not depends or depends.strip() == "":
                depends_config = next(
                    f for f in metadata_config["required_fields"] if f["name"] == "Depends"
                )
                result.errors.append(
                    ValidationError(
                        severity=depends_config["severity"],
                        message=depends_config["error_message"],
                        error_group="Metadata",
                        line_num=metadata.get("Depends_line"),
                        fix_suggestion=depends_config.get("fix_suggestion"),
                        docs_reference=depends_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

        # Validate SchemaVersion format
        if "SchemaVersion" in metadata:
            schema_version = metadata["SchemaVersion"]
            sv_config = next(
                (f for f in metadata_config["required_fields"] if f["name"] == "SchemaVersion"),
                None,
            )
            if sv_config:
                pattern = sv_config.get("pattern", r"^v\d+\.\d+(\.\d+)?$")

                if not re.match(pattern, schema_version):
                    result.errors.append(
                        ValidationError(
                            severity=sv_config["severity"],
                            message=sv_config["error_message"],
                            error_group="Metadata",
                            line_num=metadata.get("SchemaVersion_line"),
                            fix_suggestion=sv_config.get("fix_suggestion"),
                            docs_reference=sv_config.get("docs_reference"),
                        )
                    )
                else:
                    result.passed_checks += 1

        # Validate RuleVersion format
        if "RuleVersion" in metadata:
            rule_version = metadata["RuleVersion"]
            rv_config = next(
                (f for f in metadata_config["required_fields"] if f["name"] == "RuleVersion"),
                None,
            )
            if rv_config:
                pattern = rv_config.get("pattern", r"^v\d+\.\d+\.\d+$")

                if not re.match(pattern, rule_version):
                    result.errors.append(
                        ValidationError(
                            severity=rv_config["severity"],
                            message=rv_config["error_message"],
                            error_group="Metadata",
                            line_num=metadata.get("RuleVersion_line"),
                            fix_suggestion=rv_config.get("fix_suggestion"),
                            docs_reference=rv_config.get("docs_reference"),
                        )
                    )
                else:
                    result.passed_checks += 1

        # Check metadata field order
        field_order_config = metadata_config["field_order"]
        if field_order_config["required"]:
            expected_order = field_order_config["order"]
            actual_order = []

            for field in expected_order:
                if f"{field}_line" in metadata:
                    actual_order.append((field, metadata[f"{field}_line"]))

            # Check if actual order matches expected
            actual_field_order = [f[0] for f in sorted(actual_order, key=lambda x: x[1])]
            expected_present = [f for f in expected_order if f in dict(actual_order)]

            if actual_field_order != expected_present:
                # Find first metadata field line for reference
                first_field_line = min(
                    (
                        metadata.get(f"{f}_line", 999)
                        for f in expected_order
                        if f"{f}_line" in metadata
                    ),
                    default=1,
                )
                result.errors.append(
                    ValidationError(
                        severity=field_order_config["severity"],
                        message=field_order_config["error_message"],
                        error_group="Metadata",
                        line_num=first_field_line,
                        fix_suggestion=field_order_config.get("fix_suggestion"),
                        docs_reference=field_order_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

    def _validate_structure(self, content: str, lines: list[str], result: ValidationResult) -> None:
        """Validate document structure per schema."""
        structure_config = self.schema["structure"]

        self._debug(
            "Starting structure validation",
            {"total_lines": len(lines), "content_length": len(content)},
        )

        # Validate H1 title count (must have exactly one)
        if "title" in structure_config:
            title_config = structure_config["title"]
            h1_lines = self._find_h1_titles(lines)

            if len(h1_lines) == 0:
                result.errors.append(
                    ValidationError(
                        severity=title_config.get("severity", "CRITICAL"),
                        message="Missing H1 title - document must have exactly one",
                        error_group="Structure",
                        line_num=1,
                        fix_suggestion=title_config.get(
                            "fix_suggestion", "Add an H1 title at the start of the document"
                        ),
                        docs_reference=title_config.get("docs_reference"),
                    )
                )
            elif len(h1_lines) > 1:
                result.errors.append(
                    ValidationError(
                        severity=title_config.get("severity", "CRITICAL"),
                        message=f"Multiple H1 titles found at lines {h1_lines} - must have exactly one",
                        error_group="Structure",
                        line_num=h1_lines[1],
                        fix_suggestion="Remove duplicate H1 titles, keeping only the first one",
                        docs_reference=title_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

        # Find all H2 sections using shared utility with code block tracking
        sections = self._find_all_sections(lines)

        self._debug(
            "Found sections",
            {"count": len(sections), "normalized_names": list(sections.keys())[:10]},
        )

        # Check required sections
        for section_config in structure_config["required_sections"]:
            section_name = section_config["name"]
            normalized_expected = self._normalize_section_name(section_name)

            if normalized_expected not in sections:
                # Estimate where section should be based on existing sections
                existing_lines = sorted(sections.values()) if sections else [1]
                suggested_line = existing_lines[-1] if existing_lines else 1
                result.errors.append(
                    ValidationError(
                        severity=section_config["severity"],
                        message=section_config["error_message"],
                        error_group=section_config["error_group"],
                        line_num=suggested_line,
                        fix_suggestion=f"Add '## {section_name}' section",
                        docs_reference=section_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

        # Check section order with detailed diff
        if structure_config["section_order"]["validate_sequence"]:
            required_sections = structure_config["required_sections"]
            section_order_config = structure_config["section_order"]

            # Get actual order of required sections (using normalized names)
            actual_sections = []
            for section_config in required_sections:
                normalized = self._normalize_section_name(section_config["name"])
                if normalized in sections:
                    actual_sections.append((section_config["name"], sections[normalized]))

            actual_sections.sort(key=lambda x: x[1])
            actual_order = [s[0] for s in actual_sections]

            # Expected order
            expected_order = [s["name"] for s in required_sections]
            expected_present = [
                s for s in expected_order if self._normalize_section_name(s) in sections
            ]

            if actual_order != expected_present:
                # Generate detailed diff
                diff = self._format_section_order_diff(expected_present, actual_order)

                # Find line of first out-of-order section
                first_wrong_line = actual_sections[0][1] if actual_sections else 1
                result.errors.append(
                    ValidationError(
                        severity=section_order_config["severity"],
                        message=section_order_config["error_message"],
                        error_group="Structure",
                        line_num=first_wrong_line,
                        fix_suggestion=diff,
                        expected_value=expected_present,
                        actual_value=actual_order,
                    )
                )
            else:
                result.passed_checks += 1

    def _format_section_order_diff(self, expected: list[str], actual: list[str]) -> str:
        """Generate human-readable section order comparison."""
        output = ["Section order mismatch:", ""]
        output.append("Expected order:")
        for i, section in enumerate(expected, 1):
            marker = "✓" if i <= len(actual) and actual[i - 1] == section else "✗"
            output.append(f"  {marker} {i}. {section}")

        output.append("")
        output.append("Actual order:")
        for i, section in enumerate(actual, 1):
            try:
                expected_pos = expected.index(section) + 1
                marker = "✓" if expected_pos == i else "✗"
                output.append(f"  {marker} {i}. {section} (expected at position {expected_pos})")
            except ValueError:
                output.append(f"  ? {i}. {section} (not in expected list)")

        return "\n".join(output)

    def _validate_content(self, content: str, lines: list[str], result: ValidationResult) -> None:
        """Validate section content per schema."""
        content_rules = self.schema.get("content_rules", {})

        # Validate Contract content
        if "contract" in content_rules:
            self._validate_contract(content, lines, result, content_rules["contract"])

        # Validate Anti-Patterns content
        if "anti_patterns" in content_rules:
            self._validate_anti_patterns(content, lines, result, content_rules["anti_patterns"])

    def _validate_contract(
        self, content: str, lines: list[str], result: ValidationResult, config: dict
    ) -> None:
        """Validate Contract section content."""
        # Extract Contract section using centralized utility
        section_start, _, section_content = self._extract_section(
            lines, r"Contract", track_code_blocks=True
        )

        if not section_start:
            return

        # Validate required subsections (v3.2 uses ### Markdown headers)
        for validation in config.get("validations", []):
            if validation["type"] == "required_subsections":
                for subsection in validation["subsections"]:
                    subsection_name = subsection["name"]
                    pattern = subsection["pattern"]

                    if not re.search(pattern, section_content):
                        fix_msg = validation["fix_suggestion"].format(
                            subsection_name=subsection_name
                        )
                        result.errors.append(
                            ValidationError(
                                severity=validation["severity"],
                                message=f"Contract missing required subsection: {subsection_name}",
                                error_group="Contract",
                                line_num=section_start + 1,
                                fix_suggestion=fix_msg,
                            )
                        )
                    else:
                        result.passed_checks += 1

            elif validation["type"] == "no_xml_tags":
                # Check for XML tags (v3.2 prohibition)
                for tag in validation["forbidden_patterns"]:
                    if tag in section_content:
                        result.errors.append(
                            ValidationError(
                                severity=validation["severity"],
                                message=f"{validation['error_message']}: {tag}",
                                error_group="Contract",
                                line_num=section_start + 1,
                                fix_suggestion=validation.get("fix_suggestion"),
                            )
                        )
                    else:
                        result.passed_checks += 1

    def _validate_anti_patterns(
        self, content: str, lines: list[str], result: ValidationResult, config: dict
    ) -> None:
        """Validate Anti-Patterns section content."""
        # Extract section (being careful to skip ## inside code blocks)
        section_start = None
        section_end = None
        in_code_block = False

        for i, line in enumerate(lines):
            # Track code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            # Only match H2 headers outside of code blocks
            if not in_code_block:
                if re.match(r"^##\s+(?:\d+\.\s+)?Anti-Patterns", line):
                    section_start = i
                elif section_start is not None and re.match(r"^##\s+", line):
                    section_end = i
                    break

        if not section_start:
            return

        section_end = section_end or len(lines)
        section_content = "\n".join(lines[section_start:section_end])

        # Validate code blocks and keywords
        for validation in config.get("validations", []):
            if validation["type"] == "code_block_count":
                code_blocks = re.findall(r"```", section_content)
                count = len(code_blocks) // 2  # Pairs of ```
                min_count = validation["min"]

                if count < min_count:
                    result.errors.append(
                        ValidationError(
                            severity=validation["severity"],
                            message=validation["error_message"],
                            error_group="Anti-Patterns",
                            line_num=section_start + 1,
                            fix_suggestion=validation.get("fix_suggestion"),
                        )
                    )
                else:
                    result.passed_checks += 1

            elif validation["type"] == "keyword_presence":
                for keyword in validation["must_contain"]:
                    if keyword not in section_content:
                        result.errors.append(
                            ValidationError(
                                severity=validation["severity"],
                                message=validation["error_message"],
                                error_group="Anti-Patterns",
                                line_num=section_start + 1,
                                fix_suggestion=validation.get("fix_suggestion"),
                            )
                        )
                    else:
                        result.passed_checks += 1

            elif validation["type"] == "pattern_pairs":
                # Check for Problem: ... Correct Pattern: pairs
                pattern = validation["pattern"]
                min_pairs = validation["min"]
                matches = re.findall(pattern, section_content, re.DOTALL)
                count = len(matches)

                if count < min_pairs:
                    result.errors.append(
                        ValidationError(
                            severity=validation["severity"],
                            message=validation["error_message"],
                            error_group="Anti-Patterns",
                            line_num=section_start + 1,
                            fix_suggestion=validation.get("fix_suggestion"),
                        )
                    )
                else:
                    result.passed_checks += 1

    def _validate_restrictions(
        self, content: str, lines: list[str], result: ValidationResult
    ) -> None:
        """Validate format restrictions."""
        restrictions_config = self.schema.get("restrictions", {})

        # Check for numbered sections (v3.2 prohibition)
        if restrictions_config.get("no_numbered_sections", {}).get("enabled"):
            numbered_config = restrictions_config["no_numbered_sections"]
            numbered_pattern = numbered_config["pattern"]
            tracker = CodeBlockTracker()

            for i, line in enumerate(lines, 1):
                tracker.update(line)

                # Skip checking inside code blocks
                if tracker.in_code_block:
                    continue

                if re.match(numbered_pattern, line):
                    result.errors.append(
                        ValidationError(
                            severity=numbered_config["severity"],
                            message=numbered_config["error_message"],
                            error_group="Format",
                            line_num=i,
                            line_preview=line.strip(),
                            fix_suggestion=numbered_config.get("fix_suggestion"),
                            docs_reference=numbered_config.get("docs_reference"),
                        )
                    )
                else:
                    result.passed_checks += 1

        # Check for ASCII patterns (decision trees, tables, arrows)
        self._validate_ascii_patterns(content, lines, result)

        # Check for emojis
        if restrictions_config.get("no_emojis", {}).get("enabled"):
            emoji_config = restrictions_config["no_emojis"]
            emoji_pattern = emoji_config["pattern"]

            # Track code block state to exclude emojis in code examples
            in_code_block = False

            for i, line in enumerate(lines, 1):
                # Toggle code block state
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    result.passed_checks += 1
                    continue

                # Skip emoji checking inside code blocks
                if in_code_block:
                    result.passed_checks += 1
                    continue

                if re.search(emoji_pattern, line):
                    result.errors.append(
                        ValidationError(
                            severity=emoji_config["severity"],
                            message=emoji_config["error_message"],
                            error_group="Format",
                            line_num=i,
                            fix_suggestion=emoji_config.get("fix_suggestion", "").format(
                                line_number=i, emoji_char="[emoji]"
                            ),
                            docs_reference=emoji_config.get("docs_reference"),
                        )
                    )
                else:
                    result.passed_checks += 1

        # Check for YAML frontmatter
        if restrictions_config.get("no_yaml_frontmatter", {}).get("enabled"):
            yaml_config = restrictions_config["no_yaml_frontmatter"]
            if content.startswith("---"):
                result.errors.append(
                    ValidationError(
                        severity=yaml_config["severity"],
                        message=yaml_config["error_message"],
                        error_group="Format",
                        line_num=1,
                        fix_suggestion=yaml_config.get("fix_suggestion"),
                        docs_reference=yaml_config.get("docs_reference"),
                    )
                )
            else:
                result.passed_checks += 1

    def _validate_ascii_patterns(
        self, content: str, lines: list[str], result: ValidationResult
    ) -> None:
        """Validate Priority 1 compliance: agent-parseable formatting.

        Priority 1 violations (agent understanding) - See 000-global-core.md:
        - ASCII decision trees (├─, └─, │)
        - ASCII tables (|---|)
        - Arrow characters (→)
        - Mermaid diagrams (```mermaid)
        - Horizontal rule separators (---) as visual dividers

        These patterns are problematic for LLM sequential text processing.
        See 002e-agent-optimization.md for alternatives.

        Skips:
        - Content inside code blocks (``` ... ```)
        - Content inside inline code (`...`)
        """
        # Track code block state to allow examples in documentation
        tracker = CodeBlockTracker()

        # Priority 1 patterns to detect (agent understanding violations)
        tree_pattern = re.compile(r"[├└│]")
        table_pattern = re.compile(r"\|[-]+\|")
        arrow_pattern = re.compile(r"→")
        mermaid_pattern = re.compile(r"```mermaid", re.IGNORECASE)
        hr_pattern = re.compile(r"^---+\s*$")

        # Pattern to remove inline code before checking
        inline_code_pattern = re.compile(r"`[^`]+`")

        for i, line in enumerate(lines, 1):
            # Capture state BEFORE updating (for accurate nested block detection)
            was_in_code_block = tracker.in_code_block
            tracker.update(line)

            # Skip checks inside code blocks (allows examples in Anti-Patterns docs)
            if tracker.in_code_block:
                continue

            # Also skip if we WERE in a code block (handles closing fence lines)
            if was_in_code_block:
                continue

            # Remove inline code before checking (allows documenting patterns in backticks)
            line_without_inline_code = inline_code_pattern.sub("", line)

            # Check for ASCII decision tree characters (Priority 1 violation)
            if tree_pattern.search(line_without_inline_code):
                result.errors.append(
                    ValidationError(
                        severity="HIGH",
                        message="Priority 1 violation: ASCII decision tree characters detected (├─, └─, │)",
                        error_group="Priority 1",
                        line_num=i,
                        line_preview=line.strip()[:80],
                        fix_suggestion="Replace with nested conditional lists. See 002e-agent-optimization.md Anti-Pattern 7",
                        docs_reference="002e-agent-optimization.md",
                    )
                )

            # Check for ASCII tables (Priority 1 violation)
            if table_pattern.search(line_without_inline_code):
                result.errors.append(
                    ValidationError(
                        severity="HIGH",
                        message="Priority 1 violation: ASCII table pattern detected (|---|)",
                        error_group="Priority 1",
                        line_num=i,
                        line_preview=line.strip()[:80],
                        fix_suggestion="Replace with structured lists. See 002e-agent-optimization.md Anti-Pattern 1",
                        docs_reference="002e-agent-optimization.md",
                    )
                )

            # Check for arrow characters
            if arrow_pattern.search(line_without_inline_code):
                result.errors.append(
                    ValidationError(
                        severity="HIGH",
                        message="Priority 1 violation: Arrow character (→) detected",
                        error_group="Priority 1",
                        line_num=i,
                        line_preview=line.strip()[:80],
                        fix_suggestion="Replace with text alternatives (then, to, becomes). See 002e-agent-optimization.md Anti-Pattern 6",
                        docs_reference="002e-agent-optimization.md",
                    )
                )

            # Check for Mermaid diagrams (Priority 1 violation)
            # Only flag actual mermaid code fence openings (not examples in docs)
            if mermaid_pattern.match(line.strip()):
                result.errors.append(
                    ValidationError(
                        severity="HIGH",
                        message="Priority 1 violation: Mermaid diagram detected",
                        error_group="Priority 1",
                        line_num=i,
                        line_preview=line.strip()[:80],
                        fix_suggestion="Replace with structured conditional lists. See 002e-agent-optimization.md Anti-Pattern 8",
                        docs_reference="002e-agent-optimization.md",
                    )
                )

            # Check for horizontal rule separators (Priority 1 violation)
            # Only flag standalone --- lines, not YAML frontmatter or table separators
            # Skip line 1 (could be YAML frontmatter start)
            if hr_pattern.match(line) and not tracker.in_code_block and i > 1:
                result.errors.append(
                    ValidationError(
                        severity="MEDIUM",
                        message="Priority 2 violation: Horizontal rule separator (---) detected",
                        error_group="Priority 2",
                        line_num=i,
                        line_preview=line.strip()[:80],
                        fix_suggestion="Use headers (###) for structure instead of visual separators. See 002e-agent-optimization.md Anti-Pattern 9",
                        docs_reference="002e-agent-optimization.md",
                    )
                )

    def _validate_links(self, content: str, lines: list[str], result: ValidationResult) -> None:
        """Validate links and references."""
        link_config = self.schema.get("link_validation", {})

        # Validate Related Rules subsection format
        # Note: Both bare filenames (e.g., 000-global-core.md) and prefixed references
        # (e.g., rules/000-global-core.md) are valid. The rules/ location is defined
        # in AGENTS.md for token efficiency.
        refs_section_config = link_config.get("references_section", {})
        related_rules_config = refs_section_config.get("related_rules_subsection", {})

        if related_rules_config.get("rule_reference_format"):
            format_config = related_rules_config["rule_reference_format"]
            allowed_root_files = format_config.get("allowed_root_files", [])

            # Find ### Related Rules subsection
            related_rules_match = re.search(
                r"### Related Rules\s*\n(.*?)(?=\n###|\n##|$)", content, re.DOTALL
            )
            if related_rules_match:
                related_rules_content = related_rules_match.group(1)

                # Find all .md references in Related Rules subsection
                # Accept both bare filenames and rules/ prefixed paths
                md_pattern = r"`((?:rules/)?[a-zA-Z0-9_-]+\.md)`"
                for match in re.finditer(md_pattern, related_rules_content):
                    filename = match.group(1)

                    # Check if it's an allowed root file (strip rules/ prefix if present)
                    bare_filename = filename.replace("rules/", "")
                    if bare_filename in allowed_root_files or filename in allowed_root_files:
                        result.passed_checks += 1
                        continue

                    # Both formats are valid - just count as passed
                    result.passed_checks += 1

        # Validate rule references
        if link_config.get("rule_references", {}).get("enabled"):
            ref_config = link_config["rule_references"]
            pattern = ref_config["pattern"]
            check_exists = ref_config.get("check_exists", True)
            placeholders = ref_config.get("allowed_placeholders", [])

            for match in re.finditer(pattern, content):
                ref_path = match.group(0)

                # Skip placeholders
                if any(ph in ref_path for ph in placeholders):
                    result.passed_checks += 1
                    continue

                # Check if file exists
                if check_exists:
                    full_path = project_root / ref_path
                    if not full_path.exists():
                        line_num = content[: match.start()].count("\n") + 1
                        result.errors.append(
                            ValidationError(
                                severity=ref_config["severity"],
                                message=ref_config["error_message"].format(file_path=ref_path),
                                error_group="Links",
                                line_num=line_num,
                                fix_suggestion=ref_config.get("fix_suggestion"),
                            )
                        )
                    else:
                        result.passed_checks += 1

    def format_result(self, result: ValidationResult, detailed: bool = True) -> str:
        """Format validation result for console output.

        Args:
            result: ValidationResult to format
            detailed: If True, show detailed error information

        Returns:
            Formatted string for console output
        """
        output = []

        # Header
        output.append("=" * 80)
        output.append(f"VALIDATION REPORT: {result.file_path}")
        output.append("=" * 80)
        output.append("")

        # Summary
        output.append("SUMMARY:")
        output.append(f"  ❌ CRITICAL: {result.critical_count}")
        output.append(f"  ⚠️  HIGH: {result.high_count}")
        output.append(f"  ℹ️  MEDIUM: {result.medium_count}")
        output.append(f"  ✓ Passed: {result.passed_checks} checks")
        output.append("")

        if not result.errors:
            output.append("✅ All validations passed!")
            output.append("")
            output.append("=" * 80)
            return "\n".join(output)

        # Show errors by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "INFO"]:
            errors_at_level = [e for e in result.errors if e.severity == severity]
            if not errors_at_level:
                continue

            symbol = {"CRITICAL": "❌", "HIGH": "⚠️ ", "MEDIUM": "ℹ️ ", "INFO": "✓"}[severity]
            output.append(f"{symbol} {severity} ISSUES ({len(errors_at_level)}):")
            output.append("─" * 80)

            # Group by error_group
            groups = {}
            for error in errors_at_level:
                if error.error_group not in groups:
                    groups[error.error_group] = []
                groups[error.error_group].append(error)

            for _group_name, group_errors in groups.items():
                for error in group_errors:
                    if detailed:
                        output.append(error.format_detailed())
                    else:
                        output.append(f"[{error.error_group}] {error.message}")

            output.append("")

        # Footer
        output.append("=" * 80)
        if result.has_critical_or_high:
            output.append("RESULT: ❌ FAILED")
        else:
            output.append("RESULT: ⚠️  WARNINGS ONLY")
        output.append("=" * 80)

        return "\n".join(output)

    def validate_directory(
        self, directory: Path, excluded_files: set[str] | None = None
    ) -> list[ValidationResult]:
        """Validate all rule files in a directory.

        Args:
            directory: Directory containing rule files
            excluded_files: Set of filenames to exclude

        Returns:
            List of ValidationResults
        """
        if excluded_files is None:
            excluded_files = self.schema.get("excluded_files", {}).get("files", set())
            excluded_files = set(excluded_files)

        results = []
        rule_files = sorted(directory.glob("*.md"))

        for file_path in rule_files:
            if file_path.name in excluded_files:
                continue

            result = self.validate_file(file_path)
            results.append(result)

        return results

    def validate_agents_md(self, agents_path: Path | None = None) -> ValidationResult:
        """Validate AGENTS.md for ASCII patterns.

        AGENTS.md is the bootstrap protocol file that should also follow
        agent optimization patterns (no ASCII trees, tables, or arrows).

        Args:
            agents_path: Path to AGENTS.md. Defaults to project root.

        Returns:
            ValidationResult with any ASCII pattern violations
        """
        if agents_path is None:
            agents_path = project_root / "AGENTS.md"

        result = ValidationResult(file_path=agents_path)

        if not agents_path.exists():
            # AGENTS.md is optional, not an error if missing
            return result

        try:
            with open(agents_path) as f:
                content = f.read()
        except Exception as e:
            result.errors.append(
                ValidationError(
                    severity="CRITICAL",
                    message=f"Failed to read AGENTS.md: {e}",
                    error_group="File",
                )
            )
            return result

        lines = content.split("\n")

        # Only validate ASCII patterns for AGENTS.md
        self._validate_ascii_patterns(content, lines, result)

        return result

    def format_json(self, results: list[ValidationResult]) -> str:
        """Format validation results as JSON.

        Args:
            results: List of ValidationResults to format

        Returns:
            JSON string with summary, failed_files, and warning_files
        """
        import json

        output: dict[str, Any] = {
            "summary": {
                "total_files": len(results),
                "clean": sum(1 for r in results if r.is_clean),
                "warnings_only": sum(1 for r in results if r.errors and not r.has_critical_or_high),
                "failed": sum(1 for r in results if r.has_critical_or_high),
            },
            "failed_files": [],
            "warning_files": [],
        }

        for result in results:
            if result.has_critical_or_high:
                output["failed_files"].append(
                    {
                        "path": str(result.file_path),
                        "critical_count": result.critical_count,
                        "high_count": result.high_count,
                        "medium_count": result.medium_count,
                        "errors": [
                            {
                                "severity": e.severity,
                                "group": e.error_group,
                                "message": e.message,
                                "line": e.line_num,
                                "fix": e.fix_suggestion,
                            }
                            for e in result.errors
                        ],
                    }
                )
            elif result.errors:
                output["warning_files"].append(
                    {
                        "path": str(result.file_path),
                        "medium_count": result.medium_count,
                        "errors": [
                            {
                                "severity": e.severity,
                                "group": e.error_group,
                                "message": e.message,
                                "line": e.line_num,
                                "fix": e.fix_suggestion,
                            }
                            for e in result.errors
                        ],
                    }
                )

        return json.dumps(output, indent=2)


def main():
    """CLI entry point for schema validator."""
    parser = argparse.ArgumentParser(description="Validate AI coding rules against YAML schema")
    parser.add_argument(
        "path",
        type=Path,
        help="Path to rule file or directory to validate",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=None,
        help="Path to YAML schema file (default: schemas/rule-schema.yml)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed reports for each file (default: summary only)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Minimal output (summary counts only, no file lists)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to stderr",
    )

    args = parser.parse_args()

    # Initialize validator
    try:
        validator = SchemaValidator(schema_path=args.schema, debug=args.debug)
    except Exception as e:
        print(f"Error loading schema: {e}", file=sys.stderr)
        return 1

    # Validate file or directory
    if args.path.is_file():
        # Special handling for AGENTS.md - only validate ASCII patterns, not rule schema
        if args.path.name == "AGENTS.md":
            result = validator.validate_agents_md(args.path)
        else:
            result = validator.validate_file(args.path)
        print(validator.format_result(result, detailed=args.verbose))

        if result.has_critical_or_high or (args.strict and result.errors):
            return 1
        return 0

    elif args.path.is_dir():
        results = validator.validate_directory(args.path)

        # Also validate AGENTS.md if validating rules/ directory
        # Look for AGENTS.md in the parent directory of rules/
        if args.path.name == "rules" or str(args.path).endswith("rules"):
            agents_path = args.path.parent / "AGENTS.md"
            if agents_path.exists():
                agents_result = validator.validate_agents_md(agents_path)
                if agents_result.errors:
                    results.append(agents_result)

        # JSON output mode
        if args.json:
            print(validator.format_json(results))
            failed = sum(1 for r in results if r.has_critical_or_high)
            warnings = sum(1 for r in results if r.errors and not r.has_critical_or_high)
            if failed > 0 or (args.strict and warnings > 0):
                return 1
            return 0

        # Print individual results only in verbose mode
        if args.verbose:
            for result in results:
                print(validator.format_result(result, detailed=True))
                print()

        # Print summary
        total_files = len(results)
        failed = sum(1 for r in results if r.has_critical_or_high)
        warnings = sum(1 for r in results if r.errors and not r.has_critical_or_high)
        clean = sum(1 for r in results if r.is_clean)

        print("=" * 80)
        print("OVERALL SUMMARY")
        print("=" * 80)
        print(f"Total files: {total_files}")
        print(f"✅ Clean: {clean}")
        print(f"⚠️  Warnings only: {warnings}")
        print(f"❌ Failed: {failed}")

        # Show failed files list (unless --quiet mode)
        if not args.quiet:
            if failed > 0:
                print()
                print("❌ FAILED FILES:")
                for i, result in enumerate([r for r in results if r.has_critical_or_high], 1):
                    print(
                        f"  {i}. {result.file_path.name} "
                        f"({result.critical_count} CRITICAL, {result.high_count} HIGH)"
                    )

            # Show warning files preview (first 5)
            if warnings > 0:
                print()
                print("⚠️  WARNING FILES (showing first 5):")
                warning_results = [r for r in results if r.errors and not r.has_critical_or_high]
                for i, result in enumerate(warning_results[:5], 1):
                    print(f"  {i}. {result.file_path.name} ({result.medium_count} MEDIUM)")
                if len(warning_results) > 5:
                    print(f"  ... and {len(warning_results) - 5} more")

            # Helpful tip for detailed inspection
            if failed > 0 or warnings > 0:
                print()
                print(
                    "💡 TIP: Run with --verbose to see detailed reports, or validate individual file"
                )

        print("=" * 80)

        if failed > 0 or (args.strict and (warnings > 0)):
            return 1
        return 0

    else:
        print(f"Error: {args.path} is not a file or directory", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
