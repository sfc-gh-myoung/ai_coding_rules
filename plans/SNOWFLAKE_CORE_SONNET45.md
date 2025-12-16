# Rule Review: 100-snowflake-core.md

**Review Date:** 2025-12-12  
**Review Mode:** FULL  
**Reviewing Model:** Claude 3.5 Sonnet (2024-12-03)

## Scores

| Criterion | Score | Notes |
|-----------|-------|-------|
| Actionability | 4/5 | Clear instructions with some ambiguous edge cases |
| Completeness | 3/5 | Missing failure paths, implicit assumptions present |
| Consistency | 4/5 | Generally consistent, minor conflicts with validation strategy |
| Parsability | 5/5 | Well-structured tables, code blocks, and metadata |
| Token Efficiency | 4/5 | TokenBudget accurate, some consolidation opportunities |
| Staleness | 5/5 | Current patterns, references to modern Snowflake features |

**Overall:** 25/30

---

## Executive Summary

This is a **high-quality rule** that provides strong foundational guidance for Snowflake development. The rule excels at parsability and currency, with well-structured examples and modern best practices. The main gaps are in actionability (ambiguous decision criteria) and completeness (missing failure paths and edge case handling).

**Strengths:**
- Excellent anti-pattern examples with clear before/after code
- Well-organized metadata and cross-references
- Current Snowflake features and best practices
- Strong consistency with foundational dependencies

**Critical Gaps:**
1. Missing explicit failure paths for Stream/Task creation and privilege errors
2. Undefined thresholds for subjective terms ("critical query," "high change rate")
3. Incomplete edge case handling for external data and feature unavailability

---

## Critical Issues (Must Fix)

### 1. Ambiguous Conditional Logic in Contract Steps

**Location:** Lines 54-59 (Contract `<steps>`)

**Problem:** Step 4 states "For mutable large tables, design Streams + Tasks incremental pattern with idempotency" but lacks explicit failure handling. What if streams aren't available due to permissions, edition limitations, or other constraints? An agent executing this literally would fail without guidance.

**Recommendation:** Add explicit conditional branches:

```xml
<steps>
4. For mutable large tables:
   - IF table size < 10M rows AND change rate < 10%, THEN allow full reload
   - ELSE design Streams + Tasks incremental pattern with idempotency
   - IF Stream creation fails (permission denied), THEN:
     * Verify GRANT CREATE STREAM ON SCHEMA privilege
     * Escalate to user if privilege cannot be granted
   - IF Streams unavailable (edition restriction), THEN:
     * Use MERGE with timestamp-based incremental logic
     * Document limitation in comment
</steps>
```

---

### 2. Missing Fallback Instructions for External Rule Dependencies

**Location:** Lines 244-256 (Post-Execution Checklist)

**Problem:** Checklist items reference external rules (e.g., `119-snowflake-warehouse-management.md`) but don't specify what to do if those rules aren't loaded or accessible. Agent cannot complete checklist without explicit fallback behavior.

**Recommendation:** Add fallback instructions for each external dependency:

```markdown
- [ ] Warehouse configuration follows `119-snowflake-warehouse-management.md` (type, size, auto-suspend, tags, resource monitor)
      IF rule not loaded: Use defaults (STANDARD warehouse, X-SMALL, AUTO_SUSPEND=60, AUTO_RESUME=TRUE)
- [ ] Row Access Policies or Dynamic Data Masking applied for PII
      IF security rules not loaded: Flag PII columns for review, document in comment
- [ ] Streams and Tasks used for incremental processing where applicable
      IF 104-snowflake-streams-tasks not loaded: Implement basic MERGE with timestamp filter
```

---

### 3. Undefined Criteria for "Critical Query" Validation

**Location:** Lines 269-270 (Validation section)

**Problem:** States "Run and inspect Query Profile for each critical query" but provides no criteria for determining what qualifies as "critical." Agent cannot make this judgment without explicit thresholds.

