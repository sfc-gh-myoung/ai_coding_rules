# Token Efficiency Rubric

> **STATUS: INFORMATIONAL ONLY - NOT SCORED**
>
> As of Scoring Rubric v2.0, Token Efficiency has been **merged into Rule Size** and is no longer a scored dimension. Findings appear in recommendations, not in the score.

## What to Look For

When reviewing rules, note these redundancy issues for the recommendations section:

| Pattern | Action |
|---------|--------|
| Verbatim repeated definitions (>10 words) | Flag with first/repeated line numbers |
| Duplicated code examples | Flag, recommend cross-reference |
| Prose paragraphs convertible to lists | Note potential savings |
| Missing cross-references between repeated content | Recommend "see X" pattern |

## Redundancy Reporting

| Redundancy Count | Recommendation |
|------------------|----------------|
| 0 instances | No action needed |
| 1-2 instances | Note in recommendations |
| 3+ instances | Prioritize in remediation |

## How to Report Findings

Include in the **Recommendations** section of the review (not as a scored dimension):

```markdown
**Token Efficiency (Informational):**
- Redundancy instances: N
- [Line X]: "definition..." repeated at [Line Y]
- Structure ratio: NN% (lists/tables vs prose)
- Estimated savings: ~NNN tokens if redundancies removed
```

## Non-Issues (Do NOT Flag)

- **Intentional repetition for emphasis** (marked with "IMPORTANT" or "reminder")
- **Summary sections** that reference detailed sections
- **Template/example sections** with similar structure
- **Progressive disclosure** (brief mention + detailed section)

## For Project Files

- TokenBudget variance does NOT apply (no declared budget)
- Report actual token count for reference only
- Score redundancy and structure ratio the same as rule files

> **Historical Reference:** Full scored rubric archived at `_archive/token-efficiency-v1-scored.md`
