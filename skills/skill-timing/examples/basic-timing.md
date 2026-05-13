# Basic Timing Example

## Scenario

Time a rule-reviewer skill execution on a single file with minimal configuration.

## Inputs

- skill_name: `rule-reviewer`
- target_file: `rules/100-snowflake-core.md`
- model: `claude-sonnet-45`

## Workflow

### Step 1: Start Timing

```bash
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill rule-reviewer \
    --target rules/100-snowflake-core.md \
    --model claude-sonnet-45
```

**Output:**
```
TIMING_RUN_ID=a1b2c3d4e5f67890
TIMING_FILE=reviews/.timing-data/skill-timing-a1b2c3d4e5f67890.json
TIMING_AGENT_ID=cortex-code-12345
```

**Agent Action:** Store `TIMING_RUN_ID` in working memory for later use.

### Step 2: Execute Skill

Run the target skill (rule-reviewer in this case). The skill execution happens between timing-start and timing-end.

### Step 3: End Timing

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/100-snowflake-core-review.md \
    --skill rule-reviewer
```

**Output:**
```
TIMING_DURATION=3m 45s (225.50s)
TIMING_START=2026-01-06T10:30:00+00:00
TIMING_END=2026-01-06T10:33:45+00:00
TIMING_STATUS=completed

TIMING: skill-timing v1.5.0
----------------------------------------
Run ID:      a1b2c3d4e5f67890
Skill:       rule-reviewer
Target:      rules/100-snowflake-core.md
Model:       claude-sonnet-45
Agent:       cortex-code
----------------------------------------
Start:       2026-01-06T10:30:00+00:00
End:         2026-01-06T10:33:45+00:00
Duration:    3m 45s (225.50s)
Status:      completed
----------------------------------------
Tokens:      N/A
Cost:        N/A
Baseline:    N/A
    Tip: Set baseline after 5+ runs with: baseline set --skill <name> --mode <mode> --model <model>
----------------------------------------
```

### Step 4: Embed Timing Metadata

Append the STDOUT from Step 3 directly to the output file (when using `--format markdown`, output is ready for direct embedding):

```markdown
## Timing Metadata

| Field | Value |
|-------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Skill | rule-reviewer |
| Model | claude-sonnet-45 |
| Agent | cortex-code |
| Start (UTC) | 2026-01-06T10:30:00+00:00 |
| End (UTC) | 2026-01-06T10:33:45+00:00 |
| Duration | 3m 45s (225.50s) |
| Status | completed |
| Checkpoints | N/A |
| Tokens | N/A |
| Cost | N/A |
| Baseline | N/A |
```

### Step 5: Verify

Check that timing metadata exists in the output file:

```bash
grep -q "## Timing Metadata" reviews/100-snowflake-core-review.md && echo "Success"
```

## Expected Artifacts

| Location | Description |
|----------|-------------|
| Output file | Contains `## Timing Metadata` section |
| `reviews/.timing-data/skill-timing-{run_id}-complete.json` | Persistent timing data |

## Common Issues

**Issue:** Agent forgets run_id between steps

**Solution:** Use `--run-id none` to trigger automatic recovery from registry.
