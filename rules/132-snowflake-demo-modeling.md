---
schema_version: v4.0
rule_version: v4.2.0
description: "Naming conventions, Kimball dimensional modeling, view taxonomy, and data generator standards for Snowflake demo environments. Covers fact/dimension table structure with declared grains, date dimension join patterns, SCD strategy, and backward-compatibility rules."
last_updated: 2026-10-08
keywords:
  - kw:Kimball dimensional modeling
  - kw:fact dimension FK naming
  - kw:view taxonomy prefixes
  - kw:synthetic data referential integrity
  - kw:business-first column naming
  - kw:scd type 2 surrogate
token_budget: ~2200
context_tier: High
depends:
  required:
    - 130-snowflake-demo-sql.md  # Demo SQL patterns
    - 131-snowflake-demo-creation.md  # Demo creation and synthetic data
  optional:
    - 930-data-governance-quality.md  # Data governance and quality patterns
    - 940-business-analytics.md  # Business analytics patterns
---
# Snowflake Demo: Data Modeling and Generation

## Scope

**What This Rule Covers:**
Naming conventions, Kimball dimensional modeling patterns, view taxonomy, and data generator standards for Snowflake demo environments. Covers fact/dimension table structure with declared grains, date dimension join patterns, SCD strategy, view taxonomy prefixes, column documentation, and backward-compatibility rules.

**When to Load This Rule:**
Load this rule when designing data models for analytics demos, writing SQL DDL for fact and dimension tables, building view hierarchies, or implementing backward-compatible schema changes.

## Contract

### Inputs and Prerequisites

- Entity relationships and analytical use cases defined before writing DDL
- `DIM_DATE` table created before fact tables that join to it
- Grain of each fact table declared before designing its columns

### Mandatory

**Naming conventions:**
- Primary keys: `<entity>_id` (e.g., `asset_id`, `customer_id`)
- Foreign keys: must exactly match the referenced primary key name
- Display names: `<entity>_name`; external/customer-facing IDs: `<entity>_number`
- Timestamps: `<event>_timestamp TIMESTAMP_NTZ`; dates: `<event>_date DATE`
- Booleans: prefix `is_`, `has_`, `can_`, or `should_`
- Measurements: include unit in column name (`consumption_kwh`, `ambient_temp_c`)

**Declared grain:** State the fact grain in its table `COMMENT`. Use a supplied unique transaction key for transaction grain, or a composite time/entity key when that identifies the declared grain. Include numeric measures, dimension FKs matching referenced PK names, and metadata (`load_timestamp`, `source_system`). Verify uniqueness in data; a declaration is not proof of enforcement.

**Date dimension and joins:** Use `DIM_DATE` when the demo needs calendar attributes; give it one row per unique `date_key DATE`, a derived `month_start DATE`, and the attributes actually needed. Populate it across every fact date before relying on inner-joined views, and check for uncovered fact dates; creating an empty dimension is insufficient. Join each fact timestamp to exactly one daily row with `DATE(f.<timestamp_col>) = d.date_key`, then group by `d.month_start` for monthly views. The expected number of month rows comes from distinct months in actual fact timestamps, never an inferred history window. Never join an unaggregated fact directly on `d.month_start`: a daily dimension has multiple rows per month and multiplies fact amounts. If a separate month dimension is used instead, verify one unique row per month key. Do not substitute day-count approximations for calendar joins.

**View taxonomy:** All views must carry a taxonomy prefix. The `COMMENT = '...'` clause must appear before the `AS` keyword in the DDL:
- `VW_BA_*` — pre-joined dimensions, business-friendly column aliases
- `VW_EXEC_*` — aggregated KPIs, monthly or quarterly grain
- `VW_DS_*` — wide format, null-handled, ML-ready features
- `VW_DE_*` — ETL pipeline and lineage views
- `VW_REF_*` — static reference lookups
- `VW_OPS_*` — real-time operational status

**Validation phases:** Before views, check all persisted keys, including `DIM_DATE.date_key` uniqueness (the PK declaration alone is insufficient), non-null fact dates, FK/date coverage, counts and base-table column comments. After views exist, check view comments, one-order BA grain, distinct-month EXEC grain and monthly totals. No pre-view gate may query or inspect a not-yet-created view. Name the monthly measure (for example `total_revenue_usd`) and reuse that exact alias when reconciling to the fact measure.

**Design handoff:** Include every supplied entity key, type, unit, count, seed and reference clock; inspected Python version, lint/format/type-check tools and unknown manager; creation and explicit load order; each parent/fact/date key's uniqueness; orphan coverage; separate post-view grain/totals checks; and truthful execution status. Do not omit toolchain findings from a design merely because no code is written. A nonunique parent key can multiply rows just like a nonunique date key.

**Evidence boundary:** Separate supplied workload facts from proposed design choices and unresolved inputs. Example category sets, identifier storage types and date windows are not fixture facts. Never label values copied from rule examples as supplied or verified. A clock without a sampling interval leaves timestamp-generation requirements unresolved; list that missing input before the generation workflow.

**Column comments:** Every column requires a `COMMENT` with: business definition, unit of measure (if numeric), valid values (if categorical), and FK target (if foreign key).

**SCD strategy:** Use Type 1 (overwrite) for demo attributes that do not need history. Use Type 2 (surrogate key + `effective_from`/`effective_to`/`is_current`) only when the demo scenario showcases historical analysis. Do not default to SCD2 without a narrative reason.

