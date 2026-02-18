#!/usr/bin/env python3
"""Update token budgets for AI coding rule files in rules/ directory.

DEPRECATED: Use 'ai-rules tokens' instead. See: ai-rules --help

This script analyzes all rule files, calculates accurate token estimates,
and updates TokenBudget metadata to reflect current file sizes.

Token Estimation Method:
    Uses tiktoken with GPT-4o encoding (o200k_base) for exact token counts.
    This provides 100% accurate token estimates for GPT-4o models.
    Results are rounded to nearest 50 for cleaner budget numbers.

Default threshold: ±5% (updates triggered when difference exceeds threshold)

Exit codes:
    0: Successfully updated all files
    1: Errors encountered during update
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import tiktoken


@dataclass
class TokenBudgetAnalysis:
    """Analysis result for a single rule file."""

    file_path: Path
    current_budget: int | None
    estimated_tokens: int
    suggested_budget: int
    diff_percentage: float | None
    needs_update: bool
    error: str | None = None

    @property
    def status(self) -> str:
        """Get status string for display."""
        if self.error:
            return "ERROR"
        elif not self.current_budget:
            return "MISSING"
        elif not self.needs_update:
            return "OK"
        elif abs(self.diff_percentage or 0) <= 50:
            return "UPDATE"
        else:
            return "MAJOR"


@dataclass
class UpdateConfig:
    """Configuration for token budget updates."""

    # Minimum difference percentage to trigger update
    update_threshold: float = 5.0
    # Rounding increment for cleaner budget numbers
    rounding_increment: int = 50
    # Dry run mode (don't actually update files)
    dry_run: bool = False
    # Verbose output
    verbose: bool = False


class TokenBudgetUpdater:
    """Updater for token budgets in rule files."""

    def __init__(self, config: UpdateConfig | None = None):
        """Initialize updater with configuration."""
        self.config = config or UpdateConfig()
        self.encoding = tiktoken.encoding_for_model("gpt-4o")

    def estimate_tokens(self, content: str) -> int:
        """Estimate tokens using tiktoken with GPT-4o encoding.

        Args:
            content: File content to analyze

        Returns:
            Exact token count for GPT-4o model
        """
        tokens = self.encoding.encode(content)
        return len(tokens)

    def round_to_increment(self, value: int) -> int:
        """Round value to nearest increment for cleaner numbers.

        Args:
            value: Value to round

        Returns:
            Rounded value
        """
        return int(round(value / self.config.rounding_increment) * self.config.rounding_increment)

    def analyze_file(self, file_path: Path) -> TokenBudgetAnalysis:
        """Analyze a single file's token budget.

        Args:
            file_path: Path to rule file

        Returns:
            TokenBudgetAnalysis with results
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return TokenBudgetAnalysis(
                file_path=file_path,
                current_budget=None,
                estimated_tokens=0,
                suggested_budget=0,
                diff_percentage=None,
                needs_update=False,
                error=f"Failed to read file: {e}",
            )

        # Extract current TokenBudget
        token_match = re.search(r"^\*\*TokenBudget:\*\*\s*~?(\d+)", content, re.MULTILINE)
        current_budget = int(token_match.group(1)) if token_match else None

        # Calculate estimates
        estimated = self.estimate_tokens(content)
        suggested = self.round_to_increment(estimated)

        # Calculate difference
        if current_budget:
            diff_pct = ((estimated - current_budget) / current_budget) * 100
            needs_update = abs(diff_pct) > self.config.update_threshold
        else:
            diff_pct = None
            needs_update = True

        return TokenBudgetAnalysis(
            file_path=file_path,
            current_budget=current_budget,
            estimated_tokens=estimated,
            suggested_budget=suggested,
            diff_percentage=diff_pct,
            needs_update=needs_update,
        )

    def update_file(self, analysis: TokenBudgetAnalysis) -> bool:
        """Update TokenBudget in a file.

        Args:
            analysis: TokenBudgetAnalysis with update information

        Returns:
            True if file was updated, False otherwise
        """
        if not analysis.needs_update:
            return False

        if self.config.dry_run:
            return True

        try:
            content = analysis.file_path.read_text(encoding="utf-8")

            if analysis.current_budget:
                # Replace existing budget
                old_line = f"**TokenBudget:** ~{analysis.current_budget}"
                new_line = f"**TokenBudget:** ~{analysis.suggested_budget}"
                new_content = content.replace(old_line, new_line)
            else:
                # Insert TokenBudget after Keywords (per metadata field order)
                # Find Keywords line and insert after it
                keywords_pattern = r"(^\*\*Keywords:\*\*.*\n)"
                replacement = f"\\1**TokenBudget:** ~{analysis.suggested_budget}\n"
                new_content = re.sub(keywords_pattern, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                analysis.file_path.write_text(new_content, encoding="utf-8")
                return True
            else:
                return False

        except Exception as e:
            print(f"  [ERROR] Failed to update {analysis.file_path.name}: {e}")
            return False

    def analyze_all(self, directory: Path = Path("rules")) -> list[TokenBudgetAnalysis]:
        """Analyze all rule files in directory.

        Args:
            directory: Directory containing rule files

        Returns:
            List of TokenBudgetAnalysis results
        """
        results = []
        for md_file in sorted(directory.glob("*.md")):
            analysis = self.analyze_file(md_file)
            results.append(analysis)
        return results

    def update_all(self, directory: Path = Path("rules")) -> tuple[list[TokenBudgetAnalysis], int]:
        """Update all rule files in directory.

        Args:
            directory: Directory containing rule files

        Returns:
            Tuple of (analyses, update_count)
        """
        analyses = self.analyze_all(directory)
        update_count = 0

        for analysis in analyses:
            if self.update_file(analysis):
                update_count += 1

        return analyses, update_count

    def print_summary(self, analyses: list[TokenBudgetAnalysis], update_count: int) -> None:
        """Print summary of analysis and updates.

        Args:
            analyses: List of TokenBudgetAnalysis results
            update_count: Number of files updated
        """
        print()
        print("=" * 100)
        print("TOKEN BUDGET UPDATE SUMMARY")
        print("=" * 100)
        print()

        # Statistics
        total = len(analyses)
        ok = sum(1 for a in analyses if a.status == "OK")
        updates = sum(1 for a in analyses if a.needs_update and not a.error)
        errors = sum(1 for a in analyses if a.error)
        missing = sum(1 for a in analyses if a.status == "MISSING")

        print(f"Total rule files analyzed: {total}")
        print(f"  [OK]      Within ±{self.config.update_threshold}%: {ok}")
        print(f"  [UPDATE]  Need updating: {updates}")
        print(f"  [MISSING] No budget declared: {missing}")
        print(f"  [ERROR]   Errors: {errors}")
        print()

        if self.config.dry_run:
            print(f"[DRY RUN] Would update {update_count} files")
        else:
            print(f"Files updated: {update_count}")

        print()

    def print_detailed_results(self, analyses: list[TokenBudgetAnalysis]) -> None:
        """Print detailed results for all files.

        Args:
            analyses: List of TokenBudgetAnalysis results
        """
        print()
        print("DETAILED ANALYSIS")
        print("=" * 100)
        print()
        print(
            f"{'File':<45} {'Current':<10} {'Estimated':<10} {'Diff %':<10} {'Suggested':<10} {'Status'}"
        )
        print("-" * 100)

        for analysis in analyses:
            current_str = f"~{analysis.current_budget}" if analysis.current_budget else "MISSING"
            diff_str = (
                f"{analysis.diff_percentage:+.1f}%"
                if analysis.diff_percentage is not None
                else "N/A"
            )
            suggested_str = f"~{analysis.suggested_budget}"

            print(
                f"{analysis.file_path.name:<45} {current_str:<10} {analysis.estimated_tokens:<10} "
                f"{diff_str:<10} {suggested_str:<10} {analysis.status}"
            )

        print()

    def print_update_details(self, analyses: list[TokenBudgetAnalysis]) -> None:
        """Print details for files that were updated.

        Args:
            analyses: List of TokenBudgetAnalysis results
        """
        updates = [a for a in analyses if a.needs_update and not a.error]

        if not updates:
            return

        print()
        print("FILES UPDATED" if not self.config.dry_run else "FILES TO BE UPDATED")
        print("-" * 100)
        print()

        for analysis in updates:
            if analysis.current_budget:
                print(
                    f"  {analysis.file_path.name:<50} "
                    f"~{analysis.current_budget} → ~{analysis.suggested_budget} "
                    f"({analysis.diff_percentage:+.1f}%)"
                )
            else:
                print(f"  {analysis.file_path.name:<50} MISSING → ~{analysis.suggested_budget}")

        print()


def main() -> int:
    """Main entry point for token budget updater."""
    import argparse
    import warnings

    warnings.warn(
        "This script is deprecated. Use 'ai-rules tokens' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    parser = argparse.ArgumentParser(
        description="Update token budgets for AI coding rule files (single file or directory)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate single rule file
  python token_validator.py rules/100-snowflake-core.md

  # Validate single file with dry run
  python token_validator.py rules/200-python-core.md --dry-run --detailed

  # Analyze and update all production rule files
  python token_validator.py rules/

  # Dry run to see what would be updated (directory)
  python token_validator.py rules/ --dry-run

  # Update with custom threshold
  python token_validator.py rules/ --threshold 20

  # Show detailed analysis
  python token_validator.py rules/ --detailed

  # Verbose output with all information
  python token_validator.py rules/ --verbose --detailed
        """,
    )

    parser.add_argument(
        "path",
        type=Path,
        help="Rule file or directory to validate",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=5.0,
        help="Minimum difference percentage to trigger update (default: 5.0)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed analysis for all files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )

    args = parser.parse_args()

    # Verify path exists
    if not args.path.exists():
        print(f"[ERROR] Path not found: {args.path}")
        return 1

    # Create configuration
    config = UpdateConfig(
        update_threshold=args.threshold,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    # Create updater
    updater = TokenBudgetUpdater(config)

    # Handle single file vs directory
    if args.path.is_file():
        # Single file mode
        print()
        print("=" * 100)
        print("TOKEN BUDGET ANALYSIS")
        print("=" * 100)
        print()
        print(f"File: {args.path}")
        print(f"Update threshold: ±{args.threshold:.1f}%")
        print("Token counting: tiktoken (GPT-4o, o200k_base encoding)")
        print(f"Rounding increment: {config.rounding_increment}")
        if args.dry_run:
            print()
            print("[DRY RUN MODE] No files will be modified")
        print()

        # Analyze single file
        analysis = updater.analyze_file(args.path)

        # Display results
        if analysis.error:
            print(f"[ERROR] {analysis.error}")
            return 1

        current_str = f"~{analysis.current_budget}" if analysis.current_budget else "MISSING"
        diff_str = (
            f"{analysis.diff_percentage:+.1f}%" if analysis.diff_percentage is not None else "N/A"
        )

        print(f"Current Budget: {current_str}")
        print(f"Estimated Tokens: {analysis.estimated_tokens}")
        print(f"Suggested Budget: ~{analysis.suggested_budget}")
        print(f"Difference: {diff_str}")
        print(f"Status: {analysis.status}")
        print()

        # Update if needed
        if analysis.needs_update:
            if args.dry_run:
                print(
                    f"[DRY RUN] Would update TokenBudget: {current_str} → ~{analysis.suggested_budget}"
                )
            else:
                if updater.update_file(analysis):
                    print(f"✓ Updated TokenBudget: {current_str} → ~{analysis.suggested_budget}")
                else:
                    print("[ERROR] Failed to update file")
                    return 1
        else:
            print("✓ No update needed (within threshold)")

        print()
        print("=" * 100)
        return 0

    elif args.path.is_dir():
        # Directory mode (existing behavior)
        print()
        print("=" * 100)
        print("TOKEN BUDGET UPDATER")
        print("=" * 100)
        print()
        print(f"Directory: {args.path}")
        print(f"Update threshold: ±{args.threshold:.1f}%")
        print("Token counting: tiktoken (GPT-4o, o200k_base encoding)")
        print(f"Rounding increment: {config.rounding_increment}")
        if args.dry_run:
            print()
            print("[DRY RUN MODE] No files will be modified")

        # Perform updates
        analyses, update_count = updater.update_all(args.path)

        # Print results
        if args.detailed:
            updater.print_detailed_results(analyses)

        if args.verbose or update_count > 0:
            updater.print_update_details(analyses)

        updater.print_summary(analyses, update_count)

        # Print recommendations
        if not args.dry_run and update_count > 0:
            print("=" * 100)
            print("NEXT STEPS")
            print("=" * 100)
            print()
            print("1. Review changes: git diff rules/")
            print("2. Validate updates: python scripts/schema_validator.py rules/")
            print("3. Commit changes with descriptive message")
            print()

        return 0

    else:
        print(f"[ERROR] Path is neither a file nor directory: {args.path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
