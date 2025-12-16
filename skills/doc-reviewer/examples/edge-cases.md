# Edge Cases: Documentation Reviewer

This document captures ambiguous scenarios, unusual inputs, and their resolutions for the documentation review workflow.

## Edge Case 1: No Documentation Files Found

**Scenario:** Project has no standard documentation files

**Example:**

```
target_files: (not provided)
# And project has no README.md, CONTRIBUTING.md, or docs/ folder
```

**Resolution Pattern:**

```
Input validation failed: No documentation files found.

Checked locations:
- ./README.md (not found)
- ./CONTRIBUTING.md (not found)
- ./docs/*.md (directory missing)

Options:
A. Specify target_files explicitly if docs are in non-standard location
B. Create documentation first using project templates
C. Check if documentation exists under different names (readme.md, Readme.md)

Common alternative locations:
- ./wiki/
- ./documentation/
- ./guides/
- ./manual/

To proceed, specify: target_files: [path/to/your/docs.md]
```

---

## Edge Case 2: Mixed File Types in Target List

**Scenario:** User includes non-markdown files in target_files

**Example:**

```
target_files: [README.md, src/config.py, docs/guide.md]
```

**Resolution Pattern:**

```
Input validation warning: Non-markdown files in target list.

Files provided:
- README.md ✅ (markdown)
- src/config.py ❌ (Python file)
- docs/guide.md ✅ (markdown)

This skill reviews markdown documentation only.

Options:
A. Proceed with markdown files only (README.md, docs/guide.md)
B. Cancel and provide corrected list

Recommendation: Option A

Proceeding with: [README.md, docs/guide.md]
```

---

## Edge Case 3: FOCUSED Mode Without Focus Area

**Scenario:** User selects FOCUSED mode but doesn't specify focus_area

**Example:**

```
target_files: [README.md]
review_mode: FOCUSED
focus_area: (not provided)
```

**Resolution Pattern:**

```
FOCUSED review requires a focus_area parameter.

Available focus areas for documentation reviews:
A. accuracy - Cross-reference verification (code refs exist?)
B. completeness - Coverage analysis (all features documented?)
C. clarity - Readability assessment (user-friendly?)
D. consistency - Style compliance (follows conventions?)
E. staleness - Link validation (links work? versions current?)
F. structure - Organization review (logical flow?)

Please specify: focus_area: [A|B|C|D|E|F]

Or switch to FULL mode for comprehensive evaluation.
```

---

## Edge Case 4: Documentation References Non-Existent Files

**Scenario:** Docs reference code files that don't exist

**Example:**

```
# In README.md line 45:
See `scripts/deprecated_tool.py` for details.

# But scripts/deprecated_tool.py doesn't exist
```

**Resolution Pattern:**

```
Cross-reference verification found issues:

| Reference | Type | Location | Exists? | Notes |
|-----------|------|----------|---------|-------|
| `scripts/deprecated_tool.py` | file | README:45 | ❌ | Not found |

Impact on review:
- Reduces Accuracy score
- Flagged as Critical issue

Options:
A. Proceed with review, flag as issue (recommended)
B. Pause review, fix documentation first

Recommendation: Option A
The review will note this as a CRITICAL issue requiring immediate fix.
```

---

## Edge Case 5: Very Large Documentation Set

**Scenario:** Project has many documentation files

**Example:**

```
target_files: (not provided)
# Project has 25+ markdown files in docs/
```

**Resolution Pattern:**

```
Large documentation set detected:

Files found: 27
- README.md
- CONTRIBUTING.md
- docs/*.md (25 files)

Estimated review time: 10-15 minutes (FULL mode)

Options:
A. Proceed with FULL review of all files
B. Use collection scope for consolidated output
C. Use STALENESS mode for quick health check
D. Review subset: target_files: [README.md, CONTRIBUTING.md, docs/ARCHITECTURE.md]

Recommendation:
- For comprehensive audit: Option A or B
- For periodic maintenance: Option C
- For focused review: Option D

Proceeding with option: [user choice]
```

---

## Edge Case 6: Documentation Has No Baseline Rules

**Scenario:** Project doesn't have rules/801-* or rules/802-* files

**Example:**

```
# Project structure:
rules/
├── 000-global-core.md
├── 200-python-core.md
└── (no 801 or 802 rules)
```

**Resolution Pattern:**

```
Baseline rules not found:

Checked:
- rules/801-project-readme.md ❌ (not found)
- rules/802-project-contributing.md ❌ (not found)

Impact on review:
- Consistency scoring will use general best practices
- No project-specific standards to verify against

Options:
A. Proceed with general best practices (recommended)
B. Create baseline rules first, then review

Proceeding with baseline: General documentation best practices

Note in review:
"Baseline: General best practices (no project-specific rules found)"
```

---

## Edge Case 7: Collection Review with Single File

**Scenario:** User requests collection scope but only one file

**Example:**

```
target_files: [README.md]
review_scope: collection
```

**Resolution Pattern:**

