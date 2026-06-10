"""Deploy production-ready AI coding rules and skills to target projects.

This command copies rules and skills from the source directories to one or more
destinations. All rules and skills are production-ready with no generation step
required.

Deployment is split by artifact: AGENTS.md, rules/, and skills/ each go to their
own destination, so they can be placed wherever a project expects them (for
example, AGENTS.md in a project root with rules/ in a shared ~/.ai-rules/rules
directory). Provide whichever destinations you need:

    - ``--agents-dest``  AGENTS.md (and the bootstrap protocol)
    - ``--rules-dest``   rules/*.md + RULES_INDEX.md + examples/
    - ``--skills-dest``  skills/

Features:
    - Copies rules/*.md to the rules destination
    - Copies skills/ to the skills destination (respects pyproject.toml exclusions)
    - Writes AGENTS.md from the MODE (or NO_MODE) template with path substitution
    - Writes rules/RULES_INDEX.md with path substitution
    - Validates source files exist before copying
    - Supports dry-run mode for safety
    - Provides detailed logging with Rich formatting
"""

from __future__ import annotations

import re
import shutil
import tomllib
from pathlib import Path
from typing import Annotated, NamedTuple

import typer
from rich.tree import Tree

from ai_rules._shared.console import console, log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root

# Sentinel comment lines used in the AGENTS templates to mark MODE-specific and
# NO_MODE-specific regions. They are stripped from the deployed AGENTS.md so the
# output stays clean. (The parity test in tests/templates relies on these too.)
_SENTINEL_LINES = frozenset(
    {
        "<!-- MODE-ONLY:start -->",
        "<!-- MODE-ONLY:end -->",
        "<!-- NO-MODE-ONLY:start -->",
        "<!-- NO-MODE-ONLY:end -->",
    }
)


class DeploymentPaths(NamedTuple):
    """Resolved deployment paths for split deployment."""

    agents: Path | None
    rules: Path | None
    skills: Path | None


def resolve_paths(
    agents_dest: Path | None = None,
    rules_dest: Path | None = None,
    skills_dest: Path | None = None,
) -> DeploymentPaths:
    """Resolve deployment paths to absolute paths.

    Args:
        agents_dest: Destination for AGENTS.md
        rules_dest: Destination for rules/ directory
        skills_dest: Destination for skills/ directory

    Returns:
        DeploymentPaths with resolved absolute paths
    """
    return DeploymentPaths(
        agents=agents_dest.expanduser().resolve() if agents_dest else None,
        rules=rules_dest.expanduser().resolve() if rules_dest else None,
        skills=skills_dest.expanduser().resolve() if skills_dest else None,
    )


def substitute_template(template_content: str, paths: DeploymentPaths) -> str:
    """Replace placeholders with resolved paths.

    When a rules/skills destination is provided, its absolute path is used so the
    deployed AGENTS.md points at the exact location. When no destination is
    provided (for example, AGENTS-only deployment that reuses a project's existing
    rules/ directory), the placeholder falls back to the relative path ``rules`` /
    ``skills`` -- the agent reading AGENTS.md resolves it from the project root.

    Args:
        template_content: Template content with {{rules_path}} and {{skills_path}}
        paths: Resolved deployment paths

    Returns:
        Content with placeholders replaced
    """
    result = template_content
    rules_value = str(paths.rules) if paths.rules else "rules"
    skills_value = str(paths.skills) if paths.skills else "skills"
    result = result.replace("{{rules_path}}", rules_value)
    result = result.replace("{{skills_path}}", skills_value)
    return result


def strip_template_markers(content: str) -> str:
    """Remove the template header marker and MODE sentinel comment lines.

    Drops the leading ``<!-- Template: ... -->`` marker line (and the blank line
    that follows it) and any MODE-ONLY / NO-MODE-ONLY sentinel comment lines, so
    the deployed AGENTS.md does not contain template bookkeeping comments.

    Args:
        content: Raw template content

    Returns:
        Content with marker and sentinel lines removed
    """
    lines = content.split("\n")
    if lines and lines[0].startswith("<!-- Template:"):
        # Skip the marker line and the blank line that follows it.
        lines = lines[2:] if len(lines) > 1 and lines[1] == "" else lines[1:]
    lines = [line for line in lines if line.strip() not in _SENTINEL_LINES]
    return "\n".join(lines)


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