**Recommendation:** Define explicit, measurable criteria:

```markdown
- Run Query Profile for queries meeting ANY of:
  * Execution time > 30 seconds (measured in QUERY_HISTORY)
  * Scans > 100GB data (visible in Query Profile "Bytes scanned")
  * Runs > 100 times/day (check QUERY_HISTORY frequency)
  * User-flagged as performance-sensitive (explicit annotation in code comment)
  * Part of scheduled Task or production pipeline
- Ensure early filters (WHERE clauses applied before JOINs in Profile operator tree)
- Verify pruning effectiveness (Partitions scanned / Partitions total < 20%)
```

---

## Improvements (Should Fix)

### 4. Template Character Rule Lacks Consequence Specification

**Location:** Lines 36-37 (Quick Start TL;DR), Lines 408-417 (Reserved Characters)

**Problem:** "Avoid template characters in identifiers" is mentioned but consequences aren't explicit until line 416. This is a deployment-breaking issue that should be elevated with clear failure modes.

**Recommendation:** Elevate severity and specify consequences in TL;DR:

```markdown
**MANDATORY:**
**Essential Patterns:**
- **Never use template characters** - `&`, `<%`, `%>`, `{{`, `}}` in identifiers/comments
  VIOLATION: Snowflake CLI deployment fails with "SQL compilation error: syntax error"
```

And in section 8, add handling for existing violations:

```markdown
### Reserved Characters (CLI Compatibility)
- **Rule:** Avoid characters that Snowflake CLI interprets as template variables
- **Forbidden:** `&`, `<%`, `%>`, `{{`, `}}`
- **Consequence:** Deployment via `snow sql` fails with cryptic syntax errors
- **IF existing data contains forbidden characters:**
  1. In comments: Use REPLACE() during migration: `COMMENT = REPLACE(old_comment, '&', 'and')`
  2. In identifiers: Rename objects or use quoted identifiers (not recommended)
  3. In string literals: Escape with backslash or replace during INSERT/UPDATE
```

---

### 5. Ambiguous Scope for "Shared Code" in Fully Qualified Names

**Location:** Lines 313-319 (Section 1: General Principles)

**Problem:** States "Always fully qualify objects (DATABASE.SCHEMA.OBJECT) in shared code" but doesn't define "shared code." An agent cannot determine when to apply this rule.

**Recommendation:** Define scope explicitly with decision tree:

```markdown
- **Rule:** Always fully qualify objects in:
  * SQL files committed to version control
  * Views, materialized views, stored procedures, UDFs
  * Task and Dynamic Table definitions
  * Any SQL executed via CI/CD or automation
  
  **EXCEPTION (USE DATABASE/SCHEMA acceptable):**
  * Ad-hoc queries in personal Snowsight worksheets
  * Jupyter notebooks for exploratory analysis (not production)
  * Local development scripts not committed to repo
  
  **Decision:** IF file is in git OR executed by automation, THEN fully qualify
```

---

### 6. Missing Quantifiable Guidance for "Early Filtering"

**Location:** Lines 321-327 (Section 2: Optimization)

**Problem:** "Push filtering and partition pruning as early as possible" lacks quantifiable validation criteria. Agent cannot verify compliance without measurable targets.

**Recommendation:** Add measurable criteria and validation method:

```markdown
- **Always:** Apply WHERE clauses BEFORE JOINs
  * Validation: Check Query Profile operator tree order
  * Target: Filter operator should appear before Join operator in execution plan
  
- **Always:** Enable partition pruning with date/timestamp filters
  * Validation: Query Profile shows "Partitions scanned" << "Partitions total"
  * Target: Prune >80% of partitions (e.g., 200 scanned of 1000 total)
  
- **How to measure:**
  1. Run query and copy Query ID from results
  2. Navigate to Query Profile in Snowsight
  3. Check "Profile Overview" → "Partitions scanned" metric
  4. Verify filter predicates appear in "Most Expensive Nodes"
```

---

