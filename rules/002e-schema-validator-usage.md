---
schema_version: v4.0
rule_version: v5.0.0
description: "Run the active rule validator, interpret exit codes and severities, and repair structural defects without weakening validation or overwriting existing work."
last_updated: 2026-09-30
keywords:
  - kw:ai-rules validate
  - kw:schema v3.2 compliance
  - kw:severity levels CRITICAL HIGH MEDIUM
  - kw:exit code interpretation
  - kw:common validation fixes
  - kw:validator command flags
token_budget: ~1250
context_tier: High
depends:
  required:
    - 002-rule-governance.md  # Schema requirements and active standards
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 002f-schema-validator-advanced.md  # CI/CD integration and automation workflows
    - 002a-rule-creation.md  # Rule creation workflow with validation steps
    - 002c-rule-optimization.md  # Token budgets and performance
---
# Schema Validator Usage: Commands and Error Resolution

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when diagnosing rule validation failures.

## Scope

**What This Rule Covers:**
Run `ai-rules validate`, interpret its diagnostics, and repair v4 rule structure. A passing schema check does not verify technical content or model behavior.

**When to Load This Rule:**
- Validate operational rules or diagnose metadata, section, and Contract errors.
- For CI or programmatic output handling, load `002f-schema-validator-advanced.md`.

## Contract

### Inputs and Prerequisites

- A readable rule path and the current `schemas/rule-schema.yml`.
- The project's locked Python environment and `ai-rules` CLI. Use the version requirements in `pyproject.toml` rather than an obsolete Python floor.
- A beforeimage for any file you are authorized to repair.

### Mandatory

- Run the real validator and retain its exit code and diagnostics. A successful shell pipeline or an output phrase alone is not proof of validation.
- Fix CRITICAL and HIGH errors before declaring success. Review MEDIUM/INFO diagnostics and disclose those retained; strict mode treats warnings as failures.
- Do not weaken validator internals, disable checks, or use comment exceptions to turn an invalid rule into a pass.
- Compare diagnostics against the active schema. Demonstrate a false positive with a minimal reproducer before proposing a validator correction.
- Keep keyword entries typed and within the combined 5-11 bound. Do not add filler solely to satisfy the count.
- Restore only task-owned changes if recovery is needed. Never overwrite a modified schema from Git without explicit authorization.

### Execution Steps

1. Confirm the target and schema paths. Run validation on the smallest failing rule with `--verbose` when needed.
2. Read each blocking diagnostic and the relevant source lines. Distinguish invalid content from unavailable tooling or an invalid schema configuration.
3. Repair the actual cause: missing metadata, section order, malformed values, or empty required content. Preserve the rule's unique requirements.
4. Re-run the focused command, then the affected corpus and integration gates. Do not infer success from the absence of the old message.
5. Report commands, exit codes, remaining warnings, and any checks not executed.

### Validation

- [ ] The command executed against the intended rule and active schema without tool or Python errors.
- [ ] No CRITICAL or HIGH diagnostics remain; stricter checks satisfy their configured policy.
- [ ] Repairs were revalidated and did not overwrite pre-existing work.
- [ ] The rule still has meaningful prerequisites, actions, safety constraints, and verification content.
- [ ] Reported completion distinguishes schema results from technical and behavioral review.

If dependencies or schema files are missing, report the exact error and required setup. An authorized environment sync may repair dependencies. If it cannot, preserve the failure evidence and mark validation blocked rather than substituting a manual pass.

## References

- `schemas/rule-schema.yml`: active structural rules and diagnostic severities.
- `src/ai_rules/commands/validate.py`: CLI exit behavior and validation implementation.
- [CommonMark specification](https://spec.commonmark.org/): heading and fence syntax.

## Commands

```bash
uv run ai-rules validate rules/002-rule-governance.md --verbose
uv run ai-rules validate rules/ --quiet
uv run ai-rules validate rules/ --json
uv run ai-rules validate rules/ --strict
```

Exit zero means no blocking findings under the selected mode. Exit one reports a validation or execution failure; inspect the diagnostic to identify which. Keep the command's failure status when scripting around it. Use `--schema` only for an intentional schema selection, not to avoid active repository requirements.

Companion examples and skills have separate checks:

```bash
uv run ai-rules validate rules/examples/ --examples
uv run ai-rules validate-skills skills/
```

## Repair guide

- Missing metadata: add the required YAML field with a valid value, not an inline duplicate. Versions use `vMAJOR.MINOR.PATCH`; token budgets use `~NUMBER`.
- Wrong section order: move whole sections into Scope, Contract, References order without losing their content.
- Missing or empty Contract subsection: provide meaningful content under Inputs and Prerequisites, Mandatory, Execution Steps, and Validation. A sibling heading does not populate an empty subsection.
- Missing Scope labels: include What This Rule Covers and When to Load This Rule with task-specific content.
- Late Contract: move it near the start according to the active placement configuration, not a stale line-limit example.
- Malformed code fences: distinguish examples from actual headings; use a longer outer fence when nesting.

Do not reconstruct an entire rule for a local defect. If the active contract changed across the corpus, plan and validate that migration as a coupled change rather than silently relaxing the checker.
