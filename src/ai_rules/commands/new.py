"""Generate rule file templates compliant with v3.2 schema.

This module provides the `ai-rules new` command to create new rule files
with all required sections and placeholders, making it easier for users
to create rules that pass schema validation.
"""

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, ClassVar

import typer
from rich.panel import Panel

from ai_rules._shared.console import console, err_console, log_error, log_success

app = typer.Typer(help="Create new rule file templates.")


class TemplateGenerator:
    """Generate v3.2 compliant rule file templates."""

    TEMPLATE = """# {title}

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** {last_updated}
**Keywords:** {keywords}
**TokenBudget:** ~1200
**ContextTier:** {context_tier}
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
[1-2 sentence description of what this rule accomplishes and why it matters]

**When to Load This Rule:**
- [Context 1 when this rule should be loaded]
- [Context 2 when this rule should be loaded]
- [Context 3 when this rule should be loaded]

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns

**Recommended:**
- [Optional related rules that enhance this rule]

**Related:**
- [Other rules that may be relevant]

### External Documentation

**Official Documentation:**
- [Link description](https://example.com) - Brief explanation of resource

**Best Practices Guides:**
- [Link description](https://example.com) - Brief explanation of resource

## Contract

### Inputs and Prerequisites

- [What the agent needs to have/know before starting this task]
- [Required environment, tools, or access]
- [Expected initial state]

### Mandatory

- [Required tools, libraries, permissions, access]
- [Must-follow patterns or conventions]
- [Critical requirements that cannot be skipped]

### Forbidden

- [Prohibited actions, tools, or approaches]
- [Anti-patterns to avoid]
- [Security or safety restrictions]

### Execution Steps

1. [First required step]
2. [Second required step]
3. [Third required step]
4. [Fourth required step]
5. [Fifth required step]

### Output Format

[Description of expected output format (file type, structure, content)]

```bash
# Example command
[command here]

# Expected output:
[output here]
```

```[language]
# Example code output
[code example here]
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** Before marking any task as complete, ALL of the following checks MUST pass:

**Code Quality:**
- **CRITICAL:** [Validation command 1] - Must pass with zero errors
- **CRITICAL:** [Validation command 2] - Must pass with zero errors

**Success Criteria:**
- [How to verify rule compliance]
- [Specific commands or tools to run]
- [Expected outcomes]

**Investigation Required:**
1. [What to check before making recommendations]
2. [How to verify project structure]
3. [What patterns to look for]

### Design Principles

- **[Principle 1]:** [Description of design principle]
- **[Principle 2]:** [Description of design principle]
- **[Principle 3]:** [Description of design principle]

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] [First prerequisite check]
- [ ] [Second prerequisite check]

**After Completion:**
- [ ] **CRITICAL:** [First verification item]
- [ ] **CRITICAL:** [Second verification item]
- [ ] [Third verification item]
- [ ] [Fourth verification item]
- [ ] [Fifth verification item]

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: [Name of anti-pattern]

```[language]
# Bad: [Code example showing the wrong way]
[code here]
```

**Problem:** [Explanation of why this is problematic]

**Correct Pattern:**
```[language]
# Good: [Code example showing the right way]
[code here]
```

**Benefits:** [Explanation of why the correct pattern is better]

### Anti-Pattern 2: [Name of anti-pattern]

```[language]
# Bad: [Code example showing the wrong way]
[code here]
```

**Problem:** [Explanation of why this is problematic]

**Correct Pattern:**
```[language]
# Good: [Code example showing the right way]
[code here]
```

**Benefits:** [Explanation of why the correct pattern is better]

### Anti-Pattern 3: [Name of anti-pattern]

```[language]
# Bad: [Code example showing the wrong way]
[code here]
```

**Problem:** [Explanation of why this is problematic]

**Correct Pattern:**
```[language]
# Good: [Code example showing the right way]
[code here]
```

**Benefits:** [Explanation of why the correct pattern is better]
"""

    # Numbering ranges and their default keywords
    RANGE_KEYWORDS: ClassVar[dict[tuple[int, int], str]] = {
        (0, 99): "core, framework, foundation, standards, conventions",
        (100, 199): "snowflake, data platform, warehouse, SQL, analytics",
        (200, 299): "programming, language, development, coding, best practices",
        (300, 399): "framework, library, web development, frontend, backend",
        (400, 499): "testing, quality assurance, validation, test automation",
        (500, 599): "security, authentication, authorization, encryption, compliance",
        (600, 699): "data pipeline, ETL, data engineering, processing",
        (700, 799): "machine learning, ML ops, model training, deployment",
        (800, 899): "documentation, project management, workflow, collaboration",
        (900, 999): "demo, example, sample, tutorial, reference",
    }

    @staticmethod
    def parse_rule_filename(filename: str) -> tuple[int, str, str]:
        """Parse rule filename to extract number and generate title.

        Args:
            filename: Rule filename (e.g., "100-snowflake-sql" or "111a-snowflake-feature")

        Returns:
            Tuple of (number, slug, title)

        Raises:
            ValueError: If filename format is invalid
        """
        # Remove .md extension if present
        filename = filename.replace(".md", "")

        # Match pattern: NNN-technology-aspect or NNNx-technology-aspect (where x is a-z)
        match = re.match(r"^(\d{3})([a-z])?-([a-z0-9]+(?:-[a-z0-9]+)*)$", filename)
        if not match:
            raise ValueError(
                f"Invalid filename format: {filename}\n"
                "Expected format: NNN-technology-aspect (e.g., 100-snowflake-sql) "
                "or NNNx-technology-aspect (e.g., 111a-snowflake-feature)"
            )

        number = int(match.group(1))
        letter_suffix = match.group(2) or ""  # Optional letter suffix (a-z)
        slug = match.group(3)

        # Generate title from slug
        title_parts = slug.split("-")
        title = " ".join(word.capitalize() for word in title_parts)
        # Reconstruct the filename prefix (e.g., "111a" or "100")
        prefix = f"{match.group(1)}{letter_suffix}"
        full_title = f"{prefix}-{slug}: {title}"

        return number, slug, full_title

    @classmethod
    def get_default_keywords(cls, number: int, slug: str) -> str:
        """Get default keywords based on rule number range.

        Args:
            number: Rule number (e.g., 100)
            slug: Rule slug (e.g., "snowflake-sql")

        Returns:
            Comma-separated keyword string (5-20 keywords per v3.2 schema)
        """
        # Find matching range
        range_keywords = ""
        for (start, end), keywords in cls.RANGE_KEYWORDS.items():
            if start <= number <= end:
                range_keywords = keywords
                break

        if not range_keywords:
            range_keywords = "custom, specialized, advanced, specific, targeted"

        # Extract keywords from slug
        slug_keywords = ", ".join(slug.split("-"))

        # Combine range and slug keywords
        all_keywords = f"{slug_keywords}, {range_keywords}"

        # Split, deduplicate, and count
        keyword_list = [kw.strip() for kw in all_keywords.split(",")]
        keyword_list = list(dict.fromkeys(keyword_list))  # Remove duplicates, preserve order

        # Ensure we have 5-20 keywords (v3.2 schema requirement)
        if len(keyword_list) < 5:
            # Add filler keywords
            fillers = [
                "implementation",
                "best practices",
                "patterns",
                "guidelines",
                "optimization",
            ]
            keyword_list.extend(fillers[: 5 - len(keyword_list)])

        keyword_list = keyword_list[:20]  # Cap at 20

        return ", ".join(keyword_list)

    @classmethod
    def generate_template(
        cls,
        filename: str,
        context_tier: str = "Medium",
        keywords: str | None = None,
    ) -> str:
        """Generate a rule template.

        Args:
            filename: Rule filename (e.g., "100-snowflake-sql")
            context_tier: Context tier (Critical/High/Medium/Low)
            keywords: Optional custom keywords (otherwise auto-generated)

        Returns:
            Generated template content
        """
        number, slug, title = cls.parse_rule_filename(filename)

        # Validate context tier
        valid_tiers = ["Critical", "High", "Medium", "Low"]
        if context_tier not in valid_tiers:
            raise ValueError(f"Context tier must be one of: {', '.join(valid_tiers)}")

        # Generate or use provided keywords
        if keywords is None:
            keywords = cls.get_default_keywords(number, slug)
        else:
            # Validate keyword count (v3.2: 5-20 keywords)
            keyword_list = [kw.strip() for kw in keywords.split(",")]
            if len(keyword_list) < 5 or len(keyword_list) > 20:
                raise ValueError(f"Keywords must contain 5-20 terms, got {len(keyword_list)}")

        # Get current date in UTC for LastUpdated field
        last_updated = datetime.now(UTC).strftime("%Y-%m-%d")

        return cls.TEMPLATE.format(
            title=title,
            keywords=keywords,
            context_tier=context_tier,
            last_updated=last_updated,
        )

    @classmethod
    def create_rule_file(
        cls,
        filename: str,
        output_dir: Path,
        context_tier: str = "Medium",
        keywords: str | None = None,
        force: bool = False,
    ) -> Path:
        """Create a new rule file from template.

        Args:
            filename: Rule filename (without .md extension)
            output_dir: Directory to create the file in
            context_tier: Context tier (Critical/High/Medium/Low)
            keywords: Optional custom keywords
            force: Overwrite existing file if True

        Returns:
            Path to created file

        Raises:
            FileExistsError: If file exists and force=False
        """
        # Ensure filename has .md extension
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        output_path = output_dir / filename

        # Check if file exists
        if output_path.exists() and not force:
            raise FileExistsError(
                f"Rule file already exists: {output_path}\nUse --force to overwrite"
            )

        # Generate template
        template_content = cls.generate_template(
            filename, context_tier=context_tier, keywords=keywords
        )

        # Write to file
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template_content, encoding="utf-8")

        return output_path

    @staticmethod
    def format_success_message(output_path: Path) -> str:
        """Format success message for CLI output.

        Args:
            output_path: Path to created rule file

        Returns:
            Formatted success message with next steps
        """
        return (
            f"✅ Created rule template: {output_path}\n"
            "\nNext steps:\n"
            f"1. Edit {output_path} and replace all placeholders with actual content\n"
            f"2. Validate: python scripts/schema_validator.py {output_path}\n"
            "3. Add to rules/RULES_INDEX.md"
        )

    @staticmethod
    def format_error_message(error: Exception) -> str:
        """Format error message for CLI output.

        Args:
            error: Exception that occurred

        Returns:
            Formatted error message
        """
        return f"❌ Error: {error}"