### 7. No Guidance for External Data with Duplicates

**Location:** Lines 337-340 (Section 4: Anti-Patterns)

**Problem:** States "Do not use DISTINCT to fix duplicates; solve the root cause upstream" but provides no guidance when root cause is external (vendor data, third-party APIs). Agent needs exception handling.

**Recommendation:** Add exception handling and documentation requirements:

```markdown
- **Rule:** Do not use DISTINCT to fix duplicates

- **IF duplicates are from internal processes:**
  * Identify root cause (bad JOIN, missing GROUP BY, etc.)
  * Fix upstream query or data pipeline
  * Use ROW_NUMBER() with QUALIFY for explicit deduplication logic

- **IF duplicate source is external AND unmodifiable:**
  * Use ROW_NUMBER() with QUALIFY (preferred over DISTINCT)
  * Document root cause in comment above query:
    ```sql
    -- External API returns duplicate records when pagination overlaps
    -- Using ROW_NUMBER to keep latest record based on updated_at timestamp
    SELECT ... FROM source_table
    QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1;
    ```
  * Add data quality monitoring (see 124-snowflake-data-quality-core.md):
    ```sql
    -- Create DMF to track duplicate rate
    CREATE DATA METRIC FUNCTION duplicate_rate_dmf(...)
    ```
```

---

### 8. Missing Handling for Reserved Characters in Existing Data

**Location:** Lines 408-417 (Reserved Characters)

**Problem:** Rule forbids characters in new objects but doesn't specify how to handle existing data containing them. Agent needs migration guidance.

**Recommendation:** Already covered in Issue #4 above.

---

## Minor Suggestions (Nice to Have)

### 9. Add Token Budget Guidance for TL;DR Usage

**Location:** Lines 20-37 (Quick Start TL;DR)

**Enhancement:** Help agents understand when TL;DR is sufficient vs. loading full rule.

**Recommendation:**

```markdown
**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases (~15% of full rule, ~400 tokens)
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

**When TL;DR is sufficient:**
- Single query optimization
- Basic view creation
- Simple table DDL

**When to load full rule:**
- Complex incremental pipelines
- Performance troubleshooting
- Security policy implementation
- Production deployment patterns
```

---

### 10. Add Failure Example to Output Format Section

**Location:** Lines 274-290 (Output Format Examples)

**Enhancement:** Currently only shows success patterns. Adding failure examples helps agents recognize anti-patterns.

**Recommendation:**

```sql
-- ❌ ANTI-PATTERN: What NOT to do
SELECT * FROM RAW_DB.STAGE.ORDERS_JSON  -- SELECT * wastes I/O
WHERE v:order_ts::timestamp_ntz >= DATEADD(day, -7, CURRENT_TIMESTAMP());  -- Parsing VARIANT in WHERE

-- ❌ Result: Scans all columns, parses VARIANT multiple times, slow and expensive

-- ✅ CORRECT PATTERN: Parse VARIANT once, explicit columns
WITH src AS (
  SELECT v:customer_id::string AS customer_id,
         v:order_ts::timestamp_ntz AS order_ts,
         v:total_amount::number AS total_amount
  FROM RAW_DB.STAGE.ORDERS_JSON
  WHERE v:order_ts::timestamp_ntz >= DATEADD(day, -7, CURRENT_TIMESTAMP())
)
SELECT * FROM src;

-- ✅ Result: Minimal I/O, single VARIANT parse, fast and cost-effective
```

---

### 11. Add Decision Tree for Related Rule Loading

**Location:** Lines 359-372 (Section 7: Related Specialized Rules)

**Enhancement:** Help agents select which related rules to load based on task context.

**Recommendation:**

