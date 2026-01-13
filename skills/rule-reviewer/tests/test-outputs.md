# Test Cases: Output Handling

## File Writing Tests

### Test O.1: Successful File Write - New File

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Pre-condition:**
- `reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md` does NOT exist

**Expected:**
- File created: `reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md`
- Confirmation message shown
- Full review NOT printed to chat

**Verification:**
```bash
ls reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md
cat reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md | head -20
```

**Pass Criteria:**
- [ ] File created at expected path
- [ ] Content is complete review
- [ ] Chat shows only confirmation
- [ ] No duplicate output

---

### Test O.2: No-Overwrite - First Suffix

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Pre-condition:**
- `reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md` EXISTS

**Expected:**
- New file: `reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15-01.md`
- Original file unchanged
- Confirmation shows new filename

**Verification:**
```bash
# Both files should exist
ls reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md
ls reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15-01.md

# Original unchanged
diff reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md <original>
```

**Pass Criteria:**
- [ ] Suffix -01 added
- [ ] Original preserved
- [ ] New file has new review

---

### Test O.3: No-Overwrite - Sequential Suffixes

**Pre-condition:**
- Base file exists
- -01.md exists
- -02.md exists

**Expected:**
- New file: `...-03.md`

**Verification:**
```bash
ls reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15*.md | wc -l
# Should be 4 (base + 01 + 02 + 03)
```

**Pass Criteria:**
- [ ] Correct suffix calculated
- [ ] No gaps in sequence
- [ ] All previous files preserved

---

### Test O.4: File Write Failure - Permission Denied

**Scenario:** reviews/rule-reviews/ directory not writable

**Expected:**
- Error detected
- Fallback: Print to chat
- Format:
  ```
  OUTPUT_FILE: reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md
  
  [Full review content]
  ```

**Pass Criteria:**
- [ ] Error handled gracefully
- [ ] OUTPUT_FILE path shown
- [ ] Full content printed
- [ ] User can manually save

---

### Test O.5: File Write Failure - Directory Missing

**Pre-condition:**
- `reviews/` directory does not exist

**Expected:**
- Directory created automatically
- File written successfully
- OR: Error with instruction to create directory

**Pass Criteria:**
- [ ] Directory creation attempted
- [ ] Clear error if creation fails
- [ ] Recovery path provided

---

## Confirmation Message Tests

### Test C.1: Success Confirmation Format

**Expected Confirmation:**
```
 Review complete

OUTPUT_FILE: reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md
Target: rules/200-python-core.md
Mode: FULL
Model: claude-sonnet-45
```

**Pass Criteria:**
- [ ] OUTPUT_FILE path shown
- [ ] Target file confirmed
- [ ] Mode confirmed
- [ ] Model confirmed
- [ ] No full review in chat

---

### Test C.2: Success with Suffix Confirmation

**Expected (when suffix used):**
```
 Review complete

OUTPUT_FILE: reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15-01.md
Note: Base filename existed, using suffix -01

Target: rules/200-python-core.md
Mode: FULL
Model: claude-sonnet-45
```

**Pass Criteria:**
- [ ] Suffix noted in message
- [ ] User informed of reason

---

## Output Content Tests

### Test OC.1: Review Content Structure

**Expected Sections:**
1. Header with rule name
2. Review metadata block
3. Overall score
4. Dimension scores table
5. Issues by severity
6. Recommendations
7. Checklist

**Verification:**
```bash
# Check for required sections
grep "## Overall Score" reviews/<file>.md
grep "## Dimension Scores" reviews/<file>.md
grep "## Issues Found" reviews/<file>.md
grep "## Recommendations" reviews/<file>.md
```

**Pass Criteria:**
- [ ] All sections present
- [ ] Correct markdown formatting
- [ ] Tables render correctly

---

### Test OC.2: Review Content Completeness

**Verification Checklist:**
- [ ] Rule name in header
- [ ] Date matches input
- [ ] Mode matches input
- [ ] Model matches input
- [ ] All dimensions scored (FULL mode)
- [ ] Issues categorized correctly
- [ ] Recommendations are actionable
- [ ] No placeholder text
- [ ] No truncation

---

## Filename Generation Tests

### Test FN.1: Filename Format

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
model: claude-sonnet-45
```

**Expected Filename:**
```
reviews/rule-reviews/200-python-core-claude-sonnet-45-2025-12-15.md
```

**Pattern:**
```
reviews/<rule-name>-<model-slug>-<YYYY-MM-DD>.md
```

**Pass Criteria:**
- [ ] Correct directory
- [ ] Rule name extracted correctly
- [ ] Model slug normalized
- [ ] Date in correct format
- [ ] .md extension

---

### Test FN.2: Filename with Complex Rule Name

**Input:**
```
target_file: rules/115-snowflake-cortex-agents-core.md
model: claude-opus-4
```

**Expected:**
```
reviews/rule-reviews/115-snowflake-cortex-agents-core-claude-opus-4-2025-12-15.md
```

**Pass Criteria:**
- [ ] Full rule name preserved
- [ ] Hyphens handled correctly
- [ ] No truncation

---

### Test FN.3: Model Slug Normalization in Filename

**Input Variations:**
- **`Claude Sonnet 4.5`** - `claude-sonnet-45`
- **`claude-sonnet-45`** - `claude-sonnet-45`
- **`CLAUDE_OPUS_4`** - `claude-opus-4`
- **`gpt-4-turbo`** - `gpt-4-turbo`

**Pass Criteria:**
- [ ] Spaces → hyphens
- [ ] Underscores → hyphens
- [ ] Lowercase
- [ ] Dots removed from versions
- [ ] Non-Claude slugs preserved

