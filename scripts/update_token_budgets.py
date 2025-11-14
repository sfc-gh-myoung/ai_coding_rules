#!/usr/bin/env python3
"""
Update token budgets for AI coding rule files in templates/ directory.

This script analyzes all rule files, calculates accurate token estimates,
and updates TokenBudget metadata to reflect current file sizes.

Token Estimation Method:
    Uses word count method with 1.3 tokens per word multiplier, which
    provides more accurate estimates than line count for markdown files.
    Results are rounded to nearest 50 for cleaner budget numbers.

Default threshold: ±15% (updates triggered when difference exceeds threshold)

Exit codes:
    0: Successfully updated all files
    1: Errors encountered during update
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


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
    update_threshold: float = 30.0
    # Token estimation multiplier (tokens per word)
    tokens_per_word: float = 1.3
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

    def estimate_tokens(self, content: str) -> int:
        """Estimate tokens using word count method.

        Args:
            content: File content to analyze

        Returns:
            Estimated token count
        """
        word_count = len(content.split())
        return int(word_count * self.config.tokens_per_word)

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

    def analyze_all(self, directory: Path = Path("templates")) -> list[TokenBudgetAnalysis]:
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

    def update_all(
        self, directory: Path = Path("templates")
    ) -> tuple[list[TokenBudgetAnalysis], int]:
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

        print(f"Total files analyzed: {total}")
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

    parser = argparse.ArgumentParser(
        description="Update token budgets for AI coding rule files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and update all template files
  python update_token_budgets.py

  # Dry run to see what would be updated
  python update_token_budgets.py --dry-run

  # Update with custom threshold
  python update_token_budgets.py --threshold 20

  # Show detailed analysis
  python update_token_budgets.py --detailed

  # Verbose output with all information
  python update_token_budgets.py --verbose --detailed
        """,
    )

    parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        default=Path("templates"),
        help="Directory containing rule files (default: templates/)",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=15.0,
        help="Minimum difference percentage to trigger update (default: 15.0)",
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

    # Verify directory exists
    if not args.directory.exists():
        print(f"[ERROR] Directory not found: {args.directory}")
        return 1

    # Create configuration
    config = UpdateConfig(
        update_threshold=args.threshold,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    # Create updater
    updater = TokenBudgetUpdater(config)

    # Print header
    print()
    print("=" * 100)
    print("TOKEN BUDGET UPDATER")
    print("=" * 100)
    print()
    print(f"Directory: {args.directory}")
    print(f"Update threshold: ±{args.threshold:.1f}%")
    print(f"Tokens per word: {config.tokens_per_word}")
    print(f"Rounding increment: {config.rounding_increment}")
    if args.dry_run:
        print()
        print("[DRY RUN MODE] No files will be modified")

    # Perform updates
    analyses, update_count = updater.update_all(args.directory)

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
        print("1. Review changes: git diff templates/")
        print("2. Validate updates: python scripts/validate_agent_rules.py")
        print("3. Regenerate rules: task rule:generate")
        print("4. Commit changes with descriptive message")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
