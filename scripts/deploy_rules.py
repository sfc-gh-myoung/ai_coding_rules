#!/usr/bin/env python3
"""
Deploy AI coding rules to target projects with templated AGENTS.md

This script orchestrates the deployment of generated rules to a target project,
automatically updating AGENTS.md paths based on the agent type (cursor, copilot,
cline, universal).

Usage:
    python scripts/deploy_rules.py --agent cursor [--destination /path/to/project]
    python scripts/deploy_rules.py --agent universal --destination ~/my-project
    python scripts/deploy_rules.py --agent cline --dry-run
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

# Agent-specific path mappings
AGENT_PATHS = {
    "cursor": ".cursor/rules",
    "copilot": ".github/copilot/instructions",
    "cline": ".clinerules",
    "universal": "rules",
}

# Agent-specific file extensions
AGENT_EXTENSIONS = {
    "cursor": ".mdc",
    "copilot": ".md",
    "cline": ".md",
    "universal": ".md",
}

AgentType = Literal["cursor", "copilot", "cline", "universal"]


def log_info(message: str) -> None:
    """Print info message to stdout."""
    print(f"[INFO] {message}")


def log_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def log_success(message: str) -> None:
    """Print success message to stdout."""
    print(f"[SUCCESS] {message}")


def find_project_root() -> Path:
    """Find the ai_coding_rules project root directory.

    Looks for the directory containing Taskfile.yml and scripts/generate_agent_rules.py.
    """
    # Start from the script's directory
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent

    # Validate this is the project root
    if not (project_root / "Taskfile.yml").exists():
        log_error(f"Could not find Taskfile.yml in {project_root}")
        sys.exit(1)

    if not (project_root / "scripts" / "generate_agent_rules.py").exists():
        log_error(f"Could not find scripts/generate_agent_rules.py in {project_root}")
        sys.exit(1)

    return project_root


def validate_destination(dest_path: Path, dry_run: bool = False) -> None:
    """Validate the destination directory is suitable for deployment.

    Args:
        dest_path: Target directory path
        dry_run: If True, skip write permission check
    """
    if not dry_run:
        # Check if destination exists and is writable
        if dest_path.exists():
            if not dest_path.is_dir():
                log_error(f"Destination exists but is not a directory: {dest_path}")
                sys.exit(1)
            if not os.access(dest_path, os.W_OK):
                log_error(f"Destination directory is not writable: {dest_path}")
                sys.exit(1)
        else:
            # Try to create it
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                log_info(f"Created destination directory: {dest_path}")
            except Exception as e:
                log_error(f"Could not create destination directory {dest_path}: {e}")
                sys.exit(1)


def generate_rules(
    project_root: Path,
    agent: AgentType,
    temp_dir: Path,
) -> Path:
    """Generate rules to a temporary directory using the existing generator.

    Calls the generate_agent_rules.py script to generate rules for the specified
    agent type into a temporary directory, then returns the path to the generated
    rules based on the agent-specific directory structure.

    Args:
        project_root: Path to ai_coding_rules project root
        agent: Agent type (cursor, copilot, cline, universal)
        temp_dir: Temporary directory for generation

    Returns:
        Path to the generated rules directory within the temp directory
        (e.g., temp_dir/cursor/rules/ for cursor agent)
    """
    log_info(f"Generating {agent} rules to temporary location...")

    generator_script = project_root / "scripts" / "generate_agent_rules.py"
    templates_dir = project_root / "templates"

    # Run the generator
    cmd = [
        sys.executable,
        str(generator_script),
        "--agent",
        agent,
        "--source",
        str(templates_dir),
        "--destination",
        str(temp_dir),
    ]

    try:
        subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        log_info("Rule generation completed successfully")
    except subprocess.CalledProcessError as e:
        log_error(f"Rule generation failed: {e}")
        if e.stdout:
            print(e.stdout, file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(1)

    # The generator creates agent-specific subdirectories
    # e.g., temp_dir/cursor/rules/, temp_dir/universal/, etc.
    if agent == "cursor":
        return temp_dir / "cursor" / "rules"
    elif agent == "copilot":
        return temp_dir / "copilot" / "instructions"
    elif agent == "cline":
        return temp_dir / "cline"
    else:  # universal
        return temp_dir / "universal"


def render_agents_template(
    project_root: Path,
    agent: AgentType,
) -> str:
    """Render AGENTS.md template with agent-specific paths and extensions.

    Args:
        project_root: Path to ai_coding_rules project root
        agent: Agent type for path and extension substitution

    Returns:
        Rendered AGENTS.md content with correct paths and file extensions
    """
    agents_template = project_root / "discovery" / "AGENTS.md"

    if not agents_template.exists():
        log_error(f"AGENTS.md template not found: {agents_template}")
        sys.exit(1)

    log_info("Rendering AGENTS.md template...")

    # Read template
    content = agents_template.read_text(encoding="utf-8")

    # Get target path and extension for this agent
    target_path = AGENT_PATHS[agent]
    target_extension = AGENT_EXTENSIONS[agent]

    # Replace template variable for path
    rendered = content.replace("{rule_path}", target_path)

    # Replace file extensions if not .md (e.g., .mdc for Cursor)
    if target_extension != ".md":
        # Replace all occurrences of .md extension with agent-specific extension
        # Pattern: /NNN-rule-name.md → /NNN-rule-name.mdc (for Cursor)
        # Also handles placeholders like [domain]-core.md and [specialized].md
        # Handles @-mentions: @.cursor/rules/000-global-core.md → @.cursor/rules/000-global-core.mdc
        import re

        # Match .md extension when preceded by:
        # 1. Rule filenames (3 digits + hyphen + name): 000-global-core.md, 101a-streamlit.md
        # 2. Placeholder patterns in brackets with suffix: [domain]-core.md, [specialized].md
        # Excludes: README.md, RULES_INDEX.md, wildcard patterns (*.md), extensions (.mdx, .mdc)
        # Note: Pattern works with or without @ prefix (Cursor @-mentions) or ** (markdown bold)
        rendered = re.sub(
            r"(\d{3}[a-z0-9]*-[a-z0-9-]+|\[[a-z]+\](?:-[a-z-]+)?)\.md(?!\w)",
            rf"\1{target_extension}",
            rendered,
        )

    # Verify no template variables remain
    if "{rule_path}" in rendered:
        log_error("Template rendering incomplete - {rule_path} still present")
        sys.exit(1)

    log_info(f"Template rendered with path: {target_path}, extension: {target_extension}")
    return rendered


def copy_rules(
    source_dir: Path,
    dest_dir: Path,
    dry_run: bool = False,
) -> int:
    """Copy rule files from source to destination.

    Args:
        source_dir: Source directory containing rules
        dest_dir: Destination directory
        dry_run: If True, don't actually copy files

    Returns:
        Number of files that would be/were copied
    """
    if not source_dir.exists():
        log_error(f"Source directory does not exist: {source_dir}")
        sys.exit(1)

    # Find all rule files
    rule_files = list(source_dir.glob("*.md")) + list(source_dir.glob("*.mdc"))

    if not rule_files:
        log_error(f"No rule files found in {source_dir}")
        sys.exit(1)

    log_info(f"Found {len(rule_files)} rule files to copy")

    if dry_run:
        log_info(f"[DRY RUN] Would copy {len(rule_files)} files to {dest_dir}")
        return len(rule_files)

    # Create destination if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    for source_file in rule_files:
        dest_file = dest_dir / source_file.name
        shutil.copy2(source_file, dest_file)

    log_info(f"Copied {len(rule_files)} rule files to {dest_dir}")
    return len(rule_files)


def deploy(
    agent: AgentType,
    destination: Path,
    project_root: Path,
    dry_run: bool = False,
) -> None:
    """Deploy rules with rendered AGENTS.md to target project.

    Args:
        agent: Agent type (cursor, copilot, cline, universal)
        destination: Target directory for deployment
        project_root: Path to ai_coding_rules project root
        dry_run: If True, preview without writing files
    """
    log_info(f"Starting deployment: agent={agent}, destination={destination}")

    # Validate destination
    validate_destination(destination, dry_run=dry_run)

    # Use a temporary directory for generation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Generate rules to temp location
        generated_rules_dir = generate_rules(project_root, agent, temp_path)

        # Determine target path within destination
        target_rules_dir = destination / AGENT_PATHS[agent]

        # Copy rules to target
        num_files = copy_rules(generated_rules_dir, target_rules_dir, dry_run=dry_run)

        # Render AGENTS.md template
        rendered_agents = render_agents_template(project_root, agent)

        # Write AGENTS.md to destination root
        agents_dest = destination / "AGENTS.md"
        if dry_run:
            log_info(f"[DRY RUN] Would write AGENTS.md to {agents_dest}")
        else:
            agents_dest.write_text(rendered_agents, encoding="utf-8")
            log_info(f"Wrote AGENTS.md to {agents_dest}")

        # Copy RULES_INDEX.md to destination root
        rules_index_source = project_root / "discovery" / "RULES_INDEX.md"
        rules_index_dest = destination / "RULES_INDEX.md"

        if rules_index_source.exists():
            if dry_run:
                log_info(f"[DRY RUN] Would copy RULES_INDEX.md to {rules_index_dest}")
            else:
                shutil.copy2(rules_index_source, rules_index_dest)
                log_info(f"Copied RULES_INDEX.md to {rules_index_dest}")
        else:
            log_error(f"RULES_INDEX.md not found: {rules_index_source}")

    # Display summary
    log_success("Deployment completed successfully!")
    print()
    print("Deployment Summary:")
    print(f"  Agent Type: {agent}")
    print(f"  Destination: {destination}")
    print(f"  Rules Location: {target_rules_dir}")
    print(f"  Rules Count: {num_files} files")
    print(f"  AGENTS.md: {agents_dest}")
    print(f"  RULES_INDEX.md: {rules_index_dest}")
    print()
    print("Next Steps:")
    print(f"  1. Verify rules are in {target_rules_dir}")
    print(f"  2. Confirm AGENTS.md paths reference {AGENT_PATHS[agent]}")
    print("  3. Configure your AI assistant to use these rules")


def main() -> None:
    """CLI entry point for rule deployment."""
    parser = argparse.ArgumentParser(
        description="Deploy AI coding rules with templated AGENTS.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        choices=["cursor", "copilot", "cline", "universal"],
        help="Target agent type",
    )

    parser.add_argument(
        "--destination",
        type=str,
        default=None,
        help="Target directory for deployment (defaults to current directory)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deployment without writing files",
    )

    args = parser.parse_args()

    # Find project root
    project_root = find_project_root()
    log_info(f"Project root: {project_root}")

    # Determine destination
    destination = Path(args.destination).resolve() if args.destination else Path.cwd()

    # Perform deployment
    deploy(
        agent=args.agent,
        destination=destination,
        project_root=project_root,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
