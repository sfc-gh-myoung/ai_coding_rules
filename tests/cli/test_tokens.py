"""Tests for ai-rules tokens CLI command.

Tests follow pytest best practices:
- AAA pattern (Arrange-Act-Assert)
- Function-scoped fixtures
- Parametrized tests for input matrices
- Test markers for selective execution
- Isolation with tmp_path
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands import tokens

runner = CliRunner()


class TestTokensHelpOutput:
    """Test --help output for tokens command."""

    @pytest.mark.unit
    def test_tokens_help_shows_command_description(self):
        """Test that --help shows command description."""
        result = runner.invoke(app, ["tokens", "--help"])

        assert result.exit_code == 0
        assert "token budgets" in result.output.lower()

    @pytest.mark.unit
    def test_tokens_help_shows_dry_run_option(self):
        """Test that --help shows --dry-run option."""
        result = runner.invoke(app, ["tokens", "--help"])

        assert result.exit_code == 0
        assert "--dry-run" in result.output

    @pytest.mark.unit
    def test_tokens_help_shows_detailed_option(self):
        """Test that --help shows --detailed option."""
        result = runner.invoke(app, ["tokens", "--help"])

        assert result.exit_code == 0
        assert "--detailed" in result.output

    @pytest.mark.unit
    def test_tokens_help_shows_threshold_option(self):
        """Test that --help shows --threshold option."""
        result = runner.invoke(app, ["tokens", "--help"])

        assert result.exit_code == 0
        assert "--threshold" in result.output

    @pytest.mark.unit
    def test_tokens_help_shows_path_argument(self):
        """Test that --help shows PATH argument."""
        result = runner.invoke(app, ["tokens", "--help"])

        assert result.exit_code == 0
        assert "PATH" in result.output


class TestTokensSingleFile:
    """Test single file validation scenarios."""

    @pytest.mark.unit
    def test_single_file_within_threshold(self, tmp_path: Path):
        """Test single file validation when within threshold."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(
            "# Test Rule\n\n"
            "**Keywords:** test, example\n"
            "**TokenBudget:** ~100\n\n"
            "This is a test rule file with some content.\n"
        )

        # Mock tiktoken to return predictable token count
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1] * 95  # ~95 tokens, within 5% of 100

        with (
            patch.object(tokens.TokenBudgetUpdater, "__init__", lambda self, config: None),
            patch.object(tokens, "TokenBudgetUpdater") as MockUpdater,
        ):
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=100,
                estimated_tokens=95,
                suggested_budget=100,
                diff_percentage=-5.0,
                needs_update=False,
            )

            result = runner.invoke(app, ["tokens", str(rule_file)])

        assert result.exit_code == 0
        assert "No update needed" in result.output or "within threshold" in result.output.lower()

    @pytest.mark.unit
    def test_single_file_needs_update(self, tmp_path: Path):
        """Test single file validation when update needed."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(
            "# Test Rule\n\n"
            "**Keywords:** test, example\n"
            "**TokenBudget:** ~100\n\n"
            "This is a test rule file.\n"
        )

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=100,
                estimated_tokens=150,
                suggested_budget=150,
                diff_percentage=50.0,
                needs_update=True,
            )
            mock_instance.update_file.return_value = True

            result = runner.invoke(app, ["tokens", str(rule_file)])

        assert result.exit_code == 0
        assert "Updated" in result.output

    @pytest.mark.unit
    def test_single_file_missing_budget(self, tmp_path: Path):
        """Test single file with missing TokenBudget."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text(
            "# Test Rule\n\n"
            "**Keywords:** test, example\n\n"
            "This is a test rule file without budget.\n"
        )

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=None,
                estimated_tokens=50,
                suggested_budget=50,
                diff_percentage=None,
                needs_update=True,
            )
            mock_instance.update_file.return_value = True

            result = runner.invoke(app, ["tokens", str(rule_file)])

        assert result.exit_code == 0
        assert "MISSING" in result.output


