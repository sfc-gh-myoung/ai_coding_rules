# Rule Creation Guide: Step-by-Step Workflow

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** rule creation, workflow, step-by-step guide, naming conventions, metadata setup, section structure, Contract XML, validation, rule numbering, from scratch
**TokenBudget:** ~3350
**ContextTier:** High
**Depends:** rules/002-rule-governance.md, rules/000-global-core.md

## Purpose

Step-by-step workflow guide for AI agents creating new rules from scratch, covering naming, numbering, metadata setup, section structure, and validation.

## Rule Scope

All AI agents creating new rule files in the ai_coding_rules repository.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **5-step workflow** - Choose number, then Create file, then Fill metadata, then Write sections, then Validate
- **Naming convention** - `NNN-technology-aspect.md` (snake-case, 3-digit number)
- **Number ranges** - 000-099: Core, 100-199: Snowflake, 200-299: Languages, 300-399: Frameworks, 400+: Specialized
- **Required metadata** - RuleVersion (vX.Y.Z), Keywords (10-15), TokenBudget, ContextTier, Depends (in exact order)
- **Validation before commit** - `python3 scripts/schema_validator.py rules/NNN-new-rule.md`

**Pre-Execution Checklist:**
- [ ] Rule number chosen from correct range
- [ ] File named with snake-case convention
- [ ] Existing rules reviewed for similar patterns
- [ ] 5 metadata fields filled correctly
- [ ] All 9 required sections present
- [ ] Contract has all 6 XML tags
- [ ] Validation passes with 0 CRITICAL errors

## Contract

<inputs_prereqs>
Rule creation task; schema understanding; rule number assignment; technology/domain scope
</inputs_prereqs>

<mandatory>
Text editor; schema_validator.py; RULES_INDEX.md access; access to existing rules/ directory for reference
</mandatory>

<forbidden>
Skipping validation; using emojis in rule content; omitting required metadata; creating rules without dependencies
</forbidden>

<steps>
1. Choose rule number from appropriate range (000-099 core, 100-199 Snowflake, etc.)
2. Review existing rules in same category for patterns and structure
3. Create new file rules/NNN-technology-aspect.md with H1 title and ## Metadata header
4. Fill 5 required metadata fields (RuleVersion, Keywords, TokenBudget, ContextTier, Depends)
5. Write all 9 required sections in order, including Contract with 6 XML tags before line 160
6. Validate with schema_validator.py (must pass with 0 CRITICAL errors)
7. Add rule to RULES_INDEX.md with keywords
</steps>

<output_format>
Markdown file named NNN-technology-aspect.md with v3.0-compliant structure
</output_format>

<validation>
- schema_validator.py returns 0 CRITICAL errors
- File named correctly (NNN-technology-aspect.md)
- All 5 metadata fields present and formatted correctly
- All 9 required sections present in order
- Rule added to RULES_INDEX.md
</validation>

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

**Problem:** Adding only 5-8 keywords in metadata instead of the required 10-15.

**Why It Fails:** Reduces discoverability in RULES_INDEX.md; makes semantic search less effective; triggers HIGH severity errors.

**Correct Pattern:**
```markdown
**Keywords:** rule creation, schema, metadata, validation, schema_validator, numbering, governance, template, workflow, RULES_INDEX, keywords, TokenBudget, ContextTier
```

## Step 1: Choose Rule Number and Name

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
110-cortex-agent.md           # Base agent functionality
111-cortex-agent-tools.md     # Tool usage patterns
112-cortex-analyst.md         # Analyst features
115-model-registry.md         # ML model registry
116-model-training.md         # Model training workflows

# Snowflake Data Engineering (120-129)
121-snowflake-snowpipe.md               # Data ingestion
121-dynamic-tables.md         # Dynamic table patterns
122-streams.md                # Change data capture
```

### Naming Convention

**Pattern:** `NNN-technology-aspect.md`

**Requirements:**
- Use snake_case (underscores, not hyphens) - WRONG: `streamlit-best-practices.md`, RIGHT: `streamlit_best_practices.md`
- 3-digit number prefix (pad with zeros: 001, 099, 100)
- Technology or domain identifier
- Specific aspect or feature
- `.md` extension

**Examples:**
- [PASS] `100-snowflake-core.md`
- [PASS] `115-model-registry.md`
- [PASS] `320-streamlit-widgets.md`
- [FAIL] `100-SnowflakeSQL.md` (wrong: CamelCase)
- [FAIL] `streamlit.md` (wrong: no number)
- [FAIL] `100_snowflake_sql.md` (wrong: underscores in number)

## Step 2: Review Existing Rules for Patterns

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
- Metadata format and keyword selection
- Section structure and ordering
- Contract XML tag usage
- Quick Start TL;DR patterns
- Anti-Patterns section examples
- Output Format Examples style

**Use existing rules as structural guides** - maintain consistency with established patterns.

## Step 3: Create New Rule File

### File Structure Template

```markdown
# [NNN]-[technology]-[aspect]

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** [10-15 keywords here]
**TokenBudget:** ~[estimate]
**ContextTier:** [Critical|High|Medium|Low]
**Depends:** rules/000-global-core.md

