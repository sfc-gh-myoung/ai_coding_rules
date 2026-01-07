# Skill Timing

A Claude skill for timing instrumentation of other skills, enabling performance measurement, comparison, and optimization.

## Features

- **Wall-clock timing** - Measure end-to-end skill execution duration
- **Checkpoints** - Record intermediate timing points for detailed analysis
- **Token tracking** - Track input/output tokens and estimated costs
- **Anomaly detection** - Real-time alerts for suspicious durations
- **Baseline comparison** - Compare against historical performance
- **Analysis tools** - Aggregate and analyze timing data

## Quick Start

### Enable Timing in a Skill

Add timing to any skill by including these steps:

```
1. Input validation
2. **Timing start** (PLAN mode safe)
3. [Your skill steps...]
4. **Checkpoints** (optional, PLAN mode safe)
5. **Timing end (compute)** (PLAN mode safe - outputs to STDOUT)
6. File write (requires ACT)
7. **Timing end (embed)** (requires ACT - appends metadata to file)
```

### Manual Timing Commands

```bash
# Start timing (using portable wrapper)
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill rule-reviewer \
    --target rules/100-snowflake-core.md \
    --model claude-sonnet-45

# Record checkpoint
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id a1b2c3d4e5f67890 \
    --name schema_validated

# End timing
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file reviews/100-snowflake-core-claude-sonnet-45-2026-01-06.md \
    --skill rule-reviewer \
    --input-tokens 12500 \
    --output-tokens 4200
```

### Analyze Timing Data

```bash
# Analyze recent runs
bash skills/skill-timing/scripts/run_timing.sh analyze --skill rule-reviewer --days 7

# Set baseline (requires at least 5 data points)
bash skills/skill-timing/scripts/run_timing.sh baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45

# Compare against baseline
bash skills/skill-timing/scripts/run_timing.sh baseline compare --run-id a1b2c3d4e5f67890
```

**Note:** The `run_timing.sh` wrapper automatically uses `uv run python` if available, falling back to `python3` or `python`.

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

The agent must parse the STDOUT and append this section to the output file:

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
   - **File complexity:** Larger/more complex files take longer
   - **Model speed:** Faster models need lower thresholds
   - **Task scope:** FULL reviews take longer than FOCUSED
   - **Historical data:** Use `analyze` command to find typical durations

3. **Recommended approach:**
   - Run 10+ executions without alerts
   - Use `analyze` to get P95 duration
   - Set `long` = P95, `short` = P5, `error` = P5 / 2

## Token Cost Tracking

**Maintenance Note:** Token costs in `COST_PER_1M_TOKENS` should be updated periodically as model pricing changes.

**Sources for current pricing:**
- Anthropic (Claude): https://www.anthropic.com/pricing
- OpenAI (GPT): https://openai.com/pricing

**Last updated:** 2026-01-06  
**Next review:** 2026-04-06 (Quarterly maintenance)

When prices change, update the `COST_PER_1M_TOKENS` dict in `skills/skill-timing/scripts/skill_timing.py`.

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

## Data Storage

| Location | Contents | Retention |
|----------|----------|-----------|
| `{temp}/skill-timing-{id}.json` | Active runs | Until end |
| `reviews/.timing-data/skill-timing-{id}-complete.json` | Completed runs | Indefinite |
| `{temp}/skill-timing-registry.json` | Agent recovery | Auto-cleaned |
| `reviews/.timing-baselines.json` | Baselines | Indefinite |

---

## Deployment

This skill is **deployable** (included when running `task deploy`). After deployment to a project, users can time skill executions, measure performance, and track improvements.

**Integration:** Timing functionality is enabled via `timing_enabled: true` parameter in other skills (doc-reviewer, plan-reviewer, rule-reviewer, rule-creator, bulk-rule-reviewer).
