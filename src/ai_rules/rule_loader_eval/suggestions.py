"""Mechanical fixture-suggestion engine for the seed-fixture command.

Given the live agent's loaded set, the original prompt, and the rule
metadata snapshot, produce deterministic suggestions for the fixture
fields the author still has to fill in:

- ``required`` vs ``dependencies`` vs ``optional`` (auto-demoted) split.
- ``trigger_evidence`` (kw/ext/file/dir) — alias-normalised literal
  phrase extraction from the prompt matched against each rule's
  ``**Keywords:**`` metadata.
- ``ngram_kw_suggestions`` — high-signal prompt phrases not tied to any
  rule's metadata; rendered as inline comments rather than YAML values.

The output is purely advisory; authors review and edit the generated
YAML skeleton before committing.

Design invariant (C5): every emitted ``kw`` value is a literal substring
of the prompt and passes the same boundary regex used by
``fixtures._kw_pattern``.

Auto-demote contract (refresh-all-valid-by-construction): a loaded rule
with no typed-Keywords trigger evidence in the prompt is moved from ``required``
(or ``dependencies``) to ``optional`` so the rendered fixture passes
``validate`` by construction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ai_rules.rule_loader_eval.rules_meta import RuleMetadata

TRIGGER_KINDS = ("kw", "ext", "file", "dir")

MIN_KW_EVIDENCE_TARGET: int = 5
"""Target number of ``kw`` evidence suggestions per fixture skeleton.

Historically the engine padded ``evidence["kw"]`` with prompt n-grams up
to this target. Under the valid-by-construction contract n-gram
suggestions live in ``Suggestions.ngram_kw_suggestions`` instead and the
renderer emits them as inline ``# n-gram (no rule):`` comments.
"""

_STOP_WORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "is",
        "it",
        "by",
        "as",
        "be",
        "up",
        "my",
        "me",
        "we",
        "use",
        "with",
        "that",
        "this",
        "from",
        "can",
        "do",
        "i",
        "you",
        "how",
        "what",
        "when",
        "where",
        "would",
        "should",
        "could",
        "will",
        "please",
        "help",
        "write",
        "make",
        "add",
        "get",
        "let",
        "set",
        "need",
        "want",
        "create",
        "update",
        "fix",
        "run",
        "just",
        "all",
        "over",
        "our",
        "into",
        "out",
        "its",
        "has",
        "have",
        "had",
        "was",
        "are",
        "been",
        "your",
        "new",
        "so",
        "some",
        "any",
        "these",
    }
)

_TOKEN_RE: re.Pattern[str] = re.compile(r"[A-Za-z][A-Za-z0-9_-]*[A-Za-z0-9]|[A-Za-z]")
"""Matches a single word token including internal hyphens and underscores."""


@dataclass(frozen=True)
class Suggestions:
    """Per-rule and aggregate suggestions for the fixture skeleton."""

    required: tuple[str, ...] = ()
    """Loaded rules that match the prompt directly (kw/ext/file/dir)."""

    dependencies: tuple[str, ...] = ()
    """Loaded rules pulled in transitively via another loaded rule's ``**Depends:**``
    AND that have at least one typed-Keywords trigger satisfied by the prompt themselves.

    Rules that are deps but have no own evidence are auto-demoted to ``optional``
    so the rendered fixture passes ``validate`` by construction (validate ignores
    deps so this is safe; the demotion just makes the over-fire visible).
    """

    optional: tuple[str, ...] = ()
    """Loaded rules with no typed-Keywords trigger evidence in the prompt.

    These were loaded by the live agent speculatively (or pulled in via Depends)
    but the validator's trigger-evidence invariant cannot prove the rule legitimately
    fired for this prompt. The renderer emits them under ``optional:`` with a
    ``# auto-demoted`` comment + per-rule ``# missing:`` hint listing the rule's
    declared typed Keywords triggers.
    """

    rule_reasons: dict[str, str] = field(default_factory=dict)
    """Per-rule one-line reason string for inline comments."""

    trigger_evidence: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Aggregate evidence keyed by kind (``kw``, ``ext``, ``file``, ``dir``).

    Only rule-tied evidence; n-gram-derived prompt phrases live in
    ``ngram_kw_suggestions``.
    """

    ngram_kw_suggestions: tuple[str, ...] = ()
    """High-signal prompt phrases not tied to any rule's metadata.

    Rendered as inline ``# n-gram (no rule):`` comments under the ``kw:`` block
    rather than as YAML values, so they don't pollute the validator's
    ``_check_evidence_in_prompt`` cross-check.
    """

    auto_demoted: frozenset[str] = field(default_factory=frozenset)
    """Rules moved to ``optional`` because no typed-Keywords trigger evidence was found.

    Includes both rules that would have been ``required`` and rules that would
    have been ``dependencies`` but had no own evidence.
    """

    auto_demoted_was_dep: frozenset[str] = field(default_factory=frozenset)
    """Subset of ``auto_demoted`` that originally classified as a dependency.

    Used by the renderer to emit ``# auto-demoted (was dep): ...`` for these
    entries, distinguishing them from speculative top-level loads.
    """

    missing_triggers: dict[str, dict[str, tuple[str, ...]]] = field(default_factory=dict)
    """Per-rule typed-Keywords trigger metadata for auto-demoted rules.

    Keyed by rule path; values are ``{"kw": (...), "ext": (...), "file": (...),
    "dir": (...)}`` listing what the prompt would have to contain for the rule to
    legitimately match. Rendered as ``# missing: kw=...; ext=...; ...`` hints
    under each auto-demoted line.
    """


