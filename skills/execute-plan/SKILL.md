---
name: execute-plan
description: Executes tasks from a plan file in order, mutating the plan file to record per-task progress so work is resumable across sessions. Use when running an approved implementation plan, resuming an interrupted plan, or driving a checklist-style work breakdown. Triggers on "execute plan", "run plan", "resume plan", "continue plan", "work the plan".
version: 1.0.0
---

# Execute Plan

## Purpose

Drives execution of a plan file's task checklist in order, updating per-task progress markers in the plan file itself after each step so the work is resumable across sessions. Confirms each task before mutating the codebase and pauses on failure.

## Use this skill when

- Executing an approved plan produced by `plan-creator`, `analyze-plan`, or hand-authored.
- Resuming a plan that was interrupted mid-flight.
- Running a long, multi-phase task list where session continuity matters.

Do not use for: ad-hoc one-off changes (use direct edits), plan authoring (use `plan-creator`), or plan auditing (use `analyze-plan`).

## Inputs

### Required

- `plan_file`: path — the plan document to execute.
  - **Default construction:** Same plan-discovery algorithm as `analyze-plan` — search `.snowflake/cortex/plans/`, `docs/plans/`, `./plans/`, repo root for `*.plan.md`; sort by mtime descending; prefill the most recent. Always present via `ask_user_question` with `type: "text"`, `defaultValue: <discovered-path>`.

### Optional

- `start_at`: string (default: first task marked `- [ ]` or `- [~]`) — task identifier or substring to resume from.
- `stop_after_phase`: integer (default: none) — stop after the named phase completes.
- `confirmation_mode`: `"per-task"` | `"per-phase"` | `"auto"` (default: `"per-task"`).
  - `auto` skips per-task confirmation; the plan author must have approved this mode explicitly.

## Outputs

The plan file is mutated in place using the [Progress Marker](#progress-marker-convention) syntax. No other files are written by this skill directly; the tasks themselves cause whatever code/doc changes the plan specifies.

## Progress Marker Convention

Every task line in the plan is expected to match `^- \[[ x~]\] ...`. The skill mutates only those lines.

| Marker | Meaning |
|---|---|
| `- [ ] Task description` | not started |
| `- [~] Task description` | in progress (cleared on completion or session interruption) |
| `- [x] (2026-06-21) Task description` | completed with ISO date |

Tasks may have nested sub-tasks indented by two spaces; the skill treats each indented item the same way.

## Workflow

### Phase 1 — Preflight

1. Resolve `plan_file` via discovery; confirm via `ask_user_question`.
2. Read the plan. Locate the first unchecked task at or after `start_at`.
3. If no unchecked tasks remain: report "Plan complete" and exit.
4. Print a short status block:
   - Plan path
   - Total tasks / completed / remaining
   - Next task to execute

### Phase 2 — Per-task loop

For each task in order:

1. If `confirmation_mode == "per-task"`: `ask_user_question` — `Run / Skip / Stop` with task text shown.
2. Mark the task `- [~]` (in progress) in the plan file. Save.
3. Execute the task.
4. On success: mark the task `- [x] (<today>)`. Save.
5. On failure: leave the task `- [~]` and append a single-line failure note immediately below the task as `  - failure: <message>`. Stop the loop. Report and exit.
6. If a phase boundary is crossed and `confirmation_mode == "per-phase"`: confirm before continuing.
7. If `stop_after_phase` is set and that phase has just completed: stop.

### Phase 3 — Closeout

1. Re-read the plan.
2. Print a final summary: tasks completed this session, tasks remaining, any `- [~]` markers left (these indicate interrupted or failed tasks).
3. If `**End of plan.**` is present in the file and all tasks are `- [x]`, report "Plan fully executed."

## Mutation Safety

- Only lines matching `^- \[[ x~]\]` are mutated.
- Surrounding markdown is preserved exactly (no reflowing, no heading edits, no whitespace normalization).
- Each mutation is a single-line `Edit` — never a wholesale file rewrite.
- An in-memory backup of the plan is held; if a mutation fails partway, the file is restored.

## Anti-patterns

- **Reflowing the plan.** This skill never reformats markdown beyond the marker line itself.
- **Silent skips.** Skipped tasks must still receive a marker update (`- [x] (date) [skipped: reason]` or remain `- [ ]` with an explicit user `Skip` choice logged in conversation).
- **Auto mode without an explicit opt-in.** If the user did not pass `confirmation_mode: auto`, do not silently switch to it.
- **Running past failures.** A failed task halts the loop; the user must intervene.

## Examples

**Invocation:**

> "Resume the prompts-to-skills plan from where I left off."

**Confirmation prompt (per-task default):**

```
Next task: "Scaffold 6 skill directories with SKILL.md + CHANGELOG.md"

[Run] [Skip] [Stop]
```

**Final summary:**

```
Plan: prompts-to-skills-conversion.plan.md
Session tasks completed: 3
Remaining: 5
In-progress markers: 0
```

## Version History

See [CHANGELOG.md](CHANGELOG.md).
