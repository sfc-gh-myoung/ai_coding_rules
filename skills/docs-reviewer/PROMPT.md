# Documentation Review Prompt (Template)

~~~~markdown
## Documentation Review Request

**Target File(s):** [path/to/doc.md or list of paths]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** [FULL | FOCUSED | STALENESS]
**Review Scope:** [single | collection]

**Review Objective:** Evaluate project documentation for accuracy with the codebase,
completeness of coverage, clarity for users, consistency with project conventions,
staleness of references, and logical structure.

### Review Criteria

Analyze the documentation against these criteria, scoring each 1-5 (5 = excellent):

#### 1. Accuracy (Is documentation current with the codebase?)

- Do file paths mentioned in docs actually exist?
- Do commands shown (e.g., `task deploy`, `python scripts/...`) work as documented?
- Are function/class names accurate and current?
- Do code examples reflect actual implementation?
- Are configuration options and defaults correct?
- **Use the Cross-Reference Verification Table** (mandatory) to systematically verify

#### 2. Completeness (Are all features documented?)

- Are all major features and workflows documented?
- Are setup/installation steps complete?
- Are all public APIs documented?
- Are common use cases covered?
- Are troubleshooting sections present for complex features?
- What critical information is missing?

#### 3. Clarity (Is it user-friendly and intuitive?)

- Can a new user follow the documentation without confusion?
- Are technical terms explained or linked?
- Are examples provided for complex concepts?
- Is the reading level appropriate for the target audience?
- Are visuals (diagrams, screenshots) used effectively?
- Is there a clear "getting started" path?

#### 4. Consistency (Does it follow project conventions?)

- Does formatting match project style (headers, code blocks, lists)?
- Are naming conventions consistent throughout?
- Does terminology match the codebase?
- Are similar sections structured the same way?
- **If project has rules/801-project-readme.md or rules/802-project-contributing.md,
  verify compliance with those standards**

#### 5. Staleness (Are tool versions and links current?)

- Are referenced tool versions current? (e.g., Python 3.11 vs 3.13)
- Are external links working and pointing to current content?
- Are deprecated features or patterns mentioned?
- Are dates and version numbers up to date?
- **Use the Link Validation Table** (mandatory) to systematically verify

#### 6. Structure (Is organization logical and navigable?)

- Is there a clear table of contents for long documents?
- Are sections ordered logically (overview → setup → usage → reference)?
- Can users find information quickly?
- Are related topics grouped together?
- Is navigation between documents clear?
- Are anchor links used effectively?

### Output Format

Provide your assessment in this structure:

~~~markdown
## Documentation Review: [doc-name.md]

### Scores
| Criterion | Score | Notes |
|-----------|-------|-------|
| Accuracy | X/5 | [brief justification] |
| Completeness | X/5 | [brief justification] |
| Clarity | X/5 | [brief justification] |
| Consistency | X/5 | [brief justification] |
| Staleness | X/5 | [brief justification] |
| Structure | X/5 | [brief justification] |

**Overall:** X/30

**Reviewing Model:** [Model name and version that performed this review]

### Critical Issues (Must Fix)
[List issues that would cause user confusion or incorrect behavior]

### Improvements (Should Fix)
[List issues that would improve documentation quality]

### Minor Suggestions (Nice to Have)
[List stylistic or optimization suggestions]

### Specific Recommendations
For each issue, provide:
1. **Location:** Line number or section name
2. **Problem:** What's wrong and why it matters for users
3. **Recommendation:** Specific fix with example if helpful
~~~

### Mandatory Verification Tables (Required for Scoring Justification)

Include these tables in your assessment to support your scores. These ensure systematic
analysis and provide actionable feedback.

#### Cross-Reference Verification Table (Required for Accuracy scoring)

Scan the documentation for code references and verify they exist in the codebase:

~~~markdown
**Cross-Reference Verification:**

| Reference | Type | Location in Doc | Exists? | Notes |
|-----------|------|-----------------|---------|-------|
| `scripts/deploy.py` | file | README.md:45 | ✅ | — |
| `task validate` | command | README.md:78 | ✅ | — |
| `utils.parse_config()` | function | docs/API.md:23 | ❌ | Not found in codebase |
| `docs/ARCHITECTURE.md` | file | README.md:102 | ✅ | — |
| `pyproject.toml` | file | CONTRIBUTING.md:34 | ✅ | — |

**Reference Types to Check:**
- `file`: File paths (*.py, *.md, *.yml, etc.)
- `directory`: Directory paths (ending with /)
- `command`: CLI commands (task, python, npm, etc.)
- `function`: Function/method references
- `class`: Class references
- `config`: Configuration keys/values
~~~

**Scoring impact:** Each missing reference reduces Accuracy score.
More than 3 missing references = score ≤3/5.

#### Link Validation Table (Required for Staleness scoring)

Scan the documentation for all links and verify their status:

~~~markdown
**Link Validation:**

