"""Unit tests for the rank-snapshot pure helpers (Phase 2).

Focuses on the deterministic core: canonical serialization, merge, regression
detection, and sidecar-key validation: without invoking the live corpus.
"""

from __future__ import annotations

import json

from ai_rules.commands.rule_loader import rank_snapshot as RS


def test_canonical_json_is_sorted_indented_and_newline_terminated():
    out = RS.canonical_json({"b": 1, "a": 2})
    assert out.endswith("\n")
    assert out.index('"a"') < out.index('"b"')  # sorted keys
    assert "\n  " in out  # 2-space indent


def test_canonical_json_roundtrips():
    obj = {"records": [{"fixture": "f", "rule_id": "r", "rank": None}], "n": 3}
    assert json.loads(RS.canonical_json(obj)) == obj


def _artifact(records: list[dict]) -> dict:
    return {
        "git_sha_baseline": "a",
        "git_sha_current": "b",
        "rules_digest_baseline": "c",
        "rules_digest_current": "d",
        "matcher_digest_baseline": "e",
        "matcher_digest_current": "f",
        "schema_version": "3.5",
        "generator_version": RS.GENERATOR_VERSION,
        "records": records,
    }


def test_regression_keys_detects_in_to_out_only():
    art = _artifact(
        [
            {
                "fixture": "f1",
                "rule_id": "r1",
                "in_manifest_baseline": True,
                "in_manifest_current": False,
            },
            {
                "fixture": "f2",
                "rule_id": "r2",
                "in_manifest_baseline": True,
                "in_manifest_current": True,
            },
            {
                "fixture": "f3",
                "rule_id": "r3",
                "in_manifest_baseline": False,
                "in_manifest_current": False,
            },
            {
                "fixture": "f4",
                "rule_id": "r4",
                "in_manifest_baseline": False,
                "in_manifest_current": True,
            },
        ]
    )
    assert RS._regression_keys(art) == {("f1", "r1")}


def test_build_merged_artifact_combines_baseline_and_current():
    baseline_payload = {
        "identity": {"git_sha": "gb", "rules_digest": "rb", "matcher_digest": "mb"},
        "records": [
            {"fixture": "f1", "rule_id": "r1", "rank": 1, "score": 10, "in_manifest": True},
        ],
    }
    current = {("f1", "r1"): RS.Observation(rank=3, score=8, in_manifest=True)}
    ident = RS.Identity(git_sha="gc", rules_digest="rc", matcher_digest="mc")
    art = RS.build_merged_artifact(baseline_payload, current, ident, "3.5")
    assert art["git_sha_baseline"] == "gb"
    assert art["git_sha_current"] == "gc"
    assert art["schema_version"] == "3.5"
    rec = art["records"][0]
    assert rec["rank_baseline"] == 1
    assert rec["in_manifest_baseline"] is True
    assert rec["rank_current"] == 3
    assert rec["in_manifest_current"] is True


def test_build_merged_artifact_handles_missing_halves():
    baseline_payload = {
        "identity": {"git_sha": "gb", "rules_digest": "rb", "matcher_digest": "mb"},
        "records": [
            {"fixture": "only_base", "rule_id": "r", "rank": 2, "score": 9, "in_manifest": True},
        ],
    }
    current = {("only_current", "r"): RS.Observation(rank=1, score=12, in_manifest=True)}
    ident = RS.Identity("gc", "rc", "mc")
    art = RS.build_merged_artifact(baseline_payload, current, ident, "3.5")
    by_fixture = {r["fixture"]: r for r in art["records"]}
    assert by_fixture["only_base"]["in_manifest_current"] is False
    assert by_fixture["only_base"]["rank_current"] is None
    assert by_fixture["only_current"]["in_manifest_baseline"] is False
    assert by_fixture["only_current"]["rank_baseline"] is None


def test_check_snapshot_missing_artifact(tmp_path):
    missing = tmp_path / "nope.json"
    errs = RS.check_snapshot(missing, tmp_path / "disp.json")
    assert errs and "not found" in errs[0]


def test_records_from_observations_sorted():
    obs = {
        ("f2", "rb"): RS.Observation(1, 5, True),
        ("f1", "rz"): RS.Observation(2, 4, False),
        ("f1", "ra"): RS.Observation(None, None, False),
    }
    recs = RS._records_from_observations(obs)
    keys = [(r["fixture"], r["rule_id"]) for r in recs]
    assert keys == [("f1", "ra"), ("f1", "rz"), ("f2", "rb")]