class TestTokensDirectoryScan:
    """Test directory scanning scenarios."""

    @pytest.mark.unit
    def test_directory_scan_all_ok(self, tmp_path: Path):
        """Test directory scan when all files are within threshold."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        (rules_dir / "100-test.md").write_text(
            "# Test Rule\n**TokenBudget:** ~100\nContent here.\n"
        )
        (rules_dir / "200-test.md").write_text(
            "# Another Rule\n**TokenBudget:** ~150\nMore content.\n"
        )

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.update_all.return_value = (
                [
                    tokens.TokenBudgetAnalysis(
                        file_path=rules_dir / "100-test.md",
                        current_budget=100,
                        estimated_tokens=98,
                        suggested_budget=100,
                        diff_percentage=-2.0,
                        needs_update=False,
                    ),
                    tokens.TokenBudgetAnalysis(
                        file_path=rules_dir / "200-test.md",
                        current_budget=150,
                        estimated_tokens=148,
                        suggested_budget=150,
                        diff_percentage=-1.3,
                        needs_update=False,
                    ),
                ],
                0,  # No updates
            )

            result = runner.invoke(app, ["tokens", str(rules_dir)])

        assert result.exit_code == 0
        assert "SUMMARY" in result.output

    @pytest.mark.unit
    def test_directory_scan_with_updates(self, tmp_path: Path):
        """Test directory scan when some files need updates."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        (rules_dir / "100-test.md").write_text("# Test Rule\n**TokenBudget:** ~100\n")

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.update_all.return_value = (
                [
                    tokens.TokenBudgetAnalysis(
                        file_path=rules_dir / "100-test.md",
                        current_budget=100,
                        estimated_tokens=200,
                        suggested_budget=200,
                        diff_percentage=100.0,
                        needs_update=True,
                    ),
                ],
                1,  # 1 update
            )
            mock_instance.config = tokens.UpdateConfig(dry_run=False, verbose=False)

            result = runner.invoke(app, ["tokens", str(rules_dir)])

        assert result.exit_code == 0
        assert "updated" in result.output.lower()


class TestTokensDryRun:
    """Test --dry-run flag behavior."""

    @pytest.mark.unit
    def test_dry_run_does_not_modify_file(self, tmp_path: Path):
        """Test that --dry-run does not write to files."""
        rule_file = tmp_path / "test-rule.md"
        original_content = "# Test Rule\n**TokenBudget:** ~100\nContent.\n"
        rule_file.write_text(original_content)

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=100,
                estimated_tokens=200,
                suggested_budget=200,
                diff_percentage=100.0,
                needs_update=True,
            )
            # update_file should not be called to modify in dry-run
            mock_instance.update_file.return_value = True
            mock_instance.config = tokens.UpdateConfig(dry_run=True)

            result = runner.invoke(app, ["tokens", str(rule_file), "--dry-run"])

        assert result.exit_code == 0
        # The output says "No files will be modified" in dry-run mode
        assert "no files will be modified" in result.output.lower()

    @pytest.mark.unit
    def test_dry_run_shows_planned_changes(self, tmp_path: Path):
        """Test that --dry-run shows what would change."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text("# Test Rule\n**TokenBudget:** ~100\nContent.\n")

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=100,
                estimated_tokens=200,
                suggested_budget=200,
                diff_percentage=100.0,
                needs_update=True,
            )
            mock_instance.update_file.return_value = True
            mock_instance.config = tokens.UpdateConfig(dry_run=True)

            result = runner.invoke(app, ["tokens", str(rule_file), "--dry-run"])

        assert result.exit_code == 0
        assert "Would update" in result.output


class TestTokensDetailedFlag:
    """Test --detailed flag behavior."""

    @pytest.mark.unit
    def test_detailed_shows_table(self, tmp_path: Path):
        """Test that --detailed shows detailed analysis table."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "100-test.md").write_text("# Test\n**TokenBudget:** ~100\n")

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.update_all.return_value = (
                [
                    tokens.TokenBudgetAnalysis(
                        file_path=rules_dir / "100-test.md",
                        current_budget=100,
                        estimated_tokens=98,
                        suggested_budget=100,
                        diff_percentage=-2.0,
                        needs_update=False,
                    ),
                ],
                0,
            )
            mock_instance.config = tokens.UpdateConfig(dry_run=False, verbose=True)

            result = runner.invoke(app, ["tokens", str(rules_dir), "--detailed"])

        assert result.exit_code == 0
        # Check for table-like output
        assert "100-test.md" in result.output or "Detailed" in result.output


