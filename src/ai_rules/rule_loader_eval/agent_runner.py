"""Live Cortex Code Agent SDK runner.

Drives ``query()`` against a fixture prompt with AGENTS.md as the project
context. Captures the loaded rules via two primary signals plus one optional
legacy backward-compat signal:

1. ``PreToolUse`` async hook records every ``Read`` tool call where the
   path resolves to ``rules/*.md`` under the project - deterministic
   and exhaustive (ground truth).
2. End-of-run parser scans for the ``## Rules Loaded`` section (or the
   pre-v3.9 ``**Rules Loaded**`` bold form) and extracts referenced
   rule paths plus citations.
3. **(Legacy/backward-compat)** End-of-run parser scans for a
   ``## Reads Performed`` section if present. This section was retired
   in v3.8.0 (``**Bootstrap:**`` compact line replaced it). Parser is
   kept for historical fixtures and CI artifacts; v3.9+ agents do not
   emit it.

The combined set (union) is the loaded set returned to the engine.
Disagreements between signals are reported as warnings. When
``## Reads Performed`` is absent (v3.9+ output), only signal 1 vs
signal 2 comparisons are performed. Citation drift (declared line counts
that do not match actual rule line counts) is reported separately.

Tool restriction is enforced by ``allowed_tools=["Read", "Glob", "Grep"]``
on the SDK options (the SDK denies all other tool calls without a
custom hook).
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from ai_rules.rule_loader_eval.defaults import DEFAULT_EFFORT, DEFAULT_MAX_TURNS

# Suppress benign auto-apply skill-stage warnings that coco emits on every
# session when the active Snowflake role can't read
# ``CORTEX_CODE.CONFIG.AUTO_APPLY_SKILLS_STAGE``. These lines are noise for the
# eval harness — they don't affect rule discovery — but they clutter the log
# and make failure diffs harder to read. Match the three known warning
# phrases as substrings (the lines are wrapped in ANSI color escapes such as
# ``\x1b[33m…⚠…\x1b[0m``, so anchoring on ``^`` or ``\s`` would miss them).
_COCO_AUTO_APPLY_NOISE_RE = re.compile(
    r"Auto-apply \[_CORTEX_CODE_DEFAULT\]"
    r"|\[_CORTEX_CODE_DEFAULT\] Failed to fetch from stage "
    r"@CORTEX_CODE\.CONFIG\.AUTO_APPLY_SKILLS_STAGE"
    r"|Schema 'CORTEX_CODE\.CONFIG' does not exist or not authorized"
)


def _filter_coco_stderr(line: str) -> None:
    """SDK stderr callback: drop known benign auto-apply warnings, forward the rest."""
    if _COCO_AUTO_APPLY_NOISE_RE.search(line):
        return
    sys.stderr.write(line if line.endswith("\n") else line + "\n")


# Anchor the leading ``rules`` so we don't match the substring inside
# ``ai_coding_rules/...`` (the project directory name). Body is a single
# path segment (no ``/``) so we can't span ``rules/<dirname>/<file>.md``
# and end up with duplicated ``rules/rules/`` matches.
RULE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])rules/[A-Za-z0-9_.-]+\.md")

# System prompt injected into every seed-fixture run. Extracted as a
# module-level constant so tests can assert its content without running live.
_SEED_SYSTEM_PROMPT = (
    "HARD STOP: This is a rule-discovery probe. You MUST stop after "
    "emitting the PRE-FLIGHT Gate 1 foundation citation and Gate 3 domain "
    "rule list. You MUST NOT execute the user's task, "
    "write code, read or search the user's task/project files "
    "(e.g. etl_pipeline.py, via Read/Glob/find/ls/list_dir), call SQL "
    "tools, call ask_user_question, or perform ANY action beyond rule "
    "discovery. After the Gate 3 rule list, "
    "output `SEED_FIXTURE_COMPLETE` and immediately stop. "
    "This stop boundary applies AFTER rule discovery: it forbids executing the user's underlying task, but it does NOT override the AGENTS.md bootstrap reading steps — you MUST still read rules/000-global-core.md, read_file every matched rule, AND read_file each matched rule's `required:` Depends (transitively) before emitting the Gate 3 block.\n\n"
    "You are evaluating rule discovery for the ai_coding_rules repo. "
    "Before answering ANY user request, you MUST follow the AGENTS.md "
    "bootstrap protocol exactly:\n\n"
    "  1. Read `AGENTS.md` at the project root.\n"
    "  2. Always read `rules/000-global-core.md` first (this is the "
    "foundation rule, loaded on every request).\n"
    "  3. Extract candidate keywords from the user prompt and run "
    "`grep -iwE 'KW1|KW2|KW3' rules/RULES_INDEX.md` to discover "
    "matching rules. RULES_INDEX.md has one space-separated row "
    "per rule; each matching row is self-contained — the rule filename "
    "is the first field, no further context lookup needed. "
    "RULES_INDEX.md is the single agent discovery index.\n"
    "  4. Read every matched rule. Then, for EACH matched rule's "
    "`**Depends:**` field, you MUST also read_file every `required:` "
    "dependency rule — these are transitive, so a required dep that "
    "itself declares further `required:` deps must also be read, until "
    "the required-dependency closure is fully loaded. Consider "
    "`optional:` deps based on context.\n"
    "  5. Use the `Read`, `Grep`, and `Bash` tools for rule discovery "
    "(Glob/find/ls only to locate rule files, never the user's task "
    "files) - do not answer from memory.\n\n"
    "Your FINAL assistant message MUST include a PRE-FLIGHT block with "
    "Gate 1 foundation citation and Gate 3 domain rules formatted as:\n\n"
    "  PRE-FLIGHT:\n"
    "  - [x] Gate 1: Foundation rules/000-global-core.md — N lines\n"
    "  - [x] Gate 2: rules/RULES_INDEX.md searched for: keyword1, keyword2\n"
    "  - [x] Gate 3: +N domain rule(s):\n"
    "    - rules/<matched-rule>.md (<reason>) — N lines\n"
    "    - rules/<required-dep>.md (required dep of <matched-rule>) — N lines\n\n"
    "Citation rules: `N lines` MUST be the `wc -l` output for the "
    "file (number of newline characters, not visual line count). "
    "Do not include `RuleVersion` or `LastUpdated` in citations.\n\n"
    "If no domain rule matches the prompt, emit:\n\n"
    "  - [x] Gate 3: none matched\n\n"
    "Do NOT emit a standalone `## Rules Loaded` / `**Rules Loaded**` section "
    "(the old format is retired; citations now live inside PRE-FLIGHT Gate 3).\n\n"
    "If you cannot read AGENTS.md, output the single token "
    "`BOOTSTRAP_FAILED` and stop. Do NOT generate any answer that "
    "lacks the Gate 3 rule list - an answer without it is "
    "non-compliant.\n\n"
    "STOP CONDITION (seed-fixture scope only): Your task is finished "
    "as soon as you have emitted the Gate 3 rule list. "
    "After it, output the literal token `SEED_FIXTURE_COMPLETE` on "
    "its own line and IMMEDIATELY STOP. Do NOT attempt to answer the "
    "user's underlying request, do NOT invoke domain skills, do NOT "
    "call ask_user_question, and do NOT call SQL or any other tool "
    "after Gate 3 is written. Do NOT use Glob/find/ls to "
    "locate the user's task files, and do NOT read etl_pipeline.py, "
    "test files, or any project source file. Rule discovery only — "
    "task execution is FORBIDDEN."
)


def _usage_get(usage: object, key: str, default: int = 0) -> int:
    """Return a token count from a usage object that may be dict or attrs."""
    if isinstance(usage, dict):
        return usage.get(key, default) or default  # type: ignore
    return getattr(usage, key, default) or default


@dataclass(frozen=True)
class TurnEvent:
    """One event captured from the live SDK message loop, with timestamp.

    Used for opt-in per-turn timeline diagnostics (``--timing`` flag). The
    list of events is purely additive on ``AgentRun`` and has no effect
    unless a consumer formats it.

    - ``t_ms``   - milliseconds since ``query()`` start (the same clock
                   that produces ``AgentRun.duration_ms``).
    - ``kind``   - one of ``"tool_use"``, ``"assistant_text"``, ``"result"``.
    - ``detail`` - short human-readable summary (tool name + path,
                   text length, or stop reason).
    """

    t_ms: int
    kind: str
    detail: str


@dataclass(frozen=True)
class Citation:
    """A declared citation extracted from a Rules Loaded line (or legacy Reads Performed).

    Citations have the form ``<path> (<reason>) — N lines``. The line count
    may be None if the declaration was malformed or the line was a FAILED placeholder.
    """

    line_count: int | None = None
    failed: bool = False


@dataclass(frozen=True)
class AgentRun:
    """Normalized output of one live agent invocation."""

    fixture_id: str
    loaded: tuple[str, ...]
    """Union of read-call set, Rules Loaded section, and (legacy) Reads Performed section, sorted."""
    loaded_via_reads: tuple[str, ...]
    """Paths captured from real ``read_file`` (Read) tool calls."""
    loaded_via_reads_performed: tuple[str, ...]
    """Paths the agent declared under its ``## Reads Performed`` heading.

    Legacy only; always empty for v3.9+ agents (which emit
    ``**Bootstrap:**`` instead). Retained for backward compatibility
    with pre-v3.8 fixtures and historical CI artifacts.
    """
    loaded_via_section: tuple[str, ...]
    """Paths the agent declared under its ``## Rules Loaded`` heading (or legacy ``**Rules Loaded**`` bold form)."""
    citations_reads_performed: dict[str, Citation] = field(default_factory=dict)
    """Per-path citations extracted from the ``## Reads Performed`` section.

    Legacy only; always empty for v3.9+ agents.
    """
    citations_rules_loaded: dict[str, Citation] = field(default_factory=dict)
    """Per-path citations extracted from the ``## Rules Loaded`` section."""
    disagreements: tuple[str, ...] = ()
    """Rules that appeared in only some of the captured signals."""
    turns: int = 0
    duration_ms: int = 0
    model: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)
    final_text: str = ""
    """Concatenated assistant text from the live run (for debug/inspection)."""
    stop_reason: str = ""
    """The SDK's terminal ResultMessage stop reason, when exposed."""
    is_infra_error: bool = False
    """True when the SDK / model / connection failed; this run did NOT validly assess rule loading."""
    infra_error_detail: str = ""
    """Human-readable detail for the infra error classification."""
    events: tuple[TurnEvent, ...] = field(default_factory=tuple)
    """Per-message timeline (opt-in diagnostic; populated unconditionally,
    consumed only when a caller asks for it)."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0
    skill_invocations: tuple[str, ...] = field(default_factory=tuple)
    """Names of skills invoked during this run (legacy; empty for local-file rule-loader eval)."""
    output_violations: tuple[str, ...] = field(default_factory=tuple)
    """Bootstrap output-shape violations detected in the final assistant text."""


def _project_root() -> Path:
    """Locate the repo root via pyproject.toml."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def _normalize_to_repo_rule(file_path: str, project_root: Path) -> str | None:
    """Translate an absolute path into a repo-relative rule path.

    Accepts ``rules/*.md`` rule files.
    """
    try:
        p = Path(file_path).resolve()
        rel = p.relative_to(project_root.resolve())
    except (OSError, ValueError):
        return None
    rel_str = rel.as_posix()
    if not rel_str.startswith("rules/") or not rel_str.endswith(".md"):
        return None
    return rel_str


