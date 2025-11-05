#!/usr/bin/env python3
"""
Auto-generate RULES_INDEX.md from template file metadata.

This script scans the templates/ directory (or project root for legacy support),
extracts metadata from rule files, and generates a comprehensive RULES_INDEX.md
table for semantic rule discovery.

Usage:
    python scripts/build_rules_index.py [--check] [--dry-run] [--templates-dir DIR]
    
    --check: Verify current RULES_INDEX.md is up-to-date (CI mode, exit 1 if not)
    --dry-run: Print generated content without writing to file
    --templates-dir: Path to templates directory (default: templates/ or . for legacy)

Examples:
    # Generate RULES_INDEX.md
    python scripts/build_rules_index.py
    
    # Check if up-to-date (CI mode)
    python scripts/build_rules_index.py --check
    
    # Preview output without writing
    python scripts/build_rules_index.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Regex patterns for metadata extraction
RE_DESCRIPTION = re.compile(r"^\*\*Description:\*\*\s*(.*)$", re.IGNORECASE)
RE_TYPE = re.compile(r"^\*\*Type:\*\*\s*(.*)$", re.IGNORECASE)
RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.*)$", re.IGNORECASE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.*)$", re.IGNORECASE)
RE_TOKEN_BUDGET = re.compile(r"^\*\*TokenBudget:\*\*\s*(.*)$", re.IGNORECASE)
RE_CONTEXT_TIER = re.compile(r"^\*\*ContextTier:\*\*\s*(.*)$", re.IGNORECASE)

# Files to skip during scanning
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "AGENTS_V2.md",
    "EXAMPLE_PROMPT.md",
    "RULES_INDEX.md",
}


@dataclass
class RuleMetadata:
    """Extracted metadata from a rule template file."""

    filename: str  # e.g., "000-global-core.md"
    filepath: Path  # Full path to template
    description: str  # One-line purpose
    type: str  # "Auto-attach" or "Agent Requested"
    keywords: str  # Comma-separated keywords
    depends: str  # Dependencies or "—" if None
    scope: str  # Manually provided or inferred

    # Optional (for future use)
    token_budget: Optional[str] = None
    context_tier: Optional[str] = None


def infer_scope(filename: str) -> str:
    """
    Infer scope category from filename prefix.
    
    Maps rule number prefixes to scope descriptions for the Scope column.
    
    Args:
        filename: Rule filename (e.g., "000-global-core.md")
        
    Returns:
        Scope description string
    """
    # Extract prefix (e.g., "000" from "000-global-core.md")
    prefix = filename.split("-")[0] if "-" in filename else filename[:3]

    scope_map = {
        "000": "Universal",
        "001": "Project continuity",
        "002": "All rules",
        "003": "Universal context engineering",
        "004": "Agent tool development",
        "100": "Snowflake SQL & modeling",
        "101": "Streamlit apps",
        "102": "Demo SQL",
        "103": "Performance",
        "104": "Pipelines",
        "105": "Cost governance",
        "106": "Modeling",
        "107": "Security",
        "108": "Ingestion",
        "109": "Notebooks",
        "110": "ML registry",
        "111": "Observability",
        "112": "Snowflake CLI",
        "113": "Feature Store",
        "114": "AISQL",
        "119": "Warehouse management",
        "120": "SPCS",
        "121": "Snowpipe",
        "122": "Dynamic Tables",
        "123": "Object tagging",
        "124": "Data quality",
        "200": "Python core",
        "201": "Linting",
        "202": "Config validation",
        "203": "Project setup",
        "204": "Documentation",
        "205": "Classes",
        "206": "Testing",
        "210": "FastAPI",
        "220": "CLI",
        "230": "Validation",
        "240": "Data generation",
        "250": "Flask",
        "251": "Datetime",
        "252": "Pandas",
        "300": "Bash",
        "310": "Zsh",
        "400": "Docker",
        "500": "Analytics",
        "600": "Governance",
        "700": "BI",
        "800": "Changelog",
        "801": "README",
        "805": "Contributing",
        "806": "Git workflow",
        "820": "Automation",
        "900": "Demo",
        "901": "Data generation",
    }

    return scope_map.get(prefix, "General")


def extract_metadata(filepath: Path) -> RuleMetadata:
    """
    Extract metadata from a single template file.
    
    Parses the first ~20 lines of the file looking for metadata fields
    like **Keywords:**, **Type:**, **Description:**, etc.
    
    Args:
        filepath: Path to template file
        
    Returns:
        RuleMetadata object with extracted information
        
    Raises:
        ValueError: If critical metadata fields are missing
    """
    # Read file
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        raise ValueError(f"Failed to read {filepath}: {e}")

    lines = content.split("\n")

    # Initialize metadata with defaults
    metadata = {
        "filename": filepath.name,
        "filepath": filepath,
        "description": "",
        "type": "Agent Requested",  # Default type
        "keywords": "",
        "depends": "—",
        "token_budget": None,
        "context_tier": None,
    }

    # Parse metadata lines (scan first 30 lines to be safe)
    for line in lines[:30]:
        stripped = line.strip()

        if match := RE_DESCRIPTION.match(stripped):
            metadata["description"] = match.group(1).strip()

        elif match := RE_TYPE.match(stripped):
            metadata["type"] = match.group(1).strip()

        elif match := RE_KEYWORDS.match(stripped):
            metadata["keywords"] = match.group(1).strip()

        elif match := RE_DEPENDS.match(stripped):
            depends_val = match.group(1).strip()
            if depends_val.lower() in ["none", "—", "", "n/a"]:
                metadata["depends"] = "—"
            else:
                # Ensure .md extension on dependencies
                deps = [d.strip() for d in depends_val.split(",")]
                deps = [d if d.endswith(".md") else f"{d}.md" for d in deps]
                metadata["depends"] = ", ".join(deps)

        elif match := RE_TOKEN_BUDGET.match(stripped):
            metadata["token_budget"] = match.group(1).strip()

        elif match := RE_CONTEXT_TIER.match(stripped):
            metadata["context_tier"] = match.group(1).strip()

    # Infer scope from filename
    metadata["scope"] = infer_scope(filepath.name)

    # Validate critical fields
    if not metadata["keywords"]:
        print(f"⚠️  Warning: {filepath.name} missing Keywords field, using empty string")

    if not metadata["description"]:
        print(f"⚠️  Warning: {filepath.name} missing Description field")
        metadata["description"] = "No description provided"

    if not metadata["type"]:
        print(f"⚠️  Warning: {filepath.name} missing Type field, defaulting to 'Agent Requested'")

    return RuleMetadata(**metadata)


def scan_templates(templates_dir: Path) -> list[RuleMetadata]:
    """
    Recursively scan templates/ directory for rule files.
    
    Walks the directory tree, finds all .md files, extracts metadata,
    and returns sorted list of rule metadata objects.
    
    Args:
        templates_dir: Path to templates directory
        
    Returns:
        List of RuleMetadata objects, sorted by filename
    """
    rules = []

    # Walk directory tree
    for filepath in sorted(templates_dir.rglob("*.md")):
        # Skip documentation and discovery files
        if filepath.name in SKIP_FILES:
            continue

        # Extract metadata
        try:
            metadata = extract_metadata(filepath)
            rules.append(metadata)
        except ValueError as e:
            print(f"⚠️  Warning: {e}")
            continue
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            continue

    # Sort by filename (ensures 000, 001, 100, 101a, etc. order)
    rules.sort(key=lambda r: r.filename)

    return rules


def generate_table_row(metadata: RuleMetadata) -> str:
    """
    Generate markdown table row for one rule.
    
    Format: || `file` | Type | Purpose | Scope | Keywords | Depends ||
    
    Args:
        metadata: RuleMetadata object
        
    Returns:
        Formatted markdown table row string
    """
    # Wrap filename in backticks
    filename = f"`{metadata.filename}`"

    # Type as-is
    type_str = metadata.type

    # Description (first sentence only if multiple, ensure ends with period)
    purpose = metadata.description.split(".")[0].strip()
    if purpose and not purpose.endswith("."):
        purpose += "."

    # Scope (inferred from filename)
    scope = metadata.scope

    # Keywords (as-is, already comma-separated)
    keywords = metadata.keywords

    # Dependencies (wrap each in backticks if not "—")
    if metadata.depends == "—":
        depends = "—"
    else:
        deps = [f"`{d.strip()}`" for d in metadata.depends.split(",")]
        depends = ", ".join(deps)

    # Build row
    row = f"|| {filename} | {type_str} | {purpose} | {scope} | {keywords} | {depends} |"

    return row


def generate_rules_index(rules: list[RuleMetadata], preserve_header: bool = True) -> str:
    """
    Generate complete RULES_INDEX.md content.
    
    Preserves the manual header section (if preserve_header=True) and
    generates the table section from rule metadata.
    
    Args:
        rules: List of RuleMetadata objects
        preserve_header: Whether to preserve existing header (default True)
        
    Returns:
        Complete RULES_INDEX.md content as string
    """
    # Try to read current RULES_INDEX.md to preserve header
    current_index_path = Path("RULES_INDEX.md")
    header = ""

    if preserve_header and current_index_path.exists():
        try:
            current_content = current_index_path.read_text(encoding="utf-8")

            # Find table start (line with "|| File | Type |")
            lines = current_content.split("\n")
            header_lines = []

            for i, line in enumerate(lines):
                if line.startswith("|| File | Type |"):
                    # Found table header, keep everything before this
                    header_lines = lines[:i]
                    break

            # Reconstruct header (preserve everything including blank lines)
            if header_lines:
                header = "\n".join(header_lines).rstrip() + "\n\n"
        except Exception as e:
            print(f"⚠️  Warning: Could not read existing header from RULES_INDEX.md: {e}")
            # Fall through to default header

    # If no header found or couldn't read, create default
    if not header:
        header = """**Keywords:** rules index, rule discovery, semantic search, agent requested, auto-attach, rule governance, context engineering, tool design

