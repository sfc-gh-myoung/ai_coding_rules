"""Phase 3 semantic-briefing and semantic-result contract tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

import pytest

from ai_rules.rule_loader_eval.manifest import (
    SEMANTIC_RESULT_SCHEMA_VERSION,
    attach_runtime_evidence,
    build_semantic_briefing,
    validate_final_manifest,
    validate_semantic_result,
)


def _write_matcher_artifact(tmp_path: Path, candidates: list[dict[str, str]]) -> tuple[Path, str]:
    artifact = tmp_path / "matcher.json"
    artifact.write_text(json.dumps({"candidate_rules": candidates}), encoding="utf-8")
    return artifact, hashlib.sha256(artifact.read_bytes()).hexdigest()


def _runtime() -> dict[str, object]:
    return {
        "runtime_id": "cortex-code",
        "status": "supported",
        "capability_ids": ["subagents", "tools"],
        "fallback": None,
    }


def _valid_result(briefing: dict[str, object]) -> dict[str, object]:
    matcher = cast("dict[str, str]", briefing["matcher"])
    scope = briefing["semantic_scope"]
    assert isinstance(scope, dict)
    soft_candidates = cast("list[dict[str, str]]", scope["soft_candidates"])
    assert isinstance(soft_candidates, list)
    return {
        "schema_version": SEMANTIC_RESULT_SCHEMA_VERSION,
        "matcher_sha256": matcher["sha256"],
        "scope_sha256": scope["sha256"],
        "decisions": [
            {"rule_path": candidate["rule_path"], "selected": True, "evidence": "prompt matches"}
            for candidate in soft_candidates
        ],
    }


def test_builds_bound_briefing_with_hard_passthrough(tmp_path: Path) -> None:
    artifact, digest = _write_matcher_artifact(
        tmp_path,
        [
            {"rule_path": "rules/000-global-core.md", "layer": "HARD"},
            {"rule_path": "rules/200-python-core.md", "layer": "SOFT", "description": "Python"},
        ],
    )

    briefing = build_semantic_briefing(artifact, digest, "Fix auth.py", _runtime())

    assert briefing["matcher"] == {"path": str(artifact), "sha256": digest}
    assert briefing["semantic_scope"]["hard_passthrough"] == ["rules/000-global-core.md"]
    assert briefing["semantic_scope"]["soft_candidates"] == [
        {"rule_path": "rules/200-python-core.md", "excerpt": "rules/200-python-core.md | Python"}
    ]


def test_rejects_digest_mismatch(tmp_path: Path) -> None:
    artifact, _ = _write_matcher_artifact(tmp_path, [])

    with pytest.raises(ValueError, match="SHA-256"):
        build_semantic_briefing(artifact, "0" * 64, "Fix auth.py", _runtime())


def test_rejects_more_than_eight_soft_candidates(tmp_path: Path) -> None:
    candidates = [
        {"rule_path": f"rules/{index:03d}-example.md", "layer": "SOFT"} for index in range(9)
    ]
    artifact, digest = _write_matcher_artifact(tmp_path, candidates)

    with pytest.raises(ValueError, match="candidate cap exceeded"):
        build_semantic_briefing(artifact, digest, "Fix auth.py", _runtime())


def test_semantic_result_requires_matching_scope_and_decisions(tmp_path: Path) -> None:
    artifact, digest = _write_matcher_artifact(
        tmp_path, [{"rule_path": "rules/200-python-core.md", "layer": "SOFT"}]
    )
    briefing = build_semantic_briefing(artifact, digest, "Fix auth.py", _runtime())
    result = _valid_result(briefing)

    assert validate_semantic_result(result, briefing) == []

    result["scope_sha256"] = "0" * 64
    assert "scope_sha256 does not match the briefing" in validate_semantic_result(result, briefing)


def test_semantic_result_rejects_runtime_attestation(tmp_path: Path) -> None:
    artifact, digest = _write_matcher_artifact(
        tmp_path, [{"rule_path": "rules/200-python-core.md", "layer": "SOFT"}]
    )
    briefing = build_semantic_briefing(artifact, digest, "Fix auth.py", _runtime())
    result = _valid_result(briefing)
    result["runtime_evidence"] = {"status": "attested"}

    issues = validate_semantic_result(result, briefing)

    assert "semantic result must not contain coordinator-owned field 'runtime_evidence'" in issues


def test_coordinator_attaches_runtime_evidence_and_preserves_hard_order(tmp_path: Path) -> None:
    artifact, digest = _write_matcher_artifact(
        tmp_path,
        [
            {"rule_path": "rules/000-global-core.md", "layer": "HARD"},
            {"rule_path": "rules/200-python-core.md", "layer": "SOFT"},
            {"rule_path": "rules/206-python-pytest.md", "layer": "SOFT"},
        ],
    )
    briefing = build_semantic_briefing(artifact, digest, "Fix auth.py", _runtime())
    result = _valid_result(briefing)
    decisions = result["decisions"]
    assert isinstance(decisions, list)
    decisions[1]["selected"] = False
    runtime_evidence = {
        "runtime": "cortex-code",
        "capability_ids": ["tools"],
        "invocation_id": "call-1",
        "result_id": "result-1",
        "status": "attested",
    }

    manifest = attach_runtime_evidence(result, briefing, runtime_evidence)

    assert manifest["load_sequence"] == [
        "rules/000-global-core.md",
        "rules/200-python-core.md",
    ]
    assert manifest["deferred_rules"] == [
        {"rule_path": "rules/206-python-pytest.md", "reason": "semantic_rejected"}
    ]
    assert validate_final_manifest(manifest, briefing) == []


def test_final_manifest_rejects_wrong_partition_and_runtime_status(tmp_path: Path) -> None:
    artifact, digest = _write_matcher_artifact(
        tmp_path,
        [
            {"rule_path": "rules/000-global-core.md", "layer": "HARD"},
            {"rule_path": "rules/200-python-core.md", "layer": "SOFT"},
        ],
    )
    briefing = build_semantic_briefing(artifact, digest, "Fix auth.py", _runtime())
    manifest = attach_runtime_evidence(
        _valid_result(briefing),
        briefing,
        {"runtime": "unsupported", "capability_ids": [], "status": "attested"},
    )
    manifest["load_sequence"] = ["rules/200-python-core.md"]

    issues = validate_final_manifest(manifest, briefing)

    assert "unsupported runtime requires status='unsupported'" in issues
    assert "HARD candidates must lead the final load_sequence in briefing order" in issues
