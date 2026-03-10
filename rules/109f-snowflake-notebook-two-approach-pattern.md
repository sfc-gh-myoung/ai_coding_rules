# Snowflake Notebook Two-Approach Clarification Pattern

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:two-approach, kw:notebook-approach, kw:tutorial-approach, kw:approach-comparison
**Keywords:** two-approach pattern, feature store approach, simplified approach, production vs learning, approach clarification, tutorial approach selection
**TokenBudget:** ~2600
**ContextTier:** Low
**Depends:** 109a-snowflake-notebooks-tutorials.md

## Scope

**What This Rule Covers:**
Pattern for clarifying when a tutorial notebook demonstrates a feature but uses a simplified approach, explaining both the production and simplified approaches and why the simpler one is chosen for learning purposes.

**When to Load This Rule:**
- Tutorial demonstrates a feature (e.g., Feature Store) but uses a simplified approach
- Need to explain why a production-ready approach was shown but not fully used
- Comparing two valid approaches in educational content

## References

### Related Rules
**Closely Related** (consider loading together):
- **109a-snowflake-notebooks-tutorials.md** - Parent rule for tutorial design patterns
- **109e-snowflake-notebook-checkpoints.md** - Checkpoint validations for tutorials

## Contract

### Inputs and Prerequisites

- Tutorial notebook that demonstrates but doesn't fully use a feature
- Both production and simplified approaches identified

### Mandatory

- Explain BOTH approaches as valid
- Clarify which approach the notebook uses and WHY
- Provide guidance on when to use the production approach

### Forbidden

- Showing a feature without explaining why it's not fully used
- Implying the simplified approach is always correct

### Execution Steps

1. Identify features demonstrated but not fully utilized
2. Document both approaches with code examples
3. Explain which approach the notebook uses and why
4. Provide production migration guidance

### Output Format

Markdown sections with code examples for both approaches and clear explanation of notebook's choice.

### Validation

Verify both approaches are explained, the notebook's choice is justified, and production guidance is provided.

### Design Principles

- Both approaches are valid for different contexts.
- Teaching focus determines approach selection, not approach quality.
- Always provide the path from learning approach to production approach.

### Post-Execution Checklist

- [ ] Both approaches documented with code examples
- [ ] Clear explanation of which approach notebook uses and why
- [ ] Production migration guidance provided
- [ ] Benefits listed for each approach

## Implementation Details

### Two-Approach Clarification Pattern

**Purpose:** When notebook demonstrates feature but uses simplified approach, explain BOTH approaches and WHY the simpler one is used.

**Structure:**
```markdown

## [NOTE] [Feature]: Two Approaches Explained

**Why did we [setup feature] but not use it?**

The notebook demonstrates **two valid approaches** for [task]:

### Approach A: [Production Name]
```[language]
[Code example]
```

**Benefits:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**Use when:** [Scenario]

### Approach B: [Simplified Name]
```[language]
[Code example]
```

**Benefits:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**Use when:** [Scenario]

### This Notebook's Approach

**We use Approach B** to keep the focus on [primary learning goal]. The [feature] setup in Steps X-Y shows you **how to organize for production** while using the simpler approach for actual training.

**For production deployments:** Uncomment the [feature] code in Step [X] and use `[method]()`.

**Learning Takeaway:** [Key insight about when to use each approach]
```

**Best Practices:**
- **Requirement:** Use when demonstrating feature but not fully utilizing it
- **Always:** Explain why BOTH approaches are valid
- **Always:** Clarify which approach the notebook uses and WHY
- **Always:** Provide guidance on when to use production approach

> For scenarios with three or more valid approaches, use the same pattern structure but add Approach C/D sections. Keep the "This Notebook's Approach" section to explain which single approach the tutorial uses and why.

### Real-World Example: Feature Store Setup

**Scenario:** Notebook demonstrates Feature Store entity/feature organization but trains models using simplified DataFrame approach.

````markdown

## [NOTE] Feature Store: Two Approaches Explained

**Why did we set up Feature Store entities but not use `fs.generate_dataset()`?**

The notebook demonstrates **two valid approaches** for feature engineering:

### Approach A: Feature Store `generate_dataset()`
```python
# Production-ready: Automatic joins, time-travel, lineage tracking
training_df = fs.generate_dataset(
    spine_df=spine,
    features=[customer_features, order_features],
    spine_timestamp_col='OBSERVATION_DATE'
)
```

**Benefits:**
- Automatic feature joins across entities (no manual merge logic required)
- Point-in-time correctness (prevents data leakage in temporal scenarios)
- Lineage tracking (see which features used in which models via Feature Store UI)
- Version control (track feature definitions and transformations over time)

**Use when:** Multi-entity features (10+ features), production deployment scenarios, team collaboration with shared feature definitions

### Approach B: Direct Snowpark DataFrame Operations
```python
# Explicit joins for learning purposes
training_df = spine.join(customer_features, on='CUSTOMER_ID') \
                   .join(order_features, on='ORDER_ID')
```

**Benefits:**
- Transparent logic (see exactly how features combine in explicit joins)
- Simpler for single-entity features (no Feature Store overhead)
- Easier to debug for beginners (direct DataFrame operations, familiar pandas-like API)
- Faster iteration for exploratory analysis (no entity registration needed)

**Use when:** Learning Feature Store concepts, exploratory analysis with <10 features, single-entity scenarios, rapid prototyping

### This Notebook's Approach

**We use Approach B** to keep the focus on ML algorithms and imbalanced data strategies. The Feature Store setup in Steps 2-3 shows you **how to organize for production** (entity registration, feature definitions) while using the simpler DataFrame approach for actual training.

