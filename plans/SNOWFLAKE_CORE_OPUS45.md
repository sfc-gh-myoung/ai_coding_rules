# Rule Review: 100-snowflake-core.md

**Review Date:** 2025-12-12
**Review Mode:** FULL
**Target File:** rules/100-snowflake-core.md

## Scores

| Criterion | Score | Notes |
|-----------|-------|-------|
| Actionability | 4/5 | Instructions are mostly clear, but some guidance uses "Always" and "Rule" prefixes inconsistently; several conditionals lack explicit else branches |
| Completeness | 3/5 | Happy path well-covered; error conditions, recovery steps, and edge cases mostly absent; some implicit assumptions about agent knowledge |
| Consistency | 4/5 | Internal consistency is strong; minor redundancy between sections (anti-patterns appear in multiple places); no conflicts with dependencies |
| Parsability | 4/5 | Well-structured with proper tables, code blocks, and lists; metadata is machine-readable; some prose mixed with actionable items |
| Token Efficiency | 4/5 | TokenBudget ~2850 appears reasonable for 2265 words/433 lines; some redundancy between Quick Start TL;DR and later sections could be trimmed |
| Staleness | 4/5 | Core SQL patterns are current; documentation links are valid; no deprecated features referenced; Snowflake platform evolves but guidance remains applicable |

**Overall:** 23/30

**Reviewing Model:** Claude Opus 4.5 (claude-sonnet-4-20250514)

## Critical Issues (Must Fix)

### 1. Missing Error Recovery Paths

**Location:** Contract `<steps>` section (lines 54-59)

**Problem:** Steps 1-5 describe the happy path but provide no guidance for when validation fails (step 5). An agent encountering a Query Profile showing poor pruning has no explicit instruction on what to do next.

**Recommendation:** Add explicit failure branches:

```xml
<steps>
1. Define explicit columns and joins; add early filters
2. Normalize VARIANT once in a dedicated CTE
3. Prefer set-based ops; avoid row-wise loops
4. For mutable large tables, design Streams + Tasks incremental pattern with idempotency
5. Validate with Query Profile before scaling warehouse
   - IF pruning < 90%: Review WHERE clauses and partition keys
   - IF spillage detected: Reduce data volume or increase warehouse size
   - IF validation passes: Proceed to deployment
</steps>
```

### 2. Ambiguous Threshold: "Deep View Nesting (>5 layers)"

**Location:** Section 4. Anti-Patterns, line 337

**Problem:** States ">5 layers" is bad but doesn't specify what an agent should do when encountering exactly 5 layers or when tasked to create views that would exceed this threshold.

**Recommendation:** Make explicit: "If view nesting would exceed 5 layers, refactor intermediate views into materialized tables or dynamic tables. If nesting is exactly 5 layers, document the architectural justification."

### 3. Conflicting SELECT * Guidance in Output Example

**Location:** Lines 289

**Problem:** The Output Format Example ends with `SELECT * FROM agg;` which directly contradicts the rule's own prohibition on `SELECT *` (lines 35, 86-108, 331).

**Recommendation:** Replace with explicit column list:

```sql
SELECT customer_id, num_orders, total_amount FROM agg;
```

## Improvements (Should Fix)

### 1. Implicit Assumption: Agent Knows Query Profile Location

**Location:** Lines 59, 249, 268

**Problem:** Multiple references to "Query Profile" assume the agent knows how to access it. An agent unfamiliar with Snowsight UI navigation would be uncertain.

**Recommendation:** Add explicit instruction: "Access Query Profile via: Snowsight → Activity → Query History → Select query → Query Profile tab, OR use `SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY()) WHERE QUERY_ID = '<id>';`"

### 2. "Always" vs "Rule" Prefix Inconsistency

**Location:** Sections 1-6 (lines 313-355)

**Problem:** Uses both "Always:" and "Rule:" prefixes inconsistently. An agent cannot determine if these have different priority levels.

**Recommendation:** Standardize to a single prefix or explicitly define the semantic difference (e.g., "Always = mandatory in all contexts; Rule = mandatory when applicable").

### 3. Missing Warehouse Type Selection Decision Tree

**Location:** Post-Execution Checklist, line 248

**Problem:** References `119-snowflake-warehouse-management.md` for warehouse configuration but doesn't provide fallback guidance if that rule isn't loaded. Agent would be blocked.

**Recommendation:** Add minimal inline guidance: "For warehouse selection: Standard for general SQL, Snowpark-Optimized for ML/heavy Python, High-Memory for large data shuffles. See 119-snowflake-warehouse-management.md for details."

### 4. Duplicate Anti-Pattern Coverage

**Location:** Lines 84-256 (Anti-Patterns section) vs. Lines 336-340 (Section 4. Anti-Patterns)

**Problem:** Anti-patterns are covered in two separate sections with overlapping but not identical content. This could confuse an agent about authoritative guidance.

**Recommendation:** Consolidate all anti-patterns into the main "Anti-Patterns and Common Mistakes" section and convert Section 4 to a reference: "See Anti-Patterns and Common Mistakes section above."

