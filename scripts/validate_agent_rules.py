#!/usr/bin/env python3
"""
Validate AI coding rule files against 002-rule-governance.md v5.0 standards.

This script validates that all rule files follow the required structure,
include mandatory sections, and have proper metadata.

**Boilerplate Reference:** See templates/002a-rule-boilerplate.md for canonical
structure example showing all required sections with inline commentary.

**Deep Structural Validation:** Use --check-boilerplate-structure flag to enable
programmatic validation against boilerplate template structure with 8-criteria
weighted compliance scoring (0-100%).

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

Structural Compliance Criteria (when --check-boilerplate-structure enabled):
    1. Required sections present (30% weight)
    2. Section order correct (20% weight)
    3. Metadata field order (15% weight)
    4. Contract placement before line 100 (10% weight)
    5. Required subsections present (10% weight)
    6. Optional sections appropriate (5% weight)
    7. Investigation-First Protocol present (5% weight)
    8. Anti-patterns section count (5% weight)

Usage:
    # Standard validation
    python3 scripts/validate_agent_rules.py --directory templates

    # With boilerplate structural validation
    python3 scripts/validate_agent_rules.py --directory templates --check-boilerplate-structure

    # Generate compliance reports (text, markdown, HTML)
    python3 scripts/validate_agent_rules.py --directory templates --check-boilerplate-structure --compliance-report

Exit codes:
    0: All validations passed
    1: Critical errors found (missing required sections, emojis found)
    2: Warnings found (missing recommended metadata)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# Add project root to path for imports when run as script
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.markdown_parser import MarkdownParser, SectionHierarchy  # noqa: E402


@dataclass
class ValidationIssue:
    """Enhanced validation issue with context and fix suggestions.

    Provides detailed information about validation issues including:
    - Severity level (error/warning/info)
    - Message and line number
    - Context lines around the issue
    - Fix suggestions
    - Documentation references
    """

    severity: Literal["error", "warning", "info"]
    message: str
    line_num: int | None = None
    context_lines: list[tuple[int, str]] = field(default_factory=list)
    fix_suggestion: str | None = None
    docs_reference: str | None = None
    auto_fixable: bool = False

    def format_console(self) -> str:
        """Format for terminal output with visual hierarchy.

        Returns:
            Formatted string for console display
        """
        # Severity markers
        markers = {"error": "[ERROR]", "warning": "[WARN]", "info": "[INFO]"}
        marker = markers.get(self.severity, "[INFO]")

        lines = [f"{marker} {self.message}"]

        # Add line number if available
        if self.line_num:
            lines.append(f"  at line {self.line_num}")

        # Add context if available
        if self.context_lines:
            lines.append("")
            lines.append("  Context:")
            for line_num, content in self.context_lines:
                prefix = "  >" if line_num == self.line_num else "   "
                lines.append(f"{prefix} {line_num:4d} | {content}")

        # Add fix suggestion if available
        if self.fix_suggestion:
            lines.append("")
            lines.append("  Suggested fix:")
            for fix_line in self.fix_suggestion.split("\n"):
                lines.append(f"    {fix_line}")

        # Add docs reference if available
        if self.docs_reference:
            lines.append("")
            lines.append(f"  See: {self.docs_reference}")

        return "\n".join(lines)

    def format_markdown(self) -> str:
        """Format for markdown reports.

        Returns:
            Formatted markdown string
        """
        # Severity badges
        badges = {
            "error": "🔴 **ERROR**",
            "warning": "⚠️ **WARNING**",
            "info": "**INFO**",
        }
        badge = badges.get(self.severity, "**INFO**")

        lines = [f"{badge} {self.message}"]

        if self.line_num:
            lines.append(f"- **Location:** Line {self.line_num}")

        if self.context_lines:
            lines.append("")
            lines.append("**Context:**")
            lines.append("```")
            for line_num, content in self.context_lines:
                marker = "→" if line_num == self.line_num else " "
                lines.append(f"{marker} {line_num:4d} | {content}")
            lines.append("```")

        if self.fix_suggestion:
            lines.append("")
            lines.append("**Suggested Fix:**")
            lines.append("```")
            lines.append(self.fix_suggestion)
            lines.append("```")

        if self.docs_reference:
            lines.append("")
            lines.append(f"📚 {self.docs_reference}")

        return "\n".join(lines)

    def format_json(self) -> dict:
        """Format for JSON output (CI/CD integration).

        Returns:
            Dictionary representation for JSON serialization
        """
        return {
            "severity": self.severity,
            "message": self.message,
            "line": self.line_num,
            "context": [{"line": ln, "content": c} for ln, c in self.context_lines],
            "fix_suggestion": self.fix_suggestion,
            "docs_reference": self.docs_reference,
            "auto_fixable": self.auto_fixable,
        }


# Fix suggestion templates for common validation issues
FIX_TEMPLATES = {
    "missing_purpose": """Add Purpose section at the beginning of the file:

