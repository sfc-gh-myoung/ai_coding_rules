"""Unit tests for match_rules.py — CLI via main(), exit codes, JSON output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ai_rules.match_rules import main

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
# Exit codes
# ---------------------------------------------------------------------------


class TestCLIExitCodes:
    def test_exit_0_when_match_found(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        code = main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        assert code == 0

    def test_exit_1_when_no_match(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        code = main(["--keywords", "completely_unrelated_zzz", "--rules-dir", str(rules_dir)])
        assert code == 1

    def test_exit_2_when_rules_dir_missing(self, tmp_path, capsys):
        nonexistent = tmp_path / "no_such_dir"
        code = main(["--keywords", "streamlit", "--rules-dir", str(nonexistent)])
        assert code == 2

    def test_exit_2_no_json_on_stdout(self, tmp_path):
        nonexistent = tmp_path / "no_such_dir"
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"from ai_rules.match_rules import main; import sys; sys.exit(main(['--keywords', 'streamlit', '--rules-dir', '{nonexistent}']))",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert result.stdout.strip() == ""

    def test_malformed_rule_not_fatal(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(
            tmp_path,
            {"valid.md": SAMPLE_RULE, "malformed.md": "# No frontmatter here"},
        )
        code = main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        assert code in (0, 1)


# ---------------------------------------------------------------------------
# JSON output correctness
# ---------------------------------------------------------------------------


class TestCLIOutput:
    def test_valid_json_on_stdout(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["schema_version"] == "rule-loader-manifest/v2"

    def test_load_sequence_contains_matched_rule(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        filenames = [e["filename"] for e in data["load_sequence"]]
        assert "101-streamlit.md" in filenames

    def test_extension_match(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "streamlit", "--extensions", ".py", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        filenames = [e["filename"] for e in data["load_sequence"]]
        assert "101-streamlit.md" in filenames

    def test_empty_manifest_on_no_match(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "zzz_no_match_ever", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["load_sequence"] == []

    def test_dependency_resolution_in_output(self, tmp_path, capsys):
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
            {"000-global-core.md": FOUNDATION_RULE, "101-streamlit.md": main_content},
        )
        main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        filenames = [e["filename"] for e in data["load_sequence"]]
        assert "000-global-core.md" in filenames

    def test_metadata_mode(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        code = main(["--mode", "metadata", "--rules-dir", str(rules_dir)])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "rules" in data
        assert "101-streamlit.md" in [v["filename"] for v in data["rules"].values()]
