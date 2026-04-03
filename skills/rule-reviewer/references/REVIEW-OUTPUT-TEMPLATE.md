# Rule Review: {rule-filename}

**Review Date:** {YYYY-MM-DD}
**Review Mode:** {FULL|FOCUSED|STALENESS}
**Model:** {model-slug}
**Reviewer Skill:** rule-reviewer v{version}
**Schema Validator:** ai-rules validate

## Executive Summary

| Dimension | Raw (0-10) | Weight | Points | Max |
|-----------|------------|--------|--------|-----|
| Actionability | {raw} | 3.0 | {points} | 30 |
| Rule Size | {raw} | 2.5 | {points} | 25 |
| Parsability | {raw} | 1.5 | {points} | 15 |
| Completeness | {raw} | 1.5 | {points} | 15 |
| Consistency | {raw} | 1.0 | {points} | 10 |
| Cross-Agent Consistency | {raw} | 0.5 | {points} | 5 |
| **TOTAL** | | **10** | **{total}** | **100** |

**Verdict:** {verdict} ({score}/100)

**Blocking Issues:** {count}
**Hard Caps Applied:** {None|description}
**Rule Size Flag:** {None|SPLIT_RECOMMENDED|SPLIT_REQUIRED|NOT_DEPLOYABLE|BLOCKED}

## Schema Validation Results

```
CRITICAL: {count}
HIGH:     {count}
MEDIUM:   {count}
Passed:   {count}
Result:   {summary}
```

{Brief explanation of any issues found}

## Agent Executability Verdict

**Blocking Issues Count: {N}**

{For each blocking issue:}
1. **{Issue type} at line {N}:** {Description} -- {Why an agent would struggle}

## Dimension Analysis

### 1. Actionability: {raw}/10 ({points} points)

**Blocking Issue Inventory:**

| # | Line | Issue | Type | Severity |
|---|------|-------|------|----------|
| {n} | {line} | {description} | {type} | {severity} |

**After Non-Issues filtering:** {adjusted count}

**Score Decision Matrix lookup:** {criteria} = {raw}/10

**Priority fixes:** (if any)
1. Line {N}: {fix}

### 2. Rule Size: {raw}/10 ({points} points)

**Line count: {N} lines**

| Metric | Value |
|--------|-------|
| Total lines | {N} |
| Threshold | {tier} |
| Flag | {None|SPLIT_RECOMMENDED|SPLIT_REQUIRED|NOT_DEPLOYABLE|BLOCKED} |

**Score Decision Matrix lookup:** {lines} lines = {raw}/10

**Token Efficiency (Informational):**
- Redundancy instances: {count}
- {specific instances with line numbers}
- Structure ratio: {percentage} lists/tables vs prose
- Estimated savings: {tokens} if consolidated

### 3. Parsability: {raw}/10 ({points} points)

**Schema Error Inventory:**

| # | Line | Error | Severity |
|---|------|-------|----------|
| {n} | {line} | {description} | {severity} |

**After Non-Issues filtering:** {adjusted count}

**Score Decision Matrix lookup:** {criteria} = {raw}/10

### 4. Completeness: {raw}/10 ({points} points)

**Coverage Inventory:**

| Category | Required | Present | Gap |
|----------|----------|---------|-----|
| {category} | {required} | {present} | {gap} |

**After Non-Issues filtering:** {adjusted count}

**Score Decision Matrix lookup:** {criteria} = {raw}/10

### 5. Consistency: {raw}/10 ({points} points)

**Contradiction Inventory:**

| # | Line A | Line B | Issue | Type |
|---|--------|--------|-------|------|
| {n} | {lineA} | {lineB} | {description} | {type} |

**After Non-Issues filtering:** {adjusted count}

**Score Decision Matrix lookup:** {criteria} = {raw}/10

### 6. Cross-Agent Consistency: {raw}/10 ({points} points)

**Compatibility Inventory:**

| # | Line | Issue | Agent Impact |
|---|------|-------|-------------|
| {n} | {line} | {description} | {impact} |

**After Non-Issues filtering:** {adjusted count}

**Score Decision Matrix lookup:** {criteria} = {raw}/10

## Critical Issues

1. **Line {N} [vs Line {M}]:** {Issue description with specific line references}

{Or: "No critical issues identified."}

## Recommendations