```markdown
## 7. Related Specialized Rules

**Rule Selection Decision Tree:**

**IF task involves:**
- Creating/managing warehouses → Load `119-snowflake-warehouse-management.md` (High priority)
- Query performance issues → Load `103-snowflake-performance-tuning.md` (High priority)
- Incremental pipelines → Load `104-snowflake-streams-tasks.md` (High priority)
- Security/RBAC/masking → Load `107-snowflake-security-governance.md` (High priority)

**IF task involves:**
- Demo/workshop SQL → Load `102-snowflake-sql-demo-engineering.md` (Medium priority)
- Cost tracking/budgets → Load `105-snowflake-cost-governance.md` (Medium priority)
- Semantic views → Load `106-snowflake-semantic-views-core.md` (Medium priority)
- Data loading → Load `108-snowflake-data-loading.md` (Medium priority)

**Token Budget:** Most tasks need 100-snowflake-core + 1-2 specialized rules (~8,000-12,000 tokens)
```

---

### 12. Add Explicit Action for Deep View Nesting Discovery

**Location:** Line 338 (Section 4: Anti-Patterns)

**Problem:** States "Avoid deep view nesting (>5 layers)" but doesn't specify what to do when discovering existing violations.

**Recommendation:**

```markdown
- **Rule:** Avoid deep view nesting (>5 layers)

- **IF creating new view:**
  * Check dependency chain with:
    ```sql
    SHOW VIEWS LIKE 'my_view';
    -- Manually trace dependencies in view definition
    ```
  * Keep nesting ≤5 layers

- **IF encountering >5 layers in existing code:**
  1. Refactor by flattening intermediate layers into single CTE
  2. OR materialize intermediate results as tables/materialized views
  3. OR if cannot refactor (legacy system), document:
     ```sql
     -- WARNING: 7-layer view nesting (legacy, refactor pending)
     -- Layers: VW_A → VW_B → VW_C → VW_D → VW_E → VW_F → VW_G
     ```
```

---

### 13. Define Threshold for "High Change Rate"

**Location:** Line 340 (Section 4: Anti-Patterns)

**Problem:** States "avoid recomputing large fact tables from scratch daily unless a high change rate is necessary" but "high change rate" is undefined. Agent cannot evaluate this condition.

**Recommendation:**

```markdown
- **Rule:** Avoid full recompute of fact tables UNLESS change rate >30% daily

- **How to measure change rate:**
  ```sql
  -- Check DML frequency in last 7 days
  SELECT 
    table_name,
    COUNT(*) as dml_operations,
    SUM(rows_inserted + rows_updated + rows_deleted) as total_rows_changed,
    (total_rows_changed / MAX(row_count)) * 100 as change_rate_pct
  FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
  WHERE table_schema = 'PROD'
    AND table_name = 'FACT_ORDERS'
    AND query_timestamp >= DATEADD(day, -7, CURRENT_TIMESTAMP())
  GROUP BY table_name;
  ```

- **Decision:**
  * IF change_rate_pct < 10%: Use incremental (Streams + Tasks)
  * IF change_rate_pct 10-30%: Evaluate cost/complexity tradeoff
  * IF change_rate_pct > 30%: Full reload may be simpler and cost-effective
```

---

## Additional Specific Recommendations

### 14. Add Error Recovery to Streams + Tasks Example

**Location:** Lines 174-203 (Anti-Pattern 3: Streams and Tasks)

**Problem:** Shows correct pattern but doesn't cover common failure modes (permission errors, warehouse suspended, stream lag).

**Recommendation:** Add failure handling section after line 203:

```sql
-- TROUBLESHOOTING: Common Streams + Tasks failures

-- Issue 1: Stream creation fails (insufficient privileges)
-- Error: "SQL access control error: Insufficient privileges to operate on schema"
-- Solution:
GRANT USAGE ON SCHEMA my_schema TO ROLE my_role;
GRANT CREATE STREAM ON SCHEMA my_schema TO ROLE my_role;

-- Issue 2: Task execution fails (warehouse auto-suspended)
-- Error: "Object does not exist, or operation cannot be performed"
-- Solution:
ALTER WAREHOUSE compute_wh SET AUTO_RESUME = TRUE;
ALTER TASK incremental_aggregation RESUME;

-- Issue 3: Stream has data but Task didn't run
-- Diagnosis:
SHOW TASKS LIKE 'incremental_aggregation';  -- Check state (suspended?)
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE name = 'INCREMENTAL_AGGREGATION'
ORDER BY scheduled_time DESC LIMIT 10;  -- Check error messages

-- Issue 4: Stream lag growing (processing can't keep up)
-- Diagnosis:
SELECT SYSTEM$STREAM_HAS_DATA('orders_stream');  -- Check if data pending
-- Solution: Increase warehouse size or Task frequency
```

