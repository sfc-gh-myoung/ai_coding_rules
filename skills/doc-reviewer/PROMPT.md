# Documentation Review Prompt (Template)

```markdown
## Documentation Review Request

**Target File(s):** [path/to/doc.md or list of paths]
**Review Date:** [YYYY-MM-DD]
**Review Mode:** [FULL | FOCUSED | STALENESS]
**Review Scope:** [single | collection]

**Review Objective:** Evaluate project documentation for accuracy with the codebase,
completeness of coverage, clarity for users, consistency with project conventions,
staleness of references, and logical structure.

### Dimension Point Allocation

Points are allocated based on criticality for human user success:

| Dimension | Points | Rationale |
|-----------|--------|-----------|
| **Accuracy** | 25 | Critical - wrong information misleads users |
| **Completeness** | 25 | Critical - missing information blocks users |
| Clarity | 20 | Important - users need understandable prose |
| Structure | 15 | Important - users need good navigation |
| Staleness | 10 | Affects usability over time |
| Consistency | 5 | Polish - style matters less than content |

**Scoring formula:**
- Accuracy: X/5 × 5 = Y/25
- Completeness: X/5 × 5 = Y/25
- Clarity: X/5 × 4 = Y/20
- Structure: X/5 × 3 = Y/15
- Staleness: X/5 × 2 = Y/10
- Consistency: X/5 × 1 = Y/5
- **Total: Z/100**

---

### Review Criteria

Analyze the documentation against these criteria, scoring each 1-5 (5 = excellent):

#### 1. Accuracy (Is documentation current with the codebase?) — 25 points

- Do file paths mentioned in docs actually exist?
- Do commands shown (e.g., `task deploy`, `python scripts/...`) work as documented?
- Are function/class names accurate and current?
- Do code examples reflect actual implementation?
- Are configuration options and defaults correct?
- **Use the Cross-Reference Verification Table** (mandatory) to systematically verify

**Scoring Scale:**
- **5/5:** 95%+ references verified; all commands work; code examples current.
- **4/5:** 90-95% references valid; 1-2 minor inaccuracies.
- **3/5:** 80-90% references valid; some commands outdated; examples mostly work.
- **2/5:** 60-80% references valid; multiple inaccuracies would mislead users.
- **1/5:** <60% references valid; documentation significantly out of sync.

**Quantifiable Metrics (Critical Dimension):**
- Percentage of code references verified as accurate
- Count of commands tested and working
- Count of broken file/function references

**Calibration Examples:**
- **5/5:** All 20 file references exist, all 5 commands work as documented
- **3/5:** 15/20 file references exist, 1 command has wrong flag
- **1/5:** README references `src/main.py` but file is `app/main.py`

#### 2. Completeness (Are all features documented?) — 25 points

- Are all major features and workflows documented?
- Are setup/installation steps complete?
- Are all public APIs documented?
- Are common use cases covered?
- Are troubleshooting sections present for complex features?
- What critical information is missing?

**Scoring Scale:**
- **5/5:** All features documented; setup complete; APIs covered; troubleshooting present.
- **4/5:** Major features covered; 1-2 minor features undocumented; setup complete.
- **3/5:** Core features documented; some workflows missing; partial API coverage.
- **2/5:** Significant gaps; users can't complete common tasks from docs alone.
- **1/5:** Minimal coverage; most features undocumented; incomplete setup.

**Quantifiable Metrics (Critical Dimension):**
- Percentage of features with documentation
- Setup completeness (prerequisite → install → verify checklist)
- Count of missing standard sections

**Calibration Examples:**
- **5/5:** README covers all 8 major features, CONTRIBUTING has full PR workflow
- **3/5:** 6/8 features documented, setup missing "verify installation" step
- **1/5:** Only describes what the project does, no setup or usage instructions

#### 3. Clarity (Is it user-friendly and intuitive?) — 20 points

- Can a new user follow the documentation without confusion?
- Are technical terms explained or linked?
- Are examples provided for complex concepts?
- Is the reading level appropriate for the target audience?
- Are visuals (diagrams, screenshots) used effectively?
- Is there a clear "getting started" path?

**Scoring Scale:**
- **5/5:** New user can follow without confusion; terms explained; examples present; clear path.
- **4/5:** Mostly clear; minor jargon unexplained; good examples.
- **3/5:** Understandable with effort; some confusing sections; inconsistent examples.
- **2/5:** Confusing flow; technical jargon barrier; sparse examples.
- **1/5:** Impenetrable to new users; assumes prior knowledge; no examples.

**Quantifiable Metrics:**
- New user test result (Yes/No with explanation)
- Count of unexplained technical terms
- Count of complex concepts without examples

**Calibration Examples:**
- **5/5:** "Getting Started" section guides user from clone to first successful run
- **3/5:** Setup works but user must know what "virtual environment" means
- **1/5:** "Run `make deploy-prod`" with no explanation of prerequisites

#### 4. Consistency (Does it follow project conventions?) — 5 points

- Does formatting match project style (headers, code blocks, lists)?
- Are naming conventions consistent throughout?
- Does terminology match the codebase?
- Are similar sections structured the same way?
- **If project has rules/801-project-readme.md or rules/802-project-contributing.md,
  verify compliance with those standards**

**Scoring Scale:**
- **5/5:** Formatting consistent; naming matches codebase; follows project rules.
- **4/5:** Minor formatting inconsistencies; terminology mostly aligned.
- **3/5:** Some style drift; terminology inconsistent in places.
- **2/5:** Noticeable inconsistencies throughout; doesn't follow project rules.
- **1/5:** No consistent style; terminology conflicts with codebase.

#### 5. Staleness (Are tool versions and links current?) — 10 points

- Are referenced tool versions current? (e.g., Python 3.11 vs 3.13)
- Are external links working and pointing to current content?
- Are deprecated features or patterns mentioned?
- Are dates and version numbers up to date?
- **Use the Link Validation Table** (mandatory) to systematically verify

**Scoring Scale:**
- **5/5:** All versions current; 0 broken links; no deprecated patterns.
- **4/5:** Versions mostly current; 1-2 broken links; minor staleness.
- **3/5:** Some outdated versions; 3-4 broken links; deprecated patterns mentioned.
- **2/5:** Multiple outdated versions; 5+ broken links; significant staleness.
- **1/5:** Severely outdated; most links broken; recommends deprecated approaches.

#### 6. Structure (Is organization logical and navigable?) — 15 points

- Is there a clear table of contents for long documents?
- Are sections ordered logically (overview → setup → usage → reference)?
- Can users find information quickly?
- Are related topics grouped together?
- Is navigation between documents clear?
- Are anchor links used effectively?

**Scoring Scale:**
- **5/5:** Logical flow; TOC present; easy navigation; related topics grouped.
- **4/5:** Good organization; minor navigation issues; mostly findable.
- **3/5:** Adequate structure; some sections misplaced; navigation unclear.
- **2/5:** Poor organization; hard to find information; no TOC for long docs.
- **1/5:** Random ordering; information scattered; impossible to navigate.

**Quantifiable Metrics:**
- TOC present for docs >100 lines? (Yes/No)
- Section ordering follows standard pattern? (Yes/No)
- Count of navigation aids (TOC, anchor links, cross-references)

**Calibration Examples:**
- **5/5:** README has TOC, follows Overview → Install → Usage → API → Contributing
- **3/5:** Information present but API docs before installation instructions
- **1/5:** Single wall of text with no headers or sections

### Output Format

Provide your assessment in this structure:

```markdown
## Documentation Review: [doc-name.md]

