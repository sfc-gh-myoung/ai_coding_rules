# Scoring Formula and Verdict Thresholds

## Scoring Formula

**Raw Score Range:** 0-10 per dimension
**Formula:** Raw (0-10) × (Weight / 2) = Points

**Total: 100 points weighted across 8 dimensions:**

**Critical Dimensions (75 points - agent must execute without human intervention):**
- **Executability** - Raw: X/10, Weight: 4, Points: Y/20
- **Completeness** - Raw: X/10, Weight: 4, Points: Y/20
- **Success Criteria** - Raw: X/10, Weight: 4, Points: Y/20
- **Scope** - Raw: X/10, Weight: 3, Points: Y/15

**Standard Dimensions (25 points - important but recoverable):**
- **Dependencies** - Raw: X/10, Weight: 2, Points: Y/10
- **Decomposition** - Raw: X/10, Weight: 1, Points: Y/5
- **Context** - Raw: X/10, Weight: 1, Points: Y/5
- **Risk Awareness** - Raw: X/10, Weight: 1, Points: Y/5

## Dimension Summaries

**1. Executability (20 points) - Can agent execute each step?**
- Measures: Explicit commands, ambiguous phrases, undefined thresholds
- Key gate: >15 ambiguous phrases caps at 2/10

**2. Completeness (20 points) - Are all steps covered?**
- Measures: Setup, validation, cleanup, error recovery
- Key gate: No error recovery caps at 4/10

**3. Success Criteria (20 points) - Are completion signals clear?**
- Measures: Verifiable outputs, measurable criteria, agent-testable
- Key gate: <50% tasks with criteria caps at 4/10 (Count: Tasks with verifiable success criteria / Total tasks in plan)

**4. Scope (15 points) - Is work bounded?**
- Measures: Scope definition, exclusions, termination conditions
- Key gate: Unbounded scope caps at 4/10

**5. Dependencies (10 points) - Are prerequisites clear?**
- Measures: Tool/package requirements, ordering, access needs

**6. Decomposition (5 points) - Are tasks right-sized?**
- Measures: Task granularity, parallelizable steps

**7. Context (5 points) - Does plan explain why?**
- Measures: Rationale provided, context preserved

**8. Risk Awareness (5 points) - Are risks documented?**
- Measures: Failure scenarios, mitigation strategies

## Agent Execution Test (Pre-Scoring Gate)

Before scoring, answer: **"Can an autonomous agent execute this plan end-to-end without asking for clarification?"**

Count blocking issues:
1. Ambiguous phrases ("consider", "if appropriate", "as needed")
2. Implicit commands (described not specified)
3. Missing branches (no explicit else/default/error handling)
4. Undefined thresholds ("large", "significant", "appropriate")

**Impact:**
- Blocking issues ≥10: Max score = 60/100 (NEEDS_REFINEMENT)
- Blocking issues ≥20: Max score = 40/100 (NOT_EXECUTABLE)

**See:** `executability.md` for blocking issue criteria

## Verdict Thresholds

**Score Ranges:**
- **90-100** - EXCELLENT_PLAN - Ready for execution
- **80-89** - GOOD_PLAN - Minor refinements needed
- **60-79** - NEEDS_WORK - Significant refinement required
- **40-59** - POOR_PLAN - Not executable, major revision
- **<40** - INADEQUATE_PLAN - Rewrite from scratch

**Critical dimension overrides:**
- Executability ≤4/10 → Minimum NEEDS_WORK
- Completeness ≤4/10 → Minimum NEEDS_WORK
- Success Criteria ≤4/10 → Minimum NEEDS_WORK
- 2+ critical dimensions ≤4/10 → POOR_PLAN
