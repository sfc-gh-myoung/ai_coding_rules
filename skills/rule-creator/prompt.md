# Rule Creator Skill - Main Instructions

## Overview

This structured Claude skill creates production-ready Cursor rules following v3.0 schema by orchestrating existing automation scripts and validation tools. The workflow consists of 5 phases executed sequentially, with automatic validation loops ensuring 0 CRITICAL errors.

## Required Context Files

Before starting, load these rules for complete context:

```
@rules/000-global-core.md (foundation)
@rules/002-rule-governance.md (v3.0 schema standards)
@rules/002a-rule-creation-guide.md (creation workflow)
@rules/002b-rule-optimization.md (token budgets and optimization)
@rules/002d-schema-validator-usage.md (validation commands and error resolution)
```

## Skill Architecture

```
skill-creator/
├── skill.json              # Skill configuration and metadata
├── prompt.md              # This file - main instructions
├── examples/              # Complete walkthrough examples
│   ├── frontend-example.md    # DaisyUI (JavaScript/Frontend)
│   ├── python-example.md      # Python library rule
│   └── snowflake-example.md   # Snowflake feature rule
├── workflows/             # Phase-specific detailed guides
│   ├── discovery.md          # Phase 1: Discovery & Research
│   ├── template-gen.md       # Phase 2: Template Generation
│   ├── content-population.md # Phase 3: Content Population
│   ├── validation.md         # Phase 4: Validation Loop
│   └── indexing.md           # Phase 5: RULES_INDEX update
└── README.md              # Usage documentation
```

## Quick Start

When user requests a new rule:

1. **Load this skill:** Read `skill.json` and `prompt.md`
2. **Follow phase sequence:** Execute phases 1-5 in order
3. **Reference workflows:** Use `workflows/*.md` for detailed phase instructions
4. **Check examples:** Consult `examples/*.md` for similar technology patterns
5. **Validate continuously:** Run `schema_validator.py` after Phase 3, iterate in Phase 4

## Phase Sequence

### Phase 1: Discovery & Research
**Workflow:** `@skills/rule-creator/workflows/discovery.md`

**Actions:**
1. Parse user request to extract technology name
2. Search `@RULES_INDEX.md` for existing related rules
3. Identify domain range (000-099, 100-199, 200-299, etc.)
4. Determine next available number
5. Load domain core rule for context
6. Web search: "2024 2025 [TECHNOLOGY] best practices"
7. Extract 10-15 keywords, patterns, anti-patterns

**Output:** Domain number, keywords list, best practices summary

---

### Phase 2: Template Generation
**Workflow:** `@skills/rule-creator/workflows/template-gen.md`

**Actions:**
1. Determine ContextTier (Critical|High|Medium|Low)
2. Execute: `python scripts/template_generator.py NNN-tech-aspect --context-tier TIER`
3. Verify template created with all 9 sections
4. Confirm Contract has 6 XML tags

**Output:** `rules/NNN-technology-aspect.md` with complete structure

---

### Phase 3: Content Population
**Workflow:** `@skills/rule-creator/workflows/content-population.md`

**Actions:**
1. Fill metadata (Keywords, TokenBudget, ContextTier, Depends)
2. Write Purpose (1-2 sentences)
3. Write Rule Scope (1 line)
4. Write Quick Start TL;DR (3+ Essential Patterns, 5-7 Pre-Execution Checklist)
5. Fill Contract section (6 XML tags, before line 160)
6. Write Anti-Patterns (minimum 2, with code examples)
7. Write Post-Execution Checklist (5+ items)
8. Write Validation section (Success Checks + Negative Tests)
9. Write Output Format Examples (minimum 1 code block)
10. Write References section (Related Rules + External Docs)

**Output:** Fully populated rule file ready for validation

---

### Phase 4: Validation Loop
**Workflow:** `@skills/rule-creator/workflows/validation.md`

**Actions:**
1. Run: `python scripts/schema_validator.py rules/NNN-tech-aspect.md`
2. Check exit code: 0 = pass, 1 = fail
3. If CRITICAL errors: Parse output, apply fixes, re-validate
4. Iterate maximum 3 times
5. Continue until exit code 0

**Common Fixes:**
- Keywords count: Add/remove to reach 10-15
- TokenBudget format: Change to `~1200` format
- Missing XML tag: Add to Contract section
- Contract placement: Move before line 160
- Section order: Reorder per v3.0 schema

