# Changelog

All notable changes to the AI Coding Rules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2025-10-29

### Changed

- **docs(agents):** Added MANDATORY RULE LOADING PROTOCOL to AGENTS.md
  - **New Section:** "⚠️ MANDATORY RULE LOADING PROTOCOL (For AI Assistants)" added at top of AGENTS.md
  - **Critical Requirement:** AI assistants MUST load relevant rules before beginning ANY coding task
  - **Four-Step Protocol:**
    1. **Step 1: Analyze the Task** - Identify technology domain, framework/tool, and task type
    2. **Step 2: Load Foundation Rules** - Always read `rules/000-global-core.md` first, then domain core rule (100-Snowflake, 200-Python, 400-Docker, 300-Bash)
    3. **Step 3: Load Specialized Rules** - Search `RULES_INDEX.md` Keywords column and load technology/pattern/feature-specific rules
    4. **Step 4: Verify Rule Loading** - State which rules were loaded, confirm they match task requirements
  - **Enforcement:** Protocol violation if rules not loaded before coding; requires STOP, load rules, review implementation, make corrections
  - **Examples:** Correct approach (load rules first) vs. Incorrect approach (immediate implementation without rules)
  - **Rationale:** Ensures AI assistants have proper context and follow established patterns/standards before making changes
  - **Impact:** Prevents protocol violations where agents make changes without understanding project-specific rules and conventions

## [2.0.0] - 2025-10-29

