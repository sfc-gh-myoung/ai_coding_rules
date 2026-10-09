"""Unit tests for match_rules.py: CLI via main(), exit codes, JSON output."""

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
        assert data["schema_version"] == "rule-loader-matcher/v1"

    def test_load_sequence_contains_matched_rule(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rule_paths = [e["rule_path"] for e in data["load_sequence"]]
        assert any("101-streamlit.md" in rp for rp in rule_paths)

    def test_extension_match(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "streamlit", "--extensions", ".py", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rule_paths = [e["rule_path"] for e in data["load_sequence"]]
        assert any("101-streamlit.md" in rp for rp in rule_paths)

    def test_empty_manifest_on_no_match(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "zzz_no_match_ever", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["load_sequence"] == []

    def test_raw_prose_keywords_are_extracted_before_matching(self, tmp_path, capsys):
        readme_rule = SAMPLE_RULE.replace("kw:streamlit", "file:README.md")
        rules_dir = _make_rules_dir(tmp_path, {"801-project-readme.md": readme_rule})
        main(
            [
                "--keywords",
                "update README.me document demo project notebook intent customer sharing progressive disclosure markdown",
                "--rules-dir",
                str(rules_dir),
            ]
        )
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rule_paths = [entry["rule_path"] for entry in data["load_sequence"]]
        assert any("801-project-readme.md" in rp for rp in rule_paths)

    def test_comma_delimited_keywords_remain_literal_match_terms(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        main(["--keywords", "unrelated,streamlit", "--rules-dir", str(rules_dir)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        rule_paths = [entry["rule_path"] for entry in data["load_sequence"]]
        assert any("101-streamlit.md" in rp for rp in rule_paths)

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
        rule_paths = [e["rule_path"] for e in data["load_sequence"]]
        assert any("000-global-core.md" in rp for rp in rule_paths)

    def test_metadata_mode(self, tmp_path, capsys):
        rules_dir = _make_rules_dir(tmp_path, {"101-streamlit.md": SAMPLE_RULE})
        code = main(["--mode", "metadata", "--rules-dir", str(rules_dir)])
        assert code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "rules" in data
        assert "101-streamlit.md" in [v["filename"] for v in data["rules"].values()]


# ---------------------------------------------------------------------------
# Published-schema conformance (negative control)
# ---------------------------------------------------------------------------

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "schemas" / "rule-loader-matcher-v1.schema.json"
)

# A rule whose required dependency is absent, so the matcher populates `warnings`
# and exercises the field that previously failed the schema's additionalProperties.
_RULE_WITH_MISSING_DEP = """\
---
schema_version: v3.5
rule_version: v2.0.0
last_updated: 2026-01-01
keywords:
  - kw:streamlit
token_budget: ~500
context_tier: High
depends:
  required:
    - 999-does-not-exist.md
---
# Rule with a missing required dependency
"""


class TestSchemaConformance:
    def test_matcher_output_validates_against_published_schema(self, tmp_path, capsys):
        """Real matcher stdout must validate against the published matcher/v1 schema.

        Negative control: this fails if the emitter and schema diverge again
        (e.g. an emitted key the schema's additionalProperties:false rejects).
        """
        import jsonschema

        rules_dir = _make_rules_dir(
            tmp_path,
            {
                "000-global-core.md": FOUNDATION_RULE,
                "101-streamlit.md": _RULE_WITH_MISSING_DEP,
            },
        )
        code = main(["--keywords", "streamlit", "--rules-dir", str(rules_dir)])
        assert code == 0
        data = json.loads(capsys.readouterr().out)
        # Guard: the warnings field (the schema-divergence trigger) is actually present.
        assert data["warnings"], "expected a warning for the missing required dependency"
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=schema)
