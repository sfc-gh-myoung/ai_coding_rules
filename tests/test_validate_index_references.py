#!/usr/bin/env python3
"""Tests for validate_index_references.py script."""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.validate_index_references import (
    RE_RULE_REF,
    SKIP_FILES,
    extract_references_from_index,
    get_actual_rule_files,
    main,
    validate_references,
)


class TestRegexPattern:
    """Test the rule reference regex pattern."""

    def test_matches_standard_rule_format(self):
        """Test regex matches standard NNN-name.md format."""
        text = "See 000-global-core.md for details"
        matches = RE_RULE_REF.findall(text)
        assert matches == ["000-global-core.md"]

    def test_matches_lettered_suffix(self):
        """Test regex matches NNNx-name.md format with letter suffix."""
        text = "Load 101a-snowflake-streamlit.md first"
        matches = RE_RULE_REF.findall(text)
        assert matches == ["101a-snowflake-streamlit.md"]

    def test_matches_hyphenated_names(self):
        """Test regex matches multi-hyphenated filenames."""
        text = "Reference 200-python-core.md and 206-python-pytest.md"
        matches = RE_RULE_REF.findall(text)
        assert matches == ["200-python-core.md", "206-python-pytest.md"]

    def test_does_not_match_invalid_formats(self):
        """Test regex rejects invalid formats."""
        text = "Not matched: 00-short.md, ABCD-text.md, 1234-toolong.md"
        matches = RE_RULE_REF.findall(text)
        assert matches == []

    def test_matches_boundary_cases(self):
        """Test regex respects word boundaries."""
        text = "Match 100-test.md but not x100-test.md or 100-test.mdx"
        matches = RE_RULE_REF.findall(text)
        assert matches == ["100-test.md"]


class TestExtractReferences:
    """Test extracting references from index file."""

    def test_extracts_references_from_valid_index(self, tmp_path):
        """Test extracting references from a valid index file."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text(
            dedent("""
            # Rule Index

            - 000-global-core.md
            - 100-snowflake-core.md
            - 200-python-core.md
            """)
        )

        refs = extract_references_from_index(index_file)
        assert refs == {"000-global-core.md", "100-snowflake-core.md", "200-python-core.md"}

    def test_extracts_multiple_references_same_line(self, tmp_path):
        """Test extracting multiple references from same line."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Depends: 000-global-core.md, 100-snowflake-core.md")

        refs = extract_references_from_index(index_file)
        assert refs == {"000-global-core.md", "100-snowflake-core.md"}

    def test_extracts_references_with_letter_suffix(self, tmp_path):
        """Test extracting references with letter suffixes."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Load 101a-streamlit.md and 102b-sql.md")

        refs = extract_references_from_index(index_file)
        assert refs == {"101a-streamlit.md", "102b-sql.md"}

    def test_handles_empty_file(self, tmp_path):
        """Test handling empty index file."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("")

        refs = extract_references_from_index(index_file)
        assert refs == set()

    def test_deduplicates_references(self, tmp_path):
        """Test deduplication of repeated references."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text(
            dedent("""
            - 000-global-core.md
            - 100-test.md
            - 000-global-core.md (repeated)
            """)
        )

        refs = extract_references_from_index(index_file)
        assert refs == {"000-global-core.md", "100-test.md"}


class TestGetActualRuleFiles:
    """Test getting actual rule files from directory."""

    def test_finds_markdown_files(self, tmp_path):
        """Test finding .md files in rules directory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-global-core.md").write_text("content")
        (rules_dir / "100-snowflake.md").write_text("content")
        (rules_dir / "200-python.md").write_text("content")

        files = get_actual_rule_files(rules_dir)
        assert files == {"000-global-core.md", "100-snowflake.md", "200-python.md"}

    def test_skips_non_rule_files(self, tmp_path):
        """Test skipping files in SKIP_FILES set."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-rule.md").write_text("content")
        (rules_dir / "README.md").write_text("content")
        (rules_dir / "CHANGELOG.md").write_text("content")

        files = get_actual_rule_files(rules_dir)
        assert files == {"000-rule.md"}

    def test_finds_files_in_subdirectories(self, tmp_path):
        """Test finding files in nested subdirectories."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        subdir = rules_dir / "subdir"
        subdir.mkdir()
        (rules_dir / "000-top.md").write_text("content")
        (subdir / "100-nested.md").write_text("content")

        files = get_actual_rule_files(rules_dir)
        assert files == {"000-top.md", "100-nested.md"}

    def test_handles_empty_directory(self, tmp_path):
        """Test handling empty rules directory."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        files = get_actual_rule_files(rules_dir)
        assert files == set()

    def test_ignores_non_markdown_files(self, tmp_path):
        """Test ignoring non-.md files."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-rule.md").write_text("content")
        (rules_dir / "script.py").write_text("content")
        (rules_dir / "config.yaml").write_text("content")

        files = get_actual_rule_files(rules_dir)
        assert files == {"000-rule.md"}


