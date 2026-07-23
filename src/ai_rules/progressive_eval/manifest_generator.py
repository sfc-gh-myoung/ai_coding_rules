"""Progressive manifest generator.

Produces a lightweight manifest (rule name + 1-line summary + triggers) from
RULES_INDEX.md for injection into the progressive loading architecture.

The manifest is consumed by the lazy loader to determine WHEN to load each
rule's full content. Size constraint: ≤50 tokens per entry, ≤2000 tokens total.

When ``use_deterministic_matcher=True`` (the default), rule discovery is
delegated to the deterministic Python matcher (``ai_rules.rule_matcher``)
which reads YAML frontmatter directly from rule files.  Set
``use_deterministic_matcher=False`` to fall back to the RULES_INDEX.md path
(Step 2B fallback, retained for transition and regression testing).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Score threshold above which an entry appears in the RECOMMENDED tier.
RECOMMENDED_SCORE_THRESHOLD = 5
# Maximum entries shown in the RECOMMENDED section (prevents tier becoming noisy).
RECOMMENDED_MAX_ENTRIES = 5


@dataclass(frozen=True)
class ManifestEntry:
    """One rule's lightweight representation in the progressive manifest."""

    rule_path: str
    summary: str
    triggers_ext: tuple[str, ...]
    triggers_kw: tuple[str, ...]
    context_tier: str
    triggers_dir: tuple[str, ...] = ()
    triggers_file: tuple[str, ...] = ()
    rule_version: str = ""

    def to_compact(self) -> str:
        """Render as a single compact line for manifest injection."""
        parts = [self.rule_path]
        if self.rule_version:
            parts.append(self.rule_version)
        if self.triggers_ext:
            parts.append(f"ext={','.join(self.triggers_ext)}")
        if self.triggers_kw:
            # Show first 3 keywords only to stay within token budget
            kws = self.triggers_kw[:3]
            parts.append(f"kw={','.join(kws)}")
        parts.append(f"[{self.context_tier}]")
        return " | ".join(parts)


@dataclass(frozen=True)
class ProgressiveManifest:
    """The complete lightweight manifest for a user request."""

    entries: tuple[ManifestEntry, ...]
    schema_version: str = "progressive-manifest/v1"
    # Relevance scores keyed by rule_path; excluded from eq/hash (auxiliary data).
    scores: dict[str, int] = field(default_factory=dict, compare=False, hash=False)

    @property
    def token_estimate(self) -> int:
        """Rough token estimate of the rendered manifest."""
        return len(self.render()) // 4

    def render(self) -> str:
        """Render the manifest as injectable text."""
        lines = ["## Available Rules (load when needed)"]

        recommended = [
            e
            for e in self.entries
            if self.scores.get(e.rule_path, 0) >= RECOMMENDED_SCORE_THRESHOLD
        ][:RECOMMENDED_MAX_ENTRIES]
        recommended_paths = {e.rule_path for e in recommended}
        other = [e for e in self.entries if e.rule_path not in recommended_paths]

        if recommended:
            lines.append("**RECOMMENDED (strongest matches):**")
            for entry in recommended:
                lines.append(f"- {entry.to_compact()}")
                if entry.summary:
                    lines.append(f"  → {entry.summary}")

        if other:
            lines.append("Other potentially relevant:")
            for entry in other:
                lines.append(f"- {entry.to_compact()}")
                if entry.summary:
                    lines.append(f"  → {entry.summary}")

        return "\n".join(lines)


# Regex to parse one RULES_INDEX.md line
_INDEX_LINE_RE = re.compile(
    r"^(?P<filename>\S+\.md)\s+"
    r"tier=(?P<tier>\w+)\s*"
    r"(?:ver=(?P<ver>\S+)\s*)?"
    r"(?:ext=(?P<ext>\S+)\s*)?"
    r"(?:file=(?P<file>\S+)\s*)?"
    r"(?:dir=(?P<dir>\S+)\s*)?"
    r"kw=(?P<kw>.+)$"
)


def _score_keyword_match(kw: str, request_lower: str) -> int:
    """Score a single keyword against the (already lowercased) user request.

    Returns:
        10 if the full dehyphenated keyword phrase appears verbatim (compound only).
        5  if any 2 consecutive words of a compound keyword appear together.
        1  if any single word longer than 4 chars matches.
        0  otherwise.
    """
    kw_phrase = kw.replace("-", " ").replace("_", " ").lower()
    words = kw_phrase.split()

    if not words:
        return 0

    # Compound matching only for multi-word keywords
    if len(words) >= 2:
        if kw_phrase in request_lower:
            return 10
        for i in range(len(words) - 1):
            if " ".join(words[i : i + 2]) in request_lower:
                return 5

    # Single-word fallback: any word longer than 4 chars
    for w in words:
        if len(w) > 4 and w in request_lower:
            return 1

    return 0


