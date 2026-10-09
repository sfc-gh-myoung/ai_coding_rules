# Phase 3: Content Population

## Purpose

Replace scaffold placeholders with verified, task-specific instructions under the v4 authoring contract.

## Inputs

- The generated rule and research from discovery.
- Relevant typed keyword candidates, dependency owners, source links, and known failure modes.
- The current `schemas/rule-schema.yml` and `rules/002-rule-governance.md`.

## Outputs

A populated rule ready for structural validation and a separate semantic review. No minimum number of patterns, examples, or execution steps applies.

## Workflow

1. Fill YAML metadata. Keep schema_version v4.0, use the appropriate semantic rule version, and stamp the change date. Choose 5-11 combined typed entries using `kw:`, `ext:`, `file:`, and `dir:` only where applicable.
2. Declare every dependency needed for correct execution as required, including the foundation. A domain core is not optional when the procedure relies on it. Keep optional references task-conditioned and explain edges with YAML comments.
3. Write Scope once using What This Rule Covers and When to Load This Rule. Avoid a second Purpose, Rule Scope, or Quick Start section that repeats applicability.
4. Populate the Contract:
   - Inputs and Prerequisites names inputs, permissions, environment, and required initial state.
   - Mandatory states constraints, authorized behavior, confidentiality, and other essential safety requirements.
   - Execution Steps gives the necessary actions in dependency order with observable outcomes and relevant failure handling.
   - Validation contains one completion checklist with actual commands or checks, expected results, and limitations.
5. Retain distinct prohibitions or output requirements in optional Forbidden or Output Format subsections when useful. Do not invent content to fill them.
6. Add correct executable examples only when they resolve an ambiguity. Describe the incorrect behavior and its consequence in prose. State prerequisites and substitutions; use a longer outer fence around nested code.
7. Put References after Contract. Cite authoritative sources for external claims and state when optional local material must be read. Keep required safety instructions in the active rule or a required dependency.
8. Preview the final token estimate with `ai-rules tokens --dry-run`; update the budget deliberately. Record the estimator rather than using a line-count formula or promising measured model savings.
9. Continue to [validation](validation.md) after the manual checks below pass.

## Content review

- [ ] No unresolved scaffold placeholders remain.
- [ ] The rule has the four meaningful required Contract subsections in the v4 layout.
- [ ] Every action has sufficient inputs and an observable outcome; failed or uncertain effects have safe handling.
- [ ] Permission, confidentiality, required reads, and ownership-scoped recovery remain explicit.
- [ ] Technical constraints come from inspected sources or labeled project policy, not invented quotas.
- [ ] Examples are correct and task-relevant. No executable negative examples or duplicate completion checklist remain.
- [ ] Keywords describe real requests, required dependencies resolve, and optional links have load conditions.
- [ ] Token budget reflects the final text and is labeled as an estimate.

## Unavailable evidence

If product guidance cannot be verified, record the specific unresolved claim and avoid presenting it as fact. Preserve useful existing constraints during an update until their replacement is supported. A schema pass cannot resolve a technical uncertainty or prove that a model follows the instructions.