def _literal_aliases(term: str) -> tuple[str, ...]:
    """Return hyphen/space/underscore normalisation variants for *term*.

    Produces the original term plus any variants formed by replacing
    hyphens with spaces, spaces with hyphens, and underscores with spaces.
    Duplicates are removed while preserving insertion order (original first).
    """
    variants: list[str] = [term]
    if "-" in term:
        variants.append(term.replace("-", " "))
    if " " in term:
        variants.append(term.replace(" ", "-"))
    if "_" in term:
        variants.append(term.replace("_", " "))
    return tuple(dict.fromkeys(variants))


def _find_literal_match(prompt: str, term: str) -> str | None:
    """Return the literal substring of *prompt* that matches *term* or any alias.

    Uses the same word-boundary pattern as ``fixtures._kw_pattern``:
    ``(?<![A-Za-z0-9_])<term>(?![A-Za-z0-9_])``, case-insensitive.
    Tries *term* and each alias returned by ``_literal_aliases`` in order;
    returns the first captured match or ``None`` if nothing matches.
    """
    for alias in _literal_aliases(term):
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_]){re.escape(alias)}(?![A-Za-z0-9_])",
            re.IGNORECASE,
        )
        m = pattern.search(prompt)
        if m:
            return m.group(0)
    return None


def _extract_prompt_phrases(prompt: str) -> tuple[str, ...]:
    """Extract high-signal 1-4 word literal phrases from *prompt*.

    Tokenises the prompt using ``_TOKEN_RE``, then builds n-grams of
    length 1-4.  A n-gram is included only when:

    - All gaps between consecutive tokens contain only whitespace (no
      ``/``, ``.``, or other non-whitespace characters — this prevents
      generating path fragments like ``procs/cleanup``).
    - At least one token is not in ``_STOP_WORDS``.

    Phrases are de-duplicated case-insensitively.  The return tuple is
    ordered by descending score (non-stop-word count + small length
    bonus), then ascending normalised text for determinism.
    """
    token_spans = [(m.group(), m.start(), m.end()) for m in _TOKEN_RE.finditer(prompt)]
    n_tokens = len(token_spans)
    phrases: list[tuple[float, str, str]] = []  # (neg_score, normalized, literal)
    seen_lower: set[str] = set()

    for n in range(1, 5):
        for i in range(n_tokens - n + 1):
            chunk = token_spans[i : i + n]

            # Only include when gaps between consecutive tokens are non-newline
            # whitespace (spaces/tabs only). Allowing ``\s`` here would let
            # multi-line prompts produce kw phrases that span line breaks,
            # yielding YAML values like ``concrete\nsuggestions for naming``
            # which break ``kw: [...]`` rendering when serialized.
            gap_ok = all(
                re.fullmatch(r"[ \t]*", prompt[chunk[j][2] : chunk[j + 1][1]]) for j in range(n - 1)
            )
            if not gap_ok:
                continue

            tokens_lower = [t[0].lower() for t in chunk]
            non_stop = sum(1 for t in tokens_lower if t not in _STOP_WORDS)
            if non_stop == 0:
                continue

            literal = prompt[chunk[0][1] : chunk[-1][2]]
            # Belt-and-suspenders: reject any literal that still contains a
            # newline (defends against future changes to the gap regex).
            if "\n" in literal or "\r" in literal:
                continue
            normalized = literal.lower()
            if normalized in seen_lower:
                continue
            seen_lower.add(normalized)

            score = non_stop + (n - 1) * 0.3
            phrases.append((-score, normalized, literal))

    phrases.sort(key=lambda x: (x[0], x[1]))
    return tuple(p[2] for p in phrases)


