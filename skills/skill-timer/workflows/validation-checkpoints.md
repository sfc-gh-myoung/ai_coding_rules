# Validation Checkpoints (Mandatory when `timing_enabled: true`)

Validate after EACH command issued during a timed run. If validation fails, never block the skill execution — write output WITHOUT timing metadata and note: `**Timing data unavailable** - validation failed at step N`.

## After `timing-start`

Verify stdout contains `TIMING_RUN_ID=`. If missing: STOP, report failure.

## After `timing-checkpoint`

Verify stdout contains `CHECKPOINT_STATUS=recorded`. If `CHECKPOINT_STATUS=missing` — in-progress file lost, continue but note in agent working memory.

## After `timing-end`

1. Check stderr for `VALIDATION ERROR`. If present, per-dimension timing data was invalid and has been stripped; only aggregate timing remains.
2. Check `PER_DIMENSION_STATUS=` marker in stdout. Valid values:
   - `present` — explicit data accepted via `--dimension-timings`.
   - `derived` — auto-derived from `dim_<name>_start` / `dim_<name>_end` checkpoint pairs.
   - `missing` — no data supplied or derivable.
3. If `TIMING_STATUS=missing` or no output:
   - Re-run `end --format markdown` (may recover from completed file).
   - Last resort: read `reviews/.timing-data/skill-timer-{run_id}-complete.json` directly.

## After file write

Verify `## Timing Metadata` section exists in output file. If missing: append it.

## Gate 8 — Per-Dimension Timing rejection (v2.0.0+)

When `skill_timer.py end` returns `status ∈ {dimension_invalid, instrumentation_failed}`: **do not publish** the "Per-Dimension Timing" markdown table. Emit a banner pointing at `reviews/.timing-data/skill-timer-{run_id}-complete.json` instead. This contract is mirrored verbatim in plan-reviewer, rule-reviewer, doc-reviewer, and bulk-rule-reviewer.

## Failure handling

If any validation gate fails: write the output file WITHOUT timing metadata and embed the note:

```markdown
**Timing data unavailable** — validation failed at step N.
```

Timing failures never block skill execution.
