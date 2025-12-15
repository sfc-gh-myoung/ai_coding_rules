# Example: Snowflake Feature Rule Creation (Hybrid Tables)

## User Request

```
Create a new Cursor rule documenting Snowflake Hybrid Tables best practices following v3.0 schema
```

## Abbreviated Workflow (Key Steps Only)

### Phase 1: Discovery (6 min)

**Search RULES_INDEX.md:**
```bash
$ grep -i "snowflake\|hybrid\|unistore\|oltp" RULES_INDEX.md
|| `100-snowflake-core.md` | Snowflake foundations | ...
|| `122-snowflake-dynamic-tables.md` | Dynamic Tables | ...
|| `123-snowflake-object-tagging.md` | Object tagging | ...

# Analysis:
Domain: 100-199 (Snowflake)
Gap after: 123
Next available: 125 (124 is data quality, 125 is free)
```

**Research findings (Snowflake docs):**
- Hybrid Tables for OLTP workloads (GA in 2024)
- Row-level locking for concurrent writes
- Primary key enforcement
- Unistore architecture
- Integration with traditional Snowflake tables

**Keywords (15):**
```
snowflake, hybrid tables, OLTP, unistore, row-level locking, primary key,
concurrent writes, transactional, data integrity, unique constraints,
indexes, performance optimization, query patterns, table design, workload management
```

---

### Phase 2: Template Generation (1 min)

```bash
$ python scripts/template_generator.py 125-snowflake-hybrid-tables \
    --context-tier High \
    --output-dir rules/

✅ Created rule template: rules/125-snowflake-hybrid-tables.md
```

**Note:** Used "High" tier because Hybrid Tables are a major Snowflake feature (not specialized/rare)

---

### Phase 3: Content Population (12 min)

**Metadata:**
```markdown
**Keywords:** snowflake, hybrid tables, OLTP, unistore, row-level locking, primary key, concurrent writes, transactional, data integrity, unique constraints, indexes, performance optimization, query patterns, table design, workload management
**TokenBudget:** ~1800
**ContextTier:** High
**Depends:** rules/000-global-core.md, rules/100-snowflake-core.md
```

**Purpose:**
```markdown
## Purpose

Establishes best practices for Snowflake Hybrid Tables, enabling OLTP workloads with row-level locking, primary key enforcement, and transactional consistency while integrating with Snowflake's analytical capabilities.
```

**Essential Patterns:**
```markdown
- **Primary key required:** Always define PRIMARY KEY constraint for row-level locking
- **Appropriate workload:** Use for high-concurrency writes and point lookups, not bulk analytics
- **Index strategically:** Create indexes on frequently queried non-key columns for performance
- **Integration pattern:** Join Hybrid Tables with regular tables for mixed OLTP/OLAP queries
- **Row-level locking:** Leverage for concurrent UPDATE/DELETE without table-level locks
```

**Sample Anti-Pattern:**
```markdown
### Anti-Pattern 1: Using Hybrid Tables for Bulk Analytics

**Problem:** Creating Hybrid Tables for large analytical workloads instead of regular tables

```sql
-- Wrong: Hybrid Table for data warehouse fact table
CREATE HYBRID TABLE fact_sales (  -- Hybrid table inappropriate here
    sale_id INT PRIMARY KEY,
    ...millions of rows for analytics...
);
```

**Why It Fails:**
- Hybrid Tables optimized for OLTP, not bulk scans
- Higher cost per operation than regular tables
- Micro-partitioning less effective for analytics
- Missing clustering keys optimization

**Correct Pattern:**
```sql
-- Right: Regular table for analytics, Hybrid for transactional
CREATE OR REPLACE TABLE fact_sales (  -- Regular table for OLAP
    sale_id INT,
    customer_id INT,
    sale_amount DECIMAL(10,2),
    sale_date DATE
)
CLUSTER BY (sale_date);  -- Optimize for time-series queries

CREATE HYBRID TABLE current_orders (  -- Hybrid for OLTP
    order_id INT PRIMARY KEY,
    status VARCHAR,
    last_updated TIMESTAMP
);
```

**Benefits:**
- Right tool for right workload
- Cost-effective architecture
- Optimal performance for each use case
```

