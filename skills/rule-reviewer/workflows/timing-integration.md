# Workflow: Timing Integration

Detailed timing-integration procedures for the `rule-reviewer` skill. SKILL.md carries the high-level contract; this file carries the verbatim bash, anti-patterns, and per-command validation that agents should reference when `timing_enabled: true`.

## Full Command Table

Execute ALL steps when `timing_enabled: true` (not optional once enabled):

| When | Action | Command | Track |
|------|--------|---------|-------|
| Before review | Start timing | `$PYTHON skill_timer.py start --skill rule-reviewer --target {{target_file}} --model {{model}} --mode {{review_mode}}` | Store `_timing_run_id` |
| After schema validation | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name skill_loaded` | — |
| Before EACH dimension | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name dim_{name}_start` | — |
| After EACH dimension | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name dim_{name}_end` | — |
| After scoring complete | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name review_complete` | — |
| Before file write | End timing | `$PYTHON skill_timer.py end --run-id {{_timing_run_id}} --output-file {{output_file}} --skill rule-reviewer --format markdown --auto-dimension-timings` | Store `_timing_stdout` |
| After file write | Embed | Append `_timing_stdout` to output file | — |

**Working memory contract:** Retain `_timing_run_id`, `_timing_stdout`, and `_dimension_timings` from start through embed.

**Per-dimension timing responsibility:** skill-timer **validates and formats** the timing data you pass in. **You are responsible for capturing** start/end markers (checkpoint pairs in sequential mode, or sub-agent self-reports in parallel mode) around each dimension. Use `--auto-dimension-timings` in sequential mode (preferred).

## Quick Reference: Sequential Mode (copy-paste verbatim)

```bash
PYTHON=$(bash skills/skill-timer/scripts/find_python.sh)
SCRIPT=skills/skill-timer/scripts/skill_timer.py

# 1. Start
$PYTHON $SCRIPT start --skill rule-reviewer \
    --target rules/200-python-core.md --model claude-sonnet-4-6 --mode FULL
# -> capture TIMING_RUN_ID into _timing_run_id

# 2. Bootstrap checkpoint (after setup complete)
$PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name skill_loaded

# 3. Per-dimension checkpoint pairs - MANDATORY when timing_enabled=true
# Repeat for each of the 6 scored dimensions, bracketing the ACTUAL scoring work:
for dim in actionability rule_size parsability completeness consistency cross_agent; do
    $PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name "dim_${dim}_start"
    # ... perform dimension scoring work (read rubric, fill inventory, compute score) ...
    $PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name "dim_${dim}_end"
done

# 4. Aggregate checkpoint (after all dimensions scored)
$PYTHON $SCRIPT checkpoint --run-id {{_timing_run_id}} --name review_complete

# 5. End - --auto-dimension-timings derives dimension_timings from checkpoint pairs
$PYTHON $SCRIPT end --run-id {{_timing_run_id}} \
    --output-file reviews/rule-reviews/200-python-core-claude-sonnet-4-6-2026-01-08.md \
    --skill rule-reviewer --format markdown \
    --auto-dimension-timings
# Verify: stdout contains PER_DIMENSION_STATUS=derived
```

## Parallel Mode

Sub-agents self-report `start_epoch`/`end_epoch` in JSON. Coordinator assembles the array and passes `--dimension-timings` explicitly. See `workflows/parallel-execution.md`.

## Per-Command Validation and Anti-Patterns

Marker validation (`TIMING_RUN_ID`/`CHECKPOINT_STATUS`/`PER_DIMENSION_STATUS`), the "if all timing validation fails" fallback, and the 4 timing anti-patterns (fabricated epochs, missing required fields, ignored `VALIDATION ERROR`, omitting `--auto-dimension-timings`) are the shared skill-timer mechanism — single source of truth in [`../../shared/reviewer-contract.md`](../../shared/reviewer-contract.md#timing-integration-skill-timer). This file carries only the rule-reviewer command table and copy-paste blocks above.

## Schema Reference

`dimension_timings` schema (required/optional fields, validation gates, epoch capture): see `../../skill-timer/SKILL.md`.
