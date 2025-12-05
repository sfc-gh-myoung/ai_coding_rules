# Changelog

All notable changes to the AI Coding Rules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.2.0] - 2025-12-04

### Added
- `600-golang-core.md` — New Go/Golang core rule establishing 600s range for systems/backend languages (99 → 100 rules)
  - Project structure patterns (`cmd/`, `internal/`, `pkg/`)
  - Error handling with `fmt.Errorf` and `%w` wrapping
  - Interface design ("accept interfaces, return structs")
  - Testing patterns (table-driven tests, race detection)
  - Concurrency fundamentals (context, goroutines, channels)
  - Tooling integration (`go fmt`, `go vet`, `golangci-lint`)
- `ty` type checker integration as primary Python type checker (Astral toolchain)
  - New Section 4.3 in `200-python-core.md` — Type Checking with ty
  - `uvx ty check .` added to mandatory Pre-Task-Completion Validation Gate
  - ty configuration example in `203-python-project-setup.md`
  - Taskfile pattern with `lint-ty` task in `201-python-lint-format.md`
- Systems/Backend Languages domain established (600-699 range) for future Go rules

### Changed
- Consolidated `117-snowflake-cortex-analyst.md` content into semantic views and agents rules
  - Prerequisites validation moved to `106-snowflake-semantic-views-core.md`
  - Error troubleshooting moved to `106c-snowflake-semantic-views-integration.md`
  - Agent tool testing patterns moved to `115-snowflake-cortex-agents-core.md`
  - Updated all cross-references from deleted rule to appropriate destinations
- `200-python-core.md` — Added ty as primary type checker, mypy as fallback; updated keywords, validation gate, command patterns
- `201-python-lint-format.md` — Updated Taskfile example to include ty type checking task
- `203-python-project-setup.md` — Added `[tool.ty]` configuration example alongside mypy
- `106-snowflake-semantic-views-core.md` — Documented verified queries DDL limitation with Anti-Pattern 5, YAML workaround example, and cross-references to Cortex Analyst integration rules
- Renamed HTMX rules to resolve 220 numbering conflict (220-python-typer-cli.md keeps 220):
  - `220-python-htmx-core.md` → `221-python-htmx-core.md`
  - `221-python-htmx-templates.md` → `221a-python-htmx-templates.md`
  - `222-python-htmx-flask.md` → `221b-python-htmx-flask.md`
  - `223-python-htmx-fastapi.md` → `221c-python-htmx-fastapi.md`
  - `224-python-htmx-testing.md` → `221d-python-htmx-testing.md`
  - `225-python-htmx-patterns.md` → `221e-python-htmx-patterns.md`
  - `226-python-htmx-integrations.md` → `221f-python-htmx-integrations.md`
- Updated all Depends and Related Rules references for renamed HTMX files
- README.md and docs/ARCHITECTURE.md updated to reflect 100 rules and new Go domain

### Removed
- `117-snowflake-cortex-analyst.md` — Content redistributed to reduce overlap with semantic views rules
- mypy retained as fallback type checker for projects requiring mypy plugins

### Fixed
- v3.0 schema validation errors in `204-python-docs-comments.md` (37 CRITICAL emoji violations, 1 HIGH keyword count violation)

## [3.1.0] - 2025-12-03

### Added
- 8 new HTMX rules for building hypermedia-driven web applications (92 → 100 total rules, later reduced to 99 via consolidation)
  - `221-python-htmx-core.md` — Request/response lifecycle, HTTP headers, security patterns, HATEOAS
  - `221a-python-htmx-templates.md` — Jinja2 template organization, partials, fragments, conditional rendering
  - `221b-python-htmx-flask.md` — Flask-HTMX extension integration, blueprints, authentication patterns
  - `221c-python-htmx-fastapi.md` — FastAPI async patterns with HTMX, dependency injection, background tasks
  - `221d-python-htmx-testing.md` — Pytest fixtures, header assertions, HTML validation, mocking strategies
  - `221e-python-htmx-patterns.md` — Common patterns: CRUD, forms, infinite scroll, search, real-time, modals
  - `221f-python-htmx-integrations.md` — Frontend library integrations (Alpine.js, _hyperscript, Tailwind, Bootstrap, Chart.js)
  - `500-frontend-htmx-core.md` — Pure frontend HTMX reference (attributes, events, CSS transitions, debugging)
