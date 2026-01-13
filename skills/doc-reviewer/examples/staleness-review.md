# Example: STALENESS Review

## Basic Staleness Check

```text
Use the doc-reviewer skill.

review_date: 2025-12-16
review_mode: STALENESS
model: claude-sonnet45
```

**What happens:**

1. Discovers default documentation files
2. Reviews Staleness and Structure dimensions only
3. Generates Link Validation Table
4. Checks for outdated versions and deprecated patterns
5. Quick periodic maintenance check

**Expected output file:**

```
reviews/doc-reviews/README-claude-sonnet45-2025-12-16.md
```

---

## Staleness Check on Specific Files

```text
Use the doc-reviewer skill.

target_files: [README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: STALENESS
review_scope: collection
model: claude-sonnet45
```

**Expected output file:**

```
reviews/summaries/_docs-collection-claude-sonnet45-2025-12-16.md
```

---

## When to Use STALENESS Mode

- **Quarterly documentation audit** - STALENESS
- **After major release** - STALENESS
- **Before publishing docs** - FULL
- **After dependency updates** - STALENESS
- **Initial documentation review** - FULL
- **Fixing specific issues** - FOCUSED

---

## Sample STALENESS Review Output

```markdown
## Documentation Review: README.md (STALENESS)

### Scores
- **Staleness** - Score: 3/5, Notes: Multiple outdated references
- **Structure** - Score: 5/5, Notes: Well organized

**Overall:** 8/10 (Staleness mode)

**Reviewing Model:** Claude Sonnet 4.5

### Link Validation

- **`./docs/ARCHITECTURE.md`** - Type: internal, Source: README:12, Status: , Notes: —
- **`./docs/MEMORY_BANK.md`** - Type: internal, Source: README:18, Status: , Notes: —
- **`./CONTRIBUTING.md`** - Type: internal, Source: README:24, Status: , Notes: —
- **`#quick-start`** - Type: anchor, Source: README:5, Status: , Notes: —
- **`#troubleshooting`** - Type: anchor, Source: README:8, Status: , Notes: —
- **`#installation`** - Type: anchor, Source: README:6, Status: , Notes: Heading renamed to "Prerequisites"
- **`./docs/DEPRECATED.md`** - Type: internal, Source: README:134, Status: , Notes: File removed
- **`https://taskfile.dev`** - Type: external, Source: README:89, Status: , Notes: Manual check needed
- **`https://docs.python.org/3.11`** - Type: external, Source: README:156, Status: , Notes: Consider updating to 3.13
- **`https://github.com/user/repo`** - Type: external, Source: README:200, Status: , Notes: Manual check needed

**Link Summary:**
- Internal links: 4 valid, 2 broken
- Anchor links: 2 valid, 1 broken
- External links: 3 flagged for manual check

### Version References

- **Python** - Documented Version: 3.11, Current Version: 3.13, Status: Update recommended
- **Task** - Documented Version: v3.x, Current Version: v3.40, Status: Current
- **uv** - Documented Version: 0.4.x, Current Version: 0.5.x, Status: Minor update available
- **Ruff** - Documented Version: 0.7.x, Current Version: 0.8.x, Status: Minor update available

### Deprecated Patterns Found

- **`pip install`** - Location: README:67, Issue: Project uses uv, Recommendation: Change to `uv pip install` or `uv sync`
- **`python setup.py`** - Location: README:89, Issue: Deprecated in favor of pyproject.toml, Recommendation: Remove or update to `uv pip install -e .`
- **`pytest.ini`** - Location: README:112, Issue: Config now in pyproject.toml, Recommendation: Update reference

### Staleness Indicators Found

- **Tool Versions:** Python 3.11 documented, 3.13 is current
- **Deprecated Patterns:** 3 instances of outdated installation methods
- **API Changes:** None detected
- **Industry Shifts:** pip → uv transition not fully reflected

### Structure Assessment

- **Table of Contents** - Score: , Notes: Present and accurate
- **Section Ordering** - Score: , Notes: Logical flow
- **Navigation** - Score: , Notes: Clear anchor links
- **Grouping** - Score: , Notes: Related topics together

### Critical Issues (Must Fix)

1. **Location:** Line 134
   **Problem:** Link to `./docs/DEPRECATED.md` is broken
   **Recommendation:** Remove link (file was deleted in v3.0)

2. **Location:** Line 6
   **Problem:** Anchor `#installation` points to renamed heading
   **Recommendation:** Update to `#prerequisites`

### Improvements (Should Fix)

1. **Location:** Lines 67, 89
   **Problem:** Still references `pip install` instead of `uv`
   **Recommendation:** Update installation instructions to use `uv sync`

2. **Location:** Line 156
   **Problem:** Links to Python 3.11 docs
   **Recommendation:** Update to Python 3.13 or use version-agnostic URL

### Staleness Risk Assessment

- **🔴 High (broken links)** - Count: 3, Action: Fix immediately
- **🟡 Medium (outdated versions)** - Count: 4, Action: Update in next release
- **🟢 Low (style/minor)** - Count: 2, Action: Track for future

**Overall Staleness Risk:** Medium

**Recommendation:** Address high-risk items before next release. Schedule medium-risk updates for quarterly maintenance.

### Documentation Perspective Checklist

- [x] **Link health:** 3 broken / 10 total internal links (70% healthy)
- [x] **Version currency:** 2/4 tool versions current
- [x] **Deprecated patterns:** 3 instances found
- [ ] **External links verified:** 3 URLs flagged for manual check
```

---

## Quarterly Review Schedule

Recommended STALENESS review cadence:

- **README.md** - Frequency: Quarterly, Priority: High
- **CONTRIBUTING.md** - Frequency: Quarterly, Priority: High
- **docs/ARCHITECTURE.md** - Frequency: Semi-annually, Priority: Medium
- **docs/*.md (other)** - Frequency: Annually, Priority: Low

**Trigger events for immediate STALENESS review:**

- Major version release
- Dependency updates (Python, uv, Ruff, etc.)
- Project structure changes
- CI/CD pipeline changes

