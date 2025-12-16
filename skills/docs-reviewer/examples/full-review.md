# Example: FULL Review

## Basic Usage (Default Targets)

```text
Use the docs-reviewer skill.

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
Use the docs-reviewer skill.

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
Use the docs-reviewer skill.

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
| Document | Accuracy | Completeness | Clarity | Consistency | Staleness | Structure | Overall |
|----------|----------|--------------|---------|-------------|-----------|-----------|---------|
| README.md | 4/5 | 5/5 | 4/5 | 5/5 | 3/5 | 5/5 | 26/30 |
| CONTRIBUTING.md | 5/5 | 4/5 | 5/5 | 5/5 | 4/5 | 4/5 | 27/30 |
| ARCHITECTURE.md | 4/5 | 5/5 | 4/5 | 5/5 | 4/5 | 5/5 | 27/30 |

### Collection Average: 26.7/30

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
| Criterion | Score | Notes |
|-----------|-------|-------|
| Accuracy | 4/5 | 2 outdated command references |
| Completeness | 5/5 | All major features documented |
| Clarity | 4/5 | Good structure, some jargon unexplained |
| Consistency | 5/5 | Follows project conventions |
| Staleness | 3/5 | 3 broken links, outdated Python version |
| Structure | 5/5 | Clear TOC, logical flow |

**Overall:** 26/30

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

