# Using the Skill Timing Skill

**Last Updated:** 2026-03-27

The Skill Timing Skill provides execution timing instrumentation for measuring and analyzing skill performance. It tracks wall-clock duration, records checkpoints, estimates token costs, detects anomalies, and compares against historical baselines.

**Features:**
- Wall-clock timing with checkpoint support
- Token tracking and cost estimation
- Baseline comparison against historical averages
- Anomaly detection for shortcut identification
- Multiple output formats (human, JSON, markdown, CSV)
- CI/CD integration with exit codes
- Cross-platform and multi-agent safe

**Prerequisites:** Python 3.10+ and Bash shell. Optional: `uv` for faster execution.


## Examples

### Minimal Integrated Example

```text
Use the doc-reviewer skill.

target_files: README.md              # Required (by parent skill)
review_mode: FULL                    # Required (by parent skill)
timing_enabled: true                 # Required — enables timing
```

### Manual Use With All Options

```bash
# 1. Start timing
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill rule-reviewer \           # Required — skill being timed
    --target rules/100-snowflake-core.md \  # Required — target file
    --model claude-sonnet-45 \        # Required — model slug
    --mode FULL \                     # Optional (default: FULL) — review mode
    --agent cortex-code               # Optional (default: auto-detected) — agent name

# Output: TIMING_RUN_ID=a1b2c3d4e5f67890

# 2. Record checkpoints
$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id a1b2c3d4e5f67890 \       # Required — from start output
    --name rules_loaded                # Required — checkpoint name

# 3. End timing with all options
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id a1b2c3d4e5f67890 \       # Required — from start output
    --output-file reviews/rule-review.md \  # Required — output path
    --skill rule-reviewer \           # Required — for recovery
    --input-tokens 12500 \            # Optional — token count
    --output-tokens 4200 \            # Optional — token count
    --format json \                   # Optional (default: human) — output format
    --ci                              # Optional — CI mode with exit codes
```

