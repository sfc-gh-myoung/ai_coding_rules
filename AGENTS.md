# MANDATORY RULE LOADING PROTOCOL

**FIRST ACTION EVERY RESPONSE:**

1. **Load Foundation** - Read `rules/000-global-core.md` (always first, no exceptions)
   - IF not accessible → STOP: "Cannot proceed - 000-global-core.md not accessible"
   - IF empty → STOP: "Rule generation failed - 000-global-core.md is empty"

2. **Declare MODE** - First line of response: `MODE: [PLAN|ACT]`
   - Default: MODE: PLAN
   - ACT only after user types "ACT"

3. **List Loaded Rules** - Second section: `## Rules Loaded`
   - Always include: `- rules/000-global-core.md (foundation)`
   - Add domain/specialized rules based on task analysis

4. **Load Domain + Language Rules** - Based on file extensions in task:
   - `.py`, `.pyi`, `pyproject.toml` → `rules/200-python-core.md`
   - `.sql` → `rules/100-snowflake-core.md`
   - `.sh`, `.bash`, `.zsh` → `rules/300-bash-scripting-core.md`
   - `Dockerfile`, `docker-compose.yml` → `rules/400-docker-best-practices.md`
   - `.md` (in `rules/`) → `rules/002-rule-governance.md`
   - Streamlit tasks → `rules/101-snowflake-streamlit-core.md`
   - **Load even for "simple" tasks** (linting, formatting, syntax fixes)

5. **Load Activity-Specific Rules** - Search `RULES_INDEX.md` Keywords column for:
   - **test**, pytest, coverage → `rules/206-python-pytest.md`
   - **lint**, format, code quality → `rules/201-python-lint-format.md`
   - **deploy**, CI/CD, automation → `rules/820-taskfile-automation.md`
   - **optimize**, performance, cache → Performance rules
   - **secure**, auth, validation → Security rules
   - **document**, docstring, README → Documentation rules

**Violation = INVALID Response** - See Verification Protocol for enforcement gates.

## Verification Protocol

Before proceeding with ANY task, confirm all validation gates pass:

### Validation Gates (MANDATORY)

**GATE 1: Foundation Check**
- IF `rules/000-global-core.md` NOT accessible → STOP
- OUTPUT: "ERROR: Cannot proceed without 000-global-core.md. Verify file exists in context."
- THEN: Halt response, await user correction

**GATE 2: MODE Declaration**
- IF first line of response != `MODE: [PLAN|ACT]` → INVALID RESPONSE
- OUTPUT: "ERROR: Response must start with MODE declaration"
- THEN: Regenerate response with `MODE: PLAN` as first line

**GATE 3: Rule Loading Statement**
- IF `## Rules Loaded` section missing from response → INVALID RESPONSE
- OUTPUT: "ERROR: Must explicitly list loaded rules"
- THEN: Regenerate with rules listed (e.g., "- rules/000-global-core.md (foundation)")

**GATE 4: PLAN Mode Protection**
- IF current mode = PLAN AND file modification attempted → STOP IMMEDIATELY
- OUTPUT: "ERROR: Cannot modify files in PLAN mode"
- THEN: Present task list, await explicit "ACT" authorization from user

**GATE 5: ACT Mode Validation**
- IF current mode = ACT AND modifications made AND validation not executed → INCOMPLETE TASK
- OUTPUT: "ERROR: Must validate changes before completion (lint/test/compile)"
- THEN: Run validation tools, report results before marking task complete

**GATE 6: File Type Analysis**
- IF editing files AND language-specific rules NOT loaded → INVALID RESPONSE
- MAPPING: `.py`→200-python-core | `.sql`→100-snowflake-core | `.sh`→300-bash-scripting-core
- THEN: Load appropriate language rules before proceeding

**GATE 7: Activity Keyword Matching**
- IF task contains activity keywords AND specialized rules NOT loaded → SUBOPTIMAL
- KEYWORDS: test→206-pytest | lint→201-python-lint | deploy→820-taskfile | optimize→performance rules
- THEN: Search RULES_INDEX.md Keywords column, load matching rules

### Common Violations to Detect

| Violation Pattern | Consequence | Recovery Action |
|-------------------|-------------|-----------------|
| No MODE declaration | INVALID response | Regenerate starting with `MODE: PLAN` |
| Rules not listed | INVALID response | Add `## Rules Loaded` section |
| File edit in PLAN mode | STOP immediately | Return to PLAN, present task list, await "ACT" |
| No validation after changes | INCOMPLETE task | Run lint/test/compile before completion |
| Language rules skipped | INVALID response | Load file-type-specific rules (200-python, 100-snowflake, etc.) |
| Activity rules skipped | SUBOPTIMAL response | Search RULES_INDEX.md, load specialized rules |

## Response Format

**Required format for all responses:**
```
MODE: [PLAN|ACT]

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/[domain]-core.md (e.g., 100-snowflake-core, 200-python-core)
- rules/[specialized].md (task-specific rules)

[Then proceed with response...]
```

## Temporal Accuracy & Date Validation

**Context**: Tasks involving research, changelogs, copyright headers, or scheduling.
**Constraint**: Do not assume or hallucinate the current date.

