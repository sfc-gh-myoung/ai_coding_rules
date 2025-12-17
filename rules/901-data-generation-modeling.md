# Data Generation & Modeling Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Data modeling, naming conventions, Kimball, dimensional modeling, fact tables, dimension tables, foreign keys, view taxonomy, Business Analyst, data generation, backward compatibility, entity IDs, temporal columns, surrogate keys, SCD Type 2
**TokenBudget:** ~5400
**ContextTier:** High
**Depends:** rules/000-global-core.md, rules/100-snowflake-core.md, rules/102-snowflake-sql-demo-engineering.md, rules/930-data-governance-quality.md, rules/940-business-analytics.md

## Purpose
Establish comprehensive data generation and modeling standards ensuring intuitive, analytics-friendly data for Business Analysts, Executive Users, Data Scientists, and Data Engineers through consistent naming conventions, relationship patterns, and dimensional modeling best practices.

## Rule Scope

All data generation (Python generators), SQL schema design (DDL), view creation, and analytics queries for utility demo project. Applies to grid data, customer data, and all future data domains.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Kimball dimensional modeling** - Fact tables + dimension tables
- **Standardized primary keys** - <entity>_id (e.g., customer_id)
- **BA-first naming** - Business Analyst-friendly, not technical jargon
- **View taxonomy** - BASE, then INTERMEDIATE, then ANALYTICS hierarchy
- **Referential integrity** - Enforce FK relationships
- **Temporal columns** - created_at, updated_at timestamps
- **Never break backward compatibility** - Add columns, don't rename

**Quick Checklist:**
- [ ] Fact/dimension tables defined
- [ ] Primary keys standardized
- [ ] Column names BA-friendly
- [ ] View hierarchy established
- [ ] FK relationships documented
- [ ] Temporal columns present
- [ ] Backward compatibility maintained

## Contract

<contract>
<inputs_prereqs>
Data entity requirements, relationship diagrams, target analytical use cases, audience priority (Business Analysts first)
</inputs_prereqs>

<mandatory>
Python generators, SQL DDL, view creation, Snowflake stages, data validation scripts
</mandatory>

<forbidden>
Ad-hoc naming without documented rationale; breaking changes without backward compatibility; undocumented FK relationships
</forbidden>

<steps>
1. Define entity model with standardized primary keys (see Section 1)
2. Apply universal naming conventions (see Section 2)
3. Implement dimensional modeling patterns (see Section 3)
4. Create business-friendly view taxonomy (see Section 4)
5. Document all relationships and metadata
6. Validate with compliance checklist (see Section 9)
</steps>

<output_format>
Python DataFrames with standardized columns; SQL DDL with explicit PKs/FKs; View definitions with clear taxonomy prefixes
</output_format>

<validation>
Run validation script; verify FK integrity; test business analyst queries; check view taxonomy compliance
</validation>

<design_principles>
- **Business-First Naming**: Column and table names must be immediately understandable to non-technical business analysts
- **Consistent Identity**: Every entity uses `<entity>_id` as primary key; external identifiers use `<entity>_number`
- **FK Matching**: Foreign key names MUST exactly match referenced primary key names
- **Dimensional Modeling**: Separate facts (measures) from dimensions (attributes) using Kimball patterns
- **View Layering**: Progressive abstraction from raw tables to analytical views to business KPI views
- **Self-Documenting**: Every column has a clear COMMENT; every view has a PURPOSE comment
- **Backward Compatible**: All schema changes must provide migration path via views
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Inconsistent FK Naming

```sql
-- BAD: FK name doesn't match PK
CREATE TABLE TRANSFORMER_DATA (
    equipment_id VARCHAR(50),  -- ← References GRID_ASSETS.asset_id
    timestamp TIMESTAMP_NTZ,
    oil_temp_c FLOAT
);

SELECT *
FROM GRID_ASSETS a
JOIN TRANSFORMER_DATA t ON a.asset_id = t.equipment_id;  -- Confusing!
```

**Problem:** Business Analysts must memorize that `equipment_id` = `asset_id`

**Correct Pattern:**
```sql
-- GOOD: FK exactly matches PK
CREATE TABLE FACT_TRANSFORMER_READINGS (
    asset_id VARCHAR(50),  -- ← Matches GRID_ASSETS.asset_id exactly
    read_timestamp TIMESTAMP_NTZ,
    oil_temp_c FLOAT
);

SELECT *
FROM DIM_GRID_ASSET a
JOIN FACT_TRANSFORMER_READINGS t ON a.asset_id = t.asset_id;  -- Intuitive!
```

**Benefits:** Self-documenting queries; reduced cognitive load


### Anti-Pattern 2: Ambiguous View Names

```sql
-- BAD: Generic, unclear purpose
CREATE OR REPLACE VIEW ENRICHED_ASSET_FEATURES AS ...;
```

**Problem:** Who is this for? What's "enriched"? Business Analyst or Data Scientist?