**Contract filled with Snowflake-specific requirements:**
```markdown
<inputs_prereqs>
Snowflake account with Hybrid Tables enabled; understanding of OLTP vs OLAP workloads; SQL DDL knowledge
</inputs_prereqs>

<mandatory>
Snowflake Enterprise Edition or higher; CREATE HYBRID TABLE privilege; warehouse for testing
</mandatory>

<forbidden>
Don't use Hybrid Tables for bulk analytics; don't omit PRIMARY KEY; don't create without indexes on query patterns; avoid excessive index creation
</forbidden>

<steps>
1. Identify workload as OLTP (high concurrency writes, point lookups)
2. Design schema with PRIMARY KEY for row-level locking
3. Create HYBRID TABLE with constraints and indexes
4. Test concurrent write performance
5. Monitor query patterns and adjust indexes
6. Integrate with regular tables for mixed workloads if needed
</steps>
```

---

### Phase 4: Validation (3 min, 2 iterations)

**Iteration 1:**
```bash
$ python scripts/schema_validator.py rules/125-snowflake-hybrid-tables.md

SUMMARY:
  ❌ CRITICAL: 1
  ⚠️  HIGH: 0

❌ CRITICAL ISSUES (1):
[Metadata] TokenBudget format invalid: expected ~NUMBER format
  Line: 7
  Fix: Change "1800" to "~1800"

RESULT: ❌ FAILED (exit code 1)
```

**Fix:** Added tilde to TokenBudget: `~1800`

**Iteration 2:**
```bash
$ python scripts/schema_validator.py rules/125-snowflake-hybrid-tables.md

SUMMARY:
  ❌ CRITICAL: 0
  ⚠️  HIGH: 0
  ℹ️  MEDIUM: 1
  ✓ Passed: 458 checks

RESULT: ⚠️  WARNINGS ONLY (exit code 0)
```

✓ Validation passed

---

### Phase 5: Indexing (1 min)

**Entry:**
```markdown
| 125-snowflake-hybrid-tables | Snowflake Hybrid Tables for OLTP workloads with row-level locking | snowflake, hybrid tables, OLTP, unistore, row-level locking, primary key, concurrent writes, transactional | rules/100-snowflake-core.md |
```

**Inserted between:**
```bash
|| `124b-snowflake-data-quality-operations.md` | ...
|| `125-snowflake-hybrid-tables.md` | ... [NEW]
|| `200-python-core.md` | ...
```

✓ Indexed successfully

---

## Final Output

```
✅ Production-ready rule created: rules/125-snowflake-hybrid-tables.md

Statistics:
- Total time: ~23 minutes
- Validation iterations: 2
- Size: ~22KB, ~550 lines
- TokenBudget: ~1800 tokens
- ContextTier: High (major feature)

Ready for use: @rules/125-snowflake-hybrid-tables.md
```

## Key Differences from Other Examples

**Domain:** Snowflake (100-199) - enterprise data platform
**Complexity:** Higher - required deeper technical knowledge
**Research:** Official Snowflake docs (not community practices)
**ContextTier:** High (vs Medium for others) - major platform feature
**TokenBudget:** Larger (~1800 vs ~1000-1200) - more complex topic

**Challenges:**
- Hybrid Tables are newer (2024 GA) - less community content
- Required understanding of Unistore architecture
- Had to distinguish from Dynamic Tables (122)
- Forgot tilde in TokenBudget (caught by validator)

**Success factors:**
- Clear use case (OLTP workloads)
- Official documentation was comprehensive
- Good contrast with regular tables in anti-patterns
- Followed Snowflake rule patterns from 100-124 range

## Comparison Across All 3 Examples

| Aspect | DaisyUI (422) | pytest-mock (209) | Hybrid Tables (125) |
|--------|---------------|-------------------|---------------------|
| Domain | Frontend (420-449) | Python (200-299) | Snowflake (100-199) |
| ContextTier | Medium | Medium | High |
| TokenBudget | ~1200 | ~1000 | ~1800 |
| Time | 19 min | 17 min | 23 min |
| Iterations | 2 | 1 | 2 |
| Complexity | Low | Low | Medium-High |
| Research source | Community + docs | Library docs | Official platform docs |

**Universal success patterns:**
- Clear domain identification
- Accurate keyword selection
- Following existing domain patterns
- Good anti-pattern examples with code
- Thorough validation loop