def parse_rules_index(index_path: Path) -> list[ManifestEntry]:
    """Parse RULES_INDEX.md into ManifestEntry objects."""
    entries = []
    text = index_path.read_text(encoding="utf-8")
    in_code_fence = False

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        if (
            not line
            or line.startswith("#")
            or line.startswith(">")
            or line.startswith("<!--")
            or line.startswith("**")
        ):
            continue
        m = _INDEX_LINE_RE.match(line)
        if not m:
            if line.endswith(".md") or ".md " in line:
                logger.warning("Skipping malformed RULES_INDEX line: %r", line)
            continue

        filename = m.group("filename")
        tier = m.group("tier")
        ext_raw = m.group("ext") or ""
        kw_raw = m.group("kw") or ""
        dir_raw = m.group("dir") or ""
        file_raw = m.group("file") or ""

        exts = tuple(e.strip() for e in ext_raw.split(",") if e.strip()) if ext_raw else ()
        keywords = tuple(k.strip() for k in kw_raw.split() if k.strip())
        dirs = tuple(d.strip() for d in dir_raw.split() if d.strip()) if dir_raw else ()
        files = tuple(f.strip() for f in file_raw.split() if f.strip()) if file_raw else ()

        # Summary: first 3 keywords dehyphenated for richer matching surface
        summary = " ".join(kw.replace("-", " ") for kw in keywords[:3]) if keywords else ""

        ver_raw = m.group("ver") or ""
        rule_version = ver_raw if ver_raw != "-" else ""

        entries.append(
            ManifestEntry(
                rule_path=f"rules/{filename}",
                summary=summary,
                triggers_ext=exts,
                triggers_kw=keywords,
                context_tier=tier,
                triggers_dir=dirs,
                triggers_file=files,
                rule_version=rule_version,
            )
        )

    return entries


def _adapt_v2_to_progressive(
    resolved_rules: list,  # list[RuleFrontmatter]
    scores: dict[str, int],
) -> ProgressiveManifest:
    """Convert deterministic-matcher output to ProgressiveManifest.

    This is a thin translation layer; no eval harness schema changes are
    required.  The adapter maps ``RuleFrontmatter`` objects (from the
    dependency-resolved result) to ``ManifestEntry`` objects.
    """
    entries: list[ManifestEntry] = []
    for rule in resolved_rules:
        # Use first 3 kw entries as triggers_kw (matching old RULES_INDEX.md format)
        kw_triggers = tuple(rule.typed_kw[:3]) if rule.typed_kw else ()
        ext_triggers = tuple(rule.typed_ext) if rule.typed_ext else ()
        dir_triggers = tuple(rule.dir_patterns) if rule.dir_patterns else ()
        file_triggers = tuple(rule.file_patterns) if rule.file_patterns else ()
        summary = (
            rule.description[:80]
            if rule.description
            else (" ".join(k.replace("-", " ") for k in rule.typed_kw[:3]))
        )
        entries.append(
            ManifestEntry(
                rule_path=f"rules/{rule.filename}",
                summary=summary,
                triggers_ext=ext_triggers,
                triggers_kw=kw_triggers,
                context_tier=rule.context_tier,
                triggers_dir=dir_triggers,
                triggers_file=file_triggers,
                rule_version=rule.rule_version,
            )
        )

    score_map: dict[str, int] = {f"rules/{fn}": s for fn, s in scores.items()}
    return ProgressiveManifest(entries=tuple(entries), scores=score_map)


