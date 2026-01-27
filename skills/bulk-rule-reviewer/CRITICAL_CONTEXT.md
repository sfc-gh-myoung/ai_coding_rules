# CRITICAL CONTEXT

**Re-read this file every 10 rules OR if previous review was <2500 bytes.**

## Review Output Path
```
{output_root}/rule-reviews/{rule-name}-{model}-{date}.md
```

## Evidence Minimums (FULL mode)

| Requirement | Minimum |
|-------------|---------|
| Line references | ≥15 distinct |
| Direct quotes | ≥3 with line numbers |
| Review file size | 3000-8000 bytes |

## Required Sections in Review

1. Executive Summary (scores table with ALL 6 dimensions)
2. Schema Validation Results
3. Agent Executability Verdict
4. Dimension Analysis (6 sections)
5. Critical Issues (list with line numbers)
6. Recommendations (prioritized)
7. Post-Review Checklist
8. Conclusion

## Quality Gates (VIOLATIONS)

- Review <2000 bytes = VIOLATION → Re-do with full analysis
- Zero recommendations AND zero line refs = REJECT
- Missing Score Table = REJECT
- Score without rubric consultation = REJECT

## Score Table Format

```markdown
| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| Actionability | X | 25 | [evidence] |
| Completeness | X | 25 | [evidence] |
| Consistency | X | 15 | [evidence] |
| Parsability | X | 15 | [evidence] |
| Token Efficiency | X | 10 | [evidence] |
| Staleness | X | 10 | [evidence] |
| Cross-Agent Consistency | X | 5 | [evidence] |

**Total Score: XX/100**
```

## Verdicts

- 90-100: EXECUTABLE
- 80-89: EXECUTABLE_WITH_REFINEMENTS
- 60-79: NEEDS_REFINEMENT
- <60: NOT_EXECUTABLE
