"""Index generator command for ai-rules CLI.

Auto-generates RULES_INDEX.md from production-ready rule file metadata.
This command scans the rules/ directory, extracts metadata from rule files,
and generates a comprehensive RULES_INDEX.md table for semantic rule discovery.

Ported from scripts/index_generator.py with Rich console output.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from ai_rules._shared.console import console, log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root

# Regex patterns for metadata extraction
RE_KEYWORDS = re.compile(r"^\*\*Keywords:\*\*\s*(.*)$", re.IGNORECASE)
RE_DEPENDS = re.compile(r"^\*\*Depends:\*\*\s*(.*)$", re.IGNORECASE)
RE_TOKEN_BUDGET = re.compile(r"^\*\*TokenBudget:\*\*\s*(.*)$", re.IGNORECASE)
RE_CONTEXT_TIER = re.compile(r"^\*\*ContextTier:\*\*\s*(.*)$", re.IGNORECASE)
RE_LOAD_TRIGGER = re.compile(r"^\*\*LoadTrigger:\*\*\s*(.*)$", re.IGNORECASE)

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
    load_trigger: str | None = None  # e.g., "ext:.py, ext:.pyi, file:pyproject.toml"


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
        "load_trigger": None,
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

        elif match := RE_LOAD_TRIGGER.match(stripped):
            metadata["load_trigger"] = match.group(1).strip()

    # Extract scope from ## Scope section (v3.2 schema)
    metadata["scope"] = extract_scope_from_content(content)

    # Validate critical fields
    if not metadata["keywords"]:
        log_warning(f"{filepath.name} missing Keywords field, using empty string")

    if not metadata["scope"] or metadata["scope"] == "No scope provided":
        log_warning(f"{filepath.name} missing ## Scope section")

    # Construct with explicit field assignments for type safety
    token_budget_val = metadata["token_budget"]
    context_tier_val = metadata["context_tier"]
    load_trigger_val = metadata["load_trigger"]
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
        load_trigger=str(load_trigger_val) if load_trigger_val else None,
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
        # Skip examples directory (not rules, deployed separately)
        if "examples" in filepath.parts:
            continue

        # Extract metadata
        try:
            metadata = extract_metadata(filepath)
            rules.append(metadata)
        except ValueError as e:
            log_warning(str(e))
            continue
        except Exception as e:
            log_error(f"Error processing {filepath}: {e}")
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


def parse_load_triggers(
    rules: list[RuleMetadata],
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    """Parse LoadTrigger metadata from rules into categorized mappings.

    Args:
        rules: List of RuleMetadata objects

    Returns:
        Tuple of (dir_triggers, ext_triggers, file_triggers, kw_triggers)
        Each dict maps trigger value to rule filename
    """
    dir_triggers: dict[str, str] = {}  # dir:skills/ -> 002h-claude-code-skills.md
    ext_triggers: dict[str, str] = {}  # ext:.py -> 200-python-core.md
    file_triggers: dict[str, str] = {}  # file:Dockerfile -> 350-docker-best-practices.md
    kw_triggers: dict[str, str] = {}  # kw:test -> 206-python-pytest.md

    for rule in rules:
        if not rule.load_trigger:
            continue

        # Parse comma-separated triggers
        triggers = [t.strip() for t in rule.load_trigger.split(",")]
        for trigger in triggers:
            if trigger.startswith("dir:"):
                dir_triggers[trigger[4:]] = rule.filename
            elif trigger.startswith("ext:"):
                ext_triggers[trigger[4:]] = rule.filename
            elif trigger.startswith("file:"):
                file_triggers[trigger[5:]] = rule.filename
            elif trigger.startswith("kw:"):
                kw_triggers[trigger[3:]] = rule.filename

    return dir_triggers, ext_triggers, file_triggers, kw_triggers


def generate_loading_strategy(rules: list[RuleMetadata]) -> str:
    """Generate rule loading strategy section for AI agents.

    Dynamically builds the loading strategy from LoadTrigger metadata
    in rule files, eliminating hardcoded rule references.

    Args:
        rules: List of RuleMetadata objects with LoadTrigger field

    Returns:
        Formatted markdown section with loading algorithm
    """
    # Parse triggers from rule metadata
    dir_triggers, ext_triggers, file_triggers, kw_triggers = parse_load_triggers(rules)

    # Build directory rules section
    dir_lines = []
    for directory, rule_file in sorted(dir_triggers.items()):
        dir_lines.append(f"- `{directory}` directory: Load `{rule_file}`")
    dir_section = "\n".join(dir_lines) if dir_lines else "- (No directory-based triggers defined)"

    # Build file extension rules section (group by rule)
    # Invert: rule -> list of extensions
    rule_to_exts: dict[str, list[str]] = {}
    for ext, rule_file in ext_triggers.items():
        rule_to_exts.setdefault(rule_file, []).append(ext)
    for filename, rule_file in file_triggers.items():
        rule_to_exts.setdefault(rule_file, []).append(filename)

    ext_lines = []
    for rule_file, triggers in sorted(rule_to_exts.items()):
        trigger_list = ", ".join(f"`{t}`" for t in sorted(triggers))
        ext_lines.append(f"- {trigger_list}: Load `{rule_file}`")
    ext_section = "\n".join(ext_lines) if ext_lines else "- (No extension-based triggers defined)"

    # Build keyword rules section (group by rule)
    rule_to_kws: dict[str, list[str]] = {}
    for kw, rule_file in kw_triggers.items():
        rule_to_kws.setdefault(rule_file, []).append(kw)

    kw_lines = []
    for rule_file, keywords in sorted(rule_to_kws.items()):
        kw_list = ", ".join(f"**{kw}**" for kw in sorted(keywords))
        kw_lines.append(f"- {kw_list}: Consider `{rule_file}`")
    kw_section = "\n".join(kw_lines) if kw_lines else "- (No keyword-based triggers defined)"

    return f"""## Rule Loading Strategy

