"""Prompt-only discovery system prompt for --without-plugin eval mode.

Assembles a system prompt that gives the model schema hints about the
rules/ folder structure and lets it discover matching rules autonomously.
Does NOT call match_rules, build_eval_manifest, or load_rules_db.

The shared prompt constants (_DISCOVERY_HARD_STOP, _ENFORCEMENT_BLOCK) are
imported from agent_runner to prevent copy-paste drift.
"""

from __future__ import annotations

from pathlib import Path

# --- Schema hints kernel (the without-plugin equivalent of micro-kernel) ---

WITHOUT_PLUGIN_KERNEL = """\
# Rule Discovery Instructions (prompt-only mode)

## Task
You are evaluating rule discovery for the ai_coding_rules project.
Given a user prompt, discover which rules in the `rules/` directory are relevant.

## Rules Folder Structure
- Rules live in `rules/` as Markdown files (e.g., `rules/100-snowflake-core.md`)
- Each rule has YAML frontmatter between `---` fences at the top
- The frontmatter contains these discovery-relevant fields:
  - `keywords:`: list of semantic terms that trigger this rule
  - `triggers:`: dict with keys: `extensions:`, `directories:`, `keywords:`
    - `extensions:`: file extensions (e.g., `.py`, `.sql`) that activate this rule
    - `directories:`: path patterns that activate this rule
    - `keywords:`: typed keyword entries (e.g., `kw:snowflake`, `ext:.py`)
  - `depends:`: dependency declarations:
    - `required:`: list of rule filenames that MUST be co-loaded
    - `optional:`: list of rule filenames that SHOULD be loaded if contextually relevant
  - `version:`: semantic version (e.g., `v1.2.0`)
  - `scope:`: what the rule covers

## Discovery Algorithm (guidance, not prescription)
1. Extract keywords from the user's prompt (technologies, file types, concepts)
2. For each rule in `rules/`, read its frontmatter and check:
   - Do any `keywords:` or `triggers.keywords:` match the prompt's intent?
   - Do any `triggers.extensions:` match file types mentioned in the prompt?
   - Do any `triggers.directories:` match paths mentioned in the prompt?
3. Select the top matches (up to 3 domain rules)
4. For each selected rule, transitively load all `depends.required:` rules
5. `rules/000-global-core.md` is the foundation: you do NOT need to read it
   (its content is summarized in the behavioral rules below)

## Behavioral Rules
- Present a task list before any file modifications
- Make surgical edits only (minimal, targeted changes)
- Run validation before marking tasks complete
- Cap: 3 domain rules per response (required dependencies don't count)
- If no rules match: note "none matched"

## Strategy Tips
- Start by listing files in `rules/` to see what's available
- Read frontmatter of promising candidates (you can use Grep to search keywords)
- Don't read the entire rule body during discovery: frontmatter is sufficient for matching
- After selecting rules, DO read the full file so you can cite the version
"""


def build_prompt_without_plugin(rules_dir: Path) -> str:
    """Build a prompt-only discovery system prompt (no manifest injection).

    Assembles the HARD STOP preamble, schema-hints kernel, and enforcement
    block. Does NOT call match_rules, build_eval_manifest, or load_rules_db,
    and does not accept a fixture_prompt parameter.

    Args:
        rules_dir: Resolved path to the rules/ directory (used to tell the
            model where rule files live).

    Returns:
        Complete system prompt string for without-plugin eval mode.
    """
    rules_root = rules_dir.resolve()

    return (
        "HARD STOP: This is a rule-discovery probe. Your job has exactly two "
        "steps, in this order:\n"
        "  (1) Discover and READ the relevant rule files.\n"
        "  (2) Emit the PRE-FLIGHT gates, then `SEED_FIXTURE_COMPLETE`, then stop.\n"
        "The stop boundary applies AFTER step 1. It forbids executing the user's "
        "underlying task; it does NOT forbid reading rule files. Reading rules IS "
        "the task, so step 1 must actually happen before you stop.\n\n"
        "<system-reminder>\n"
        "## AI Coding Rules: Rule Discovery (prompt-only mode)\n\n"
        f"{WITHOUT_PLUGIN_KERNEL}\n"
        "</system-reminder>\n\n"
        f"RULE PATHS: rule files live under `{rules_root}`. Read them using "
        "relative paths like `rules/100-snowflake-core.md`. "
        "Do NOT rewrite them as absolute paths and do NOT guess a project root; "
        "a wrong path yields a file-not-found and counts as loading nothing.\n\n"
        "ENFORCEMENT: Every rule listed under Gate 3 MUST have a matching Read tool call.\n"
        "The evaluator independently verifies tool calls against your Gate 3 citations.\n"
        "If you cite `rules/X.md` in Gate 3 but did not Read it, the fixture FAILS.\n\n"
        "FAILURE CONDITION: FABRICATED CITATIONS:\n"
        "You MUST call the Read tool on a rule file BEFORE citing it in Gate 3.\n"
        "Do NOT cite rules from memory. Do NOT cite rules you merely know exist.\n"
        "The ONLY way to pass: Read tool call → then cite in Gate 3.\n"
        "Any Gate 3 citation without a prior Read = automatic FAIL.\n\n"
        "DO NOT:\n"
        "- Read or cite rules/000-global-core.md (the micro-kernel above replaces it)\n"
        "- Cite ANY rule in Gate 3 that you did not Read; this WILL fail the fixture\n"
        "- Execute the user's task or write code\n"
        "- Ask a clarifying question, or answer the user's request instead of stopping\n\n"
        "UNCONDITIONAL OUTPUT REQUIREMENT:\n"
        "Your FINAL message MUST contain the PRE-FLIGHT block below: always, with "
        "no exceptions. This still applies if rule files are missing, if discovery "
        "fails, if the user's files cannot be located, or if the request seems "
        "ambiguous. In those cases still emit the block and record what happened "
        "in the Gate 3 reason text.\n\n"
        "  PRE-FLIGHT:\n"
        "  - [x] Gate 1: Foundation loaded\n"
        "  - [x] Gate 2: Discovery performed\n"
        "  - [x] Gate 3: +N domain rule(s):\n"
        "    - rules/<matched-rule>.md (<reason>)\n\n"
        "When no domain rule was loaded, use exactly this Gate 3 line and nothing "
        "else in its place:\n\n"
        "  - [x] Gate 3: none matched\n\n"
        "After the Gate 3 block, output `SEED_FIXTURE_COMPLETE` and IMMEDIATELY STOP."
    )
