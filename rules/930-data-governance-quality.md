# Data Governance & Quality Directives

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Data governance, data quality, lineage, metadata management, compliance, data catalog, Great Expectations, schema evolution, data observability, incident response
**TokenBudget:** ~1200
**ContextTier:** Medium
**Depends:** None

## Purpose
Establish comprehensive directives for ensuring data quality, governance, and operational reliability throughout the data lifecycle, using code-based validation, schema evolution management, and automated quality gates.

## Rule Scope
Data quality, governance, and operational reliability throughout the data lifecycle

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Data quality as code** - Version expectation suites in Git
- **Profile before expectations** - Use profiling to discover initial checks
- **Schema evolution** - Add columns first, avoid destructive changes
- **Single source of truth** - Every metric has one canonical definition
- **Automate quality gates** - Integrate validation into ETL/ELT pipelines
- **Monitor data drift** - Track distribution changes with thresholds
- **Never hard-code credentials** - Use secrets management

**Quick Checklist:**
- [ ] Expectation suites in version control
- [ ] Data profiling completed
- [ ] Schema changes non-destructive
- [ ] Metrics documented in catalog
- [ ] Quality gates in CI/CD
- [ ] Drift monitoring configured
- [ ] Incident response plan documented

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

### Pattern 1: [Common Mistake Title]

**Problem:**
[Describe what developers commonly do wrong]

**Why It Fails:**
[Explain why this approach causes issues]

**Correct Pattern:**
```python
# Correct approach with explanation
```

### Pattern 2: [Another Common Mistake]

**Problem:**
[Description of the anti-pattern]

**Why It Fails:**
[Technical explanation of the problem]

**Correct Pattern:**
```python
# Proper implementation
```

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Profile data BEFORE creating expectations** - Understand baseline characteristics
> 2. **Check existing quality checks** - Review current validation framework
> 3. **Never assume schema stability** - Check for recent schema changes
> 4. **Verify catalog existence** - Confirm metrics are documented
> 5. **Test quality gates** - Ensure validation catches known bad data
>
> **Anti-Pattern:**
> "Adding quality check... (without profiling data first)"
> "Changing schema... (without impact analysis)"
>
> **Correct Pattern:**
> "Let me check your data quality setup first."
> [profiles data, reviews existing checks, checks catalog]
> "I see 5% NULL rate. Adding expectation with threshold..."

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
- [Data Management Body of Knowledge (DMBOK)](https://www.dama.org/cpages/body-of-knowledge) - Comprehensive data management framework
- [Data Quality Assessment](https://www.dataversity.net/data-quality-assessment/) - Data quality evaluation methodologies
- [Incident Response Best Practices](https://www.sans.org/white-papers/incident-response/) - SANS incident response guidelines

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Snowflake Security**: `rules/107-snowflake-security-governance.md`
- **Semantic Views**: `rules/106-snowflake-semantic-views-core.md`
- **Data Science Analytics**: `rules/920-data-science-analytics.md`

## 1. Data Quality as Code
- **Requirement:** Treat data quality as code. Version expectation suites and integrate into CI/CD.
- **Requirement:** Layer expectations: start with schema/basic validity, then add business rules.
- **Requirement:** Keep suites lean and focused; avoid noisy or redundant checks.
- **Always:** Use profiling to discover initial expectations, then manually curate and refine before acceptance.
- **Requirement:** Never hard-code credentials or secrets in data quality configurations.
- **Always:** Integrate validation as a gating step in ETL/ELT pipelines.
- **Always:** Monitor for data drift by tracking distribution changes with thresholds.
- **Always:** Reference Great Expectations docs: https://docs.greatexpectations.io/

## 2. Data Stewardship & Schema Evolution
- **Requirement:** Every metric must have a Single Source of Truth in a catalog, with formula, lineage, and ownership.
- **Requirement:** Version metrics and schemas immutably when updated.
- **Always:** Add new columns first; avoid destructive in-place changes.
- **Always:** For major changes, prepare a communication plan with impact and rollback strategy.
- **Requirement:** Use idempotent migration scripts under version control.
- **Requirement:** Validate that downstream consumers are unaffected before production deployment.
- **Always:** Reference Snowflake schema management docs: https://docs.snowflake.com/en/user-guide/database-schemas

## 3. Data Observability
- **Always:** Implement observability to monitor freshness, volume, and schema changes.
- **Always:** Use Snowflake Tasks to automate freshness checks and other metrics.
- **Always:** Create automated alerts for anomalies and quality failures.

## 4. Incident Response & Reliability
- **Always:** Respond with a clear plan; triage severity and assign an incident commander.
- **Requirement:** Avoid uncoordinated fixes; log all actions with timestamps.
- **Requirement:** After stabilization, run a blameless postmortem focusing on systems/processes.
- **Requirement:** Preserve all evidence (logs, query history) until root cause is identified.
- **Requirement:** Make failures visible; avoid silent failures.

## Final Self-Audit Checklist
- **Always:** Ensure all changes comply with these rules.
- **Always:** Confirm the solution addresses the problem with a clear plan.
- **Always:** Verify that the solution promotes data quality, stewardship, and reliability.
