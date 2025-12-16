# Example: FULL Review

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
reviews/README-claude-sonnet45-2025-12-16.md
reviews/CONTRIBUTING-claude-sonnet45-2025-12-16.md
reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md
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
reviews/README-claude-sonnet45-2025-12-16.md
reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md
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
reviews/docs-collection-claude-sonnet45-2025-12-16.md
```

**Collection review structure:**

```markdown
## Documentation Collection Review

### Overview
- Files reviewed: 3
- Total lines: 1,847
- Review date: 2025-12-16

### Summary Scores
| Document | Accuracy | Completeness | Clarity | Structure | Staleness | Consistency | Overall |
|----------|----------|--------------|---------|-----------|-----------|-------------|---------|
| README.md | 20/25 | 25/25 | 16/20 | 15/15 | 6/10 | 5/5 | 87/100 |
| CONTRIBUTING.md | 25/25 | 20/25 | 20/20 | 12/15 | 8/10 | 5/5 | 90/100 |
| ARCHITECTURE.md | 20/25 | 25/25 | 16/20 | 15/15 | 8/10 | 5/5 | 89/100 |

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
| Criterion | Max | Raw | Points | Notes |
|-----------|-----|-----|--------|-------|
| Accuracy | 25 | 4/5 | 20/25 | 2 outdated command references |
| Completeness | 25 | 5/5 | 25/25 | All major features documented |
| Clarity | 20 | 4/5 | 16/20 | Good structure, some jargon unexplained |
| Structure | 15 | 5/5 | 15/15 | Clear TOC, logical flow |
| Staleness | 10 | 3/5 | 6/10 | 3 broken links, outdated Python version |
| Consistency | 5 | 5/5 | 5/5 | Follows project conventions |

**Overall:** 87/100

**Verdict:** PUBLISHABLE_WITH_EDITS

**Reviewing Model:** Claude Sonnet 4.5

### Cross-Reference Verification

| Reference | Type | Location | Exists? | Notes |
|-----------|------|----------|---------|-------|
| `scripts/deploy.py` | file | README:45 | ✅ | — |
| `task validate` | command | README:78 | ✅ | — |
| `scripts/old_script.py` | file | README:112 | ❌ | Removed in v3.0 |
| `docs/ARCHITECTURE.md` | file | README:156 | ✅ | — |

### Link Validation

| Link | Type | Source | Status | Notes |
|------|------|--------|--------|-------|
| `./docs/ARCHITECTURE.md` | internal | README:12 | ✅ | — |
| `#installation` | anchor | README:5 | ✅ | — |
| `https://taskfile.dev` | external | README:89 | ⚠️ | Manual check |
| `./docs/DEPRECATED.md` | internal | README:134 | ❌ | File removed |

### Baseline Compliance Check

Checking against: rules/801-project-readme.md

| Requirement | Source | Compliant? | Notes |
|-------------|--------|------------|-------|
| Quick Start section | 801 | ✅ | Lines 45-78 |
| Prerequisites listed | 801 | ✅ | Lines 23-35 |
| License section | 801 | ✅ | Lines 890-920 |
| Troubleshooting | 801 | ✅ | Lines 750-850 |

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

