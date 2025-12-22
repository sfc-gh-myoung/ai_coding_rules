#!/usr/bin/env python3
"""Generate rule file templates compliant with v3.0 schema.

This script creates new rule files with all required sections and placeholders,
making it easier for users to create rules that pass schema validation.

Usage:
    python scripts/template_generator.py 100-snowflake-example
    python scripts/template_generator.py 200-python-example --output-dir custom/
    python scripts/template_generator.py 300-react-example --context-tier High
"""

import argparse
import re
import sys
from pathlib import Path
from typing import ClassVar


class TemplateGenerator:
    """Generate v3.0 compliant rule file templates."""

    TEMPLATE = """# {title}

## Metadata

**SchemaVersion:** v3.0
**Keywords:** {keywords}
**TokenBudget:** ~1200
**ContextTier:** {context_tier}
**Depends:** rules/000-global-core.md

## Purpose

[1-2 sentence description of what this rule accomplishes and why it matters]

## Rule Scope

[Single line defining what contexts this rule applies to]

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1]:** [Description of first essential pattern]
- **[Pattern 2]:** [Description of second essential pattern]
- **[Pattern 3]:** [Description of third essential pattern]

**Pre-Execution Checklist:**
- [ ] [First prerequisite check]
- [ ] [Second prerequisite check]
- [ ] [Third prerequisite check]
- [ ] [Fourth prerequisite check]
- [ ] [Fifth prerequisite check]

## Contract

<inputs_prereqs>
[What the agent needs to have/know before starting this task]
</inputs_prereqs>

<mandatory>
[Required tools, libraries, permissions, access]
</mandatory>

<forbidden>
[Prohibited actions, tools, or approaches]
</forbidden>

<steps>
1. [First required step]
2. [Second required step]
3. [Third required step]
4. [Fourth required step]
5. [Fifth required step]
</steps>

<output_format>
[Description of expected output format (file type, structure, content)]
</output_format>

<validation>
[How to verify success - specific checks agent should run]
</validation>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: [Name of anti-pattern]**
```[language]
[Code example showing the wrong way]
```
**Problem:** [Explanation of why this is problematic]

**Correct Pattern:**
```[language]
[Code example showing the right way]
```
**Benefits:** [Explanation of why the correct pattern is better]

**Anti-Pattern 2: [Name of anti-pattern]**
```[language]
[Code example showing the wrong way]
```
**Problem:** [Explanation of why this is problematic]

**Correct Pattern:**
```[language]
[Code example showing the right way]
```
**Benefits:** [Explanation of why the correct pattern is better]

## Post-Execution Checklist

- [ ] [First verification item]
- [ ] [Second verification item]
- [ ] [Third verification item]
- [ ] [Fourth verification item]
- [ ] [Fifth verification item]

## Validation

**Success Checks:**
- [How to verify rule compliance]
- [Specific commands or tools to run]
- [Expected outcomes]

**Negative Tests:**
- [What should fail and how to detect it]
- [Edge cases to verify]

## Output Format Examples

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

## References

### Related Rules
- `rules/000-global-core.md` - Global standards and conventions

### External Documentation
- [Link description](https://example.com) - Brief explanation of resource
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
            Comma-separated keyword string (10-15 keywords)
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

        # Ensure we have 10-15 keywords
        if len(keyword_list) < 10:
            # Add filler keywords
            fillers = [
                "implementation",
                "best practices",
                "patterns",
                "guidelines",
                "optimization",
            ]
            keyword_list.extend(fillers[: 10 - len(keyword_list)])

        keyword_list = keyword_list[:15]  # Cap at 15

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
            # Validate keyword count
            keyword_list = [kw.strip() for kw in keywords.split(",")]
            if len(keyword_list) < 10 or len(keyword_list) > 15:
                raise ValueError(f"Keywords must contain 10-15 terms, got {len(keyword_list)}")

        return cls.TEMPLATE.format(
            title=title,
            keywords=keywords,
            context_tier=context_tier,
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
            "3. Add to RULES_INDEX.md"
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


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate v3.0 compliant rule file templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a Snowflake rule
  python scripts/template_generator.py 100-snowflake-example

  # Create a Python rule with custom tier
  python scripts/template_generator.py 200-python-example --context-tier High

  # Create a rule with custom keywords
  python scripts/template_generator.py 300-react-hooks --keywords "react, hooks, state, effects, custom hooks, lifecycle, functional components, useState, useEffect, optimization, performance, patterns, best practices, debugging, testing"

  # Overwrite existing file
  python scripts/template_generator.py 100-example --force
        """,
    )

    parser.add_argument(
        "filename",
        help="Rule filename (e.g., 100-snowflake-sql, 111a-snowflake-feature, or with .md extension)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("rules"),
        help="Output directory (default: rules/)",
    )
    parser.add_argument(
        "--context-tier",
        choices=["Critical", "High", "Medium", "Low"],
        default="Medium",
        help="Context tier for the rule (default: Medium)",
    )
    parser.add_argument(
        "--keywords",
        help="Custom comma-separated keywords (10-15 terms)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing file",
    )

    args = parser.parse_args()

    try:
        output_path = TemplateGenerator.create_rule_file(
            filename=args.filename,
            output_dir=args.output_dir,
            context_tier=args.context_tier,
            keywords=args.keywords,
            force=args.force,
        )

        print(TemplateGenerator.format_success_message(output_path))
        return 0

    except (ValueError, FileExistsError) as e:
        print(TemplateGenerator.format_error_message(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