def _augment_kw_evidence(
    evidence: dict[str, set[str]],
    prompt_phrases: tuple[str, ...],
    target: int = MIN_KW_EVIDENCE_TARGET,
) -> None:
    """Extend ``evidence["kw"]`` with high-signal prompt phrases up to *target*.

    Adds phrases from *prompt_phrases* in score order, skipping any whose
    lower-cased form is already represented in the evidence set.  Stops
    when ``len(evidence["kw"]) >= target``.  Modifies *evidence* in place.

    If fewer than *target* safe literal phrases exist in the prompt, emits
    fewer than *target* rather than fabricating evidence.

    Retained for backward compatibility with existing tests; the modern
    refresh-all path uses :func:`_compute_ngram_suggestions` and emits
    n-grams as comments rather than padding evidence.
    """
    kw_lower: set[str] = {v.lower() for v in evidence["kw"]}
    for phrase in prompt_phrases:
        if len(evidence["kw"]) >= target:
            break
        if phrase.lower() not in kw_lower:
            evidence["kw"].add(phrase)
            kw_lower.add(phrase.lower())


def _compute_ngram_suggestions(
    prompt: str,
    rule_tied_kw: set[str],
    target: int = MIN_KW_EVIDENCE_TARGET,
) -> tuple[str, ...]:
    """Return up to *target* high-signal n-gram phrases not already represented.

    Phrases must not appear in *rule_tied_kw*.

    Each returned phrase is a literal substring of *prompt* and passes the
    fixture validator's ``_kw_pattern`` boundary check by construction.
    Used by :func:`build_suggestions` to populate
    :attr:`Suggestions.ngram_kw_suggestions` for inline comment rendering.
    """
    phrases = _extract_prompt_phrases(prompt)
    rule_lower = {v.lower() for v in rule_tied_kw}
    out: list[str] = []
    seen_lower: set[str] = set()
    for phrase in phrases:
        if len(out) >= target:
            break
        low = phrase.lower()
        if low in rule_lower or low in seen_lower:
            continue
        out.append(phrase)
        seen_lower.add(low)
    return tuple(out)


