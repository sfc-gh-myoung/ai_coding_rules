---
schema_version: v4.0
rule_version: v3.0.0
description: "Designing token-efficient tool outputs for AI agents. Covers returning only necessary information, using structured parseable formats, progressive output for large results, and avoiding verbose"
last_updated: 2026-10-06
keywords:
  - kw:tool output minimization
  - kw:progressive loading
  - kw:token-efficient responses
  - kw:silent success pattern
  - kw:metadata elimination
  - kw:agent context preservation
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 004-tool-design-for-agents.md  # Core tool design principles
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 003-context-engineering.md  # Context management and attention budgets
    - 004a-tool-set-curation.md  # Minimal viable tool sets
---
# Tool Output Token Efficiency

## Scope

**What This Rule Covers:**
Minimal complete outputs, progressive loading, pagination, large-result handling and token measurements that preserve evidence and decision quality.

**When to Load This Rule:**
When designing/optimizing tool responses or diagnosing context overflow from verbose results.

## Contract

### Inputs and Prerequisites

- Current output schema, representative payloads and downstream consumer requirements.
- Target context budget and actual tokenizer/counting API when available.
- Existing project token tooling; no new tokenizer dependency solely for rough estimation.

### Mandatory

- Trace each field to a downstream decision, then verify consumers still work when unnecessary fields are removed.
- Remove redundant boilerplate, echoed parameters and unrelated timestamps/API metadata, but retain status, provenance, resource identifiers and evidence needed for safe verification or resumption.
- Array length is not total-result count when paginated; preserve total/has-more/cursor information that distinguishes complete results from truncated output.
- Use consistent structured schemas for results/errors. Minimal output must remain complete enough to interpret failures and actual side effects.
- Measure before/after tokens with the target model tokenizer when available. tiktoken/cl100k counts for another model and word/character ratios are approximations, not actual usage.
- Treat output targets (<100 mutation tokens, <500 read tokens, <2000 search tokens, 5% context per call) as review signals, not hard limits that justify hiding essential content.
- Silent success is appropriate only when the contract reliably distinguishes completion from failure. Uncertain/partial mutations need explicit outcome and recoverable evidence.
- Prefer filters, bounded limits, field selection and summary/detail reads. Do not summarize mandatory source/rule reads as if complete.
- Never emit a single response over 50000 tokens; use pagination or an access-controlled local artifact reference. Do not upload confidential content externally to obtain a URL.

### Execution Steps

1. Map the agent's next decisions and required evidence to output fields; identify genuine redundancy.
2. Define compact consistent returns with clear success/failure, scope, completeness and cursor semantics.
3. For large text, offer line/section ranges; for result sets, paginate; for binary content, provide safe metadata and authorized retrieval rather than base64 in ordinary responses.
4. For irreducible logs/results, save locally in an established evidence location and return its actual path plus summary. Preserve full evidence; do not conceal truncation.
5. Stream long operations as bounded progress/status events and a final outcome, without flooding context with repeated logs.
6. Measure representative before/after token counts and run downstream task tests. Restore demonstrably required fields when optimization breaks interpretation or task completion.

### Validation

- Agent can complete the same authorized tasks with reduced output and no lost safety/evidence.
- Counts/cursors/status are accurate and truncation explicit; a page is never represented as the full dataset.
- Error returns identify the failure and safe remediation without secrets or irrelevant raw payloads.
- Measurements specify tokenizer/model and distinguish observed savings from estimates.
- Large-output recovery offers refinement, continuation or local full-evidence reference.
- Tests cover consumers that need provenance, total counts, partial results and uncertain mutation outcomes; absence of redundant messages is not a substitute for these tests.

## References

- [Anthropic: Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [OpenAI: tiktoken](https://github.com/openai/tiktoken)
- `004-tool-design-for-agents.md` for tool contracts and authorization.
