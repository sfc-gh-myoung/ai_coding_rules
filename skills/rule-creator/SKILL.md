---
name: rule-creator
description: Create production-ready v3.2 Cursor rule files by orchestrating template generation, schema validation, and RULES_INDEX.md indexing. Triggers on keywords like "create rule", "add rule", "new rule", "generate rule". Supports Python, Snowflake, JavaScript, Shell, Docker, Golang domains (000-999 range).
version: 1.3.0
---

# Rule Creator

## Overview

Create production-ready Cursor rule files that comply with v3.2 schema by orchestrating `template_generator.py`, `schema_validator.py`, and web research.

### When to Use

- User asks to create a new rule under `rules/` (e.g., `NNN-technology-aspect.md`)
- User asks to add a rule to `RULES_INDEX.md`
- User requests documentation for a technology following v3.2 schema

### Inputs

- **Technology name**: e.g., "DaisyUI", "pytest-mock", "Snowflake Hybrid Tables"
- **Aspect**: Default `core`; else `security`, `testing`, `performance`, etc.
- **Constraints**: Optional (offline/online research, ContextTier)
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

### Outputs

- Rule file: `rules/NNN-technology-aspect.md`
- Entry in `RULES_INDEX.md` (correct numeric position)
- Schema-validated (0 CRITICAL errors)

### Safety Constraints

- Write only to `rules/` and `RULES_INDEX.md`
- Treat external sources as untrusted; prefer official docs

## Critical Execution Protocol

### Pre-Flight Checks (Required)

1. Search `RULES_INDEX.md` for existing technology rules
2. Identify domain range (e.g., 420-449 for JavaScript)
3. Determine next available rule number
4. Load domain core rule and governance rules

See `workflows/discovery.md` for domain mappings and detailed discovery process.

### Required Behavior

- Execute all 5 phases sequentially (no skipping)
- Run `ai-rules new` for initial structure
- Conduct web research for current best practices
- Fill ALL sections (no placeholders)
- Run `ai-rules validate` in loop until exit code 0
- Add entry to `RULES_INDEX.md` in numeric order

### Forbidden

- Skipping phases to save time
- Manually creating structure without `ai-rules new`
- Proceeding with CRITICAL validation errors
- Using placeholder text
- Single-pass validation without re-checking

## Workflow

### [OPTIONAL] Timing Start

**When:** Only if `timing_enabled: true` in inputs  
**MODE:** Safe in PLAN mode

**See:** `../skill-timing/workflows/timing-start.md`

**Action:** Capture `run_id` in working memory for later use.

### [OPTIONAL] Checkpoint: skill_loaded

**When:** Only if timing was started  
**Checkpoint name:** `skill_loaded`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Phase 1: Discovery & Research

Identify domain, assign rule number, research best practices. Extract 10-15 semantic keywords.

**See:** `workflows/discovery.md` for domain mappings, search commands, and research strategy.

### [OPTIONAL] Checkpoint: discovery_complete

**When:** Only if timing was started  
**Checkpoint name:** `discovery_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Phase 2: Template Generation

Execute `ai-rules new` to create validated structure with v3.2 sections and Markdown Contract headers.

**See:** `workflows/template-gen.md` for command syntax and verification steps.

### [OPTIONAL] Checkpoint: template_generated

**When:** Only if timing was started  
**Checkpoint name:** `template_generated`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Phase 3: Content Population

Fill all sections with researched content. Add minimum 2 code examples and 2 anti-patterns. No placeholders allowed.

**See:** `workflows/content-population.md` for section-by-section guidance and requirements.

### [OPTIONAL] Checkpoint: content_populated

**When:** Only if timing was started  
**Checkpoint name:** `content_populated`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Phase 4: Validation & Iteration

Run `schema_validator.py` in loop until exit code 0. Apply fixes for CRITICAL errors. Max 3 iterations. If CRITICAL errors remain after 3 iterations: STOP, report unresolved errors to user with specific fix guidance.

**See:** `workflows/validation.md` for error resolution patterns and validation loop implementation.

### [OPTIONAL] Checkpoint: validation_complete

**When:** Only if timing was started  
**Checkpoint name:** `validation_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Phase 5: Indexing

Add entry to `RULES_INDEX.md` in correct numeric position with matching keywords.

**See:** `workflows/indexing.md` for entry format and verification steps.

### [OPTIONAL] Checkpoint: indexing_complete

**When:** Only if timing was started  
**Checkpoint name:** `indexing_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### [OPTIONAL] Timing End (Compute)

**When:** Only if timing was started  
**MODE:** Safe in PLAN mode (outputs to STDOUT only)

**See:** `../skill-timing/workflows/timing-end.md` (Step 1)

**Action:** Capture STDOUT output for metadata embedding.

### [MODE TRANSITION: PLAN → ACT]

Request user ACT authorization before file modifications in Phases 2-5.

### [OPTIONAL] Timing End (Embed)

**When:** Only if timing was started  
**MODE:** Requires ACT mode (appends metadata to file)

**See:** `../skill-timing/workflows/timing-end.md` (Step 2)

**Action:** Parse STDOUT, append timing metadata section to rule file.

## Quick Validation

Fast inline checks without external dependencies:

```python
# Keyword count (5-20 required)
def check_keywords(line: str) -> tuple[bool, int]:
    keywords = [k.strip() for k in line.split(',') if k.strip()]
    return (5 <= len(keywords) <= 20, len(keywords))

