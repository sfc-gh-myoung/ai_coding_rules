# Rule Creation Guide: Step-by-Step Workflow

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.1
**LastUpdated:** 2026-01-13
**Keywords:** rule creation, workflow, step-by-step guide, naming conventions, metadata setup, v3.2 schema, validation, rule numbering, from scratch, new rule
**TokenBudget:** ~5400
**ContextTier:** High
**Depends:** 002-rule-governance.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Step-by-step workflow for creating new rules from scratch. Covers rule numbering, naming conventions, metadata setup, v3.2 section structure, Contract with Markdown headers, and validation. For updating existing rules, see 002b-rule-update.md.

**When to Load This Rule:**
- Creating a new rule file from scratch
- Understanding rule creation workflow
- Setting up rule metadata correctly for new rules
- Structuring rule sections per v3.2 schema

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Schema requirements and standards
- **000-global-core.md** - Foundation for all rules

**Related:**
- **002b-rule-update.md** - Updating and maintaining existing rules
- **002e-schema-validator-usage.md** - Detailed validation commands and error resolution
- **002c-rule-optimization.md** - Token budget optimization strategies

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema definition
- **Rules Index:** `RULES_INDEX.md` - Master index of all rules
- **[CommonMark Spec](https://spec.commonmark.org/)** - Authoritative Markdown specification (all rule files MUST comply)

## Contract

### Inputs and Prerequisites

- Rule creation task
- v3.2 schema understanding
- Rule number assignment
- Technology/domain scope

### Mandatory

- Text editor
- `schema_validator.py` script
- `RULES_INDEX.md` access
- Access to existing rules/ directory for reference

### Forbidden

- Skipping validation
- Using emojis in rule content
- Omitting required metadata
- Creating rules without dependencies
- Using XML tags in Contract (v3.2 uses Markdown headers)
- Using numbered section headings
- Non-compliant Markdown (must follow CommonMark spec - see 002-rule-governance.md)

### Execution Steps

1. Choose rule number from appropriate range (000-099 core, 100-199 Snowflake, etc.)
2. Review existing rules in same category for patterns and structure
3. Create new file `rules/NNN-technology-aspect.md` with H1 title and `## Metadata` header
4. Fill required metadata fields (SchemaVersion: v3.2, RuleVersion, Keywords: 5-20 terms, TokenBudget, ContextTier, Depends)
5. Write required sections in v3.2 order: Scope, References, Contract, Anti-Patterns (optional)
6. Add Contract section with Markdown subsections (###), NOT XML tags
7. Use descriptive section names (not numbered: "Environment Setup" not "1. Environment Setup")
8. Validate with `schema_validator.py` (must pass with 0 CRITICAL errors)
9. Add rule to `RULES_INDEX.md` with keywords

### Output Format

Markdown file named `NNN-technology-aspect.md` with:
- v3.2-compliant structure
- Metadata with SchemaVersion: v3.2
- Contract with Markdown headers (###), not XML tags
- Descriptive section names (not numbered)
- 5-20 keywords

### Validation

**Pre-Task-Completion Checks:**
- Rule number chosen from correct range
- File naming follows convention (snake-case)
- Metadata fields all present
- Required sections in v3.2 order
- Contract uses Markdown headers, not XML tags
- No numbered section headings
- Keywords count is 5-20 terms

**Success Criteria:**
- `schema_validator.py` returns 0 CRITICAL errors
- File named correctly (NNN-technology-aspect.md)
- All required metadata fields present and formatted correctly
- All required sections present in v3.2 order
- Rule added to `RULES_INDEX.md`

**Error Recovery:**
- **Permission denied writing rule file:** Report error with path, suggest checking directory permissions
- **Validator returns CRITICAL errors:** Fix each error per 002e guidance before proceeding
- **RULES_INDEX.md not writable:** Report error, provide index entry for manual addition

### Post-Execution Checklist

- [ ] Rule number chosen from correct range for domain
- [ ] File named with snake-case convention (NNN-technology-aspect.md)
- [ ] Existing rules reviewed for similar patterns
- [ ] All metadata fields filled correctly (SchemaVersion: v3.2)
- [ ] Keywords count is 5-20 terms
- [ ] All required sections present in v3.2 order (Scope, References, Contract)
- [ ] Contract uses Markdown headers (###), not XML tags
- [ ] No numbered section headings in file
- [ ] Validation passes with 0 CRITICAL errors
- [ ] Rule added to RULES_INDEX.md with keywords

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Skipping Schema Validation**

**Problem:** Creating rule files without running schema_validator.py before committing.

**Why It Fails:** Introduces CRITICAL/HIGH errors that break rule compliance; wastes time in code review.

**Correct Pattern:**
```bash
# Always validate before committing
python3 scripts/schema_validator.py rules/NNN-new-rule.md
# Fix all CRITICAL errors before commit
```

**Anti-Pattern 2: Vague Rule Numbers**

**Problem:** Choosing rule numbers that don't align with the domain (e.g., using 200-299 for Snowflake rules).

**Why It Fails:** Breaks organizational structure; makes rule discovery difficult; violates governance.

**Correct Pattern:**
```markdown
# Snowflake rules: 100-199
100-snowflake-core.md
115-snowflake-cortex-agents-core.md

# Python rules: 200-299
200-python-core.md
206-python-pytest.md
```

**Anti-Pattern 3: Insufficient Keywords**

**Problem:** Adding only 3-4 keywords in metadata instead of the required 5-20.

**Why It Fails:** Reduces discoverability in RULES_INDEX.md; makes semantic search less effective; triggers HIGH severity errors.

**Correct Pattern:**
```markdown
**Keywords:** rule creation, schema, metadata, validation, schema_validator, numbering, governance, template, workflow, RULES_INDEX, keywords, TokenBudget, ContextTier
```

## Choose Rule Number and Name (Overview)

### Numbering Ranges

**Rule Number Categories:**
- **000-099:** Core Framework (000-global-core, 001-rule-composition, 002-rule-governance)
- **100-199:** Snowflake (100-snowflake-sql, 110-cortex-agent, 115-model-registry)
- **200-299:** Programming Languages (200-python, 210-javascript, 220-sql)
- **300-399:** Frameworks (300-react, 310-django, 320-streamlit)
- **400-499:** Testing & Quality (400-pytest, 410-integration-testing)
- **500-599:** Security (500-security-core, 510-authentication)
- **600+:** Specialized Domains (600-data-pipeline, 700-ml-ops)

### Subdomain Patterns

Within each range, use logical grouping:

```markdown
# Snowflake ML/AI Features (110-119)
110-snowflake-model-registry.md   # ML model registry
114-snowflake-cortex-aisql.md     # AI SQL features
115-snowflake-cortex-agents-core.md  # Cortex agents
116-snowflake-cortex-search.md    # Cortex search

# Snowflake Data Engineering (120-129)
121-snowflake-snowpipe.md         # Data ingestion
122-snowflake-dynamic-tables.md   # Dynamic table patterns
```

### Naming Convention

**Pattern:** `NNN-technology-aspect.md`

**Requirements:**
- Use hyphens between components (not underscores): `NNN-technology-aspect.md`
- 3-digit number prefix (pad with zeros: 001, 099, 100)
- Technology or domain identifier
- Specific aspect or feature
- `.md` extension

**Examples:**
- CORRECT: `100-snowflake-core.md`, `206-python-pytest.md`, `101-snowflake-streamlit-core.md`
- INCORRECT: `100_snowflake_core.md`, `200-python_pytest.md`, `streamlit_best_practices.md`

**Examples:**
- [PASS] `100-snowflake-core.md`
- [PASS] `110-snowflake-model-registry.md`
- [PASS] `206-python-pytest.md`
- [FAIL] `100-SnowflakeSQL.md` (wrong: CamelCase)
- [FAIL] `streamlit.md` (wrong: no number)
- [FAIL] `100_snowflake_sql.md` (wrong: underscores in number)

## Review Existing Rules for Patterns (Overview)

### Find Similar Rules

```bash
# List rules in same category
ls -la rules/100-*.md  # Snowflake rules
ls -la rules/200-*.md  # Language rules
ls -la rules/300-*.md  # Framework rules

# Search for rules by keyword
grep -l "your-technology" rules/*.md
```

### Reference Structure

Review 2-3 existing rules to understand:
- Metadata format and keyword selection (5-20 keywords)
- Section structure and v3.2 ordering (Scope, References, Contract)
- Contract Markdown ### header usage (NOT XML tags)
- Anti-Patterns section examples
- Output Format Examples style

**Use existing rules as structural guides** - maintain consistency with established patterns.

## Create New Rule File (Overview)

### File Structure Template (v3.2)

```markdown
# [NNN]-[technology]-[aspect]

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** [YYYY-MM-DD]
**Keywords:** [5-20 keywords here]
**TokenBudget:** ~[estimate]
**ContextTier:** [Critical|High|Medium|Low]
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
[1-2 sentence description of what this rule accomplishes]

**When to Load This Rule:**
- [Condition 1]
- [Condition 2]
- [Condition 3]

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **[related-rule].md** - [Brief description]

### External Documentation

- **[Resource Name]:** [URL or path]
```

### Metadata Field Guidance

#### RuleVersion and LastUpdated

**For New Rules:**
- **RuleVersion:** Always start at `v1.0.0` for new rule files
- **LastUpdated:** Set to creation date in `YYYY-MM-DD` format

**For Updating Existing Rules:**
See `002b-rule-update.md` for complete versioning policy and update workflows.

### Importance Markers

Add an importance marker after the title for foundation rules:

**When to use CORE FOUNDATION marker (domain cores only):**
- Rule name ends with `-core.md`
- Defines essential patterns for a technology domain
- Other rules in the domain depend on it

**When to use FOUNDATION marker (governance rules only):**
- Rule is in 002-series
- Defines rule creation/maintenance patterns
- Required for rule infrastructure work

**When to use no marker (most rules):**
- Standard specialized rules
- Can be summarized if context limits reached

```markdown
## Contract

### Inputs and Prerequisites
[Prerequisites here]

### Mandatory
[Required tools/libraries]

### Forbidden
[Prohibited actions]

### Execution Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]
5. [Step 5]

### Output Format
[Expected output description]

### Validation
**Pre-Task-Completion Checks:**
- [Check 1]

**Success Criteria:**
- [Criterion 1]

### Post-Execution Checklist
- [ ] Verification item 1
- [ ] Verification item 2

## Anti-Patterns and Common Mistakes
[Anti-patterns with code examples]
```

## Fill Required Metadata

### Metadata Field Order (MANDATORY)

```markdown
# [Rule Number]-[technology]-[aspect]

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**Keywords:** [5-20 comma-separated keywords]
**TokenBudget:** ~[number]
**ContextTier:** [Critical | High | Medium | Low]
**Depends:** [rule-dependencies]
```

### Field Requirements

**Required Metadata Fields:**
- **SchemaVersion:** `v3.2` format (e.g., `**SchemaVersion:** v3.2`) - REQUIRED for v3.2 compliance
- **RuleVersion:** `vX.Y.Z` format (e.g., `**RuleVersion:** v1.0.0`) - REQUIRED for issue tracking
- **Keywords:** 5-20 comma-separated terms - CRITICAL for semantic discovery
- **TokenBudget:** See `002-rule-governance.md` for complete format requirements
- **ContextTier:** One of Critical/High/Medium/Low only (see `002c-rule-optimization.md` for selection guidance)
- **Depends:** Rule path(s) (e.g., `000-global-core.md`) - At least one required

### Keywords Best Practices

**Purpose:** Enable semantic discovery - AI agents search keywords to find relevant rules.

**Guidelines:**
- Include primary technology (e.g., Snowflake, Python, React)
- Include domain concepts (e.g., performance, security, testing)
- Include specific features (e.g., CTE, widget, authentication)
- Use searchable terms agents would query
- Avoid generic words (e.g., "code", "rule", "best")

**Example - Good Keywords:**
```markdown
**Keywords:** Snowflake, Cortex Agent, tool usage, function calling, error handling, retry logic, state management, debugging, monitoring, observability
```

**Example - Bad Keywords:**
```markdown
**Keywords:** agent, stuff, things, code, best practices, good, patterns, rules, tips, advice
```

### TokenBudget Estimation

**Quick Guide:**
- Small rule (~300 lines): `~800`
- Medium rule (~500 lines): `~1200`
- Large rule (~800 lines): `~1800`
- Very large rule (~1200 lines): `~2500`

**Validation:** Run `python3 scripts/token_validator.py` after creation to get actual count.

### ContextTier Selection

**Tier Guidelines:**
- **Critical:** Framework core, always loaded (000-global-core, 002-rule-governance)
- **High:** Frequently used, broad applicability (100-snowflake-sql, 200-python-core)
- **Medium:** Specific features, moderate usage (115-model-registry, 320-streamlit-widgets)
- **Low:** Specialized, rarely used (600-data-pipeline-advanced)

## Write Required Sections (v3.2)

### Section Order (MANDATORY)

See `002-rule-governance.md` for complete v3.2 schema changes and section requirements.

**Required sections (in order):**
1. **Metadata** - All 6 required fields
2. **Scope** - What the rule covers + when to load it
3. **References** - Dependencies and external documentation
4. **Contract** - Structured contract with Markdown subsections (###)
5. **Anti-Patterns and Common Mistakes** - Optional but strongly recommended

**Key v3.2 changes:**
- Scope replaces Purpose + Rule Scope
- Contract uses Markdown headers (###), not XML tags
- Post-Execution Checklist moved inside Contract
- Validation moved inside Contract

### Scope Section (v3.2 - Replaces Purpose + Rule Scope)

**Format:**
```markdown
## Scope

**What This Rule Covers:**
[1-2 sentence description of what this rule accomplishes and why it matters]

**When to Load This Rule:**
- [Loading condition 1]
- [Loading condition 2]
- [Loading condition 3]
```

**Example:**
```markdown
## Scope

**What This Rule Covers:**
Best practices for Snowflake SQL query optimization, focusing on CTE usage, join strategies, and warehouse sizing for cost-effective performance.

**When to Load This Rule:**
- Writing or optimizing Snowflake SQL queries
- Debugging slow query performance
- Designing warehouse sizing strategies
```

**Note:** v3.2 ELIMINATED the separate Purpose, Rule Scope, and Quick Start TL;DR sections. Use Scope for overview.

## Add Contract Section (v3.2 - Markdown Headers)

### Contract Structure (MANDATORY)

```markdown
## Contract

### Inputs and Prerequisites
What the agent needs to have/know before starting this task

### Mandatory
Required tools, libraries, permissions, access

### Forbidden
Prohibited actions, tools, approaches

### Execution Steps
1. First required step
2. Second required step
3. Third required step
4. Fourth required step
5. Fifth required step
[Minimum 5 steps, maximum 10 steps]

### Output Format
Description of expected output format (file type, structure, content)

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

### Contract Best Practices

**Inputs and Prerequisites:**
- List required knowledge, files, data, context
- Be specific about prerequisites
- Include required access permissions

**Mandatory:**
- List exact tool names (e.g., `schema_validator.py`, not "validator")
- Include required libraries with versions if critical
- Specify required file access

**Forbidden:**
- Explicitly prohibit problematic approaches
- List tools that should NOT be used
- Call out common mistakes to avoid

**Execution Steps:**
- Actionable, sequential steps
- 5-10 steps (not too granular, not too high-level)
- Each step should be verifiable

**Output Format:**
- Describe exact format (Markdown, Python, SQL, etc.)
- Specify required structure
- Include file naming conventions if relevant

**Validation:**
- List specific commands to run
- Define success criteria
- Include negative tests (what should NOT happen)

### Contract Placement

**Requirement:** Contract section must appear before line 160.

**Why:** Ensures AI agents read requirements early before processing detailed content.

## Validate with schema_validator.py

### Running Validation

See `002e-schema-validator-usage.md` for complete validation commands and options.

Quick reference:

```bash
# Validate single file
python3 scripts/schema_validator.py rules/NNN-new-rule.md

# Verbose output (detailed checks)
python3 scripts/schema_validator.py rules/NNN-new-rule.md --verbose
```

### Common Errors and Fixes

**Metadata Errors:**
- **Missing metadata field:** Add missing Keywords, TokenBudget, ContextTier, or Depends in correct order
- **Keywords count wrong:** Adjust to 5-20 comma-separated terms
- **TokenBudget format:** See `002-rule-governance.md` for format requirements

**Structure Errors:**
- **Missing required section:** Add missing section per v3.2 order
- **Contract missing Markdown subsection:** Add subsection with ### header
- **Contract after line 160:** Move Contract section earlier in file

**For detailed error resolution:** See `002e-schema-validator-usage.md`

## Add to RULES_INDEX.md

### Index Entry Format

```markdown
- **NNN-new-rule:** Brief description (Keywords: keyword1, keyword2, keyword3)
```

### Example

```bash
# Edit RULES_INDEX.md
vim RULES_INDEX.md

# Add entry:
# | 321-streamlit-validation | Streamlit form validation patterns | Streamlit, validation, forms, widgets, error handling |
```

**Note:** Use the same keywords as the rule's Keywords metadata for consistency.

## Post-Execution Checklist

### Priority 1: Agent Understanding (CRITICAL - Must Pass)

These checks ensure agents can execute the rule reliably:

- [ ] No ASCII tables in content (use structured lists instead)
- [ ] No arrow characters (`→`) outside code blocks (use "then", "to", "Instead")
- [ ] No ASCII decision trees (`├─`, `└─`, `│`) (use nested conditional lists)
- [ ] No Mermaid diagrams or ASCII art (use structured text)
- [ ] All subjective terms quantified with thresholds (e.g., "large" defined as ">1M rows")
- [ ] All conditionals have explicit branches (if X, then Y; else Z)
- [ ] Instructions use imperative voice (commands, not passive)
- [ ] Critical information front-loaded in each section

### Priority 2: Token Efficiency (HIGH - Should Pass)

These checks ensure efficient context window usage:

- [ ] TokenBudget declared with `~NUMBER` format
- [ ] TokenBudget within ±5% of actual token count
- [ ] No duplicate content (use references to other rules)
- [ ] Lists preferred over prose paragraphs
- [ ] Terminology consistent with existing rules (see glossary in 000-global-core.md)

### Schema Compliance (Required)

- [ ] Rule number chosen from correct range (000-099, 100-199, etc.)
- [ ] File named with snake-case convention (NNN-technology-aspect.md)
- [ ] All 6 metadata fields filled: SchemaVersion (v3.2), RuleVersion, Keywords (5-20), TokenBudget, ContextTier, Depends
- [ ] All required sections present in v3.2 order (Scope, References, Contract, Anti-Patterns)
- [ ] Contract section has all Markdown subsections (###) before line 160
- [ ] Post-Execution Checklist inside Contract section

### Final Validation

- [ ] `python3 scripts/schema_validator.py rules/NNN-rule.md` returns 0 CRITICAL errors
- [ ] Rule added to RULES_INDEX.md with keywords
- [ ] No emojis in rule file content
- [ ] Existing rules reviewed for structural patterns

## Validation

**Success Checks:**
- New rule file exists at `rules/NNN-technology-aspect.md`
- `python3 scripts/schema_validator.py rules/NNN-new-rule.md` returns 0 CRITICAL errors
- All 6 metadata fields present and correctly formatted
- All required sections present in v3.2 order
- Contract has all Markdown subsections (###) before line 160
- Keywords count is 5-20
- Rule appears in RULES_INDEX.md

**Negative Tests:**
- File named with spaces triggers error
- Missing metadata field triggers CRITICAL error
- Wrong section order triggers HIGH error
- Missing Contract Markdown subsection triggers CRITICAL error
- Contract after line 160 triggers HIGH warning

## Output Format Examples

### Example 1: New Snowflake Rule

```bash
# Step 1: Choose number (Snowflake range: 100-199)
# Creating rule for Snowpipe best practices
# Number: 121-snowflake-snowpipe.md

# Step 2: Review existing Snowflake rules
ls -la rules/100-*.md
cat rules/100-snowflake-core.md  # Review structure

# Step 3: Create new file
vim rules/121-snowflake-snowpipe.md
# Fill in metadata:
# **Keywords:** Snowflake, Snowpipe, data ingestion, streaming, CDC, error handling, monitoring, cost optimization, retry logic, file formats
# **TokenBudget:** ~1200
# **ContextTier:** High
# **Depends:** 000-global-core.md, 100-snowflake-core.md

# Step 4: Write all required sections with Contract
# [Edit file with all 9 required sections]

# Step 5: Validate
python3 scripts/schema_validator.py rules/121-snowflake-snowpipe.md
# [PASS] RESULT: PASSED

# Step 6: Add to index
echo "| 120-snowpipe | Snowpipe data ingestion best practices | Snowflake, Snowpipe, data ingestion, streaming, CDC |" >> RULES_INDEX.md
```

### Example 2: New Framework Rule

```bash
# Creating Streamlit widget validation rule
# Number: 101d-snowflake-streamlit-testing.md

# Review existing Streamlit rules
grep -l "Streamlit" rules/*.md

# Create new file
vim rules/101d-snowflake-streamlit-testing.md

# Fill metadata:
# **Keywords:** Streamlit, validation, forms, widgets, error handling, user input, data validation, UI feedback, session state, form submission
# **TokenBudget:** ~800
# **ContextTier:** Medium
# **Depends:** 000-global-core.md, 101-snowflake-streamlit-core.md

# Write all required sections

# Validate
python3 scripts/schema_validator.py rules/101d-snowflake-streamlit-testing.md
# [PASS] RESULT: PASSED
```
