# Documentation Review: {doc-name}

**Review Date:** {YYYY-MM-DD}
**Review Mode:** {FULL|FOCUSED|STALENESS}
**Model:** {model-slug}
**Reviewer Skill:** doc-reviewer v{version}
**Target:** {doc_path}

## Executive Summary

| Dimension | Raw (0-10) | Weight | Points | Max |
|-----------|------------|--------|--------|-----|
| Accuracy | {raw} | 5 | {points} | 25 |
| Completeness | {raw} | 5 | {points} | 25 |
| Clarity | {raw} | 4 | {points} | 20 |
| Structure | {raw} | 3 | {points} | 15 |
| Staleness | {raw} | 2 | {points} | 10 |
| Consistency | {raw} | 1 | {points} | 5 |
| **TOTAL** | | | **{total}** | **100** |

**Verdict:** {verdict} ({score}/100)

**Critical Dimension Overrides:** {None|Accuracy ≤4 cap|Completeness ≤4 cap|Both ≤4 cap}

## Cross-Reference Verification (Accuracy Evidence)

| Reference | Type | Location | Status |
|-----------|------|----------|--------|
| {reference} | {file/command/function} | Line {N} | {Valid|Broken|Outdated} |

**Summary:** {Valid / Total} references verified.

## Coverage Checklist (Completeness Evidence)

| Feature/Area | Required | Documented | Gap |
|--------------|----------|------------|-----|
| {feature} | {yes/no} | {yes/no} | {description} |

## Link Validation (Staleness Evidence)

| URL | Status | HTTP Code | Notes |
|-----|--------|-----------|-------|
| {url} | {OK|Broken|Redirect} | {200|404|301} | {notes} |

## Dimension Analysis

### 1. Accuracy: {raw}/10 ({points} points)

**Evidence:** Line {N} states: "{quote}"

{analysis}

### 2. Completeness: {raw}/10 ({points} points)

{analysis}

### 3. Clarity: {raw}/10 ({points} points)

{analysis}

### 4. Structure: {raw}/10 ({points} points)

{analysis}

### 5. Staleness: {raw}/10 ({points} points)

{analysis}

### 6. Consistency: {raw}/10 ({points} points)

{analysis}

## Critical Issues

1. **Line {N}:** {Issue description}

{Or: "No critical issues identified."}

## Recommendations

**P1 (Blocking):**
1. **[Line {N}]** {Specific recommendation} **Expected improvement: +X {Dimension}**

**P2 (Important):**
1. **[Lines {N-M}]** {Recommendation} **Expected improvement: +X {Dimension}**

**P3 (Nice-to-have):**
1. **[Line {N}]** {Recommendation} **Expected improvement: +X {Dimension}**

## Post-Review Checklist

- [x] All 7 rubric files read before target
- [x] All 6 verification tables created and filled
- [x] Target read line 1 to END
- [x] Non-Issues list applied
- [x] Overlap resolution applied
- [x] Cross-Reference Verification table populated
- [x] Link Validation table populated
- [x] Coverage Checklist populated
- [x] All 6 dimension scores derived from decision matrices
- [x] Recommendations prioritized with line numbers
- [x] Review written to {output_path}

## Conclusion

{doc-name} is a {quality} {doc type} scoring **{score}/100 ({verdict})**. {1-2 sentences on strengths}. {1-2 sentences on improvement areas}.

## Timing Metadata

> **Required when `timing_enabled: true`.** Include this section verbatim; Quality Gate 7 (see `workflows/review-verification.md`) rejects reviews missing this block or its Per-Dimension Timing subsection.

| Field | Value |
|-------|-------|
| Run ID | `{run_id}` |
| Skill | doc-reviewer |
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

> **Required when `timing_enabled: true`.** The table below must contain at least 6 rows
> (one per scored dimension). If timing capture fails, include the subsection with a single
> row stating `unavailable` and the failure reason, so the omission is visible rather than
> silent. See `workflows/review-verification.md` Gate 7. Mode `not-requested` is reserved
> for the explicit `timing_enabled: false` opt-out case documented in the migration guide.

| Dimension | Duration | Mode |
|-----------|----------|------|
| accuracy | {Xs} | {checkpoint\|self-report\|inline\|unavailable\|not-requested} |
| completeness | {Xs} | {checkpoint\|self-report\|inline\|unavailable\|not-requested} |
| clarity | {Xs} | {checkpoint\|self-report\|inline\|unavailable\|not-requested} |
| structure | {Xs} | {checkpoint\|self-report\|inline\|unavailable\|not-requested} |
| staleness | {Xs} | {checkpoint\|self-report\|inline\|unavailable\|not-requested} |
| consistency | {Xs} | {checkpoint\|self-report\|inline\|unavailable\|not-requested} |
| **Total (dimension work)** | **{Xs}** | - |

> **Mode key:** `checkpoint` = sequential checkpoint pairs (auto-derived via `--auto-dimension-timings`), `self-report` = parallel sub-agent epoch timestamps, `inline` = coordinator-computed, `unavailable` = timing capture failed (include reason), `not-requested` = timing explicitly disabled (`timing_enabled: false`). `-1` = dimension failed/timed out.

---

## Quality Gates (AUTO-REJECT if violated)

| Gate | Requirement |
|------|-------------|
| Minimum Size | >=2500 bytes |
| Maximum Size | <=13500 bytes |
| Line References | >=15 distinct (FULL mode) |
| Direct Quotes | >=3 with line numbers |
| Score Table | Exact column format: Dimension | Raw (0-10) | Weight | Points | Max |
| Verification Tables | Cross-Reference + Coverage + Link Validation all present |
| Per-Dimension Timing (Gate 7) | When `timing_enabled: true`, the `### Per-Dimension Timing` subsection is present with >=6 rows (or a single explicit `unavailable` row with reason). |

## Anti-Drift Protocol

**Self-check questions (ask after each review):**
- Does my Executive Summary table have exactly 6 dimension rows plus TOTAL?
- Are the column headers: `Dimension | Raw (0-10) | Weight | Points | Max`?
- Did I include Cross-Reference Verification, Coverage Checklist, and Link Validation tables?
- Do I have >=15 line references and >=3 direct quotes?
- If `timing_enabled: true`, does the output contain `### Per-Dimension Timing` with 6 rows?

If ANY answer is "no" → Re-read this template → Regenerate the review.
