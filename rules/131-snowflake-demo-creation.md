# Snowflake Demo: Creation and Synthetic Data

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Demo creation, synthetic data, realistic demos, data generation, demo applications, narrative design, reproducible data, progressive disclosure, Streamlit, data visualization
**LoadTrigger:** kw:demo-creation, kw:synthetic-data
**TokenBudget:** ~3050
**ContextTier:** Low
**Depends:** 130-snowflake-demo-sql.md

## Scope

**What This Rule Covers:**
Directives for creating realistic, deterministic, and effective demo applications. Covers data generation, narrative design, and visual clarity to deliver compelling demonstrations that showcase product capabilities.

**When to Load This Rule:**
- Creating demo applications or proof-of-concepts
- Generating synthetic data for demonstrations
- Designing narrative-driven demos
- Building reproducible demo environments
- Optimizing demo performance and reliability

## References

### Dependencies

**Must Load First:**
- **130-snowflake-demo-sql.md** - Demo SQL patterns

**Related:**
- **132-snowflake-demo-modeling.md** - Data modeling for demos
- **101-snowflake-streamlit-core.md** - Streamlit UI patterns
- **240-python-faker.md** - Synthetic data generation with Faker
- **920-data-science-analytics.md** - Data science and analytics patterns

### External Documentation

