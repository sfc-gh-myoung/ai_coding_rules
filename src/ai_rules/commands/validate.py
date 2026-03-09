"""Schema-based validator for AI coding rules.

This validator uses YAML schema definitions to validate rule files against
002-rule-governance.md v3.0 standards. It replaces regex-based validation
with a declarative, maintainable schema approach.

Ported from scripts/schema_validator.py to the ai-rules CLI.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Literal

import typer
import yaml
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ai_rules._shared.console import (
    console,
    err_console,
    log_error,
    log_info,
)
from ai_rules._shared.paths import find_project_root, get_schemas_dir


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

    def __init__(self) -> None:
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

    def __init__(
        self,
        schema_path: Path | None = None,
        debug: bool = False,
        project_root: Path | None = None,
    ) -> None:
        """Initialize validator with schema.

        Args:
            schema_path: Path to YAML schema file. Defaults to schemas/rule-schema.yml
            debug: Enable debug logging
            project_root: Project root for resolving relative paths
        """
        self.project_root = project_root or find_project_root()

        if schema_path is None:
            schema_path = get_schemas_dir(self.project_root) / "rule-schema.yml"

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

        err_console.print(f"[dim][DEBUG] {message}[/dim]")
        if context:
            for key, value in context.items():
                err_console.print(f"[dim]  {key}: {value}[/dim]")

    def _get_null_byte_locations(self, content: str, positions: list[int]) -> list[dict[str, Any]]:
        """Convert byte offsets of null bytes to line/column locations.

        Args:
            content: Full file content
            positions: List of byte offsets where null bytes were found

        Returns:
            List of dicts with line, column, offset, and preview for each null byte
        """
        locations = []
        lines = content.split("\n")

        for pos in positions:
            # Find line number (1-indexed)
            line_num = content[:pos].count("\n") + 1
            # Find column (1-indexed)
            line_start = content.rfind("\n", 0, pos) + 1
            column = pos - line_start + 1

            # Get line preview (handle line containing null byte)
            if line_num <= len(lines):
                preview = lines[line_num - 1][:60].replace("\x00", "<NUL>")
                if len(lines[line_num - 1]) > 60:
                    preview += "..."
            else:
                preview = "<unable to extract>"

            locations.append(
                {
                    "line": line_num,
                    "column": column,
                    "offset": pos,
                    "preview": preview,
                }
            )

        return locations

    def _validate_file_integrity(
        self, content: str, result: ValidationResult, verbose: bool = False
    ) -> bool:
        """Check for null bytes and other file integrity issues.

        Null bytes in text files cause silent truncation - content after the
        null byte is ignored, causing validators to pass on incomplete files.

        Args:
            content: Full file content to check
            result: ValidationResult to append errors to
            verbose: If True, report each null byte location; otherwise summary only

        Returns:
            True if file is clean, False if corruption detected
        """
        null_positions = []
        for i, char in enumerate(content):
            if char == "\x00":
                null_positions.append(i)

        if null_positions:
            # Calculate line/column for each occurrence
            locations = self._get_null_byte_locations(content, null_positions)

            if verbose:
                # Detailed output: show each location
                for loc in locations:
                    result.errors.append(
                        ValidationError(
                            severity="CRITICAL",
                            message=f"Null byte at line {loc['line']}, column {loc['column']} (byte offset {loc['offset']})",
                            error_group="File Integrity",
                            line_num=loc["line"],
                            line_preview=loc["preview"],
                            fix_suggestion="Remove null bytes using: sed -i 's/\\x00//g' <file>",
                        )
                    )
            else:
                # Summary output: single error with count
                result.errors.append(
                    ValidationError(
                        severity="CRITICAL",
                        message=f"File contains {len(null_positions)} null byte(s) - content may be silently truncated",
                        error_group="File Integrity",
                        line_num=locations[0]["line"] if locations else 1,
                        fix_suggestion="Run with --verbose to see all locations. Fix: sed -i 's/\\x00//g' <file>",
                    )
                )
            return False

        result.passed_checks += 1
        return True

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
        section_name_pattern: str | re.Pattern[str],
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

            if section_start is None and (match := re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line)):
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

    def validate_file(self, file_path: Path, verbose: bool = False) -> ValidationResult:
        """Validate a single rule file against the schema.

        Args:
            file_path: Path to rule file to validate
            verbose: If True, show detailed null byte locations

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

        # File integrity check (runs first, before line parsing)
        # Null bytes cause silent truncation - stop early if detected
        if not self._validate_file_integrity(content, result, verbose=verbose):
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

            for field_name in expected_order:
                if f"{field_name}_line" in metadata:
                    actual_order.append((field_name, metadata[f"{field_name}_line"]))

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
            marker = "+" if i <= len(actual) and actual[i - 1] == section else "-"
            output.append(f"  {marker} {i}. {section}")

        output.append("")
        output.append("Actual order:")
        for i, section in enumerate(actual, 1):
            try:
                expected_pos = expected.index(section) + 1
                marker = "+" if expected_pos == i else "-"
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
        self, content: str, lines: list[str], result: ValidationResult, config: dict[str, Any]
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
        self, content: str, lines: list[str], result: ValidationResult, config: dict[str, Any]
    ) -> None:
        """Validate Anti-Patterns section content."""
        # Extract section (being careful to skip ## inside code blocks)
        # Use CodeBlockTracker for proper handling of variable-length fences (```, ````, etc.)
        section_start = None
        section_end = None
        tracker = CodeBlockTracker()

        for i, line in enumerate(lines):
            tracker.update(line)

            # Only match H2 headers outside of code blocks
            if not tracker.in_code_block:
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
        - ASCII decision trees
        - ASCII tables (|---|)
        - Arrow characters
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
                        message="Priority 1 violation: ASCII decision tree characters detected",
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
                        message="Priority 1 violation: Arrow character detected",
                        error_group="Priority 1",
                        line_num=i,
                        line_preview=line.strip()[:80],
                        fix_suggestion="Replace with text alternatives (then, to, becomes). See 002e-agent-optimization.md Anti-Pattern 6",
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

            for match in re.finditer(pattern, content):
                ref_path = match.group(0)

                # Check if file exists
                if check_exists:
                    full_path = self.project_root / ref_path
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

    def format_result(self, result: ValidationResult, detailed: bool = True) -> None:
        """Format validation result for Rich console output.

        Args:
            result: ValidationResult to format
            detailed: If True, show detailed error information
        """
        # Summary table
        table = Table(title=f"Validation: {result.file_path.name}", show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Count", justify="right")

        table.add_row("[red]CRITICAL[/red]", str(result.critical_count))
        table.add_row("[yellow]HIGH[/yellow]", str(result.high_count))
        table.add_row("[blue]MEDIUM[/blue]", str(result.medium_count))
        table.add_row("[green]Passed[/green]", str(result.passed_checks))

        console.print(table)

        if result.is_clean:
            console.print(Panel("[green]All validations passed![/green]", border_style="green"))
            return

        # Show errors by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "INFO"]:
            errors_at_level = [e for e in result.errors if e.severity == severity]
            if not errors_at_level:
                continue

            color = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "blue", "INFO": "dim"}[severity]
            console.print(
                f"\n[{color} bold]{severity} ISSUES ({len(errors_at_level)}):[/{color} bold]"
            )

            # Group by error_group
            groups: dict[str, list[ValidationError]] = {}
            for error in errors_at_level:
                if error.error_group not in groups:
                    groups[error.error_group] = []
                groups[error.error_group].append(error)

            for _group_name, group_errors in groups.items():
                for error in group_errors:
                    if detailed:
                        console.print(f"[{color}]{error.format_detailed()}[/{color}]")
                    else:
                        console.print(f"[{color}][{error.error_group}] {error.message}[/{color}]")

        # Result summary
        if result.has_critical_or_high:
            console.print(Panel("[red bold]RESULT: FAILED[/red bold]", border_style="red"))
        else:
            console.print(Panel("[yellow]RESULT: WARNINGS ONLY[/yellow]", border_style="yellow"))

    def validate_directory(
        self, directory: Path, excluded_files: set[str] | None = None, verbose: bool = False
    ) -> list[ValidationResult]:
        """Validate all rule files in a directory.

        Args:
            directory: Directory containing rule files
            excluded_files: Set of filenames to exclude
            verbose: If True, show detailed null byte locations

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

            result = self.validate_file(file_path, verbose=verbose)
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
            agents_path = self.project_root / "AGENTS.md"

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


class ExampleValidator:
    """Validates example files against example-schema.yml."""

    def __init__(
        self,
        schema_path: Path | None = None,
        debug: bool = False,
        project_root: Path | None = None,
    ) -> None:
        """Initialize validator with example schema.

        Args:
            schema_path: Path to example YAML schema file. Defaults to schemas/example-schema.yml
            debug: Enable debug logging
            project_root: Project root for resolving relative paths
        """
        self.project_root = project_root or find_project_root()

        if schema_path is None:
            schema_path = get_schemas_dir(self.project_root) / "example-schema.yml"

        self.schema_path = schema_path
        self.debug = debug
        self.schema = self._load_schema()

    def _load_schema(self) -> dict[str, Any]:
        """Load and validate example YAML schema file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Example schema file not found: {self.schema_path}")

        with open(self.schema_path) as f:
            schema = yaml.safe_load(f)

        return schema

    def _debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log debug message if debug mode enabled."""
        if not self.debug:
            return

        err_console.print(f"[dim][DEBUG] {message}[/dim]")
        if context:
            for key, value in context.items():
                err_console.print(f"[dim]  {key}: {value}[/dim]")

    def _get_null_byte_locations(self, content: str, positions: list[int]) -> list[dict[str, Any]]:
        """Convert byte offsets of null bytes to line/column locations.

        Args:
            content: Full file content
            positions: List of byte offsets where null bytes were found

        Returns:
            List of dicts with line, column, offset, and preview for each null byte
        """
        locations = []
        lines = content.split("\n")

        for pos in positions:
            # Find line number (1-indexed)
            line_num = content[:pos].count("\n") + 1
            # Find column (1-indexed)
            line_start = content.rfind("\n", 0, pos) + 1
            column = pos - line_start + 1

            # Get line preview (handle line containing null byte)
            if line_num <= len(lines):
                preview = lines[line_num - 1][:60].replace("\x00", "<NUL>")
                if len(lines[line_num - 1]) > 60:
                    preview += "..."
            else:
                preview = "<unable to extract>"

            locations.append(
                {
                    "line": line_num,
                    "column": column,
                    "offset": pos,
                    "preview": preview,
                }
            )

        return locations

    def _validate_file_integrity(
        self, content: str, result: ValidationResult, verbose: bool = False
    ) -> bool:
        """Check for null bytes and other file integrity issues.

        Args:
            content: Full file content to check
            result: ValidationResult to append errors to
            verbose: If True, report each null byte location; otherwise summary only

        Returns:
            True if file is clean, False if corruption detected
        """
        null_positions = []
        for i, char in enumerate(content):
            if char == "\x00":
                null_positions.append(i)

        if null_positions:
            locations = self._get_null_byte_locations(content, null_positions)

            if verbose:
                for loc in locations:
                    result.errors.append(
                        ValidationError(
                            severity="CRITICAL",
                            message=f"Null byte at line {loc['line']}, column {loc['column']} (byte offset {loc['offset']})",
                            error_group="File Integrity",
                            line_num=loc["line"],
                            line_preview=loc["preview"],
                            fix_suggestion="Remove null bytes using: sed -i 's/\\x00//g' <file>",
                        )
                    )
            else:
                result.errors.append(
                    ValidationError(
                        severity="CRITICAL",
                        message=f"File contains {len(null_positions)} null byte(s) - content may be silently truncated",
                        error_group="File Integrity",
                        line_num=locations[0]["line"] if locations else 1,
                        fix_suggestion="Run with --verbose to see all locations. Fix: sed -i 's/\\x00//g' <file>",
                    )
                )
            return False

        result.passed_checks += 1
        return True

    def validate_file(self, file_path: Path, verbose: bool = False) -> ValidationResult:
        """Validate a single example file against the schema.

        Args:
            file_path: Path to example file to validate
            verbose: If True, show detailed null byte locations

        Returns:
            ValidationResult with errors and passed checks
        """
        result = ValidationResult(file_path=file_path)

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

        # File integrity check (runs first, before line parsing)
        if not self._validate_file_integrity(content, result, verbose=verbose):
            return result

        lines = content.split("\n")

        # Validate required sections
        for section in self.schema.get("required_sections", []):
            self._validate_section(content, lines, result, section)

        # Validate context fields
        for ctx_field in self.schema.get("context_fields", []):
            self._validate_context_field(content, result, ctx_field)

        return result

    def _validate_section(
        self, content: str, lines: list[str], result: ValidationResult, section: dict[str, Any]
    ) -> None:
        """Validate a required section exists."""
        name = section.get("name", "Unknown")
        pattern = section.get("pattern")
        heading = section.get("heading")

        found = False

        if pattern:
            if re.search(pattern, content, re.MULTILINE):
                found = True
        elif heading:
            for line in lines:
                if line.strip() == heading:
                    found = True
                    break

        if found:
            result.passed_checks += 1
            # Check must_contain if specified
            if section.get("must_contain"):
                if section["must_contain"] in content:
                    result.passed_checks += 1
                else:
                    result.errors.append(
                        ValidationError(
                            severity=section.get("severity", "HIGH"),
                            message=f"{name} section must contain {section['must_contain']}",
                            error_group=section.get("error_group", "Structure"),
                        )
                    )
        else:
            result.errors.append(
                ValidationError(
                    severity=section.get("severity", "HIGH"),
                    message=section.get("error_message", f"Missing required section: {name}"),
                    error_group=section.get("error_group", "Structure"),
                )
            )

    def _validate_context_field(
        self, content: str, result: ValidationResult, field: dict[str, Any]
    ) -> None:
        """Validate a context field format."""
        name = field.get("name", "Unknown")
        pattern = field.get("pattern")

        if pattern and re.search(pattern, content):
            result.passed_checks += 1
        else:
            result.errors.append(
                ValidationError(
                    severity=field.get("severity", "MEDIUM"),
                    message=field.get("error_message", f"Invalid format for {name}"),
                    error_group="Context",
                )
            )

    def validate_directory(self, directory: Path, verbose: bool = False) -> list[ValidationResult]:
        """Validate all example files in a directory.

        Args:
            directory: Directory containing example files (typically rules/examples/)
            verbose: If True, show detailed null byte locations

        Returns:
            List of ValidationResults
        """
        results = []
        example_files = sorted(directory.glob("*.md"))

        for file_path in example_files:
            result = self.validate_file(file_path, verbose=verbose)
            results.append(result)

        return results

    def format_result(self, result: ValidationResult, detailed: bool = True) -> None:
        """Format validation result for Rich console output."""
        table = Table(title=f"Example Validation: {result.file_path.name}", show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Count", justify="right")

        table.add_row("[red]CRITICAL[/red]", str(result.critical_count))
        table.add_row("[yellow]HIGH[/yellow]", str(result.high_count))
        table.add_row("[blue]MEDIUM[/blue]", str(result.medium_count))
        table.add_row("[green]Passed[/green]", str(result.passed_checks))

        console.print(table)

        if result.is_clean:
            console.print(Panel("[green]All validations passed![/green]", border_style="green"))
            return

        for error in result.errors:
            color = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "blue", "INFO": "dim"}.get(
                error.severity, "white"
            )
            if detailed:
                console.print(f"[{color}]{error.format_detailed()}[/{color}]")
            else:
                console.print(f"[{color}][{error.error_group}] {error.message}[/{color}]")


def validate(
    ctx: typer.Context,
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to rule file or directory to validate.",
            show_default=False,
        ),
    ] = None,
    schema: Annotated[
        Path | None,
        typer.Option(
            "--schema",
            help="Path to YAML schema file (default: schemas/rule-schema.yml).",
        ),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Treat warnings as errors.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed reports for each file (default: summary only).",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Minimal output (summary counts only, no file lists).",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results in JSON format.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug logging to stderr.",
        ),
    ] = False,
    examples: Annotated[
        bool,
        typer.Option(
            "--examples",
            help="Validate example files in rules/examples/ against example-schema.yml.",
        ),
    ] = False,
    templates: Annotated[
        bool,
        typer.Option(
            "--templates",
            help="Validate AGENTS template files against ASCII pattern rules.",
        ),
    ] = False,
) -> None:
    """Validate AI coding rules against YAML schema.

    Validates rule files against 002-rule-governance.md v3.0 standards using
    declarative YAML schema definitions.

    Examples:
        # Validate a single rule file
        ai-rules validate rules/100-snowflake-core.md

        # Validate all rules in a directory
        ai-rules validate rules/

        # Validate with strict mode (warnings as errors)
        ai-rules validate rules/ --strict

        # Output results as JSON
        ai-rules validate rules/ --json

        # Validate example files
        ai-rules validate rules/examples/ --examples
    """
    if path is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Resolve project root
    try:
        project_root = find_project_root()
    except FileNotFoundError:
        log_error("Could not find project root (no pyproject.toml found)")
        raise typer.Exit(1) from None

    # Handle --examples mode separately
    if examples:
        try:
            example_validator = ExampleValidator(debug=debug, project_root=project_root)
        except Exception as e:
            log_error(f"Error loading example schema: {e}")
            raise typer.Exit(1) from None

        # Determine examples directory
        if path.is_dir():
            examples_dir = path
        else:
            # Assume rules/examples/ if a file is specified
            examples_dir = (
                path.parent if "examples" in str(path) else project_root / "rules" / "examples"
            )

        if not examples_dir.exists():
            log_info(f"Examples directory not found: {examples_dir}")
            raise typer.Exit(0)  # Not an error if no examples exist yet

        results = example_validator.validate_directory(examples_dir, verbose=verbose)

        if not results:
            log_info(f"No example files found in {examples_dir}")
            raise typer.Exit(0)

        if verbose:
            for result in results:
                example_validator.format_result(result, detailed=True)
                console.print()

        # Print summary
        total_files = len(results)
        failed = sum(1 for r in results if r.has_critical_or_high)
        clean = sum(1 for r in results if r.is_clean)

        # List failed examples (even without verbose mode)
        if failed > 0 and not verbose:
            console.print("\n[bold red]FAILED EXAMPLES:[/bold red]")
            for result in results:
                if result.has_critical_or_high:
                    console.print(f"  • {result.file_path.name}")
                    # Show first error for context
                    for error in result.errors:
                        if error.severity in ("CRITICAL", "HIGH"):
                            console.print(f"    [dim]{error.message}[/dim]")
                            break
            console.print()

        summary_table = Table(title="Example Validation Summary")
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Count", justify="right")
        summary_table.add_row("Total examples", str(total_files))
        summary_table.add_row("[green]Valid[/green]", str(clean))
        summary_table.add_row("[red]Invalid[/red]", str(failed))
        console.print(summary_table)

        if failed > 0:
            raise typer.Exit(1) from None
        raise typer.Exit(0)

    # Handle --templates mode separately
    if templates:
        try:
            validator = SchemaValidator(schema_path=schema, debug=debug, project_root=project_root)
        except Exception as e:
            log_error(f"Error loading schema: {e}")
            raise typer.Exit(1) from None

        # Determine templates directory
        if path.is_dir():
            templates_dir = path
        else:
            templates_dir = path.parent if "templates" in str(path) else project_root / "templates"

        if not templates_dir.exists():
            log_info(f"Templates directory not found: {templates_dir}")
            raise typer.Exit(0)

        template_files = sorted(templates_dir.glob("*.md.template"))

        if not template_files:
            log_info(f"No template files found in {templates_dir}")
            raise typer.Exit(0)

        results: list[ValidationResult] = []
        for template_path in template_files:
            result = validator.validate_agents_md(template_path)
            results.append(result)

        if verbose:
            for result in results:
                validator.format_result(result, detailed=True)
                console.print()

        # Print summary
        total_files = len(results)
        failed = sum(1 for r in results if r.has_critical_or_high)
        clean = sum(1 for r in results if r.is_clean)

        # List failed templates (even without verbose mode)
        if failed > 0 and not verbose:
            console.print("\n[bold red]FAILED TEMPLATES:[/bold red]")
            for result in results:
                if result.has_critical_or_high:
                    console.print(f"  • {result.file_path.name}")
                    for error in result.errors:
                        if error.severity in ("CRITICAL", "HIGH"):
                            console.print(f"    [dim]{error.message}[/dim]")
                            break
            console.print()

        summary_table = Table(title="Template Validation Summary")
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Count", justify="right")
        summary_table.add_row("Total templates", str(total_files))
        summary_table.add_row("[green]Valid[/green]", str(clean))
        summary_table.add_row("[red]Invalid[/red]", str(failed))
        console.print(summary_table)

        if failed > 0:
            raise typer.Exit(1) from None
        raise typer.Exit(0)

    # Initialize validator for rule files
    try:
        validator = SchemaValidator(schema_path=schema, debug=debug, project_root=project_root)
    except Exception as e:
        log_error(f"Error loading schema: {e}")
        raise typer.Exit(1) from None

    # Validate file or directory
    if path.is_file():
        # Special handling for AGENTS.md - only validate ASCII patterns, not rule schema
        if path.name == "AGENTS.md":
            result = validator.validate_agents_md(path)
        else:
            result = validator.validate_file(path, verbose=verbose)
        validator.format_result(result, detailed=verbose)

        if result.has_critical_or_high or (strict and result.errors):
            raise typer.Exit(1) from None
        raise typer.Exit(0)

    elif path.is_dir():
        # Use progress bar for multi-file validation
        rule_files = sorted(path.glob("*.md"))
        excluded_files = validator.schema.get("excluded_files", {}).get("files", set())
        excluded_files = set(excluded_files)
        rule_files = [f for f in rule_files if f.name not in excluded_files]

        results: list[ValidationResult] = []

        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Validating files...", total=len(rule_files))
                for file_path in rule_files:
                    progress.update(task, description=f"Validating {file_path.name}...")
                    result = validator.validate_file(file_path, verbose=verbose)
                    results.append(result)
                    progress.advance(task)
        else:
            for file_path in rule_files:
                result = validator.validate_file(file_path, verbose=verbose)
                results.append(result)

        # JSON output mode
        if json_output:
            console.print(validator.format_json(results))
            failed = sum(1 for r in results if r.has_critical_or_high)
            warnings = sum(1 for r in results if r.errors and not r.has_critical_or_high)
            if failed > 0 or (strict and warnings > 0):
                raise typer.Exit(1) from None
            raise typer.Exit(0)

        # Print individual results only in verbose mode
        if verbose:
            for result in results:
                validator.format_result(result, detailed=True)
                console.print()

        # Print summary
        total_files = len(results)
        failed = sum(1 for r in results if r.has_critical_or_high)
        warnings = sum(1 for r in results if r.errors and not r.has_critical_or_high)
        clean = sum(1 for r in results if r.is_clean)

        summary_table = Table(title="Overall Summary")
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Count", justify="right")
        summary_table.add_row("Total files", str(total_files))
        summary_table.add_row("[green]Clean[/green]", str(clean))
        summary_table.add_row("[yellow]Warnings only[/yellow]", str(warnings))
        summary_table.add_row("[red]Failed[/red]", str(failed))
        console.print(summary_table)

        # Show failed files list (unless --quiet mode)
        if not quiet:
            if failed > 0:
                console.print("\n[red bold]FAILED FILES:[/red bold]")
                for i, result in enumerate([r for r in results if r.has_critical_or_high], 1):
                    console.print(
                        f"  {i}. [red]{result.file_path.name}[/red] "
                        f"({result.critical_count} CRITICAL, {result.high_count} HIGH)"
                    )

            # Show warning files preview (first 5)
            if warnings > 0:
                console.print("\n[yellow bold]WARNING FILES (showing first 5):[/yellow bold]")
                warning_results = [r for r in results if r.errors and not r.has_critical_or_high]
                for i, result in enumerate(warning_results[:5], 1):
                    console.print(
                        f"  {i}. [yellow]{result.file_path.name}[/yellow] ({result.medium_count} MEDIUM)"
                    )
                if len(warning_results) > 5:
                    console.print(f"  ... and {len(warning_results) - 5} more")

            # Helpful tip for detailed inspection
            if failed > 0 or warnings > 0:
                console.print()
                log_info(
                    "TIP: Run with --verbose to see detailed reports, or validate individual file"
                )

        if failed > 0 or (strict and warnings > 0):
            raise typer.Exit(1) from None
        raise typer.Exit(0)

    else:
        log_error(f"{path} is not a file or directory")
        raise typer.Exit(1) from None
