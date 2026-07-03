---
name: skill-timer
description: Measures skill execution time with microsecond precision and tracks performance baselines per skill, mode, and model. Use when timing a skill, measuring duration, comparing performance across models, analyzing execution speed, or detecting agent shortcuts. Triggers on "time this skill", "measure skill duration", "benchmark a skill", "skill performance", "detect shortcut".
version: 2.0.0
metadata:
  tags: [timing, performance, measurement, instrumentation, metrics, ci-cd]
---

# Skill Timer

Timing instrumentation for skill execution measurement with microsecond precision and anomaly detection.

## Purpose

Enable comprehensive performance measurement and analysis:

- **Wall-clock duration** — microsecond precision from start to end.
- **Checkpoints** — intermediate timing points for bottleneck analysis.
- **Token tracking** — input/output token counts with cost estimation.
- **Anomaly detection** — real-time detection of shortcuts and timeouts.
- **Baseline comparison** — compare against historical averages.
- **Cross-analysis** — performance across models, agents, and modes.

## Use this skill when

- Measuring skill execution duration.
- Comparing performance across models or agents.
- Identifying bottlenecks with checkpoints.
- Tracking token consumption and costs.
- Detecting potential agent shortcuts (suspiciously fast execution).
- Building performance baselines for CI/CD.
- Analyzing historical timing trends.

Do not use for: skills with sub-5-second expected duration, pure syntax tests, or skills that produce no file output (timing metadata needs a file to embed in).

## Quick Start

```bash
# Measure a skill execution with checkpoints
Use the skill-timer skill.

skill_name: rule-reviewer
target_file: rules/200-python-core.md
model: claude-sonnet-4-6
review_mode: FULL
timing_enabled: true
```

**Output:** Timing metadata embedded in output file with duration, checkpoints, token costs, and baseline comparison.

## Inputs

### Required (timing-start)

- `skill_name`: `string` — name of the skill being timed.
- `target_file`: `path` — target file path.
- `model`: `string` — model slug (e.g., `claude-sonnet-4-6`).

### Required (timing-end)

- `run_id`: `hex string (16 chars)` — from timing-start output.
- `output_file`: `path` — output file for metadata embedding.
- `skill_name`: `string` — skill name (for recovery if `run_id` lost).

### Optional (timing-end)

- `input_tokens`: `integer` (default: none).
- `output_tokens`: `integer` (default: none).
- `format`: `string` (default: `human`) — `human`, `json`, `markdown`, `quiet`.
- `dimension_timings`: `JSON array` (default: none) — per-dimension timing data (schema below).
- `auto_dimension_timings`: `flag` (default: off) — derive `dimension_timings` automatically from `dim_<name>_start` / `dim_<name>_end` checkpoint pairs. Explicit `dimension_timings` wins if both are supplied (with WARNING).
- `review_mode`: `string` (default: `FULL`).

### `dimension_timings` schema

| Field | Required | Type | Notes |
|---|---|---|---|
| `dimension` | Yes | string | Dimension name (e.g., `actionability`). |
| `duration_seconds` | Yes | number | Actual duration in seconds. Use `-1` for failed/unavailable. |
| `mode` | Yes | string | `checkpoint` (auto-derived), `self-report`, `self-report-flagged`, `coordinator`, `inline`, `validation-failed`, `failed`, `not-requested`. |
| `start_epoch` | No | number | Unix timestamp (fractional). |
| `end_epoch` | No | number | Unix timestamp (fractional). |
| `validation_warning` | No | string | Warning message if flagged. |
| `validation_error` | No | string | Error message if validation failed. |

**Epoch capture (IMPORTANT):** Use `python3 -c "import time; print(time.time())"` for fractional precision. Do NOT use `date +%s` (integer-only).

Validation gates applied automatically by `timing-end`:

- **Plausibility:** rejects if `end_epoch <= start_epoch` or timestamps fall outside execution window (±60s buffer).
- **Fabrication detection:** flags suspiciously round durations (exact 60s multiples ≥60s) or unusually long durations (>300s for a single dimension).
- **Outcomes:** `self-report` (passed), `self-report-flagged` (warning, accepted), `validation-failed` (rejected, duration set to -1).

## Outputs

- **Timing data:** `reviews/.timing-data/skill-timer-{run_id}-complete.json`.
- **Metadata block** appended to `output_file`: markdown table with duration, checkpoints, token costs, baseline comparison.
- **No overwrites:** each run produces a unique `run_id`; completed files never collide.

## Workflow

### 1. timing-start

Initialize timing for a skill execution.

> **Universal default (as of 2026-04-21):** local reviewer skills (rule-reviewer ≥ v2.9.0, bulk-rule-reviewer ≥ v2.4.0) treat `timing_enabled: true` as the default. When callers opt out, reviewers emit a `not-requested` row in their Per-Dimension Timing table rather than omitting the section.

```bash
PYTHON=$(bash skills/skill-timer/scripts/find_python.sh)
$PYTHON skills/skill-timer/scripts/skill_timer.py start \
    --skill rule-reviewer \
    --target rules/200-python-core.md \
    --model claude-sonnet-4-6 \
    --mode FULL
```

Output:

```
TIMING_RUN_ID=a1b2c3d4e5f67890
TIMING_FILE=reviews/.timing-data/skill-timer-a1b2c3d4e5f67890.json
TIMING_AGENT_ID=unknown-12345
```

Store `TIMING_RUN_ID` — required for checkpoint and end commands. Detailed workflow: [`workflows/timing-start.md`](workflows/timing-start.md).