- Python domain expanded from 15 to 23 rules (+8 HTMX rules)
- Frontend/Containers domain expanded from 4 to 5 rules (+1 HTMX frontend rule)
- Comprehensive HTMX rule coverage across Flask, FastAPI, testing, templates, and frontend integration
- HTMX section added to README.md with detailed rule descriptions
- New rule `441-react-backend.md` for React + Python backend integration patterns
- Python (FastAPI/Flask) as organizational default backend for React applications
- Next.js API routes as lightweight option for simpler APIs
- Comprehensive test coverage for `template_generator.py` (73% → 100%)
- Comprehensive test coverage for `index_generator.py` (83% → 100%)
- Comprehensive test coverage for `badge_updater.py` (0% → 100%, 32 new tests)
- Comprehensive test coverage for `rule_deployer.py` (90% → 98%, 6 new tests)
- Overall project test coverage increased from 89% to 96%
- CLI formatting helper functions (`format_success_message`, `format_error_message`)
- 16 new integration and unit tests for template generator CLI execution paths
- 9 new tests for index generator covering error handling, auto-detection, and edge cases
- 32 new tests for badge updater covering version extraction, test percentage calculation, badge updating, and edge cases
- 6 new tests for rule deployer covering file validation, copy failures, deployment errors, and CLI argument logic
- Enhanced test docstrings explaining validation purpose and edge case coverage
- Dynamic footer generation with complete dependency chain trees in RULES_INDEX.md

### Changed
- README.md updated to reflect new rule counts
- Rule Categories table updated with HTMX coverage in Python and Frontend domains
- RULES_INDEX.md regenerated with new HTMX rule entries and keywords
- Established consistent naming pattern: `python-htmx-*.md` for all HTMX-related rules
- Restructured `440-react-core.md` for v3.0 schema compliance (section ordering, checklist naming)
- Softened Zustand recommendation to acknowledge Redux Toolkit for complex enterprise apps
- Added Next.js default export exception to forbidden section in React rules
- Removed model-specific "Claude 4 Guidance" sections from React rules (not durable)
- Added error-focused keywords to React rule metadata for better discovery
- **BREAKING:** RULES_INDEX.md is now 100% dynamically generated (no header/footer preservation)
- Removed `preserve_header` parameter from `generate_rules_index()` function
- Simplified index generation logic with new `generate_footer()` helper function
- Improved docstring formatting across all scripts (multiline to single line)
- Enhanced test documentation for better maintainability and understanding

### Deprecated

### Removed

### Fixed
- Import errors in `test_deployment.py` (changed `deploy_rules` → `rule_deployer` after script rename)
- Import errors in `test_update_token_budgets.py` (corrected module path for `token_validator`)
- Whitespace in blank lines across test files (auto-fixed by ruff format)
- Deprecated `IOError` alias replaced with `OSError` in test files (ruff UP024)
- Formatting inconsistencies in 2 test files (auto-fixed by ruff format)

### Security

## [3.0.0] - 2025-11-25

### Added
- Phase 4 assessment report with 97.7% token compliance and validation metrics
- Schema-based validation system with 556-line YAML schema
- Comprehensive test suite with 91 passing tests for all Python scripts
- Audit scripts for keyword, section order, and contract field compliance
- Example prompt templates in prompts/ directory with 3 real-world patterns
- Comprehensive prompts/README.md guide with keyword reference and best practices
- "Example Prompts" section in main README.md linking to prompt templates
- Production-ready rule system with 87 rules in `rules/` directory
- Simplified deployment script with agent-agnostic `--dest` flag
- Comprehensive migration guide (MIGRATION.md)
- Test suite for deployment and validation scripts

### Changed
- **BREAKING:** Removed template generation system in favor of production-ready rules
- **BREAKING:** Simplified deployment to agent-agnostic `--dest` flag workflow
- **BREAKING:** Removed `--agent` flag from deployment script
- **BREAKING:** Removed agent-specific deployment paths
- Updated 800-project-changelog.md to align with Keep a Changelog v1.1.0
- Fixed section ordering issues in 7 rules (92% to 93% compliance)
- Completed Contract fields for 4 rules (100% compliance achieved)
- Renamed sections across 87 rules for schema compliance
- Reduced keyword counts in 43 rules for better semantic discovery (50.6% to 96.6% compliance)
- Enhanced schema with clearer section names and quality requirements
- Relaxed schema constraints (line 160 limit removed, Essential Patterns minimum 3 instead of 6-7)
- Updated rule validator defaults to `rules/` directory for v3.0 architecture
- Updated AGENTS.md and RULES_INDEX.md to project root
- Updated README.md for v3.0 architecture
- Promoted TokenBudget and ContextTier to required metadata

### Removed
- Template-based generation workflow (`templates/`, `generated/`, `discovery/` directories)
- Generation scripts (`scripts/generate_agent_rules.py`, `scripts/index_generator.py`)
- Agent-specific deployment paths (`.cursor/rules/`, `.clinerules/`, etc.)
- 443 lines of obsolete template-based tests from test suite
- `scripts/validate_rules.py` wrapper script
- Template generation commands and workflow
- Agent-specific formats
- Placeholder substitution system