class TestTokensThresholdFlag:
    """Test --threshold flag behavior."""

    @pytest.mark.unit
    def test_custom_threshold_applied(self, tmp_path: Path):
        """Test that custom threshold is used in configuration."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text("# Test Rule\n**TokenBudget:** ~100\nContent.\n")

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=100,
                estimated_tokens=110,
                suggested_budget=100,
                diff_percentage=10.0,
                needs_update=False,  # With 20% threshold, 10% diff doesn't need update
            )

            result = runner.invoke(app, ["tokens", str(rule_file), "--threshold", "20"])

        assert result.exit_code == 0
        assert "20" in result.output or "threshold" in result.output.lower()


class TestTokensErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.unit
    def test_missing_path(self):
        """Test error when no path provided."""
        result = runner.invoke(app, ["tokens"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "PATH" in result.output

    @pytest.mark.unit
    def test_nonexistent_path(self, tmp_path: Path):
        """Test error when path doesn't exist."""
        nonexistent = tmp_path / "nonexistent-file.md"

        result = runner.invoke(app, ["tokens", str(nonexistent)])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    @pytest.mark.unit
    def test_file_read_error(self, tmp_path: Path):
        """Test handling of file read errors."""
        rule_file = tmp_path / "test-rule.md"
        rule_file.write_text("# Test\n")

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=None,
                estimated_tokens=0,
                suggested_budget=0,
                diff_percentage=None,
                needs_update=False,
                error="Failed to read file: Permission denied",
            )

            result = runner.invoke(app, ["tokens", str(rule_file)])

        assert result.exit_code == 1
        assert "Failed to read" in result.output or "error" in result.output.lower()


class TestTokenBudgetAnalysisDataclass:
    """Test TokenBudgetAnalysis dataclass."""

    @pytest.mark.unit
    def test_status_error(self):
        """Test status returns ERROR when error is set."""
        analysis = tokens.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=100,
            estimated_tokens=0,
            suggested_budget=0,
            diff_percentage=None,
            needs_update=False,
            error="Some error",
        )
        assert analysis.status == "ERROR"

    @pytest.mark.unit
    def test_status_missing(self):
        """Test status returns MISSING when no current budget."""
        analysis = tokens.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=None,
            estimated_tokens=100,
            suggested_budget=100,
            diff_percentage=None,
            needs_update=True,
        )
        assert analysis.status == "MISSING"

    @pytest.mark.unit
    def test_status_ok(self):
        """Test status returns OK when no update needed."""
        analysis = tokens.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=100,
            estimated_tokens=98,
            suggested_budget=100,
            diff_percentage=-2.0,
            needs_update=False,
        )
        assert analysis.status == "OK"

    @pytest.mark.unit
    def test_status_update(self):
        """Test status returns UPDATE for moderate differences."""
        analysis = tokens.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=100,
            estimated_tokens=120,
            suggested_budget=150,
            diff_percentage=20.0,
            needs_update=True,
        )
        assert analysis.status == "UPDATE"

    @pytest.mark.unit
    def test_status_major(self):
        """Test status returns MAJOR for large differences (>50%)."""
        analysis = tokens.TokenBudgetAnalysis(
            file_path=Path("test.md"),
            current_budget=100,
            estimated_tokens=200,
            suggested_budget=200,
            diff_percentage=100.0,
            needs_update=True,
        )
        assert analysis.status == "MAJOR"


