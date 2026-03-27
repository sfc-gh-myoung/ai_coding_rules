---
name: skill-timing
description: Measures skill execution time and tracks performance. Use when you want to time a skill, measure duration, track how long something takes, compare performance across models, analyze execution speed, or detect agent shortcuts.
version: 1.4.0
tags: [timing, performance, measurement, instrumentation, metrics, ci-cd]
---

# Skill Timing

Timing instrumentation for skill execution measurement with microsecond precision and anomaly detection.

## Quick Start

```bash
# Measure a skill execution with checkpoints
Use the skill-timing skill.

skill_name: rule-reviewer
target_file: rules/200-python-core.md
model: claude-sonnet-45
review_mode: FULL
timing_enabled: true
```

**Output:** Timing metadata embedded in output file with duration, checkpoints, token costs, and baseline comparison.

## When to Use

✅ **Use this skill when:**
- Measuring skill execution duration
- Comparing performance across models or agents
- Identifying bottlenecks with checkpoints
- Tracking token consumption and costs
- Detecting potential agent shortcuts (suspiciously fast execution)
- Building performance baselines for CI/CD
- Analyzing historical timing trends

❌ **Don't use this skill when:**
- The skill execution is trivial (<5 seconds expected)
- You're just testing syntax (not measuring actual performance)
- The skill doesn't produce a file output (timing metadata needs a file to embed in)

## Purpose

Enable comprehensive performance measurement and analysis:
- **Wall-clock duration** - Microsecond precision from start to end
- **Checkpoints** - Intermediate timing points for bottleneck analysis
- **Token tracking** - Input/output token counts with cost estimation
- **Anomaly detection** - Real-time detection of shortcuts and timeouts
- **Baseline comparison** - Compare against historical averages
- **Cross-analysis** - Performance across models, agents, and modes

## Core Operations

### 1. timing-start

Initialize timing for a skill execution.

**Required inputs:**
- `skill_name` - Name of the skill being timed
- `target_file` - Target file path
- `model` - Model slug (e.g., claude-sonnet-45)
- `review_mode` - Review mode if applicable (default: FULL)

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill rule-reviewer \
    --target rules/200-python-core.md \
    --model claude-sonnet-45 \
    --mode FULL
```

**Output:**
```
TIMING_RUN_ID=a1b2c3d4e5f67890
TIMING_FILE=reviews/.timing-data/skill-timing-a1b2c3d4e5f67890.json
TIMING_AGENT_ID=unknown-12345
```

**Store `TIMING_RUN_ID` - you'll need it for checkpoint and end commands.**

**Detailed workflow:** See [`workflows/timing-start.md`](workflows/timing-start.md)

### 2. timing-checkpoint

Record an intermediate timing checkpoint (optional but recommended).

**Required inputs:**
- `run_id` - Run ID from timing-start
- `name` - Checkpoint name (e.g., skill_loaded, gates_started, rules_loaded, work_complete)

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name skill_loaded
```

**Output:**
```
CHECKPOINT_NAME=skill_loaded
CHECKPOINT_ELAPSED=4.87s
CHECKPOINT_STATUS=recorded
```

**Gate-level checkpoints** are recommended for tracking bootstrap overhead:
- `gates_started` - After Gate 1 (foundation loaded)
- `rules_loaded` - After Gate 3 (rules loaded)
- `skill_loaded` - After full setup complete
- `work_complete` - After core work finished

**Detailed workflow:** See [`workflows/timing-checkpoint.md`](workflows/timing-checkpoint.md)

### 3. timing-end

Finalize timing and compute duration.

**Required inputs:**
- `run_id` - Run ID from timing-start
- `output_file` - Path to output file (for metadata embedding)
- `skill_name` - Skill name (for recovery if run_id is lost)

**Optional inputs:**
- `input_tokens` - Input token count
- `output_tokens` - Output token count
- `format` - Output format: `human` (default), `json`, `markdown`, `quiet`
- `dimension_timings` - JSON array of per-dimension timing data

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/output.md \
    --skill rule-reviewer \
    --input-tokens 50000 \
    --output-tokens 5000 \
    --format markdown \
    --dimension-timings '[{"dimension":"actionability","duration_seconds":42.3,"mode":"checkpoint"}]'
```

**Output (markdown format):**
```markdown
## Timing Metadata

| Field | Value |
|-------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Skill | rule-reviewer |
| Duration | 6m 24s (384.49s) |
| Status | completed |
| Checkpoints | skill_loaded: 31.73s, review_complete: 358.71s |
| Tokens | 55,000 (50,000 in / 5,000 out) |
| Cost | $0.2250 |
```

**IMPORTANT:** You must append this output to the output file.

**Detailed workflow:** See [`workflows/timing-end.md`](workflows/timing-end.md)

## Validation Checkpoints (Mandatory)

When `timing_enabled: true`, validate after EACH command:

1. **After `start`:** Verify output contains `TIMING_RUN_ID=`. If missing → STOP, report failure.
2. **After `checkpoint`:** Verify output contains `CHECKPOINT_STATUS=recorded`. If `missing` → in-progress file lost, continue but note.
3. **After `end`:** Verify output does NOT contain `WARNING` or `TIMING_STATUS=missing`. If failed:
   - Re-run `end --format markdown` (may recover from completed file)
   - Last resort: Read `reviews/.timing-data/skill-timing-{run_id}-complete.json` directly
4. **After file write:** Verify `## Timing Metadata` section exists in output file. If missing → append it.