| Link | Type | Source Location | Status | Notes |
|------|------|-----------------|--------|-------|
| `./docs/API.md` | internal | README.md:12 | ✅ | — |
| `#installation` | anchor | README.md:5 | ✅ | Heading exists |
| `../CONTRIBUTING.md` | internal | docs/setup.md:89 | ✅ | — |
| `https://docs.python.org` | external | README.md:156 | ⚠️ | Manual check needed |
| `./missing-file.md` | internal | CONTRIBUTING.md:34 | ❌ | File not found |
| `#nonexistent-heading` | anchor | README.md:78 | ❌ | Anchor not found |

**Link Types:**
- `internal`: Relative paths to project files
- `anchor`: Same-document heading links (#section-name)
- `external`: URLs to external resources (flag for manual check)

**Status Legend:**
- ✅ Verified (internal links checked, anchors validated)
- ⚠️ Manual check needed (external URLs)
- ❌ Broken (file/anchor not found)
~~~

**Scoring impact:** Each broken internal link reduces Staleness score.
More than 2 broken links = score ≤3/5.
External links flagged but don't reduce score (manual verification needed).

#### Baseline Compliance Check (Required for Consistency scoring)

If project has documentation rules, verify compliance:

~~~markdown
**Baseline Compliance Check:**

Checking against: [rules/801-project-readme.md | rules/802-project-contributing.md | General best practices]

| Requirement | Source | Compliant? | Notes |
|-------------|--------|------------|-------|
| Quick Start section present | 801 | ✅ | Lines 45-78 |
| Prerequisites listed | 801 | ✅ | Lines 23-35 |
| License section | 801 | ❌ | Missing |
| Code of Conduct reference | 802 | ⚠️ | Present but outdated |
| PR guidelines | 802 | ✅ | Lines 89-120 |

**If no project rules found:**
- Using general documentation best practices
- Note: Consider creating rules/801-project-readme.md for consistent standards
~~~

**Scoring impact:** Non-compliance with project rules reduces Consistency score.

### Documentation Perspective Checklist (REQUIRED)

Answer each question explicitly in your assessment:

- [ ] **New user test:** Can someone unfamiliar with the project get started using only this documentation? (Yes/No with explanation)
- [ ] **Accuracy audit:** What percentage of code references were verified as accurate? (e.g., "15/18 references valid = 83%")
- [ ] **Link health:** How many internal links are broken vs total? (e.g., "2 broken / 24 total")
- [ ] **Missing sections:** List any standard sections that are absent (e.g., "No troubleshooting section")
- [ ] **Staleness indicators:** List any outdated versions, deprecated patterns, or stale dates found

---

### Output Guidelines

- **Target length (flexible based on document size):**
  - **Concise:** 100-150 lines (small docs, focused reviews)
  - **Standard:** 150-250 lines (typical README, FULL mode)
  - **Comprehensive:** 300+ lines (large doc collections, include all tables)
- **Code examples:** Include fix examples for Critical issues; optional for Minor suggestions
- **Line references:** Always include line numbers or section names for issues
- **Prioritization:** If >10 issues found, group by implementation priority

## Review Modes

### FULL Mode (Comprehensive)
Use for initial documentation review or major updates. Evaluates all 6 criteria with
detailed recommendations and all verification tables.

### FOCUSED Mode (Targeted)
Use when you know specific areas need attention. Specify which criteria to evaluate
via `focus_area` parameter.

**Available focus areas:**
- `accuracy` - Cross-reference verification only
- `completeness` - Coverage analysis only
- `clarity` - Readability and user experience only
- `consistency` - Style and convention compliance only
- `staleness` - Link validation and version checking only
- `structure` - Organization and navigation only

### STALENESS Mode (Periodic Maintenance)
Use for quarterly/annual documentation audits. Focuses on criteria 5-6 (Staleness,
Structure) plus link validation. Quick check for drift from codebase.

**For FOCUSED/STALENESS modes:** Include only the relevant Mandatory Verification Tables.

### Output File (REQUIRED)

Save your full review output as a Markdown file under `reviews/` using this filename
format:

**Single scope (default):**
`reviews/<doc-name>-<model>-<YYYY-MM-DD>.md`

**Collection scope:**
`reviews/docs-collection-<model>-<YYYY-MM-DD>.md`

Rules:
- `<doc-name>`: base name of **Target File** with no extension
  (example: `README.md` → `README`, `docs/ARCHITECTURE.md` → `ARCHITECTURE`)
- `<model>`: lowercase, hyphenated model identifier
  (example: `claude-sonnet45`, `gpt-52`)
- `<YYYY-MM-DD>`: **Review Date**

Examples:
- Target File: `README.md`
- Reviewing Model: `Claude Sonnet 4.5`
- Review Date: `2025-12-16`
- Output file: `reviews/README-claude-sonnet45-2025-12-16.md`

Collection example:
- Target Files: `README.md`, `CONTRIBUTING.md`, `docs/*.md`
- Review Scope: `collection`
- Output file: `reviews/docs-collection-claude-sonnet45-2025-12-16.md`

If you cannot write files in this environment, output the full Markdown content and
include the intended path on the first line exactly as:

`OUTPUT_FILE: reviews/<doc-name>-<model>-<YYYY-MM-DD>.md`
<!-- End of prompt template -->
<!-- EOF -->
~~~~

