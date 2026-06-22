---
name: analyze-plan
description: Audits a planning document against industry best practices and discoverable project standards, emitting a remediation report with prioritized findings and recommendations. Use when reviewing a plan before execution, performing pre-implementation analysis, or comparing a draft plan against standards. Triggers on "analyze plan", "review plan", "audit plan", "plan analysis", "remediate plan".
version: 1.0.0
---

# Analyze Plan

## Purpose

Audits a planning document and produces a non-implementation remediation report. The skill grounds findings in discoverable project standards (CONTRIBUTING.md, ADRs, lint configs) and authoritative external best-practice sources, then emits a P0–P3 prioritized work plan a human or another agent can execute.

## Use this skill when

- Reviewing a plan before any implementation begins.
- Auditing an existing plan for gaps, conflicts, or missing details.
- Comparing a plan against industry best practices.
- Producing a remediation checklist a downstream skill (e.g., `execute-plan`) can consume.

Do not use for: implementing the plan, writing code, or modifying the plan file itself.

## Inputs

### Required

- `plan_file`: path — the plan document to analyze.
  - **Default construction:** Apply the plan-discovery algorithm (search `.snowflake/cortex/plans/`, `docs/plans/`, `./plans/`, repo root for `*.plan.md`; sort by mtime descending; take the most recent). Always present via `ask_user_question` with `type: "text"`, `defaultValue: <discovered-path>`. If discovery returns nothing, prefill `.snowflake/cortex/plans/<slug>.plan.md` as a placeholder.

### Optional

- `output_dir`: path (default: same directory as `plan_file`).
- `external_sources`: list of URLs (default: skill selects sources appropriate to the detected plan domain — e.g., Twelve-Factor for service deploys, MADR 4.0 for decision records, Diátaxis for docs plans).

## Outputs

Write to: `<output_dir>/<plan-stem>_<YYYYMMDD_HHMMSS>_ANALYSIS.md`

- `plan-stem` is the basename of `plan_file` without its final extension; path separators and unsafe characters replaced with hyphens.
- Timestamp uses local system time.
- **No overwrites:** if the computed filename exists, recompute the timestamp or append `-01`, `-02`.

## Workflow

### Phase 1 — Preflight

1. Resolve `plan_file` using the discovery algorithm; confirm via `ask_user_question`.
2. Verify the file exists and is readable. If missing or unreadable: stop, report the exact problem, ask whether to retry with a different path.
3. Compute the output filename. If it would overwrite an existing file, recompute.
4. Identify the plan's domain (migration, refactor, feature design, doc audit, etc.) from headings and content. Choose external sources accordingly.

### Phase 2 — Source assembly

1. Read the plan file in full.
2. Scan the workspace for discoverable project standards:
   - `CONTRIBUTING.md`, `README.md`
   - `docs/adr/` if present
   - `.editorconfig`, `commitlint.config.*`, `.markdownlint.*`
   - Language-specific configs (`pyproject.toml`, `package.json`, `Cargo.toml`, etc.)
3. For each external source, fetch authoritative content (specs, official docs). Cite versions explicitly.
4. Record every source consulted; rank by precedence: (a) plan-specific guidance, (b) project-level standards, (c) workspace-wide standards, (d) external best practices.

### Phase 3 — Analysis

For each of the following, ground every finding in a cited source:

1. **Rule-by-rule compliance** — does each section of the plan satisfy applicable standards?
2. **Design quality** — are alternatives considered, tradeoffs explicit, constraints stated?
3. **Implementation approach** — are tasks atomic, ordered, and verifiable?
4. **Plan structure and flow** — is the document navigable, internally consistent, complete?
5. **Risk surface** — what could go wrong; what is unmitigated?
6. **Validation** — does the plan specify how completion will be measured?

### Phase 4 — Recommendations

Every recommendation row must carry:

- recommendation
- target area: design / implementation / structure / flow / validation / risk / dependency
- pros
- cons
- best-practice alignment (with source)
- supporting source(s)

### Phase 5 — Write report

Write the analysis to the computed output path using the `Output Schema` below.

### Phase 6 — Completion check

- [ ] Output file written and verified on disk.
- [ ] No existing file overwritten.
- [ ] Every finding cites at least one source.
- [ ] Every recommendation has pros and cons.
- [ ] Priorities use P0–P3.
- [ ] Phase-by-phase work breakdown includes exit criteria.

## Output Schema

```markdown
# Plan Analysis: <plan-stem>

## 1. Summary

- Analysis output path
- Plan file analyzed
- Why this plan file was selected
- Project standards consulted
- External best-practice sources consulted
- Key findings (3–7 bullets)
- Assumptions and open questions

## 2. Rule-by-Rule Analysis

For each rule/source: applicable plan sections, compliance assessment, gaps,
recommended remediation, target area, pros, cons, alignment, source.

## 3. Remediation Checklist by File

For each affected file: required changes, reason, related rules, dependency
notes, target area, pros, cons, alignment, source.

## 4. Prioritized Implementation Plan

P0 (blocking) | P1 (high impact) | P2 (important, non-blocking) | P3 (polish).
Each row: task, target files, rationale, dependencies, target area, pros, cons,
alignment, source.

## 5. Phase-by-Phase Work Breakdown

Minimum phases needed for safe ordered execution. Each phase has: number + goal,
exact file edit scope, ordered tasks, validation checkpoints, exit criteria,
structure/flow recommendation, pros, cons, alignment, source.

## 6. Risks and Unresolved Items

Each row: risk/item, impact, mitigation/follow-up, target area, pros, cons,
alignment, source.

**End of analysis.**
```

## Anti-patterns

- **Implementing the plan.** This skill is analysis-only. The only file it writes is the analysis report.
- **Unsupported recommendations.** Every recommendation must cite a source; if no source supports the claim, mark it as an assumption.
- **Single-priority backlog.** Findings must distribute across P0–P3 by severity, not be flattened.
- **Vague best-practice claims.** "Industry best practice" without a cited source is not acceptable.

## Examples

**Invocation:**

> "Analyze the most recent plan in .snowflake/cortex/plans/."

**Resulting prompt:**

```
Question: Confirm plan file to analyze.
Default:  .snowflake/cortex/plans/prompts-to-skills-conversion.plan.md
```

**Output path example:**

`.snowflake/cortex/plans/prompts-to-skills-conversion_20260621_141532_ANALYSIS.md`

## References

- MADR 4.0 — Architecture Decision Records template.
- Twelve-Factor App — operational concerns for deploy plans.
- Diátaxis — documentation structure for docs plans.

## Version History

See [CHANGELOG.md](CHANGELOG.md).
