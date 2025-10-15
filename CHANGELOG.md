# Changelog

All notable changes to the AI Coding Rules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
