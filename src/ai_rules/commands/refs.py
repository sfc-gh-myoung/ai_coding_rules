"""Validate that all rule references in RULES_INDEX.md map to actual files.

This command ensures 100% mapping between:
1. Rule filenames referenced in RULES_INDEX.md -> actual files in rules/
2. Rule files in rules/ -> referenced in RULES_INDEX.md (optional orphan check)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from ai_rules._shared.console import console, log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root, get_rules_dir

# Regex to find rule file references (NNN-*.md or NNNx-*.md patterns)
# Matches patterns like: 000-global-core.md, 101a-snowflake-streamlit-visualization.md
RE_RULE_REF = re.compile(r"\b(\d{3}[a-z]?-[\w-]+\.md)\b")

# Files in rules/ that are NOT rules (should be skipped)
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
}


def extract_references_from_index(index_path: Path) -> set[str]:
    """Extract all rule file references from RULES_INDEX.md.

    Args:
        index_path: Path to RULES_INDEX.md

    Returns:
        Set of rule filenames referenced in the index
    """
    content = index_path.read_text(encoding="utf-8")
    references = set(RE_RULE_REF.findall(content))
    return references


def get_actual_rule_files(rules_dir: Path) -> set[str]:
    """Get all actual rule files in the rules/ directory.

    Args:
        rules_dir: Path to rules/ directory

    Returns:
        Set of rule filenames that exist on disk
    """
    rule_files = set()
    for filepath in rules_dir.rglob("*.md"):
        if filepath.name not in SKIP_FILES:
            rule_files.add(filepath.name)
    return rule_files


def validate_references(
    index_path: Path,
    rules_dir: Path,
    check_orphans: bool = False,
    verbose: bool = False,
) -> tuple[list[str], list[str]]:
    """Validate all references in the index against actual files.

    Args:
        index_path: Path to RULES_INDEX.md
        rules_dir: Path to rules/ directory
        check_orphans: If True, also report unreferenced rule files
        verbose: If True, print all references found

    Returns:
        Tuple of (broken_refs, orphaned_files) lists
    """
    # Extract references and actual files
    referenced = extract_references_from_index(index_path)
    actual = get_actual_rule_files(rules_dir)

    if verbose:
        log_info(f"References found in {index_path.name}: {len(referenced)}")
        log_info(f"Rule files found in {rules_dir}: {len(actual)}")

        # Show table of references
        table = Table(title="Rule References")
        table.add_column("Reference", style="cyan")
        table.add_column("Status", style="green")

        for ref in sorted(referenced):
            status = "[green]exists[/green]" if ref in actual else "[red]missing[/red]"
            table.add_row(ref, status)

        console.print(table)

    # Find broken references (referenced but don't exist)
    broken_refs = sorted(referenced - actual)

    # Find orphaned files (exist but not referenced)
    orphaned_files = sorted(actual - referenced) if check_orphans else []

    return broken_refs, orphaned_files


refs_app = typer.Typer(
    name="refs",
    help="Validate rule references in RULES_INDEX.md.",
    no_args_is_help=True,
)


@refs_app.command(name="check")
def check(
    check_orphans: Annotated[
        bool,
        typer.Option(
            "--check-orphans",
            help="Also report rule files that exist but aren't referenced.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show all references found, not just errors.",
        ),
    ] = False,
    index_path: Annotated[
        Path | None,
        typer.Option(
            "--index-path",
            help="Path to RULES_INDEX.md.",
        ),
    ] = None,
    rules_dir: Annotated[
        Path | None,
        typer.Option(
            "--rules-dir",
            help="Path to rules directory.",
        ),
    ] = None,
) -> None:
    """Validate that all rule references in RULES_INDEX.md map to actual files.

    Ensures all rule filenames referenced in RULES_INDEX.md map to actual
    files in the rules/ directory.
    """
    # Resolve defaults from project root when not explicitly provided
    if index_path is None or rules_dir is None:
        try:
            project_root = find_project_root()
        except FileNotFoundError:
            log_error("Could not find project root (no pyproject.toml found)")
            raise typer.Exit(1) from None
        if index_path is None:
            index_path = project_root / "rules" / "RULES_INDEX.md"
        if rules_dir is None:
            rules_dir = get_rules_dir(project_root)

    # Validate paths exist
    if not index_path.exists():
        log_error(f"{index_path} not found")
        raise typer.Exit(1)

    if not rules_dir.exists():
        log_error(f"{rules_dir} directory not found")
        raise typer.Exit(1)

    log_info(f"Validating references in {index_path}...")

    # Run validation
    broken_refs, orphaned_files = validate_references(
        index_path,
        rules_dir,
        check_orphans=check_orphans,
        verbose=verbose,
    )

    # Report results
    has_errors = False

    if broken_refs:
        has_errors = True
        console.print(f"\n[red bold]BROKEN REFERENCES ({len(broken_refs)}):[/red bold]")
        console.print("   These files are referenced in RULES_INDEX.md but don't exist:")
        for ref in broken_refs:
            console.print(f"   [red]-[/red] {ref}")

    if orphaned_files:
        console.print(f"\n[yellow bold]ORPHANED FILES ({len(orphaned_files)}):[/yellow bold]")
        console.print("   These rule files exist but aren't referenced in RULES_INDEX.md:")
        for orphan in orphaned_files:
            console.print(f"   [yellow]-[/yellow] {orphan}")

    # Summary
    if has_errors:
        log_error(f"VALIDATION FAILED: {len(broken_refs)} broken reference(s)")
        raise typer.Exit(1)
    else:
        # Get counts for success message
        referenced = extract_references_from_index(index_path)
        actual = get_actual_rule_files(rules_dir)
        matched = len(referenced & actual)
        log_success(f"VALIDATION PASSED: {matched} references, all valid")
        if orphaned_files:
            log_warning(f"Note: {len(orphaned_files)} rule files not referenced")