```
Collection scope with single file:

Files: 1 (README.md)
Requested scope: collection

Collection scope is designed for multiple documents.
With a single file, output will be identical to single scope.

Options:
A. Proceed with collection scope (single-file collection)
B. Switch to single scope (recommended for clarity)

Recommendation: Option B

Using scope: single
Output: reviews/README-claude-sonnet45-2025-12-16.md
```

---

## Edge Case 8: Review Output File Already Exists (All Suffixes)

**Scenario:** Base filename and all numbered suffixes exist

**Example:**

```
Existing files:
- reviews/README-claude-sonnet45-2025-12-16.md
- reviews/README-claude-sonnet45-2025-12-16-01.md
- reviews/README-claude-sonnet45-2025-12-16-02.md
... through -99.md
```

**Resolution Pattern:**

```
Output filename exhausted:

All suffix slots (01-99) are occupied for:
reviews/README-claude-sonnet45-2025-12-16-XX.md

Options:
A. Use different date (tomorrow's date)
B. Use different model slug
C. Archive old reviews and reuse base filename
D. Use timestamp suffix

Recommendation: Option D

Alternative filename:
reviews/README-claude-sonnet45-2025-12-16-1734355200.md
(using Unix timestamp)
```

---

## Edge Case 9: Documentation Contains Placeholder Text

**Scenario:** Documentation has TODO markers or template placeholders

**Example:**

```markdown
## Installation

[TODO: Add installation steps]

## Usage

See [LINK_TO_DOCS] for more information.
```

**Resolution Pattern:**

```
Placeholder content detected:

File: README.md
Placeholders found:
- Line 12: "[TODO: Add installation steps]"
- Line 18: "[LINK_TO_DOCS]"

Review handling options:
A. Proceed with review, flag placeholders as Critical issues
B. Decline review - documentation incomplete
C. Review structure only, skip content scoring

Recommendation: Option A

The review will:
- Flag each placeholder as CRITICAL issue
- Reduce Completeness score significantly
- Provide specific recommendations for each placeholder
```

---

## Edge Case 10: External Links Only (No Internal Links)

**Scenario:** Documentation only links to external resources

**Example:**

```markdown
# Project

See [Python Docs](https://docs.python.org) for language reference.
See [Taskfile](https://taskfile.dev) for task runner.
```

**Resolution Pattern:**

```
Link validation note:

External links found: 5
Internal links found: 0

All links are external URLs, which cannot be automatically verified.

Link Validation Table:
| Link | Type | Source | Status | Notes |
|------|------|--------|--------|-------|
| https://docs.python.org | external | README:5 | ⚠️ | Manual check |
| https://taskfile.dev | external | README:8 | ⚠️ | Manual check |

Impact on scoring:
- Staleness score based on URL patterns and version references
- No internal link health to assess
- Consider adding internal cross-references

Recommendation in review:
"Consider adding internal links to other project documentation
(e.g., ./docs/ARCHITECTURE.md, ./CONTRIBUTING.md) to improve
navigation and reduce dependency on external resources."
```

---

## Quick Reference: Edge Case Decision Tree

```
Is target_files provided?
├─ YES → Validate each file exists and is .md
│   ├─ All valid → Proceed
│   └─ Some invalid → Warn, proceed with valid only
└─ NO → Use defaults
    ├─ Defaults found → Proceed
    └─ No defaults → Error, request explicit targets

Is review_mode FOCUSED?
├─ YES → Is focus_area provided?
│   ├─ YES → Proceed
│   └─ NO → Request focus_area
└─ NO → Proceed

Is review_scope collection?
├─ YES → Multiple files?
│   ├─ YES → Proceed with collection
│   └─ NO → Suggest single scope
└─ NO → Proceed with single

Are baseline rules available?
├─ YES → Use for Consistency scoring
└─ NO → Use general best practices

Does documentation have placeholders?
├─ YES → Flag as Critical issues
└─ NO → Proceed normally

Is output filename available?
├─ YES → Write file
└─ NO → Use suffix or timestamp
```

---

## Integration Notes

### With rule-reviewer

The doc-reviewer is independent from rule-reviewer:

- Different target files (docs vs rules)
- Different dimensions (Accuracy vs Actionability)
- Same output location (reviews/)
- Different filename patterns

### Cross-Skill Validation

When reviewing documentation that references rules:

```
# In README.md:
See rules/801-project-readme.md for README standards.
```

The doc-reviewer will:
1. Verify the rule file exists (Cross-Reference)
2. NOT review the rule file itself (that's rule-reviewer's job)
3. Note if the rule is used as a baseline

### Quality Thresholds

Suggested thresholds for documentation quality:

| Metric | Good | Acceptable | Needs Work |
|--------|------|------------|------------|
| Overall Score | ≥90/100 | 70-89/100 | <70/100 |
| Accuracy | ≥20/25 | 15-19/25 | <15/25 |
| Broken Links | 0 | 1-2 | ≥3 |
| Placeholders | 0 | 0 | ≥1 |

