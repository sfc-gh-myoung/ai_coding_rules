# Example: Snowflake Feature Rule Creation

This walkthrough illustrates researching and authoring Hybrid Tables guidance. It is not a product specification or an executed database workflow.

## Request

```text
Create focused Hybrid Tables guidance for our documented workload. Check existing Snowflake rules first. Do not execute SQL or change the account.
```

## Workflow

1. Discover existing Snowflake owners and inspect their applicability. Read required foundation/domain rules and the current category map before proposing a new filename.
2. Research the relevant capability, availability, privileges, and limitations using current primary documentation for the intended deployment. Record unresolved claims rather than copying historical assumptions about editions, storage, or performance.
3. Generate an unused scaffold with `uv run ai-rules new <NNN-snowflake-aspect> --context-tier High`, replacing the filename placeholder. ContextTier follows the rule's role, not a fixed size range.
4. Populate YAML metadata and Scope, Contract, References. Contract needs meaningful Inputs and Prerequisites, Mandatory, Execution Steps, and Validation. Required Snowflake safety and access guidance stays in the active rule or required dependencies.
5. Use correct, version-appropriate examples only when needed. State prerequisites and expected outcomes, explain defects in prose, and preserve the request's prohibition on database execution.
6. Run structural validation, preview token estimates, and verify discovery using the creator workflows. Review technical claims separately; local Markdown checks do not prove SQL compilation or account behavior.

## Expected result

Provide the populated rule, primary-source references, dependency/keyword decisions, and executed local checks. Disclose unverified account-specific behavior and any model-generation approval still needed.

No table, warehouse, privilege, or account change is authorized by this example. No separate rule index is created. Avoid claimed savings or performance outcomes without actual measurements.
