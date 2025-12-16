# Test Cases: Review Modes

## Test 1: FULL Mode - All Dimensions

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected Output Contains:**

- [ ] Scores table with all 6 dimensions
- [ ] Overall score (X/100)
- [ ] Cross-Reference Verification table
- [ ] Link Validation table
- [ ] Baseline Compliance Check (if rules exist)
- [ ] Critical Issues section
- [ ] Improvements section
- [ ] Minor Suggestions section
- [ ] Documentation Perspective Checklist

---

## Test 2: FOCUSED Mode - Accuracy

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: accuracy
model: claude-sonnet45
```

**Expected Output Contains:**

- [ ] Scores table with Accuracy only
- [ ] Cross-Reference Verification table (detailed)
- [ ] Issues specific to accuracy
- [ ] NO Link Validation table
- [ ] NO Baseline Compliance Check

---

## Test 3: FOCUSED Mode - Staleness

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: staleness
model: claude-sonnet45
```

**Expected Output Contains:**

- [ ] Scores table with Staleness only
- [ ] Link Validation table (detailed)
- [ ] Version References table
- [ ] Deprecated Patterns list
- [ ] NO Cross-Reference Verification table

---

## Test 4: FOCUSED Mode - Clarity

**Inputs:**

```text
target_files: [docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: clarity
model: claude-sonnet45
```

**Expected Output Contains:**

- [ ] Scores table with Clarity only
- [ ] Reading Level Assessment
- [ ] Jargon Audit table
- [ ] Example Coverage analysis
- [ ] New User Test assessment

---

## Test 5: STALENESS Mode

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: STALENESS
model: claude-sonnet45
```

**Expected Output Contains:**

- [ ] Scores table with Staleness and Structure only
- [ ] Overall score (X/25)
- [ ] Link Validation table
- [ ] Version References table
- [ ] Deprecated Patterns list
- [ ] Staleness Risk Assessment
- [ ] NO full Cross-Reference Verification

---

## Test 6: Single Scope (Default)

**Inputs:**

```text
target_files: [README.md, CONTRIBUTING.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] Two separate output files created:
  - `reviews/README-claude-sonnet45-2025-12-16.md`
  - `reviews/CONTRIBUTING-claude-sonnet45-2025-12-16.md`
- [ ] Each file contains complete review for that document

---

## Test 7: Collection Scope

**Inputs:**

```text
target_files: [README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FULL
review_scope: collection
model: claude-sonnet45
```

**Expected:**

- [ ] Single output file:
  - `reviews/docs-collection-claude-sonnet45-2025-12-16.md`
- [ ] Contains Overview section with file list
- [ ] Contains Summary Scores table (all docs)
- [ ] Contains individual review sections for each doc

---

## Test 8: Collection Scope with STALENESS Mode

**Inputs:**

```text
target_files: [README.md, CONTRIBUTING.md]
review_date: 2025-12-16
review_mode: STALENESS
review_scope: collection
model: claude-sonnet45
```

**Expected:**

- [ ] Single output file:
  - `reviews/docs-collection-claude-sonnet45-2025-12-16.md`
- [ ] Consolidated link validation across all docs
- [ ] Summary of staleness issues by document
- [ ] Overall staleness risk assessment

---

## Test 9: Baseline Rule Detection

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
# Project has rules/801-project-readme.md
```

**Expected:**

- [ ] Baseline Compliance Check section present
- [ ] References rules/801-project-readme.md
- [ ] Lists compliance status for each requirement
- [ ] Consistency score reflects rule compliance

---

## Mode Comparison Matrix

| Feature | FULL | FOCUSED | STALENESS |
|---------|------|---------|-----------|
| All 6 dimensions | ✅ | ❌ (1 only) | ❌ (2 only) |
| Cross-Reference table | ✅ | If accuracy | ❌ |
| Link Validation table | ✅ | If staleness | ✅ |
| Baseline Compliance | ✅ | If consistency | ❌ |
| Version References | ✅ | If staleness | ✅ |
| Deprecated Patterns | ✅ | If staleness | ✅ |
| Clarity analysis | ✅ | If clarity | ❌ |
| Structure analysis | ✅ | If structure | ✅ |

---

## Scope Comparison

| Feature | Single | Collection |
|---------|--------|------------|
| Output files | One per doc | One total |
| Summary table | Per doc | All docs |
| Cross-doc analysis | ❌ | ✅ |
| Best for | Detailed feedback | Overall health |

