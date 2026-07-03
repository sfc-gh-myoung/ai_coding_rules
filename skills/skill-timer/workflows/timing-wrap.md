# timing-wrap (v2.0.0+)

The `wrap` subcommand atomically captures a per-dimension duration with a
**server-side end timestamp**, eliminating the failure mode where an agent
emits two checkpoint commands back-to-back and collapses the measured duration.

## When to use

For every per-dimension analysis in a multi-dimension local reviewer skill
(`rule-reviewer` or `bulk-rule-reviewer`). Replaces
the legacy `dim_<name>_start` / `dim_<name>_end` checkpoint pattern.

## Contract

```bash
python skills/skill-timer/scripts/skill_timer.py wrap \
    --run-id <id> \
    --dimension <name> \
    --evidence <path-or-dash> \
    [--start-epoch <float>] \
    [--start-monotonic <float>] \
    [--mode wrap|inline]
```

- `--evidence` is **mandatory**. It must be a file path containing the
  per-dimension worksheet draft you just produced, or `-` to read from stdin.
  Defaults reject inputs smaller than **100 bytes** (configurable via
  `reviews/.timing-thresholds.json` `min_evidence_bytes`).
- `end_epoch` is assigned by skill-timer at the moment of the call. The agent
  cannot fabricate it.
- `--start-epoch` / `--start-monotonic` default to:
  1. The previous `wrap` entry's `end_epoch` / `end_monotonic`, if any.
  2. The run's `start_epoch` / `start_monotonic`, otherwise.
- `--mode` defaults to `wrap`. Use `inline` for deterministic synchronous
  capture from a coordinator process.

## Example

```bash
RUN_ID=$(python skill_timer.py start --skill rule-reviewer --target rules/x.md \
    --model claude-opus-4 --mode FULL | grep -oE 'TIMING_RUN_ID=[a-f0-9]+' | cut -d= -f2)

# ... do executability analysis, write worksheet to disk ...
python skill_timer.py wrap --run-id $RUN_ID --dimension executability \
    --evidence /tmp/exec-worksheet.md

# ... do completeness analysis ...
python skill_timer.py wrap --run-id $RUN_ID --dimension completeness \
    --evidence /tmp/complete-worksheet.md

# ... continue for remaining dimensions ...
```

## Failure modes

- **`evidence_too_small`**: file/stdin under 100 bytes. Exit 4
  (`EXIT_INSTRUMENTATION_FAILED`).
- **Negative duration**: clock skew detected. Exit 1.
- **Run not found**: invalid `--run-id`. Exit 1.

## Compared to legacy `dim_*` checkpoints

| Concern | Legacy `dim_*` | `wrap` |
|---|---|---|
| Atomicity | Two separate commands | Single command |
| End timestamp | Agent-supplied | Server-side |
| Evidence requirement | None | Mandatory ≥100B |
| Mode label | `checkpoint` | `wrap` |
| Backward compat | Still parsed; emits deprecation WARNING | Native v2.0.0 path |
