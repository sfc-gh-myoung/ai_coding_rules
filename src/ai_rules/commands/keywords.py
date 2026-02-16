"""Keyword generator command for ai-rules CLI.

This command analyzes rule files using TF-IDF and multi-signal extraction
to suggest 10-15 optimal keywords for the **Keywords:** metadata field.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

import typer
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from ai_rules._shared.console import (
    console,
    err_console,
    log_error,
    log_info,
    log_success,
    log_warning,
)

# Lazy import sklearn to avoid startup penalty
_TfidfVectorizer = None


def _get_tfidf_vectorizer():
    """Lazy import of TfidfVectorizer."""
    global _TfidfVectorizer
    if _TfidfVectorizer is None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        _TfidfVectorizer = TfidfVectorizer
    return _TfidfVectorizer


# Files to skip when building corpus
SKIP_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "AGENTS_V2.md",
    "RULES_INDEX.md",
}

# Domain-specific technology terms to prioritize
TECHNOLOGY_TERMS = {
    # Snowflake ecosystem
    "snowflake",
    "cortex",
    "streamlit",
    "snowpark",
    "spcs",
    "snowpipe",
    "snowsight",
    "snowcli",
    # AI/ML
    "aisql",
    "ai_complete",
    "ai_classify",
    "ai_extract",
    "ai_sentiment",
    "ai_embed",
    "embeddings",
    "rag",
    "llm",
    # Python ecosystem
    "python",
    "pytest",
    "ruff",
    "pydantic",
    "fastapi",
    "flask",
    "typer",
    "htmx",
    "pandas",
    "faker",
    # Data patterns
    "cdc",
    "etl",
    "elt",
    "rbac",
    "scd",
    "dmf",
    "udf",
    "udtf",
    "sproc",
    # Infrastructure
    "docker",
    "taskfile",
    "ci/cd",
    "git",
    "bash",
    "zsh",
    # Other
    "sql",
    "yaml",
    "json",
    "markdown",
    "typescript",
    "javascript",
    "react",
    "golang",
}

# Terms to exclude (too generic or common in all rules)
STOP_TERMS = {
    # Generic programming terms
    "data",
    "code",
    "file",
    "example",
    "function",
    "method",
    "class",
    "variable",
    "value",
    "type",
    "string",
    "number",
    "list",
    "dict",
    "object",
    "array",
    "return",
    "import",
    "module",
    "package",
    # Generic document terms
    "section",
    "rule",
    "rules",
    "pattern",
    "patterns",
    "best",
    "practice",
    "practices",
    "guide",
    "guidelines",
    "documentation",
    "reference",
    "references",
    "note",
    "notes",
    "tip",
    "tips",
    "warning",
    "error",
    "errors",
    # Common verbs
    "use",
    "using",
    "create",
    "creating",
    "add",
    "adding",
    "update",
    "updating",
    "delete",
    "deleting",
    "get",
    "set",
    "run",
    "running",
    "check",
    "checking",
    # Schema/metadata terms (present in all rules)
    "metadata",
    "schemaversion",
    "keywords",
    "tokenbudget",
    "contexttier",
    "depends",
    "purpose",
    "scope",
    "contract",
    "mandatory",
    "forbidden",
    "validation",
    # Common markdown terms
    "markdown",
    "heading",
    "table",
    "link",
    "image",
    # Common rule section terms (appear in all rules)
    "anti-pattern",
    "anti-patterns",
    "antipattern",
    "antipatterns",
    "mode",
    "core",
    "configuration",
    "setup",
    "overview",
    "introduction",
    "summary",
    "checklist",
    "output",
    "format",
    "examples",
    # Common English words that slip through
    "and",
    "the",
    "for",
    "with",
    "from",
    "that",
    "this",
    "when",
    "how",
    "why",
    "what",
    "where",
    "which",
    "should",
    "must",
    "can",
    "will",
    "may",
    "not",
    "all",
    "any",
    "each",
    "every",
    "both",
    "either",
    "neither",
    "only",
    "also",
    "just",
    "more",
    "most",
    "other",
    "same",
    "such",
    "than",
    "then",
    "very",
    "well",
    "even",
    "still",
    "already",
    "always",
    "never",
    "often",
    "usually",
    "sometimes",
}

# Compound terms to preserve (matched as phrases)
COMPOUND_TERMS = {
    "session state": "session_state",
    "semantic view": "semantic_view",
    "semantic views": "semantic_views",
    "dynamic table": "dynamic_table",
    "dynamic tables": "dynamic_tables",
    "cortex agent": "cortex_agent",
    "cortex agents": "cortex_agents",
    "cortex search": "cortex_search",
    "cortex analyst": "cortex_analyst",
    "feature store": "feature_store",
    "model registry": "model_registry",
    "data quality": "data_quality",
    "data loading": "data_loading",
    "data governance": "data_governance",
    "cost governance": "cost_governance",
    "resource monitor": "resource_monitor",
    "virtual warehouse": "virtual_warehouse",
    "compute pool": "compute_pool",
    "event table": "event_table",
    "planning instructions": "planning_instructions",
    "response instructions": "response_instructions",
    "type checking": "type_checking",
    "type hints": "type_hints",
    "dependency management": "dependency_management",
    "virtual environment": "virtual_environment",
    "error handling": "error_handling",
    "input validation": "input_validation",
    "access control": "access_control",
    "row access policy": "row_access_policy",
    "masking policy": "masking_policy",
    "object tagging": "object_tagging",
}


@dataclass
class KeywordCandidate:
    """A candidate keyword with scoring information."""

    term: str
    score: float
    source: str  # "tfidf", "header", "code_lang", "emphasis", "technology"

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


class KeywordExtractor:
    """Extract and rank keywords from rule files using TF-IDF and multi-signal analysis."""

    def __init__(self, corpus_dir: Path | None = None, debug: bool = False):
        """Initialize the keyword extractor.

        Args:
            corpus_dir: Directory containing rule files for TF-IDF corpus.
                       If None, TF-IDF scoring is disabled.
            debug: Enable debug output
        """
        self.corpus_dir = corpus_dir
        self.debug = debug
        self.vectorizer = None
        self.corpus_docs: list[str] = []
        self.corpus_paths: list[Path] = []

        if corpus_dir:
            self._build_corpus()

    def _debug(self, message: str) -> None:
        """Print debug message if debug mode enabled."""
        if self.debug:
            err_console.print(f"[dim][DEBUG] {message}[/dim]")

    def _build_corpus(self) -> None:
        """Build TF-IDF corpus from all rule files in corpus_dir."""
        if not self.corpus_dir or not self.corpus_dir.exists():
            return

        self._debug(f"Building corpus from {self.corpus_dir}")

        # Collect all rule files
        for filepath in sorted(self.corpus_dir.rglob("*.md")):
            if filepath.name in SKIP_FILES:
                continue
            # Skip examples directory (not rules, deployed separately)
            if "examples" in filepath.parts:
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
                # Preprocess for TF-IDF
                processed = self._preprocess_for_tfidf(content)
                self.corpus_docs.append(processed)
                self.corpus_paths.append(filepath)
            except Exception as e:
                self._debug(f"Error reading {filepath}: {e}")

        self._debug(f"Corpus contains {len(self.corpus_docs)} documents")

        if self.corpus_docs:
            # Build TF-IDF vectorizer
            TfidfVectorizer = _get_tfidf_vectorizer()
            # Use max_df=1.0 for small corpora to avoid ValueError
            # (max_df=0.8 with <2 docs causes issues)
            max_df = 1.0 if len(self.corpus_docs) < 3 else 0.8
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words="english",
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=1,
                max_df=max_df,  # Ignore terms in >80% of docs (when corpus large enough)
                token_pattern=r"(?u)\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b",
            )
            self.vectorizer.fit(self.corpus_docs)

    def _preprocess_for_tfidf(self, content: str) -> str:
        """Preprocess content for TF-IDF analysis.

        - Replace compound terms with underscored versions
        - Remove code blocks (they skew term frequency)
        - Remove URLs and file paths
        - Normalize whitespace
        """
        text = content

        # Replace compound terms
        for phrase, replacement in COMPOUND_TERMS.items():
            text = re.sub(re.escape(phrase), replacement, text, flags=re.IGNORECASE)

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`[^`]+`", " ", text)

        # Remove URLs
        text = re.sub(r"https?://\S+", " ", text)

        # Remove file paths
        text = re.sub(r"[\w/.-]+\.(py|md|sql|yml|yaml|toml|json|sh)", " ", text)

        # Normalize whitespace
        text = " ".join(text.split())

        return text

    def _extract_headers(self, content: str) -> list[KeywordCandidate]:
        """Extract keywords from H2 and H3 headers."""
        candidates = []

        # Match ## and ### headers
        header_pattern = r"^#{2,3}\s+(?:\d+\.\s+)?(.+)$"
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            header_text = match.group(1).strip()

            # Skip common section names
            if header_text.lower() in {
                "metadata",
                "purpose",
                "rule scope",
                "quick start tl;dr",
                "contract",
                "anti-patterns and common mistakes",
                "post-execution checklist",
                "validation",
                "output format examples",
                "references",
                "external documentation",
                "related rules",
            }:
                continue

            # Extract meaningful terms from header
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b", header_text)
            for word in words:
                if word.lower() not in STOP_TERMS:
                    candidates.append(KeywordCandidate(term=word, score=0.8, source="header"))

        return candidates

    def _extract_code_languages(self, content: str) -> list[KeywordCandidate]:
        """Extract programming language identifiers from code blocks."""
        candidates = []

        # Match ```language
        lang_pattern = r"```(\w+)"
        languages = set(re.findall(lang_pattern, content))

        # Map common language identifiers
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

        # Bold terms: **term** or __term__
        bold_pattern = r"\*\*([^*]+)\*\*|__([^_]+)__"
        for match in re.finditer(bold_pattern, content):
            term = match.group(1) or match.group(2)
            # Skip if it looks like a label (ends with :)
            if term.endswith(":"):
                continue
            # Extract individual words
            words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b", term)
            for word in words:
                if word.lower() not in STOP_TERMS:
                    candidates.append(KeywordCandidate(term=word, score=0.5, source="emphasis"))

        # Backtick terms: `term`
        backtick_pattern = r"`([^`]+)`"
        for match in re.finditer(backtick_pattern, content):
            term = match.group(1)
            # Skip if it looks like code/command
            if " " in term or "/" in term or "(" in term:
                continue
            # Skip file paths and extensions
            if "." in term and term.split(".")[-1] in {"py", "md", "sql", "yml", "yaml"}:
                continue
            if term.lower() not in STOP_TERMS and len(term) > 2:
                candidates.append(KeywordCandidate(term=term, score=0.4, source="emphasis"))

        return candidates

    def _extract_technology_terms(self, content: str) -> list[KeywordCandidate]:
        """Extract known technology terms from content."""
        candidates = []
        content_lower = content.lower()

        for tech in TECHNOLOGY_TERMS:
            # Check if term appears in content
            if re.search(rf"\b{re.escape(tech)}\b", content_lower):
                # Use original casing for display
                candidates.append(KeywordCandidate(term=tech, score=0.7, source="technology"))

        return candidates

    def _extract_tfidf_terms(
        self, content: str, file_path: Path, top_n: int = 20
    ) -> list[KeywordCandidate]:
        """Extract top TF-IDF terms for this document."""
        candidates = []

        if not self.vectorizer:
            return candidates

        # Find document index in corpus
        doc_idx = None
        for i, path in enumerate(self.corpus_paths):
            if path == file_path:
                doc_idx = i
                break

        if doc_idx is None:
            # Document not in corpus, transform it
            processed = self._preprocess_for_tfidf(content)
            tfidf_matrix = self.vectorizer.transform([processed])
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
        else:
            # Get pre-computed TF-IDF scores
            tfidf_matrix = self.vectorizer.transform(self.corpus_docs)
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[doc_idx]

        # Get top N terms by TF-IDF score
        top_indices = scores.argsort()[-top_n:][::-1]

        for idx in top_indices:
            term = feature_names[idx]
            score = scores[idx]
            if score > 0 and term.lower() not in STOP_TERMS:
                # Convert underscored compounds back to spaces
                display_term = term.replace("_", " ")
                candidates.append(
                    KeywordCandidate(term=display_term, score=float(score), source="tfidf")
                )

        return candidates

    def _extract_current_keywords(self, content: str) -> list[str]:
        """Extract current keywords from the **Keywords:** metadata field."""
        pattern = r"\*\*Keywords:\*\*\s*(.+)"
        match = re.search(pattern, content)
        if match:
            keywords_str = match.group(1).strip()
            return [k.strip() for k in keywords_str.split(",") if k.strip()]
        return []

    def extract_candidates(self, content: str, file_path: Path) -> list[KeywordCandidate]:
        """Extract all keyword candidates from content using multiple signals.

        Args:
            content: Rule file content
            file_path: Path to the rule file (for TF-IDF lookup)

        Returns:
            List of KeywordCandidate objects with scores
        """
        candidates = []

        # Extract from different sources
        candidates.extend(self._extract_headers(content))
        candidates.extend(self._extract_code_languages(content))
        candidates.extend(self._extract_emphasized_terms(content))
        candidates.extend(self._extract_technology_terms(content))
        candidates.extend(self._extract_tfidf_terms(content, file_path))

        return candidates

    def rank_keywords(self, candidates: list[KeywordCandidate], count: int = 12) -> list[str]:
        """Rank and deduplicate candidates to produce final keyword list.

        Args:
            candidates: List of KeywordCandidate objects
            count: Target number of keywords (10-15 range)

        Returns:
            List of keywords sorted by relevance
        """
        # Aggregate scores by normalized term
        term_scores: dict[str, float] = {}
        term_display: dict[str, str] = {}  # Track best display form

        for candidate in candidates:
            key = candidate.term.lower()

            # Skip stop terms
            if key in STOP_TERMS:
                continue

            # Aggregate score
            if key not in term_scores:
                term_scores[key] = 0.0
                term_display[key] = candidate.term
            term_scores[key] += candidate.score

            # Prefer display form with proper casing
            if candidate.term[0].isupper() and not term_display[key][0].isupper():
                term_display[key] = candidate.term

        # Sort by score descending
        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top N with proper display form
        result = []
        for key, _score in sorted_terms[:count]:
            result.append(term_display[key])

        return result

    def suggest_keywords(self, file_path: Path, count: int = 12) -> ExtractionResult:
        """Analyze a rule file and suggest keywords.

        Args:
            file_path: Path to rule file
            count: Target number of keywords

        Returns:
            ExtractionResult with current and suggested keywords
        """
        content = file_path.read_text(encoding="utf-8")

        # Extract current keywords
        current = self._extract_current_keywords(content)

        # Extract candidates
        candidates = self.extract_candidates(content, file_path)

        # Rank and select
        suggested = self.rank_keywords(candidates, count)

        return ExtractionResult(
            file_path=file_path,
            current_keywords=current,
            suggested_keywords=suggested,
            candidates=candidates,
        )


def format_keywords_line(keywords: list[str]) -> str:
    """Format keywords as a metadata line."""
    return f"**Keywords:** {', '.join(keywords)}"


def update_keywords_in_file(file_path: Path, new_keywords: list[str]) -> bool:
    """Update the Keywords field in a rule file.

    Args:
        file_path: Path to rule file
        new_keywords: New keywords to set

    Returns:
        True if updated, False if no change needed
    """
    content = file_path.read_text(encoding="utf-8")

    # Find and replace Keywords line
    pattern = r"(\*\*Keywords:\*\*\s*)(.+)"
    new_line = format_keywords_line(new_keywords)

    new_content, count = re.subn(pattern, new_line, content, count=1)

    if count == 0:
        log_warning(f"No **Keywords:** field found in {file_path}")
        return False

    if new_content == content:
        return False

    file_path.write_text(new_content, encoding="utf-8")
    return True


def print_diff_rich(result: ExtractionResult) -> None:
    """Print a rich diff between current and suggested keywords."""
    # Create side-by-side panels
    current_lines = []
    suggested_lines = []

    # Mark keywords with colors
    current_lower = {k.lower() for k in result.current_keywords}
    suggested_lower = {k.lower() for k in result.suggested_keywords}

    for kw in result.current_keywords:
        if kw.lower() in suggested_lower:
            current_lines.append(f"[dim]{kw}[/dim]")  # Kept
        else:
            current_lines.append(f"[red strikethrough]{kw}[/red strikethrough]")  # Removed

    for kw in result.suggested_keywords:
        if kw.lower() in current_lower:
            suggested_lines.append(f"[dim]{kw}[/dim]")  # Kept
        else:
            suggested_lines.append(f"[green bold]{kw}[/green bold]")  # Added

    current_panel = Panel(
        "\n".join(current_lines) if current_lines else "[dim]No keywords[/dim]",
        title=f"[bold]Current ({len(result.current_keywords)})[/bold]",
        border_style="red",
    )

    suggested_panel = Panel(
        "\n".join(suggested_lines) if suggested_lines else "[dim]No keywords[/dim]",
        title=f"[bold]Suggested ({len(result.suggested_keywords)})[/bold]",
        border_style="green",
    )

    console.print()
    console.print(f"[bold cyan]{result.file_path.name}[/bold cyan]")
    console.print(Columns([current_panel, suggested_panel], equal=True, expand=True))

    # Summary
    if result.removed:
        console.print(
            f"  [red]- Removed ({len(result.removed)}):[/red] {', '.join(sorted(result.removed))}"
        )
    if result.added:
        console.print(
            f"  [green]+ Added ({len(result.added)}):[/green] {', '.join(sorted(result.added))}"
        )
    if result.kept:
        console.print(f"  [dim]= Kept ({len(result.kept)}):[/dim] {', '.join(sorted(result.kept))}")


def print_suggestions_table(results: list[ExtractionResult]) -> None:
    """Print keyword suggestions as a Rich table."""
    table = Table(title="Keyword Suggestions", show_lines=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Current", style="yellow")
    table.add_column("Suggested", style="green")

    for result in results:
        table.add_row(
            result.file_path.name,
            ", ".join(result.current_keywords) if result.current_keywords else "[dim]None[/dim]",
            ", ".join(result.suggested_keywords)
            if result.suggested_keywords
            else "[dim]None[/dim]",
        )

    console.print(table)


def keywords(
    path: Annotated[
        Path,
        typer.Argument(
            help="Path to rule file or directory.",
        ),
    ],
    update: Annotated[
        bool,
        typer.Option(
            "--update",
            "-u",
            help="Update the Keywords field in-place.",
        ),
    ] = False,
    diff: Annotated[
        bool,
        typer.Option(
            "--diff",
            "-d",
            help="Show diff between current and suggested keywords.",
        ),
    ] = False,
    corpus: Annotated[
        bool,
        typer.Option(
            "--corpus",
            "-c",
            help="Build TF-IDF corpus from rules directory for better scoring.",
        ),
    ] = False,
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Target number of keywords.",
        ),
    ] = 12,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug output.",
        ),
    ] = False,
) -> None:
    """Generate semantically relevant keywords for AI coding rule files.

    Uses TF-IDF vectorization and multi-signal extraction to suggest
    optimal keywords for the **Keywords:** metadata field.

    Examples:
        # Suggest keywords for a single file
        ai-rules keywords rules/100-snowflake-core.md

        # Update the Keywords field in-place
        ai-rules keywords rules/100-snowflake-core.md --update

        # Show diff between current and suggested keywords
        ai-rules keywords rules/100-snowflake-core.md --diff

        # Build corpus from all rules for better TF-IDF scoring
        ai-rules keywords rules/100-snowflake-core.md --corpus

        # Analyze all rules in a directory
        ai-rules keywords rules/
    """
    # Validate path
    if not path.exists():
        log_error(f"Path does not exist: {path}")
        raise typer.Exit(1)

    # Determine corpus directory
    corpus_dir = None
    if corpus:
        if path.is_dir():
            corpus_dir = path
        else:
            # Use parent directory if it's named 'rules'
            if path.parent.name == "rules":
                corpus_dir = path.parent
            else:
                # Try to find rules/ in common locations
                for parent in [path.parent, path.parent.parent]:
                    rules_dir = parent / "rules"
                    if rules_dir.exists():
                        corpus_dir = rules_dir
                        break

        if corpus_dir:
            log_info(f"Building TF-IDF corpus from {corpus_dir}")

    # Initialize extractor
    try:
        extractor = KeywordExtractor(corpus_dir=corpus_dir, debug=debug)
    except ImportError as e:
        log_error(f"Missing dependency: {e}")
        log_info("Install scikit-learn: pip install scikit-learn")
        raise typer.Exit(1) from None

    # Process file(s)
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.glob("*.md"))
        files = [f for f in files if f.name not in SKIP_FILES]

    if not files:
        log_error(f"No rule files found in {path}")
        raise typer.Exit(1)

    results: list[ExtractionResult] = []
    updated_count = 0
    unchanged_count = 0

    for file_path in files:
        try:
            result = extractor.suggest_keywords(file_path, count=count)
            results.append(result)

            if diff:
                print_diff_rich(result)
            elif update:
                if update_keywords_in_file(file_path, result.suggested_keywords):
                    log_success(f"Updated: {file_path.name}")
                    updated_count += 1
                else:
                    log_info(f"No change: {file_path.name}")
                    unchanged_count += 1

        except Exception as e:
            log_error(f"Error processing {file_path}: {e}")
            if debug:
                raise

    # Print summary for non-diff, non-update mode
    if not diff and not update:
        print_suggestions_table(results)

    # Print final summary for update mode
    if update:
        console.print()
        if updated_count > 0:
            log_success(f"Updated {updated_count} file(s)")
        if unchanged_count > 0:
            log_info(f"Unchanged: {unchanged_count} file(s)")