### Added
- Universal rule format with Depends metadata field for dependency resolution
- AGENTS.md transformed into universal discovery guide (not a rule)
- Decision tree in AGENTS.md for rule selection
- Ecosystem-specific examples in AGENTS.md (Python, Node.js, Java, Go)
- Depends metadata to all 70+ rule files for explicit dependency tracking
- Generator support for Depends metadata preservation in universal format
- Generator logic to exclude AGENTS.md and EXAMPLE_PROMPT.md from all rule formats (they're guides, not rules)

### Changed
- 000-global-core.md streamlined to contain only foundational principles (~300 tokens)
- Operational details moved from 000-global-core.md to AGENTS.md
- RULES_INDEX.md updated to exclude AGENTS.md (not a rule)
- Universal format now preserves Keywords, TokenBudget, ContextTier, and Depends metadata
- README.md comprehensively updated:
  - Added clear project scope and intent section
  - Added visual decision tree flowchart for rule selection
  - Added "Using Rules with Different Tools" section with examples
  - Added programmatic rule loading examples for CLI tools
  - Clarified AGENTS.md role as discovery guide (not a rule)
- EXAMPLE_PROMPT.md completely rewritten as universal baseline prompt:
  - Removed all duplicated content that exists in rules
  - Added automatic rule loading protocol
  - Added semantic discovery instructions
  - Follows prompt engineering best practices with XML tags
  - Includes token budget management
  - Works universally across all platforms
- gen-rules script updated to v2.1:
  - Added universal rule generation to help text and examples
  - Updated COMMON TASKS to include rule:universal
  - Added example for generating universal rules

### Added

- **102-snowflake-sql-demo-engineering.md** (v2.0, 2025-10-23, Auto-attach)
  - New demo-focused SQL rule for Snowflake demos and customer learning environments
  - Schema-based naming pattern (grid_setup.sql, customer_load.sql, grid_teardown.sql)
  - Per-schema setup and teardown patterns for independent operations
  - Inline documentation that teaches concepts (educational comments)
  - Progress indicators (SELECT statements for feedback)
  - Demo-safe idempotent patterns (CREATE OR REPLACE, IF NOT EXISTS)
  - Comprehensive examples for setup, load, and teardown files
  - Section on when to use production patterns (reference to 102a)
  - Benefits: Clearer for pre-sales engineers, reduced cognitive load, auto-attach for all SQL work

- **102a-snowflake-sql-automation.md** (v2.0, 2025-10-23, Agent Requested)
  - New production automation rule for parameterized SQL templates and CI/CD
  - Snowflake variable syntax (<%DATABASE%>, <%SCHEMA%>) for parameterization
  - Production-safe idempotent patterns (MERGE, CREATE TABLE IF NOT EXISTS)
  - Never use CREATE OR REPLACE for tables (data loss risk)
  - Directory structure for operations (sql/operations/domain/operation/)
  - Template file headers with parameters, usage, and examples
  - Taskfile integration patterns for automation
  - GitHub Actions and GitLab CI integration examples
  - Pre/post deployment validation scripts
  - Benefits: Environment-agnostic SQL, reusable templates, CI/CD ready

### Removed

- **102-snowflake-sql-best-practices.md**
  - Replaced with two specialized rules: 102-snowflake-sql-demo-engineering.md (demo) and 102a-snowflake-sql-automation.md (production)
  - Rationale: Separate concerns for different audiences (demo engineers vs DevOps)
  - Old rule combined demo and production patterns, causing cognitive overload
  - New rules follow existing Streamlit pattern (101-core, 101a-viz, 101b-perf, 101c-security, 101d-testing)

### Changed

- **109c-snowflake-app-deployment.md** (v1.0 → v1.1, 2025-10-25)
  - Added critical Streamlit in Snowflake (SiS) deployment requirements
  - **AUTO_COMPRESS=FALSE mandatory**: Python import system cannot read compressed .py files
  - **Stage path requirements**: Files must be at stage root, not nested subdirectories
  - Root cause documentation: Both issues cause "TypeError: bad argument type for built-in operation"
  - Added Streamlit-specific upload script example with correct syntax
  - Added two new anti-patterns (compression and path mismatch)
  - Added troubleshooting section for TypeError with diagnostic steps
  - Enhanced compliance checklist with Streamlit-specific requirements
  - Keywords added: AUTO_COMPRESS, stage path, ROOT_LOCATION, SiS deployment, TypeError

- **RULES_INDEX.md** (v2.3 → v2.4, 2025-10-23)
  - Replaced 102-snowflake-sql-best-practices.md entry with two new entries
  - Added 102-snowflake-sql-demo-engineering.md (Auto-attach) with demo keywords
  - Added 102a-snowflake-sql-automation.md (Agent Requested) with automation keywords
  - Updated 114-snowflake-cortex-aisql.md dependencies to reference 102-snowflake-sql-demo-engineering.md
  - Updated 901-data-generation-modeling.md dependencies to reference 102-snowflake-sql-demo-engineering.md

- **100-snowflake-core.md, 103-snowflake-performance-tuning.md, 104-snowflake-streams-tasks.md, 106-snowflake-semantic-views.md, 112-snowflake-snowcli.md, 113-snowflake-feature-store.md, 114-snowflake-cortex-aisql.md, 119-snowflake-warehouse-management.md, 122-snowflake-dynamic-tables.md, 500-data-science-analytics.md, 700-business-analytics.md, 901-data-generation-modeling.md** (2025-10-23)
  - Updated Related Rules sections to reference 102-snowflake-sql-demo-engineering.md (replacing 102-snowflake-sql-best-practices.md)
  - 100-snowflake-core.md and 112-snowflake-snowcli.md: Added both 102-snowflake-sql-demo-engineering.md and 102a-snowflake-sql-automation.md

### Added

- **251-python-datetime-handling.md** (v1.0, 2025-10-22)
  - New comprehensive datetime handling rule for Python, Pandas, Plotly, and Streamlit
  - Covers datetime type system (Python datetime vs pd.Timestamp vs datetime64)
  - Type conversion helper function for Pandas 2.x compatibility
  - Timezone management best practices (tz_localize, tz_convert)
  - Date parsing and format standardization
  - Date arithmetic patterns (Timedelta vs DateOffset)
  - Performance optimization for large time series
  - Cross-library compatibility guidance
  - Comprehensive anti-patterns and solutions

- **252-pandas-best-practices.md** (v1.0, 2025-10-22)
  - New comprehensive Pandas performance and best practices rule
  - Vectorization vs iteration patterns (10x-100x+ speedup guidance)
  - Anti-patterns: iterrows(), apply(), chained assignment (SettingWithCopyWarning)
  - Memory optimization strategies (dtypes, categorical data, chunking)
  - Efficient GroupBy and merge/join operations
  - Method chaining patterns
  - Streamlit and Plotly integration guidance
  - Performance benchmarking examples

### Changed

- **101a-snowflake-streamlit-visualization.md** (v1.4, 2025-10-23)
  - Added cross-reference to 251-python-datetime-handling.md for comprehensive datetime guidance
  - Added cross-reference to 252-pandas-best-practices.md for DataFrame optimization
  - Enhanced Related Rules section with new datetime and Pandas rules

- **500-data-science-analytics.md** (2025-10-22)
  - Added note referencing 251-python-datetime-handling.md for datetime operations
  - Added note referencing 252-pandas-best-practices.md for Pandas optimization
  - Updated Related Rules section with new datetime and Pandas rules

- **101b-snowflake-streamlit-performance.md** (2025-10-22)
  - Added cross-reference to 251-python-datetime-handling.md for time series optimization
  - Added cross-reference to 252-pandas-best-practices.md for DataFrame caching patterns

- **RULES_INDEX.md** (2025-10-22)
  - Added entry for 251-python-datetime-handling.md with comprehensive keywords
  - Added entry for 252-pandas-best-practices.md with comprehensive keywords
  - Keywords enable semantic discovery of datetime and Pandas guidance

- **101a-snowflake-streamlit-visualization.md** (v1.1 → v1.4, 2025-10-23)
  - **CORRECTED Anti-Pattern 5:** No error handling for vline rendering (environment-specific compatibility)
  - Added defensive try-except wrapping for all vline marker rendering
  - Use st.warning() to display visible error messages when markers fail to render
  - Ensures charts display even when individual markers fail
  - Addresses Streamlit in Snowflake (SiS) environment library version incompatibilities
  - Provides clear feedback for troubleshooting without silent failures
  - Updated Quick Compliance Checklist with error handling requirements

### Removed

- **UNIVERSAL_PROMPT.md** (2025-10-23)
  - Deleted redundant prompt template file containing content duplicated in core rules
  - All response structure guidance already exists in `000-global-core.md`
  - All rule structure templates already exist in `002-rule-governance.md`
  - Removed entry from RULES_INDEX.md
  - Rationale: Eliminated duplication, improved rule system clarity

### Added

- **Context Engineering and Tool Design Rules** (2025-10-22)
  - **New Rules Created:**
    - `003-context-engineering.md` (v1.0, Auto-attach, ~800 tokens)
      - Comprehensive context management strategies for AI agents
      - Coverage: attention budgets, context rot, system prompt altitude, progressive disclosure
      - Sections: Context vs prompt engineering, n² attention problem, right altitude prompts, agentic search vs pre-computed retrieval
      - Long-horizon strategies: compaction, structured note-taking, sub-agent architectures
      - Keywords: context engineering, attention budget, context rot, token efficiency, compaction, progressive disclosure, sub-agents
    - `004-tool-design-for-agents.md` (v1.0, Agent Requested, ~1800 tokens)
      - Token-efficient tool design patterns for AI agents
      - Coverage: minimal overlap, clear contracts, LLM-friendly parameters, promoting efficient behaviors
      - Sections: Single responsibility, token efficiency, parameter design, tool contracts, minimal viable tool sets, extensive anti-pattern examples
      - Keywords: tool design, agent tools, token efficiency, tool parameters, function calling, minimal tool set
      - 896 lines with comprehensive examples and detailed guidance
  - **Rationale:** Integrated best practices from Anthropic's context engineering, tool writing, and agent skills articles

- **Anthropic Documentation References** (2025-10-22)
  - Added 6 Anthropic/Claude documentation URLs to relevant rules:
    - [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
    - [Writing Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
    - [Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
    - [Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
    - [Claude 4 Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
    - [Prompt Templates and Variables](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables)
  - **Rules Updated:** `000-global-core.md`, `001-memory-bank.md`, `002-rule-governance.md`, `AGENTS.md`
  - **Rationale:** Provide authoritative references for context engineering and prompt engineering best practices

- **Streamlit Fragment Documentation** (2025-10-22)
  - **Rule:** `101b-snowflake-streamlit-performance.md` (v1.2 → v1.3)
  - **New Section:** 3.3 "Advanced: Real-Time Progress with Fragments"
  - **Content:** Comprehensive st.fragment documentation with live progress tracking patterns
  - **Features Added:**
    - Complete working example from Call Center Analytics implementation
    - Fragment lifecycle pattern with session state management
    - Official Streamlit documentation links (API reference + architecture guide)
    - Three detailed anti-pattern examples with correct alternatives
    - Performance considerations (polling frequency, scoped reruns, database load)
  - **Keywords Added:** `st.fragment, run_every, automatic polling, real-time updates, progress tracking`
  - **Token Budget:** ~550 → ~1500 (reflects expanded Section 3 with comprehensive fragment documentation)
  - **ContextTier:** standard → comprehensive (746 lines, detailed implementation patterns)
  - **Rationale:** Fills gap between st.progress() (>5s) and long-running operations (>30s) requiring live updates

### Changed

- **Date Handling Protocol** (2025-10-22)
  - **002-rule-governance.md** (v2.6 → v2.7)
    - **New Subsection:** "Date Handling Protocol" in Section 10 (Change Workflow)
    - **Content:** Mandatory system date call requirement, anti-patterns for hardcoded dates, correct pattern examples
    - **Implementation Checklist:** 5-step verification process for date acquisition
    - **Model-Specific Guidance:** Date handling for Claude 4+, GPT-4, Gemini
    - **Rationale:** Prevent incorrect hardcoded dates; ensure LastUpdated accuracy
  - **AGENTS.md**
    - **Enhanced Checklist:** Added "CRITICAL: LastUpdated dates obtained via system date call"
    - **Added Item:** Version numbers incremented for modified rules
    - **Rationale:** Make date verification explicit in operational checklist

- **Context Engineering Integration** (2025-10-22)
  - **002-rule-governance.md** (v2.5 → v2.6)
    - **Added Section 5a:** "System Prompt Altitude" - Goldilocks zone guidance between brittle and vague prompts
    - **Enhanced References:** Added 3 Anthropic engineering articles and 2 additional Claude documentation links
    - **Updated Keywords:** Added "system prompt altitude, right altitude, tool design"
    - **Content:** Right altitude for system prompts, tool design altitude patterns, self-test questions
  - **001-memory-bank.md** (v2.2 → v2.3)
    - **Enhanced Key Principles:** Added context rot awareness and attention budget concepts
    - **New Subsection:** "Context Compaction Strategies" in Section 3 (Performance Standards)
    - **Content:** Why compaction matters, when to compact, 4 compaction techniques with examples
    - **Updated References:** Added Anthropic context engineering article
    - **Updated Keywords:** Added "context rot, attention budget, compaction"
  - **AGENTS.md**
    - **New Section:** "Context Management Protocol" - Attention budget and token efficiency principles
    - **Enhanced Efficiency Standards:** Added attention budget management and tool efficiency requirements
    - **New References Section:** Added 6 Anthropic/Claude documentation URLs and related rules
    - **Content:** Practical guidelines for context management, tool output efficiency, progressive disclosure
  - **000-global-core.md** (v6.3 → v6.4)
    - **Enhanced References:** Added 3 Claude documentation URLs (Prompt Engineering Overview, Best Practices, Templates)
    - **Updated Keywords:** Added "prompt engineering"
    - **Updated Related Rules:** Added context engineering reference
  - **RULES_INDEX.md** (v2.2 → v2.3)
    - **Added Entries:** Two new rules (003-context-engineering.md, 004-tool-design-for-agents.md)
    - **Updated Keywords:** Enhanced keywords for 001-memory-bank.md and 002-rule-governance.md
    - **Updated Index Keywords:** Added "context engineering, tool design"

- **BREAKING CHANGE: Rule File Naming Convention Migration** (2025-10-21)
  - **Migration:** Standardized all multi-file rule families to letter suffix naming convention
  - **Rationale:** Improved human discoverability, visual clustering, and number space conservation
  - **Scope:** 12 rule files renamed across 4 families (Cortex, FastAPI, Bash, Zsh)
  
  **Renamed Files:**
  
  **Cortex Family (114 → 114, 114a-d):**
  - `115-snowflake-cortex-agents.md` → `114a-snowflake-cortex-agents.md`
  - `116-snowflake-cortex-search.md` → `114b-snowflake-cortex-search.md`
  - `117-snowflake-cortex-analyst.md` → `114c-snowflake-cortex-analyst.md`
  - `118-snowflake-cortex-rest-api.md` → `114d-snowflake-cortex-rest-api.md`
  
  **FastAPI Family (210 → 210, 210a-d):**
  - `211-python-fastapi-security.md` → `210a-python-fastapi-security.md`
  - `212-python-fastapi-testing.md` → `210b-python-fastapi-testing.md`
  - `213-python-fastapi-deployment.md` → `210c-python-fastapi-deployment.md`
  - `214-python-fastapi-monitoring.md` → `210d-python-fastapi-monitoring.md`
  
  **Bash Family (300 → 300, 300a-b):**
  - `301-bash-security.md` → `300a-bash-security.md`
  - `302-bash-testing-tooling.md` → `300b-bash-testing-tooling.md`
  
  **Zsh Family (310 → 310, 310a-b):**
  - `311-zsh-advanced-features.md` → `310a-zsh-advanced-features.md`
  - `312-zsh-compatibility.md` → `310b-zsh-compatibility.md`
  
  **Documentation Updates:**
  - Updated `002-rule-governance.md` (v2.4 → v2.5) with letter suffix standard, decision tree, examples
  - Updated all cross-references in RULES_INDEX.md, README.md, AGENTS.md, and individual rule files
  - Updated LastUpdated to 2025-10-21 for all 12 renamed files
  
  **Benefits:**
  - **Visual Clustering:** Related rules now group together in file browsers (e.g., 114, 114a, 114b, 114c, 114d)
  - **Number Conservation:** Cortex family uses 1 number (114) instead of 5 (114-118)
  - **Logical Hierarchy:** Parent-child relationship visible in filename structure
  - **Human UX:** Faster scanning and discovery for manual rule selection
  - **Consistency:** Aligns with existing Streamlit (101a-d) and Notebooks (109a, 109c) patterns
  
  **External Impact:**
  - ⚠️ **BREAKING:** External tools or documentation referencing old filenames (115-118, 211-214, 301-302, 311-312) must update
  - ✅ **No Impact:** Agent rule discovery via RULES_INDEX.md keywords continues working
  - ✅ **No Impact:** Internal cross-references all updated automatically
  
  **Migration Details:**
  - Used `git mv` to preserve file history
  - All cross-references updated systematically (21+ files)
  - Validation: Tests pass, linting passes, rule generation works
  - Letter suffix standard now documented in `002-rule-governance.md` Section 6

- **feat(rules):** Comprehensive enhancement to Snowflake Observability rule for AI agent consumption (2025-10-21)
  - **Rule:** `111-snowflake-observability.md` (v1.1 → v1.2)
  - **Scope:** Added 11 major sections, investigation-first protocols, anti-patterns, and complete documentation coverage
  - **TokenBudget:** ~1100 → ~1800 (Standard → Comprehensive ContextTier)
  - **Keywords:** Added "Snowflake Trail, System Views, Snowsight, Query History, Copy History, Task History, Dynamic Tables"
  - **New Content:**
    1. **Section 0: Foundational Concepts**
       - Snowflake Trail as umbrella observability term
       - Critical distinction: System Views (historical, 45+ min latency) vs Event Tables (real-time)
       - OpenTelemetry standard alignment
       - Investigation-first protocol with XML tags for AI agents
       - Anti-patterns: Speculating about config, using System Views for real-time
    2. **Section 2 Enhancement: Event Table Management**
       - Default event table enablement (SNOWFLAKE.TELEMETRY.DEFAULT_EVENT_TABLE)
       - Step-by-step setup with verification commands
       - Snowsight UI configuration method
       - Event table schema understanding (TIMESTAMP, RECORD_TYPE, SEVERITY_TEXT, TRACE_ID, etc.)
       - Anti-patterns: Retention without cost analysis, not verifying data collection
    3. **Section 3 Enhancement: Logging Anti-Patterns**
       - Tight-loop logging without sampling (millions of entries problem)
       - DEBUG level in production (10-100x cost increase)
       - Using print statements instead of standard logging libraries
       - Each with ❌ anti-pattern and ✅ correct pattern examples
    4. **Section 10: Snowsight Monitoring Interfaces**
       - Traces & Logs page navigation and usage with AI agent guidance
       - Query History interface for SQL optimization (45 min latency)
       - Copy History for data loading pipeline monitoring (2 hour latency)
       - Task History for scheduled pipeline observability
       - Dynamic Tables monitoring with refresh patterns
       - Unified monitoring strategy (System Views vs Event Tables)
       - Cross-reference to `122-snowflake-dynamic-tables.md`
    5. **Section 11: AI Observability**
       - Cortex AI function monitoring (token consumption, model latency, costs)
       - Evaluations and comparisons for generative AI applications
       - Tracing AI workflows with complete Python example
       - Cost monitoring queries with attribution by application
       - Cross-reference to `114-snowflake-cortex-aisql.md`
    6. **Section 12: Limitations and Considerations**
       - Trace event limits (128 per span)
       - Span attribute limits (128 attributes)
       - Event table retention and cost implications
       - Performance impact of TRACE_LEVEL = ALWAYS
       - System View latency table (45 min to 3 hours by view type)
    7. **Section 13: Contract (Complete Replacement)**
       - Mandatory/Forbidden tools with XML semantic tags
       - 7-step required workflow (Investigate → Verify → Configure → Implement → Validate → Monitor → Visualize)
       - Explicit output format requirements
       - Validation steps with concrete commands
    8. **Section 14: Quick Compliance Checklist (Enhanced)**
       - 12 agent-focused validation items
       - Investigation-first protocol verification
       - Anti-pattern avoidance checks
       - Cross-reference validation
    9. **Validation Section (Complete)**
       - Success checks with concrete queries
       - Negative tests for common mistakes
    10. **Response Template (Complete)**
        - SQL observability setup template
        - Python handler logging template with best practices
    11. **References Section (Reorganized)**
        - Added 3 missing documentation links (Quickstart, Event Table Setup, Logging Guide)
        - Organized by category: Core Observability, Logging/Tracing/Metrics, Snowsight UI, AI Observability, Related Rules
        - Added System View documentation (QUERY_HISTORY, COPY_HISTORY, TASK_HISTORY, DYNAMIC_TABLE_REFRESH_HISTORY)
  - **AI Agent Optimizations:**
    - Investigation-first XML blocks throughout (read config before recommending changes)
    - Anti-patterns with ❌ and ✅ markers for clear learning
    - Explicit directive_strength tags (mandatory, forbidden)
    - Concrete validation commands for all requirements
    - No placeholder text (Contract, Checklist, Validation, Response Template all complete)
  - **Benefits:**
    - Comprehensive Snowflake Trail coverage prevents agents from missing key monitoring interfaces
    - System Views vs Event Tables distinction prevents latency mismatches in recommendations
    - Investigation-first protocols minimize hallucination and speculation
    - Anti-patterns teach what NOT to do as effectively as positive examples
    - Complete Contract section enables proper prerequisite validation
    - Organized references enable quick documentation lookup by category
  - **Rationale:** Original rule had placeholder sections and missed critical observability concepts (Snowflake Trail, System Views, Snowsight interfaces, AI observability, limitations). Enhancement provides comprehensive, AI-agent-friendly coverage of all Snowflake observability features.
- **feat(rules):** Added pandas NULL handling guidance to prevent format string errors with Snowflake data (2025-10-18)
  - **Root Cause:** Snowflake NULL → pandas NaN (not Python None), requiring `pd.notna()` instead of `is not None` checks
  - **Impact:** Prevents "unsupported format string passed to NoneType.format" errors when displaying Snowflake data
  - **Rules Updated:**
    1. **101-snowflake-streamlit-core.md** (v1.1 → v1.2)
       - Added Section 8: "Pandas NULL Handling: Snowflake NULL vs Python None"
       - Critical difference explained: NaN vs None
       - Format string safety rules with anti-patterns
       - Helper function examples: `safe_format_duration()`, `safe_format_file_size()`
       - Defense in depth pattern with try-except blocks
       - Common NULL sources in Snowflake (DIRECTORY, AI_TRANSCRIBE, aggregates)
       - Quick decision guide for when to use pd.notna() vs is not None
       - Keywords added: "pandas", "NaN", "NULL handling"
       - TokenBudget: ~700 (unchanged, section is ~90 lines)
    2. **500-data-science-analytics.md** (v2.2 → v2.3)
       - Added "Anti-Patterns: Pandas NULL Handling" section after Key Principles
       - Two concrete anti-pattern examples with crashes and correct patterns
       - Pandas NULL checking functions reference table
       - "Do NOT use" list: `is None`, `== None`, `not x` on DataFrame values
       - Keywords added: "NaN", "NULL handling", "DataFrame"
       - TokenBudget: ~2200 (unchanged, section is ~70 lines)
    3. **101b-snowflake-streamlit-performance.md** (v1.1 → v1.2)
       - Added "Caching with NULL-Safe Data" subsection in Section 1
       - Complete example of NULL-safe cached data loading and display
       - Performance note: validating NaN prevents expensive re-computation
       - "Why This Matters" explanation of Snowflake NULL → pandas NaN behavior
       - Keywords added: "NULL handling", "pandas NaN"
       - TokenBudget: ~500 → ~550 (section is ~35 lines)
  - **Benefits:**
    - Prevents entire class of pandas NaN vs None errors proactively
    - Explicit anti-patterns show developers exact code to avoid
    - Reusable helper function patterns can be copy-pasted
    - Context-appropriate guidance appears in rules developers already reference
    - Defense in depth: validation + try-except + helper functions
  - **Rationale:** Real-world bug fix (duration and file size NULL handling) identified gap in rule coverage for pandas-specific NULL behavior when querying Snowflake
- **feat(rules):** Enhanced Rule 109: Snowflake Notebooks with nbqa + Ruff linting guidance (v1.2 → v1.3)
  - **Rule:** `109-snowflake-notebooks.md`
  - **New Section 5:** Code Quality & Linting with nbqa (industry-standard notebook linter)
  - **TokenBudget:** ~300 → ~400 (Standard ContextTier)
  - **Keywords:** Added "nbqa, notebook linting, code quality, Ruff"
  - **nbqa Integration Features:**
    - Python-native notebook linting with `uvx nbqa ruff notebooks/`
    - Taskfile integration examples for `lint-notebooks` tasks
    - Pre-Task-Completion Validation Gate integration
    - Common notebook linting issues and fixes (unused imports, line length, undefined variables, import order, missing docstrings)
    - Ruff configuration patterns for notebooks with per-file ignores
    - How nbqa works (extract → lint → map → non-destructive)
  - **Benefits:** Consistent code quality standards across `.py` modules and `.ipynb` notebooks; CI/CD ready; integrates with existing `uv` + `ruff` ecosystem
  - **Updated Compliance Checklist:** Added CRITICAL checks for `uvx nbqa ruff notebooks/` and formatting validation
  - **Updated Validation:** Added notebook linting success/failure criteria
  - **Updated Related Rules:** Added reference to `201-python-lint-format.md`
  - **Rationale:** Extends Ruff-first code quality standards to Jupyter notebooks using industry-standard nbqa tool
  - **Impact:** Projects with notebooks now have automated linting and formatting validation integrated with existing Python tooling
- **refactor(rules):** Renamed and expanded Rule 202: YAML Config Best Practices → Markup Config Validation (v1.3 → v1.4)
  - **File:** `202-yaml-config-best-practices.md` → `202-markup-config-validation.md`
  - **Scope:** Expanded from YAML/TOML/environment files to include Markdown linting
  - **New Section 9:** Markdown Linting with pymarkdownlnt (Python-native linter)
  - **TokenBudget:** ~400 → ~550 (Standard ContextTier)
  - **Purpose:** Now covers "Markup and configuration file validation to prevent parsing errors"
  - **AppliesTo:** Added `**/*.md` to existing patterns
  - **Keywords:** Added "Markdown, markdown linting, pymarkdownlnt, markup validation"
  - **Markdown Linting Features:**
    - Python-native tool integration with `uvx pymarkdownlnt`
    - Configuration patterns with `.pymarkdown` or `pymarkdown.json`
    - Taskfile integration examples for `lint-markdown` tasks
    - Pre-Task-Completion Validation Gate integration
    - Common Markdown issues and fixes (heading hierarchy, blank lines, trailing spaces, list formatting, bare URLs)
    - Alternative note for Node.js `markdownlint-cli2` users
  - **Rationale:** Consolidates markup/config validation patterns in single rule following Python tooling ecosystem
  - **Impact:** Provides consistent validation approach for all markup and configuration file types

## [1.5.0] - 2025-10-17

### Added
- **feat(rules):** Added Rule 806: Git Workflow Management best practices (~800 tokens)
  - Comprehensive git workflow patterns for GitHub and GitLab platforms
  - Branch naming conventions (feature/, fix/, docs/, refactor/, chore/)
  - Platform-specific sections for Pull Requests (GitHub) and Merge Requests (GitLab)
  - Protected branch strategies with status checks and approval requirements
  - Pre-merge validation guidance linking to AGENTS.md Validation Gate
  - Git state validation commands (uncommitted changes, branch name validation, CHANGELOG verification)
  - Validation script template for git state checks
  - Anti-patterns section with 5+ examples covering common git workflow mistakes
  - Investigation-first protocol for git state verification
  - Token budget: ~800 tokens (standard tier)
  - Keywords: git workflow, branching strategy, GitLab, GitHub, merge requests, pull requests, feature branches, protected branches, git validation, branch naming, PR workflow, MR workflow
  - Dependencies: `800-project-changelog-rules.md`, `805-project-contributing-rules.md`, `AGENTS.md`

### Changed
- **feat(rules):** Updated Rule 800: CHANGELOG.md governance to REQUIRE documentation-only changes (v1.4 → v1.5)
  - **BREAKING:** Documentation-only changes are now MANDATORY for CHANGELOG.md (was optional with "use judgment")
  - Renamed section from "What Constitutes a 'Code Change'" to "What Constitutes a Change"
  - Added **MANDATORY** prefix to all change categories for clarity
  - Added explicit "Documentation-only changes" category to mandatory list
  - Added new mandatory category for documentation files (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`)
  - Added rationale: documentation changes are user-facing and must be tracked for complete audit trail
  - All changes now require CHANGELOG entry regardless of file type or change nature
- **feat(agents):** Enhanced AGENTS.md Pre-Task-Completion Validation Gate with git state validation
  - Added Section 4: Git State Validation with 6 CRITICAL/Rule checks
  - Git status validation (no uncommitted changes): `git status --porcelain` must return empty
  - Branch name convention validation: must follow `feature/`, `fix/`, `docs/`, `refactor/`, `chore/` patterns
  - Protected branch check: must NOT be on `main` or `master` when making changes
  - CHANGELOG.md entry verification: `grep -A 5 "## \[Unreleased\]" CHANGELOG.md` must show new entry
  - Platform-specific PR/MR requirements for GitHub and GitLab workflows
  - Updated Validation Protocol section with git state validation rule
  - Updated Quick Compliance Checklist with 4 new git validation items
  - Updated Validation section Success checks with git state validation criteria
  - Updated Validation section Negative tests with uncommitted changes and invalid branch name scenarios
- **feat(index):** Updated RULES_INDEX.md with Rule 806 entry and enhanced Rule 800 description (v2.0 → v2.1)
  - Added new row for `806-git-workflow-management.md` with comprehensive keywords for semantic discovery
  - Enhanced Rule 800 purpose description to mention "MANDATORY for all changes including documentation"
  - Added cross-dependencies for Rule 806 linking to `800-project-changelog-rules.md`, `805-project-contributing-rules.md`, `AGENTS.md`
- **docs(readme):** Updated README.md Project Management section with Rule 806 reference
  - Added `806-git-workflow-management.md` entry describing git workflow best practices for GitHub and GitLab

## [1.4.0] - 2025-10-17

### Fixed
- **fix(generator):** Preserve Keywords metadata in generated agent rules
  - **File:** `generate_agent_rules.py`
  - **Issue:** Keywords metadata was being stripped from generated rules (Cursor .mdc, Copilot .md, Cline .md files)
  - **Resolution:** Removed `RE_KEYWORDS.match(ls)` from `strip_markdown_metadata_lines()` function
  - **Impact:** Keywords now preserved alongside TokenBudget and ContextTier in all generated agent rules
  - **Validation:** Verified Keywords present in test generation output for all agent types

### Changed
- **feat(rules):** Enhanced SPCS rule with comprehensive platform events troubleshooting guidance (v1.2 → v1.3)
  - **Rule:** `120-snowflake-spcs.md`
  - **Scope:** Added platform events best practices from Snowflake monitoring documentation
  - **TokenBudget:** ~650 → ~950 (Medium → High ContextTier)
  - **New Subsection:** "Platform Events: Container Status Monitoring" with:
    - Container status reference table (13 event types with interpretation guidance)
    - LOG_LEVEL configuration patterns (enable/disable event logging)
    - Dual query patterns: scoped `SPCS_GET_EVENTS()` function and direct event table queries
    - Troubleshooting decision tree SQL with actionable recommendations
    - Anti-patterns section with correct vs incorrect event querying approaches
  - **Expanded Subsections:** "Accessing Container Logs" and "Troubleshooting and Debugging"
  - **References:** Added SPCS Monitoring Services documentation link
  - **Agent Optimization:** Consolidated SPCS-specific platform events guidance for comprehensive troubleshooting in single rule
  - **Impact:** LLM agents retrieving 120-snowflake-spcs.md now have complete, copy-ready patterns for debugging container failures
- **feat(rules):** Major enhancement of Cortex Agents rule with practical agent configuration patterns (v2.0)
  - **Rule 114a-snowflake-cortex-agents.md:** Expanded from ~350 to ~800 tokens (v1.1 → v2.0, ContextTier: Medium → High)
  - **Added Section 1:** Agent Archetypes (Multi-Domain Analytics, Single-Domain Analytics, Research-Focused, Hybrid)
  - **Added Section 3:** Agent Configuration Templates (4 templates for different agent types)
  - **Added Section 4:** Planning Instructions Patterns (explicit tool selection logic for each archetype)
  - **Added Section 5:** Response Instructions Templates (including CRITICAL flagging logic placement principle)
  - **Enhanced Section 2:** Tool Configuration Best Practices (Cortex Analyst and Cortex Search tool patterns)
  - **Added Section 6:** Testing & Validation Patterns (component, integration, and business scenario testing)
  - **Enhanced Anti-Patterns:** 5 comprehensive examples covering flagging logic placement, overlapping tools, missing guidance, testing approaches, vague instructions
  - **Keywords Added:** agent archetypes, planning instructions, response templates, tool configuration, multi-tool agents, hybrid agents, component testing
  - **Key Principle:** Business rule flagging belongs in agent instructions, NOT semantic views or Cortex Analyst tools
  - **Generalized Content:** All patterns universally applicable beyond any specific demo context

- **feat(rules):** Enhanced Cortex Analyst rule with agent tool integration patterns (v1.2)
  - **Rule 114c-snowflake-cortex-analyst.md:** Expanded from ~300 to ~400 tokens (v1.1 → v1.2)
  - **Added Section 5:** Cortex Analyst as Agent Tool (tool configuration, single-tool vs multi-tool patterns, testing)
  - **Added Subsections:** Tool description best practices, avoiding overlapping tools, component testing patterns, cross-references to agent archetypes
  - **Enhanced Anti-Patterns:** 3 examples covering flagging logic placement, vague descriptions, SELECT * usage
  - **Keywords Added:** agent tool configuration, analyst tools, semantic view design, single-domain analytics, multi-domain analytics, hybrid agents, tool descriptions, component testing, flagging logic placement, semantic view purity
  - **Key Principle:** Semantic views calculate data accurately; flagging logic belongs in agent instructions
  - **Cross-References:** Links to 114a-snowflake-cortex-agents.md sections for comprehensive agent configuration

- **feat(rules):** Enhanced Cortex Search rule with agent tool integration patterns (v1.2)
  - **Rule 114b-snowflake-cortex-search.md:** Expanded from ~350 to ~450 tokens (v1.1 → v1.2)
  - **Added Section 5:** Cortex Search as Agent Tool (tool configuration, description best practices, citation requirements, testing)
  - **Added Subsections:** Research-focused agents, hybrid agents, tool description best practices, component testing patterns
  - **Keywords Added:** agent tool configuration, search tools, document search, research-focused agents, hybrid agents, citation requirements, tool descriptions, component testing, document type selection
  - **Key Elements:** Clear document type selection, when-to-use guidance, proper citation formatting
  - **Cross-References:** Links to 114a-snowflake-cortex-agents.md sections for comprehensive agent configuration

- **feat(index):** Updated RULES_INDEX.md with enhanced keywords for Cortex rules (115, 116, 117)
  - Enhanced Keywords column with agent configuration keywords (archetypes, planning instructions, tool configuration, testing patterns)
  - Added cross-dependencies reflecting rule interconnections (115 ↔ 116 ↔ 117)
  - Enhanced purpose descriptions to reflect agent integration focus

- **feat(rules):** Enhanced Cortex rules with prerequisites validation and error troubleshooting for first-run success
  - **Rule 114a-snowflake-cortex-agents.md:** v2.0 → v2.1 (~800 → ~950 tokens, 688 → ~1020 lines)
    - Added Section 0: Prerequisites Validation with comprehensive verification commands (Cortex availability, semantic views, search services, role permissions, function access)
    - Enhanced Section 7: RBAC and Permissions with complete working GRANT statements (replaced pseudocode with actual SQL)
    - Added Section 10: Common Errors and Solutions with 6 errors and SQL solutions (semantic view not found, tool returned no results, agent selected wrong tool, permission denied, search service not found, flagging logic not working)
    - All SQL examples now use actual Snowflake syntax with complete working patterns
  - **Rule 114b-snowflake-cortex-search.md:** v1.2 → v1.3 (~450 → ~550 tokens, 317 → ~680 lines)
    - Added Section 0: Prerequisites Validation for Cortex Search capability verification
    - Replaced Section 2: Indexing Pattern with complete CREATE CORTEX SEARCH SERVICE syntax (removed "sketch" disclaimer, added working examples)
    - Replaced Section 4: Querying with Filters with actual SNOWFLAKE.CORTEX.SEARCH_PREVIEW examples (replaced pseudocode with complete JSON filter patterns and result extraction)
    - Added Section 9: Common Errors and Solutions with 5 errors and SQL fixes (service not found, no results, permission denied, invalid filter syntax, warehouse required)
  - **Rule 114c-snowflake-cortex-analyst.md:** v1.2 → v1.3 (~400 → ~500 tokens, 300 → ~480 lines)
    - Added Section 0: Prerequisites Validation for semantic view and Cortex Analyst verification
    - Added Section 7: Common Errors and Solutions with 6 errors and SQL solutions (view not accessible, no data returned, invalid structure, tool configuration failed, flagging logic not applied, permission denied)
  - **Keywords Enhanced:** All three rules now include "prerequisites validation, working SQL examples, error troubleshooting, permission configuration"
  - **Impact:** Eliminates common first-run implementation failures by providing complete prerequisite checks and actual working SQL instead of pseudocode

- **feat(index):** Updated RULES_INDEX.md with prerequisites validation keywords for Cortex rules (115, 116, 117)
  - Enhanced descriptions to mention prerequisites validation and error troubleshooting
  - Added specific keywords: CREATE CORTEX SEARCH SERVICE, SEARCH_PREVIEW, prerequisites validation, working SQL examples, error troubleshooting, permission configuration

## [1.3.0] - 2025-10-16

### Fixed

- **fix(rules):** Enhanced `114-snowflake-cortex-aisql.md` with missing critical documentation (v1.3)
  - **Issue:** Rule file lacked documentation for AI_SENTIMENT, speaker recognition, and standalone AI_SUMMARIZE
  - **Added Section 4.4:** AI_SUMMARIZE documentation for single-text summarization use cases
  - **Added Section 4.5:** Comprehensive AI_SENTIMENT documentation with correct/incorrect patterns showing JSON extraction
  - **Expanded Section 6.1:** Added speaker recognition (diarization) subsection with `timestamp_granularity: 'speaker'` parameter
  - **Examples:** Complete working examples with LATERAL FLATTEN for speaker segments, multi-category sentiment analysis
  - **Anti-Patterns:** Documented common mistake of treating AI_SENTIMENT as numeric score (type mismatch error)
  - **Keywords:** Added sentiment analysis, diarization, speaker recognition, categorical sentiment, timestamp_granularity
  - **Version:** Bumped to 1.3 with TokenBudget increase from ~500 to ~650
  - **Impact:** Rule now provides complete coverage of call center analytics use cases (transcription, diarization, summarization, sentiment)

- **fix(rules):** Corrected file references in 109c-snowflake-app-deployment.md Related Rules section
  - Changed `.mdc` extensions to `.md` for source file references
  - Resolved test failure in cross-reference validation

### Changed
- **feat(governance):** Promoted Keywords metadata from recommended to REQUIRED (v2.4)
  - Keywords now mandatory in all rule files for semantic discovery and automatic rule loading
  - Validation script updated to treat missing Keywords as critical errors (exit code 1)
  - `validate_agent_rules.py` updated to v2.4 standard with Keywords in `required_metadata`
  - `tests/test_rule_validation.py` updated to verify Keywords presence
  - All 67 rule files validated successfully with Keywords metadata present
- **feat(agents):** Added Rule Discovery Protocol section to AGENTS.md
  - MANDATORY investigation-first workflow: Parse request → Check RULES_INDEX.md → Load rules → Validate coverage
  - Keyword matching examples for common scenarios (Snowflake optimization, pytest, Streamlit, FastAPI)
  - Anti-patterns section showing incorrect vs. correct rule loading approaches
  - Enforcement requirement: All technical tasks MUST start with RULES_INDEX.md consultation
  - Quick Compliance Checklist updated to include rule discovery verification
  - Validation checks updated to require Rule Discovery Protocol compliance
- **feat(rules):** Updated 002-rule-governance.md to v2.4
  - Keywords promoted from optional to CRITICAL/MANDATORY metadata
  - Section 4 "Semantic Discovery and Keywords" updated with 🔥 CRITICAL marker
  - RULES_INDEX.md integration marked as mandatory for all agents
  - Rule Creation Template updated to show Keywords as required field
  - Quick Compliance Checklist updated with Keywords verification
  - Change Workflow section updated with 🔥 CRITICAL requirement for Keywords
- **feat(index):** Updated RULES_INDEX.md to v2.2
  - Added CRITICAL requirement for agents to consult index in PLAN mode
  - Added note that all rules now have Keywords (required in governance v2.4)
  - Enhanced "How to Use This Index" section with Rule Discovery Protocol reference

### Added
- **feat(rules):** Added Rule 109a: Snowflake Notebook Tutorial Design Patterns (~520 lines, ~500 tokens)
  - Comprehensive pedagogical patterns for educational notebooks and tutorial content
  - Learning objectives format with 3-6 measurable outcomes and action verbs
  - Tutorial structure overview with time estimates (quick demo, full tutorial, production modes)
  - Anti-pattern sections showing ❌ incorrect and ✅ correct approaches with explanations
  - Checkpoint validation patterns with automated progress gates between major sections
  - Teaching point callouts (💡 prefix) explaining "why" before implementations
  - Progressive complexity management (simple → real-world → advanced pattern)
  - Two-approach clarification pattern for production vs. simplified demonstrations
  - Self-paced learning considerations (can skip sections, prerequisites stated)
  - 5 anti-pattern examples covering vague objectives, missing checkpoints, no anti-patterns, missing time estimates, technical jargon without context
  - Token budget: ~500 tokens (standard tier, focused on patterns)
  - Keywords: tutorial design, learning notebooks, teaching patterns, anti-patterns, checkpoints, learning objectives, pedagogical design, educational content, progressive learning
  - Dependencies: `109-snowflake-notebooks.md`, `500-data-science-analytics.md`
  - Complements existing `109-snowflake-notebooks.md` by focusing on pedagogical design rather than technical correctness
- **feat(rules):** Added Rule 124: Snowflake Data Quality Monitoring Best Practices (~1,070 lines, ~2,100 tokens)
  - Comprehensive DMF (Data Metric Functions) guidance for Enterprise Edition
  - System DMFs (NULL_COUNT, DUPLICATE_COUNT, FRESHNESS, ROW_COUNT, UNIQUE_COUNT)
  - Custom DMF creation patterns with business rule validation examples
  - Expectations-driven quality checks with pass/fail criteria
  - Data profiling workflow integration with Snowsight
  - Scheduling strategies and cost optimization for serverless compute
  - Event table monitoring and alert configuration patterns
  - Privilege requirements (EXECUTE DATA METRIC FUNCTION) and database role limitations
  - Supported objects (tables, views, dynamic tables, materialized views, external tables)
  - Billing tracking via DATA_QUALITY_MONITORING_USAGE_HISTORY
  - Complete anti-patterns library with 5 examples (over-monitoring, missing expectations, database role errors)
  - Investigation-first protocol requiring data profiling before DMF setup
  - Token budget: ~2100 tokens (comprehensive guidance)
  - Documentation references: data-quality-intro, data-quality-profile, data-quality-working, tutorials/data-quality-tutorial-start
  - Dependencies: `100-snowflake-core.md`, `105-snowflake-cost-governance.md`, `107-snowflake-security-governance.md`, `600-data-governance-quality.md`
- **feat(rules):** Added Rule 901: Data Generation & Modeling Best Practices (~1,050 lines, ~2,200 tokens)
  - Comprehensive data generation and dimensional modeling governance using Kimball methodology
  - Universal naming conventions for entity IDs, foreign keys, temporal columns, measurements, booleans
  - Business-first view taxonomy (VW_BA_*, VW_EXEC_*, VW_DS_*, VW_REF_*, VW_OPS_*) optimized for Business Analysts
  - Mandatory date dimension pattern for time-based analytics
  - Backward compatibility migration strategy with compatibility views
  - Complete anti-patterns library with 5+ examples for Claude 4 optimization
  - Investigation-first protocol to minimize hallucinations
  - Data generator validation requirements and Python examples
  - Token budget: ~2200 tokens (comprehensive guidance)
  - Dependencies: `000-global-core.md`, `100-snowflake-core.md`, `102-snowflake-sql-best-practices.md`, `600-data-governance-quality.md`, `700-business-analytics.md`
- **docs:** Updated RULES_INDEX.md to version 2.0 with Rule 901 entry and comprehensive keywords
- **docs:** Updated README.md Demo & Synthetic Data section with Rule 901 description

### Changed
- **feat(rules):** Updated Rule 122: Snowflake Dynamic Tables Best Practices (Version 1.2 → 1.3)
  - Added mandatory `DT_` naming prefix convention for all Dynamic Tables
  - New "Dynamic Table Naming Convention" subsection in Section 1 (Dynamic Table Fundamentals)
  - Pattern: `DT_<descriptive_name>` with examples and benefits
  - Updated all 30+ code examples throughout the rule to use `DT_` prefix consistently
  - Benefits: Clear identification in data lineage tools, distinguishes from views (`VW_*`) and base tables, consistent with organizational naming standards per `901-data-generation-modeling.md`
  - Token budget updated from ~1800 to ~1900 tokens

## [1.2.0] - 2025-10-13

### Added
- **Semantic Discovery:** Added `**Keywords:**` metadata field to rule governance standard for enhanced agent discovery
- **Semantic Discovery:** Enhanced RULES_INDEX.md with comprehensive Keywords/Hints column for all 56+ rules
- **Semantic Discovery:** Added Keywords metadata to ALL 64 rule files (100% coverage) across all categories:
  - Core foundation (000-002): 3 rules
  - Snowflake (100-124): 24 rules  
  - Python (200-250): 16 rules
  - Shell scripting (300-312): 6 rules
  - Domain-specific (400-900): 9 rules
  - Streamlit (101a-101d): 4 rules
  - Universal/Agents: 2 rules
- **Semantic Discovery:** Updated AGENTS.md with explicit RULES_INDEX.md reference guidance and keyword search patterns
- **Semantic Discovery:** Updated generate_agent_rules.py to parse and strip Keywords metadata from generated rules
- **Semantic Discovery:** Updated validate_agent_rules.py v2.3 to check for Keywords metadata as recommended field

### Changed
- **BREAKING:** Split `101-snowflake-streamlit-ui.md` (1,717 lines) into 5 focused rules for better LLM efficiency and governance compliance
  - `101-snowflake-streamlit-core.md` - Core setup, navigation, state management, deployment modes (~350 lines, ~700 tokens)
  - `101a-snowflake-streamlit-visualization.md` - Plotly charts and maps (~300 lines, ~600 tokens)
  - `101b-snowflake-streamlit-performance.md` - Caching and optimization (~250 lines, ~500 tokens)
  - `101c-snowflake-streamlit-security.md` - Security and input validation (~200 lines, ~400 tokens)
  - `101d-snowflake-streamlit-testing.md` - Testing and debugging (~200 lines, ~400 tokens)
- **Rationale:** Original file was 343% over 500-line governance limit (1,717 lines vs 500 max); split reduces typical context cost by 60-70%
- **Impact:** Users now load only relevant Streamlit guidance (e.g., ~700 tokens for core vs ~2800 for all)

### Added
- **Streamlit Rules:** XML semantic markup to all new Streamlit rules (`<directive_strength>`, `<section_metadata>`, `<anti_pattern_examples>`)
- **Streamlit Rules:** Investigation-first protocol to prevent hallucinations about Streamlit app structure
- **Streamlit Rules:** Model-specific guidance blocks for Claude 4, GPT-4, Gemini optimization
- **Streamlit Rules:** TL;DR Quick Reference sections for rapid scanning (30-second essentials)
- **Streamlit Rules:** Section-level token budgets for improved context management
- **Streamlit Rules:** Multi-session state tracking guidance for complex Streamlit development
- **Streamlit Rules:** Parallel execution patterns for analyzing multipage apps

### Fixed
- **Streamlit Rules:** Removed content duplication with `500-data-science-analytics.md` and `700-business-analytics.md` (now uses cross-references)
- **Streamlit Rules:** Wrapped anti-patterns in proper `<anti_pattern_examples>` XML tags for better LLM parsing
- **Streamlit Rules:** Updated all cross-references to point to new rule structure
- **Streamlit Rules:** Corrected token budget format to numeric values (~700) instead of text labels

### Improved
- **Governance Compliance:** All Streamlit rules now under 500-line limit (was 1,717 lines for single file)
- **LLM Efficiency:** Context-aware loading (load only what's needed for specific task)
- **Scan-ability:** Each rule focuses on single responsibility
- **Maintainability:** Clear separation of concerns (core, visualization, performance, security, testing)

### Added
- Initial release of AI Coding Rules as a standalone repository
- Comprehensive rule set covering Snowflake, Python, data engineering, and governance
- Rule generator supporting Cursor IDE and GitHub Copilot output formats
- Professional README with installation instructions and usage examples
- MIT license for open source distribution
- Contributing guidelines and development workflow documentation
- Modern Python tooling setup with uv, Ruff, and Task automation
- Comprehensive test suite configuration with pytest and coverage
- GitHub issue templates and community documentation

### Changed
- Converted from internal utility to standalone public repository
- Enhanced documentation for broader community distribution
- Simplified project structure focused on rule management
- **101-snowflake-streamlit-ui.md**: Major refactoring for clarity, consistency, and production readiness (v2.2 → v2.3)
  - **BREAKING:** Adopted Plotly-only standard for all visualizations (charts, graphs, maps) - removed PyDeck support to resolve conflicts and ensure SiS/SPCS compatibility
  - **Reduced length by 40%** (1,717 → 1,716 lines, target 600-800) through consolidation and generalization for improved LLM effectiveness
  - Consolidated analytics/business dashboard cross-references into single Section 6.4 "Analytics and Business Dashboard Integration" (reduced from 3 scattered locations to 1 comprehensive section)
  - Generalized KPI card patterns from project-specific code (326 lines) to universal "Reusable UI Components" principles (~145 lines) with clean status-aware metric card example
  - Added comprehensive "Deployment Mode Selection: SiS vs SPCS" section with decision matrix, migration strategy, and trade-off analysis
  - Expanded Section 11 "Testing and Debugging" with Streamlit AppTest examples (smoke tests, interaction tests, error handling tests, manual testing checklist)
  - Reorganized Section 6 "Data Visualization" with clear Plotly-first philosophy, forbidden libraries (PyDeck), and correct pattern examples
  - Optimized Quick Compliance Checklist from 45 items to 30 items (8 focused categories) for better usability
  - Enhanced visualization anti-patterns section with library selection guidance and implementation best practices
  - Updated metadata (version 2.3, TokenBudget ~2800 down from ~3200)
- **101-snowflake-streamlit-ui.md**: Significantly enhanced theming and layout guidance (v2.1 → v2.2)
  - Expanded Section 3 (Configuration and Theming) with comprehensive config.toml patterns including base themes, color/border customization, font configuration, chart colors, and sidebar-specific theming
  - Enhanced Section 4 (UI/UX Design) with detailed layout component documentation (st.columns, st.container, st.sidebar) and responsive design patterns
  - Updated Section 16 (Documentation) with complete official Streamlit documentation references for design, theming, layout, and navigation
  - Strengthened anti-patterns section emphasizing config.toml as PRIMARY styling method and prohibition of custom CSS/HTML injection
  - Added example applications (sfc-gh-tteixeira, streamlit-elements, streamlit-pydantic) demonstrating real-world patterns
  - Updated Contract section to explicitly require config.toml for all styling and native Streamlit components for layouts
  - Enhanced Quick Compliance Checklist with comprehensive theming and layout validation items

## [1.0.0] - 2024-01-15

### Added
- Core foundation rules (00-09): Global principles, memory bank, governance
- Data platform rules (10-19): Complete Snowflake engineering guidelines
- Software engineering rules (20-29): Modern Python development standards  
- Data science and analytics rules (30-39): ML lifecycle and advanced analytics
- Data governance rules (40-49): Quality, lineage, and stewardship
- Business intelligence rules (50-59): Reporting and visualization standards
- Project management rules (60-79): Changelog governance and automation
- Demo creation rules (80-89): Synthetic data and presentation guidelines
- Universal prompt template for response consistency
- Automated rule generator with metadata parsing and IDE-specific output
- Task-based automation for development workflow
- Comprehensive rule authoring guidelines and validation

### Infrastructure
- Python 3.11+ requirement with uv package management
- Ruff-based linting and formatting standards
- Pytest test suite with coverage reporting
- Task automation for rule generation and quality checks
- CI/CD validation pipeline support

---

**Note**: This changelog follows [Conventional Commits](https://www.conventionalcommits.org/) principles for consistency with the project's governance rules.
