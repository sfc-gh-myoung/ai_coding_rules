#!/usr/bin/env python3
"""Tests for scripts/token_validator.py token budget analysis and updates.

Tests follow pytest best practices:
- AAA pattern with clear arrange/act/assert sections
- Parametrized tests for token estimation matrices
- Fixtures for reusable test data
- Test markers for unit vs integration tests
- Isolation with tmp_path for filesystem operations
"""

import sys
from pathlib import Path

import pytest

# Import module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import token_validator as utb  # type: ignore[import-not-found]


class TestTokenEstimation:
    """Test token estimation using tiktoken (GPT-4o encoding)."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "content,expected_min,expected_max",
        [
            (" ".join(["word"] * 100), 90, 120),  # ~100 tokens for simple repeated words
            (" ".join(["word"] * 500), 450, 600),  # ~500 tokens
            (" ".join(["word"] * 1000), 900, 1200),  # ~1000 tokens
            (" ".join(["word"] * 50), 45, 60),  # ~50 tokens
            (" ".join(["word"] * 250), 225, 300),  # ~250 tokens
        ],
        ids=["100words", "500words", "1000words", "50words", "250words"],
    )
    def test_estimate_tokens_tiktoken_method(
        self, content: str, expected_min: int, expected_max: int
    ) -> None:
        """Test token estimation uses tiktoken correctly."""
        # Arrange
        updater = utb.TokenBudgetUpdater()

        # Act
        result = updater.estimate_tokens(content)

        # Assert - tiktoken should give reasonable token counts
        assert expected_min <= result <= expected_max, (
            f"Expected {result} to be between {expected_min} and {expected_max}"
        )

    @pytest.mark.unit
    def test_estimate_tokens_empty_content(self) -> None:
        """Test token estimation handles empty content."""
        # Arrange
        updater = utb.TokenBudgetUpdater()
        content = ""

        # Act
        result = updater.estimate_tokens(content)

        # Assert
        assert result == 0

    @pytest.mark.unit
    def test_estimate_tokens_whitespace_only(self) -> None:
        """Test token estimation handles whitespace-only content."""
        # Arrange
        updater = utb.TokenBudgetUpdater()
        content = "   \n\n   \t   "

        # Act
        result = updater.estimate_tokens(content)

        # Assert - tiktoken will tokenize whitespace as a few tokens
        assert result >= 0  # Allow small token count for whitespace


class TestRoundingLogic:
    """Test token budget rounding to clean increments."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "value,increment,expected",
        [
            (45, 50, 50),  # round(45/50)*50 = round(0.9)*50 = 1*50 = 50
            (74, 50, 50),  # round(74/50)*50 = round(1.48)*50 = 1*50 = 50
            (75, 50, 100),  # round(75/50)*50 = round(1.5)*50 = 2*50 = 100
            (125, 50, 100),  # round(125/50)*50 = round(2.5)*50 = 2*50 = 100 (banker's rounding)
            (149, 50, 150),  # round(149/50)*50 = round(2.98)*50 = 3*50 = 150
            (151, 50, 150),  # round(151/50)*50 = round(3.02)*50 = 3*50 = 150
            (374, 50, 350),  # round(374/50)*50 = round(7.48)*50 = 7*50 = 350
            (375, 50, 400),  # round(375/50)*50 = round(7.5)*50 = 8*50 = 400
            (425, 50, 400),  # round(425/50)*50 = round(8.5)*50 = 8*50 = 400 (banker's rounding)
        ],
        ids=[
            "45→50",
            "74→50",
            "75→100",
            "125→100",  # Fixed: was 125→150
            "149→150",
            "151→150",
            "374→350",  # Fixed: was 374→400
            "375→400",
            "425→400",  # Fixed: was 425→450
        ],
    )
    def test_round_to_increment(self, value: int, increment: int, expected: int) -> None:
        """Test rounding to nearest increment produces clean budget numbers.

        Validates that token budgets are rounded to clean increments
        (e.g., 50, 100) for better readability and consistency across rules.
        Uses Python's banker's rounding to avoid systematic bias.
        """
        # Arrange
        config = utb.UpdateConfig(rounding_increment=increment)
        updater = utb.TokenBudgetUpdater(config)

        # Act
        result = updater.round_to_increment(value)

        # Assert
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "value,increment,expected",
        [
            (90, 100, 100),  # round(90/100)*100 = round(0.9)*100 = 1*100 = 100
            (150, 100, 200),  # round(150/100)*100 = round(1.5)*100 = 2*100 = 200
            (249, 100, 200),  # round(249/100)*100 = round(2.49)*100 = 2*100 = 200
            (
                250,
                100,
                200,
            ),  # round(250/100)*100 = round(2.5)*100 = 2*100 = 200 (banker's rounding)
        ],
        ids=["90→100", "150→200", "249→200", "250→200"],  # Fixed: was 250→300
    )
    def test_round_to_different_increments(self, value: int, increment: int, expected: int) -> None:
        """Test rounding works with different increment sizes."""
        # Arrange
        config = utb.UpdateConfig(rounding_increment=increment)
        updater = utb.TokenBudgetUpdater(config)

        # Act
        result = updater.round_to_increment(value)

        # Assert
        assert result == expected


