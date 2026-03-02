"""Deploy production-ready AI coding rules and skills to target projects.

This command copies rules and skills from the source directories to a destination.
All rules and skills are production-ready with no generation step required.

Features:
    - Copies rules/*.md to DEST/rules/
    - Copies skills/ to DEST/skills/ (respects pyproject.toml exclusions)
    - Copies AGENTS.md to DEST/ (or AGENTS_NO_MODE.md as AGENTS.md with --no-mode)
    - Copies rules/RULES_INDEX.md to DEST/rules/
    - Validates source files exist before copying
    - Supports dry-run mode for safety
    - Provides detailed logging with Rich formatting
"""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path
from typing import Annotated, NamedTuple

import typer
from rich.tree import Tree

from ai_rules._shared.console import console, log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root


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
        response = console.input(
            f"[yellow]{flag_name} directory does not exist:[/yellow] {path}\nCreate it? [Y/n] "
        )
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

    if verbose:
        log_info(f"Found {len(rule_files)} rule files to copy")

    # Determine target directory
    dest_rules_dir = dest_dir if direct_copy else dest_dir / "rules"
    if not dry_run:
        dest_rules_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            log_info(f"Created destination directory: {dest_rules_dir}")
    elif verbose:
        log_info(f"[dry-run] Would create directory: {dest_rules_dir}")

    # Copy each rule file
    for rule_file in rule_files:
        dest_file = dest_rules_dir / rule_file.name

        try:
            if not dry_run:
                shutil.copy2(rule_file, dest_file)
                if verbose:
                    log_info(f"Copied: {rule_file.name} -> {dest_file}")
            elif verbose:
                log_info(f"[dry-run] Would copy: {rule_file.name} -> {dest_file}")

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
                if verbose:
                    log_info(
                        f"Generated: AGENTS.md (from template with path substitution) -> {dest_file}"
                    )
            elif verbose:
                log_info(f"[dry-run] Would generate: AGENTS.md (from template) -> {dest_file}")
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
                    if verbose:
                        log_info(f"Generated: AGENTS.md (from template) -> {dest_file}")
                elif verbose:
                    log_info(f"[dry-run] Would generate: AGENTS.md (from template) -> {dest_file}")
            elif not dry_run:
                shutil.copy2(source_file, dest_file)
                if verbose:
                    log_info(f"Copied: {source_name} -> {dest_file}")
            elif verbose:
                log_info(f"[dry-run] Would copy: {source_name} -> {dest_file}")
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
                    if verbose:
                        log_info(
                            f"Generated: RULES_INDEX.md (with path substitution) -> {dest_file}"
                        )
                elif verbose:
                    log_info(
                        f"[dry-run] Would generate: RULES_INDEX.md (with path substitution) -> {dest_file}"
                    )
            else:
                # Unified mode: direct copy
                if not dry_run:
                    dest_rules_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    if verbose:
                        log_info(f"Copied: rules/RULES_INDEX.md -> {dest_file}")
                elif verbose:
                    log_info(f"[dry-run] Would copy: rules/RULES_INDEX.md -> {dest_file}")
            files_copied += 1
        except Exception as e:
            log_error(f"Failed to copy rules/RULES_INDEX.md: {e}")
            files_failed += 1

    return (files_copied, files_failed)


