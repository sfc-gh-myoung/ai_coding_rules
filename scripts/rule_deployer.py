#!/usr/bin/env python3
"""Deploy production-ready AI coding rules and skills to target projects.

This script copies rules and skills from the source directories to a destination.
All rules and skills are production-ready with no generation step required.

Features:
    - Copies rules/*.md to DEST/rules/
    - Copies skills/ to DEST/skills/ (respects pyproject.toml exclusions)
    - Copies AGENTS.md and RULES_INDEX.md to DEST/
    - Validates source files exist before copying
    - Supports dry-run mode for safety
    - Provides detailed logging

Usage:
    python scripts/rule_deployer.py --dest /path/to/project
    python scripts/rule_deployer.py --dest ~/my-project --dry-run
    python scripts/rule_deployer.py --dest . --skip-skills
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
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


def validate_source_structure(project_root: Path, only_skills: bool = False) -> tuple[bool, list[str]]:
    """Validate that source structure exists and is complete.

    Args:
        project_root: Root directory of the project
        only_skills: If True, only validate skills directory (skip rules validation)

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required source files
    rules_dir = project_root / "rules"
    agents_md = project_root / "AGENTS.md"
    rules_index_md = project_root / "RULES_INDEX.md"
    skills_dir = project_root / "skills"

    if only_skills:
        # Only validate skills directory for skills-only deployment
        if not skills_dir.exists():
            errors.append(f"Source skills directory not found: {skills_dir}")
        elif not skills_dir.is_dir():
            errors.append(f"Source skills path is not a directory: {skills_dir}")
        else:
            # Check if skills directory contains subdirectories
            skill_items = list(skills_dir.iterdir())
            skill_dirs = [s for s in skill_items if s.is_dir() and not s.name.startswith(".")]
            if not skill_dirs:
                errors.append(f"No skill directories found in source skills directory: {skills_dir}")
    else:
        # Validate rules and root files for normal deployment
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


def load_skill_exclusions(project_root: Path) -> set[str]:
    """Load skill exclusion patterns from pyproject.toml.

    Reads [tool.rule_deployer] exclude_skills list.
    Returns empty set if config not found or parsing fails.

    Returns:
        Set of skill names/patterns to exclude from deployment
    """
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        log_warning("pyproject.toml not found, deploying all skills")
        return set()

    try:
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)

        exclude_list = config.get("tool", {}).get("rule_deployer", {}).get("exclude_skills", [])

        if not exclude_list:
            # Empty list = no exclusions, deploy all skills
            return set()

        log_info(f"Loaded {len(exclude_list)} exclusion patterns from pyproject.toml", verbose=True)
        return set(exclude_list)

    except Exception as e:
        log_warning(f"Failed to parse pyproject.toml: {e}")
        log_warning("Deploying all skills (no exclusions applied)")
        return set()


def copy_skills(
    project_root: Path, dest_dir: Path, dry_run: bool = False, verbose: bool = True
) -> tuple[int, int, int]:
    """Copy skills/ directory to destination, respecting exclusions.

    Exclusions are loaded from [tool.rule_deployer] in pyproject.toml.
    Copies both files and directories, skipping excluded items.

    Returns:
        Tuple of (skills_count, files_copied, files_failed)
    """
    skills_count = 0
    files_copied = 0
    files_failed = 0

    source_skills_dir = project_root / "skills"
    dest_skills_dir = dest_dir / "skills"

    if not source_skills_dir.exists():
        log_warning(f"Skills directory not found: {source_skills_dir}")
        return (0, 0, 0)

    # Load exclusion patterns from pyproject.toml
    exclusions = load_skill_exclusions(project_root)

    if exclusions:
        log_info(f"Excluding skills: {', '.join(sorted(exclusions))}", verbose)

    log_info(f"Deploying skills from: {source_skills_dir}", verbose)

    # Create destination skills directory
    if not dry_run:
        dest_skills_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"Created destination directory: {dest_skills_dir}", verbose)
    else:
        log_info(f"[DRY RUN] Would create directory: {dest_skills_dir}", verbose)

    # Process all items in skills/ directory
    for item in source_skills_dir.iterdir():
        # Skip hidden files/dirs and excluded items
        if item.name.startswith("."):
            continue

        # Check both with and without trailing slash for directories
        if item.name in exclusions or (item.is_dir() and f"{item.name}/" in exclusions):
            log_info(f"Skipping excluded: {item.name}", verbose)
            continue

        dest_item = dest_skills_dir / item.name

        try:
            if item.is_file():
                # Copy individual file (counts as 1 skill)
                if not dry_run:
                    shutil.copy2(item, dest_item)
                    log_info(f"Copied: {item.name} → {dest_item}", verbose)
                else:
                    log_info(f"[DRY RUN] Would copy: {item.name} → {dest_item}", verbose)
                skills_count += 1
                files_copied += 1

            elif item.is_dir():
                # Copy directory recursively (counts as 1 skill)
                if not dry_run:
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    # Count files in directory
                    dir_files = list(item.rglob("*"))
                    dir_files = [f for f in dir_files if f.is_file()]
                    log_info(
                        f"Copied directory: {item.name} ({len(dir_files)} files) → {dest_item}",
                        verbose,
                    )
                    skills_count += 1
                    files_copied += len(dir_files)
                else:
                    dir_files = list(item.rglob("*"))
                    dir_files = [f for f in dir_files if f.is_file()]
                    log_info(
                        f"[DRY RUN] Would copy directory: {item.name} ({len(dir_files)} files)",
                        verbose,
                    )
                    skills_count += 1
                    files_copied += len(dir_files)

        except Exception as e:
            log_error(f"Failed to copy {item.name}: {e}")
            files_failed += 1

    return (skills_count, files_copied, files_failed)


