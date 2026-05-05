# Timing Integration (bulk-rule-reviewer)

## Purpose

Canonical copy-paste timing block and anti-pattern guide for timed bulk
reviews. Used when `timing_enabled: true`.

## Quick Reference Block

Copy-paste this block verbatim when executing a timed bulk review. The
coordinator owns all bulk-level and per-rule checkpoints; sub-agents (parallel
mode) report back via JSON.

```bash
# --- Setup ---
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
BULK_RUN_ID=$($PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill bulk-rule-reviewer --target rules/ --model {{model}} --mode {{review_mode}})

# --- Stage checkpoints ---
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id $BULK_RUN_ID --name skill_loaded
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id $BULK_RUN_ID --name discovery_complete

# --- FOR EACH rule (MANDATORY when timing_enabled: true) ---
for rule_file in "${rule_file_paths[@]}"; do
    RULE_SLUG=$(basename "$rule_file" .md)
    $PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
        --run-id $BULK_RUN_ID --name rule_${RULE_SLUG}_start
    # ... invoke rule-reviewer for $rule_file (child run_id captures
    #     per-dimension timings in its own Timing Metadata section) ...
    $PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
        --run-id $BULK_RUN_ID --name rule_${RULE_SLUG}_end
done

# --- Remaining stages ---
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id $BULK_RUN_ID --name reviews_complete
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id $BULK_RUN_ID --name aggregation_complete
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id $BULK_RUN_ID --name summary_complete

# --- End: auto-derive per-rule durations from rule_*_start/end pairs ---
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id $BULK_RUN_ID \
    --output-file {{output_root}}/summaries/_bulk-review-{{model}}-{{date}}.md \
    --skill bulk-rule-reviewer --format markdown \
    --auto-dimension-timings
```

**Note:** `--auto-dimension-timings` derives rule-reviewer's per-DIMENSION
durations from `dim_*_start/end` pairs embedded in each review's child
run_id. Bulk-level per-RULE durations are computed by
`workflows/aggregation.md` parsing the `rule_*_start/end` checkpoints on
`$BULK_RUN_ID` (no skill-timing change needed).

## Contract

- Every rule processed MUST emit a matching `rule_${SLUG}_start` /
  `rule_${SLUG}_end` pair. Missing pairs cause the rule to be dropped from
  the Timing Breakdown and trigger a warning (see
  `workflows/per-rule-verification.md` Gate).
- `--auto-dimension-timings` forwards per-DIMENSION derivation to
  rule-reviewer's child run_ids. Bulk-level per-RULE durations are derived
  by `workflows/aggregation.md` parsing the checkpoint log on
  `$BULK_RUN_ID`; no explicit `--dimension-timings` is required at the bulk
  level.
- Sub-agents (parallel mode) MUST return their child run_ids + per-dimension
  timings per `workflows/parallel-execution.md` schema; the coordinator
  merges them into the master summary.

## Responsibility Split

- **You (coordinator)** capture: bulk run_id, `rule_*_start/end` pairs,
  child run_ids from rule-reviewer.
- **skill-timing** validates/formats and emits
  `PER_DIMENSION_STATUS={present|derived|missing}`.

Silent omission produces a summary without the Timing Breakdown section
unless the Gate in `workflows/per-rule-verification.md` catches it.

## Common Timing Mistakes (Anti-Patterns)

All patterns below assume `timing_enabled: true`. If disabled, skip the
entire timing pipeline.

### Pattern 1: Fabricated epochs

WRONG:

```bash
# ❌ Agent invents timestamps to satisfy the schema
--dimension-timings '[{"dimension":"actionability","duration_seconds":0,"start_epoch":0,"end_epoch":0}]'
```

Correct:

```bash
# ✅ Use real checkpoint pairs; let --auto-dimension-timings derive durations
$PYTHON ... checkpoint --run-id $BULK_RUN_ID --name rule_${SLUG}_start
# ... work ...
$PYTHON ... checkpoint --run-id $BULK_RUN_ID --name rule_${SLUG}_end
$PYTHON ... end --run-id $BULK_RUN_ID --auto-dimension-timings
```

### Pattern 2: Missing required fields in `dimension_timings`

WRONG:

```json
[{"dimension": "actionability", "duration_seconds": 12.4}]
```

(Missing `mode` field — skill-timing v1.5.0 strips entry with
`VALIDATION ERROR`.)

Correct:

```json
[{"dimension": "actionability", "duration_seconds": 12.4, "mode": "coordinator"}]
```

### Pattern 3: Ignored `VALIDATION ERROR` from skill-timing

WRONG: Agent sees "VALIDATION ERROR: missing `mode`" and proceeds, producing
a summary with empty `dimension_timings` array and no Timing Breakdown
section.

Correct: Treat VALIDATION ERROR as fatal for the affected rule: log warning,
add to summary Warnings subsection, re-emit checkpoint pair if recoverable,
otherwise drop that rule from the Timing Breakdown and continue.

### Pattern 4: Omitting `--dimension-timings` / `--auto-dimension-timings` at end

WRONG (for bulk):

```bash
# Bulk run emits rule_*_start/end pairs but never passes --auto-dimension-timings
# Result: Timing Breakdown section missing; per-rule durations silently lost.
$PYTHON ... end --run-id $BULK_RUN_ID --output-file ...
```

Correct:

```bash
$PYTHON ... end --run-id $BULK_RUN_ID --auto-dimension-timings --output-file ...
```

### Sub-agent implication (parallel mode)

Each sub-agent invokes rule-reviewer with `timing_enabled: true`; coordinator
merges their returned `dimension_timings` into the bulk `end` call. See
`workflows/parallel-execution.md`.
