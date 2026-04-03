# Workflow: Timing Checkpoint

## Purpose

Record an intermediate timing checkpoint for detailed analysis.

## Prerequisites

- Timing start was executed
- `run_id` is available

## Inputs

- `run_id`: From timing-start output
- `checkpoint_name`: Name of this checkpoint

## Execution

```bash
# Using wrapper script (recommended):
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id '{{run_id}}' \
    --name '{{checkpoint_name}}'

# Or direct invocation with uv (if available):
uv run python skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id '{{run_id}}' \
    --name '{{checkpoint_name}}'
```

## Predefined Checkpoint Names

- **`skill_loaded`** - After loading SKILL.md
- **`schema_validated`** - After schema validation completes
- **`target_loaded`** - After loading target file
- **`review_complete`** - After review/task execution
- **`file_written`** - After output file write

### Gate Checkpoints

These checkpoints map to the AGENTS.md bootstrap gates and provide visibility into where time is spent during rule loading and gate execution:

- **`gates_started`** - After Gate 1 foundation rule loaded (marks start of gate processing)
- **`rules_loaded`** - After Gate 3 matching rules loaded (all rule discovery and loading complete)
- **`work_started`** - After gate processing, when core skill work begins
- **`work_complete`** - After core skill work finishes (before file write)

## Error Handling

If this command fails:
1. Log warning: "Checkpoint recording failed"
2. Continue with skill execution

## File Write Requirements

**This operation:** Read-only (updates in-progress timing file in `reviews/.timing-data/`)
