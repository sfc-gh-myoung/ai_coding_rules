#!/usr/bin/env python3
"""Deploy production-ready AI coding rules and skills to target projects.

This script copies rules and skills from the source directories to a destination.
All rules and skills are production-ready with no generation step required.

Features:
    - Copies rules/*.md to DEST/rules/
    - Copies skills/ to DEST/skills/ (respects pyproject.toml exclusions)
    - Copies AGENTS.md to DEST/ (or AGENTS_NO_MODE.md as AGENTS.md with --no-mode)
    - Copies rules/RULES_INDEX.md to DEST/rules/
    - Validates source files exist before copying
    - Supports dry-run mode for safety
    - Provides detailed logging

Usage:
    python scripts/rule_deployer.py --dest /path/to/project
    python scripts/rule_deployer.py --dest ~/my-project --dry-run
    python scripts/rule_deployer.py --dest . --skip-skills
    python scripts/rule_deployer.py --dest /path/to/project --no-mode
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tomllib
from pathlib import Path
from typing import NamedTuple


class DeploymentPaths(NamedTuple):
    """Resolved deployment paths for split or unified deployment."""

    agents: Path | None
    rules: Path | None
    skills: Path | None


def resolve_paths(
    dest: Path | None = None,
    agents_dest: Path | None = None,
    rules_dest: Path | None = None,
    skills_dest: Path | None = None,
) -> DeploymentPaths:
    """Resolve deployment paths to absolute paths.

    Args:
        dest: Single destination for unified deployment
        agents_dest: Destination for AGENTS.md (split mode)
        rules_dest: Destination for rules/ directory (split mode)
        skills_dest: Destination for skills/ directory (split mode)

    Returns:
        DeploymentPaths with resolved absolute paths
    """
    if dest:
        # Unified deployment mode
        base = dest.expanduser().resolve()
        return DeploymentPaths(
            agents=base,
            rules=base / "rules",
            skills=base / "skills",
        )
    # Split deployment mode
    return DeploymentPaths(
        agents=agents_dest.expanduser().resolve() if agents_dest else None,
        rules=rules_dest.expanduser().resolve() if rules_dest else None,
        skills=skills_dest.expanduser().resolve() if skills_dest else None,
    )


def substitute_template(template_content: str, paths: DeploymentPaths) -> str:
    """Replace placeholders with resolved absolute paths.

    Args:
        template_content: Template content with {{rules_path}} and {{skills_path}} placeholders
        paths: Resolved deployment paths

    Returns:
        Content with placeholders replaced by absolute paths
    """
    result = template_content
    if paths.rules:
        result = result.replace("{{rules_path}}", str(paths.rules))
    else:
        # AGENTS-only mode: use CWD-based absolute path as reference
        result = result.replace("{{rules_path}}", str(Path.cwd() / "rules"))
    if paths.skills:
        result = result.replace("{{skills_path}}", str(paths.skills))
    else:
        # AGENTS-only mode: use CWD-based absolute path as reference
        result = result.replace("{{skills_path}}", str(Path.cwd() / "skills"))
    return result


def load_template(project_root: Path, no_mode: bool = False) -> str | None:
    """Load AGENTS template file content.

    Args:
        project_root: Root directory of the project
        no_mode: If True, load AGENTS_NO_MODE.md.template

    Returns:
        Template content as string, or None if template not found
    """
    template_name = "AGENTS_NO_MODE.md.template" if no_mode else "AGENTS_MODE.md.template"
    template_path = project_root / "templates" / template_name
    if template_path.exists():
        return template_path.read_text()
    return None


def _prompt_create_directory(path: Path, flag_name: str) -> bool:
    """Prompt user to create a missing directory.

    Args:
        path: The directory path to create
        flag_name: The CLI flag name for display (e.g., '--agents-dest')

    Returns:
        True if directory was created, False if user declined
    """
    try:
        response = input(f"{flag_name} directory does not exist: {path}\nCreate it? [Y/n] ")
    except (EOFError, OSError):
        # Non-interactive environment, treat as decline
        return False
    if response.strip().lower() in ("", "y", "yes"):
        path.mkdir(parents=True, exist_ok=True)
        log_success(f"Created directory: {path}")
        return True
    return False


def validate_split_destinations(
    agents_dest: Path | None,
    rules_dest: Path | None,
    skills_dest: Path | None,
    *,
    force: bool = False,
) -> tuple[bool, list[str]]:
    """Validate split destination arguments.

    Args:
        agents_dest: Destination for AGENTS.md
        rules_dest: Destination for rules/
        skills_dest: Destination for skills/
        force: If True, create missing directories without prompting

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Rule: --skills-dest requires --agents-dest (if skills are referenced)
    if skills_dest and not agents_dest:
        errors.append("--skills-dest requires --agents-dest")

    # Bail early on dependency errors before checking directories
    if errors:
        return (False, errors)

    # Validate directories exist, offering to create if missing
    for flag_name, dest in [
        ("--agents-dest", agents_dest),
        ("--rules-dest", rules_dest),
        ("--skills-dest", skills_dest),
    ]:
        if dest and not dest.exists():
            if force:
                dest.mkdir(parents=True, exist_ok=True)
                log_success(f"Created directory: {dest}")
            elif not _prompt_create_directory(dest, flag_name):
                errors.append(f"{flag_name} directory does not exist: {dest}")

    return (len(errors) == 0, errors)


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


