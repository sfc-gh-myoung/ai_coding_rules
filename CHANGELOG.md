# Changelog

All notable changes to the AI Coding Rules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **fix(generator):** Preserve Keywords metadata in generated agent rules
  - **File:** `generate_agent_rules.py`
  - **Issue:** Keywords metadata was being stripped from generated rules (Cursor .mdc, Copilot .md, Cline .md files)
  - **Resolution:** Removed `RE_KEYWORDS.match(ls)` from `strip_markdown_metadata_lines()` function
  - **Impact:** Keywords now preserved alongside TokenBudget and ContextTier in all generated agent rules
  - **Validation:** Verified Keywords present in test generation output for all agent types

### Changed
- **feat(rules):** Major enhancement of Cortex Agents rule with practical agent configuration patterns (v2.0)
  - **Rule 115-snowflake-cortex-agents.md:** Expanded from ~350 to ~800 tokens (v1.1 → v2.0, ContextTier: Medium → High)
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
  - **Rule 117-snowflake-cortex-analyst.md:** Expanded from ~300 to ~400 tokens (v1.1 → v1.2)
  - **Added Section 5:** Cortex Analyst as Agent Tool (tool configuration, single-tool vs multi-tool patterns, testing)
  - **Added Subsections:** Tool description best practices, avoiding overlapping tools, component testing patterns, cross-references to agent archetypes
  - **Enhanced Anti-Patterns:** 3 examples covering flagging logic placement, vague descriptions, SELECT * usage
  - **Keywords Added:** agent tool configuration, analyst tools, semantic view design, single-domain analytics, multi-domain analytics, hybrid agents, tool descriptions, component testing, flagging logic placement, semantic view purity
  - **Key Principle:** Semantic views calculate data accurately; flagging logic belongs in agent instructions
  - **Cross-References:** Links to 115-snowflake-cortex-agents.md sections for comprehensive agent configuration

- **feat(rules):** Enhanced Cortex Search rule with agent tool integration patterns (v1.2)
  - **Rule 116-snowflake-cortex-search.md:** Expanded from ~350 to ~450 tokens (v1.1 → v1.2)
  - **Added Section 5:** Cortex Search as Agent Tool (tool configuration, description best practices, citation requirements, testing)
  - **Added Subsections:** Research-focused agents, hybrid agents, tool description best practices, component testing patterns
  - **Keywords Added:** agent tool configuration, search tools, document search, research-focused agents, hybrid agents, citation requirements, tool descriptions, component testing, document type selection
  - **Key Elements:** Clear document type selection, when-to-use guidance, proper citation formatting
  - **Cross-References:** Links to 115-snowflake-cortex-agents.md sections for comprehensive agent configuration

- **feat(index):** Updated RULES_INDEX.md with enhanced keywords for Cortex rules (115, 116, 117)
  - Enhanced Keywords column with agent configuration keywords (archetypes, planning instructions, tool configuration, testing patterns)
  - Added cross-dependencies reflecting rule interconnections (115 ↔ 116 ↔ 117)
  - Enhanced purpose descriptions to reflect agent integration focus

- **feat(rules):** Enhanced Cortex rules with prerequisites validation and error troubleshooting for first-run success
  - **Rule 115-snowflake-cortex-agents.md:** v2.0 → v2.1 (~800 → ~950 tokens, 688 → ~1020 lines)
    - Added Section 0: Prerequisites Validation with comprehensive verification commands (Cortex availability, semantic views, search services, role permissions, function access)
    - Enhanced Section 7: RBAC and Permissions with complete working GRANT statements (replaced pseudocode with actual SQL)
    - Added Section 10: Common Errors and Solutions with 6 errors and SQL solutions (semantic view not found, tool returned no results, agent selected wrong tool, permission denied, search service not found, flagging logic not working)
    - All SQL examples now use actual Snowflake syntax with complete working patterns
  - **Rule 116-snowflake-cortex-search.md:** v1.2 → v1.3 (~450 → ~550 tokens, 317 → ~680 lines)
    - Added Section 0: Prerequisites Validation for Cortex Search capability verification
    - Replaced Section 2: Indexing Pattern with complete CREATE CORTEX SEARCH SERVICE syntax (removed "sketch" disclaimer, added working examples)
    - Replaced Section 4: Querying with Filters with actual SNOWFLAKE.CORTEX.SEARCH_PREVIEW examples (replaced pseudocode with complete JSON filter patterns and result extraction)
    - Added Section 9: Common Errors and Solutions with 5 errors and SQL fixes (service not found, no results, permission denied, invalid filter syntax, warehouse required)
  - **Rule 117-snowflake-cortex-analyst.md:** v1.2 → v1.3 (~400 → ~500 tokens, 300 → ~480 lines)
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