_INFRA_STOP_REASONS = frozenset({"error_during_execution"})


def _classify_infra(
    *,
    stop_reason: str,
    turns: int,
    duration_ms: int,
    reads_set: set[str],
    saw_result_message: bool,
) -> tuple[bool, str]:
    """Classify a run as INFRA error (SDK / model / connection) vs valid agent run.

    Returns (is_infra_error, detail). Detail is empty string when not an infra error.
    Per the v3.15 plan, four signals are OR'd together:
      1. stop_reason in INFRA_STOP_REASONS (e.g. "error_during_execution")
      2. No ResultMessage observed (iterator broke before completion)
      3. Zero turns AND duration_ms < 5000 (agent never started)
      4. Zero turns AND zero reads (agent never engaged)
    """
    if stop_reason in _INFRA_STOP_REASONS:
        return True, f"SDK reported stop_reason={stop_reason!r}"
    if not saw_result_message:
        return True, "no ResultMessage observed; SDK iterator broke before completion"
    if turns == 0 and duration_ms < 5000:
        return True, f"zero turns in {duration_ms}ms; agent never started"
    if turns == 0 and not reads_set:
        return True, "zero turns and zero reads; agent never engaged"
    return False, ""


_RULES_LOADED_HEADING_RE = re.compile(
    r"^(#{1,6}\s+Rules Loaded\b|\*\*Rules Loaded\*\*)",
    re.IGNORECASE,
)