---

### 15. Add Conditional for Time Travel Availability

**Location:** Line 333 (Section 3: Security and Governance)

**Problem:** States "Use Time Travel and Cloning for safe development" but assumes feature is available. Time Travel requires Enterprise Edition and configured retention.

**Recommendation:**

```markdown
- **Always:** Use Time Travel and Cloning for safe development, testing, and dev/test isolation

- **Prerequisite check:**
  ```sql
  -- Verify Time Travel retention configured
  SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN ACCOUNT;
  SHOW PARAMETERS LIKE 'DATA_RETENTION_TIME_IN_DAYS' IN DATABASE my_db;
  ```

- **IF Time Travel available (retention > 0 days):**
  * Use for safe schema changes:
    ```sql
    -- Backup before change
    CREATE TABLE backup_table CLONE production_table;
    
    -- Or use Time Travel for recovery
    SELECT * FROM production_table AT(OFFSET => -60*60);  -- 1 hour ago
    ```

- **IF Time Travel NOT available (Standard Edition or retention = 0):**
  * Implement manual backup strategy:
    ```sql
    -- Create backup before schema changes
    CREATE TABLE backup_table AS SELECT * FROM production_table;
    ```
  * Document limitation in runbook
```

---

## Staleness Indicators Found

**None detected.** The rule references current Snowflake features and best practices as of 2025:

- ✅ **QUALIFY clause:** Introduced 2020, now standard best practice
- ✅ **Dynamic Tables:** GA in 2023, correctly referenced in related rules
- ✅ **Streams + Tasks:** Current best practice for incremental processing
- ✅ **VARIANT parsing patterns:** Aligns with current Snowflake optimization guides
- ✅ **Warehouse types:** References `119-snowflake-warehouse-management.md` for current offerings (Standard, Snowpark-Optimized, High-Memory)
- ✅ **Documentation links:** Point to `docs.snowflake.com` (canonical, version-agnostic URLs)
- ✅ **Security patterns:** Row Access Policies and Dynamic Data Masking are current
- ✅ **Object naming:** Template character warnings align with current Snowflake CLI behavior

**No deprecated features referenced.**

**API/Tool versions:** All references are to current stable features without version pinning (appropriate for a platform rule).

---

## Dependency Drift Check

**Declared Dependency:** `rules/000-global-core.md`

### Alignment Verification

✅ **MODE workflow:** Rule properly inherits PLAN/ACT protocol
- Implicit in Contract `<validation>` section (line 66-72)
- Checklist references validation (line 267-272)

✅ **Surgical editing:** Rule reinforces minimal changes principle
- Line 75: "prefer set-based SQL with clear CTEs"
- Contract `<design_principles>` emphasizes targeted optimization

✅ **Validation-first:** Rule mandates Query Profile inspection
- Lines 267-272: Explicit validation requirements
- Post-Execution Checklist includes validation (line 249)

✅ **Professional communication:** Rule uses technical tone
- SQL-first, minimal prose
- Line 63-64: "SQL snippets or task definitions only"

### Conflicts Found

**None.** The rule properly inherits and extends foundational patterns without contradicting parent rule.

### Missing Dependencies

**None.** The rule correctly lists only its foundational dependency. Specialized rules (103, 104, 105, etc.) are properly listed as "Related Rules" rather than hard dependencies.

### Related Rules Alignment

