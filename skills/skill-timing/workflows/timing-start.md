# Workflow: Timing Start

## Purpose

Initialize timing instrumentation for skill execution measurement.

## Prerequisites

- Input validation has passed
- All required skill inputs are available

## Inputs

- `skill_name`: Name of the skill being executed
- `target_file`: Primary target file path
- `model`: Model slug being used
- `review_mode`: (optional) Mode if applicable

## Execution

Run this command and capture the `TIMING_RUN_ID` from output:

```bash
# Discover Python interpreter (once per session):
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)

# Start timing:
$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill '{{skill_name}}' \
    --target '{{target_file}}' \
    --model '{{model}}' \
    --mode '{{review_mode}}'
```

## Output

- `TIMING_RUN_ID`: Unique identifier for this timing session (capture from stdout)
- `TIMING_AGENT_ID`: Agent identifier for registry lookup

## Agent Memory Management

**Store in working memory:**
- `run_id`: For use in timing-checkpoint and timing-end
- Store alongside other skill inputs

**Recovery mechanism:**
If agent forgets `run_id`, timing-end will attempt automatic recovery from registry.

## Error Handling

If this command fails:
1. Log warning: "Timing initialization failed, continuing without timing"
2. Set `run_id` to `none`
3. Continue with skill execution

## File Write Requirements

**This operation:** Creates timing file in `reviews/.timing-data/` and updates registry

## Next Step

Proceed with skill-specific workflow.
