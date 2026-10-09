# Schema Validation Workflow

## Purpose

Record objective structural findings from the active v4 schema before scoring a rule. Schema validation does not verify technical accuracy or the manual authoring contract.

## Applicability

Consume `FILE_TYPE` and `SKIP_SCHEMA` from input validation. Run this workflow for rule files in FULL and FOCUSED modes. STALENESS mode may skip it. PROJECT.md uses a different structure: record `SKIPPED (project file)` rather than running the operational rule schema.

## Prerequisites

- Read the complete target rule.
- Use the project's configured Python/uv environment and current schema.
- Preserve the target: reviewing does not authorize repairs.

## Execution

1. Run `uv run --locked ai-rules validate <target_file> --json`, substituting the actual path. Capture stdout, stderr, and exit status separately.
2. Parse JSON with a JSON parser. Require a summary with the expected nonzero file count and the `failed_files` and `warning_files` collections. Missing, malformed, or truncated output is unavailable evidence, never a zero-error result.
3. Collect each returned error's severity, group, message, line, and fix from both collections. Use returned severities rather than counting decorative text markers. The current validator uses CRITICAL, HIGH, MEDIUM, and INFO, not LOW.
4. Record all CRITICAL and HIGH findings as blocking schema findings. A failed content check can still produce a completed review; it cannot be called a passing rule validation.
5. Apply [the parsability rubric](../rubrics/parsability.md) on its 0-10 raw scale and the configured 1.5 weight. Do not use the retired 1-5 calculation or invent a new cap here.
6. Populate the canonical review JSON with the executed status, diagnostics, and limitations. Follow SKILL.md's render/verify workflow rather than writing a second authoritative Markdown report.

## V4 interpretation

Check required H2 order Scope, Contract, References. Contract requires non-empty Inputs and Prerequisites, Mandatory, Execution Steps, and Validation. An empty subsection is not repaired by a sibling heading or a code-fenced example heading.

Do not penalize the absence of optional Forbidden or Output Format sections, a separate Post-Execution Checklist, an anti-pattern gallery, or a fixed number of steps. Review the single completion checklist and positive-example policy as manual authoring requirements, separately from emitted structural diagnostics.

## Failure handling

- Tool unavailable or execution timeout: preserve the actual diagnostic and mark validation unavailable. Continue other review work if possible, applying the rubric's documented manual-assessment limit.
- Nonzero exit with valid findings: report the failed rule validation, including HIGH errors. Do not classify ordinary content failure as missing tooling.
- Unexpected exit or output: report the uncertainty; do not turn absent fields into empty success collections.
- No files checked: correct the target or mark the check blocked. Exit zero alone does not prove the requested file was reviewed.

## Completion

- [ ] File-type gating is explicit and no operational-rule requirements were imposed on PROJECT.md.
- [ ] The intended rule was checked, or the unavailable check is accurately disclosed.
- [ ] Diagnostics preserve real severities and line references, including all HIGH findings.
- [ ] Scoring uses the canonical raw scale, weight, and rubric caps.
- [ ] Canonical review JSON distinguishes structural results from semantic review and unverified behavior.