def build_suggestions(
    loaded: tuple[str, ...],
    prompt: str,
    rules_meta: dict[str, RuleMetadata],
) -> Suggestions:
    """Compute fixture-field suggestions from the live-loaded set + prompt.

    Uses each rule's typed ``Keywords`` metadata as the
    authoritative trigger source.  Alias-normalised matching (hyphen/space
    variants via ``_find_literal_match``) finds the literal phrase in the
    prompt rather than returning the metadata token.

    Auto-demote: any loaded rule with no per-rule trigger evidence is moved
    to ``optional`` regardless of whether it would otherwise classify as
    ``required`` or ``dependencies``. This is the valid-by-construction
    contract: validate's trigger-evidence invariant only applies to
    ``required`` so demoting evidence-less rules eliminates a class of
    refresh-all to validate failures.
    """
    loaded_set = set(loaded)
    if not loaded_set:
        return Suggestions()

    # 1. required vs dependencies via the Depends DAG (initial classification).
    #    Only ``required:`` Depends drive the strict dep bucket; ``optional:``
    #    Depends are recorded separately and routed into the optional bucket.
    is_dependency: set[str] = set()
    optional_dep_parents: dict[str, set[str]] = {}
    for rule in loaded_set:
        meta = rules_meta.get(rule)
        if not meta:
            continue
        for dep in meta.depends_required or meta.depends:
            if dep in loaded_set:
                is_dependency.add(dep)
        for dep in meta.depends_optional:
            if dep in loaded_set:
                optional_dep_parents.setdefault(dep, set()).add(rule)

    initial_required = sorted(loaded_set - is_dependency)
    initial_dependencies = sorted(is_dependency)

    # 2. Per-rule reasons + aggregate evidence + auto-demote split.
    reasons: dict[str, str] = {}
    evidence: dict[str, set[str]] = {k: set() for k in TRIGGER_KINDS}
    auto_demoted: set[str] = set()
    auto_demoted_was_dep: set[str] = set()
    missing_triggers: dict[str, dict[str, tuple[str, ...]]] = {}

    final_required: list[str] = []
    final_dependencies: list[str] = []
    final_optional: list[str] = []

    for rule in initial_required:
        rule_evidence = _evidence_for_rule(rule, rules_meta, prompt)
        for kind, hits in rule_evidence.items():
            evidence[kind].update(hits)
        any_evidence = any(rule_evidence.values())
        if any_evidence:
            reasons[rule] = _reason_from_evidence(rule_evidence)
            final_required.append(rule)
        else:
            reasons[rule] = "auto-demoted: no trigger evidence"
            auto_demoted.add(rule)
            missing_triggers[rule] = _missing_triggers_for_rule(rule, rules_meta)
            final_optional.append(rule)

    for rule in initial_dependencies:
        rule_evidence = _evidence_for_rule(rule, rules_meta, prompt)
        for kind, hits in rule_evidence.items():
            evidence[kind].update(hits)
        any_evidence = any(rule_evidence.values())
        parents = sorted(
            other
            for other in loaded_set
            for _meta in (rules_meta.get(other),)
            if _meta is not None and rule in _meta.depends
        )
        if any_evidence:
            # Dep rule that also has its own evidence — keep classification as dep.
            parent_str = ", ".join(_short(p) for p in parents) if parents else "unknown"
            reasons[rule] = f"dep of {parent_str}"
            final_dependencies.append(rule)
        else:
            reasons[rule] = "auto-demoted (was dep): no trigger evidence"
            auto_demoted.add(rule)
            auto_demoted_was_dep.add(rule)
            missing_triggers[rule] = _missing_triggers_for_rule(rule, rules_meta)
            final_optional.append(rule)

    # 3. Case-insensitive dedup on kw evidence (space vs hyphen variants may
    #    appear from different rules; keep the first occurrence in sorted order).
    kw_deduped: list[str] = []
    kw_seen: set[str] = set()
    for phrase in sorted(evidence["kw"], key=str.lower):
        if phrase.lower() not in kw_seen:
            kw_deduped.append(phrase)
            kw_seen.add(phrase.lower())
    evidence["kw"] = set(kw_deduped)

    # 4. Compute n-gram suggestions (NOT added to evidence; rendered as comments).
    ngram_suggestions = _compute_ngram_suggestions(prompt, evidence["kw"])

    # 5. Assemble result.
    return Suggestions(
        required=tuple(sorted(final_required)),
        dependencies=tuple(sorted(final_dependencies)),
        optional=tuple(sorted(final_optional)),
        rule_reasons=reasons,
        trigger_evidence={k: tuple(sorted(v, key=str.lower)) for k, v in evidence.items() if v},
        ngram_kw_suggestions=ngram_suggestions,
        auto_demoted=frozenset(auto_demoted),
        auto_demoted_was_dep=frozenset(auto_demoted_was_dep),
        missing_triggers=missing_triggers,
    )