# NEW - Gate 3 anchor (matches "- [x] Gate 3: ..." or "[ ] Gate 3: ...")
_GATE3_HEADING_RE = re.compile(
    r"^[-*]?\s*\[[ xX]\]\s*Gate 3\b",
    re.IGNORECASE,
)


def _is_rules_section_start(stripped: str) -> bool:
    return bool(_RULES_LOADED_HEADING_RE.match(stripped) or _GATE3_HEADING_RE.match(stripped))


def parse_rules_loaded_section(text: str) -> tuple[str, ...]:
    """Extract rule paths from a ``**Rules Loaded**`` (or legacy ``## Rules Loaded``) section.

    Permissive parser: scans every ``rules/*.md`` token under the
    Rules Loaded marker until the next heading or ``Task Switch:`` line.
    Accepts the current Gate 3 anchor (``- [x] Gate 3:``) and the legacy
    ``**Rules Loaded**`` / ``## Rules Loaded`` formats for backward
    compatibility with pre-v3.9-patch fixtures and historical CI artifacts.
    Returns sorted unique paths.
    """
    if not text:
        return ()
    lines = text.splitlines()
    found: set[str] = set()
    in_section = False
    for line in lines:
        stripped = line.strip()
        if _is_rules_section_start(stripped):
            in_section = True
            continue
        if in_section and (stripped.startswith("#") or re.match(r"^Task Switch:", stripped)):
            break
        if in_section:
            for m in RULE_PATH_RE.findall(line):
                found.add(m)
    return tuple(sorted(found))