def _run_deterministic_matcher(
    rules_dir: Path,
    user_request: str,
    *,
    max_entries: int = 15,
    max_tokens: int = 2000,
) -> ProgressiveManifest:
    """Invoke the Python rule matcher and adapt result to ProgressiveManifest.

    Falls back gracefully on ImportError (module not installed yet).
    """
    try:
        from ai_rules.rule_matcher.dependency import resolve_dependencies
        from ai_rules.rule_matcher.frontmatter import load_rules_db
        from ai_rules.rule_matcher.matcher import FileContext, match_rules
    except ImportError as exc:
        logger.warning("rule_matcher not available (%s); falling back to RULES_INDEX path", exc)
        return ProgressiveManifest(entries=(), scores={})

    try:
        db = load_rules_db(rules_dir)
    except FileNotFoundError as exc:
        logger.warning("rules_dir not found (%s); falling back", exc)
        return ProgressiveManifest(entries=(), scores={})

    # Extract keywords from user_request: split on word boundaries, keep >= 3 chars
    keywords = [w for w in re.split(r"[^\w]+", user_request.lower()) if len(w) >= 3]

    # Also preserve compound terms that match common patterns (dotted filenames, hyphenated terms)
    compound_re = re.compile(r"[\w][\w.-]+[\w]")
    compounds = [
        m.group().lower() for m in compound_re.finditer(user_request) if len(m.group()) > 3
    ]
    # Add compounds that aren't already in keywords (e.g., "snowflake.yml", "cortex-search")
    keywords_set = set(keywords)
    for c in compounds:
        if c not in keywords_set and ("." in c or "-" in c):
            keywords.append(c)
            keywords_set.add(c)

    # Extract file context: extensions, filenames, and directory paths from the prompt
    ext_re = re.compile(r"\.\w{1,5}\b")
    file_re = re.compile(r"[\w][\w.-]*\.\w{1,5}")
    dir_re = re.compile(r"[\w][\w.-]*/")
    extensions = list({m.group().lower() for m in ext_re.finditer(user_request)})
    paths = list({m.group() for m in file_re.finditer(user_request)})
    # Directory references (e.g., "skills/", "src/") — add as paths for dir matching
    dirs = list({m.group() for m in dir_re.finditer(user_request)})
    paths.extend(f"{d}placeholder" for d in dirs)  # dirname() will strip "placeholder"
    file_context = FileContext(extensions=extensions, paths=paths)

    scored = match_rules(keywords, file_context, list(db.values()))
    score_map: dict[str, int] = {sr.rule.filename: sr.score for sr in scored}

    matched_filenames = {sr.rule.filename for sr in scored}
    resolved, warnings = resolve_dependencies(scored, db)
    if warnings:
        for w in warnings:
            logger.debug("Missing dep: %s → %s", w.get("rule"), w.get("missing_dep"))

    # Enforce max_entries via simple slice (deps are not capped)
    direct = [r for r in resolved if r.filename in matched_filenames][:max_entries]
    deps_only = [r for r in resolved if r.filename not in matched_filenames]
    capped_resolved = direct + deps_only

    return _adapt_v2_to_progressive(capped_resolved, score_map)


def generate_manifest(
    index_path: Path,
    *,
    user_request: str = "",
    max_entries: int = 15,
    max_tokens: int = 2000,
    use_deterministic_matcher: bool = True,
    rules_dir: Path | None = None,
) -> ProgressiveManifest:
    """Generate a progressive manifest for a user request.

    When ``use_deterministic_matcher=True`` (default), delegates to the Python
    rule matcher (reads YAML frontmatter directly from rule files).  When
    ``False``, uses the legacy RULES_INDEX.md path (Step 2B fallback).

    ``index_path`` is required in both modes:
    - Deterministic path: ``rules_dir`` defaults to ``index_path.parent``.
    - Legacy path: ``index_path`` is passed to ``parse_rules_index()``.
    """
    if use_deterministic_matcher:
        effective_rules_dir = rules_dir or index_path.parent
        manifest = _run_deterministic_matcher(
            effective_rules_dir,
            user_request,
            max_entries=max_entries,
            max_tokens=max_tokens,
        )
        # Fall back to legacy path if matcher returned empty (import error, etc.)
        if manifest.entries or not user_request:
            return manifest
        logger.debug("Deterministic matcher returned empty; falling back to RULES_INDEX path")

    # Legacy RULES_INDEX.md path (Step 2B fallback)
    all_entries = parse_rules_index(index_path)

    if user_request:
        request_lower = user_request.lower()
        scored: list[tuple[int, ManifestEntry]] = []

        for entry in all_entries:
            score = 0

            # Extension match (strongest signal)
            for ext in entry.triggers_ext:
                if ext.lstrip(".") in request_lower:
                    score += 10

            # Directory match
            for dir_trigger in entry.triggers_dir:
                if dir_trigger in request_lower:
                    score += 10

            # File match
            for file_trigger in entry.triggers_file:
                if file_trigger in request_lower:
                    score += 10

            # Keyword scoring — deduplicate before scoring
            seen_kws: set[str] = set()
            matched_count = 0
            for kw in entry.triggers_kw:
                kw_lower = kw.lower()
                if kw_lower in seen_kws:
                    continue
                seen_kws.add(kw_lower)
                kw_score = _score_keyword_match(kw, request_lower)
                if kw_score > 0:
                    score += kw_score
                    matched_count += 1

            # Multi-keyword boost
            if matched_count >= 2:
                score += 3

            if score > 0:
                scored.append((score, entry))

        # Deterministic order: descending score, then ascending rule_path as tie-break
        scored.sort(key=lambda t: (-t[0], t[1].rule_path))
        top_scored = scored[:max_entries]
        entries = [entry for _, entry in top_scored]
        scores: dict[str, int] = {entry.rule_path: s for s, entry in top_scored}
    else:
        # No request context: return Critical + High tier rules
        entries = [e for e in all_entries if e.context_tier in ("Critical", "High")][:max_entries]
        scores = {}

    # Enforce token budget
    manifest = ProgressiveManifest(entries=tuple(entries), scores=scores)
    while manifest.token_estimate > max_tokens and len(entries) > 1:
        entries.pop()
        scores = {e.rule_path: scores[e.rule_path] for e in entries if e.rule_path in scores}
        manifest = ProgressiveManifest(entries=tuple(entries), scores=scores)

    return manifest
