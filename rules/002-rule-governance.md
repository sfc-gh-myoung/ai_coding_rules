# Rule Governance: Schema Standards

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** rule governance, schema, metadata requirements, required sections, Contract XML tags, validation, schema compliance, rule structure, semantic discovery, RULES_INDEX
**TokenBudget:** ~2300
**ContextTier:** Critical
**Depends:** rules/000-global-core.md

## Purpose

Defines schema standards for AI coding rule files, ensuring consistent structure, semantic discoverability, and automated validation for AI agents creating and maintaining rules.

## Rule Scope

All rule files in the ai_coding_rules repository must comply with schema standards defined in schemas/rule-schema.yml

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Required metadata (5 fields):** RuleVersion (vX.Y.Z), Keywords (10-15 terms), TokenBudget (~NUMBER), ContextTier (Critical/High/Medium/Low), Depends (at least one dependency)
- **RuleVersion field is REQUIRED** - Enables version tracking for issue reporting (semantic versioning: v1.0.0)
- **Keywords field is CRITICAL** - Enables semantic discovery and automatic rule loading (10-15 comma-separated terms)
- **9 required sections** - Purpose, Rule Scope, Quick Start TL;DR, Contract, Post-Execution Checklist, Validation, Output Format Examples, References (+ optional: Key Principles, Anti-Patterns)
- **Contract with 6 XML tags** - `<inputs_prereqs>`, `<mandatory>`, `<forbidden>`, `<steps>`, `<output_format>`, `<validation>`
- **Minimum 3 Essential Patterns** - No maximum limit, quality over quantity
- **Validation command** - `python3 scripts/schema_validator.py rules/NNN-rule.md`

**Pre-Execution Checklist:**
- [ ] Metadata present: RuleVersion (vX.Y.Z), Keywords (10-15), TokenBudget, ContextTier, Depends
- [ ] All 9 required sections present in correct order
- [ ] Contract section has all 6 XML tags before line 160
- [ ] Quick Start has minimum 3 Essential Patterns
- [ ] Post-Execution Checklist has 5+ verification items
- [ ] Output Format Examples has concrete code samples
- [ ] Validation command runs without CRITICAL errors

## Contract

<inputs_prereqs>
Rule creation/maintenance task; schema understanding; access to schemas/rule-schema.yml
</inputs_prereqs>

<mandatory>
Text editor; schema_validator.py; access to existing rules/ directory; schemas/rule-schema.yml file
</mandatory>

<forbidden>
Creating rules without metadata; skipping validation; using outdated schema (v2.x); emojis in rule files
</forbidden>

<steps>
1. Review schema requirements (metadata, sections, XML tags)
2. Review existing rules in same category for patterns (use 002a-rule-creation-guide.md for workflow)
3. Fill 5 required metadata fields correctly (RuleVersion, Keywords, TokenBudget, ContextTier, Depends)
4. Write all 9 required sections in order
5. Add Contract section with 6 XML tags
6. Validate with schema_validator.py before committing
</steps>

<output_format>
Markdown file (.md) with v3.0 metadata and required sections
</output_format>

<validation>
- schema_validator.py passes with zero CRITICAL errors
- All 5 metadata fields present and correctly formatted
- All 9 required sections present in correct order
- Contract has all 6 XML tags
- RuleVersion: semantic version format (vX.Y.Z)
- Keywords count: 10-15 terms
</validation>

## Schema Requirements

### Metadata Fields (6 Required)

**Required Fields:**
- **SchemaVersion:** `vX.Y` format, must match current schema (e.g., v3.1) - CRITICAL
- **RuleVersion:** Semantic version `vX.Y.Z` (e.g., v1.0.0)
- **Keywords:** 10-15 comma-separated terms for discovery
- **TokenBudget:** `~NUMBER` format (e.g., ~1200)
- **ContextTier:** One of: Critical, High, Medium, Low
- **Depends:** At least one rule dependency (e.g., `rules/000-global-core.md`)

**Field Order:** Must appear in exact order: RuleVersion, Keywords, TokenBudget, ContextTier, Depends

### Required Sections (9 Mandatory)

