# Example: FULL Review

## Custom Output Directory

```text
Use the doc-reviewer skill.

review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
output_root: mytest/
```

**Expected output files:**

```
mytest/doc-reviews/README-claude-sonnet45-2025-12-16.md
mytest/doc-reviews/CONTRIBUTING-claude-sonnet45-2025-12-16.md
mytest/doc-reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md
```

---

## Basic Usage (Default Targets)

```text
Use the doc-reviewer skill.

review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**What happens:**

1. Skill discovers default documentation files:
   - `./README.md`
   - `./CONTRIBUTING.md`
   - `./docs/*.md`

2. For each file, performs full 6-dimension review

3. Generates verification tables:
   - Cross-Reference Verification
   - Link Validation
   - Baseline Compliance

4. Writes individual review files

**Expected output files:**

```
reviews/doc-reviews/README-claude-sonnet45-2025-12-16.md
reviews/doc-reviews/CONTRIBUTING-claude-sonnet45-2025-12-16.md
reviews/doc-reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md
```

(or `...-01.md`, `...-02.md`, etc. if base filenames already exist)

---

## Specific Files

```text
Use the doc-reviewer skill.

target_files: [README.md, docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected output files:**

```
reviews/doc-reviews/README-claude-sonnet45-2025-12-16.md
reviews/doc-reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md
```

---

## Collection Review (Consolidated Output)

```text
Use the doc-reviewer skill.

target_files: [README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FULL
review_scope: collection
model: claude-sonnet45
```

**Expected output file:**

```
reviews/summaries/_docs-collection-claude-sonnet45-2025-12-16.md
```

**Collection review structure:**

```markdown
## Documentation Collection Review

### Overview
- Files reviewed: 3
- Total lines: 1,847
- Review date: 2025-12-16

### Summary Scores
- **README.md** - Accuracy: 20/25, Completeness: 25/25, Clarity: 16/20, Structure: 15/15, Staleness: 6/10, Consistency: 5/5, Overall: 87/100
- **CONTRIBUTING.md** - Accuracy: 25/25, Completeness: 20/25, Clarity: 20/20, Structure: 12/15, Staleness: 8/10, Consistency: 5/5, Overall: 90/100
- **ARCHITECTURE.md** - Accuracy: 20/25, Completeness: 25/25, Clarity: 16/20, Structure: 15/15, Staleness: 8/10, Consistency: 5/5, Overall: 89/100

### Collection Average: 88.7/100

---

### README.md Review
[Full review content]

---

### CONTRIBUTING.md Review
[Full review content]

---

### ARCHITECTURE.md Review
[Full review content]
```

---

## Sample FULL Review Output

```markdown
## Documentation Review: README.md

### Scores
- **Accuracy** - Max: 25, Raw: 4/5, Points: 20/25, Notes: 2 outdated command references
- **Completeness** - Max: 25, Raw: 5/5, Points: 25/25, Notes: All major features documented
- **Clarity** - Max: 20, Raw: 4/5, Points: 16/20, Notes: Good structure, some jargon unexplained
- **Structure** - Max: 15, Raw: 5/5, Points: 15/15, Notes: Clear TOC, logical flow
- **Staleness** - Max: 10, Raw: 3/5, Points: 6/10, Notes: 3 broken links, outdated Python version
- **Consistency** - Max: 5, Raw: 5/5, Points: 5/5, Notes: Follows project conventions

**Overall:** 87/100

**Verdict:** PUBLISHABLE_WITH_EDITS

**Reviewing Model:** Claude Sonnet 4.5

### Cross-Reference Verification

- **`scripts/deploy.py`** - Type: file, Location: README:45, Exists?: , Notes: —
- **`task validate`** - Type: command, Location: README:78, Exists?: , Notes: —
- **`scripts/old_script.py`** - Type: file, Location: README:112, Exists?: , Notes: Removed in v3.0
- **`docs/ARCHITECTURE.md`** - Type: file, Location: README:156, Exists?: , Notes: —

### Link Validation

- **`./docs/ARCHITECTURE.md`** - Type: internal, Source: README:12, Status: , Notes: —
- **`#installation`** - Type: anchor, Source: README:5, Status: , Notes: —
- **`https://taskfile.dev`** - Type: external, Source: README:89, Status: , Notes: Manual check
- **`./docs/DEPRECATED.md`** - Type: internal, Source: README:134, Status: , Notes: File removed

### Baseline Compliance Check

Checking against: rules/801-project-readme.md

- **Quick Start section** - Source: 801, Compliant?: , Notes: Lines 45-78
- **Prerequisites listed** - Source: 801, Compliant?: , Notes: Lines 23-35
- **License section** - Source: 801, Compliant?: , Notes: Lines 890-920
- **Troubleshooting** - Source: 801, Compliant?: , Notes: Lines 750-850

### Critical Issues (Must Fix)

1. **Location:** Line 112
   **Problem:** References `scripts/old_script.py` which was removed
   **Recommendation:** Update to `scripts/rule_deployer.py`

2. **Location:** Line 134
   **Problem:** Link to `./docs/DEPRECATED.md` is broken
   **Recommendation:** Remove link or create redirect

### Improvements (Should Fix)

1. **Location:** Line 67
   **Problem:** Python version listed as 3.11, current is 3.13
   **Recommendation:** Update to "Python 3.11+" or "Python 3.13"

### Minor Suggestions (Nice to Have)

1. **Location:** Lines 200-250
   **Problem:** Long code block without explanation
   **Recommendation:** Add brief description before code example

### Documentation Perspective Checklist

- [x] **New user test:** Yes, Quick Start section is comprehensive
- [x] **Accuracy audit:** 15/17 references valid = 88%
- [x] **Link health:** 2 broken / 24 total internal links
- [ ] **Missing sections:** No API reference section
- [x] **Staleness indicators:** Python version outdated, 2 deprecated script references
```