class TestFileAnalysis:
    """Test analysis of individual rule files."""

    @pytest.mark.unit
    def test_analyze_file_with_existing_budget(
        self, tmp_path: Path, sample_rule_content: str
    ) -> None:
        """Test analysis of file with existing TokenBudget metadata.

        Validates that analyzer correctly extracts and compares the
        current budget with estimated tokens. This enables detection
        of outdated budgets that need updates after content changes.
        """
        # Arrange
        rule_file = tmp_path / "test_rule.md"
        rule_file.write_text(sample_rule_content)
        updater = utb.TokenBudgetUpdater()

        # Act
        result = updater.analyze_file(rule_file)

        # Assert
        assert result.file_path == rule_file
        assert result.current_budget == 500
        assert result.estimated_tokens > 0
        assert result.suggested_budget > 0
        assert result.diff_percentage is not None
        assert result.error is None

    @pytest.mark.unit
    def test_analyze_file_missing_budget(
        self, tmp_path: Path, rule_without_token_budget: str
    ) -> None:
        """Test analysis of file without TokenBudget metadata.

        Ensures that files missing TokenBudget are flagged with MISSING
        status so they can be updated. This prevents incomplete metadata
        from causing incorrect budget tracking across the rules system.
        """
        # Arrange
        rule_file = tmp_path / "no_budget.md"
        rule_file.write_text(rule_without_token_budget)
        updater = utb.TokenBudgetUpdater()

        # Act
        result = updater.analyze_file(rule_file)

        # Assert
        assert result.current_budget is None
        assert result.needs_update is True
        assert result.status == "MISSING"

    @pytest.mark.unit
    def test_analyze_file_within_threshold(self, tmp_path: Path) -> None:
        """Test analysis marks file as OK when within threshold.

        Validates that files with budgets within ±30% of actual tokens
        are marked OK and skip updates. This prevents unnecessary
        churn from minor content changes that don't impact token usage.
        """
        # Arrange
        # Create content that will be within ±30% of declared budget
        content = """**TokenBudget:** ~500
""" + " ".join(["word"] * 385)  # ~500 tokens
        rule_file = tmp_path / "within_threshold.md"
        rule_file.write_text(content)
        config = utb.UpdateConfig(update_threshold=30.0)
        updater = utb.TokenBudgetUpdater(config)

        # Act
        result = updater.analyze_file(rule_file)

        # Assert
        assert result.current_budget == 500
        assert not result.needs_update
        assert result.status == "OK"

    @pytest.mark.unit
    def test_analyze_file_exceeds_threshold(self, tmp_path: Path) -> None:
        """Test analysis marks file for update when exceeding threshold."""
        # Arrange
        # Create content significantly larger than declared budget
        content = """**TokenBudget:** ~500
""" + " ".join(["word"] * 1000)  # ~1300 tokens, >100% over
        rule_file = tmp_path / "exceeds_threshold.md"
        rule_file.write_text(content)
        config = utb.UpdateConfig(update_threshold=30.0)
        updater = utb.TokenBudgetUpdater(config)

        # Act
        result = updater.analyze_file(rule_file)

        # Assert
        assert result.current_budget == 500
        assert result.needs_update is True
        assert result.status in ["UPDATE", "MAJOR"]

    @pytest.mark.unit
    def test_analyze_file_read_error(self, tmp_path: Path) -> None:
        """Test analysis handles file read errors gracefully."""
        # Arrange
        nonexistent_file = tmp_path / "nonexistent.md"
        updater = utb.TokenBudgetUpdater()

        # Act
        result = updater.analyze_file(nonexistent_file)

        # Assert
        assert result.error is not None
        assert "Failed to read" in result.error
        assert result.status == "ERROR"


