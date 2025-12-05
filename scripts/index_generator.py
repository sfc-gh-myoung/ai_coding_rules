#!/usr/bin/env python3
"""Auto-generate project root RULES_INDEX.md from production-ready rule file metadata.

This script scans the rules/ directory, extracts metadata from rule files,
and generates a comprehensive RULES_INDEX.md table for semantic rule discovery
in the project root.

Usage:
    python scripts/index_generator.py [--check] [--dry-run] [--rules-dir DIR]

    --check: Verify current RULES_INDEX.md is up-to-date (CI mode, exit 1 if not)
    --dry-run: Print generated content without writing to file
    --rules-dir: Path to rules directory (default: rules/)

Examples:
    # Generate RULES_INDEX.md in project root
    python scripts/index_generator.py

    # Check if up-to-date (CI mode)
    python scripts/index_generator.py --check

    # Preview output without writing
    python scripts/index_generator.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Regex patterns for metadata extraction
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
    "RULES_INDEX.md",
}


@dataclass
class RuleMetadata:
    """Extracted metadata from a production-ready rule file."""

    filename: str  # e.g., "000-global-core.md"
    filepath: Path  # Full path to rule file
    keywords: str  # Comma-separated keywords
    depends: str  # Dependencies or "—" if None
    scope: str  # Extracted from ## Rule Scope section

    # Optional (for future use)
    token_budget: str | None = None
    context_tier: str | None = None


def extract_scope_from_content(content: str) -> str:
    """Extract scope description from ## Rule Scope section.

    Looks for the ## Rule Scope heading and extracts the next non-empty line.

    Args:
        content: Full file content

    Returns:
        Scope description string (single line) or "No scope provided"
    """
    lines = content.split("\n")

    # Find ## Rule Scope heading
    for i, line in enumerate(lines):
        if line.strip() == "## Rule Scope":
            # Extract next non-empty line
            for j in range(i + 1, min(i + 10, len(lines))):
                scope_line = lines[j].strip()
                if scope_line and not scope_line.startswith("#"):
                    return scope_line
            break

    return "No scope provided"


def extract_metadata(filepath: Path) -> RuleMetadata:
    """Extract metadata from a single template file.

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
        raise ValueError(f"Failed to read {filepath}: {e}") from e

    lines = content.split("\n")

    # Initialize metadata with defaults
    metadata = {
        "filename": filepath.name,
        "filepath": filepath,
        "keywords": "",
        "depends": "—",
        "token_budget": None,
        "context_tier": None,
        "scope": "",
    }

    # Parse metadata lines (scan first 30 lines to be safe)
    for line in lines[:30]:
        stripped = line.strip()

        if match := RE_KEYWORDS.match(stripped):
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

    # Extract scope from ## Rule Scope section
    metadata["scope"] = extract_scope_from_content(content)

    # Validate critical fields
    if not metadata["keywords"]:
        print(f"⚠️  Warning: {filepath.name} missing Keywords field, using empty string")

    if not metadata["scope"] or metadata["scope"] == "No scope provided":
        print(f"⚠️  Warning: {filepath.name} missing ## Rule Scope section")

    return RuleMetadata(**metadata)


def scan_rules(rules_dir: Path) -> list[RuleMetadata]:
    """Recursively scan rules/ directory for rule files.

    Walks the directory tree, finds all .md files, extracts metadata,
    and returns sorted list of rule metadata objects.

    Args:
        rules_dir: Path to rules directory

    Returns:
        List of RuleMetadata objects, sorted by filename
    """
    rules = []

    # Walk directory tree
    for filepath in sorted(rules_dir.rglob("*.md")):
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
    """Generate markdown table row for one rule.

    Format: || `file` | Scope | Keywords | Depends ||

    Args:
        metadata: RuleMetadata object

    Returns:
        Formatted markdown table row string
    """
    # Wrap filename in backticks
    filename = f"`{metadata.filename}`"

    # Scope (extracted from ## Rule Scope section)
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
    row = f"|| {filename} | {scope} | {keywords} | {depends} |"

    return row


