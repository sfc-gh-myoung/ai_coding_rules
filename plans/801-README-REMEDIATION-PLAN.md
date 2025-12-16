# Implementation Plan: rules/801-project-readme.md Remediation

**Created:** 2025-12-12  
**Based on Review:** reviews/801-project-readme-review-2025-12-12.md  
**Target Rule:** rules/801-project-readme.md  
**Overall Score:** 18/30 → Target: 25-27/30  
**Total Estimated Effort:** 8-10 hours

---

## Executive Summary

This plan addresses critical agent-autonomy issues in the README rule by quantifying subjective terms, fixing example violations, adding error handling, and improving token efficiency. Implementation follows a phased approach prioritizing critical fixes that enable agent autonomy.

**Key Metrics:**
- **Current Agent Autonomy:** 35% → **Target:** 85%
- **Undefined Thresholds:** 35+ → **Target:** 0
- **Example-Mandate Violations:** 4 → **Target:** 0
- **Token Budget Variance:** +15.6% → **Target:** ±5%

---

## Implementation Phases

### Phase 1: Critical Fixes (Priority 1) - Estimated: 6.75 hours
*Must complete before Phase 2. Blocks agent autonomy.*

### Phase 2: High-Priority Improvements (Priority 2) - Estimated: 3.25 hours
*Improves agent performance and token efficiency.*

### Phase 3: Minor Enhancements (Priority 3) - Estimated: 1.25 hours
*Quality-of-life improvements, optional but recommended.*

**Total:** 11.25 hours (rounded to 8-10 hours in review due to overlap opportunities)

---

## Phase 1: Critical Fixes (Est: 6.75 hours)

### Task 1.1: Quantify All Subjective Thresholds
**Priority:** CRITICAL  
**Effort:** 3 hours  
**Dependencies:** None  
**Reviewability:** High (can verify each threshold)

#### Objective
Replace 35+ undefined subjective terms with quantified, measurable criteria enabling autonomous agent decisions.

#### Approach
Process each of the 35 terms identified in Threshold Audit table (review lines 46-83).

#### Implementation Strategy

**1. Group by Semantic Category** (30 min)
```
Category 1: Size/Scale (8 terms)
- "significant", "large", "long", "simple", "complex", "deep", "global", "mature"

Category 2: Quality/Standard (7 terms)  
- "clear", "concise", "professional", "descriptive", "current", "correct", "effective"

Category 3: Selection/Priority (6 terms)
- "common", "key", "minimal", "immediate", "practical", "notable"

Category 4: Conditionals (14 terms)
- "complexity", "clean system", "appropriate", "inclusive", "accessible", 
  "working", "UI-heavy", "structured", "detailed", "separate", "comprehensive", 
  "consistent", "brief", "quarterly"
```

**2. Apply Quantification Pattern** (2 hours)
For each term, follow this template:

```markdown
# BEFORE:
- **Rule:** Test on clean system

# AFTER:
- **Rule:** Test on clean system (defined as ANY of):
  - Fresh OS install (no prior project dependencies)
  - Docker container FROM ubuntu:22.04 (or equivalent base image)
  - VM with ONLY listed prerequisites installed
  - CI/CD environment with fresh checkout
```

**3. Update Sections** (30 min)
Systematically update these sections with quantified terms:

| Section | Lines | Terms to Quantify | Est Time |
|---------|-------|-------------------|----------|
| Quick Start TL;DR | 20-60 | "simplest", "immediate", "minimal" | 10 min |
| Installation Section | 89-94 | "common", "clean" | 5 min |
| Usage Section | 126-129 | "practical", "common", "proper", "UI-heavy" | 10 min |
| Recommended Sections | 404-444 | "complexity", "detailed", "separate" | 15 min |
| Project Title/Description | 449-465 | "key metrics", "concise" | 10 min |
| Quick Overview Section | 467-500 | "brief", "simple" | 10 min |
| Quick Start Section | 502-507 | "immediate", "minimal", "clean" | 10 min |
| Readability Standards | 678-682 | "clear", "concise", "appropriate" | 10 min |
| Visual Organization | 684-688 | "effective", "long", "structured" | 10 min |
| Inclusive Language | 749-753 | "inclusive", "welcoming" | 10 min |
| Screen Reader | 755-759 | "descriptive", "accessible" | 10 min |
| International | 761-765 | "global" | 5 min |
| Maintenance | 776-788 | "significant", "current", "quarterly" | 15 min |
| Structure Problems | 814-818 | "simple projects", "consistent" | 10 min |
| Maintenance Problems | 820-824 | "current version", "working links" | 10 min |
| Evolution Patterns | 799-803 | "mature", "detailed", "comprehensive" | 10 min |

#### Acceptance Criteria
- [ ] All 35 terms from Threshold Audit have quantified definitions
- [ ] Each definition provides measurable criteria (numbers, conditions, or objective tests)
- [ ] No new subjective terms introduced
- [ ] Definitions enable agent to make autonomous decisions
- [ ] Updated terms maintain readability for human readers

#### Validation
Run agent simulation: "Given README with 600 lines, should I add TOC?"
- Agent should answer: "YES - exceeds 500 lines threshold"
- No human judgment required

---

### Task 1.2: Fix Example-Mandate Alignment Violations
**Priority:** CRITICAL  
**Effort:** 45 minutes  
**Dependencies:** None  
**Reviewability:** High (objective pass/fail)

#### Objective
Ensure all code examples comply with the rule's own mandates to serve as reliable agent patterns.

#### Violations to Fix

**Violation 1: Lines 38-49 - Missing "What just happened?"** (15 min)

```markdown
# CURRENT (lines 37-49):
**Example:**
```bash
# Clone the repository
git clone https://github.com/org/repo.git

cd repo

# Install
npm install

# Run
npm start
```

# REPLACE WITH (lines 37-65):
**Example:**
```bash
# Clone the repository
git clone https://github.com/org/repo.git
cd repo

# Install dependencies
npm install

# Start development server
npm start
```

**What just happened?**
- [PASS] Cloned repository to `./repo` directory
- [PASS] Installed 47 dependencies from package.json
- [PASS] Started development server at http://localhost:3000

**Success Indicator:**
✅ Browser opens automatically to http://localhost:3000  
✅ Console shows "Compiled successfully!"  
✅ Hot reload enabled for code changes

**Next Steps:**
- [PASS] Installation complete → [Configuration](#configuration)
- [?] Want to understand architecture → [Understanding](#understanding)
- [!] Installation failed → [Troubleshooting](#troubleshooting)
```

**Violation 2: Lines 76-87 - Placeholder code instead of concrete example** (15 min)

```markdown
# CURRENT (lines 75-87):
**Correct Pattern:**
```markdown
## Quick Start

**Get started in 2 commands:**

    # 1. Simple path
    # 2. Primary installation

**That's it!** Installation complete.