def _evidence_for_rule(
    rule: str,
    rules_meta: dict[str, RuleMetadata],
    prompt: str,
) -> dict[str, list[str]]:
    """Match a single rule's metadata against the prompt; return per-kind literal hits.

    For ``kw`` evidence, uses ``_find_literal_match`` to obtain the exact
    phrase as it appears in *prompt* (including hyphen/space variants).
    For ``ext``, ``file``, and ``dir`` evidence, uses simple case-insensitive
    substring matching against the lower-cased prompt (unchanged behaviour).

    Important contract: only typed-Keywords trigger tokens (``kw:``, ``ext:``,
    ``file:``, ``dir:``) contribute to the evidence used by the auto-demote
    decision and the validator's cross-check. In schema v3.3 this comes from
    the ``triggers`` field of ``RuleMetadata`` (populated from typed Keywords).
    Aligning to the same source ensures the renderer's auto-demote decision
    matches the validator's invariant by construction.
    """
    meta = rules_meta.get(rule)
    hits_kw: list[str] = []
    hits_other: dict[str, list[str]] = {k: [] for k in ("ext", "file", "dir")}
    if not meta:
        return {k: [] for k in TRIGGER_KINDS}

    # kw evidence: from typed kw: Keywords entries (via trigger_values('kw')).
    # Emit the LITERAL phrase found in the prompt, not the metadata token.
    seen_kw_lower: set[str] = set()
    for kw in meta.trigger_values("kw"):
        if not kw:
            continue
        literal = _find_literal_match(prompt, kw)
        if literal is not None:
            low = literal.lower()
            if low not in seen_kw_lower:
                hits_kw.append(literal)
                seen_kw_lower.add(low)

    # ext / file / dir evidence: from rule.trigger_values(kind).
    prompt_lower = prompt.lower()
    for kind in ("ext", "file", "dir"):
        for value in meta.trigger_values(kind):
            if value and value.lower() in prompt_lower:
                hits_other[kind].append(value.lower())

    # Deduplicate and sort; kw sorted case-insensitively for stable ordering.
    result: dict[str, list[str]] = {
        "kw": sorted(dict.fromkeys(hits_kw), key=str.lower),
    }
    for kind in ("ext", "file", "dir"):
        result[kind] = sorted(set(hits_other[kind]))
    return result


def _missing_triggers_for_rule(
    rule: str,
    rules_meta: dict[str, RuleMetadata],
) -> dict[str, tuple[str, ...]]:
    """Return the rule's declared typed-Keywords trigger tokens by kind.

    Used by the renderer to emit ``# missing: kw=...; ext=...; file=...; dir=...``
    hints under auto-demoted lines so the author can decide whether to extend the
    rule's ``Keywords:`` field or accept the demotion.
    """
    meta = rules_meta.get(rule)
    if meta is None:
        return dict.fromkeys(TRIGGER_KINDS, ())
    return {kind: meta.trigger_values(kind) for kind in TRIGGER_KINDS}


def _reason_from_evidence(rule_evidence: dict[str, list[str]]) -> str:
    """Render a ``kw: a, b; ext: .py`` style reason string for inline comments.

    Caller must only invoke this when at least one kind has non-empty
    evidence — the auto-demoted path emits its own reason text.
    """
    parts = []
    for kind in TRIGGER_KINDS:
        vals = rule_evidence.get(kind) or []
        if vals:
            parts.append(f"{kind}: {', '.join(vals)}")
    return "; ".join(parts)


def _short(rule_path: str) -> str:
    """Shorten ``rules/116-snowflake-cortex-search.md`` -> ``116``."""
    base = rule_path.removeprefix("rules/").removesuffix(".md")
    head = base.split("-", 1)[0]
    return head if head.isdigit() or head.isalnum() else base