**Backward compatibility:** When renaming a table or schema, create a compatibility view with the old name pointing to the new object. Set a concrete removal event in the `COMMENT` tied to a known migration milestone (e.g., `'DEPRECATED: use DIM_GRID_ASSET. Remove after workshop-2026-12 consumers migrated.'`). Do not state a generic time window as a deprecation period — the window is determined by the actual consumer migration timeline.

**Reverse dependency order:** A separately authorized teardown removes dependent views first, then facts, then parent/date dimensions. Do not list views last in deferred prose or executable steps. If any dependent is unowned or unverified, stop and obtain a scoped dependency disposition; ownership of a table does not authorize deleting its consumers.

```sql
-- Grain: one row per meter reading per 15-minute interval
CREATE TABLE IF NOT EXISTS DEMO_DB.GRID_DATA.FACT_METER_READINGS (
    asset_id        VARCHAR(50)    NOT NULL  COMMENT 'FK -> DIM_GRID_ASSET.asset_id',
    read_timestamp  TIMESTAMP_NTZ  NOT NULL  COMMENT 'UTC timestamp of the reading',
    customer_id     VARCHAR(50)    NOT NULL  COMMENT 'FK -> DIM_CUSTOMER.customer_id',
    consumption_kwh FLOAT          NOT NULL  COMMENT 'Energy consumed in kilowatt-hours',
    demand_kw       FLOAT          NOT NULL  COMMENT 'Peak demand in kilowatts',
    load_timestamp  TIMESTAMP_NTZ  NOT NULL  DEFAULT CURRENT_TIMESTAMP() COMMENT 'Load time',
    source_system   VARCHAR(50)    NOT NULL COMMENT 'Origin system',
    PRIMARY KEY (asset_id, read_timestamp)
) COMMENT = 'Grain: one row per meter reading per 15-minute interval';
```

```sql
-- VW_BA_: pre-joined for analyst self-service; COMMENT placed before AS
CREATE VIEW DEMO_DB.GRID_DATA.VW_BA_METER_READINGS
COMMENT = 'BA View: Meter readings with asset, customer, and date dimensions pre-joined'
AS
SELECT
    f.read_timestamp,
    a.asset_name,
    c.customer_name,
    f.consumption_kwh,
    f.demand_kw,
    d.fiscal_quarter
FROM DEMO_DB.GRID_DATA.FACT_METER_READINGS  f
JOIN DEMO_DB.GRID_DATA.DIM_GRID_ASSET       a  ON f.asset_id    = a.asset_id
JOIN DEMO_DB.GRID_DATA.DIM_CUSTOMER         c  ON f.customer_id = c.customer_id
JOIN DEMO_DB.GRID_DATA.DIM_DATE             d  ON DATE(f.read_timestamp) = d.date_key;
```

### Execution Steps

Use the following ordered workflow in the final execution plan. For design-only work, describe every action as proposed and mark missing inputs; never execute it.

1. Establish authorization, target state, supplied entity keys/grain/units and Python toolchain. Resolve missing date-window inputs before implementing timestamp generation.
2. Generate parent and fact rows in memory with the supplied seed/reference clock. Derive one unique date-dimension row per covered calendar date from those generated timestamps; validate the generated keys and parent references.
3. Create base tables in dependency order, using entity-key naming, declared grain, metadata and column comments. Do not replace existing objects without separate approval.
4. **Load parent dimensions**, using only authorized targets.
5. **Load `DIM_DATE` rows** generated in step 2. This must be its own execution-plan action, not merely an inventory note.
6. **Load fact rows.** Only after all three table types exist and are loaded, verify persisted counts, each parent/fact/date key's uniqueness, non-null timestamps, FK/date coverage and base-table comments. Never run a full fact-referencing gate between dimension load and fact creation/load. Stop on any failed check. This gate does not include views.
7. Create required taxonomy-prefixed views with `COMMENT` before `AS`, after checking existing names, grants and dependents. Use a unique daily date join before grouping by month. For renamed objects, use approved compatibility views with a concrete removal event.
8. After views exist, verify their comments, representative queries, BA/EXEC grain and monthly reconciliation using the declared output alias. Derive distinct fact months from `DATE_TRUNC('month', f.<timestamp_col>)`, not a `month_start` column absent from the fact definition. Check every verification expression against the columns actually defined above and remove contradictory claims (view `COMMENT` placement applies even when no COPY operation exists). Report actual results; unexecuted checks remain unverified.

### Validation

- All PKs follow `<entity>_id`; all FKs exactly match their referenced PK name
- Every fact table has grain declared in its table-level `COMMENT`
- `DIM_DATE.date_key` is type `DATE` and populated for all fact dates; an orphan/coverage check returns zero before joining dependent views
- Daily fact-to-date joins preserve one dimension row per fact; group by month only after that join and reconcile monthly totals to the fact total
- All views carry a taxonomy prefix and `COMMENT` placed before the `AS` keyword
- Every column has a `COMMENT`; validate with `INFORMATION_SCHEMA.COLUMNS WHERE comment IS NULL OR comment = ''`
- Backward-compatibility views reference a concrete removal event, not a generic time window
- Representative `VW_BA_*` queries execute correctly against fact and dimension joins

## References

- [Snowflake Data Modeling](https://docs.snowflake.com/en/user-guide/data-modeling)
- [Kimball Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
