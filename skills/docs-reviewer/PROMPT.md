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

### Dimension Weighting

Not all review dimensions have equal impact. Use these weights when calculating overall scores:

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| **Accuracy** | 2× | Critical - incorrect docs worse than no docs |
| **Completeness** | 2× | Critical - missing info blocks user progress |
| **Staleness** | 2× | Critical - outdated docs are incorrect docs; users waste time on wrong info |
| Clarity | 1× | Important but users can work through confusion |
| Consistency | 1× | Quality concern, not correctness blocker |
| Structure | 1× | UX optimization, not content correctness |

**Weighted scoring formula:**
- Accuracy: X/5 × 2 = Y/10
- Completeness: X/5 × 2 = Y/10
- Staleness: X/5 × 2 = Y/10
- Clarity: X/5 × 1 = Y/5
- Consistency: X/5 × 1 = Y/5
- Structure: X/5 × 1 = Y/5
- **Total: Z/45**

### Review Criteria

Analyze the documentation against these criteria, scoring each 1-5 (5 = excellent):

#### 1. Accuracy (Is documentation current with the codebase?) — Weight: 2×

- Do file paths mentioned in docs actually exist?
- Do commands shown (e.g., `task deploy`, `python scripts/...`) work as documented?
- Are function/class names accurate and current?
- Do code examples reflect actual implementation?
- Are configuration options and defaults correct?
- **Use the Cross-Reference Verification Table** (mandatory) to systematically verify

**Scoring Scale:**
- **5/5:** 100% of code references verified; all commands work; all paths exist.
- **4/5:** 95-99% references valid; 1-2 minor inaccuracies (typos, outdated defaults).
- **3/5:** 85-94% references valid; 3-5 missing references; some commands may fail.
- **2/5:** 70-84% references valid; >5 missing references; significant inaccuracies.
- **1/5:** <70% references valid; docs actively mislead users; commands fail systematically.

**Quantifiable Metrics (Critical Dimension):**
- Percentage of code references verified via Cross-Reference Verification Table
- Count of file paths that don't exist
- Count of commands that fail when executed

#### 2. Completeness (Are all features documented?) — Weight: 2×

- Are all major features and workflows documented?
- Are setup/installation steps complete?
- Are all public APIs documented?
- Are common use cases covered?
- Are troubleshooting sections present for complex features?
- What critical information is missing?

**Scoring Scale:**
- **5/5:** All major features documented; setup complete; troubleshooting present; 0-1 missing sections.
- **4/5:** Most features documented; setup works; 2-3 missing sections (minor features).
- **3/5:** Core features documented; setup has gaps; 4-5 missing sections; no troubleshooting.
- **2/5:** Significant features undocumented; incomplete setup; >5 missing sections.
- **1/5:** Sparse documentation; users cannot complete basic tasks; critical info missing.

**Quantifiable Metrics (Critical Dimension):**
- Count of standard sections present vs expected (Quick Start, Installation, Usage, API, etc.)
- Can new user complete setup using only documentation? (Yes/No)
- Count of major features without documentation

#### 3. Clarity (Is it user-friendly and intuitive?) — Weight: 1×

- Can a new user follow the documentation without confusion?
- Are technical terms explained or linked?
- Are examples provided for complex concepts?
- Is the reading level appropriate for the target audience?
- Are visuals (diagrams, screenshots) used effectively?
- Is there a clear "getting started" path?

**Scoring Scale:**
- **5/5:** New user can follow without confusion; terms explained; examples present; clear getting started path.
- **4/5:** Minor confusion points; most terms explained; examples for complex concepts.
- **3/5:** Some sections confusing; several undefined terms; sparse examples; getting started unclear.
- **2/5:** Significant confusion; jargon-heavy; few examples; users frequently blocked.
- **1/5:** Incomprehensible to target audience; no examples; assumes unstated knowledge.

#### 4. Consistency (Does it follow project conventions?) — Weight: 1×

