# Rule Creator Skill

A Claude skill for reproducibly creating production-ready Cursor rules following schema standards by orchestrating existing automation tools (`template_generator.py` and `schema_validator.py`).

## Overview

This skill automates the complete rule creation workflow from discovery through validation, ensuring all generated rules:
- Pass schema validation with 0 CRITICAL errors
- Follow schema requirements exactly
- Reflect current (2024-2025) best practices
- Are immediately usable in Cursor

## Skill Formats

This repository provides a Claude Code–compliant structured skill:

**Directory:** `skills/rule-creator/`

**Entrypoint:** `skills/rule-creator/SKILL.md`

## Quick Start

### Step 1: Prerequisites

Ensure you have:
- Python 3.11+ with PyYAML installed
- Access to `rules/`, `scripts/`, and `RULES_INDEX.md`
- Loaded governance rules:
  - `rules/000-global-core.md`
  - `rules/002-rule-governance.md`
  - `rules/002a-rule-creation-guide.md`
  - `rules/002b-rule-optimization.md`
  - `rules/002d-schema-validator-usage.md`

### Step 2: Load the Skill

Open:
```
skills/rule-creator/SKILL.md
```

### Step 3: Request Rule Creation

```
Create a new Cursor rule documenting [TECHNOLOGY] best practices following schema
```

**Examples:**
- "Create a new rule for DaisyUI best practices following schema"
- "Create a new rule for pytest-mock usage following schema"
- "Create a new rule for Snowflake Hybrid Tables following schema"

### Step 4: Follow Agent Workflow

The agent will execute 5 phases automatically:
1. **Discovery:** Search RULES_INDEX.md, research best practices
2. **Template Generation:** Run `template_generator.py`
3. **Content Population:** Fill all sections with researched content
4. **Validation Loop:** Run `schema_validator.py` until 0 CRITICAL errors
5. **Indexing:** Add to RULES_INDEX.md

### Step 5: Verify Output

Check that:
- File exists: `rules/NNN-technology-aspect.md`
- Validation passed: `python scripts/schema_validator.py rules/NNN-technology-aspect.md` returns exit code 0
- Indexed: Entry present in `RULES_INDEX.md`
- Loadable: `rules/NNN-technology-aspect.md` exists and contains the new rule content

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    5-PHASE WORKFLOW                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Phase 1: Discovery & Research                          │
│    ├─ Search RULES_INDEX.md for domain                  │
│    ├─ Identify next available number                    │
│    ├─ Web search for best practices                     │
│    └─ Extract keywords and patterns                     │
│                                                          │
│  Phase 2: Template Generation                           │
│    ├─ Execute: template_generator.py                    │
│    ├─ Verify structure (9 sections, 6 XML tags)         │
│    └─ Confirm Contract before line 160                  │
│                                                          │
│  Phase 3: Content Population                            │
│    ├─ Fill metadata (Keywords, TokenBudget, etc.)       │
│    ├─ Write all required sections                       │
│    └─ Add code examples and anti-patterns               │
│                                                          │
│  Phase 4: Validation Loop (Max 3 iterations)            │
│    ├─ Execute: schema_validator.py                      │
│    ├─ Parse errors (CRITICAL/HIGH/MEDIUM)               │
│    ├─ Apply fixes                                        │
│    └─ Re-validate until exit code 0                     │
│                                                          │
│  Phase 5: Indexing                                      │
│    ├─ Add entry to RULES_INDEX.md                       │
│    ├─ Insert in correct numeric position                │
│    └─ Verify table formatting                           │
│                                                          │
│  ✅ Production-ready rule created                        │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
skills/rule-creator/
├── SKILL.md               # Main skill instructions (Claude Code entrypoint)
├── PROMPT.md              # Rule creation prompt template and workflow
├── README.md              # This file - usage documentation
├── VALIDATION.md          # Skill self-validation procedures
├── examples/              # Complete workflow examples
│   ├── frontend-example.md    # DaisyUI (JavaScript 420-449)
│   ├── python-example.md      # pytest-mock (Python 200-299)
│   ├── snowflake-example.md   # Hybrid Tables (Snowflake 100-199)
│   └── edge-cases.md          # Ambiguous scenarios and resolutions
├── tests/                 # Skill test cases
│   ├── README.md              # Test overview and instructions
│   ├── test-inputs.md         # Input validation test cases
│   └── test-workflows.md      # Workflow execution test cases
└── workflows/             # Phase-specific detailed guides
    ├── discovery.md          # Phase 1: Discovery & Research
    ├── template-gen.md       # Phase 2: Template Generation
    ├── content-population.md # Phase 3: Content Population
    ├── validation.md         # Phase 4: Validation Loop
    └── indexing.md           # Phase 5: Indexing