## Purpose
[Clear 1-2 sentence description of what this rule accomplishes and why it exists]

[Optional: Additional context about the problem this rule solves]""",
    "missing_contract": """Add Contract section after Purpose and Rule Type:

## Contract

- **Inputs/Prereqs:** [What the AI needs before applying this rule]
- **Allowed Tools:** [Which tools/commands are permitted]
- **Forbidden Tools:** [What must be avoided]
- **Required Steps:**
  1. [First mandatory step]
  2. [Second mandatory step]
- **Output Format:** [Expected deliverable format]
- **Validation Steps:** [How to verify correctness]""",
    "missing_validation": """Add Validation section near the end of the file:

## Validation

**Critical Checks (Must Pass):**
- [ ] [First critical validation]
- [ ] [Second critical validation]

**Quality Checks (Should Pass):**
- [ ] [First quality check]
- [ ] [Second quality check]

**Pre-Task-Completion Validation Gate:**
- [ ] All critical checks passed
- [ ] Code compiles/runs without errors
- [ ] Tests pass (if applicable)""",
    "missing_anti_patterns": """Add Anti-Patterns section before Quick Compliance Checklist:

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: [Descriptive Name]**
```[language]
// Bad example showing what NOT to do
```
**Problem:** [Why this is wrong]
**Correct Pattern:**
```[language]
// Good example showing the right way
```
**Benefits:** [Why the correct way is better]

[Repeat for 2-4 anti-patterns]""",
    "missing_quick_start": """Add Quick Start TL;DR section after Key Principles:

## Quick Start TL;DR (Essential Patterns Reference)

**Core Pattern 1:**
```[language]
// Most common use case example
```

**Core Pattern 2:**
```[language]
// Second most common use case
```

**Common Gotchas:**
- [First common mistake to avoid]
- [Second common mistake to avoid]""",
    "contract_too_late": """Move Contract section earlier in the file.

Current location: Line {current_line}
Recommended: Before line 100 (typically after Purpose and Rule Type sections)

