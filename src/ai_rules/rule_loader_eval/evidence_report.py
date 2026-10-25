"""Local, evidence-bound report selection, descriptive metrics, and publication."""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ai_rules.cortex.models import COCO_BENCHMARK_MODELS, CONSUMPTION_TABLE_EFFECTIVE_DATE

SELECTION_SCHEMA = "ai-rules-report-selection/v1"
REPORT_SCHEMA = "ai-rules-evidence-report/v1"
SETTINGS = ("effort", "max_turns", "concurrency", "runs_requested", "strict_forbidden", "mode")
OUTCOMES = frozenset(
    {
        "pass",
        "fail",
        "error",
        "model-skipped-reads",
        "signal-violation",
        "agent-miss",
        "matcher-miss",
        "empty-manifest",
        "recovery-only",
    }
)
Json = dict[str, Any]


class ReportError(ValueError):
    """Report evidence or artifact cannot safely satisfy its declared contract."""


def _json(path: Path) -> Json:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ReportError(f"Cannot read JSON evidence: {path}") from exc
    if not isinstance(value, dict):
        raise ReportError(f"Expected JSON object: {path}")
    return value


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _files(root: Path) -> list[Path]:
    return sorted(root.glob("run-*/fixtures/*.json"))


def _source(root: Path) -> Json:
    root = root.resolve()
    manifest = _json(root / "manifest.json")
    files = [root / "manifest.json", *_files(root)]
    if not manifest.get("model_requested"):
        raise ReportError(f"Missing model identity: {root}")
    return {
        "path": str(root),
        "model": manifest["model_requested"],
        "digests": {str(path.relative_to(root)): _digest(path) for path in files},
    }


def create_selection(
    runs: list[Path],
    *,
    archives: list[Path] | None = None,
    exclusions: dict[str, str] | None = None,
) -> Json:
    """Bind exact current evidence bytes; callers persist this snapshot for replay."""
    sources = [_source(path) for path in runs]
    identities = [source["path"] for source in sources]
    if len(set(identities)) != len(identities):
        raise ReportError("duplicate selected source")
    return {
        "schema_version": SELECTION_SCHEMA,
        "selected": sources,
        "archives": [_source(path) for path in archives or []],
        "exclusions": exclusions or {},
        "pricing": {
            "effective_date": CONSUMPTION_TABLE_EFFECTIVE_DATE,
            "unit": "AI Credits per million tokens",
            "models": [asdict(model) for model in COCO_BENCHMARK_MODELS],
        },
    }


def load_selection(path: Path) -> Json:
    """Resolve explicit selection paths against their file, never process CWD."""
    selection = _json(path)
    validate_selection(selection)
    for group in ("selected", "archives"):
        for source in selection.get(group, []):
            source["path"] = str((path.parent / source["path"]).resolve())
    return selection


def validate_selection(selection: Json) -> None:
    """Validate untrusted selection structure before reading any supplied paths."""
    if selection.get("schema_version") != SELECTION_SCHEMA:
        raise ReportError("Unsupported selection contract")
    if not isinstance(selection.get("selected"), list) or not selection["selected"]:
        raise ReportError("Invalid or empty report selection")
    if not isinstance(selection.get("archives", []), list):
        raise ReportError("Invalid archive inventory")
    sources = selection["selected"] + selection.get("archives", [])
    identities = []
    for source in sources:
        if (
            not isinstance(source, dict)
            or not isinstance(source.get("path"), str)
            or not source["path"]
            or "://" in source["path"]
            or not isinstance(source.get("model"), str)
        ):
            raise ReportError("Invalid local source identity")
        digests = source.get("digests")
        if not isinstance(digests, dict) or "manifest.json" not in digests:
            raise ReportError("Source digests are required")
        for relative, digest in digests.items():
            if (
                not isinstance(relative, str)
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
                or not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ReportError("Invalid evidence digest or relative path")
        identities.append(str(Path(source["path"]).resolve()))
    if len(set(identities)) != len(identities):
        raise ReportError("duplicate selected/archive source")
    exclusions = selection.get("exclusions", {})
    if not isinstance(exclusions, dict) or any(
        not isinstance(key, str) or not isinstance(reason, str) or not reason.strip()
        for key, reason in exclusions.items()
    ):
        raise ReportError("Exclusions require explicit reasons")
    pricing = selection.get("pricing")
    if (
        not isinstance(pricing, dict)
        or not isinstance(pricing.get("effective_date"), str)
        or pricing.get("unit") != "AI Credits per million tokens"
        or not isinstance(pricing.get("models"), list)
    ):
        raise ReportError("Invalid pricing snapshot")
    models = []
    for rate in pricing["models"]:
        if not isinstance(rate, dict) or not isinstance(rate.get("model_id"), str):
            raise ReportError("Invalid pricing model")
        models.append(rate["model_id"])
        for key in ("input", "output", "cache_write", "cache_read"):
            value = rate.get(f"{key}_credits_per_million")
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (float, int))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ReportError("Invalid nonnegative pricing rate")
    if len(set(models)) != len(models):
        raise ReportError("duplicate pricing model")