## Purpose

[1-2 sentence description]

## Rule Scope

[Single line defining applicability]

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1]:** Description
- **[Pattern 2]:** Description
- **[Pattern 3]:** Description

**Pre-Execution Checklist:**
- [ ] Checklist item 1
- [ ] Checklist item 2
- [ ] Checklist item 3
- [ ] Checklist item 4
- [ ] Checklist item 5
```

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

<inputs_prereqs>
[Prerequisites here]
</inputs_prereqs>

<mandatory>
[Required tools/libraries]
</mandatory>

<forbidden>
[Prohibited actions]
</forbidden>

<steps>
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]
5. [Step 5]
</steps>

<output_format>
[Expected output description]
</output_format>

<validation>
[How to verify success]
</validation>

## Anti-Patterns and Common Mistakes

[Anti-patterns with code examples]

## Post-Execution Checklist

- [ ] Verification item 1
- [ ] Verification item 2
- [ ] Verification item 3
- [ ] Verification item 4
- [ ] Verification item 5

## Validation

[Success criteria and negative tests]

## Output Format Examples

[Code examples and sample outputs]

## References

### Related Rules
- `000-global-core.md` - Description
```

## Step 4: Fill Required Metadata

### Metadata Field Order (MANDATORY)

```markdown
# [Rule Number]-[technology]-[aspect]

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** [10-15 comma-separated keywords]
**TokenBudget:** ~[number]
**ContextTier:** [Critical | High | Medium | Low]
**Depends:** [rule-dependencies]
```

### Field Requirements

**Required Metadata Fields:**
- **SchemaVersion:** `v3.0` format (e.g., `**SchemaVersion:** v3.1`) - Optional but recommended
- **RuleVersion:** `vX.Y.Z` format (e.g., `**RuleVersion:** v1.0.0`) - REQUIRED for issue tracking
- **Keywords:** 10-15 comma-separated terms - CRITICAL for semantic discovery
- **TokenBudget:** `~NUMBER` format (e.g., `**TokenBudget:** ~1200`) - Use tilde prefix
- **ContextTier:** One of Critical/High/Medium/Low only
- **Depends:** Rule path(s) (e.g., `rules/000-global-core.md`) - At least one required

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

## Step 4: Write Required Sections

### Section Order (MANDATORY)

1. **Purpose** (1-2 sentences)
2. **Rule Scope** (1 line)
3. **Quick Start TL;DR** (Essential Patterns + Pre-Execution Checklist)
4. **Contract** (6 XML tags)
5. **Key Principles** (Optional, 3-5 bullets)
6. **Anti-Patterns** (Optional but strongly recommended)
7. **Post-Execution Checklist** (5+ items)
8. **Validation** (Success checks + negative tests)
9. **Output Format Examples** (Concrete code samples)
10. **References** (Related rules + external docs)

### Purpose Section

**Format:**
```markdown
## Purpose

[1-2 sentence description of what this rule accomplishes and why it matters]
```

**Example:**
```markdown
## Purpose

Defines best practices for Snowflake SQL query optimization, focusing on CTE usage, join strategies, and warehouse sizing for cost-effective performance.
```

### Rule Scope Section

**Format:**
```markdown
## Rule Scope

[Single line defining what contexts this rule applies to]
```

**Example:**
```markdown
## Rule Scope

All SQL queries executed in Snowflake data warehouses, particularly queries with complex joins or large data volumes.
```

### Quick Start TL;DR Section

**Structure:**
```markdown
## Quick Start TL;DR

**Essential Patterns:**
- **Pattern 1:** Description
- **Pattern 2:** Description
- **Pattern 3:** Description
[Minimum 3 patterns, no maximum]

**Pre-Execution Checklist:**
- [ ] Checklist item 1
- [ ] Checklist item 2
- [ ] Checklist item 3
- [ ] Checklist item 4
- [ ] Checklist item 5
[5-7 items recommended]
```

**Purpose:** 30-second overview for agents to understand core patterns without reading entire file.

## Step 5: Add Contract Section with XML Tags

### Contract Structure (MANDATORY)

```markdown
## Contract

<inputs_prereqs>
What the agent needs to have/know before starting this task
</inputs_prereqs>

<mandatory>
Required tools, libraries, permissions, access
</mandatory>

<forbidden>
Prohibited actions, tools, approaches
</forbidden>

<steps>
1. First required step
2. Second required step
3. Third required step
4. Fourth required step
5. Fifth required step
[Minimum 5 steps, maximum 10 steps]
</steps>

<output_format>
Description of expected output format (file type, structure, content)
</output_format>

<validation>
How to verify success - specific checks agent should run
</validation>
```

