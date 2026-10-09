---
schema_version: v4.0
rule_version: v5.0.0
description: "Write actionable rules for investigation, multi-session state, parallel work, and coupled changes while preserving authorization and recovery boundaries."
last_updated: 2026-09-30
keywords:
  - kw:system prompt altitude
  - kw:investigation-first protocol
  - kw:multi-session workflows
  - kw:anti-pattern library structure
  - kw:parallel execution design
  - kw:goldilocks zone heuristics
token_budget: ~1150
context_tier: Medium
depends:
  required:
    - 002-rule-governance.md  # Schema requirements and standards
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 002a-rule-creation.md  # Step-by-step rule creation workflow
    - 002c-rule-optimization.md  # Token budgets and performance
    - 004-tool-design-for-agents.md  # Tool Design Altitude patterns (moved from this rule)
---
# Advanced Rule Patterns: Investigation and Complex Workflows

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when designing rules for multi-step or stateful work.

## Scope

**What This Rule Covers:**
Specify actionable instructions, state handoffs, parallel work, and recovery for tasks that need more than a basic rule scaffold.

**When to Load This Rule:**
- Design a rule for investigation, multiple sessions, parallel execution, or coupled file changes.
- For tool interfaces rather than rule prose, load `004-tool-design-for-agents.md`.

## Contract

### Inputs and Prerequisites

- Read the rule draft, its required owners, and the actual files or system facts it references.
- Identify inputs, side effects, authorization boundaries, dependencies, and observable success or failure.
- Load `002a-rule-creation.md` when the work needs a new rule scaffold.

### Mandatory

- Give concrete decision criteria without brittle keyword-only routing or invented numerical thresholds. Match procedural detail to the task's risk.
- Read referenced code, configuration, schemas, or user data before making claims. Report missing evidence rather than guessing typical contents.
- State success, failure, and safe escalation where outcomes change correctness. A safe no-op does not need a fabricated alternative action.
- Describe failure mechanisms in prose and show correct examples only. Preserve useful prohibitions without a gallery of incorrect executable code.
- Keep state proportional to interruption risk. Record completed checks, pending work, file ownership, and evidence paths in one authoritative plan or checkpoint.
- Parallelize only independent operations. Give parallel writers disjoint files and do not run competing writes to shared environments or state.
- Treat tightly coupled edits as one integration unit. Validate cross-file consistency; never claim the unit complete while a required part fails.
- Recovery must preserve unrelated and concurrent work. Do not use whole-tree Git restoration as a routine response to one failed check.

### Execution Steps

1. Investigate the actual implementation and list the dependencies between proposed actions. Independent reads may run in parallel.
2. Write task conditions, authorized actions, and verifiable outcomes. Review whether another engineer could execute them without guessing missing requirements.
3. Add a small state handoff only where interruption or multiple workers requires it. Name the sole state owner and record pending checks honestly.
4. Execute independent work concurrently only after its boundaries are known. Keep dependent work sequential and checkpoint completed evidence.
5. Review failure behavior and cross-file consistency. Validate the rule and its examples; report partial completion explicitly.

### Validation

- [ ] File and system claims are supported by inspected sources.
- [ ] Conditions guide the intended behavior without arbitrary branch counts, example quotas, or unsupported thresholds.
- [ ] Required safety, authorization, and recovery constraints remain explicit.
- [ ] State has a clear owner and contains actual results rather than presumed completion.
- [ ] Parallel work has disjoint write ownership and no unmet dependencies.
- [ ] The integrated change and rule schema pass their checks; failures and unverified claims remain visible.

For a read timeout, retry within the permitted tool budget and report incomplete evidence if still unavailable. For a missing source, request the correct path. For corrupt state, preserve the damaged artifact and recover from verified evidence; do not mark pending work complete.

## References

- `schemas/rule-schema.yml`: v4 structure and separately reviewed semantic requirements.
- [CommonMark specification](https://spec.commonmark.org/): nested fenced-code syntax.
- `002-rule-governance.md`: formatting, markers, and dependency ownership.

## Multi-session and parallel recovery

On resumption, read the checkpoint and verify source hashes or current diffs before acting on it. A checklist is evidence only when its completed entries link to executed checks. Keep temporary task state in the project's ignored workbench, not durable personal memory.

If some parallel operations fail, report successful and failed results separately. Retry only failed operations when retry is safe. Before retrying a non-idempotent write with an uncertain result, inspect whether the action already took effect. Stop dependent operations on an unresolved prerequisite; do not use an arbitrary percentage of failures as the criterion.

## Multi-File Task Patterns

For tightly coupled files, present one authorized scope, capture each beforeimage, apply the necessary edits together, and cross-validate the result. If repair cannot finish safely, restore only the task-owned changes or leave an explicit incomplete checkpoint with the user's decision.

For independent files, validate each separately and preserve successful work when another file needs revision. Do not re-request authorization for scope the user already approved. Conflicting concurrent edits require re-reading and an intent decision, not an automatic preference for one author.