```

## Domain Ranges Reference

| Range | Domain | Examples |
|-------|--------|----------|
| 000-099 | Core/Foundational | 000-global-core, 002-rule-governance |
| 100-199 | Snowflake | 100-snowflake-core, 125-hybrid-tables |
| 200-299 | Python | 200-python-core, 209-pytest-mock |
| 300-399 | Shell/Bash | 300-bash-scripting-core |
| 400-499 | Docker/Containers | 350-docker-best-practices |
| 420-449 | JavaScript/Frontend | 420-javascript-core, 422-daisyui-core |
| 500-599 | Data Science | 920-data-science-analytics |
| 600-699 | Golang | 600-golang-core |
| 800-899 | Project Management | 800-project-changelog, 820-taskfile |
| 900-999 | Demos/Examples | 900-demo-creation |

## Examples

### Example 1: Frontend Framework (DaisyUI)

**Request:**
```
Create a new rule for DaisyUI best practices following schema
```

**Result:**
- File: `rules/422-daisyui-core.md`
- Domain: 420-449 (JavaScript/Frontend)
- Time: ~19 minutes
- Iterations: 2
- Status: ✅ Production-ready

**See:** `examples/frontend-example.md` for complete walkthrough

### Example 2: Python Library (pytest-mock)

**Request:**
```
Create a new rule for pytest-mock usage following schema
```

**Result:**
- File: `rules/209-python-pytest-mock.md`
- Domain: 200-299 (Python)
- Time: ~17 minutes
- Iterations: 1
- Status: ✅ Production-ready

**See:** `examples/python-example.md` for complete walkthrough

### Example 3: Snowflake Feature (Hybrid Tables)

**Request:**
```
Create a new rule for Snowflake Hybrid Tables following schema
```

**Result:**
- File: `rules/125-snowflake-hybrid-tables.md`
- Domain: 100-199 (Snowflake)
- Time: ~23 minutes
- Iterations: 2
- Status: ✅ Production-ready

**See:** `examples/snowflake-example.md` for complete walkthrough

## Validation Gates

All rules must pass these gates before completion:

- [x] RULES_INDEX.md searched for existing rules
- [x] Domain range identified (e.g., 420-449)
- [x] Next available number determined
- [x] `template_generator.py` executed successfully
- [x] Template verified (9 sections, 6 XML tags)
- [x] All metadata fields filled correctly
- [x] Keywords: 10-15 comma-separated terms
- [x] TokenBudget: ~NUMBER format (e.g., ~1200)
- [x] ContextTier: valid value (Critical|High|Medium|Low)
- [x] Contract placed before line 160
- [x] `schema_validator.py` returns exit code 0
- [x] Rule added to RULES_INDEX.md

## Common Error Patterns and Fixes

### Error 1: Keywords Count Wrong

**Error:**
```
[Metadata] Keywords count: 9 (expected 10-15)
```

**Fix:** Add 1-6 more keywords to reach 10-15 range

### Error 2: TokenBudget Format Invalid

**Error:**
```
[Metadata] TokenBudget format invalid: expected ~NUMBER
```

**Fix:** Change `1200` to `~1200` (tilde required)

### Error 3: Missing Contract XML Tag

**Error:**
```
[Contract] Missing XML tag: <validation>
```

**Fix:** Add missing tag to Contract section (all 6 required)

### Error 4: Contract After Line 160

**Error:**
```
[Contract] Contract section after line 160 (current line: 185)
```

**Fix:** Move Contract section earlier (typically after Quick Start TL;DR)

## Troubleshooting

### Issue: Domain Unclear

**Symptom:** Technology could fit multiple domains

**Action:**
1. Check RULES_INDEX.md for similar technologies
2. If ambiguous, ask user to clarify
3. Example: "React Testing Library" → Frontend (440s) or Testing (400s)?

### Issue: Validation Fails After 3 Iterations

**Symptom:** Still have CRITICAL errors after 3 attempts

**Action:**
1. Review `rules/002d-schema-validator-usage.md`
2. Check similar rules for structure examples
3. Run with `--verbose` flag for detailed output
4. Request user assistance

### Issue: Template Generation Fails

**Symptom:** `template_generator.py` returns error

**Common causes:**
- Invalid filename format (must be `NNN-technology-aspect`)
- Wrong capitalization (must be lowercase)
- Underscores instead of hyphens

**Fix:**
- Verify 3-digit number: `42` → `042` or `422`
- Use lowercase: `DaisyUI` → `daisyui`
- Use hyphens: `pytest_mock` → `pytest-mock`

## Performance Metrics

| Metric | Target | Typical |
|--------|--------|---------|
| Total time | < 30 min | 17-23 min |
| Validation iterations | ≤ 3 | 1-2 |
| Exit code 0 | 100% | ✓ |
| CRITICAL errors | 0 | ✓ |
| Manual intervention | 0% | ✓ |

**Comparison to manual rule creation:**
- Manual: 45-60 minutes
- With skill: 17-23 minutes
- **Time savings: ~60-70%**

## Best Practices

### DO:
✓ Load required governance rules before starting
✓ Use web search for current (2024-2025) best practices
✓ Include 2+ anti-patterns with code examples
✓ Run validation loop until exit code 0
✓ Add keywords that enable semantic discovery
✓ Use `rules/` prefix for Related Rules in References

### DON'T:
✗ Skip template_generator.py (manual structure error-prone)
✗ Proceed with CRITICAL errors (blocks completion)
✗ Use placeholder text (populate all sections)
✗ Forget tilde in TokenBudget (~1200 not 1200)
✗ Omit Contract XML tags (all 6 required)
✗ Place Contract after line 160 (must be early)

## Advanced Usage

### Custom ContextTier Selection

Override default "Medium" tier when appropriate:

```
Create a new rule for [CORE FRAMEWORK] following schema with High context tier
```

**Tier guidelines:**
- **Critical:** <500 tokens, always-loaded (e.g., 000-global-core)
- **High:** 500-1500 tokens, domain foundations
- **Medium:** 1500-3000 tokens, most new rules (default)
- **Low:** 3000-5000 tokens, specialized/reference

### Specifying Aspect

For non-core rules, specify aspect:

```
Create a new rule for pytest security testing patterns following schema
```

Would create: `209-python-pytest-security.md` (aspect: "security")

### Multiple Dependencies

If rule depends on multiple domain rules:

```
Create a new rule for Snowflake+Python integration patterns following schema
```

Agent will add both `rules/100-snowflake-core.md` and `rules/200-python-core.md` to Depends

## Support and References

### Detailed Phase Guides

For step-by-step phase instructions:
- **Phase 1:** `workflows/discovery.md`
- **Phase 2:** `workflows/template-gen.md`
- **Phase 3:** `workflows/content-population.md`
- **Phase 4:** `workflows/validation.md`
- **Phase 5:** `workflows/indexing.md`

### Example Walkthroughs

For complete end-to-end examples:
- **Frontend:** `examples/frontend-example.md` (DaisyUI)
- **Python:** `examples/python-example.md` (pytest-mock)
- **Snowflake:** `examples/snowflake-example.md` (Hybrid Tables)

### Related Documentation

- **Rule Governance:** `rules/002-rule-governance.md` - schema standards
- **Creation Guide:** `rules/002a-rule-creation-guide.md` - Manual rule creation
- **Optimization:** `rules/002b-rule-optimization.md` - Token budgets
- **Validator Usage:** `rules/002d-schema-validator-usage.md` - Validation details
- **Rules Index:** `RULES_INDEX.md` - Master index for discovery
- **Prompt Template:** `PROMPT.md` - Rule creation prompt template (colocated in this skill folder)

### Tool Documentation

- **Template Generator:** `@scripts/template_generator.py` - Run with `--help`
- **Schema Validator:** `@scripts/schema_validator.py` - Run with `--help`

## Success Criteria

Rule creation is successful when:
- ✅ File exists at `rules/NNN-technology-aspect.md`
- ✅ `schema_validator.py` returns exit code 0
- ✅ Rule added to `RULES_INDEX.md` in correct position
- ✅ Rule file exists under `rules/` and can be opened/read
- ✅ Metadata enables semantic discovery
- ✅ Content reflects current (2024-2025) best practices
- ✅ All 9 required sections present with quality content
- ✅ Contract has 6 XML tags before line 160
- ✅ 2+ anti-patterns with code examples included

## Version History

- **v1.1.0** (2025-12-15): Enhanced skill structure
  - Added version, author, tags, dependencies to SKILL.md frontmatter
  - Improved description with trigger keywords and domain coverage
  - Added inline validation snippets for quick checks
  - Added edge-cases.md with 10 documented scenarios
  - Added tests/ folder with input and workflow test cases
  - Added VALIDATION.md for skill self-validation
  - Cross-referenced with rule-reviewer for quality assurance
- **v1.0.0** (2024-12-11): Initial release
  - 5-phase workflow with script orchestration
  - Claude Code–compliant structured skill format
  - Complete examples for 3 domains
  - Phase-specific workflow guides
  - Comprehensive error handling

## Contributing

To improve this skill:
1. Test with new technology domains
2. Document edge cases in workflow guides
3. Add more examples to `examples/`
4. Report validation patterns to enhance error handling
5. Suggest improvements to phase workflows

## License

This skill is part of the AI Coding Rules project. Use freely within your organization.

