"""Unit tests for cli.py — end-to-end CLI, exit codes, JSON output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.rule_matcher.cli import app

runner = CliRunner()

SAMPLE_RULE = """\
---
schema_version: v3.5
rule_version: v2.0.0
last_updated: 2026-01-01
keywords:
  - kw:streamlit
  - ext:.py
token_budget: ~500
context_tier: High
---
# Streamlit rule body
"""

FOUNDATION_RULE = """\
---
schema_version: v3.5
rule_version: v4.0.0
last_updated: 2026-01-01
keywords:
  - kw:foundation
token_budget: ~500
context_tier: Critical
---
# Foundation
"""


def _make_rules_dir(tmp_path: Path, rules: dict[str, str]) -> Path:
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    for name, content in rules.items():
        (rules_dir / name).write_text(content, encoding="utf-8")
    return rules_dir


# ---------------------------------------------------------------------------
# Exit code 0 — matched
# ---------------------------------------------------------------------------


class TestCLIExitCodes:
    def test_exit_0_when_match_found(self, tmp_path):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        result = runner.invoke(
            app,
            [
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        assert result.exit_code == 0

    def test_exit_1_when_no_match(self, tmp_path):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        result = runner.invoke(
            app,
            [
                "--keywords",
                "completely_unrelated_zzz",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        assert result.exit_code == 1

    def test_exit_2_when_rules_dir_missing(self, tmp_path):
        """Exit code 2 for fatal error: non-existent --rules-dir."""
        nonexistent = tmp_path / "no_such_dir"
        result = runner.invoke(
            app,
            [
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(nonexistent),
            ],
        )
        assert result.exit_code == 2

    def test_exit_2_no_json_on_stdout(self, tmp_path):
        """When exit code 2, stdout must be empty (error JSON goes to stderr)."""
        nonexistent = tmp_path / "no_such_dir"
        # Use subprocess so stdout and stderr are truly separated
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ai_rules.rule_matcher",
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(nonexistent),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert result.stdout.strip() == "", (
            f"Expected empty stdout on exit 2, got: {result.stdout!r}"
        )

    def test_exit_2_not_returned_for_single_malformed_rule(self, tmp_path):
        """A single malformed rule file does NOT cause exit code 2."""
        rules_dir = _make_rules_dir(
            tmp_path,
            {
                "valid.md": SAMPLE_RULE,
                "malformed.md": "# No frontmatter here",
            },
        )
        result = runner.invoke(
            app,
            [
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        # Should succeed (0 or 1), not fatal (2)
        assert result.exit_code in (0, 1)


# ---------------------------------------------------------------------------
# JSON output correctness
# ---------------------------------------------------------------------------


class TestCLIOutput:
    def test_valid_json_on_stdout(self, tmp_path):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        result = runner.invoke(
            app,
            [
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        data = json.loads(result.output)
        assert data["schema_version"] == "rule-loader-manifest/v2"

    def test_load_sequence_contains_matched_rule(self, tmp_path):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        result = runner.invoke(
            app,
            [
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        data = json.loads(result.output)
        filenames = [e["filename"] for e in data["load_sequence"]]
        assert "101-streamlit.md" in filenames

    def test_extension_match(self, tmp_path):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        result = runner.invoke(
            app,
            [
                "--keywords",
                "",
                "--extensions",
                ".py",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        data = json.loads(result.output)
        filenames = [e["filename"] for e in data["load_sequence"]]
        assert "101-streamlit.md" in filenames

    def test_empty_manifest_on_no_match(self, tmp_path):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        result = runner.invoke(
            app,
            [
                "--keywords",
                "zzz_no_match_ever",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        data = json.loads(result.output)
        assert data["load_sequence"] == []

    def test_dependency_resolution_in_output(self, tmp_path):
        """Matched rule's required dep appears in load_sequence."""
        dep_content = """\
---
rule_version: v1.0
context_tier: Critical
keywords:
  - kw:foundation
token_budget: ~500
---
# Foundation
"""
        main_content = """\
---
rule_version: v2.0
context_tier: High
keywords:
  - kw:streamlit
token_budget: ~500
depends:
  required:
    - 000-global-core.md
---
# Main
"""
        rules_dir = _make_rules_dir(
            tmp_path,
            {
                "000-global-core.md": dep_content,
                "101-streamlit.md": main_content,
            },
        )
        result = runner.invoke(
            app,
            [
                "--keywords",
                "streamlit",
                "--rules-dir",
                str(rules_dir),
            ],
        )
        data = json.loads(result.output)
        filenames = [e["filename"] for e in data["load_sequence"]]
        assert "000-global-core.md" in filenames