def deploy_rules(
    dest: Path,
    skip_skills: bool = False,
    only_skills: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
) -> bool:
    """Deploy rules and skills to destination directory.

    Args:
        dest: Destination directory path
        skip_skills: If True, skip deploying skills/ directory (default: False, skills deployed)
        only_skills: If True, deploy only skills/ directory (skip rules and root files)
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

    if only_skills and skip_skills:
        log_error("Cannot use both --only-skills and --skip-skills flags together")
        return False

    # Validate source structure
    is_valid, errors = validate_source_structure(project_root, only_skills=only_skills)
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

    # Initialize counters
    rules_copied = 0
    rules_failed = 0
    root_copied = 0
    root_failed = 0
    skills_count = 0
    skills_files_copied = 0
    skills_failed = 0

    if only_skills:
        # Skills-only deployment mode
        log_info("SKILLS-ONLY DEPLOYMENT MODE", verbose)
        log_info("Copying skills directory (respecting pyproject.toml exclusions)...", verbose)
        skills_count, skills_files_copied, skills_failed = copy_skills(project_root, dest, dry_run, verbose)
    else:
        # Normal deployment mode (rules + optional skills)
        # Copy rules
        log_info("Copying rule files...", verbose)
        rules_copied, rules_failed = copy_rules(project_root / "rules", dest, dry_run, verbose)

        # Copy root files
        log_info("Copying root files (AGENTS.md, RULES_INDEX.md)...", verbose)
        root_copied, root_failed = copy_root_files(project_root, dest, dry_run, verbose)

        # Copy skills unless explicitly skipped
        if not skip_skills:
            log_info("Copying skills directory (respecting pyproject.toml exclusions)...", verbose)
            skills_count, skills_files_copied, skills_failed = copy_skills(project_root, dest, dry_run, verbose)
        else:
            log_info("Skipping skills deployment (--skip-skills flag set)", verbose)

    # Summary
    total_files = rules_copied + root_copied + skills_files_copied
    total_failed = rules_failed + root_failed + skills_failed

    print("\n" + "=" * 60)
    if only_skills:
        print("SKILLS-ONLY DEPLOYMENT SUMMARY")
    else:
        print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if only_skills:
        # Skills-only summary
        print(f"Skills copied:     {skills_count}")
        print(f"Files copied:      {skills_files_copied}")
        print(f"Total failed:      {total_failed}")
    else:
        # Full deployment summary
        print(f"Rules copied:      {rules_copied}")
        print(f"Root files copied: {root_copied}")
        if not skip_skills:
            print(f"Skills copied:     {skills_count}")
        else:
            print("Skills copied:     0 (skipped)")
        print(f"Files copied:      {total_files}")
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
  Deploy rules and skills to a project directory:
    python scripts/rule_deployer.py --dest /path/to/project

  Dry run to see what would be copied:
    python scripts/rule_deployer.py --dest ~/my-project --dry-run

  Deploy rules only (skip skills):
    python scripts/rule_deployer.py --dest /path/to/project --skip-skills

  Deploy only skills (for agent configuration directories):
    python scripts/rule_deployer.py --dest ~/.claude/skills --only-skills

  Deploy with verbose output:
    python scripts/rule_deployer.py --dest . --verbose
        """,
    )

    parser.add_argument(
        "--dest",
        type=Path,
        required=True,
        help="Destination directory (REQUIRED). Rules and skills will be copied to DEST/",
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

    parser.add_argument(
        "--skip-skills",
        action="store_true",
        help="Skip deploying skills/ directory (default: skills are deployed)",
    )

    parser.add_argument(
        "--only-skills",
        action="store_true",
        help="Deploy only skills/ directory (skip rules and root files)",
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
    success = deploy_rules(
        dest=dest_path,
        skip_skills=args.skip_skills,
        only_skills=args.only_skills,
        dry_run=args.dry_run,
        verbose=verbose,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
