# Reference: `dimension_timings`

Schema and validation rules for the `dimension_timings` input to `timing-end`. Linked from [`SKILL.md`](../SKILL.md) → Inputs.

## `dimension_timings` schema

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

## Validation gates

Validation gates applied automatically by `timing-end`:

- **Plausibility:** rejects if `end_epoch <= start_epoch` or timestamps fall outside execution window (±60s buffer).
- **Fabrication detection:** flags suspiciously round durations (exact 60s multiples ≥60s) or unusually long durations (>300s for a single dimension).
- **Outcomes:** `self-report` (passed), `self-report-flagged` (warning, accepted), `validation-failed` (rejected, duration set to -1).