# Valid context tier choices
CONTEXT_TIERS = ["Critical", "High", "Medium", "Low"]


@app.command()
def new(
    ctx: typer.Context,
    filename: Annotated[
        str | None,
        typer.Argument(
            help="Rule filename (e.g., 100-snowflake-sql, 111a-snowflake-feature)",
            show_default=False,
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Output directory for the rule file.",
        ),
    ] = Path("rules"),
    context_tier: Annotated[
        str,
        typer.Option(
            "--context-tier",
            "-t",
            help="Context tier for the rule (Critical/High/Medium/Low).",
        ),
    ] = "Medium",
    keywords: Annotated[
        str | None,
        typer.Option(
            "--keywords",
            "-k",
            help="Custom comma-separated keywords (5-20 terms per v3.2 schema).",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing file.",
        ),
    ] = False,
) -> None:
    """Create a new rule file from a v3.2 compliant template.

    Examples:
        # Create a Snowflake rule
        ai-rules new 100-snowflake-example

        # Create a Python rule with custom tier
        ai-rules new 200-python-example --context-tier High

        # Create a rule with custom keywords (5-20 terms per v3.2 schema)
        ai-rules new 300-react-hooks --keywords "react, hooks, state, effects, custom hooks, lifecycle, functional components, useState, useEffect, optimization"

        # Overwrite existing file
        ai-rules new 100-example --force
    """
    if filename is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Validate context tier
    if context_tier not in CONTEXT_TIERS:
        log_error(f"Invalid context tier: {context_tier}")
        err_console.print(f"  Must be one of: {', '.join(CONTEXT_TIERS)}")
        raise typer.Exit(1)

    try:
        output_path = TemplateGenerator.create_rule_file(
            filename=filename,
            output_dir=output_dir,
            context_tier=context_tier,
            keywords=keywords,
            force=force,
        )

        # Show success panel with summary
        # Parse filename to get metadata for summary
        try:
            number, slug, _title = TemplateGenerator.parse_rule_filename(filename)
            actual_keywords = (
                keywords if keywords else TemplateGenerator.get_default_keywords(number, slug)
            )
        except ValueError:
            actual_keywords = keywords or "auto-generated"

        summary = (
            f"[bold green]File:[/bold green] {output_path}\n"
            f"[bold green]Context Tier:[/bold green] {context_tier}\n"
            f"[bold green]Keywords:[/bold green] {actual_keywords}"
        )

        console.print(
            Panel(summary, title="[bold]Generated Rule Template[/bold]", border_style="green")
        )

        log_success(f"Created rule template: {output_path}")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print(
            f"  1. Edit [cyan]{output_path}[/cyan] and replace all placeholders with actual content"
        )
        console.print(f"  2. Validate: [cyan]ai-rules validate {output_path}[/cyan]")
        console.print("  3. Add to [cyan]rules/RULES_INDEX.md[/cyan]")

    except (ValueError, FileExistsError) as e:
        log_error(str(e))
        raise typer.Exit(1) from None
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        raise typer.Exit(1) from None