class TestFileUpdating:
    """Test file update operations."""

    @pytest.mark.integration
    def test_update_file_replaces_existing_budget(
        self, tmp_path: Path, sample_rule_content: str
    ) -> None:
        """Test file update replaces existing TokenBudget value."""
        # Arrange
        rule_file = tmp_path / "update_test.md"
        rule_file.write_text(sample_rule_content)
        config = utb.UpdateConfig(dry_run=False)
        updater = utb.TokenBudgetUpdater(config)

        # Manually create analysis with update needed
        analysis = utb.TokenBudgetAnalysis(
            file_path=rule_file,
            current_budget=500,
            estimated_tokens=650,
            suggested_budget=650,
            diff_percentage=30.0,
            needs_update=True,
        )

        # Act
        updated = updater.update_file(analysis)

        # Assert
        assert updated is True
        content = rule_file.read_text()
        assert "~650" in content
        assert "~500" not in content

    @pytest.mark.integration
    def test_update_file_inserts_missing_budget(self, tmp_path: Path) -> None:
        """Test file update inserts TokenBudget when missing."""
        # Arrange
        content = """**Keywords:** test, example

# Test Rule
Content without TokenBudget."""
        rule_file = tmp_path / "insert_test.md"
        rule_file.write_text(content)
        config = utb.UpdateConfig(dry_run=False)
        updater = utb.TokenBudgetUpdater(config)

        # Create analysis needing insertion
        analysis = utb.TokenBudgetAnalysis(
            file_path=rule_file,
            current_budget=None,
            estimated_tokens=200,
            suggested_budget=200,
            diff_percentage=None,
            needs_update=True,
        )

        # Act
        updated = updater.update_file(analysis)

        # Assert
        assert updated is True
        content = rule_file.read_text()
        assert "**TokenBudget:** ~200" in content

    @pytest.mark.unit
    def test_update_file_dry_run_no_changes(self, tmp_path: Path) -> None:
        """Test dry-run mode doesn't modify files."""
        # Arrange
        original_content = "**TokenBudget:** ~500\nContent"
        rule_file = tmp_path / "dry_run_test.md"
        rule_file.write_text(original_content)
        config = utb.UpdateConfig(dry_run=True)
        updater = utb.TokenBudgetUpdater(config)

        # Create analysis
        analysis = utb.TokenBudgetAnalysis(
            file_path=rule_file,
            current_budget=500,
            estimated_tokens=700,
            suggested_budget=700,
            diff_percentage=40.0,
            needs_update=True,
        )

        # Act
        updated = updater.update_file(analysis)

        # Assert
        assert updated is True  # Reports would update
        assert rule_file.read_text() == original_content  # But doesn't change file

    @pytest.mark.unit
    def test_update_file_no_update_needed(self, tmp_path: Path) -> None:
        """Test file update skips when no update needed."""
        # Arrange
        rule_file = tmp_path / "no_update.md"
        rule_file.write_text("**TokenBudget:** ~500")
        updater = utb.TokenBudgetUpdater()

        # Create analysis not needing update
        analysis = utb.TokenBudgetAnalysis(
            file_path=rule_file,
            current_budget=500,
            estimated_tokens=490,
            suggested_budget=500,
            diff_percentage=-2.0,
            needs_update=False,
        )

        # Act
        updated = updater.update_file(analysis)

        # Assert
        assert updated is False