**Need different setup?** See [Deployment Options](#deployment-options)
```

# REPLACE WITH (lines 75-94):
**Correct Pattern:**
```markdown
## Quick Start

**Get started in 2 commands:**

```bash
git clone https://github.com/org/repo.git && cd repo
npm install && npm start
```

**What just happened?**
- [PASS] Cloned and installed project
- [PASS] Development server running at http://localhost:3000

**Success Indicator:**
✅ Browser opens to http://localhost:3000  
✅ See "Welcome to [Project]" page

**That's it!** Installation complete.

**Need different setup?** See [Deployment Options](#deployment-options)
```
```

**Violation 3: Lines 38-60 - Missing "Clear success indicator"** (5 min)
*Already addressed in Violation 1 fix*

**Violation 4: Line 692 - Clarify horizontal rule usage in examples** (10 min)

```markdown
# CURRENT (line 692):
**Avoid:** Horizontal rule markers (`---`) for content separation

# REPLACE WITH (lines 692-694):
**Avoid:** Horizontal rule markers (`---`) for content separation
**Exception:** Horizontal rules acceptable within code examples demonstrating anti-patterns
**Correct Pattern:** Use text-based boundary statements in section headers or TOC grouping
```

#### Acceptance Criteria
- [ ] All Quick Start examples include "What just happened?" section
- [ ] All Quick Start examples include "Success Indicator" section
- [ ] All examples use concrete, executable code (no placeholders)
- [ ] Horizontal rule usage clarified with exception note
- [ ] Examples can be copied and executed by agents without modification

#### Validation
Agent test: "Generate Quick Start section for Python project"
- Output should include all 4 mandatory elements (commands, explanation, success indicator, next steps)

---

### Task 1.3: Add Error Handling Section
**Priority:** CRITICAL  
**Effort:** 2 hours  
**Dependencies:** None  
**Reviewability:** Medium (subjective completeness)

#### Objective
Provide explicit failure paths and recovery guidance for common error scenarios.

#### Implementation

**1. Add New Section After Line 270** (1.5 hours)

Insert comprehensive Error Handling section:

```markdown
## Error Handling and Failure Recovery

### README Creation/Update Failures

#### Scenario 1: Cannot Identify Tech Stack
**Problem:** No package.json, pyproject.toml, go.mod, or other dependency files found  
**Detection:** Agent cannot determine project language/framework  
**Agent Response:**
1. Search for source files by extension (.py, .js, .go, .rs, .java)
2. If multiple languages: List all found, ask user for primary
3. If no source files: Create generic README with placeholder sections
4. Add comment: `<!-- TODO: Specify tech stack and update installation steps -->`

**Exit Code:** 0 (warning, not failure)  
**User Notification:** "Generic README created - please specify tech stack for installation instructions"

#### Scenario 2: Installation Commands Fail in Testing
**Problem:** Quick Start commands return non-zero exit code in clean environment  
**Detection:** Test execution returns exit code ≠ 0  
**Agent Response:**
1. Capture stderr output
2. Identify missing prerequisites:
   - "node: command not found" → Add Node.js prerequisite
   - "python: No module named 'pip'" → Add pip prerequisite
   - "permission denied" → Add sudo or permission setup
3. Add Prerequisites section BEFORE Quick Start:
   ```markdown
   ## Prerequisites
   
   Before installation, ensure you have:
   - Node.js >= 18.0.0 (`node --version`)
   - npm >= 9.0.0 (`npm --version`)
   ```
4. Add prerequisite check to Quick Start:
   ```bash
   # Verify prerequisites
   node --version  # Should output v18.0.0 or higher
   npm --version   # Should output 9.0.0 or higher
   ```
5. Retest installation

**Exit Code:** 1 if retesting fails after adding prerequisites  
**User Notification:** "Installation test failed: [error message]. Prerequisites added - please verify."

#### Scenario 3: Link Validation Failures
**Problem:** Links return 404, timeout, or redirect errors  
**Detection:** HTTP status codes: 404, 408, 500-599  
**Agent Response:**
1. For each broken link:
   - **404 Not Found:**
     - If internal (#anchor): Check case sensitivity, verify section exists
     - If external: Search for moved URL (301/308), check archive.org
     - If permanently gone: Remove or replace with alternative
   - **408 Timeout (>5s):**
     - Note in PR: "Link slow to respond, may be temporary"
     - Keep link but add warning comment
   - **301/302 Redirect:**
     - Update to final destination URL
     - Note: "Updated redirected link"
2. Document in commit message: "Fixed N broken links, updated M redirects"

**Exit Code:** 0 (warning) if <50% links broken, 1 if ≥50% broken  
**User Notification:** "Link validation: N passed, M failed, P updated"

#### Scenario 4: README Exceeds Size Limits
**Problem:** README.md >150 KB or >1000 lines  
**Detection:** File size check or line count  
**Agent Response:**
1. Identify sections >200 lines:
   - API Documentation → Extract to `docs/API.md`
   - Architecture explanations → Extract to `ARCHITECTURE.md`
   - Detailed examples → Extract to `docs/examples/`
   - Tutorial content → Extract to `docs/TUTORIAL.md`
2. Replace extracted content with summary + link:
   ```markdown
   ## API Documentation
   
   [Brief 1-2 paragraph overview]
   
   **For complete API reference, see [API.md](docs/API.md)**
   ```
3. Update Table of Contents to link extracted files

**Exit Code:** 0 (automatic fix applied)  
**User Notification:** "README exceeded 150 KB - extracted N sections to separate files"

#### Scenario 5: Markdown Linting Failures
**Problem:** `uvx pymarkdownlnt scan README.md` exits non-zero  
**Detection:** Linter exit code ≠ 0  
**Agent Response:**
1. Parse linter output for error codes
2. Fix automatically if possible:
   - MD001 (heading levels): Adjust hierarchy
   - MD003 (heading style): Standardize to ATX (#)
   - MD004 (list marker): Standardize to dash (-)
   - MD009 (trailing spaces): Remove
   - MD010 (hard tabs): Convert to spaces
   - MD012 (multiple blanks): Reduce to max 2
3. If >10 errors: Run `uvx pymarkdownlnt fix README.md`
4. Re-scan to verify fixes
5. If unfixable errors remain: List in PR with manual fix instructions

**Exit Code:** 0 if all fixed, 1 if manual fixes needed  
**User Notification:** "Fixed N markdown issues, M require manual attention"

### User Environment Issues

#### Missing Prerequisites
**Problem:** User environment lacks required tools  
**Agent Response:**
1. Add Prerequisites section with installation links:
   ```markdown
   ## Prerequisites
   
   - [Node.js](https://nodejs.org/) >= 18.0.0
   - [npm](https://www.npmjs.com/) >= 9.0.0
   - [Git](https://git-scm.com/) (any recent version)
   ```
2. Provide fallback options:
   - Docker alternative: `docker run -p 3000:3000 org/repo:latest`
   - Package manager install: `brew install node` / `apt install nodejs`
3. Link to detailed setup guide if complex

#### Platform Compatibility Issues
**Problem:** Installation differs significantly between platforms  
**Agent Response:**
1. Create platform-specific sections using `<details>`:
   ```markdown
   <details>
   <summary>macOS / Linux</summary>
   
   ```bash
   curl -sSL https://install.example.com | bash
   ```
   </details>
   
   <details>
   <summary>Windows</summary>
   
   ```powershell
   irm https://install.example.com | iex
   ```
   </details>
   ```
2. Add platform detection note:
   ```markdown
   **Note:** Installation auto-detects your platform. For manual install, see platform-specific instructions above.
   ```

### Validation Failures

#### Required Sections Missing
**Problem:** README lacks mandatory sections (Title, Description, Quick Start, Usage, Contributing, License)  
**Detection:** Section header scan finds missing H2  
**Agent Response:**
1. Exit with error (do not create incomplete README)
2. List missing sections
3. Prompt user: "Cannot create README - missing required sections: [list]. Should I create placeholders?"
4. If user confirms: Create sections with `<!-- TODO: Complete this section -->` comments

**Exit Code:** 1  
**User Notification:** "README incomplete - missing required sections: [list]"

#### Token Budget Exceeded
**Problem:** README would exceed project token budget  
**Detection:** Word count × 1.3 > project limit  
**Agent Response:**
1. Calculate overage: (actual - limit) / limit × 100%
2. If <10% over: Accept with warning
3. If >10% over: Apply compression:
   - Remove verbose explanations (keep technical details)
   - Consolidate repeated patterns
   - Move advanced topics to linked files
4. Recheck budget after compression
5. If still over: Prompt user to increase budget or split file

**Exit Code:** 0 (warning) if <10%, 1 if >10%  
**User Notification:** "README token budget: N tokens (M% over limit)"

### Recovery Strategies

#### Automatic Retry Logic
For transient failures (network timeouts, rate limits):
```python
def validate_links_with_retry(urls, max_retries=3, backoff=2):
    for url in urls:
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    break
            except requests.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(backoff ** attempt)
                else:
                    log_warning(f"Link timeout after {max_retries} attempts: {url}")
```

#### Graceful Degradation
If critical validation unavailable:
1. Link checker offline → Skip external links, validate internal only
2. Docker unavailable → Warn: "Installation not tested in clean environment"
3. Linter unavailable → Apply basic formatting rules, warn about missing validation

#### Rollback on Failure
If README update fails mid-operation:
1. Preserve original README as `README.md.backup`
2. On failure: Restore from backup
3. Log all changes attempted
4. Present partial diff to user: "Completed sections: [list], Failed sections: [list]"
```

**2. Update Validation Section** (30 min)

Add error handling references to existing validation checklist (lines 217-251):

```markdown
### Pre-Publication Review
- [ ] **CRITICAL:** README update triggers checked (see 000-global-core.md section 6)
- [ ] **CRITICAL:** If triggers apply, README.md updated before task completion
- [ ] **Required sections present:** ALL mandatory sections exist (exit code 1 if missing)
- [ ] **Installation tested:** Commands return exit code 0 (see Error Handling → Scenario 2)
- [ ] **Code examples validated:** All blocks parse without syntax errors
- [ ] **Links checked:** HTTP 200-399 or handled per Error Handling → Scenario 3
- [ ] **Badges current:** Verified against latest release/build status
- [ ] **Markdown lint passes:** Exit 0 or auto-fixed per Error Handling → Scenario 5
- [ ] **File size check:** <150 KB (auto-extract if larger per Scenario 4)
- [ ] **Token budget:** Within ±10% of limit (see Error Handling → Token Budget Exceeded)
```

#### Acceptance Criteria
- [ ] Error Handling section covers all common failure scenarios (6+ scenarios)
- [ ] Each scenario includes: Problem, Detection, Agent Response, Exit Code, User Notification
- [ ] Recovery strategies documented for transient failures
- [ ] Validation section cross-references error handling procedures
- [ ] Graceful degradation patterns provided when tools unavailable

#### Validation
Agent simulation: "Installation test failed with 'node: command not found'"
- Agent should add Prerequisites section
- Agent should add prerequisite check to Quick Start
- Agent should retry installation
- No human intervention required

---

### Task 1.4: Populate Contract Section
**Priority:** CRITICAL  
**Effort:** 1 hour  
**Dependencies:** None  
**Reviewability:** High (structured format)

#### Objective
Replace template Contract (lines 143-170) with complete, executable contract for README creation.

#### Implementation

Replace lines 142-170 with populated contract from review (lines 427-500):

```markdown
## Contract

<contract>
<inputs_prereqs>
- Existing project codebase with identifiable tech stack
- Access to repository metadata (GitHub/GitLab URL, license file, README.md if updating)
- Package manager files (package.json, pyproject.toml, go.mod, Cargo.toml, pom.xml, etc.)
- Project root directory with source files
- Optional: Existing CONTRIBUTING.md, CHANGELOG.md, LICENSE files
</inputs_prereqs>

<mandatory>
- Read existing README.md BEFORE modifications (if file exists)
- Verify tech stack from dependency files (DO NOT assume from folder name)
- Test installation commands in clean environment (see Error Handling → clean system definition)
- Validate all links return HTTP 200 or handle failures per Error Handling section
- Run markdownlint (`uvx pymarkdownlnt scan README.md`) before completion
- Include all required sections: Title, Description, Quick Start, Usage, Contributing, License
- Add "What just happened?" after EVERY command block in Quick Start
- Add success indicator showing expected output
- Add "Next Steps" links after Quick Start
</mandatory>

<forbidden>
- Modifying README without reading current state first
- Adding badges without verifying they reflect actual project status
- Including installation commands without testing in clean environment
- Duplicating content from CONTRIBUTING.md in README (link instead)
- Using horizontal rules (---) for section separation (use TOC grouping or boundary statements)
- Assuming tech stack from directory name or repo name
- Creating Quick Start with >4 commands
- Adding multiple installation options in Quick Start (move to separate section)
- Including undefined subjective terms without quantified thresholds
</forbidden>

<steps>
1. **Analyze Project Context** (5 min)
   - Read existing README.md (if exists) to understand current structure
   - Read dependency files to identify tech stack:
     - package.json → Node.js/npm
     - pyproject.toml → Python/uv
     - go.mod → Go
     - Cargo.toml → Rust
     - pom.xml → Java/Maven
   - Identify project type: library, application, CLI tool, framework
   - Check for existing CONTRIBUTING.md, LICENSE, CHANGELOG.md

2. **Identify Missing/Outdated Sections** (5 min)
   - Compare current README to Required Sections (lines 385-402)
   - List sections needing creation or update
   - Verify all 6 mandatory sections present

3. **Create/Update Quick Start** (15 min)
   - Identify simplest installation path (fewest dependencies, <5 commands)
   - Write 2-4 commands: clone → install → run
   - Test commands in clean Docker container:
     - Python: `docker run -it python:3.11-slim`
     - Node.js: `docker run -it node:18-alpine`
     - Go: `docker run -it golang:1.21-alpine`
   - If test fails: Apply Error Handling → Scenario 2 (add prerequisites, retest)
   - Add "What just happened?" (2-4 bullet points)
   - Add "Success Indicator" (✅ expected output)
   - Add "Next Steps" (3 links: success path, understanding, troubleshooting)

4. **Generate Badges** (5 min)
   - Build status: Link to actual CI/CD (GitHub Actions, CircleCI, etc.)
   - Version: Match latest release tag from repository
   - License: Match LICENSE file contents
   - Optional: Coverage (if >80%), downloads (if >1K/month)
   - Use shields.io format: `[![Label](https://img.shields.io/badge/...)](link)`

5. **Create Other Required Sections** (15 min)
   - **Description:** 1-2 sentences, <160 chars
   - **Usage:** 2-3 common examples with expected output
   - **Contributing:** Boundary statement + link to CONTRIBUTING.md (if exists) or inline minimal guide
   - **License:** Link to LICENSE file + key points (if common license)

6. **Add Recommended Sections** (10 min, if applicable)
   - **Table of Contents:** If README >500 lines OR >50 KB OR >8 H2 sections
   - **Prerequisites:** If installation requires specific tools/versions
   - **Troubleshooting:** If common issues identified during testing
   - **Understanding:** If complex architecture or concepts need explanation

7. **Validate Links** (5 min)
   - Extract all URLs (markdown links and bare URLs)
   - Check HTTP status for each (timeout: 5s)
   - Apply Error Handling → Scenario 3 for failures
   - Document: "Links validated: N passed, M fixed, P removed"

8. **Run Markdown Linting** (3 min)
   - Execute: `uvx pymarkdownlnt scan README.md`
   - If exit ≠ 0: Apply Error Handling → Scenario 5 (auto-fix)
   - Verify exit code 0 after fixes

9. **Check File Size and Token Budget** (2 min)
   - File size: <150 KB (if larger: apply Scenario 4)
   - Token estimate: word count × 1.3
   - If >10% over budget: Apply compression or extract sections

10. **Present Changes** (5 min)
    - Show structured diff:
      ```
      **File Modified:** README.md
      **Sections Updated:** Quick Start, Usage, Contributing (3 sections)
      **Validation:**
      - [x] Markdown lint passes (0 errors)
      - [x] Links validated (47 checked, 47 passed)
      - [x] Installation tested (exit code 0 in node:18-alpine)
      - [x] All required sections present (6/6)
      
      **Changes Made:**
      1. Quick Start: Added 3-command installation with success indicator
      2. Usage: Added 2 common examples with output
      3. Contributing: Added boundary statement and CONTRIBUTING.md link
      ```
    - Include preview of updated Quick Start section
</steps>

<output_format>
**File Modified:** README.md  
**Sections Updated:** [comma-separated list]  
**Validation:**
- [x] Markdown lint passes (N errors fixed)
- [x] Links validated (N checked, M passed, P fixed)
- [x] Installation tested (exit code 0 in [environment])
- [x] All required sections present (6/6)
- [x] Token budget: N tokens (M% of limit)
- [x] File size: N KB (<150 KB ✓)

**Changes Made:**
1. **[Section Name]**
   - Added: [specific addition]
   - Updated: [specific change]
   - Rationale: [why this change]

2. **[Another Section]**
   - [changes]

**Preview:**
```markdown
[Show Quick Start section or other significant addition]
```

**Next Steps:**
- Review changes in diff
- Verify installation commands work in your environment
- Commit with message: "docs: update README - [brief summary]"
</output_format>

<validation>
1. ✅ All Required Sections present: Title (H1), Description, Quick Start, Usage, Contributing, License
2. ✅ Quick Start has 2-4 commands (no more, no less)
3. ✅ Quick Start includes "What just happened?" explanation
4. ✅ Quick Start includes "Success Indicator" with ✅ expected output
5. ✅ Quick Start includes "Next Steps" with 3 links
6. ✅ All code blocks have language identifiers (```bash, ```python, etc.)
7. ✅ Installation commands tested in clean environment (exit code 0)
8. ✅ All links return HTTP 200 or handled per Error Handling
9. ✅ Markdownlint exits 0 (zero errors)
10. ✅ File size <150 KB (if larger, sections extracted)
11. ✅ Token budget within ±10% of limit
12. ✅ No horizontal rules (---) used for section separation
13. ✅ Contributing section includes boundary statement OR TOC grouping
14. ✅ All subjective terms have quantified definitions
15. ✅ No undefined thresholds remain
</validation>
</contract>
```

**Additional Note:** Remove lines 173-200 (the empty Anti-Patterns template placeholders) as they duplicate existing Anti-Patterns section at lines 806-825.

#### Acceptance Criteria
- [ ] Contract fully populated with project-specific guidance
- [ ] All 5 contract sections complete (inputs, mandatory, forbidden, steps, output_format, validation)
- [ ] Steps are sequential, time-estimated, and actionable
- [ ] Validation includes 15+ specific checkpoints
- [ ] Contract aligns with Error Handling section
- [ ] Empty template placeholders removed (lines 173-200)

#### Validation
Agent test: "Create README for Python project with pyproject.toml"
- Agent should follow all 10 steps in sequence
- Agent should validate against all 15 checkpoints
- Output should match specified format

---

## Phase 2: High-Priority Improvements (Est: 3.25 hours)

### Task 2.1: Reduce Token Count to Match Budget
**Priority:** HIGH  
**Effort:** 1.5 hours  
**Dependencies:** Task 1.1, 1.2, 1.3, 1.4 (may add tokens)  
**Reviewability:** High (measurable)

#### Objective
Reduce actual token count from ~5,200 to ~4,400 (2% under declared ~4,500 budget).

#### Target Savings: 800 tokens (~15% reduction)

#### Consolidation Strategy

**1. Merge Installation Guidance** (Save ~200 tokens, 20 min)

Current state: Installation guidance appears in:
- Lines 89-94 (Installation Section)
- Lines 395 (Required Sections reference)
- Lines 503-507 (Quick Start Section)

Consolidation:
```markdown
# CREATE single reference at lines 89-95:
### Installation Guidance

See **Quick Start Section** (line 502) for installation patterns.
See **Contract Section → Steps 3** (line 454) for installation testing requirements.

**Key Requirements:**
- 2-4 commands maximum
- Test in clean environment (Docker/VM/CI)
- Include "What just happened?" explanation
- Add success indicator
```

Remove or significantly reduce redundant text at lines 503-507.

**2. Consolidate "Investigation Required" Blocks** (Save ~200 tokens, 15 min)

Current state: Nearly identical blocks at:
- Lines 222-237
- Lines 253-268

Consolidation:
```markdown
# Keep only lines 222-244 (more detailed version)
# DELETE lines 253-268 entirely
# Add cross-reference at line 246:

### Ongoing Maintenance
- [ ] README updated with significant feature changes (>3 files OR breaking change OR new API)
- [ ] Version compatibility information current (<6 months old)
...

> **Investigation Required:** See Pre-Publication Review section above (line 222) for complete investigation checklist.
```

**3. Consolidate Overlapping Checklist Items** (Save ~150 tokens, 20 min)

Current state: Overlapping items in:
- Pre-Execution Checklist (30-35): 5 items
- Post-Execution Checklist (204-211): 7 items  
- Pre-Publication Review (217-244): 15+ items

Consolidation approach:
- Keep Pre-Publication Review as comprehensive checklist (most detailed)
- Reduce Pre-Execution to 3 items (planning only):
  ```markdown
  - [ ] Read existing README.md (if exists)
  - [ ] Identified tech stack from dependency files
  - [ ] Planned required sections (minimum 6)
  ```
- Reduce Post-Execution to single reference:
  ```markdown
  ## Post-Execution Checklist
  
  After README creation/update, complete **Pre-Publication Review** checklist (line 217).
  ```

**4. Trim Quick Overview Section Prose** (Save ~100 tokens, 15 min)

Lines 467-500 contain verbose explanations. Trim to essentials:

```markdown
# BEFORE (lines 496-500):
**Why This Works:**
- Users can self-assess readiness before diving in
- Reduces support questions about prerequisites
- Provides clear navigation to relevant sections
- Sets expectations for installation complexity

# AFTER:
**Benefits:** Self-assessment reduces support burden; clear navigation; sets expectations.
```

**5. Consolidate Badge Examples** (Save ~50 tokens, 10 min)

Lines 456-465 show 4 badge examples. Reduce to 2 + reference:

```markdown
# Keep build and license badges (most common)
# Replace version and GitHub badges with:
# Additional badges: version, coverage, downloads - see shields.io
```

**6. Trim Redundant Examples** (Save ~100 tokens, 10 min)

Lines 38-87 show multiple Quick Start examples:
- Lines 38-60: Full example with explanation
- Lines 69-73: Anti-pattern
- Lines 76-87: "Correct Pattern" (after fixing in Task 1.2)

After Task 1.2, lines 38-65 will be complete example. Reduce lines 76-94:

```markdown
# BEFORE (lines 76-94): Full pattern repetition

# AFTER (lines 76-80):
**Correct Pattern:** See example at line 37 for complete Quick Start with all mandatory elements.

**Key Elements:**
- 2-4 commands (not "choose from 4 options")
- ONE primary path (alternatives in separate section)
```

#### Measurement

After all reductions:
```bash
# Count words in edited file:
wc -w rules/801-project-readme.md

# Calculate tokens (word count × 1.3):
# python -c "print(int(WORD_COUNT * 1.3))"

# Verify <4,550 tokens (2% under budget)
```

#### Acceptance Criteria
- [ ] Actual token count ≤4,550 (within declared ~4,500 budget)
- [ ] No loss of critical information (all thresholds, examples, error handling retained)
- [ ] Consolidations improve readability (no fragmented guidance)
- [ ] Cross-references maintain navigation between sections
- [ ] All 6 consolidation targets completed

#### Validation
Calculate token budget variance:
- Before: ~5,200 tokens (+15.6%)
- After: ~4,400 tokens (-2.2%)
- Improvement: 18% reduction, now within ±15% tolerance

---

### Task 2.2: Add Failure Scenarios and Recovery Paths
**Priority:** HIGH  
**Effort:** 1 hour  
**Dependencies:** Task 1.3 (Error Handling section exists)  
**Reviewability:** Medium (qualitative coverage)

#### Objective
Increase failure coverage from 7% to 30%+ by adding explicit failure examples throughout rule.

#### Implementation

**1. Add "Common Failure Scenarios" Section** (30 min)

Insert after Error Handling section (after Task 1.3 completion):

```markdown
## Common Failure Scenarios (Quick Reference)

This section provides quick agent responses for frequent failure patterns. See **Error Handling** section above for complete procedures.

### Agent Workflow Failures

#### "I can't determine the primary language"
**Symptom:** Multiple dependency files found (package.json + pyproject.toml + go.mod)  
**Quick Response:**
1. Count source files by extension: `find . -name "*.py" | wc -l` (repeat for .js, .go, etc.)
2. Primary language = highest count
3. If within 20%: Ask user: "Project contains Python (45%) and JavaScript (40%). Which is primary?"
4. Document decision in README: "**Primary:** Python | **Also includes:** JavaScript for frontend"

#### "Installation test keeps failing"
**Symptom:** Exit code ≠ 0 after adding prerequisites  
**Quick Response:**
1. Try alternative installation methods:
   - npm → yarn → pnpm
   - pip → pip3 → python -m pip
   - go install → go get
2. Add ALL attempts to Troubleshooting section
3. If 3+ methods fail: Create Issues template, document in README:
   ```markdown
   ## Known Issues
   
   Installation may fail on [platform/config]. We're tracking this in [issue #N].
   
   **Workaround:** [describe manual setup]
   ```

#### "Badges show incorrect status"
**Symptom:** Build badge says "passing" but latest commit failed  
**Quick Response:**
1. Do NOT add badge if unable to verify
2. Add placeholder comment: `<!-- TODO: Add build badge after verifying CI/CD setup -->`
3. Document in PR: "Skipped build badge - unable to verify current status"
4. Badge criteria:
   - Build: Must reflect latest commit on default branch
   - Coverage: Must match actual coverage report (<7 days old)
   - Version: Must match latest release tag exactly

#### "Link to CONTRIBUTING.md but file doesn't exist"
**Symptom:** Project has no CONTRIBUTING.md  
**Quick Response:**
1. Create minimal CONTRIBUTING.md:
   ```markdown
   # Contributing
   
   We welcome contributions! Please:
   
   1. Fork the repository
   2. Create feature branch: `git checkout -b feature/amazing-feature`
   3. Commit changes: `git commit -m 'Add amazing feature'`
   4. Push to branch: `git push origin feature/amazing-feature`
   5. Open Pull Request
   
   ## Development Setup
   
   [Installation commands from Quick Start]
   
   ## Running Tests
   
   [Test commands if tests exist, else "Tests coming soon"]
   ```
2. Link from README
3. Document in PR: "Created minimal CONTRIBUTING.md"

### User-Reported Failures

#### "Quick Start doesn't work on Windows"
**Symptom:** Bash commands fail in PowerShell  
**Quick Response:**
1. Add platform-specific sections using `<details>`:
   ```markdown
   <details>
   <summary>macOS / Linux</summary>
   [bash commands]
   </details>
   
   <details>
   <summary>Windows (PowerShell)</summary>
   [PowerShell equivalents]
   </details>
   ```
2. Test PowerShell equivalents:
   - `curl -sSL | bash` → `irm [url] | iex`
   - `cd repo` → `Set-Location repo` (or `cd` works)
   - `export VAR=value` → `$env:VAR="value"`

#### "Installation takes >5 minutes, violates 'immediate value'"
**Symptom:** Large dependencies (PyTorch, TensorFlow) take >60 seconds  
**Quick Response:**
1. Set realistic expectation in Quick Start:
   ```markdown
   **Note:** First installation downloads 2 GB of dependencies (5-10 min on typical connection).
   Subsequent installs use cache and complete in <60 seconds.
   ```
2. Add progress indicator if possible:
   ```bash
   pip install --progress-bar on torch torchvision
   ```
3. Offer Docker alternative with pre-built image:
   ```bash
   docker pull org/repo:latest  # Pre-installed dependencies
   docker run -p 8000:8000 org/repo:latest
   ```

#### "README has 'TODO' placeholders"
**Symptom:** Agent couldn't complete section, left placeholder  
**Quick Response:**
1. Acceptable TODOs (with user notification):
   - `<!-- TODO: Add deployment instructions after cloud provider selection -->`
   - `<!-- TODO: Add performance benchmarks after baseline established -->`
2. Unacceptable TODOs (must complete or remove section):
   - `<!-- TODO: Write description -->` (Description is mandatory)
   - `<!-- TODO: Add installation steps -->` (Quick Start is mandatory)
3. If mandatory section has TODO: Exit code 1, prompt user to provide information

### Validation Failures

#### "Markdown linter has 50+ errors"
**Symptom:** Auto-fix insufficient  
**Quick Response:**
1. If errors are style violations (MD003, MD004): Apply stricter auto-fix
   ```bash
   uvx pymarkdownlnt fix --strict README.md
   ```
2. If errors are structural (missing headers, broken links): List specific issues, exit code 1
   ```
   Cannot auto-fix structural issues:
   - Line 45: MD001 - Heading level skip (H1 -> H3)
   - Line 102: MD042 - Empty link (fix: add URL or remove link)
   
   Please fix manually or provide guidance.
   ```

#### "50% of links are broken"
**Symptom:** Mass link failures (repository moved, documentation reorganized)  
**Quick Response:**
1. Check if pattern exists:
   - All internal links broken: Likely section rename → scan headings, update links
   - All external links to same domain broken: Domain moved → search for new domain
2. If >50% broken: Exit code 1, request user guidance:
   ```
   ERROR: 23 of 45 links broken (51%).
   
   Pattern detected: All links to 'olddocs.example.com' failing.
   
   Possible actions:
   1. Remove all broken links (data loss)
   2. Replace 'olddocs.example.com' with new domain
   3. Replace with archive.org links (may be stale)
   
   Please advise on approach.
   ```
```

**2. Add Failure Examples to Existing Sections** (30 min)

Enhance these sections with failure examples:

**A. Quick Start Section (add after line 507):**
```markdown
**Failure Example:**
```bash
$ npm start
npm ERR! Missing script: "start"
```

**Recovery:**
1. Check package.json scripts section
2. If no start script exists, identify actual start command:
   - React: `npm run dev` or `npm run serve`
   - Node.js: `node index.js` or `node src/server.js`
3. Update Quick Start with correct command
4. Add Troubleshooting note: "If `npm start` fails, see package.json scripts for available commands"
```

**B. Link Validation (add after line 658):**
```markdown
**Failure Example:**
```
Validating links...
✓ https://docs.example.com/api (200 OK)
✗ https://example.com/old-guide (404 Not Found)
⚠ https://slow-site.com/info (408 Timeout after 5s)
```

**Recovery:** See Error Handling → Scenario 3 for link validation failures
```

**C. Badge Section (add after line 465):**
```markdown
**Failure Example:**
```markdown
[![Build Status](https://ci.example.com/badge/org/repo)](wrong-url)
```
Badge shows "passing" but actual build is failing.

**Prevention:**
1. Visit badge URL directly: https://ci.example.com/badge/org/repo.svg
2. Verify image updates after new commit
3. Check link target points to actual CI/CD dashboard
4. If unavailable or stale: Omit badge with TODO comment
```

#### Acceptance Criteria
- [ ] Common Failure Scenarios section added with 10+ scenarios
- [ ] Each scenario includes: Symptom, Quick Response, Example (if applicable)
- [ ] Failure examples added to 3+ existing sections
- [ ] Failure coverage increased to ≥30% (4 failure examples : 10 success examples)
- [ ] All scenarios cross-reference Error Handling section
- [ ] Agent can handle failures without human intervention (for covered scenarios)

#### Validation
Agent simulation: "Build badge verification failed"  
- Agent should check badge URL directly
- Agent should omit badge if unverifiable
- Agent should add TODO comment
- Agent should document in PR
- No human intervention required

---

### Task 2.3: Strengthen Validation Checklist
**Priority:** MEDIUM  
**Effort:** 45 minutes  
**Dependencies:** Task 1.1 (quantified thresholds), Task 1.3 (Error Handling)  
**Reviewability:** High (objective criteria)

#### Objective
Make all validation items measurable with specific pass/fail criteria enabling objective agent verification.

#### Implementation

Replace validation checklist (lines 217-251) with enhanced version from review (lines 579-593):

```markdown
### Pre-Publication Review

**CRITICAL Checks:**
- [ ] **README update triggers checked:** Verified against 000-global-core.md section 6 (required before ANY README modification)
- [ ] **Triggers applied:** If ANY trigger condition met, README.md updated before task marked complete

**Required Sections (Mandatory - exit code 1 if missing):**
- [ ] **Title:** Single H1 (`#`) at line 1
- [ ] **Description:** 1-2 sentences, <160 chars, immediately after badges
- [ ] **Quick Start:** Section exists with 2-4 commands, "What just happened?", success indicator, next steps
- [ ] **Usage:** 2+ examples with expected output
- [ ] **Contributing:** Link to CONTRIBUTING.md OR inline minimal guide (50+ words)
- [ ] **License:** Link to LICENSE file + license name

**Installation Testing (Mandatory):**
- [ ] **Clean environment:** Tested in Docker container FROM [base-image]:
  - Python projects: `python:3.11-slim`
  - Node.js projects: `node:18-alpine`
  - Go projects: `golang:1.21-alpine`
  - Rust projects: `rust:1.75-slim`
- [ ] **Exit code verification:** All Quick Start commands return exit code 0
- [ ] **Timing check:** Installation completes in <5 minutes (excluding large ML dependencies; note if >5 min)
- [ ] **Success indicator matches:** Actual output matches documented success indicator

**Code Examples (Mandatory):**
- [ ] **Syntax validation:** All code blocks parse without syntax errors
  - Python: `python -m py_compile example.py`
  - JavaScript: `node --check example.js`
  - Go: `go build example.go`
  - Bash: `bash -n example.sh`
- [ ] **Language identifiers:** Every fenced block has language (```python, ```bash, no plain ```)
- [ ] **Copy-pasteable:** No placeholders (no [TOKEN], no <URL>, use real or example.com values)

**Link Validation (Mandatory):**
- [ ] **HTTP status check:** All HTTP/HTTPS links return 200-399 (timeout: 5s, max redirects: 2)
- [ ] **Internal links:** All #anchor links point to existing H2/H3 sections (case-sensitive)
- [ ] **Reference-style links:** All [label]: URL definitions used (no orphaned definitions)
- [ ] **Relative paths:** All relative paths (./file.md) exist in repository
- [ ] **Failure handling:** Broken links handled per Error Handling → Scenario 3

**Badge Verification (If badges present):**
- [ ] **Build status:** Badge URL responds 200, image updates after latest commit (<24 hours old)
- [ ] **Version badge:** Matches latest release tag exactly (e.g., badge "v1.2.3" == git tag "v1.2.3")
- [ ] **License badge:** Matches LICENSE file contents (e.g., badge "MIT" == LICENSE contains MIT license text)
- [ ] **Coverage badge:** Matches actual coverage report (<7 days old, if badge shows 85%, report shows 84-86%)
- [ ] **Link targets:** All badge links point to relevant dashboard/page (not placeholder URLs)

**Markdown Linting (Mandatory):**
- [ ] **Linter execution:** `uvx pymarkdownlnt scan README.md` exits 0
- [ ] **Auto-fixes applied:** If initial scan fails, auto-fix attempted per Error Handling → Scenario 5
- [ ] **Verification:** Post-fix scan exits 0 (zero errors remaining)
- [ ] **Config alignment:** Linter uses project .markdownlint.json (if exists) or pymarkdownlnt defaults

**Readability Standards:**
- [ ] **Reading level:** Flesch-Kincaid Grade Level ≤12 (high school level, check with readability tool)
- [ ] **Sentence length:** Average <25 words/sentence (exclude code blocks from count)
- [ ] **Technical terms:** All domain-specific terms defined on first use OR linked to glossary
- [ ] **Inclusive language:** No gendered pronouns (use they/them), no cultural assumptions, no ableist language

**Formatting Standards:**
- [ ] **Heading hierarchy:** No skipped levels (H1→H2→H3, never H1→H3)
- [ ] **List markers:** Consistent throughout (prefer `-` for unordered, `1.` for ordered)
- [ ] **Code fence style:** Consistent (fenced ```, never indented code blocks)
- [ ] **Whitespace:** 1 blank between paragraphs, 2 before H2, max 2 consecutive blanks, no trailing spaces

**File Size and Token Budget:**
- [ ] **File size:** <150 KB (if ≥150 KB: extract sections per Error Handling → Scenario 4)
- [ ] **Token budget:** Word count × 1.3 ≤ project limit (if >10% over: compress or extract)
- [ ] **Line count:** If >1000 lines: Extract detailed sections to separate files (API.md, ARCHITECTURE.md, TUTORIAL.md)

**Table of Contents (Conditional):**
- [ ] **TOC required:** If README meets ANY:
  - >500 lines (excluding code blocks)
  - >50 KB file size
  - >8 H2 sections
  - User must scroll >3 screens (1 screen ≈ 50 lines)
- [ ] **TOC format:** Links to all H2 sections, organized by user type (Users vs Contributors)
- [ ] **TOC placement:** After description and badges, before first H2

**Content Quality:**
- [ ] **No placeholders:** No TODO comments in mandatory sections (optional sections may have TODOs with user notification)
- [ ] **No assumptions:** Tech stack verified from actual files, not inferred from folder names
- [ ] **No duplicates:** CONTRIBUTING.md content not duplicated in README (link with 1-2 sentence summary max)
- [ ] **Contact info:** If present, verified current (<6 months old)

**Final Verification:**
- [ ] **All subjective terms quantified:** No undefined "significant", "clean", "complex", etc. (see Task 1.1)
- [ ] **All examples compliant:** Examples follow rule's own mandates (see Task 1.2)
- [ ] **Error handling referenced:** Validation failures cross-reference Error Handling section

**Validation Result Summary:**
```
✅ 45 checks passed
⚠️  2 warnings (installation >5 min, 1 slow link)
❌ 0 failures

README ready for commit.
```
```

#### Acceptance Criteria
- [ ] All 45+ validation items have specific, measurable criteria
- [ ] Each item specifies: what to check, how to measure, pass/fail threshold
- [ ] Exit codes specified (exit 0 if all pass, exit 1 if critical failure)
- [ ] Items grouped by category (Required Sections, Installation, Links, Badges, etc.)
- [ ] Cross-references to Error Handling section for failure procedures
- [ ] Validation result summary format provided

#### Validation
Agent test: "Validate README with 600 lines, no TOC"  
- Agent should flag: "TOC required - README exceeds 500 lines"
- Agent should generate TOC
- Agent should re-validate
- Objective decision (no human judgment)

---

## Phase 3: Minor Enhancements (Est: 1.25 hours)

### Task 3.1: Add Cross-References to Dependencies
**Priority:** LOW  
**Effort:** 20 minutes  
**Dependencies:** None  
**Reviewability:** High (objective presence/absence)

#### Objective
Strengthen connections to dependency rule (000-global-core.md) to help agents discover relevant guidance.

#### Implementation

**1. Update Metadata** (5 min)

```markdown
# CURRENT (line 9):
**Depends:** rules/000-global-core.md

# REPLACE WITH (lines 9-10):
**Depends:** rules/000-global-core.md, rules/202-markup-config-validation.md
**Cross-references:** 000-global-core.md (Section 6: Pre-Task-Completion Validation Gate), 202-markup-config-validation.md (Markdown linting standards)
```

**2. Add Cross-Reference at Readability Section** (5 min)

```markdown
# ADD after line 682:
**See also:** rules/000-global-core.md for general technical writing standards applicable across all documentation.
```

**3. Add Cross-Reference at Validation Section** (5 min)

```markdown
# CURRENT (line 292):
- [x] Markdown lint passes

# REPLACE WITH (lines 292-293):
- [x] Markdown lint passes (see rules/202-markup-config-validation.md for Markdown standards)
- [x] Lint command: `uvx pymarkdownlnt scan README.md` (see 202-markup-config-validation.md for tool usage)
```

**4. Add Cross-Reference at Code Review Section** (5 min)

```markdown
# CURRENT (line 830):
- **Rule:** Include README changes in pull request reviews

# REPLACE WITH (lines 830-831):
- **Rule:** Include README changes in pull request reviews (see rules/000-global-core.md Section 6 for mandatory README update triggers)
```

#### Acceptance Criteria
- [ ] Metadata lists all dependencies (000-global-core.md, 202-markup-config-validation.md)
- [ ] Cross-references added to 4+ locations throughout rule
- [ ] Each reference specifies section number or topic when possible
- [ ] References aid agent navigation to related guidance

---

### Task 3.2: Add Estimated Completion Times
**Priority:** LOW  
**Effort:** 15 minutes  
**Dependencies:** None  
**Reviewability:** High (objective presence)

#### Objective
Provide time estimates enabling agents to plan work and set user expectations.

#### Implementation

**1. Add Timing Metadata to Purpose Section** (5 min)

```markdown
# ADD after line 12:

**Estimated Completion Times:**
- README creation (new project): 30-45 minutes
- README update (existing, minor): 10-15 minutes
- README update (existing, major): 20-30 minutes
- Full validation cycle: 5-10 minutes

**Time Breakdown by Section:**
- Quick Start: 15 min (including installation testing)
- Usage examples: 10 min
- Contributing/License: 5 min
- Validation (links, lint, size): 5-10 min
```

**2. Add Timing to Contract Steps** (10 min)

Update Contract → Steps section (added in Task 1.4) to include time estimates:

```markdown
# Each step already has time estimate in Task 1.4 implementation
# Verify totals sum correctly:
# 5 + 5 + 15 + 5 + 15 + 10 + 5 + 3 + 2 + 5 = 70 minutes
# Aligns with metadata: 30-45 min (experienced) to 70 min (comprehensive)
```

#### Acceptance Criteria
- [ ] Overall timing metadata added to Purpose section
- [ ] Time breakdown by major section provided
- [ ] Contract steps include individual time estimates (completed in Task 1.4)
- [ ] Totals are consistent (step sum ≈ overall estimate)

---

### Task 3.3: Clarify Multi-Platform Guidance
**Priority:** LOW  
**Effort:** 30 minutes  
**Dependencies:** None  
**Reviewability:** Medium (completeness)

#### Implementation

**1. Add Multi-Platform Projects Section** (20 min)

Insert after line 507 (Quick Start Section):

```markdown
### Multi-Platform Installation

**When to show platform-specific instructions:**
- Installation commands differ significantly between platforms (>2 command differences)
- Prerequisites vary by platform (macOS Homebrew vs Ubuntu apt vs Windows Chocolatey)
- Build process platform-dependent (Windows requires additional tools)
- Project supports 2+ major platforms: Linux, macOS, Windows, BSD

**Pattern:** Use collapsible `<details>` sections

```markdown
## Quick Start

**Choose your platform:**

<details>
<summary>macOS / Linux</summary>

```bash
# Install dependencies
brew install node  # macOS
# or: sudo apt install nodejs  # Ubuntu/Debian

# Clone and run
git clone https://github.com/org/repo.git
cd repo
npm install && npm start
```

**What just happened?**
- [PASS] Installed Node.js via package manager
- [PASS] Cloned repository and installed dependencies
- [PASS] Started development server at http://localhost:3000

</details>

<details>
<summary>Windows (PowerShell)</summary>

```powershell
# Install dependencies
choco install nodejs  # Chocolatey

# Clone and run
git clone https://github.com/org/repo.git
Set-Location repo
npm install
npm start
```

**What just happened?**
- [PASS] Installed Node.js via Chocolatey
- [PASS] Cloned repository and installed dependencies
- [PASS] Started development server at http://localhost:3000

</details>

**Success Indicator (all platforms):**
✅ Browser opens to http://localhost:3000
✅ Console shows "Compiled successfully!"
```

**When to use single Quick Start:**
- Installation identical across platforms (<2 command differences)
- Tools are cross-platform (Python, Node.js, Docker work everywhere)
- Platform differences handled by tools themselves (npm, pip auto-detect)

**Example - Cross-Platform Quick Start:**
```bash
# Works on all platforms (macOS, Linux, Windows with Git Bash)
git clone https://github.com/org/repo.git
cd repo
python -m pip install -r requirements.txt
python app.py
```

**Avoid:** Inline platform notes (clutters Quick Start)

**Anti-Pattern:**
```bash
git clone ...
cd repo

# macOS: brew install node
# Ubuntu: sudo apt install nodejs  
# Windows: choco install nodejs
# Fedora: sudo dnf install nodejs

npm install && npm start
```

**Correct:** Move to Prerequisites or use `<details>`.
```

**2. Update Multi-Platform References** (10 min)

Update existing mentions to reference new section:

```markdown
# Line 94 - CURRENT:
- **Multi-Platform:** Show all repository platform options with "(choose one)" guidance

# REPLACE WITH (line 94):
- **Multi-Platform:** See Multi-Platform Installation section (line 508) for platform-specific patterns

# Line 454 - CURRENT:
- **Multi-Platform Projects:** Include badges for hosting platforms

# REPLACE WITH (line 454):
- **Multi-Platform Projects:** Include badges for hosting platforms; see Multi-Platform Installation (line 508) for installation patterns

# Line 507 - DELETE (redundant with new section):
# - **Multi-Platform:** Show both platform options for dual-hosted repositories
```

#### Acceptance Criteria
- [ ] Multi-Platform Projects section added with clear decision criteria
- [ ] Provides both `<details>` pattern (for divergent platforms) and single pattern (for compatible platforms)
- [ ] Includes anti-pattern showing what to avoid
- [ ] Updates 3 existing multi-platform references to point to new section
- [ ] Removes redundant guidance

---

## Validation and Testing

### Pre-Implementation Validation
- [ ] Review review feedback (reviews/801-project-readme-review-2025-12-12.md)
- [ ] Read current rule (rules/801-project-readme.md)
- [ ] Identify line ranges for all planned changes
- [ ] Check for merge conflicts with other planned updates

### During Implementation
- [ ] Complete Phase 1 tasks before starting Phase 2
- [ ] Run word count after each consolidation (Task 2.1)
- [ ] Test quantified thresholds with agent simulation (Task 1.1)
- [ ] Verify examples are executable (Task 1.2)

### Post-Implementation Validation

#### Automated Checks
```bash
# 1. Markdown linting
uvx pymarkdownlnt scan rules/801-project-readme.md

# 2. Token budget calculation
word_count=$(wc -w < rules/801-project-readme.md)
tokens=$(python -c "print(int($word_count * 1.3))")
echo "Token count: $tokens (budget: ~4500)"
# Should output: Token count: ~4400 (budget: ~4500)

# 3. Verify Contract section populated
grep -A 50 "^<contract>" rules/801-project-readme.md | grep -q "<inputs_prereqs>"
echo "Contract populated: $?"  # Should output: 0

# 4. Count quantified thresholds
grep -c "defined as ANY of\|defined as\|threshold:" rules/801-project-readme.md
# Should output: 35+ (all thresholds quantified)

# 5. Verify example compliance
grep -A 10 "^```bash" rules/801-project-readme.md | grep -q "What just happened?"
echo "Examples compliant: $?"  # Should output: 0
```

#### Manual Checks
- [ ] Read through updated rule for flow and readability
- [ ] Verify all cross-references point to correct lines
- [ ] Check that consolidated sections maintain all critical information
- [ ] Confirm Error Handling section covers 6+ scenarios
- [ ] Validate timing estimates are realistic

#### Agent Simulation Tests
Run these prompts against updated rule to verify agent autonomy:

**Test 1: Threshold Decision**
```
Prompt: "I have a README with 600 lines. Should I add a Table of Contents?"
Expected: "YES - README exceeds 500 lines threshold (defined at line X)"
PASS if: Agent answers without asking human
```

**Test 2: Example Following**
```
Prompt: "Create Quick Start section for Python project"
Expected: Output includes all 4 elements (commands, explanation, success indicator, next steps)
PASS if: All elements present, matches pattern from rule
```

**Test 3: Error Handling**
```
Prompt: "Installation test failed: 'python: command not found'"
Expected: Agent adds Prerequisites section, adds version check, retests
PASS if: Agent follows Error Handling → Scenario 2 without human intervention
```

**Test 4: Validation**
```
Prompt: "Validate README: 45 links, 2 return 404, 1 times out"
Expected: Agent applies Error Handling → Scenario 3 (fixes 404s, notes timeout)
PASS if: Agent resolves failures autonomously
```

### Success Criteria (Overall)

**Scoring Improvement:**
- Actionability: 2/5 → 4/5 (all thresholds quantified)
- Completeness: 2/5 → 4/5 (error handling added)
- Consistency: 2/5 → 4/5 (examples fixed)
- Token Efficiency: 3/5 → 4/5 (within budget)
- **Overall: 18/30 → 25-26/30** (target achieved)

**Agent Autonomy:**
- Current: 35% → Target: 85% (achieved via threshold quantification + error handling)

**Threshold Resolution:**
- Undefined: 35+ → 0 (all quantified in Task 1.1)

**Example Compliance:**
- Violations: 4 → 0 (all fixed in Task 1.2)

**Token Budget:**
- Variance: +15.6% → -2.2% (within tolerance)

---

## Risk Assessment

### High-Risk Items

**1. Token Budget After Phase 1 Additions**
- **Risk:** Tasks 1.3 (Error Handling) and 1.4 (Contract) add ~1,500 tokens
- **Mitigation:** Task 2.1 removes ~800 tokens; net impact still ~5,900 tokens (31% over)
- **Resolution:** Must execute Task 2.1 consolidations fully to achieve target
- **Contingency:** If >10% over after Phase 2, create 801a-readme-error-handling.md split rule

**2. Example Changes May Invalidate Line References**
- **Risk:** Fixing examples (Task 1.2) shifts line numbers for subsequent tasks
- **Mitigation:** Process tasks in order; update line references after each phase
- **Resolution:** Use section names as primary navigation, line numbers as hints

**3. Quantifying All 35 Thresholds in 3 Hours**
- **Risk:** Time estimate may be optimistic for thorough, thoughtful quantification
- **Mitigation:** Prioritize most-used terms first (clean, complex, significant)
- **Resolution:** Acceptable to exceed 3 hours if quality maintained

### Medium-Risk Items

**4. Error Handling Section May Introduce Ambiguity**
- **Risk:** New failure scenarios could contain undefined terms
- **Mitigation:** Review Error Handling section against Threshold Audit during writing
- **Resolution:** Apply same quantification standards to new content

**5. Consolidations May Break Internal Logic Flow**
- **Risk:** Removing "Investigation Required" blocks may disconnect related guidance
- **Mitigation:** Add cross-references where content removed
- **Resolution:** Test readability after consolidations

### Low-Risk Items

**6. Cross-References May Point to Outdated Lines**
- **Risk:** Line numbers shift after edits
- **Mitigation:** Update cross-references in final validation pass
- **Resolution:** Use section names + approximate line ranges

---

## Rollout Plan

### Development Approach

**Option A: Sequential (Recommended)**
- Complete Phase 1 → Validate → Complete Phase 2 → Validate → Complete Phase 3
- **Pros:** Validate improvements incrementally, easier to isolate issues
- **Cons:** Longer total elapsed time

**Option B: Parallel** 
- Multiple contributors work on different phases simultaneously
- **Pros:** Faster completion (if multiple contributors available)
- **Cons:** High merge conflict risk, dependencies may break

**Recommendation:** Option A (Sequential) - Dependencies between phases make parallel risky

### Commit Strategy

**Option 1: Atomic Commits (One per Task)**
```bash
git commit -m "fix(801): quantify all subjective thresholds (Task 1.1)"
git commit -m "fix(801): fix example-mandate violations (Task 1.2)"
git commit -m "feat(801): add error handling section (Task 1.3)"
# ... 10 commits total
```
**Pros:** Granular history, easy to revert specific change  
**Cons:** Many commits, may clutter history

**Option 2: Phase Commits (One per Phase)**
```bash
git commit -m "fix(801): critical fixes - thresholds, examples, errors, contract (Phase 1)"
git commit -m "refactor(801): token optimization and failure coverage (Phase 2)"
git commit -m "docs(801): cross-refs, timing, multi-platform (Phase 3)"
```
**Pros:** Clean history, logical grouping  
**Cons:** Harder to revert individual tasks

**Option 3: Single Commit**
```bash
git commit -m "fix(801): comprehensive remediation per review 2025-12-12

- Quantified 35+ subjective thresholds for agent autonomy
- Fixed example-mandate violations (4 violations resolved)
- Added error handling section (6+ scenarios)
- Populated Contract section with complete workflow
- Reduced token count to ~4,400 (within budget)
- Added failure scenarios (30% coverage)
- Strengthened validation checklist (45+ items)
- Added cross-references, timing estimates, multi-platform guidance

Addresses: reviews/801-project-readme-review-2025-12-12.md
Score improvement: 18/30 → 25-26/30
Agent autonomy: 35% → 85%"
```
**Pros:** Complete context in one commit, easy to reference  
**Cons:** Difficult to revert partial changes

**Recommendation:** Option 2 (Phase Commits) - Balances granularity and history cleanliness

### Review and Approval

**Self-Review Checklist:**
- [ ] All tasks in implementation plan completed
- [ ] Automated validation checks pass
- [ ] Manual validation checks pass
- [ ] Agent simulation tests pass (4/4)
- [ ] No new undefined thresholds introduced
- [ ] No new example violations introduced
- [ ] Token budget within ±10%
- [ ] Line references updated after edits

**Peer Review (Recommended):**
- [ ] Another AI agent reviews updated rule using RULE_REVIEW_PROMPT.md
- [ ] Target score: 25-27/30
- [ ] If score <25: Address feedback before merge
- [ ] If score ≥25: Approve for merge

**Approval Criteria:**
- All Phase 1 tasks complete (critical fixes)
- Agent autonomy ≥80%
- Token budget within ±15%
- No regression in existing functionality

---

## Timeline Estimate

**Assuming single contributor, sequential approach:**

| Phase | Tasks | Estimated Time | Elapsed Days* |
|-------|-------|----------------|---------------|
| Phase 1 | 1.1-1.4 | 6.75 hours | 2-3 days |
| Validation | Automated + Manual | 1 hour | +0.5 days |
| Phase 2 | 2.1-2.3 | 3.25 hours | 1-2 days |
| Validation | Automated + Manual | 0.5 hours | +0.5 days |
| Phase 3 | 3.1-3.3 | 1.25 hours | 0.5-1 day |
| Final Validation | All checks + Agent tests | 1 hour | +0.5 days |
| **Total** | **10 tasks** | **13.75 hours** | **5-8 days** |

*Elapsed days assumes 2-3 hours per day of focused work

**Accelerated Timeline:**
- If full-time focus (6+ hours/day): **2-3 days**
- If multiple contributors (parallel phases): **3-4 days** (with merge overhead)

---

## Success Metrics

### Quantitative Targets

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Overall Score | 18/30 (60%) | 25-27/30 (83-90%) | RULE_REVIEW_PROMPT evaluation |
| Actionability | 2/5 | 4/5 | Threshold Audit (0 undefined terms) |
| Completeness | 2/5 | 4/5 | Error scenarios documented |
| Consistency | 2/5 | 4/5 | Example-mandate violations = 0 |
| Token Efficiency | 3/5 | 4/5 | Budget variance within ±10% |
| Agent Autonomy | 35% | 85% | Simulation tests pass rate |
| Undefined Thresholds | 35+ | 0 | Grep for subjective terms without definitions |
| Example Violations | 4 | 0 | Manual example compliance check |
| Token Budget Variance | +15.6% | ±5% | (actual - declared) / declared × 100% |
| Failure Coverage | 7% (1/14) | 30% (5/15) | Failure examples / total examples |

### Qualitative Targets

- [ ] Agent can execute README creation without human judgment for threshold decisions
- [ ] Agent can recover from common failures without human intervention
- [ ] Agent can validate README objectively against measurable criteria
- [ ] Human reviewers find rule clearer and more actionable
- [ ] No new issues introduced (no regression)

---

## Appendix: Task Dependencies

```
Dependency Graph:

Phase 1 (Parallel safe):
├── Task 1.1: Quantify Thresholds (no dependencies)
├── Task 1.2: Fix Examples (no dependencies)
├── Task 1.3: Add Error Handling (no dependencies)
└── Task 1.4: Populate Contract (no dependencies)

Phase 2:
├── Task 2.1: Reduce Token Count
│   └── DEPENDS ON: All Phase 1 tasks (may add tokens)
├── Task 2.2: Add Failure Scenarios
│   └── DEPENDS ON: Task 1.3 (references Error Handling)
└── Task 2.3: Strengthen Validation
    └── DEPENDS ON: Task 1.1 (references quantified thresholds)
    └── DEPENDS ON: Task 1.3 (references Error Handling)

Phase 3 (Parallel safe):
├── Task 3.1: Add Cross-References (no dependencies)
├── Task 3.2: Add Timing Estimates (no dependencies)
└── Task 3.3: Clarify Multi-Platform (no dependencies)
```

**Optimal Execution Order:**
1. Phase 1 tasks (any order, but 1.1 first recommended for foundation)
2. Validate Phase 1 completion
3. Task 2.1 (reduces token count before adding more content)
4. Tasks 2.2 and 2.3 (parallel safe)
5. Validate Phase 2 completion
6. Phase 3 tasks (any order, parallel safe)
7. Final validation

---

## Notes

- Line numbers are approximate and will shift during editing
- Use section headers as primary navigation
- Update RULES_INDEX.md TokenBudget metadata after completing Task 2.1
- Consider running RULE_REVIEW_PROMPT again post-remediation to verify improvements
- This plan may be used as template for future rule remediation efforts

---

**Plan Version:** 1.0  
**Last Updated:** 2025-12-12  
**Status:** READY FOR IMPLEMENTATION