### Contract Best Practices

**inputs_prereqs:**
- List required knowledge, files, data, context
- Be specific about prerequisites
- Include required access permissions

**mandatory:**
- List exact tool names (e.g., `schema_validator.py`, not "validator")
- Include required libraries with versions if critical
- Specify required file access

**forbidden:**
- Explicitly prohibit problematic approaches
- List tools that should NOT be used
- Call out common mistakes to avoid

**steps:**
- Actionable, sequential steps
- 5-10 steps (not too granular, not too high-level)
- Each step should be verifiable

**output_format:**
- Describe exact format (Markdown, Python, SQL, etc.)
- Specify required structure
- Include file naming conventions if relevant

**validation:**
- List specific commands to run
- Define success criteria
- Include negative tests (what should NOT happen)

### Contract Placement

**Requirement:** Contract section must appear before line 160.

**Why:** Ensures AI agents read requirements early before processing detailed content.

## Step 6: Validate with schema_validator.py

### Running Validation

```bash
# Validate single file
python3 scripts/schema_validator.py rules/NNN-new-rule.md

# Verbose output (detailed checks)
python3 scripts/schema_validator.py rules/NNN-new-rule.md --verbose

# Expected success output:
# ================================================================================
# VALIDATION REPORT: rules/NNN-new-rule.md
# ================================================================================
# [PASS] Passed: 458 checks
#
# [PASS] RESULT: PASSED
# ================================================================================
```

### Common Errors and Fixes

**Metadata Errors:**
- **Missing metadata field:** Add missing Keywords, TokenBudget, ContextTier, or Depends in correct order
- **Keywords count wrong:** Adjust to 10-15 comma-separated terms
- **TokenBudget format:** Change to `~1200` format (tilde + number)

**Structure Errors:**
- **Missing required section:** Add missing section per v3.0 order
- **Contract missing XML tag:** Add tag: `<inputs_prereqs>`, `<mandatory>`, etc.
- **Contract after line 160:** Move Contract section earlier in file

**For detailed error resolution:** See `002d-schema-validator-usage.md`

## Step 7: Add to RULES_INDEX.md

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
- [ ] TokenBudget within ±15% of actual token count
- [ ] No duplicate content (use references to other rules)
- [ ] Lists preferred over prose paragraphs
- [ ] Terminology consistent with existing rules (see glossary in 000-global-core.md)

### Schema Compliance (Required)

- [ ] Rule number chosen from correct range (000-099, 100-199, etc.)
- [ ] File named with snake-case convention (NNN-technology-aspect.md)
- [ ] All 5 metadata fields filled: RuleVersion, Keywords (10-15), TokenBudget, ContextTier, Depends
- [ ] All 9 required sections present in correct order
- [ ] Contract section has all 6 XML tags before line 160
- [ ] Quick Start TL;DR has minimum 3 Essential Patterns
- [ ] Post-Execution Checklist has 5+ verification items

### Final Validation

- [ ] `python3 scripts/schema_validator.py rules/NNN-rule.md` returns 0 CRITICAL errors
- [ ] Rule added to RULES_INDEX.md with keywords
- [ ] No emojis in rule file content
- [ ] Existing rules reviewed for structural patterns

## Validation

**Success Checks:**
- New rule file exists at `rules/NNN-technology-aspect.md`
- `python3 scripts/schema_validator.py rules/NNN-new-rule.md` returns 0 CRITICAL errors
- All 4 metadata fields present and correctly formatted
- All 9 required sections present in order
- Contract has all 6 XML tags before line 160
- Keywords count is 10-15
- Rule appears in RULES_INDEX.md

**Negative Tests:**
- File named with spaces triggers error
- Missing metadata field triggers CRITICAL error
- Wrong section order triggers HIGH error
- Missing Contract XML tag triggers CRITICAL error
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
# **Depends:** rules/000-global-core.md, rules/100-snowflake-core.md

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
# **Depends:** rules/000-global-core.md, rules/101-snowflake-streamlit-core.md

# Write all required sections

# Validate
python3 scripts/schema_validator.py rules/101d-snowflake-streamlit-testing.md
# [PASS] RESULT: PASSED
```

## References

### Related Rules
- **Rule Governance**: `002-rule-governance.md` - Schema requirements and standards
- **Validator Usage**: `002d-schema-validator-usage.md` - Detailed validation commands and error resolution
- **Optimization Guide**: `002b-rule-optimization.md` - Token budget optimization strategies
- **Global Core**: `000-global-core.md` - Foundation for all rules

### External Documentation
- **Schema Definition**: `schemas/rule-schema.yml` - Authoritative schema definition
- **Rules Index**: `RULES_INDEX.md` - Master index of all rules
