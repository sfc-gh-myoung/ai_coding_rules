---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using 6-dimension rubric and write results to reviews/rule-reviews/ with no-overwrite safety. Use when reviewing rule files, auditing rule quality, checking rule staleness, validating rule compliance, or analyzing agent executability.
version: 2.7.1
---

# Rule Reviewer

Execute comprehensive agent-centric reviews evaluating whether autonomous agents can execute rules without judgment calls.

## Quick Start

```
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

Output: `reviews/rule-reviews/200-python-core-claude-sonnet-45-2026-01-06.md`

(With `output_root: mytest/` → `mytest/rule-reviews/200-python-core-claude-sonnet-45-2026-01-06.md`)

## Scoring System (100 points)

> **Scoring Rubric v2.0** - 6 scored dimensions, 100 points total

**Raw Score Range:** 0-10 per dimension
**Formula:** Raw (0-10) × Weight = Points

**Scored Dimensions:**

| Dimension | Weight | Max Points | Focus |
|-----------|--------|------------|-------|
| Actionability | 3.0 | 30 | Can agents execute without judgment? |
| Rule Size | 2.5 | 25 | Within 500-line target? (deterministic) |
| Parsability | 1.5 | 15 | Schema valid? |
| Completeness | 1.5 | 15 | All scenarios covered? |
| Consistency | 1.0 | 10 | Internal alignment correct? |
| Cross-Agent Consistency | 0.5 | 5 | Works across all agents? |

**Informational Only (Not Scored):**
- **Token Efficiency** - Merged into Rule Size; findings in recommendations
- **Staleness** - Flagged in recommendations; not scored

**Hard Caps:**

| Condition | Effect |
|-----------|--------|
| >600 lines | Total score capped at 70/100 |
| >700 lines | Total score capped at 50/100 |
| ≥6 blocking issues | Total score capped at 80/100 |
| ≥10 blocking issues | Verdict forced to NOT_EXECUTABLE |

**Detailed rubrics:** `rubrics/[dimension].md`

**Example Calculation (Actionability):**
- Raw score: 8/10
- Weight: 3.0
- Points: 8 × 3.0 = 24 points

## Review Modes

- **FULL:** All 6 scored dimensions (100 points max)
- **FOCUSED:** Actionability + Completeness only (45 points max)
- **STALENESS:** Informational staleness check (not scored)

## Execution Discipline

**FOUNDATIONAL PRINCIPLE:** This skill prioritizes ACCURACY over efficiency. The user authorized this review knowing the scope. Proceed with the full process.

**Forbidden Behaviors:**
- Calculating or mentioning projected completion time
- Asking about time constraints mid-execution
- Proposing "faster" or "streamlined" alternatives
- Creating template-based reviews without analysis
- Estimating scores without consulting rubrics
- Skipping dimensions, schema validation, or Agent Execution Test
- Expressing concern about token costs or scope
- Abbreviating reviews to save tokens

**Required Behaviors:**
- Read the complete rule file (line 1 to END)
- Run schema validator (`uv run ai-rules validate`)
- Measure line count (`wc -l`)
- Consult rubrics for each scored dimension
- Generate specific recommendations with line numbers
- Write complete review (3000-8000 bytes for FULL mode)

**Skills vs Rules Distinction:**
- **Rules** are loaded 100s-1000s of times → token efficiency CRITICAL
- **Skills** are used occasionally → quality over efficiency, tokens IRRELEVANT
- Do NOT apply token-efficiency principles from rules to this skill's execution

**Self-Correction Triggers:** If you think or write "to save time", "for efficiency", "should I continue with", "would you prefer", or "let me create a streamlined" → STOP, re-read this section, resume comprehensive process silently.

**Pre-Execution Commitment:** Before starting ANY review, confirm you will NOT calculate projected time, NOT ask about time constraints, NOT create template-based reviews, NOT propose faster alternatives, and WILL read the file completely, consult rubrics, and write specific analysis.

## Workflow

**Execution Mode Selection:**
```
IF execution_mode == "parallel":
    → Follow workflows/parallel-execution.md (5 sub-agents)
ELSE:
    → Follow sequential workflow below
