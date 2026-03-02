# Skill Timing

A performance measurement tool for Claude Code skills that tracks execution time, token usage, and costs. Use it to identify bottlenecks, detect agent shortcuts, compare model performance, and integrate timing checks into CI/CD pipelines.

## Features

- **Wall-clock timing** - Measure end-to-end skill execution duration
- **Checkpoints** - Record intermediate timing points for bottleneck analysis
- **Token tracking** - Track input/output tokens and estimated costs
- **Baseline comparison** - Compare against historical performance averages
- **Multiple output formats** - Human, JSON, Markdown, CSV for different use cases
- **CI/CD integration** - Exit codes for automated pipeline checks
- **Cross-platform** - Works on macOS, Linux, and Windows
- **Multi-agent safe** - Concurrent executions don't collide

## Installation

No installation required. The skill uses Python standard library only.

**Prerequisites:**
- Python 3.10+
- Bash shell (for wrapper script)

**Optional:** If `uv` is available, the wrapper script uses `uv run python` for faster execution.

## Quick Start

```bash
# 1. Start timing
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill rule-reviewer \
    --target rules/100-snowflake-core.md \
    --model claude-sonnet-45

# Output: TIMING_RUN_ID=a1b2c3d4e5f67890

# 2. (Optional) Record checkpoints during execution
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name rules_loaded

# 3. End timing
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/rule-review.md \
    --skill rule-reviewer \
    --input-tokens 12500 \
    --output-tokens 4200
```

## Commands

### start

Initialize a timing session.

| Argument | Required | Description |
|----------|----------|-------------|
| `--skill` | Yes | Skill name being timed |
| `--target` | Yes | Target file path |
| `--model` | Yes | Model slug (e.g., claude-sonnet-45) |
| `--mode` | No | Review mode (default: FULL) |
| `--agent` | No | Agent name (auto-detected from env) |

```bash
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill rule-reviewer \
    --target rules/100-snowflake-core.md \
    --model claude-sonnet-45 \
    --mode FULL
```

**Output:**
```
TIMING_RUN_ID=a1b2c3d4e5f67890
TIMING_FILE=/tmp/skill-timing-a1b2c3d4e5f67890.json
TIMING_AGENT_ID=cortex-code-12345
```

### checkpoint

Record an intermediate timing point.

| Argument | Required | Description |
|----------|----------|-------------|
| `--run-id` | Yes | Run ID from start command |
| `--name` | Yes | Checkpoint name |

**Predefined checkpoint names:**

| Name | When to Use |
|------|-------------|
| `gates_started` | After Gate 1 foundation loaded |
| `rules_loaded` | After Gate 3 rules loaded |
| `skill_loaded` | After skill fully parsed |
| `work_complete` | After core task finished |
| `file_written` | After output file written |

```bash
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name rules_loaded
```

### end

Finalize timing and compute duration.

| Argument | Required | Description |
|----------|----------|-------------|
| `--run-id` | Yes | Run ID from start (or "none" for recovery) |
| `--output-file` | Yes | Path to output file |
| `--skill` | Yes | Skill name (for recovery) |
| `--input-tokens` | No | Input token count |
| `--output-tokens` | No | Output token count |
| `--format` | No | Output format (human/json/markdown/quiet) |
| `--ci` | No | CI mode: JSON output + exit codes |

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/rule-review.md \
    --skill rule-reviewer \
    --input-tokens 12500 \
    --output-tokens 4200
```

### analyze

Analyze timing data across multiple runs.

| Argument | Required | Description |
|----------|----------|-------------|
| `--skill` | No | Filter by skill name |
| `--model` | No | Filter by model |
| `--days` | No | Days of data (default: 7) |
| `--output` | No | Output file path |
| `--format` | No | Output format (human/json/csv) |

```bash
bash skills/skill-timing/scripts/run_timing.sh analyze \
    --skill rule-reviewer \
    --days 30 \
    --format json