- [Demo Design Best Practices](https://www.salesforce.com/resources/articles/sales-demo/) - Effective demonstration techniques and strategies
- [Faker Documentation](https://faker.readthedocs.io/) - Synthetic data generation library documentation
- [Streamlit Demo Gallery](https://streamlit.io/gallery) - Examples of effective data application demonstrations

## Contract

### Inputs and Prerequisites

- Demo narrative and target audience defined
- Technology stack selected (Streamlit, Snowflake, etc.)
- Data schema requirements identified
- Performance and latency constraints understood

### Mandatory

- Use Faker library for synthetic data generation with consistent seeding
- Implement batch generation for large datasets (avoid in-memory generation)
- Build offline fallback mechanisms for live demo resilience
- Pre-warm data and caches to minimize latency
- Use relative timestamps to keep demos fresh over time
- Provide clean reset capability for session state

### Forbidden

- Generating massive datasets in memory during live demos
- Using fully random independent columns without realistic correlations
- Showing raw stack traces to demo audiences
- Hard-coding record counts (use DemoScenario pattern)
- Random noise data without narrative alignment

### Execution Steps

1. Define demo narrative with customer problem and clear outcome
2. Design data schema with referential integrity constraints
3. Implement batch data generation with Faker seeding (seed=42 for reproducibility)
4. Create progressive disclosure path from basic to advanced features
5. Build offline fallback mechanisms for resilience
6. Pre-warm caches and optimize for minimal latency
7. Add user-friendly error messages and annotations
8. Implement clean reset capability
9. Test demo flow end-to-end with realistic timing
10. Validate data reproducibility and narrative alignment

### Output Format

Demo application with:
- Story-first narrative structure
- Reproducible synthetic data (seeded)
- Offline fallback mode
- Progressive disclosure UI
- Clean visual design with limited color palette
- User-friendly error messages
- Annotations for anomalies and AI outputs
- Clean reset capability

### Validation

**Pre-Task-Completion Checks:**
- Demo narrative defined and clear
- Data generation uses consistent seeding
- Offline mode implemented and tested
- Progressive disclosure path validated
- Performance optimized (pre-warmed caches)
- Data realistic with correlations
- Batch generation used for large datasets

**Success Criteria:**
- Demo runs reproducibly with same seed
- Data shows realistic correlations and patterns
- Offline mode works without external dependencies
- Demo timing predictable and optimized
- Error messages user-friendly (no stack traces)
- Reset capability clears all state cleanly
- Visual design clean and consistent

**Negative Tests:**
- Massive dataset generation should NOT block UI
- Random independent columns should NOT pass review
- Raw stack traces should NOT appear to users
- Hard-coded record counts should trigger refactoring
- Demo should work offline (no external API failures)

### Design Principles

- **Story-first approach:** Lead with customer problem and clear outcome
- **Reproducibility:** Use consistent seeding for deterministic results
- **Resilience:** Build offline fallback for live demo failures
- **Progressive disclosure:** Start basic, show advanced features later
- **Performance:** Minimize latency with pre-warmed data and caches
- **Realism:** Narrative-aligned data with correlations, not random noise
- **Efficiency:** Batch generation for large datasets, never in-memory

### Post-Execution Checklist

- [ ] Demo narrative defined with customer problem and outcome
- [ ] Data reproducible with consistent seeding (Faker seed=42)
- [ ] Offline mode available and tested
- [ ] Progressive disclosure path clear and validated
- [ ] Performance optimized (pre-warmed caches, minimal latency)
- [ ] Data realistic with correlations aligned to narrative
- [ ] Batch generation used for large datasets
- [ ] User-friendly error messages (no raw stack traces)
- [ ] Annotations provided for anomalies and AI outputs
- [ ] Clean reset capability implemented and tested
- [ ] Visual design clean with limited color palette
- [ ] Relative timestamps used to keep demos fresh

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Generating Massive Datasets Live During Demo**
```python
# Problem: Generating 1M rows in memory during demo
import random
data = []
for i in range(1_000_000):
    data.append({
        'id': i,
        'value': random.random(),
        'category': random.choice(['A', 'B', 'C'])
    })
df = pd.DataFrame(data)
```
**Problem:** Memory exhaustion, slow execution, demo timing unpredictable - audience waits while data generates.

**Correct Pattern:**
```python
# Pre-generated data or batch generation
from faker import Faker
fake = Faker()
fake.seed_instance(42)  # Deterministic

def generate_batch(n=1000):
    """Generate data in batches for efficiency"""
    return pd.DataFrame([
        {'id': i, 'value': fake.pyfloat(), 'category': fake.random_element(['A', 'B', 'C'])}
        for i in range(n)
    ])
```
**Benefits:** Predictable timing, memory efficient, reproducible results with seeding.

**Anti-Pattern 2: Fully Random Independent Columns**
```python
# Problem: No realistic patterns
df['age'] = np.random.randint(18, 80, size=1000)
df['income'] = np.random.randint(20000, 200000, size=1000)
df['purchase'] = np.random.randint(0, 10000, size=1000)
```
**Problem:** Unrealistic - no correlation between age/income/purchase behavior. Data doesn't tell a story.

**Correct Pattern:**
```python
# Correlated, realistic patterns
fake = Faker()
fake.seed_instance(42)

data = []
for _ in range(1000):
    age = fake.random_int(22, 70)
    income = 25000 + (age - 22) * 2000 + fake.random_int(-5000, 15000)  # Age-income correlation
    purchase = income * 0.05 + fake.random_int(-500, 1500)  # Income-purchase correlation
    data.append({'age': age, 'income': income, 'purchase': purchase})
```
**Benefits:** Realistic correlations, meaningful patterns, supports narrative storytelling.

## DemoScenario Pattern

**Rule:** Never hard-code record counts. Use a scenario pattern for configurable data generation:

```python
from dataclasses import dataclass

@dataclass
class DemoScenario:
    name: str
    customers: int = 100
    orders: int = 500
    products: int = 50
    days_of_history: int = 90

# Usage
scenario = DemoScenario(name="quick_demo", customers=50, orders=200)

def generate_demo_data(scenario: DemoScenario):
    fake = Faker()
    fake.seed_instance(42)
    customers = [fake.simple_profile() for _ in range(scenario.customers)]
    # Generate orders referencing customer IDs
    orders = [{'customer_id': fake.random_element(range(scenario.customers)),
               'amount': fake.pyfloat(min_value=10, max_value=500)}
              for _ in range(scenario.orders)]
    return customers, orders
```

## Offline Fallback Pattern

```python
import json
from pathlib import Path

CACHE_DIR = Path("demo_cache")

def get_demo_data(scenario: DemoScenario):
    cache_file = CACHE_DIR / f"{scenario.name}.json"
    try:
        # Try live generation from Snowflake
        df = session.sql("SELECT * FROM demo_source LIMIT 1000").to_pandas()
        # Cache for offline use
        CACHE_DIR.mkdir(exist_ok=True)
        df.to_json(cache_file, orient="records")
        return df
    except Exception:
        # Fall back to cached data
        if cache_file.exists():
            return pd.read_json(cache_file, orient="records")
        # Final fallback: generate synthetic
        return generate_demo_data(scenario)
```

## Vectorized Snowflake Writes

**Connection Paradigms:** Use Snowpark `session` for interactive/notebook contexts (e.g., `session.sql(...).collect()`). Use `snowflake-connector-python` `conn` for batch scripts (e.g., `write_pandas(conn, ...)`). Do not mix paradigms in the same script.

```python
from snowflake.connector.pandas_tools import write_pandas

# Tag queries for cost tracking
session.sql("ALTER SESSION SET QUERY_TAG = 'demo_data_pipeline'").collect()

# Vectorized write (much faster than row-by-row INSERT)
write_pandas(conn, df, table_name='DEMO_TABLE', database='DEMO_DB', schema='PUBLIC', overwrite=True)
```

## Snowflake-Native Data Generation with GENERATOR()

For generating data directly in Snowflake without Python, use the `GENERATOR()` table function:

```sql
-- Generate 10,000 rows of synthetic customer data
CREATE OR REPLACE TABLE DEMO_DB.PUBLIC.CUSTOMERS AS
SELECT
    ROW_NUMBER() OVER (ORDER BY SEQ4()) AS customer_id,
    'CUST-' || LPAD(ROW_NUMBER() OVER (ORDER BY SEQ4()), 6, '0') AS customer_code,
    ARRAY_CONSTRUCT('Enterprise', 'SMB', 'Consumer')[UNIFORM(0, 2, RANDOM(42))] AS segment,
    DATEADD(day, -UNIFORM(30, 1095, RANDOM(42)), CURRENT_DATE()) AS signup_date,
    ROUND(UNIFORM(1000, 50000, RANDOM(42))::FLOAT + RANDOM(42) / 1e18, 2) AS annual_spend
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- Generate correlated orders referencing customers
CREATE OR REPLACE TABLE DEMO_DB.PUBLIC.ORDERS AS
SELECT
    ROW_NUMBER() OVER (ORDER BY SEQ4()) AS order_id,
    UNIFORM(1, 10000, RANDOM(42)) AS customer_id,
    DATEADD(day, -UNIFORM(0, 365, RANDOM(42)), CURRENT_DATE()) AS order_date,
    ROUND(UNIFORM(10, 2000, RANDOM(42))::FLOAT, 2) AS amount
FROM TABLE(GENERATOR(ROWCOUNT => 50000));
```

**When to use GENERATOR() vs Python Faker:**
- **GENERATOR()**: Large volumes (>10K rows), simple column types, no need for realistic names/emails
- **Python Faker**: Realistic PII (names, emails, addresses), complex correlations, narrative-driven data

## Data Generation and Loading

- **Narrative alignment:** Keep synthetic data realistic, not random noise
- **Referential integrity:** Enforce foreign key constraints for all relationships
- **Batch generation:** Avoid generating massive datasets in memory; use generators to stream chunks
- **Snowflake loading:** Use DataFrame vectorized writes and tag queries with `QUERY_TAG='demo_data_pipeline'`
- **Write strategy:** Overwrite on first batch; append on subsequent batches
- **Scenario pattern:** Do not hard-code record counts; use `DemoScenario` or similar pattern

## Demo Presentation and Reliability

- **Visual design:** Keep clean and consistent with limited color palette
- **UI/UX clarity:** Ensure each element serves a clear purpose
- **Error handling:** Never show raw stack traces; use user-friendly error messages
- **Annotations:** Provide context for anomalies and AI outputs for explainability
- **Reset capability:** Provide clean reset to clear caches and session state between runs
- **Timestamps:** Use relative timestamps so demos stay fresh over time

## Streamlit Demo Integration

Minimal pattern for a Streamlit demo app with Snowflake data:

```python
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

st.title("Customer Analytics Demo")

# Sidebar: scenario selection
scenario = st.selectbox("Demo Scenario", ["Quick (50 customers)", "Full (500 customers)"])
n_customers = 50 if "Quick" in scenario else 500

# Load or generate data
@st.cache_data(ttl=300)
def load_demo_data(n):
    return session.sql(f"SELECT * FROM DEMO_DB.ANALYTICS.CUSTOMERS LIMIT {n}").to_pandas()

try:
    df = load_demo_data(n_customers)
    st.metric("Total Customers", len(df))
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Could not load data. Check that DEMO_DB exists. Error: {e}")

# Reset button
if st.button("Reset Demo"):
    st.cache_data.clear()
    st.rerun()
```

**Key patterns:** Use `@st.cache_data` for pre-warming, `try/except` with `st.error()` (never raw tracebacks), sidebar for scenario selection, and a reset button that clears cache + reruns.
