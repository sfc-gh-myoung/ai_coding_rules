# Parallel Execution Workflow

Coordinator workflow for parallel dimension evaluation using sub-agents.

## Overview

> **Scoring Rubric v2.0:** 6 scored dimensions (100 points), Token Efficiency and Staleness are informational only.

This workflow enables parallel evaluation of rule dimensions by launching 5 sub-agents (one per non-deterministic scored dimension) while computing Rule Size inline.

```
Coordinator (Main Agent)
│
├── Phase 1: Setup
│   ├── Validate inputs (target_file, review_date, review_mode, model)
│   ├── Detect file type (rule vs project)
│   ├── Run schema validation (if rule file)
│   ├── Read rule content once
│   ├── Load overlap resolution rules
│   └── Prepare shared context
│
├── Phase 2: Parallel Dimension Evaluation (6 scored dimensions)
│   ├── INLINE: Rule Size (25pts, 100% deterministic - `wc -l`)
│   ├── SA-1: Actionability (30pts) [background]
│   ├── SA-2: Parsability (15pts) [background]
│   ├── SA-3: Completeness (15pts) [background]
│   ├── SA-4: Consistency (10pts) [background]
│   └── SA-5: Cross-Agent Consistency (5pts) [background]
│
├── Phase 3: Collect & Validate Results
│   ├── Gather 5 dimension worksheets + Rule Size result
│   ├── Verify no overlap violations
│   └── Flag any double-counted issues
│
└── Phase 4: Score Aggregation & Report
    ├── Apply scoring formula: Raw × Weight
    ├── Apply hard caps (line count, blocking issues)
    ├── Apply critical dimension override
    ├── Calculate total score (max 100)
    └── Generate unified review document
```

## Phase 1: Setup

### 1.1 Pre-Launch Validation

Before launching sub-agents, validate the rule file:

| Check | Condition | Action |
|-------|-----------|--------|
| File exists | `os.path.exists(rule_path)` returns false | **ERROR** - abort |
| File not empty | Size == 0 bytes | **ERROR** - abort |
| File readable | Cannot read file | **ERROR** - abort |
| File unusually small | Size < 500 bytes | **WARNING** - continue |
| YAML frontmatter | Does not start with `---` | **WARNING** - continue |
| Minimum structure | Fewer than 3 headers | **WARNING** - continue |

### 1.2 Input Validation

| Parameter | Required | Validation |
|-----------|----------|------------|
| `target_file` | Yes | Must be provided |
| `review_date` | Yes | Must match `YYYY-MM-DD` regex |
| `review_mode` | Yes | Must be FULL, FOCUSED, or STALENESS |
| `model` | No | Auto-detect from session |

### 1.3 File Type Detection

```bash
target_basename=$(basename "$target_file")

if [[ "$target_basename" =~ ^(AGENTS|PROJECT)\.md$ ]]; then
    FILE_TYPE="project"
    SKIP_SCHEMA=true
elif [[ "$target_file" == rules/*.md ]]; then
    FILE_TYPE="rule"
    SKIP_SCHEMA=false
else
    echo "ERROR: Target must be AGENTS.md, PROJECT.md, or rules/*.md"
    exit 1
fi
```

### 1.4 Load Shared Context

1. Read rule content once (store for all sub-agents)
2. Load overlap resolution rules from `rubrics/_overlap-resolution.md`
3. Get line count for Rule Size: `wc -l [target_file]`
4. Store: `rule_content`, `overlap_rules`, `line_count`, `file_type`, `target_file`

## Phase 2: Parallel Dimension Evaluation

### 2.1 Rule Size (Inline - 100% Deterministic)

Computed directly by coordinator (no LLM needed). Run `wc -l [rule_path]` and look up score:

| Lines | Raw Score | Points | Flag | Hard Cap |
|-------|-----------|--------|------|----------|
| ≤300 | 10 | 25 | None | - |
| 301-400 | 9 | 22.5 | None | - |
| 401-500 | 8 | 20 | None | - |
| 501-550 | 5 | 12.5 | `SPLIT_RECOMMENDED` | - |
| 551-600 | 3 | 7.5 | `SPLIT_REQUIRED` | - |
| 601-700 | 1 | 2.5 | `NOT_DEPLOYABLE` | Max 70/100 |
| >700 | 0 | 0 | `BLOCKED` | Max 50/100 |

### 2.2 Launch Sub-Agents

Launch 5 sub-agents using the Task tool, one per non-deterministic scored dimension:

| Sub-Agent | Dimension | Weight | Rubric Path |
|-----------|-----------|--------|-------------|
| SA-1 | Actionability | 3.0 | `rubrics/actionability.md` |
| SA-2 | Parsability | 1.5 | `rubrics/parsability.md` |
| SA-3 | Completeness | 1.5 | `rubrics/completeness.md` |
| SA-4 | Consistency | 1.0 | `rubrics/consistency.md` |
| SA-5 | Cross-Agent Consistency | 0.5 | `rubrics/cross-agent-consistency.md` |

