**Description:** Directives for creating realistic, deterministic, and effective demo applications, from data generation to narrative and visual clarity.
**AppliesTo:** `scripts/**/*`, `data/**/*`, `streamlit/**/*`, `demos/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.2
**LastUpdated:** 2025-09-16

# Demo & Synthetic Data Generation Directives

## Purpose
Establish directives for creating realistic, deterministic, and effective demo applications, covering data generation, narrative design, and visual clarity to deliver compelling demonstrations that showcase product capabilities.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Realistic, deterministic, and effective demo application creation with narrative clarity


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

## 4. Anti-Patterns
- **Avoid:** Generating massive datasets live during the demo.
- **Avoid:** Unlabeled anomalies or AI outputs.
- **Avoid:** Fully random independent columns.
- **Avoid:** A single monolithic generator for all data regardless of industry.
- **Avoid:** Row-by-row data loading.

## References

### External Documentation
- [Demo Design Best Practices](https://www.salesforce.com/resources/articles/sales-demo/) - Effective demonstration techniques and strategies                                                                           
- [Faker Documentation](https://faker.readthedocs.io/) - Synthetic data generation library documentation
- [Streamlit Demo Gallery](https://streamlit.io/gallery) - Examples of effective data application demonstrations

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Streamlit UI**: `101-snowflake-streamlit-ui.md`
- **Faker**: `240-python-faker.md`
- **Data Science Analytics**: `500-data-science-analytics.md`
