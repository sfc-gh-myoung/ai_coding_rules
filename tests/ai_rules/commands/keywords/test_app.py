"""Tests for the keywords Typer app: display helpers and the collisions command.

Covers the presentation and reporting layer of
``ai_rules.commands.rule_loader.keywords.app``, which is reachable without a
Cortex connection. Every test asserts observable output -- rendered text, JSON
structure, written files, exit codes -- rather than that a code path executed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.commands.rule_loader.keywords import keywords_app
from ai_rules.commands.rule_loader.keywords.app import (
    print_diff_rich,
    print_suggestions_table,
)
from ai_rules.commands.rule_loader.keywords.extractor import ExtractionResult

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


def _result(current: list[str], suggested: list[str], name: str = "100-x.md") -> ExtractionResult:
    """Build an ExtractionResult without touching the filesystem or an LLM."""
    return ExtractionResult(
        file_path=Path("rules") / name,
        current_keywords=current,
        suggested_keywords=suggested,
    )


# ---------------------------------------------------------------------------
# print_diff_rich -- the added/removed/kept classification
# ---------------------------------------------------------------------------


class TestPrintDiffRich:
    @pytest.mark.unit
    def test_reports_added_removed_and_kept_sections(self, capsys):
        """A keyword in both lists is kept; otherwise it is added or removed."""
        print_diff_rich(_result(["kept-one", "gone"], ["kept-one", "fresh"]))

        out = capsys.readouterr().out
        assert "Removed (1)" in out
        assert "gone" in out
        assert "Added (1)" in out
        assert "fresh" in out
        assert "Kept (1)" in out
        assert "kept-one" in out

    @pytest.mark.unit
    def test_classification_is_case_insensitive(self, capsys):
        """Casing differences must not register as an add plus a remove."""
        print_diff_rich(_result(["Snowflake SQL"], ["snowflake sql"]))

        out = capsys.readouterr().out
        assert "Kept (1)" in out
        assert "Removed" not in out
        assert "Added" not in out

    @pytest.mark.unit
    def test_counts_appear_in_panel_titles(self, capsys):
        """Panel titles carry the size of each keyword list."""
        print_diff_rich(_result(["a", "b", "c"], ["a"]))

        out = capsys.readouterr().out
        assert "Current (3)" in out
        assert "Suggested (1)" in out

    @pytest.mark.unit
    def test_empty_keyword_lists_render_placeholder(self, capsys):
        """An empty side renders a placeholder instead of an empty panel."""
        print_diff_rich(_result([], []))

        out = capsys.readouterr().out
        assert "No keywords" in out
        # Nothing changed, so no change sections should appear at all.
        assert "Removed" not in out
        assert "Added" not in out
        assert "Kept" not in out

    @pytest.mark.unit
    def test_file_name_is_shown(self, capsys):
        """The rule under diff is identified by filename."""
        print_diff_rich(_result(["a"], ["b"], name="206-python-pytest.md"))

        assert "206-python-pytest.md" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# print_suggestions_table
# ---------------------------------------------------------------------------


class TestPrintSuggestionsTable:
    @pytest.mark.unit
    def test_renders_one_row_per_result(self, capsys):
        """Each result contributes a row keyed by filename."""
        print_suggestions_table(
            [
                _result(["old"], ["new"], name="100-a.md"),
                _result(["keep"], ["keep"], name="200-b.md"),
            ]
        )

        out = capsys.readouterr().out
        assert "Keyword Suggestions" in out
        assert "100-a.md" in out
        assert "200-b.md" in out

    @pytest.mark.unit
    def test_missing_keywords_render_as_none(self, capsys):
        """A rule with no keywords shows a placeholder, not a blank cell."""
        print_suggestions_table([_result([], [])])

        assert "None" in capsys.readouterr().out

    @pytest.mark.unit
    def test_empty_result_list_still_renders_headers(self, capsys):
        """An empty run prints the table shell rather than nothing at all."""
        print_suggestions_table([])

        out = capsys.readouterr().out
        assert "Keyword Suggestions" in out
        assert "File" in out


# ---------------------------------------------------------------------------
# collisions command
# ---------------------------------------------------------------------------


class TestCollisionsCommand:
    @pytest.mark.unit
    def test_missing_rules_dir_exits_nonzero(self, tmp_path: Path):
        """A bad --rules-dir is a usage error, not an empty report."""
        result = runner.invoke(
            keywords_app,
            ["collisions", "--rules-dir", str(tmp_path / "nope")],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    @pytest.mark.integration
    def test_stdout_payload_is_valid_json_with_expected_shape(self):
        """With no --output the report goes to stdout as parseable JSON."""
        result = runner.invoke(keywords_app, ["collisions"])

        assert result.exit_code == 0, result.output
        report = json.loads(result.output)
        assert set(report) == {
            "rules_dir",
            "max_collision",
            "total_keywords",
            "violation_count",
            "collision_map",
            "violations",
        }
        assert report["total_keywords"] == len(report["collision_map"])
        assert report["violation_count"] == len(report["violations"])

    @pytest.mark.integration
    def test_output_flag_writes_file_and_creates_parent(self, tmp_path: Path):
        """--output writes the payload and creates missing parent directories."""
        target = tmp_path / "nested" / "deeper" / "collisions.json"

        result = runner.invoke(keywords_app, ["collisions", "--output", str(target)])

        assert result.exit_code == 0, result.output
        assert target.is_file()
        report = json.loads(target.read_text(encoding="utf-8"))
        assert "collision_map" in report
        assert target.read_text(encoding="utf-8").endswith("\n")

    @pytest.mark.integration
    def test_max_collision_threshold_is_applied(self):
        """Every reported violation must exceed the threshold, and a higher
        threshold can only narrow the set.
        """
        low = json.loads(runner.invoke(keywords_app, ["collisions", "--max-collision", "2"]).output)
        high = json.loads(
            runner.invoke(keywords_app, ["collisions", "--max-collision", "8"]).output
        )

        assert low["max_collision"] == 2
        assert high["max_collision"] == 8
        for rules in low["violations"].values():
            assert len(rules) > 2
        assert set(high["violations"]) <= set(low["violations"])
        # The full map is threshold-independent; only the violating subset moves.
        assert low["total_keywords"] == high["total_keywords"]
