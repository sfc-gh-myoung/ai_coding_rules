# Gate 8 — Per-Dimension Timing rejection (skill-timer v2.0.0+)

**Verbatim contract.** This block is mirrored across local reviewer skills `rule-reviewer` and `bulk-rule-reviewer`. Do not edit per-skill copies independently; change all copies together in one commit.

## Rule

After `skill_timer.py end` returns, check the run-level `status` field:

- If `status ∈ {dimension_invalid, instrumentation_failed}`: **DO NOT publish** the "Per-Dimension Timing" markdown table. Instead emit:

  ```markdown
  > **Per-Dimension Timing rejected**
  >
  > Per-dimension timing data was rejected by skill-timer v2.0.0 due to
  > alerts: <comma-separated alert types>. See
  > `reviews/.timing-data/skill-timer-{run_id}-complete.json` for details.
  ```

- If `status ∈ {completed, warning}`: publish the table as before.
