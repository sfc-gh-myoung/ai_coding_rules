# Rule Governance: Schema Standards

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.1
**LastUpdated:** 2026-01-13
**Keywords:** rule governance, schema, metadata requirements, validation, schema compliance, rule structure, semantic discovery, RULES_INDEX, descriptive headings
**TokenBudget:** ~3800
**ContextTier:** Critical
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Schema standards (v3.2) for AI coding rule files. Defines required sections, metadata fields, Contract structure, and validation requirements. All rules must comply with `schemas/rule-schema.yml` v3.2 specifications.

**When to Load This Rule:**
- Creating new rule files (also load 002a-rule-creation.md)
- Updating existing rules (also load 002b-rule-update.md for versioning)
- Reviewing rule compliance
- Understanding schema validation requirements
- Working with schema_validator.py

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **002a-rule-creation.md** - Step-by-step guide for creating new rules
- **002b-rule-update.md** - Updating and maintaining existing rules, versioning policy
- **002c-rule-optimization.md** - Token budgets, performance tuning, model-specific tips
- **002d-advanced-rule-patterns.md** - System prompt altitude, investigation-first, multi-session workflows
- **002e-schema-validator-usage.md** - Detailed validator commands, error interpretation, CI/CD integration

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema with validation rules
- **Rules Index:** `RULES_INDEX.md` - Master index of all rules with keywords
- **[CommonMark Spec](https://spec.commonmark.org/)** - Authoritative Markdown specification (all rule files MUST comply)

## Contract

### Inputs and Prerequisites

- Rule creation or maintenance task
- Schema understanding (v3.2)
- Access to `schemas/rule-schema.yml`
- Understanding of required sections and metadata fields

### Mandatory

- Text editor
- `schema_validator.py` script
- Access to existing `rules/` directory
- `schemas/rule-schema.yml` file (v3.2)

### Forbidden

- Creating rules without metadata
- Skipping validation
- Using outdated schema (v3.0 or v3.1)
- Using emojis in rule files
- Using XML tags in Contract section (v3.2 uses Markdown headers)
- Using numbered section headings (v3.2 uses descriptive names)
- Non-compliant Markdown (must follow CommonMark spec)

### Execution Steps

1. Review v3.2 schema requirements (metadata, required sections, Markdown headers)
2. For creating new rules: use 002a-rule-creation.md workflow
3. For updating existing rules: use 002b-rule-update.md workflow
4. Fill required metadata fields correctly (SchemaVersion: v3.2, RuleVersion, Keywords: 5-20 terms, TokenBudget, ContextTier, Depends)
5. Write required sections in order: Scope, References, Contract, Anti-Patterns (optional)
6. Add Contract section with Markdown subsections (###): Inputs and Prerequisites, Mandatory, Forbidden, Execution Steps, Output Format, Validation, Design Principles, Post-Execution Checklist
7. Use descriptive section names (not numbered: "## Environment Setup" not "## 1. Environment Setup")
8. Validate with `schema_validator.py` before committing

### Output Format

Markdown file (.md) with:
- v3.2 schema metadata
- Required sections in correct order
- Contract with Markdown headers (###), not XML tags
- Descriptive section names (not numbered)
- 5-20 keywords for semantic discovery

### Validation

**Pre-Task-Completion Checks:**
- All metadata fields present and correctly formatted
- Required sections present in v3.2 order (Scope, References, Contract)
- Contract has Markdown subsections (###), not XML tags
- No numbered section headings
- Keywords count is 5-20 terms (semantic and discoverable)
- schema_validator.py ready to run

**Success Criteria:**
- `python3 scripts/schema_validator.py rules/NNN-rule.md` returns zero CRITICAL errors
- All metadata fields parse correctly
- All required sections found in correct order
- Contract Markdown subsections validated successfully
- Keywords count within 5-20 range
- RuleVersion in semantic version format (vX.Y.Z)
- TokenBudget reflects actual file size (±10% acceptable)

**Negative Tests:**
- Missing metadata field triggers CRITICAL error
- Wrong section order triggers HIGH error
- XML tags in Contract trigger HIGH error
- Numbered section headings trigger HIGH error
- Keywords <5 or >20 triggers HIGH error
- TokenBudget without tilde triggers MEDIUM error

**Error Recovery:**
- **Permission denied on rules/:** Report error, suggest checking file permissions or running as different user
- **Validator script not found:** Check scripts/ directory exists, offer to create from schema
- **Schema file missing:** Report which schema version expected, provide path to download/create

### Post-Execution Checklist

- [ ] New/updated rule has all required metadata fields correctly formatted
- [ ] SchemaVersion is v3.2
- [ ] All required sections present in v3.2 order
- [ ] Contract section uses Markdown headers (###), not XML tags
- [ ] No numbered section headings (## 1., ## 2., etc.)
- [ ] Keywords count is 5-20 terms (semantic and discoverable)
- [ ] schema_validator.py runs with 0 CRITICAL errors
- [ ] TokenBudget reflects actual file size (±10% acceptable)
- [ ] File added to RULES_INDEX.md with keywords
- [ ] Dependencies declared in Depends metadata
- [ ] No emojis in rule file content

## Schema Requirements (v3.2)

### Metadata Fields (6 Required)

**Required Fields:**
- **SchemaVersion:** `v3.2` - CRITICAL (must be v3.2 for new/updated rules)
- **RuleVersion:** Semantic version `vX.Y.Z` (e.g., v1.0.0, v2.0.0)
- **Keywords:** 5-20 comma-separated terms for semantic discovery
- **TokenBudget:** `~NUMBER` format (e.g., ~1200)
- **ContextTier:** One of: Critical, High, Medium, Low (see `002c-rule-optimization.md` for detailed tier selection guidance)
- **Depends:** At least one rule dependency (e.g., `000-global-core.md`)

**Field Order:** Must appear in exact order: SchemaVersion, RuleVersion, Keywords, TokenBudget, ContextTier, Depends

**Note on Versioning:** For guidance on when and how to increment RuleVersion and update LastUpdated fields, see `002b-rule-update.md`.

### Required Sections (v3.2)

**Required Sections (in order):**
1. **Metadata** - All 6 required fields in correct order
2. **Scope** - What the rule covers + when to load it (replaces Purpose and Rule Scope from v3.1)
3. **References** - Dependencies and external documentation (moved early for discovery)
4. **Contract** - Structured contract with Markdown subsections (###), NOT XML tags
5. **Anti-Patterns and Common Mistakes** - Optional but strongly recommended

**Numbering:**
- **FORBIDDEN:** Do NOT use numbered section headings (e.g., `## 1. Environment Setup`)
- **REQUIRED:** Use descriptive section names (e.g., `## Environment and Tooling Requirements`)

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

### Contract Structure (v3.2 - Markdown Headers)

The Contract section must use Markdown subsections (###), NOT XML tags:

```markdown
## Contract

### Inputs and Prerequisites
What the agent needs to have/know before starting

### Mandatory
Required tools, libraries, access permissions

### Forbidden
Actions/patterns that must NOT be used

### Execution Steps
1. First step (actionable, specific)
2. Second step (clear deliverable)
3. Third step (validation criteria)
...
N. Final step (completion signal)

### Output Format
Description of expected output structure

### Validation
**Pre-Task-Completion Checks:**
- Check 1
- Check 2

**Success Criteria:**
- Criterion 1
- Criterion 2

### Post-Execution Checklist
- [ ] Item 1
- [ ] Item 2
```

**Note:** Contract section must appear before line 160 to ensure agent reads it early.

## Validation Process

### Running the Validator

See `002e-schema-validator-usage.md` for complete validation commands, options, and error resolution.

Quick reference:
```bash
# Validate single file
python3 scripts/schema_validator.py rules/NNN-rule.md

# Validate all rules
python3 scripts/schema_validator.py rules/
```

### Success Criteria

- [PASS] **CRITICAL errors:** 0
- [WARN] **HIGH errors:** Acceptable if intentional (e.g., model-specific emojis in 002c)
- [INFO] **MEDIUM/INFO:** Review and fix if possible

### Common Validation Errors

**Metadata Errors:**
- **Missing metadata field** - Add missing Keywords, TokenBudget, ContextTier, or Depends in correct order
- **Keywords count wrong** - Adjust to 5-20 comma-separated terms
- **TokenBudget format** - Use `~NUMBER` format (e.g., ~500, ~1200)

**Structure Errors:**
- **Missing required section** - Add missing section per v3.2 order (Scope, References, Contract)
- **Contract missing Markdown subsection** - Add missing ### header (e.g., `### Inputs and Prerequisites`)
- **Section order wrong** - Reorder sections per v3.2: Metadata, Scope, References, Contract

**For detailed error resolution:** See `002e-schema-validator-usage.md`

### Validator Not Available

If schema_validator.py fails or is not found:

**Option 1: Install Dependencies**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

**Option 2: Manual Verification**
If validator installation fails:
1. Open schemas/rule-schema.yml
2. Verify metadata fields present (SchemaVersion, RuleVersion, LastUpdated, Keywords, TokenBudget, ContextTier, Depends)
3. Check section order: Metadata, Scope, References, Contract, Content
4. Verify no XML tags in Contract section (use Markdown headers ###)
5. Confirm Keywords count: 5-20 terms
6. Validate TokenBudget format: ~NUMBER

**Option 3: Request Assistance**
If both options fail, note the validation gap in commit message and request review.

**Schema Version Mismatch:**
- **Error:** "Expected v3.2, found v3.1" or "SchemaVersion field missing"
- **Fix:**
  1. Update SchemaVersion field to `v3.2`
  2. Verify section order matches v3.2 requirements:
     - Metadata at top
     - Scope section
     - References section
     - Contract section (with Inputs/Outputs/Execution Workflow subsections)
  3. Remove deprecated sections (Preconditions, Setup, Validation if separate)
  4. Merge validation steps into Contract, Execution Workflow
- **Bulk migration:** If updating multiple rules, see `002a-rule-creation.md` for batch update workflow
- **Example:**
  ```markdown
  <!-- Change from v3.1: -->
  **SchemaVersion:** v3.1
  
  <!-- To v3.2: -->
  **SchemaVersion:** v3.2
  ```

## Key Principles

- **Priority Hierarchy:** All rules follow the design priorities defined in `000-global-core.md`:
  1. **Priority 1 (CRITICAL):** Agent understanding and execution reliability
  2. **Priority 2 (HIGH):** Rule discovery efficacy and determinism
  3. **Priority 3 (HIGH):** Context window and token utilization efficiency
  4. **Priority 4 (LOW):** Human developer maintainability
- **Schema Compliance:** All rules must validate against schemas/rule-schema.yml with zero CRITICAL errors
- **CommonMark Compliance:** All Markdown must follow [CommonMark spec](https://spec.commonmark.org/) for consistent parsing
- **Semantic Discovery:** Keywords (5-20) enable AI agents to automatically discover relevant rules
- **Progressive Disclosure:** Scope section provides overview, Contract defines execution requirements
- **Validation-First:** Always run schema_validator.py before committing rule changes
- **Text-Only Format:** No emojis in rule files (schema requirement for universal compatibility)
- **Agent-First Formatting:** See `002g-agent-optimization.md` for required formatting patterns

## CommonMark Compliance

All rule files MUST follow [CommonMark specification](https://spec.commonmark.org/). Key requirements:

### Code Fence Rules

**Nested Code Blocks:** When showing markdown examples containing code blocks:
- Outer fence MUST have MORE characters than any inner fence
- Use 4 backticks (`` ```` ``) to wrap content containing 3 backticks (`` ``` ``)

`````markdown
<!-- WRONG: Inner fence closes outer fence prematurely -->
```markdown
## Example
```python
# This closes the outer block!
```
```

<!-- CORRECT: Outer fence longer than inner -->
````markdown
## Example
```python
# This stays inside the outer block
```
````
`````

**Fence Character Consistency:**
- Do not mix backticks (`` ` ``) and tildes (`~`) in the same document
- Closing fence must use same character as opening fence
- Closing fence must be at least as long as opening fence

**Indentation:**
- Fenced code blocks inside lists must maintain consistent indentation
- Opening and closing fences must have matching indentation levels

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
**Depends:** 100-snowflake-core.md, 000-global-core.md

# Rule 100 is foundation, 101 extends it (no reverse dependency)
```

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
version: "3.2"
metadata:
  required_fields:
    - SchemaVersion (v3.2)
    - RuleVersion (vX.Y.Z)
    - Keywords (5-20 items)
    - TokenBudget (~NUMBER format)
    - ContextTier (enum: Critical/High/Medium/Low)
    - Depends (min 1 dependency)
structure:
  required_sections: Metadata, Scope, References, Contract
  Contract_subsections: 7 Markdown ### headers required
```
