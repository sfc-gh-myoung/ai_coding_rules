# Rule Schema v3.2 Documentation

**Location:** `schemas/rule-schema.yml`  
**Version:** 3.2  
**Purpose:** Validation schema for AI coding rules per 002-rule-governance.md v3.2

## Overview

This schema defines the structure, content, and format requirements for all AI coding rule files. It is used by `scripts/schema_validator.py` to validate rule files and ensure they are optimized for AI agent comprehension and execution.

**Key v3.2 Changes:**
- ✅ Eliminated `## Purpose` and `## Rule Scope` (separate sections)
- ✅ Eliminated `## Quick Start TL;DR` (redundant with Contract)
- ✅ Added unified `## Scope` section with `**What This Rule Covers:**` and `**When to Load This Rule:**`
- ✅ Moved `## References` early (after Scope, before Contract) for better dependency discovery
- ✅ Contract now uses Markdown headers (`###`) instead of XML tags
- ✅ Added `**SchemaVersion:**` metadata field
- ✅ Increased Keywords to 5-20 terms (was 10-15)

## Schema Structure

The schema is organized into 9 main sections:

1. **Metadata Validation** - SchemaVersion, RuleVersion, Keywords, TokenBudget, ContextTier, Depends
2. **Document Structure** - Required sections, order, placement
3. **Content Validation** - Deep content checks (code blocks, keywords, etc.)
4. **Placement Rules** - Section positioning (Contract before line 200)
5. **Format Restrictions** - No emojis, no YAML frontmatter, universal format
6. **Link Validation** - Rule references, external URLs
7. **Error Reporting** - Grouping, severity levels, formatting
8. **Excluded Files** - Files to skip during validation
9. **Validation Behavior** - Global settings

## Using the Schema

### Validate Single File

```bash
python scripts/schema_validator.py rules/100-snowflake-core.md
```

### Validate Directory

```bash
python scripts/schema_validator.py rules/
```

### Strict Mode (Warnings as Errors)

```bash
python scripts/schema_validator.py rules/ --strict
```

### Custom Schema Path

```bash
python scripts/schema_validator.py rules/ --schema schemas/custom-schema.yml
```

## Severity Levels

Errors are classified by severity:

- **CRITICAL** ❌ - Must fix, blocking (missing required sections, emojis)
- **HIGH** ⚠️  - Should fix, important (missing keywords, wrong order)
- **MEDIUM** ℹ️  - Consider fixing, quality (pattern counts, style)
- **INFO** ✓ - Informational, suggestions

## Metadata Validation

All rule files must have 7 metadata fields in this exact order:

1. **SchemaVersion:** `v3.2` (CRITICAL - must match current schema)
2. **RuleVersion:** Semantic version format `vX.Y.Z` (e.g., v1.0.0)
3. **LastUpdated:** Date format `YYYY-MM-DD` (e.g., 2025-12-23)
4. **Keywords:** 5-20 comma-separated semantic terms
5. **TokenBudget:** `~NUMBER` format (e.g., ~1500)
6. **ContextTier:** `Critical` | `High` | `Medium` | `Low`
7. **Depends:** At least one prerequisite rule (e.g., `000-global-core.md`)

### Agent Impact: Metadata Fields

**SchemaVersion:**
- **Purpose:** Ensures agents know which schema format to expect
- **Agent Impact:** Agents can adapt parsing logic based on schema version
- **Validation:** Must be v3.2 for new/updated rules

**RuleVersion:**
- **Purpose:** Tracks rule evolution and breaking changes
- **Agent Impact:** Agents can detect outdated cached rules
- **Validation:** Semantic versioning (vX.Y.Z)

**LastUpdated:**
- **Purpose:** Provides temporal context for troubleshooting and maintenance tracking
- **Agent Impact:** Helps identify when breaking changes occurred, especially when RuleVersion and SchemaVersion alone are insufficient
- **Validation:** Date format YYYY-MM-DD
- **Use Cases:**
  - Troubleshooting: "Was this rule updated before or after the bug was introduced?"
  - Maintenance: "Which rules haven't been reviewed in 6+ months?"
  - Change tracking: "What rules changed during the v3.1 → v3.2 migration?"
  - Correlation: "Did this rule update coincide with the production issue?"
