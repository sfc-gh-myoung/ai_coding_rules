# Baseline Workflow Example

## Scenario

Establish a performance baseline and compare future runs against it.

## Prerequisites

- At least 5 completed timing runs for the skill/mode/model combination
- Timing data stored in `reviews/.timing-data/`

## Step 1: Analyze Existing Data

Before setting a baseline, analyze your timing data:

```bash
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
$PYTHON skills/skill-timing/scripts/skill_timing.py analyze \
    --skill rule-reviewer \
    --model claude-sonnet-45 \
    --days 30
```

**Output:**
```
TIMING: Analysis v1.3.0
----------------------------------------
Count:       12 runs
Filters:     skill=rule-reviewer, model=claude-sonnet-45, days=30
----------------------------------------
Average:     3m 45s (225.50s)
Median:      3m 30s (210.00s)
Stddev:      45.30s
Min:         2m 15s (135.00s)
Max:         6m 20s (380.00s)
P5:          2m 20s (140.00s)
P50:         3m 30s (210.00s)
P95:         5m 45s (345.00s)
----------------------------------------
```

## Step 2: Set Baseline

Once you have enough data points, set a baseline:

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --days 30
```

**Output:**
```
Baseline set for rule-reviewer/FULL/claude-sonnet-45:
  Sample size: 12
  Average: 3m 45s (225.5s)
  Median: 3m 30s (210.0s)
  P95: 5m 45s (345.0s)
  Stddev: 45.3s
```

**Storage:** Baseline is saved to `reviews/.timing-baselines.json`

## Step 3: Run with Baseline Comparison

Future timing runs automatically compare against the baseline:

```bash
# Start timing
$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill rule-reviewer \
    --target rules/100-snowflake-core.md \
    --model claude-sonnet-45 \
    --mode FULL

# [Execute skill...]

# End timing
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/100-snowflake-core-review.md \
    --skill rule-reviewer
```

**Output with Baseline:**
```
TIMING: skill-timing v1.3.0
----------------------------------------
Run ID:      a1b2c3d4e5f67890
...
Duration:    4m 0s (240.00s)
Status:      completed
----------------------------------------
...
Baseline:    +6.4% vs avg (within normal)
----------------------------------------
```

## Step 4: Compare Specific Run

Compare a specific run against baseline:

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py baseline compare \
    --run-id a1b2c3d4e5f67890
```

**Output:**
```
Baseline Comparison for a1b2c3d4e5f67890:
  Current: 4m 0s (240.0s)
  Baseline: 3m 45s (225.5s avg)
  Delta: +14.5s (+6.4%)
  Status: within normal
```

## Baseline Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| `within_normal` | Within 1 stddev of average | Normal operation |
| `slightly_outside` | Within 2 stddev of average | Monitor for trends |
| `significantly_outside` | More than 2 stddev from average | Investigate |

## Baseline Data Structure

The baseline file (`reviews/.timing-baselines.json`) contains:

```json
{
  "rule-reviewer": {
    "FULL": {
      "claude-sonnet-45": {
        "baseline_date": "2026-01-06",
        "sample_size": 12,
        "avg_seconds": 225.5,
        "median_seconds": 210.0,
        "p95_seconds": 345.0,
        "stddev_seconds": 45.3
      }
    }
  }
}
```

## Updating Baselines

Re-run baseline set periodically to account for model changes or skill updates:

```bash
# Update baseline with recent data only
$PYTHON skills/skill-timing/scripts/skill_timing.py baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --days 7
```

## Testing with Fewer Samples

For testing, use `--min-samples` to lower the threshold:

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --min-samples 2
```