- Does formatting match project style (headers, code blocks, lists)?
- Are naming conventions consistent throughout?
- Does terminology match the codebase?
- Are similar sections structured the same way?
- **If project has rules/801-project-readme.md or rules/802-project-contributing.md,
  verify compliance with those standards**

**Scoring Scale:**
- **5/5:** Formatting consistent; terminology matches codebase; complies with project rules.
- **4/5:** Minor formatting inconsistencies; 1-2 terminology mismatches; mostly compliant.
- **3/5:** Several formatting issues; inconsistent terminology; partial rule compliance.
- **2/5:** Significant inconsistencies; terminology confusing; multiple rule violations.
- **1/5:** No consistent style; terminology contradicts codebase; ignores project standards.

#### 5. Staleness (Are tool versions and links current?) — Weight: 2×

- Are referenced tool versions current? (e.g., Python 3.11 vs 3.13)
- Are external links working and pointing to current content?
- Are deprecated features or patterns mentioned?
- Are dates and version numbers up to date?
- **Use the Link Validation Table** (mandatory) to systematically verify

**Scoring Scale:**
- **5/5:** All versions current; all internal links valid; no deprecated patterns; dates current.
- **4/5:** 1-2 minor version drifts; all links valid; no deprecated patterns.
- **3/5:** 3-5 outdated references; 1-2 broken internal links; minor deprecated patterns.
- **2/5:** >5 outdated references; 3-4 broken links; deprecated patterns that may confuse users.
- **1/5:** Systematically outdated; >4 broken links; users will follow wrong instructions.

**Quantifiable Metrics (Critical Dimension):**
- Count of broken internal links via Link Validation Table
- Count of outdated version references
- Count of deprecated patterns or features mentioned

#### 6. Structure (Is organization logical and navigable?) — Weight: 1×

- Is there a clear table of contents for long documents?
- Are sections ordered logically (overview → setup → usage → reference)?
- Can users find information quickly?
- Are related topics grouped together?
- Is navigation between documents clear?
- Are anchor links used effectively?

**Scoring Scale:**
- **5/5:** Logical flow; TOC present for long docs; anchor links work; easy to navigate.
- **4/5:** Good structure; minor ordering issues; TOC present but could be improved.
- **3/5:** Adequate structure; some sections misplaced; no TOC for long docs; navigation unclear.
- **2/5:** Poor organization; hard to find information; sections scattered; no cross-links.
- **1/5:** No logical structure; users cannot navigate; information buried or duplicated.

### Output Format

Provide your assessment in this structure:

~~~markdown
## Documentation Review: [doc-name.md]

### Scores (Weighted)
| Criterion | Weight | Raw | Weighted | Notes |
|-----------|--------|-----|----------|-------|
| Accuracy | 2× | X/5 | Y/10 | [brief justification] |
| Completeness | 2× | X/5 | Y/10 | [brief justification] |
| Staleness | 2× | X/5 | Y/10 | [brief justification] |
| Clarity | 1× | X/5 | Y/5 | [brief justification] |
| Consistency | 1× | X/5 | Y/5 | [brief justification] |
| Structure | 1× | X/5 | Y/5 | [brief justification] |

**Overall:** X/45 (weighted)

### Overall Score Interpretation

| Score Range | Assessment | Recommended Action |
|-------------|------------|-------------------|
| 41-45/45 (91-100%) | Excellent | Ready for use; minor polish only |
| 36-40/45 (80-90%) | Good | Usable with noted improvements |
| 27-35/45 (60-79%) | Needs Work | Requires fixes before reliable use |
| 18-26/45 (40-59%) | Poor | Major rework needed |
| <18/45 (<40%) | Inadequate | Rewrite from scratch |

**Critical dimension overrides:**
- If Accuracy ≤2/5 → Assessment = "Needs Work" minimum
- If Completeness ≤2/5 → Assessment = "Needs Work" minimum
- If Staleness ≤2/5 → Assessment = "Needs Work" minimum
- If 2+ critical dimensions ≤2/5 → Assessment = "Poor" minimum

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