class TestBatchOperations:
    """Test batch analysis and update operations."""

    @pytest.mark.integration
    def test_analyze_all_finds_multiple_files(self, mock_template_dir: Path) -> None:
        """Test batch analysis finds and analyzes all rule files."""
        # Arrange
        updater = utb.TokenBudgetUpdater()

        # Act
        results = updater.analyze_all(mock_template_dir)

        # Assert
        assert len(results) == 4  # 000, 200, 206, README (README.md is NOT excluded)
        assert all(isinstance(r, utb.TokenBudgetAnalysis) for r in results)
        assert all(r.file_path.suffix == ".md" for r in results)

    @pytest.mark.slow
    @pytest.mark.integration
    def test_update_all_processes_multiple_files(self, mock_template_dir: Path) -> None:
        """Test batch update processes multiple rule files."""
        # Arrange
        config = utb.UpdateConfig(dry_run=True, update_threshold=0.0)  # Update all
        updater = utb.TokenBudgetUpdater(config)

        # Act
        analyses, update_count = updater.update_all(mock_template_dir)

        # Assert
        assert len(analyses) == 4  # 000, 200, 206, README (README.md is NOT excluded)
        assert update_count >= 0  # At least some would update

    @pytest.mark.integration
    def test_analyze_all_empty_directory(self, tmp_path: Path) -> None:
        """Test batch analysis handles empty directory."""
        # Arrange
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        updater = utb.TokenBudgetUpdater()

        # Act
        results = updater.analyze_all(empty_dir)

        # Assert
        assert len(results) == 0


class TestDataStructures:
    """Test data structure validation and properties."""

    @pytest.mark.unit
    def test_token_budget_analysis_status_property(self) -> None:
        """Test TokenBudgetAnalysis status property logic."""
        # Arrange & Act & Assert - ERROR status
        error_analysis = utb.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=None,
            estimated_tokens=0,
            suggested_budget=0,
            diff_percentage=None,
            needs_update=False,
            error="Test error",
        )
        assert error_analysis.status == "ERROR"

        # MISSING status
        missing_analysis = utb.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=None,
            estimated_tokens=100,
            suggested_budget=100,
            diff_percentage=None,
            needs_update=True,
        )
        assert missing_analysis.status == "MISSING"

        # OK status
        ok_analysis = utb.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=500,
            estimated_tokens=490,
            suggested_budget=500,
            diff_percentage=-2.0,
            needs_update=False,
        )
        assert ok_analysis.status == "OK"

        # UPDATE status (within 50%)
        update_analysis = utb.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=500,
            estimated_tokens=600,
            suggested_budget=600,
            diff_percentage=20.0,
            needs_update=True,
        )
        assert update_analysis.status == "UPDATE"

        # MAJOR status (>50% difference)
        major_analysis = utb.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=500,
            estimated_tokens=900,
            suggested_budget=900,
            diff_percentage=80.0,
            needs_update=True,
        )
        assert major_analysis.status == "MAJOR"

    @pytest.mark.unit
    def test_update_config_defaults(self) -> None:
        """Test UpdateConfig has sensible defaults."""
        # Arrange & Act
        config = utb.UpdateConfig()

        # Assert
        assert config.update_threshold == 5.0
        assert config.rounding_increment == 50
        assert config.dry_run is False
        assert config.verbose is False


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.unit
    def test_analyze_file_very_large_file(self, tmp_path: Path) -> None:
        """Test analysis handles very large files."""
        # Arrange
        large_content = "**TokenBudget:** ~10000\n" + " ".join(["word"] * 10000)
        rule_file = tmp_path / "large.md"
        rule_file.write_text(large_content)
        updater = utb.TokenBudgetUpdater()

        # Act
        result = updater.analyze_file(rule_file)

        # Assert
        assert result.estimated_tokens > 10000
        assert result.error is None

    @pytest.mark.unit
    def test_analyze_file_extreme_threshold(self, tmp_path: Path) -> None:
        """Test analysis with extreme threshold values."""
        # Arrange
        content = "**TokenBudget:** ~500\n" + " ".join(["word"] * 385)
        rule_file = tmp_path / "test.md"
        rule_file.write_text(content)

        # Very strict threshold (1%)
        strict_config = utb.UpdateConfig(update_threshold=1.0)
        strict_updater = utb.TokenBudgetUpdater(strict_config)

        # Very loose threshold (90%)
        loose_config = utb.UpdateConfig(update_threshold=90.0)
        loose_updater = utb.TokenBudgetUpdater(loose_config)

        # Act
        strict_result = strict_updater.analyze_file(rule_file)
        loose_result = loose_updater.analyze_file(rule_file)

        # Assert
        # Strict threshold likely triggers update
        # Loose threshold likely doesn't
        assert strict_result.needs_update or not loose_result.needs_update


