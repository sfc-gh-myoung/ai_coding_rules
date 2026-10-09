"""Phase 6: eval semantics split: six-gate result taxonomy.

Exercises the manifest-recall vs agent-compliance attribution and the
fixed-precedence ``result`` taxonomy (Section 6 truth table), plus the
legacy fallback for rows without a captured manifest and the reader-side
legacy classifier.
"""

from __future__ import annotations

from ai_rules.rule_loader_eval.agent_runner import AgentRun
from ai_rules.rule_loader_eval.diagnostics import SignalReport
from ai_rules.rule_loader_eval.engine import RunResult
from ai_rules.rule_loader_eval.matcher import MatchResult
from ai_rules.rule_loader_eval.results_schemas import (
    classify_loaded_result,
    serialize_run_result,
)

FOUND = "rules/000-global-core.md"


def _rr(
    *,
    required=(),
    manifest=None,
    loaded=(),
    signal_ok=True,
    drifts=(),
    output_violations=(),
    infra=False,
    cited_without_read=(),
    cited_without_manifest=(),
    forbidden=(),
):
    """Build a RunResult with explicit manifest/loaded/required sets.

    ``manifest=None`` models a legacy/unit row where the manifest was not
    captured; any other value (including an empty set) models a captured
    manifest.
    """
    manifest_paths = None if manifest is None else frozenset(manifest)
    loaded_full = (FOUND, *loaded)
    run = AgentRun(
        fixture_id="fx",
        loaded=loaded_full,
        loaded_via_reads=loaded_full,
        loaded_via_reads_performed=(),
        loaded_via_section=loaded_full,
        output_violations=tuple(output_violations),
        is_infra_error=infra,
        manifest_paths=manifest_paths,
    )
    # match.passed reflects whether the agent loaded all required rules.
    req_set = {r for r in required if r != FOUND}
    loaded_set = set(loaded)
    match = MatchResult(
        missing_required=tuple(sorted(req_set - loaded_set)),
        missing_dependencies=(),
        forbidden_present=tuple(forbidden),
        optional_loaded=(),
        passed=(req_set <= loaded_set) and not forbidden,
    )
    # A read/cite fabrication forces signal_report.ok False (mirrors diagnostics).
    sr_ok = signal_ok and not cited_without_read and not cited_without_manifest
    return RunResult(
        fixture_id="fx",
        run=run,
        match=match,
        signal_report=SignalReport(
            ok=sr_ok,
            disagreements=(),
            cited_without_read=tuple(cited_without_read),
            cited_without_manifest=tuple(cited_without_manifest),
        ),
        citation_drifts=tuple(drifts),
        effective_loaded=loaded_full,
        required=tuple(required),
    )


# ── taxonomy ─────────────────────────────────────────────────────────────────


def test_pass() -> None:
    rr = _rr(required=("rules/112-x.md",), manifest={"rules/112-x.md"}, loaded=("rules/112-x.md",))
    assert rr.result == "pass"
    assert rr.passed is True
    assert rr.manifest_recall and rr.agent_compliance


def test_matcher_miss() -> None:
    # Required rule absent from manifest and not recovered.
    rr = _rr(required=("rules/112-x.md",), manifest={"rules/999-other.md"}, loaded=())
    assert rr.result == "matcher-miss"
    assert rr.passed is False
    assert rr.out_of_manifest_recovery["count"] == 0


def test_recovery_only() -> None:
    # Absent from manifest but the agent loaded it anyway (out-of-manifest recovery).
    rr = _rr(
        required=("rules/112-x.md",), manifest={"rules/999-other.md"}, loaded=("rules/112-x.md",)
    )
    assert rr.result == "recovery-only"
    assert rr.passed is False
    assert rr.out_of_manifest_recovery == {"count": 1, "rules": ["rules/112-x.md"]}


def test_agent_miss() -> None:
    # In manifest but the agent failed to load it.
    rr = _rr(required=("rules/112-x.md",), manifest={"rules/112-x.md"}, loaded=())
    assert rr.result == "agent-miss"
    assert rr.passed is False
    assert rr.manifest_recall is True
    assert rr.agent_compliance is False


def test_empty_manifest() -> None:
    # Non-empty required set but the injected manifest had no non-foundation rules.
    rr = _rr(required=("rules/112-x.md",), manifest={FOUND}, loaded=())
    assert rr.manifest_empty is True
    assert rr.result == "empty-manifest"
    assert rr.passed is False


def test_empty_manifest_captured_empty_set() -> None:
    # A captured manifest with zero candidates (what the real pipeline produces
    # when the matcher matches nothing: foundation is filtered out upstream)
    # must classify as empty-manifest, not fall back to legacy scoring.
    rr = _rr(required=("rules/112-x.md",), manifest=set(), loaded=())
    assert rr.manifest_available is True
    assert rr.manifest_empty is True
    assert rr.result == "empty-manifest"
    assert rr.passed is False


def test_empty_manifest_precedes_recovery() -> None:
    # Manifest empty AND the agent recovered the rule → empty-manifest wins.
    rr = _rr(required=("rules/112-x.md",), manifest={FOUND}, loaded=("rules/112-x.md",))
    assert rr.result == "empty-manifest"


