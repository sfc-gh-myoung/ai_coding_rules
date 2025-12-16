# Test Cases: Output Handling

## Test 1: Basic File Output

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] File created: `reviews/README-claude-sonnet45-2025-12-16.md`
- [ ] File contains complete review
- [ ] Confirmation message printed (not full content)

---

## Test 2: Nested Document Path

**Inputs:**

```text
target_files: [docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] File created: `reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md`
- [ ] Uses base filename only (not full path)
- [ ] File contains complete review

---

## Test 3: No-Overwrite (First Collision)

**Pre-condition:**

```bash
# Create existing file
touch reviews/README-claude-sonnet45-2025-12-16.md
```

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] Original file unchanged
- [ ] New file created: `reviews/README-claude-sonnet45-2025-12-16-01.md`
- [ ] Confirmation shows actual filename used

---

## Test 4: No-Overwrite (Multiple Collisions)

**Pre-condition:**

```bash
# Create existing files
touch reviews/README-claude-sonnet45-2025-12-16.md
touch reviews/README-claude-sonnet45-2025-12-16-01.md
touch reviews/README-claude-sonnet45-2025-12-16-02.md
```

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] All existing files unchanged
- [ ] New file created: `reviews/README-claude-sonnet45-2025-12-16-03.md`

---

## Test 5: Collection Output Naming

**Inputs:**

```text
target_files: [README.md, CONTRIBUTING.md]
review_date: 2025-12-16
review_mode: FULL
review_scope: collection
model: claude-sonnet45
```

**Expected:**

- [ ] Single file created: `reviews/docs-collection-claude-sonnet45-2025-12-16.md`
- [ ] File contains consolidated review

---

## Test 6: Model Slug Normalization

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: Claude Sonnet 4.5
```

**Expected:**

- [ ] Model normalized to: `claude-sonnet-45`
- [ ] File created: `reviews/README-claude-sonnet-45-2025-12-16.md`

---

## Test 7: Reviews Directory Creation

**Pre-condition:**

```bash
# Remove reviews directory
rm -rf reviews/
```

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] Directory `reviews/` created automatically
- [ ] File created successfully
- [ ] No error about missing directory

---

## Test 8: Fallback Output (Write Failure)

**Scenario:** File write fails (permission denied, disk full, etc.)

**Expected:**

- [ ] Message: "Review completed but file write failed"
- [ ] OUTPUT_FILE path printed
- [ ] Full review content printed to chat
- [ ] Instructions for manual save provided

**Expected Format:**

```
⚠️ Review completed but file write failed.

OUTPUT_FILE: reviews/README-claude-sonnet45-2025-12-16.md

--- BEGIN REVIEW CONTENT ---
[Full review markdown]
--- END REVIEW CONTENT ---

To save manually:
1. Copy content between markers above
2. Create file: touch reviews/README-claude-sonnet45-2025-12-16.md
3. Paste content into file
```

---

## Test 9: Confirmation Message Format

**Inputs:**

```text
target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected Confirmation:**

```
✓ Review complete

OUTPUT_FILE: reviews/README-claude-sonnet45-2025-12-16.md
Target: README.md
Mode: FULL
Scope: single
Model: claude-sonnet45

Summary:
- Accuracy: X/25
- Completeness: X/25
- Clarity: X/20
- Structure: X/15
- Staleness: X/10
- Consistency: X/5
Overall: X/100
Verdict: [PUBLISHABLE|PUBLISHABLE_WITH_EDITS|NEEDS_REVISION|NOT_PUBLISHABLE]
```

---

## Test 10: Multiple File Output (Single Scope)

**Inputs:**

```text
target_files: [README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- [ ] Three files created:
  - `reviews/README-claude-sonnet45-2025-12-16.md`
  - `reviews/CONTRIBUTING-claude-sonnet45-2025-12-16.md`
  - `reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md`
- [ ] Each file contains complete review for that document
- [ ] Confirmation lists all output files

---

## Output Verification Checklist

For each review output file, verify:

### Structure

- [ ] Starts with `## Documentation Review: [name]`
- [ ] Contains Scores table
- [ ] Contains Overall score
- [ ] Contains Reviewing Model line

### Verification Tables (FULL mode)

- [ ] Cross-Reference Verification table present
- [ ] Link Validation table present
- [ ] Baseline Compliance Check (if rules exist)

### Issues Sections

- [ ] Critical Issues section present
- [ ] Improvements section present
- [ ] Minor Suggestions section present

### Checklist

- [ ] Documentation Perspective Checklist present
- [ ] All checklist items answered

### Formatting

- [ ] Valid markdown syntax
- [ ] Tables render correctly
- [ ] Code blocks properly fenced
- [ ] No broken links within review

