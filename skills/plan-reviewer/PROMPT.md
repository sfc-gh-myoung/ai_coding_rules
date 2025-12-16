# Plan Review Prompt (Template)

~~~~markdown
## Plan Review Request

**Target File(s):** [path/to/plan.md or list of paths]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** [FULL | COMPARISON | META-REVIEW]
**Reviewing Model:** [model-slug]

**Review Objective:** Evaluate LLM-generated plans for **autonomous agent executability**.
The winning plan must enable any agent to implement it successfully without human intervention.

### Dimension Weighting

Not all review dimensions have equal impact. Use these weights when calculating overall scores:

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| **Executability** | 2× | Critical - agent must execute without human intervention |
| **Completeness** | 2× | Critical - missing steps cause agent failure |
| **Success Criteria** | 2× | Critical - agent needs measurable completion signals |
| **Scope** | 2× | Critical - unbounded scope leads to drift and failure |
| Decomposition | 1× | Important but recoverable if tasks too large |
| Dependencies | 1× | Important but agents can often infer order |
| Context | 1× | Important but agents can request clarification |
| Risk Awareness | 1× | Nice-to-have, helps but not blocking |

**Weighted scoring formula:**
- Executability: X/5 × 2 = Y/10
- Completeness: X/5 × 2 = Y/10
- Success Criteria: X/5 × 2 = Y/10
- Scope: X/5 × 2 = Y/10
- Decomposition: X/5 × 1 = Y/5
- Dependencies: X/5 × 1 = Y/5
- Context: X/5 × 1 = Y/5
- Risk Awareness: X/5 × 1 = Y/5
- **Total: Z/60**

---

## Review Criteria (FULL Mode)

Analyze the plan against these criteria, scoring each 1-5 (5 = excellent):

### 1. Executability (Can an agent execute each step without human judgment?) — Weight: 2×

- Are all actions concrete and unambiguous?
- Are tool/command invocations explicit (exact commands, not descriptions)?
- Are there phrases requiring interpretation ("consider", "if appropriate", "as needed")?
- Are file paths absolute or clearly relative to a defined root?
- Can each step be executed programmatically?

**Scoring Scale:**
- **5/5:** 0-1 ambiguous phrases; all commands explicit; agent executes without clarification.
- **4/5:** 2-3 ambiguous phrases; 95%+ steps have explicit commands; minor inference needed.
- **3/5:** 4-7 ambiguous phrases; major steps clear but some require judgment.
- **2/5:** 8-15 ambiguous phrases; significant human interpretation required.
- **1/5:** >15 ambiguous phrases; plan reads as guidance, not instructions.

**Quantifiable Metrics (Critical Dimension):**
- Count phrases requiring interpretation ("consider," "if appropriate," "may need to")
- Count steps with explicit vs implicit commands
- Count undefined terms or placeholders

### 2. Completeness (Does the plan cover all necessary steps?) — Weight: 2×

- Are setup/prerequisites documented?
- Are validation steps between phases?
- Are teardown/cleanup steps included?
- Are error recovery steps explicit?
- Are edge cases addressed?

**Scoring Scale:**
- **5/5:** All phases have setup, validation, and cleanup; error recovery explicit; 0-1 gaps.
- **4/5:** Major phases complete; 2-3 minor gaps (e.g., missing cleanup for one phase).
- **3/5:** Core steps present; 4-5 gaps; no error recovery documented.
- **2/5:** Significant gaps; agent would need to infer multiple steps.
- **1/5:** Sparse outline; more gaps than content; not actionable.

**Quantifiable Metrics (Critical Dimension):**
- Count of phases with explicit validation steps
- Count of error recovery procedures
- Percentage of steps with verifiable outputs

### 3. Success Criteria (Are acceptance criteria clear and measurable?) — Weight: 2×

- Does each task have a verifiable completion signal?
- Are expected outputs explicitly specified?
- Can an agent determine "done" without human confirmation?
- Are success/failure states distinguishable programmatically?

**Scoring Scale:**
- **5/5:** Every task has measurable completion signal; outputs specified; agent-verifiable.
- **4/5:** 90%+ tasks have clear criteria; minor tasks lack explicit signals.
- **3/5:** Major milestones have criteria; individual tasks often lack them.
- **2/5:** Few explicit criteria; agent cannot self-verify completion.
- **1/5:** No measurable criteria; requires human judgment to assess completion.

**Quantifiable Metrics (Critical Dimension):**
- Percentage of tasks with explicit success criteria
- Count of tasks with programmatically verifiable outputs
- Count of tasks requiring human judgment to verify

### 4. Scope (Is the plan well-bounded with clear start/end?) — Weight: 2×

