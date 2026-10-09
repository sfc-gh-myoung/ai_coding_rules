---
schema_version: v4.0
rule_version: v5.0.0
description: "Comprehensive tool design practices that maximize agent effectiveness. Covers single responsibility, token-efficient outputs, LLM-friendly parameters, clear contracts, minimal tool overlap,"
last_updated: 2026-10-06
keywords:
  - kw:agent tool design
  - kw:single responsibility tools
  - kw:token-efficient outputs
  - kw:LLM-friendly parameters
  - kw:tool boundary overlap
  - kw:actionable error messages
token_budget: ~1300
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 003-context-engineering.md  # Context management and attention budgets
  optional:
    - 002g-agent-optimization.md  # Agent-first design principles
    - 004a-tool-set-curation.md  # Minimal viable tool sets, when to split/merge tools
    - 004b-tool-output-efficiency.md  # Token-efficient tool output design
---
# Tool Design for AI Agents

## Scope

**What This Rule Covers:**
Agent-facing tool contracts, unambiguous boundaries, validated parameters, efficient outputs, explicit state, actionable failures and usability testing.

**When to Load This Rule:**
When implementing or evaluating agent tools, their schemas, outputs, permissions or tool-set overlap.

## Contract

### Inputs and Prerequisites

- Existing tool inventory, intended users/tasks, framework and authorization boundaries.
- Context/output budgets and representative safe test inputs; a testing harness and tokenizer when available.
- Required context-engineering guidance read; language rule loaded before implementation.

### Mandatory

- Review existing tools before adding one. Give each tool a clear operation and descriptive verb-noun name; all parameters must serve that operation. Avoid vague mode switches or overlapping tools with indistinguishable purposes.
- Document purpose, each parameter's type/meaning/constraints, exact accepted enums, return schema, errors, side effects and authorization requirements. Examples must match the implementation.
- Prefer semantic parameters over opaque integer codes or undocumented flags. Validate types, bounds, dates, empty/null values and scope before any side effect.
- Separate tool availability from permission. Enforce per-call path/resource/operation scope, including nested calls. A rejected call remains observable; do not convert denied attempts into successful execution.
- Return enough structured information for the next decision: results, meaningful status, truncation/completeness and pagination cursor. Do not omit provenance or identifiers needed for verification merely to save tokens.
- Make large outputs progressive with filters, bounded limits and detail reads. Measure tokens on representative outputs; avoid arbitrary metadata-percentage targets that make small errors impossible to explain.
- Prefer stateless parameters/cursors. Explicit stateful sessions are allowed only when state, lifetime, side effects and inspection/recovery behavior are documented. Never depend on the agent remembering hidden state after compaction.
- Report what failed, why when established, the safe relevant input/location and a concrete correction. Redact credentials/confidential payloads; do not attach arbitrary raw outputs to external systems.
- Distinguish attempted, dispatched, completed and verified actions. Do not claim tool behavior from typical API patterns without inspecting/tests.
- Retry only when authorized and safe: bounded retries/backoff for idempotent reads with confirmed outcome; inspect uncertain mutations first. Do not replay non-idempotent or denied operations through another tool.

### Execution Steps

1. Inspect current contracts/implementations and identify the actual task gap or overlap.
2. Define one operation, meaningful parameters, exact allowed values and validated output/error schemas.
3. Implement fail-closed authorization and validation before dispatch; document mutation and session behavior.
4. Return bounded, decision-useful structured output with explicit cursor/completeness and actionable failures.
5. Test valid inputs and invalid types, nulls, boundaries, unauthorized scope, nested calls, pagination, uncertain outcomes and state reset. Use mocks for destructive operations rather than executing documented examples.
6. With approval for paid/external testing, evaluate actual agent discovery, parameter selection, output interpretation and recovery. Capture failures, not selected successful retries; measure output tokens and selection errors.
7. Refine demonstrated ambiguities, document distinct use cases and rerun affected tests before declaring the tool usable.

### Validation

- A developer can select the intended tool and explain its single operation without ambiguous alternatives.
- Parameter schema, exact enums and contract agree with implementation; invalid inputs fail before side effects.
- Returns expose accurate status, necessary evidence, completeness and resumption state without irrelevant boilerplate.
- Hidden state is absent or explicitly inspectable with a documented lifetime; reset/resume tests pass.
- Unauthorized direct/nested calls are rejected and recorded; permissions cannot be bypassed through fallback tools.
- Errors are specific and safe, including timeouts and missing resources; no secret or unnecessary confidential content is leaked.
- Retry/recovery tests prove bounded safe behavior. Tool unavailability is disclosed; manual equivalents require the same authorization.
- Actual agent usability testing is reported separately from unit tests and from unavailable runtime verification. Repeated wrong parameters or tool choices drive contract fixes, not guesses.

## References

- [Anthropic: Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: Tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [OpenAI: Function calling](https://platform.openai.com/docs/guides/function-calling)
- `004a-tool-set-curation.md` for when to split or merge tools.
- `004b-tool-output-efficiency.md` for progressive outputs and token measurements.