**For production deployments:** Uncomment the `fs.generate_dataset()` code in Step 4 and use `training_df = fs.retrieve_feature_values(spine_df=spine, features=[...])` for automatic joins and lineage tracking.

**Learning Takeaway:** Feature Store adds governance and automation valuable for production multi-entity scenarios. Use it when team collaboration, lineage tracking, and point-in-time correctness matter. Use direct DataFrames for exploration, learning, and single-entity feature engineering.
````

This example demonstrates when to show feature setup (teaching organizational patterns) while using simpler execution (maintaining focus on primary learning objectives like imbalanced data handling).

### Real-World Example: Stored Procedures vs Inline SQL

**Scenario:** Tutorial teaches data transformation concepts using inline SQL cells, but production would use stored procedures for reusability and parameterization.

**This Notebook's Approach:** We use inline SQL to keep transformations visible and step-by-step. For production, wrap these transformations in stored procedures with parameterized inputs. See `102-snowflake-stored-procedures.md` for procedure patterns.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Showing Only the Simplified Approach Without Acknowledging the Production Alternative**

**Problem:** The notebook uses a simplified approach (e.g., direct DataFrame joins) but never mentions that a production-ready alternative exists (e.g., Feature Store `generate_dataset()`). Learners assume the simplified approach is the only way, then struggle when they encounter the production pattern in real codebases. Worse, they may deploy the simplified approach to production where it lacks governance, lineage tracking, and point-in-time correctness.

**Correct Pattern:** Always document both approaches with code examples, even when the notebook only uses one. Include a "This Notebook's Approach" section that explains the choice and provides explicit guidance on when to switch to the production approach.

```python
# Wrong: Only showing the simplified approach with no mention of alternatives
# (Learner assumes this is the only/best way)
training_df = spine.join(customer_features, on="CUSTOMER_ID") \
                   .join(order_features, on="ORDER_ID")
model.fit(training_df)

# Correct: Show both approaches, explain the notebook's choice
# --- Approach A (Production): Feature Store with automatic joins ---
# training_df = fs.generate_dataset(
#     spine_df=spine,
#     features=[customer_features, order_features],
#     spine_timestamp_col="OBSERVATION_DATE"
# )
# --- Approach B (This Notebook): Direct DataFrame joins ---
# We use direct joins to keep focus on ML algorithms. See [NOTE] above.
training_df = spine.join(customer_features, on="CUSTOMER_ID") \
                   .join(order_features, on="ORDER_ID")
# For production: uncomment Approach A for lineage tracking and time-travel
```

**Anti-Pattern 2: Presenting the Simplified Approach as Inferior or "Wrong"**

**Problem:** The notebook frames the simplified approach with dismissive language like "for simplicity, we'll use this hacky workaround" or "ideally you'd use X, but we'll cut corners with Y." This creates anxiety in learners who think they're learning bad practices, and it undermines their confidence in the tutorial's value.

**Correct Pattern:** Present both approaches as valid for different contexts. The simplified approach is correct for learning and exploratory work. Use neutral language: "We use Approach B to keep focus on [learning goal]" rather than "We use the shortcut because the real way is too complex."

```markdown
<!-- Wrong: Dismissive language that undermines learner confidence -->
### Hacky Workaround
Ideally we'd use Feature Store's `generate_dataset()` but that's too
complex for this tutorial, so we'll cut corners with manual joins.
This is NOT how you'd do it in production.

<!-- Correct: Neutral language presenting both as valid -->
### This Notebook's Approach
We use **Approach B (direct DataFrame joins)** to keep the focus on
imbalanced data strategies. Direct joins are the correct choice for
exploratory analysis and single-entity features.

**For production multi-entity scenarios:** Use Approach A
(`fs.generate_dataset()`) for automatic joins, lineage tracking,
and point-in-time correctness.
```

**Anti-Pattern 3: Setting Up a Feature But Never Explaining Why It Goes Unused**

**Problem:** The notebook includes setup steps for a feature (e.g., registering Feature Store entities in Steps 2-3) but then silently uses a different approach in subsequent steps without explanation. Learners are confused about why they spent time on setup that appears to serve no purpose, and they suspect they missed something or the notebook is broken.

**Correct Pattern:** Use the Two-Approach Clarification Pattern immediately after the setup steps. Explicitly state: "Why did we set up [feature] but not use it?" Then explain that the setup demonstrates production organizational patterns while the simpler approach keeps focus on the primary learning objective. Provide a clear path for learners to "uncomment and switch" to the production approach.

```python
# Wrong: Register entities then silently ignore them
fs = FeatureStore(session)
entity = Entity(name="CUSTOMER", join_keys=["CUSTOMER_ID"])
fs.register_entity(entity)
fv = FeatureView(name="CUSTOMER_FEATURES", entities=[entity], ...)
fs.register_feature_view(fv)
# ... 10 cells later, no mention of Feature Store ...
training_df = spine.join(features_df, on="CUSTOMER_ID")  # Learner: "Why did I register entities?"

# Correct: Add a Two-Approach Clarification cell immediately after setup
# [Markdown cell after registration]:
# ## [NOTE] Feature Store: Two Approaches Explained
# **Why did we set up entities but not use `fs.generate_dataset()`?**
# Steps 2-3 show how to organize for production (entity registration).
# We use direct joins (Approach B) to keep focus on ML algorithms.
# **To switch:** Uncomment this line in Step 4:
# training_df = fs.generate_dataset(spine_df=spine, features=[fv])
training_df = spine.join(features_df, on="CUSTOMER_ID")
```