# Rules Index

This index helps agents select the correct rule quickly through semantic keyword matching.

**How to Use This Index:**
- Browse by category (000=Core, 100=Snowflake, 200=Python, 300=Shell, 400=Docker, 500-900=Domain-specific)
- Search Keywords column for semantic discovery (technologies, patterns, use cases)
- Check Depends On column for prerequisite rules
- Auto-attach rules load automatically; Agent Requested rules load on-demand

"""

    # Generate table
    table_header = "|| File | Type | Purpose (one line) | Scope | Keywords/Hints | Depends On |"
    table_separator = "||------|------|---------------------|-------|----------------|------------|"

    table_rows = [generate_table_row(rule) for rule in rules]

    # Combine everything
    content = header + table_header + "\n" + table_separator + "\n" + "\n".join(table_rows) + "\n"

    return content


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 = success, 1 = error/check failed)
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Auto-generate RULES_INDEX.md from template metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_rules_index.py                 # Generate RULES_INDEX.md
  python scripts/build_rules_index.py --check         # Check if up-to-date (CI)
  python scripts/build_rules_index.py --dry-run       # Preview output
  python scripts/build_rules_index.py --templates-dir src/templates
        """,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if RULES_INDEX.md is up-to-date (exit 1 if not, for CI)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated content without writing to file",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=None,
        help="Path to templates directory (default: auto-detect templates/ or .)",
    )

    args = parser.parse_args()

    # Auto-detect templates directory if not specified
    if args.templates_dir is None:
        if Path("templates").exists():
            args.templates_dir = Path("templates")
            print("📁 Using templates/ directory")
        else:
            args.templates_dir = Path(".")
            print("📁 Using current directory (legacy mode)")
    else:
        if not args.templates_dir.exists():
            print(f"❌ Error: Templates directory not found: {args.templates_dir}")
            return 1

    # Scan templates
    print(f"🔍 Scanning {args.templates_dir}...")
    try:
        rules = scan_templates(args.templates_dir)
    except Exception as e:
        print(f"❌ Error scanning templates: {e}")
        return 1

    if not rules:
        print(f"❌ Error: No rule files found in {args.templates_dir}")
        return 1

    print(f"✓ Found {len(rules)} rule files")

    # Generate content
    try:
        content = generate_rules_index(rules)
    except Exception as e:
        print(f"❌ Error generating RULES_INDEX.md: {e}")
        return 1

    # Handle modes
    if args.dry_run:
        # Print to stdout
        print("\n" + "=" * 70)
        print("Generated RULES_INDEX.md content:")
        print("=" * 70 + "\n")
        print(content)
        return 0

    if args.check:
        # Compare with existing
        current_path = Path("RULES_INDEX.md")
        if not current_path.exists():
            print("❌ Error: RULES_INDEX.md does not exist")
            print("Run: python scripts/build_rules_index.py")
            return 1

        try:
            current_content = current_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ Error reading RULES_INDEX.md: {e}")
            return 1

        if current_content.strip() == content.strip():
            print("✓ RULES_INDEX.md is up-to-date")
            return 0
        else:
            print("❌ RULES_INDEX.md is out of date")
            print("\nRun this to update:")
            print("  python scripts/build_rules_index.py")
            print("\nOr with task:")
            print("  task rules:index")
            return 1

    # Write to file
    output_path = Path("RULES_INDEX.md")
    try:
        output_path.write_text(content, encoding="utf-8")
        print(f"✓ Generated {output_path}")
        print(f"  {len(rules)} rules indexed")
        return 0
    except Exception as e:
        print(f"❌ Error writing RULES_INDEX.md: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

