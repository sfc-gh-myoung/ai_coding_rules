"""Unit tests for the rank-snapshot pure helpers (Phase 2).

Focuses on the deterministic core: canonical serialization, merge, regression
detection, and sidecar-key validation: without invoking the live corpus.
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.rule_loader import rank_snapshot as RS

_runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})


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


# ── identity helpers (no live corpus) ───────────────────────────────────────


def test_default_baseline_path_derives_suffix():
    assert RS._default_baseline_path(RS.Path("reports/snap.json")) == RS.Path(
        "reports/snap.baseline.json"
    )


def test_git_sha_real_repo_and_unknown(tmp_path):
    # Real repo root resolves to a concrete SHA (40 hex chars).
    root = RS.find_project_root()
    sha = RS._git_sha(root)
    assert sha != "unknown"
    assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha)
    # A non-git directory falls back to "unknown".
    assert RS._git_sha(tmp_path) == "unknown"


def test_rules_digest_is_stable_and_excludes_readme(tmp_path):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "100-a.md").write_text("alpha", encoding="utf-8")
    (rules / "200-b.md").write_text("beta", encoding="utf-8")
    d1 = RS._rules_digest(rules)
    assert len(d1) == 64
    # README.md is skipped, so adding it must not change the digest.
    (rules / "README.md").write_text("ignore me", encoding="utf-8")
    assert RS._rules_digest(rules) == d1
    # Changing a real rule's bytes changes the digest.
    (rules / "100-a.md").write_text("alpha-2", encoding="utf-8")
    assert RS._rules_digest(rules) != d1


def test_matcher_digest_success_and_oserror(tmp_path):
    root = RS.find_project_root()
    assert len(RS._matcher_digest(root)) == 64
    # tmp_path has no src/ai_rules/match_rules.py → OSError → "unknown".
    assert RS._matcher_digest(tmp_path) == "unknown"


def test_schema_version_parses_quoted_unquoted_and_unknown(tmp_path):
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    schema = schemas / "rule-schema.yml"
    schema.write_text('version: "3.5"\nother: x\n', encoding="utf-8")
    assert RS._schema_version(tmp_path) == "3.5"
    schema.write_text("version: 4.0\n", encoding="utf-8")
    assert RS._schema_version(tmp_path) == "4.0"
    schema.write_text("no_version_here: true\n", encoding="utf-8")
    assert RS._schema_version(tmp_path) == "unknown"


def test_schema_version_missing_file_is_unknown(tmp_path):
    # No schemas/ directory at all → OSError → "unknown".
    assert RS._schema_version(tmp_path) == "unknown"


def test_identity_capture_from_bare_dirs(tmp_path):
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "100-a.md").write_text("a", encoding="utf-8")
    ident = RS.Identity.capture(tmp_path, rules)
    assert ident.git_sha == "unknown"  # tmp_path is not a git repo
    assert ident.matcher_digest == "unknown"  # no match_rules.py under tmp_path
    assert len(ident.rules_digest) == 64


# ── compute_observations against the real (deterministic) corpus ────────────


def test_compute_observations_over_real_corpus():
    root, db, fixtures = RS._load_project()
    assert db and fixtures
    obs = RS.compute_observations(fixtures[:3], db)
    assert obs, "expected at least one (fixture, rule) observation"
    for (fixture_id, rule_id), o in obs.items():
        assert isinstance(fixture_id, str) and isinstance(rule_id, str)
        assert isinstance(o.in_manifest, bool)
        assert o.rank is None or isinstance(o.rank, int)


# ── capture_baseline / capture_current (corpus + identity mocked) ───────────


@pytest.fixture
def _mock_corpus(monkeypatch, tmp_path):
    """Isolate capture/check from the live corpus with a fixed observation set."""
    obs = {("f1", "rules/100-a.md"): RS.Observation(rank=2, score=7, in_manifest=True)}
    monkeypatch.setattr(RS, "_load_project", lambda: (tmp_path, {}, []))
    monkeypatch.setattr(RS, "compute_observations", lambda fixtures, db: obs)
    monkeypatch.setattr(
        RS.Identity, "capture", classmethod(lambda cls, r, d: RS.Identity("gc", "rc", "mc"))
    )
    monkeypatch.setattr(RS, "_schema_version", lambda root: "3.5")
    return obs


def test_capture_baseline_then_current_roundtrip(_mock_corpus, tmp_path):
    output = tmp_path / "snap.json"
    baseline_path = RS.capture_baseline(output)
    assert baseline_path == tmp_path / "snap.baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    assert baseline["stage"] == "baseline"
    assert baseline["records"][0]["fixture"] == "f1"

    artifact = RS.capture_current(output)
    assert artifact["git_sha_baseline"] == "gc"
    assert artifact["schema_version"] == "3.5"
    assert artifact["generator_version"] == RS.GENERATOR_VERSION
    # The merged file was written canonically.
    assert output.read_text(encoding="utf-8") == RS.canonical_json(artifact)


def test_capture_current_missing_baseline_raises(_mock_corpus, tmp_path):
    with pytest.raises(FileNotFoundError, match="baseline half not found"):
        RS.capture_current(tmp_path / "never-captured.json")


# ── check_snapshot branches ─────────────────────────────────────────────────


def _full_records(*, base_in=True, cur_in=False):
    return [
        {
            "fixture": "f1",
            "rule_id": "rules/100-a.md",
            "rank_baseline": 1,
            "score_baseline": 9,
            "in_manifest_baseline": base_in,
            "rank_current": None,
            "score_current": None,
            "in_manifest_current": cur_in,
        }
    ]


def _committed_artifact(records):
    return {
        "git_sha_baseline": "gb",
        "git_sha_current": "gc",
        "rules_digest_baseline": "rb",
        "rules_digest_current": "rc",
        "matcher_digest_baseline": "mb",
        "matcher_digest_current": "mc",
        "schema_version": "3.5",
        "generator_version": RS.GENERATOR_VERSION,
        "records": records,
    }


@pytest.fixture
def _mock_check(monkeypatch, tmp_path):
    """Make check_snapshot's regen deterministic and matching the committed 'current' half."""
    # Regenerated observation matches _full_records current half (None/None/False).
    regen = {("f1", "rules/100-a.md"): RS.Observation(rank=None, score=None, in_manifest=False)}
    monkeypatch.setattr(RS, "_load_project", lambda: (tmp_path, {}, []))
    monkeypatch.setattr(RS, "compute_observations", lambda fixtures, db: regen)
    monkeypatch.setattr(
        RS.Identity, "capture", classmethod(lambda cls, r, d: RS.Identity("gc", "rc", "mc"))
    )