**Required Sections (in order):**
1. **Purpose** - 1-2 sentences explaining rule purpose
2. **Rule Scope** - Single line scope statement
3. **Quick Start TL;DR** - 30-second overview with Essential Patterns (min 3) + Pre-Execution Checklist (5-7 items)
4. **Contract** - Structured contract with 6 XML tags (must appear before line 160)
5. **Key Principles** - Core concepts (optional for simple rules)
6. **Anti-Patterns** - Problem/Correct Pattern pairs (optional but strongly recommended)
7. **Post-Execution Checklist** - Verification checklist (5+ items, different from Pre-Execution)
8. **Validation** - Success checks and negative tests
9. **References** - Related rules and external resources
| **Output Format Examples** | 9 | [PASS] | Concrete code examples (min 1 code block) |
| **References** | 10 | [PASS] | External docs + related rules |

### Context Preservation Mechanisms

**Primary Mechanism: Natural Language Markers (Universal)**

All rules use natural language importance markers that work across all LLM providers:

**Importance Markers:**
- **CRITICAL: DO NOT SUMMARIZE** - Bootstrap files (AGENTS.md, 000-global-core.md), never summarize
- **CORE RULE: PRESERVE WHEN POSSIBLE** - Domain cores (*-core.md files), preserve for domain tasks
- **FOUNDATION RULE: PRESERVE WHEN POSSIBLE** - Governance rules (002-series), preserve for rule work
- **(none)** - Standard rules, can be summarized if needed

**Secondary Mechanism: ContextTier Metadata (Project-Specific)**

The `ContextTier` field (Critical/High/Medium/Low) provides fine-grained prioritization
within natural language tiers. This metadata is validated by schema but not universally
recognized by all LLMs - rely on natural language markers as primary signal.

See `000-global-core.md`, section "Context Window Management Protocol" for full details.

### Contract XML Tags (6 Required)

The Contract section must include these 6 XML tags in this order:

```markdown
## Contract

<inputs_prereqs>
What the agent needs to have/know before starting
</inputs_prereqs>

<mandatory>
Required tools, libraries, access permissions
</mandatory>

<forbidden>
Prohibited actions, tools, or approaches
</forbidden>

<steps>
1. First step
2. Second step
3. Third step (minimum 5 steps, maximum 10)
</steps>

<output_format>
Description of expected output format
</output_format>

<validation>
How to verify success (success criteria)
</validation>
```

**Note:** Contract section must appear before line 160 to ensure agent reads it early.

## Validation Process

### Running the Validator

```bash
# Validate single file
python3 scripts/schema_validator.py rules/NNN-rule.md

# Validate all rules
python3 scripts/schema_validator.py rules/

# Verbose output with detailed checks
python3 scripts/schema_validator.py rules/NNN-rule.md --verbose
```

### Success Criteria

- [PASS] **CRITICAL errors:** 0
- [WARN] **HIGH errors:** Acceptable if intentional (e.g., model-specific emojis in 002c)
- [INFO] **MEDIUM/INFO:** Review and fix if possible

### Common Validation Errors

**Metadata Errors:**
- **Missing metadata field** - Add missing Keywords, TokenBudget, ContextTier, or Depends in correct order
- **Keywords count wrong** - Adjust to 10-15 comma-separated terms
- **TokenBudget format** - Use `~NUMBER` format (e.g., ~500, ~1200)

**Structure Errors:**
- **Missing required section** - Add missing section per schema structure
- **Contract missing XML tag** - Add missing tag: `<inputs_prereqs>`, `<mandatory>`, etc.
- **Section order wrong** - Reorder sections: Purpose, then Rule Scope, then Quick Start, then Contract...

**For detailed error resolution:** See `002d-schema-validator-usage.md`

## Key Principles

- **Priority Hierarchy:** All rules follow the design priorities defined in `000-global-core.md`:
  1. **Agent understanding and execution reliability** (PRIMARY) - Instructions must be deterministic
  2. **Token and context window efficiency** (SECONDARY) - Minimize without sacrificing clarity
  3. **Human readability** (TERTIARY) - Organize logically for reviewers
- **Schema Compliance:** All rules must validate against schemas/rule-schema.yml with zero CRITICAL errors
- **Semantic Discovery:** Keywords (10-15) enable AI agents to automatically discover relevant rules
- **Progressive Disclosure:** Quick Start TL;DR provides 30-second overview, detailed sections follow
- **Validation-First:** Always run schema_validator.py before committing rule changes
- **Text-Only Format:** No emojis in rule files (schema requirement for universal compatibility)
- **Agent-First Formatting:** See `002e-agent-optimization.md` for required formatting patterns

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Keyword Stuffing for Discovery

**Problem:** Adding irrelevant or duplicate keywords to meet the 10-15 requirement, or using overly generic terms that don't aid semantic discovery.