- **Best Practice:** Update whenever making significant content changes, not just version bumps

**Keywords:**
- **Purpose:** Semantic discovery - agents search keywords to find relevant rules
- **Agent Impact:** Better keyword coverage = better rule discovery
- **Validation:** 5-20 terms (balance between specificity and discoverability)
- **Best Practice:** Include technology names, use cases, and common search terms

**TokenBudget:**
- **Purpose:** Token budget management for context window optimization
- **Agent Impact:** Agents can calculate cumulative token costs before loading
- **Validation:** Must be ~NUMBER format, within ±10% of actual token count
- **Best Practice:** Use `scripts/count_tokens.py` to measure actual tokens

**ContextTier:**
- **Purpose:** Secondary prioritization signal for context management
- **Agent Impact:** Agents defer Low/Medium tier rules when approaching token limits
- **Validation:** Critical | High | Medium | Low
- **Note:** Primary preservation mechanism is natural language markers (CRITICAL/CORE/FOUNDATION)

**Depends:**
- **Purpose:** Dependency graph for rule loading order
- **Agent Impact:** Agents load prerequisites first, avoiding missing context
- **Validation:** At least one dependency (typically 000-global-core.md)
- **Best Practice:** List all rules that provide essential context

**Example:**
```markdown
## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2025-12-23
**Keywords:** snowflake, sql, data warehouse, query optimization, performance, caching, clustering, partitioning, snowpipe, stages, external tables, streams, tasks, materialized views, security
**TokenBudget:** ~2500
**ContextTier:** High
**Depends:** 000-global-core.md
```

## Required Sections (v3.2)

All rules must have these 4 sections in order:

