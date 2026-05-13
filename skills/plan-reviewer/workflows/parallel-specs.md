# Parallel Execution Specifications

Detailed specifications for parallel execution mode using 8 sub-agents.

## Timeout Handling

1. **Per-dimension timeout:** 120 seconds (2 minutes)
2. **Total review timeout:** 15 minutes for parallel, 20 minutes for sequential
3. **On timeout:**
   - Mark dimension as `"status": "TIMEOUT"`
   - Assign score: 0 (treated as evaluation failure, not plan failure)
   - Log: `"Dimension {name} timed out after {seconds}s"`
   - Continue with remaining dimensions
4. **Retry policy:** No automatic retry; manual re-run required

## Aggregation Result Schema

```json
{
  "review_id": "string (UUID)",
  "plan_file": "string (path)",
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
      "weight": "number (max points)",
      "weighted_score": "number",
      "status": "COMPLETE|TIMEOUT|ERROR",
      "blocking_issues": ["string"],
      "evidence": ["string with line references"]
    }
  ],
  "total_score": "number (0-100)",
  "verdict": "EXCELLENT|GOOD_PLAN|NEEDS_WORK|REJECTED",
  "blocking_issue_count": "number",
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
   - Format: `"[See Executability #3]"` 
   - Weight: 0 points (informational only)
3. **Conflict resolution:** If two dimensions claim ownership:
   - Check `rubrics/_overlap-resolution.md` for definitive owner
   - If not listed, assign to higher-weighted dimension
4. **Deduplication:** Same line reference may appear in multiple dimensions' evidence lists, but contributes to score of only ONE dimension

## Citation Deduplication

1. **Line-level deduplication:** Each `line:XXX` citation appears once in the final report's "Key Evidence" section
2. **Dimension-level citations:** Dimensions may reference same lines but must use distinct quotes
3. **Aggregation rule:** When merging dimension reports:
   - Collect all citations
   - Group by line number
   - Keep longest quote per line
   - Attribute to primary owner dimension
4. **Format:** `line:123 (Executability): "exact quote here"`

## Anti-Optimization Protocol

Prevent agents from gaming the scoring system:

### Detection Patterns
1. **Keyword stuffing:** Repeating rubric keywords without substance
2. **Score anchoring:** Explicitly stating target scores in plan
3. **Checklist mimicry:** Matching rubric structure without actual content
4. **Metric gaming:** Optimizing measurable criteria while ignoring intent

### Scoring Adjustments
- **Detected gaming:** -2 points per dimension affected
- **Severe gaming:** Automatic REJECTED verdict
- **Borderline cases:** Flag for human review

### Evidence Requirements
Each score must cite:
- Specific line number(s) from plan
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
**Scenario:** Plan file modified during review
**Handling:**
- Capture plan file hash at review start
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
- Aggregation waits for all 8 before processing
- Final report orders dimensions by weight (highest first)

### Partial Failure Recovery
**Scenario:** 3 of 8 sub-agents fail, 5 succeed
**Handling:**
- Log failed dimensions with error messages
- Calculate partial score from successful dimensions
- Mark review as `"status": "PARTIAL"` 
- Include warning: "Review incomplete - {N} dimensions failed"
- Provide prorated score: `(successful_points / successful_max) * 100`

## Conflict Detection

Before aggregation, check for:

1. **Score conflicts:** Same line cited with different scores
   - Resolution: Use primary owner's score per overlap matrix
   
2. **Evidence conflicts:** Contradictory assessments of same section
   - Resolution: Flag in report, include both perspectives
   
3. **Verdict conflicts:** Dimension scores suggest different verdicts
   - Resolution: Use weighted total, note discrepancy

4. **Blocking issue conflicts:** Same issue listed differently
   - Resolution: Deduplicate by line number, keep most specific description

## Rollback Procedure

If parallel execution fails catastrophically:

1. **Immediate:** Kill all running sub-agents
2. **Cleanup:** Delete partial temp files
3. **Log:** Record failure state to memory
4. **Fallback:** Offer sequential execution as alternative
5. **Report:** Generate failure report with:
   - Which sub-agents succeeded/failed
   - Error messages
   - Partial scores if available
   - Recommendation for retry

## Sub-Agent Dimension Timing Report Schema (When `timing_enabled: true`)

Each of the 8 dimension sub-agents MUST return a single `dimension_timings`
entry for its dimension. The coordinator aggregates all 8 entries into a JSON
array and passes them to `skill_timing.py end --dimension-timings`.

### Per-Sub-Agent Entry Schema

```json
{
  "dimension": "executability",
  "start_epoch": 1713700000.123,
  "end_epoch": 1713700001.456,
  "duration_seconds": 1.333,
  "mode": "self-report"
}
```

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `dimension` | Yes | string | One of the 8 dimension names (snake_case). |
| `start_epoch` | Yes | float | Unix epoch seconds at dimension scoring start. |
| `end_epoch` | Yes | float | Unix epoch seconds at dimension scoring end. |
| `duration_seconds` | Yes | float | Must equal `end_epoch - start_epoch`. |
| `mode` | Yes | string | Always `"self-report"` for parallel sub-agents. |

### Coordinator Aggregation

1. Wait for all 8 sub-agents (respecting per-dimension timeout).
2. Collect each sub-agent's `dimension_timings` entry.
3. Validate each entry against the schema above. Reject non-conforming entries.
4. Assemble into a single JSON array preserving dimension order (by weight desc).
5. Pass to `end`:

   ```bash
   $PYTHON skills/skill-timing/scripts/skill_timing.py end \
       --run-id {{_timing_run_id}} \
       --output-file {{output_path}} \
       --skill plan-reviewer --format markdown \
       --dimension-timings "$(cat aggregated.json)"
   ```

6. If a sub-agent times out or fails, emit an `unavailable` row in the
   Per-Dimension Timing table with the reason (see Gate 7 fallback).

### Sample Aggregated Payload

```json
[
  {"dimension": "executability", "start_epoch": 1713700000.10, "end_epoch": 1713700001.45, "duration_seconds": 1.35, "mode": "self-report"},
  {"dimension": "completeness",  "start_epoch": 1713700000.11, "end_epoch": 1713700001.50, "duration_seconds": 1.39, "mode": "self-report"},
  {"dimension": "success_criteria","start_epoch": 1713700000.12,"end_epoch": 1713700001.60,"duration_seconds": 1.48, "mode": "self-report"},
  {"dimension": "scope",         "start_epoch": 1713700000.13, "end_epoch": 1713700001.30, "duration_seconds": 1.17, "mode": "self-report"},
  {"dimension": "dependencies",  "start_epoch": 1713700000.14, "end_epoch": 1713700000.90, "duration_seconds": 0.76, "mode": "self-report"},
  {"dimension": "decomposition", "start_epoch": 1713700000.15, "end_epoch": 1713700000.75, "duration_seconds": 0.60, "mode": "self-report"},
  {"dimension": "context",       "start_epoch": 1713700000.16, "end_epoch": 1713700000.70, "duration_seconds": 0.54, "mode": "self-report"},
  {"dimension": "risk_awareness","start_epoch": 1713700000.17, "end_epoch": 1713700000.65, "duration_seconds": 0.48, "mode": "self-report"}
]
```

This payload conforms to the schema in `skills/skill-timing/schemas/` and is
directly accepted by `--dimension-timings`.
