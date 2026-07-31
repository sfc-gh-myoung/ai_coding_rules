"""Micro-kernel generator for progressive rule loading.

Produces a compressed ~500 token foundation that replaces the full
000-global-core.md (273 lines, ~2550 tokens) in the progressive architecture.

Content selection criteria (from v3 plan Section 4.4):
- INCLUDE: All CRITICAL-tagged principles and MANDATORY behavioral rules
- INCLUDE: Rule loading protocol and validation sequence
- EXCLUDE: PRE-FLIGHT format (on-demand only, injected by eval or $show-rules skill)
- EXCLUDE: Anti-patterns section, worked examples, multi-paragraph explanations
- EXCLUDE: Gate failure message catalog (lazy-loaded on first gate failure)
- EXCLUDE: High-risk action rule map and reference-file definitions
"""

from __future__ import annotations

# The micro-kernel is hand-authored for precision, not auto-generated.
# Target: ≤500 tokens. Expand in 100-token increments (up to 800) if
# behavioral compliance drops >2%.

MICRO_KERNEL = """\
# Foundation (micro-kernel)

## Mandatory Behaviors
- Present a task list before any file modifications
- Make surgical edits only (minimal, targeted changes)
- Run validation (lint, test, format) before marking tasks complete
- Never declare a rule as loaded without a successful read
- Load language-specific rules when modifying code files

## Validation Sequence
1. Detect project automation, first match wins: Makefile, then Taskfile.yml, then package.json, then direct commands
2. Run validation tools appropriate to the language
3. On failure: revert, report with exact error and fix

## Rule Loading
- The manifest is metadata only — each load_sequence entry with read_required=true MUST be loaded via read_file before citation
- Read rule paths EXACTLY as given, relative to the repository root (e.g. `rules/100-snowflake-core.md`). Never convert them to absolute paths and never guess a project root
- Matched rules are CANDIDATES, not instructions to read all of them: select the most relevant, up to 3
- Cap: 3 domain rules per response (dependencies don't count against cap)
- Load domain rules matching file extensions being modified
- If no rules match: proceed with foundation only, note "none matched"

## Communication
- Technical, concise, code-first
- No emojis unless requested
- Show deltas not entire files
"""

MICRO_KERNEL_VERSION = "1.2.0"


def get_micro_kernel() -> str:
    """Return the micro-kernel content."""
    return MICRO_KERNEL


def token_estimate() -> int:
    """Rough token estimate (1 token ≈ 4 chars for English markdown)."""
    return len(MICRO_KERNEL) // 4