1. **Metadata** - All 6 required fields in correct order
2. **Scope** - What the rule covers + when to load it
3. **References** - Dependencies and external documentation (moved early for discovery)
4. **Contract** - Structured contract with Markdown subsections (###)

### Optional but Recommended:
5. **Anti-Patterns and Common Mistakes** - Code examples showing what NOT to do

## Section Details and Agent Impact

### 1. Scope Section

**Format:**
```markdown
## Scope

**What This Rule Covers:**
[1-3 sentences describing the rule's content and focus areas]

**When to Load This Rule:**
- [Specific scenario 1]
- [Specific scenario 2]
- [Specific scenario 3]
- [Specific scenario 4]
- [Specific scenario 5]
```

**Agent Impact:**
- **Discovery:** Agents use "What This Rule Covers" for semantic search in RULES_INDEX.md
- **Loading Decision:** "When to Load This Rule" helps agents decide if rule is relevant
- **Token Efficiency:** Clear scope prevents loading irrelevant rules
- **Task Matching:** Bullet points map directly to user task descriptions

**Validation:**
- Must contain `**What This Rule Covers:**` (CRITICAL)
- Must contain `**When to Load This Rule:**` (CRITICAL)
- Minimum 5 lines of content (HIGH)

**Best Practices:**
- "What This Rule Covers" should be 1-3 sentences, comprehensive but concise
- "When to Load This Rule" should have 3-7 specific, actionable scenarios
- Use concrete keywords that match how users describe tasks
- Include file extensions, tool names, and common problem descriptions

**Example:**
```markdown
## Scope

**What This Rule Covers:**
Systematic approaches for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage to achieve optimal performance while managing costs effectively.

**When to Load This Rule:**
- Optimizing slow Snowflake queries
- Tuning warehouse performance
- Managing query costs
- Analyzing Query Profile for bottlenecks
- Implementing partition pruning strategies
```

### 2. References Section

**Format:**
```markdown
## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns
- **100-snowflake-core.md** - Snowflake SQL patterns and best practices

**Related:**
- **103-snowflake-performance-tuning.md** - Query optimization patterns
- **119-snowflake-warehouse-management.md** - Warehouse sizing strategies

### External Documentation

- [Query Profile Guide](https://docs.snowflake.com/...) - Query execution analysis
- [Virtual Warehouse Management](https://docs.snowflake.com/...) - Warehouse sizing
```

**Agent Impact:**
- **Dependency Loading:** Agents load "Must Load First" rules before current rule
- **Context Completeness:** Ensures agents have prerequisite knowledge
- **Progressive Loading:** "Related" rules loaded only if needed
- **External Context:** Links provide additional context when agents need deeper understanding

**Validation:**
- Must have "Dependencies" subsection (HIGH)
- Must have "External Documentation" subsection (HIGH)
- Must list at least one dependency (HIGH)

**Best Practices:**
- Separate "Must Load First" (critical) from "Related" (optional)
- Include brief descriptions of why each dependency is needed
- Link to official documentation for authoritative sources
- Keep external links current and accessible

### 3. Contract Section

**Format:**
```markdown
## Contract

### Inputs and Prerequisites
[What agent needs to have/know before starting]

### Mandatory
[Required tools, libraries, access permissions]

### Forbidden
[Actions/patterns that must NOT be used]

### Execution Steps
[5-10 numbered steps for systematic execution]

### Output Format
[Expected format of deliverables]

### Validation
[How to verify successful completion]

### Design Principles
[Core principles guiding implementation]

### Post-Execution Checklist
[Checklist items to verify before completion]
```

**Agent Impact:**
- **Task Understanding:** Contract defines clear expectations and constraints
- **Execution Plan:** Execution Steps provide systematic approach
- **Quality Assurance:** Validation criteria prevent incomplete work
- **Pattern Adherence:** Design Principles guide decision-making
- **Completeness Check:** Post-Execution Checklist ensures nothing missed

**Validation:**
- Must use Markdown headers (`###`), NOT XML tags (CRITICAL)
- Must contain required subsections (HIGH):
  - Inputs and Prerequisites
  - Mandatory
  - Forbidden
  - Execution Steps
  - Output Format
  - Validation
- Recommended subsections:
  - Design Principles
  - Post-Execution Checklist

**Best Practices:**
- Use descriptive subsection names (not numbered)
- Execution Steps should be 5-10 concrete, actionable steps
- Forbidden section prevents common mistakes proactively
- Validation criteria should be objective and measurable
- Design Principles should be concise (3-5 key principles)

**Example:**
```markdown
## Contract

### Inputs and Prerequisites

- Snowflake account with query execution privileges
- Access to Query Profile in Snowsight or via SQL
- Slow query identified (>10s execution time)
- Understanding of table structures and data volumes

### Mandatory

- Query Profile analysis before optimization (CRITICAL)
- SHOW WAREHOUSES, SHOW TABLES for context
- QUERY_HISTORY queries for execution patterns
- Partition pruning verification

### Forbidden

- Optimizing queries without reviewing Query Profile
- Adding clustering keys without evidence of poor pruning
- Using functions in WHERE clause that prevent partition pruning
- Oversizing warehouses without measuring impact

### Execution Steps

1. Identify slow query (execution time, user report, monitoring alert)
2. Open Query Profile in Snowsight or query QUERY_HISTORY
3. Analyze partition pruning: Compare "Partitions Scanned" vs "Partitions Total"
4. Identify bottlenecks: Large TableScans, join explosions, spillage
5. Check WHERE clause for functions that prevent pruning
6. Verify warehouse size appropriate for data volume
7. Apply optimization: Rewrite query, adjust warehouse, consider clustering
8. Measure impact: Compare before/after execution times

### Output Format

- Optimized SQL query with explicit column selection
- Query Profile screenshots or statistics (before/after)
- Performance metrics: Execution time reduction, partitions scanned reduction
- Warehouse sizing recommendations with justification

### Validation

**Test Requirements:**
- Query executes successfully
- Execution time reduced by ≥30%
- Partition pruning improved (lower scanned:total ratio)
- No spillage to remote storage

**Success Criteria:**
- Query Profile shows pruning improvement
- Execution time meets SLA
- No anti-patterns present

### Design Principles

- Use Query Profile to find bottlenecks; maximize pruning
- Right-size warehouses; enable AUTO_SUSPEND/RESUME
- Consider clustering only with clear justification

### Post-Execution Checklist

- [ ] Query Profile analyzed before optimization
- [ ] Partition pruning verified and improved
- [ ] Warehouse appropriately sized
- [ ] Performance improvement measured and documented
```

### 4. Anti-Patterns Section (Optional but Recommended)

**Format:**
```markdown
## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: [Descriptive Name]**
```[language]
-- Bad: [Description of problem]
[incorrect code example]
```
**Problem:** [Why this is wrong, consequences]

**Correct Pattern:**
```[language]
-- Good: [Description of solution]
[correct code example]
```
**Benefits:** [Why this is better, advantages]
```

**Agent Impact:**
- **Error Prevention:** Agents learn what NOT to do before making mistakes
- **Pattern Recognition:** Agents recognize anti-patterns in existing code
- **Code Review:** Agents can identify anti-patterns during review
- **Learning:** Side-by-side comparison accelerates understanding

**Validation:**
- Must have at least 2 code examples (MEDIUM)
- Must contain "Problem:" keyword (MEDIUM)
- Must contain "Correct Pattern:" keyword (MEDIUM)

**Best Practices:**
- Show realistic, production-like examples
- Explain consequences clearly (performance, cost, reliability)
- Provide complete correct alternative, not just criticism
- Use descriptive anti-pattern names that match common mistakes
- Include 3-5 anti-patterns per rule (balance coverage vs token budget)

## Format Restrictions

### No Emojis

**Rule:** No emojis allowed in rule files  
**Severity:** CRITICAL  
**Rationale:** Machine-readable text-only markup required for universal compatibility across all LLM providers and tools

### No YAML Frontmatter

**Rule:** No YAML frontmatter blocks (`---`)  
**Severity:** CRITICAL  
**Rationale:** Universal output format - metadata in inline `**Field:**` format ensures compatibility with all Markdown parsers

### Universal Markdown Format

**Rule:** Pure Markdown syntax only  
**Severity:** HIGH  
**Rationale:** Compatible with all Markdown parsers, tools, and LLM providers

### No Numbered Section Headings

**Rule:** Use descriptive names, not `## 1. Setup` or `## 2. Configuration`  
**Severity:** HIGH  
**Rationale:** Descriptive headings improve semantic understanding and navigation

**Bad:**
```markdown
## 1. Environment Setup
## 2. Configuration
## 3. Execution
```

**Good:**
```markdown
## Environment and Tooling Requirements
## Configuration Best Practices
## Execution Workflow
```

## Link Validation

### Rule References

**Pattern:** `rules/[filename].md` or bare `[filename].md`  
**Check:** File exists  
**Severity:** HIGH

**Example:**
```markdown
**Depends:** 000-global-core.md, 100-snowflake-core.md
```

### External URLs

**Pattern:** `http://` or `https://`  
**Check:** Reachability (optional, disabled by default)  
**Severity:** INFO

## Error Reporting

Errors are grouped by section for easier fixing:

```
================================================================================
VALIDATION REPORT: rules/100-snowflake-core.md
================================================================================

SUMMARY:
  ❌ CRITICAL: 1
  ⚠️  HIGH: 2
  ℹ️  MEDIUM: 3
  ✓ Passed: 12 checks

CRITICAL ISSUES (1):
─────────────────────────────────────────────────────────────────────────────
[Structure] Missing required section: "Scope"
  Line: N/A
  Fix: Add "## Scope" section with "**What This Rule Covers:**" and "**When to Load This Rule:**"
  Reference: 002-rule-governance.md Section 11.2

HIGH ISSUES (2):
─────────────────────────────────────────────────────────────────────────────
[Contract] Contract uses XML tags instead of Markdown headers
  Line: 89-120
  Fix: Replace <inputs_prereqs> with ### Inputs and Prerequisites
  
[Metadata] Keywords count: 4 (expected 5-20)
  Line: 3
  Fix: Add at least 1 more semantic keyword for better discovery

MEDIUM ISSUES (3):
─────────────────────────────────────────────────────────────────────────────
[Anti-Patterns] Only 1 code example found, expected 2+
  Line: 150-180
  Fix: Add 1-2 more anti-pattern examples with code

================================================================================
RESULT: ❌ FAILED (1 CRITICAL, 2 HIGH, 3 MEDIUM issues)
================================================================================
```

## Schema Versioning

**Current Version:** 3.2  
**Strategy:** Single version file - all rules use latest schema (version tracked inside file)

**Version History:**
- **v3.2** (2025-12-23): Eliminated Purpose/Quick Start, added unified Scope, early References, Markdown Contract
- **v3.1** (2025-12): Added ContextTier, improved Contract structure
- **v3.0** (2025-11): Initial YAML schema implementation

**When Schema Changes:**
1. Update `schemas/rule-schema.yml` (version field inside file)
2. Update `schemas/README.md` with new requirements
3. Document breaking changes in CHANGELOG
4. Run validation on all rules
5. Fix high-priority rules first
6. Update `002-rule-governance.md` with new patterns

## Common Validation Scenarios

### Scenario 1: Missing Scope Section

**Error:**
```
[Structure] Missing required section: "Scope"
```

**Fix:**
```markdown
## Scope

**What This Rule Covers:**
[1-3 sentences describing what this rule covers]

**When to Load This Rule:**
- [Specific scenario 1]
- [Specific scenario 2]
- [Specific scenario 3]
```

### Scenario 2: Contract Uses XML Tags

**Error:**
```
[Contract] Contract uses XML tags instead of Markdown headers
```

**Fix:** Replace XML tags with Markdown headers:

**Before (v3.1):**
```markdown
## Contract

<inputs_prereqs>
[Content]
</inputs_prereqs>

<mandatory>
[Content]
</mandatory>
```

**After (v3.2):**
```markdown
## Contract

### Inputs and Prerequisites
[Content]

### Mandatory
[Content]
```

### Scenario 3: Missing Keywords

**Error:**
```
[Metadata] Keywords count: 4 (expected 5-20)
```

**Fix:** Add more semantic keywords:
```markdown
**Keywords:** [original 4], [new keyword 1], [new keyword 2]
```

### Scenario 4: Wrong Schema Version

**Error:**
```
[Metadata] SchemaVersion is v3.1, expected v3.2
```

**Fix:** Update schema version and ensure file follows v3.2 format:
```markdown
**SchemaVersion:** v3.2
```

## Schema Validation Performance

**Expected Performance:**
- Single file: ~10-20ms
- All 111 rules: ~1-2 seconds
- Parallel mode: ~0.5-1 second

**Optimization:**
- Schema caching (loaded once)
- Parallel validation (optional)
- Early exit on critical errors (optional `--fail-fast`)

## Troubleshooting

### Schema Not Found

**Error:** `FileNotFoundError: schemas/rule-schema.yml`

**Fix:** Ensure schema file exists, or specify path:
```bash
python scripts/schema_validator.py rules/ --schema /path/to/schema.yml
```

### Too Many Errors

**Error:** Validation report shows 100+ errors

**Fix:** Use `--fail-fast` to stop on first critical error:
```bash
python scripts/schema_validator.py rules/ --fail-fast
```

### Validation Too Strict

**Issue:** Many false positives, too many warnings

**Fix:** 
1. Check if rule genuinely needs fixing
2. Update schema if rule is correct and schema is too strict
3. Use `--no-strict` to ignore warnings (not recommended for production)

## References

**Related Documentation:**
- `rules/002-rule-governance.md` - Rule standards and governance
- `rules/002a-rule-creation-guide.md` - Step-by-step rule creation guide
- `rules/002b-rule-optimization.md` - Token budgets and optimization

**Schema File:**
- `schemas/rule-schema.yml` - This schema (authoritative source)

**Validator:**
- `scripts/schema_validator.py` - Validation engine
- `scripts/index_generator.py` - RULES_INDEX.md generator

**Tools:**
- `scripts/count_tokens.py` - Token counting for TokenBudget validation
