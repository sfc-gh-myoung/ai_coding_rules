# Using the Skill Timing Skill

**Last Updated:** 2026-01-21

The Skill Timing Skill provides execution timing instrumentation for measuring and analyzing skill performance.

## Background

The skill-timing skill enables performance measurement and comparison for skill executions through:

- Wall-clock duration (actual elapsed time) tracking with microsecond precision (accurate to millionths of a second)
- Intermediate checkpoint recording for bottleneck identification
- Token usage and cost estimation
- Real-time anomaly detection (shortcuts, timeouts)
- Historical baseline comparison (performance vs previous runs)
- Cross-model and cross-agent performance analysis

## Quick Start

### Integrated Use (Recommended)

Most skills support timing through the `timing_enabled` parameter:

```text
Use the doc-reviewer skill.

target_files: README.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
timing_enabled: true
```

When enabled, the output includes:
- **Timing Metadata section** in the review file
- **STDOUT summary** with duration, checkpoints, tokens, baseline comparison
- **Real-time anomaly alerts** if duration is suspicious

### Skills Supporting Timing

- **doc-reviewer** - Documentation review timing
- **plan-reviewer** - Plan review timing
- **rule-reviewer** - Rule review timing
- **rule-creator** - Rule creation timing
- **bulk-rule-reviewer** - Bulk review timing (tracks entire process)

## Timing Operations

**Prerequisites:** Python 3.11+ and uv installed

### timing-start

Initialize timing for a skill execution.

**Manual usage:**
```bash
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill doc-reviewer \
    --target README.md \
    --model claude-sonnet-45
```

**Output:** Returns `run_id` for tracking this execution

### timing-checkpoint

Record an intermediate timing checkpoint.

**Manual usage:**
```bash
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name schema_validated
```

**Common checkpoints:**
- `skill_loaded` - After loading SKILL.md
- `input_validated` - After input validation
- `review_complete` - After review generation
- `file_written` - After writing output file

### timing-end

Finalize timing and compute duration.

**Manual usage:**
```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/README-claude-sonnet-45-2026-01-06.md \
    --skill doc-reviewer \
    --input-tokens 8500 \
    --output-tokens 3800
```

**Output:** STDOUT (standard output) timing summary (agent must parse and embed in file)

### baseline set

Set a performance baseline from recent timing data.

**Usage:**
```bash
bash skills/skill-timing/scripts/run_timing.sh baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --days 30
```

**Requirements:** At least 5 data points needed

### analyze

Analyze timing data across runs.

**Usage:**
```bash
bash skills/skill-timing/scripts/run_timing.sh analyze \
    --skill rule-reviewer \
    --days 7
```

**Output:** Aggregate statistics, P50/P95 durations (median/95th percentile), outliers

## Output Format

### STDOUT Summary

```
⏱️ Timing Summary
├── Duration: 3m 45s (225.5s)
├── Started:  10:30:00 UTC
├── Ended:    10:33:45 UTC
├── Run ID:   a1b2c3d4e5f67890
├── Tokens:   16,700 (12,500 in / 4,200 out) ~$0.04
└── Baseline: +7.4% vs avg (within normal)

Checkpoints:
├── skill_loaded      1.2s   (0.5%)
├── schema_validated  8.5s   (3.8%)
├── review_complete   210.3s (93.3%)
└── file_written      222.1s (98.5%)
```

### Timing Metadata (in output file)

The agent appends this section to the output file:

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

## Anomaly Detection

The skill automatically detects and alerts on:

| Condition | Alert Level | Threshold (rule-reviewer FULL) |
|-----------|-------------|-------------------------------|
| Very short duration | ❌ Error | < 60s |
| Short duration | ⚠️ Warning | < 120s |
| Long duration | ⚠️ Warning | > 600s |

**Alerts indicate:**
- Agent shortcuts (skipped steps)
- Cached results
- Process hangs or timeouts
- Unusually complex targets

### Tuning Alert Thresholds

If you need to adjust alert thresholds for your use case:

1. **Edit `ALERT_THRESHOLDS` in `skill_timing.py`:**
   ```python
   ALERT_THRESHOLDS = {
       'your-skill': {
           'YOUR_MODE': {'short': 90, 'long': 480, 'error': 45},
       },
   }
   ```

