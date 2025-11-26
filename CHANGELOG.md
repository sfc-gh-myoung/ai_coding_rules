# Changelog

All notable changes to the AI Coding Rules project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test coverage for `template_generator.py` (73% → 100%)
- Comprehensive test coverage for `index_generator.py` (83% → 100%)
- CLI formatting helper functions (`format_success_message`, `format_error_message`)
- 16 new integration and unit tests for template generator CLI execution paths
- 9 new tests for index generator covering error handling, auto-detection, and edge cases
- Enhanced test docstrings explaining validation purpose and edge case coverage
- Dynamic footer generation with complete dependency chain trees in RULES_INDEX.md

### Changed
- **BREAKING:** RULES_INDEX.md is now 100% dynamically generated (no header/footer preservation)
- Removed `preserve_header` parameter from `generate_rules_index()` function
- Simplified index generation logic with new `generate_footer()` helper function
- Improved docstring formatting across all scripts (multiline to single line)
- Enhanced test documentation for better maintainability and understanding

### Deprecated

### Removed

### Fixed

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

[Unreleased]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.6.1...v3.0.0
[2.6.1]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.6.0...v2.6.1
[2.6.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.5.1...v2.6.0
[2.5.1]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.5.0...v2.5.1
[2.5.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.4.2...v2.5.0
[2.4.2]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.4.1...v2.4.2
[2.4.1]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.3.2...v2.4.0
[2.3.2]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.3.1...v2.3.2
[2.3.1]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.2.2...v2.3.0
[2.2.2]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.2.1...v2.2.2
[2.2.1]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/Snowflake-Labs/ai_coding_rules/compare/v1.0.0...v1.5.0
[1.0.0]: https://github.com/Snowflake-Labs/ai_coding_rules/releases/tag/v1.0.0
