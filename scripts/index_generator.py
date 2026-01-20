#!/usr/bin/env python3
"""Auto-generate rules/RULES_INDEX.md from production-ready rule file metadata.

This script scans the rules/ directory, extracts metadata from rule files,
and generates a comprehensive rules/RULES_INDEX.md table for semantic rule discovery.

Usage:
    python scripts/index_generator.py [--check] [--dry-run] [--rules-dir DIR]

    --check: Verify current rules/RULES_INDEX.md is up-to-date (CI mode, exit 1 if not)
    --dry-run: Print generated content without writing to file
    --rules-dir: Path to rules directory (default: rules/)

Examples:
    # Generate rules/RULES_INDEX.md
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
    """Extract scope description from ## Scope section (v3.2 schema).

    Looks for the ## Scope heading and extracts content in one of two formats:
    1. v3.2 format with "What This Rule Covers:" marker
    2. Plain text format (first non-empty line after ## Scope)

    Args:
        content: Full file content

    Returns:
        Scope description string (single line) or "No scope provided"
    """
    lines = content.split("\n")

    # Find ## Scope heading
    for i, line in enumerate(lines):
        if line.strip() == "## Scope":
            # Look for content in the next 20 lines
            for j in range(i + 1, min(i + 20, len(lines))):
                current_line = lines[j].strip()

                # Check if we've reached another section
                if current_line.startswith("##") and current_line != "## Scope":
                    break

                # Skip empty lines
                if not current_line:
                    continue

                # Format 1: Found the "What This Rule Covers:" marker (v3.2 format)
                if current_line.startswith("**What This Rule Covers:**"):
                    # Extract content after the marker on same line or next line
                    content_after_marker = current_line.replace(
                        "**What This Rule Covers:**", ""
                    ).strip()
                    if content_after_marker:
                        return content_after_marker

                    # Content is on next line
                    for k in range(j + 1, min(j + 5, len(lines))):
                        next_line = lines[k].strip()
                        if (
                            next_line
                            and not next_line.startswith("**")
                            and not next_line.startswith("#")
                        ):
                            return next_line
                    break  # Marker found but no content

                # Format 2: Plain text (first non-empty line after ## Scope)
                # This is the fallback for files that don't use the marker format
                if not current_line.startswith("#"):
                    return current_line
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

    # Extract scope from ## Scope section (v3.2 schema)
    metadata["scope"] = extract_scope_from_content(content)

    # Validate critical fields
    if not metadata["keywords"]:
        print(f"⚠️  Warning: {filepath.name} missing Keywords field, using empty string")

    if not metadata["scope"] or metadata["scope"] == "No scope provided":
        print(f"⚠️  Warning: {filepath.name} missing ## Scope section")

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


def generate_rule_entry(metadata: RuleMetadata) -> str:
    """Generate structured list entry for one rule.

    Format:
    **`filename`** - Scope description
    - Keywords: keyword1, keyword2, ...
    - Depends: `dep1`, `dep2` or —

    Args:
        metadata: RuleMetadata object

    Returns:
        Formatted markdown list entry string
    """
    # Wrap filename in backticks and bold
    filename = f"**`{metadata.filename}`**"

    # Scope (extracted from ## Scope section)
    scope = metadata.scope

    # Keywords (as-is, already comma-separated)
    keywords = metadata.keywords

    # Dependencies (wrap each in backticks if not "—")
    if metadata.depends == "—":
        depends = "—"
    else:
        deps = [f"`{d.strip()}`" for d in metadata.depends.split(",")]
        depends = ", ".join(deps)

    # Build structured entry
    entry = f"{filename} - {scope}\n- Keywords: {keywords}\n- Depends: {depends}"

    return entry


def get_domain_name(prefix: str) -> str:
    """Get human-readable domain name for rule prefix.

    Args:
        prefix: Rule prefix (e.g., "000", "100", "200")

    Returns:
        Domain name string
    """
    domain_map = {
        "000": "Core Foundation (000-series)",
        "001": "Core Foundation (000-series)",
        "002": "Core Foundation (000-series)",
        "003": "Core Foundation (000-series)",
        "004": "Core Foundation (000-series)",
        "100": "Snowflake (100-series)",
        "101": "Snowflake (100-series)",
        "102": "Snowflake (100-series)",
        "103": "Snowflake (100-series)",
        "104": "Snowflake (100-series)",
        "105": "Snowflake (100-series)",
        "106": "Snowflake (100-series)",
        "107": "Snowflake (100-series)",
        "108": "Snowflake (100-series)",
        "109": "Snowflake (100-series)",
        "110": "Snowflake (100-series)",
        "111": "Snowflake (100-series)",
        "112": "Snowflake (100-series)",
        "113": "Snowflake (100-series)",
        "114": "Snowflake (100-series)",
        "115": "Snowflake (100-series)",
        "116": "Snowflake (100-series)",
        "117": "Snowflake (100-series)",
        "118": "Snowflake (100-series)",
        "119": "Snowflake (100-series)",
        "120": "Snowflake (100-series)",
        "121": "Snowflake (100-series)",
        "122": "Snowflake (100-series)",
        "123": "Snowflake (100-series)",
        "124": "Snowflake (100-series)",
        "125": "Snowflake (100-series)",
        "200": "Python (200-series)",
        "201": "Python (200-series)",
        "202": "Python (200-series)",
        "203": "Python (200-series)",
        "204": "Python (200-series)",
        "205": "Python (200-series)",
        "206": "Python (200-series)",
        "207": "Python (200-series)",
        "210": "Python (200-series)",
        "220": "Python (200-series)",
        "221": "Python (200-series)",
        "230": "Python (200-series)",
        "240": "Python (200-series)",
        "250": "Python (200-series)",
        "251": "Python (200-series)",
        "252": "Python (200-series)",
        "300": "Shell Scripting (300-series)",
        "310": "Shell Scripting (300-series)",
        "350": "Docker/Containers (300-series)",
        "420": "JavaScript/TypeScript (400-series)",
        "421": "JavaScript/TypeScript (400-series)",
        "430": "JavaScript/TypeScript (400-series)",
        "440": "React/Frontend (400-series)",
        "441": "React/Frontend (400-series)",
        "500": "Frontend/HTMX (500-series)",
        "600": "Go/Systems (600-series)",
        "800": "Project Management (800-series)",
        "801": "Project Management (800-series)",
        "802": "Project Management (800-series)",
        "803": "Project Management (800-series)",
        "820": "Project Management (800-series)",
        "900": "Demo/Analytics (900-series)",
        "901": "Demo/Analytics (900-series)",
        "920": "Demo/Analytics (900-series)",
        "930": "Demo/Analytics (900-series)",
        "940": "Demo/Analytics (900-series)",
    }
    return domain_map.get(prefix, "Other")


def group_rules_by_domain(rules: list[RuleMetadata]) -> dict[str, list[RuleMetadata]]:
    """Group rules by domain based on filename prefix.

    Args:
        rules: List of RuleMetadata objects

    Returns:
        Dictionary mapping domain names to lists of rules
    """
    from collections import OrderedDict

    # Use OrderedDict to preserve insertion order
    domains: dict[str, list[RuleMetadata]] = OrderedDict()

    for rule in rules:
        # Extract prefix (first 3 digits)
        prefix = rule.filename[:3]
        domain = get_domain_name(prefix)

        if domain not in domains:
            domains[domain] = []
        domains[domain].append(rule)

    return domains


def generate_agent_guidance() -> str:
    """Generate AI agent usage guidance section.

    Returns:
        Formatted markdown section with agent-specific instructions
    """
    return """**For AI Agents:**
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
    return """## Rule Loading Strategy

AI agents should follow this algorithm when loading rules:

### 1. Foundation (Always Load)
```
Load: 000-global-core.md
```

### 2. Domain Rules (Directory and File Extension Match)
Based on files mentioned in user request:

**Directory-based rules (check FIRST, before file extension):**
- `skills/` directory: Load `002g-claude-code-skills.md`
- `rules/` directory: Load `002-rule-governance.md`

**File extension rules:**
- `.py`, `.pyi`, `pyproject.toml`: Load `200-python-core.md`
- `.sql`: Load `100-snowflake-core.md`
- `.sh`, `.bash`, `.zsh`: Load `300-bash-scripting-core.md`
- `Dockerfile`, `docker-compose.yml`: Load `350-docker-best-practices.md`
- `.md` (outside `rules/` and `skills/`, e.g., README, CONTRIBUTING): Load `202-markup-config-validation.md`
- `.ts`, `.tsx`: Load `430-typescript-core.md`
- `.js`, `.jsx`: Load `420-javascript-core.md`
- `.go`: Load `600-golang-core.md`

### 3. Activity Rules (Keyword Match)
Use `grep -i "KEYWORD" RULES_INDEX.md` to search Keywords column:
- **skill**, SKILL.md, skill authoring: Consider `002g-claude-code-skills.md`
- **test**, pytest, coverage: Consider `206-python-pytest.md`
- **lint**, format, code quality: Consider `201-python-lint-format.md`
- **deploy**, CI/CD, automation: Consider `820-taskfile-automation.md`
- **streamlit**, dashboard: Consider `101-snowflake-streamlit-core.md`
- **docker**, container: Consider `350-docker-best-practices.md`
- **agent**, cortex agent: Consider `115-snowflake-cortex-agents-core.md`
- **semantic view**: Consider `106-snowflake-semantic-views-core.md`
- **README**, documentation: Consider `801-project-readme.md`

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
- Extension `.py`: 200-python-core.md
- Keyword "test": 206-python-pytest.md
- Keyword "Streamlit": 101-snowflake-streamlit-core.md
- Dependency check: 101 requires 100-snowflake-core.md

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
    footer = """---

## Common Rule Dependency Chains

Two representative examples demonstrating all dependency patterns. Apply these patterns to other rule combinations using the Depends field in the catalog above.

**Reading the Chains:**
- Indentation shows dependency relationships
- Token budgets shown in parentheses
- "Minimal/Standard/Complete" shows progressive loading strategies

### Example 1: Linear Chain (Streamlit Dashboard)

**`000-global-core.md`** (3300 tokens) - Foundation
- **`100-snowflake-core.md`** (2850 tokens) - Snowflake foundation
  - **`101-snowflake-streamlit-core.md`** (3700 tokens) - Streamlit core
    - **`101a-snowflake-streamlit-visualization.md`** (3600 tokens) - Visualization
    - **`101b-snowflake-streamlit-performance.md`** (5950 tokens) - Performance
    - **`101c-snowflake-streamlit-security.md`** (2550 tokens) - Security

**Token Cost Scenarios:**
- Minimal (basic app): 000 + 100 + 101 = ~9,850 tokens
- Standard (with viz): + 101a = ~13,450 tokens
- Complete (production-ready): + 101b + 101c = ~21,950 tokens

### Example 2: Multi-Branch (Cortex Agent)

**`000-global-core.md`** (3300 tokens) - Foundation
- **`100-snowflake-core.md`** (2850 tokens) - Snowflake foundation
  - **`106-snowflake-semantic-views-core.md`** (5550 tokens) - Semantic views
  - **`111-snowflake-observability-core.md`** (4200 tokens) - Observability
- **`115-snowflake-cortex-agents-core.md`** (4650 tokens) - Cortex agents
  - **`115a-snowflake-cortex-agents-instructions.md`** (3450 tokens) - Instructions
  - **`115b-snowflake-cortex-agents-operations.md`** (3650 tokens) - Operations

**Token Cost Scenarios:**
- Minimal (agent setup): 000 + 100 + 115 = ~10,800 tokens
- Standard (+ semantic): + 106 = ~16,350 tokens
- Production (+ ops): + 115b + 111 = ~24,200 tokens

**Usage Tips:**
- "Minimal" covers 70-80% of typical use cases
- Start minimal, add rules as complexity requires
- Check Depends field for prerequisites
"""
    return footer


def generate_rules_index(rules: list[RuleMetadata]) -> str:
    """Generate complete RULES_INDEX.md content.

    All content is dynamically generated - no preservation of existing content.
    Uses structured list format instead of tables for better agent comprehension.

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
Generated at: rules/RULES_INDEX.md
Last updated: {timestamp}

To regenerate this index:
  1. Make changes to rule files in rules/ directory
  2. Run: task index:generate
  3. Commit both rule files AND rules/RULES_INDEX.md together

This index provides semantic discovery for AI agents.
-->

# Rules Index

This index provides semantic rule discovery for AI agents. All rules in `rules/` are production-ready and deployment-ready.

**Filename Convention (CRITICAL):**
- All rule references in this index use **bare filenames** (e.g., `000-global-core.md`)
- All rules are located in the `rules/` directory
- **Tool Call Translation:** When loading rules, prefix with `rules/`
- Example: `Depends: 000-global-core.md` in this index requires `read_file("rules/000-global-core.md")`

**How to Use This Index:**
- Browse by domain section (Core, Snowflake, Python, Shell, etc.)
- Search Keywords field for semantic discovery (technologies, patterns, use cases)
- Check Depends field for prerequisite rules
"""

    # Generate agent guidance
    agent_guidance = generate_agent_guidance()

    # Generate loading strategy
    loading_strategy = generate_loading_strategy()

    # Generate rule catalog grouped by domain
    catalog_header = "\n## Rule Catalog\n"

    # Group rules by domain
    domains = group_rules_by_domain(rules)

    # Generate entries for each domain
    catalog_entries = []
    for domain_name, domain_rules in domains.items():
        # Domain section header (add blank line before each domain except first)
        if catalog_entries:
            catalog_entries.append("")  # Blank line before domain
        catalog_entries.append(f"### {domain_name}")
        catalog_entries.append("")  # Blank line after domain header

        # Generate entry for each rule in domain
        for i, rule in enumerate(domain_rules):
            catalog_entries.append(generate_rule_entry(rule))
            # Add blank line between entries (but not after last entry in domain)
            if i < len(domain_rules) - 1:
                catalog_entries.append("")

    # Generate footer
    footer = generate_footer()

    # Combine everything with proper spacing
    content = (
        header
        + "\n"
        + agent_guidance
        + "\n"
        + loading_strategy
        + catalog_header
        + "\n".join(catalog_entries)
        + "\n"
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
        current_path = Path("rules/RULES_INDEX.md")
        if not current_path.exists():
            print("❌ Error: rules/RULES_INDEX.md does not exist")
            print("Run: python scripts/index_generator.py")
            return 1

        try:
            current_content = current_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ Error reading rules/RULES_INDEX.md: {e}")
            return 1

        def _normalize_for_check(text: str) -> str:
            """Normalize generated content for deterministic comparisons.

            rules/RULES_INDEX.md includes a timestamp in the auto-generated header.
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
            print("✓ rules/RULES_INDEX.md is up-to-date")
            return 0
        else:
            print("❌ rules/RULES_INDEX.md is out of date")
            print("\nRun this to update:")
            print("  python scripts/index_generator.py")
            print("\nOr with task:")
            print("  task rules:index")
            return 1

    # Write to file
    output_path = Path("rules/RULES_INDEX.md")
    try:
        output_path.write_text(content, encoding="utf-8")
        print(f"✓ Generated {output_path}")
        print(f"  {len(rules)} rules indexed")
        return 0
    except Exception as e:
        print(f"❌ Error writing rules/RULES_INDEX.md: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
