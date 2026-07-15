"""Validator for rule-loader-manifest/v1 JSON manifests.

The rule-loader skill returns a fenced JSON manifest (metadata only; rule file
bodies never appear in it).  This module validates the shape of that manifest so
the eval harness and ``ai-rules rule-loader validate`` can assert well-formedness
offline, without touching a live agent.

Public API
----------
- ``validate_manifest(manifest: dict) -> list[str]``
    Validate an already-decoded manifest dict.  Returns a list of human-readable
    issue strings; an empty list means the manifest is valid.

- ``load_and_validate_manifest(path) -> list[str]``
    Read a JSON file and validate it.  Returns an issue on invalid JSON or I/O
    errors.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

# ── constants ────────────────────────────────────────────────────────────────

SCHEMA_VERSION_V1 = "rule-loader-manifest/v1"
SCHEMA_VERSION_V2 = "rule-loader-manifest/v2"
ACCEPTED_SCHEMA_VERSIONS: frozenset[str] = frozenset({SCHEMA_VERSION_V1, SCHEMA_VERSION_V2})

# Kept for backward compat with callers that import the v1 constant.
REQUIRED_SCHEMA_VERSION = SCHEMA_VERSION_V1

_REQUIRED_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "runtime",
        "keywords_searched",
        "index_evidence",
        "candidate_rules",
        "candidate_count",
        "load_sequence",
        "deferred_rules",
    }
)

_V2_ADDITIONAL_TOP_LEVEL_KEYS: frozenset[str] = frozenset({"second_pass_evidence"})

_REQUIRED_RUNTIME_KEYS: frozenset[str] = frozenset({"primitive", "spawn_evidence", "agent_id"})

_REQUIRED_DEFERRED_KEYS: frozenset[str] = frozenset(
    {"rule_path", "reason_type", "reason", "deferred_because"}
)

_REQUIRED_SECOND_PASS_KEYS: frozenset[str] = frozenset(
    {"evaluated", "confirmed", "confirmation_reason"}
)

_REQUIRED_SECOND_PASS_EVIDENCE_KEYS: frozenset[str] = frozenset(
    {"rule_path", "confirmed", "reason"}
)

_SECOND_PASS_REJECTED_REASON = "second_pass_rejected"

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
                f"{location}: disallowed body-like key {key!r} — rule body content in manifest"
            )
        elif isinstance(val, str) and len(val) > _MAX_ENTRY_STR_LEN:
            issues.append(
                f"{location}: key {key!r} value length {len(val)} exceeds "
                f"{_MAX_ENTRY_STR_LEN} chars — rule body content in manifest"
            )
    return issues


# ── public API ───────────────────────────────────────────────────────────────


def _check_second_pass(value: Any, location: str, layer: Any = None) -> list[str]:
    """Validate a v2 ``second_pass`` annotation on a candidate rule."""
    issues: list[str] = []
    if value is None:
        issues.append(f"{location}: v2 requires 'second_pass' annotation")
        return issues
    if not isinstance(value, dict):
        issues.append(f"{location}.second_pass: must be an object, got {type(value).__name__!r}")
        return issues
    for key in sorted(_REQUIRED_SECOND_PASS_KEYS):
        if key not in value:
            issues.append(f"{location}.second_pass: missing required key {key!r}")
    if "evaluated" in value and not isinstance(value["evaluated"], bool):
        issues.append(f"{location}.second_pass.evaluated must be a boolean")
    if "confirmed" in value and not isinstance(value["confirmed"], bool):
        issues.append(f"{location}.second_pass.confirmed must be a boolean")
    cr = value.get("confirmation_reason")
    if cr is not None and (not isinstance(cr, str) or not cr.strip()):
        issues.append(f"{location}.second_pass.confirmation_reason must be a non-empty string")
    # HARD candidates get the exempt reason and evaluated=false.
    if isinstance(layer, str) and layer.upper() == "HARD":
        if value.get("evaluated") is True:
            issues.append(f"{location}.second_pass: HARD candidates must have evaluated=false")
        if value.get("confirmation_reason") != "hard-candidate-exempt":
            issues.append(
                f"{location}.second_pass: HARD candidates must use "
                "confirmation_reason='hard-candidate-exempt'"
            )
    return issues


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Validate a decoded rule-loader-manifest/v1 or v2 dict.

    Returns a list of human-readable issue strings.  An empty list means the
    manifest is valid.  Issues are stable enough for substring matching in tests
    but are not part of a versioned contract.

    Both ``rule-loader-manifest/v1`` and ``rule-loader-manifest/v2`` are
    accepted; when ``schema_version`` is v2, additional invariants are checked:
    each candidate carries a ``second_pass`` annotation, HARD candidates use
    ``confirmation_reason: "hard-candidate-exempt"``, HARD candidates are never
    ``second_pass_rejected`` in ``deferred_rules``, and ``second_pass_evidence``
    is present at the root.
    """
    issues: list[str] = []

    # ── required top-level keys ───────────────────────────────────────────────
    missing = _REQUIRED_TOP_LEVEL_KEYS - set(manifest.keys())
    for key in sorted(missing):
        issues.append(f"missing required top-level key: {key!r}")
    if missing:
        # Cannot do meaningful further validation without the required keys.
        return issues

    # ── schema_version ────────────────────────────────────────────────────────
    sv = manifest["schema_version"]
    if sv not in ACCEPTED_SCHEMA_VERSIONS:
        issues.append(
            f"schema_version must be one of {sorted(ACCEPTED_SCHEMA_VERSIONS)!r}, got {sv!r}"
        )
    is_v2 = sv == SCHEMA_VERSION_V2

    # ── runtime ───────────────────────────────────────────────────────────────
    runtime = manifest["runtime"]
    if not isinstance(runtime, dict):
        issues.append(f"runtime must be an object, got {type(runtime).__name__!r}")
    else:
        for key in sorted(_REQUIRED_RUNTIME_KEYS - set(runtime.keys())):
            issues.append(f"runtime: missing required key {key!r}")
        for key in ("spawn_evidence", "agent_id"):
            val = runtime.get(key)
            if isinstance(val, str) and not val.strip():
                issues.append(f"runtime.{key} must be non-empty")

    # ── keywords_searched ─────────────────────────────────────────────────────
    if not isinstance(manifest["keywords_searched"], list):
        issues.append("keywords_searched must be a list")

    # ── index_evidence ────────────────────────────────────────────────────────
    ie = manifest["index_evidence"]
    if not isinstance(ie, list) or len(ie) == 0:
        issues.append("index_evidence must be a non-empty list")

    # ── candidate_rules ───────────────────────────────────────────────────────
    crs = manifest["candidate_rules"]
    if not isinstance(crs, list):
        issues.append("candidate_rules must be a list")
        crs = []
    hard_rule_paths: set[str] = set()
    for i, entry in enumerate(crs):
        loc = f"candidate_rules[{i}]"
        if not isinstance(entry, dict):
            issues.append(f"{loc}: must be an object")
            continue
        issues.extend(_check_rule_path(entry.get("rule_path"), loc))
        issues.extend(_check_body_content(entry, loc))
        if (
            isinstance(entry.get("rule_path"), str)
            and str(entry.get("layer", "")).upper() == "HARD"
        ):
            hard_rule_paths.add(entry["rule_path"])
        if is_v2:
            issues.extend(_check_second_pass(entry.get("second_pass"), loc, entry.get("layer")))

    # ── candidate_count ───────────────────────────────────────────────────────
    cc = manifest["candidate_count"]
    if not isinstance(cc, int):
        issues.append(f"candidate_count must be an integer, got {type(cc).__name__!r}")
    elif cc != len(crs):
        issues.append(f"candidate_count {cc} != len(candidate_rules) {len(crs)}")

    # ── load_sequence ─────────────────────────────────────────────────────────
    ls = manifest["load_sequence"]
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
    dr = manifest["deferred_rules"]
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
        for key in sorted(_REQUIRED_DEFERRED_KEYS):
            val = entry.get(key)
            if val is None:
                issues.append(f"{loc}: missing required key {key!r}")
            elif isinstance(val, str) and not val.strip():
                issues.append(f"{loc}: {key!r} must be non-empty")
        issues.extend(_check_body_content(entry, loc))
        # v2 HARD-never-filtered invariant: HARD candidates must not appear
        # in deferred_rules with reason_type=second_pass_rejected.
        if (
            is_v2
            and entry.get("reason_type") == _SECOND_PASS_REJECTED_REASON
            and isinstance(rp, str)
            and rp in hard_rule_paths
        ):
            issues.append(f"{loc}: HARD candidate {rp!r} must not be second_pass_rejected")

    # ── second_pass_evidence (v2 only) ───────────────────────────────────────
    if is_v2:
        if "second_pass_evidence" not in manifest:
            issues.append("v2: missing required top-level key 'second_pass_evidence'")
        else:
            spe = manifest["second_pass_evidence"]
            if not isinstance(spe, list):
                issues.append("second_pass_evidence must be a list")
            else:
                for i, raw_entry in enumerate(spe):
                    loc = f"second_pass_evidence[{i}]"
                    if not isinstance(raw_entry, dict):
                        issues.append(f"{loc}: must be an object")
                        continue
                    entry = cast("dict[str, Any]", raw_entry)
                    issues.extend(_check_rule_path(entry.get("rule_path"), loc))
                    for key in sorted(_REQUIRED_SECOND_PASS_EVIDENCE_KEYS):
                        if key not in entry:
                            issues.append(f"{loc}: missing required key {key!r}")
                    if "confirmed" in entry and not isinstance(entry["confirmed"], bool):
                        issues.append(f"{loc}: 'confirmed' must be a boolean")

    # ── completeness invariant ────────────────────────────────────────────────
    # Every unique candidate_rules[*].rule_path must appear in exactly one of
    # load_sequence[*].rule_path or deferred_rules[*].rule_path.
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


def load_and_validate_manifest(path: str | Path) -> list[str]:
    """Read a JSON file at *path* and validate it as a rule-loader-manifest/v1.

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
    return validate_manifest(data)