Lines 301-311 and 359-372 provide comprehensive cross-references. Verification against RULES_INDEX.md:

✅ All referenced rules exist in index  
✅ Dependency chains are accurate (e.g., 101 → 100, 104 → 100)  
✅ Keywords align with index (e.g., "streams" → 104, "warehouse" → 119)  

---

## Agent Perspective Checklist

Evaluating whether an agent with no context beyond this rule could execute every instruction:

- [x] ✅ **Could execute most instructions:** 80% of rule is actionable with loaded context
  - SQL examples are copy-pasteable
  - Anti-patterns have clear before/after
  - Validation commands are explicit

- [ ] ❌ **Judgment calls remain:** Some decisions require undefined criteria
  - "Critical query" (no threshold)
  - "High change rate" (no percentage)
  - "Shared code" (ambiguous scope)
  - "Large tables" (no size threshold)

- [ ] ❌ **Some literal execution would fail:** Missing error handling
  - Stream creation without privilege check
  - Query Profile access without permission validation
  - External rule references without fallback

- [x] ✅ **Most decision points are binary or enumerated**
  - Anti-pattern examples are excellent (208 lines, 20% of rule)
  - Contract steps are mostly clear
  - Validation commands are specific

- [ ] ⚠️ **Examples focus on success; failure modes need coverage**
  - 4 anti-pattern examples with fixes (excellent)
  - 0 error recovery examples (gap)
  - 0 privilege failure examples (gap)
  - 0 feature unavailability examples (gap)

**Gap Summary:**
1. **Thresholds:** 5 undefined thresholds (critical, large, high, deep, early)
2. **Error paths:** 8 common failures without recovery guidance
3. **Conditionals:** 4 IF statements without ELSE branches

---

## Recommendations Summary

### Priority 1: Critical (Blocks agent execution)

1. **Add explicit failure paths** for Stream/Task creation (Lines 54-59)
2. **Define thresholds** for "critical query," "high change rate" (Lines 269-270, 340)
3. **Add fallback instructions** for external rule dependencies (Lines 244-256)

**Estimated effort:** 2 hours

---

### Priority 2: High (Improves reliability)

4. **Elevate template character warnings** with consequences (Lines 36-37)
5. **Define scope** for "shared code" qualification (Lines 313-319)
6. **Add quantifiable criteria** for optimization validation (Lines 321-327)
7. **Add exception handling** for external duplicate sources (Lines 337-340)

**Estimated effort:** 1.5 hours

---

### Priority 3: Medium (Enhances usability)

9. **Add token budget guidance** for TL;DR usage (Lines 20-37)
10. **Add failure examples** to Output Format (Lines 274-290)
11. **Add decision tree** for related rule loading (Lines 359-372)
12. **Add explicit action** for deep nesting discovery (Line 338)
13. **Define threshold** for change rate (Line 340)

**Estimated effort:** 1 hour

---

### Priority 4: Low (Nice to have)

14. **Add error recovery** to Streams + Tasks example (Lines 174-203)
15. **Add conditional** for Time Travel availability (Line 333)

**Estimated effort:** 0.5 hours

---

## Total Estimated Effort

**5 hours** to address all recommendations across all priority levels.

**Quick Win (2 hours):** Addressing Priority 1 issues would increase actionability from 4/5 to 5/5 and completeness from 3/5 to 4/5, raising overall score from 25/30 to 28/30.

---

## Conclusion

`100-snowflake-core.md` is a **strong foundational rule** with excellent structure, current best practices, and comprehensive anti-pattern coverage. The primary improvements needed are:

1. **Explicit failure paths** for privilege errors and feature unavailability
2. **Quantified thresholds** for subjective decision criteria
3. **Error recovery patterns** for common operational failures

With these enhancements, the rule would provide complete, unambiguous guidance suitable for autonomous agent execution without human judgment calls.

**Recommended action:** Implement Priority 1 fixes (2 hours) to achieve high confidence in agent executability.