AI agents should follow this algorithm when loading rules:

### 1. Foundation (Always Load)
```
Load: 000-global-core.md
```

### 2. Domain Rules (Directory and File Extension Match)
Based on files mentioned in user request:

**Directory-based rules (check FIRST, before file extension):**
{dir_section}

**File extension and filename rules:**
{ext_section}

### 3. Activity Rules (Keyword Match)
Use `grep -i "KEYWORD" RULES_INDEX.md` to search Keywords column:
{kw_section}

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

**Token Budget:** 000 (3300) + 200 (1800) + 206 (3500) + 100 (1800) + 101 (3700) = 14,100

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
Last updated: {timestamp}

To regenerate this index:
  1. Make changes to rule files in rules/ directory
  2. Run: task index:generate
  3. Commit both rule files AND RULES_INDEX.md together

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
    loading_strategy = generate_loading_strategy(rules)

    # Generate rule catalog grouped by domain
    catalog_header = "\n## Rule Catalog\n"

    # Group rules by domain
    domains = group_rules_by_domain(rules)

    # Generate entries for each domain
    catalog_entries = []
    for domain_name, domain_rules in domains.items():
        # Domain section header
        catalog_entries.append(f"### {domain_name}")

        # Generate entry for each rule in domain
        for i, rule in enumerate(domain_rules):
            catalog_entries.append(generate_rule_entry(rule))
            # Add blank line between entries, but not after last entry in domain
            if i < len(domain_rules) - 1:
                catalog_entries.append("")

    # Combine everything
    content = (
        header
        + agent_guidance
        + loading_strategy
        + catalog_header
        + "\n".join(catalog_entries)
        + "\n"
    )

    return content


def _normalize_for_check(text: str) -> str:
    """Normalize generated content for deterministic comparisons.

    RULES_INDEX.md includes a timestamp in the auto-generated header.
    For CI checks, ignore timestamp differences so --check can be stable.

    Args:
        text: Content to normalize

    Returns:
        Normalized content with timestamp replaced
    """
    # Replace "Last updated: <timestamp>" with a stable placeholder
    normalized = re.sub(
        r"^Last updated:\s+.*$",
        "Last updated: <normalized>",
        text,
        flags=re.MULTILINE,
    )
    return normalized.strip()


