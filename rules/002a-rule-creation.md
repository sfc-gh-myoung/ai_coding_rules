# Rule Creation Guide: Step-by-Step Workflow

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.3.0
**LastUpdated:** 2026-03-09
**Keywords:** rule creation, workflow, step-by-step guide, naming conventions, metadata setup, v3.2 schema, validation, rule numbering, from scratch, new rule
**TokenBudget:** ~4200
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
- `ai-rules validate` CLI command
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
3. Create new file `rules/<NNN>[<letter>]-<technology>-<aspect>.md` with H1 title and `## Metadata` header
4. Fill required metadata fields (SchemaVersion: v3.2, RuleVersion, Keywords: 5-20 terms, TokenBudget, ContextTier, Depends)
5. Write required sections in v3.2 order: Scope, References, Contract, Anti-Patterns (optional)
6. Add Contract section with Markdown subsections (###), NOT XML tags
7. Use descriptive section names (not numbered: "Environment Setup" not "1. Environment Setup")
8. Validate with `ai-rules validate` (must pass with 0 CRITICAL errors)
9. Add rule to `RULES_INDEX.md` with keywords

### Output Format

Markdown file named `<NNN>[<letter>]-<technology>-<aspect>.md` with:
- v3.2-compliant structure
- Metadata with SchemaVersion: v3.2
- Contract with Markdown headers (###), not XML tags
- Descriptive section names (not numbered)
- 5-20 keywords

### Validation

**Pre-Task-Completion Checks:**
- Rule number chosen from correct range
- File naming follows convention: `<NNN>[<letter>]-<technology>-<aspect>.md` (single-letter suffix only, no multi-char suffixes)
- Metadata fields all present
- Required sections in v3.2 order
- Contract uses Markdown headers, not XML tags
- No numbered section headings
- Keywords count is 5-20 terms

**Success Criteria:**
- `ai-rules validate` returns 0 CRITICAL errors
- File named correctly (`<NNN>[<letter>]-<technology>-<aspect>.md`, single-letter suffix only)
- All required metadata fields present and formatted correctly
- All required sections present in v3.2 order
- Rule added to `RULES_INDEX.md`

**Negative Tests:**
- File named with spaces triggers error
- Missing metadata field triggers CRITICAL error
- Wrong section order triggers HIGH error
- Missing Contract Markdown subsection triggers CRITICAL error
- Contract after line 160 triggers HIGH warning

**Error Recovery:**
- **Permission denied writing rule file:** Report error with path, suggest checking directory permissions
- **Validator returns CRITICAL errors:** Fix each error per 002e guidance before proceeding
- **RULES_INDEX.md not writable:** Report error, provide index entry for manual addition

### Post-Execution Checklist

**Agent Understanding (CRITICAL - Must Pass):**
- [ ] No ASCII tables in content (use structured lists instead)
- [ ] No arrow characters outside code blocks (use "then", "to", "Instead")
- [ ] No ASCII decision trees (use nested conditional lists)
- [ ] No Mermaid diagrams or ASCII art (use structured text)
- [ ] All subjective terms quantified with thresholds (e.g., "large" defined as ">1M rows")
- [ ] All conditionals have explicit branches (if X, then Y; else Z)
- [ ] Instructions use imperative voice (commands, not passive)

**Token Efficiency (HIGH - Should Pass):**
- [ ] TokenBudget declared with `~NUMBER` format
- [ ] TokenBudget within plus or minus 5% of actual token count
- [ ] No duplicate content (use references to other rules)
- [ ] Lists preferred over prose paragraphs
- [ ] Terminology consistent with existing rules (see glossary in 000-global-core.md)

**Schema Compliance:**
- [ ] Rule number chosen from correct range for domain
- [ ] File named with kebab-case convention (`<NNN>[<letter>]-<technology>-<aspect>.md`, single-letter suffix only)
- [ ] Existing rules reviewed for similar patterns
- [ ] All 6 metadata fields filled: SchemaVersion (v3.2), RuleVersion, Keywords (5-20), TokenBudget, ContextTier, Depends
- [ ] All required sections present in v3.2 order (Scope, References, Contract, Anti-Patterns)
- [ ] Contract section has all Markdown subsections (###) before line 160
- [ ] Post-Execution Checklist inside Contract section
- [ ] No numbered section headings in file
- [ ] No emojis in rule file content

**Final Validation:**
- [ ] `uv run ai-rules validate rules/<your-rule>.md` returns 0 CRITICAL errors
- [ ] Rule added to RULES_INDEX.md with keywords

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Skipping Schema Validation**

**Problem:** Creating rule files without running `ai-rules validate` before committing.

**Why It Fails:** Introduces CRITICAL/HIGH errors that break rule compliance; wastes time in code review.

**Correct Pattern:**
```bash
# Always validate before committing
uv run ai-rules validate rules/<your-new-rule>.md
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

**Pattern:** `<NNN>[<letter>]-<technology>-<aspect>.md`

**Requirements:**
- `<NNN>` = 3-digit number prefix (000-999), zero-padded
- `[<letter>]` = Optional single lowercase letter suffix (a-z). Single-letter suffix only (a-z). Multi-character suffixes (a1, b2) are NOT allowed.
- `<technology>` = Technology or domain identifier (kebab-case)
- `<aspect>` = Specific aspect or feature (kebab-case)
- Use hyphens between components (not underscores)
- `.md` extension

**Validation regex:** `^[0-9]{3}[a-z]?-[a-z]+-[a-z-]+\.md$`

**Examples:**
- [PASS] `100-snowflake-core.md`
- [PASS] `100a-snowflake-auth.md`
- [PASS] `200b-python-testing.md`
- [PASS] `110-snowflake-model-registry.md`
- [PASS] `206-python-pytest.md`
- [PASS] `101-snowflake-streamlit-core.md`
- [FAIL] `100a1-something.md` (multi-character suffix "a1")
- [FAIL] `1-core.md` (not 3-digit)
- [FAIL] `100-SnowflakeSQL.md` (wrong: CamelCase)
- [FAIL] `streamlit.md` (wrong: no number)
- [FAIL] `100_snowflake_sql.md` (wrong: underscores)
- [FAIL] `200-python_pytest.md` (wrong: underscore in name)

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

For the complete v3.2 rule template with importance markers and Contract structure, see `rules/examples/002a-rule-template.md`.

## Fill Required Metadata

For detailed metadata field guidance, see `002-rule-governance.md` §Metadata Fields.

**Quick Reference - Required Fields (in order):**
- **SchemaVersion:** `v3.2`
- **RuleVersion:** `v1.0.0` for new rules (see `002b-rule-update.md` for versioning policy)
- **LastUpdated:** Creation date in `YYYY-MM-DD` format
- **Keywords:** 5-20 comma-separated terms that appear in task descriptions agents typically receive
- **TokenBudget:** `~NUMBER` format (Small ~800, Medium ~1200, Large ~1800)
- **ContextTier:** Critical / High / Medium / Low (see `002c-rule-optimization.md` for selection guidance)
- **Depends:** At least one rule dependency (e.g., `000-global-core.md`)

## Write Required Sections (v3.2)

For complete v3.2 section requirements and ordering, see `002-rule-governance.md` §Required Sections.

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
- List exact tool names (e.g., `ai-rules validate`, not "validator")
- Include required libraries with versions if critical
- Specify required file access

**Forbidden:**
- Explicitly prohibit problematic approaches
- List tools that should NOT be used
- Call out common mistakes to avoid

**Execution Steps:**
- Actionable, sequential steps
- 5-10 steps (each step should produce a verifiable output)
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

## Validate with ai-rules validate

### Running Validation

See `002e-schema-validator-usage.md` for complete validation commands and options.

Quick reference:

```bash
# Validate single file
uv run ai-rules validate rules/<your-new-rule>.md

# Verbose output (detailed checks)
uv run ai-rules validate rules/<your-new-rule>.md --verbose
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

## Multi-File Task Patterns

### Atomic Changes (Single ACT Session)

Use when files are tightly coupled and changes must be consistent:
- Refactoring that renames functions/classes across files
- Updating API contracts (client + server)
- Schema migrations (DDL + application code)

**Task List Format:**
```
1. Update function signature in `auth.py`
2. Update all call sites in `middleware.py`
3. Update route handlers in `routes.py`
4. Run validation suite (all files)
```

**Rollback Strategy:**

If validation fails, you MUST:
- Revert ALL files to original state
- Return to PLAN mode
- Present revised task list with fixes

**Rollback Mechanisms:**
- **Git repo available (preferred):** Use `git checkout -- <file>` or `git stash`
- **No git, few files:** Store original content in-memory before edit, restore via write tool
- **No git, many files:** Read and store each file before editing; revert individually on failure

**Selection:** Check git availability first (`git status`). If unavailable, use in-memory for simple tasks or incremental for multi-file changes.

**Rollback Reporting:**
```markdown
WARNING: Validation failed. Reverting changes:
- Reverted: `auth.py` (original restored)
- Reverted: `middleware.py` (original restored)
- Unchanged: `routes.py` (not yet modified)

MODE: PLAN
[Revised task list with fixes]
```

### Progressive Changes (Multiple ACT Sessions)

Use when files are loosely coupled:
- Adding independent features to different modules
- Updating documentation across multiple files
- Performance optimizations in separate components

**Task List Format:**
```
Session 1: Update `auth.py`
- [specific changes]
- [validation]
- [await "ACT"]

Session 2: Update `middleware.py`
- [specific changes]
- [validation]
- [await "ACT"]
```
