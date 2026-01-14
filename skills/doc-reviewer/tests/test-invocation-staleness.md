# Test Invocation: doc-reviewer (STALENESS Mode)

## Purpose

Verify doc-reviewer skill executes correctly in fast STALENESS mode (1 dimension only).

## Test Input

```
Use the doc-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
target_files: README.md
```

## Expected Behavior

### Phase 1: Input Validation
-  Date format valid
-  Mode recognized (STALENESS)
-  Target file exists

### Phase 2: Review Execution (Fast Mode)
-  Read README.md
-  Load ONLY staleness.md rubric
-  Test external links (200/404/301)
-  Check tool versions
-  Score Staleness dimension only

### Phase 3: Output
-  Write to: `reviews/doc-reviews/README-claude-sonnet-45-2026-01-06.md`
-  Execution time: <1 minute (fast mode)

## Expected Output Structure

```markdown
# Documentation Review: README.md (STALENESS Check)

**Reviewed:** 2026-01-06
**Model:** claude-sonnet-45
**Mode:** STALENESS

## Staleness Assessment

**Score:** X/10
**Status:** [EXCELLENT|GOOD|ACCEPTABLE|NEEDS_WORK|POOR]

### Link Validation

- **https://docs.python.org/3/** - Line: 23, Status: 200, Response Time: 0.3s, Action: None
- **https://oldsite.com** - Line: 45, Status: 404, Response Time: -, Action: Remove

**Summary:**
- Total links: X
- Valid (200): Y (Z%)
- Broken: A
- Redirects: B

### Tool Version Currency

- **Python** - Doc Version: 3.11, Current Version: 3.12, Status: Current
- **Node.js** - Doc Version: 18, Current Version: 20, Status: Prev LTS

## Recommendations

1. Update broken links
2. Update tool versions to current

## Conclusion

Staleness check complete. [Next steps]
```

## Success Criteria

- [ ] Only Staleness dimension scored
- [ ] Link validation performed
- [ ] Tool versions checked
- [ ] Fast execution (<1 min)
- [ ] Other dimensions NOT scored

## Performance Target

**Execution time:** <1 minute (vs 3-5 min for FULL mode)
