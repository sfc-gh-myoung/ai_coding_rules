# Edge Cases and Resolutions

This document covers ambiguous scenarios and how to resolve them when reviewing plans.

## Executability Edge Cases

### Case 1: Implicit Commands

**Scenario:** Plan says "Run the tests" without specifying the command.

**Resolution:** Score as ambiguous (counts toward limit).

**Justification:** An agent cannot determine whether to run `pytest`, `npm test`, `make test`, etc.

**Better version:** "Run `pytest tests/ -v`"

---

### Case 2: Conditional Without Defined Trigger

**Scenario:** "If necessary, restart the service."

**Resolution:** Score as ambiguous.

**Justification:** Agent cannot determine when "necessary" is true.

**Better version:** "If `curl http://localhost:8080/health` returns non-200, run `systemctl restart app`"

---

### Case 3: Shell Exit Codes as Validation

**Scenario:** Plan says "Verify grep finds matches" without explicit success criteria.

**Resolution:** Accept if command is explicit; exit code 0 is implicit success.

**Justification:** Standard shell convention - agents understand exit codes.

**Note:** This is documented in Scoring Decision Matrix.

---

### Case 4: Ambiguous Phrase in Comment

**Scenario:** Code comment says "consider optimizing this later" but task is explicit.

**Resolution:** Do not count as ambiguous.

**Justification:** Comments are not executable instructions; task clarity is what matters.

---

## Completeness Edge Cases

### Case 5: Cleanup Not Applicable

**Scenario:** A read-only analysis phase has no cleanup step.

**Resolution:** Mark as N/A, do not penalize.

**Justification:** Completeness audit should reflect reality; not all phases have cleanup.

---

### Case 6: Error Recovery Deferred to Global Handler

**Scenario:** Plan says "See Error Handling section for all recovery procedures."

**Resolution:** Accept if error handling section exists and is comprehensive.

**Justification:** Centralized error handling is valid architecture.

---

### Case 7: External Prerequisites

**Scenario:** Plan assumes database is already running.

**Resolution:** Partial credit unless starting state is documented.

**Justification:** Prerequisites should be explicit; "database running" could mean various states.

---

## Success Criteria Edge Cases

### Case 8: Subjective Success Criteria

**Scenario:** "Verify the output looks correct."

**Resolution:** Does not count as agent-verifiable.

**Justification:** "Looks correct" requires human judgment.

**Better version:** "Verify `diff expected.txt output.txt` returns empty"

---

### Case 9: Criteria in Prose, Not Checklist

**Scenario:** Success criteria embedded in paragraph text rather than bullet points.

**Resolution:** Accept if criteria are specific and measurable.

**Justification:** Format is less important than clarity; agents can parse prose.

---

### Case 10: Implicit Success via No Errors

**Scenario:** "Task succeeds if no errors are thrown."

**Resolution:** Accept as agent-verifiable.

**Justification:** Exit code 0 and no stderr output is programmatically verifiable.

---

## Scope Edge Cases

### Case 11: Scope Defined in Linked Document

**Scenario:** Plan references "See requirements.md for scope."

**Resolution:** Partial credit (max 3/5 for Scope).

**Justification:** Self-contained plans preferred; external dependencies reduce agent reliability.

---

### Case 12: Open-Ended Enhancement

**Scenario:** Plan includes "and any other improvements identified during implementation."

**Resolution:** Penalize Scope score.

**Justification:** Unbounded scope leads to drift; agent cannot determine completion.

**Better version:** Remove open-ended language or explicitly list acceptable enhancements.

---

### Case 13: Rolling End State

**Scenario:** "Continue until all tests pass."

**Resolution:** Accept if test suite is defined.

**Justification:** Bounded by test suite; agent can verify completion.

---

## META-REVIEW Edge Cases

### Case 14: Reviews Use Different Rubrics

**Scenario:** One review used 6-dimension rubric, another used 8-dimension.

**Resolution:** Compare only common dimensions; flag incompatible dimensions.

**Output example:**
```
⚠️ Dimension mismatch detected:
- Review A: 8 dimensions
- Review B: 6 dimensions
Comparing only common dimensions; Risk Awareness and Context excluded from comparison.
```

---

### Case 15: Extreme Score Variance

**Scenario:** Same document scored 92/100 by one model and 58/100 by another.

**Resolution:**
1. Flag as high variance (>30 points)
2. Examine methodology differences
3. Check if one review missed major sections
4. Do not calculate simple consensus; investigate first

---

### Case 16: All Reviews Agree on Wrong Score

**Scenario:** All 3 reviews score Executability 5/5 but plan has 8 ambiguous phrases.

**Resolution:** Note calibration failure across all reviews.

**Output example:**
```
⚠️ Calibration anomaly detected:
All reviews scored Executability 5/5, but verification found 8 ambiguous phrases.
Per Scoring Impact Rules, maximum score should be 2/5.
Consensus score adjusted accordingly.
```

---

## Comparison Mode Edge Cases

### Case 17: Plans for Different Scopes

**Scenario:** Plan A covers auth + user management; Plan B covers only auth.

**Resolution:** Cannot compare directly; note scope mismatch.

**Output example:**
```
⚠️ Scope mismatch detected:
- Plan A scope: Authentication + User Management
- Plan B scope: Authentication only
Direct comparison invalid; scores reflect different deliverables.
```

---

### Case 18: Tied Total Score

**Scenario:** Both plans score 80/100.

**Resolution:** Break tie using critical dimension scores.

**Priority order:**
1. Sum of critical dimensions (Executability + Completeness + Success Criteria + Scope)
2. If still tied: prefer plan with higher Executability
3. If still tied: declare tie with recommendation to review both

---

### Case 19: One Plan Much Shorter

**Scenario:** Plan A is 300 lines; Plan B is 80 lines.

**Resolution:** Length is not a scoring criterion.

**Justification:** A concise, complete plan may score higher than a verbose incomplete one. Evaluate on rubric criteria, not length.

---

## General Resolution Principles

1. **When in doubt, be conservative** - lower score protects agent from failure
2. **Cite evidence** - every edge case decision should reference specific content
3. **Document reasoning** - use Notes column in scoring table
4. **Apply rules mechanically first** - Scoring Impact Rules before subjective judgment
5. **Prefer explicit over implicit** - agents struggle with implicit knowledge