### 2. timing-checkpoint

Record an intermediate timing checkpoint (optional but recommended).

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name skill_loaded
```

Output:

```
CHECKPOINT_NAME=skill_loaded
CHECKPOINT_ELAPSED=4.87s
CHECKPOINT_STATUS=recorded
```

Recommended gate-level checkpoint names: `gates_started`, `rules_loaded`, `skill_loaded`, `work_complete`. Detailed workflow: [`workflows/timing-checkpoint.md`](workflows/timing-checkpoint.md).

### 3. timing-end

Finalize timing and compute duration.

```bash
$PYTHON skills/skill-timer/scripts/skill_timer.py end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/output.md \
    --skill rule-reviewer \
    --input-tokens 50000 \
    --output-tokens 5000 \
    --format markdown \
    --dimension-timings '[{"dimension":"actionability","duration_seconds":42.3,"mode":"checkpoint"}]'
```

Markdown output (append to the output file):

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

Detailed workflow: [`workflows/timing-end.md`](workflows/timing-end.md).

### 4. Validation checkpoints (mandatory when `timing_enabled: true`)

Validate after every command; on failure, write the output without timing metadata and embed a `**Timing data unavailable**` note — never block skill execution. Full gate list and Gate 8 contract: [`workflows/validation-checkpoints.md`](workflows/validation-checkpoints.md).

### 5. Advanced operations (optional)

`baseline set` / `baseline compare` / `analyze` / `wrap` / `finalize` / `replay`. Full reference: [`workflows/advanced-operations.md`](workflows/advanced-operations.md).

## Integration Pattern

Add this step to your skill's workflow:

```markdown
### [CONDITIONAL] Timing Instrumentation

**Execute IF:** `timing_enabled: true`
**Skip IF:** `timing_enabled: false`

| When | Action | Track Variable |
|------|--------|----------------|
| Before core work | timing-start | `_timing_run_id` |
| After Gate 1 | checkpoint: gates_started | — |
| After Gate 3 | checkpoint: rules_loaded | — |
| After setup | checkpoint: skill_loaded | — |
| After core work | checkpoint: work_complete | — |
| Before file write | timing-end --format markdown | `_timing_stdout` |
| After file write | Append `_timing_stdout` to file | — |
```

**Per-Dimension Timing (optional):**

- **Sequential mode (preferred):** record `dim_{name}_start` / `dim_{name}_end` checkpoint pairs around each dimension; call `timing-end --auto-dimension-timings` to derive the array.
- **Parallel mode:** sub-agents self-report `start_epoch` / `end_epoch`; coordinator assembles and passes via `--dimension-timings`.
- **Explicit override:** `--dimension-timings` wins over `--auto-dimension-timings`.
- **Precision:** capture fractional epochs with `python3 -c "import time; print(time.time())"`.

## Working Memory Contract

When `timing_enabled: true`, the agent MUST track these variables across workflow steps:

| Variable | Source | Used In | Notes |
|---|---|---|---|
| `_timing_run_id` | timing-start STDOUT | checkpoint, end | If lost, end attempts registry recovery |
| `_timing_enabled` | input parameter | conditional checks | boolean |
| `_timing_stdout` | timing-end STDOUT | metadata embedding | full markdown table |
| `_dimension_timings` | checkpoint deltas or sub-agent JSON | timing-end `--dimension-timings` | per-dimension array |

If `_timing_run_id` is lost: `timing-end` can attempt registry recovery via `--run-id none --skill <name>`; success not guaranteed.

## File Storage

All timing data lives in `reviews/.timing-data/`:

- **In-progress:** `skill-timer-{run_id}.json` (deleted after completion).
- **Completed:** `skill-timer-{run_id}-complete.json` (persisted).
- **Registry:** `skill-timer-registry.json` (agent recovery).

Stale files (>7 days) are automatically cleaned up.

## File Write Requirements

- **Read-only:** timing-start, timing-checkpoint, timing-end computation, analyze.
- **Requires write:** timing-end metadata embedding (appends timing table to output file); baseline set (writes baseline file).

## Error Handling

Timing failures NEVER block skill execution:

- **timing-start fails:** set `run_id='none'`, skip all timing operations.
- **timing-checkpoint fails:** log warning, continue.
- **timing-end fails:** log warning; skill succeeds without timing metadata.

## Examples

- [`examples/basic-timing.md`](examples/basic-timing.md)
- [`examples/with-checkpoints.md`](examples/with-checkpoints.md)
- [`examples/baseline-workflow.md`](examples/baseline-workflow.md)
- [`examples/ci-integration.md`](examples/ci-integration.md)

## Files

```
skill-timer/
├── SKILL.md                          # This file
├── CHANGELOG.md                      # Version history
├── schemas/
│   └── timing-output.schema.json     # JSON schema for timing output
├── scripts/
│   ├── skill_timer.py                # Core CLI
│   └── find_python.sh                # Python interpreter discovery
├── workflows/
│   ├── timing-start.md               # Detailed start workflow
│   ├── timing-checkpoint.md          # Detailed checkpoint workflow
│   ├── timing-end.md                 # Detailed end workflow
│   ├── validation-checkpoints.md     # Mandatory validation gates
│   └── advanced-operations.md        # baseline / analyze / wrap / finalize / replay
├── examples/                         # See ## Examples above
└── tests/
    └── test_skill_timer.sh           # Test suite
```

## Version History

See [CHANGELOG.md](CHANGELOG.md).
