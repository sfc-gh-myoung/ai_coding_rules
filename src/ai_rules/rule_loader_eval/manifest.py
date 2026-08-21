"""Validator for rule-loader-matcher/v1 and staged-loader artifacts.

Public API
----------
- ``validate_matcher_manifest(manifest: dict) -> list[str]``
    Validate a rule-loader-matcher/v1 dict. Empty list means valid.

- ``validate_manifest(manifest: dict) -> list[str]``
    Rejects legacy loader manifests (schema versions v1 and v2); delegates to validate_matcher_manifest for matcher/v1.

- ``load_and_validate_manifest(path) -> list[str]``
    Read a JSON file and validate it as a rule-loader-matcher/v1.

- ``build_semantic_briefing(...)`` / ``validate_semantic_result(...)``
    Semantic-stage briefing builder and result validator.

- ``attach_runtime_evidence(...)`` / ``validate_final_manifest(...)``
    Coordinator-owned final manifest builder and validator.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

# ── constants ────────────────────────────────────────────────────────────────

# Deprecated schema versions — rejected by validate_manifest; kept for tests.
_LEGACY_SCHEMA_VERSIONS: frozenset[str] = frozenset(
    {"rule-loader-manifest/v1", "rule-loader-manifest/v2"}
)
MATCHER_SCHEMA_VERSION = "rule-loader-matcher/v1"
SEMANTIC_BRIEFING_SCHEMA_VERSION = "rule-loader-semantic-briefing/v1"
SEMANTIC_RESULT_SCHEMA_VERSION = "rule-loader-semantic/v1"
FINAL_MANIFEST_SCHEMA_VERSION = "rule-loader-manifest/v3"
MAX_SEMANTIC_CANDIDATES = 8
_RUNTIME_ATTESTATION_KEYS = frozenset({"runtime", "runtime_evidence", "attestation"})

# Keys whose presence in any rule entry signals an accidentally embedded body.
_BODY_LIKE_KEYS: frozenset[str] = frozenset(
    {"content", "body", "text", "markdown", "file_contents"}
)

# String values longer than this in any manifest entry are treated as embedded
# rule-body content (heuristic limit, ~600 chars).
_MAX_ENTRY_STR_LEN = 600


# ── helpers ──────────────────────────────────────────────────────────────────


def _check_rule_path(value: Any, location: str) -> list[str]:
    """Return issues if *value* is not a valid rule_path string."""
    if not isinstance(value, str):
        return [f"{location}: rule_path must be a string, got {type(value).__name__!r}"]
    if not value.startswith("rules/"):
        return [f"{location}: rule_path must start with 'rules/', got {value!r}"]
    return []


def _check_body_content(entry: dict[str, Any], location: str) -> list[str]:
    """Reject entries that contain body-like keys or suspiciously long values."""
    issues: list[str] = []
    for key, val in entry.items():
        if key in _BODY_LIKE_KEYS:
            issues.append(
                f"{location}: disallowed body-like key {key!r} - rule body content in manifest"
            )
        elif isinstance(val, str) and len(val) > _MAX_ENTRY_STR_LEN:
            issues.append(
                f"{location}: key {key!r} value length {len(val)} exceeds "
                f"{_MAX_ENTRY_STR_LEN} chars - rule body content in manifest"
            )
    return issues


# ── semantic-stage helpers ───────────────────────────────────────────────────


def _canonical_sha256(value: Any) -> str:
    """Return the SHA-256 digest of canonical JSON for a JSON-compatible value."""
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_json_object(path: Path) -> tuple[dict[str, Any], bytes]:
    """Read a JSON object and its raw bytes from a path, or raise a descriptive ValueError.

    Returns the decoded object together with the exact bytes it was parsed from so
    callers can hash the same bytes they parsed, without a second read.
    """
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read matcher artifact: {exc}") from exc
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid matcher JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise ValueError("matcher artifact must be a JSON object")
    return decoded, raw


def _rule_layer(entry: Mapping[str, Any]) -> str:
    """Return a candidate layer, defaulting to SOFT for legacy matcher entries."""
    return str(entry.get("layer", "SOFT")).upper()


def _candidate_excerpt(entry: Mapping[str, Any]) -> str:
    """Build a bounded matcher-owned excerpt for a semantic worker."""
    rule_path = str(entry.get("rule_path", ""))
    description = str(entry.get("description", "")).strip()
    context_tier = str(entry.get("context_tier", "")).strip()
    return " | ".join(part for part in (rule_path, context_tier, description) if part)[:600]


def build_semantic_briefing(
    matcher_path: str | Path,
    matcher_sha256: str,
    request_text: str,
    runtime_capabilities: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a bounded semantic-worker briefing from a deterministic matcher artifact."""
    path = Path(matcher_path)
    matcher, matcher_bytes = _read_json_object(path)
    actual_matcher_sha256 = hashlib.sha256(matcher_bytes).hexdigest()
    if actual_matcher_sha256 != matcher_sha256:
        raise ValueError("matcher SHA-256 does not match the supplied artifact")

    candidates = matcher.get("candidate_rules")
    if not isinstance(candidates, list):
        raise ValueError("matcher artifact candidate_rules must be a list")

    soft_candidates: list[dict[str, str]] = []
    hard_passthrough: list[str] = []
    for raw_entry in candidates:
        if not isinstance(raw_entry, dict):
            raise ValueError("matcher candidate_rules entries must be objects")
        rule_path = raw_entry.get("rule_path")
        if not isinstance(rule_path, str) or not rule_path.startswith("rules/"):
            raise ValueError("matcher candidates must have rules/ rule_path values")
        if _rule_layer(raw_entry) == "HARD":
            hard_passthrough.append(rule_path)
        else:
            soft_candidates.append(
                {"rule_path": rule_path, "excerpt": _candidate_excerpt(raw_entry)}
            )

    if len(soft_candidates) > MAX_SEMANTIC_CANDIDATES:
        raise ValueError(
            f"semantic candidate cap exceeded: {len(soft_candidates)} > {MAX_SEMANTIC_CANDIDATES}"
        )

    scope = {"soft_candidates": soft_candidates, "hard_passthrough": hard_passthrough}
    return {
        "schema_version": SEMANTIC_BRIEFING_SCHEMA_VERSION,
        "request_sha256": hashlib.sha256(request_text.encode("utf-8")).hexdigest(),
        "matcher": {"path": str(path), "sha256": matcher_sha256},
        "semantic_scope": {"sha256": _canonical_sha256(scope), **scope},
        "runtime_capabilities": dict(runtime_capabilities),
        "output_contract": {
            "schema_version": SEMANTIC_RESULT_SCHEMA_VERSION,
            "allowed_fields": ["schema_version", "matcher_sha256", "scope_sha256", "decisions"],
        },
        "retry": {"max_attempts": 2, "terminal_behavior": "return_validation_error"},
    }


