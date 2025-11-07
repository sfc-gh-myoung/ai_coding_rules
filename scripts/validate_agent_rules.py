#!/usr/bin/env python3
"""
Validate AI coding rule files against 002-rule-governance.md v4.0 standards.

This script validates that all rule files follow the required structure,
include mandatory sections, and have proper metadata.

Checks for:
    - Required sections (Purpose, Contract, Validation, etc.)
    - Required metadata (Version, LastUpdated, Keywords)
    - Recommended metadata (TokenBudget, ContextTier)
    - NO emojis in machine-consumed files (v4.0 - text-only markup required)
    - Universal format validation (no YAML, no comments, metadata stripped)
    - Section 11 Universal Compatibility Standards:
        * Metadata field order
        * Quick Start TL;DR presence
        * Contract placement (early in file)
        * Investigation-First Protocol (for code/file rules)
        * Response Template completeness
        * Token budget accuracy
        * Dependencies declaration

Exit codes:
    0: All validations passed
    1: Critical errors found (missing required sections, emojis found)
    2: Warnings found (missing recommended metadata)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of validating a single rule file."""

    file_path: Path
    critical_errors: list[str]
    warnings: list[str]
    info_messages: list[str]

    @property
    def has_errors(self) -> bool:
        """Check if validation has critical errors."""
        return len(self.critical_errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0

    @property
    def is_clean(self) -> bool:
        """Check if validation is completely clean."""
        return not self.has_errors and not self.has_warnings


@dataclass
class ValidationConfig:
    """Configuration for rule validation."""

    # Files to exclude from validation
    excluded_files: set[str] = None
    # Required sections (critical - must be present)
    required_sections: list[str] = None
    # Required metadata (critical - must be present)
    required_metadata: list[str] = None
    # Recommended metadata (warning if missing)
    recommended_metadata: list[str] = None
    # Whether to show verbose output
    verbose: bool = False

    def __post_init__(self):
        """Initialize default values."""
        if self.excluded_files is None:
            self.excluded_files = {
                "README.md",
                "CHANGELOG.md",
                "CONTRIBUTING.md",
                "RULES_INDEX.md",
                "UNIVERSAL_PROMPT.md",
                "AGENTS.md",
                "EXAMPLE_PROMPT.md",
            }

        if self.required_sections is None:
            # Per 002-rule-governance.md v2.5
            # Support both numbered (## 13. Contract) and unnumbered (## Contract) sections
            self.required_sections = [
                r"^##\s+(?:\d+\.\s+)?Purpose\b",
                r"^##\s+(?:\d+\.\s+)?Rule Type and Scope\b",
                r"^##\s+(?:\d+\.\s+)?Contract\b",
                r"^##\s+(?:\d+\.\s+)?Validation\b",
                r"^##\s+(?:\d+\.\s+)?Response Template\b",
                r"^##\s+(?:\d+\.\s+)?Quick Compliance Checklist\b",
                r"^##\s+(?:\d+\.\s+)?References\b",
            ]

        if self.required_metadata is None:
            # Basic required metadata
            self.required_metadata = [
                r"^\*\*Version:\*\*",
                r"^\*\*LastUpdated:\*\*",
                r"^\*\*Keywords:\*\*",  # CRITICAL: Required for semantic discovery (promoted from recommended in v2.4)
            ]

        if self.recommended_metadata is None:
            # New in v2.1+ - recommended but not blocking
            self.recommended_metadata = [
                r"^\*\*TokenBudget:\*\*",
                r"^\*\*ContextTier:\*\*",
            ]


class RuleValidator:
    """Validator for AI coding rule files."""

    def __init__(self, config: ValidationConfig | None = None):
        """Initialize validator with configuration."""
        self.config = config or ValidationConfig()

    def get_rule_files(self, directory: Path = Path(".")) -> list[Path]:
        """Get all rule files in directory, excluding documentation files."""
        rule_files = []
        for md_file in directory.glob("*.md"):
            if md_file.name not in self.config.excluded_files:
                rule_files.append(md_file)
        return sorted(rule_files)

    def validate_metadata_field_order(self, content: str, result: ValidationResult) -> None:
        """Validate metadata field order per Section 11.1."""
        # Expected order: Description, Type, AppliesTo, AutoAttach, Keywords, TokenBudget, ContextTier, Version, LastUpdated, Depends
        expected_order = [
            "Description",
            "Type",
            "AppliesTo",
            "AutoAttach",
            "Keywords",
            "TokenBudget",
            "ContextTier",
            "Version",
            "LastUpdated",
            "Depends",
        ]

        # Extract metadata section (before first #)
        metadata_lines = []
        for line in content.split("\n"):
            if line.startswith("#"):
                break
            if line.startswith("**") and ":**" in line:
                field = line.split(":**")[0].replace("**", "")
                metadata_lines.append(field)

        # Check order
        found_positions = {}
        for i, field in enumerate(metadata_lines):
            if field in expected_order:
                found_positions[field] = i

        # Verify monotonic ordering
        prev_idx = -1
        for expected_field in expected_order:
            if expected_field in found_positions:
                current_idx = found_positions[expected_field]
                if current_idx < prev_idx:
                    result.critical_errors.append(
                        f"Metadata field order incorrect: {expected_field} should appear before previous field"
                    )
                    return
                prev_idx = current_idx

    def validate_quick_start_tldr(self, content: str, result: ValidationResult) -> None:
        """Validate Quick Start TL;DR section per Section 11.2."""
        if not re.search(r"^## Quick Start TL;DR", content, re.MULTILINE):
            result.critical_errors.append(
                "Missing Quick Start TL;DR section (MANDATORY per Section 11.2)"
            )

    def validate_contract_placement(self, content: str, result: ValidationResult) -> None:
        """Validate Contract section placement per Section 11.3."""
        lines = content.split("\n")
        contract_line = None

        for i, line in enumerate(lines, 1):
            if re.match(r"^##\s+(?:\d+\.\s+)?Contract\b", line):
                contract_line = i
                break

        if contract_line is None:
            # Already checked in required_sections, skip here
            return

        if contract_line > 100:
            result.warnings.append(
                f"Contract section appears late (line {contract_line}, should be before line 100)"
            )

    def validate_investigation_protocol(self, content: str, result: ValidationResult) -> None:
        """Validate Investigation-First Protocol per Section 11.5."""
        # Check if file references code/files
        code_indicators = [
            r"\.(py|sql|sh|js|ts|yaml|json|toml)",
            r"read_file",
            r"grep",
            r"codebase",
            r"file system",
            r"directory",
        ]

        has_code_references = any(re.search(pattern, content) for pattern in code_indicators)

        if has_code_references and not re.search(r"Investigation Required", content):
            result.critical_errors.append(
                "Missing Investigation-First Protocol (MANDATORY per Section 11.5 for code/file rules)"
                )

    def validate_response_template_completeness(
        self, content: str, result: ValidationResult
    ) -> None:
        """Validate Response Template completeness per Section 11.6."""
        # Find Response Template section
        match = re.search(
            r"^## Response Template\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL
        )
        if not match:
            # Already checked in required_sections
            return

        template_content = match.group(1)
        # Count non-empty lines
        lines = [line for line in template_content.split("\n") if line.strip()]

        if len(lines) < 5:
            result.warnings.append(
                f"Response Template appears incomplete ({len(lines)} lines, should provide complete working examples)"
            )

    def validate_token_budget_accuracy(self, content: str, result: ValidationResult) -> None:
        """Validate token budget accuracy per Section 11.9."""
        # Find TokenBudget declaration
        match = re.search(r"^\*\*TokenBudget:\*\*\s*~?(\d+)", content, re.MULTILINE)
        if not match:
            # Already checked in recommended_metadata
            return

        declared_budget = int(match.group(1))

        # Calculate estimated tokens using word count method (more accurate than line count)
        # Most tokenizers use ~0.75-1.3 tokens per word; we use 1.3 for safety margin
        word_count = len(content.split())
        estimated_tokens = int(word_count * 1.3)

        # Check if within ±30% (allow more variance due to tokenizer differences)
        lower_bound = int(declared_budget * 0.7)
        upper_bound = int(declared_budget * 1.3)

        if not (lower_bound <= estimated_tokens <= upper_bound):
            result.warnings.append(
                f"Token budget may be inaccurate (declared: ~{declared_budget}, estimated: ~{estimated_tokens}, ±30% range: {lower_bound}-{upper_bound})"
            )

    def validate_keywords_count(self, content: str, result: ValidationResult) -> None:
        """Validate keywords count (5-15 recommended)."""
        match = re.search(r"^\*\*Keywords:\*\*\s*(.+)$", content, re.MULTILINE)
        if not match:
            # Already checked in required_metadata
            return

        keywords = match.group(1).split(",")
        keyword_count = len([k for k in keywords if k.strip()])

        if keyword_count < 5:
            result.warnings.append(
                f"Few keywords ({keyword_count}, recommended 5-15 for better semantic discovery)"
            )
        elif keyword_count > 15:
            result.warnings.append(
                f"Too many keywords ({keyword_count}, recommended 5-15 for better semantic discovery)"
            )

    def validate_no_emojis(self, content: str, result: ValidationResult) -> None:
        """Validate NO emojis in machine-consumed files per 002-rule-governance.md v4.0.
        
        Per v4.0: ALL emojis are PROHIBITED in machine-consumed files (templates/, 
        AGENTS.md, RULES_INDEX.md). Use text-only markup instead.
        
        Exceptions:
        - Emojis in code examples (Python/SQL strings): icon="⚙️", st.caption("⏱️")
        - Emojis in strikethrough examples showing what NOT to do: ~~🔥 **MANDATORY:**~~
        """
        # Functional semantic marker emojis that are now PROHIBITED
        functional_emojis = r"[🔥⚠️✅❌📊🆕🚨📋]"
        
        # Find all emoji occurrences
        lines_with_emojis = []
        for i, line in enumerate(content.split("\n"), 1):
            # Skip if in code example (contains icon=, st.caption, st.expander, or similar)
            if any(pattern in line for pattern in ['icon=', 'st.caption', 'st.expander', 'f"']):
                continue
            
            # Skip if in strikethrough example (showing what NOT to do)
            if "~~" in line:
                continue
            
            # Skip if in code block (between ``` markers)
            # This is a simplified check; full parsing would track code block state
            if line.strip().startswith("```"):
                continue
                
            # Check for functional emojis
            if re.search(functional_emojis, line):
                lines_with_emojis.append((i, line.strip()[:80]))  # Truncate long lines
        
        if lines_with_emojis:
            result.critical_errors.append(
                f"Emojis found in machine-consumed file (PROHIBITED per v4.0 - use text-only markup instead)"
            )
            for line_num, line_content in lines_with_emojis[:5]:  # Show first 5 occurrences
                result.critical_errors.append(
                    f"  Line {line_num}: {line_content}"
                )
            if len(lines_with_emojis) > 5:
                result.critical_errors.append(
                    f"  ... and {len(lines_with_emojis) - 5} more occurrence(s)"
                )

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single rule file."""
        result = ValidationResult(
            file_path=file_path,
            critical_errors=[],
            warnings=[],
            info_messages=[],
        )

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result.critical_errors.append(f"Failed to read file: {e}")
            return result

        # Check required sections
        for section_pattern in self.config.required_sections:
            if not re.search(section_pattern, content, re.MULTILINE):
                section_name = section_pattern.replace(r"^## ", "").replace(r"\b", "")
                result.critical_errors.append(f"Missing required section: {section_name}")

        # Check required metadata
        for metadata_pattern in self.config.required_metadata:
            if not re.search(metadata_pattern, content, re.MULTILINE):
                field_name = metadata_pattern.replace(r"^\*\*", "").replace(r":\*\*", "")
                result.critical_errors.append(f"Missing required metadata: {field_name}")

        # Check recommended metadata (warnings only)
        for metadata_pattern in self.config.recommended_metadata:
            if not re.search(metadata_pattern, content, re.MULTILINE):
                field_name = metadata_pattern.replace(r"^\*\*", "").replace(r":\*\*", "")
                result.warnings.append(f"Missing recommended metadata: {field_name}")

        # Section 11 Universal Compatibility Checks
        self.validate_metadata_field_order(content, result)
        self.validate_quick_start_tldr(content, result)
        self.validate_contract_placement(content, result)
        self.validate_investigation_protocol(content, result)
        self.validate_response_template_completeness(content, result)
        self.validate_token_budget_accuracy(content, result)
        self.validate_keywords_count(content, result)
        
        # v4.0: Check for prohibited emojis in machine-consumed files
        self.validate_no_emojis(content, result)

        return result

    def validate_universal_output(
        self, source_file: Path, universal_dir: Path = Path("rules")
    ) -> ValidationResult:
        """Validate a universal format output file.

        Checks that:
        - File exists in universal directory
        - No YAML frontmatter (doesn't start with ---)
        - No generated HTML comments
        - Metadata lines are stripped
        """
        result = ValidationResult(
            file_path=source_file,
            critical_errors=[],
            warnings=[],
            info_messages=[],
        )

        # Check if universal output exists
        universal_file = universal_dir / source_file.name
        if not universal_file.exists():
            result.critical_errors.append(f"Universal output not found: {universal_file}")
            return result

        try:
            content = universal_file.read_text(encoding="utf-8")
        except Exception as e:
            result.critical_errors.append(f"Failed to read universal file: {e}")
            return result

        # Check for YAML frontmatter
        if content.startswith("---\n"):
            result.critical_errors.append("Universal file contains YAML frontmatter")

        # Check for generated HTML comments
        if "<!-- Generated for" in content:
            result.critical_errors.append("Universal file contains generated HTML comments")

        # Check for metadata lines that should be stripped
        # Note: Keywords, TokenBudget, ContextTier, and Depends are preserved in universal format
        # as they are universally useful for semantic discovery, attention budget, prioritization, and dependency resolution
        metadata_patterns = [
            r"^\*\*Description:\*\*",
            r"^\*\*AutoAttach:\*\*",
            r"^\*\*AppliesTo:\*\*",
            r"^\*\*Version:\*\*",
            r"^\*\*LastUpdated:\*\*",
            r"^\*\*Type:\*\*",
        ]
        for pattern in metadata_patterns:
            if re.search(pattern, content, re.MULTILINE):
                field_name = pattern.replace(r"^\*\*", "").replace(r":\*\*", "")
                result.critical_errors.append(
                    f"Universal file contains metadata line: {field_name}"
                )

        if not result.critical_errors:
            result.info_messages.append("Universal format validation passed")

        return result

    def validate_all_universal(
        self, directory: Path = Path("."), universal_dir: Path = Path("rules")
    ) -> list[ValidationResult]:
        """Validate all universal format output files."""
        rule_files = self.get_rule_files(directory)
        results = []

        for rule_file in rule_files:
            result = self.validate_universal_output(rule_file, universal_dir)
            results.append(result)

        return results

    def validate_all(self, directory: Path = Path(".")) -> list[ValidationResult]:
        """Validate all rule files in directory."""
        rule_files = self.get_rule_files(directory)
        results = []

        for rule_file in rule_files:
            result = self.validate_file(rule_file)
            results.append(result)

        return results

    def print_results(self, results: list[ValidationResult]) -> None:
        """Print validation results with colored output."""
        print("\nRule Validation Report (002-rule-governance.md v4.0)")
        print("Including Section 11: Universal Compatibility Standards")
        print("v4.0: Text-only markup required - NO emojis in machine-consumed files")
        print("=" * 80)

        total_files = len(results)
        files_with_errors = sum(1 for r in results if r.has_errors)
        files_with_warnings = sum(1 for r in results if r.has_warnings)
        clean_files = sum(1 for r in results if r.is_clean)

        # Print summary
        print("\nSummary:")
        print(f"  Total files validated: {total_files}")
        print(f"  [PASS] Clean files: {clean_files}")
        print(f"  [WARN] Files with warnings: {files_with_warnings}")
        print(f"  [FAIL] Files with errors: {files_with_errors}")

        # Print detailed results for files with issues
        if files_with_errors > 0 or files_with_warnings > 0:
            print("\nDetailed Results:")
            print("-" * 80)

            for result in results:
                if not result.is_clean:
                    status = "[FAIL]" if result.has_errors else "[WARN]"
                    print(f"\n{status} {result.file_path.name}")

                    if result.critical_errors:
                        for error in result.critical_errors:
                            print(f"    [ERROR] {error}")

                    if result.warnings:
                        for warning in result.warnings:
                            print(f"    [WARN] {warning}")

        # Print clean files if verbose
        if self.config.verbose and clean_files > 0:
            print(f"\n[PASS] Clean Files ({clean_files}):")
            print("-" * 80)
            for result in results:
                if result.is_clean:
                    print(f"  [PASS] {result.file_path.name}")

        print("\n" + "=" * 80)

    def get_exit_code(self, results: list[ValidationResult]) -> int:
        """Determine exit code based on validation results."""
        has_errors = any(r.has_errors for r in results)
        has_warnings = any(r.has_warnings for r in results)

        if has_errors:
            return 1  # Critical errors
        elif has_warnings:
            return 2  # Warnings only
        else:
            return 0  # All clean


def main() -> int:
    """Main entry point for validation script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate AI coding rule files against governance standards"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output including clean files",
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        default=None,
        help="Directory containing rule files (auto-detects: templates/ > current directory)",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with error code if warnings are found",
    )
    parser.add_argument(
        "--format",
        choices=["source", "universal"],
        default="source",
        help="Validation mode: source (validate .md files) or universal (validate rules/ output)",
    )
    parser.add_argument(
        "--universal-dir",
        type=Path,
        default=Path("generated/universal"),
        help="Directory containing universal format rules (default: generated/universal)",
    )

    args = parser.parse_args()

    # Auto-detect directory if not specified
    if args.directory is None:
        if Path("templates").exists() and list(Path("templates").glob("*.md")):
            args.directory = Path("templates")
            print("[INFO] Using source directory: templates/ (new structure)")
        else:
            args.directory = Path(".")
            print("[INFO] Using source directory: . (current directory)")

    # Create validator with configuration
    config = ValidationConfig(verbose=args.verbose)
    validator = RuleValidator(config)

    # Validate based on format
    if args.format == "universal":
        results = validator.validate_all_universal(args.directory, args.universal_dir)
    else:
        results = validator.validate_all(args.directory)

    # Print results
    validator.print_results(results)

    # Determine exit code
    exit_code = validator.get_exit_code(results)

    # Override exit code if --fail-on-warnings is set
    if args.fail_on_warnings and exit_code == 2:
        exit_code = 1

    # Print final status
    if exit_code == 0:
        print("[PASS] All validations passed!")
    elif exit_code == 1:
        print("[FAIL] Validation failed with critical errors")
    elif exit_code == 2:
        print("[WARN] Validation passed with warnings")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