### Scores
| Criterion | Max | Raw | Points | Notes |
|-----------|-----|-----|--------|-------|
| Accuracy | 25 | X/5 | Y/25 | [brief justification] |
| Completeness | 25 | X/5 | Y/25 | [brief justification] |
| Clarity | 20 | X/5 | Y/20 | [brief justification] |
| Structure | 15 | X/5 | Y/15 | [brief justification] |
| Staleness | 10 | X/5 | Y/10 | [brief justification] |
| Consistency | 5 | X/5 | Y/5 | [brief justification] |

**Overall:** X/100

**Reviewing Model:** [Model name and version that performed this review]

### Overall Score Interpretation

| Score Range | Assessment | Verdict |
|-------------|------------|---------|
| 90-100 | Excellent | PUBLISHABLE |
| 80-89 | Good | PUBLISHABLE_WITH_EDITS |
| 60-79 | Needs Work | NEEDS_REVISION |
| 40-59 | Poor | NOT_PUBLISHABLE |
| <40 | Inadequate | NOT_PUBLISHABLE - Rewrite required |

**Critical dimension overrides:**
- If Accuracy ≤2/5 → Verdict = "NEEDS_REVISION" minimum
- If Completeness ≤2/5 → Verdict = "NEEDS_REVISION" minimum
- If 2+ critical dimensions ≤2/5 → Verdict = "NOT_PUBLISHABLE"

