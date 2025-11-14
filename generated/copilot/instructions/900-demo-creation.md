---
appliesTo:
  - "scripts/**/*"
  - "data/**/*"
  - "streamlit/**/*"
  - "demos/**/*"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Demo creation, synthetic data, realistic demos, data generation, demo applications, narrative design, reproducible data, progressive disclosure
**TokenBudget:** ~900
**ContextTier:** Low
**Depends:** None

# Demo & Synthetic Data Generation Directives

## Purpose
Establish directives for creating realistic, deterministic, and effective demo applications, covering data generation, narrative design, and visual clarity to deliver compelling demonstrations that showcase product capabilities.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Realistic, deterministic, and effective demo application creation with narrative clarity

## Quick Start TL;DR (Read First - 30 Seconds)

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template

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
- **Snowflake Core**: `100-snowflake-core.md`
- **Streamlit UI**: `101-snowflake-streamlit-ui.md`
- **Faker**: `240-python-faker.md`
- **Data Science Analytics**: `500-data-science-analytics.md`
