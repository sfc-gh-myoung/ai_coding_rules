# Reviewer Contract

Shared contract for the rule-review skill family (`rule-reviewer`, `bulk-rule-reviewer`)
and any skill that collects parameters interactively (`rule-creator`). This file is the
single source of truth for the passages below; consuming skills reference it rather than
restating it. Passages that already have a canonical owner are indexed under
[Canonical Sources](#canonical-sources), not duplicated here.

The reference convention is "read the linked file": there is no transclusion. Change this
file once; consumers pick it up by link.

## Parameter Collection

Applies to any skill that collects parameters interactively.

**Detection flow:**

```
IF required parameters missing:
    IF ask_user_question tool available:
        → use interactive question prompts
    ELSE:
        → fall back to text-based prompting
```

**Rules (MANDATORY):**

- Prompt for ALL parameters — required AND optional — in batched `ask_user_question` calls,
  **max 4 questions per call**.
- Do NOT silently apply defaults for optional parameters. The user must explicitly confirm
  each setting (the shown default may be accepted, but it must be shown and chosen).
- If `ask_user_question` is unavailable, fall back to text-based prompting: list each
  parameter, its options, and its default, then wait for the user to re-invoke with values.

Each consuming skill defines its own question sets (labels, options, header→parameter
mapping) in its `workflows/parameter-collection.md`; only the rules above are shared.

## Timing Integration (skill-timer)

Applies when `timing_enabled: true`. Shared mechanism only — each skill owns its own
checkpoint-name table (reviewer brackets each scored dimension with `dim_<name>_start/end`;
bulk brackets each rule/stage with `rule_<slug>_start/end` and stage checkpoints).

**Interpreter discovery + invocation:**

```bash
PYTHON=$(bash skills/skill-timer/scripts/find_python.sh)
SCRIPT=skills/skill-timer/scripts/skill_timer.py
$PYTHON $SCRIPT start   --skill <name> --target <path> --model <model> --mode <mode>
$PYTHON $SCRIPT checkpoint --run-id <run_id> --name <checkpoint>
$PYTHON $SCRIPT end     --run-id <run_id> --output-file <file> --skill <name> \
    --format markdown --auto-dimension-timings
```

`--auto-dimension-timings` derives the `dimension_timings` array from the recorded
`*_start/*_end` checkpoint pairs (sequential mode, preferred). Assemble an explicit
`--dimension-timings` JSON array only when aggregating sub-agent self-reports (parallel mode).

**Working-memory contract:** retain `_timing_run_id` and `_timing_stdout` from `start`
through the embed step. Requires skill-timer v2.0.0+.

**Per-command validation (MANDATORY):**

1. After `start`: stdout must contain `TIMING_RUN_ID=`. Missing → STOP, report timing failure.
2. After `checkpoint`: stdout must contain `CHECKPOINT_STATUS=recorded`. `missing` → note and continue.
3. After `end`: stdout must NOT contain `VALIDATION ERROR`. Check `PER_DIMENSION_STATUS=`:
   - `present` — explicit `--dimension-timings` accepted (parallel mode).
   - `derived` — auto-derived from checkpoint pairs (sequential mode, expected).
   - `missing` — FAIL: re-run with `--auto-dimension-timings` or document unavailability.
4. After file write: verify the `## Timing Metadata` section exists in the output file;
   if missing, append from `_timing_stdout`.

If ALL timing validation fails: write the review WITHOUT timing metadata and note
`**Timing data unavailable** — validation failed at step N`. Never block the review on a
timing failure.

**Anti-patterns (never do these):**

1. **Fabricated epochs.** Never invent timestamps to satisfy the schema. Capture real
   checkpoint pairs and let `--auto-dimension-timings` derive durations.
2. **Missing required fields.** Every explicit `dimension_timings` entry needs `dimension`,
   `duration_seconds`, and `mode`. Omitting `mode` → skill-timer strips the entry with a
   `VALIDATION ERROR`.
3. **Ignoring `VALIDATION ERROR`.** Treat it as fatal for the affected entry: log a warning,
   note it in the output, re-emit if recoverable, otherwise drop that entry and continue.
4. **Omitting `--auto-dimension-timings` / `--dimension-timings` at `end`.** Checkpoint pairs
   were recorded but neither flag is passed → the per-dimension section is silently omitted
   and the review fails its timing gate. Always pass one.

## Timing Opt-Out (reviewers only)

Reviewer skills (`rule-reviewer`, `bulk-rule-reviewer`) treat `timing_enabled: true` as the
default. Set `timing_enabled: false` to explicitly opt out; the Per-Dimension Timing section
is then satisfied by a single `not-requested` row rather than being absent.

This default is reviewer-scoped. Non-reviewer skills (e.g. `rule-creator`) set their own
`timing_enabled` default and do not use the `not-requested` row.

## Canonical Sources

Already-owned contracts — reference these, never restate them:

| Concern | Canonical source |
|---------|------------------|
| Verdict bands, scoring weights, hard caps | `skills/rule-reviewer/references/reviewer-defaults.yml` |
| Gate 8 (Per-Dimension Timing rejection) | `skills/rule-reviewer/references/gate-8.md` |
| No-overwrite / sequential `-01 -02` numbering | `skills/rule-reviewer/workflows/file-write.md` |
| JSON-is-authority (Markdown is derived output) | `docs/ARCHITECTURE.md` §3.6 |