def _read_source(source: Json) -> tuple[Json, list[Json]]:
    root = Path(source["path"])
    expected = source.get("digests", {})
    actual = {
        str(path.relative_to(root)): _digest(path)
        for path in [root / "manifest.json", *_files(root)]
    }
    if actual != expected:
        raise ReportError(f"Source evidence changed: {root}")
    manifest = _json(root / "manifest.json")
    if manifest.get("model_requested") != source["model"]:
        raise ReportError("Source identity changed")
    samples = [_json(root / relative) for relative in sorted(actual) if relative != "manifest.json"]
    if {
        str(path.relative_to(root)): _digest(path)
        for path in [root / "manifest.json", *_files(root)]
    } != expected:
        raise ReportError(f"Source evidence changed during ingestion: {root}")
    return manifest, samples


def repeated_success(
    successes: int, attempts: int, count: int
) -> tuple[float | None, float | None]:
    """Estimate at-least-one/all success in random subsets without replacement."""
    if not 0 <= successes <= attempts or count < 1:
        raise ReportError("Invalid repeated-attempt counts")
    if attempts < count:
        return None, None
    denominator = math.comb(attempts, count)
    return 1 - math.comb(attempts - successes, count) / denominator, math.comb(
        successes, count
    ) / denominator


def _reading(sample: Json, name: str) -> float | None:
    value = sample.get(name)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        return None
    return float(value)


def _cost(sample: Json, rate: Json | None) -> float | None:
    if (
        rate is None
        or rate.get("input_credits_per_million") is None
        or rate.get("output_credits_per_million") is None
    ):
        return None
    counts = [
        _reading(sample, name)
        for name in (
            "input_tokens",
            "output_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
        )
    ]
    if any(value is None for value in counts):
        return None
    total, output, write, read = counts
    assert total is not None and output is not None and write is not None and read is not None
    uncached = total - write - read
    if uncached < 0:
        raise ReportError("Cache counters exceed inclusive input counter")
    charges = [
        (uncached, "input"),
        (output, "output"),
        (write, "cache_write"),
        (read, "cache_read"),
    ]
    if any(amount and rate.get(f"{kind}_credits_per_million") is None for amount, kind in charges):
        return None
    return sum(
        amount * (rate.get(f"{kind}_credits_per_million") or 0) / 1_000_000
        for amount, kind in charges
    )


def _metric(values: list[float], expected: int, *, fixtures: int | None = None) -> Json:
    return {
        "value": statistics.mean(values) if values else None,
        "captured": len(values),
        "expected": expected,
        "status": "complete"
        if len(values) == expected and expected
        else "partial"
        if values
        else "unavailable",
        "eligible_fixtures": fixtures,
        "reason": None if len(values) == expected and expected else "incomplete_capture",
    }


