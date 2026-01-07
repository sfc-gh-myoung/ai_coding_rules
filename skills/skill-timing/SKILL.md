---
name: skill-timing
description: Measures skill execution time and tracks performance. Use when you want to time a skill, measure duration, track how long something takes, compare performance across models, analyze execution speed, or detect agent shortcuts.
version: 1.0.0
---

# Skill Timing

Timing instrumentation for skill execution measurement.

## Purpose

Enable performance measurement and analysis for skill executions:
- Wall-clock duration tracking with microsecond precision
- Intermediate checkpoint recording for bottleneck identification
- Token usage and cost estimation
- Real-time anomaly detection (shortcuts, timeouts)
- Historical baseline comparison
- Cross-model and cross-agent performance analysis

## Use this skill when

- You want to measure how long a skill takes to execute
- You need to compare performance across models or agents
- You want to identify bottlenecks in skill execution
- You need to track token consumption and costs
- You want to detect potential agent shortcuts
- You need timing metadata embedded in output files

## Detailed Instructions

This skill uses progressive disclosure with separate workflow files. Each operation below references its detailed workflow guide.

Workflow files:
- [Timing Start](workflows/timing-start.md) - Initialize timing session
- [Timing Checkpoint](workflows/timing-checkpoint.md) - Record intermediate points
- [Timing End](workflows/timing-end.md) - Finalize and compute duration

## Operations

### timing-start

Initialize timing for a skill execution.

**Workflow:** See `workflows/timing-start.md` for complete execution details and error handling.

**Inputs:**
- `skill_name`: Name of the skill being timed (required)
- `target_file`: Target file path (required)
- `model`: Model slug (required)
- `review_mode`: Review mode if applicable (default: FULL)

**Quick Reference:**
```bash
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill {{skill_name}} \
    --target {{target_file}} \
    --model {{model}} \
    --mode {{review_mode}}
```

**Output:** `TIMING_RUN_ID`, `TIMING_FILE`, `TIMING_AGENT_ID`

---

### timing-checkpoint

Record an intermediate timing checkpoint.

**Workflow:** See `workflows/timing-checkpoint.md` for predefined checkpoint names and usage guidance.

**Inputs:**
- `run_id`: Run ID from timing-start (required)
- `name`: Checkpoint name (required)

**Quick Reference:**
```bash
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id {{run_id}} \
    --name {{checkpoint_name}}
```

---

### timing-end

Finalize timing and compute duration.

**Workflow:** See `workflows/timing-end.md` for complete execution details including agent responsibilities for metadata embedding.

**Important:** This operation has two parts:
1. **Python module (PLAN safe):** Computes duration, outputs to STDOUT
2. **Agent action (ACT required):** Parses STDOUT, appends metadata to output file

**Inputs:**
- `run_id`: Run ID from timing-start (required)
- `output_file`: Path to output file (required)
- `skill_name`: Skill name for recovery (required)
- `input_tokens`: Input token count (optional)
- `output_tokens`: Output token count (optional)

**Quick Reference:**
```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id {{run_id}} \
    --output-file {{output_file}} \
    --skill {{skill_name}} \
    --input-tokens {{input_tokens}} \
    --output-tokens {{output_tokens}}
```

**Output:** STDOUT timing summary (agent must parse and embed in file)

---

### baseline set

Set a performance baseline from recent timing data.

**Inputs:**
- `skill`: Skill name (required)
- `mode`: Review mode (required)
- `model`: Model slug (required)
- `days`: Days of data to include (default: 30)

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh baseline set \
    --skill {{skill}} \
    --mode {{mode}} \
    --model {{model}} \
    --days {{days}}
```

---

### analyze

Analyze timing data across runs.

**Inputs:**
- `skill`: Filter by skill (optional)
- `model`: Filter by model (optional)
- `days`: Days of data to analyze (default: 7)
- `output`: Output file path (optional)

**Command:**
```bash
bash skills/skill-timing/scripts/run_timing.sh analyze \
    --skill {{skill}} \
    --model {{model}} \
    --days {{days}} \
    --output {{output}}
```

---

## MODE Compatibility

| Operation | PLAN Mode | ACT Mode |
|-----------|-----------|----------|
| timing-start | ✓ Safe | ✓ Safe |
| timing-checkpoint | ✓ Safe | ✓ Safe |
| timing-end (Python module) | ✓ Safe | ✓ Safe |
| timing-end (metadata embed) | ✗ Not safe | ✓ Required |
| baseline set | ✗ Not safe | ✓ Required |
| analyze | ✓ Safe | ✓ Safe |

**Note:** The Python module outputs to STDOUT only (PLAN safe). The agent must parse STDOUT and append timing metadata to the output file (ACT required).

## Error Handling

- If timing-start fails: Log warning, set run_id to 'none', continue without timing
- If timing-checkpoint fails: Log warning, continue execution
- If timing-end fails: Log warning, skill execution still succeeds
- Timing failures are NEVER fatal to skill execution

## Integration with Other Skills

Add timing to any skill by including these steps in the procedure:

```markdown
## Procedure

1. Input validation → `workflows/input-validation.md`
2. **[OPTIONAL] Timing start** → `../skill-timing/workflows/timing-start.md`
   - When: `timing_enabled: true`
   - Store `run_id` in working memory
3. [Skill-specific steps...]
4. **[OPTIONAL] Checkpoint** → `../skill-timing/workflows/timing-checkpoint.md`
5. [More steps...]
6. **[OPTIONAL] Timing end (compute)** → `../skill-timing/workflows/timing-end.md` (Step 1)
   - Outputs timing data to STDOUT (PLAN mode safe)
7. **[MODE TRANSITION: PLAN → ACT]**
8. File write → `workflows/file-write.md`
9. **[OPTIONAL] Timing end (embed)** → `../skill-timing/workflows/timing-end.md` (Step 2)
   - Agent parses STDOUT and appends metadata to file (ACT mode required)
```