To fix:
1. Cut the entire Contract section (## Contract through the end of that section)
2. Paste it after "## Rule Type and Scope" section
3. Ensure it appears before detailed content sections like Quick Start or Key Principles""",
    "section_order_violation": """Reorder sections to match the required structure.

Expected section order:
1. Purpose
2. Rule Type and Scope
3. Contract
4. Key Principles
5. Quick Start TL;DR
6. [Your content sections]
7. Anti-Patterns and Common Mistakes
8. Quick Compliance Checklist
9. Validation
10. Response Template
11. References

Current issue: {details}

Sections can be omitted, but their relative order must be preserved.""",
    "metadata_order_violation": """Fix metadata field ordering.

Correct metadata order (at top of file):
1. **Keywords:**
2. **TokenBudget:**
3. **ContextTier:**
4. **Depends:**
5. [Any additional custom fields]

Current issue: {details}""",
    "missing_keywords": """Add Keywords metadata at the very top of the file:

**Keywords:** keyword1, keyword2, keyword3, keyword4, keyword5
**TokenBudget:** ~1500
**ContextTier:** Standard
**Depends:** 000-global-core

Guidelines for keywords:
- Include 8-12 keywords
- Use lowercase (except proper nouns)
- Focus on technical terms, patterns, and use cases
- Help AI assistants discover this rule based on user intent""",
}


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
    """Configuration for rule validation.

    Note: Light integration with templates/002a-rule-boilerplate.md.
    Deep structural comparison planned for future release.
    """

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

    # Boilerplate structural validation (Phase 1.3)
    check_boilerplate_structure: bool = False
    boilerplate_path: Path = None
    compliance_criteria: ComplianceCriteria = None
    generate_compliance_report: bool = False
    compliance_report_dir: Path = None

    def __post_init__(self):
        """Initialize default values for ValidationConfig."""
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

        # Initialize boilerplate validation fields (Phase 1.3)
        if self.boilerplate_path is None:
            # Default to templates/002a-rule-boilerplate.md
            self.boilerplate_path = Path("templates/002a-rule-boilerplate.md")

        if self.compliance_criteria is None:
            # Import here to avoid circular reference issues
            self.compliance_criteria = ComplianceCriteria()

        if self.compliance_report_dir is None:
            self.compliance_report_dir = Path("validation_reports")


@dataclass
class SectionDefinition:
    """Definition of a section within a rule file.

    Represents structural information about a section including its heading,
    hierarchical level, requirement status, and location within the file.
    """

    heading: str
    level: int
    required: bool
    line_range: tuple[int, int]
    subsections: list[SectionDefinition]
    metadata_fields: list[str]


@dataclass
class BoilerplateStructure:
    """Parsed structure of the canonical boilerplate template.

    Contains all structural information extracted from templates/002a-rule-boilerplate.md
    for use in deep validation comparison against rule files.
    """

    required_sections: list[SectionDefinition]
    optional_sections: list[SectionDefinition]
    metadata_order: list[str]
    max_contract_line: int
    total_lines: int
    section_hierarchy: dict[str, list[str]]


@dataclass
class BoilerplateComparisonResult:
    """Result of comparing a rule file against boilerplate structure.

    Contains detailed compliance information including violations, scoring,
    and actionable recommendations for achieving boilerplate compliance.
    """

    file_path: Path
    compliance_score: float
    critical_violations: list[str]
    warnings: list[str]
    info_messages: list[str]
    missing_required_sections: list[str]
    section_order_mismatches: list[tuple[str, int, int]]
    metadata_order_violations: list[str]
    contract_line_number: int | None
    optional_sections_present: list[str]
    recommendations: list[str]


@dataclass
class ComplianceCriteria:
    """Weighted criteria for boilerplate compliance scoring.

    Defines 8 validation criteria with weights totaling 100% for
    comprehensive structural compliance assessment.
    """

    # Criterion 1: Required sections present (30%)
    required_sections_weight: float = 0.30

    # Criterion 2: Section order correct (20%)
    section_order_weight: float = 0.20

    # Criterion 3: Metadata field order (15%)
    metadata_order_weight: float = 0.15

    # Criterion 4: Contract placement before line 100 (10%)
    contract_placement_weight: float = 0.10

    # Criterion 5: Required subsections present (10%)
    required_subsections_weight: float = 0.10

    # Criterion 6: Optional sections appropriate (5%)
    optional_sections_weight: float = 0.05

    # Criterion 7: Investigation-First Protocol present (5%)
    investigation_protocol_weight: float = 0.05

    # Criterion 8: Anti-patterns section count (5%)
    anti_patterns_weight: float = 0.05

    def __post_init__(self):
        """Validate that weights sum to 1.0 (100%)."""
        total = (
            self.required_sections_weight
            + self.section_order_weight
            + self.metadata_order_weight
            + self.contract_placement_weight
            + self.required_subsections_weight
            + self.optional_sections_weight
            + self.investigation_protocol_weight
            + self.anti_patterns_weight
        )
        if not (0.99 <= total <= 1.01):  # Allow float precision tolerance
            raise ValueError(f"Compliance criteria weights must sum to 1.0, got {total}")


class RuleValidator:
    """Validator for AI coding rule files."""

    def __init__(self, config: ValidationConfig | None = None):
        """Initialize validator with configuration."""
        self.config = config or ValidationConfig()
        self._boilerplate_cache: BoilerplateStructure | None = None

    def parse_boilerplate_structure(self) -> BoilerplateStructure:
        """Parse boilerplate template structure for validation comparison.

        Returns cached structure if available (singleton pattern for performance).

        Returns:
            BoilerplateStructure containing all structural information from
            templates/002a-rule-boilerplate.md
        """
        # Return cached structure if available
        if self._boilerplate_cache is not None:
            return self._boilerplate_cache

        boilerplate_path = self.config.boilerplate_path
        if not boilerplate_path.exists():
            raise FileNotFoundError(
                f"Boilerplate template not found at {boilerplate_path}. "
                "Cannot perform structural validation."
            )

        with open(boilerplate_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Extract section information
        required_sections = []
        optional_sections = []
        section_hierarchy = {}
        current_h2 = None

        # Metadata field order from boilerplate
        metadata_order = [
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

        # Define required vs optional sections per 002-rule-governance.md
        required_section_names = {
            "Purpose",
            "Rule Type and Scope",
            "Contract",
            "Quick Start TL;DR",
            "Anti-Patterns and Common Mistakes",
            "Quick Compliance Checklist",
            "Validation",
            "Response Template",
            "References",
        }

        for line_num, line in enumerate(lines, start=1):
            # Find ## headings
            h2_match = re.match(r"^## (.+)$", line.strip())
            if h2_match:
                heading = h2_match.group(1)
                # Remove numbering if present (e.g., "1. Purpose" -> "Purpose")
                heading_clean = re.sub(r"^\d+\.\s+", "", heading)
                heading_clean = re.sub(
                    r"\[.*?\]", "[...]", heading_clean
                ).strip()  # Normalize placeholders

                is_required = any(req in heading_clean for req in required_section_names)

                section_def = SectionDefinition(
                    heading=heading_clean,
                    level=2,
                    required=is_required,
                    line_range=(line_num, line_num),  # Will update end in full implementation
                    subsections=[],
                    metadata_fields=[],
                )

                if is_required:
                    required_sections.append(section_def)
                else:
                    optional_sections.append(section_def)

                current_h2 = heading_clean
                if current_h2 not in section_hierarchy:
                    section_hierarchy[current_h2] = []

        # Cache and return
        self._boilerplate_cache = BoilerplateStructure(
            required_sections=required_sections,
            optional_sections=optional_sections,
            metadata_order=metadata_order,
            max_contract_line=100,  # Per Section 11.3
            total_lines=len(lines),
            section_hierarchy=section_hierarchy,
        )

        return self._boilerplate_cache

    def compare_against_boilerplate(self, file_path: Path) -> BoilerplateComparisonResult:
        """Compare a rule file against boilerplate structure.

        Args:
            file_path: Path to rule file to validate

        Returns:
            BoilerplateComparisonResult with compliance scoring and detailed violations
        """
        # Parse boilerplate structure (cached)
        boilerplate = self.parse_boilerplate_structure()

        # Read target file
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Use markdown-aware parser to extract actual headers
        parser = MarkdownParser(content)
        hierarchy = SectionHierarchy(parser)
        hierarchy.build()

        # Get actual rule sections (excluding templates)
        actual_sections = hierarchy.get_actual_h2_sections()

        # Initialize result containers
        critical_violations = []
        warnings = []
        info_messages = []
        missing_required_sections = []
        section_order_mismatches = []
        metadata_order_violations = []
        optional_sections_present = []
        recommendations = []
        contract_line_number = None

        # Extract H2 sections from file (excluding code blocks, comments, and templates)
        file_sections = []
        file_section_names = set()
        for section in actual_sections:
            heading_clean = re.sub(r"^\d+\.\s+", "", section.name).strip()
            file_sections.append((heading_clean, section.line_num))
            file_section_names.add(heading_clean)

            if "Contract" in heading_clean:
                contract_line_number = section.line_num

        # Criterion 1: Check required sections present (30%)
        required_section_score = 0.0
        for req_section in boilerplate.required_sections:
            # Fuzzy match to handle variations
            found = any(
                req_section.heading.lower() in fname.lower()
                or fname.lower() in req_section.heading.lower()
                for fname in file_section_names
            )
            if found:
                required_section_score += 1.0 / len(boilerplate.required_sections)
            else:
                missing_required_sections.append(req_section.heading)
                critical_violations.append(f"Missing required section: {req_section.heading}")

        # Criterion 2: Section order correct (20%)
        section_order_score = 1.0  # Start optimistic
        expected_order = [s.heading for s in boilerplate.required_sections]
        file_order = [name for name, _ in file_sections]

        # Check relative ordering of sections that exist
        for i, exp_section in enumerate(expected_order[:-1]):
            if exp_section in file_order:
                exp_idx = file_order.index(exp_section)
                # Check if next expected section appears after current
                for next_exp in expected_order[i + 1 :]:
                    if next_exp in file_order:
                        next_idx = file_order.index(next_exp)
                        if next_idx < exp_idx:
                            section_order_score -= 0.1
                            section_order_mismatches.append((exp_section, exp_idx, next_idx))
                            warnings.append(
                                f"Section order: '{next_exp}' appears before '{exp_section}'"
                            )
                        break
        section_order_score = max(0.0, section_order_score)

        # Criterion 3: Metadata field order (15%)
        metadata_order_score = 0.0
        metadata_pattern = r"^\*\*(\w+):\*\*"
        found_metadata = []

        # Only check first 50 lines for metadata
        content_lines = content.split("\n")
        for line in content_lines[:50]:
            match = re.match(metadata_pattern, line.strip())
            if match:
                found_metadata.append(match.group(1))

        if found_metadata:
            correct_order_count = 0
            for i, field in enumerate(found_metadata[:-1]):
                if field in boilerplate.metadata_order:
                    expected_idx = boilerplate.metadata_order.index(field)
                    next_field = found_metadata[i + 1]
                    if next_field in boilerplate.metadata_order:
                        next_expected_idx = boilerplate.metadata_order.index(next_field)
                        if next_expected_idx > expected_idx:
                            correct_order_count += 1
                        else:
                            metadata_order_violations.append(f"{field} before {next_field}")
            if len(found_metadata) > 1:
                metadata_order_score = correct_order_count / (len(found_metadata) - 1)

        # Criterion 4: Contract placement before line 100 (10%)
        contract_placement_score = 0.0
        if contract_line_number:
            if contract_line_number <= boilerplate.max_contract_line:
                contract_placement_score = 1.0
                info_messages.append(
                    f"Contract section at line {contract_line_number} (before line 100 ✓)"
                )
            else:
                critical_violations.append(
                    f"Contract section at line {contract_line_number} exceeds limit of {boilerplate.max_contract_line}"
                )
                warnings.append("Contract section should appear before line 100")
        else:
            critical_violations.append("Contract section not found")

        # Criterion 5-8: Placeholder scoring (will enhance in Phase 3)
        required_subsections_score = 0.8  # Assume mostly compliant
        optional_sections_score = 0.9  # Assume mostly appropriate
        investigation_protocol_score = 1.0 if "investigation" in content.lower() else 0.0
        anti_patterns_score = 1.0 if "anti-pattern" in content.lower() else 0.5

        # Calculate weighted compliance score
        criteria = self.config.compliance_criteria
        compliance_score = (
            required_section_score * criteria.required_sections_weight
            + section_order_score * criteria.section_order_weight
            + metadata_order_score * criteria.metadata_order_weight
            + contract_placement_score * criteria.contract_placement_weight
            + required_subsections_score * criteria.required_subsections_weight
            + optional_sections_score * criteria.optional_sections_weight
            + investigation_protocol_score * criteria.investigation_protocol_weight
            + anti_patterns_score * criteria.anti_patterns_weight
        )

        # Generate recommendations
        if compliance_score < 0.80:
            recommendations.append(
                "Review templates/002a-rule-boilerplate.md for complete structure guidance"
            )
        if missing_required_sections:
            recommendations.append(f"Add missing sections: {', '.join(missing_required_sections)}")
        if metadata_order_violations:
            recommendations.append("Reorder metadata fields per boilerplate template")
        if contract_line_number and contract_line_number > 100:
            recommendations.append("Move Contract section earlier in file (before line 100)")

        return BoilerplateComparisonResult(
            file_path=file_path,
            compliance_score=compliance_score,
            critical_violations=critical_violations,
            warnings=warnings,
            info_messages=info_messages,
            missing_required_sections=missing_required_sections,
            section_order_mismatches=section_order_mismatches,
            metadata_order_violations=metadata_order_violations,
            contract_line_number=contract_line_number,
            optional_sections_present=optional_sections_present,
            recommendations=recommendations,
        )

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

    def calculate_contract_allowance(self, content: str, file_path: Path) -> int:
        """Calculate additional lines allowed for Contract placement (0-50).

        Uses graduated thresholds based on file characteristics:
        - Long keyword lists (15+ keywords): +10 lines
        - Governance/meta files: +30-50 lines
        - Extended metadata (>11 fields): +5 per extra field
        - Long Purpose section (>500 chars): +10 lines

        Args:
            content: File content to analyze
            file_path: Path to file being validated

        Returns:
            Additional lines allowed (0-50, capped)
        """
        allowance = 0

        # 1. Long keyword lists (15-20 recommended for comprehensive coverage)
        keywords_match = re.search(r"^\*\*Keywords:\*\*\s*(.+)$", content, re.MULTILINE)
        if keywords_match:
            keywords = [k.strip() for k in keywords_match.group(1).split(",")]
            if len(keywords) >= 15:
                allowance += 10  # +10 lines for comprehensive keyword coverage

        # 2. Governance/meta files get substantial allowance
        filename = file_path.name.lower()
        if "governance" in filename or "boilerplate" in filename:
            allowance += 30  # +30 lines for meta-documentation files

        # Check content for governance indicators
        if "governance" in content[:500].lower():
            allowance += 20

        # 3. Extended metadata (more than 11 standard fields)
        metadata_count = len(re.findall(r"^\*\*\w+:\*\*", content[:1000], re.MULTILINE))
        if metadata_count > 11:
            allowance += 5 * (metadata_count - 11)  # +5 per extra metadata field

        # 4. Long Purpose or Key Principles sections indicate comprehensive rules
        purpose_match = re.search(
            r"^## Purpose\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL
        )
        if purpose_match and len(purpose_match.group(1)) > 500:
            allowance += 10  # +10 for detailed purpose explanations

        # Cap total allowance at 50 lines
        return min(allowance, 50)

    def validate_contract_placement(
        self, content: str, result: ValidationResult, file_path: Path
    ) -> None:
        """Validate Contract section placement with flexible allowances.

        Graduated thresholds:
        - ≤100 lines: Perfect ✓
        - 101-150 lines: Acceptable with allowance (warning if no allowance)
        - >150 lines: Error (even with allowance)

        Args:
            content: File content
            result: ValidationResult to append issues to
            file_path: Path to file being validated
        """
        lines = content.split("\n")
        contract_line = None

        for i, line in enumerate(lines, 1):
            if re.match(r"^##\s+(?:\d+\.\s+)?Contract\b", line):
                contract_line = i
                break

        if contract_line is None:
            # Already checked in required_sections, skip here
            return

        # Calculate allowance based on file characteristics
        allowance = self.calculate_contract_allowance(content, file_path)

        # Graduated thresholds
        perfect_threshold = 100
        acceptable_threshold = 150
        adjusted_threshold = perfect_threshold + allowance

        if contract_line <= perfect_threshold:
            # Perfect placement
            return
        elif contract_line <= adjusted_threshold:
            # Acceptable with allowance - just info
            result.info_messages.append(
                f"Contract section at line {contract_line} (acceptable with +{allowance} line allowance)"
            )
        elif contract_line <= acceptable_threshold:
            # Within acceptable range but no allowance - warning
            result.warnings.append(
                f"Contract section at line {contract_line} (recommended: before line {adjusted_threshold})"
            )
        else:
            # Beyond acceptable range - error
            result.critical_errors.append(
                f"Contract section at line {contract_line} exceeds maximum of {acceptable_threshold} "
                f"(recommended: before line {perfect_threshold}, allowance: +{allowance} lines)"
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
        """Validate keywords count (10 minimum, 15-20 optimal)."""
        match = re.search(r"^\*\*Keywords:\*\*\s*(.+)$", content, re.MULTILINE)
        if not match:
            # Already checked in required_metadata
            return

        keywords = match.group(1).split(",")
        keyword_count = len([k for k in keywords if k.strip()])

        if keyword_count < 10:
            result.warnings.append(
                f"Too few keywords ({keyword_count}, minimum 10 required, optimal 15-20 for semantic discovery)"
            )
        elif keyword_count > 20:
            result.warnings.append(
                f"Too many keywords ({keyword_count}, optimal 15-20 for semantic discovery, reduces clarity above 20)"
            )
        # 10-20 keywords = PASS (no message needed)
        # Note: 15-20 is optimal range, 10-14 is acceptable

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
            if any(pattern in line for pattern in ["icon=", "st.caption", "st.expander", 'f"']):
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
                "Emojis found in machine-consumed file (PROHIBITED per v4.0 - use text-only markup instead)"
            )
            for line_num, line_content in lines_with_emojis[:5]:  # Show first 5 occurrences
                result.critical_errors.append(f"  Line {line_num}: {line_content}")
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
        self.validate_contract_placement(content, result, file_path)
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

    def generate_compliance_report_text(self, results: list[BoilerplateComparisonResult]) -> str:
        """Generate text format compliance report for console output."""
        lines = []
        lines.append("=" * 80)
        lines.append("BOILERPLATE COMPLIANCE REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary statistics
        total_files = len(results)
        avg_score = sum(r.compliance_score for r in results) / total_files if total_files > 0 else 0
        perfect_files = sum(1 for r in results if r.compliance_score >= 0.95)
        needs_work = sum(1 for r in results if r.compliance_score < 0.80)

        lines.append(f"Total Files Analyzed: {total_files}")
        lines.append(f"Average Compliance: {avg_score:.1%}")
        lines.append(f"Perfect Compliance (≥95%): {perfect_files}")
        lines.append(f"Needs Improvement (<80%): {needs_work}")
        lines.append("")
        lines.append("=" * 80)

        # Individual file results
        for result in sorted(results, key=lambda r: r.compliance_score):
            score_indicator = (
                "✓"
                if result.compliance_score >= 0.90
                else "⚠"
                if result.compliance_score >= 0.80
                else "✗"
            )
            lines.append("")
            lines.append(
                f"{score_indicator} {result.file_path.name}: {result.compliance_score:.1%}"
            )
            lines.append("-" * 80)

            if result.critical_violations:
                lines.append("  CRITICAL VIOLATIONS:")
                for violation in result.critical_violations[:5]:
                    lines.append(f"    - {violation}")

            if result.warnings and len(result.warnings) > 0:
                lines.append("  WARNINGS:")
                for warning in result.warnings[:3]:
                    lines.append(f"    - {warning}")

            if result.recommendations:
                lines.append("  RECOMMENDATIONS:")
                for rec in result.recommendations[:3]:
                    lines.append(f"    - {rec}")

        return "\n".join(lines)

    def generate_compliance_report_markdown(
        self, results: list[BoilerplateComparisonResult]
    ) -> str:
        """Generate markdown format compliance report."""
        from datetime import datetime

        lines = []
        lines.append("# Boilerplate Compliance Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        total_files = len(results)
        avg_score = sum(r.compliance_score for r in results) / total_files if total_files > 0 else 0
        perfect_files = sum(1 for r in results if r.compliance_score >= 0.95)
        needs_work = sum(1 for r in results if r.compliance_score < 0.80)

        lines.append("## Summary Statistics")
        lines.append("")
        lines.append(f"- **Total Files:** {total_files}")
        lines.append(f"- **Average Compliance:** {avg_score:.1%}")
        lines.append(f"- **Perfect Compliance (≥95%):** {perfect_files}")
        lines.append(f"- **Needs Improvement (<80%):** {needs_work}")
        lines.append("")

        # Detailed Results
        lines.append("## Detailed Results")
        lines.append("")

        for result in sorted(results, key=lambda r: r.compliance_score):
            status = (
                "🟢"
                if result.compliance_score >= 0.90
                else "🟡"
                if result.compliance_score >= 0.80
                else "🔴"
            )
            lines.append(f"### {status} {result.file_path.name}")
            lines.append("")
            lines.append(f"**Compliance Score:** {result.compliance_score:.1%}")
            lines.append("")

            if result.critical_violations:
                lines.append("**Critical Violations:**")
                for violation in result.critical_violations:
                    lines.append(f"- {violation}")
                lines.append("")

            if result.warnings:
                lines.append("**Warnings:**")
                for warning in result.warnings:
                    lines.append(f"- {warning}")
                lines.append("")

            if result.recommendations:
                lines.append("**Recommendations:**")
                for rec in result.recommendations:
                    lines.append(f"- {rec}")
                lines.append("")

        return "\n".join(lines)

    def generate_compliance_report_html(self, results: list[BoilerplateComparisonResult]) -> str:
        """Generate HTML format compliance report with dashboard."""
        from datetime import datetime

        total_files = len(results)
        avg_score = sum(r.compliance_score for r in results) / total_files if total_files > 0 else 0
        perfect_files = sum(1 for r in results if r.compliance_score >= 0.95)
        needs_work = sum(1 for r in results if r.compliance_score < 0.80)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Boilerplate Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #0066cc; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .file-result {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .file-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .score-high {{ color: #28a745; }}
        .score-medium {{ color: #ffc107; }}
        .score-low {{ color: #dc3545; }}
        .violations, .warnings, .recommendations {{ margin-top: 15px; }}
        .violations h4 {{ color: #dc3545; }}
        .warnings h4 {{ color: #ffc107; }}
        .recommendations h4 {{ color: #0066cc; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Boilerplate Compliance Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{total_files}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_score:.1%}</div>
                <div class="stat-label">Avg Compliance</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{perfect_files}</div>
                <div class="stat-label">Perfect (≥95%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{needs_work}</div>
                <div class="stat-label">Needs Work (&lt;80%)</div>
            </div>
        </div>

        <h2>Detailed Results</h2>
"""

        for result in sorted(results, key=lambda r: r.compliance_score):
            score_class = (
                "score-high"
                if result.compliance_score >= 0.90
                else "score-medium"
                if result.compliance_score >= 0.80
                else "score-low"
            )

            html += f"""
        <div class="file-result">
            <div class="file-header">
                <h3>{result.file_path.name}</h3>
                <span class="{score_class}" style="font-size: 1.5em; font-weight: bold;">{result.compliance_score:.1%}</span>
            </div>
"""

            if result.critical_violations:
                html += """
            <div class="violations">
                <h4>❌ Critical Violations</h4>
                <ul>
"""
                for violation in result.critical_violations:
                    html += f"                    <li>{violation}</li>\n"
                html += """                </ul>
            </div>
"""

            if result.warnings:
                html += """
            <div class="warnings">
                <h4>⚠️ Warnings</h4>
                <ul>
"""
                for warning in result.warnings:
                    html += f"                    <li>{warning}</li>\n"
                html += """                </ul>
            </div>
"""

            if result.recommendations:
                html += """
            <div class="recommendations">
                <h4>💡 Recommendations</h4>
                <ul>
"""
                for rec in result.recommendations:
                    html += f"                    <li>{rec}</li>\n"
                html += """                </ul>
            </div>
"""

            html += """        </div>
"""

        html += """    </div>
</body>
</html>
"""

        return html


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
    parser.add_argument(
        "--check-boilerplate-structure",
        action="store_true",
        help="Enable deep structural validation against templates/002a-rule-boilerplate.md",
    )
    parser.add_argument(
        "--boilerplate-path",
        type=Path,
        default=Path("templates/002a-rule-boilerplate.md"),
        help="Path to boilerplate template file (default: templates/002a-rule-boilerplate.md)",
    )
    parser.add_argument(
        "--compliance-report",
        action="store_true",
        help="Generate compliance report (text, markdown, HTML formats)",
    )
    parser.add_argument(
        "--compliance-report-dir",
        type=Path,
        default=Path("validation_reports"),
        help="Directory for compliance reports (default: validation_reports)",
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
    config = ValidationConfig(
        verbose=args.verbose,
        check_boilerplate_structure=args.check_boilerplate_structure,
        boilerplate_path=args.boilerplate_path,
        generate_compliance_report=args.compliance_report,
        compliance_report_dir=args.compliance_report_dir,
    )
    validator = RuleValidator(config)

    # Validate based on format
    if args.format == "universal":
        results = validator.validate_all_universal(args.directory, args.universal_dir)
    else:
        results = validator.validate_all(args.directory)

    # Print results
    validator.print_results(results)

    # Generate compliance reports if requested
    if args.check_boilerplate_structure or args.compliance_report:
        print("\n" + "=" * 80)
        print("[INFO] Running boilerplate structural validation...")
        print("=" * 80 + "\n")

        # Get rule files
        rule_files = validator.get_rule_files(args.directory)

        # Run boilerplate comparison on each file
        compliance_results = []
        for file_path in rule_files:
            try:
                comparison = validator.compare_against_boilerplate(file_path)
                compliance_results.append(comparison)
            except Exception as e:
                print(f"[ERROR] Failed to compare {file_path.name}: {e}")

        # Print text report to console
        if compliance_results:
            text_report = validator.generate_compliance_report_text(compliance_results)
            print(text_report)

            # Save reports to files if --compliance-report flag is set
            if args.compliance_report:
                from datetime import datetime

                # Create report directory
                report_dir = args.compliance_report_dir
                report_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Generate and save markdown report
                md_report = validator.generate_compliance_report_markdown(compliance_results)
                md_path = report_dir / f"compliance_report_{timestamp}.md"
                with open(md_path, "w") as f:
                    f.write(md_report)
                print(f"\n[INFO] Markdown report saved: {md_path}")

                # Generate and save HTML report
                html_report = validator.generate_compliance_report_html(compliance_results)
                html_path = report_dir / f"compliance_report_{timestamp}.html"
                with open(html_path, "w") as f:
                    f.write(html_report)
                print(f"[INFO] HTML report saved: {html_path}")

                # Create symlink to latest report
                latest_html = report_dir / "latest.html"
                if latest_html.exists():
                    latest_html.unlink()
                latest_html.symlink_to(html_path.name)
                print(f"[INFO] Latest report: {latest_html}")

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