**Why It Fails:** Pollutes RULES_INDEX.md with false matches, causes wrong rules to load, wastes agent context budget on irrelevant rules, and degrades rule discovery accuracy.

**Correct Pattern:**
```markdown
# BAD: Keyword stuffing
**Keywords:** code, coding, programming, software, development, best, practices, rules, guidelines, standards, quality, good, better, best

# GOOD: Semantic, specific keywords
**Keywords:** Snowflake SQL, query optimization, CTE patterns, warehouse sizing, clustering keys, materialized views, query profiling, cost reduction, performance tuning, execution plans
```

### Anti-Pattern 2: Circular or Missing Dependencies

**Problem:** Declaring dependencies that create circular references, or omitting critical dependencies that the rule assumes are loaded.

**Why It Fails:** Circular dependencies cause infinite loading loops or stack overflows. Missing dependencies mean agents lack required context, leading to incomplete or incorrect rule application.

**Correct Pattern:**
```markdown
# BAD: Circular dependency
# 100-snowflake-core.md depends on 101-snowflake-streamlit-core.md
# 101-snowflake-streamlit-core.md depends on 100-snowflake-core.md

# GOOD: Hierarchical dependencies
# 101-snowflake-streamlit-core.md
**Depends:** rules/100-snowflake-core.md, rules/000-global-core.md

# Rule 100 is foundation, 101 extends it (no reverse dependency)
```

## Post-Execution Checklist

- [ ] New/updated rule has all 4 metadata fields correctly formatted
- [ ] All 9 required sections present in correct order
- [ ] Contract section includes all 6 XML tags
- [ ] Quick Start TL;DR has min 3 Essential Patterns
- [ ] Keywords count is 10-15 terms (semantic and discoverable)
- [ ] schema_validator.py runs with 0 CRITICAL errors
- [ ] TokenBudget reflects actual file size (±10% acceptable)
- [ ] File added to RULES_INDEX.md with keywords
- [ ] Dependencies declared in Depends metadata
- [ ] No emojis in rule file content

## Validation

**Success Checks:**
- `python3 scripts/schema_validator.py rules/NNN-rule.md` returns zero CRITICAL errors
- All metadata fields parse correctly
- All required sections found in correct order
- Contract XML tags validated successfully
- Keywords count within 10-15 range

**Negative Tests:**
- Missing metadata field triggers CRITICAL error
- Wrong section order triggers HIGH error
- Missing Contract XML tag triggers CRITICAL error
- Keywords <10 or >15 triggers HIGH error
- TokenBudget without tilde triggers MEDIUM error

## Output Format Examples

```bash
# Create new rule file
vim rules/NNN-new-rule.md

# Fill metadata and all required sections
# Update: Keywords, TokenBudget, ContextTier, Depends

# Validate
python3 scripts/schema_validator.py rules/NNN-new-rule.md

# Expected output (success):
================================================================================
VALIDATION REPORT: rules/NNN-new-rule.md
================================================================================
[PASS] Passed: 458 checks

[PASS] RESULT: PASSED
================================================================================

# Add to index
echo "| NNN-new-rule | Description | Keywords here |" >> RULES_INDEX.md
```

```yaml
# schemas/rule-schema.yml structure (reference)
version: "3.0"
metadata:
  required_fields:
    - Keywords (10-15 items)
    - TokenBudget (~NUMBER format)
    - ContextTier (enum: Critical/High/Medium/Low)
    - Depends (min 1 dependency)
structure:
  required_sections: 9 sections
  Contract_XML_tags: 6 tags required
```

## References

### Related Rules
- **Rule Creation Workflow**: `002a-rule-creation-guide.md` - Step-by-step guide for creating new rules
- **Optimization Guide**: `002b-rule-optimization.md` - Token budgets, performance tuning, model-specific tips
- **Advanced Patterns**: `002c-advanced-rule-patterns.md` - System prompt altitude, investigation-first, multi-session workflows
- **Validator Usage**: `002d-schema-validator-usage.md` - Detailed validator commands, error interpretation, CI/CD integration
- **Global Core**: `000-global-core.md` - Foundation for all rules

### External Documentation
- **Schema Definition**: `schemas/rule-schema.yml` - Authoritative schema with validation rules
- **Rules Index**: `RULES_INDEX.md` - Master index of all rules with keywords

### Schema File Location
All rules must validate against: `schemas/rule-schema.yml`