def load_skill_exclusions(project_root: Path, verbose: bool = True) -> set[str]:
    """Load skill exclusion patterns from pyproject.toml.

    Reads [tool.rule_deployer] exclude_skills list.
    Returns empty set if config not found or parsing fails.

    Args:
        project_root: Root directory of the project
        verbose: If True, print detailed logging

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

        if verbose:
            log_info(f"Loaded {len(exclude_list)} exclusion patterns from pyproject.toml")
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
    exclusions = load_skill_exclusions(project_root, verbose=verbose)

    if exclusions and verbose:
        log_info(f"Excluding skills: {', '.join(sorted(exclusions))}")

    if verbose:
        log_info(f"Deploying skills from: {source_skills_dir}")

    # Create destination skills directory
    if not dry_run:
        dest_skills_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            log_info(f"Created destination directory: {dest_skills_dir}")
    elif verbose:
        log_info(f"[dry-run] Would create directory: {dest_skills_dir}")

    # Process all items in skills/ directory
    for item in source_skills_dir.iterdir():
        # Skip hidden files/dirs and excluded items
        if item.name.startswith("."):
            continue

        # Check both with and without trailing slash for directories
        if item.name in exclusions or (item.is_dir() and f"{item.name}/" in exclusions):
            if verbose:
                log_info(f"Skipping excluded: {item.name}")
            continue

        dest_item = dest_skills_dir / item.name

        try:
            if item.is_file():
                # Copy individual file (counts as 1 skill)
                if not dry_run:
                    shutil.copy2(item, dest_item)
                    if verbose:
                        log_info(f"Copied: {item.name} -> {dest_item}")
                elif verbose:
                    log_info(f"[dry-run] Would copy: {item.name} -> {dest_item}")
                skills_count += 1
                files_copied += 1

            elif item.is_dir():
                # Copy directory recursively (counts as 1 skill)
                if not dry_run:
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    # Count files in directory
                    dir_files = list(item.rglob("*"))
                    dir_files = [f for f in dir_files if f.is_file()]
                    if verbose:
                        log_info(
                            f"Copied directory: {item.name} ({len(dir_files)} files) -> {dest_item}"
                        )
                    skills_count += 1
                    files_copied += len(dir_files)
                else:
                    dir_files = list(item.rglob("*"))
                    dir_files = [f for f in dir_files if f.is_file()]
                    if verbose:
                        log_info(
                            f"[dry-run] Would copy directory: {item.name} ({len(dir_files)} files)"
                        )
                    skills_count += 1
                    files_copied += len(dir_files)

        except Exception as e:
            log_error(f"Failed to copy {item.name}: {e}")
            files_failed += 1

    return (skills_count, files_copied, files_failed)


def build_deployment_tree(
    paths: DeploymentPaths,
    dest: Path | None,
    is_split_mode: bool,
    skip_skills: bool,
    only_skills: bool,
    rules_copied: int,
    root_copied: int,
    skills_count: int,
    skills_files_copied: int,
) -> Tree:
    """Build a Rich Tree showing the deployment structure.

    Args:
        paths: Resolved deployment paths
        dest: Unified destination path
        is_split_mode: Whether in split deployment mode
        skip_skills: Whether skills were skipped
        only_skills: Whether only skills were deployed
        rules_copied: Number of rule files copied
        root_copied: Number of root files copied
        skills_count: Number of skills copied
        skills_files_copied: Number of skill files copied

    Returns:
        Rich Tree object for display
    """
    if only_skills:
        skills_dest_dir = paths.skills if is_split_mode and paths.skills else dest
        tree = Tree("[bold green]Deployment Summary[/bold green]")
        tree.add(
            f"[cyan]skills/[/cyan] -> {skills_dest_dir} ({skills_count} skills, {skills_files_copied} files)"
        )
        return tree

    if is_split_mode:
        tree = Tree("[bold green]Split Deployment Summary[/bold green]")
        if paths.agents:
            tree.add(f"[cyan]AGENTS.md[/cyan] -> {paths.agents}/AGENTS.md")
        if paths.rules:
            tree.add(f"[cyan]rules/[/cyan] -> {paths.rules}/ ({rules_copied} files)")
        else:
            tree.add("[dim]rules/ (not copied, CWD reference)[/dim]")
        if paths.skills:
            tree.add(f"[cyan]skills/[/cyan] -> {paths.skills}/ ({skills_count} skills)")
        else:
            tree.add("[dim]skills/ (not copied, CWD reference)[/dim]")
    else:
        tree = Tree(f"[bold green]Deployment to {dest}[/bold green]")
        tree.add(f"[cyan]AGENTS.md[/cyan] ({root_copied} root files)")
        tree.add(f"[cyan]rules/[/cyan] ({rules_copied} files)")
        if not skip_skills:
            tree.add(f"[cyan]skills/[/cyan] ({skills_count} skills, {skills_files_copied} files)")
        else:
            tree.add("[dim]skills/ (skipped)[/dim]")

    return tree


def deploy_rules(
    project_root: Path,
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
    1. Unified mode (dest): All files go to single destination
    2. Split mode (--agents-dest, --rules-dest, --skills-dest): Files go to separate destinations

    Args:
        project_root: Project root directory
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
    # Determine deployment mode
    is_split_mode = bool(agents_dest or rules_dest or skills_dest)
    paths = resolve_paths(dest, agents_dest, rules_dest, skills_dest)

    if verbose:
        log_info(f"Project root: {project_root}")
        if is_split_mode:
            log_info("Split deployment mode")
            if paths.agents:
                log_info(f"  AGENTS.md destination: {paths.agents}")
            if paths.rules:
                log_info(f"  Rules destination: {paths.rules}")
            if paths.skills:
                log_info(f"  Skills destination: {paths.skills}")
        else:
            log_info(f"Destination: {dest}")

    if dry_run:
        log_warning("DRY RUN MODE - No files will be copied")

    if only_skills and skip_skills:
        log_error("Cannot use both --only-skills and --skip-skills flags together")
        return False

    if no_mode and verbose:
        log_info("NO-MODE: Will deploy AGENTS_NO_MODE.md as AGENTS.md")

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
        if verbose:
            log_info(f"Ensured destination directory exists: {dest}")

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
        if verbose:
            log_info("SKILLS-ONLY DEPLOYMENT MODE")
            log_info("Copying skills directory (respecting pyproject.toml exclusions)...")
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
            if verbose:
                log_info("Copying rule files...")
            rules_copied, rules_failed = copy_rules(
                project_root / "rules",
                rules_dest_dir,
                dry_run,
                verbose,
                direct_copy=is_split_mode,
            )

        # Copy root files (AGENTS.md with template substitution in split mode)
        if agents_dest_dir:
            if verbose:
                log_info("Copying root files (AGENTS.md, rules/RULES_INDEX.md)...")
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
            else:
                assert dest is not None  # unified mode always has dest
                dest_rules_dir = dest / "rules"
                examples_dest = dest_rules_dir / "examples"

            if examples_dest:
                try:
                    if not dry_run:
                        if examples_dest.exists():
                            shutil.rmtree(examples_dest)
                        shutil.copytree(examples_src, examples_dest)
                        example_files = list(examples_src.glob("*.md"))
                        if verbose:
                            log_info(f"Copied examples/ ({len(example_files)} files)")
                        root_copied += len(example_files)
                    elif verbose:
                        example_files = list(examples_src.glob("*.md"))
                        log_info(f"[dry-run] Would copy examples/ ({len(example_files)} files)")
                except Exception as e:
                    log_error(f"Failed to copy examples/: {e}")
                    root_failed += 1

        # Copy skills unless explicitly skipped
        if not skip_skills:
            skills_dest_dir = paths.skills if is_split_mode else dest
            if skills_dest_dir:
                if verbose:
                    log_info("Copying skills directory (respecting pyproject.toml exclusions)...")
                skills_count, skills_files_copied, skills_failed = copy_skills(
                    project_root, skills_dest_dir, dry_run, verbose, direct_copy=is_split_mode
                )
            elif is_split_mode and verbose:
                log_info("Skipping skills deployment (no --skills-dest specified)")
        elif verbose:
            log_info("Skipping skills deployment (--skip-skills flag set)")

    # Summary
    total_files = rules_copied + root_copied + skills_files_copied
    total_failed = rules_failed + root_failed + skills_failed

    console.print()
    console.rule("[bold]Deployment Summary[/bold]")

    # Build and display deployment tree
    tree = build_deployment_tree(
        paths,
        dest,
        is_split_mode,
        skip_skills,
        only_skills,
        rules_copied,
        root_copied,
        skills_count,
        skills_files_copied,
    )
    console.print(tree)
    console.print()

    # Statistics
    if only_skills:
        console.print(f"[bold]Skills copied:[/bold]     {skills_count}")
        console.print(f"[bold]Files copied:[/bold]      {skills_files_copied}")
    else:
        console.print(f"[bold]Rules copied:[/bold]      {rules_copied}")
        console.print(f"[bold]Root files copied:[/bold] {root_copied}")
        if not skip_skills:
            console.print(f"[bold]Skills copied:[/bold]     {skills_count}")
        else:
            console.print("[bold]Skills copied:[/bold]     0 (skipped)")
        console.print(f"[bold]Files copied:[/bold]      {total_files}")

    console.print(f"[bold]Total failed:[/bold]      {total_failed}")

    console.rule()

    if total_failed > 0:
        log_error(f"Deployment completed with {total_failed} failures")
        return False
    else:
        log_success("Deployment completed successfully!")
        return True


def deploy(
    ctx: typer.Context,
    dest: Annotated[
        Path | None,
        typer.Argument(
            help="Destination directory for unified deployment. Rules go to DEST/rules/, skills to DEST/skills/.",
        ),
    ] = None,
    split: Annotated[
        bool,
        typer.Option(
            "--split",
            help="Enable split deployment mode with separate destinations.",
        ),
    ] = False,
    agents_dest: Annotated[
        Path | None,
        typer.Option(
            "--agents-dest",
            help="Destination directory for AGENTS.md (split mode). Requires --split.",
        ),
    ] = None,
    rules_dest: Annotated[
        Path | None,
        typer.Option(
            "--rules-dest",
            help="Destination directory for rules/ (split mode). Requires --split.",
        ),
    ] = None,
    skills_dest: Annotated[
        Path | None,
        typer.Option(
            "--skills-dest",
            help="Destination directory for skills/ (split mode). Requires --split and --agents-dest.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Preview deployment without copying files.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose output.",
        ),
    ] = True,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress detailed output (only show summary).",
        ),
    ] = False,
    skip_skills: Annotated[
        bool,
        typer.Option(
            "--skip-skills",
            help="Skip deploying skills/ directory.",
        ),
    ] = False,
    only_skills: Annotated[
        bool,
        typer.Option(
            "--only-skills",
            help="Deploy only skills/ directory (skip rules and root files).",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Create destination directories if they don't exist (no prompt).",
        ),
    ] = False,
    no_mode: Annotated[
        bool,
        typer.Option(
            "--no-mode",
            help="Deploy AGENTS_NO_MODE.md as AGENTS.md (simplified workflow without PLAN/ACT).",
        ),
    ] = False,
) -> None:
    """Deploy production-ready AI coding rules to target project.

    Supports two deployment modes:

    1. Unified mode: All files go to single destination

        ai-rules deploy /path/to/project

    2. Split mode: Files go to separate destinations

        ai-rules deploy --split --agents-dest ~/project --rules-dest ~/project/rules

    Examples:
        # Deploy rules and skills to a project directory

        ai-rules deploy /path/to/project

        # Dry run to see what would be copied

        ai-rules deploy ~/my-project --dry-run

        # Deploy rules only (skip skills)

        ai-rules deploy /path/to/project --skip-skills

        # Deploy only skills (for agent configuration directories)

        ai-rules deploy ~/.claude/skills --only-skills

        # Deploy with AGENTS_NO_MODE.md (no PLAN/ACT workflow)

        ai-rules deploy /path/to/project --no-mode

        # Split deployment mode

        ai-rules deploy --split --agents-dest ~/project --rules-dest ~/project/rules --skills-dest ~/project/skills
    """
    # Handle quiet mode
    actual_verbose = verbose and not quiet

    # Find project root
    try:
        project_root = find_project_root()
    except FileNotFoundError:
        log_error("Could not find project root (no pyproject.toml found)")
        raise typer.Exit(code=1) from None

    # Normalize paths: expand ~ and resolve relative paths
    if dest:
        dest = dest.expanduser()
    if agents_dest:
        agents_dest = agents_dest.expanduser()
    if rules_dest:
        rules_dest = rules_dest.expanduser()
    if skills_dest:
        skills_dest = skills_dest.expanduser()

    # Determine if using split mode
    has_split_args = agents_dest or rules_dest or skills_dest

    # If --split flag used, require at least one split destination
    if split and not has_split_args:
        log_error("--split requires at least one of: --agents-dest, --rules-dest, --skills-dest")
        raise typer.Exit(code=1) from None

    # If split args provided without --split flag, treat as split mode
    if has_split_args:
        split = True

    # Validate mutual exclusivity: dest XOR split destinations
    if dest and split:
        log_error(
            "Cannot use positional destination with split destination arguments "
            "(--agents-dest, --rules-dest, --skills-dest)"
        )
        log_error(
            "Use either positional DEST for unified deployment OR --split with separate directories"
        )
        raise typer.Exit(code=1) from None

    # Validate that at least one destination is provided
    if not dest and not split:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Validate split destination dependencies and directory existence
    if split:
        is_valid, errors = validate_split_destinations(
            agents_dest, rules_dest, skills_dest, force=force
        )
        if not is_valid:
            for error in errors:
                log_error(error)
            raise typer.Exit(code=1) from None

    # Deploy
    success = deploy_rules(
        project_root=project_root,
        dest=dest,
        agents_dest=agents_dest,
        rules_dest=rules_dest,
        skills_dest=skills_dest,
        skip_skills=skip_skills,
        only_skills=only_skills,
        dry_run=dry_run,
        verbose=actual_verbose,
        no_mode=no_mode,
    )

    if not success:
        raise typer.Exit(code=1) from None