# Filename format (NNN-lowercase-hyphenated)
import re
def is_valid_filename(name: str) -> bool:
    return bool(re.match(r'^\d{3}-[a-z]+(-[a-z]+)*$', name))

# TokenBudget format (~NUMBER)
def check_token_budget(value: str) -> bool:
    return bool(re.match(r'^~\d+$', value.strip()))

# ContextTier validation
VALID_TIERS = {'Critical', 'High', 'Medium', 'Low'}
def check_context_tier(tier: str) -> bool:
    return tier.strip() in VALID_TIERS
```

Full validation: `python scripts/schema_validator.py rules/<file>.md`

## Validation Gates

All must pass before completion:

- [ ] Domain range identified, number available
- [ ] `template_generator.py` executed successfully
- [ ] Keywords: 10-15 comma-separated terms
- [ ] TokenBudget: ~NUMBER format
- [ ] All 9 sections present in order
- [ ] Contract has 6 XML tags before line 160
- [ ] Minimum 2 code examples
- [ ] Minimum 2 anti-patterns
- [ ] `schema_validator.py` exit code 0 (0 CRITICAL errors)
- [ ] Entry added to `RULES_INDEX.md`

## Examples

### Example 1: DaisyUI Rule

```markdown
Create a new Cursor rule documenting DaisyUI best practices.

Expected output:
- rules/422-daisyui-core.md
- Validates with 0 CRITICAL errors
- Added to RULES_INDEX.md
```

### Example 2: pytest-mock Rule

```markdown
Create a new Cursor rule documenting pytest-mock best practices.

Expected output:
- rules/209-python-pytest-mock.md (if 209 is next in 200-299)
- Validates with 0 CRITICAL errors
- Added to RULES_INDEX.md
```

### Example 3: Snowflake Hybrid Tables Rule

```markdown
Create a new Cursor rule documenting Snowflake Hybrid Tables.

Expected output:
- rules/125-snowflake-hybrid-tables.md (if 125 is next in 100-199)
- Validates with 0 CRITICAL errors
- Added to RULES_INDEX.md
```

**More examples:** See `examples/` for detailed walkthroughs (frontend, python, snowflake, edge-cases).

## Anti-Patterns

Common mistakes to avoid:
- Manual structure creation (always use `ai-rules new`)
- Single-pass validation (loop until exit code 0)
- Proceeding with CRITICAL errors (must resolve first)
- Placeholder text (complete all sections before validation)

**See:** `examples/edge-cases.md` for detailed examples and resolution strategies.

## Success Criteria

Measurable outcomes for rule creation:

- [ ] Generated rule passes `ai-rules validate` with zero errors
- [ ] Keywords count is within 5-20 range
- [ ] All v3.2 required sections present (Scope, References, Contract subsections)
- [ ] TokenBudget accurate within ±10%
- [ ] Rule indexed in RULES_INDEX.md via `ai-rules index`
- [ ] Minimum 2 code examples with proper syntax highlighting
- [ ] Minimum 2 anti-patterns documented

## Out of Scope

This skill does NOT handle:

- Modifying existing rules (use rule-reviewer skill)
- Rule deprecation workflows
- Cross-rule dependency management
- Production deployment decisions
- Bulk rule migrations

## Rollback Strategy

Recovery guidance for common failure scenarios:

1. **Failed validation:** Re-run `ai-rules validate` and apply suggested fixes
2. **Schema mismatch:** Regenerate from `ai-rules new` with correct domain
3. **Index corruption:** Rebuild with `ai-rules index --rebuild`
4. **Git recovery:** `git checkout -- rules/NNN-*.md` for uncommitted changes
5. **Partial completion:** Resume from last successful phase checkpoint

## Related Skills

### Quality Assurance

After creating a rule, validate with **rule-reviewer** skill:

```
Use the rule-reviewer skill.

target_file: rules/<created-rule>.md
review_date: <today>
review_mode: FULL
model: <current>
```

**Quality threshold:** Score ≥ 75/100, no CRITICAL issues, no HIGH issues in Actionability/Completeness. If score <75: report issues and recommend specific fixes before considering rule complete.

## References

### CLI Commands

- `ai-rules new` - Create rule templates (v3.2 compliant)
- `ai-rules validate` - Validate against v3.2 schema
- `ai-rules index` - Maintain RULES_INDEX.md

### Rules

- `rules/002-rule-governance.md` - v3.2 schema requirements
- `rules/002a-rule-creation.md` - Detailed workflow
- `rules/002b-rule-optimization.md` - Token budget guidance
- `rules/002e-schema-validator-usage.md` - Validation commands

### Documentation

- `RULES_INDEX.md` - Semantic discovery index
- `schemas/rule-schema.yml` - v3.2 s