def validate_semantic_result(result: Mapping[str, Any], briefing: Mapping[str, Any]) -> list[str]:
    """Validate semantic-worker output against its matcher-bound briefing."""
    issues: list[str] = []
    if result.get("schema_version") != SEMANTIC_RESULT_SCHEMA_VERSION:
        issues.append("schema_version must be 'rule-loader-semantic/v1'")

    forbidden = _RUNTIME_ATTESTATION_KEYS & set(result)
    for key in sorted(forbidden):
        issues.append(f"semantic result must not contain coordinator-owned field {key!r}")

    matcher = briefing.get("matcher")
    if not isinstance(matcher, Mapping):
        return [*issues, "briefing.matcher must be an object"]
    if result.get("matcher_sha256") != matcher.get("sha256"):
        issues.append("matcher_sha256 does not match the briefing")

    scope = briefing.get("semantic_scope")
    if not isinstance(scope, Mapping):
        return [*issues, "briefing.semantic_scope must be an object"]
    if result.get("scope_sha256") != scope.get("sha256"):
        issues.append("scope_sha256 does not match the briefing")

    soft_candidates = scope.get("soft_candidates")
    if not isinstance(soft_candidates, list):
        return [*issues, "briefing semantic_scope.soft_candidates must be a list"]
    expected_paths = {
        entry.get("rule_path") for entry in soft_candidates if isinstance(entry, Mapping)
    }
    decisions = result.get("decisions")
    if not isinstance(decisions, list):
        return [*issues, "decisions must be a list"]

    decision_paths: set[str] = set()
    for index, decision in enumerate(decisions):
        location = f"decisions[{index}]"
        if not isinstance(decision, Mapping):
            issues.append(f"{location} must be an object")
            continue
        decision_data = cast("Mapping[str, Any]", decision)
        rule_path = decision_data.get("rule_path")
        if not isinstance(rule_path, str):
            issues.append(f"{location}.rule_path must be a string")
            continue
        if rule_path in decision_paths:
            issues.append(f"{location}.rule_path duplicates an earlier decision")
        decision_paths.add(rule_path)
        if rule_path not in expected_paths:
            issues.append(f"{location}.rule_path is outside the semantic scope")
        if not isinstance(decision_data.get("selected"), bool):
            issues.append(f"{location}.selected must be a boolean")
        evidence = decision_data.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            issues.append(f"{location}.evidence must be a non-empty string")

    missing = expected_paths - decision_paths
    if missing:
        issues.append(f"semantic result is missing decisions for {sorted(missing)!r}")
    extra = decision_paths - expected_paths
    if extra:
        issues.append(f"semantic result has decisions outside scope: {sorted(extra)!r}")
    return issues