def parse_reads_performed_section(text: str) -> tuple[str, ...]:
    """Extract rule paths from a ``## Reads Performed`` section.

    **Legacy/backward-compat.** This section was retired by the
    AGENTS.md bootstrap contract. Modern agents emit a ``**Bootstrap:**``
    compact summary line instead. This parser is kept for pre-v3.8
    fixtures and historical CI artifacts. When the section is absent,
    returns an empty tuple (no spurious disagreements are raised).
    """
    if not text:
        return ()
    lines = text.splitlines()
    found: set[str] = set()
    in_section = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+Reads Performed\b", stripped, re.IGNORECASE):
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            break
        if in_section:
            for m in RULE_PATH_RE.findall(line):
                found.add(m)
    return tuple(sorted(found))


_BOOTSTRAP_RE = re.compile(
    r"\*\*Bootstrap:\*\*.*?(\d+)\s+rules?\s+loaded,\s*(\d+)\s+failed",
    re.IGNORECASE,
)

_NO_RULES_RE = re.compile(
    r"\(none\s+[—-]\s+no\s+domain\s+rules\s+matched\)"  # legacy
    r"|Gate 3:\s*none\s+matched",  # new sentinel
    re.IGNORECASE,
)

# Gate 1 foundation-citation anchor (new shape: foundation on Gate 1 only)
_GATE1_FOUNDATION_RE = re.compile(
    r"^[-*]?\s*\[[ xX]\]\s*Gate 1\b.*?Foundation\b",
    re.IGNORECASE,
)


def parse_bootstrap_line(text: str) -> dict[str, int | bool]:
    """Parse the compact ``**Bootstrap:**`` summary line from v3.8 output.

    Returns ``{'found': bool, 'n_loaded': int, 'n_failed': int}``.
    The ``**Bootstrap:**`` line must be the first emitted output per the
    AGENTS.md bootstrap contract.
    """
    if not text:
        return {"found": False, "n_loaded": 0, "n_failed": 0}
    for line in text.splitlines():
        m = _BOOTSTRAP_RE.search(line)
        if m:
            return {
                "found": True,
                "n_loaded": int(m.group(1)),
                "n_failed": int(m.group(2)),
            }
    return {"found": False, "n_loaded": 0, "n_failed": 0}


def extract_contract_text(text: str) -> str:
    """Return the contract block from the first Rules Loaded marker onward.

    The current AGENTS.md contract emits a PRE-FLIGHT ``- [x] Gate 3:`` rule
    list. Legacy responses emit ``## Rules Loaded`` / ``**Rules Loaded**`` (or
    the retired ``**Bootstrap:**`` prefix). Anchoring backs up to the start of
    the line containing the earliest marker so a bullet/checkbox prefix (e.g.
    ``- [x] Gate 3:``) is preserved for downstream anchor-regex matching.
    """
    candidates = ["Gate 3:", "## Rules Loaded", "**Rules Loaded**", "**Bootstrap:**"]
    earliest = -1
    for marker in candidates:
        idx = text.find(marker)
        if idx >= 0 and (earliest == -1 or idx < earliest):
            earliest = idx
    if earliest < 0:
        return text
    line_start = text.rfind("\n", 0, earliest) + 1
    return text[line_start:]


