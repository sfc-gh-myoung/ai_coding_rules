# Parallel Execution Specifications

Detailed specifications for parallel execution mode using 6 sub-agents.

## Timeout Handling

1. **Per-dimension timeout:** 120 seconds (2 minutes)
2. **Total review timeout:** 15 minutes for parallel, 20 minutes for sequential
3. **On timeout:**
   - Mark dimension as `"status": "TIMEOUT"`
   - Assign score: 0 (treated as evaluation failure, not documentation failure)
   - Log: `"Dimension {name} timed out after {seconds}s"`
   - Continue with remaining dimensions
4. **Retry policy:** Single retry with extended timeout (180s), then sequential fallback
5. **Launch stagger:** 5 seconds between sub-agent launches to avoid API throttling

### Timeout Rationale

| Timeout | Value | Justification |
|---------|-------|---------------|
| Per-dimension | 120s | 90th percentile execution time from plan-reviewer benchmarks + 30s buffer |
| Total execution | 15min | 6 dimensions × 120s + 3min aggregation overhead |
| Retry delay | 5s | Allows rate-limit recovery without excessive wait |
| Launch stagger | 5s | Prevents API throttling on concurrent requests |

## Aggregation Result Schema

```json
{
  "review_id": "string (UUID)",
  "doc_file": "string (path)",
  "model": "string (model name)",
  "timestamp": "ISO-8601",
  "execution_mode": "parallel|sequential",
  "timing": {
    "total_ms": "number",
    "per_dimension_ms": {"dimension_name": "number"}
  },
  "dimensions": [
    {
      "name": "string",
      "raw_score": "number (0-10)",
      "weight": "number",
      "points": "number",
      "max_points": "number",
      "status": "COMPLETE|TIMEOUT|ERROR",
      "issues_found": ["object"],
      "evidence": ["string with line references"]
    }
  ],
  "total_score": "number (0-100)",
  "verdict": "EXCELLENT|GOOD|NEEDS_IMPROVEMENT|POOR|INADEQUATE",
  "critical_overrides": {"applied": "boolean", "reason": "string"},
  "recommendations": ["string"]
}
```

## Variance Tolerance

- **Acceptable variance:** +/-5 points between parallel and sequential execution
- **Warning threshold:** +/-3 points (log warning but accept)
- **Investigation trigger:** >5 points variance requires:
  1. Log all dimension-level score differences
  2. Identify dimensions with >1 point delta
  3. Check for overlap resolution inconsistencies
  4. If unresolved, flag for human review

## Cross-Reference Behavior

When evidence applies to multiple dimensions:

1. **Primary owner** (per overlap matrix) scores the evidence
2. **Secondary dimensions** may reference but NOT score:
   - Format: `"[See Accuracy #3]"` 
   - Weight: 0 points (informational only)
3. **Conflict resolution:** If two dimensions claim ownership:
   - Check `rubrics/_overlap-resolution.md` for definitive owner
   - If not listed, use priority order: Accuracy > Completeness > Clarity > Structure > Staleness > Consistency
4. **Deduplication:** Same line reference may appear in multiple dimensions' evidence lists, but contributes to score of only ONE dimension

## Citation Deduplication

1. **Line-level deduplication:** Each `line:XXX` citation appears once in the final report's "Key Evidence" section
2. **Dimension-level citations:** Dimensions may reference same lines but must use distinct quotes
3. **Aggregation rule:** When merging dimension reports:
   - Collect all citations
   - Group by line number
   - Keep longest quote per line
   - Attribute to primary owner dimension
4. **Format:** `line:123 (Accuracy): "exact quote here"`

## Anti-Optimization Protocol

Prevent agents from gaming the scoring system:

### Detection Patterns
1. **Keyword stuffing:** Repeating rubric keywords without substance
2. **Score anchoring:** Explicitly stating target scores in review
3. **Checklist mimicry:** Matching rubric structure without actual content
4. **Metric gaming:** Optimizing measurable criteria while ignoring intent

