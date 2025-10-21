#!/usr/bin/env python3
"""
Validate AI coding rule files against 002-rule-governance.md v2.5 standards.

This script validates that all rule files follow the required structure,
include mandatory sections, and have proper metadata.

Checks for:
    - Required sections (Purpose, Contract, Validation, etc.)
    - Required metadata (Version, LastUpdated, Keywords)
    - Recommended metadata (TokenBudget, ContextTier)

Exit codes:
    0: All validations passed
    1: Critical errors found (missing required sections)
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

        return result

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
        print("\n📋 Rule Validation Report (002-rule-governance.md v2.5)")
        print("=" * 80)

        total_files = len(results)
        files_with_errors = sum(1 for r in results if r.has_errors)
        files_with_warnings = sum(1 for r in results if r.has_warnings)
        clean_files = sum(1 for r in results if r.is_clean)

        # Print summary
        print("\n📊 Summary:")
        print(f"  Total files validated: {total_files}")
        print(f"  ✅ Clean files: {clean_files}")
        print(f"  ⚠️  Files with warnings: {files_with_warnings}")
        print(f"  ❌ Files with errors: {files_with_errors}")

        # Print detailed results for files with issues
        if files_with_errors > 0 or files_with_warnings > 0:
            print("\n📝 Detailed Results:")
            print("-" * 80)

            for result in results:
                if not result.is_clean:
                    status = "❌" if result.has_errors else "⚠️ "
                    print(f"\n{status} {result.file_path.name}")

                    if result.critical_errors:
                        for error in result.critical_errors:
                            print(f"    ❌ {error}")

                    if result.warnings:
                        for warning in result.warnings:
                            print(f"    ⚠️  {warning}")

        # Print clean files if verbose
        if self.config.verbose and clean_files > 0:
            print(f"\n✅ Clean Files ({clean_files}):")
            print("-" * 80)
            for result in results:
                if result.is_clean:
                    print(f"  ✅ {result.file_path.name}")

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
        default=Path("."),
        help="Directory containing rule files (default: current directory)",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with error code if warnings are found",
    )

    args = parser.parse_args()

    # Create validator with configuration
    config = ValidationConfig(verbose=args.verbose)
    validator = RuleValidator(config)

    # Validate all files
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
        print("✅ All validations passed!")
    elif exit_code == 1:
        print("❌ Validation failed with critical errors")
    elif exit_code == 2:
        print("⚠️  Validation passed with warnings")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