def validate_output_shape(text: str, *, loaded_count: int) -> tuple[str, ...]:
    """Return output-shape violations for the AGENTS.md bootstrap contract.

    Required: a PRE-FLIGHT Gate 3 rule list or legacy ``**Rules Loaded**``
    section in the final response. No-match runs must use the explicit
    ``(none - no domain rules matched)`` body.
    """
    violations: list[str] = []
    if not text:
        return ("final assistant text is empty",)
    has_legacy = "**Rules Loaded**" in text or re.search(r"(?m)^#{1,6}\s+Rules Loaded\b", text)
    has_gate3 = bool(re.search(r"(?m)^[-*]?\s*\[[ xX]\]\s*Gate 3\b", text, re.IGNORECASE))
    has_rules_loaded = has_legacy or has_gate3
    if not has_rules_loaded:
        violations.append("missing Rules Loaded (Gate 3 or **Rules Loaded**) section")
    if loaded_count == 0 and not _NO_RULES_RE.search(text):
        violations.append("zero loaded rules must use explicit no-match Rules Loaded body")
    return tuple(violations)


CITATION_RE_LINES_ONLY = re.compile(
    r"(?:[—\-]\s*(?P<suffix>\d+)\s*lines\b|\blines\s+(?P<prefix>\d+)\b)",
    re.IGNORECASE,
)

FAILED_RE = re.compile(r"FAILED\s*:\s*not\s+found", re.IGNORECASE)


def extract_citations(text: str, section_heading: str) -> dict[str, Citation]:
    """Extract per-rule citations from the named section.

    Citation format per AGENTS.md is ``<path> (<reason>) — N lines``.
    ``FAILED: not found`` lines yield a ``Citation(failed=True)``. Returns
    ``{rule_path: Citation}``.

    For ``section_heading == "Rules Loaded"``, accepts the current Gate 3
    anchor (``- [x] Gate 3:``) and the legacy bold-inline
    (``**Rules Loaded**``) / heading (``## Rules Loaded``) formats for
    backward compatibility. Additionally scans the Gate 1 line for a
    foundation citation (new Gate-1-only shape) so citation-drift detection
    is preserved after the foundation row moved from Gate 3 to Gate 1.
    """
    if not text:
        return {}
    lines = text.splitlines()
    citations: dict[str, Citation] = {}
    in_section = False
    if section_heading == "Rules Loaded":
        use_rules_anchor = True
        # Scan Gate 1 foundation citation (new shape: foundation on Gate 1 only)
        for line in lines:
            stripped = line.strip()
            if _GATE1_FOUNDATION_RE.match(stripped):
                paths = RULE_PATH_RE.findall(line)
                if paths:
                    path = paths[0]
                    m2 = CITATION_RE_LINES_ONLY.search(line)
                    if m2:
                        line_count = int(m2.group("suffix") or m2.group("prefix"))
                        citations[path] = Citation(line_count=line_count)
                    elif path not in citations:
                        citations[path] = Citation()
                break
    else:
        use_rules_anchor = False
        heading_re = re.compile(rf"^#{{1,6}}\s+{re.escape(section_heading)}\b", re.IGNORECASE)
    for line in lines:
        stripped = line.strip()
        if use_rules_anchor:
            if _is_rules_section_start(stripped):
                in_section = True
                continue
        elif heading_re.match(stripped):
            in_section = True
            continue
        if in_section and (stripped.startswith("#") or re.match(r"^Task Switch:", stripped)):
            break
        if not in_section:
            continue
        paths = RULE_PATH_RE.findall(line)
        if not paths:
            continue
        path = paths[0]
        if FAILED_RE.search(line):
            citations[path] = Citation(failed=True)
            continue
        m2 = CITATION_RE_LINES_ONLY.search(line)
        if m2:
            line_count = int(m2.group("suffix") or m2.group("prefix"))
            citations[path] = Citation(line_count=line_count)
        elif path not in citations:
            citations[path] = Citation()
    return citations


def is_live_enabled() -> bool:
    """Return True when explicit live-agent runs are permitted."""
    return os.environ.get("RUN_LIVE_AGENT") == "1"


def run_live(
    fixture_id: str,
    prompt: str,
    *,
    project_root: Path | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    effort: str = DEFAULT_EFFORT,
    model: str = "auto",
    connection: str | None = None,
) -> AgentRun:
    """Drive the Cortex Code Agent SDK against ``prompt``.

    Allowed tools restricted to ``Read``/``Glob``/``Grep``. Records every
    rule-file ``Read`` call via a ``PreToolUse`` hook and parses the
    Gate 1 foundation citation and Gate 3 domain rule list (or legacy
    ``**Rules Loaded**`` section) from the assistant output.
    Contract: AGENTS.md bootstrap contract.
    """
    return asyncio.run(
        run_live_async(
            fixture_id,
            prompt,
            project_root=project_root,
            max_turns=max_turns,
            effort=effort,
            model=model,
            connection=connection,
        )
    )