**If validation fails:** Never block the skill execution. Write output WITHOUT timing metadata and note: `**Timing data unavailable** - validation failed at step N`.

## Advanced Operations

### baseline set

Set a performance baseline from recent timing data (requires 5+ runs).

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --days 30
```

**Output:**
```
Baseline set for rule-reviewer/FULL/claude-sonnet-45:
  Sample size: 12
  Average: 6m 24s (384.1s)
  Median: 6m 18s (378.0s)
  P95: 7m 12s (432.0s)
  Stddev: 45.2s
```

### baseline compare

Compare a specific run against the baseline.

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh baseline compare \
    --run-id a1b2c3d4e5f67890
```

### analyze

Analyze timing data across multiple runs.

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh analyze \
    --skill rule-reviewer \
    --model claude-sonnet-45 \
    --days 7 \
    --format json \
    --per-dimension
```

**Output formats:** `human` (default), `json`, `csv`

**Flags:**
- `--per-dimension` - Include per-dimension timing breakdown (requires `dimension_timings` in completed data)

## Integration Pattern

**Add this step to your skill's workflow:**

```markdown
### [CONDITIONAL] Timing Instrumentation

**Execute IF:** `timing_enabled: true`
**Skip IF:** `timing_enabled: false` (default)

**When enabled, execute ALL steps:**

| When | Action | Track Variable |
|------|--------|----------------|
| Before core work | timing-start | `_timing_run_id` |
| After Gate 1 | checkpoint: gates_started | - |
| After Gate 3 | checkpoint: rules_loaded | - |
| After setup | checkpoint: skill_loaded | - |
| After core work | checkpoint: work_complete | - |
| Before file write | timing-end --format markdown | `_timing_stdout` |
| After file write | Append `_timing_stdout` to file | - |

**Per-Dimension Timing (optional):**

When the skill evaluates multiple dimensions (e.g., rule-reviewer):
- **Sequential mode:** Use checkpoint pairs (`dim_{name}_start` / `dim_{name}_end`) around each dimension
- **Parallel mode:** Sub-agents self-report `start_epoch` / `end_epoch` in their JSON output
- Pass collected timings to `timing-end` via `--dimension-timings` JSON flag

**Validation:** Verify `## Timing Metadata` exists in output file.
```

## Working Memory Contract

**CRITICAL:** When `timing_enabled: true`, the agent MUST track these variables across workflow steps:

| Variable | Source | Used In | Notes |
|----------|--------|---------|-------|
| `_timing_run_id` | timing-start STDOUT | checkpoint, end | If lost, end attempts registry recovery |
| `_timing_enabled` | Input parameter | Conditional checks | Boolean flag |
| `_timing_stdout` | timing-end STDOUT | Metadata embedding | Full markdown table |
| `_dimension_timings` | Checkpoint deltas or sub-agent JSON | timing-end `--dimension-timings` | Per-dimension timing array |

**If agent loses `_timing_run_id`:** timing-end can attempt recovery from registry using `--run-id none --skill <name>`, but may fail.

## File Storage

All timing data is stored in `reviews/.timing-data/`:
- **In-progress files:** `skill-timing-{run_id}.json` (deleted after completion)
- **Completed files:** `skill-timing-{run_id}-complete.json` (persisted)
- **Registry:** `skill-timing-registry.json` (for agent recovery)

Stale files (>7 days) are automatically cleaned up.

## File Write Requirements

**Read-only operations:**
- timing-start ✅
- timing-checkpoint ✅
- timing-end (computation) ✅
- analyze ✅

**Requires file write permissions:**
- timing-end (metadata embedding) - Appends timing table to output file
- baseline set - Writes/updates baseline file

## Error Handling

Timing failures are NEVER fatal to skill execution:

- **timing-start fails:** Set `run_id='none'`, skip all timing operations
- **timing-checkpoint fails:** Log warning, continue
- **timing-end fails:** Log warning, skill succeeds without timing metadata

## Examples

### Basic Timing
See [`examples/basic-timing.md`](examples/basic-timing.md)

### With Checkpoints
See [`examples/with-checkpoints.md`](examples/with-checkpoints.md)

### Baseline Workflow
See [`examples/baseline-workflow.md`](examples/baseline-workflow.md)

### CI Integration
See [`examples/ci-integration.md`](examples/ci-integration.md)

## Files

```
skill-timing/
├── SKILL.md                          # This file
├── CHANGELOG.md                      # Version history and changes
├── VALIDATION.md                     # Schema validation rules
└── schemas/
    └── timing-output.schema.json    # JSON schema for timing output
├── scripts/
│   ├── skill_timing.py              # Core CLI (v1.4.0)
│   └── run_timing.sh                # Wrapper script
├── workflows/
│   ├── timing-start.md              # Detailed start workflow
│   ├── timing-checkpoint.md         # Detailed checkpoint workflow
│   └── timing-end.md                # Detailed end workflow
├── examples/
│   ├── basic-timing.md              # Simple example
│   ├── with-checkpoints.md          # Checkpoint example
│   ├── baseline-workflow.md         # Baseline usage
│   └── ci-integration.md            # CI/CD integration
└── tests/
    └── test_skill_timing.sh         # Test suite (23 tests)
```