def validate_source_structure(
    project_root: Path, only_skills: bool = False, no_mode: bool = False
) -> tuple[bool, list[str]]:
    """Validate that source structure exists and is complete.

    Args:
        project_root: Root directory of the project
        only_skills: If True, only validate skills directory (skip rules validation)
        no_mode: If True, validate AGENTS_NO_MODE.md exists instead of AGENTS.md

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required source files
    rules_dir = project_root / "rules"
    agents_md_name = "AGENTS_NO_MODE.md" if no_mode else "AGENTS.md"
    agents_md = project_root / agents_md_name
    rules_index_md = project_root / "rules" / "RULES_INDEX.md"
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
                errors.append(
                    f"No skill directories found in source skills directory: {skills_dir}"
                )
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
            # Fall back to template file
            template_name = "AGENTS_NO_MODE.md.template" if no_mode else "AGENTS_MODE.md.template"
            template_path = project_root / "templates" / template_name
            if not template_path.exists():
                errors.append(
                    f"{agents_md_name} not found in project root or templates/: {agents_md}"
                )

        if not rules_index_md.exists():
            errors.append(f"rules/RULES_INDEX.md not found: {rules_index_md}")

    return (len(errors) == 0, errors)


def copy_rules(
    source_dir: Path,
    dest_dir: Path,
    dry_run: bool = False,
    verbose: bool = True,
    direct_copy: bool = False,
) -> tuple[int, int]:
    """Copy rule files from source to destination.

    Skips RULES_INDEX.md as it's handled separately by copy_root_files().

    Args:
        source_dir: Source rules directory
        dest_dir: Destination directory
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging
        direct_copy: If True, copy directly to dest_dir (split mode).
                    If False, copy to dest_dir/rules/ (unified mode).

    Returns:
        Tuple of (files_copied, files_failed)
    """
    files_copied = 0
    files_failed = 0

    # Get all .md files in source rules directory, excluding RULES_INDEX.md
    rule_files = sorted([f for f in source_dir.glob("*.md") if f.name != "RULES_INDEX.md"])

    if not rule_files:
        log_warning(f"No .md files found in {source_dir}")
        return (0, 0)

    log_info(f"Found {len(rule_files)} rule files to copy", verbose)

    # Determine target directory
    dest_rules_dir = dest_dir if direct_copy else dest_dir / "rules"
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
    project_root: Path,
    dest_dir: Path,
    dry_run: bool = False,
    verbose: bool = True,
    no_mode: bool = False,
    paths: DeploymentPaths | None = None,
) -> tuple[int, int]:
    """Copy AGENTS.md to destination root and rules/RULES_INDEX.md to destination rules/.

    When no_mode is True, copies AGENTS_NO_MODE.md as AGENTS.md to the destination.
    When paths is provided (split mode), uses template substitution for AGENTS.md.

    Args:
        project_root: Root directory of the project
        dest_dir: Destination directory for AGENTS.md
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging
        no_mode: If True, use AGENTS_NO_MODE template/file
        paths: DeploymentPaths for template substitution (split mode)

    Returns:
        Tuple of (files_copied, files_failed)
    """
    files_copied = 0
    files_failed = 0

    # Copy AGENTS.md to destination root
    # When no_mode=True, source is AGENTS_NO_MODE.md but destination is still AGENTS.md
    try:
        source_name = "AGENTS_NO_MODE.md" if no_mode else "AGENTS.md"
        dest_file = dest_dir / "AGENTS.md"

        # Check if we should use template substitution (split mode)
        template_content = load_template(project_root, no_mode=no_mode) if paths else None

        if template_content and paths:
            # Split mode: use template with path substitution
            substituted_content = substitute_template(template_content, paths)
            # Remove template header comment from output
            lines = substituted_content.split("\n")
            if lines and lines[0].startswith("<!-- Template:"):
                substituted_content = "\n".join(lines[2:])  # Skip header and blank line

            if not dry_run:
                dest_file.write_text(substituted_content)
                log_info(
                    f"Generated: AGENTS.md (from template with path substitution) → {dest_file}",
                    verbose,
                )
            else:
                log_info(
                    f"[DRY RUN] Would generate: AGENTS.md (from template) → {dest_file}", verbose
                )
        else:
            # Unified mode: direct copy or template fallback
            source_file = project_root / source_name
            template_content_fallback = (
                load_template(project_root, no_mode=no_mode) if not source_file.exists() else None
            )
            if template_content_fallback:
                # Source file missing, use template (strip header comment)
                lines = template_content_fallback.split("\n")
                if lines and lines[0].startswith("<!-- Template:"):
                    template_content_fallback = "\n".join(lines[2:])
                if not dry_run:
                    dest_file.write_text(template_content_fallback)
                    log_info(f"Generated: AGENTS.md (from template) → {dest_file}", verbose)
                else:
                    log_info(
                        f"[DRY RUN] Would generate: AGENTS.md (from template) → {dest_file}",
                        verbose,
                    )
            elif not dry_run:
                shutil.copy2(source_file, dest_file)
                log_info(f"Copied: {source_name} → {dest_file}", verbose)
            else:
                log_info(f"[DRY RUN] Would copy: {source_name} → {dest_file}", verbose)
        files_copied += 1
    except Exception as e:
        log_error(f"Failed to copy/generate AGENTS.md: {e}")
        files_failed += 1

    # Copy rules/RULES_INDEX.md to destination rules/
    # In split mode, rules_dest is used instead of dest_dir/rules
    # and path prefixes are substituted to match deployed locations
    # Skip entirely when in split mode and rules path is None (AGENTS-only)
    if paths and paths.rules is None:
        # AGENTS-only split mode: no rules copied, skip RULES_INDEX.md
        pass
    else:
        try:
            source_file = project_root / "rules" / "RULES_INDEX.md"
            dest_rules_dir = paths.rules if paths and paths.rules else dest_dir / "rules"
            dest_file = dest_rules_dir / "RULES_INDEX.md"

            if paths and paths.rules:
                # Split mode: substitute rules/ and skills/ path prefixes
                content = source_file.read_text()
                content = content.replace("rules/", str(paths.rules) + "/")
                if paths.skills:
                    content = content.replace("skills/", str(paths.skills) + "/")

                if not dry_run:
                    dest_rules_dir.mkdir(parents=True, exist_ok=True)
                    dest_file.write_text(content)
                    log_info(
                        f"Generated: RULES_INDEX.md (with path substitution) → {dest_file}",
                        verbose,
                    )
                else:
                    log_info(
                        f"[DRY RUN] Would generate: RULES_INDEX.md (with path substitution) → {dest_file}",
                        verbose,
                    )
            else:
                # Unified mode: direct copy
                if not dry_run:
                    dest_rules_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    log_info(f"Copied: rules/RULES_INDEX.md → {dest_file}", verbose)
                else:
                    log_info(f"[DRY RUN] Would copy: rules/RULES_INDEX.md → {dest_file}", verbose)
            files_copied += 1
        except Exception as e:
            log_error(f"Failed to copy rules/RULES_INDEX.md: {e}")
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
    project_root: Path,
    dest_dir: Path,
    dry_run: bool = False,
    verbose: bool = True,
    direct_copy: bool = False,
) -> tuple[int, int, int]:
    """Copy skills/ directory to destination, respecting exclusions.

    Exclusions are loaded from [tool.rule_deployer] in pyproject.toml.
    Copies both files and directories, skipping excluded items.

    Args:
        project_root: Project root directory
        dest_dir: Destination directory
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging
        direct_copy: If True, copy directly to dest_dir (split mode).
                    If False, copy to dest_dir/skills/ (unified mode).

    Returns:
        Tuple of (skills_count, files_copied, files_failed)
    """
    skills_count = 0
    files_copied = 0
    files_failed = 0

    source_skills_dir = project_root / "skills"
    dest_skills_dir = dest_dir if direct_copy else dest_dir / "skills"

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
    dest: Path | None = None,
    agents_dest: Path | None = None,
    rules_dest: Path | None = None,
    skills_dest: Path | None = None,
    skip_skills: bool = False,
    only_skills: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
    no_mode: bool = False,
) -> bool:
    """Deploy rules and skills to destination directory.

    Supports two deployment modes:
    1. Unified mode (--dest): All files go to single destination
    2. Split mode (--agents-dest, --rules-dest, --skills-dest): Files go to separate destinations

    Args:
        dest: Single destination directory path (unified mode)
        agents_dest: Destination for AGENTS.md (split mode)
        rules_dest: Destination for rules/ directory (split mode)
        skills_dest: Destination for skills/ directory (split mode)
        skip_skills: If True, skip deploying skills/ directory
        only_skills: If True, deploy only skills/ directory
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging
        no_mode: If True, deploy AGENTS_NO_MODE.md as AGENTS.md

    Returns:
        True if deployment successful, False otherwise
    """
    # Determine project root (script is in scripts/ subdirectory)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    # Determine deployment mode
    is_split_mode = bool(agents_dest or rules_dest or skills_dest)
    paths = resolve_paths(dest, agents_dest, rules_dest, skills_dest)

    log_info(f"Project root: {project_root}", verbose)
    if is_split_mode:
        log_info("SPLIT DEPLOYMENT MODE", verbose)
        if paths.agents:
            log_info(f"  AGENTS.md destination: {paths.agents}", verbose)
        if paths.rules:
            log_info(f"  Rules destination: {paths.rules}", verbose)
        if paths.skills:
            log_info(f"  Skills destination: {paths.skills}", verbose)
    else:
        log_info(f"Destination: {dest}", verbose)

    if dry_run:
        log_warning("DRY RUN MODE - No files will be copied")

    if only_skills and skip_skills:
        log_error("Cannot use both --only-skills and --skip-skills flags together")
        return False

    if no_mode:
        log_info("NO-MODE: Will deploy AGENTS_NO_MODE.md as AGENTS.md", verbose)

    # Validate source structure
    is_valid, errors = validate_source_structure(
        project_root, only_skills=only_skills, no_mode=no_mode
    )
    if not is_valid:
        log_error("Source structure validation failed:")
        for error in errors:
            log_error(f"  - {error}")
        return False

    log_success("Source structure validation passed")

    # In split mode, directories must already exist (validated earlier)
    # In unified mode, create destination if needed
    if not dry_run and not is_split_mode and dest:
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
        skills_dest_dir = paths.skills if is_split_mode and paths.skills else dest
        if skills_dest_dir:
            skills_count, skills_files_copied, skills_failed = copy_skills(
                project_root, skills_dest_dir, dry_run, verbose, direct_copy=is_split_mode
            )
        else:
            log_error("No destination specified for skills")
            return False
    else:
        # Normal deployment mode (rules + optional skills)
        # Determine destination directories
        rules_dest_dir = paths.rules if is_split_mode else dest
        agents_dest_dir = paths.agents if is_split_mode else dest

        # Copy rules
        if rules_dest_dir:
            log_info("Copying rule files...", verbose)
            rules_copied, rules_failed = copy_rules(
                project_root / "rules",
                rules_dest_dir,
                dry_run,
                verbose,
                direct_copy=is_split_mode,
            )

        # Copy root files (AGENTS.md with template substitution in split mode)
        if agents_dest_dir:
            log_info("Copying root files (AGENTS.md, rules/RULES_INDEX.md)...", verbose)
            root_copied, root_failed = copy_root_files(
                project_root,
                agents_dest_dir,
                dry_run,
                verbose,
                no_mode=no_mode,
                paths=paths if is_split_mode else None,
            )

        # Copy examples/ subdirectory if it exists
        examples_src = project_root / "rules" / "examples"
        if examples_src.exists() and examples_src.is_dir() and rules_dest_dir:
            # In split mode, examples go under rules destination
            # In unified mode, examples go under dest/rules
            if is_split_mode:
                examples_dest = rules_dest_dir / "examples"
            elif dest:
                dest_rules_dir = dest / "rules"
                examples_dest = dest_rules_dir / "examples"
            else:
                examples_dest = None

            if examples_dest:
                try:
                    if not dry_run:
                        if examples_dest.exists():
                            shutil.rmtree(examples_dest)
                        shutil.copytree(examples_src, examples_dest)
                        example_files = list(examples_src.glob("*.md"))
                        log_info(f"Copied examples/ ({len(example_files)} files)", verbose)
                        root_copied += len(example_files)
                    else:
                        example_files = list(examples_src.glob("*.md"))
                        log_info(
                            f"[DRY RUN] Would copy examples/ ({len(example_files)} files)", verbose
                        )
                except Exception as e:
                    log_error(f"Failed to copy examples/: {e}")
                    root_failed += 1

        # Copy skills unless explicitly skipped
        if not skip_skills:
            skills_dest_dir = paths.skills if is_split_mode else dest
            if skills_dest_dir:
                log_info(
                    "Copying skills directory (respecting pyproject.toml exclusions)...", verbose
                )
                skills_count, skills_files_copied, skills_failed = copy_skills(
                    project_root, skills_dest_dir, dry_run, verbose, direct_copy=is_split_mode
                )
            elif is_split_mode:
                log_info("Skipping skills deployment (no --skills-dest specified)", verbose)
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

    # Show deployment locations
    if only_skills:
        skills_dest_dir = paths.skills if is_split_mode and paths.skills else dest
        if skills_dest_dir:
            print(f"SKILLS:            {skills_dest_dir}")
    elif is_split_mode:
        if paths.agents:
            print(f"AGENTS:            {paths.agents}/AGENTS.md")
        if paths.rules:
            print(f"RULES:             {paths.rules}/")
        else:
            print(f"RULES (ref):       {Path.cwd()}/rules (not copied, CWD reference)")
        if paths.skills:
            print(f"SKILLS:            {paths.skills}/")
        else:
            print(f"SKILLS (ref):      {Path.cwd()}/skills (not copied, CWD reference)")
    else:
        print(f"DEST:              {dest}")
        print(f"  AGENTS:          {dest}/AGENTS.md")
        print(f"  RULES:           {dest}/rules/")
        if not skip_skills:
            print(f"  SKILLS:          {dest}/skills/")
    print()

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
  Deploy rules and skills to a project directory (unified mode):
    python scripts/rule_deployer.py --dest /path/to/project

  Deploy to separate destinations (split mode):
    python scripts/rule_deployer.py --agents-dest ~/project --rules-dest ~/project/rules --skills-dest ~/project/skills

  Deploy only AGENTS.md and rules (no skills, split mode):
    python scripts/rule_deployer.py --agents-dest ~/project --rules-dest ~/project/rules

  Dry run to see what would be copied:
    python scripts/rule_deployer.py --dest ~/my-project --dry-run

  Deploy rules only (skip skills):
    python scripts/rule_deployer.py --dest /path/to/project --skip-skills

  Deploy only skills (for agent configuration directories):
    python scripts/rule_deployer.py --dest ~/.claude/skills --only-skills

  Deploy with AGENTS_NO_MODE.md (no PLAN/ACT workflow):
    python scripts/rule_deployer.py --dest /path/to/project --no-mode

  Deploy with verbose output:
    python scripts/rule_deployer.py --dest . --verbose
        """,
    )

    # Unified destination (mutually exclusive with split destinations)
    parser.add_argument(
        "--dest",
        type=Path,
        help="Destination directory for unified deployment. Rules go to DEST/rules/, skills to DEST/skills/",
    )

    # Split destination arguments
    parser.add_argument(
        "--agents-dest",
        type=Path,
        help="Destination directory for AGENTS.md (split mode). Requires --rules-dest.",
    )

    parser.add_argument(
        "--rules-dest",
        type=Path,
        help="Destination directory for rules/ (split mode). Can be used with --agents-dest.",
    )

    parser.add_argument(
        "--skills-dest",
        type=Path,
        help="Destination directory for skills/ (split mode). Requires --agents-dest.",
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

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Create destination directories if they don't exist (no prompt)",
    )

    parser.add_argument(
        "--no-mode",
        action="store_true",
        help="Deploy AGENTS_NO_MODE.md as AGENTS.md (simplified workflow without PLAN/ACT)",
    )

    args = parser.parse_args()

    # Handle quiet mode
    verbose = args.verbose and not args.quiet

    # Normalize paths: expand ~ and resolve relative paths
    if args.dest:
        args.dest = args.dest.expanduser()
    if args.agents_dest:
        args.agents_dest = args.agents_dest.expanduser()
    if args.rules_dest:
        args.rules_dest = args.rules_dest.expanduser()
    if args.skills_dest:
        args.skills_dest = args.skills_dest.expanduser()

    # Determine if using split mode
    has_split_args = args.agents_dest or args.rules_dest or args.skills_dest

    # Validate mutual exclusivity: --dest XOR split destinations
    if args.dest and has_split_args:
        log_error(
            "Cannot use --dest with split destination arguments (--agents-dest, --rules-dest, --skills-dest)"
        )
        log_error(
            "Use either --dest for unified deployment OR split destinations for separate directories"
        )
        return 1

    # Validate that at least one destination is provided
    if not args.dest and not has_split_args:
        log_error(
            "Error: Must specify either --dest or at least one split destination (--agents-dest, --rules-dest, --skills-dest)"
        )
        parser.print_help()
        return 1

    # Validate split destination dependencies and directory existence
    if has_split_args:
        is_valid, errors = validate_split_destinations(
            args.agents_dest, args.rules_dest, args.skills_dest, force=args.force
        )
        if not is_valid:
            for error in errors:
                log_error(error)
            return 1

    # Deploy
    success = deploy_rules(
        dest=args.dest,
        agents_dest=args.agents_dest,
        rules_dest=args.rules_dest,
        skills_dest=args.skills_dest,
        skip_skills=args.skip_skills,
        only_skills=args.only_skills,
        dry_run=args.dry_run,
        verbose=verbose,
        no_mode=args.no_mode,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
