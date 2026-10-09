# with-wrap example (v2.0.0+)

Atomic per-dimension capture using the `wrap` subcommand. Replaces the
legacy `dim_<name>_start` / `dim_<name>_end` checkpoint pattern.

```bash
SCRIPT=skills/skill-timer/scripts/skill_timer.py

# Start
RUN_ID=$(python $SCRIPT start --skill rule-reviewer \
    --target rules/example-rule.md --model claude-opus-4 --mode FULL \
    | grep -oE 'TIMING_RUN_ID=[a-f0-9]+' | cut -d= -f2)

python $SCRIPT checkpoint --run-id $RUN_ID --name skill_loaded

# Per-dimension wraps (each requires evidence >=100B by default)
for DIM in actionability rule_size parsability completeness consistency cross_agent; do
    # ... do real analysis, materialize worksheet at /tmp/${DIM}.md ...
    python $SCRIPT wrap --run-id $RUN_ID --dimension $DIM --evidence /tmp/${DIM}.md
done

# Finalize stages bracket the file-write cost
python $SCRIPT finalize --run-id $RUN_ID --stage pre_write \
    --review-artifact reviews/example-review.md

# ... actual file write ...

python $SCRIPT finalize --run-id $RUN_ID --stage post_write

# End
python $SCRIPT end --run-id $RUN_ID --output-file reviews/example-review.md \
    --skill rule-reviewer --format json
```

## Expected output shape (excerpt)

```json
{
  "run_id": "...",
  "status": "completed",
  "alerts": [],
  "clock_source": "monotonic",
  "duration_seconds_monotonic": 312.418,
  "work_window_seconds": 198.41,
  "work_window_source": "skill_loaded_to_finalize_pre_write",
  "finalize": {
    "pre_write_epoch": 1779022114.43,
    "post_write_epoch": 1779022114.97,
    "review_artifact": "reviews/example-review.md"
  },
  "dimension_timings": [
    {
      "dimension": "executability",
      "duration_seconds": 12.83,
      "mode": "wrap",
      "evidence_bytes": 4137,
      "validation_status": "valid",
      "clock_source": "monotonic"
    }
    /* ... */
  ]
}
```

## Adversarial example (status=instrumentation_failed)

If `wrap` is called back-to-back with tiny evidence (or test fixtures emit
sub-second uniform durations), the distribution validator escalates:

```json
{
  "status": "instrumentation_failed",
  "alerts": [
    {"type": "dim_uniformity_suspect", "severity": "warning", "...": "..."},
    {"type": "dim_floor_violation", "severity": "warning", "...": "..."},
    {"type": "dim_coverage_severe", "severity": "error", "...": "..."}
  ],
  "dimension_timings_rejected": [/* moved aside, not in dimension_timings */]
}
```

Exit code: **4** (`EXIT_INSTRUMENTATION_FAILED`).