**Launch procedure:**
1. For each dimension, generate a prompt containing: rubric content, rule content, overlap rules for that dimension, and review parameters

> **Note:** Each rubric file is self-contained — it includes the full counting protocol inline. No additional files (e.g., `_shared-preamble.md`) need to be loaded for sub-agents.
2. Launch via Task tool with `subagent_type="general-purpose"`, `run_in_background=True`
3. Wait 5 seconds between launches (API rate limit safety)
4. Track each agent ID, dimension name, weight, and status

### 2.3 Overlap Rules Per Dimension

Each sub-agent receives dimension-specific ownership rules extracted from `rubrics/_overlap-resolution.md`. See that file for the full priority rules mapping and issue type ownership matrix.

**Decision protocol for each sub-agent:**
1. Check if issue matches a priority rule (Rules 1-5 in order)
2. First matching rule determines ownership
3. If no rule match, use issue type matrix
4. If issue type not in matrix, default to Completeness
5. Document ownership decisions in `issues_deferred`

## Phase 3: Collect & Validate Results

### 3.1 Monitor Sub-Agent Progress

- Poll each agent every 30 seconds via `agent_output(agent_id)`
- Timeout: 90 seconds per agent
- On completion: parse dimension result (raw_score, evidence, issues)
- On failure: record error, continue collecting others
- On timeout: mark dimension incomplete, continue

### 3.1a: Collect Per-Dimension Timings (IF timing_enabled)

After collecting all sub-agent results, build the `_dimension_timings` array:

For each completed sub-agent result:
1. Extract `start_epoch` and `end_epoch` from the result JSON
2. Compute `duration_seconds = end_epoch - start_epoch`
3. Append to `_dimension_timings`:
   ```json
   {
     "dimension": result.dimension,
     "duration_seconds": round(duration_seconds, 2),
     "mode": "self-report",
     "start_epoch": result.start_epoch,
     "end_epoch": result.end_epoch
   }
   ```

For Rule Size (computed inline by coordinator):
- Record `start_epoch` before `wc -l` command
- Run `wc -l` on the target rule file
- If `wc -l` exits non-zero or produces no output:
  - Set `duration_seconds: -1`
  - Set `mode: "failed"`
  - Log: "WARNING: Rule Size inline measurement failed — wc -l returned non-zero"
- Else:
  - Record `end_epoch` after score lookup
  - Append with `"mode": "inline"` and computed duration

For failed/timed-out sub-agents:
- Append with `"duration_seconds": -1, "mode": "failed"`

### 3.2 Validate No Overlaps

After collecting all results:

1. Build a map of line numbers to (dimension, pattern) pairs across all results
2. For each line cited by multiple dimensions, determine the owner using the priority-based ownership rules
3. If a dimension claims a line it doesn't own, record a violation
4. Defer to the owning dimension's score for violations

**Ownership priority order** (first keyword match wins):
1. `schema`, `yaml`, `frontmatter` → Parsability
2. `undefined`, `ambiguous`, `verification` → Actionability
3. `contradict`, `inconsistent`, `mismatch` → Consistency
4. `redundant`, `duplicate` → Token Efficiency (informational)
5. `deprecated`, `outdated` → Staleness (informational)
6. `hardcoded` → Cross-Agent Consistency
7. `missing`, `error handling`, `edge case` → Completeness (default)

## Phase 4: Score Aggregation

See `score-aggregation.md` for detailed aggregation workflow.

### Timing Integration (IF timing_enabled)

Before calling `timing-end`, serialize `_dimension_timings` to JSON string:

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id {{_timing_run_id}} \
    --output-file {{output_file}} \
    --skill rule-reviewer \
    --format markdown \
    --dimension-timings '{{_dimension_timings_json}}'
```

## Threshold Rationale

| Value | Location | Rationale |
|-------|----------|-----------|
| **30s polling** | Phase 3 | Balance between responsiveness and API overhead |
| **90s timeout** | Phase 3 | 1.5x median dimension evaluation time |
| **5s launch delay** | Phase 2 | API rate limit safety margin |
| **5 sub-agents** | Phase 2 | 6 scored dimensions minus Rule Size (inline) |
| **Max 2 retries** | Error handling | Diminishing returns after 2 failures |

## Error Handling

| Scenario | Action |
|----------|--------|
| Sub-agent fails | Record error, continue collecting others, report partial results, recommend `execution_mode: sequential` |
| Sub-agent timeout | Kill agent, mark dimension incomplete, continue with available results, note missing dimensions |
| Overlap violations | Log each violation with line/dimension, defer to owning dimension, flag for review, note in report |

## Execution Mode Selection

```
IF execution_mode == "parallel":
    → Follow this workflow (parallel-execution.md)
ELSE:
    → Follow existing serial workflow in review-execution.md
```
