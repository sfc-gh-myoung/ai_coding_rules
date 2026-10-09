---
schema_version: v4.0
rule_version: v3.0.0
description: "Compose skills with validated intermediate plans, traceable visual extraction, worker ownership, and safe recovery from partial or uncertain results."
last_updated: 2026-09-30
keywords:
  - kw:plan-validate-execute
  - kw:orchestrator-worker composition
  - kw:visual analysis pattern
  - kw:intermediate validation scripts
  - kw:claude ab iteration
  - kw:batch failure handling
token_budget: ~1050
context_tier: Low
depends:
  required:
    - 002h-claude-code-skills.md  # Core skill authoring patterns and structure
  optional:
    - 002d-advanced-rule-patterns.md  # Advanced rule patterns (parallel to skill patterns)
---
# Advanced Skill Patterns

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**

## Scope

**What This Rule Covers:**
Choose intermediate validation, visual analysis, or worker composition when those patterns reduce a workflow's actual failure risks.

**When to Load This Rule:**
- Design a batch skill, a workflow with protected writes, or an extraction task where layout carries meaning.
- Keep simple work inline; do not add orchestration solely because a task has multiple steps.

## Contract

### Inputs and Prerequisites

- Read the skill and any worker contracts before designing composition.
- Identify source files, intended outputs, dependencies, write ownership, and authorized side effects.
- Define observable failure cases and a durable checkpoint location appropriate to the project.

### Mandatory

- Validate a proposed change set before destructive or coupled execution. Validation must reject missing targets, conflicting edits, invalid inputs, and unauthorized actions.
- Preserve the plan's source identity between validation and execution. If inputs changed, revalidate; do not apply a stale approved plan.
- Keep worker logic in the worker's documented implementation. Invoke it through the current runtime's supported mechanism; reading a skill is not proof its steps ran.
- Give each worker explicit inputs, outputs, file ownership, and stop conditions. Prevent circular composition and shared-file races.
- Record completed, failed, and partial outcomes with item identity and evidence. Keep temporary execution state in the project workbench, not the distributable skill directory.
- Continue after an item failure only when remaining items are independent and the contract permits it. Stop dependent work on an unresolved prerequisite.
- Inspect whether a non-idempotent action already took effect before retrying an uncertain result. Do not convert a missing required input into an empty successful output.
- For visual extraction, retain page/image provenance, ambiguous observations, and schema checks. Do not treat guessed layout content as verified data.

### Execution Steps

1. Choose the simplest pattern that addresses the identified risk. Reuse the existing worker instead of copying its procedure.
2. Define required inputs, output schema, and a safe validation step. Prove that an invalid disposable input fails before real writes.
3. Capture the input identity and proposed changes, then validate them. Obtain any required approval before execution.
4. Execute within the approved write scope, collecting per-item evidence. Use disjoint checkpoints for independent workers and one coordinator for combined state.
5. Verify outputs and report partial failures. Re-read changed worker contracts before resuming a later batch.

### Validation

- [ ] Intermediate validation fails on invalid or stale inputs and does not merely restate generated values.
- [ ] Each worker's actual execution and output are evidenced, not inferred from loading its instructions.
- [ ] Dependencies, write ownership, and circular-composition checks hold.
- [ ] Missing inputs, unavailable tools, and uncertain writes produce explicit blocked or failed outcomes.
- [ ] Visual results retain page provenance and distinguish observed from inferred content.
- [ ] Checkpoints accurately record completed, failed, partial, and pending work without fabricated success.

If the validator is defective, repair and revalidate before execution. If a worker contract changes, reassess compatibility and authorization. If repeated attempts do not resolve the same failure, stop under the agreed retry policy and report the specific blocker.

## References

- `002h-claude-code-skills.md`: core authoring and validation requirements.
- `002d-advanced-rule-patterns.md`: load for cross-session recovery and parallel work boundaries.

## Pattern details

For plan-validate-execute, preserve the proposed changes, validation result, source identity, and execution outcome as distinct records. A plan that parses is not necessarily valid against the target system.

For visual analysis, read images or rendered document pages with the available tool when spatial relationships matter. Compare extracted fields with the expected schema and original page. A code diff normally needs textual comparison, not screenshot analysis. Process large documents in bounded page groups without silently omitting later pages.

For worker composition, use the worker's documented interface and preserve its error result. Do not substitute a no-op function or copied pseudocode for a real call. A coordinator may aggregate partial results only if the output clearly names omissions.

For iterative skill development, evaluate representative tasks in a fresh context, record observed failures, change the smallest relevant instruction, and rerun matched tasks. Avoid assuming the author's successful session predicts behavior in a fresh one.
