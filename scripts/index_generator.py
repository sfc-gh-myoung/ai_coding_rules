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

    # Construct with explicit field assignments for type safety
    token_budget_val = metadata["token_budget"]
    context_tier_val = metadata["context_tier"]
    return RuleMetadata(
        filename=str(metadata["filename"]),
        filepath=Path(metadata["filepath"])
        if isinstance(metadata["filepath"], str | Path)
        else filepath,
        keywords=str(metadata["keywords"] or ""),
        depends=str(metadata["depends"] or "—"),
        scope=str(metadata["scope"] or ""),
        token_budget=str(token_budget_val) if token_budget_val else None,
        context_tier=str(context_tier_val) if context_tier_val else None,
    )


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

    Format: | `file` | Scope | Keywords | Depends |

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
    row = f"| {filename} | {scope} | {keywords} | {depends} |"

    return row


def generate_agent_guidance() -> str:
    """Generate AI agent usage guidance section.

    Returns:
        Formatted markdown section with agent-specific instructions
    """
    return """

**For AI Agents:**
- This file is **READ-ONLY** for rule discovery purposes
- Use `grep`, `read_file`, or codebase_search to find relevant rules
- **Never modify** this file during task execution
- Regeneration happens automatically via `task index:generate`
- To suggest improvements, modify source rule files or `scripts/index_generator.py`

"""


def generate_loading_strategy() -> str:
    """Generate rule loading strategy section for AI agents.

    Returns:
        Formatted markdown section with loading algorithm
    """
    return """
## Rule Loading Strategy

AI agents should follow this algorithm when loading rules:

### 1. Foundation (Always Load)
```
Load: rules/000-global-core.md
```

### 2. Domain Rules (File Extension Match)
Based on files mentioned in user request:
- `.py`, `.pyi`, `pyproject.toml` → Load `rules/200-python-core.md`
- `.sql` → Load `rules/100-snowflake-core.md`
- `.sh`, `.bash`, `.zsh` → Load `rules/300-bash-scripting-core.md`
- `Dockerfile`, `docker-compose.yml` → Load `rules/350-docker-best-practices.md`
- `.md` (in `rules/`) → Load `rules/002-rule-governance.md`
- `.md` (outside `rules/`, e.g., README, CONTRIBUTING) → Load `rules/202-markup-config-validation.md`
- `.ts`, `.tsx` → Load `rules/430-typescript-core.md`
- `.js`, `.jsx` → Load `rules/420-javascript-core.md`
- `.go` → Load `rules/600-golang-core.md`

### 3. Activity Rules (Keyword Match)
Use `grep -i "KEYWORD" RULES_INDEX.md` to search Keywords column:
- **test**, pytest, coverage → Consider `rules/206-python-pytest.md`
- **lint**, format, code quality → Consider `rules/201-python-lint-format.md`
- **deploy**, CI/CD, automation → Consider `rules/820-taskfile-automation.md`
- **streamlit**, dashboard → Consider `rules/101-snowflake-streamlit-core.md`
- **docker**, container → Consider `rules/350-docker-best-practices.md`
- **agent**, cortex agent → Consider `rules/115-snowflake-cortex-agents-core.md`
- **semantic view** → Consider `rules/106-snowflake-semantic-views-core.md`

### 4. Check Dependencies
- For each rule to be loaded, read its **Depends On** column
- Load all prerequisite rules first (in dependency order)
- If rule lists multiple dependencies, load all of them

### 5. Token Budget Management
**Progressive Loading Strategy:**
- **Minimal**: Foundation + Domain = ~3,000-5,000 tokens (covers 70-80% of tasks)
- **Standard**: + 1-2 activity-specific rules = ~8,000-12,000 tokens
- **Complete**: + specialized rules = ~15,000-20,000 tokens

**Token Budget Check:**

**Warning Threshold:** At 15,000 tokens, begin deferring Low-tier rules and evaluate Medium-tier necessity.

**Example - At 17,000 tokens:**
```
Loaded (Critical/High):
- 000-global-core.md, 200-python-core.md, 206-python-pytest.md

Deferred (Medium/Low - available if needed):
- 204-python-docs-comments.md (not required for test execution)
```

If total exceeds 20,000 tokens, prioritize by ContextTier:
1. Critical (always load)
2. High (load if directly relevant)
3. Medium (defer unless task complexity requires)
4. Low (load only if explicitly needed)

**Token Budget Enforcement:**
- Agent self-regulates token budget (no external enforcement)
- At 15,000 tokens: Log warning, begin deferring Low/Medium tier rules
- At 20,000 tokens: STOP loading additional rules, proceed with loaded rules only

**Deferral Priority (when at warning threshold):**
1. Defer all Low tier rules first
2. Defer Medium tier rules not directly related to task keywords
3. Never defer Critical tier rules

**Declaration Format (when deferring):**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- [Deferred: 204-python-docs-comments.md - Low tier, not required for task]
```

### 6. Declare Loaded Rules
After loading, list all rules in response:
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/206-python-pytest.md (keyword: test)
```

**Example Workflow:**

User: "Write tests for my Streamlit dashboard"

**Rule Selection:**
- Extension `.py` → rules/200-python-core.md
- Keyword "test" → rules/206-python-pytest.md
- Keyword "Streamlit" → rules/101-snowflake-streamlit-core.md
- Dependency check: 101 requires rules/100-snowflake-core.md

**Token Budget:** 000 (3300) + 200 (1800) + 206 (3500) + 100 (1800) + 101 (3700) = 14,100 ✓

**Declaration:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
```

"""


