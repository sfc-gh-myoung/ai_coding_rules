"""Tests for the audit-report diagnostic triage command."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.commands.rule_loader.audit_report import (
    AtomicWriteError,
    UsableInputError,
    atomic_write_pair,
    audit_report_cmd,
    build_report,
    classify,
    derive_trigger_shape,
    load_taxonomy,
    validate_artifact,
    validate_sidecar_toplevel,
)

runner = CliRunner()


# --- Fixtures ---


def _make_artifact(records: list[dict], identity: dict | None = None) -> dict:
    return {
        "artifact": identity
        or {
            "git_sha": "abc123",
            "rules_digest": "rd1",
            "matcher_digest": "md1",
            "schema_version": "1",
            "generator_version": "1",
        },
        "records": records,
    }


def _make_record(
    rule_id: str = "rules/100-test.md",
    trigger_kind: str = "kw",
    trigger_value: str = "test",
    in_manifest: bool = False,
    score: int | float | None = None,
    rank: int | None = None,
    probe: str = "test probe",
    prompt_source: str = "synthetic",
) -> dict:
    return {
        "rule_id": rule_id,
        "trigger_kind": trigger_kind,
        "trigger_value": trigger_value,
        "in_manifest": in_manifest,
        "score": score,
        "rank": rank,
        "probe": probe,
        "prompt_source": prompt_source,
    }


# --- derive_trigger_shape tests ---


class TestDeriveTriggerShape:
    def test_punctuated_at_sign(self):
        assert derive_trigger_shape("@st.cache_data decorator") == "punctuated"

    def test_punctuated_dot(self):
        assert derive_trigger_shape(".sql") == "punctuated"

    def test_punctuated_slash(self):
        assert derive_trigger_shape("ci/cd") == "punctuated"

    def test_punctuated_dollar(self):
        assert derive_trigger_shape("$dispatch cross-component") == "punctuated"

    def test_single_token(self):
        assert derive_trigger_shape("cortex") == "single-token"

    def test_single_token_no_punct(self):
        assert derive_trigger_shape("fastapi") == "single-token"

    def test_multi_token(self):
        assert derive_trigger_shape("claude iteration") == "multi-token"

    def test_multi_token_spaces(self):
        assert derive_trigger_shape("snowflake dynamic tables") == "multi-token"


# --- load_taxonomy tests ---


class TestLoadTaxonomy:
    def test_loads_default_taxonomy(self):
        taxonomy = load_taxonomy()
        assert len(taxonomy) == 4
        assert taxonomy[0]["name"] == "cap-displacement"
        assert taxonomy[0]["precedence"] == 1
        assert taxonomy[3]["name"] == "no-score-unexplained"

    def test_precedence_order(self):
        taxonomy = load_taxonomy()
        precedences = [e["precedence"] for e in taxonomy]
        assert precedences == sorted(precedences)

    def test_rejects_missing_precedence(self, tmp_path: Path):
        bad_toml = tmp_path / "bad.toml"
        bad_toml.write_text('[categories.broken]\ntrigger_shape = "any"\n')
        with pytest.raises(UsableInputError, match="missing 'precedence' key"):
            load_taxonomy(bad_toml)

    def test_rejects_empty_categories(self, tmp_path: Path):
        bad_toml = tmp_path / "empty.toml"
        bad_toml.write_text("[categories]\n")
        with pytest.raises(UsableInputError, match="missing or empty"):
            load_taxonomy(bad_toml)


# --- classify tests ---


class TestClassify:
    @pytest.fixture()
    def taxonomy(self):
        return load_taxonomy()

    def test_cap_displacement(self, taxonomy):
        rec = _make_record(score=0.85, rank=4, trigger_value="snowpipe")
        category, evidence = classify(rec, taxonomy)
        assert category == "cap-displacement"
        assert evidence["score"] == 0.85
        assert evidence["rank"] == 4
        assert evidence["inferred_cause"] is False

    def test_punctuated_no_score(self, taxonomy):
        rec = _make_record(trigger_value="@st.cache_data decorator")
        category, evidence = classify(rec, taxonomy)
        assert category == "punctuated-no-score"
        assert evidence["score"] is None
        assert evidence["rank"] is None
        assert evidence["trigger_shape"] == "punctuated"
        assert evidence["inferred_cause"] is False

    def test_generic_ambiguous(self, taxonomy):
        rec = _make_record(trigger_value="cortex")
        category, evidence = classify(rec, taxonomy)
        assert category == "generic-ambiguous"
        assert evidence["trigger_shape"] == "single-token"

    def test_no_score_unexplained(self, taxonomy):
        rec = _make_record(trigger_value="claude iteration")
        category, evidence = classify(rec, taxonomy)
        assert category == "no-score-unexplained"
        assert evidence["trigger_shape"] == "multi-token"


# --- validate_artifact tests ---


class TestValidateArtifact:
    def test_valid_artifact(self):
        data = _make_artifact([_make_record()])
        validate_artifact(data)  # no exception

    def test_missing_records_key(self):
        data = {
            "artifact": {
                "rules_digest": "a",
                "matcher_digest": "b",
                "schema_version": "1",
                "generator_version": "1",
            }
        }
        with pytest.raises(UsableInputError, match="missing required key 'records'"):
            validate_artifact(data)

    def test_wrong_in_manifest_type(self):
        rec = _make_record()
        rec["in_manifest"] = "false"  # string, not bool
        data = _make_artifact([rec])
        with pytest.raises(UsableInputError, match="in_manifest must be bool"):
            validate_artifact(data)

    def test_wrong_score_type(self):
        rec = _make_record()
        rec["score"] = "10"  # string, not number
        data = _make_artifact([rec])
        with pytest.raises(UsableInputError, match="score must be int/float/null"):
            validate_artifact(data)

    def test_null_trigger_value(self):
        rec = _make_record()
        rec["trigger_value"] = None
        data = _make_artifact([rec])
        with pytest.raises(UsableInputError, match="trigger_value must be str"):
            validate_artifact(data)


# --- validate_sidecar_toplevel tests ---


class TestValidateSidecarToplevel:
    def test_valid_object(self):
        validate_sidecar_toplevel({})  # no exception

    def test_non_object(self):
        with pytest.raises(UsableInputError, match="top-level must be an object"):
            validate_sidecar_toplevel([1, 2, 3])


# --- Report parity test ---


class TestReportParity:
    def test_unresolved_set_matches_evaluate(self):
        from ai_rules.commands.rule_loader.audit import evaluate

        records = [
            _make_record(rule_id="rules/100-a.md", trigger_value="a", in_manifest=True),
            _make_record(rule_id="rules/100-b.md", trigger_value="b", in_manifest=False),
            _make_record(rule_id="rules/100-c.md", trigger_value="@c.d", in_manifest=False),
        ]
        identity = {
            "rules_digest": "rd1",
            "matcher_digest": "md1",
            "schema_version": "1",
            "generator_version": "1",
        }
        dispositions: dict = {}

        # evaluate
        eval_misses, _ = evaluate(records, identity, dispositions)

        # build_report
        taxonomy = load_taxonomy()
        artifact_data = _make_artifact(records, identity)
        report = build_report(artifact_data, dispositions, taxonomy, Path("a.json"), Path("d.json"))

        # Compare rule sets
        eval_rules = {(m["rule_id"], m["trigger_kind"], m["trigger_value"]) for m in eval_misses}
        report_rules = {(r["rule"], r["trigger_kind"], r["trigger_value"]) for r in report["rows"]}
        assert eval_rules == report_rules


# --- Read-only guarantee ---


class TestReadOnlyGuarantee:
    def test_sidecar_unchanged_after_report(self, tmp_path: Path):
        records = [_make_record(trigger_value="test_val")]
        identity = {
            "rules_digest": "rd1",
            "matcher_digest": "md1",
            "schema_version": "1",
            "generator_version": "1",
        }
        sidecar = {"some|key|val|rd1|md1|1|1": {"disposition": "ok"}}

        sidecar_path = tmp_path / "dispositions.json"
        sidecar_path.write_text(json.dumps(sidecar))
        original_bytes = sidecar_path.read_bytes()

        taxonomy = load_taxonomy()
        artifact_data = _make_artifact(records, identity)
        build_report(artifact_data, sidecar, taxonomy, Path("a.json"), sidecar_path)

        assert sidecar_path.read_bytes() == original_bytes


# --- Integrity error surfacing ---


class TestIntegrityErrors:
    def test_stale_key_in_integrity_errors(self):
        records = [_make_record(trigger_value="val")]
        identity = {
            "rules_digest": "rd1",
            "matcher_digest": "md1",
            "schema_version": "1",
            "generator_version": "1",
        }
        # Stale key (wrong digest)
        stale_key = "rules/100-test.md|kw|val|WRONG|md1|1|1"
        dispositions = {stale_key: {"disposition": "ok"}}

        taxonomy = load_taxonomy()
        artifact_data = _make_artifact(records, identity)
        report = build_report(artifact_data, dispositions, taxonomy, Path("a.json"), Path("d.json"))

        assert report["summary"]["unresolved_count"] == 1
        assert any("stale" in err for err in report["integrity_errors"])


# --- atomic_write_pair tests ---


class TestAtomicWritePair:
    def test_success(self, tmp_path: Path):
        json_path = tmp_path / "out.json"
        md_path = tmp_path / "out.md"
        atomic_write_pair(json_path, md_path, '{"a":1}', "# hello")
        assert json_path.read_text() == '{"a":1}'
        assert md_path.read_text() == "# hello"

    def test_failure_cleans_up(self, tmp_path: Path):
        # Make target dir read-only so rename fails
        read_only_dir = tmp_path / "locked"
        read_only_dir.mkdir()
        json_path = read_only_dir / "out.json"
        md_path = read_only_dir / "out.md"

        # Write temp files then make dir read-only
        # Actually we need a different approach — make rename fail
        # by removing write permission on the parent after temp creation
        json_tmp = json_path.with_suffix(".json.tmp")
        md_tmp = md_path.with_suffix(".md.tmp")

        # Use mock to force os.replace to fail
        original_replace = os.replace

        call_count = [0]

        def mock_replace(src, dst):
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("simulated rename failure")
            return original_replace(src, dst)

        with patch(
            "ai_rules.commands.rule_loader.audit_report.os.replace", side_effect=mock_replace
        ):
            with pytest.raises(AtomicWriteError, match="failed to rename"):
                atomic_write_pair(json_path, md_path, '{"a":1}', "# hello")

        # Final paths should not exist
        assert not json_path.exists()
        assert not md_path.exists()


# --- CLI smoke test ---


class TestCliSmoke:
    def test_full_run(self, tmp_path: Path):
        from typer import Typer

        app = Typer()
        app.command()(audit_report_cmd)

        records = [
            _make_record(trigger_value="@cache", in_manifest=False),
            _make_record(rule_id="rules/101-b.md", trigger_value="pandas", in_manifest=False),
        ]
        identity = {
            "git_sha": "abc",
            "rules_digest": "rd1",
            "matcher_digest": "md1",
            "schema_version": "1",
            "generator_version": "1",
        }
        artifact = _make_artifact(records, identity)
        sidecar: dict = {}

        audit_path = tmp_path / "audit.json"
        sidecar_path = tmp_path / "dispositions.json"
        output_path = tmp_path / "report.json"

        audit_path.write_text(json.dumps(artifact))
        sidecar_path.write_text(json.dumps(sidecar))

        result = runner.invoke(
            app,
            [
                "--audit",
                str(audit_path),
                "--dispositions",
                str(sidecar_path),
                "--output",
                str(output_path),
            ],
        )
        assert result.exit_code == 0, result.output

        # Both files created
        assert output_path.exists()
        md_path = output_path.with_suffix(".md")
        assert md_path.exists()

        # JSON envelope structure
        report = json.loads(output_path.read_text())
        assert "artifact" in report
        assert "summary" in report
        assert "integrity_errors" in report
        assert "rows" in report
        assert report["summary"]["unresolved_count"] == 2

        # Every row has required columns
        for row in report["rows"]:
            for col in (
                "rule",
                "trigger_kind",
                "trigger_value",
                "probe",
                "source",
                "score",
                "rank",
                "category",
                "evidence",
                "recommended_action",
            ):
                assert col in row

    def test_missing_artifact_exits_1(self, tmp_path: Path):
        from typer import Typer

        app = Typer()
        app.command()(audit_report_cmd)

        result = runner.invoke(
            app,
            ["--audit", str(tmp_path / "nonexistent.json"), "--output", str(tmp_path / "r.json")],
        )
        assert result.exit_code == 1

    def test_invalid_artifact_schema_exits_1(self, tmp_path: Path):
        from typer import Typer

        app = Typer()
        app.command()(audit_report_cmd)

        bad_artifact = tmp_path / "bad.json"
        bad_artifact.write_text('{"artifact": "not_an_object", "records": []}')

        result = runner.invoke(
            app,
            ["--audit", str(bad_artifact), "--output", str(tmp_path / "r.json")],
        )
        assert result.exit_code == 1


# --- Characterization test (real on-disk artifact) ---


@pytest.mark.characterization
class TestCharacterization:
    def test_real_artifact_report(self, tmp_path: Path):
        """Run the report against the real on-disk audit artifact (read-only)."""
        audit_path = Path("reports/rule-loader-corpus-audit.json")
        sidecar_path = Path("reports/rule-loader-corpus-audit-dispositions.json")

        if not audit_path.exists():
            pytest.skip("real audit artifact not present")

        artifact_data = json.loads(audit_path.read_text(encoding="utf-8"))
        sidecar_data = (
            json.loads(sidecar_path.read_text(encoding="utf-8")) if sidecar_path.exists() else {}
        )

        taxonomy = load_taxonomy()
        report = build_report(artifact_data, sidecar_data, taxonomy, audit_path, sidecar_path)

        # Write to tmp_path (not to reports/)
        out = tmp_path / "report.json"
        out.write_text(json.dumps(report, indent=2))

        assert report["summary"]["unresolved_count"] >= 0
        if report["rows"]:
            assert all(row["evidence"]["inferred_cause"] is False for row in report["rows"])
            # Every row has a valid category
            valid_cats = {e["name"] for e in taxonomy}
            for row in report["rows"]:
                assert row["category"] in valid_cats
