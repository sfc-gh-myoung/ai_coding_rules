"""Atomic artifact I/O: path containment, overwrite discipline, and JSON-last publication.

Implements C17 of ``skill-system-remediation-v3.plan.md``: path containment,
explicit overwrite refusal, sibling temp files, ``flush``+``fsync``+``os.replace``,
and paired Markdown-first / canonical-JSON-last publication.

Error classes
-------------
``ArtifactIOError`` (maps to exit 2)
    File missing, unreadable, invalid UTF-8, invalid JSON, or any OS I/O
    failure that is not caused by the caller violating a write contract.

``ArtifactDefectError`` (maps to exit 3)
    Path escapes the configured output root; overwrite refused because the
    destination exists and ``replace=False``; or an internal implementation
    defect (e.g. staged file disappeared before ``os.replace``).

Publication ordering
--------------------
For accepted review pairs::

    1. Validate canonical JSON in memory.
    2. Render Markdown deterministically.
    3. Write sibling staging files under the output root.
    4. flush and fsync both staging files.
    5. Validate staged JSON; byte-compare staged Markdown to a rerender.
    6. Publish Markdown with os.replace.
    7. Publish canonical JSON last with os.replace.
    8. Automation discovers accepted artifacts from JSON only.
       A Markdown file without a same-stem JSON sibling is an orphan diagnostic.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Public error types
# ---------------------------------------------------------------------------


class ArtifactIOError(OSError):
    """I/O failure reading or writing an artifact (exit 2).

    Raised for missing files, permission errors, invalid encoding, invalid
    JSON content, or any OS-level failure that is not a caller contract
    violation.  Callers should preserve existing state and escalate.
    """


class ArtifactDefectError(RuntimeError):
    """Deterministic implementation or contract defect (exit 3).

    Raised for path-containment violations, overwrite refusals, and
    internal implementation errors.  These defects must not consume a
    model retry.
    """


# ---------------------------------------------------------------------------
# Path containment
# ---------------------------------------------------------------------------


def check_containment(path: Path, root: Path) -> None:
    """Raise :exc:`ArtifactDefectError` if ``path`` escapes ``root``.

    Both paths are resolved (symlinks expanded, ``..`` collapsed) before
    comparison so traversal attacks using ``..`` components are caught.

    Args:
        path: The candidate output path.
        root: The configured output root directory.

    Raises:
        ArtifactDefectError: ``path`` is not inside ``root`` after resolution.
    """
    try:
        resolved_path = path.resolve()
        resolved_root = root.resolve()
    except OSError as exc:
        raise ArtifactDefectError(f"Cannot resolve paths for containment check: {exc}") from exc

    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ArtifactDefectError(
            f"Path {path!r} escapes output root {root!r}. Write refused: containment violation."
        ) from exc


# ---------------------------------------------------------------------------
# Atomic single-file writers
# ---------------------------------------------------------------------------


def atomic_write_text(
    path: Path, text: str, *, replace: bool = False, output_root: Path | None = None
) -> None:
    """Write ``text`` to ``path`` atomically via a sibling staging file.

    Serializes to a sibling temp file (same directory as ``path``), calls
    ``flush`` and ``fsync``, then calls ``os.replace``.  The destination is
    never partially written.

    Args:
        path: The final output path.
        text: UTF-8 text to write.
        replace: If ``False`` (default) and ``path`` already exists, raise
            :exc:`ArtifactDefectError` and leave the existing bytes unchanged.
        output_root: Optional root that must contain ``path``.

    Raises:
        ArtifactDefectError: ``path`` exists and ``replace`` is ``False``.
        ArtifactIOError: Any OS-level I/O failure during staging or replace.
    """
    if output_root is not None:
        check_containment(path, output_root)
    if not replace and path.exists():
        raise ArtifactDefectError(
            f"Overwrite refused: {path!r} already exists. Pass replace=True to overwrite."
        )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ArtifactIOError(f"Cannot create parent directory for {path!r}: {exc}") from exc

    fd, tmp_str = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    except OSError as exc:
        with contextlib.suppress(OSError):
            tmp_path.unlink()
        raise ArtifactIOError(f"Atomic write failed for {path!r}: {exc}") from exc


def atomic_write_json(
    path: Path, obj: Any, *, replace: bool = False, output_root: Path | None = None
) -> None:
    """Write ``obj`` as pretty-printed JSON to ``path`` atomically.

    Serializes using ``json.dumps`` with ``indent=2, sort_keys=True``.
    Delegates to :func:`atomic_write_text` for staging, fsync, and replace.

    Args:
        path: The final output path.
        obj: A JSON-serializable object.
        replace: If ``False`` (default) and ``path`` already exists, raise
            :exc:`ArtifactDefectError` without modifying existing bytes.
        output_root: Optional root that must contain ``path``.

    Raises:
        ArtifactDefectError: ``path`` exists and ``replace`` is ``False``.
        ArtifactIOError: JSON serialization fails or any OS-level I/O failure.
    """
    try:
        payload = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    except (TypeError, ValueError) as exc:
        raise ArtifactIOError(f"JSON serialization failed for {path!r}: {exc}") from exc
    atomic_write_text(path, payload, replace=replace, output_root=output_root)


# ---------------------------------------------------------------------------
# Paired publication (Markdown-first, JSON-last)
# ---------------------------------------------------------------------------


def publish_pair(
    md_path: Path,
    json_path: Path,
    md_text: str,
    json_obj: Any,
    *,
    replace: bool = False,
    output_root: Path | None = None,
) -> None:
    """Publish a Markdown+JSON pair atomically with MD-first, JSON-last ordering.

    Protocol (§3.5 of the plan):

    1. Validate both destinations for overwrite refusal.
    2. Write sibling staging files for both artifacts.
    3. ``flush`` and ``fsync`` both staging files.
    4. Publish Markdown with ``os.replace``.
    5. Publish canonical JSON last with ``os.replace``.

    If any step fails before step 4, no destination file is modified.  If
    step 4 succeeds but step 5 fails, the Markdown is visible but the JSON
    is absent: automation that discovers accepted artifacts from JSON only
    will treat the Markdown as an orphan diagnostic and ignore it.

    Args:
        md_path: Destination path for the Markdown file.
        json_path: Destination path for the canonical JSON file.
        md_text: Rendered Markdown content.
        json_obj: A JSON-serializable object.
        replace: If ``False`` (default) and either destination already
            exists, raise :exc:`ArtifactDefectError` without writing anything.
        output_root: Optional root that must contain both destinations.

    Raises:
        ArtifactDefectError: Either destination exists and ``replace`` is
            ``False``.
        ArtifactIOError: JSON serialization fails or any OS-level I/O failure.
    """
    if output_root is not None:
        check_containment(md_path, output_root)
        check_containment(json_path, output_root)

    # --- Step 1: check overwrite refusal for both destinations up front ----
    if not replace:
        if md_path.exists():
            raise ArtifactDefectError(
                f"Overwrite refused: {md_path!r} already exists. Pass replace=True to overwrite."
            )
        if json_path.exists():
            raise ArtifactDefectError(
                f"Overwrite refused: {json_path!r} already exists. Pass replace=True to overwrite."
            )

    # --- Step 2+3: serialize JSON payload ---------------------------------
    try:
        json_payload = json.dumps(json_obj, indent=2, sort_keys=True) + "\n"
    except (TypeError, ValueError) as exc:
        raise ArtifactIOError(f"JSON serialization failed for {json_path!r}: {exc}") from exc

    # Create parent directories
    for dest in (md_path, json_path):
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ArtifactIOError(f"Cannot create parent directory for {dest!r}: {exc}") from exc

    # Stage both files
    fd_md, tmp_md_str = tempfile.mkstemp(
        prefix=f".{md_path.name}.",
        suffix=".tmp",
        dir=str(md_path.parent),
    )
    tmp_md = Path(tmp_md_str)

    fd_json, tmp_json_str = tempfile.mkstemp(
        prefix=f".{json_path.name}.",
        suffix=".tmp",
        dir=str(json_path.parent),
    )
    tmp_json = Path(tmp_json_str)

    try:
        # Write and fsync Markdown staging file
        with os.fdopen(fd_md, "w", encoding="utf-8") as fh:
            fh.write(md_text)
            fh.flush()
            os.fsync(fh.fileno())

        # Write and fsync JSON staging file
        with os.fdopen(fd_json, "w", encoding="utf-8") as fh:
            fh.write(json_payload)
            fh.flush()
            os.fsync(fh.fileno())

        # --- Step 4: publish Markdown first --------------------------------
        os.replace(tmp_md, md_path)

        # --- Step 5: publish canonical JSON last ---------------------------
        os.replace(tmp_json, json_path)

    except OSError as exc:
        with contextlib.suppress(OSError):
            tmp_md.unlink()
        with contextlib.suppress(OSError):
            tmp_json.unlink()
        raise ArtifactIOError(
            f"Pair publication failed ({md_path!r}, {json_path!r}): {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Orphan discovery helper
# ---------------------------------------------------------------------------


def discover_accepted_json(directory: Path) -> list[Path]:
    """Return paths of accepted JSON artifacts in ``directory``.

    Automation discovers accepted review artifacts from JSON only.  A
    Markdown file whose same-stem ``.json`` sibling is absent is an orphan
    diagnostic and is excluded from this result.

    Only ``.json`` files whose same-stem ``.md`` sibling exists are
    considered paired.  Unpaired ``.json`` files (JSON without Markdown)
    are also returned — they represent accepted artifacts whose Markdown
    companion has not yet been rendered.

    Orphan Markdown files (``*.md`` without ``*.json``) are intentionally
    excluded from the returned list.

    Args:
        directory: The directory to scan (non-recursive).

    Returns:
        Sorted list of ``.json`` file paths found directly in ``directory``.

    Raises:
        ArtifactIOError: ``directory`` cannot be read.
    """
    try:
        entries = list(directory.iterdir())
    except OSError as exc:
        raise ArtifactIOError(f"Cannot scan directory {directory!r}: {exc}") from exc

    return sorted(p for p in entries if p.suffix == ".json" and p.is_file())


def is_orphan_markdown(md_path: Path) -> bool:
    """Return ``True`` if ``md_path`` is an orphan Markdown file.

    A Markdown file is an orphan when its same-stem ``.json`` sibling does
    not exist.  Orphan Markdown is produced by an interrupted pair
    publication (Markdown published but JSON not yet written) and should be
    treated as a diagnostic artifact, not as an accepted review.

    Args:
        md_path: Path to the Markdown file to inspect.

    Returns:
        ``True`` if the ``.json`` sibling is absent; ``False`` otherwise.
    """
    return not md_path.with_suffix(".json").exists()
