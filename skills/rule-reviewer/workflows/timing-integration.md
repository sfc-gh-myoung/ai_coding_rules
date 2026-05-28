# Workflow: Timing Integration

Detailed timing-integration procedures for the `rule-reviewer` skill. SKILL.md carries the high-level contract; this file carries the verbatim bash, anti-patterns, and per-command validation that agents should reference when `timing_enabled: true`.

## Quick Reference — Sequential Mode (copy-paste verbatim)

```bash
PYTHON=$(bash skills/skill-timer/scripts/find_python.sh)
SCRIPT=skills/skill-timer/scripts/skill_timer.py

# 1. Start
$PYTHON $SCRIPT start --skill rule-reviewer \
    --target rules/200-python-core.md --model claude-sonnet-45 --mode FULL
# -> capture TIMING_RUN_ID into _timing_run_id

# 2. Bootstrap checkpoint (after setup complete)
$PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name skill_loaded

# 3. Per-dimension checkpoint pairs — MANDATORY when timing_enabled=true
# Repeat for each of the 6 scored dimensions, bracketing the ACTUAL scoring work:
for dim in actionability rule_size parsability completeness consistency cross_agent; do
    $PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name "dim_${dim}_start"
    # ... perform dimension scoring work (read rubric, fill inventory, compute score) ...
    $PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name "dim_${dim}_end"
done

# 4. Aggregate checkpoint (after all dimensions scored)
$PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name review_complete

# 5. End — --auto-dimension-timings derives dimension_timings from checkpoint pairs
$PYTHON $SCRIPT end --run-id {{_timing_run_id}} \
    --output-file reviews/rule-reviews/200-python-core-claude-sonnet-45-2026-01-08.md \
    --skill rule-reviewer --format markdown \
    --auto-dimension-timings
# Verify: stdout contains PER_DIMENSION_STATUS=derived
```

## Parallel Mode

Sub-agents self-report `start_epoch`/`end_epoch` in JSON. Coordinator assembles the array and passes `--dimension-timings` explicitly. See `workflows/parallel-execution.md`.

## Per-Command Validation (MANDATORY)

1. **After `start`:** Output must contain `TIMING_RUN_ID=`. If missing → STOP, report timing failure.
2. **After `checkpoint`:** Output must contain `CHECKPOINT_STATUS=recorded`. If `missing` → note and continue.
3. **After `end`:** Output must NOT contain `VALIDATION ERROR`. Check `PER_DIMENSION_STATUS=` stdout marker:
   - `present` — explicit `--dimension-timings` accepted (parallel mode)
   - `derived` — auto-derived from checkpoint pairs (sequential mode, expected)
   - `missing` — FAIL: re-run with `--auto-dimension-timings` or document unavailability.
   If `VALIDATION ERROR` present → per-dimension data was auto-stripped, note "Per-dimension timing unavailable" in review. If `end` fails entirely → re-run or read `reviews/.timing-data/skill-timer-{run_id}-complete.json` directly.
4. **After file write:** Verify `## Timing Metadata` section exists in output file. If missing → append from `_timing_stdout`.

**If ALL timing validation fails:** Write the review WITHOUT timing metadata and note `**Timing data unavailable** - validation failed at step N`. Never block the review on timing failures.

## Common Timing Mistakes (Critical to Avoid)

### Anti-Pattern 1: Copy-pasting example epochs from documentation

```bash
# WRONG — Agent uses example epoch from Quick Reference instead of real timestamps
dimension_timings='[{"dimension":"actionability","start_epoch":1743897960,"end_epoch":1743897960,"mode":"coordinator"}]'
# Result: All dimensions get identical fabricated epochs → 0s duration, validation error
```

**Correct:** Capture real timestamps around actual work:

```bash
start_epoch=$(python3 -c "import time; print(time.time())")
# ... perform actual dimension scoring work ...
end_epoch=$(python3 -c "import time; print(time.time())")
duration=$(python3 -c "print($end_epoch - $start_epoch)")

dimension_timings='[{"dimension":"actionability","duration_seconds":'$duration',"mode":"self-report","start_epoch":'$start_epoch',"end_epoch":'$end_epoch'}]'
```

### Anti-Pattern 2: Missing required `duration_seconds` or `mode` field

```bash
# WRONG — Only has start/end epochs, no duration_seconds or mode
dimension_timings='[{"dimension":"actionability","start_epoch":100,"end_epoch":120}]'
# Result: skill_timer.py rejects with "missing required fields"
```

**Correct:** Include all required fields (`dimension`, `duration_seconds`, `mode`):

```bash
dimension_timings='[{"dimension":"actionability","duration_seconds":20,"mode":"self-report","start_epoch":100,"end_epoch":120}]'
```

### Anti-Pattern 3: Ignoring `VALIDATION ERROR` from timing-end

```bash
# WRONG — Agent sees VALIDATION ERROR but proceeds without noting it
output=$($PYTHON skill_timer.py end --dimension-timings "$dimension_timings" 2>&1)
# Output contains: "VALIDATION ERROR: dimension_timings[0] missing required fields"
# Agent ignores error and doesn't note timing failure in review
```

**Correct:** Check for errors and note in review:

```bash
output=$($PYTHON skill_timer.py end --dimension-timings "$dimension_timings" 2>&1)

if echo "$output" | grep -q "VALIDATION ERROR"; then
    echo "Per-dimension timing validation failed — aggregate timing only"
    # Note in review: "Per-dimension timing unavailable — validation failed"
fi
```

### Anti-Pattern 4: Calling `timing-end` without `--auto-dimension-timings` (or `--dimension-timings`)

```bash
# WRONG — dim_* checkpoints were recorded but neither flag is passed
$PYTHON skill_timer.py end --run-id X --output-file Y --skill rule-reviewer
# Result: Per-Dimension Timing section silently omitted. Stderr WARNING is easy to miss.
#         Stdout shows PER_DIMENSION_STATUS=missing. Review fails Quality Gate 7.
```

**Correct:** Always pass `--auto-dimension-timings` in sequential mode (preferred), or assemble an explicit `--dimension-timings` JSON array in parallel mode:

```bash
# Sequential (auto-derive from dim_*_start / dim_*_end checkpoints)
$PYTHON skill_timer.py end --run-id X --output-file Y --skill rule-reviewer \
    --auto-dimension-timings

# Parallel (explicit JSON from sub-agent self-reports)
$PYTHON skill_timer.py end --run-id X --output-file Y --skill rule-reviewer \
    --dimension-timings "$dimension_timings_json"
```

## Schema Reference

`dimension_timings` schema (required/optional fields, validation gates, epoch capture): see `../../skill-timer/SKILL.md`.
