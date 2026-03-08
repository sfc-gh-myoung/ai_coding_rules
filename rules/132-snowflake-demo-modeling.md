# Snowflake Demo: Data Modeling and Generation

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**Keywords:** Data modeling, naming conventions, Kimball, dimensional modeling, fact tables, dimension tables, foreign keys, view taxonomy, data generation, backward compatibility, surrogate keys
**TokenBudget:** ~3300
**ContextTier:** High
**LoadTrigger:** kw:data-modeling, kw:dimensional-model, kw:kimball
**Depends:** 130-snowflake-demo-sql.md, 131-snowflake-demo-creation.md

## Scope

**What This Rule Covers:**
Comprehensive data generation and modeling standards for Business Analysts, Executive Users, Data Scientists, and Data Engineers. Covers naming conventions, Kimball dimensional modeling, view taxonomy, and backward compatibility strategies.

**When to Load This Rule:**
- Designing data models for analytics or demos
- Creating Python data generators
- Writing SQL DDL for fact and dimension tables
- Building view hierarchies (BASE, INTERMEDIATE, ANALYTICS)
- Implementing backward-compatible schema changes

## References

### Dependencies

**Must Load First:**
- **130-snowflake-demo-sql.md** - Demo SQL patterns
- **131-snowflake-demo-creation.md** - Demo creation and synthetic data

**Related:**
- **930-data-governance-quality.md** - Data governance and quality patterns
- **940-business-analytics.md** - Business analytics patterns
- **100-snowflake-core.md** - Snowflake SQL patterns

### External Documentation

- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [Snowflake Data Modeling](https://docs.snowflake.com/en/user-guide/data-modeling)

## Contract

### Inputs and Prerequisites

- Data entity requirements and relationship diagrams
- Target analytical use cases defined
- Understanding of Kimball dimensional modeling
- Snowflake SQL DDL knowledge

### Mandatory

- Python generators for synthetic data with referential integrity
- SQL DDL with explicit primary keys and foreign keys
- View creation with taxonomy prefixes (VW_BA_, VW_EXEC_, VW_DS_)
- Column and view COMMENT documentation
- Temporal columns (created_at, updated_at)

### Forbidden

- Ad-hoc naming without documented rationale
- Breaking changes without backward compatibility strategy
- Primary keys that don't follow `<entity>_id` pattern
- Foreign keys that don't match referenced primary key names
- Views without PURPOSE comments

### Execution Steps

1. Define entity model with standardized primary keys (`<entity>_id` pattern)
2. Apply universal naming conventions (Business Analyst-friendly)
3. Implement dimensional modeling patterns (Kimball methodology)
4. Create business-friendly view taxonomy (VW_BA_, VW_EXEC_, VW_DS_)
5. Document all relationships and metadata with COMMENT
6. Enforce referential integrity with foreign key constraints
7. Validate with compliance checklist
8. Test Business Analyst queries against views

### Output Format

- Python DataFrames with standardized columns (`<entity>_id`, temporal columns)
- SQL DDL with explicit PKs/FKs and COMMENT documentation
- View definitions with clear taxonomy prefixes and PURPOSE comments

### Validation

**Success Criteria:**
- All primary keys follow `<entity>_id` pattern
- Foreign key names exactly match referenced primary key names
- All columns have clear COMMENT documentation
- All views have PURPOSE comments
- Business Analyst queries execute successfully against views
- FK integrity validation passes
- View taxonomy compliance verified

### Design Principles

- **Business-First Naming:** Column and table names immediately understandable to non-technical business analysts
- **Consistent Identity:** Every entity uses `<entity>_id` as primary key; external identifiers use `<entity>_number`
- **FK Matching:** Foreign key names MUST exactly match referenced primary key names
- **Dimensional Modeling:** Separate facts (measures) from dimensions (attributes)
- **View Layering:** Progressive abstraction from raw tables to analytical views
- **Self-Documenting:** Every column has clear COMMENT; every view has PURPOSE comment
- **Backward Compatible:** All schema changes provide migration path via views

### Post-Execution Checklist

- [ ] Entity IDs use `<entity>_id` suffix
- [ ] FKs exactly match referenced PK names
- [ ] Display names use `<entity>_name`
- [ ] Temporal columns use `<event>_timestamp` or `<event>_date`
- [ ] Boolean columns use `is_`, `has_`, `can_`, `should_`
- [ ] Measurements include unit in column name
- [ ] Views use taxonomy prefixes (VW_BA_, VW_EXEC_, VW_DS_)
- [ ] All columns have COMMENT
- [ ] Date dimension exists and is used
- [ ] Backward compatibility views created for renames
- [ ] FK integrity validated in generator

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Inconsistent FK Naming

```sql
-- BAD: FK name doesn't match PK
CREATE TABLE TRANSFORMER_DATA (equipment_id VARCHAR(50));  -- References asset_id
```

**Problem:** Business Analysts must memorize that `equipment_id` = `asset_id`. Creates cognitive load and query errors.

**Correct Pattern:**
```sql
CREATE TABLE FACT_TRANSFORMER_READINGS (asset_id VARCHAR(50));  -- Matches DIM_GRID_ASSET.asset_id
```

### Anti-Pattern 2: Ambiguous View Names

```sql
-- BAD: Generic, unclear purpose
CREATE VIEW ENRICHED_ASSET_FEATURES AS ...;
```

**Problem:** Users don't know if view is for Business Analysts, Data Scientists, or Engineers.

**Correct Pattern:**
```sql
CREATE VIEW VW_DS_ASSET_FEATURES AS ...
COMMENT = 'DS View: ML-ready feature table for transformer failure prediction';
```

### Anti-Pattern 3: Unitless Measurements

```sql
-- BAD: Units unclear
CREATE TABLE AMI_DATA (consumption FLOAT, temperature FLOAT, voltage FLOAT);
```

**Problem:** Analysts must guess units or reference external documentation.

**Correct Pattern:**
```sql
CREATE TABLE FACT_METER_READINGS (
    consumption_kwh FLOAT COMMENT 'Energy consumption in kilowatt-hours',
    ambient_temp_c FLOAT COMMENT 'Ambient temperature in Celsius'
);
```

### Anti-Pattern 4: Missing Date Dimension

```sql
-- BAD: Direct date filtering with functions
SELECT YEAR(read_timestamp), SUM(consumption_kwh) FROM AMI_DATA;
```

**Problem:** Expensive date functions; no fiscal year/holiday logic; not BA-friendly.

**Correct Pattern:**
```sql
SELECT d.year_num, d.fiscal_quarter, SUM(f.consumption_kwh)
FROM FACT_METER_READINGS f JOIN DIM_DATE d ON DATE(f.read_timestamp) = d.date_key;
```

## Universal Naming Conventions

### Entity Identifier Standards

**Mandatory Patterns:**
- **Primary Keys**: Always `<entity>_id` (e.g., `asset_id`, `meter_id`, `customer_id`)
- **Foreign Keys**: Must exactly match referenced PK name
- **Display Names**: Use `<entity>_name` for human-readable labels
- **External IDs**: Use `<entity>_number` for customer-facing identifiers

### Temporal Column Standards

- **Exact timestamp:** `<event>_timestamp` (TIMESTAMP_NTZ)
- **Date only:** `<event>_date` (DATE)
- **Duration:** `<event>_duration_<unit>` (NUMBER)

### Boolean Column Standards

All boolean columns must use: `is_`, `has_`, `can_`, `should_` prefixes.

### Measurement Column Standards

All measurements include unit: `<metric>_kwh`, `<metric>_kw`, `<metric>_volts`, `<metric>_temp_c`

## Dimensional Modeling Standards (Kimball)

### Fact Table Patterns

**Naming:** `FACT_<business_process>` (e.g., `FACT_METER_READINGS`, `FACT_BILLING`)

**Required Columns:**
1. Composite Primary Key (time + entity FK)
2. Measures (numeric facts)
3. Dimension FKs (matching dimension PKs)
4. Metadata (`load_timestamp`, `source_system`)

```sql
CREATE TABLE FACT_METER_READINGS (
    meter_id VARCHAR(50) NOT NULL,
    read_timestamp TIMESTAMP_NTZ NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    consumption_kwh FLOAT NOT NULL,
    demand_kw FLOAT NOT NULL,
    PRIMARY KEY (meter_id, read_timestamp)
);
```

### Dimension Table Patterns

**Naming:** `DIM_<entity>` (e.g., `DIM_GRID_ASSET`, `DIM_CUSTOMER`, `DIM_DATE`)

**Required Columns:**
1. Primary Key (`<entity>_id`)
2. Business Key (`<entity>_name` or `<entity>_number`)
3. Attributes (descriptive text, categories)
4. Metadata (`created_timestamp`, `updated_timestamp`)

```sql
CREATE TABLE DIM_GRID_ASSET (
    asset_id VARCHAR(50) NOT NULL PRIMARY KEY,
    asset_name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    manufacturer VARCHAR(100),
    install_date DATE,
    operational_status VARCHAR(20),
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Dimension: Grid asset inventory';
```

### Bridge Table Patterns (Many-to-Many)

**Naming:** `BRIDGE_<entity1>_<entity2>`

```sql
CREATE TABLE BRIDGE_METER_CONTRACT (
    meter_id VARCHAR(50) NOT NULL,
    contract_id VARCHAR(50) NOT NULL,
    effective_start_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (meter_id, contract_id, effective_start_date)
);
```

### Date Dimension (Mandatory)

Every dimensional model MUST include a date dimension with calendar attributes, business attributes (is_holiday, fiscal_year), and utility-specific fields.

## View Taxonomy (Business-First Design)

### View Prefix Standards

- **`VW_BA_*`** - Business Analyst views (pre-joined, low complexity)
- **`VW_EXEC_*`** - Executive dashboard views (aggregated KPIs)
- **`VW_DS_*`** - Data Science feature views (wide format, ML-ready)
- **`VW_DE_*`** - Data Engineering pipeline views (ETL/lineage)
- **`VW_REF_*`** - Reference lookup views (static lists)
- **`VW_OPS_*`** - Operational monitoring (real-time status)

### Business Analyst Views (`VW_BA_*`)

**Design Principles:**
- Pre-join all relevant dimensions
- Use business-friendly column aliases
- Include commonly filtered dimensions
- Add inline documentation via column comments

```sql
CREATE VIEW VW_BA_METER_READINGS AS
SELECT f.read_timestamp, d.asset_name, c.customer_name,
       f.consumption_kwh, f.demand_kw, dt.fiscal_quarter
FROM FACT_METER_READINGS f
JOIN DIM_GRID_ASSET d ON f.asset_id = d.asset_id
JOIN DIM_CUSTOMER c ON f.customer_id = c.customer_id
JOIN DIM_DATE dt ON DATE(f.read_timestamp) = dt.date_key
COMMENT = 'BA View: Pre-joined meter readings with asset and customer dimensions';
```

### Executive Dashboard Views (`VW_EXEC_*`)

**Design Principles:**
- Highly aggregated (monthly, quarterly grains)
- Include trend calculations (YoY, MoM)
- Pre-calculate KPIs and ratios
- Focus on business outcomes

```sql
CREATE VIEW VW_EXEC_ENERGY_KPI AS
SELECT dt.fiscal_quarter, dt.year_num,
       SUM(f.consumption_kwh) AS total_consumption_kwh,
       COUNT(DISTINCT f.meter_id) AS active_meters,
       ROUND(SUM(f.consumption_kwh) / COUNT(DISTINCT f.meter_id), 2) AS avg_consumption_per_meter
FROM FACT_METER_READINGS f
JOIN DIM_DATE dt ON DATE(f.read_timestamp) = dt.date_key
GROUP BY dt.fiscal_quarter, dt.year_num
COMMENT = 'EXEC View: Quarterly energy KPIs with per-meter averages';
```

### Data Science Feature Views (`VW_DS_*`)

**Design Principles:**
- Wide format (one row per entity)
- Include engineered features (lags, rolling aggregates)
- Handle nulls explicitly
- Include target variable columns for ML

```sql
CREATE VIEW VW_DS_ASSET_FEATURES AS
SELECT d.asset_id, d.asset_type, d.operational_status,
       COALESCE(agg.avg_consumption_kwh, 0) AS avg_consumption_kwh,
       COALESCE(agg.max_demand_kw, 0) AS max_demand_kw,
       COALESCE(agg.reading_count, 0) AS reading_count,
       DATEDIFF('day', d.install_date, CURRENT_DATE()) AS asset_age_days
FROM DIM_GRID_ASSET d
LEFT JOIN (
  SELECT asset_id, AVG(consumption_kwh) AS avg_consumption_kwh,
         MAX(demand_kw) AS max_demand_kw, COUNT(*) AS reading_count
  FROM FACT_METER_READINGS GROUP BY asset_id
) agg ON d.asset_id = agg.asset_id
COMMENT = 'DS View: ML-ready asset features for predictive maintenance';
```

## Backward Compatibility and Migration

### Migration Principles

1. **Create new objects with standard names** (e.g., `DIM_GRID_ASSET`)
2. **Create compatibility views with old names** (e.g., `GRID_ASSETS` pointing to new)
3. **Deprecation notice period** (minimum 30 days)
4. **Remove old objects** only after all consumers migrated

```sql
-- Backward compatibility view
CREATE VIEW GRID_ASSETS AS
SELECT asset_id, asset_name, asset_type,
       asset_id AS equipment_id  -- Compatibility alias
FROM DIM_GRID_ASSET
COMMENT = 'DEPRECATED: Use DIM_GRID_ASSET instead. Removing 2026-07-01.';
```

## Data Generator Requirements

### Generator Output Standards

All Python generators must produce:
1. Standardized column names (Section 1 conventions)
2. Metadata columns (`created_timestamp`, `source_system`)
3. Explicit data types
4. Referential integrity (all FKs reference valid PKs)

### Required Columns for All Entities

```python
required_columns = {
    '<entity>_id': 'VARCHAR(50)',
    '<entity>_name': 'VARCHAR(100)',
    'created_timestamp': 'TIMESTAMP_NTZ',
    'source_system': 'VARCHAR(50)',
}
```

### Relationship Integrity Validation

```python
def validate_foreign_keys(df_child, df_parent, fk_column, pk_column):
    missing_refs = df_child[~df_child[fk_column].isin(df_parent[pk_column])]
    if not missing_refs.empty:
        raise ValueError(f"Referential integrity violation: {len(missing_refs)} rows")
```

## SQL DDL Standards

### Column Comment Standards

Every column must have COMMENT including:
1. What it represents (business definition)
2. Unit of measure (if numeric)
3. Valid values (if categorical)
4. FK reference (if foreign key)

```sql
consumption_kwh FLOAT COMMENT 'Total energy in kilowatt-hours',
operational_status VARCHAR(20) COMMENT 'Values: ACTIVE, FAILED, MAINTENANCE',
parent_asset_id VARCHAR(50) COMMENT 'References DIM_GRID_ASSET.asset_id'
```