```

**Progress Display:** Show only `Starting: [rule-name]` and `Complete: [rule-name] → score/100`.
All canary checks, dimension scoring, and evidence gathering are INTERNAL (silent).

1. **Validate inputs**
   - Date format: YYYY-MM-DD
   - File exists (rules/*.md, AGENTS.md, or PROJECT.md)
   - Mode: FULL | FOCUSED | STALENESS

1a. **Collect ALL parameters** (use `ask_user_question`)
   
   **See:** `workflows/parameter-collection.md`
   
   **MANDATORY:** Prompt for ALL parameters in batched questions (max 4 per call):
   - Do NOT silently apply defaults for optional parameters
   - User must explicitly confirm each setting
   - If `ask_user_question` unavailable, fall back to text-based prompting

1b. **Detect file type**
   ```bash
   target_basename=$(basename "$target_file")
   
   if [[ "$target_basename" =~ ^(AGENTS|PROJECT)\.md$ ]]; then
       FILE_TYPE="project"
       SKIP_SCHEMA=true
       echo "File type: Project configuration (schema validation skipped)"
   elif [[ "$target_file" == rules/*.md ]]; then
       FILE_TYPE="rule"
       SKIP_SCHEMA=false
       echo "File type: Rule (full schema validation)"
   else
       echo "ERROR: Target must be AGENTS.md, PROJECT.md, or rules/*.md"
       exit 1
   fi
   ```

2. **Pre-Review Canary Check (SILENT - do not output)**
   Before reading the rule file, mentally verify:
   - What will I find in this rule? (RIGHT: "I don't know yet")
   - How long will this review take? (RIGHT: "However long it takes")
   - Can I reuse anything from previous work? (RIGHT: "No, different rule")
   
   **Any wrong answer → Re-read Anti-Optimization Protocol before proceeding**

3. **Run schema validation (conditional)**
   
   **IF FILE_TYPE == "rule":**
   ```bash
   uv run ai-rules validate [target_file]
   ```
   Parse output for CRITICAL/HIGH/MEDIUM errors
   
   **IF FILE_TYPE == "project":**
   ```bash
   echo "Schema validation skipped for project file"
   echo "Note: Project files use different structure than rule schema"
   ```
   Set schema_validation_result = "SKIPPED (project file)"
   
   **Rationale:** AGENTS.md and PROJECT.md are bootstrap/configuration files with different structure than domain rules. They don't use rule metadata (SchemaVersion, RuleVersion, TokenBudget) or rule sections (Scope, Contract, References).

4. **Agent Execution Test (SILENT - results go to review file)**
   Count blocking issues (≥6 caps score at 80/100, ≥10 forces NOT_EXECUTABLE):
   - Undefined thresholds ("large", "significant", "appropriate")
   - Missing conditional branches (no explicit else)
   - Ambiguous actions (multiple interpretations)
   - Visual formatting (ASCII art, arrows, diagrams)

5. **Post-Read Canary Check (SILENT - do not output)**
   After reading file, before scoring, verify internally:
   - Can name 3 specific things unique to THIS file
   - Can cite a specific line number with content
   - Know the exact TokenBudget value (rule files) OR file purpose (project files)
   
   **Unable to verify → Did not actually read → Re-read file**

6. **Score dimensions**
   Read rubrics/ as needed for each dimension:
   - `rubrics/actionability.md`
   - `rubrics/completeness.md`
   - `rubrics/consistency.md`
   - `rubrics/parsability.md`
   - `rubrics/token-efficiency.md`
   - `rubrics/rule-size.md` (100% deterministic - line count)
   - `rubrics/staleness.md`
   - `rubrics/cross-agent-consistency.md`
     - Includes documentation currency check via `web_fetch`
     - See `workflows/doc-currency-check.md` for details

7. **Mid-Review Canary (after dimension 3) (SILENT)**
   - Have I loaded the rubric for EACH dimension scored? (If NO → Go back)
   - Do my first 3 dimensions have distinct line references? (If NO → Find new evidence)
   
8. **Generate recommendations**
   - Specific line numbers
   - Quantified fixes
   - Expected score improvements

9. **Verify review authenticity**
   Before writing, verify review contains:
   - ≥15 line references (FULL mode)
   - Direct quotes with line numbers
   - Rule-specific findings (not generic)
   - See `workflows/review-verification.md`
   - Verify output matches `references/REVIEW-OUTPUT-TEMPLATE.md` structure
   - **FAILURE → Trigger reset: Re-read SKILL.md completely**

10. **Write review**
   Path: `{output_root}/rule-reviews/[rule-name]-[model]-[date].md`
   Auto-increment: `-01.md`, `-02.md` if exists (when overwrite=false)

**See workflows/** for detailed error handling

## Verdicts

**Score Ranges (100-point scale):**
- **90-100** - EXECUTABLE - Production-ready
- **75-89** - EXECUTABLE_WITH_REFINEMENTS - Good, minor fixes
- **50-74** - NEEDS_REFINEMENT - Needs work
- **<50** - NOT_EXECUTABLE - Major issues

**Hard Cap Overrides:**
- >600 lines → Total score capped at 70/100, verdict NEEDS_REFINEMENT or lower
- >700 lines → Total score capped at 50/100, verdict NOT_EXECUTABLE
- ≥6 blocking issues → Total score capped at 80/100
- ≥10 blocking issues → Verdict forced to NOT_EXECUTABLE

**Critical dimension override:** If both Actionability ≤4/10 AND Completeness ≤4/10 → NOT_EXECUTABLE regardless of total score

**Rule Size flags:**
- `SPLIT_RECOMMENDED` (501-550 lines) - Review for split opportunities
- `SPLIT_REQUIRED` (551-600 lines) - Mandatory split plan required
- `NOT_DEPLOYABLE` (601-700 lines) - Block deployment, hard cap 70/100
- `BLOCKED` (>700 lines) - Reject review, hard cap 50/100

## Supported File Types

**Rule Files (rules/*.md):**
- Domain-specific patterns and guidelines
- Loaded on-demand by agents
- Full schema validation against `schemas/rule-schema.yml`
- All 6 dimensions scored (100 points max)
- TokenBudget variance check applies

**Project Files (AGENTS.md, PROJECT.md):**
- Bootstrap and configuration documents
- Loaded once during project initialization
- Schema validation skipped (different structure than rules)
- All 6 dimensions scored (100 points max)
- TokenBudget variance skipped (no declared budget)
- Still evaluated for actionability, completeness, consistency, markdown quality, and currency

**Key Differences:**

| Aspect | Rule Files | Project Files |
|--------|------------|---------------|
| Schema validation | Full check | Skipped |
| Parsability scoring | Schema + markdown | Markdown only |
| Token efficiency | Budget variance + redundancy | Redundancy + structure only |
| Metadata required | 7 fields (SchemaVersion, etc.) | None |
| Section structure | Scope → Contract → Content | Custom per project |
| Max score | 100 points | 100 points |

**Both file types are agent-executable documents** - they just follow different schemas optimized for their architectural roles.

## Required Sections in Review

1. File Header (H1 + 5 metadata fields)
2. Executive Summary (score table + verdict block)
3. Schema Validation Results
4. Agent Executability Verdict
5. Dimension Analysis (6 subsections for FULL mode)
6. Critical Issues
7. Recommendations (with inline Staleness)
8. Post-Review Checklist (11 fixed items)
9. Conclusion
10. Timing Metadata (conditional)

**Authoritative template:** `references/REVIEW-OUTPUT-TEMPLATE.md`

## Inputs

- **target_file:** Path to file (e.g., `rules/200-python-core.md`, `AGENTS.md`, `PROJECT.md`)
- **review_date:** ISO 8601 format (YYYY-MM-DD)
- **review_mode:** FULL | FOCUSED | STALENESS
- **model:** Lowercase-hyphenated slug (e.g., `claude-sonnet-45`)
- **output_root:** (optional) Root directory for output files (default: `reviews/`). Subdirectory `rule-reviews/` is appended automatically. Supports relative paths including `../`.
- **overwrite:** (optional) true | false (default: false) - If true, overwrite existing review file. If false, use sequential numbering (-01, -02, etc.)
- **timing_enabled:** (optional) true | false (default: false)
- **execution_mode:** (optional) `parallel` | `sequential` (default: `parallel`)
  - `parallel`: Uses 5 sub-agents for scored dimension evaluation (faster, recommended for 8GB+ RAM)
  - `sequential`: Legacy single-agent behavior (for debugging or low-resource environments)

## Integration with Other Skills

### With bulk-rule-reviewer

bulk-rule-reviewer invokes this skill once per rule file. **Never** implement review logic yourself when bulk-rule-reviewer calls you.

### With skill-timing

**Execute IF:** `timing_enabled: true`  
**Skip IF:** `timing_enabled: false` (default)

**When enabled, execute ALL steps below (not optional once enabled):**

| When | Action | Command | Track |
|------|--------|---------|-------|
| Before review | Start timing | `$PYTHON skill_timing.py start --skill rule-reviewer --target {{target_file}} --model {{model}} --mode {{review_mode}}` | Store `_timing_run_id` |
| After schema validation | Checkpoint | `$PYTHON skill_timing.py checkpoint --run-id {{_timing_run_id}} --name skill_loaded` | - |
| After scoring complete | Checkpoint | `$PYTHON skill_timing.py checkpoint --run-id {{_timing_run_id}} --name review_complete` | - |
| Before file write | End timing | `$PYTHON skill_timing.py end --run-id {{_timing_run_id}} --output-file {{output_file}} --skill rule-reviewer --format markdown --dimension-timings '{{_dimension_timings_json}}'` | Store `_timing_stdout` |
| After file write | Embed | Append `_timing_stdout` to output file | - |

**Working memory contract:** Retain `_timing_run_id`, `_timing_stdout`, and `_dimension_timings` from start through embed.

**Per-dimension timing:** Skill-timing handles all timestamp capture, validation, and formatting. See `../skill-timing/SKILL.md` for the `--dimension-timings` schema and epoch capture methods. Rule-reviewer's only responsibility is passing the collected JSON array to `timing-end`.

**Quick Reference:**
```bash
PYTHON=$(bash skills/skill-timing/scripts/find_python.sh)
$PYTHON skills/skill-timing/scripts/skill_timing.py start \
    --skill rule-reviewer --target rules/200-python-core.md --model claude-sonnet-45 --mode FULL

$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id {{_timing_run_id}} --name skill_loaded

$PYTHON skills/skill-timing/scripts/skill_timing.py checkpoint \
    --run-id {{_timing_run_id}} --name review_complete

$PYTHON skills/skill-timing/scripts/skill_timing.py end \
    --run-id {{_timing_run_id}} \
    --output-file reviews/rule-reviews/200-python-core-claude-sonnet-45-2026-01-08.md \
    --skill rule-reviewer --format markdown
```

**Validation after each command (MANDATORY):**

1. **After `start`:** Output must contain `TIMING_RUN_ID=`. If missing → STOP, report timing failure.
2. **After `checkpoint`:** Output must contain `CHECKPOINT_STATUS=recorded`. If `missing` → note and continue.
3. **After `end`:** Output must NOT contain `VALIDATION ERROR`. If present → per-dimension data was auto-stripped, note "Per-dimension timing unavailable" in review. If `end` fails entirely → re-run with `--format markdown` or read `reviews/.timing-data/skill-timing-{run_id}-complete.json` directly.
4. **After file write:** Verify `## Timing Metadata` section exists in output file. If missing → append from `_timing_stdout`.

**If ALL timing validation fails:** Write the review WITHOUT timing metadata and note `**Timing data unavailable** - validation failed at step N`. Never block the review on timing failures.

**See:** `../skill-timing/SKILL.md` for timing implementation details, validation gates, dimension_timings schema, and epoch capture methods

## Error Handling

**Schema validator fails:**
- Continue review
- Note validation unavailable in Parsability section
- Recommend manual schema check

**Rule file not found:**
- Report: "File not found: [path]"
- Verify path and try again

**Review write fails:**
- Print: `OUTPUT_FILE: [path]`
- Print full review content
- User must save manually

**Documentation currency check fails:**
- If `web_fetch` unavailable: Skip currency check, note in review
- If >50% links timeout: Skip penalty, note "Currency check incomplete"
- If all links fail: Note "Unable to verify documentation currency - manual review recommended"
- Continue with remaining staleness scoring (LastUpdated, deprecated tools, patterns, link status)

**See:** `workflows/error-handling.md`

## No-Overwrite Safety

**When `overwrite: false` (default):**

If `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` exists:
- Try `-01.md`
- Try `-02.md`
- Increment until available (max: `-99.md`)
- If `-99.md` exists: STOP, report error `Maximum review versions exceeded for [rule-name]`

**When `overwrite: true`:**

The existing file at `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` will be replaced. Use this when intentionally re-running a review to replace a previous version.

## Progressive Disclosure

Don't load all rubrics at once. Read as needed:
- Scoring Actionability → Read `rubrics/actionability.md`
- Scoring Completeness → Read `rubrics/completeness.md`
- Etc.

Only load what you need for current dimension.

## Validation Checklists

**Pre-execution:**
- [ ] target_file exists
- [ ] review_date matches YYYY-MM-DD format
- [ ] review_mode is valid enum
- [ ] model slug is lowercase-hyphenated

**During execution:**
- [ ] Schema validation attempted
- [ ] Agent Execution Test completed
- [ ] Line count measured (`wc -l`)
- [ ] All dimensions scored (FULL mode - 6 dimensions)
- [ ] Recommendations include line numbers

**Post-execution:**
- [ ] Review file written
- [ ] Path confirmed
- [ ] No overwrites occurred

## Expected Review Size

Typical FULL mode review: 3000-8000 bytes

**Size validation:**
- If <2000 bytes: STOP, expand analysis with more specific findings
- If 2000-12000 bytes: Acceptable range
- If >12000 bytes: STOP, consolidate redundant content before writing

## Examples

See `examples/` for complete review samples:
- `full-review.md` - FULL mode walkthrough
- `focused-review.md` - FOCUSED mode example  
- `staleness-review.md` - STALENESS mode example
- `edge-cases.md` - Error scenarios

**Output template:** `references/REVIEW-OUTPUT-TEMPLATE.md` (authoritative fill-in skeleton)

## Related Skills

- **bulk-rule-reviewer:** Batch review orchestrator (uses this skill)
- **rule-creator:** Rule authoring (validated with this skill)
- **skill-timing:** Execution time measurement (optional integration)

## Quality Checklist

Before considering review complete:

- [ ] Schema validator executed
- [ ] Agent Execution Test performed
- [ ] Line count measured (`wc -l`)
- [ ] All required dimensions scored (6 for FULL mode)
- [ ] Each score has rationale
- [ ] Critical issues identified
- [ ] Rule Size flags applied if applicable
- [ ] Recommendations prioritized
- [ ] Line numbers provided for fixes
- [ ] Review written to {output_root}/rule-reviews/
- [ ] File path confirmed
- [ ] **Review file ≥2500 bytes (drift check)**

## Context Preservation (Bulk Reviews)

When invoked by `bulk-rule-reviewer`, this skill may experience context drift after 10-20 rules.

**Structural Safeguards:**

1. **Pre-write verification:** Check review has ≥15 line refs, score table, verdict before writing
2. **Post-write size check:** If <2500 bytes, flag potential drift
3. **Periodic refresh:** Every 10 rules, re-read `bulk-rule-reviewer/CRITICAL_CONTEXT.md`

**See:** `workflows/review-execution.md` Pre-Write Output Verification section

## Version History

- **v2.7.0:** Standardized review output template -- created references/REVIEW-OUTPUT-TEMPLATE.md as authoritative fill-in skeleton (opus-4-6 structure), integrated template loading into review-execution and file-write workflows, fixed 11-item Post-Review Checklist, standardized Executive Summary table columns (Raw (0-10) | Weight | Points | Max), inline Token Efficiency and Staleness, added structural validation gate (Step 5a) in file-write.md, added template compliance check in review-verification.md. Removed examples/TEMPLATE.md (superseded). Aligned weight notation to decimal across all files. Added Per-Dimension Timing subsection to REVIEW-OUTPUT-TEMPLATE.md (was missing from v2.6.0 template integration). (2026-03-27)
- **v2.6.0:** Added per-dimension timing support — sequential mode uses checkpoint pairs (`dim_{name}_start`/`dim_{name}_end`), parallel mode uses sub-agent self-reported `start_epoch`/`end_epoch`. New `--dimension-timings` flag on timing-end, `--per-dimension` on analyze/baseline. Requires skill-timing v1.4.0 (2026-03-27)
- **v2.5.3:** Cross-model consistency improvements — added Non-Issues Patterns 9-10 (tool names, checklists), domain applicability adjustment for completeness edge cases, expanded cross-agent "Do NOT Count" list, added overlap resolution for tool names, new calibration examples file (2026-03-25)
- **v2.5.2:** Fixed agent determinism regressions from v2.5.1 optimization (2026-03-24)
  - Inlined shared preamble into all 5 scored rubrics (eliminates cross-reference dependency for sub-agents)
  - Fixed Rule Size scoring table in parallel-execution.md (was using 6-tier simplified table instead of canonical 7-tier)
  - Restructured staleness deprecated tools from ambiguous inline `|` format to proper tables
  - Each scored rubric is now fully self-contained for sub-agent consumption
- **v2.5.1:** Optimization pass - compressed anti-optimization protocol, archived informational rubrics, deduplicated scoring matrices, extracted shared boilerplate, streamlined parameter collection and parallel execution
- **v2.5.0:** Added parallel execution mode with 5 sub-agents for scored dimension evaluation
- **v2.4.0:** Added documentation currency check to staleness dimension
- **v2.0.0:** Removed PROMPT.md, added progressive disclosure with rubrics/
- **v1.4.0:** Added timing integration, schema validation
- **v1.3.0:** Added FOCUSED and STALENESS modes
- **v1.2.0:** Added Agent Execution Test
- **v1.1.0:** Added no-overwrite safety
- **v1.0.0:** Initial release

## Determinism Requirements

**Purpose:** Reduce score variance from ±5-8 points to <±2 points across runs.

### Mandatory Behaviors (ALWAYS DO)

1. **Batch-load all rubrics BEFORE reading target rule** - See `workflows/review-execution.md` Phase 1
2. **Create ALL 8 inventories BEFORE reading target rule** - Empty templates from each rubric
3. **Read target rule from line 1 to END** - No skipping sections
4. **Fill inventories systematically** - One dimension at a time, in order
5. **Check Non-Issues list for EACH flagged item** - Remove false positives with notes
6. **Apply overlap resolution rules** - Assign each issue to ONE dimension only
7. **Use Score Decision Matrix for EVERY score** - Look up tier from count/percentage
8. **Include completed inventories in review output** - As evidence for scoring

### Prohibited Behaviors (NEVER DO)

1. **NEVER read target rule before loading rubrics** - Anchors interpretation incorrectly
2. **NEVER skip inventory creation** - Leads to inconsistent counting
3. **NEVER estimate scores without counting** - Creates variance
4. **NEVER double-count issues across dimensions** - Use overlap resolution
5. **NEVER flag items without checking Non-Issues list** - Creates false positives
6. **NEVER omit inventories from review output** - Prevents verification
7. **NEVER score on "feel" or "impression"** - Use decision matrices only
8. **NEVER start scoring before completing all inventories** - Order matters

### Expected Variance Tolerance

| Component | Expected Variance |
|-----------|-------------------|
| Issue counts per dimension | ±1 item |
| Dimension scores | ±1 point |
| Overall score | ±2 points |

**If variance exceeds tolerance:** Review inventory counting, check Non-Issues application, verify overlap resolution.

### Self-Verification Checklist

Before submitting ANY review, verify:

- [ ] All 9 rubric files read BEFORE reading target rule?
- [ ] All 8 inventories created (even if empty)?
- [ ] Line count measured (`wc -l`) for Rule Size?
- [ ] Target rule read line 1 to END (no skipping)?
- [ ] Each inventory filled using only rubric-defined patterns?
- [ ] Non-Issues list checked for EVERY flagged item?
- [ ] Overlap resolution applied to multi-dimension issues?
- [ ] All inventories included in review output?
- [ ] All scores from Score Decision Matrix lookups?

**If ANY checkbox is NO:** Review is INVALID. Regenerate from Phase 1.