class TestValidateReferences:
    """Test validation logic."""

    def test_valid_references_no_errors(self, tmp_path):
        """Test validation with all valid references."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md, 100-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")
        (rules_dir / "100-test.md").write_text("content")

        broken, orphaned = validate_references(index_file, rules_dir)
        assert broken == []
        assert orphaned == []

    def test_detects_broken_references(self, tmp_path):
        """Test detection of broken references."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-exists.md, 100-missing.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-exists.md").write_text("content")

        broken, orphaned = validate_references(index_file, rules_dir)
        assert broken == ["100-missing.md"]
        assert orphaned == []

    def test_detects_orphaned_files(self, tmp_path):
        """Test detection of orphaned files when check enabled."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-referenced.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-referenced.md").write_text("content")
        (rules_dir / "100-orphaned.md").write_text("content")

        broken, orphaned = validate_references(index_file, rules_dir, check_orphans=True)
        assert broken == []
        assert orphaned == ["100-orphaned.md"]

    def test_does_not_detect_orphans_when_disabled(self, tmp_path):
        """Test orphan detection disabled by default."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-referenced.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-referenced.md").write_text("content")
        (rules_dir / "100-orphaned.md").write_text("content")

        broken, orphaned = validate_references(index_file, rules_dir, check_orphans=False)
        assert broken == []
        assert orphaned == []

    def test_verbose_mode_prints_counts(self, tmp_path, capsys):
        """Test verbose mode prints reference counts."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")

        validate_references(index_file, rules_dir, verbose=True)

        captured = capsys.readouterr()
        assert "References found" in captured.out
        assert "Rule files found" in captured.out


class TestMainFunction:
    """Test main CLI function."""

    def test_main_success_with_valid_references(self, tmp_path, monkeypatch, capsys):
        """Test main returns 0 with valid references."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_index_references.py",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
            ],
        )

        exit_code = main()
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "VALIDATION PASSED" in captured.out

    def test_main_fails_with_broken_references(self, tmp_path, monkeypatch, capsys):
        """Test main returns 1 with broken references."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-missing.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_index_references.py",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
            ],
        )

        exit_code = main()
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "BROKEN REFERENCES" in captured.out
        assert "000-missing.md" in captured.out

    def test_main_with_check_orphans_flag(self, tmp_path, monkeypatch, capsys):
        """Test main with --check-orphans flag."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")
        (rules_dir / "100-orphan.md").write_text("content")

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_index_references.py",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
                "--check-orphans",
            ],
        )

        exit_code = main()
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "ORPHANED FILES" in captured.out
        assert "100-orphan.md" in captured.out

    def test_main_with_verbose_flag(self, tmp_path, monkeypatch, capsys):
        """Test main with --verbose flag."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_index_references.py",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
                "--verbose",
            ],
        )

        exit_code = main()
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "References found" in captured.out

    def test_main_fails_when_index_missing(self, tmp_path, monkeypatch, capsys):
        """Test main returns 1 when index file doesn't exist."""
        index_file = tmp_path / "MISSING_INDEX.md"
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_index_references.py",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
            ],
        )

        exit_code = main()
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_main_fails_when_rules_dir_missing(self, tmp_path, monkeypatch, capsys):
        """Test main returns 1 when rules directory doesn't exist."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("content")
        rules_dir = tmp_path / "missing_rules"

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "validate_index_references.py",
                "--index-path",
                str(index_file),
                "--rules-dir",
                str(rules_dir),
            ],
        )

        exit_code = main()
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_main_uses_default_paths(self, tmp_path, monkeypatch, capsys):
        """Test main uses default paths when not specified."""
        # Create default paths in current directory
        monkeypatch.chdir(tmp_path)
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 000-test.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-test.md").write_text("content")

        monkeypatch.setattr(sys, "argv", ["validate_index_references.py"])

        exit_code = main()
        assert exit_code == 0


class TestSkipFiles:
    """Test SKIP_FILES constant."""

    def test_skip_files_contains_expected_files(self):
        """Test SKIP_FILES contains standard non-rule files."""
        assert "README.md" in SKIP_FILES
        assert "CHANGELOG.md" in SKIP_FILES
        assert "CONTRIBUTING.md" in SKIP_FILES

    def test_skip_files_prevents_false_positives(self, tmp_path):
        """Test SKIP_FILES prevents counting documentation as rules."""
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "000-rule.md").write_text("content")
        (rules_dir / "README.md").write_text("documentation")

        files = get_actual_rule_files(rules_dir)
        assert "README.md" not in files
        assert "000-rule.md" in files


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_handles_unicode_in_filenames(self, tmp_path):
        """Test handling unicode characters in file content."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Unicode: 000-test.md — 100-example.md")

        refs = extract_references_from_index(index_file)
        assert "000-test.md" in refs
        assert "100-example.md" in refs

    def test_handles_mixed_line_endings(self, tmp_path):
        """Test handling mixed line endings in index file."""
        index_file = tmp_path / "RULES_INDEX.md"
        # Mix of LF and CRLF
        content = "Rule 1: 000-test.md\r\nRule 2: 100-test.md\n"
        index_file.write_bytes(content.encode("utf-8"))

        refs = extract_references_from_index(index_file)
        assert refs == {"000-test.md", "100-test.md"}

    def test_handles_large_index_file(self, tmp_path):
        """Test handling large index files with many references."""
        index_file = tmp_path / "RULES_INDEX.md"
        # Generate 100 rule references
        content = "\n".join([f"- {i:03d}-test-rule.md" for i in range(100)])
        index_file.write_text(content)

        refs = extract_references_from_index(index_file)
        assert len(refs) == 100

    def test_sorted_output_for_broken_refs(self, tmp_path):
        """Test broken references are sorted alphabetically."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("Rules: 200-z.md, 100-b.md, 000-a.md")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        broken, _ = validate_references(index_file, rules_dir)
        assert broken == ["000-a.md", "100-b.md", "200-z.md"]

    def test_sorted_output_for_orphaned_files(self, tmp_path):
        """Test orphaned files are sorted alphabetically."""
        index_file = tmp_path / "RULES_INDEX.md"
        index_file.write_text("")

        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        (rules_dir / "200-z.md").write_text("content")
        (rules_dir / "100-b.md").write_text("content")
        (rules_dir / "000-a.md").write_text("content")

        _, orphaned = validate_references(index_file, rules_dir, check_orphans=True)
        assert orphaned == ["000-a.md", "100-b.md", "200-z.md"]