def validate_destinations(
    agents_dest: Path | None,
    rules_dest: Path | None,
    skills_dest: Path | None,
    *,
    force: bool = False,
    only_skills: bool = False,
) -> tuple[bool, list[str]]:
    """Validate destination arguments.

    Args:
        agents_dest: Destination for AGENTS.md
        rules_dest: Destination for rules/
        skills_dest: Destination for skills/
        force: If True, create missing directories without prompting
        only_skills: If True, only skills are deployed (relaxes the
            --skills-dest requires --agents-dest rule)

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Rule: --skills-dest requires --agents-dest (skills are referenced from
    # AGENTS.md). Skipped for --only-skills, which deploys no AGENTS.md.
    if skills_dest and not agents_dest and not only_skills:
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
) -> tuple[int, int]:
    """Copy rule files from source directly to destination.

    Skips RULES_INDEX.md as it's handled separately by copy_root_files().

    Args:
        source_dir: Source rules directory
        dest_dir: Destination directory for rule files
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging

    Returns:
        Tuple of (files_copied, files_failed)
    """
    files_copied = 0
    files_failed = 0

    rule_files = sorted([f for f in source_dir.glob("*.md") if f.name != "RULES_INDEX.md"])

    if not rule_files:
        log_warning(f"No .md files found in {source_dir}")
        return (0, 0)

    if verbose:
        log_info(f"Found {len(rule_files)} rule files to copy")

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            log_info(f"Created destination directory: {dest_dir}")
    elif verbose:
        log_info(f"[dry-run] Would create directory: {dest_dir}")

    for rule_file in rule_files:
        dest_file = dest_dir / rule_file.name
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
    paths: DeploymentPaths,
    dry_run: bool = False,
    verbose: bool = True,
    no_mode: bool = False,
) -> tuple[int, int]:
    """Write AGENTS.md to the agents destination and RULES_INDEX.md to rules dest.

    AGENTS.md is rendered from the MODE (or NO_MODE) template with {{rules_path}} /
    {{skills_path}} substitution and template/sentinel markers stripped.
    RULES_INDEX.md carries a relative `rules/` path; when a rules destination is
    given, that path is rewritten to the absolute deployed location. Each artifact
    is only written when its destination is provided.

    Args:
        project_root: Root directory of the project
        paths: Resolved deployment paths
        dry_run: If True, don't actually write files
        verbose: If True, print detailed logging
        no_mode: If True, use the AGENTS_NO_MODE template

    Returns:
        Tuple of (files_written, files_failed)
    """
    files_written = 0
    files_failed = 0

    # AGENTS.md -> agents destination
    if paths.agents:
        try:
            template_content = load_template(project_root, no_mode=no_mode)
            if template_content is None:
                raise FileNotFoundError(
                    f"AGENTS template not found in {project_root / 'templates'}"
                )
            content = substitute_template(template_content, paths)
            content = strip_template_markers(content)
            dest_file = paths.agents / "AGENTS.md"
            if not dry_run:
                paths.agents.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(content)
                if verbose:
                    log_info(f"Generated: AGENTS.md (path substitution) -> {dest_file}")
            elif verbose:
                log_info(f"[dry-run] Would generate: AGENTS.md -> {dest_file}")
            files_written += 1
        except Exception as e:
            log_error(f"Failed to generate AGENTS.md: {e}")
            files_failed += 1

    # rules/RULES_INDEX.md -> rules destination
    if paths.rules:
        try:
            source_file = project_root / "rules" / "RULES_INDEX.md"
            # RULES_INDEX.md carries the relative `rules/` path (see index generate).
            # Rewrite it to the absolute deployed rules location so the deployed
            # index's read/grep references point at the right directory.
            content = source_file.read_text()
            # Rewrite path-prefix `rules/` to the absolute deployed location.
            # Use negative lookbehind to preserve `dir:rules/` keyword trigger
            # tokens (used by agent grep patterns for directory-match discovery).
            abs_rules = str(paths.rules).rstrip("/") + "/"
            content = re.sub(r"(?<!dir:)rules/", abs_rules, content)
            dest_file = paths.rules / "RULES_INDEX.md"
            if not dry_run:
                paths.rules.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(content)
                if verbose:
                    log_info(f"Generated: RULES_INDEX.md (path substitution) -> {dest_file}")
            elif verbose:
                log_info(f"[dry-run] Would generate: RULES_INDEX.md -> {dest_file}")
            files_written += 1
        except Exception as e:
            log_error(f"Failed to copy rules/RULES_INDEX.md: {e}")
            files_failed += 1

    return (files_written, files_failed)


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
) -> tuple[int, int, int]:
    """Copy skills/ contents directly to destination, respecting exclusions.

    Exclusions are loaded from [tool.rule_deployer] in pyproject.toml.
    Copies both files and directories, skipping excluded items.

    Args:
        project_root: Project root directory
        dest_dir: Destination directory for skills
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging

    Returns:
        Tuple of (skills_count, files_copied, files_failed)
    """
    skills_count = 0
    files_copied = 0
    files_failed = 0

    source_skills_dir = project_root / "skills"

    if not source_skills_dir.exists():
        log_warning(f"Skills directory not found: {source_skills_dir}")
        return (0, 0, 0)

    exclusions = load_skill_exclusions(project_root, verbose=verbose)

    if exclusions and verbose:
        log_info(f"Excluding skills: {', '.join(sorted(exclusions))}")

    if verbose:
        log_info(f"Deploying skills from: {source_skills_dir}")

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            log_info(f"Created destination directory: {dest_dir}")
    elif verbose:
        log_info(f"[dry-run] Would create directory: {dest_dir}")

    for item in source_skills_dir.iterdir():
        if item.name.startswith("."):
            continue

        if item.name in exclusions or (item.is_dir() and f"{item.name}/" in exclusions):
            if verbose:
                log_info(f"Skipping excluded: {item.name}")
            continue

        dest_item = dest_dir / item.name

        try:
            if item.is_file():
                if not dry_run:
                    shutil.copy2(item, dest_item)
                    if verbose:
                        log_info(f"Copied: {item.name} -> {dest_item}")
                elif verbose:
                    log_info(f"[dry-run] Would copy: {item.name} -> {dest_item}")
                skills_count += 1
                files_copied += 1

            elif item.is_dir():
                dir_files = [f for f in item.rglob("*") if f.is_file()]
                if not dry_run:
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    if verbose:
                        log_info(
                            f"Copied directory: {item.name} ({len(dir_files)} files) -> {dest_item}"
                        )
                elif verbose:
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
    only_skills: bool,
    rules_copied: int,
    root_copied: int,
    skills_count: int,
    skills_files_copied: int,
) -> Tree:
    """Build a Rich Tree showing the deployment structure.

    Args:
        paths: Resolved deployment paths
        only_skills: Whether only skills were deployed
        rules_copied: Number of rule files copied
        root_copied: Number of root files written
        skills_count: Number of skills copied
        skills_files_copied: Number of skill files copied

    Returns:
        Rich Tree object for display
    """
    if only_skills:
        tree = Tree("[bold green]Deployment Summary[/bold green]")
        tree.add(
            f"[cyan]skills/[/cyan] -> {paths.skills} ({skills_count} skills, {skills_files_copied} files)"
        )
        return tree

    tree = Tree("[bold green]Deployment Summary[/bold green]")
    if paths.agents:
        tree.add(f"[cyan]AGENTS.md[/cyan] -> {paths.agents}/AGENTS.md")
    if paths.rules:
        tree.add(f"[cyan]rules/[/cyan] -> {paths.rules}/ ({rules_copied} files)")
    else:
        tree.add("[dim]rules/ (not deployed; AGENTS.md uses relative 'rules')[/dim]")
    if paths.skills:
        tree.add(f"[cyan]skills/[/cyan] -> {paths.skills}/ ({skills_count} skills)")
    else:
        tree.add("[dim]skills/ (not deployed; AGENTS.md uses relative 'skills')[/dim]")
    return tree


def deploy_rules(
    project_root: Path,
    agents_dest: Path | None = None,
    rules_dest: Path | None = None,
    skills_dest: Path | None = None,
    skip_skills: bool = False,
    only_skills: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
    no_mode: bool = False,
) -> bool:
    """Deploy rules and skills to their destinations.

    Each artifact (AGENTS.md, rules/, skills/) is deployed to its own destination.
    Provide whichever destinations are needed.

    Args:
        project_root: Project root directory
        agents_dest: Destination for AGENTS.md
        rules_dest: Destination for rules/ directory
        skills_dest: Destination for skills/ directory
        skip_skills: If True, skip deploying skills/ directory
        only_skills: If True, deploy only skills/ directory
        dry_run: If True, don't actually copy files
        verbose: If True, print detailed logging
        no_mode: If True, deploy AGENTS_NO_MODE.md as AGENTS.md

    Returns:
        True if deployment successful, False otherwise
    """
    paths = resolve_paths(agents_dest, rules_dest, skills_dest)

    if verbose:
        log_info(f"Project root: {project_root}")
        if paths.agents:
            log_info(f"  AGENTS.md destination: {paths.agents}")
        if paths.rules:
            log_info(f"  Rules destination: {paths.rules}")
        if paths.skills:
            log_info(f"  Skills destination: {paths.skills}")

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

    # Initialize counters
    rules_copied = 0
    rules_failed = 0
    root_copied = 0
    root_failed = 0
    skills_count = 0
    skills_files_copied = 0
    skills_failed = 0

    if only_skills:
        if verbose:
            log_info("SKILLS-ONLY DEPLOYMENT MODE")
            log_info("Copying skills directory (respecting pyproject.toml exclusions)...")
        if paths.skills:
            skills_count, skills_files_copied, skills_failed = copy_skills(
                project_root, paths.skills, dry_run, verbose
            )
        else:
            log_error("No destination specified for skills (--skills-dest)")
            return False
    else:
        # Copy rules
        if paths.rules:
            if verbose:
                log_info("Copying rule files...")
            rules_copied, rules_failed = copy_rules(
                project_root / "rules",
                paths.rules,
                dry_run,
                verbose,
            )

        # Write AGENTS.md and RULES_INDEX.md
        if paths.agents or paths.rules:
            if verbose:
                log_info("Writing root files (AGENTS.md, rules/RULES_INDEX.md)...")
            root_copied, root_failed = copy_root_files(
                project_root,
                paths,
                dry_run,
                verbose,
                no_mode=no_mode,
            )

        # Copy examples/ subdirectory if it exists (under rules destination)
        examples_src = project_root / "rules" / "examples"
        if examples_src.exists() and examples_src.is_dir() and paths.rules:
            examples_dest = paths.rules / "examples"
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
            if paths.skills:
                if verbose:
                    log_info("Copying skills directory (respecting pyproject.toml exclusions)...")
                skills_count, skills_files_copied, skills_failed = copy_skills(
                    project_root, paths.skills, dry_run, verbose
                )
            elif verbose:
                log_info("Skipping skills deployment (no --skills-dest specified)")
        elif verbose:
            log_info("Skipping skills deployment (--skip-skills flag set)")

    # Summary
    total_files = rules_copied + root_copied + skills_files_copied
    total_failed = rules_failed + root_failed + skills_failed

    console.print()
    console.rule("[bold]Deployment Summary[/bold]")

    tree = build_deployment_tree(
        paths,
        only_skills,
        rules_copied,
        root_copied,
        skills_count,
        skills_files_copied,
    )
    console.print(tree)
    console.print()

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


_UNIFIED_REMOVED_HINT = (
    "Unified deployment (a single positional destination) was removed. "
    "Deploy each artifact to its own destination instead:\n"
    "  ai-rules deploy --agents-dest <dir> --rules-dest <dir>/rules --skills-dest <dir>/skills\n"
    "Use only the destinations you need (for example, --agents-dest alone)."
)


def deploy(
    ctx: typer.Context,
    legacy_dest: Annotated[
        Path | None,
        typer.Argument(
            hidden=True,
            help="(removed) Unified destination. Use --agents-dest/--rules-dest/--skills-dest.",
        ),
    ] = None,
    agents_dest: Annotated[
        Path | None,
        typer.Option(
            "--agents-dest",
            help="Destination directory for AGENTS.md.",
        ),
    ] = None,
    rules_dest: Annotated[
        Path | None,
        typer.Option(
            "--rules-dest",
            help="Destination directory for rules/ (and RULES_INDEX.md, examples/).",
        ),
    ] = None,
    skills_dest: Annotated[
        Path | None,
        typer.Option(
            "--skills-dest",
            help="Destination directory for skills/. Requires --agents-dest.",
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
            help="Deploy only skills/ directory (requires --skills-dest).",
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
    with_mode: Annotated[
        bool,
        typer.Option(
            "--with-mode",
            help="Deploy the PLAN/ACT workflow (AGENTS_MODE). Default is the simplified auto-execute workflow (AGENTS_NO_MODE).",
        ),
    ] = False,
) -> None:
    """Deploy production-ready AI coding rules and skills to target locations.

    Each artifact goes to its own destination, so AGENTS.md, rules/, and skills/
    can live wherever a project expects them. Provide whichever destinations you
    need.

    Examples:
        # Deploy AGENTS.md only (reuses the project's existing rules/ directory)

        ai-rules deploy --agents-dest ~/my-project

        # Deploy everything into one project, each artifact in its place

        ai-rules deploy --agents-dest ~/my-project --rules-dest ~/my-project/rules --skills-dest ~/my-project/skills

        # AGENTS.md in a project, rules/skills shared across projects

        ai-rules deploy --agents-dest ~/my-project --rules-dest ~/.ai-rules/rules --skills-dest ~/.ai-rules/skills

        # Dry run to preview

        ai-rules deploy --agents-dest ~/my-project --rules-dest ~/my-project/rules --dry-run

        # Deploy only skills (for agent configuration directories)

        ai-rules deploy --skills-dest ~/.claude/skills --only-skills

        # Deploy with the PLAN/ACT workflow (AGENTS_MODE)

        ai-rules deploy --agents-dest ~/my-project --with-mode
    """
    actual_verbose = verbose and not quiet

    # Reject the removed unified positional-destination form with a migration hint.
    if legacy_dest is not None:
        log_error(_UNIFIED_REMOVED_HINT)
        raise typer.Exit(code=2) from None

    try:
        project_root = find_project_root()
    except FileNotFoundError:
        log_error("Could not find project root (no pyproject.toml found)")
        raise typer.Exit(code=1) from None

    # Normalize paths
    if agents_dest:
        agents_dest = agents_dest.expanduser()
    if rules_dest:
        rules_dest = rules_dest.expanduser()
    if skills_dest:
        skills_dest = skills_dest.expanduser()

    has_destinations = bool(agents_dest or rules_dest or skills_dest)

    # No destinations: show help (consistent with prior no-arg behavior)
    if not has_destinations:
        console.print(ctx.get_help())
        raise typer.Exit(0)

    # Validate destination dependencies and directory existence
    is_valid, errors = validate_destinations(
        agents_dest, rules_dest, skills_dest, force=force, only_skills=only_skills
    )
    if not is_valid:
        for error in errors:
            log_error(error)
        raise typer.Exit(code=1) from None

    success = deploy_rules(
        project_root=project_root,
        agents_dest=agents_dest,
        rules_dest=rules_dest,
        skills_dest=skills_dest,
        skip_skills=skip_skills,
        only_skills=only_skills,
        dry_run=dry_run,
        verbose=actual_verbose,
        no_mode=not with_mode,
    )

    if not success:
        raise typer.Exit(code=1) from None