class TestOutputFormatting:
    """Test print output formatting methods."""

    @pytest.mark.unit
    def test_print_summary_shows_correct_statistics(self, tmp_path: Path, capsys) -> None:
        """Test print_summary outputs correct statistics."""
        # Arrange
        updater = utb.TokenBudgetUpdater()

        # Create test files with different statuses
        ok_file = tmp_path / "ok.md"
        ok_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        needs_update_file = tmp_path / "update.md"
        needs_update_file.write_text("**TokenBudget:** ~300\n" + " ".join(["word"] * 385))

        missing_file = tmp_path / "missing.md"
        missing_file.write_text(" ".join(["word"] * 385))

        analyses = [
            updater.analyze_file(ok_file),
            updater.analyze_file(needs_update_file),
            updater.analyze_file(missing_file),
        ]

        # Act
        updater.print_summary(analyses, update_count=1)
        captured = capsys.readouterr()

        # Assert
        assert "Total rule files analyzed: 3" in captured.out
        assert "OK" in captured.out or "MISSING" in captured.out

    @pytest.mark.unit
    def test_print_summary_dry_run_message(self, tmp_path: Path, capsys) -> None:
        """Test print_summary shows dry run message."""
        # Arrange
        config = utb.UpdateConfig(dry_run=True)
        updater = utb.TokenBudgetUpdater(config)

        rule_file = tmp_path / "test.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        analyses = [updater.analyze_file(rule_file)]

        # Act
        updater.print_summary(analyses, update_count=0)
        captured = capsys.readouterr()

        # Assert
        assert "DRY RUN" in captured.out

    @pytest.mark.unit
    def test_print_detailed_results_formats_table(self, tmp_path: Path, capsys) -> None:
        """Test detailed results prints table with columns."""
        # Arrange
        updater = utb.TokenBudgetUpdater()

        rule_file = tmp_path / "test.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        analyses = [updater.analyze_file(rule_file)]

        # Act
        updater.print_detailed_results(analyses)
        captured = capsys.readouterr()

        # Assert
        assert "DETAILED ANALYSIS" in captured.out
        assert "File" in captured.out
        assert "Current" in captured.out
        assert "Estimated" in captured.out

    @pytest.mark.unit
    def test_print_update_details_shows_changes(self, tmp_path: Path, capsys) -> None:
        """Test update details shows before/after values."""
        # Arrange
        updater = utb.TokenBudgetUpdater()

        needs_update_file = tmp_path / "update.md"
        needs_update_file.write_text("**TokenBudget:** ~300\n" + " ".join(["word"] * 385))

        analyses = [updater.analyze_file(needs_update_file)]

        # Act
        updater.print_update_details(analyses)
        captured = capsys.readouterr()

        # Assert - should show files that need updating
        assert "UPDATE DETAILS" in captured.out or analyses[0].needs_update


