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
reviews/doc-reviews/README-claude-sonnet45-2025-12-16.md
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
- **Accuracy** - Score: 4/5, Notes: 3 outdated references found

**Focus Area:** Accuracy - Codebase alignment verification

**Reviewing Model:** Claude Sonnet 4.5

### Cross-Reference Verification

- **`scripts/rule_deployer.py`** - Type: file, Location: README:45, Exists?: , Notes: —
- **`scripts/schema_validator.py`** - Type: file, Location: README:52, Exists?: , Notes: —
- **`scripts/template_generator.py`** - Type: file, Location: README:58, Exists?: , Notes: —
- **`scripts/old_generator.py`** - Type: file, Location: README:112, Exists?: , Notes: Removed in v3.0
- **`task deploy`** - Type: command, Location: README:78, Exists?: , Notes: —
- **`task generate:rules`** - Type: command, Location: README:85, Exists?: , Notes: Command renamed
- **`task validate`** - Type: command, Location: README:92, Exists?: , Notes: —
- **`pyproject.toml`** - Type: file, Location: README:134, Exists?: , Notes: —
- **`Taskfile.yml`** - Type: file, Location: README:140, Exists?: , Notes: —
- **`rules/`** - Type: directory, Location: README:156, Exists?: , Notes: —
- **`docs/ARCHITECTURE.md`** - Type: file, Location: README:178, Exists?: , Notes: —
- **`config.yaml`** - Type: file, Location: README:190, Exists?: , Notes: File never existed

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
- **Clarity** - Score: 3/5, Notes: Technical jargon, missing examples

**Focus Area:** Clarity - User experience and readability

**Reviewing Model:** Claude Sonnet 4.5

### Clarity Analysis

#### Reading Level Assessment
- **Target audience:** Developers familiar with AI coding tools
- **Current level:** Advanced (assumes significant prior knowledge)
- **Recommended level:** Intermediate (add explanations for newcomers)

#### Jargon Audit

- **"progressive disclosure"** - Location: Line 45, Defined?: , Suggestion: Add brief definition
- **"token budget"** - Location: Line 78, Defined?: , Suggestion: Definition exists but buried
- **"ContextTier"** - Location: Line 112, Defined?: , Suggestion: Well explained
- **"semantic discovery"** - Location: Line 156, Defined?: , Suggestion: Needs explanation
- **"agent-agnostic"** - Location: Line 189, Defined?: , Suggestion: Clarify meaning

#### Example Coverage

- **Rule Creation Flow** - Has Examples?: , Quality: Good - code + diagram
- **Deployment System** - Has Examples?: , Quality: Good - command examples
- **Schema Validation** - Has Examples?: , Quality: Partial - missing error examples
- **Testing Infrastructure** - Has Examples?: , Quality: No examples

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

