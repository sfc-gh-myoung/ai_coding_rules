# Workflow: Timing End

## Purpose

Finalize timing instrumentation and compute execution duration. This workflow has two distinct steps:
1. **Compute timing data** (Python module, PLAN mode safe)
2. **Embed metadata** (Agent action, ACT mode required)

## Prerequisites

- Timing start was executed (or `run_id` is `none`)
- File write has completed successfully

## Inputs

- `run_id`: From timing-start output (or `none` if timing was skipped)
- `output_file`: Path to the output file that was written
- `skill_name`: Name of the skill (for recovery)
- `input_tokens`: (optional) Input token count
- `output_tokens`: (optional) Output token count

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

## Step 1: Compute Timing Data (PLAN Mode Safe)

If `run_id` is `none`, skip this workflow.

Otherwise, execute both steps:

```bash
# Using wrapper script (recommended):
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id '{{run_id}}' \
    --output-file '{{output_file}}' \
    --skill '{{skill_name}}' \
    --input-tokens {{input_tokens}} \
    --output-tokens {{output_tokens}}

# Or direct invocation with uv (if available):
uv run python skills/skill-timing/scripts/skill_timing.py end \
    --run-id '{{run_id}}' \
    --output-file '{{output_file}}' \
    --skill '{{skill_name}}' \
    --input-tokens {{input_tokens}} \
    --output-tokens {{output_tokens}}
```

**Output (STDOUT):**
- `TIMING_DURATION`: Human-readable duration
- `TIMING_START`: ISO timestamp of start
- `TIMING_END`: ISO timestamp of end
- `TIMING_STATUS`: completed, warning, missing, or error
- Timing summary with checkpoints, tokens, baseline comparison

**Important:** This command does NOT modify any files. It only outputs to STDOUT.

## Step 2: Embed Metadata in Output File (ACT Mode Required)

**Responsibility:** The **agent** must parse the STDOUT from Step 1 and append the timing metadata section to the output file.

**MODE:** ACT mode required (file modification)

If timing completed (TIMING_STATUS=completed), append this section to the output file:

```markdown
---

## Timing Metadata

- **Run ID** - `{{run_id}}`
- **Start (UTC)** - {{start_iso}}
- **End (UTC)** - {{end_iso}}
- **Duration** - {{duration_human}} ({{duration_seconds}}s)
- **Model** - {{model}}
- **Agent** - {{agent}}
- **Tokens** - {{total_tokens}} ({{input_tokens}} in / {{output_tokens}} out)
- **Cost** - ~${{estimated_cost_usd}}
```

## Error Handling

**Missing timing file:**
1. Attempt agent memory recovery from registry
2. If recovery fails, log warning
3. Do NOT add Timing Metadata section
4. Consider skill execution successful

**Anomaly detected:**
1. Print alert to STDOUT
2. Include alert in timing data
3. Continue execution (non-fatal)

## MODE Compatibility

**Step 1 (Python module):**
- PLAN Mode:  Safe (no file modifications)
- ACT Mode:  Also safe

**Step 2 (Metadata embedding):**
- PLAN Mode:  NOT safe (modifies output file)
- ACT Mode:  Required

## Next Step

Report completion summary in chat.
