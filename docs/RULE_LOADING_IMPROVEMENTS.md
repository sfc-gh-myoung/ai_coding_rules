# Rule Loading Improvement Recommendations

## Problem Statement

An AI assistant edited Python files (`scripts/validate_agent_rules.py`, `scripts/generate_rules_index.py`) without loading any Python-specific rules (`200-python-core.mdc`, `201-python-lint-format.mdc`). This occurred because:

1. **Session continuation context** focused on documentation/validation infrastructure, not Python development
2. **Task framing** ("Fix linting issues") felt syntactic/mechanical rather than code development
3. **No auto-load mechanism** triggers language rules when editing files of that type
4. **Keyword matching failed** - "linting" should have triggered `201-python-lint-format.mdc` lookup

## Root Causes

### 1. AGENTS.md Relies Too Much on Manual Keyword Matching
- Step 3 requires "Explicitly search Keywords column for terms matching your task"
- AI must manually extract keywords and search RULES_INDEX.md
- No structured guidance for file-type-based triggers
- "Linting" task with Python files didn't trigger Python rule loading

### 2. Missing File Extension Trigger Logic
- No explicit instruction: "If editing .py files → load 200-python-core.mdc"
- Agents must infer file type relationships
- Session continuation can lose file type context

### 3. 000-global-core.md Lacks File-Type Trigger Guidance
- Section 2 (Task Confirmation) doesn't mention file type analysis
- No requirement to analyze file extensions before rule selection

### 4. Weak Keyword Coverage in RULES_INDEX.md
- `201-python-lint-format.mdc` keywords: "Ruff, linting, formatting, code quality..."
- "Fix linting issues" should match but requires explicit search
- No bidirectional mapping: task type → file type → required rules

## Recommended Changes

**IMPORTANT:** All rule file changes should be made to template versions:
- AGENTS.md changes → Edit `discovery/AGENTS.md` (not `.cursor/rules/`)
- Rule content changes → Edit files in `templates/` directory (not `.cursor/rules/`)
- After editing templates, regenerate deployments with `task rule:all`

---

## 1. discovery/AGENTS.md Improvements

**File to edit:** `discovery/AGENTS.md`

### A. Add File-Type Trigger Section (After Line 29)

**Location:** Insert between Step 2 and Step 3

```markdown
3. **Load Language/Framework Rules Based on File Types**: Analyze files being edited and load corresponding rules:
   - **Python files** (`.py`, `.pyi`) → `.cursor/rules/200-python-core.mdc`
   - **SQL files** (`.sql`) → `.cursor/rules/100-snowflake-core.mdc`
   - **Markdown files** (`.md`) → Consider `002-rule-governance.mdc` if editing rules
   - **Docker files** (`Dockerfile`, `docker-compose.yml`) → `.cursor/rules/400-docker-best-practices.mdc`
   - **Shell scripts** (`.sh`, `.bash`) → `.cursor/rules/300-bash-scripting-core.mdc`
   - **YAML/TOML config** (`pyproject.toml`, `.yml`) → Load project-type rules (Python/Docker/etc.)
   - **If editing multiple file types**: Load all corresponding language rules
   - **This step is mandatory** even if task seems simple (linting, formatting, syntax fixes)
```

### B. Enhance Step 3 (Specialized Rules) with Activity-Based Keywords

**Location:** Replace existing Step 3 (Line 31-37)

```markdown
4. **Load Specialized Rules**: Read task-specific rules using both file type AND activity keywords:
   - **Activity Keywords to Search**: 
     - Code quality tasks: `linting`, `formatting`, `validation`, `code quality`
     - Testing tasks: `pytest`, `testing`, `test fixtures`, `coverage`
     - Performance tasks: `optimization`, `performance`, `caching`, `profiling`
     - Security tasks: `security`, `authentication`, `input validation`, `secrets`
     - Deployment tasks: `deployment`, `CI/CD`, `automation`, `Docker`
   - **Search Strategy**:
     1. Extract file extensions from files being edited
     2. Extract activity keywords from user task description
     3. Search RULES_INDEX.md Keywords column for matches
     4. Prioritize rules that match BOTH file type AND activity
   - **Example**: Editing `app.py` with "fix linting" → Load `200-python-core.mdc` (file type) + `201-python-lint-format.mdc` (activity)
   - **Check "Depends On" column**: Load prerequisites before dependent rules
   - **Document search results**: State which keywords were searched and which rules matched
   - **If RULES_INDEX.md not accessible**: Proceed with foundation + language rules, inform user
```

