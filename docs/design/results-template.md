# Git-sourced install: validation results template

Copy this table into the PR or issue comment that reports a run of the [validation matrix](git-sourced-plugin-install.md#11-validation-matrix). Fill one row per matrix ID and client. Do not delete rows that were not run; leave them as NOT YET RUN.

Rules for filling it in:

- Status is PASS, FAIL or NOT YET RUN. A missing binary, a SKIPPED step, empty hook output or an unanswered question is FAIL.
- Record the source form actually used: `file://` clone, plain path, or GitHub shorthand.
- Record the exact client version from `--version`.
- Attach the `RESULT` line and every `FAIL` line from the matching `results/*.summary`. Redact secrets.
- Attach the output of `00-diff.sh`. Any change in the real `~/.claude`, `~/.codex` or `~/.snowflake` invalidates the run.

| Matrix ID | Client | Client version | Source form | Run by | Date | Status | Log path | Notes (FAIL lines, surprises, answers to V6 and V7 questions) |
|---|---|---|---|---|---|---|---|---|
| V0 | n/a | n/a | n/a | agent | | NOT YET RUN | | |
| V1 | Claude Code | | | human | | NOT YET RUN | | |
| V1 | Codex | | | human | | NOT YET RUN | | |
| V1 | CoCo CLI | | | human | | NOT YET RUN | | |
| V1b | Claude Code / Codex / CoCo CLI | | GitHub shorthand | human | | NOT YET RUN | | |
| V2 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V3 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V3b | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V4 (direct) | n/a | n/a | n/a | agent | | NOT YET RUN | | |
| V4 (client) | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V5 (direct) | n/a | n/a | n/a | agent | | NOT YET RUN | | |
| V5 (client) | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V6 | Claude Code / CoCo CLI | | | human | | NOT YET RUN | | |
| V7 | Codex | | | human | | NOT YET RUN | | |
| V8 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V9 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V10 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V11 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
| V12 | Claude Code / Codex / CoCo CLI | | | human | | NOT YET RUN | | |
