"""Declarative manifest of primary files and their replicas.

The plugin ships as a self-contained directory: `skills/`, `hooks/`, and the
matcher script, but deliberately **not** `src/`. A shipped skill therefore cannot
reference `src/ai_rules/match_rules.py`, so the matcher necessarily exists twice --
once as an importable module for the CLI and the wheel, once as a standalone
stdlib-only script the plugin carries.

Before this module the replica topology was expressed twice: as a series of
hand-written ``shutil.copy2`` calls in ``commands/plugin.py``, and again as a
literal ``EXPECTED_ARTIFACTS`` tuple. Adding a copy step without registering it in
both places produced an artifact nothing verified. Worse, the tracked in-repo
replica had no writer at all and drifted silently from its primary.

This module is the single place the topology is declared. ``plugin build`` copies
from it, ``plugin sync`` writes in-repo replicas from it, ``plugin verify``
byte-compares against it, the artifact contract is derived from it, and the parity
tests parameterize over it. Adding a replica extends every one of those surfaces
at once.

Components CoCo supports that this plugin intentionally does **not** ship:

- ``agents/`` -- subagent definitions. None are authored.
- ``commands/`` -- slash commands. Skills cover the same need here.
- ``.mcp.json`` -- MCP servers. The plugin exposes no external tools.
- ``activation.md`` -- re-enable stub shown when the plugin is inactive.

Their absence is a decision, not an oversight. Because ``check_artifacts``
rejects undeclared output, emitting any of them without adding a
:class:`BuildCopy` here fails the build rather than shipping unverified.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuildCopy:
    """A primary file or tree copied into the built plugin.

    Attributes:
        primary: Source path, relative to the repository root.
        dest: Destination path, relative to the built plugin directory.
        is_tree: When True, `primary` is a directory copied wholesale. Tree
            destinations are cleaned before copying so a removed source file does
            not linger in the output.
        pattern: Glob applied to a tree's immediate children. ``None`` copies the
            whole tree recursively. Only meaningful when `is_tree` is True.
        required: When False, the copy is skipped if the primary is absent,
            mirroring the historic ``if src.exists()`` guards. The artifact
            contract still expects the destination, so a silently skipped copy
            surfaces as a missing artifact rather than passing unnoticed.
    """

    primary: str
    dest: str
    is_tree: bool = False
    pattern: str | None = None
    required: bool = True


@dataclass(frozen=True)
class RepoReplica:
    """A generated, tracked in-repo byte-copy of a primary.

    The replica must stay byte-identical to its primary. Byte equality is the
    contract, which is why the copy carries no "generated" header of its own --
    the provenance note lives in the primary's module docstring so both files
    carry identical text.

    Attributes:
        primary: Source of truth, relative to the repository root.
        replica: Generated copy, relative to the repository root. Written by
            ``ai-rules plugin sync``; never hand-edited.
    """

    primary: str
    replica: str


#: Artifacts the build generates rather than copies. They have no primary, so
#: they are part of the contract but excluded from byte comparison.
GENERATED_ARTIFACTS: tuple[str, ...] = (".cortex-plugin/plugin.json",)

#: Every copy the build performs. Order matches the build sequence so the emitted
#: log reads top to bottom.
BUILD_COPIES: tuple[BuildCopy, ...] = (
    BuildCopy(
        primary="src/ai_rules/match_rules.py",
        dest="skills/rule-loader/scripts/match_rules.py",
    ),
    BuildCopy(primary="rules", dest="rules", is_tree=True, pattern="*.md"),
    BuildCopy(primary="hooks/user-prompt-submit", dest="hooks/user-prompt-submit"),
    BuildCopy(primary="hooks/hooks.json", dest="hooks/hooks.json"),
    BuildCopy(
        primary="skills/rule-loader/SKILL.md",
        dest="skills/rule-loader/SKILL.md",
    ),
    BuildCopy(
        primary="skills/rule-loader/CHANGELOG.md",
        dest="skills/rule-loader/CHANGELOG.md",
        required=False,
    ),
    BuildCopy(
        primary="skills/rule-loader/workflows",
        dest="skills/rule-loader/workflows",
        is_tree=True,
    ),
    BuildCopy(
        primary="skills/rule-loader/examples",
        dest="skills/rule-loader/examples",
        is_tree=True,
    ),
    BuildCopy(
        primary="skills/show-rules/SKILL.md",
        dest="skills/show-rules/SKILL.md",
        required=False,
    ),
    BuildCopy(
        primary="src/ai_rules/plugin/micro_kernel_content.md",
        dest="micro_kernel_content.md",
        required=False,
    ),
)

#: Tracked in-repo replicas. The matcher is the only one: it must sit under
#: `skills/rule-loader/scripts/` for the shipped skill and for the in-repo agent
#: workflows that invoke that literal path.
REPO_REPLICAS: tuple[RepoReplica, ...] = (
    RepoReplica(
        primary="src/ai_rules/match_rules.py",
        replica="skills/rule-loader/scripts/match_rules.py",
    ),
)


def file_copies() -> tuple[BuildCopy, ...]:
    """Return the build copies that produce a single file.

    Returns:
        Every :class:`BuildCopy` whose `is_tree` is False.
    """
    return tuple(c for c in BUILD_COPIES if not c.is_tree)


def tree_copies() -> tuple[BuildCopy, ...]:
    """Return the build copies that produce a directory.

    Returns:
        Every :class:`BuildCopy` whose `is_tree` is True.
    """
    return tuple(c for c in BUILD_COPIES if c.is_tree)


def expected_artifacts() -> tuple[str, ...]:
    """Return every individual file the build must emit.

    Derived from the manifest rather than duplicated, so a new copy step cannot
    fall out of sync with the contract that validates it.

    Returns:
        Sorted plugin-relative file paths, including generated artifacts.
    """
    return tuple(sorted(GENERATED_ARTIFACTS + tuple(c.dest for c in file_copies())))


def expected_trees() -> tuple[str, ...]:
    """Return every directory prefix the build must emit.

    Trees are validated by prefix rather than enumeration, so adding a rule never
    requires editing the manifest.

    Returns:
        Sorted plugin-relative directory paths.
    """
    return tuple(sorted(c.dest for c in tree_copies()))
