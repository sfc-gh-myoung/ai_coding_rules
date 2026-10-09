---
schema_version: v4.0
rule_version: v3.1.0
description: "Curating minimal viable tool sets for AI agents. Covers deciding the right number of tools, when to split complex tools into focused ones, when to merge related tools for efficiency, and maintaining"
last_updated: 2026-10-08
keywords:
  - kw:tool set curation
  - kw:minimal viable tool set
  - kw:tool splitting criteria
  - kw:tool merging criteria
  - kw:tool bloat detection
  - kw:tool boundaries
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 004-tool-design-for-agents.md  # Core tool design principles
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 004b-tool-output-efficiency.md  # Token-efficient tool outputs
---
# Tool Set Curation for AI Agents

## Scope

**What This Rule Covers:**
Selecting the smallest useful tool set, defining boundaries and evaluating evidence-based splits, merges, version changes and experimental promotion.

**When to Load This Rule:**
When adding/removing tools, diagnosing ambiguous selection, auditing overlap or designing an agent's capabilities.

## Contract

### Inputs and Prerequisites

- Current tool contracts/source and required use-case inventory.
- Representative agent traces, selection errors, co-occurrence and authorization boundaries.
- Approval before removing compatibility or conducting paid/external evaluations.

### Mandatory

- Map each required capability to a tool before adding new ones. Do not add speculative nice-to-have tools or preserve redundant aliases without a compatibility reason.
- Every tool needs a distinct operation and explicit Use for boundaries. Tool count alone does not prove bloat: 5-12, 13-20 and 20+ are review heuristics, not forced architectural caps.
- Split when responsibilities, parameters, outputs, permissions or recovery diverge. Read retries and destructive mutation recovery must not share ambiguous action switches.
- Merge only when tasks consistently use the same resource/context and combining them reduces overhead without hiding side effects or expanding authority.
- Co-occurrence, shared parameters and usage rates inform review, not automatic decisions. Measure the actual task distribution and sample size; do not present arbitrary percentages as universal acceptance thresholds.
- Keep optional capabilities discoverable/on-demand rather than loading unrelated tools into every task. Excluding a tool from a task does not grant permission to invoke it through another path.
- Version changes must update affected schemas, docs, bundled groups and downstream parsers. Test critical consumers before upgrading; pin versions when the project requires stability.

### Execution Steps

1. Inventory tools and core use cases, then identify demonstrated missing capability or selection ambiguity.
2. Review contracts/trace evidence and propose minimal changes with explicit compatibility and permission effects.
3. Split unrelated operations, or merge tightly coupled safe reads, while preserving required capability coverage.
4. Trial new tools in an isolated test configuration rather than the main set. Track successful use, wrong selection, parameter errors and unused capabilities by relevant task category.
5. Run representative usability/consumer tests; add back a removed required capability if evidence shows regression.
6. Document split/merge/promotion/removal rationale and update dependent pipelines and version bindings.

### Validation

- Required tasks remain achievable and each tool has an unambiguous purpose.
- No redundant tool adds confusion without a documented compatibility reason.
- Agent selection/parameter evidence supports changes; paid/runtime testing is distinguished from static contract review.
- Permissions, mutation/retry boundaries and state contracts remain explicit after merging or splitting.
- Downstream callers parse changed outputs and use renamed parameters correctly.
- A missing capability restores the minimal required tool, not an indiscriminate tool expansion.

## References

- [Anthropic: Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- `004-tool-design-for-agents.md` for implementation contracts.
- `004b-tool-output-efficiency.md` for output measurement and progressive loading.