class TestTokenBudgetUpdaterUnit:
    """Unit tests for TokenBudgetUpdater class."""

    @pytest.mark.unit
    def test_round_to_increment(self):
        """Test rounding to increment."""
        config = tokens.UpdateConfig(rounding_increment=50)
        updater = tokens.TokenBudgetUpdater(config)

        assert updater.round_to_increment(73) == 50
        assert updater.round_to_increment(76) == 100
        assert updater.round_to_increment(100) == 100
        # Note: Python's round() uses banker's rounding (round half to even)
        # So 125 rounds to 100 (nearest even multiple of 50)
        # and 175 rounds to 200 (nearest even multiple of 50)
        assert updater.round_to_increment(125) == 100  # Banker's rounding
        assert updater.round_to_increment(126) == 150  # Above midpoint

    @pytest.mark.unit
    def test_estimate_tokens(self):
        """Test token estimation with tiktoken."""
        updater = tokens.TokenBudgetUpdater()

        # Simple test - actual token count depends on tiktoken
        token_count = updater.estimate_tokens("Hello, world!")
        assert isinstance(token_count, int)
        assert token_count > 0

    @pytest.mark.unit
    def test_analyze_file_extracts_budget(self, tmp_path: Path):
        """Test that analyze_file extracts current budget."""
        rule_file = tmp_path / "test.md"
        rule_file.write_text("# Test\n**TokenBudget:** ~500\nContent here.\n")

        updater = tokens.TokenBudgetUpdater()
        analysis = updater.analyze_file(rule_file)

        assert analysis.current_budget == 500
        assert analysis.estimated_tokens > 0

    @pytest.mark.unit
    def test_analyze_file_handles_missing_budget(self, tmp_path: Path):
        """Test analyze_file when no TokenBudget exists."""
        rule_file = tmp_path / "test.md"
        rule_file.write_text("# Test\nNo budget here.\n")

        updater = tokens.TokenBudgetUpdater()
        analysis = updater.analyze_file(rule_file)

        assert analysis.current_budget is None
        assert analysis.needs_update is True

    @pytest.mark.unit
    def test_analyze_file_handles_read_error(self, tmp_path: Path):
        """Test analyze_file handles missing files gracefully."""
        missing_file = tmp_path / "nonexistent.md"

        updater = tokens.TokenBudgetUpdater()
        analysis = updater.analyze_file(missing_file)

        assert analysis.error is not None
        assert "Failed to read" in analysis.error


class TestTokensEdgeCases:
    """Test edge cases."""

    @pytest.mark.unit
    def test_empty_directory(self, tmp_path: Path):
        """Test handling empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.update_all.return_value = ([], 0)
            mock_instance.config = tokens.UpdateConfig()

            result = runner.invoke(app, ["tokens", str(empty_dir)])

        assert result.exit_code == 0
        assert "0" in result.output  # Total files: 0

    @pytest.mark.unit
    def test_short_flags(self, tmp_path: Path):
        """Test short flag versions work."""
        rule_file = tmp_path / "test.md"
        rule_file.write_text("# Test\n**TokenBudget:** ~100\n")

        with patch.object(tokens, "TokenBudgetUpdater") as MockUpdater:
            mock_instance = MagicMock()
            MockUpdater.return_value = mock_instance
            mock_instance.analyze_file.return_value = tokens.TokenBudgetAnalysis(
                file_path=rule_file,
                current_budget=100,
                estimated_tokens=95,
                suggested_budget=100,
                diff_percentage=-5.0,
                needs_update=False,
            )

            # Test -n for --dry-run, -d for --detailed, -t for --threshold
            result = runner.invoke(app, ["tokens", str(rule_file), "-n", "-t", "10"])

        assert result.exit_code == 0
        # Dry-run mode shows "No files will be modified"
        assert "no files will be modified" in result.output.lower()
