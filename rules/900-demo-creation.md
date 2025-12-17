# Demo & Synthetic Data Generation Directives

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Demo creation, synthetic data, realistic demos, data generation, demo applications, narrative design, reproducible data, progressive disclosure, Streamlit, data visualization
**TokenBudget:** ~1150
**ContextTier:** Low
**Depends:** None

## Purpose
Establish directives for creating realistic, deterministic, and effective demo applications, covering data generation, narrative design, and visual clarity to deliver compelling demonstrations that showcase product capabilities.

## Rule Scope

Realistic, deterministic, and effective demo application creation with narrative clarity

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Story-first approach** - Lead with customer problem and clear outcome
- **Reproducible data** - Use consistent seeding for deterministic results
- **Offline fallback** - Build resilience for live demo failures
- **Progressive disclosure** - Start basic, show advanced features later
- **Minimize latency** - Pre-warm data and caches
- **Narrative-aligned data** - Realistic, not random noise
- **Never generate massive datasets in memory** - Use batch generation

**Quick Checklist:**
- [ ] Demo narrative defined
- [ ] Data reproducible with seeding
- [ ] Offline mode available
- [ ] Progressive disclosure path clear
- [ ] Performance optimized
- [ ] Data realistic and aligned
- [ ] Batch generation used

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

</contract>

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

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Output Format Examples

```markdown
Implementation Summary:

**Rule Applied:** [rule filename]
**Domain:** [technology/framework]
**Changes:** [high-level summary]

Investigation Results:
- Current state: [what was found]
- Requirements: [what needs to change]
- Constraints: [limitations identified]

Implementation Steps:
1. **[Step 1]**: [Specific action taken]
   - File: `path/to/file`
   - Change: [delta description]

2. **[Step 2]**: [Another action]
   - Configuration: [what was configured]
   - Rationale: [why this approach]

3. **[Step 3]**: [Validation action]
   - Test: [specific test run]
   - Result: [outcome]

Validation Results:
```bash
# Commands run to validate
command --validate
test --run-all
```

Output:
```
[Test output showing success]
```

Next Steps:
- [Optional follow-up items]
- [Monitoring recommendations]
```

## References

### External Documentation
- [Demo Design Best Practices](https://www.salesforce.com/resources/articles/sales-demo/) - Effective demonstration techniques and strategies
- [Faker Documentation](https://faker.readthedocs.io/) - Synthetic data generation library documentation
- [Streamlit Demo Gallery](https://streamlit.io/gallery) - Examples of effective data application demonstrations

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Streamlit UI**: `rules/101-snowflake-streamlit-core.md`
- **Faker**: `rules/240-python-faker.md`
- **Data Science Analytics**: `rules/920-data-science-analytics.md`

## 1. Core Principles
- **Requirement:** Make demos story-first, leading with a customer problem and clear outcome.
- **Requirement:** Ensure data is reproducible and deterministic via consistent seeding.
- **Requirement:** Build resilience with an offline fallback for live failures.
- **Requirement:** Follow progressive disclosure, from basic insights to advanced features.
- **Requirement:** Minimize latency with pre-warmed data and caches.

## 2. Data Generation & Loading
- **Requirement:** Keep synthetic data narrative-aligned and realistic, not random noise.
- **Requirement:** Enforce referential integrity for all foreign keys.
- **Requirement:** Avoid generating massive datasets in memory; use batch generation with generators to stream chunks.
- **Always:** When loading into Snowflake, use DataFrame vectorized writes and tag queries with `QUERY_TAG='demo_data_pipeline'`.
- **Always:** Overwrite on the first batch; append on subsequent batches.
- **Requirement:** Do not hard-code record counts; use a `DemoScenario` or similar pattern.

## 3. Demo Presentation & Reliability
- **Requirement:** Keep the visual design clean and consistent with a limited color palette.
- **Requirement:** Ensure each UI/UX element serves a clear purpose.
- **Mandatory:** Never show raw stack traces; use user-friendly error messages.
- **Always:** Provide annotations for anomalies and AI outputs for context and explainability.
- **Always:** Provide a clean reset capability to clear caches and session state between runs.
- **Requirement:** Use relative timestamps so demos stay fresh over time.