def test_check_snapshot_invalid_json(tmp_path):
    art = tmp_path / "snap.json"
    art.write_text("not json", encoding="utf-8")
    errs = RS.check_snapshot(art, tmp_path / "disp.json")
    assert errs and "not valid JSON" in errs[0]


def test_check_snapshot_non_canonical_form(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    # Compact (non-canonical) but semantically valid; disposition covers the regression.
    art.write_text(json.dumps(_committed_artifact(_full_records())), encoding="utf-8")
    disp = tmp_path / "disp.json"
    disp.write_text(json.dumps([{"fixture": "f1", "rule_id": "rules/100-a.md"}]), encoding="utf-8")
    errs = RS.check_snapshot(art, disp)
    assert any("not in canonical JSON form" in e for e in errs)


def test_check_snapshot_identity_mismatches(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    bad = _committed_artifact(_full_records())
    bad["git_sha_current"] = "STALE"
    bad["rules_digest_current"] = "STALE"
    bad["matcher_digest_current"] = "STALE"
    art.write_text(RS.canonical_json(bad), encoding="utf-8")
    disp = tmp_path / "disp.json"
    disp.write_text(json.dumps([{"fixture": "f1", "rule_id": "rules/100-a.md"}]), encoding="utf-8")
    errs = RS.check_snapshot(art, disp)
    assert any("git_sha_current mismatch" in e for e in errs)
    assert any("rules_digest_current mismatch" in e for e in errs)
    assert any("matcher_digest_current mismatch" in e for e in errs)


def test_check_snapshot_regen_mismatch(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    # Committed 'current' says in_manifest True, but regen says False → mismatch.
    recs = _full_records(cur_in=True)
    recs[0]["rank_current"] = 5
    art.write_text(RS.canonical_json(_committed_artifact(recs)), encoding="utf-8")
    errs = RS.check_snapshot(art, tmp_path / "disp.json")
    assert any("regenerated current observations differ" in e for e in errs)


def test_check_snapshot_dispositions_invalid_json(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    art.write_text(RS.canonical_json(_committed_artifact(_full_records())), encoding="utf-8")
    disp = tmp_path / "disp.json"
    disp.write_text("{bad", encoding="utf-8")
    errs = RS.check_snapshot(art, disp)
    assert any("dispositions sidecar is not valid JSON" in e for e in errs)


def test_check_snapshot_duplicate_and_stale_dispositions(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    art.write_text(RS.canonical_json(_committed_artifact(_full_records())), encoding="utf-8")
    disp = tmp_path / "disp.json"
    disp.write_text(
        json.dumps(
            {
                "dispositions": [
                    {"fixture": "f1", "rule_id": "rules/100-a.md"},
                    {"fixture": "f1", "rule_id": "rules/100-a.md"},  # duplicate
                    {"fixture": "zz", "rule_id": "rules/999.md"},  # stale
                ]
            }
        ),
        encoding="utf-8",
    )
    errs = RS.check_snapshot(art, disp)
    assert any("duplicate sidecar disposition" in e for e in errs)
    assert any("stale sidecar disposition" in e for e in errs)


def test_check_snapshot_unexplained_regression(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    art.write_text(RS.canonical_json(_committed_artifact(_full_records())), encoding="utf-8")
    # No dispositions file at all → the regression is unexplained.
    errs = RS.check_snapshot(art, tmp_path / "missing-disp.json")
    assert any("unexplained regression without sidecar disposition" in e for e in errs)


def test_check_snapshot_happy_path(_mock_check, tmp_path):
    art = tmp_path / "snap.json"
    art.write_text(RS.canonical_json(_committed_artifact(_full_records())), encoding="utf-8")
    disp = tmp_path / "disp.json"
    disp.write_text(json.dumps([{"fixture": "f1", "rule_id": "rules/100-a.md"}]), encoding="utf-8")
    assert RS.check_snapshot(art, disp) == []


# ── CLI command wiring ──────────────────────────────────────────────────────


def test_cli_check_passes(monkeypatch, tmp_path):
    monkeypatch.setattr(RS, "check_snapshot", lambda output, disp: [])
    art = tmp_path / "snap.json"
    art.write_text("{}", encoding="utf-8")
    result = _runner.invoke(app, ["rule-loader", "rank-snapshot", "--check", str(art)])
    assert result.exit_code == 0, result.output
    assert "check passed" in result.output


def test_cli_check_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(RS, "check_snapshot", lambda output, disp: ["boom"])
    art = tmp_path / "snap.json"
    art.write_text("{}", encoding="utf-8")
    result = _runner.invoke(app, ["rule-loader", "rank-snapshot", "--check", str(art)])
    assert result.exit_code == 1


def test_cli_stage_baseline(monkeypatch, tmp_path):
    called = {}

    def _fake_baseline(output):
        called["output"] = output
        return tmp_path / "snap.baseline.json"

    monkeypatch.setattr(RS, "capture_baseline", _fake_baseline)
    result = _runner.invoke(
        app,
        [
            "rule-loader",
            "rank-snapshot",
            "--stage",
            "baseline",
            "--output",
            str(tmp_path / "snap.json"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert called["output"] == tmp_path / "snap.json"


def test_cli_stage_current(monkeypatch, tmp_path):
    monkeypatch.setattr(RS, "capture_current", lambda output: {"records": []})
    result = _runner.invoke(
        app,
        [
            "rule-loader",
            "rank-snapshot",
            "--stage",
            "current",
            "--output",
            str(tmp_path / "snap.json"),
        ],
    )
    assert result.exit_code == 0, result.output


def test_cli_no_args_exits_4():
    result = _runner.invoke(app, ["rule-loader", "rank-snapshot"])
    assert result.exit_code == 4