### Scoring Adjustments
- **Detected gaming:** -2 points per dimension affected
- **Severe gaming:** Automatic INADEQUATE verdict
- **Borderline cases:** Flag for human review

### Evidence Requirements
Each score must cite:
- Specific line number(s) from documentation
- Direct quote (10-50 words)
- Explanation of how quote supports score

Without all three, the score is invalid.

## Edge Cases

### File Write Conflicts
**Scenario:** Multiple sub-agents attempt to write to same output file
**Handling:**
- Each sub-agent writes to temp file: `{dimension}_worksheet.json`
- Only orchestrator writes final review file
- Temp files deleted after aggregation

### Shared Context Drift
**Scenario:** Documentation file modified during review
**Handling:**
- Capture documentation file hash at review start
- Each sub-agent receives identical snapshot
- If hash changes mid-review, abort and notify

### Memory Tool Contention
**Scenario:** Multiple sub-agents update memory simultaneously
**Handling:**
- Sub-agents are READ-ONLY for memory
- Only orchestrator updates memory after aggregation
- Sub-agents may read shared context but not write

### Result Ordering Non-Determinism
**Scenario:** Sub-agents complete in different order each run
**Handling:**
- Results keyed by dimension name, not arrival order
- Aggregation waits for all 6 before processing
- Final report orders dimensions by weight (highest first)

### Partial Failure Recovery
**Scenario:** 3 of 6 sub-agents fail, 3 succeed
**Handling:**
- Log failed dimensions with error messages
- Calculate partial score from successful dimensions
- Mark review as `"status": "PARTIAL"` 
- Include warning: "Review incomplete - {N} dimensions failed"
- Provide prorated score: `(successful_points / successful_max) * 100`

**Failure threshold:** If 3+ sub-agents fail, trigger sequential fallback

## Conflict Detection

Before aggregation, check for:

1. **Score conflicts:** Same line cited with different scores
   - Resolution: Use primary owner's score per overlap matrix
   
2. **Evidence conflicts:** Contradictory assessments of same section
   - Resolution: Flag in report, include both perspectives
   
3. **Verdict conflicts:** Dimension scores suggest different verdicts
   - Resolution: Use weighted total, note discrepancy

4. **Issue conflicts:** Same issue listed differently
   - Resolution: Deduplicate by line number, keep most specific description

## Rollback Procedure

If parallel execution fails catastrophically:

1. **Immediate:** Kill all running sub-agents
2. **Cleanup:** Delete partial temp files
3. **Log:** Record failure state to memory
4. **Fallback:** Execute sequential review as alternative
5. **Report:** Generate failure report with:
   - Which sub-agents succeeded/failed
   - Error messages
   - Partial scores if available
   - Recommendation for retry

### Fallback Trigger Conditions

| Condition | Action |
|-----------|--------|
| 1-2 sub-agents fail | Retry failed dimensions once |
| 3+ sub-agents fail | Fallback to sequential execution |
| All 6 timeout | Check network, increase timeouts, retry parallel |
| JSON parse errors > 2 | Fallback to sequential with schema reminder |
| Overlap violations > 5 | Fallback to sequential for consistent counting |

## Performance Targets

| Metric | Sequential | Parallel | Improvement |
|--------|------------|----------|-------------|
| Execution time | ~12-15 min | ~3-4 min | 3-4× faster |
| Token cost | ~12K | ~72K | 6× higher |
| Context freshness | Degraded after dim 3 | Fresh for all | Better accuracy |
| Fault tolerance | Restart from beginning | Retry single dimension | Improved |

## Dimension Weight Reference

| Dimension | Weight | Max Points | Category |
|-----------|--------|------------|----------|
| Accuracy | 5 | 25 | Critical |
| Completeness | 5 | 25 | Critical |
| Clarity | 4 | 20 | Important |
| Structure | 3 | 15 | Important |
| Staleness | 2 | 10 | Standard |
| Consistency | 1 | 5 | Standard |
| **TOTAL** | **20** | **100** | |
