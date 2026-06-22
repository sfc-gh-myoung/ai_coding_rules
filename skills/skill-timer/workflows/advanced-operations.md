# Advanced Operations

Beyond `timing-start` / `timing-checkpoint` / `timing-end`, skill-timer supports baselines and cross-run analysis.

## `baseline set`

Set a performance baseline from recent timing data (requires 5+ runs).

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-4-6 \
    --days 30
```

Output:

```
Baseline set for rule-reviewer/FULL/claude-sonnet-4-6:
  Sample size: 12
  Average: 6m 24s (384.1s)
  Median: 6m 18s (378.0s)
  P95: 7m 12s (432.0s)
  Stddev: 45.2s
```

## `baseline compare`

Compare a specific run against the baseline.

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py baseline compare \
    --run-id a1b2c3d4e5f67890
```

## `analyze`

Analyze timing data across multiple runs.

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py analyze \
    --skill rule-reviewer \
    --model claude-sonnet-4-6 \
    --days 7 \
    --format json \
    --per-dimension
```

**Output formats:** `human` (default), `json`, `csv`.

**Flags:**
- `--per-dimension` — include per-dimension timing breakdown (requires `dimension_timings` in completed data).

## `replay`

Re-run the v2.0.0 distribution validator against a completed JSON. Useful for CI gates and post-hoc audit.

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py replay \
    --fixture tests/fixtures/run_f92f9d72f408a356.json
# exit 4 when the run originally would have escalated to instrumentation_failed
```

## `wrap`

Atomic per-dimension capture; server-side end timestamp; `--evidence` ≥100 bytes.

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py wrap \
    --run-id a1b2c3d4e5f67890 \
    --dimension actionability \
    --evidence ./evidence/actionability.txt
```

## `finalize`

Server-side work-complete semantics; replaces caller-defined `review_complete` checkpoints.

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py finalize \
    --run-id a1b2c3d4e5f67890 \
    --stage pre_write \
    --review-artifact reviews/output.md
```

Stages: `pre_write` (before output file is written) and `post_write` (after).