**P1 (Blocking):**
1. **[Line {N}]** {Specific, actionable recommendation} **Expected improvement: +X {Dimension}**

**P2 (Important):**
1. **[Lines {N-M}]** {Recommendation} **Expected improvement: +X {Dimension}**

**P3 (Nice-to-have):**
1. **[Line {N}]** {Recommendation} **Expected improvement: +X {Dimension}**

**Staleness (Informational):**
- LastUpdated: {date} ({age})
- Deprecated tools: {count}
- Broken links: {count} ({details})
- Documentation currency: {summary}

## Post-Review Checklist

- [x] Schema validator executed ({error count} errors)
- [x] Agent Execution Test performed ({blocking issue count} blocking issues)
- [x] Line count measured: {N} lines
- [x] All 6 dimensions scored
- [x] Each score has rationale with inventories
- [x] Critical issues identified ({count})
- [x] Rule Size flags: {flag or None} ({line count} lines)
- [x] Recommendations prioritized ({count} items)
- [x] Line numbers provided for all fixes
- [x] Review written to {output_path}
- [x] Review file >=2500 bytes

## Conclusion

{rule-filename} is a {quality adjective} {rule type} scoring **{score}/100 ({verdict})**. {1-2 sentences on strengths}. {1-2 sentences on improvement areas}. {size assessment}.

## Timing Metadata

> **Conditional:** Include this section only when `timing_enabled: true`.

| Field | Value |
|-------|-------|
| Run ID | `{run_id}` |
| Skill | rule-reviewer |
| Model | {model} |
| Agent | {agent or unknown} |
| Start (UTC) | {ISO 8601} |
| End (UTC) | {ISO 8601} |
| Duration | {Xm Ys (total_seconds)} |
| Status | {completed|partial} |
| Checkpoints | {checkpoint_name: Xs, ...} |
| Tokens | {count or N/A} |
| Cost | {amount or N/A} |
| Baseline | {reference or N/A} |

### Per-Dimension Timing

> **Conditional:** Include this subsection only when `_dimension_timings` data is available.

| Dimension | Duration | Mode |
|-----------|----------|------|
| actionability | {Xs} | {checkpoint\|self-report\|inline} |
| rule_size | {Xs} | {checkpoint\|self-report\|inline} |
| parsability | {Xs} | {checkpoint\|self-report\|inline} |
| completeness | {Xs} | {checkpoint\|self-report\|inline} |
| consistency | {Xs} | {checkpoint\|self-report\|inline} |
| cross_agent | {Xs} | {checkpoint\|self-report\|inline} |
| token_efficiency | {Xs} | {checkpoint\|self-report\|inline} |
| staleness | {Xs} | {checkpoint\|self-report\|inline} |
| **Total (dimension work)** | **{Xs}** | - |

> **Mode key:** `checkpoint` = sequential timing pairs, `self-report` = parallel sub-agent epoch timestamps, `inline` = coordinator-computed (Rule Size only). `-1` = dimension failed/timed out.

---

## Quality Gates (AUTO-REJECT if violated)

| Gate | Requirement |
|------|-------------|
| Minimum Size | >=2500 bytes |
| Maximum Size | <=12000 bytes |
| Line References | >=15 distinct (FULL mode) |
| Direct Quotes | >=3 with line numbers |
| Score Table | Exact column format: Dimension | Raw (0-10) | Weight | Points | Max |
| All Sections | 9 sections present (10 with Timing) |
| Checklist Items | Exactly 11 items with fixed wording |

## Anti-Drift Protocol

**MANDATORY re-read triggers:**
1. Every 5 rules processed in a batch
2. Immediately after any review with <2500 bytes (below Quality Gate minimum)
3. Before starting a new batch
4. If structural validation (Step 5a in file-write.md) fails

**Self-check questions (ask after each review):**
- Does my Executive Summary table have exactly 6 dimension rows plus TOTAL?
- Are the column headers: `Dimension | Raw (0-10) | Weight | Points | Max`?
- Did I include all 9 required H2 sections (10 with Timing)?
- Do I have >=15 line references and >=3 direct quotes?
- Does my Post-Review Checklist have exactly 11 items with fixed wording?
- Are Token Efficiency and Staleness inline (not separate H2)?

If ANY answer is "no" -> Re-read this template -> Regenerate the review.