- Are boundaries explicit (what's in scope vs out of scope)?
- Is the starting state/prerequisites defined?
- Is the end state measurable and specific?
- Are scope creep risks identified?

**Scoring Scale:**
- **5/5:** Explicit in/out scope; defined start state; measurable end state; boundaries clear.
- **4/5:** Scope mostly clear; 1-2 boundary ambiguities; end state defined.
- **3/5:** General scope understood; several unclear boundaries; end state vague.
- **2/5:** Scope poorly defined; agent may over- or under-deliver significantly.
- **1/5:** No scope boundaries; open-ended; agent cannot determine completion.

**Quantifiable Metrics (Critical Dimension):**
- Explicit scope boundaries present? (Yes/No)
- Starting state defined? (Yes/No)
- End state measurable? (Yes/No)
- Count of scope ambiguities identified

### 5. Decomposition (Is task granularity appropriate?) — Weight: 1×

- Are tasks broken into single-action steps?
- Is granularity consistent across phases?
- Are complex tasks split appropriately?

**Scoring Scale:**
- **5/5:** All tasks are single-action; consistent granularity; no monolithic steps.
- **4/5:** Most tasks appropriately sized; 1-2 oversized tasks.
- **3/5:** Mixed granularity; some tasks need further decomposition.
- **2/5:** Many oversized tasks; agent would need to self-decompose.
- **1/5:** Monolithic tasks; no meaningful decomposition.

### 6. Dependencies (Are task order and blockers explicit?) — Weight: 1×

- Is task execution order clear?
- Are blocking dependencies identified?
- Are parallel-safe tasks marked?

**Scoring Scale:**
- **5/5:** All dependencies explicit; blocking relationships clear; parallel opportunities noted.
- **4/5:** Major dependencies clear; minor implicit ordering.
- **3/5:** Some dependencies stated; execution order inferable but not explicit.
- **2/5:** Dependencies unclear; agent may execute out of order.
- **1/5:** No dependency information; arbitrary execution order would fail.

### 7. Context (Is sufficient background provided for each task?) — Weight: 1×

- Is necessary context provided inline or referenced?
- Are domain-specific terms defined?
- Can an agent understand each task without external research?

**Scoring Scale:**
- **5/5:** All necessary context inline; terms defined; self-contained.
- **4/5:** Most context provided; 1-2 external references needed.
- **3/5:** Core context present; some domain knowledge assumed.
- **2/5:** Significant context missing; agent would need to research.
- **1/5:** Minimal context; requires extensive external knowledge.

### 8. Risk Awareness (Are potential blockers and fallbacks identified?) — Weight: 1×

- Are potential failure points identified?
- Are fallback strategies documented?
- Is rollback guidance provided?

**Scoring Scale:**
- **5/5:** Risks identified per phase; fallbacks documented; rollback strategy clear.
- **4/5:** Major risks identified; some fallback guidance.
- **3/5:** Risks mentioned but not systematically; limited fallback options.
- **2/5:** Few risks acknowledged; no fallback strategy.
- **1/5:** No risk awareness; agent has no recovery path.

---

## Output Format (FULL Mode)

Provide your assessment in this structure:

~~~markdown
## Plan Review: [plan-name.md]

**Plan:** [path/to/plan.md]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** FULL
**Reviewing Model:** [Model name and version]

---

### Scores (Weighted)
| Criterion | Weight | Raw | Weighted | Notes |
|-----------|--------|-----|----------|-------|
| Executability | 2× | X/5 | Y/10 | [brief justification] |
| Completeness | 2× | X/5 | Y/10 | [brief justification] |
| Success Criteria | 2× | X/5 | Y/10 | [brief justification] |
| Scope | 2× | X/5 | Y/10 | [brief justification] |
| Decomposition | 1× | X/5 | Y/5 | [brief justification] |
| Dependencies | 1× | X/5 | Y/5 | [brief justification] |
| Context | 1× | X/5 | Y/5 | [brief justification] |
| Risk Awareness | 1× | X/5 | Y/5 | [brief justification] |

**Overall:** X/60 (weighted)

### Overall Score Interpretation

| Score Range | Assessment | Verdict |
|-------------|------------|---------|
| 54-60/60 (90-100%) | Excellent | EXECUTABLE |
| 48-53/60 (80-89%) | Good | EXECUTABLE with minor refinements |
| 36-47/60 (60-79%) | Needs Work | NEEDS_REFINEMENT |
| 24-35/60 (40-59%) | Poor | NOT_EXECUTABLE |
| <24/60 (<40%) | Inadequate | NOT_EXECUTABLE - Rewrite required |

**Critical dimension overrides:**
- If Executability ≤2/5 → Verdict = "NEEDS_REFINEMENT" minimum
- If Completeness ≤2/5 → Verdict = "NEEDS_REFINEMENT" minimum
- If Success Criteria ≤2/5 → Verdict = "NEEDS_REFINEMENT" minimum
- If Scope ≤2/5 → Verdict = "NEEDS_REFINEMENT" minimum
- If 2+ critical dimensions ≤2/5 → Verdict = "NOT_EXECUTABLE"

### Agent Executability Verdict
**[EXECUTABLE | NEEDS_REFINEMENT | NOT_EXECUTABLE]**

[1-2 sentence summary of why this verdict was assigned]

### Critical Issues (Must Fix Before Agent Execution)
[List issues that would cause agent failure]

### Improvements (Should Fix)
[List issues that would improve agent success rate]

### Minor Suggestions (Nice to Have)
[List optimizations that don't affect executability]

### Specific Recommendations
For each issue:
1. **Location:** Line number or section name
2. **Problem:** What's wrong and why it blocks agent execution
3. **Recommendation:** Specific fix with example
~~~

---

## Mandatory Verification Tables (FULL Mode)

### Executability Audit (Required for Executability scoring)

Scan the plan for phrases requiring human judgment:

~~~markdown
**Executability Audit:**

| Phrase | Line(s) | Issue | Proposed Fix |
|--------|---------|-------|--------------|
| "consider using" | 45 | Requires judgment | "use X" (concrete command) |
| "if appropriate" | 89 | Conditional undefined | "if [condition], then..." |
| "as needed" | 123 | Undefined trigger | "when [event], do [action]" |

**Ambiguous Phrase Count:** N
**Steps with Explicit Commands:** X/Y (Z%)
~~~

**Scoring impact:** >10 ambiguous phrases → Executability ≤2/5

### Completeness Audit (Required for Completeness scoring)

~~~markdown
**Completeness Audit:**

| Phase | Setup | Validation | Cleanup | Error Recovery |
|-------|-------|------------|---------|----------------|
| Phase 1 | ✅ | ✅ | ❌ | ❌ |
| Phase 2 | ✅ | ✅ | ✅ | ⚠️ Partial |

**Phases with Full Coverage:** X/Y
**Missing Elements:** [list]
~~~

**Scoring impact:** <60% phases complete → Completeness ≤3/5

### Success Criteria Audit (Required for Success Criteria scoring)

~~~markdown
**Success Criteria Audit:**

| Task/Milestone | Has Criteria? | Verifiable by Agent? | Notes |
|----------------|---------------|---------------------|-------|
| Task 1.1 | ✅ | ✅ | "grep returns 0 matches" |
| Task 1.2 | ✅ | ❌ | "looks correct" - subjective |
| Phase 1 Complete | ✅ | ✅ | "pytest passes" |

**Tasks with Criteria:** X/Y (Z%)
**Agent-Verifiable:** A/B (C%)
~~~

**Scoring impact:** <70% agent-verifiable → Success Criteria ≤3/5

---

## Scoring Impact Rules (Algorithmic Overrides)

These rules override subjective assessment:

### Executability (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| >15 ambiguous phrases | 1/5 |
| 8-15 ambiguous phrases | 2/5 |
| 4-7 ambiguous phrases | 3/5 |
| 2-3 ambiguous phrases | 4/5 |
| 0-1 ambiguous phrases | 5/5 |

### Completeness (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| <40% phases with validation | 1/5 |
| 40-60% phases with validation | 2/5 |
| 60-80% phases with validation | 3/5 |
| 80-95% phases with validation | 4/5 |
| >95% phases with validation | 5/5 |

### Success Criteria (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| <50% tasks with criteria | 1/5 |
| 50-70% tasks with criteria | 2/5 |
| 70-85% tasks with criteria | 3/5 |
| 85-95% tasks with criteria | 4/5 |
| >95% tasks with criteria | 5/5 |

### Scope (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| No scope boundaries defined | 1/5 |
| Partial boundaries, no end state | 2/5 |
| Boundaries defined, vague end state | 3/5 |
| Clear boundaries, measurable end state | 4/5 |
| Explicit in/out, start/end, no ambiguity | 5/5 |

---

## Scoring Decision Matrix

| Scenario | Resolution | Rationale |
|----------|------------|-----------|
| Phrase count at boundary (e.g., exactly 4) | Use lower score | Conservative for agent reliability |
| Implicit validation (command returns exit code) | Counts as validation | Standard shell convention |
| Success criteria in prose, not checklist | Counts if specific | Format less important than clarity |
| Scope defined elsewhere (e.g., linked doc) | Partial credit (3/5 max) | Self-contained plans preferred |
| Risk section absent but risks noted inline | Partial credit | Consolidated section preferred |

---

## Inter-Rater Reliability Guidelines

To ensure consistent scoring across models and runs:

1. **Apply Scoring Impact Rules first** — algorithmic overrides take precedence
2. **Use verification tables** — scores must be supported by audit evidence
3. **Cite line numbers** — all findings must reference specific locations
4. **Document edge case decisions** — use Notes column for judgment calls
5. **When uncertain between scores** — default to lower score; cite specific gap

**Calibration process:**
- Count findings mechanically (phrases, validation coverage, etc.)
- Apply Scoring Impact Rules table
- Adjust only if qualitative factors strongly justify (document reasoning)

---

## Plan Perspective Checklist (REQUIRED)

Answer each question explicitly:

- [ ] **Agent execution test:** Could an autonomous agent execute this plan end-to-end
  without asking for clarification? (Yes/No with explanation)
  - *Scoring impact:* No → Executability ≤3/5
- [ ] **Ambiguity count:** How many phrases require human interpretation?
  - *Scoring impact:* Per Executability Scoring Impact Rules
- [ ] **Validation coverage:** What percentage of phases have explicit validation steps?
  - *Scoring impact:* Per Completeness Scoring Impact Rules
- [ ] **Success criteria coverage:** What percentage of tasks have agent-verifiable
  completion criteria?
  - *Scoring impact:* Per Success Criteria Scoring Impact Rules
- [ ] **Scope clarity:** Are start state, end state, and boundaries explicit?
  - *Scoring impact:* Per Scope Scoring Impact Rules

---

## COMPARISON Mode

Use when evaluating multiple plans for the same task.

### Inputs
- `target_files`: List of 2+ plan file paths
- `task_description`: Brief description of what plans should accomplish

### Output Format

~~~markdown
## Plan Comparison: [task-description]

**Task:** [Brief description]
**Review Date:** [YYYY-MM-DD]
**Reviewing Model:** [Model name]

### Plans Reviewed
| # | Plan File | Created By | Lines |
|---|-----------|------------|-------|
| A | [plan-a.md] | [model/author] | 250 |
| B | [plan-b.md] | [model/author] | 180 |

---

### Comparative Scores
| Criterion | Weight | Plan A | Plan B | Winner |
|-----------|--------|--------|--------|--------|
| Executability | 2× | 8/10 | 6/10 | A |
| Completeness | 2× | 9/10 | 8/10 | A |
| Success Criteria | 2× | 7/10 | 9/10 | B |
| Scope | 2× | 8/10 | 7/10 | A |
| Decomposition | 1× | 4/5 | 5/5 | B |
| Dependencies | 1× | 5/5 | 4/5 | A |
| Context | 1× | 4/5 | 4/5 | Tie |
| Risk Awareness | 1× | 3/5 | 4/5 | B |
| **Total** | | **48/60** | **47/60** | **A** |

### Verdict by Plan
| Plan | Score | Verdict |
|------|-------|---------|
| A | 48/60 | EXECUTABLE |
| B | 47/60 | EXECUTABLE |

### Head-to-Head Analysis

**Executability:** Plan A wins
- A: All commands explicit; zero ambiguous phrases
- B: 3 instances of "consider" requiring interpretation

**Completeness:** Plan A wins
- A: All 6 phases have validation and cleanup
- B: Phase 4 missing validation step

[Continue for each dimension with specific evidence]

### Recommendation

**Winner:** Plan A (48/60)

**Rationale:** Plan A is more immediately executable by an autonomous agent due to:
1. Zero ambiguous phrases vs 3 in Plan B
2. Complete validation coverage (100% vs 83%)
3. Explicit error recovery in all phases

**When to use Plan B instead:** If the task prioritizes [specific scenario],
Plan B's [strength] may be preferable.
~~~

---

## META-REVIEW Mode

Use when evaluating the quality and consistency of review files.

### Purpose
Analyze multiple reviews of the same document to:
1. Identify scoring variance between reviewers
2. Assess review thoroughness and calibration
3. Determine which review is most reliable
4. Calculate consensus score

### Inputs
- `target_files`: List of 2+ review files for the same document
- `original_document`: Path to the document being reviewed (optional)

### META-REVIEW Dimensions (4 dimensions, /20 total)

| Dimension | Weight | Focus |
|-----------|--------|-------|
| **Thoroughness** | 1× | Did review check all required elements? |
| **Evidence Quality** | 1× | Are scores supported by specific citations? |
| **Calibration** | 1× | Does scoring match rubric definitions? |
| **Actionability** | 1× | Are recommendations specific and implementable? |

### Output Format

~~~markdown
## Meta-Review: [document-name] Reviews

**Document Reviewed:** [path/to/original.md]
**Review Date:** [YYYY-MM-DD]
**Reviewing Model:** [Model name]
**Reviews Analyzed:** [N]

---

### Reviews Summary
| Review File | Model | Score | Critical Issues | Lines |
|-------------|-------|-------|-----------------|-------|
| [review-a.md] | Claude Sonnet 4.5 | 45/45 | 0 | 340 |
| [review-b.md] | GPT-5.2 | 37/45 | 2 | 186 |
| [review-c.md] | Claude Opus 4.5 | 44/45 | 0 | 280 |

**Score Variance:** 8 points (17.8% spread)

---

### Consistency Analysis

| Metric | Value | Assessment |
|--------|-------|------------|
| Score spread | 8 points | ⚠️ High variance (>10% = investigate) |
| Critical issues agreement | 1/3 reviews | ⚠️ Low consensus |
| Verification table presence | 3/3 reviews | ✅ Consistent methodology |
| Line citations | 2/3 reviews | ⚠️ One review lacks specifics |

### Issue Detection Comparison
| Issue | Review A | Review B | Review C | Consensus |
|-------|----------|----------|----------|-----------|
| [Issue 1] | ❌ | ✅ | ❌ | 1/3 |
| [Issue 2] | ❌ | ✅ | ❌ | 1/3 |
| [Issue 3] | ✅ | ✅ | ✅ | 3/3 |

**Issue Detection Rate:**
- Review A: 1/3 issues (33%)
- Review B: 3/3 issues (100%)
- Review C: 1/3 issues (33%)

---

### Meta-Review Scores
| Review | Thoroughness | Evidence | Calibration | Actionability | Total |
|--------|--------------|----------|-------------|---------------|-------|
| A | 4/5 | 5/5 | 3/5 | 4/5 | 16/20 |
| B | 5/5 | 4/5 | 5/5 | 5/5 | 19/20 |
| C | 4/5 | 5/5 | 4/5 | 4/5 | 17/20 |

### Calibration Assessment

**Most Thorough:** Review B (found all issues)
**Most Generous:** Review A (no critical issues identified)
**Best Calibrated:** Review B (issues align with rubric criteria)

**Calibration Issues Found:**
- Review A: Scored 5/5 on Accuracy despite [specific gap]
- Review C: Inconsistent application of Scoring Impact Rules

---

### Consensus Determination

**Method:** Weighted average adjusted for calibration confidence

| Review | Score | Calibration Weight | Weighted Contribution |
|--------|-------|-------------------|----------------------|
| A | 45/45 | 0.80 | 36.0 |
| B | 37/45 | 1.00 | 37.0 |
| C | 44/45 | 0.90 | 39.6 |

**Consensus Score:** 40/45 (weighted average)
**Confidence:** Medium (high variance indicates potential rubric ambiguity)

---

### Recommendation

**Most Reliable Review:** Review B (GPT-5.2)
- Highest issue detection rate (100%)
- Best calibration with rubric definitions
- Most actionable recommendations

**Action Items:**
1. Investigate why Reviews A/C missed [Issue 1] and [Issue 2]
2. Consider rubric clarification for [specific dimension]
3. Use Review B as calibration example for future reviews
~~~

---

## Output Guidelines

- **Target length:**
  - FULL mode: 200-400 lines
  - COMPARISON mode: 150-300 lines
  - META-REVIEW mode: 150-250 lines
- **Evidence required:** All scores must cite line numbers or specific content
- **Recommendations:** Include concrete fixes, not just problem descriptions
- **Prioritization:** Group issues by impact on agent executability

---

## Output File (REQUIRED)

Save review output to `reviews/` using these formats:

**FULL mode:**
`reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md`

**COMPARISON mode:**
`reviews/plan-comparison-<model>-<YYYY-MM-DD>.md`

**META-REVIEW mode:**
`reviews/meta-<document-name>-<model>-<YYYY-MM-DD>.md`

**No overwrites:** If file exists, append `-01.md`, `-02.md`, etc.

Example:
- Plan file: `plans/IMPROVE_RULE_LOADING.md`
- Model: Claude Sonnet 4.5
- Date: 2025-12-16
- Output: `reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

If file writing fails, output:
`OUTPUT_FILE: reviews/plan-<name>-<model>-<date>.md`
followed by full review content.
<!-- End of prompt template -->
<!-- EOF -->
~~~~