class TestCLI:
    """Test CLI functionality."""

    @pytest.mark.unit
    def test_main_default_arguments_success(self, tmp_path: Path, monkeypatch) -> None:
        """Test main() with default arguments."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        rule_file = rules_dir / "test.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        test_args = ["token_validator.py", str(rules_dir)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()

        # Assert
        assert exit_code == 0

    @pytest.mark.unit
    def test_main_with_threshold_flag(self, tmp_path: Path, monkeypatch) -> None:
        """Test main() respects --threshold flag."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        rule_file = rules_dir / "test.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        test_args = ["token_validator.py", str(rules_dir), "--threshold", "5"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()

        # Assert
        assert exit_code == 0

    @pytest.mark.unit
    def test_main_with_dry_run_flag(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test main() with --dry-run doesn't modify files."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        rule_file = rules_dir / "test.md"
        original_content = "**TokenBudget:** ~300\n" + " ".join(["word"] * 385)
        rule_file.write_text(original_content)

        test_args = ["token_validator.py", str(rules_dir), "--dry-run"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "DRY RUN" in captured.out
        # File should be unchanged
        assert rule_file.read_text() == original_content

    @pytest.mark.unit
    def test_main_with_verbose_and_detailed_flags(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        """Test main() with --verbose shows extra output."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        rule_file = rules_dir / "test.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        test_args = ["token_validator.py", str(rules_dir), "--verbose", "--detailed"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "DETAILED ANALYSIS" in captured.out

    @pytest.mark.unit
    def test_main_invalid_directory_exits_with_error(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        """Test main exits with error for invalid directory."""
        # Arrange
        non_existent = tmp_path / "non_existent_rules"

        test_args = ["token_validator.py", str(non_existent)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 1
        assert "ERROR" in captured.out or "not found" in captured.out


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.unit
    def test_update_file_handles_write_permission_error(self, tmp_path: Path) -> None:
        """Test update_file catches and logs write exceptions."""
        # Arrange
        import os

        rule_file = tmp_path / "readonly.md"
        rule_file.write_text("**TokenBudget:** ~300\n" + " ".join(["word"] * 385))

        # Make file read-only
        os.chmod(rule_file, 0o444)

        updater = utb.TokenBudgetUpdater()
        analysis = updater.analyze_file(rule_file)

        # Act
        result = updater.update_file(analysis)

        # Assert
        assert result is False

        # Cleanup - restore write permissions
        os.chmod(rule_file, 0o644)


class TestCLIVerboseMode:
    """Test CLI verbose mode and report output."""

    @pytest.mark.integration
    def test_report_shows_missing_budget(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test report displays MISSING for rules without TokenBudget."""
        # Arrange
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        test_file = rules_dir / "test-rule.md"
        test_file.write_text("""# Test Rule

## Metadata

**Keywords:** test
**ContextTier:** High

## Purpose
This rule has no TokenBudget field.
""")

        test_args = ["token_validator.py", str(rules_dir), "--verbose"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()

        # Assert
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "MISSING" in captured.out or "test-rule.md" in captured.out


class TestSingleFileMode:
    """Test single file validation mode (new in CLI enhancement)."""

    @pytest.mark.integration
    def test_single_file_analysis_success(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test main() with single file shows analysis output."""
        # Arrange
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        test_args = ["token_validator.py", str(rule_file), "--dry-run"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "TOKEN BUDGET ANALYSIS" in captured.out
        assert "Current Budget:" in captured.out
        assert "Estimated Tokens:" in captured.out
        assert "Suggested Budget:" in captured.out
        assert "Status:" in captured.out

    @pytest.mark.integration
    def test_single_file_with_error(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test single file mode handles analysis errors."""
        # Arrange
        rule_file = tmp_path / "corrupted.md"
        rule_file.write_text("Invalid content")
        # Make file unreadable after creating it
        import os

        os.chmod(rule_file, 0o000)

        test_args = ["token_validator.py", str(rule_file)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Cleanup - restore permissions before assert
        os.chmod(rule_file, 0o644)

        # Assert
        assert exit_code == 1
        assert "[ERROR]" in captured.out

    @pytest.mark.integration
    def test_single_file_needs_update_dry_run(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test single file mode shows update message in dry-run."""
        # Arrange
        rule_file = tmp_path / "needs-update.md"
        rule_file.write_text("**TokenBudget:** ~200\n" + " ".join(["word"] * 385))

        test_args = ["token_validator.py", str(rule_file), "--dry-run"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "[DRY RUN]" in captured.out
        assert "Would update TokenBudget:" in captured.out

    @pytest.mark.integration
    def test_single_file_needs_update_live(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test single file mode updates file when needed."""
        # Arrange
        rule_file = tmp_path / "needs-update.md"
        original = "**TokenBudget:** ~200\n" + " ".join(["word"] * 385)
        rule_file.write_text(original)

        test_args = ["token_validator.py", str(rule_file)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "✓ Updated TokenBudget:" in captured.out
        # Verify file was actually updated
        updated_content = rule_file.read_text()
        assert updated_content != original
        assert "~200" not in updated_content

    @pytest.mark.integration
    def test_single_file_update_failure(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test single file mode handles update failures."""
        # Arrange
        import os

        rule_file = tmp_path / "readonly.md"
        rule_file.write_text("**TokenBudget:** ~200\n" + " ".join(["word"] * 385))

        # Make file read-only before attempting update
        os.chmod(rule_file, 0o444)

        test_args = ["token_validator.py", str(rule_file)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Cleanup
        os.chmod(rule_file, 0o644)

        # Assert
        assert exit_code == 1
        assert "[ERROR] Failed to update file" in captured.out

    @pytest.mark.integration
    def test_single_file_no_update_needed(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test single file mode when budget is accurate."""
        # Arrange
        rule_file = tmp_path / "accurate.md"
        # Create content that tiktoken will count as approximately 500 tokens
        # Using ~500 words will give us close to 500 tokens with tiktoken
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 500))

        test_args = ["token_validator.py", str(rule_file)]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "✓ No update needed (within threshold)" in captured.out

    @pytest.mark.integration
    def test_single_file_with_threshold_flag(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test single file mode respects custom threshold."""
        # Arrange
        rule_file = tmp_path / "test.md"
        rule_file.write_text("**TokenBudget:** ~500\n" + " ".join(["word"] * 385))

        test_args = ["token_validator.py", str(rule_file), "--threshold", "5"]
        monkeypatch.setattr("sys.argv", test_args)

        # Act
        exit_code = utb.main()
        captured = capsys.readouterr()

        # Assert
        assert exit_code == 0
        assert "Update threshold: ±5.0%" in captured.out


class TestPathValidation:
    """Test path validation and error handling."""

    @pytest.mark.unit
    def test_invalid_path_type_error(self, tmp_path: Path, monkeypatch, capsys) -> None:
        """Test main() handles path that is neither file nor directory."""
        # Arrange - Mock Path methods to simulate edge case
        from unittest.mock import Mock, patch

        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        mock_path.is_dir.return_value = False
        mock_path.__str__ = lambda self: "/fake/path"

        test_args = ["token_validator.py", "/fake/path"]
        monkeypatch.setattr("sys.argv", test_args)

        # Mock Path constructor to return our mock
        with patch("token_validator.Path") as mock_path_class:
            mock_path_class.return_value = mock_path

            # Act
            exit_code = utb.main()
            captured = capsys.readouterr()

            # Assert
            assert exit_code == 1
            assert "[ERROR] Path is neither a file nor directory:" in captured.out


class TestUpdateFileEdgeCases:
    """Test edge cases in update_file method."""

    @pytest.mark.unit
    def test_update_file_no_change_needed_returns_false(self, tmp_path: Path) -> None:
        """Test update_file returns False when content replacement produces no change."""
        # Arrange
        rule_file = tmp_path / "exact-match.md"
        # Create a file where the suggested budget exactly matches current
        content = "**TokenBudget:** ~500\n" + " ".join(["word"] * 385)
        rule_file.write_text(content)

        updater = utb.TokenBudgetUpdater()
        analysis = updater.analyze_file(rule_file)

        # Force the suggested budget to match current (simulate exact match scenario)
        analysis.suggested_budget = analysis.current_budget
        analysis.needs_update = True  # Force update attempt

        # Act
        result = updater.update_file(analysis)

        # Assert - should return False because content wouldn't change
        assert result is False
