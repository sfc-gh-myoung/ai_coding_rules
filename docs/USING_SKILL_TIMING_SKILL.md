# Using the Skill Timing Skill

**Last Updated:** 2026-03-07

The Skill Timing Skill provides execution timing instrumentation for measuring and analyzing skill performance. It tracks wall-clock duration, records checkpoints, estimates token costs, detects anomalies, and compares against historical baselines.

**Prerequisites:** Python 3.11+ and uv installed.


## Quick Start

### Integrated Use (Recommended)

Add `timing_enabled: true` to any supported skill:

```text
Use the doc-reviewer skill.

target_files: README.md
review_mode: FULL
timing_enabled: true
```

Output includes timing metadata in the review file and a summary in STDOUT.

### Manual Use

**Step 1: Start timing**

```bash
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill doc-reviewer \
    --target README.md \
    --model claude-sonnet-45
```

Returns a `run_id` for tracking.

**Step 2: End timing**

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id <run_id> \
    --output-file reviews/doc-reviews/README-claude-sonnet-45-2026-03-08.md \
    --skill doc-reviewer \
    --input-tokens 8500 \
    --output-tokens 3800
```

**Step 3: View results**

The module outputs a timing summary to STDOUT. The agent embeds timing metadata in the output file.


## Timing Operations

| Operation | Purpose | When to Use |
|-----------|---------|-------------|
| **start** | Initialize timing | Beginning of skill execution |
| **checkpoint** | Record intermediate milestone | After significant phases |
| **end** | Finalize and compute duration | End of skill execution |
| **baseline set** | Create performance baseline | After gathering 5+ data points |
| **analyze** | Aggregate statistics | Performance analysis across runs |

### timing-start

```bash
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill doc-reviewer \
    --target README.md \
    --model claude-sonnet-45
```

Returns `run_id` for tracking this execution.

### timing-checkpoint

```bash
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id <run_id> \
    --name schema_validated
```

**Common checkpoints:** `skill_loaded`, `input_validated`, `review_complete`, `file_written`

### timing-end

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id <run_id> \
    --output-file <path> \
    --skill <skill-name> \
    --input-tokens <count> \
    --output-tokens <count>
```

Outputs timing summary to STDOUT. Agent must parse and embed in output file.

### baseline set

```bash
bash skills/skill-timing/scripts/run_timing.sh baseline set \
    --skill rule-reviewer \
    --mode FULL \
    --model claude-sonnet-45 \
    --days 30
```

Requires at least 5 data points.

### analyze

```bash
bash skills/skill-timing/scripts/run_timing.sh analyze \
    --skill rule-reviewer \
    --days 7
```

Returns aggregate statistics, P50/P95 durations (median/95th percentile), and outliers.


## Understanding Your Results

### STDOUT Summary

After `timing-end`, the module outputs:

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

### Timing Metadata

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

### Anomaly Alerts

The skill automatically detects and alerts on suspicious durations:

| Condition | Alert Level | Threshold (rule-reviewer FULL) |
|-----------|-------------|-------------------------------|
| Very short duration | ❌ Error | < 60s |
| Short duration | ⚠️ Warning | < 120s |
| Long duration | ⚠️ Warning | > 600s |

**What alerts indicate:**
- **Very short/short:** Agent shortcuts (skipped steps), cached results
- **Long:** Process hangs, timeouts, unusually complex targets

### Token Cost Estimates

Cost estimates use model pricing from `COST_PER_1M_TOKENS` in `skill_timing.py`.

**Note:** Estimates may differ from provider billing due to:
- Outdated pricing (update quarterly)
- Extended-context pricing variants


## Advanced Usage

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
2. Use `analyze` to get P95 duration
3. Set `long` = P95, `short` = P5, `error` = P5 / 2

### MODE Compatibility

| Operation | PLAN Mode | ACT Mode |
|-----------|-----------|----------|
| timing-start | ✓ Safe | ✓ Safe |
| timing-checkpoint | ✓ Safe | ✓ Safe |
| timing-end (Python) | ✓ Safe | ✓ Safe |
| timing-end (metadata embed) | ✗ Not safe | ✓ Required |
| baseline set | ✗ Not safe | ✓ Required |
| analyze | ✓ Safe | ✓ Safe |

