# Test Cases: Review Modes

## FULL Mode Tests

### Test F.1: FULL Review - Complete Execution

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Expected Output Structure:**
```markdown
# Rule Review: 200-python-core.md

## Review Metadata
- Date: 2025-12-15
- Mode: FULL
- Model: claude-sonnet-45
- Reviewer: AI Agent

## Overall Score: X/100

## Dimension Scores

| Criterion | Max | Raw | Points | Notes |
|-----------|-----|-----|--------|-------|
| Actionability | 25 | X/5 | Y/25 | ... |
| Completeness | 20 | X/5 | Y/20 | ... |
| Consistency | 20 | X/5 | Y/20 | ... |
| Parsability | 15 | X/5 | Y/15 | ... |
| Token Efficiency | 10 | X/5 | Y/10 | ... |
| Staleness | 10 | X/5 | Y/10 | ... |

## Issues Found

### CRITICAL
- [None or list]

### HIGH
- [None or list]

### MEDIUM
- [None or list]

## Recommendations
- [List of improvements]

## Checklist
- [ ] Item 1
- [ ] Item 2
```

**Pass Criteria:**
- [ ] All dimensions scored
- [ ] Overall score calculated
- [ ] Issues categorized by severity
- [ ] Recommendations provided
- [ ] Checklist included

---

### Test F.2: FULL Review - Rule with Issues

**Input:**
```
target_file: rules/incomplete-rule.md  # Has known issues
review_mode: FULL
```

**Expected:**
- Issues correctly identified
- Severity correctly assigned
- Specific fix recommendations

**Pass Criteria:**
- [ ] Known issues detected
- [ ] Severity matches actual impact
- [ ] Fixes are actionable

---

## FOCUSED Mode Tests

### Test FO.1: FOCUSED Review - Metadata Focus

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FOCUSED
focus_area: metadata
model: claude-sonnet-45
```

**Expected Output Structure:**
```markdown
# Focused Review: 200-python-core.md
## Focus Area: Metadata

## Metadata Analysis

### Keywords
- Count: X (expected 10-15)
- Relevance: [assessment]
- Discoverability: [assessment]

### TokenBudget
- Value: ~XXXX
- Validation: Run `python scripts/token_validator.py <rule-file>`
- Actual tokens (tiktoken): [value]
- Variance: [%]
- Appropriateness: [assessment]

### ContextTier
- Value: [tier]
- Justification: [assessment]

### Dependencies
- Listed: [count]
- Validity: [all exist / missing X]

## Score: X/100

## Recommendations
- [Specific to metadata]
```

**Pass Criteria:**
- [ ] Only metadata analyzed
- [ ] Deep analysis of each field
- [ ] No other dimensions scored
- [ ] Focused recommendations

---

### Test FO.2: FOCUSED Review - Contract Focus

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FOCUSED
focus_area: contract
model: claude-sonnet-45
```

**Expected:**
- Contract section analyzed in depth
- All 6 XML tags checked
- Placement verified (before line 160)
- Content quality assessed

**Pass Criteria:**
- [ ] All 6 tags verified
- [ ] Placement checked
- [ ] Content quality scored
- [ ] Missing/weak elements identified

---

### Test FO.3: FOCUSED Review - Examples Focus

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FOCUSED
focus_area: examples
model: claude-sonnet-45
```

**Expected:**
- Code examples analyzed
- Syntax correctness checked
- Best practice alignment verified
- Anti-patterns quality assessed

**Pass Criteria:**
- [ ] All code examples found
- [ ] Syntax validity noted
- [ ] Correctness assessed
- [ ] Anti-pattern quality scored

---

## STALENESS Mode Tests

### Test S.1: STALENESS Review - Current Rule

**Input:**
```
target_file: rules/200-python-core.md  # Recently updated
review_date: 2025-12-15
review_mode: STALENESS
model: claude-sonnet-45
```

**Expected Output Structure:**
```markdown
# Staleness Review: 200-python-core.md

## Staleness Assessment: CURRENT

## Version References
| Item | Rule Version | Current Version | Status |
|------|--------------|-----------------|--------|
| Python | 3.11+ | 3.13 | ⚠️ Minor |
| Tool X | v2.0 | v2.1 | ✓ Current |

## Deprecated Patterns
- None found

## Outdated Recommendations
- None found

## Overall: LOW STALENESS RISK
```

**Pass Criteria:**
- [ ] Version references checked
- [ ] Deprecated patterns scanned
- [ ] Staleness risk assessed
- [ ] No false positives for current content

---

### Test S.2: STALENESS Review - Outdated Rule

**Input:**
```
target_file: rules/old-rule.md  # Known to have outdated content
review_mode: STALENESS
```

**Expected:**
- Outdated versions identified
- Deprecated patterns found
- Staleness risk: HIGH
- Update recommendations provided

**Pass Criteria:**
- [ ] Outdated content detected
- [ ] Specific versions cited
- [ ] HIGH risk assigned
- [ ] Update path recommended

---

### Test S.3: STALENESS Review - Deprecated APIs

**Scenario:** Rule references deprecated API/tool

**Expected:**
```markdown
## Deprecated Patterns Found

### Pattern 1: [Deprecated API]
- Location: Line XX
- Status: Deprecated since [version/date]
- Replacement: [New approach]
- Impact: [Breaking/Non-breaking]
```

**Pass Criteria:**
- [ ] Deprecated API identified
- [ ] Deprecation date/version noted
- [ ] Replacement suggested
- [ ] Impact assessed

---

## Mode Comparison Tests

### Test MC.1: Same Rule, Different Modes

**Input:** Same rule reviewed with FULL, FOCUSED, STALENESS

**Expected:**
- FULL: Comprehensive, all dimensions
- FOCUSED: Deep on one area
- STALENESS: Time-sensitive content only

**Verification:**
- FULL output > FOCUSED output (length)
- STALENESS focuses on versions/dates
- Scores may differ by mode

**Pass Criteria:**
- [ ] Output structure differs by mode
- [ ] FULL most comprehensive
- [ ] FOCUSED most detailed on area
- [ ] STALENESS most time-relevant

---

### Test MC.2: Mode Appropriateness Warning

**Scenario:** STALENESS mode on brand-new rule

**Expected:**
- Warning: "Rule created recently, STALENESS review may not be meaningful"
- Proceeds if user confirms
- Results show "CURRENT" for most items

**Pass Criteria:**
- [ ] Warning issued
- [ ] User can proceed
- [ ] Results reflect newness

