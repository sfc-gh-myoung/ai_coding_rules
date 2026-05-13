# Workflow: Timing End

## Purpose

Finalize timing instrumentation and compute execution duration. This workflow has two distinct steps:
1. **Compute timing data** (Python module, read-only)
2. **Embed metadata** (Agent appends timing table to output file)

## Prerequisites

- Timing start was executed (or `run_id` is `none`)
- File write has completed successfully

## Inputs

- `run_id`: From timing-start output (or `none` if timing was skipped)
- `output_file`: Path to the output file that was written
- `skill_name`: Name of the skill (for recovery)
- `input_tokens`: (optional) Input token count
- `output_tokens`: (optional) Output token count
- `dimension_timings`: (optional) JSON array of per-dimension timing data. Format: `[{"dimension":"name","duration_seconds":N,"mode":"checkpoint|self-report|inline"}]`

## Token Sources

Token counts can be obtained from:
- **API response headers:** Look for `x-usage-input-tokens`, `x-usage-output-tokens` (Claude API)
- **SDK response objects:** Check `usage.input_tokens`, `usage.output_tokens` (Python SDKs)
- **Model tooling:** Provider-specific usage tracking interfaces
- **Manual estimation:** Character/word count approximations as fallback
- **If unavailable:** Simply omit `--input-tokens` and `--output-tokens` flags (timing still works)

**Example (Claude Python SDK):**
```python
response = client.messages.create(...)
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
```

## Step 1: Compute Timing Data (Read-Only)

If `run_id` is `none`, skip this workflow.

Otherwise, execute:

```bash
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id '{{run_id}}' \
    --output-file '{{output_file}}' \
    --skill '{{skill_name}}' \
    --input-tokens {{input_tokens}} \
    --output-tokens {{output_tokens}} \
    --format markdown \
    --dimension-timings '{{dimension_timings_json}}'
```

**Output (STDOUT):** A markdown timing table ready to append to the output file:

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

### Per-Dimension Timing

| Dimension | Duration | Mode |
|-----------|----------|------|
| actionability | 42.30s | checkpoint |
| rule_size | 0.10s | inline |
| parsability | 38.70s | checkpoint |
| **Total (dimension work)** | **81.10s** | - |
```

**Note:** The `--format markdown` flag produces output ready for direct embedding. Without it, output is human-readable but not suitable for file embedding.

## Step 2: Embed Metadata in Output File

The agent must append the STDOUT from Step 1 to the output file.

If timing completed successfully (output contains `## Timing Metadata`), append the full markdown table to the end of the output file.

## Validation

After embedding, verify:
```bash
grep -q "## Timing Metadata" {{output_file}}
```

If missing and `_timing_run_id` exists, re-run `end --format markdown` (the completed file persists and can be recovered).

## Error Handling

**Missing timing file:**
1. Attempt agent memory recovery from registry
2. If recovery fails, check for completed file (`reviews/.timing-data/skill-timing-{run_id}-complete.json`)
3. If no completed file, log warning
4. Do NOT add Timing Metadata section
5. Consider skill execution successful

**Anomaly detected:**
1. Print alert to STDOUT
2. Include alert in timing data
3. Continue execution (non-fatal)

## File Write Requirements

**Step 1 (Python computation):** Read-only (no file modifications)
**Step 2 (Metadata embedding):** Requires file write permissions (appends to output file)

## Next Step

Report completion summary in chat.