### 5. Incomplete Template Character Guidance

**Location:** Lines 407-416

**Problem:** States which characters to avoid but doesn't provide guidance on what to do if an agent encounters existing objects with these characters.

**Recommendation:** Add: "If existing objects contain forbidden characters, do NOT rename without explicit user authorization. Document the issue and propose renaming in PLAN mode."

## Minor Suggestions (Nice to Have)

### 1. Keywords Could Include More Discovery Terms

**Location:** Metadata, line 6

**Problem:** Keywords don't include common search terms like "DDL", "naming conventions", "object naming", "VARIANT", "JSON parsing"

**Recommendation:** Expand keywords: `SQL, CTE, performance, cost optimization, query profile, warehouse, security, governance, stages, COPY INTO, streams, tasks, warehouse creation, DDL, naming conventions, VARIANT, JSON, semi-structured`

### 2. Documentation Links Use Bare URLs in Prose

**Location:** Lines 326, 333, 345

**Problem:** Inline URLs in prose are harder to parse than the structured format in the References section.

**Recommendation:** Either remove inline URLs (they're duplicated in References) or convert to consistent markdown link format.

### 3. ROW_NUMBER() vs QUALIFY Inconsistency

**Location:** Line 255 vs. Lines 229-241

**Problem:** Checklist says "use ROW_NUMBER() instead" but the detailed example correctly uses `QUALIFY ROW_NUMBER()`. The checklist is technically accurate but less precise.

**Recommendation:** Update checklist to: "No DISTINCT used for deduplication (use QUALIFY with ROW_NUMBER() instead)"

## Specific Recommendations Summary

| # | Location | Problem | Recommendation |
|---|----------|---------|----------------|
| 1 | Line 289 | `SELECT * FROM agg` contradicts rule's own prohibition | Change to `SELECT customer_id, num_orders, total_amount FROM agg;` |
| 2 | Lines 54-59 | No failure branches in steps | Add IF/THEN branches for validation failures |
| 3 | Line 337 | ">5 layers" threshold has no action guidance | Add explicit refactoring instruction |
| 4 | Lines 313-355 | "Always:" vs "Rule:" prefix inconsistency | Standardize or define semantic difference |
| 5 | Line 248 | External dependency without fallback | Add minimal inline warehouse guidance |

## Staleness Indicators Found

- **Tool Versions:** None detected - rule is tool-agnostic for SQL
- **Deprecated Patterns:** None detected - Streams, Tasks, CTEs, QUALIFY all current
- **API Changes:** None detected - SQL syntax is stable
- **Industry Shifts:** None detected - guidance aligns with current Snowflake best practices
- **Documentation Links:** All 7 URLs reference current Snowflake documentation paths (verified structure, not live links)

**Note:** Snowflake releases features continuously. While no staleness was detected, the following should be monitored:

- Dynamic Tables (mentioned in naming conventions) - relatively new feature, guidance may evolve
- High-Memory warehouses - referenced via 119 rule, ensure that rule stays current

## Dependency Drift Check

- **Depends:** `rules/000-global-core.md`
- **Conflicts Found:** None - 100-snowflake-core.md properly defers to 000-global-core.md for MODE/ACT workflow
- **Missing Dependencies:** None required - this is appropriately a foundation rule

**Cross-Reference Verification:**

The rule references 14 other Snowflake rules in Section 7 (Related Specialized Rules). These are correctly presented as "reference for deeper guidance" rather than dependencies, which is appropriate for a core rule.

## Agent Perspective Checklist

- [x] If I were an agent with no context beyond this rule, could I execute every instruction?
  - **Mostly yes**, but would need Query Profile access instructions and warehouse type selection guidance
- [ ] Are there places where I'd need to "use judgment" (agents can't)?
  - **Yes**: "Prefer declarative set-based operations" (line 316) - "prefer" requires judgment
  - **Yes**: "when useful" (line 398) - subjective assessment
  - **Yes**: "when you must distinguish" (line 394) - judgment call
- [x] Would following this rule literally produce the intended outcome?
  - **Mostly yes**, except for the SELECT * contradiction in the example
- [ ] Are all decision points binary or explicitly enumerated?
  - **No**: Several thresholds (>5 layers, "large tables") lack explicit boundaries
- [ ] Do examples cover failure modes, not just success cases?
  - **Partially**: Anti-patterns show what NOT to do, but no examples of recovering from failures

## Summary

This is a well-structured, comprehensive Snowflake foundation rule with strong actionability for common cases. The main gaps are around error recovery paths, some internal inconsistencies (particularly the SELECT * example), and a few places requiring agent judgment. Addressing the critical issues would elevate this from a good reference document to an excellent agent instruction set.

### Priority Action Items

1. **Immediate:** Fix the `SELECT * FROM agg` example (contradicts core rule)
2. **High:** Add failure recovery branches to Contract steps
3. **Medium:** Consolidate duplicate anti-pattern sections
4. **Low:** Expand keywords for better discoverability