### Baseline Set Example

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py baseline set \
    --skill rule-reviewer \           # Required — skill name
    --mode FULL \                     # Required — review mode
    --model claude-sonnet-45 \        # Required — model slug
    --days 30 \                       # Optional (default: 30) — days of history
    --min-samples 5                   # Optional (default: 5) — minimum data points
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
$PYTHON skills/skill-timing/scripts/skill_timing.py analyze \
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
$PYTHON skills/skill-timing/scripts/skill_timing.py aggregate \
    reviews/*.md \
    --format csv
```

### baseline set

Set a performance baseline from recent timing data.

| Argument | Required | Description |
|----------|----------|-------------|
| `--skill` | Yes | Skill name |
| `--mode` | Yes | Review mode |
| `--model` | Yes | Model slug |
| `--days` | No | Days of data (default: 30) |
| `--min-samples` | No | Minimum samples required (default: 5) |

### baseline compare

Compare a specific run against baseline.

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py baseline compare \
    --run-id a1b2c3d4e5f67890
```


## Understanding Your Results

### Output Formats

| Format | Use Case | Flag |
|--------|----------|------|
| `human` | Terminal review (default) | `--format human` |
| `json` | CI/CD pipelines, parsing | `--format json` |
| `markdown` | File embedding | `--format markdown` |
| `quiet` | Exit code only | `--format quiet` |
| `csv` | Spreadsheet analysis (analyze only) | `--format csv` |

### Human Format Output

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

### JSON Format Output

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

### Timing Metadata (Embedded in Output Files)

```markdown
## Timing Metadata

| Metric | Value |
|--------|-------|
| Run ID | `a1b2c3d4e5f67890` |
| Start (UTC) | 2026-01-06T10:30:00Z |
| End (UTC) | 2026-01-06T10:33:45Z |
| Duration | 3m 45s (225.5s) |
| Model | claude-sonnet-45 |
| Agent | cursor |
| Tokens | 16,700 (12,500 in / 4,200 out) |
| Cost | ~$0.04 |
```

### Anomaly Detection

The tool automatically detects suspicious timing patterns:

| Condition | Alert Level | Meaning |
|-----------|-------------|---------|
| Duration below error threshold | ERROR | Likely agent shortcut |
| Duration below warning threshold | WARNING | Potentially incomplete |
| Duration above warning threshold | WARNING | Slow execution |

**Default Thresholds:**

| Skill | Mode | Error (<) | Warning (<) | Warning (>) |
|-------|------|-----------|-------------|-------------|
| rule-reviewer | FULL | 60s | 120s | 600s |
| rule-reviewer | FOCUSED | 30s | 60s | 360s |
| rule-reviewer | STALENESS | 15s | 30s | 240s |
| plan-reviewer | FULL | 15s | 30s | 720s |
| doc-reviewer | FULL | 45s | 90s | 480s |
| rule-creator | default | 90s | 180s | 900s |


## Advanced Usage

### CI/CD Integration

Use `--ci` flag for JSON output with exit codes:

| Exit Code | Meaning | CI Action |
|-----------|---------|-----------|
| 0 | Success (within baseline) | Pass |
| 1 | General error | Fail |
| 2 | Duration below error threshold (shortcut) | Fail |
| 3 | Duration significantly above baseline | Warning/Fail |

```bash
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id a1b2c3d4e5f67890 \
    --output-file output.md \
    --skill my-skill \
    --ci

echo "Exit code: $?"
```

### Custom Alert Thresholds

Edit `ALERT_THRESHOLDS` in `skills/skill-timing/scripts/skill_timing.py`:

```python
ALERT_THRESHOLDS = {
    'your-skill': {
        'YOUR_MODE': {'short': 90, 'long': 480, 'error': 45},
    },
}
```

**Recommended approach:**
1. Run 10+ executions without alerts
2. Use `analyze` to get P5, P50, P95 statistics
3. Set: `error` = P5/2, `short` = P5, `long` = P95

### Token Pricing Configuration

Edit `COST_PER_1M_TOKENS` in `scripts/skill_timing.py`:

```python
COST_PER_1M_TOKENS = {
    "claude-sonnet-45": {"input": 3.00, "output": 15.00},
    "claude-opus-45": {"input": 15.00, "output": 75.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "default": {"input": 5.00, "output": 15.00},
}
```

**Sources:** [Anthropic Pricing](https://www.anthropic.com/pricing), [OpenAI Pricing](https://openai.com/pricing)

**Maintenance schedule:** Quarterly

### Secure Mode

For shared/multi-user environments:

```bash
export TIMING_SECURE_MODE=1
```

Sets timing files to `0600` (owner read/write only) instead of default `0644`.

### MODE Compatibility

| Operation | PLAN Mode | ACT Mode |
|-----------|-----------|----------|
| timing-start | Safe | Safe |
| timing-checkpoint | Safe | Safe |
| timing-end (Python) | Safe | Safe |
| timing-end (metadata embed) | Not safe | Required |
| baseline set | Not safe | Required |
| analyze | Safe | Safe |


## FAQ

### Why does it say "Timing file not found"?

**Causes:** Agent forgot run_id (context loss), file manually deleted, or temp directory cleaned.

**Solutions:**
- Use `--run-id none` to trigger automatic registry recovery
- Check temp: `ls $(python3 -c "import tempfile; print(tempfile.gettempdir())")/skill-timing-*.json`

### Why does the agent forget run_id between steps?

Use `--run-id none` for automatic recovery from the agent registry.

### Why is duration suspiciously short?

**Alert:** ERROR: Duration below threshold

**Causes:** Agent shortcut, cached result, very simple target.

**Action:** Review output file for completeness. If legitimate, adjust the `error` threshold.

### Why do token costs seem wrong?

**Causes:** Outdated pricing in `COST_PER_1M_TOKENS`, or different model variant.

**Solutions:**
- Update pricing in `skill_timing.py`
- Use `--input-tokens 0 --output-tokens 0` to skip cost estimation


## Reference

### Architecture

```text
Timing Module (skill_timing.py)
│
├── start
│   ├── Generate run_id (PID + random suffix)
│   ├── Create timing file in temp
│   ├── Register in recovery registry
│   └── Return run_id
│
├── checkpoint
│   ├── Load timing file
│   ├── Append checkpoint with timestamp
│   └── Save timing file
│
├── end
│   ├── Load timing file
│   ├── Compute duration
│   ├── Calculate token cost
│   ├── Check against baselines
│   ├── Detect anomalies
│   └── Output summary
│
├── analyze
│   └── Query timing data with statistics (P5/P50/P95)
│
├── aggregate
│   └── Parse timing metadata from review files
│
└── baseline
    ├── set: Aggregate recent data into baseline
    └── compare: Compare run against baseline
```

### File Structure

```text
skills/skill-timing/
├── SKILL.md               # Skill definition (entrypoint)
├── VALIDATION.md          # Self-validation procedures
├── scripts/
│   ├── skill_timing.py    # Python module
│   └── find_python.sh    # Python interpreter discovery
├── examples/              # Workflow examples
│   ├── basic-timing.md
│   ├── with-checkpoints.md
│   ├── baseline-workflow.md
│   └── ci-integration.md
└── workflows/             # Step-by-step guides
    ├── timing-start.md
    ├── timing-checkpoint.md
    └── timing-end.md
```

### Data Storage

| Location | Contents | Retention |
|----------|----------|-----------|
| `{temp}/skill-timing-{id}.json` | Active runs | Until end |
| `reviews/.timing-data/` | Completed timing records | Indefinite |
| `reviews/.timing-baselines.json` | Performance baselines | Indefinite |
| `{temp}/skill-timing-registry.json` | Agent recovery registry | Auto-cleaned |

### Cross-Platform Support

| Platform | Temp Directory |
|----------|----------------|
| macOS | `/var/folders/.../T/` |
| Linux | `/tmp/` |
| Windows | `C:\Users\...\AppData\Local\Temp\` |

### Multi-Agent Safety

Multiple agents can run timing sessions simultaneously without collisions:
- Each run ID includes: timestamp + PID + random suffix
- Agent recovery registry prevents conflicts
- Concurrent start commands generate unique IDs

### Supported Skills

| Skill | What's Timed |
|-------|--------------|
| doc-reviewer | Documentation review |
| plan-reviewer | Plan review |
| rule-reviewer | Rule review |
| rule-creator | Rule creation |
| bulk-rule-reviewer | Bulk review process |

All support `timing_enabled: true` parameter.

### Deployment

This skill is **deployable** (included in `task deploy`). After deployment, users can time skill executions, measure performance, and track improvements.

### Support

- **Skill entrypoint:** `skills/skill-timing/SKILL.md`
- **Validation:** `skills/skill-timing/VALIDATION.md`
- **Workflow guides:** `skills/skill-timing/workflows/*.md`
- **Examples:** `skills/skill-timing/examples/*.md`
- **Python module:** `skills/skill-timing/scripts/skill_timing.py`
- **Python interpreter discovery:** `skills/skill-timing/scripts/find_python.sh`
