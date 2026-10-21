"""Evidence-bound report contracts, independent of the live evaluator."""

import json
from pathlib import Path

import pytest

from ai_rules.rule_loader_eval.evidence_report import (
    ReportError,
    build_payload,
    create_selection,
    repeated_success,
    verify_artifact,
    write_generation,
)


def make_run(root: Path, model="openai-gpt-6-sol", outcomes=("pass", "pass", "pass")):
    directory = root / model
    directory.mkdir()
    manifest = {
        "model_requested": model,
        "git": {"sha": "baseline"},
        "fixture_selection": ["python-task"],
        "fixture_count": 1,
        "effort": "medium",
        "max_turns": 25,
        "concurrency": 3,
        "runs_requested": len(outcomes),
        "strict_forbidden": False,
        "connection": "local-test",
        "mode": "plugin",
        "ai_rules_version": "4.0.0",
    }
    (directory / "manifest.json").write_text(json.dumps(manifest))
    for number, outcome in enumerate(outcomes, 1):
        fixtures = directory / f"run-{number:02d}" / "fixtures"
        fixtures.mkdir(parents=True)
        (fixtures / "python-task.json").write_text(
            json.dumps(
                {
                    "schema_version": "ai-rules-eval-fixture/v1",
                    "fixture_id": "python-task",
                    "run_number": number,
                    "model": model,
                    "result": outcome,
                    "passed": outcome == "pass",
                    "is_infra_error": outcome == "error",
                    "input_tokens": 100,
                    "cache_creation_input_tokens": 20,
                    "cache_read_input_tokens": 30,
                    "output_tokens": 10,
                    "duration_ms": 2000,
                    "turns": 2,
                    "loaded_via_reads": [],
                    "match": {},
                    "signal_report": {"ok": True},
                    "citation_drifts": [],
                    "output_violations": [],
                    "depends_ok": True,
                }
            )
        )
    return directory


def test_exact_subset_metrics():
    assert repeated_success(4, 5, 3) == (1, 0.4)
    assert repeated_success(2, 5, 3) == (0.9, 0)
    assert repeated_success(1, 2, 3) == (None, None)


def test_skipped_reads_remain_in_protocol_denominator(tmp_path):
    run = make_run(tmp_path, outcomes=("pass", "model-skipped-reads", "pass"))
    payload = build_payload(create_selection([run]))
    configuration = payload["configurations"][0]
    assert configuration["metrics"]["pass_at_1"]["value"] == pytest.approx(2 / 3)
    assert configuration["metrics"]["scored_rate"]["value"] == 1
    assert configuration["metrics"]["pass_all_3"]["value"] == 0
    assert configuration["outcomes"]["model-skipped-reads"] == 1


def test_source_changes_fail_closed(tmp_path):
    run = make_run(tmp_path)
    selection = create_selection([run])
    (run / "manifest.json").write_text("{}")
    with pytest.raises(ReportError, match="changed"):
        build_payload(selection)


def test_partial_retry_never_replaces_selected_complete_run(tmp_path):
    complete = make_run(tmp_path)
    retry = make_run(tmp_path, model="retry", outcomes=("error",))
    selection = create_selection([complete], archives=[retry], exclusions={"glm-5.2": "excluded"})
    payload = build_payload(selection)
    assert payload["totals"]["observed"] == 3
    assert payload["archives"][0]["observed"] == 1
    assert payload["exclusions"] == {"glm-5.2": "excluded"}


def test_duplicate_selected_configuration_rejected(tmp_path):
    run = make_run(tmp_path)
    with pytest.raises(ReportError, match="duplicate"):
        create_selection([run, run])


def test_incompatible_protocol_rejected(tmp_path):
    first = make_run(tmp_path)
    second = make_run(tmp_path, model="openai-gpt-6-luna")
    manifest_path = second / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["effort"] = "high"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ReportError, match="incompatible"):
        build_payload(create_selection([first, second]))


def test_missing_cost_capture_is_not_zero(tmp_path):
    run = make_run(tmp_path)
    path = run / "run-01" / "fixtures" / "python-task.json"
    sample = json.loads(path.read_text())
    del sample["output_tokens"]
    path.write_text(json.dumps(sample))
    metric = build_payload(create_selection([run]))["configurations"][0]["metrics"]["credits"]
    assert metric["value"] is not None
    assert metric["status"] == "partial"
    assert metric["captured"] == 2


def test_atomic_generation_and_verification(tmp_path):
    run = make_run(tmp_path)
    payload = build_payload(create_selection([run]))
    generation = write_generation(payload, tmp_path / "reports")
    assert verify_artifact(generation)["observed"] == 3
    assert (generation / "report.html").is_file()
    second = write_generation(payload, tmp_path / "reports")
    assert generation != second
    with pytest.raises(ReportError, match="evidence"):
        write_generation(payload, run / "output")


def test_inspection_has_no_ranking_eligibility(tmp_path):
    run = make_run(tmp_path)
    payload = build_payload(create_selection([run]), inspection=True)
    assert payload["mode"] == "inspection"
    assert not payload["configurations"][0]["eligible"]


def test_selection_rejects_traversal_and_invalid_rates(tmp_path):
    selection = create_selection([make_run(tmp_path)])
    selection["selected"][0]["digests"]["../outside"] = "a" * 64
    with pytest.raises(ReportError, match="relative path"):
        build_payload(selection)
    del selection["selected"][0]["digests"]["../outside"]
    selection["pricing"]["models"][0]["input_credits_per_million"] = -1
    with pytest.raises(ReportError, match="pricing rate"):
        build_payload(selection)


def test_real_wildcard_manifest_inventory(tmp_path):
    run = make_run(tmp_path)
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["fixture_selection"] = ["all"]
    manifest_path.write_text(json.dumps(manifest))
    assert build_payload(create_selection([run]))["totals"]["observed"] == 3


def test_equal_fixture_weight_and_partial_cohort(tmp_path):
    run = make_run(tmp_path)
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["fixture_selection"].append("missing-task")
    manifest["fixture_count"] = 2
    manifest_path.write_text(json.dumps(manifest))
    row = build_payload(create_selection([run]))["configurations"][0]
    assert row["missing"] == 3
    assert not row["eligible"]
    assert row["metrics"]["pass_at_1"]["status"] == "partial"
    assert row["metrics"]["pass_at_3"]["captured"] == 1


def test_report_cli_does_not_authenticate(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    from ai_rules.cli import app

    selection = tmp_path / "selection.json"
    selection.write_text(json.dumps(create_selection([make_run(tmp_path)])))
    monkeypatch.setenv("SNOWFLAKE_CONNECTION_NAME", "must-not-authenticate")
    result = CliRunner().invoke(
        app,
        [
            "rule-loader",
            "report",
            "--selection",
            str(selection),
            "--output",
            str(tmp_path / "reports"),
        ],
    )
    assert result.exit_code == 0, result.output
    generations = list((tmp_path / "reports").glob("eval-report-*"))
    assert len(generations) == 1
    verification = CliRunner().invoke(app, ["rule-loader", "verify-report", str(generations[0])])
    assert verification.exit_code == 0, verification.output


def test_cli_rejects_ambiguous_inputs(tmp_path):
    from typer.testing import CliRunner

    from ai_rules.cli import app

    result = CliRunner().invoke(
        app, ["rule-loader", "report", "--selection", "x.json", "--results-dir", str(tmp_path)]
    )
    assert result.exit_code == 4
    assert "mutually exclusive" in result.output
