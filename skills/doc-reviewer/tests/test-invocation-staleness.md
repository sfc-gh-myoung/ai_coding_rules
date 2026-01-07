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
- ✅ Date format valid
- ✅ Mode recognized (STALENESS)
- ✅ Target file exists

### Phase 2: Review Execution (Fast Mode)
- ✅ Read README.md
- ✅ Load ONLY staleness.md rubric
- ✅ Test external links (200/404/301)
- ✅ Check tool versions
- ✅ Score Staleness dimension only

### Phase 3: Output
- ✅ Write to: `reviews/README-claude-sonnet-45-2026-01-06.md`
- ✅ Execution time: <1 minute (fast mode)

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

| URL | Line | Status | Response Time | Action |
|-----|------|--------|---------------|--------|
| https://docs.python.org/3/ | 23 | 200 ✅ | 0.3s | None |
| https://oldsite.com | 45 | 404 ❌ | - | Remove |

**Summary:**
- Total links: X
- Valid (200): Y (Z%)
- Broken: A
- Redirects: B

### Tool Version Currency

| Tool | Doc Version | Current Version | Status |
|------|-------------|-----------------|--------|
| Python | 3.11 | 3.12 | ✅ Current |
| Node.js | 18 | 20 | ⚠️  Prev LTS |

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
