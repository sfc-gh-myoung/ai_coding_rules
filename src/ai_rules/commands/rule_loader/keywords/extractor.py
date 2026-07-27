"""Keyword extraction and ranking logic."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ai_rules._shared.console import err_console, log_warning
from ai_rules.commands.rule_loader.keywords.cache import (
    _content_hash,
    _get_cached_keywords,
    _set_cached_keywords,
)
from ai_rules.commands.rule_loader.keywords.client import CortexClient
from ai_rules.commands.rule_loader.keywords.collision import (
    apply_collision_postfilter,
    build_keyword_collision_map,
)
from ai_rules.commands.rule_loader.keywords.formatting import _parse_frontmatter_block
from ai_rules.commands.rule_loader.keywords.stoplist import (
    STOP_TERMS,
    TECHNOLOGY_TERMS,
    load_keyword_stoplist,
    load_keyword_stoplist_overrides,
)


@dataclass
class KeywordCandidate:
    """A candidate keyword with scoring information."""

    term: str
    score: float
    source: str  # "llm", "header", "code_lang", "emphasis", "technology"

    def __hash__(self) -> int:
        """Hash by normalized term for deduplication."""
        return hash(self.term.lower())

    def __eq__(self, other: object) -> bool:
        """Equal if terms match (case-insensitive)."""
        if not isinstance(other, KeywordCandidate):
            return False
        return self.term.lower() == other.term.lower()


@dataclass
class ExtractionResult:
    """Result of keyword extraction for a rule file."""

    file_path: Path
    current_keywords: list[str] = field(default_factory=list)
    suggested_keywords: list[str] = field(default_factory=list)
    candidates: list[KeywordCandidate] = field(default_factory=list)
    # Per-keyword rationale captured from the LLM response.
    rationale_map: dict[str, str] = field(default_factory=dict)

    @property
    def added(self) -> set[str]:
        """Keywords in suggested but not in current."""
        current_lower = {k.lower() for k in self.current_keywords}
        return {k for k in self.suggested_keywords if k.lower() not in current_lower}

    @property
    def removed(self) -> set[str]:
        """Keywords in current but not in suggested."""
        suggested_lower = {k.lower() for k in self.suggested_keywords}
        return {k for k in self.current_keywords if k.lower() not in suggested_lower}

    @property
    def kept(self) -> set[str]:
        """Keywords in both current and suggested."""
        suggested_lower = {k.lower() for k in self.suggested_keywords}
        return {k for k in self.current_keywords if k.lower() in suggested_lower}


def _deduplicate_across_rules(
    results: list[ExtractionResult],
    max_overlap: int = 2,
) -> None:
    """Remove over-shared keywords from rules where they're least relevant.

    Mutates ``suggested_keywords`` in place.
    """
    keyword_owners: dict[str, list[tuple[ExtractionResult, int]]] = {}
    for result in results:
        content = result.file_path.read_text(encoding="utf-8").lower()
        for kw in result.suggested_keywords:
            key = kw.lower()
            body_count = content.count(key)
            keyword_owners.setdefault(key, []).append((result, body_count))

    for key, owners in keyword_owners.items():
        if len(owners) <= max_overlap:
            continue
        owners.sort(key=lambda x: x[1], reverse=True)
        keep_results = {id(r) for r, _ in owners[:max_overlap]}
        for result, _ in owners[max_overlap:]:
            if id(result) not in keep_results:
                result.suggested_keywords = [
                    kw for kw in result.suggested_keywords if kw.lower() != key
                ]


class KeywordExtractor:
    """Extract and rank keywords from rule files using Cortex LLM and heuristic signals."""

    def __init__(
        self,
        *,
        debug: bool = False,
        connection_name: str = "default",
        model: str = "claude-sonnet-4-5",
    ) -> None:
        """Initialize the keyword extractor.

        Args:
            debug: Enable debug output.
            connection_name: Snowflake connection name for Cortex API calls.
            model: LLM model name (default: ``claude-sonnet-4-5``).
        """
        self.debug = debug
        self.connection_name = connection_name
        self.model = model

    def _debug(self, message: str) -> None:
        if self.debug:
            err_console.print(f"[dim][DEBUG] {message}[/dim]")

    def _extract_headers(self, content: str) -> list[KeywordCandidate]:
        """Extract keywords from H2 and H3 headers."""
        candidates = []
        header_pattern = r"^#{2,3}\s+(?:\d+\.\s+)?(.+)$"
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            header_text = match.group(1).strip()

            if header_text.lower() in {
                "metadata",
                "purpose",
                "scope",
                "rule scope",
                "quick start",
                "quick start tl;dr",
                "contract",
                "inputs and prerequisites",
                "mandatory",
                "forbidden",
                "execution steps",
                "output format",
                "validation",
                "post-execution checklist",
                "anti-patterns and common mistakes",
                "output format examples",
                "references",
                "external documentation",
                "related rules",
                "dependencies",
                "design principles",
                "key principles",
                "implementation details",
                "performance optimization",
                "performance considerations",
                "performance and optimization",
                "troubleshooting",
                "validation checklist",
                "rules loaded",
                "unreleased",
                "fixed",
                "added",
                "changed",
                "deprecated",
                "quantification standards",
                "related examples",
            }:
                continue

            clean_header = re.sub(r"[*_`]", "", header_text).strip()
            clean_header = re.sub(
                r"^(?:Step \d+|Scenario \d+|Anti-Pattern \d+|Priority \d+|Phase \d+|Option \d+|Example \d+)\s*[:—–-]\s*",
                "",
                clean_header,
            ).strip()
            clean_header = re.sub(r"\s*\([^)]*\)\s*$", "", clean_header).strip()
            clean_header = re.sub(r"^Error \d+\s*:\s*", "", clean_header).strip()
            clean_header = clean_header.strip(":").strip()
            if clean_header.endswith("?"):
                continue
            if re.search(r"[≤≥<>=~]|^---$", clean_header):
                continue
            if len(clean_header) > 45:
                continue
            if not clean_header:
                continue

            header_words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b", clean_header)
            non_stop_words = [w for w in header_words if w.lower() not in STOP_TERMS]

            if len(non_stop_words) >= 2:
                candidates.append(KeywordCandidate(term=clean_header, score=0.9, source="header"))
            elif len(non_stop_words) == 1:
                word = non_stop_words[0]
                if word[0].isupper() or word.lower() in TECHNOLOGY_TERMS:
                    candidates.append(KeywordCandidate(term=word, score=0.8, source="header"))

        return candidates

    def _extract_code_languages(self, content: str) -> list[KeywordCandidate]:
        """Extract programming language identifiers from code blocks."""
        candidates = []
        lang_pattern = r"```(\w+)"
        languages = set(re.findall(lang_pattern, content))

        lang_map = {
            "python": "Python",
            "py": "Python",
            "sql": "SQL",
            "bash": "Bash",
            "sh": "shell",
            "shell": "shell",
            "zsh": "Zsh",
            "javascript": "JavaScript",
            "js": "JavaScript",
            "typescript": "TypeScript",
            "ts": "TypeScript",
            "yaml": "YAML",
            "yml": "YAML",
            "json": "JSON",
            "toml": "TOML",
            "markdown": "Markdown",
            "md": "Markdown",
            "go": "Go",
            "golang": "Go",
            "dockerfile": "Docker",
            "html": "HTML",
            "css": "CSS",
        }

        for lang in languages:
            normalized = lang_map.get(lang.lower(), lang)
            if normalized.lower() not in STOP_TERMS:
                candidates.append(KeywordCandidate(term=normalized, score=0.6, source="code_lang"))

        return candidates

    def _extract_emphasized_terms(self, content: str) -> list[KeywordCandidate]:
        """Extract terms from bold and backtick emphasis."""
        candidates = []

        bold_pattern = r"\*\*([^*]+)\*\*|__([^_]+)__"
        for match in re.finditer(bold_pattern, content):
            term = match.group(1) or match.group(2)
            if term.endswith(":"):
                continue
            if term.lower() in {
                "schemaversion",
                "ruleversion",
                "lastupdated",
                "keywords",
                "tokenbudget",
                "contexttier",
                "depends",
                "what this rule covers",
                "when to load this rule",
                "must load first",
                "note",
                "critical",
                "always",
                "never",
            }:
                continue
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b", term)
            non_stop_words = [w for w in words if w.lower() not in STOP_TERMS]
            if len(non_stop_words) >= 2 and len(term) <= 50:
                candidates.append(KeywordCandidate(term=term, score=0.6, source="emphasis"))
            elif len(non_stop_words) == 1:
                word = non_stop_words[0]
                if word[0].isupper() or word.lower() in TECHNOLOGY_TERMS:
                    candidates.append(KeywordCandidate(term=word, score=0.5, source="emphasis"))

        backtick_pattern = r"`([^`]+)`"
        for match in re.finditer(backtick_pattern, content):
            term = match.group(1)
            if "\n" in term or "*" in term:
                continue
            if " " in term or "/" in term or "(" in term:
                continue
            if term.startswith("-"):
                continue
            if "." in term and term.split(".")[-1] in {
                "py",
                "md",
                "sql",
                "yml",
                "yaml",
                "toml",
                "json",
            }:
                continue
            if term.lower() not in STOP_TERMS and len(term) > 2:
                candidates.append(KeywordCandidate(term=term, score=0.4, source="emphasis"))

        return candidates

    def _extract_technology_terms(self, content: str) -> list[KeywordCandidate]:
        """Extract known technology terms from content."""
        candidates = []
        content_lower = content.lower()
        for tech in TECHNOLOGY_TERMS:
            if re.search(rf"\b{re.escape(tech)}\b", content_lower):
                candidates.append(KeywordCandidate(term=tech, score=0.7, source="technology"))
        return candidates

    def _extract_current_keywords(self, content: str) -> list[str]:
        """Extract current keywords (dual-parse: v3.5 YAML frontmatter → inline fallback)."""
        fm = _parse_frontmatter_block(content)
        if fm is not None:
            kw_val = fm.get("keywords")
            if isinstance(kw_val, list):
                return [str(k).strip() for k in kw_val if str(k).strip()]
            if isinstance(kw_val, str):
                return [k.strip() for k in kw_val.split(",") if k.strip()]
        pattern = r"\*\*Keywords:\*\*\s*(.+)"
        match = re.search(pattern, content)
        if match:
            keywords_str = match.group(1).strip()
            return [k.strip() for k in keywords_str.split(",") if k.strip()]
        return []

    def _collect_heuristic_candidates(self, content: str) -> list[KeywordCandidate]:
        """Collect keyword candidates from all heuristic signals."""
        candidates = []
        candidates.extend(self._extract_headers(content))
        candidates.extend(self._extract_code_languages(content))
        candidates.extend(self._extract_emphasized_terms(content))
        candidates.extend(self._extract_technology_terms(content))
        return candidates

    def _rank_heuristic_keywords(
        self, candidates: list[KeywordCandidate], count: int = 12
    ) -> list[str]:
        """Rank and deduplicate heuristic candidates (fallback when no API)."""
        term_scores: dict[str, float] = {}
        term_display: dict[str, str] = {}

        for candidate in candidates:
            key = candidate.term.lower()
            if key in STOP_TERMS:
                continue
            if key not in term_scores:
                term_scores[key] = 0.0
                term_display[key] = candidate.term
            term_scores[key] += candidate.score
            if candidate.term[0].isupper() and not term_display[key][0].isupper():
                term_display[key] = candidate.term

        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        return [term_display[key] for key, _score in sorted_terms[:count]]

    @staticmethod
    def _merge_llm_with_heuristics(
        llm_keywords: list[str],
        heuristic_candidates: list[KeywordCandidate],
        count: int,
        rule_filename: str | None = None,
    ) -> list[str]:
        """Merge LLM keywords with high-confidence heuristic candidates.

        LLM output is the primary set; high-confidence heuristic terms
        (technology matches, code languages) that the LLM missed are appended
        up to the count limit.
        """
        result = list(llm_keywords)
        result_lower = {k.lower() for k in result}

        stoplist = load_keyword_stoplist()
        overrides_map = load_keyword_stoplist_overrides()
        permitted_overrides = overrides_map.get(rule_filename or "", set())

        high_confidence_sources = {"technology", "code_lang"}
        supplements: dict[str, str] = {}
        for c in heuristic_candidates:
            if c.source in high_confidence_sources and c.term.lower() not in result_lower:
                key = c.term.lower()
                if key in STOP_TERMS:
                    continue
                if key in stoplist and key not in permitted_overrides:
                    continue
                if key not in supplements:
                    supplements[key] = c.term

        for term in sorted(supplements.values()):
            if len(result) >= count:
                break
            result.append(term)

        return result

    def suggest_keywords(
        self,
        file_path: Path,
        count: int = 15,
        *,
        use_api: bool = True,
        cache: dict | None = None,
        force: bool = False,
        max_collision: int | None = None,
        collision_map: dict[str, list[str]] | None = None,
    ) -> ExtractionResult:
        """Analyze a rule file and suggest keywords.

        Args:
            file_path: Path to rule file
            count: Maximum number of keywords
            use_api: Whether to use Cortex API (False = heuristic-only fallback)
            cache: Optional keyword cache dict
            force: Bypass cache even if hash matches
            max_collision: When set, apply the T6 collision post-filter.
            collision_map: Pre-computed collision map.

        Returns:
            ExtractionResult with current and suggested keywords
        """
        content = file_path.read_text(encoding="utf-8")
        current = self._extract_current_keywords(content)
        heuristic_candidates = self._collect_heuristic_candidates(content)

        # Check cache
        if cache is not None and not force:
            file_key = str(file_path.resolve())
            ch = _content_hash(content)
            cached = _get_cached_keywords(cache, file_key, ch)
            if cached is not None:
                self._debug(f"Cache hit for {file_path.name}")
                return ExtractionResult(
                    file_path=file_path,
                    current_keywords=current,
                    suggested_keywords=cached,
                    candidates=heuristic_candidates,
                )

        # Try Cortex API
        suggested: list[str] = []
        rationale_map: dict[str, str] = {}
        if use_api:
            try:
                client = CortexClient(connection_name=self.connection_name, model=self.model)
                parse_result = client.generate_keywords(content, count=count, debug=self.debug)
                suggested = parse_result.keywords
                rationale_map = parse_result.rationale_map
            except RuntimeError as e:
                self._debug(f"Cortex API failed, falling back to heuristic: {e}")
                log_warning(f"Cortex API unavailable, using heuristic fallback: {e}")

        # Snapshot LLM rationale candidates for collision postfilter substitution
        rationale_pool = list(rationale_map.keys())

        # Fallback to heuristic ranking if API didn't produce results
        if not suggested:
            suggested = self._rank_heuristic_keywords(heuristic_candidates, count)
        else:
            suggested = self._merge_llm_with_heuristics(
                suggested, heuristic_candidates, count, rule_filename=file_path.name
            )

        # Filter stop terms from LLM output as post-processing
        suggested = [k for k in suggested if k.lower() not in STOP_TERMS][:count]

        # T6 collision post-filter
        if max_collision is not None:
            resolved_map = (
                collision_map if collision_map is not None else build_keyword_collision_map()
            )
            suggested = apply_collision_postfilter(
                suggested,
                rationale_pool,
                resolved_map,
                max_collision,
                current_rule_filename=file_path.name,
            )[:count]

        # Update cache
        if cache is not None:
            file_key = str(file_path.resolve())
            ch = _content_hash(content)
            _set_cached_keywords(cache, file_key, ch, suggested)

        return ExtractionResult(
            file_path=file_path,
            current_keywords=current,
            suggested_keywords=suggested,
            candidates=heuristic_candidates,
            rationale_map={kw: rationale_map.get(kw, "") for kw in suggested},
        )