def _show_diff(current: str, generated: str) -> None:
    """Show a Rich diff between current and generated content.

    Args:
        current: Current file content
        generated: Newly generated content
    """
    import difflib

    current_lines = _normalize_for_check(current).splitlines(keepends=True)
    generated_lines = _normalize_for_check(generated).splitlines(keepends=True)

    diff = list(
        difflib.unified_diff(
            current_lines,
            generated_lines,
            fromfile="current RULES_INDEX.md",
            tofile="generated RULES_INDEX.md",
            lineterm="",
        )
    )

    if not diff:
        return

    # Build styled diff output
    diff_text = Text()
    for line in diff[:100]:  # Limit to first 100 lines
        line = line.rstrip("\n")
        if line.startswith("+++") or line.startswith("---"):
            diff_text.append(line + "\n", style="bold")
        elif line.startswith("@@"):
            diff_text.append(line + "\n", style="cyan")
        elif line.startswith("+"):
            diff_text.append(line + "\n", style="green")
        elif line.startswith("-"):
            diff_text.append(line + "\n", style="red")
        else:
            diff_text.append(line + "\n")

    if len(diff) > 100:
        diff_text.append(f"\n... ({len(diff) - 100} more lines)\n", style="dim")

    console.print(Panel(diff_text, title="[bold]Diff[/bold]", border_style="yellow"))


def index(
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Check if RULES_INDEX.md is up-to-date (exit 1 if not, for CI).",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Print generated content without writing to file.",
        ),
    ] = False,
    rules_dir: Annotated[
        Path | None,
        typer.Option(
            "--rules-dir",
            help="Path to rules directory (default: rules/).",
        ),
    ] = None,
) -> None:
    """Generate RULES_INDEX.md from production-ready rule metadata.

    Scans the rules/ directory, extracts metadata from rule files,
    and generates a comprehensive index for semantic rule discovery.

    Examples:
        # Generate RULES_INDEX.md
        ai-rules index

        # Check if up-to-date (CI mode)
        ai-rules index --check

        # Preview output without writing
        ai-rules index --dry-run

        # Use custom rules directory
        ai-rules index --rules-dir custom/rules
    """
    # Auto-detect rules directory if not specified
    if rules_dir is None:
        try:
            project_root = find_project_root()
            rules_dir = project_root / "rules"
        except FileNotFoundError:
            # Fallback to current directory
            if Path("rules").exists():
                rules_dir = Path("rules")
            else:
                log_error("rules/ directory not found in current directory")
                raise typer.Exit(code=1) from None

    if not rules_dir.exists():
        log_error(f"Rules directory not found: {rules_dir}")
        raise typer.Exit(code=1) from None

    log_info(f"Using {rules_dir}/ directory")

    # Scan rules directory
    log_info(f"Scanning {rules_dir}...")
    try:
        rules = scan_rules(rules_dir)
    except Exception as e:
        log_error(f"Error scanning rules: {e}")
        raise typer.Exit(code=1) from None

    if not rules:
        log_error(f"No rule files found in {rules_dir}")
        raise typer.Exit(code=1) from None

    log_success(f"Found {len(rules)} rule files")

    # Generate content
    try:
        content = generate_rules_index(rules)
    except Exception as e:
        log_error(f"Error generating RULES_INDEX.md: {e}")
        raise typer.Exit(code=1) from None

    # Handle modes
    if dry_run:
        # Print to stdout with Rich formatting
        console.print()
        console.rule("[bold]Generated RULES_INDEX.md content[/bold]")
        console.print()
        # Show first 100 lines as preview
        lines = content.split("\n")
        preview = "\n".join(lines[:100])
        console.print(Syntax(preview, "markdown", theme="monokai", line_numbers=True))
        if len(lines) > 100:
            console.print(f"\n[dim]... ({len(lines) - 100} more lines)[/dim]")
        return

    # Determine output path (inside rules_dir, not project root)
    output_path = rules_dir / "RULES_INDEX.md"

    if check:
        # Compare with existing
        if not output_path.exists():
            log_error(f"{output_path} does not exist")
            console.print("\n[yellow]Run:[/yellow] ai-rules index")
            raise typer.Exit(code=1) from None

        try:
            current_content = output_path.read_text(encoding="utf-8")
        except Exception as e:
            log_error(f"Error reading {output_path}: {e}")
            raise typer.Exit(code=1) from None

        if _normalize_for_check(current_content) == _normalize_for_check(content):
            log_success("RULES_INDEX.md is up-to-date")
            return
        else:
            log_error("RULES_INDEX.md is out of date")
            console.print()
            _show_diff(current_content, content)
            console.print()
            console.print("[yellow]Run to update:[/yellow]")
            console.print("  ai-rules index")
            raise typer.Exit(code=1) from None

    # Write to file
    try:
        output_path.write_text(content, encoding="utf-8")
        log_success(f"Generated {output_path}")
        log_info(f"{len(rules)} rules indexed")
    except Exception as e:
        log_error(f"Error writing {output_path}: {e}")
        raise typer.Exit(code=1) from None