def generate_footer() -> str:
    """Generate footer section with rule dependency chains.

    Returns:
        Formatted footer content with dependency visualization
    """
    footer = """

---

## Common Rule Dependency Chains

This section visualizes common rule loading patterns to help AI assistants calculate token costs and load rules in the correct order.

**Reading the Trees:**
- Indentation shows dependency relationships
- Token budgets shown in parentheses
- "Minimal/Standard/Complete" shows progressive loading strategies
- Always load parent rules before child rules

### Streamlit Dashboard Development
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    └── 101-snowflake-streamlit-core (3700 tokens)
        ├── 101a-snowflake-streamlit-visualization (3600 tokens)
        ├── 101b-snowflake-streamlit-performance (3800 tokens)
        └── 101c-snowflake-streamlit-security (2550 tokens)

Token Cost Scenarios:
• Minimal (basic app):        000 + 100 + 101      = ~6,800 tokens
• Standard (with viz):         + 101a               = ~10,400 tokens
• Performance (caching):       + 101b               = ~14,200 tokens
• Complete (production-ready): + 101c               = ~16,750 tokens
```

### Cortex Agent Development
```
000-global-core (1300 tokens)
├── 100-snowflake-core (1800 tokens)
│   ├── 106-snowflake-semantic-views-core (2800 tokens)
│   │   ├── 106a-snowflake-semantic-views-advanced (2200 tokens)
│   │   └── 106b-snowflake-semantic-views-querying (5000 tokens)
│   └── 111-snowflake-observability-core (2000 tokens)
│       ├── 111a-snowflake-observability-logging (varies)
│       └── 111c-snowflake-observability-monitoring (varies)
└── 115-snowflake-cortex-agents-core (2200 tokens)
    ├── 115a-snowflake-cortex-agents-instructions (800 tokens)
    └── 115b-snowflake-cortex-agents-operations (2400 tokens)

Token Cost Scenarios:
• Minimal (agent setup):         000 + 100 + 115           = ~5,300 tokens
• Standard (with semantic views): + 106                     = ~8,100 tokens
• Advanced (instructions):        + 115a                    = ~8,900 tokens
• Production (operations):        + 115b + 111             = ~13,300 tokens
• Complete (all capabilities):    + 106a + 106b            = ~20,500 tokens
```

### Cortex Analyst Integration
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    └── 106-snowflake-semantic-views-core (2800 tokens)
        ├── 106a-snowflake-semantic-views-advanced (2200 tokens)
        ├── 106b-snowflake-semantic-views-querying (5000 tokens)
        └── 106c-snowflake-semantic-views-integration (4600 tokens)

Token Cost Scenarios:
• Minimal (basic analyst):    000 + 100 + 106       = ~5,900 tokens
• Standard (with queries):    + 106b                 = ~10,900 tokens
• With integration:           + 106c                 = ~15,500 tokens
• Complete (full capability): + 106a                 = ~17,700 tokens
```

### Performance Tuning Workflow
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 103-snowflake-performance-tuning (800 tokens)
    ├── 105-snowflake-cost-governance (1150 tokens)
    └── 119-snowflake-warehouse-management (3650 tokens)

Token Cost Scenarios:
• Minimal (query optimization):  000 + 100 + 103      = ~3,900 tokens
• Standard (with warehouses):    + 119                 = ~7,550 tokens
• Complete (cost governance):    + 105                 = ~8,700 tokens
```

### Data Pipeline Development
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 104-snowflake-streams-tasks (850 tokens)
    │   └── 122-snowflake-dynamic-tables (5200 tokens)
    ├── 108-snowflake-data-loading (950 tokens)
    └── 124-snowflake-data-quality-core (6200 tokens)

Token Cost Scenarios:
• Minimal (basic CDC):           000 + 100 + 104     = ~3,950 tokens
• With dynamic tables:           + 122                = ~9,150 tokens
• With data loading:             + 108                = ~10,100 tokens
• Complete (with quality):       + 124                = ~16,300 tokens
```

### Cortex Search Implementation
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 116-snowflake-cortex-search (4000 tokens)
    ├── 108-snowflake-data-loading (950 tokens)
    └── 115-snowflake-cortex-agents-core (2200 tokens)
        └── 115b-snowflake-cortex-agents-operations (2400 tokens)

Token Cost Scenarios:
• Minimal (search setup):        000 + 100 + 116     = ~7,100 tokens
• With document loading:         + 108                = ~8,050 tokens
• Agent integration:             + 115                = ~10,250 tokens
• Complete (operations):         + 115b               = ~12,650 tokens
```

### SPCS Container Deployment
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 120-snowflake-spcs (3550 tokens)
    ├── 119-snowflake-warehouse-management (3650 tokens)
    └── 111-snowflake-observability-core (2000 tokens)
        ├── 111a-snowflake-observability-logging (varies)
        └── 111c-snowflake-observability-monitoring (varies)

Token Cost Scenarios:
• Minimal (basic SPCS):          000 + 100 + 120     = ~6,650 tokens
• With compute pools:            + 119                = ~10,300 tokens
• Complete (observability):      + 111                = ~12,300 tokens
```

**Usage Tips:**
- Load only what you need based on task complexity
- "Minimal" scenarios cover 70-80% of typical use cases
- "Standard" adds commonly needed extensions
- "Complete" for production-ready, comprehensive implementations
- If unsure, start with Minimal and load additional rules as needed
"""
    return footer