**Minimum Evidence Requirement:** Check at least 5 reference types from the list above.
If <5 total references found, explicitly state "documentation has minimal code references."

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

**Minimum Evidence Requirement:** Check all internal links and anchor links. External
URLs flagged for manual verification but don't count against Staleness score.

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

### Documentation Perspective Checklist (REQUIRED)

Answer each question explicitly in your assessment:

- [ ] **New user test:** Can someone unfamiliar with the project get started using only
  this documentation? (Yes/No with explanation)
  - *Scoring impact:* No → Completeness ≤3/5, Clarity ≤3/5
- [ ] **Accuracy audit:** What percentage of code references were verified as accurate?
  (e.g., "15/18 references valid = 83%")
  - *Scoring impact:* <70% → Accuracy ≤2/5; 70-85% → Accuracy ≤3/5; 85-95% → Accuracy ≤4/5
- [ ] **Link health:** How many internal links are broken vs total?
  (e.g., "2 broken / 24 total")
  - *Scoring impact:* Per Staleness Scoring Impact Rules
- [ ] **Missing sections:** List any standard sections that are absent
  (e.g., "No troubleshooting section")
  - *Scoring impact:* >3 missing standard sections → Completeness ≤3/5
- [ ] **Staleness indicators:** List any outdated versions, deprecated patterns, or stale
  dates found
  - *Scoring impact:* >3 outdated references → Staleness ≤3/5

---

### Scoring Impact Rules (Algorithmic Overrides)

These rules override subjective assessment. Apply them mechanically based on counts:

#### Accuracy (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| <70% references valid | 2/5 |
| 70-84% references valid | 3/5 |
| 85-94% references valid | 4/5 |
| 95-99% references valid | 4/5 |
| 100% references valid | 5/5 |

#### Completeness (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| >5 missing standard sections | 2/5 |
| 4-5 missing sections | 3/5 |
| 2-3 missing sections | 4/5 |
| 0-1 missing sections | 5/5 |

#### Staleness (2× weight)
| Finding | Maximum Score |
|---------|---------------|
| >4 broken internal links OR >10 outdated references | 1/5 |
| 3-4 broken links OR 6-10 outdated references | 2/5 |
| 1-2 broken links OR 3-5 outdated references | 3/5 |
| 0 broken links, 1-2 minor version drifts | 4/5 |
| All current, all links valid | 5/5 |

#### Consistency (1× weight)
| Finding | Maximum Score |
|---------|---------------|
| Multiple rule violations (if project rules exist) | 2/5 |
| Significant formatting inconsistencies | 3/5 |
| Minor inconsistencies | 4/5 |

#### Clarity (1× weight)
| Finding | Maximum Score |
|---------|---------------|
| New user cannot complete setup | 3/5 |
| No examples for complex concepts | 3/5 |

---

### Scoring Decision Matrix

Use this table to resolve common edge cases:

| Scenario | Resolution | Rationale |
|----------|------------|-----------|
| Reference percentage between bands (e.g., exactly 85%) | Use higher score band | Documentation gets benefit of doubt |
| External link status unknown | Flag as ⚠️, don't count against score | Cannot verify without network access |
| Optional section missing | Don't count as missing | Only required sections affect score |
| Documentation references removed file | Count as broken reference | Indicates staleness |
| Terminology differs but meaning clear | Minor inconsistency | Users can understand intent |
| Project rules don't exist | Use general best practices | Note absence in review |

---

### Inter-Rater Reliability Guidelines

To ensure consistent scoring across models and runs:

1. **Apply Scoring Impact Rules first** — algorithmic overrides take precedence
2. **Use verification tables** — scores must be supported by table evidence
3. **Cite line numbers** — all findings must reference specific locations
4. **Document edge case decisions** — use Notes column to explain judgment calls
5. **When uncertain between scores** — default to higher score for documentation (users benefit)

**Calibration process:**
- Count findings mechanically (broken links, missing references, etc.)
- Apply Scoring Impact Rules table
- Adjust only if qualitative factors strongly justify (document reasoning)

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