def _configuration(
    source: Json, manifest: Json, samples: list[Json], rates: dict[str, Json], inspection: bool
) -> Json:
    fixtures = manifest.get("fixture_selection")
    runs = manifest.get("runs_requested")
    if fixtures == ["all"]:
        fixtures = sorted(
            {
                sample.get("fixture_id")
                for sample in samples
                if isinstance(sample.get("fixture_id"), str)
            }
        )
        if len(fixtures) != manifest.get("fixture_count"):
            raise ReportError(
                "Wildcard fixture inventory cannot be verified from incomplete evidence"
            )
    if (
        not isinstance(fixtures, list)
        or not fixtures
        or any(not isinstance(item, str) for item in fixtures)
        or len(set(fixtures)) != len(fixtures)
        or type(runs) is not int
        or runs < 1
    ):
        raise ReportError("Invalid fixture inventory or planned run count")
    if manifest.get("fixture_count") != len(fixtures):
        raise ReportError("Fixture inventory count mismatch")
    by_fixture: dict[str, list[Json]] = defaultdict(list)
    pairs = set()
    rate = rates.get(source["model"])
    for sample in samples:
        fixture, run = sample.get("fixture_id"), sample.get("run_number")
        if fixture not in fixtures or type(run) is not int or not 1 <= run <= runs:
            raise ReportError("Unexpected fixture/run sample")
        if (fixture, run) in pairs:
            raise ReportError("duplicate fixture/run sample")
        pairs.add((fixture, run))
        if (
            sample.get("result") not in OUTCOMES
            or sample.get("model") != source["model"]
            or sample.get("passed") is not (sample.get("result") == "pass")
            or sample.get("is_infra_error") is not (sample.get("result") == "error")
        ):
            raise ReportError("Malformed outcome or model identity")
        by_fixture[fixture].append(sample)
    observations = len(samples)
    expected = len(fixtures) * runs
    metrics: Json = {}
    at_one, at_three, all_three, scored = [], [], [], []
    fixture_rows = []
    for fixture in sorted(fixtures):
        records = by_fixture[fixture]
        count = len(records)
        passes = sum(record["result"] == "pass" for record in records)
        if count:
            at_one.append(passes / count)
        at, every = repeated_success(passes, count, 3)
        if at is not None:
            at_three.append(at)
            all_three.append(every)
        scored_count = sum(
            record["result"] not in {"error", "model-skipped-reads"} for record in records
        )
        if scored_count:
            scored.append(passes / scored_count)
        fixture_rows.append(
            {
                "fixture": fixture,
                "observed": count,
                "planned": runs,
                "passed": passes,
                "pass_at_1": passes / count if count else None,
                "pass_at_3": at,
                "pass_all_3": every,
            }
        )
    for name, values in (
        ("pass_at_1", at_one),
        ("pass_at_3", at_three),
        ("pass_all_3", all_three),
        ("scored_rate", scored),
    ):
        metrics[name] = _metric(values, len(fixtures), fixtures=len(values))
    for name in ("duration_ms", "turns", "input_tokens", "output_tokens"):
        metrics[name] = _metric(
            [value for sample in samples if (value := _reading(sample, name)) is not None],
            observations,
        )
    costs = [cost for sample in samples if (cost := _cost(sample, rate)) is not None]
    metrics["credits"] = _metric(costs, observations)
    if observations and not costs:
        metrics["credits"]["reason"] = "missing_rate_or_usage"
    total_passes = sum(sample["result"] == "pass" for sample in samples)
    metrics["credits_per_pass"] = {
        **metrics["credits"],
        "value": sum(costs) / total_passes
        if costs and total_passes and len(costs) == observations
        else None,
    }
    outcome_counts = dict(Counter(sample["result"] for sample in samples))
    failures = {
        field: sum(bool(sample.get("match", {}).get(field)) for sample in samples)
        for field in (
            "missing_required",
            "missing_dependencies",
            "forbidden_present",
            "extra_loaded",
        )
    }
    failures.update(
        {
            "output_shape": sum(bool(sample.get("output_violations")) for sample in samples),
            "citation_drift": sum(bool(sample.get("citation_drifts")) for sample in samples),
            "read_cite": sum(
                sample.get("signal_report", {}).get("ok") is False for sample in samples
            ),
            "dependency": sum(sample.get("depends_ok") is False for sample in samples),
        }
    )
    return {
        "id": source["model"] + ":" + manifest.get("mode", "unknown"),
        "model": source["model"],
        "source": source["path"],
        "observed": observations,
        "planned": expected,
        "missing": expected - observations,
        "eligible": not inspection and observations == expected and not outcome_counts.get("error"),
        "metrics": metrics,
        "outcomes": outcome_counts,
        "failures": failures,
        "fixtures": fixture_rows,
        "executions": samples,
        "diagnostics": {
            "distinct_rule_reads": _metric(
                [
                    float(len(sample["loaded_via_reads"]))
                    for sample in samples
                    if isinstance(sample.get("loaded_via_reads"), list)
                ],
                observations,
            ),
            "declared_domain_cap_violations": sum(
                any(
                    line.partition("Gate 3: +")[2].split(" ", 1)[0].isdigit()
                    and int(line.partition("Gate 3: +")[2].split(" ", 1)[0]) > 3
                    for line in (sample.get("final_text") or "").splitlines()
                )
                for sample in samples
            ),
            "domain_cap_basis": "Declared Gate 3 primary-domain count; dependency closure is not counted as primary rules.",
        },
    }