### Documentation Quality Verdict
**[PUBLISHABLE | NEEDS_REVISION | NOT_PUBLISHABLE]**

[1-2 sentence summary of why this verdict was assigned]

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
```

### Mandatory Verification Tables (Required for Scoring Justification)

Include these tables in your assessment to support your scores. These ensure systematic
analysis and provide actionable feedback.

#### Cross-Reference Verification Table (Required for Accuracy scoring)

Scan the documentation for code references and verify they exist in the codebase:

```markdown
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
```

**Scoring impact:** Each missing reference reduces Accuracy score.
More than 3 missing references = score ≤3/5.

#### Link Validation Table (Required for Staleness scoring)

Scan the documentation for all links and verify their status:

```markdown
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
```

**Scoring impact:** Each broken internal link reduces Staleness score.
More than 2 broken links = score ≤3/5.
External links flagged but don't reduce score (manual verification needed).

#### Baseline Compliance Check (Required for Consistency scoring)

If project has documentation rules, verify compliance:

```markdown
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
```

**Scoring impact:** Non-compliance with project rules reduces Consistency score.

### Documentation Perspective Checklist (REQUIRED)

Answer each question explicitly in your assessment:

- [ ] **New user test:** Can someone unfamiliar with the project get started using only this documentation? (Yes/No with explanation)
- [ ] **Accuracy audit:** What percentage of code references were verified as accurate? (e.g., "15/18 references valid = 83%")
- [ ] **Link health:** How many internal links are broken vs total? (e.g., "2 broken / 24 total")
- [ ] **Missing sections:** List any standard sections that are absent (e.g., "No troubleshooting section")
- [ ] **Staleness indicators:** List any outdated versions, deprecated patterns, or stale dates found

---

## Scoring Impact Rules (Algorithmic Overrides)

These rules override subjective assessment:

### Accuracy (25 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| <60% references valid | 1/5 | 5/25 |
| 60-80% references valid | 2/5 | 10/25 |
| 80-90% references valid | 3/5 | 15/25 |
| 90-95% references valid | 4/5 | 20/25 |
| >95% references valid | 5/5 | 25/25 |

### Completeness (25 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| Minimal coverage (<40% features) | 1/5 | 5/25 |
| Incomplete setup + major gaps | 2/5 | 10/25 |
| Core features covered, some gaps | 3/5 | 15/25 |
| Major features covered | 4/5 | 20/25 |
| All features + troubleshooting | 5/5 | 25/25 |

### Clarity (20 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| Impenetrable to new users | 1/5 | 4/20 |
| Confusing flow, jargon barrier | 2/5 | 8/20 |
| Understandable with effort | 3/5 | 12/20 |
| Mostly clear, minor issues | 4/5 | 16/20 |
| New user succeeds without confusion | 5/5 | 20/20 |

### Structure (15 points)
| Finding | Maximum Score | Max Points |
|---------|---------------|------------|
| Random ordering, no structure | 1/5 | 3/15 |
| Poor organization, hard to navigate | 2/5 | 6/15 |
| Adequate structure, some issues | 3/5 | 9/15 |
| Good organization, mostly findable | 4/5 | 12/15 |
| Logical flow, TOC, easy navigation | 5/5 | 15/15 |

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
```