**Output:** Validated rule with 0 CRITICAL errors

---

### Phase 5: Indexing
**Workflow:** `@skills/rule-creator/workflows/indexing.md`

**Actions:**
1. Add entry to `@RULES_INDEX.md`:
   ```
   | NNN-tech-aspect | [Scope] | [Keywords] | [Dependencies] |
   ```
2. Insert in correct numeric position
3. Verify table formatting intact

**Output:** Rule indexed and ready for use

---

## Validation Gates

All gates must pass before completion:

- [x] RULES_INDEX.md searched for existing rules
- [x] Domain range identified (e.g., 420-449)
- [x] Next available number determined
- [x] template_generator.py executed successfully
- [x] Template verified (9 sections present)
- [x] All metadata fields filled correctly
- [x] Keywords: 10-15 comma-separated terms
- [x] TokenBudget: ~NUMBER format (e.g., ~1200)
- [x] ContextTier: valid value
- [x] Contract placed before line 160
- [x] schema_validator.py returns exit code 0
- [x] Rule added to RULES_INDEX.md

## Example Usage

### User Request
```
Create a new rule documenting DaisyUI best practices following v3.0 schema
```

### Agent Execution
```
Loading skill: @skills/rule-creator/prompt.md
Loading workflows: @skills/rule-creator/workflows/*.md
Loading example: @skills/rule-creator/examples/frontend-example.md

Executing Phase 1: Discovery...
  → Searching RULES_INDEX.md for "daisyui", "javascript", "tailwind"
  → Found domain: 420-449 (JavaScript/Frontend)
  → Next available: 422
  → Keywords: daisyui, tailwind, components, ui library...

Executing Phase 2: Template Generation...
  → Running: python scripts/template_generator.py 422-daisyui-core --context-tier Medium
  → Template created: rules/422-daisyui-core.md
  → Verified: 9 sections, 6 XML tags

Executing Phase 3: Content Population...
  → Filling metadata...
  → Writing sections...
  → Contract placed at line 56 (before 160) ✓

Executing Phase 4: Validation Loop...
  → Running: python scripts/schema_validator.py rules/422-daisyui-core.md
  → Exit code: 1 (FAILED)
  → CRITICAL: Keywords count 9 (need 10-15)
  → Fix applied: Added keyword
  → Re-validating...
  → Exit code: 0 (PASSED) ✓

Executing Phase 5: Indexing...
  → Adding to RULES_INDEX.md at position 422
  → Entry added ✓

✅ Complete: rules/422-daisyui-core.md ready for use
```

## Workflow File References

For detailed phase instructions, see:
- **Phase 1:** `@skills/rule-creator/workflows/discovery.md`
- **Phase 2:** `@skills/rule-creator/workflows/template-gen.md`
- **Phase 3:** `@skills/rule-creator/workflows/content-population.md`
- **Phase 4:** `@skills/rule-creator/workflows/validation.md`
- **Phase 5:** `@skills/rule-creator/workflows/indexing.md`

## Example References

For complete walkthroughs, see:
- **Frontend:** `@skills/rule-creator/examples/frontend-example.md` (DaisyUI)
- **Python:** `@skills/rule-creator/examples/python-example.md` (Library rule)
- **Snowflake:** `@skills/rule-creator/examples/snowflake-example.md` (Feature rule)

## Error Recovery

If validation fails after 3 iterations:
1. Review `@rules/002d-schema-validator-usage.md` for error patterns
2. Check similar rules in same domain for structure examples
3. Verify section order matches v3.0 schema exactly
4. Confirm all XML tags spelled correctly
5. Request user assistance if needed

## Success Criteria

Rule creation successful when:
- ✅ File exists at `rules/NNN-technology-aspect.md`
- ✅ `schema_validator.py` returns exit code 0
- ✅ Rule added to `RULES_INDEX.md`
- ✅ Rule loads in Cursor with `@rules/` prefix
- ✅ Content reflects 2024-2025 best practices

## References

- **Skill Config:** `@skills/rule-creator/skill.json`
- **Usage Guide:** `@skills/rule-creator/README.md`
- **Rule Governance:** `@rules/002-rule-governance.md`
- **Creation Guide:** `@rules/002a-rule-creation-guide.md`
- **Optimization:** `@rules/002b-rule-optimization.md`
- **Validator Usage:** `@rules/002d-schema-validator-usage.md`