def build_payload(selection: Json, *, inspection: bool = False) -> Json:
    """Compute one immutable local evidence payload, without AI or credentials."""
    validate_selection(selection)
    rates = {rate["model_id"]: rate for rate in selection["pricing"]["models"]}
    configurations, archives, protocols = [], [], []
    for source in selection["selected"]:
        manifest, samples = _read_source(source)
        fixture_inventory = manifest.get("fixture_selection", [])
        if fixture_inventory == ["all"]:
            fixture_inventory = sorted(
                {
                    sample.get("fixture_id")
                    for sample in samples
                    if isinstance(sample.get("fixture_id"), str)
                }
            )
        signature = {
            "sha": manifest.get("git", {}).get("sha"),
            "fixtures": sorted(fixture_inventory),
            "settings": {name: manifest.get(name) for name in SETTINGS},
            "version": manifest.get("ai_rules_version"),
            "execution_protocol": manifest.get("execution_protocol", "legacy-sdk/v1"),
        }
        if not inspection and (
            not signature["sha"]
            or any(value is None for value in signature["settings"].values())
            or not signature["version"]
        ):
            raise ReportError("Unverified comparison protocol")
        protocols.append(signature)
        configurations.append(_configuration(source, manifest, samples, rates, inspection))
    if (
        not inspection
        and len({json.dumps(protocol, sort_keys=True) for protocol in protocols}) != 1
    ):
        raise ReportError("incompatible comparison protocols or fixture inventories")
    identities = [configuration["id"] for configuration in configurations]
    if len(set(identities)) != len(identities):
        raise ReportError("duplicate selected configuration")
    if set(selection.get("exclusions", {})) & {row["model"] for row in configurations}:
        raise ReportError("Selected model also excluded")
    for source in selection.get("archives", []):
        _, samples = _read_source(source)
        archives.append(
            {
                "model": source["model"],
                "source": source["path"],
                "observed": len(samples),
                "outcomes": dict(Counter(sample.get("result", "unknown") for sample in samples)),
                "cost_capture": "archived attempts excluded from competitive metrics; uncaptured retries unavailable",
            }
        )
    payload = {
        "schema_version": REPORT_SCHEMA,
        "mode": "inspection" if inspection else "comparison",
        "methodology": "equal-fixture-descriptive/v1",
        "selection": selection,
        "protocols": protocols,
        "configurations": configurations,
        "archives": archives,
        "exclusions": selection.get("exclusions", {}),
        "totals": {
            "observed": sum(row["observed"] for row in configurations),
            "planned": sum(row["planned"] for row in configurations),
        },
        "limitations": [
            "Selected attempt estimates are not metered spend or complete infrastructure cost.",
            "Usage for retries not captured by the evaluator is unavailable.",
            "pass@3 and pass^3 sample observed subsets without replacement, not adaptive retries.",
            "Descriptive extrema are not statistical superiority; no confidence intervals are asserted.",
        ],
    }
    validate_payload(payload)
    return payload


