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
reviews/README-claude-sonnet45-2025-12-16.md
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
reviews/docs-collection-claude-sonnet45-2025-12-16.md
```

---

## When to Use STALENESS Mode

| Scenario | Recommended Mode |
|----------|------------------|
| Quarterly documentation audit | STALENESS |
| After major release | STALENESS |
| Before publishing docs | FULL |
| After dependency updates | STALENESS |
| Initial documentation review | FULL |
| Fixing specific issues | FOCUSED |

---

## Sample STALENESS Review Output

```markdown
## Documentation Review: README.md (STALENESS)

### Scores
| Criterion | Score | Notes |
|-----------|-------|-------|
| Staleness | 3/5 | Multiple outdated references |
| Structure | 5/5 | Well organized |

**Overall:** 8/10 (Staleness mode)

**Reviewing Model:** Claude Sonnet 4.5

### Link Validation

| Link | Type | Source | Status | Notes |
|------|------|--------|--------|-------|
| `./docs/ARCHITECTURE.md` | internal | README:12 | ✅ | — |
| `./docs/MEMORY_BANK.md` | internal | README:18 | ✅ | — |
| `./CONTRIBUTING.md` | internal | README:24 | ✅ | — |
| `#quick-start` | anchor | README:5 | ✅ | — |
| `#troubleshooting` | anchor | README:8 | ✅ | — |
| `#installation` | anchor | README:6 | ❌ | Heading renamed to "Prerequisites" |
| `./docs/DEPRECATED.md` | internal | README:134 | ❌ | File removed |
| `https://taskfile.dev` | external | README:89 | ⚠️ | Manual check needed |
| `https://docs.python.org/3.11` | external | README:156 | ⚠️ | Consider updating to 3.13 |
| `https://github.com/user/repo` | external | README:200 | ⚠️ | Manual check needed |

**Link Summary:**
- Internal links: 4 valid, 2 broken
- Anchor links: 2 valid, 1 broken
- External links: 3 flagged for manual check

### Version References

| Technology | Documented Version | Current Version | Status |
|------------|-------------------|-----------------|--------|
| Python | 3.11 | 3.13 | ⚠️ Update recommended |
| Task | v3.x | v3.40 | ✅ Current |
| uv | 0.4.x | 0.5.x | ⚠️ Minor update available |
| Ruff | 0.7.x | 0.8.x | ⚠️ Minor update available |

### Deprecated Patterns Found

| Pattern | Location | Issue | Recommendation |
|---------|----------|-------|----------------|
| `pip install` | README:67 | Project uses uv | Change to `uv pip install` or `uv sync` |
| `python setup.py` | README:89 | Deprecated in favor of pyproject.toml | Remove or update to `uv pip install -e .` |
| `pytest.ini` | README:112 | Config now in pyproject.toml | Update reference |

### Staleness Indicators Found

- **Tool Versions:** Python 3.11 documented, 3.13 is current
- **Deprecated Patterns:** 3 instances of outdated installation methods
- **API Changes:** None detected
- **Industry Shifts:** pip → uv transition not fully reflected

### Structure Assessment

| Aspect | Score | Notes |
|--------|-------|-------|
| Table of Contents | ✅ | Present and accurate |
| Section Ordering | ✅ | Logical flow |
| Navigation | ✅ | Clear anchor links |
| Grouping | ✅ | Related topics together |

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

| Risk Level | Count | Action |
|------------|-------|--------|
| 🔴 High (broken links) | 3 | Fix immediately |
| 🟡 Medium (outdated versions) | 4 | Update in next release |
| 🟢 Low (style/minor) | 2 | Track for future |

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

| Document Type | Frequency | Priority |
|---------------|-----------|----------|
| README.md | Quarterly | High |
| CONTRIBUTING.md | Quarterly | High |
| docs/ARCHITECTURE.md | Semi-annually | Medium |
| docs/*.md (other) | Annually | Low |

**Trigger events for immediate STALENESS review:**

- Major version release
- Dependency updates (Python, uv, Ruff, etc.)
- Project structure changes
- CI/CD pipeline changes