1. **Verification**:
   - Before generating date-specific content, you MUST verify the current date.
   - If in `MODE: ACT` (Terminal Access): Execute `date +%Y-%m-%d` (or `date "+%Y %m %d"`) to confirm.
   - If in `MODE: PLAN` (No Terminal): Strictly rely on the System Time provided in the prompt context. If unavailable, ask the user.

2. **Formatting**:
   - Standard: ISO 8601 (`YYYY-MM-DD`) for all technical logs and filenames.
   - Research/Prose: "Month Day, Year" (e.g., October 05, 2023).

3. **Prohibited**:
   - Never use phrases like "As of my last update..." for *current* file generation tasks (e.g., Changelogs).
   - Never hardcode a date from the future or distant past without explicit user instruction.

## Rule Discovery Reference

### Rule Organization

Rules are organized by numeric domain prefixes:
- **000-099:** Core/Foundational (always start here)
- **100-199:** Snowflake ecosystem
- **200-299:** Python ecosystem
- **300-399:** Shell/Bash scripting
- **400-499:** Docker/Containers
- **500-599:** Data Science/Analytics
- **600-699:** Data Governance
- **700-799:** Business Analytics
- **800-899:** Project Management
- **900-999:** Demo/Examples

### Task Keyword Extraction

**Technology Keywords** (trigger domain rules):
- Python, pytest, FastAPI, Flask, Typer, Pydantic, pandas → 200-python-core.md + specialized rules
- Snowflake, SQL, Streamlit, Cortex, SPCS → 100-snowflake-core.md + specialized rules
- Docker, containers, multi-stage builds → 400-docker-best-practices.md
- Bash, shell, zsh → 300-bash-scripting-core.md or 310-zsh-scripting-core.md

**Activity Keywords** (trigger specialized rules):
- **testing, test coverage, unit tests, integration tests, fixtures, mocking** → 206-python-pytest.md
- deployment, CI/CD, automation, workflow → 820-taskfile-automation.md, 803-project-git-workflow.md
- validation, linting, formatting, code quality → 201-python-lint-format.md
- documentation, docs, docstrings, README, CHANGELOG → 204-python-docs-comments.md, 800-project-changelog.md
- security, authentication, authorization, XSS, SQL injection → *-security.md rules
- performance, optimization, caching, slow queries → *-performance*.md rules

**Process for Every Task:**
1. Extract keywords: Identify ALL technology and activity terms in user's request
2. Search RULES_INDEX.md: Look for matches in Keywords column
3. Load matching rules: In dependency order (check "Depends On" column)
4. State loaded rules AND searched keywords: In "Rules Loaded" section of response

### Common Rule Loading Pitfalls

**Testing tasks without pytest rule** ⚠️
- Trigger words: testing, test coverage, unit tests, integration tests, fixtures, parametrization
- Required: 206-python-pytest.md
- Contains: AAA pattern, fixture patterns, Pre-Task-Completion Test Execution Gate

**Python tasks without linting rule** ⚠️
- Trigger words: Python, code quality, formatting, style, lint errors
- Required: 200-python-core.md + 201-python-lint-format.md
- Contains: `uvx ruff` usage, validation gates, linting standards

**Deployment tasks without automation rules** ⚠️
- Trigger words: deploy, CI/CD, automation, workflow, release
- Required: 820-taskfile-automation.md, 803-project-git-workflow.md
- Contains: deployment patterns, git workflow management, task automation

**Documentation tasks without docs rules** ⚠️
- Trigger words: documentation, docs, README, CHANGELOG, docstrings
- Required: 800-project-changelog.md, 801-project-readme.md, 204-python-docs-comments.md
- Contains: structured documentation standards, changelog format, docstring conventions

**Streamlit tasks without Streamlit rules** ⚠️
- Trigger words: Streamlit, dashboard, st.cache, fragments, SiS
- Required: 101-snowflake-streamlit-core.md + specialized 101*-streamlit-*.md
- Contains: state management, caching, performance patterns

### Progressive Loading Strategy

Load rules incrementally to manage token budget:

1. **Foundation:** 000-global-core.md (always first)
2. **Domain:** Technology-specific core (e.g., 100-snowflake-core, 200-python-core)
3. **Specialized:** Task-specific rules based on Keywords match
4. **Monitor:** Track cumulative tokens, prioritize Critical/High tiers

### Rule Discovery Methods

**Primary Method: Search RULES_INDEX.md**

Use RULES_INDEX.md as the authoritative source for rule discovery:
1. **Search Keywords/Hints column** for terms matching your task
2. **Check Depends On column** for prerequisites
3. **Load in dependency order** (prerequisites first)

**Split Rules Pattern**

Rules may use letter suffixes (e.g., 111a, 111b, 111c) for subtopic specialization. This improves token efficiency by allowing focused loading. Search RULES_INDEX.md Keywords column and check "Related Rules" sections to discover related split rules.

### Essential Rule Metadata

When parsing rules, use these metadata fields:

- **Keywords:** Comma-separated terms for semantic discovery
- **TokenBudget:** Approximate tokens needed for context management
- **ContextTier:** Priority level (Critical > High > Medium > Low)
- **Depends:** Prerequisites that must be loaded first