### Fixed
- Metadata validation errors reporting incorrect "Version" and "LastUpdated" requirements
- Missing pytest fixtures causing 5 test failures
- Linting issues across Python files (RUF001, E402, SIM117)
- Cursor deployment extension handling (.md to .mdc conversion)
- Validation warnings in 53 rule templates
- Metadata validation duplicate initialization

## [2.6.1] - 2025-11-22

### Changed
- Template compliance enhancements across 12 rule templates
- Standardized Quick Start TL;DR headers to consistent format
- Improved boilerplate compliance from 87.2% to 87.5%

### Added
- Rule validator improvements with markdown-aware parser
- Context-aware section validation with SectionHierarchy class
- Flexible Contract placement validation with graduated thresholds

### Fixed
- Zero false positives from template examples in validation

## [2.6.0] - 2025-11-21

### Added
- 12 new rules covering Python, data science, business analytics, and project management
- Best practices documentation templates (README, CONTRIBUTING, CHANGELOG)
- Automation rules for Taskfile-based workflows

### Changed
- Enhanced 2 existing rules with additional content and examples
- Improved validator output formatting with section grouping

## [2.5.1] - 2025-11-20

### Fixed
- Customer temporary table handling for empty result sets
- Rule content audit warnings in 10 templates
- Token budget calculations for large rule files

## [2.5.0] - 2025-11-20

### Added
- Advanced semantic view rules for Snowflake Cortex Analyst
- Git workflow and contribution guidelines
- Rule governance and metadata standards

### Changed
- Reorganized rule structure with split rules pattern
- Enhanced metadata requirements with ContextTier field

## [2.4.2] - 2025-11-19

### Fixed
- Schema validation errors in 15 rule templates
- Section ordering in core foundation rules

## [2.4.1] - 2025-11-19

### Fixed
- Token budget overruns in Streamlit performance rules
- Missing Contract sections in 8 rules

## [2.4.0] - 2025-11-18

### Added
- Streamlit performance optimization patterns
- SPCS deployment and troubleshooting rules
- Python testing and pytest best practices

### Changed
- Split large rules into focused subtopic files (101a/b/c, 106a/b, 109a/b/c)

## [2.3.2] - 2025-11-17

### Fixed
- Validation script handling of optional metadata fields
- Test suite compatibility with Python 3.11+

## [2.3.1] - 2025-11-17

### Fixed
- Rule deployment script path resolution
- Missing imports in validation utilities

## [2.3.0] - 2025-11-16

### Added
- Docker best practices and multi-stage build patterns
- Shell scripting standards (Bash and Zsh)
- Python CLI development rules (Typer, Click)

### Changed
- Enhanced Quick Start TL;DR sections with checklist format

## [2.2.2] - 2025-11-15

### Fixed
- Metadata parsing errors for rules with complex YAML
- Token budget validator accuracy for markdown tables

## [2.2.1] - 2025-11-15

### Fixed
- Rule validator handling of code blocks in Anti-Patterns sections
- False positives in Contract field validation

## [2.2.0] - 2025-11-14

### Added
- Python linting and formatting standards (Ruff)
- Documentation and docstring conventions
- Package management rules (UV, Poetry)

### Changed
- Updated all Python rules to use UV for dependency management

## [2.1.0] - 2025-11-13

### Added
- Snowflake Streamlit core patterns and state management
- Cortex Agent creation and optimization rules
- Semantic model best practices

### Changed
- Enhanced Snowflake core rules with additional SQL patterns

## [2.0.0] - 2025-11-12

### Added
- Schema-driven rule validation framework
- Rule boilerplate template (002a)
- Automated token budget calculation

### Changed
- **BREAKING:** Migrated to v2.0 metadata schema
- **BREAKING:** Required Contract XML tags in all rules
- Reorganized rule numbering system by domain prefix

### Removed
- Legacy v1.x placeholder format
- Deprecated auto-attach mechanism

## [1.5.0] - 2025-11-10

### Added
- Initial rule governance framework
- Template-based rule generation system
- Agent-specific deployment formats

## [1.0.0] - 2025-11-01

### Added
- Initial release with 25 core rules
- Basic validation scripts
- Documentation templates

[Unreleased]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v3.2.0...HEAD
[3.2.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.6.1...v3.0.0
[2.6.1]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.6.0...v2.6.1
[2.6.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.5.1...v2.6.0
[2.5.1]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.5.0...v2.5.1
[2.5.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.4.2...v2.5.0
[2.4.2]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.4.1...v2.4.2
[2.4.1]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.3.2...v2.4.0
[2.3.2]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.3.1...v2.3.2
[2.3.1]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.2.2...v2.3.0
[2.2.2]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.2.1...v2.2.2
[2.2.1]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/compare/v1.0.0...v1.5.0
[1.0.0]: https://github.com/sfc-gh-myoung/ai_coding_rules/releases/tag/v1.0.0