**Note:** Python module outputs to STDOUT only (PLAN safe). Agent must parse and embed metadata (ACT required).

### Secure Mode

For shared/multi-user environments:

```bash
export TIMING_SECURE_MODE=1
```

Sets timing files to 0600 (owner read/write only) instead of default 0644.

### Cross-Platform Notes

Works on macOS, Linux, and Windows (uses `tempfile.gettempdir()`).

### Multi-Agent Safety

Multiple agents can run simultaneously without timing collisions (uses PID + random suffix + registry).


## FAQ

### Why does it say "Timing file not found"?

**Causes:** Agent forgot run_id (context loss), file manually deleted, or temp directory cleaned.

**Solutions:**
- Use `--run-id none` to trigger automatic registry recovery
- Check temp: `ls $(python -c "import tempfile; print(tempfile.gettempdir())")/skill-timing-*.json`
- Verify run_id is 16-character hex string

### Why does the agent forget run_id between steps?

**Solutions:**
1. Use `--run-id none` for automatic recovery
2. Find manually: `ls -t /tmp/skill-timing-*.json | head -1`
3. Extract: `basename /tmp/skill-timing-<id>.json | cut -d- -f3 | cut -d. -f1`

### Why is duration suspiciously short?

**Alert:** ❌ TIMING ERROR: Duration below threshold

**Likely causes:** Agent shortcut, cached result, very simple target.

**Action:** Review output file for completeness.

### Why is run_id format invalid?

**Alert:** WARNING: Invalid run_id format

**Cause:** Typo or memory corruption.

**Solution:** Module triggers registry recovery automatically. If that fails, find correct run_id from temp directory.

### Why do token costs seem wrong?

**Causes:** Outdated pricing in `COST_PER_1M_TOKENS`, or different model variant.

**Solutions:**
- Update pricing in `skill_timing.py`
- Use `--input-tokens 0 --output-tokens 0` to skip cost estimation

### How do I update token pricing?

**Sources:**
- Anthropic: https://www.anthropic.com/pricing
- OpenAI: https://openai.com/pricing

Update `COST_PER_1M_TOKENS` in `skills/skill-timing/scripts/skill_timing.py`.

**Maintenance schedule:** Quarterly (next review: 2026-04-06)


## Reference

### Architecture

```
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
│   └── Output STDOUT summary
│
├── baseline set
│   └── Aggregate recent data into baseline file
│
└── analyze
    └── Query timing data with statistics
```

### File Structure

```text
skills/skill-timing/
├── SKILL.md               # Skill definition
├── README.md              # Full documentation
├── scripts/
│   ├── skill_timing.py    # Python module
│   └── run_timing.sh      # Shell wrapper
└── workflows/             # Step-by-step guides
```

### Data Storage

| Location | Contents | Retention |
|----------|----------|-----------|
| `{temp}/skill-timing-{id}.json` | Active runs | Until end |
| `{temp}/skill-timing-{id}-complete.json` | Completed runs | 7 days |
| `{temp}/skill-timing-registry.json` | Agent recovery | Auto-cleaned |
| `reviews/.timing-baselines.json` | Baselines | Indefinite |

### Supported Skills

| Skill | What's Timed |
|-------|--------------|
| doc-reviewer | Documentation review |
| plan-reviewer | Plan review |
| rule-reviewer | Rule review |
| rule-creator | Rule creation |
| bulk-rule-reviewer | Bulk review process |

### Integration with Other Skills

All reviewer skills (doc-reviewer, plan-reviewer, rule-reviewer, bulk-rule-reviewer) and rule-creator support `timing_enabled: true` parameter.

### Deployment

This skill is **deployable** (included in `task deploy`). After deployment, users can time skill executions, measure performance, and track improvements.

### Support

- **Skill README:** `skills/skill-timing/README.md`
- **Workflow guides:** `skills/skill-timing/workflows/*.md`
- **Python module:** `skills/skill-timing/scripts/skill_timing.py`
- **Shell wrapper:** `skills/skill-timing/scripts/run_timing.sh`