### C. Add Validation Checklist (After Step 5)

**Location:** Insert after line 45

```markdown
## Rule Loading Validation Checklist

Before making ANY code changes, verify:
- [ ] **File extensions analyzed**: Identified all file types being edited
- [ ] **Language rules loaded**: Loaded core rules for each file type (200-python-core for .py, etc.)
- [ ] **Activity keywords extracted**: Identified task type (linting, testing, deployment, etc.)
- [ ] **Specialized rules loaded**: Loaded activity-specific rules from RULES_INDEX.md
- [ ] **Dependencies resolved**: All "Depends On" prerequisites loaded
- [ ] **Rules declared**: Listed all loaded rules in "## Rules Loaded" section

**Common Mistakes to Avoid:**
- ❌ Loading only 000-global-core for Python editing tasks
- ❌ Skipping language rules for "simple" tasks like linting or formatting
- ❌ Not searching RULES_INDEX.md Keywords column for activity matches
- ❌ Loading rules after starting code edits instead of before
```

---

## 2. templates/000-global-core.md Improvements

**File to edit:** `templates/000-global-core.md`

### A. Enhance Section 2 (Task Confirmation Protocol)

**Location:** Around line 120-150 (Section 2 content)

**Add subsection:**

```markdown
#### 2.3 File Type Analysis and Rule Loading

Before proposing a task list, analyze the workspace to determine required rules:

**Automatic Rule Loading Triggers:**
1. **Detect file types** from user request or workspace analysis
2. **Load language core rules** for all file types being edited:
   - `.py` files → Load `200-python-core.mdc`
   - `.sql` files → Load `100-snowflake-core.mdc`
   - `Dockerfile` → Load `400-docker-best-practices.mdc`
   - `.sh` files → Load `300-bash-scripting-core.mdc`
3. **Extract activity keywords** from task description:
   - "lint", "format" → Load `201-python-lint-format.mdc` (if Python)
   - "test", "pytest" → Load `206-python-pytest.mdc` (if Python)
   - "optimize", "performance" → Load performance-specific rules
4. **Search RULES_INDEX.md** Keywords column for activity matches
5. **Load dependencies** from "Depends On" column

**Critical Rule:**
> Even for seemingly "simple" tasks (linting, formatting, syntax fixes), you MUST load language core rules. These tasks still require understanding language-specific patterns, tool usage, and best practices.

**Example - Task: "Fix linting issues in Python files"**
```
## Rules Loaded
- .cursor/rules/000-global-core.mdc (foundation)
- .cursor/rules/200-python-core.mdc (Python file type detected)
- .cursor/rules/201-python-lint-format.mdc (linting activity keyword matched)

File type analysis: Detected .py files → Python language rules required
Activity analysis: "linting" → Matched Keywords: "Ruff, linting, code quality"
```
```

### B. Update Quick Start TL;DR

**Location:** Line 58-66

**Add to Essential Patterns list:**

```markdown
- **Load rules by file type** - Editing .py? Load 200-python-core first
- **Search RULES_INDEX.md by activity** - Linting? Testing? Search Keywords column
- **Never skip language rules** - Even "simple" tasks need language-specific guidance
```

---

## 3. discovery/RULES_INDEX.md Improvements

**File to edit:** `discovery/RULES_INDEX.md`

### A. Add Reverse Lookup Table (Insert After Line 25)

