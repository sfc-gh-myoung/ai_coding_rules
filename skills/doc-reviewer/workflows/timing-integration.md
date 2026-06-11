# Timing Integration (doc-reviewer)

## Purpose

Canonical timing pipeline and anti-pattern guide for doc-reviewer when
`timing_enabled: true`. Requires skill-timer ≥ v1.5.0.

## When to Use

Execute this entire pipeline if `timing_enabled: true`. Skip entirely when
`timing_enabled: false` (default).

## Command Matrix

| When | Action | Command | Track |
|------|--------|---------|-------|
| Before review | Start timing | `$PYTHON skill_timer.py start --skill doc-reviewer --target {{target_file}} --model {{model}} --mode {{review_mode}}` | Store `_timing_run_id` |
| After rubrics loaded | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name skill_loaded` | — |
| Before EACH dimension | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name dim_{name}_start` | — |
| After EACH dimension | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name dim_{name}_end` | — |
| After scoring complete | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name review_complete` | — |
| Before file write | Compute | `$PYTHON skill_timer.py end --run-id {{_timing_run_id}} --output-file {{output_file}} --skill doc-reviewer --format markdown --auto-dimension-timings` | Store `_timing_stdout` |
| After file write (ACT) | Embed | Parse `_timing_stdout`, append timing metadata + Per-Dimension Timing table to output file | — |

**Working memory contract:** Retain `_timing_run_id`, `_timing_stdout`,
`_dimension_timings` from start through embed.

## Per-Dimension Checkpoint Names (MANDATORY)

One start/end pair per scored dimension:

- `dim_accuracy_start` / `dim_accuracy_end`
- `dim_completeness_start` / `dim_completeness_end`
- `dim_clarity_start` / `dim_clarity_end`
- `dim_structure_start` / `dim_structure_end`
- `dim_staleness_start` / `dim_staleness_end`
- `dim_consistency_start` / `dim_consistency_end`

On `timing-end`, pass `--auto-dimension-timings` (**preferred**) to derive the
`dimension_timings` array from captured pairs. Only assemble
`--dimension-timings` JSON manually in parallel mode.

**Failure:** Without per-dimension pairs the `### Per-Dimension Timing`
subsection is absent and the review fails post-write Quality Gate 7
(see `workflows/review-verification.md`).

## Quick Reference (sequential mode — copy-paste verbatim)

```bash
PYTHON=$(bash skills/skill-timer/scripts/find_python.sh)
SCRIPT=skills/skill-timer/scripts/skill_timer.py

# 1. Start
$PYTHON $SCRIPT start --skill doc-reviewer \
    --target README.md --model claude-sonnet-4-6 --mode FULL
# -> capture TIMING_RUN_ID into _timing_run_id

# 2. Bootstrap checkpoint (after rubrics loaded)
$PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name skill_loaded

# 3. Per-dimension checkpoint pairs — MANDATORY when timing_enabled=true
for dim in accuracy completeness clarity structure staleness consistency; do
    $PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name "dim_${dim}_start"
    # ... perform dimension scoring work (read rubric, fill table, compute score) ...
    $PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name "dim_${dim}_end"
done

# 4. Aggregate checkpoint (after all dimensions scored)
$PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name review_complete

# 5. End — --auto-dimension-timings derives dimension_timings from checkpoint pairs
$PYTHON $SCRIPT end --run-id {{_timing_run_id}} \
    --output-file reviews/doc-reviews/README-claude-sonnet-4-6-2026-01-08.md \
    --skill doc-reviewer --format markdown \
    --auto-dimension-timings
# Verify: stdout contains PER_DIMENSION_STATUS=derived
```

**Parallel mode:** Sub-agents self-report `start_epoch`/`end_epoch` in JSON.
Coordinator assembles the array and passes `--dimension-timings` JSON
explicitly. See `workflows/parallel-execution.md`. Do NOT use
`--auto-dimension-timings` in parallel mode — sub-agents run concurrently so
coordinator checkpoint pairs would double-count wall-clock time.

## Mandatory Validation After Each Command

1. **After `start`:** Output must contain `TIMING_RUN_ID=`. If missing →
   STOP, report timing failure.
2. **After `checkpoint`:** Output must contain `CHECKPOINT_STATUS=recorded`.
   If `missing` → note and continue.
3. **After `end`:** Output must NOT contain `VALIDATION ERROR`. Check
   `PER_DIMENSION_STATUS=` stdout marker:
   - `present` — explicit `--dimension-timings` accepted (parallel mode)
   - `derived` — auto-derived from checkpoint pairs (sequential mode, expected)
   - `missing` — FAIL: re-run with `--auto-dimension-timings` or document
     unavailability
4. **After file write:** Verify `## Timing Metadata` AND
   `### Per-Dimension Timing` sections exist. If missing → append from
   `_timing_stdout` or trigger Gate 7 remediation.

**If ALL timing validation fails:** Write the review WITHOUT timing metadata
and note `**Timing data unavailable** - validation failed at step N`. Never
block the review on timing failures.

## Common Timing Mistakes (Anti-Patterns)

### Anti-Pattern 1: Copy-pasting example epochs from documentation

```bash
# WRONG — Agent uses example epoch from Quick Reference instead of real timestamps
dimension_timings='[{"dimension":"accuracy","start_epoch":1743897960,"end_epoch":1743897960,"mode":"coordinator"}]'
# Result: All dimensions get identical fabricated epochs → 0s duration, validation error
```

Correct: Capture real timestamps around actual work:

```bash
start_epoch=$(python3 -c "import time; print(time.time())")
# ... perform actual dimension scoring work ...
end_epoch=$(python3 -c "import time; print(time.time())")
duration=$(python3 -c "print($end_epoch - $start_epoch)")
dimension_timings='[{"dimension":"accuracy","duration_seconds":'$duration',"mode":"self-report","start_epoch":'$start_epoch',"end_epoch":'$end_epoch'}]'
```

### Anti-Pattern 2: Missing required `duration_seconds` or `mode` field

```bash
# WRONG — Only has start/end epochs, no duration_seconds or mode
dimension_timings='[{"dimension":"accuracy","start_epoch":100,"end_epoch":120}]'
# Result: skill_timer.py rejects with "missing required fields"
```

Correct: Include all required fields (`dimension`, `duration_seconds`, `mode`):

```bash
dimension_timings='[{"dimension":"accuracy","duration_seconds":20,"mode":"self-report","start_epoch":100,"end_epoch":120}]'
```

### Anti-Pattern 3: Ignoring `VALIDATION ERROR` from timing-end

Correct: Check for errors and note in review:

```bash
output=$($PYTHON skill_timer.py end --dimension-timings "$dimension_timings" 2>&1)
if echo "$output" | grep -q "VALIDATION ERROR"; then
    echo "Per-dimension timing validation failed — aggregate timing only"
fi
```

### Anti-Pattern 4: Calling `timing-end` without a dimension-timings flag

```bash
# WRONG — dim_* checkpoints were recorded but neither flag is passed
$PYTHON skill_timer.py end --run-id X --output-file Y --skill doc-reviewer
# Result: Per-Dimension Timing section silently omitted. Review fails Quality Gate 7.
```

Correct: Always pass `--auto-dimension-timings` in sequential mode
(preferred), or assemble an explicit `--dimension-timings` JSON array in
parallel mode.

**Schema reference:** See `../skill-timer/SKILL.md` for complete
`dimension_timings` schema (required/optional fields).
