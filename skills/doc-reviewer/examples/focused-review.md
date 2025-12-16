# Example: FOCUSED Review

## Accuracy Focus

```text
Use the doc-reviewer skill.

target_files: [README.md]
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: accuracy
model: claude-sonnet45
```

**What happens:**

1. Reviews only the Accuracy dimension
2. Generates detailed Cross-Reference Verification Table
3. Skips other dimensions and tables
4. Faster, targeted output

**Expected output file:**

```
reviews/README-claude-sonnet45-2025-12-16.md
```

---

## Staleness Focus

```text
Use the doc-reviewer skill.

target_files: [README.md, CONTRIBUTING.md]
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: staleness
model: claude-sonnet45
```

**What happens:**

1. Reviews only the Staleness dimension
2. Generates Link Validation Table
3. Checks for outdated versions, deprecated patterns
4. Quick health check for documentation currency

---

## Clarity Focus

```text
Use the doc-reviewer skill.

target_files: [docs/ARCHITECTURE.md]
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: clarity
model: claude-sonnet45
```

**What happens:**

1. Reviews only the Clarity dimension
2. Assesses readability and user experience
3. Identifies jargon, unclear explanations
4. Suggests improvements for new users

---

## Sample FOCUSED Review Output (Accuracy)

```markdown
## Documentation Review: README.md (FOCUSED: Accuracy)

### Score
| Criterion | Score | Notes |
|-----------|-------|-------|
| Accuracy | 4/5 | 3 outdated references found |

**Focus Area:** Accuracy - Codebase alignment verification

**Reviewing Model:** Claude Sonnet 4.5

### Cross-Reference Verification

| Reference | Type | Location | Exists? | Notes |
|-----------|------|----------|---------|-------|
| `scripts/rule_deployer.py` | file | README:45 | ✅ | — |
| `scripts/schema_validator.py` | file | README:52 | ✅ | — |
| `scripts/template_generator.py` | file | README:58 | ✅ | — |
| `scripts/old_generator.py` | file | README:112 | ❌ | Removed in v3.0 |
| `task deploy` | command | README:78 | ✅ | — |
| `task generate:rules` | command | README:85 | ❌ | Command renamed |
| `task validate` | command | README:92 | ✅ | — |
| `pyproject.toml` | file | README:134 | ✅ | — |
| `Taskfile.yml` | file | README:140 | ✅ | — |
| `rules/` | directory | README:156 | ✅ | — |
| `docs/ARCHITECTURE.md` | file | README:178 | ✅ | — |
| `config.yaml` | file | README:190 | ❌ | File never existed |

**Summary:**
- Total references: 12
- Valid: 9 (75%)
- Invalid: 3 (25%)

### Critical Issues (Must Fix)

1. **Location:** Line 112
   **Problem:** References `scripts/old_generator.py` which was removed in v3.0
   **Recommendation:** Remove reference or update to `scripts/template_generator.py`

2. **Location:** Line 85
   **Problem:** Command `task generate:rules` no longer exists
   **Recommendation:** Update to `task rule:new` or remove section

3. **Location:** Line 190
   **Problem:** References `config.yaml` which doesn't exist in project
   **Recommendation:** Remove reference or clarify this is user-created

### Accuracy Assessment

**Literal execution test:** If a user followed the documented commands:
- 9/12 commands/paths would work correctly
- 3 would fail with "file not found" or "task not found"

**Recommendation:** Fix the 3 critical issues to achieve 100% accuracy.
```

---

## Sample FOCUSED Review Output (Clarity)

```markdown
## Documentation Review: docs/ARCHITECTURE.md (FOCUSED: Clarity)

### Score
| Criterion | Score | Notes |
|-----------|-------|-------|
| Clarity | 3/5 | Technical jargon, missing examples |

**Focus Area:** Clarity - User experience and readability

**Reviewing Model:** Claude Sonnet 4.5

### Clarity Analysis

#### Reading Level Assessment
- **Target audience:** Developers familiar with AI coding tools
- **Current level:** Advanced (assumes significant prior knowledge)
- **Recommended level:** Intermediate (add explanations for newcomers)

#### Jargon Audit

| Term | Location | Defined? | Suggestion |
|------|----------|----------|------------|
| "progressive disclosure" | Line 45 | ❌ | Add brief definition |
| "token budget" | Line 78 | ⚠️ | Definition exists but buried |
| "ContextTier" | Line 112 | ✅ | Well explained |
| "semantic discovery" | Line 156 | ❌ | Needs explanation |
| "agent-agnostic" | Line 189 | ❌ | Clarify meaning |

#### Example Coverage

| Section | Has Examples? | Quality |
|---------|---------------|---------|
| Rule Creation Flow | ✅ | Good - code + diagram |
| Deployment System | ✅ | Good - command examples |
| Schema Validation | ⚠️ | Partial - missing error examples |
| Testing Infrastructure | ❌ | No examples |

### Critical Issues (Must Fix)

1. **Location:** Lines 45-60
   **Problem:** "Progressive disclosure" used 5 times without definition
   **Recommendation:** Add definition: "Progressive disclosure: revealing information gradually as needed, rather than all at once"

2. **Location:** Lines 200-250
   **Problem:** Testing section has no examples
   **Recommendation:** Add sample test commands and expected output

### Improvements (Should Fix)

1. **Location:** Line 78
   **Problem:** Token budget definition is in a footnote
   **Recommendation:** Move to main text or add glossary section

### New User Test

**Can someone unfamiliar with the project understand this document?**

No - the document assumes familiarity with:
- AI coding assistants and their context windows
- Token counting and budget management
- YAML schema validation
- The project's rule numbering system

**Recommendation:** Add a "Prerequisites" or "Background" section explaining these concepts, or link to explanatory resources.
```

