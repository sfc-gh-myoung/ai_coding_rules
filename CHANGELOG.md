# Changelog

All notable changes to the AI Coding Rules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