def generate_rules_index(rules: list[RuleMetadata]) -> str:
    """Generate complete RULES_INDEX.md content.

    All content is dynamically generated - no preservation of existing content.

    Args:
        rules: List of RuleMetadata objects

    Returns:
        Complete RULES_INDEX.md content as string
    """
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate header with AUTO-GENERATED notice
    header = f"""<!--
╔══════════════════════════════════════════════════════════════════════════╗
║                           AUTO-GENERATED FILE                             ║
║                    DO NOT EDIT THIS FILE MANUALLY                         ║
╚══════════════════════════════════════════════════════════════════════════╝

Generated by: scripts/index_generator.py
Last updated: {timestamp}

To regenerate this index:
  1. Make changes to rule files in rules/ directory
  2. Run: task index:generate
  3. Commit both rule files AND RULES_INDEX.md together

This index provides semantic discovery for AI agents.
-->

# Rules Index

This index provides semantic rule discovery for AI agents. All rules in `rules/` are production-ready and deployment-ready.

**How to Use This Index:**
- Browse by category (000=Core, 100=Snowflake, 200=Python, 300=Shell, 400=Docker, 500-900=Domain-specific)
- Search Keywords column for semantic discovery (technologies, patterns, use cases)
- Check Depends On column for prerequisite rules
"""

    # Generate table
    table_header = "|| File | Scope | Keywords/Hints | Depends On |"
    table_separator = "||------|-------|----------------|------------|"

    table_rows = [generate_table_row(rule) for rule in rules]

    # Generate footer
    footer = generate_footer()

    # Combine everything (header + table + footer)
    content = (
        header
        + "\n\n"
        + table_header
        + "\n"
        + table_separator
        + "\n"
        + "\n".join(table_rows)
        + footer
    )

    return content


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 = success, 1 = error/check failed)
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Auto-generate RULES_INDEX.md from production-ready rule metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/index_generator.py                 # Generate RULES_INDEX.md in project root
  python scripts/index_generator.py --check         # Check if up-to-date (CI)
  python scripts/index_generator.py --dry-run       # Preview output
  python scripts/index_generator.py --rules-dir custom/rules
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
        "--rules-dir",
        type=Path,
        default=None,
        help="Path to rules directory (default: rules/)",
    )

    args = parser.parse_args()

    # Auto-detect rules directory if not specified
    if args.rules_dir is None:
        if Path("rules").exists():
            args.rules_dir = Path("rules")
            print("📁 Using rules/ directory")
        else:
            print("❌ Error: rules/ directory not found in current directory")
            return 1
    else:
        if not args.rules_dir.exists():
            print(f"❌ Error: Rules directory not found: {args.rules_dir}")
            return 1

    # Scan rules directory
    print(f"🔍 Scanning {args.rules_dir}...")
    try:
        rules = scan_rules(args.rules_dir)
    except Exception as e:
        print(f"❌ Error scanning rules: {e}")
        return 1

    if not rules:
        print(f"❌ Error: No rule files found in {args.rules_dir}")
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
            print("Run: python scripts/index_generator.py")
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
            print("  python scripts/index_generator.py")
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
