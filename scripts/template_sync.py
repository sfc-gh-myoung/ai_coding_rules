#!/usr/bin/env python3
"""Template synchronization tool for AGENTS.md templates.

This script synchronizes AGENTS.md and AGENTS_NO_MODE.md to their template
versions by replacing hardcoded paths with placeholders.

Usage:
    python scripts/template_sync.py           # Sync templates from source files
    python scripts/template_sync.py --check   # Check if templates are in sync
    python scripts/template_sync.py --reverse # Generate source from templates (for reference)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Template header comment
TEMPLATE_HEADER = """\
<!-- Template: Do not edit directly. Run task templates:sync to regenerate. -->

"""

# Path placeholders
RULES_PLACEHOLDER = "{{rules_path}}"
SKILLS_PLACEHOLDER = "{{skills_path}}"

# Default paths used in source files
DEFAULT_RULES_PATH = "rules"
DEFAULT_SKILLS_PATH = "skills"


def log_info(msg: str) -> None:
    """Print info message."""
    print(f"[INFO] {msg}")


def log_success(msg: str) -> None:
    """Print success message."""
    print(f"[✓] {msg}")


def log_error(msg: str) -> None:
    """Print error message to stderr."""
    print(f"[✗] {msg}", file=sys.stderr)


def log_warning(msg: str) -> None:
    """Print warning message."""
    print(f"[!] {msg}")


def source_to_template(content: str) -> str:
    """Convert source file content to template format.

    Replaces hardcoded paths with placeholders:
    - rules/ -> {{rules_path}}/
    - skills/ -> {{skills_path}}/
    """
    result = content

    # Replace rules/ paths (but not {{rules_path}}/ which would be double-replaced)
    # Match rules/ but not already templated paths
    result = re.sub(r"(?<!\{)rules/", f"{RULES_PLACEHOLDER}/", result)

    # Replace skills/ paths
    result = re.sub(r"(?<!\{)skills/", f"{SKILLS_PLACEHOLDER}/", result)

    # Add template header
    result = TEMPLATE_HEADER + result

    return result


def template_to_source(content: str) -> str:
    """Convert template content back to source format.

    Replaces placeholders with default paths:
    - {{rules_path}}/ -> rules/
    - {{skills_path}}/ -> skills/
    """
    result = content

    # Remove template header if present
    if result.startswith("<!-- Template:"):
        lines = result.split("\n")
        # Skip header line and following blank line
        start_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("<!-- Template:"):
                start_idx = i + 1
                # Skip blank line after header
                if start_idx < len(lines) and lines[start_idx].strip() == "":
                    start_idx += 1
                break
        result = "\n".join(lines[start_idx:])

    # Replace placeholders with default paths
    result = result.replace(f"{RULES_PLACEHOLDER}/", f"{DEFAULT_RULES_PATH}/")
    result = result.replace(f"{SKILLS_PLACEHOLDER}/", f"{DEFAULT_SKILLS_PATH}/")

    return result


def sync_template(source_path: Path, template_path: Path, dry_run: bool = False) -> bool:
    """Sync a source file to its template version.

    Returns True if successful or no changes needed, False on error.
    """
    if not source_path.exists():
        log_error(f"Source file not found: {source_path}")
        return False

    source_content = source_path.read_text()
    template_content = source_to_template(source_content)

    # Check if template exists and compare
    if template_path.exists():
        existing_content = template_path.read_text()
        if existing_content == template_content:
            log_info(f"Template already in sync: {template_path.name}")
            return True

    if dry_run:
        log_info(f"[DRY RUN] Would update: {template_path}")
        return True

    # Write template
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(template_content)
    log_success(f"Updated template: {template_path}")
    return True


def check_template(source_path: Path, template_path: Path) -> bool:
    """Check if a template is in sync with its source.

    Returns True if in sync, False otherwise.
    """
    if not source_path.exists():
        log_error(f"Source file not found: {source_path}")
        return False

    if not template_path.exists():
        log_error(f"Template file not found: {template_path}")
        return False

    source_content = source_path.read_text()
    expected_template = source_to_template(source_content)
    actual_template = template_path.read_text()

    if expected_template == actual_template:
        log_success(f"Template in sync: {template_path.name}")
        return True
    else:
        log_error(f"Template out of sync: {template_path.name}")
        log_info("Run 'task templates:sync' to update")
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synchronize AGENTS.md templates with source files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Sync templates from source files:
    python scripts/template_sync.py

  Check if templates are in sync (for CI):
    python scripts/template_sync.py --check

  Preview sync without making changes:
    python scripts/template_sync.py --dry-run
        """,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if templates are in sync (exit 1 if not)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Determine project root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    # Define source and template mappings
    mappings = [
        (
            project_root / "AGENTS.md",
            project_root / "templates" / "AGENTS_MODE.md.template",
        ),
        (
            project_root / "AGENTS_NO_MODE.md",
            project_root / "templates" / "AGENTS_NO_MODE.md.template",
        ),
    ]

    if args.check:
        # Check mode - verify templates are in sync
        log_info("Checking template synchronization...")
        all_in_sync = True
        for source_path, template_path in mappings:
            if not check_template(source_path, template_path):
                all_in_sync = False

        if all_in_sync:
            log_success("All templates are in sync")
            return 0
        else:
            log_error("Templates are out of sync")
            return 1
    else:
        # Sync mode - update templates from source
        log_info("Synchronizing templates...")
        all_success = True
        for source_path, template_path in mappings:
            if not sync_template(source_path, template_path, args.dry_run):
                all_success = False

        if all_success:
            log_success("Template synchronization complete")
            return 0
        else:
            log_error("Template synchronization failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