async def run_live_async(
    fixture_id: str,
    prompt: str,
    *,
    project_root: Path | None,
    max_turns: int,
    effort: str,
    model: str,
    connection: str | None,
) -> AgentRun:
    """Async core of the live SDK runner. Intended for batch use."""
    try:
        from cortex_code_agent_sdk import (  # type: ignore[import-not-found,import-untyped]
            AssistantMessage,
            CortexCodeAgentOptions,
            HookMatcher,
            ResultMessage,
            query,
        )
    except ImportError as exc:  # pragma: no cover — covered by doctor
        raise RuntimeError(
            "Cortex Code Agent SDK not installed. Live runs require: "
            "`uv add --group live-agent cortex-code-agent-sdk` "
            "(or the equivalent `uv pip install cortex-code-agent-sdk`)."
        ) from exc

    root = project_root or _project_root()
    reads: set[str] = set()
    final_text_chunks: list[str] = []
    notes: list[str] = []

    async def pre_tool_use(input_data, _tool_use_id, _context):
        """Record every rule-file Read path."""
        # PreToolUseHookInput exposes ``tool_name`` and ``tool_input`` fields.
        tool = getattr(input_data, "tool_name", None) or ""
        tool_input = getattr(input_data, "tool_input", None) or {}
        if tool.lower() == "read":
            target = tool_input.get("file_path") or tool_input.get("filePath") or ""
            if target:
                rel = _normalize_to_repo_rule(target, root)
                if rel:
                    reads.add(rel)
                    notes.append(f"Read: {rel}")
        return {}

    options = CortexCodeAgentOptions(
        cwd=str(root),
        max_turns=max_turns,
        effort=effort,
        model=model,
        setting_sources=["project"],
        allowed_tools=["Read", "Glob", "Grep", "Bash"],
        system_prompt=(
            "HARD STOP: This is a rule-discovery probe. You MUST stop after "
            "emitting the PRE-FLIGHT Gate 1 foundation citation and Gate 3 domain "
            "rule list. You MUST NOT execute the user's task, "
            "write code, read or search the user's task/project files "
            "(e.g. etl_pipeline.py, via Read/Glob/find/ls/list_dir), call SQL "
            "tools, call ask_user_question, or perform ANY action beyond rule "
            "discovery. After the Gate 3 rule list, "
            "output `SEED_FIXTURE_COMPLETE` and immediately stop. "
            "This stop boundary applies AFTER rule discovery: it forbids executing the user's underlying task, but it does NOT override the AGENTS.md bootstrap reading steps — you MUST still read rules/000-global-core.md, read_file every matched rule, AND read_file each matched rule's `required:` Depends (transitively) before emitting the Gate 3 block.\n\n"
            "You are evaluating rule discovery for the ai_coding_rules repo. "
            "Before answering ANY user request, you MUST follow the AGENTS.md "
            "bootstrap protocol exactly:\n\n"
            "  1. Read `AGENTS.md` at the project root.\n"
            "  2. Always read `rules/000-global-core.md` first (this is the "
            "foundation rule, loaded on every request).\n"
            "  3. Extract candidate keywords from the user prompt and run "
            "`grep -iwE 'KW1|KW2|KW3' rules/RULES_INDEX.md` to discover "
            "matching rules. RULES_INDEX.md has one space-separated row "
            "per rule; each matching row is self-contained — the rule filename "
            "is the first field, no further context lookup needed. "
            "RULES_INDEX.md is the single agent discovery index.\n"
            "  4. Read every matched rule. Then, for EACH matched rule's "
            "`**Depends:**` field, you MUST also read_file every `required:` "
            "dependency rule — these are transitive, so a required dep that "
            "itself declares further `required:` deps must also be read, until "
            "the required-dependency closure is fully loaded. Consider "
            "`optional:` deps based on context.\n"
            "  5. Use the `Read`, `Grep`, and `Bash` tools for rule discovery "
            "(Glob/find/ls only to locate rule files, never the user's task "
            "files) - do not answer from memory.\n\n"
            "Your FINAL assistant message MUST include a PRE-FLIGHT block with "
            "Gate 1 foundation citation and Gate 3 domain rules formatted as:\n\n"
            "  PRE-FLIGHT:\n"
            "  - [x] Gate 1: Foundation rules/000-global-core.md — N lines\n"
            "  - [x] Gate 2: rules/RULES_INDEX.md searched for: keyword1, keyword2\n"
            "  - [x] Gate 3: +N domain rule(s):\n"
            "    - rules/<matched-rule>.md (<reason>) — N lines\n"
            "    - rules/<required-dep>.md (required dep of <matched-rule>) — N lines\n\n"
            "Citation rules: `N lines` MUST be the `wc -l` output for the "
            "file (number of newline characters, not visual line count). "
            "Do not include `RuleVersion` or `LastUpdated` in citations.\n\n"
            "If no domain rule matches the prompt, emit:\n\n"
            "  - [x] Gate 3: none matched\n\n"
            "Do NOT emit a standalone `## Rules Loaded` / `**Rules Loaded**` section "
            "(the old format is retired; citations now live inside PRE-FLIGHT Gate 3).\n\n"
            "If you cannot read AGENTS.md, output the single token "
            "`BOOTSTRAP_FAILED` and stop. Do NOT generate any answer that "
            "lacks the Gate 3 rule list - an answer without it is "
            "non-compliant.\n\n"
            "STOP CONDITION (seed-fixture scope only): Your task is finished "
            "as soon as you have emitted the Gate 3 rule list. "
            "After it, output the literal token `SEED_FIXTURE_COMPLETE` on "
            "its own line and IMMEDIATELY STOP. Do NOT attempt to answer the "
            "user's underlying request, do NOT invoke domain skills, do NOT "
            "call ask_user_question, and do NOT call SQL or any other tool "
            "after Gate 3 is written. Do NOT use Glob/find/ls to "
            "locate the user's task files, and do NOT read etl_pipeline.py, "
            "test files, or any project source file. Rule discovery only — "
            "task execution is FORBIDDEN."
        ),
        hooks={"PreToolUse": [HookMatcher(matcher="Read", hooks=[pre_tool_use])]},
        connection=connection,
        stderr=_filter_coco_stderr,
    )

    start = time.perf_counter()
    turns = 0
    stop_reason = ""
    saw_result_message = False
    input_tokens = 0
    output_tokens = 0
    total_cost_usd = 0.0
    events: list[TurnEvent] = []

    def _now_ms() -> int:
        return int((time.perf_counter() - start) * 1000)

    def _short_tool_detail(name: str, ti: object) -> str:
        if isinstance(ti, dict):
            for key in (
                "file_path",
                "filePath",
                "path",
                "command",
                "pattern",
                "skill_name",
                "name",
            ):
                v = ti.get(key)
                if isinstance(v, str) and v:
                    return f"{name} {key}={v[:120]}"
        return name

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content or []:
                text = getattr(block, "text", None)
                if text:
                    final_text_chunks.append(text)
                    events.append(
                        TurnEvent(
                            t_ms=_now_ms(),
                            kind="assistant_text",
                            detail=f"len={len(text)} head={text[:80]!r}",
                        )
                    )
                # Capture tool_use blocks regardless of which tool. This
                # surfaces calls the runner does not otherwise track
                # (e.g., Glob, Grep, Bash) for debugging.
                tool_name = getattr(block, "name", None) or getattr(block, "tool_name", None)
                tool_input = getattr(block, "input", None) or getattr(block, "tool_input", None)
                if tool_name and tool_input is not None:
                    notes.append(f"tool_use: {tool_name} {tool_input!r}")
                    events.append(
                        TurnEvent(
                            t_ms=_now_ms(),
                            kind="tool_use",
                            detail=_short_tool_detail(str(tool_name), tool_input),
                        )
                    )
                elif tool_name:
                    notes.append(f"tool_use: {tool_name}")
                    events.append(
                        TurnEvent(
                            t_ms=_now_ms(),
                            kind="tool_use",
                            detail=str(tool_name),
                        )
                    )
                # Belt-and-suspenders: also derive ``loaded_via_reads`` from
                # message-loop tool_use blocks. The PreToolUse hook is the
                # primary source but does not always fire (SDK hook
                # registration can silently no-op). Capture Read paths
                # directly from the assistant message stream as well.
                if tool_name and str(tool_name).lower() == "read" and isinstance(tool_input, dict):
                    target = tool_input.get("file_path") or tool_input.get("filePath") or ""
                    if target:
                        rel = _normalize_to_repo_rule(target, root)
                        if rel:
                            reads.add(rel)
        elif isinstance(message, ResultMessage):
            saw_result_message = True
            turns = getattr(message, "num_turns", 0) or getattr(message, "turns", 0)
            stop_reason = (
                getattr(message, "stop_reason", "")
                or getattr(message, "subtype", "")
                or getattr(message, "result", "")
                or ""
            )
            usage = getattr(message, "usage", None) or {}
            input_tokens = (
                _usage_get(usage, "input_tokens")
                + _usage_get(usage, "cache_creation_input_tokens")
                + _usage_get(usage, "cache_read_input_tokens")
            )
            output_tokens = _usage_get(usage, "output_tokens")
            total_cost_usd = getattr(message, "total_cost_usd", None) or 0.0
            events.append(
                TurnEvent(
                    t_ms=_now_ms(),
                    kind="result",
                    detail=f"stop_reason={stop_reason or '(none)'} turns={turns}",
                )
            )
            # Do not break: let the generator complete so anyio's TaskGroup
            # exits in the same task that entered it.

    duration_ms = int((time.perf_counter() - start) * 1000)
    final_text = extract_contract_text("\n".join(final_text_chunks))
    section_rules = parse_rules_loaded_section(final_text)
    reads_performed = parse_reads_performed_section(final_text)
    citations_reads = extract_citations(final_text, "Reads Performed")
    citations_section = extract_citations(final_text, "Rules Loaded")

    reads_set = set(reads)
    reads_performed_set = set(reads_performed)
    section_set = set(section_rules)

    # Discovery artifacts: read for protocol, never cited. Suppress these paths
    # from all signal-mismatch comparisons so reading them does not produce
    # false-positive "In (A) tool reads only" failures.
    _DISCOVERY_ARTIFACTS = frozenset({"AGENTS.md"})
    reads_set -= _DISCOVERY_ARTIFACTS
    reads_performed_set -= _DISCOVERY_ARTIFACTS
    section_set -= _DISCOVERY_ARTIFACTS

    reads_for_perf_cmp = reads_set
    reads_perf_for_reads_cmp = reads_performed_set
    reads_for_loaded_cmp = reads_set
    reads_perf_for_loaded_cmp = reads_performed_set

    # v3.8+: ``## Reads Performed`` is retired. Skip comparisons involving
    # reads-performed when the section is absent to avoid spurious
    # disagreements on every v3.8-compliant run.
    _has_reads_performed = bool(reads_performed_set)

    disagreements_list: list[str] = []
    if _has_reads_performed:
        for r in sorted(reads_for_perf_cmp - reads_perf_for_reads_cmp):
            disagreements_list.append(f"only-in-tool-reads-vs-reads-performed: {r}")
        for r in sorted(reads_perf_for_reads_cmp - reads_for_perf_cmp):
            c = citations_reads.get(r)
            if c is None or not c.failed:
                disagreements_list.append(f"only-in-reads-performed-vs-tool-reads: {r}")
    for r in sorted(reads_for_loaded_cmp - section_set):
        disagreements_list.append(f"only-in-tool-reads-vs-rules-loaded: {r}")
    for r in sorted(section_set - reads_for_loaded_cmp):
        disagreements_list.append(f"only-in-rules-loaded-vs-tool-reads: {r}")
    if _has_reads_performed:
        for r in sorted(reads_perf_for_loaded_cmp - section_set):
            c = citations_reads.get(r)
            if c is None or not c.failed:
                disagreements_list.append(f"only-in-reads-performed-vs-rules-loaded: {r}")
        for r in sorted(section_set - reads_perf_for_loaded_cmp):
            disagreements_list.append(f"only-in-rules-loaded-vs-reads-performed: {r}")

    union = tuple(sorted(reads_set | reads_performed_set | section_set))
    output_violations = validate_output_shape(final_text, loaded_count=len(union))

    is_infra_error, infra_error_detail = _classify_infra(
        stop_reason=str(stop_reason),
        turns=turns,
        duration_ms=duration_ms,
        reads_set=reads_set,
        saw_result_message=saw_result_message,
    )

    return AgentRun(
        fixture_id=fixture_id,
        loaded=union,
        loaded_via_reads=tuple(sorted(reads_set)),
        loaded_via_reads_performed=tuple(sorted(reads_performed_set)),
        loaded_via_section=section_rules,
        citations_reads_performed=citations_reads,
        citations_rules_loaded=citations_section,
        disagreements=tuple(disagreements_list),
        turns=turns,
        duration_ms=duration_ms,
        model=model,
        notes=tuple(notes),
        final_text=final_text,
        stop_reason=str(stop_reason),
        is_infra_error=is_infra_error,
        infra_error_detail=infra_error_detail,
        events=tuple(events),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_cost_usd=total_cost_usd,
        skill_invocations=(),
        output_violations=output_violations,
    )
