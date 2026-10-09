---
schema_version: v4.0
rule_version: v3.0.0
description: "Plan model-specific context and output budgets from verified runtime limits; estimate rule costs without dropping required instructions or inventing prices."
last_updated: 2026-09-30
keywords:
  - kw:context window sizing
  - kw:loading budget calculation
  - kw:GPT-4o GPT-5.1
  - kw:Claude Sonnet Opus
  - kw:Gemini Pro
  - kw:prompt caching strategy
token_budget: ~950
context_tier: Low
depends:
  required:
    - 002c-rule-optimization.md  # Token budget estimates, progressive loading, and sizing guidelines
---
# Model-Specific Rule Optimization

> **REFERENCE RULE: LOAD WHEN NEEDED**

## Scope

**What This Rule Covers:**
Allocate context for a specific model and deployment using verified limits, current task needs, and the active rule-loader policy.

**When to Load This Rule:**
- Compare available models, plan context/output reserves, or assess prompt-caching cost assumptions.
- This rule does not provide a static price or context-window catalog.

## Contract

### Inputs and Prerequisites

- Exact model identity, provider or gateway, deployment configuration, and approved budget.
- Current source for effective input/context/output limits and pricing, with retrieval date.
- Estimated system, history, tool, task, and required-rule tokens; observed traces when available.

### Mandatory

- Verify limits for the actual runtime. A provider maximum does not prove the gateway exposes that capacity.
- Reserve output and any applicable reasoning/tool overhead explicitly. Do not allocate the whole context to rules.
- Respect the active loader's cap and dependency policy. A large model context does not authorize loading all rule families.
- Preserve required rules and safety constraints. Defer optional material or split the task when needed; do not silently omit a prerequisite to fit a budget.
- Treat input/output/cache prices, cache eligibility, and model availability as time-sensitive. State unknowns instead of using guessed defaults.
- Do not assume caching is enabled or promise a cache discount. Verify support and actual hit accounting before using it in a cost result.
- Do not substitute models without authorization where identity, capability, privacy, or cost matters. Unknown model limits block a confident sizing recommendation.

### Execution Steps

1. Resolve the exact model and runtime settings from the current environment and authoritative documentation.
2. Estimate required context components using the same tokenizer/accounting basis. Separate estimates from runtime-reported usage.
3. Calculate remaining capacity after fixed input, task input, and output reserves, then apply the stricter active loader policy.
4. Select task-relevant rules plus complete required dependencies. If they do not fit, defer optional context or propose task partitioning with explicit limitations.
5. Compare supported model or cache options within the user's authorization. Report sources, assumptions, selected rules, estimated cost, and unverified behavior.

### Validation

- [ ] Model and gateway identity are verified; documented limits match the relevant deployment.
- [ ] Context accounting includes history, tools, task input, required closure, and output reserve without double counting.
- [ ] No required safety instruction or dependency was dropped for size.
- [ ] Prices, routing, cache assumptions, and unsupported metrics are disclosed.
- [ ] Recommendations match the user's task and approved cost/privacy boundaries.

If capacity is uncertain, do not assume a generic 128K or 200K window. Ask for the missing configuration or present a conditional recommendation. If the model is unavailable, report it and propose alternatives for approval. When context pressure grows, preserve mandatory instructions and durable task evidence before summarizing optional material.

## References

- [OpenAI model documentation](https://platform.openai.com/docs/models): verify the selected model's current provider limits.
- [Anthropic model overview](https://docs.claude.com/en/docs/about-claude/models/overview): verify model capabilities and applicable constraints.
- [Gemini model documentation](https://ai.google.dev/gemini-api/docs/models): verify the selected model and deployment limits.
- `002c-rule-optimization.md`: consistent tokenizer estimates and closure accounting.

## Comparison reporting

For a comparison, record exact models, settings, prompts, rule-set hashes, repetitions, and observed outcomes. Do not infer capability from model-family names or advertising claims. Separate measured usage and latency from theoretical capacity, and use the same workloads before claiming an improvement.

Retired fixed-percentage allocations and static model/pricing tables are not substitutes for current evidence. Use a project-defined reserve only when its purpose and limitations are explicit.