def test_signal_violation() -> None:
    # Manifest + agent gates pass, but a legacy gate (signal) failed.
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        signal_ok=False,
    )
    assert rr.result == "signal-violation"
    assert rr.passed is False


def test_infra_error_wins() -> None:
    rr = _rr(required=("rules/112-x.md",), manifest={"rules/112-x.md"}, loaded=(), infra=True)
    assert rr.result == "error"


# ── model-skipped-reads: infra healthy, model cited unread rules ─────────────


def test_model_skipped_reads_cited_without_read() -> None:
    # Manifest recalled the rule and the agent loaded it (infra healthy), but the
    # model cited a rule it never read. Non-scored model behavior, not a failure.
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_read=("rules/112-x.md",),
    )
    assert rr.result == "model-skipped-reads"
    assert rr.passed is False
    assert rr.scored is False
    assert rr.manifest_recall and rr.agent_compliance


def test_model_skipped_reads_cited_without_manifest() -> None:
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_manifest=("rules/999-hallucinated.md",),
    )
    assert rr.result == "model-skipped-reads"
    assert rr.scored is False


def test_citation_drift_still_signal_violation() -> None:
    # A read/cite fabrication PLUS citation drift is not a pure model-skip: the
    # drift is a genuine protocol violation, so it stays a scored failure.
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_read=("rules/112-x.md",),
        drifts=("rules/112-x.md",),
    )
    assert rr.result == "signal-violation"
    assert rr.scored is True


def test_output_violation_still_signal_violation() -> None:
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_read=("rules/112-x.md",),
        output_violations=("missing Rules Loaded (Gate 3 or **Rules Loaded**) section",),
    )
    assert rr.result == "signal-violation"
    assert rr.scored is True


def test_forbidden_present_still_signal_violation() -> None:
    # match fails via a forbidden rule → not a pure model-skip.
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_read=("rules/112-x.md",),
        forbidden=("rules/900-forbidden.md",),
    )
    assert rr.result == "signal-violation"


def test_scored_property_across_buckets() -> None:
    passed = _rr(
        required=("rules/112-x.md",), manifest={"rules/112-x.md"}, loaded=("rules/112-x.md",)
    )
    skipped = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_read=("rules/112-x.md",),
    )
    infra = _rr(required=("rules/112-x.md",), manifest={"rules/112-x.md"}, loaded=(), infra=True)
    violation = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        signal_ok=False,
    )
    assert passed.scored is True
    assert skipped.scored is False
    assert infra.scored is False
    assert violation.scored is True


def test_no_required_rules_passes_with_empty_manifest() -> None:
    # A no-match fixture (only foundation required) is not an empty-manifest failure.
    rr = _rr(required=(FOUND,), manifest={FOUND}, loaded=())
    assert rr.result == "pass"
    assert rr.passed is True


# ── legacy fallback (no captured manifest) ───────────────────────────────────


def test_legacy_row_uses_pre_phase6_semantics() -> None:
    rr = _rr(required=("rules/112-x.md",), manifest=None, loaded=("rules/112-x.md",))
    assert rr.manifest_available is False
    assert rr.result == "pass"
    assert rr.passed is True


def test_legacy_row_fail() -> None:
    rr = _rr(required=("rules/112-x.md",), manifest=None, loaded=(), signal_ok=False)
    assert rr.result == "fail"
    assert rr.passed is False


# ── reader-side legacy classification ────────────────────────────────────────


def test_classify_loaded_result_legacy_when_fields_absent() -> None:
    assert classify_loaded_result({"result": "pass"}) == "legacy"


def test_classify_loaded_result_current_record() -> None:
    doc = {
        "result": "recovery-only",
        "manifest_recall": False,
        "agent_compliance": True,
        "manifest_empty": False,
    }
    assert classify_loaded_result(doc) == "recovery-only"


# ── serialization carries the new fields ─────────────────────────────────────


def test_serialize_emits_manifest_available() -> None:
    captured = _rr(required=("rules/112-x.md",), manifest=set(), loaded=())
    legacy = _rr(required=("rules/112-x.md",), manifest=None, loaded=("rules/112-x.md",))
    assert serialize_run_result(captured, run_number=1)["manifest_available"] is True
    assert serialize_run_result(legacy, run_number=1)["manifest_available"] is False


def test_serialize_emits_phase6_fields() -> None:
    rr = _rr(required=("rules/112-x.md",), manifest={"rules/999.md"}, loaded=("rules/112-x.md",))
    doc = serialize_run_result(rr, run_number=1)
    assert doc["result"] == "recovery-only"
    assert doc["manifest_recall"] is False
    assert doc["agent_compliance"] is True
    assert doc["manifest_empty"] is False
    assert doc["out_of_manifest_recovery"]["count"] == 1


def test_serialize_emits_model_skipped_reads() -> None:
    rr = _rr(
        required=("rules/112-x.md",),
        manifest={"rules/112-x.md"},
        loaded=("rules/112-x.md",),
        cited_without_read=("rules/112-x.md",),
    )
    doc = serialize_run_result(rr, run_number=1)
    assert doc["result"] == "model-skipped-reads"
    assert doc["passed"] is False