def generate_footer() -> str:
    """Generate footer section with rule dependency chains.

    Returns:
        Formatted footer content with dependency visualization
    """
    footer = """

---

## Common Rule Dependency Chains

Two representative examples demonstrating all dependency patterns. Apply these patterns to other rule combinations using the Depends On column in the table above.

**Reading the Trees:**
- Indentation shows dependency relationships
- Token budgets shown in parentheses
- "Minimal/Standard/Complete" shows progressive loading strategies

### Example 1: Linear Chain (Streamlit Dashboard)
```
000-global-core (3300 tokens)
└── 100-snowflake-core (2850 tokens)
    └── 101-snowflake-streamlit-core (3700 tokens)
        ├── 101a-snowflake-streamlit-visualization (3600 tokens)
        ├── 101b-snowflake-streamlit-performance (5950 tokens)
        └── 101c-snowflake-streamlit-security (2550 tokens)

Token Cost Scenarios:
• Minimal (basic app):        000 + 100 + 101      = ~9,850 tokens
• Standard (with viz):         + 101a               = ~13,450 tokens
• Complete (production-ready): + 101b + 101c        = ~21,950 tokens
```

### Example 2: Multi-Branch (Cortex Agent)
```
000-global-core (3300 tokens)
├── 100-snowflake-core (2850 tokens)
│   ├── 106-snowflake-semantic-views-core (5550 tokens)
│   └── 111-snowflake-observability-core (4200 tokens)
└── 115-snowflake-cortex-agents-core (4650 tokens)
    ├── 115a-snowflake-cortex-agents-instructions (3450 tokens)
    └── 115b-snowflake-cortex-agents-operations (3650 tokens)

Token Cost Scenarios:
• Minimal (agent setup):    000 + 100 + 115        = ~10,800 tokens
• Standard (+ semantic):    + 106                   = ~16,350 tokens
• Production (+ ops):       + 115b + 111           = ~24,200 tokens
```

**Usage Tips:**
- "Minimal" covers 70-80% of typical use cases
- Start minimal, add rules as complexity requires
- Check Depends On column for prerequisites
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

    # Generate agent guidance
    agent_guidance = generate_agent_guidance()

    # Generate loading strategy
    loading_strategy = generate_loading_strategy()

    # Generate table
    table_header = "| File | Scope | Keywords/Hints | Depends On |"
    table_separator = "|------|-------|----------------|------------|"

    table_rows = [generate_table_row(rule) for rule in rules]

    # Generate footer
    footer = generate_footer()

    # Combine everything (header + agent_guidance + loading_strategy + table + footer)
    content = (
        header
        + agent_guidance
        + loading_strategy
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

        def _normalize_for_check(text: str) -> str:
            """Normalize generated content for deterministic comparisons.

            RULES_INDEX.md includes a timestamp in the auto-generated header.
            For CI checks, ignore timestamp differences so --check can be stable.
            """
            # Replace "Last updated: <timestamp>" with a stable placeholder
            normalized = re.sub(
                r"^Last updated:\s+.*$",
                "Last updated: <normalized>",
                text,
                flags=re.MULTILINE,
            )
            return normalized.strip()

        if _normalize_for_check(current_content) == _normalize_for_check(content):
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
