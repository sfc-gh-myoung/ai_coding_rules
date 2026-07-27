"""Bootstrap-health diagnostics for the rule-loader eval harness.

Centralizes the checks that detect rule-loading regressions when AGENTS.md
or the ``rule-loader`` skill changes:

1. **2-signal agreement** - the agent's ``## Rules Loaded`` section
   must agree with the actual ``Read`` tool calls captured by the
   PreToolUse hook. Disagreement is a fabrication signal. A legacy 3rd signal
   (``## Reads Performed``) is also compared when present, but v3.9+
   agents do not emit it.
2. **Citation drift** - declared line counts in ``**Rules Loaded**``
   citations must match the rule file's actual line count. Mismatch
   indicates the agent cited from pretraining instead of reading.

Both checks are unconditional inputs to ``eval`` pass/fail. There are
no escape flags by design - rule-loading correctness is non-negotiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ai_rules.rule_loader_eval.matcher import (
    CitationDrift,
    validate_version_citations,
)

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.rules_meta import RuleMetadata


@dataclass(frozen=True)
class SignalReport:
    """Result of the signal-agreement check between (A) read_file calls and (B) Rules Loaded.

    Under v3.15.0 semantics, signal disagreements are partitioned:

    - ``cited_without_read`` (B > A): the agent listed a rule in
      ``**Rules Loaded**`` but never `read_file`'d it. Pure fabrication
      (R1 violation). Always fails the fixture.
    - ``read_without_cite_unexpected`` (A > B, path NOT in fixture's
      ``optional:`` list): the agent read a rule for triage and didn't cite it.
      Reported diagnostically; this no longer fails the fixture because the new
      workflow permits exploratory metadata reads before final selection.
    - ``read_without_cite_tolerated`` (A > B, path IN fixture's
      ``optional:`` list): benign over-read of a known optional rule.
      Reported informationally; does NOT fail the fixture.

    v9 (RF10): marker-aware partition:
    - ``cited_without_manifest``: `[~]` citation of a path NOT in manifest.
    - ``inferred_citation_count``: count of `[?]` citations (soft signal).
    - ``inferred_citation_rate``: `[?]` count / total citations.

    ``ok = not cited_without_read and not cited_without_manifest``.
    Read-without-cite rows are diagnostics; cited-without-read is fabrication.

    ``disagreements`` retains the raw flat string list for backward
    compat with snapshot artifacts; new callers should use the
    partitioned fields.
    """

    ok: bool
    disagreements: tuple[str, ...]
    cited_without_read: tuple[str, ...] = ()
    read_without_cite_unexpected: tuple[str, ...] = ()
    read_without_cite_tolerated: tuple[str, ...] = ()
    cited_without_manifest: tuple[str, ...] = ()
    inferred_citation_count: int = 0
    inferred_citation_rate: float = 0.0


# Paths neutral to R1 protocol accounting: read is neither expected nor
# forbidden; cite is forbidden. See "Rule vs Reference File" in
# templates/AGENTS_MODE.md.template.
_DISCOVERY_ARTIFACTS: frozenset[str] = frozenset(
    {
        "AGENTS.md",
        "rules/" + "RULES_INDEX.md",  # legacy; excluded from signal checks even if deleted
    }
)


def signal_disagreement(
    run: AgentRun,
    *,
    fixture_optional: tuple[str, ...] | list[str] | set[str] = (),
) -> SignalReport:
    """Return a :class:`SignalReport` for the given agent run.

    Args:
        run: The agent run to analyze.
        fixture_optional: Paths the fixture lists in ``optional:``.
            Over-reads (A>B) of these paths are reported as tolerated instead of unexpected.

    Read-without-cite is diagnostic in both cases. Cited-without-read remains a
    hard failure.
    """
    reads = (set(run.loaded_via_reads) | set(run.prior_reads)) - _DISCOVERY_ARTIFACTS
    section = set(run.loaded_via_section) - _DISCOVERY_ARTIFACTS
    optional_set = set(fixture_optional)
    manifest = set(run.manifest_paths)

    # RF10: marker-aware partition using citations_rules_loaded provenance
    citations = run.citations_rules_loaded

    # Partition section paths by provenance marker
    read_required: set[str] = set()  # [x] or no marker → must be in reads
    manifest_required: set[str] = set()  # [~] → must be in manifest
    inferred: set[str] = set()  # [?] → soft signal only

    for path in section:
        cit = citations.get(path)
        prov = cit.provenance if cit else None
        if prov == "~":
            manifest_required.add(path)
        elif prov == "?":
            inferred.add(path)
        else:
            # [x] or None (backward compat) → must be in reads
            read_required.add(path)

    # B > A (read-required paths): cited [x] but not read → fabrication
    cited_without_read = tuple(sorted(read_required - reads))
    # [~] paths not in manifest → hard fail
    cited_without_manifest = tuple(sorted(manifest_required - manifest)) if manifest else ()

    # A > B: read but not cited. Tolerated when path is in fixture's optional.
    read_without_cite_all = sorted(reads - section)
    tolerated = tuple(p for p in read_without_cite_all if p in optional_set)
    unexpected = tuple(p for p in read_without_cite_all if p not in optional_set)

    # RF11: inferred citation metrics
    inferred_count = len(inferred)
    total_citations = len(section)
    inferred_rate = inferred_count / total_citations if total_citations > 0 else 0.0

    ok = not cited_without_read and not cited_without_manifest

    return SignalReport(
        ok=ok,
        disagreements=tuple(run.disagreements),
        cited_without_read=cited_without_read,
        read_without_cite_unexpected=unexpected,
        read_without_cite_tolerated=tolerated,
        cited_without_manifest=cited_without_manifest,
        inferred_citation_count=inferred_count,
        inferred_citation_rate=inferred_rate,
    )


def version_citation_drift(
    run: AgentRun, rules_meta: dict[str, RuleMetadata]
) -> tuple[CitationDrift, ...]:
    """Return version-based citation drifts.

    Checks only the Rules Loaded section.
    """
    return validate_version_citations(
        citations=run.citations_rules_loaded,
        rules_meta=rules_meta,
        section="Rules Loaded",
    )


# ---------------------------------------------------------------------------
# Human-readable formatters
# ---------------------------------------------------------------------------


def format_disagreement_warning(run: AgentRun, *, signal_report: SignalReport | None = None) -> str:
    """Render a human-readable explanation of a signal mismatch.

    Under v3.15.0 semantics, prints the partitioned signal report when
    available: ``cited_without_read`` (FAIL), ``read_without_cite_unexpected``
    (FAIL), ``read_without_cite_tolerated`` (informational). Falls back to
    the legacy 3-signal output when no signal_report is provided.
    """
    reads = set(run.loaded_via_reads)
    reads_performed = set(run.loaded_via_reads_performed)
    section = set(run.loaded_via_section)
    failed_paths = {path for path, c in run.citations_reads_performed.items() if c.failed}

    if signal_report is not None and (
        signal_report.cited_without_read
        or signal_report.read_without_cite_unexpected
        or signal_report.read_without_cite_tolerated
    ):
        lines: list[str] = [
            "Signal mismatch (v3.15.0 partitioned):",
            f"  (A) tool reads     - read_file calls captured via PreToolUse hook ({len(reads)} total)",
            f"  (B) Rules Loaded   - agent's `**Rules Loaded**` section            ({len(section)} total)",
            "",
        ]
        if signal_report.cited_without_read:
            lines.append("FAIL  cited_without_read (B>A, R1 fabrication):")
            lines.extend(f"  - {r}" for r in signal_report.cited_without_read)
            lines.append("")
        if signal_report.read_without_cite_unexpected:
            lines.append("FAIL  read_without_cite_unexpected (A>B, path NOT in fixture optional):")
            lines.extend(f"  - {r}" for r in signal_report.read_without_cite_unexpected)
            lines.append(
                "  Likely an over-eager kw: trigger; narrow the rule's keywords or add to fixture optional."
            )
            lines.append("")
        if signal_report.read_without_cite_tolerated:
            lines.append(
                "INFO  read_without_cite_tolerated (A>B, path IN fixture optional — benign):"
            )
            lines.extend(f"  - {r}" for r in signal_report.read_without_cite_tolerated)
            lines.append("")
        return "\n".join(lines)

    # Legacy fallback (no signal_report provided)
    n_signals = 3 if reads_performed else 2
    lines = [
        f"{n_signals}-signal mismatch detected. The runner compares:",
        f"  (A) tool reads     - read_file calls captured via PreToolUse hook ({len(reads)} total)",
        f"  (B) Rules Loaded   - agent's `## Rules Loaded` section            ({len(section)} total)",
    ]
    if reads_performed:
        lines.append(
            f"  (C) Reads Performed - agent's `## Reads Performed` section (legacy) ({len(reads_performed)} total)"
        )
    lines.extend(
        [
            "",
            "Per AGENTS.md, every entry in (B) must be backed by a `read_file` call in (A).",
        ]
    )
    if reads_performed:
        lines.append(
            "Per fabrication detection, (C) should equal (A) (with FAILED entries excluded)."
        )
    lines.append("")

    def _emit_pair(label_a: str, set_a: set[str], label_b: str, set_b: set[str]) -> None:
        only_a = sorted(set_a - set_b - failed_paths)
        only_b = sorted(set_b - set_a - failed_paths)
        if not only_a and not only_b:
            return
        lines.append(f"--- {label_a} vs {label_b} ---")
        if only_a:
            lines.append(f"In {label_a} only:")
            lines.extend(f"  - {r}" for r in only_a)
        if only_b:
            lines.append(f"In {label_b} only:")
            lines.extend(f"  - {r}" for r in only_b)
        lines.append("")

    _emit_pair("(A) tool reads", reads, "(B) Rules Loaded", section)
    if reads_performed:
        _emit_pair("(A) tool reads", reads, "(C) Reads Performed", reads_performed)
        _emit_pair("(B) Rules Loaded", section, "(C) Reads Performed", reads_performed)

    lines.extend(
        [
            "Likely causes:",
            "  1. Agent declared rules in (B) without read_file (Anti-Pattern 3:",
            "     fabricated gate compliance). Most reliably caught by (B) > (A).",
            "  2. Reads happened but the runner did not capture them (cached,",
            "     sub-process, alternate tool path). Caught by (A) > (B).",
            "  3. Agent omitted (B) entirely (R1/R2 violation).",
        ]
    )
    if reads_performed:
        lines.append("  4. (Legacy) Agent emitted (C) without read_file - same Anti-Pattern 3.")
    return "\n".join(lines)


def format_citation_drift_warning(drifts: tuple[CitationDrift, ...]) -> str | None:
    """Render a human-readable summary of citation drifts.

    Returns None if the input is empty.
    """
    if not drifts:
        return None
    lines = [
        "Citation drift detected. Declared citation values do not match the actual",
        "rule file metadata. This is a fabrication signal: the agent likely cited",
        "values from pretraining instead of reading the file in this turn.",
        "",
    ]
    for d in drifts:
        lines.append(
            f"  [{d.section}] {d.rule_path} {d.field}: declared={d.declared!r}, actual={d.actual!r}"
        )
    return "\n".join(lines)


def format_debug(run: AgentRun) -> list[str]:
    """Print all captured signals plus the raw final_text.

    Useful when the fixture skeleton's ``required:`` list is empty: lets
    the operator see whether the live agent emitted anything at all,
    which signals are diverging, and what the agent's final assistant
    text actually contained.
    """
    lines: list[str] = ["--- diagnostics debug ---"]
    lines.append(
        f"model: {run.model}  turns: {run.turns}  "
        f"duration_ms: {run.duration_ms}  stop_reason: {run.stop_reason or '(none)'}"
    )
    lines.append(f"loaded_via_reads ({len(run.loaded_via_reads)}):")
    for r in run.loaded_via_reads:
        lines.append(f"  - {r}")
    lines.append(f"loaded_via_section ({len(run.loaded_via_section)}):")
    for r in run.loaded_via_section:
        lines.append(f"  - {r}")
    if run.loaded_via_reads_performed:
        lines.append(f"loaded_via_reads_performed (legacy, {len(run.loaded_via_reads_performed)}):")
        for r in run.loaded_via_reads_performed:
            lines.append(f"  - {r}")
    if run.notes:
        lines.append(f"notes ({len(run.notes)}):")
        for n in run.notes:
            lines.append(f"  - {n}")
    lines.append("--- final assistant text ---")
    lines.append(run.final_text or "(empty)")
    lines.append("--- end diagnostics debug ---")
    return lines


def format_timing_lines(run: AgentRun, *, effort: str, model: str) -> list[str]:
    """Render the per-event timeline as a list of stderr-bound lines.

    Pure formatter on ``AgentRun.events`` so it is unit-testable without
    the SDK. Each event line has the form
    ``"{t_ms:>8} ms  {kind:16} {detail}"`` with a header and footer
    summarizing total wall time and turns.
    """
    lines: list[str] = []
    lines.append("--- diagnostics timing ---")
    lines.append(
        f"total: {run.duration_ms:_} ms across {run.turns} turns (model={model} effort={effort})"
    )
    lines.append(f"{0:>8} ms  {'[start]':16}")
    for ev in run.events:
        lines.append(f"{ev.t_ms:>8} ms  {ev.kind:16} {ev.detail}")
    lines.append("--- end diagnostics timing ---")
    return lines


# Project-root helper for callers that need to bridge to validate_citations.
def load_rule_meta_for_project(project_root: Path) -> dict[str, RuleMetadata]:
    """Load rule metadata snapshot for the given project root."""
    from ai_rules.rule_loader_eval.rules_meta import load_rules_metadata

    return load_rules_metadata(project_root / "rules")