**Correct Pattern:**
```sql
-- GOOD: Clear taxonomy and purpose
CREATE OR REPLACE VIEW VW_DS_ASSET_FEATURES AS ...
COMMENT = 'DS View: ML-ready feature table for transformer failure prediction';

CREATE OR REPLACE VIEW VW_BA_ASSET_SUMMARY AS ...
COMMENT = 'BA View: Simplified asset inventory for business reporting';
```

**Benefits:** Users immediately know which view to use; self-documenting


### Anti-Pattern 3: Unitless Measurements

```sql
-- BAD: Units unclear
CREATE TABLE AMI_DATA (
    consumption FLOAT,   -- Is this kWh? MWh? kW?
    temperature FLOAT,   -- Celsius? Fahrenheit?
    voltage FLOAT        -- Volts? kV?
);
```

**Problem:** Analysts must guess units or reference documentation

**Correct Pattern:**
```sql
-- GOOD: Units explicit in column name
CREATE TABLE FACT_METER_READINGS (
    consumption_kwh FLOAT COMMENT 'Energy consumption in kilowatt-hours',
    ambient_temp_c FLOAT COMMENT 'Ambient temperature in Celsius',
    voltage_volts FLOAT COMMENT 'Line voltage in volts'
);
```

**Benefits:** Self-documenting; prevents unit conversion errors


### Anti-Pattern 4: Mixing Temporal Suffixes

```sql
-- BAD: Inconsistent temporal naming
CREATE TABLE CALLS (
    timestamp TIMESTAMP_NTZ,        -- Generic
    call_time TIMESTAMP_NTZ,         -- Ambiguous
    start_date DATE                  -- Missing entity prefix
);
```

**Problem:** Inconsistent pattern; unclear which time this represents

**Correct Pattern:**
```sql
-- GOOD: Consistent <event>_timestamp pattern
CREATE TABLE FACT_CUSTOMER_CALLS (
    call_timestamp TIMESTAMP_NTZ COMMENT 'Exact time call started',
    call_end_timestamp TIMESTAMP_NTZ COMMENT 'Exact time call ended',
    billing_date DATE COMMENT 'Date for billing allocation'
);
```

**Benefits:** Pattern is learnable; clear semantics


### Anti-Pattern 5: Missing Date Dimension

```sql
-- BAD: Direct date filtering in fact table
SELECT
    YEAR(read_timestamp) AS year,
    MONTH(read_timestamp) AS month,
    SUM(consumption_kwh)
FROM AMI_DATA
WHERE YEAR(read_timestamp) = 2024
GROUP BY YEAR(read_timestamp), MONTH(read_timestamp);
```

**Problem:** Expensive date functions; no fiscal year/holiday logic; not BA-friendly

**Correct Pattern:**
```sql
-- GOOD: Join to date dimension
SELECT
    d.year_num,
    d.month_name,
    d.fiscal_quarter,
    SUM(f.consumption_kwh) AS total_consumption_kwh
FROM FACT_METER_READINGS f
JOIN DIM_DATE d ON DATE(f.read_timestamp) = d.date_key
WHERE d.year_num = 2024
GROUP BY d.year_num, d.month_name, d.fiscal_quarter;
```

**Benefits:** Better performance; rich time attributes; business calendar support


## Post-Execution Checklist

**MANDATORY:**

Before committing any data generation or SQL changes, verify:

- [ ] **Entity IDs**: All primary keys use `<entity>_id` suffix
- [ ] **FK Matching**: All foreign keys exactly match referenced primary key names
- [ ] **Display Names**: All entities have `<entity>_name` for human-readable labels
- [ ] **Temporal Consistency**: All temporal columns use `<event>_timestamp` or `<event>_date` pattern
- [ ] **Boolean Prefixes**: All flags use `is_`, `has_`, `can_`, `should_` prefixes
- [ ] **Measurement Units**: All numeric measurements include unit in column name
- [ ] **View Taxonomy**: All views use `VW_BA_*`, `VW_EXEC_*`, `VW_DS_*`, etc. prefixes
- [ ] **Column Comments**: Every column has a descriptive COMMENT
- [ ] **Date Dimension**: Date dimension exists and is used in time-based queries
- [ ] **Backward Compatibility**: Compatibility views created for any renamed objects
- [ ] **Referential Integrity**: All FK values exist in parent tables (validated in generator)
- [ ] **Documentation**: Changes documented in README, ARCHITECTURE.md, CHANGELOG.md


## Validation

- **Success Checks:** All entity IDs follow `<entity>_id` pattern; FKs match PKs exactly; views follow taxonomy; column comments present; date dimension exists; business analyst queries require <10 lines of SQL
- **Negative Tests:** Queries with mismatched FKs fail; undocumented columns caught in review; views without taxonomy prefix rejected; unitless measurements flagged

> **Investigation Required**
> When applying this rule:
> 1. Read all generator files to understand current naming patterns BEFORE proposing changes
> 2. Read SQL DDL files to verify FK relationships BEFORE modifying schemas
> 3. Never speculate about column meanings - read the actual code/DDL
> 4. Test queries against actual views before claiming they work
> 5. Validate FK integrity by reading both parent and child DataFrames

## Output Format Examples

