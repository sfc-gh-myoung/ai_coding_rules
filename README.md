# AI Coding Rules

[![License: Apache 2.0](https://img.shields.io/badge/License-APACHE-yellow.svg)](https://opensource.org/license/apache-2-0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Task](https://img.shields.io/badge/Task-Taskfile-brightgreen)](https://taskfile.dev)

> **Universal AI coding rules for consistent, reliable software engineering across LLMs and IDEs**

This repository provides a comprehensive collection of engineering rules designed to work seamlessly with AI coding assistants including Claude, ChatGPT, GitHub Copilot, Cursor, and others. The rules cover everything from Python and SQL best practices to data engineering, analytics, and project governance.

This project was inspired by: [how-to-add-cline-memory-bank-feature-to-your-cursor](https://forum.cursor.com/t/how-to-add-cline-memory-bank-feature-to-your-cursor/67868) and [cline memory bank](https://docs.cline.bot/prompting/cline-memory-bank)

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended: install via [uv](https://github.com/astral-sh/uv))
- **Task** (recommended: install via `brew install go-task/tap/go-task` or [other methods](https://taskfile.dev/installation/))

### Installation

```bash
# Clone the repository
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
cd ai_coding_rules

# Set up development environment
task deps:dev

# Generate IDE-specific rule files
task rule:cursor    # For Cursor IDE
task rule:copilot   # For GitHub Copilot
```

### Basic Usage

#### Option 1: Direct Rule Usage
Open any `.md` rule file directly in your IDE and follow the directive language (`Requirement`, `Always`, `Avoid`, `Rule`, `Consider`).

#### Option 2: Generate IDE-Specific Rules
```bash
# Generate Cursor project rules
task rule:cursor
# Creates .cursor/rules/*.mdc files

# Generate GitHub Copilot instructions  
task rule:copilot
# Creates .github/instructions/*.md files

# Manual generation with options
uv run generate_agent_rules.py --agent cursor --dry-run
uv run generate_agent_rules.py --agent copilot --check
```

#### Option 3: System Prompt Integration
Concatenate selected `.md` files for use with LLM tools like Claude Projects, ChatGPT custom instructions, or other AI coding assistants.

## 📁 Rule Categories

### Core Foundation (00-09)
- **`00-global-core.md`** — Universal operating principles and safety protocols
- **`01-cursor-memory-bank.md`** — Project memory management for AI assistants  
- **`02-cursor-rules-governance.md`** — Comprehensive rule authoring governance: creation standards, naming conventions, structure requirements, and validation workflows

#### Universal Rule Authoring Best Practices

The following best practices apply to all AI coding assistants and development environments:

**Structure Standards**
- Use a single `#` H1 title for each rule file
- Keep rules focused and concise (target 150-300 lines, max 500 lines)
- Split large topics into multiple composable rules
- Include clear metadata at the top with description and scope

**Content Guidelines**  
- Use explicit directive language: `Requirement`, `Always`, `Avoid`, `Rule`, `Consider`
- Avoid content duplication across rules; reference other files instead
- Include links to current, relevant documentation for validation
- Provide practical examples and usage patterns

**Naming & Organization**
- Use snake-case naming with `.md` extension (e.g., `my_rule_name.md`)
- Place universal rules in the canonical directory structure
- Group related rules by domain/technology (10-19 for Snowflake, 20-29 for Python, etc.)
- Use consistent numbering for logical ordering

**Scope Management**
- Keep rule scope tightly focused on specific domains or technologies
- Prefer on-demand (Agent Requested) pattern over auto-attach for specialized rules
- Only global core rules should auto-attach universally
- Design rules to be composable and reusable across projects

**Validation & Maintenance**
- Test rules with multiple AI models and development environments
- Verify syntax, best practices, and API usage against current documentation
- Regularly update rules to reflect evolving best practices
- Remove outdated content and consolidate overlapping guidance

### Data Platform - Snowflake (10-19)
- **`10-snowflake-core.md`** — Core Snowflake guidelines (SQL, performance, security)
- **`11-snowflake-streamlit-ui.md`** — Modern Streamlit application development
- **`12-snowflake-sql-best-practices.md`** — Advanced SQL authoring patterns
- **`13-snowflake-performance-tuning.md`** — Query optimization and warehouse tuning
- **`14-snowflake-streams-tasks.md`** — Incremental data pipelines
- **`15-snowflake-cost-governance.md`** — Cost optimization and resource management
- **`16-snowflake-semantic-views.md`** — Layered data modeling architecture
- **`17-snowflake-security-governance.md`** — Security policies and access control
- **`18-snowflake-data-loading.md`** — Data ingestion best practices
- **`19-snowflake-notebooks.md`** — Jupyter notebook standards

### Software Engineering - Python (20-29)
- **`20-python-core.md`** — Modern Python engineering with `uv` and Ruff
- **`21-python-lint-format.md`** — Code quality and formatting standards

### Data Science & Analytics (30-39)
- **`30-data-science-analytics.md`** — ML lifecycle, feature engineering, and analytics

### Data Governance (40-49)  
- **`40-data-governance-quality.md`** — Data quality, lineage, and stewardship

### Business Intelligence (50-59)
- **`50-business-analytics.md`** — Business-oriented reporting and visualization

### Project Management (60-79)
- **`60-changelog-rules.md`** — Changelog governance using Conventional Commits
- **`65-contributing-rules.md`** — Contribution workflow and PR standards
- **`70-taskfile-automation.md`** — Project automation with Taskfile

### Demo & Synthetic Data (80-89)
- **`80-demo-creation.md`** — Realistic demo application development

### Templates
- **`universal_prompt.md`** — Universal response guidelines template

## 🔧 Rule Generator Architecture

The project includes a sophisticated rule generator (`generate_agent_rules.py`) that transforms universal Markdown rules into IDE-specific formats:

### Supported Output Formats

| IDE/Tool | Output Format | Location | Features |
|----------|---------------|----------|----------|
| **Cursor** | `.mdc` files | `.cursor/rules/` | YAML frontmatter with globs, auto-apply |
| **GitHub Copilot** | `.md` files | `.github/instructions/` | YAML frontmatter with appliesTo patterns |

### Metadata Parsing

Rules support embedded metadata in Markdown:

```markdown
**Description:** Brief description of the rule's purpose
**Applies to:** `**/*.py`, `**/*.sql` (file patterns)  
**Auto-attach:** true (automatically apply rule)
**Version:** 2.0
**Last updated:** 2024-01-15
```

## 🧠 Memory Bank System

The Memory Bank is a project-level documentation system that enables AI assistants to maintain context and continuity across sessions. Since AI assistants reset their memory between sessions, the Memory Bank serves as the critical link for understanding project state, decisions, and ongoing work.

### Overview

The Memory Bank addresses a fundamental challenge in AI-assisted development: **memory reset between sessions**. When an AI assistant starts a new session, it has no knowledge of previous work, decisions, or project context. The Memory Bank solves this by maintaining a structured set of documentation files that capture:

- **Project foundation** — Core requirements, goals, and scope
- **System architecture** — Technical decisions and design patterns  
- **Current context** — Active work, recent changes, and next steps
- **Development progress** — What works, what's left to build, known issues

### File Structure

The Memory Bank uses a hierarchical structure with required core files:

```
memory-bank/
├── projectbrief.md      # Foundation document (project scope & goals)
├── productContext.md    # Why project exists, problems solved
├── systemPatterns.md    # Architecture & technical decisions  
├── techContext.md       # Technologies, setup, constraints
├── activeContext.md     # Current work focus & recent changes
├── progress.md          # Status, what works, known issues
└── [additional]/        # Optional: features, APIs, testing docs
```

#### Core Files (Required)

| File | Purpose |
|------|---------|
| `projectbrief.md` | Foundation document defining core requirements and project scope |
| `productContext.md` | Business context: why project exists, problems solved, user experience goals |
| `systemPatterns.md` | System architecture, key technical decisions, design patterns |
| `techContext.md` | Technologies used, development setup, technical constraints |
| `activeContext.md` | Current work focus, recent changes, next steps, active decisions |
| `progress.md` | Current status, what works, what's left to build, known issues |

### Memory Bank Commands

#### Initialization
For new projects, create the memory bank structure:

```bash
# Create memory bank directory
mkdir memory-bank

# Initialize core files (manual creation)
touch memory-bank/{projectbrief,productContext,systemPatterns,techContext,activeContext,progress}.md
```

#### Update Commands
The Memory Bank updates automatically during development, triggered by:

1. **Explicit user request**: `"update memory bank"`
2. **After significant changes**: Major feature implementations or architectural decisions
3. **Context clarification needs**: When project understanding requires documentation
4. **Pattern discovery**: New technical patterns or workflow insights

### Workflow Integration

#### Plan Mode Workflow
```mermaid
flowchart TD
    Start[New Session] --> Read[Read ALL Memory Bank Files]
    Read --> Check{Files Complete?}
    Check -->|No| Plan[Create Missing Files]
    Check -->|Yes| Context[Verify Current Context]
    Context --> Strategy[Develop Work Strategy]
    Strategy --> Present[Present Approach to User]
```

#### Act Mode Workflow  
```mermaid
flowchart TD
    Start[Execute Task] --> Context[Check Memory Bank]
    Context --> Work[Perform Development Work]
    Work --> Document[Update Documentation]
    Document --> Rules[Update IDE Rules if Needed]
    Rules --> Complete[Mark Task Complete]
```

### Usage Examples

#### Starting a New Session
```bash
# AI assistant workflow (automatic)
1. Read all memory-bank/*.md files
2. Understand current project state  
3. Review activeContext.md for recent work
4. Check progress.md for known issues
5. Proceed with informed context
```

#### Updating Memory Bank
```bash
# User command
"update memory bank"

# AI assistant workflow (automatic)
1. Review ALL memory bank files
2. Update current state in activeContext.md
3. Record progress in progress.md  
4. Document new patterns in systemPatterns.md
5. Update technical context if needed
```

#### Best Practices

- **Always read**: Memory Bank files at session start (non-optional)
- **Update frequently**: After major changes or discoveries
- **Keep current**: Focus on activeContext.md and progress.md
- **Be precise**: Accuracy directly impacts work effectiveness
- **Stay organized**: Use additional files for complex features

## 🎯 Key Features

- **🔄 Universal Compatibility** — Works with Claude, ChatGPT, Copilot, Cursor, and more
- **📋 Structured Directive Language** — Clear `Requirement`, `Always`, `Avoid` patterns  
- **🏗️ Modular Architecture** — Mix and match rules by domain/technology
- **🤖 Auto-Generation** — Transform universal rules into IDE-specific formats
- **📊 Data-Focused** — Comprehensive coverage of data engineering and analytics
- **🛡️ Production-Ready** — Battle-tested patterns for reliability and performance

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-new-rule`
3. **Follow** the rule authoring guidelines in `02-rules-governance.md`
4. **Test** your changes: `task lint` and `task rule:cursor --dry-run`
5. **Submit** a pull request

### Rule Authoring Guidelines

- Use standard Markdown headings (`#`, `##`, `###`) for structure
- Use explicit directive words: `Requirement`, `Always`, `Avoid`, `Rule`, `Consider`
- Keep rules focused and under 500 lines
- Include relevant documentation links
- Test with the rule generator before submitting

## 📋 Development Commands

```bash
# Environment setup
task deps:dev              # Install development dependencies
task uv:pin               # Pin Python version and create venv

# Code quality
task lint                 # Check code with Ruff
task format              # Check formatting
task lint:fix            # Auto-fix linting issues
task format:fix          # Apply formatting

# Rule generation
task rule:cursor         # Generate Cursor rules
task rule:copilot        # Generate Copilot rules

# Utilities  
task clean_venv          # Remove virtual environment
task -l                  # List all available tasks
```

## 🔍 IDE Integration Examples

### Cursor IDE
```bash
task rule:cursor
# Rules appear in Cursor's AI context automatically
# Configure via .cursor/rules/*.mdc files
```

### GitHub Copilot
```bash  
task rule:copilot
# Add repository instructions to GitHub
# Configure via .github/instructions/*.md files
```

### Claude Projects
Add selected `.md` rule files to your Claude project knowledge base for consistent code generation.

### VS Code Extensions
Use the generated `.md` files with VS Code AI extensions or copy content for custom instructions.

## 📊 Compatibility Matrix

| LLM/Tool | Direct Rules | Generated Rules | Status |
|----------|--------------|-----------------|--------|
| **Claude (API/Web)** | ✅ Markdown | ➖ Native | Full Support |
| **Gemini (API/Web)** | ✅ Markdown | ➖ Native | Full Support |
| **ChatGPT** | ✅ Markdown | ➖ Native | Full Support |
| **GitHub Copilot** | ➖ Limited | ✅ Instructions | Full Support |
| **Cursor** | ✅ Markdown | ✅ .mdc Rules | Full Support |
| **Cline/Claude Dev** | ✅ Markdown | ➖ Native | Full Support |

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git/issues)  
- **Discussions**: [GitHub Discussions](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git/discussions)
- **Documentation**: All rules include links to official documentation

## 🗺️ Roadmap

- [ ] **Multi-language Support** — Rules for Go, JavaScript, Rust
- [ ] **Cloud Platform Rules** — AWS, Azure, GCP best practices  
- [ ] **Framework-Specific Rules** — FastAPI, Django, React patterns
- [ ] **IDE Plugin Development** — Native integrations beyond file generation
- [ ] **Community Rule Registry** — User-contributed specialized rules

---

<p align="center">
  <strong>Built for the AI-powered development era</strong><br>
  Consistent • Reliable • Production-Ready
</p>
