#!/usr/bin/env python3
"""Deploy production-ready AI coding rules to target projects.

This script copies rules from the source rules/ directory to a destination directory.
All rules are production-ready with no generation step required.

Features:
    - Copies rules/*.md to DEST/rules/
    - Copies AGENTS.md and RULES_INDEX.md to DEST/
    - Validates source files exist before copying
    - Supports dry-run mode for safety
    - Provides detailed logging

Usage:
    python scripts/rule_deployer.py --dest /path/to/project
    python scripts/rule_deployer.py --dest ~/my-project --dry-run
    python scripts/rule_deployer.py --dest . --verbose
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def log_info(message: str, verbose: bool = True) -> None:
    """Print info message to stdout."""
    if verbose:
        print(f"[INFO] {message}")


def log_success(message: str) -> None:
    """Print success message to stdout."""
    print(f"[✓] {message}")


def log_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"[✗] {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    """Print warning message to stdout."""
    print(f"[!] {message}")


def validate_source_structure(project_root: Path) -> tuple[bool, list[str]]:
    """Validate that source structure exists and is complete.

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required source files
    rules_dir = project_root / "rules"
    agents_md = project_root / "AGENTS.md"
    rules_index_md = project_root / "RULES_INDEX.md"

    if not rules_dir.exists():
        errors.append(f"Source rules directory not found: {rules_dir}")
    elif not rules_dir.is_dir():
        errors.append(f"Source rules path is not a directory: {rules_dir}")
    else:
        # Check if rules directory contains .md files
        rule_files = list(rules_dir.glob("*.md"))
        if not rule_files:
            errors.append(f"No .md files found in source rules directory: {rules_dir}")

    if not agents_md.exists():
        errors.append(f"AGENTS.md not found in project root: {agents_md}")

    if not rules_index_md.exists():
        errors.append(f"RULES_INDEX.md not found in project root: {rules_index_md}")

    return (len(errors) == 0, errors)


def copy_rules(
    source_dir: Path, dest_dir: Path, dry_run: bool = False, verbose: bool = True
) -> tuple[int, int]:
    """Copy rule files from source to destination.

    Returns:
        Tuple of (files_copied, files_failed)
    """
    files_copied = 0
    files_failed = 0

    # Get all .md files in source rules directory
    rule_files = sorted(source_dir.glob("*.md"))

    if not rule_files:
        log_warning(f"No .md files found in {source_dir}")
        return (0, 0)

    log_info(f"Found {len(rule_files)} rule files to copy", verbose)

    # Create destination rules directory
    dest_rules_dir = dest_dir / "rules"
    if not dry_run:
        dest_rules_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"Created destination directory: {dest_rules_dir}", verbose)
    else:
        log_info(f"[DRY RUN] Would create directory: {dest_rules_dir}", verbose)

    # Copy each rule file
    for rule_file in rule_files:
        dest_file = dest_rules_dir / rule_file.name

        try:
            if not dry_run:
                shutil.copy2(rule_file, dest_file)
                log_info(f"Copied: {rule_file.name} → {dest_file}", verbose)
            else:
                log_info(f"[DRY RUN] Would copy: {rule_file.name} → {dest_file}", verbose)

            files_copied += 1
        except Exception as e:
            log_error(f"Failed to copy {rule_file.name}: {e}")
            files_failed += 1

    return (files_copied, files_failed)


def copy_root_files(
    project_root: Path, dest_dir: Path, dry_run: bool = False, verbose: bool = True
) -> tuple[int, int]:
    """Copy AGENTS.md and RULES_INDEX.md to destination root.

    Returns:
        Tuple of (files_copied, files_failed)
    """
    files_copied = 0
    files_failed = 0

    root_files = ["AGENTS.md", "RULES_INDEX.md"]

    for filename in root_files:
        source_file = project_root / filename
        dest_file = dest_dir / filename

        try:
            if not dry_run:
                shutil.copy2(source_file, dest_file)
                log_info(f"Copied: {filename} → {dest_file}", verbose)
            else:
                log_info(f"[DRY RUN] Would copy: {filename} → {dest_file}", verbose)

            files_copied += 1
        except Exception as e:
            log_error(f"Failed to copy {filename}: {e}")
            files_failed += 1

    return (files_copied, files_failed)


def deploy_rules(dest: Path, dry_run: bool = False, verbose: bool = True) -> bool:
    """Deploy rules to destination directory.

    Args:
        dest: Destination directory path
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging

    Returns:
        True if deployment successful, False otherwise
    """
    # Determine project root (script is in scripts/ subdirectory)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    log_info(f"Project root: {project_root}", verbose)
    log_info(f"Destination: {dest}", verbose)

    if dry_run:
        log_warning("DRY RUN MODE - No files will be copied")

    # Validate source structure
    is_valid, errors = validate_source_structure(project_root)
    if not is_valid:
        log_error("Source structure validation failed:")
        for error in errors:
            log_error(f"  - {error}")
        return False

    log_success("Source structure validation passed")

    # Ensure destination exists
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
        log_info(f"Ensured destination directory exists: {dest}", verbose)

    # Copy rules
    log_info("Copying rule files...", verbose)
    rules_copied, rules_failed = copy_rules(project_root / "rules", dest, dry_run, verbose)

    # Copy root files
    log_info("Copying root files (AGENTS.md, RULES_INDEX.md)...", verbose)
    root_copied, root_failed = copy_root_files(project_root, dest, dry_run, verbose)

    # Summary
    total_copied = rules_copied + root_copied
    total_failed = rules_failed + root_failed

    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"Rules copied:      {rules_copied}")
    print(f"Root files copied: {root_copied}")
    print(f"Total copied:      {total_copied}")
    print(f"Total failed:      {total_failed}")
    print("=" * 60)

    if total_failed > 0:
        log_error(f"Deployment completed with {total_failed} failures")
        return False
    else:
        log_success("Deployment completed successfully!")
        return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy production-ready AI coding rules to target project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Deploy to a project directory:
    python scripts/rule_deployer.py --dest /path/to/project

  Dry run to see what would be copied:
    python scripts/rule_deployer.py --dest ~/my-project --dry-run

  Deploy with verbose output:
    python scripts/rule_deployer.py --dest . --verbose
        """,
    )

    parser.add_argument(
        "--dest",
        type=Path,
        required=True,
        help="Destination directory (REQUIRED). Rules will be copied to DEST/rules/",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview deployment without copying files"
    )

    parser.add_argument(
        "--verbose", action="store_true", default=True, help="Enable verbose output (default: True)"
    )

    parser.add_argument(
        "--quiet", action="store_true", help="Suppress detailed output (only show summary)"
    )

    args = parser.parse_args()

    # Handle quiet mode
    verbose = args.verbose and not args.quiet

    # Validate destination is provided
    if not args.dest:
        log_error("Error: --dest argument is required")
        parser.print_help()
        return 1

    # Resolve destination path
    dest_path = args.dest.resolve()

    # Deploy
    success = deploy_rules(dest=dest_path, dry_run=args.dry_run, verbose=verbose)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
