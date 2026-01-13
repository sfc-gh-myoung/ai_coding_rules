# Snowflake Demo: Creation and Synthetic Data

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-12
**Keywords:** Demo creation, synthetic data, realistic demos, data generation, demo applications, narrative design, reproducible data, progressive disclosure, Streamlit, data visualization
**TokenBudget:** ~1900
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

## Core Principles

- **Story-first approach:** Make demos lead with a customer problem and clear outcome
- **Reproducibility:** Ensure data is deterministic via consistent seeding (Faker seed=42)
- **Resilience:** Build offline fallback for live failures
- **Progressive disclosure:** Start with basic insights, show advanced features later
- **Performance:** Minimize latency with pre-warmed data and caches

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
