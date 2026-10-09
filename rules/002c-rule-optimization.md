---
schema_version: v4.0
rule_version: v5.0.0
description: "Estimate rule context costs and reduce duplicate guidance without losing safety, dependency closure, or coherent workflows."
last_updated: 2026-09-30
keywords:
  - kw:token budget tiers
  - kw:progressive rule loading
  - kw:ai-rules tokens CLI
  - kw:rule splitting decision tree
  - kw:context window budget allocation
  - kw:TokenBudget metadata format
token_budget: ~1050
context_tier: High
depends:
  required:
    - 002-rule-governance.md  # Schema requirements and standards
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 002a-rule-creation.md  # Step-by-step rule creation workflow
---
# Rule Optimization: Token Budgets and Loading

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when measuring or reducing rule context.

## Scope

**What This Rule Covers:**
Estimate rule size and dependency-closure costs, then remove duplication or split independent tasks without weakening their contracts.

**When to Load This Rule:**
- Update token budgets, choose progressive loading, or evaluate a rule split.
- For verified model-specific limits, load `002k-model-optimization.md`.

## Contract

### Inputs and Prerequisites

- Read the proposed rule, its required dependencies, and the active loader budget policy.
- Identify representative tasks and the available tokenizer or runtime token traces.
- Capture the pre-edit content and estimates before an optimization comparison.

### Mandatory

- Declare `token_budget: ~NUMBER` in YAML. A tokenizer estimate is not a measured runtime read cost or a universal model token count.
- Preview with `--dry-run`. The ordinary `ai-rules tokens` command can update files; `--detailed` does not make it read-only.
- Preserve safety requirements, authorization boundaries, required reads, and coherent procedures before reducing tokens.
- Enforce the 250-line maximum and at most three correct examples for each operational file. Remove redundant tutorials and link primary documentation, without relocating essential safety requirements into optional resources.
- Measure the selected rule set and its complete required closure. Do not infer savings from one file while moving the same text into a dependency.
- Use ContextTier for importance and applicability, not as a function of file size. Follow the active loader's rule cap and budget policy instead of loading whole families.
- Split only genuinely independent tasks. Keep coupled steps together and avoid missing prerequisites or cycles. Use single-letter suffixes for specialized children.
- Do not claim fixed latency, cost, or quality gains without measurements. Word and character heuristics are fallback estimates, not authoritative budgets.

### Execution Steps

1. Preview current budgets and record the tokenizer and selected workload. Use the same estimator before and after changes.
2. Identify duplicate instructions, tutorials unrelated to the task, and examples that resolve no distinct ambiguity. Preserve unique constraints in their required owner.
3. Choose a focused edit or split by applicability. Do not split merely to satisfy an unsupported size target.
4. Update references and metadata after editing. Verify the complete required dependency closure and any new optional load conditions.
5. Re-estimate the same workloads, review semantic preservation, and run schema and discovery checks. Material rewrites require the approved behavioral comparison, not just fewer tokens.

### Validation

- [ ] Budget values use tilde-prefixed numbers and reflect the final text.
- [ ] Before/after estimates use the same tokenizer, selected rules, and closure accounting.
- [ ] Safety constraints and required-read edges are preserved or explicitly corrected with evidence.
- [ ] The rule remains coherent; optional resources have load conditions and dependencies do not cycle.
- [ ] Schema validation, recall checks, trigger-contract checks, and plugin verification pass.
- [ ] Report estimated token change separately from measured runtime latency, token usage, or behavior. Do not claim a metric that was not observed.

If token tooling is missing, report the limitation and any heuristic used. If parsing fails, fix malformed metadata before updating budgets. For unexpected writes, inspect the diff and restore only session-owned changes from the beforeimage; never overwrite concurrent work.

## References

- `schemas/rule-schema.yml`: token-budget format and v4 authoring requirements.
- `src/ai_rules/commands/tokens.py`: estimator and update behavior.
- `skills/rule-loader/workflows/token-budget.md`: load when applying the current selection budget and escalation policy.
- `000-global-core.md`: required context-preservation priorities.

## Token command behavior

Read-only previews:

```bash
uv run ai-rules tokens rules/002-rule-governance.md --detailed --dry-run
uv run ai-rules tokens rules/ --detailed --dry-run
```

The current tool uses `o200k_base`, rounds suggested budgets to 50, and proposes updates beyond its configured threshold, default 5%. Those are tool defaults, not limits on useful rule length. Inspect the actual diff when authorizing an update.

`--context-estimate` sums explicitly selected rule files plus its fixed floor. It does not traverse dependencies automatically. Supply each needed dependency once and inspect the reported components; do not describe the result as an observed agent read trace.