```

### aggregate

Aggregate timing data from review files (parses timing metadata tables).

| Argument | Required | Description |
|----------|----------|-------------|
| `files` | Yes | Review files to parse |
| `--output` | No | Output file path |
| `--format` | No | Output format (json/csv) |

```bash
bash skills/skill-timing/scripts/run_timing.sh aggregate \
    reviews/*.md \
    --format csv
```

### baseline set

Set a performance baseline from recent timing data. Requires at least 5 data points.

| Argument | Required | Description |
|----------|----------|-------------|
| `--skill` | Yes | Skill name |
| `--mode` | Yes | Review mode |
| `--model` | Yes | Model slug |
| `--days` | No | Days of data (default: 30) |
| `--min-samples` | No | Minimum samples required (default: 5) |

```bash
bash skills/skill-timing/scripts/run_timing.sh baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --days 30
```

### baseline compare

Compare a specific run against baseline.

| Argument | Required | Description |
|----------|----------|-------------|
| `--run-id` | Yes | Run ID to compare |

```bash
bash skills/skill-timing/scripts/run_timing.sh baseline compare \
    --run-id a1b2c3d4e5f67890
```

## Output Formats

| Format | Use Case | Flag |
|--------|----------|------|
| `human` | Terminal review (default) | `--format human` |
| `json` | CI/CD pipelines, parsing | `--format json` |
| `markdown` | File embedding | `--format markdown` |
| `quiet` | Exit code only | `--format quiet` |
| `csv` | Spreadsheet analysis (analyze only) | `--format csv` |

## Output Examples

### Human Format (default)

```
TIMING: skill-timing v1.2.0
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
Checkpoints:
  gates_started:  9.90s
  rules_loaded:   32.30s
  work_complete:  210.30s
  file_written:   222.10s
----------------------------------------
Tokens:      16,700 (12,500 in / 4,200 out)
Cost:        $0.1200
Baseline:    +7.4% vs avg (within normal)
----------------------------------------
```

### JSON Format

```json
{
  "run_id": "a1b2c3d4e5f67890",
  "skill_name": "rule-reviewer",
  "model": "claude-sonnet-45",
  "duration_seconds": 225.5,
  "duration_human": "3m 45s",
  "status": "completed",
  "checkpoints": [
    {"name": "gates_started", "elapsed_seconds": 9.9},
    {"name": "rules_loaded", "elapsed_seconds": 32.3}
  ],
  "tokens": {
    "input_tokens": 12500,
    "output_tokens": 4200,
    "total_tokens": 16700,
    "estimated_cost_usd": 0.12
  },
  "baseline_comparison": {
    "delta_percent": 7.4,
    "status": "within_normal"
  }
}
```

### Analyze Output

```
TIMING: Analysis v1.2.0
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

## Anomaly Detection

The tool automatically detects suspicious timing patterns and alerts you:

| Condition | Alert Level | Meaning |
|-----------|-------------|---------|
| Duration below error threshold | ERROR | Likely agent shortcut - review output for completeness |
| Duration below warning threshold | WARNING | Potentially incomplete execution |
| Duration above warning threshold | WARNING | Slow execution - check for issues |

### Default Thresholds

Thresholds are configured per skill and mode in `scripts/skill_timing.py`:

| Skill | Mode | Error (<) | Warning (<) | Warning (>) |
|-------|------|-----------|-------------|-------------|
| rule-reviewer | FULL | 60s | 120s | 600s |
| rule-reviewer | FOCUSED | 30s | 60s | 360s |
| rule-reviewer | STALENESS | 15s | 30s | 240s |
| plan-reviewer | FULL | 15s | 30s | 720s |
| doc-reviewer | FULL | 45s | 90s | 480s |
| rule-creator | default | 90s | 180s | 900s |

### Tuning Thresholds

To add or adjust thresholds for your skill:

1. Run 10+ executions without alerts
2. Use `analyze` command to get P5, P50, P95 statistics
3. Set thresholds:
   - `error` = P5 / 2 (definite shortcut)
   - `short` = P5 (suspicious)
   - `long` = P95 (too slow)

Edit `ALERT_THRESHOLDS` in `scripts/skill_timing.py`:

```python
ALERT_THRESHOLDS = {
    'your-skill': {
        'YOUR_MODE': {'short': 90, 'long': 480, 'error': 45},
    },
}
```

## Exit Codes (CI Mode)

Use `--ci` flag for JSON output with appropriate exit codes:

| Code | Meaning | CI Action |
|------|---------|-----------|
| 0 | Success (within baseline or no baseline) | Pass |
| 1 | General error | Fail |
| 2 | Duration below error threshold (shortcut detected) | Fail |
| 3 | Duration significantly above baseline | Warning/Fail |

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file output.md \
    --skill my-skill \
    --ci

echo "Exit code: $?"
```

## Configuration

### Token Pricing

Edit `COST_PER_1M_TOKENS` in `scripts/skill_timing.py`:

```python
COST_PER_1M_TOKENS = {
    "claude-sonnet-45": {"input": 3.00, "output": 15.00},
    "claude-opus-45": {"input": 15.00, "output": 75.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "default": {"input": 5.00, "output": 15.00},
}
```

**Last updated:** 2026-01-06

**Sources:**
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [OpenAI Pricing](https://openai.com/pricing)

## Data Storage

| Location | Contents | Retention |
|----------|----------|-----------|
| `{temp}/skill-timing-{id}.json` | Active timing sessions | Until end command |
| `reviews/.timing-data/` | Completed timing records | Indefinite |
| `reviews/.timing-baselines.json` | Performance baselines | Indefinite |
| `{temp}/skill-timing-registry.json` | Agent recovery registry | Auto-cleaned |

## Cross-Platform Support

Works on macOS, Linux, and Windows. Uses `tempfile.gettempdir()` for platform-appropriate temp directory:

| Platform | Temp Directory |
|----------|----------------|
| macOS | `/var/folders/.../T/` |
| Linux | `/tmp/` |
| Windows | `C:\Users\...\AppData\Local\Temp\` |

## Multi-Agent Safety

Multiple agents can run timing sessions simultaneously without collisions:

- Each run ID includes: timestamp + PID + random suffix
- Agent recovery registry prevents conflicts
- Concurrent start commands generate unique IDs

## Secure Mode

For shared or multi-user environments, enable restricted file permissions:

```bash
export TIMING_SECURE_MODE=1
```

This sets timing files to `0600` (owner read/write only) instead of default `0644`.

## Troubleshooting

### Timing file not found

**Symptom:** `WARNING: Timing file not found for run_id=...`

**Causes:**
1. Agent forgot run_id (context loss)
2. Timing file was manually deleted
3. Temp directory was cleaned by OS

**Solutions:**
```bash
# Use registry recovery
bash skills/skill-timing/scripts/run_timing.sh end --run-id none ...

# Or find active timing files
ls $(python3 -c "import tempfile; print(tempfile.gettempdir())")/skill-timing-*.json
```

### Agent forgets run_id

Set `--run-id none` to trigger automatic recovery from the agent registry.

### Invalid run_id format

Must be 16-character hex string (e.g., `a1b2c3d4e5f67890`). Recovery is automatic.

### Duration too short (shortcut detected)

Review output file for completeness. If execution was legitimate, adjust the `error` threshold for your skill.

### Token costs seem wrong

**Causes:**
- Outdated pricing in `COST_PER_1M_TOKENS`
- Different model variant (e.g., extended-context pricing)

**Solutions:**
- Update pricing in `scripts/skill_timing.py`
- Use `--input-tokens 0 --output-tokens 0` to skip cost estimation

## Resources

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Skill specification (for autonomous agents) |
| [VALIDATION.md](VALIDATION.md) | Self-validation procedures |
| [examples/](examples/) | Workflow examples |
| [schemas/](schemas/) | JSON schema for output validation |
| [workflows/](workflows/) | Detailed workflow guides |

## Version

- **Current:** 1.2.0
- **Schema:** `schemas/timing-output.schema.json`