# ── final-manifest helpers ───────────────────────────────────────────────────


def attach_runtime_evidence(
    semantic_result: Mapping[str, Any],
    briefing: Mapping[str, Any],
    runtime_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Attach coordinator-owned runtime evidence to a validated semantic result."""
    issues = validate_semantic_result(semantic_result, briefing)
    if issues:
        raise ValueError(f"cannot build final manifest from invalid semantic result: {issues!r}")

    scope = cast("Mapping[str, Any]", briefing["semantic_scope"])
    hard_paths = cast("list[str]", scope["hard_passthrough"])
    decisions = cast("list[Mapping[str, Any]]", semantic_result["decisions"])
    return {
        "schema_version": FINAL_MANIFEST_SCHEMA_VERSION,
        "matcher_sha256": semantic_result["matcher_sha256"],
        "scope_sha256": semantic_result["scope_sha256"],
        "load_sequence": [
            *hard_paths,
            *(str(decision["rule_path"]) for decision in decisions if decision["selected"]),
        ],
        "deferred_rules": [
            {"rule_path": str(decision["rule_path"]), "reason": "semantic_rejected"}
            for decision in decisions
            if not decision["selected"]
        ],
        "runtime_evidence": dict(runtime_evidence),
    }


def validate_final_manifest(manifest: Mapping[str, Any], briefing: Mapping[str, Any]) -> list[str]:
    """Validate final-manifest ownership, foundation ordering, and exact partitioning."""
    issues: list[str] = []
    if manifest.get("schema_version") != FINAL_MANIFEST_SCHEMA_VERSION:
        issues.append("schema_version must be 'rule-loader-manifest/v3'")

    matcher = briefing.get("matcher")
    if not isinstance(matcher, Mapping):
        return [*issues, "briefing.matcher must be an object"]
    if manifest.get("matcher_sha256") != matcher.get("sha256"):
        issues.append("matcher_sha256 does not match the briefing")

    scope = briefing.get("semantic_scope")
    if not isinstance(scope, Mapping):
        return [*issues, "briefing.semantic_scope must be an object"]
    if manifest.get("scope_sha256") != scope.get("sha256"):
        issues.append("scope_sha256 does not match the briefing")

    runtime_evidence = manifest.get("runtime_evidence")
    if not isinstance(runtime_evidence, Mapping):
        issues.append("runtime_evidence must be a coordinator-owned object")
    else:
        runtime = runtime_evidence.get("runtime")
        status = runtime_evidence.get("status")
        if runtime not in {"cortex-code", "claude-code", "unsupported"}:
            issues.append("runtime_evidence.runtime is invalid")
        if status not in {"attested", "unsupported"}:
            issues.append("runtime_evidence.status is invalid")
        if runtime == "unsupported" and status != "unsupported":
            issues.append("unsupported runtime requires status='unsupported'")
        if runtime != "unsupported" and status != "attested":
            issues.append("supported runtime requires status='attested'")

    hard_paths = cast("list[str]", scope.get("hard_passthrough", []))
    soft_entries = cast("list[Mapping[str, Any]]", scope.get("soft_candidates", []))
    soft_paths = {str(entry["rule_path"]) for entry in soft_entries}
    load_sequence = manifest.get("load_sequence")
    deferred_rules = manifest.get("deferred_rules")
    if not isinstance(load_sequence, list):
        return [*issues, "load_sequence must be a list"]
    if not isinstance(deferred_rules, list):
        return [*issues, "deferred_rules must be a list"]
    if load_sequence[: len(hard_paths)] != hard_paths:
        issues.append("HARD candidates must lead the final load_sequence in briefing order")

    loaded_soft_seq = [path for path in load_sequence if path in soft_paths]
    loaded_soft_paths = set(loaded_soft_seq)
    if len(loaded_soft_seq) != len(loaded_soft_paths):
        issues.append("load_sequence contains a semantic candidate more than once")
    deferred_paths = {
        entry.get("rule_path") for entry in deferred_rules if isinstance(entry, Mapping)
    }
    if loaded_soft_paths & deferred_paths:
        issues.append("semantic candidates cannot appear in both load_sequence and deferred_rules")
    if loaded_soft_paths | deferred_paths != soft_paths:
        issues.append("final manifest must partition every semantic candidate exactly once")
    allowed_paths = set(hard_paths) | soft_paths
    if any(path not in allowed_paths for path in load_sequence):
        issues.append("load_sequence contains a path outside the briefing scope")
    return issues


# ── matcher-artifact validation ──────────────────────────────────────────────


def validate_matcher_manifest(manifest: dict[str, Any]) -> list[str]:
    """Validate a decoded rule-loader-matcher/v1 dict.

    Returns a list of human-readable issue strings.  An empty list means valid.
    """
    issues: list[str] = []

    sv = manifest.get("schema_version")
    if sv in _LEGACY_SCHEMA_VERSIONS:
        return [
            f"unsupported schema version {sv!r}: "
            "rule-loader-manifest/v1 and v2 are no longer accepted; "
            "produce rule-loader-matcher/v1 output instead"
        ]
    if sv != MATCHER_SCHEMA_VERSION:
        issues.append(f"schema_version must be {MATCHER_SCHEMA_VERSION!r}, got {sv!r}")

    # ── candidate_rules ───────────────────────────────────────────────────────
    crs = manifest.get("candidate_rules")
    if not isinstance(crs, list):
        issues.append("candidate_rules must be a list")
        crs = []
    for i, entry in enumerate(crs):
        loc = f"candidate_rules[{i}]"
        if not isinstance(entry, dict):
            issues.append(f"{loc}: must be an object")
            continue
        issues.extend(_check_rule_path(entry.get("rule_path"), loc))
        issues.extend(_check_body_content(entry, loc))

    # ── load_sequence ─────────────────────────────────────────────────────────
    ls = manifest.get("load_sequence")
    if not isinstance(ls, list) or len(ls) == 0:
        issues.append("load_sequence must be a non-empty list")
        ls = []

    ls_paths: set[str] = set()
    for i, entry in enumerate(ls):
        loc = f"load_sequence[{i}]"
        if not isinstance(entry, dict):
            issues.append(f"{loc}: must be an object")
            continue
        rp = entry.get("rule_path")
        issues.extend(_check_rule_path(rp, loc))
        if isinstance(rp, str):
            ls_paths.add(rp)
        issues.extend(_check_body_content(entry, loc))

    # ── deferred_rules ────────────────────────────────────────────────────────
    dr = manifest.get("deferred_rules")
    if not isinstance(dr, list):
        issues.append("deferred_rules must be a list")
        dr = []

    dr_paths: set[str] = set()
    for i, entry in enumerate(dr):
        loc = f"deferred_rules[{i}]"
        if not isinstance(entry, dict):
            issues.append(f"{loc}: must be an object")
            continue
        rp = entry.get("rule_path")
        issues.extend(_check_rule_path(rp, loc))
        if isinstance(rp, str):
            dr_paths.add(rp)
        if not isinstance(entry.get("reason"), str) or not str(entry.get("reason", "")).strip():
            issues.append(f"{loc}: 'reason' must be a non-empty string")
        issues.extend(_check_body_content(entry, loc))

    # ── completeness invariant ────────────────────────────────────────────────
    cr_paths = {
        e["rule_path"] for e in crs if isinstance(e, dict) and isinstance(e.get("rule_path"), str)
    }
    for path in sorted(cr_paths):
        in_ls = path in ls_paths
        in_dr = path in dr_paths
        if in_ls and in_dr:
            issues.append(
                f"completeness: {path!r} appears in both load_sequence and deferred_rules"
            )
        elif not in_ls and not in_dr:
            issues.append(
                f"completeness: {path!r} is in candidate_rules but missing from "
                "both load_sequence and deferred_rules"
            )

    return issues


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Reject legacy loader manifest schema versions (v1 and v2); validate matcher/v1 manifests.

    This function previously accepted rule-loader-manifest/v1 and v2. Both
    schema versions are now unsupported. Callers must produce rule-loader-matcher/v1
    output via ``build_manifest`` in ``match_rules.py``. Use
    ``validate_matcher_manifest`` directly when the input is already known to be
    a matcher artifact.
    """
    sv = manifest.get("schema_version")
    if sv in _LEGACY_SCHEMA_VERSIONS:
        return [
            f"unsupported schema version {sv!r}: "
            "rule-loader-manifest/v1 and v2 are no longer accepted; "
            "produce rule-loader-matcher/v1 output instead"
        ]
    return validate_matcher_manifest(manifest)


def load_and_validate_manifest(path: str | Path) -> list[str]:
    """Read a JSON file at *path* and validate it as a rule-loader-matcher/v1.

    Returns a list of human-readable issue strings.  An empty list means valid.
    Returns a single-element list with an error description on I/O or JSON errors.
    """
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read file: {exc}"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return ["manifest must be a JSON object"]
    return validate_matcher_manifest(data)