2. **Consider these factors when tuning:**
   - File complexity: Larger/more complex files take longer
   - Model speed: Faster models need lower thresholds
   - Task scope: FULL reviews take longer than FOCUSED
   - Historical data: Use `analyze` command to find typical durations

3. **Recommended approach:**
   - Run 10+ executions without alerts
   - Use `analyze` to get P95 duration
   - Set `long` = P95, `short` = P5, `error` = P5 / 2

## Token Cost Tracking

**Maintenance Note:** Token costs in `COST_PER_1M_TOKENS` should be updated periodically as model pricing changes.

**Sources for current pricing:**
- Anthropic (Claude): [https://www.anthropic.com/pricing](https://www.anthropic.com/pricing)
- OpenAI (GPT): [https://openai.com/pricing](https://openai.com/pricing)

**Note:** Verify URLs are current before updating costs.

**Last updated:** 2026-01-06  
**Next review:** 2026-04-06 (Quarterly maintenance)

When prices change, update the `COST_PER_1M_TOKENS` dict in `skills/skill-timing/scripts/skill_timing.py`.

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

## Data Storage

| Location | Contents | Retention | Notes |
|----------|----------|-----------|-------|
| `{temp}/skill-timing-{id}.json` | Active runs | Until end | - |
| `{temp}/skill-timing-{id}-complete.json` | Completed runs | 7 days | - |
| `{temp}/skill-timing-registry.json` | Agent recovery | Auto-cleaned | - |
| `reviews/.timing-baselines.json` | Baselines | Indefinite | Created on first `baseline set` |

## Troubleshooting

### Timing file not found

**Symptom:** `WARNING: Timing file not found for run_id=...`

**Causes:**
1. Agent forgot run_id (context loss)
2. Timing file was manually deleted
3. Temp directory was cleaned by OS

**Solutions:**
- Registry recovery: Set `--run-id none` to trigger automatic recovery
- Check temp directory: `ls $(python -c "import tempfile; print(tempfile.gettempdir())")/skill-timing-*.json`
- Verify run_id format: Must be 16-character hex string

### Agent forgets run_id between steps

**Symptom:** Agent asks for run_id during timing-end

**Solutions:**
1. **Preferred:** Agent recovery registry (automatic with `--run-id none`)
2. **Manual:** Find active timing file: `ls -t /tmp/skill-timing-*.json | head -1`
3. **Extract run_id:** `basename /tmp/skill-timing-a1b2c3d4e5f67890.json | cut -d- -f3 | cut -d. -f1`

### Duration suspiciously short

**Symptom:** ❌ TIMING ERROR: Duration below threshold

**Likely causes:**
- Agent shortcut (skipped steps)
- Cached result
- Very simple target file

**Action:** Review output file for completeness

### Invalid run_id format

**Symptom:** `WARNING: Invalid run_id format`

**Cause:** Typo or memory corruption in run_id

**Solution:** The module automatically triggers registry recovery. If that fails, manually find the correct run_id from temp directory.

### Token costs seem wrong

**Symptom:** Cost estimate doesn't match provider billing

**Causes:**
- Outdated pricing in `COST_PER_1M_TOKENS`
- Different model variant (e.g., extended-context pricing)

**Solutions:**
- Update `COST_PER_1M_TOKENS` in `skill_timing.py`
- Check provider pricing pages
- Use `--input-tokens 0 --output-tokens 0` to skip cost estimation

## Cross-Platform Support

Works on macOS, Linux, and Windows (uses `tempfile.gettempdir()`).

## Multi-Agent Safety

Multiple agents can run simultaneously without timing collisions (uses PID + random suffix + registry).

## Secure Mode

For shared/multi-user environments, enable secure file permissions:

```bash
export TIMING_SECURE_MODE=1
```

This sets timing files to 0600 (owner read/write only) instead of default 0644.

## Deployment

This skill is **deployable** (included when running `task deploy`). After deployment to a project, users can time skill executions, measure performance, and track improvements.

## Support

For detailed documentation:
- **Skill README:** `skills/skill-timing/README.md`
- **Workflow guides:** `skills/skill-timing/workflows/*.md`
- **Python module:** `skills/skill-timing/scripts/skill_timing.py`
- **Shell wrapper:** `skills/skill-timing/scripts/run_timing.sh`

