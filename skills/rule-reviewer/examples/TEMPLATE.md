# Rule Review Output Template

**PURPOSE:** This is the AUTHORITATIVE format specification for all rule reviews. Re-read this file every 5 rules OR immediately after any deviation is detected.

---

## Required File Header

```markdown
# Rule Review: {rule-filename}

**Review Date:** {YYYY-MM-DD}
**Reviewer Model:** {model-name}
**Review Mode:** {FULL|FOCUSED|STALENESS}
```

---

## Section 1: Executive Summary (REQUIRED)

**CRITICAL: Use this EXACT table format with these EXACT column headers:**

```markdown
## Executive Summary

| Dimension | Raw (0-10) | Weight | Points | Notes |
|-----------|------------|--------|--------|-------|
| Actionability | X | 6 | XX | [brief evidence] |
| Rule Size | X | 5 | XX | [line count note] |
| Parsability | X | 3 | XX | [schema check summary] |
| Completeness | X | 3 | XX | [coverage note] |
| Consistency | X | 2 | XX | [reference status] |
| Cross-Agent | X | 1 | XX | [portability note] |
| **TOTAL** | | | **XXX/200 → XX/100** | |

**Verdict:** {EXECUTABLE|EXECUTABLE_WITH_REFINEMENTS|NEEDS_REFINEMENT|NOT_EXECUTABLE}
```

**Scoring Rules:**
- Raw score: 0-10 per dimension
- Points = Raw × Weight
- Total possible = 200 (convert to /100 for verdict)
- Verdicts: 90-100 = EXECUTABLE, 80-89 = EXECUTABLE_WITH_REFINEMENTS, 60-79 = NEEDS_REFINEMENT, <60 = NOT_EXECUTABLE

---

## Section 2: Schema Validation Results (REQUIRED)

```markdown
## Schema Validation Results

\```
CRITICAL: {count}
HIGH:     {count}
MEDIUM:   {count}
Passed:   {count}
Result:   {summary}
\```

{Brief explanation of any issues found}
```

---

## Section 3: Agent Executability Analysis (REQUIRED)

```markdown
## Agent Executability Analysis

**Blocking Issues Count: {N}**

1. **{Issue type} at line {N}:** {Description of ambiguity/problem} — {Why an agent would struggle}

2. ...
```

**Evidence Requirements:**
- Each issue MUST cite a specific line number
- Explain WHY it blocks agent execution (not just what the text says)

---

## Section 4: Dimension Analysis (REQUIRED - 6 subsections)

```markdown
## Dimension Analysis

### 1. Actionability (X/10 × 6 = XX points)

**Strengths:**
- Lines {N-M}: {Specific strength with line reference}
- ...

**Weaknesses:**
- Line {N}: {Specific weakness with line reference}
- ...

**Quote (line {N}):** `"{exact quote from rule}"` — {Why this matters}

### 2. Rule Size (X/10 × 5 = XX points)

**Line count: {N} lines**

{Assessment against ≤400 optimal target}

### 3. Parsability (X/10 × 3 = XX points)

{Schema validation details, metadata block assessment}

### 4. Completeness (X/10 × 3 = XX points)

**Covered well:**
- Lines {N-M}: {Area of good coverage}
- ...

**Gaps:**
- {Missing element or incomplete section}
- ...

### 5. Consistency (X/10 × 2 = XX points)

**Internal consistency:**
- {Term/concept} defined at line {N} and referenced at lines {X, Y, Z}
- ...

**Issues:**
- Line {N}: {Inconsistency description}
- ...

### 6. Cross-Agent Consistency (X/10 × 1 = XX points)

**Strengths:**
- {Technology-agnostic element}
- ...

**Concerns:**
- {Platform-specific element that may not transfer}
- ...
```

---

## Section 5: Critical Issues (REQUIRED)

```markdown
## Critical Issues

1. **Line {N} [vs Line {M}]:** {Issue description with specific line references}

2. **Line {N}:** {Issue description}

...
```

**Minimum: At least 1 critical issue OR explicit statement "No critical issues identified"**

---

## Section 6: Recommendations (REQUIRED)

```markdown
## Recommendations

1. **[Line {N}]** {Specific, actionable recommendation} **Expected improvement: +X {Dimension}**

2. **[Lines {N-M}]** {Recommendation} **Expected improvement: +X {Dimension}**

...
```

**Requirements:**
- Every recommendation MUST have a line reference
- Every recommendation MUST have an expected improvement metric
- Recommendations should be prioritized (most impactful first)

---

## Section 7: Conclusion (REQUIRED)

```markdown
## Conclusion

{rule-filename} is a {quality assessment} that {summary of purpose}. At {N} lines it {size assessment}. Its main strengths are {top 2-3 strengths}. The primary areas for improvement are: {top 2-3 improvements}. Overall, {final verdict explanation}.
```

---

## Quality Gates (AUTO-REJECT if violated)

| Gate | Requirement | Action if Failed |
|------|-------------|------------------|
| Minimum Size | ≥3000 bytes | Re-do with full analysis |
| Maximum Size | ≤8000 bytes | Trim redundant content |
| Line References | ≥15 distinct | Add more evidence |
| Direct Quotes | ≥3 with line numbers | Add quotes from rule |
| Score Table | Must use exact format above | Fix table format |
| All Sections | All 7 sections present | Add missing sections |

---

## Anti-Drift Protocol

**MANDATORY re-read triggers:**
1. Every 5 rules processed
2. Immediately after any review with <3000 bytes
3. Before starting a new batch
4. If self-check detects format deviation

**Self-check questions (ask after each review):**
- Does my Executive Summary table have exactly 6 dimension rows plus TOTAL?
- Are the column headers: `Dimension | Raw (0-10) | Weight | Points | Notes`?
- Did I include all 7 required sections?
- Do I have ≥15 line references and ≥3 direct quotes?

If ANY answer is "no" → Re-read this template → Regenerate the review.
