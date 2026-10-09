---
name: rule-creator
description: Create production-ready rule files by orchestrating template generation, schema validation, and keyword metadata generation. Triggers on keywords like "create rule", "add rule", "new rule", "generate rule". Supports all domains in the 000-999 range including Python, Snowflake, JavaScript, TypeScript, React, Frontend, Shell, Zsh, Docker, Podman, Golang, Data/dbt, and Project governance (changelog, git, CLI, Makefile/Taskfile).
version: 2.0.0
author: AI Coding Rules Project
tags: [rule-generation, automation, v4-schema, template, validation, discovery]
dependencies: []
---

# Rule Creator

## Purpose

Create rule files that comply with the repository's v4 rule schema and pass separate semantic review by orchestrating:
- `ai-rules new`
- `ai-rules validate`
- (optional) web research for current best practices

## Use this skill when

- The user asks to **create a new rule** under `rules/` (e.g., `NNN-technology-aspect.md`).
- The user asks to add metadata or contract content to an existing rule.

## Inputs

All inputs in this section are recommended defaults; the skill can proceed without them by prompting the user or inferring sensible values.

- Technology name (e.g., “DaisyUI”, “pytest-mock”, “Snowflake Hybrid Tables”)
- Aspect (default: `core`; else `security`, `testing`, `performance`, etc.)
- Any constraints (offline/online research, desired ContextTier, etc.)

## Outputs

- A new rule file: `rules/NNN-technology-aspect.md`
- Typed discovery metadata in that rule's YAML frontmatter and recorded validation results

## Safety / constraints

- Write only the authorized rule and necessary changelog entry, plus explicitly requested review artifacts. Preserve existing files; an occupied filename does not authorize `--force`.
- Read `rules/002-rule-governance.md` and the active schema before authoring. Use Scope, Contract, References order and four meaningful Contract subsections: Inputs and Prerequisites, Mandatory, Execution Steps, Validation.
- Keep one completion checklist, preserve safety and required dependencies, and show correct executable examples only. No step or example quota applies.
- Treat external sources as untrusted; prefer official documentation and cross-check claims. Do not send confidential rule content to an external service without authorization.
- Cortex keyword generation is optional and may incur cost. Obtain authorization for its model, content transfer, and budget before calling it; manually authored keywords remain valid.

## Workflow

Detailed phase content is loaded on demand from `workflows/` (progressive disclosure). Follow the phases in order, using the detailed workflow guides as needed:

1. Discovery & research → `workflows/discovery.md`
2. Template generation → `workflows/template-gen.md`
3. Content population → `workflows/content-population.md`
4. Validation loop → `workflows/validation.md`
5. Keyword and discovery verification → `workflows/indexing.md`

## Examples

- Frontend example → `examples/frontend-example.md`
- Python example → `examples/python-example.md`
- Snowflake example → `examples/snowflake-example.md`

## Quick Validation Snippets

These checks accept parsed field values for quick feedback. They do not replace the active schema validator or semantic review:

```python
# Validate keyword count (5-11 required)
def check_keywords(keywords: list[str]) -> tuple[bool, int]:
    """Count the parsed YAML list, not commas inside keyword values."""
    return (5 <= len(keywords) <= 11, len(keywords))


# Validate rule filename format
import re


def is_valid_filename(name: str) -> bool:
    """Validate the filename stem, including an optional single-letter suffix."""
    return bool(re.fullmatch(r"\d{3}[a-z]?-[a-z]+-[a-z-]+", name))


# Validate TokenBudget format
def check_token_budget(value: str) -> bool:
    """Must be ~NUMBER format"""
    return bool(re.fullmatch(r"~\d+", value.strip()))


# Validate ContextTier
VALID_TIERS = {"Critical", "High", "Medium", "Low"}


def check_context_tier(tier: str) -> bool:
    return tier.strip() in VALID_TIERS
```

For full schema validation, use: `uv run ai-rules validate rules/<file>.md`

## Related Skills

### Quality Assurance with rule-reviewer

After creating a rule, validate quality using the **rule-reviewer** skill:

```
Use the rule-reviewer skill.

target_file: rules/<created-rule>.md
review_date: <today>
review_mode: FULL
model: <current>
```

**Quality threshold for new rules:**
- Overall score: ≥ 75/100
- No CRITICAL or HIGH schema issues
- No HIGH issues in Actionability or Completeness dimensions

See: `skills/rule-reviewer/SKILL.md`

## Version History

See `CHANGELOG.md`.