```markdown
Implementation: Summary

**Rule Applied:** [rule filename]
**Domain:** [technology/framework]
**Changes:** [high-level summary]

### Investigation Results
- Current state: [what was found]
- Requirements: [what needs to change]
- Constraints: [limitations identified]

### Implementation Steps
1. **[Step 1]**: [Specific action taken]
   - File: `path/to/file`
   - Change: [delta description]

2. **[Step 2]**: [Another action]
   - Configuration: [what was configured]
   - Rationale: [why this approach]

3. **[Step 3]**: [Validation action]
   - Test: [specific test run]
   - Result: [outcome]

### Validation Results
```bash
# Commands run to validate
command --validate
test --run-all
```

**Output:**
```
[Test output showing success]
```

### Next Steps
- [Optional follow-up items]
- [Monitoring recommendations]
```

## References

### External Documentation
- [Kimball Dimensional Modeling](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) - Ralph Kimball's dimensional modeling methodology
- [Snowflake Data Modeling Best Practices](https://docs.snowflake.com/en/user-guide/data-modeling) - Official Snowflake guidance
- [Snowflake View Best Practices](https://docs.snowflake.com/en/user-guide/views-introduction) - View creation and optimization
- [Smart Grid Interoperability Standards (NIST)](https://www.nist.gov/programs-projects/smart-grid) - Utility industry data standards
- [IEC 61970 (CIM)](https://en.wikipedia.org/wiki/Common_Information_Model_(electricity)) - Common Information Model for grid assets

### Related Rules
- **Global Core**: `rules/000-global-core.md`
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Data Governance**: `rules/930-data-governance-quality.md`
- **Business Analytics**: `rules/940-business-analytics.md`
- **Demo Creation**: `rules/900-demo-creation.md`

## 1. Universal Naming Conventions

### 1.1 Entity Identifier Standards

**MANDATORY Entity Key Patterns:**
- **Grid Assets:** PK: `asset_id`, FK: `asset_id`, Display: `asset_name` (e.g., `'XFMR-A1-001-015'`)
- **Meters:** PK: `meter_id`, FK: `meter_id`, Display: `meter_number` (e.g., `'MTR-A1-001-001'`)
- **Transformers:** PK: `transformer_id`, FK: `transformer_id`, Display: `transformer_name`
- **Customers:** PK: `customer_id`, FK: `customer_id`, Display: `customer_name` (e.g., `'CUST-001234'`)
- **Substations:** PK: `substation_id`, FK: `substation_id`, Display: `substation_name`
- **Contracts:** PK: `contract_id`, FK: `contract_id`, Display: `contract_number` (e.g., `'CA-123456'`)

**Universal Rules:**
- **Primary Keys**: Always use `<entity>_id` suffix
- **Foreign Keys**: Must exactly match the referenced primary key name (no renaming!)
- **Display Names**: Use `<entity>_name` for human-readable labels
- **External IDs**: Use `<entity>_number` for customer-facing or legacy system identifiers
- **Avoid**: `equipment_id`, `device_id`, or other non-standard synonyms unless explicitly documented

### 1.2 Temporal Column Standards

**MANDATORY Temporal Column Patterns:**
- **Exact timestamp:** `<event>_timestamp` (TIMESTAMP_NTZ) - e.g., `call_timestamp`, `reading_timestamp`
- **Date only:** `<event>_date` (DATE) - e.g., `billing_date`, `install_date`
- **Time only:** `<event>_time` (TIME) - e.g., `shift_start_time`
- **Duration:** `<event>_duration_<unit>` (NUMBER) - e.g., `call_duration_seconds`
- **Period start:** `period_start_date` (DATE) - e.g., `billing_period_start`
- **Period end:** `period_end_date` (DATE) - e.g., `billing_period_end`

**Anti-Patterns to Avoid:**
- Mixing `timestamp`, `_time`, `_date`, `_ts` without clear pattern
- Using `read_time` in one table and `timestamp` in another for the same concept
- Ambiguous names like `date` or `time` (always prefix with event/entity)

### 1.3 Boolean Column Standards

**MANDATORY:**

All boolean/flag columns must use one of these prefixes:

**Boolean Prefix Patterns:**
- **`is_`** - State or classification (e.g., `is_active`, `is_failing`, `is_critical`)
- **`has_`** - Possession or capability (e.g., `has_smart_meter`, `has_payment_plan`)
- **`can_`** - Permission or ability (e.g., `can_disconnect`, `can_remote_read`)
- **`should_`** - Recommendation flag (e.g., `should_inspect`, `should_replace`)

**Data Type:** Always use `BOOLEAN` in Snowflake (not `INTEGER` or `VARCHAR`)

### 1.4 Measurement Column Standards

**MANDATORY:**

All measurement columns must include unit of measure in the name:

**Measurement Column Patterns:**
- **Energy:** `<metric>_kwh`, `<metric>_mwh` (e.g., `consumption_kwh`, `generation_mwh`)
- **Power:** `<metric>_kw`, `<metric>_mw` (e.g., `demand_kw`, `capacity_mw`)
- **Voltage:** `<metric>_volts`, `<metric>_kv` (e.g., `voltage_volts`, `nominal_voltage_kv`)
- **Current:** `<metric>_amps` (e.g., `load_current_amps`)
- **Temperature:** `<metric>_temp_c`, `<metric>_temp_f` (e.g., `oil_temp_c`, `ambient_temp_c`)
- **Distance:** `<metric>_km`, `<metric>_miles` (e.g., `feeder_length_km`)
- **Currency:** `<metric>_amount` + `currency` column (e.g., `bill_amount` + `currency = 'USD'`)

**Anti-Patterns:**
- Unitless measurements: `temperature`, `voltage`, `power`
- Abbreviated units: `temp`, `volt`, `dist`

### 1.5 Categorical Column Standards

**RECOMMENDED:**

Categorical columns should use clear, self-documenting values:

**Categorical Value Patterns (UPPERCASE):**
- **Status:** e.g., `operational_status = 'ACTIVE'`, `'FAILED'`, `'MAINTENANCE'`
- **Type:** e.g., `asset_type = 'TRANSFORMER'`, `'METER'`, `'SUBSTATION'`
- **Class:** e.g., `billing_class = 'RESIDENTIAL'`, `'COMMERCIAL'`
- **Category:** e.g., `rate_category = 'STANDARD'`, `'TIME_OF_USE'`

**Abbreviations:** Only use if industry-standard (e.g., `RES`/`COMM` acceptable for utilities)


## 2. Dimensional Modeling Standards (Kimball Methodology)

### 2.1 Fact Table Patterns

**MANDATORY:**

**Fact tables store measurements and metrics (numeric, additive).**

**Naming:** `FACT_<business_process>` - Grain + Measures + Dimension FKs
- Examples: `FACT_METER_READINGS`, `FACT_BILLING`, `FACT_OUTAGES`

**Required Columns:**
1. **Composite Primary Key**: Time dimension + entity FK (e.g., `read_timestamp + meter_id`)
2. **Measures**: Numeric facts (e.g., `consumption_kwh`, `demand_kw`)
3. **Dimension FKs**: Exactly match dimension table PKs (e.g., `meter_id`, `customer_id`)
4. **Metadata**: `load_timestamp`, `source_system`

**Example Fact Table:**
```sql
CREATE TABLE FACT_METER_READINGS (
    -- Composite Primary Key (grain)
    meter_id VARCHAR(50) NOT NULL,
    read_timestamp TIMESTAMP_NTZ NOT NULL,

    -- Dimension Foreign Keys
    customer_id VARCHAR(50) NOT NULL,
    asset_id VARCHAR(50) NOT NULL,  -- References DIM_GRID_ASSET

    -- Measures (facts)
    consumption_kwh FLOAT NOT NULL,
    demand_kw FLOAT NOT NULL,
    voltage_volts FLOAT,
    power_factor FLOAT,

    -- Metadata
    load_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (meter_id, read_timestamp)
);
```

### 2.2 Dimension Table Patterns

**MANDATORY:**

**Dimension tables store descriptive attributes (text, categories).**

**Naming:** `DIM_<entity>` - Surrogate/Natural Key + Attributes
- Examples: `DIM_GRID_ASSET`, `DIM_CUSTOMER`, `DIM_DATE`

**Required Columns:**
1. **Primary Key**: `<entity>_id` (natural key preferred for this project)
2. **Business Key**: `<entity>_name` or `<entity>_number` (human-readable)
3. **Attributes**: Descriptive text, categories, classifications
4. **Hierarchy**: Parent FK for hierarchical dimensions (e.g., `parent_asset_id`)
5. **Metadata**: `created_timestamp`, `updated_timestamp`

**Example Dimension Table:**
```sql
CREATE TABLE DIM_GRID_ASSET (
    -- Primary Key (natural key)
    asset_id VARCHAR(50) NOT NULL PRIMARY KEY,

    -- Business Keys
    asset_name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,

    -- Hierarchy
    parent_asset_id VARCHAR(50),  -- Self-referencing FK

    -- Descriptive Attributes
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    install_date DATE,
    operational_status VARCHAR(20),
    criticality_level VARCHAR(10),

    -- Geographic
    latitude FLOAT,
    longitude FLOAT,
    city VARCHAR(100),

    -- Metadata
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    COMMENT = 'Dimension: Grid asset inventory with hierarchical relationships'
);
```

### 2.3 Bridge Table Patterns (Many-to-Many)

**MANDATORY:**

Use bridge tables for many-to-many relationships:

**Naming:** `BRIDGE_<entity1>_<entity2>` - PK1 + PK2 + Attributes
- Example: `BRIDGE_METER_CONTRACT`

```sql
CREATE TABLE BRIDGE_METER_CONTRACT (
    meter_id VARCHAR(50) NOT NULL,
    contract_id VARCHAR(50) NOT NULL,
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (meter_id, contract_id, effective_start_date)
);
```

### 2.4 Date Dimension (Mandatory)

**MANDATORY:**

**Every dimensional model MUST include a date dimension.**

```sql
CREATE TABLE DIM_DATE (
    date_key DATE NOT NULL PRIMARY KEY,

    -- Calendar Attributes
    date_timestamp TIMESTAMP_NTZ,
    day_of_week VARCHAR(10),
    day_of_week_num INT,
    day_of_month INT,
    day_of_year INT,

    week_of_year INT,
    month_num INT,
    month_name VARCHAR(10),
    month_abbr VARCHAR(3),
    quarter_num INT,
    year_num INT,

    -- Business Attributes
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100),
    fiscal_year INT,
    fiscal_quarter INT,

    -- Utility-Specific
    is_peak_season BOOLEAN,  -- Summer/Winter
    billing_cycle_day INT,   -- Day within 30-day billing cycle

    COMMENT = 'Dimension: Date attributes for time-based analytics'
);
```

**Usage in Fact Tables:**
```sql
-- Join pattern for business analysts
SELECT
    d.year_num,
    d.month_name,
    SUM(f.consumption_kwh) AS total_consumption_kwh
FROM FACT_METER_READINGS f
JOIN DIM_DATE d ON DATE(f.read_timestamp) = d.date_key
WHERE d.year_num = 2024
GROUP BY d.year_num, d.month_name;
```


## 3. View Taxonomy (Business-First Design)

### 3.1 View Naming Conventions

**MANDATORY:**

All analytical views must follow this taxonomy:

**View Prefix Taxonomy:**
- **`VW_BA_*`** - Business Analyst views (Low complexity, pre-joined) - e.g., `VW_BA_CUSTOMER_360`
- **`VW_EXEC_*`** - Executive dashboard views (Very Low, aggregated KPIs) - e.g., `VW_EXEC_OUTAGE_SUMMARY`
- **`VW_DS_*`** - Data Science feature views (Medium, wide format) - e.g., `VW_DS_ASSET_FEATURES`
- **`VW_DE_*`** - Data Engineering pipeline views (High, ETL/lineage) - e.g., `VW_DE_DATA_QUALITY`
- **`VW_REF_*`** - Reference lookup views (Very Low, static lists) - e.g., `VW_REF_ASSET_TYPES`
- **`VW_OPS_*`** - Operational monitoring (Medium, real-time status) - e.g., `VW_OPS_GRID_HEALTH`

### 3.2 Business Analyst Views (`VW_BA_*`)

**MANDATORY:**

**Purpose:** Enable self-service analytics with minimal SQL knowledge.

**Design Principles:**
- Pre-join all relevant dimensions
- Use business-friendly column aliases
- Include commonly filtered dimensions
- Provide aggregated and detailed versions
- Add inline documentation via column comments

**Example:**
```sql
CREATE OR REPLACE VIEW VW_BA_CUSTOMER_360 AS
-- Purpose: Complete customer profile with billing, consumption, and service history
-- Target Audience: Business Analysts, Customer Service
-- Usage: SELECT * FROM VW_BA_CUSTOMER_360 WHERE customer_name LIKE '%Smith%'
SELECT
    -- Customer Identity
    c.customer_id,
    c.customer_name,
    c.customer_email,
    c.customer_phone,

    -- Service Address
    m.premise AS service_address,
    m.city,
    m.state,
    m.zip_code,

    -- Meter Information
    m.meter_id,
    m.meter_number,
    m.meter_type,
    m.install_date AS meter_install_date,

    -- Billing Summary (Last 12 Months)
    b.total_bills_12mo,
    b.total_amount_12mo,
    b.avg_monthly_bill,
    b.total_consumption_kwh_12mo,
    b.avg_monthly_consumption_kwh,

    -- Service Quality
    o.total_outages_12mo,
    o.total_outage_hours_12mo,
    o.avg_restoration_time_minutes,

    -- Customer Satisfaction
    r.total_reviews,
    r.avg_sentiment_score,
    r.latest_review_date,

    -- Call Center Activity
    cc.total_calls_12mo,
    cc.last_call_date,
    cc.primary_call_reason

FROM DIM_CUSTOMER c
LEFT JOIN DIM_METER m ON c.customer_id = m.customer_id
LEFT JOIN (
    -- Billing aggregates
    SELECT
        customer_id,
        COUNT(*) AS total_bills_12mo,
        SUM(bill_amount) AS total_amount_12mo,
        AVG(bill_amount) AS avg_monthly_bill,
        SUM(consumption_kwh) AS total_consumption_kwh_12mo,
        AVG(consumption_kwh) AS avg_monthly_consumption_kwh
    FROM FACT_BILLING
    WHERE billing_date >= DATEADD(month, -12, CURRENT_DATE())
    GROUP BY customer_id
) b ON c.customer_id = b.customer_id
LEFT JOIN (
    -- Outage aggregates
    SELECT
        meter_id,
        COUNT(*) AS total_outages_12mo,
        SUM(outage_duration_hours) AS total_outage_hours_12mo,
        AVG(restoration_time_minutes) AS avg_restoration_time_minutes
    FROM FACT_OUTAGES
    WHERE outage_timestamp >= DATEADD(month, -12, CURRENT_DATE())
    GROUP BY meter_id
) o ON m.meter_id = o.meter_id
LEFT JOIN (
    -- Review aggregates
    SELECT
        customer_id,
        COUNT(*) AS total_reviews,
        AVG(sentiment_score) AS avg_sentiment_score,
        MAX(review_date) AS latest_review_date
    FROM FACT_CUSTOMER_REVIEWS
    GROUP BY customer_id
) r ON c.customer_id = r.customer_id
LEFT JOIN (
    -- Call center aggregates
    SELECT
        customer_id,
        COUNT(*) AS total_calls_12mo,
        MAX(call_timestamp) AS last_call_date,
        MODE(call_intent) AS primary_call_reason
    FROM FACT_CUSTOMER_CALLS
    WHERE call_timestamp >= DATEADD(month, -12, CURRENT_DATE())
    GROUP BY customer_id
) cc ON c.customer_id = cc.customer_id

COMMENT = 'BA View: 360-degree customer profile for self-service analytics';
```

### 3.3 Executive Dashboard Views (`VW_EXEC_*`)

**MANDATORY:**

**Purpose:** High-level KPIs for executive dashboards and reporting.

**Design Principles:**
- Highly aggregated (monthly, quarterly, yearly grains)
- Include trend calculations (YoY, MoM)
- Pre-calculate KPIs and ratios
- Focus on business outcomes, not technical metrics

**Example:**
```sql
CREATE OR REPLACE VIEW VW_EXEC_OUTAGE_SUMMARY AS
-- Purpose: Executive-level outage KPIs with trends
-- Target Audience: C-Suite, VP Operations
-- Refresh: Daily
WITH monthly_outages AS (
    SELECT
        DATE_TRUNC('month', outage_timestamp) AS month_date,
        COUNT(*) AS total_outages,
        SUM(customers_affected) AS total_customers_affected,
        AVG(restoration_time_minutes) AS avg_restoration_time_minutes,
        SUM(outage_duration_hours) AS total_outage_hours
    FROM FACT_OUTAGES
    WHERE outage_timestamp >= DATEADD(year, -2, CURRENT_DATE())
    GROUP BY month_date
)
SELECT
    month_date,
    TO_VARCHAR(month_date, 'YYYY-MM') AS month_label,

    -- Current Month KPIs
    total_outages,
    total_customers_affected,
    avg_restoration_time_minutes,
    total_outage_hours,

    -- Calculated KPIs
    ROUND(total_customers_affected / NULLIF(total_outages, 0), 1) AS avg_customers_per_outage,
    ROUND(total_outage_hours / NULLIF(total_outages, 0), 2) AS avg_outage_duration_hours,

    -- Month-over-Month Trends
    LAG(total_outages, 1) OVER (ORDER BY month_date) AS prev_month_outages,
    ROUND((total_outages - LAG(total_outages, 1) OVER (ORDER BY month_date)) /
          NULLIF(LAG(total_outages, 1) OVER (ORDER BY month_date), 0) * 100, 1) AS mom_outage_change_pct,

    -- Year-over-Year Trends
    LAG(total_outages, 12) OVER (ORDER BY month_date) AS prev_year_outages,
    ROUND((total_outages - LAG(total_outages, 12) OVER (ORDER BY month_date)) /
          NULLIF(LAG(total_outages, 12) OVER (ORDER BY month_date), 0) * 100, 1) AS yoy_outage_change_pct

FROM monthly_outages
ORDER BY month_date DESC

COMMENT = 'Executive View: Monthly outage KPIs with trend analysis for C-suite dashboards';
```

### 3.4 Data Science Feature Views (`VW_DS_*`)

**MANDATORY:**

**Purpose:** ML-ready feature tables for training and inference.

**Design Principles:**
- Wide format (one row per entity)
- Include engineered features (lags, rolling aggregates)
- Handle nulls explicitly
- Include feature metadata columns

**Example:**
```sql
CREATE OR REPLACE VIEW VW_DS_ASSET_FEATURES AS
-- Purpose: ML feature table for transformer failure prediction
-- Target Audience: Data Scientists
-- ML Task: Binary classification (failure prediction)
SELECT
    a.asset_id,
    a.asset_type,
    a.asset_name,

    -- Static Features
    a.manufacturer,
    a.model,
    a.rated_capacity_kva,
    DATEDIFF(year, a.install_date, CURRENT_DATE()) AS age_years,
    a.criticality_level,

    -- Time-Series Aggregates (Last 30 Days)
    AVG(t.oil_temp_c) AS avg_oil_temp_c_30d,
    MAX(t.oil_temp_c) AS max_oil_temp_c_30d,
    STDDEV(t.oil_temp_c) AS stddev_oil_temp_c_30d,

    AVG(t.load_pct) AS avg_load_pct_30d,
    MAX(t.load_pct) AS max_load_pct_30d,

    -- Failure Indicators
    MAX(t.failure_imminent) AS failure_flag_30d,
    SUM(t.failure_imminent) AS failure_count_30d,

    -- Derived Features
    CASE
        WHEN MAX(t.oil_temp_c) > 95 THEN 1
        ELSE 0
    END AS high_temp_flag,

    CASE
        WHEN AVG(t.load_pct) > 80 THEN 1
        ELSE 0
    END AS high_load_flag,

    -- Target Variable (for training)
    MAX(CASE
        WHEN t.timestamp >= DATEADD(day, -7, CURRENT_DATE())
        THEN t.failure_imminent
        ELSE NULL
    END) AS target_failure_7d

FROM DIM_GRID_ASSET a
LEFT JOIN FACT_TRANSFORMER_READINGS t
    ON a.asset_id = t.transformer_id
    AND t.timestamp >= DATEADD(day, -30, CURRENT_DATE())
WHERE a.asset_type = 'TRANSFORMER'
GROUP BY
    a.asset_id, a.asset_type, a.asset_name,
    a.manufacturer, a.model, a.rated_capacity_kva,
    a.install_date, a.criticality_level

COMMENT = 'DS View: ML features for transformer failure prediction model';
```

### 3.5 Reference Views (`VW_REF_*`)

**MANDATORY:**

**Purpose:** Static lookup tables and enumerated values.

**Example:**
```sql
CREATE OR REPLACE VIEW VW_REF_ASSET_TYPES AS
-- Purpose: Reference list of valid asset types
SELECT
    'SUBSTATION' AS asset_type,
    'Transmission-to-distribution interface' AS description,
    1 AS hierarchy_level
UNION ALL
SELECT 'FEEDER', 'Primary distribution circuit', 2
UNION ALL
SELECT 'TRANSFORMER', 'Distribution-to-service transformation', 3
UNION ALL
SELECT 'METER', 'Advanced metering infrastructure (AMI) endpoint', 4

COMMENT = 'Reference View: Valid asset types with descriptions';
```


## 4. Backward Compatibility & Migration Strategy

### 4.1 Migration Principles

**MANDATORY:**

All schema changes MUST follow this migration path:

1. **Create new objects with standard names** (e.g., `DIM_GRID_ASSET`)
2. **Create compatibility views with old names** (e.g., `GRID_ASSETS` pointing to `DIM_GRID_ASSET`)
3. **Deprecation notice period** (minimum 30 days)
4. **Remove old objects** only after all consumers migrated

### 4.2 Backward Compatibility View Pattern

```sql
-- Step 1: Create new dimension table with standards
CREATE OR REPLACE TABLE DIM_GRID_ASSET (
    asset_id VARCHAR(50) PRIMARY KEY,
    asset_name VARCHAR(100),
    asset_type VARCHAR(20),
    -- ... standard columns
);

-- Step 2: Create backward compatibility view
CREATE OR REPLACE VIEW GRID_ASSETS AS
SELECT
    asset_id,
    asset_name,
    asset_type,
    -- Map old column names to new if changed
    asset_id AS equipment_id  -- Compatibility alias
FROM DIM_GRID_ASSET

COMMENT = 'DEPRECATED: Use DIM_GRID_ASSET instead. This view provided for backward compatibility until 2025-02-01.';
```

### 4.3 Foreign Key Column Migration

**For mismatched FK names (e.g., `equipment_id` renamed to `asset_id`):**

```sql
-- Old fact table with non-standard FK
CREATE TABLE TRANSFORMER_DATA_OLD (
    equipment_id VARCHAR(50),  -- Non-standard FK name
    timestamp TIMESTAMP_NTZ,
    oil_temp_c FLOAT
);

-- New fact table with standard FK
CREATE TABLE FACT_TRANSFORMER_READINGS (
    transformer_id VARCHAR(50),  -- Standard FK matching DIM_GRID_ASSET.asset_id
    read_timestamp TIMESTAMP_NTZ,
    oil_temp_c FLOAT,
    PRIMARY KEY (transformer_id, read_timestamp)
);

-- Compatibility view
CREATE OR REPLACE VIEW TRANSFORMER_DATA AS
SELECT
    transformer_id AS equipment_id,  -- Alias for backward compatibility
    read_timestamp AS timestamp,
    oil_temp_c
FROM FACT_TRANSFORMER_READINGS

COMMENT = 'DEPRECATED: Use FACT_TRANSFORMER_READINGS instead. This view maps old column names for compatibility.';
```


## 5. Data Generator Requirements

### 5.1 Generator Output Standards

**MANDATORY:**

All Python data generators must produce DataFrames with:

1. **Standardized column names** following Section 1 conventions
2. **Complete metadata columns**: `created_timestamp`, `source_system`
3. **Explicit data types** (no implicit conversions)
4. **Referential integrity** (all FKs reference valid PKs)
5. **Documentation** (inline comments + README)

### 5.2 Required Columns for All Entities

Every generated entity must include:

```python
# Minimum required columns for any entity
required_columns = {
    '<entity>_id': 'VARCHAR(50)',      # Primary key
    '<entity>_name': 'VARCHAR(100)',   # Display name
    'created_timestamp': 'TIMESTAMP_NTZ',  # When record was created
    'source_system': 'VARCHAR(50)',    # Data lineage
}
```

### 5.3 Relationship Integrity Validation

```python
# Example validation in generator
def validate_foreign_keys(df_child, df_parent, fk_column, pk_column):
    """
    Ensure all FK values exist in parent table.

    Args:
        df_child: DataFrame with foreign key
        df_parent: DataFrame with primary key
        fk_column: Foreign key column name in child
        pk_column: Primary key column name in parent

    Raises:
        ValueError: If any FK values are missing from parent
    """
    missing_refs = df_child[~df_child[fk_column].isin(df_parent[pk_column])]

    if not missing_refs.empty:
        raise ValueError(
            f"Referential integrity violation: {len(missing_refs)} rows in child "
            f"have {fk_column} values not found in parent {pk_column}"
        )
```


## 6. SQL DDL Standards

### 6.1 Table Definition Template

```sql
CREATE OR REPLACE TABLE <SCHEMA>.<TABLE_NAME> (
    -- Primary Key
    <entity>_id VARCHAR(50) NOT NULL PRIMARY KEY COMMENT 'Unique identifier',

    -- Foreign Keys (if applicable)
    <parent_entity>_id VARCHAR(50) COMMENT 'References <PARENT_TABLE>.<parent_entity>_id',

    -- Business Keys
    <entity>_name VARCHAR(100) COMMENT 'Human-readable name',
    <entity>_number VARCHAR(50) COMMENT 'External/customer-facing identifier',

    -- Attributes
    <attribute>_<unit> <DATA_TYPE> COMMENT 'Description with unit',

    -- Flags
    is_<state> BOOLEAN DEFAULT FALSE COMMENT 'Boolean flag',

    -- Temporal
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation time',
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'Last update time',

    -- Table-level comment
    COMMENT = '<TABLE_TYPE>: <Purpose> for <audience>'
);

-- Clustering key for large tables (optional but recommended)
ALTER TABLE <SCHEMA>.<TABLE_NAME> CLUSTER BY (<key_column>, <timestamp_column>);
```

### 6.2 Column Comment Standards

**MANDATORY:**

Every column must have a COMMENT that includes:
1. **What it represents** (business definition)
2. **Unit of measure** (if numeric)
3. **Valid values** (if categorical)
4. **FK reference** (if foreign key)

```sql
-- Good Examples
consumption_kwh FLOAT COMMENT 'Total energy consumption in kilowatt-hours for the read interval',
operational_status VARCHAR(20) COMMENT 'Current asset status: ACTIVE, FAILED, MAINTENANCE, DECOMMISSIONED',
parent_asset_id VARCHAR(50) COMMENT 'References GRID_ASSETS.asset_id for hierarchical parent',

-- Bad Examples (too vague)
consumption FLOAT COMMENT 'Consumption value',
status VARCHAR(20) COMMENT 'Status',
parent VARCHAR(50) COMMENT 'Parent ID'
```


## 7. Query Optimization Guidelines

### 7.1 Clustering Keys

**RECOMMENDED:**

For tables > 1 GB, define clustering keys on:
1. **Most frequently filtered columns** (e.g., `asset_id`, `customer_id`)
2. **Temporal columns** (e.g., `read_timestamp`, `billing_date`)

```sql
-- Fact table clustering
ALTER TABLE FACT_METER_READINGS CLUSTER BY (meter_id, DATE(read_timestamp));

-- Dimension table clustering (if large)
ALTER TABLE DIM_GRID_ASSET CLUSTER BY (asset_type, operational_status);
```

### 7.2 View Materialization

**RECOMMENDED:**

For frequently accessed views with complex joins, consider materialization:

```sql
-- Option 1: Materialized View (Snowflake Enterprise+)
CREATE MATERIALIZED VIEW VW_BA_CUSTOMER_360_MAT AS
SELECT * FROM VW_BA_CUSTOMER_360;

-- Option 2: Scheduled Refresh Pattern
CREATE TABLE VW_BA_CUSTOMER_360_CACHE AS
SELECT *, CURRENT_TIMESTAMP() AS cache_refresh_timestamp
FROM VW_BA_CUSTOMER_360;

-- Refresh via Task (daily)
CREATE TASK REFRESH_CUSTOMER_360_CACHE
  WAREHOUSE = UTILITY_DEMO_WH
  SCHEDULE = 'USING CRON 0 2 * * * America/New_York'  -- 2 AM daily
AS
  CREATE OR REPLACE TABLE VW_BA_CUSTOMER_360_CACHE AS
  SELECT *, CURRENT_TIMESTAMP() AS cache_refresh_timestamp
  FROM VW_BA_CUSTOMER_360;
```


## Data Modeling Assessment
- **Entity**: [Entity being modeled]
- **Current Issues**: [Naming inconsistencies, FK mismatches]
- **Proposed Changes**: [Specific column renames, view creations]
- **Backward Compatibility**: [Views created for migration]
- **Validation**: [FK integrity checks, query tests]

## Implementation
[Specific code changes following standards]
