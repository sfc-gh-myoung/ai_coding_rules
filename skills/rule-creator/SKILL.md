---
name: rule-creator
description: Create production-ready v3.2 Cursor rule files by orchestrating template generation, schema validation, and RULES_INDEX.md indexing. Triggers on keywords like "create rule", "add rule", "new rule", "generate rule". Supports Python, Snowflake, JavaScript, Shell, Docker, Golang domains (000-999 range).
version: 1.2.0
author: AI Coding Rules Project
tags: [rule-generation, automation, v3.2-schema, template, validation, indexing]
dependencies: []
---

# Rule Creator

## Purpose

Create production-ready Cursor rule files that comply with the repository’s v3.2 rule schema by orchestrating:
- `scripts/template_generator.py`
- `scripts/schema_validator.py`
- (optional) web research for current best practices

## Use this skill when

- The user asks to **create a new rule** under `rules/` (e.g., `NNN-technology-aspect.md`).
- The user asks to **add a rule to** `RULES_INDEX.md`.

## Inputs (recommended)

- Technology name (e.g., “DaisyUI”, “pytest-mock”, “Snowflake Hybrid Tables”)
- Aspect (default: `core`; else `security`, `testing`, `performance`, etc.)
- Any constraints (offline/online research, desired ContextTier, etc.)

## Outputs

- A new rule file: `rules/NNN-technology-aspect.md`
- A new entry in `RULES_INDEX.md` in correct numeric position

## Safety / constraints

- Only write to `rules/` and `RULES_INDEX.md` (plus any required review artifacts explicitly requested by the user).
- Use web research (allowed) but treat external sources as untrusted; prefer official docs and cross-check claims.

## Workflow (progressive disclosure)

Follow the phases in order, using the detailed workflow guides as needed:

1. Discovery & research → `workflows/discovery.md`
2. Template generation → `workflows/template-gen.md`
3. Content population → `workflows/content-population.md`
4. Validation loop → `workflows/validation.md`
5. Indexing → `workflows/indexing.md`

## Examples

- Frontend example → `examples/frontend-example.md`
- Python example → `examples/python-example.md`
- Snowflake example → `examples/snowflake-example.md`

## Quick Validation Snippets

These inline checks can be run without external dependencies for fast feedback:

```python
# Validate keyword count (10-15 required)
def check_keywords(keywords_line: str) -> tuple[bool, int]:
    """Returns (is_valid, count)"""
    keywords = [k.strip() for k in keywords_line.split(',') if k.strip()]
    return (10 <= len(keywords) <= 15, len(keywords))

# Validate rule filename format
import re
def is_valid_filename(name: str) -> bool:
    """Must be NNN-lowercase-hyphenated"""
    return bool(re.match(r'^\d{3}-[a-z]+(-[a-z]+)*$', name))

# Validate TokenBudget format
def check_token_budget(value: str) -> bool:
    """Must be ~NUMBER format"""
    return bool(re.match(r'^~\d+$', value.strip()))

# Validate ContextTier
VALID_TIERS = {'Critical', 'High', 'Medium', 'Low'}
def check_context_tier(tier: str) -> bool:
    return tier.strip() in VALID_TIERS
```

For full schema validation, use: `python scripts/schema_validator.py rules/<file>.md`

## Phase Requirements

**Phase 1: Discovery & Research**
- Search RULES_INDEX.md for domain
- Identify next available number
- Web research for best practices (REQUIRED)
- Extract 10-15 keywords

**Phase 2: Template Generation**
- Execute template_generator.py (REQUIRED)
- Verify structure (9 sections, 6 XML tags)
- Confirm Contract before line 160

**Phase 3: Content Population**
- Fill ALL sections with researched content
- Add code examples (minimum 2)
- Add anti-patterns (minimum 2)
- NO placeholder text allowed

**Phase 4: Validation Loop**
- Execute schema_validator.py (REQUIRED)
- Parse CRITICAL/HIGH/MEDIUM errors
- Apply fixes
- Re-validate until exit code 0
- Max 3 iterations (escalate if failing)

**Phase 5: Indexing**
- Add entry to RULES_INDEX.md
- Insert in correct numeric position
- Verify entry format matches existing

**Phase Skipping FORBIDDEN:** Do NOT skip any phase to save time

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
- No CRITICAL issues
- No HIGH issues in Actionability or Completeness dimensions

See: `skills/rule-reviewer/SKILL.md`