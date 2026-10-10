# Reference: Integration Pattern

How a calling skill adds timing instrumentation. Linked from [`SKILL.md`](../SKILL.md) → Integration Pattern.

## Workflow step to add

Add this step to your skill's workflow:

```markdown
### [CONDITIONAL] Timing Instrumentation

**Execute IF:** `timing_enabled: true`
**Skip IF:** `timing_enabled: false`

| When | Action | Track Variable |
|------|--------|----------------|
| Before core work | timing-start | `_timing_run_id` |
| After Gate 1 | checkpoint: gates_started | - |
| After Gate 3 | checkpoint: rules_loaded | - |
| After setup | checkpoint: skill_loaded | - |
| After core work | checkpoint: work_complete | - |
| Before file write | timing-end --format markdown | `_timing_stdout` |
| After file write | Append `_timing_stdout` to file | - |
```

## Per-Dimension Timing (optional)

- **Sequential mode (preferred):** record `dim_{name}_start` / `dim_{name}_end` checkpoint pairs around each dimension; call `timing-end --auto-dimension-timings` to derive the array.
- **Parallel mode:** sub-agents self-report `start_epoch` / `end_epoch`; coordinator assembles and passes via `--dimension-timings`.
- **Explicit override:** `--dimension-timings` wins over `--auto-dimension-timings`.
- **Precision:** capture fractional epochs with `python3 -c "import time; print(time.time())"`.

Field schema and validation gates for `--dimension-timings`: [`dimension-timings.md`](dimension-timings.md).
