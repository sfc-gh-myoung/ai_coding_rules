"""Fixture loading and the trigger-evidence invariant validator.

A fixture is a YAML file under ``fixtures/rule_loader_eval/`` describing one
prompt the evaluator sends to the agent under test. The loader enforces:

1. Schema-level shape (required keys, types).
2. The trigger-evidence invariant (Section 3.1 of the plan):
   - Every ``ext:``, ``file:``, and ``dir:`` entry declared in
     ``trigger_evidence`` MUST appear literally in ``prompt``.
   - Every required rule's declared typed ``Keywords`` trigger of kind
     ``ext:``/``file:``/``dir:`` MUST be matched by a literal token in
     ``prompt`` — even if the fixture author forgot to declare evidence.
   - ``kw`` evidence is checked case-insensitively at word boundaries.

Failures raise :class:`FixtureValidationError` and are surfaced by the CLI
as exit code 4 (fixture/schema/trigger-evidence error).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ai_rules.rule_loader_eval.rules_meta import RuleMetadata

REQUIRED_TOP_KEYS = ("schema_version", "updated", "id", "prompt", "expected", "trigger_evidence")
ALLOWED_VARIANTS = {"simple", "complex"}
ALLOWED_TRIGGER_KINDS = {"kw", "ext", "file", "dir"}
SUPPORTED_SCHEMA_VERSION = 3
SUPPORTED_SCHEMA_VERSIONS = (2, 3)

# ISO 8601 with explicit offset (+HH:MM, -HH:MM, or Z).
# Example: 2026-05-16T14:30:00-07:00 or 2026-05-16T21:30:00Z
_UPDATED_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class FixtureValidationError(Exception):
    """Raised when a fixture fails schema or trigger-evidence validation."""


@dataclass(frozen=True)
class TriggerEvidence:
    """Literal tokens that must appear in the prompt."""

    kw: tuple[str, ...] = ()
    ext: tuple[str, ...] = ()
    file: tuple[str, ...] = ()
    dir: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        """Return True if no evidence tokens are declared."""
        return not (self.kw or self.ext or self.file or self.dir)


@dataclass(frozen=True)
class Fixture:
    """A loaded, schema-validated fixture."""

    path: Path
    schema_version: int
    updated: str
    id: str
    description: str
    variant: str
    prompt: str
    required: tuple[str, ...]
    dependencies: tuple[str, ...]
    forbidden: tuple[str, ...]
    optional: tuple[str, ...]
    trigger_evidence: TriggerEvidence
    notes: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


def _kw_pattern(token: str) -> re.Pattern[str]:
    """Kw pattern."""
    return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", re.IGNORECASE)


def _ext_pattern(ext: str) -> re.Pattern[str]:
    """Ext pattern."""
    if not ext.startswith("."):
        ext = f".{ext}"
    # Note: no lookbehind on the dot — filenames have alphanumeric chars before
    # the extension by definition. The lookahead ensures we don't match e.g.
    # ``.python`` when looking for ``.py``.
    return re.compile(rf"\{ext}(?![A-Za-z0-9_])")


def _file_pattern(name: str) -> re.Pattern[str]:
    """File pattern."""
    return re.compile(rf"(?<![A-Za-z0-9_/]){re.escape(name)}(?![A-Za-z0-9_])")


def _dir_pattern(path: str) -> re.Pattern[str]:
    """Dir pattern."""
    normalized = path.rstrip("/")
    return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(normalized)}(?![A-Za-z0-9_])")


def _coerce_str_tuple(value: Any, *, key: str, fixture_id: str) -> tuple[str, ...]:
    """Coerce str tuple."""
    if value is None:
        return ()
    if isinstance(value, tuple):
        value = list(value)
    if not isinstance(value, list):
        raise FixtureValidationError(
            f"[{fixture_id}] {key} must be a list, got {type(value).__name__}"
        )
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise FixtureValidationError(
                f"[{fixture_id}] {key} entries must be strings, got {type(item).__name__}"
            )
        out.append(item)
    return tuple(out)


def _parse_trigger_evidence(raw: Any, fixture_id: str) -> TriggerEvidence:
    """Parse trigger evidence."""
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise FixtureValidationError(
            f"[{fixture_id}] trigger_evidence must be a mapping, got {type(raw).__name__}"
        )
    unknown = set(raw) - ALLOWED_TRIGGER_KINDS
    if unknown:
        raise FixtureValidationError(
            f"[{fixture_id}] trigger_evidence has unknown kinds: {sorted(unknown)}"
        )
    return TriggerEvidence(
        kw=_coerce_str_tuple(raw.get("kw", ()), key="trigger_evidence.kw", fixture_id=fixture_id),
        ext=_coerce_str_tuple(
            raw.get("ext", ()), key="trigger_evidence.ext", fixture_id=fixture_id
        ),
        file=_coerce_str_tuple(
            raw.get("file", ()), key="trigger_evidence.file", fixture_id=fixture_id
        ),
        dir=_coerce_str_tuple(
            raw.get("dir", ()), key="trigger_evidence.dir", fixture_id=fixture_id
        ),
    )


def _parse_fixture(path: Path, raw: Any) -> Fixture:
    """Parse fixture."""
    if not isinstance(raw, dict):
        raise FixtureValidationError(f"{path}: top-level YAML must be a mapping")
    fixture_id = raw.get("id", path.stem)
    if not isinstance(fixture_id, str) or not fixture_id:
        raise FixtureValidationError(f"{path}: id must be a non-empty string")

    missing = [k for k in REQUIRED_TOP_KEYS if k not in raw]
    if missing:
        raise FixtureValidationError(f"[{fixture_id}] missing required keys: {missing}")

    schema_version = raw["schema_version"]
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise FixtureValidationError(
            f"[{fixture_id}] unsupported schema_version {schema_version!r}; "
            f"expected one of {SUPPORTED_SCHEMA_VERSIONS}"
        )

    updated = raw["updated"]
    # PyYAML auto-parses ISO 8601 timestamps as datetime objects under the
    # default safe loader. Coerce back to a canonical isoformat string with
    # explicit offset so the regex check below works uniformly regardless of
    # whether the value was emitted quoted or bare in the source YAML.
    if isinstance(updated, datetime):
        if updated.tzinfo is None:
            raise FixtureValidationError(
                f"[{fixture_id}] updated value {updated.isoformat()!r} is missing a "
                f"timezone offset (use 'YYYY-MM-DDTHH:MM:SS+HH:MM' or 'YYYY-MM-DDTHH:MM:SSZ')"
            )
        updated = updated.replace(microsecond=0).isoformat()
    if not isinstance(updated, str) or not updated.strip():
        raise FixtureValidationError(
            f"[{fixture_id}] updated must be a non-empty ISO 8601 timestamp string with offset "
            f"(e.g. '2026-05-16T14:30:00-07:00')"
        )
    if not _UPDATED_PATTERN.match(updated.strip()):
        raise FixtureValidationError(
            f"[{fixture_id}] updated value {updated!r} is not a valid ISO 8601 timestamp with "
            f"offset (expected form: 'YYYY-MM-DDTHH:MM:SS+HH:MM' or 'YYYY-MM-DDTHH:MM:SSZ')"
        )
    updated = updated.strip()

    variant = raw.get("variant", "simple")
    if variant not in ALLOWED_VARIANTS:
        raise FixtureValidationError(
            f"[{fixture_id}] variant must be one of {sorted(ALLOWED_VARIANTS)}"
        )

    prompt = raw["prompt"]
    if not isinstance(prompt, str) or not prompt.strip():
        raise FixtureValidationError(f"[{fixture_id}] prompt must be a non-empty string")

    expected = raw["expected"]
    if not isinstance(expected, dict):
        raise FixtureValidationError(f"[{fixture_id}] expected must be a mapping")

    required = _coerce_str_tuple(
        expected.get("required", ()), key="expected.required", fixture_id=fixture_id
    )
    # Empty required sets are valid for no-match prompts under the retired-foundation contract.
    forbidden = _coerce_str_tuple(
        expected.get("forbidden", ()), key="expected.forbidden", fixture_id=fixture_id
    )
    optional = _coerce_str_tuple(
        expected.get("optional", ()), key="expected.optional", fixture_id=fixture_id
    )
    dependencies = _coerce_str_tuple(
        expected.get("dependencies", ()), key="expected.dependencies", fixture_id=fixture_id
    )

    overlap_rf = set(required) & set(forbidden)
    if overlap_rf:
        raise FixtureValidationError(
            f"[{fixture_id}] same rule(s) listed as both required and forbidden: {sorted(overlap_rf)}"
        )
    overlap_df = set(dependencies) & set(forbidden)
    if overlap_df:
        raise FixtureValidationError(
            f"[{fixture_id}] same rule(s) listed as both dependencies and forbidden: {sorted(overlap_df)}"
        )
    overlap_rd = set(required) & set(dependencies)
    if overlap_rd:
        raise FixtureValidationError(
            f"[{fixture_id}] same rule(s) listed as both required and dependencies: {sorted(overlap_rd)}"
        )

    trigger_evidence = _parse_trigger_evidence(raw["trigger_evidence"], fixture_id)

    description = raw.get("description") or ""
    notes = raw.get("notes", "") or ""
    if not isinstance(notes, str):
        raise FixtureValidationError(f"[{fixture_id}] notes must be a string")

    return Fixture(
        path=path,
        schema_version=schema_version,
        updated=updated,
        id=fixture_id,
        description=description,
        variant=variant,
        prompt=prompt,
        required=required,
        dependencies=dependencies,
        forbidden=forbidden,
        optional=optional,
        trigger_evidence=trigger_evidence,
        notes=notes,
        raw=raw,
    )


def _check_evidence_in_prompt(fixture: Fixture) -> list[str]:
    """Return a list of error messages for missing literal evidence in the prompt."""
    errors: list[str] = []
    prompt = fixture.prompt

    for token in fixture.trigger_evidence.kw:
        if not _kw_pattern(token).search(prompt):
            errors.append(f"kw evidence {token!r} not found in prompt")
    for ext in fixture.trigger_evidence.ext:
        if not _ext_pattern(ext).search(prompt):
            errors.append(
                f"ext evidence {ext!r} not found in prompt (need a filename ending with this extension)"
            )
    for name in fixture.trigger_evidence.file:
        if not _file_pattern(name).search(prompt):
            errors.append(f"file evidence {name!r} not found in prompt")
    for path in fixture.trigger_evidence.dir:
        if not _dir_pattern(path).search(prompt):
            errors.append(f"dir evidence {path!r} not found in prompt")
    return errors


def _cross_check_required_rules(fixture: Fixture, rules: dict[str, RuleMetadata]) -> list[str]:
    """Cross-check required rules' typed-Keywords triggers against fixture evidence/prompt.

    For each ``ext:``/``file:``/``dir:`` trigger declared by a required rule, the
    fixture's ``prompt`` must contain a literal token that satisfies it. This
    catches the ``python-file-edit`` / ``bash-script`` class of bug even when
    the author forgets to declare ``trigger_evidence``.

    ``kw`` triggers are not strictly checked here (kw matching is handled by
    rule-loader activity matching), but at least one literal kw
    or any other trigger must satisfy at least one required rule, otherwise
    the fixture is unverifiable.
    """
    errors: list[str] = []
    unverifiable_required: list[str] = []

    if not rules:
        # No metadata available to cross-check against; only the prompt-evidence
        # check (already run by the caller) applies.
        return errors

    for rel in fixture.required:
        meta = rules.get(rel)
        if meta is None:
            errors.append(f"required rule {rel!r} not found under rules/")
            continue

        # Hard-check ext/file/dir
        rule_satisfied = False
        for ext in meta.trigger_values("ext"):
            if _ext_pattern(ext).search(fixture.prompt):
                rule_satisfied = True
                if ext.lstrip(".") not in {e.lstrip(".") for e in fixture.trigger_evidence.ext}:
                    errors.append(
                        f"required rule {rel} declares Keywords trigger ext:{ext} but "
                        f"fixture trigger_evidence.ext is missing it"
                    )
        for name in meta.trigger_values("file"):
            if _file_pattern(name).search(fixture.prompt):
                rule_satisfied = True
                if name not in fixture.trigger_evidence.file:
                    errors.append(
                        f"required rule {rel} declares Keywords trigger file:{name} but "
                        f"fixture trigger_evidence.file is missing it"
                    )
        for d in meta.trigger_values("dir"):
            if _dir_pattern(d).search(fixture.prompt):
                rule_satisfied = True
                if d not in fixture.trigger_evidence.dir:
                    errors.append(
                        f"required rule {rel} declares Keywords trigger dir:{d} but "
                        f"fixture trigger_evidence.dir is missing it"
                    )
        for kw in meta.trigger_values("kw"):
            if _kw_pattern(kw).search(fixture.prompt):
                rule_satisfied = True

        # Check file-name-extension match (rule has ext trigger but prompt lacks it)
        rule_ext_triggers = meta.trigger_values("ext")
        rule_file_triggers = meta.trigger_values("file")
        rule_dir_triggers = meta.trigger_values("dir")

        if (
            rule_ext_triggers
            and not any(_ext_pattern(e).search(fixture.prompt) for e in rule_ext_triggers)
            and not _has_kw_or_other_match(meta, fixture)
        ):
            errors.append(
                f"required rule {rel} can only be discovered via ext:{rule_ext_triggers} "
                f"or kw:{meta.trigger_values('kw')} but prompt contains none of those tokens"
            )

        if (
            rule_file_triggers
            and not any(_file_pattern(f).search(fixture.prompt) for f in rule_file_triggers)
            and not _has_kw_or_other_match(meta, fixture)
        ):
            errors.append(
                f"required rule {rel} can only be discovered via file:{rule_file_triggers} "
                f"but prompt contains no matching filename"
            )

        if (
            rule_dir_triggers
            and not any(_dir_pattern(d).search(fixture.prompt) for d in rule_dir_triggers)
            and not _has_kw_or_other_match(meta, fixture)
        ):
            errors.append(
                f"required rule {rel} can only be discovered via dir:{rule_dir_triggers} "
                f"but prompt contains no matching directory token"
            )

        if not rule_satisfied and meta.triggers:
            unverifiable_required.append(rel)

    if unverifiable_required:
        errors.append(
            "no trigger evidence satisfied for required rules "
            f"{unverifiable_required}; the prompt must contain at least one literal "
            "kw/ext/file/dir token from each required rule's metadata"
        )

    return errors


def _has_kw_or_other_match(meta: RuleMetadata, fixture: Fixture) -> bool:
    """Return True if any kw/ext/dir trigger of the rule matches the prompt.

    Despite the historical name (kept for stability), this guard accepts a
    match from any non-file trigger kind. A rule that declares both
    ``ext:.py`` and ``file:pyproject.toml`` should not be reported as
    "discoverable only via file:" when the prompt contains ``loader.py``.
    """
    if any(_kw_pattern(kw).search(fixture.prompt) for kw in meta.trigger_values("kw")):
        return True
    if any(_ext_pattern(ext).search(fixture.prompt) for ext in meta.trigger_values("ext")):
        return True
    return bool(any(_dir_pattern(d).search(fixture.prompt) for d in meta.trigger_values("dir")))


def read_prompt(path: Path) -> str:
    """Read the top-level ``prompt:`` field from a fixture YAML file.

    Used by the ``refresh`` CLI command. Intentionally bypasses the
    full schema validator so it works on partially-authored fixtures.
    Only the ``prompt`` key is required; every other top-level key is
    ignored.

    Raises:
        FixtureValidationError: missing file, malformed YAML, or
            missing/empty/non-string ``prompt`` value.
    """
    if not path.exists():
        raise FixtureValidationError(f"fixture file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FixtureValidationError(f"failed to parse fixture YAML at {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise FixtureValidationError(
            f"fixture YAML at {path} must be a mapping with a top-level `prompt:` key"
        )
    value = raw.get("prompt")
    if not isinstance(value, str) or not value.strip():
        raise FixtureValidationError(
            f"fixture YAML at {path} is missing a non-empty `prompt:` string"
        )
    return value


def current_updated_timestamp() -> str:
    """Return the current local time as an ISO 8601 string with explicit offset.

    Used by ``refresh --write``, ``refresh-all``, and ``create`` to stamp the
    ``updated:`` field. Format: ``YYYY-MM-DDTHH:MM:SS+HH:MM`` (seconds
    precision, local timezone offset).
    """
    now = datetime.now().astimezone().replace(microsecond=0)
    return now.isoformat()


def read_updated(path: Path) -> str | None:
    """Read the top-level ``updated:`` field from a fixture YAML file.

    Used by the ``refresh`` CLI command (read-only mode) to preserve the
    on-disk timestamp in the regenerated skeleton so drift detection only
    flags real semantic changes. Bypasses full schema validation.

    Returns:
        The ``updated`` string if present and non-empty; otherwise ``None``.
    """
    if not path.exists():
        return None
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    if not isinstance(raw, dict):
        return None
    value = raw.get("updated")
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return None
        return value.replace(microsecond=0).isoformat()
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def validate_fixture(fixture: Fixture, rules: dict[str, RuleMetadata]) -> None:
    """Run the full trigger-evidence invariant against ``fixture``.

    Raises:
        FixtureValidationError: aggregate error listing every discovered issue.
    """
    errors: list[str] = []
    errors.extend(_check_evidence_in_prompt(fixture))
    errors.extend(_cross_check_required_rules(fixture, rules))
    if errors:
        joined = "\n  - ".join(errors)
        raise FixtureValidationError(
            f"[{fixture.id}] trigger-evidence invariant failures:\n  - {joined}"
        )


def validate_rendered_snippet(
    snippet_text: str,
    fixture_id: str,
    rules: dict[str, RuleMetadata],
) -> list[str]:
    """Parse ``snippet_text`` in-memory and return any trigger-evidence errors.

    Used by ``refresh`` and ``refresh-all`` as a round-trip gate before
    overwriting an existing fixture: render a candidate snippet, run the
    same trigger-evidence invariant the validate command applies, and
    surface any failures so the driver can write a ``<name>.invalid``
    candidate instead of overwriting on-disk content.

    Args:
        snippet_text: full YAML text of a candidate fixture (the output of
            :func:`ai_rules.rule_loader_eval.snippet.format_fixture_snippet`).
        fixture_id: id used in error messages; falls back to a synthesized
            name if parsing the YAML doesn't yield one.
        rules: rule metadata snapshot for the cross-checker.

    Returns:
        List of human-readable error strings; empty when the snippet would
        pass ``validate``. Schema-level parse failures (malformed YAML,
        missing keys, etc.) are surfaced as a single ``"schema: ..."``
        entry so callers can treat them uniformly with invariant failures.
    """
    try:
        raw = yaml.safe_load(snippet_text)
    except yaml.YAMLError as exc:
        return [f"schema: failed to parse rendered snippet as YAML: {exc}"]

    synth_path = Path(f"<rendered:{fixture_id}>")
    try:
        fixture = _parse_fixture(synth_path, raw)
    except FixtureValidationError as exc:
        return [f"schema: {exc}"]

    errors: list[str] = []
    errors.extend(_check_evidence_in_prompt(fixture))
    errors.extend(_cross_check_required_rules(fixture, rules))
    return errors


def load_fixtures(
    fixtures_dir: Path,
    rules: dict[str, RuleMetadata] | None = None,
    *,
    enforce_invariant: bool = True,
) -> list[Fixture]:
    """Load and validate all ``*.yaml`` fixtures under ``fixtures_dir``.

    Args:
        fixtures_dir: directory containing fixture YAML files.
        rules: optional preloaded rules metadata used by the cross-checker.
            If None and ``enforce_invariant=True``, only prompt-level evidence
            is enforced.
        enforce_invariant: when True (default), raise on validation failure.

    Returns:
        Sorted list of validated :class:`Fixture` objects.
    """
    fixtures: list[Fixture] = []
    yaml_paths = sorted(p for p in fixtures_dir.glob("*.yaml") if p.is_file())
    for path in yaml_paths:
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        fixture = _parse_fixture(path, raw)
        fixtures.append(fixture)

    if enforce_invariant:
        for fixture in fixtures:
            if rules is None:
                errors = _check_evidence_in_prompt(fixture)
                if errors:
                    joined = "\n  - ".join(errors)
                    raise FixtureValidationError(
                        f"[{fixture.id}] trigger-evidence invariant failures:\n  - {joined}"
                    )
            else:
                validate_fixture(fixture, rules)

    fixtures.sort(key=lambda f: f.id)
    return fixtures


def _apply_invariant(
    fixture: Fixture,
    rules: dict[str, RuleMetadata] | None,
) -> None:
    """Apply the trigger-evidence invariant to a single fixture.

    Mirrors the per-fixture branch inside :func:`load_fixtures`.
    """
    if rules is None:
        errors = _check_evidence_in_prompt(fixture)
        if errors:
            joined = "\n  - ".join(errors)
            raise FixtureValidationError(
                f"[{fixture.id}] trigger-evidence invariant failures:\n  - {joined}"
            )
    else:
        validate_fixture(fixture, rules)


def load_fixture(
    fixtures_dir: Path,
    fixture_id: str,
    rules: dict[str, RuleMetadata] | None = None,
    *,
    enforce_invariant: bool = True,
) -> Fixture:
    """Load and validate a single fixture by ID.

    Fast path: tries ``fixtures_dir / f"{fixture_id}.yaml"`` first (covers the
    common case where the filename matches the ``id`` field).

    Fallback: scans all ``*.yaml`` files for the first whose parsed ``id``
    matches ``fixture_id``.  Only triggered when the filename and ``id`` field
    diverge, which is rare in practice.

    Args:
        fixtures_dir: directory containing fixture YAML files.
        fixture_id: the ``id`` field value to look up.
        rules: optional preloaded rules metadata for the cross-checker.
            If ``None`` and ``enforce_invariant=True``, only prompt-level
            evidence is enforced.
        enforce_invariant: when True (default), raise on trigger-evidence
            failures.

    Returns:
        A validated :class:`Fixture`.

    Raises:
        FixtureValidationError: if no fixture with ``fixture_id`` is found, or
            if the fixture fails schema or invariant checks.
    """
    # --- fast path -----------------------------------------------------------
    candidate = fixtures_dir / f"{fixture_id}.yaml"
    if candidate.is_file():
        with candidate.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        fixture = _parse_fixture(candidate, raw)
        if fixture.id == fixture_id:
            if enforce_invariant:
                _apply_invariant(fixture, rules)
            return fixture
        # filename matched but id: field differs — fall through to full scan

    # --- fallback: scan all files -------------------------------------------
    for path in sorted(fixtures_dir.glob("*.yaml")):
        if path == candidate:
            continue  # already tried above
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        fixture = _parse_fixture(path, raw)
        if fixture.id == fixture_id:
            if enforce_invariant:
                _apply_invariant(fixture, rules)
            return fixture

    raise FixtureValidationError(f"fixture {fixture_id!r} not found in {fixtures_dir}")
