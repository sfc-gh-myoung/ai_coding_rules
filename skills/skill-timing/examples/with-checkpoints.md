# Timing with Checkpoints Example

## Scenario

Time a skill execution with intermediate checkpoints to identify bottlenecks.

## Inputs

- skill_name: `rule-reviewer`
- target_file: `rules/200-python-core.md`
- model: `claude-sonnet-45`
- mode: `FULL`

## Workflow

### Step 1: Start Timing

```bash
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill rule-reviewer \
    --target rules/200-python-core.md \
    --model claude-sonnet-45 \
    --mode FULL
```

Store the `TIMING_RUN_ID` from output.

### Step 2: Record Gate Checkpoints

After completing each AGENTS.md gate, record a checkpoint:

```bash
# After Gate 1 (foundation loaded)
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name gates_started

# After Gate 3 (all rules loaded)
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name rules_loaded
```

### Step 3: Record Work Checkpoints

During skill execution:

```bash
# After skill is fully loaded and ready
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name skill_loaded

# After core work is complete (before file write)
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name work_complete

# After file is written
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name file_written
```

### Step 4: End Timing

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/200-python-core-review.md \
    --skill rule-reviewer \
    --input-tokens 15000 \
    --output-tokens 5000
```

## Expected Output

```
TIMING: skill-timing v1.3.0
----------------------------------------
Run ID:      a1b2c3d4e5f67890
Skill:       rule-reviewer
Target:      rules/200-python-core.md
Model:       claude-sonnet-45
Agent:       cortex-code
----------------------------------------
Start:       2026-01-06T10:30:00+00:00
End:         2026-01-06T10:34:30+00:00
Duration:    4m 30s (270.00s)
Status:      completed
----------------------------------------
Checkpoints:
  gates_started:  8.50s
  rules_loaded:   25.30s
  skill_loaded:   28.00s
  work_complete:  255.00s
  file_written:   268.50s
----------------------------------------
Tokens:      20,000 (15,000 in / 5,000 out)
Cost:        $0.1200
Baseline:    N/A
----------------------------------------
```

## Checkpoint Analysis

The checkpoints reveal where time is spent:

| Phase | Duration | % of Total |
|-------|----------|------------|
| Gate 1 (foundation) | 8.50s | 3.1% |
| Gate 2-3 (rule loading) | 16.80s | 6.2% |
| Skill loading | 2.70s | 1.0% |
| Core work | 227.00s | 84.1% |
| File writing | 13.50s | 5.0% |
| Post-write | 1.50s | 0.6% |

**Insight:** 84% of time is spent on core work (as expected). If gate loading is >10%, consider optimizing rule discovery.

## Predefined Checkpoint Names

| Checkpoint | When to Use |
|------------|-------------|
| `gates_started` | After Gate 1 foundation loaded |
| `rules_loaded` | After Gate 3 all rules loaded |
| `skill_loaded` | After SKILL.md fully parsed |
| `target_loaded` | After target file read |
| `schema_validated` | After schema validation |
| `work_complete` | After core task finished |
| `file_written` | After output file written |

## Timing Metadata with Checkpoints

```markdown
## Timing Metadata

| Field | Value |
|-------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Skill | rule-reviewer |
| Model | claude-sonnet-45 |
| Agent | cortex-code |
| Start (UTC) | 2026-01-06T10:30:00+00:00 |
| End (UTC) | 2026-01-06T10:34:30+00:00 |
| Duration | 4m 30s (270.00s) |
| Status | completed |
| Checkpoints | gates_started: 8.50s, rules_loaded: 25.30s, skill_loaded: 28.00s, work_complete: 255.00s, file_written: 268.50s |
| Tokens | 20,000 (15,000 in / 5,000 out) |
| Cost | $0.1200 |
| Baseline | N/A |
```

## Per-Dimension Timing

When using `--dimension-timings`, the output includes a per-dimension breakdown:

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/200-python-core-review.md \
    --skill rule-reviewer \
    --format markdown \
    --dimension-timings '[{"dimension":"actionability","duration_seconds":42.3,"mode":"checkpoint"},{"dimension":"rule_size","duration_seconds":0.1,"mode":"inline"},{"dimension":"parsability","duration_seconds":38.7,"mode":"checkpoint"}]'
```

**Result (appended to markdown):**

```markdown
### Per-Dimension Timing

| Dimension | Duration | Mode |
|-----------|----------|------|
| actionability | 42.30s | checkpoint |
| rule_size | 0.10s | inline |
| parsability | 38.70s | checkpoint |
| **Total (dimension work)** | **81.10s** | - |
```