```markdown
## Quick Lookup: File Type → Required Rules

**Python Files (`.py`, `.pyi`):**
- Core: `200-python-core.mdc`
- Linting/Formatting: `201-python-lint-format.mdc`
- Testing: `206-python-pytest.mdc`
- Documentation: `204-python-docs-comments.mdc`

**SQL Files (`.sql`):**
- Core: `100-snowflake-core.mdc`
- Performance: `103-snowflake-performance-tuning.mdc`
- Demo Engineering: `102-snowflake-sql-demo-engineering.mdc`

**Streamlit Apps (`.py` with Streamlit):**
- Core: `101-snowflake-streamlit-core.mdc`
- Performance: `101b-snowflake-streamlit-performance.mdc`
- Testing: `101d-snowflake-streamlit-testing.mdc`
- Security: `101c-snowflake-streamlit-security.mdc`

**Docker Files (`Dockerfile`, `docker-compose.yml`):**
- Core: `400-docker-best-practices.mdc`

**Shell Scripts (`.sh`, `.bash`):**
- Core: `300-bash-scripting-core.mdc`

**Configuration Files (`pyproject.toml`, `setup.py`):**
- Core: `200-python-core.mdc`
- Setup: `203-python-project-setup.mdc`

---
```

### B. Enhance Python Rule Keywords

**Location:** Update `200-python-core.mdc` row (around line 60)

**Current Keywords:**
```
Python, uv, Ruff, pyproject.toml, dependency management, virtual environments, modern Python tooling, pytest, validation, uv run, uvx, datetime.now(UTC)
```

**Enhanced Keywords:**
```
Python, .py files, Python development, uv, Ruff, pyproject.toml, dependency management, virtual environments, modern Python tooling, pytest, validation, uv run, uvx, datetime.now(UTC), edit Python files, Python scripts, Python modules
```

**Location:** Update `201-python-lint-format.mdc` row

**Current Keywords:**
```
Ruff, linting, formatting, code quality, style checking, uvx ruff, lint errors, ruff check, ruff format, pyproject.toml configuration
```

**Enhanced Keywords:**
```
Ruff, linting, formatting, code quality, style checking, uvx ruff, lint errors, ruff check, ruff format, pyproject.toml configuration, fix linting, fix formatting, code style, lint violations, format code, linting issues, syntax errors
```

---

## 4. Example Prompts for AI Assistants and Users

See separate files for detailed prompt templates:
- **EXAMPLE_SYSTEM_PROMPT.md** - System prompt additions for AI assistants
- **EXAMPLE_USER_PROMPT.md** - User prompt templates for better results

---

## 5. Implementation Priority

**High Priority (Immediate):**
1. Add File-Type Trigger Section to `discovery/AGENTS.md` (Section 1.A)
2. Add Reverse Lookup Table to `discovery/RULES_INDEX.md` (Section 3.A)
3. Enhance 201-python-lint-format.mdc keywords in `templates/201-python-lint-format.md` (Section 3.B)
4. Create `EXAMPLE_SYSTEM_PROMPT.md` and `EXAMPLE_USER_PROMPT.md`

**Medium Priority (Next Iteration):**
5. Add File Type Analysis subsection to `templates/000-global-core.md` (Section 2.A)
6. Add Rule Loading Validation Checklist to `discovery/AGENTS.md` (Section 1.C)
7. Update Quick Start TL;DR in `templates/000-global-core.md` (Section 2.B)

**Low Priority (Future Enhancement):**
8. Integrate system prompt guidance into CI/CD validation
9. Add rule loading compliance checks to validation script

**After Template Changes:**
- Run `task rule:all` to regenerate all deployment formats
- Verify changes propagated to `.cursor/rules/`, `rules/`, etc.
- Test with real AI assistant to validate improvements

---

## Expected Impact

**Before Changes:**
- AI edits Python files without loading Python rules
- Keyword matching requires manual inference
- "Simple" tasks bypass specialized rule loading
- File type context lost in session continuation

**After Changes:**
- File extensions automatically trigger language rule loading
- Activity keywords explicitly mapped to specialized rules
- Validation checklist prevents common mistakes
- Reverse lookup table accelerates rule discovery

**Success Metrics:**
- 100% rule loading compliance for file-type-specific tasks
- Zero instances of editing code without language core rules
- Reduced time to identify correct specialized rules
- Improved consistency across session continuations