def validate_payload(payload: Json) -> None:
    """Reject malformed or nonfinite report artifacts before publication."""
    if payload.get("schema_version") != REPORT_SCHEMA or payload.get("mode") not in {
        "comparison",
        "inspection",
    }:
        raise ReportError("Unsupported report contract")
    try:
        json.dumps(payload, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ReportError("Nonfinite or non-JSON report data") from exc
    try:
        validate_selection(payload["selection"])
        rows = payload["configurations"]
        invalid = (
            not rows
            or sum(row["observed"] for row in rows) != payload["totals"]["observed"]
            or any(
                len(row["executions"]) != row["observed"]
                or row["observed"] + row["missing"] != row["planned"]
                for row in rows
            )
        )
    except (KeyError, TypeError) as exc:
        raise ReportError("Malformed report payload") from exc
    if invalid:
        raise ReportError("Report observation counts disagree")


def render_html(payload: Json) -> str:
    """Render the same canonical JSON used by every table, chart, and print view."""
    templates = Path(__file__).resolve().parents[3] / "templates" / "reports"
    environment = Environment(
        loader=FileSystemLoader(str(templates)), autoescape=select_autoescape(["html", "j2"])
    )
    return environment.get_template("evidence-report.html.j2").render(
        payload=payload,
        embedded=json.dumps(payload, sort_keys=True, allow_nan=False).replace("<", "\\u003c"),
    )


def write_generation(payload: Json, output: Path) -> Path:
    """Publish a new immutable report pair through one directory rename."""
    validate_payload(payload)
    output = output.resolve()
    roots = [
        Path(source["path"]).resolve()
        for source in payload["selection"]["selected"] + payload["selection"].get("archives", [])
    ]
    if any(output.is_relative_to(root) for root in roots):
        raise ReportError("Report output must not be inside source evidence")
    html = render_html(payload)
    if build_payload(payload["selection"], inspection=payload["mode"] == "inspection") != payload:
        raise ReportError("Source evidence changed before publication")
    output.mkdir(parents=True, exist_ok=True)
    target = output / ("eval-report-" + uuid4().hex)
    with tempfile.TemporaryDirectory(prefix=".report-staging-", dir=output) as temporary:
        staging = Path(temporary) / "generation"
        staging.mkdir()
        for name, text in (
            ("report.json", json.dumps(payload, sort_keys=True, indent=2, allow_nan=False)),
            ("report.html", html),
        ):
            with (staging / name).open("w", encoding="utf-8") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
        os.rename(staging, target)
    return target


def verify_artifact(generation: Path) -> Json:
    """Check contract, embedded equality, and recomputed evidence-based metrics."""
    from html.parser import HTMLParser

    class Embedded(HTMLParser):
        def __init__(self):
            super().__init__()
            self.active = False
            self.parts: list[str] = []

        def handle_starttag(self, tag, attrs):
            self.active = tag == "script" and dict(attrs).get("id") == "report-data"

        def handle_endtag(self, tag):
            if tag == "script":
                self.active = False

        def handle_data(self, data):
            if self.active:
                self.parts.append(data)

    payload = _json(generation / "report.json")
    validate_payload(payload)
    parser = Embedded()
    parser.feed((generation / "report.html").read_text(encoding="utf-8"))
    if json.loads("".join(parser.parts)) != payload:
        raise ReportError("Embedded report JSON differs from report.json")
    rebuilt = build_payload(payload["selection"], inspection=payload["mode"] == "inspection")
    if rebuilt != payload:
        raise ReportError("Report metrics differ from source evidence")
    return payload["totals"]
