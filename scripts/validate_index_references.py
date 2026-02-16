#!/usr/bin/env python3
"""Validate that all rule references in RULES_INDEX.md map to actual files.

DEPRECATED: Use 'ai-rules refs' instead. See: ai-rules --help

This script ensures 100% mapping between:
1. Rule filenames referenced in RULES_INDEX.md → actual files in rules/
2. Rule files in rules/ → referenced in RULES_INDEX.md (optional orphan check)

Usage:
    python scripts/validate_index_references.py [--check-orphans] [--verbose]

    --check-orphans: Also report rules that exist but aren't referenced
    --verbose: Show all references found, not just errors

Exit codes:
    0: All references valid
    1: One or more broken references found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

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
        print(f"\n📋 References found in {index_path.name}: {len(referenced)}")
        print(f"📁 Rule files found in {rules_dir}: {len(actual)}")

    # Find broken references (referenced but don't exist)
    broken_refs = sorted(referenced - actual)

    # Find orphaned files (exist but not referenced)
    orphaned_files = sorted(actual - referenced) if check_orphans else []

    return broken_refs, orphaned_files


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 = success, 1 = validation failed)
    """
    import warnings

    warnings.warn(
        "This script is deprecated. Use 'ai-rules refs' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    parser = argparse.ArgumentParser(
        description="Validate rule references in RULES_INDEX.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check-orphans",
        action="store_true",
        help="Also report rule files that exist but aren't referenced",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all references found, not just errors",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=Path("RULES_INDEX.md"),
        help="Path to RULES_INDEX.md (default: RULES_INDEX.md)",
    )
    parser.add_argument(
        "--rules-dir",
        type=Path,
        default=Path("rules"),
        help="Path to rules directory (default: rules/)",
    )

    args = parser.parse_args()

    # Validate paths exist
    if not args.index_path.exists():
        print(f"❌ Error: {args.index_path} not found")
        return 1

    if not args.rules_dir.exists():
        print(f"❌ Error: {args.rules_dir} directory not found")
        return 1

    print(f"🔍 Validating references in {args.index_path}...")

    # Run validation
    broken_refs, orphaned_files = validate_references(
        args.index_path,
        args.rules_dir,
        check_orphans=args.check_orphans,
        verbose=args.verbose,
    )

    # Report results
    has_errors = False

    if broken_refs:
        has_errors = True
        print(f"\n❌ BROKEN REFERENCES ({len(broken_refs)}):")
        print("   These files are referenced in RULES_INDEX.md but don't exist:")
        for ref in broken_refs:
            print(f"   - {ref}")

    if orphaned_files:
        print(f"\n⚠️  ORPHANED FILES ({len(orphaned_files)}):")
        print("   These rule files exist but aren't referenced in RULES_INDEX.md:")
        for orphan in orphaned_files:
            print(f"   - {orphan}")

    # Summary
    if has_errors:
        print(f"\n❌ VALIDATION FAILED: {len(broken_refs)} broken reference(s)")
        return 1
    else:
        # Get counts for success message
        referenced = extract_references_from_index(args.index_path)
        actual = get_actual_rule_files(args.rules_dir)
        matched = len(referenced & actual)
        print(f"\n✅ VALIDATION PASSED: {matched} references, all valid")
        if orphaned_files:
            print(f"   (Note: {len(orphaned_files)} rule files not referenced)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
