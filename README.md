# AI Coding Rules

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/license/apache-2-0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Task](https://img.shields.io/badge/Task-Taskfile-brightgreen)](https://taskfile.dev)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Snowflake-Labs/ai_coding_rules)
[![GitLab](https://img.shields.io/badge/GitLab-Repository-orange?logo=gitlab)](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules)

> **One universal rule set for all AI assistants, IDEs, and agents — portable, intelligent, and IDE-agnostic**

## Quick Overview

**What:** 84 specialized engineering rules for AI coding assistants  
**Works with:** Any AI assistant, IDE, or agent (Cursor, Claude, ChatGPT, GitHub Copilot, Cline)  
**Deploy:** 3 commands, works immediately  
**Benefit:** Consistent, high-quality AI-assisted development

**Quick Checklist:**
- [ ] Python 3.11+ and Task installed? → See [Prerequisites](#prerequisites)
- [ ] Ready to deploy? → See [Quick Start](#quick-start)
- [ ] Want to understand first? → See [Understanding Rules](#understanding-rules)
- [ ] Contributing? → See [Contributing](#contributing)

## Overview

This repository provides a **universal-first rule system** designed to work seamlessly with any AI assistant, IDE, or development tool. Write rules once in a universal format, use them everywhere.

**What you get:** A comprehensive collection of 84 engineering rules covering Python, SQL, Snowflake, Docker, Shell scripting, data engineering, analytics, and project governance. The rules work seamlessly with AI coding assistants including Claude, ChatGPT, GitHub Copilot, Cursor, and others.

**Important:** Some aspects of the rules are opinionated, particularly regarding naming conventions, project structure, usage of uv/ruff/Task, and documentation standards. You are **encouraged to review and adjust** the rules to align with your best practices or preferred approaches.

## Key Features

- **📚 84 Specialized Rules** — Comprehensive coverage across Snowflake, Python, Docker, Shell scripting, and project management
- **🔄 Universal Format** — Write once, use everywhere: Cursor, VS Code, Claude, ChatGPT, GitHub Copilot, and more
- **🤖 Intelligent Discovery** — AI assistants automatically find and load relevant rules using semantic keyword matching
- **🎯 Dependency-Aware** — Explicit dependency chains ensure rules load in the correct order
- **⚡ Token-Efficient** — Modular, focused rules (150-500 lines) minimize context window usage
- **🔓 No Lock-In** — Standard Markdown with embedded metadata works with any tool or custom integration

This project was inspired, in part, by:

- [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [how-to-add-cline-memory-bank-feature-to-your-cursor](https://forum.cursor.com/t/how-to-add-cline-memory-bank-feature-to-your-cursor/67868)
- [cline memory bank](https://docs.cline.bot/prompting/cline-memory-bank)

<details>
<summary><h3>Universal Format Philosophy (Click to expand)</h3></summary>

The rule system is built on a template-first architecture: 84 source templates in `templates/` generate portable rules that work with any tool, IDE, or AI assistant.

**Key Features:**

- **Any AI Assistant**: Claude, GPT, Gemini, custom agents
- **Any IDE**: Cursor, VS Code, IntelliJ, JetBrains, Vim
- **Any Tool**: CLI tools, scripts, custom integrations
- **No lock-in**: Standard Markdown with semantic metadata

**Core Principles:**

1. **Template-First Design**: Source templates in `templates/` directory → Generate to `generated/` outputs
2. **Generate Once, Use Everywhere**: Run `task generate:rules:universal` to create portable rules
3. **Automatic Rule Discovery**: AI assistants use `AGENTS.md` and `RULES_INDEX.md` (deployed to project root) for semantic keyword matching
4. **Dependency-Aware Architecture**: Explicit dependency chains ensure correct rule loading order
5. **Token-Efficient Design**: Modular, focused rules (150-500 lines) minimize context usage
6. **Technology Coverage**: 84 specialized rules covering Snowflake, Python, Docker, Shell scripting, and project management
7. **Auto-Generated Catalog**: `RULES_INDEX.md` automatically generated from template metadata and deployed to project root

**What This Repository Provides:**

- **84 source templates** in `templates/` directory covering best practices, patterns, and governance
- **Universal format** in `generated/universal/` with preserved metadata (Keywords, TokenBudget, ContextTier, Depends)
- **Discovery system** files (deployed to project root):
  - `AGENTS.md` - Discovery guide used by AI assistants to locate and load rules
  - `RULES_INDEX.md` - Auto-generated catalog with semantic keywords
- **IDE-specific formats** in `generated/` for Cursor, Copilot, Cline
- **Automated generation pipeline** with validation and CI checks

**Who Should Use This:**

- **Developers** working with AI coding assistants who want consistent, high-quality guidance
- **Teams** seeking to standardize AI-assisted development practices across multiple IDEs
- **Organizations** implementing AI coding standards with version control
- **Tool Builders** creating AI-powered development environments
- **Contributors** wanting to extend or customize rules for their domain

</details>

## Table of Contents

**For Users:**
- [Quick Overview](#quick-overview)
- [Overview](#overview)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Understanding Rules](#understanding-rules)
- [Rule Selection Guide](#rule-selection-decision-tree)
- [Rule Categories](#rule-categories)
- [AI Configuration](#ai-configuration)
- [Document Map](#document-map-what-to-read-first)
- [Troubleshooting](#troubleshooting)
- [Compatibility Matrix](#compatibility-matrix)
- [License](#license)

**For Contributors:**
- [Contributing](#contributing)
- [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)
- [Project Structure](#project-structure)
- [Development Commands](#development-commands)

## Document Map: What to Read First

This repository contains multiple documentation files for different audiences:

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Project overview, setup, usage | Start here (you are here) |
| **docs/ONBOARDING.md** | Team onboarding guide | When setting up for your team |
| **CONTRIBUTING.md** | Development guidelines, PR process | When contributing rules |
| **docs/ARCHITECTURE.md** | System architecture, design decisions | When understanding internals or extending |
| **docs/MEMORY_BANK.md** | Memory Bank system for long-running projects | When using Memory Bank (optional) |
| **CHANGELOG.md** | Version history, changes | When checking updates |
| **Taskfile.yml** | Build automation reference | When running tasks |

### AI Assistant Configuration

During deployment, the system automatically configures two files that enable AI assistants to discover and load rules:

- **AGENTS.md** - Discovery guide used by AI assistants to locate and load rules
- **RULES_INDEX.md** - Searchable catalog of all available rules with keywords

These files are deployed to your project root automatically and require no manual configuration.

### Generated Outputs (Use These)

| Directory | Format | Use With |
|-----------|--------|----------|
| **generated/universal/** | Clean Markdown | Any IDE, LLM, or agent |
| **generated/cursor/rules/** | .mdc files | Cursor IDE |
| **generated/copilot/instructions/** | .md with YAML | GitHub Copilot |
| **generated/cline/** | Plain .md | Cline AI |

**Quick Decision**:

- **New to the project?** → See [Team Onboarding](docs/ONBOARDING.md)
- **Just want to use rules?** → See [Quick Start](#quick-start)
- **Want to modify rules?** → See [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)
- **Want to configure your AI?** → See [AI Configuration](#ai-configuration)
- **Want to understand the system?** → See [Architecture](docs/ARCHITECTURE.md)

## Prerequisites

Before getting started, ensure you have:

- **Python 3.11+** — [Download Python](https://www.python.org/downloads/)
- **Task** — Automation tool: [Installation guide](https://taskfile.dev/installation/)
- **Git** — For cloning repository: [Install Git](https://git-scm.com/downloads)
- **Optional: uv** — Python package manager (automatically installed by Task if missing)

**Quick check:**

```bash
python --version  # Should show 3.11 or higher
task --version    # Should show Task version
git --version     # Should show Git version
```

## Quick Start

**Choose your path:**

- 🚀 **Use rules in your project** → See [Deployment](#deployment-recommended) below
- 🛠️ **Modify or contribute** → See [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)
- 📹 **Watch first** → [Video: Overview](https://youtu.be/IhkfZwmkQyM) | [Demo](https://youtu.be/YOGxwtTWBCI)

### Deployment (Recommended)

**Get started in 3 commands:**

```bash
# 1. Clone this repository (choose one)
# GitLab:
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
# GitHub:
git clone https://github.com/Snowflake-Labs/ai_coding_rules.git

cd ai_coding_rules

# 2. Explore available commands (categorized for easy discovery)
task    # Shows organized task list with quickstart section

# 3. Deploy rules to your project
task deploy:universal DEST=~/my-project   # Works with any IDE/LLM
```

**That's it!** Your project now has 84 specialized rules ready to use. Run `task` anytime to see categorized commands with quickstart section—30% faster task discovery through logical grouping.

**What just happened?**
- Generated rules for your environment
- Copied to `rules/` directory (or IDE-specific location like `.cursor/rules/`)
- Created `AGENTS.md` and `RULES_INDEX.md` for automatic AI discovery
- Ready to use immediately—no additional configuration needed!

**Next Steps:**
- ✅ Deployment complete → [Configure Your AI](#ai-configuration)
- 🤔 Want to understand how rules work → [Understanding Rules](#understanding-rules)
- 🔧 Need different format → Continue reading deployment options below

#### Full Deployment Options

Choose the format that matches your tools:

#### Option A: Universal Format

```bash
task deploy:universal DEST=~/my-project   # For any IDE/LLM (most portable)
```

#### Option B: IDE-Specific Formats

```bash
task deploy:cursor DEST=~/my-project      # For Cursor IDE
task deploy:copilot DEST=~/my-project     # For GitHub Copilot
task deploy:cline DEST=~/my-project       # For Cline
```

#### Deploy to Current Directory

```bash
cd ~/my-project
task deploy:universal  # No DEST needed
```

**What happens:**
- Generates rules for your target agent/IDE
- Copies to correct location (`.cursor/rules/`, `rules/`, `.github/copilot/instructions/`, `.clinerules/`)
- Updates `AGENTS.md` with proper paths for your agent (replaces `{rule_path}` template variable)
- Updates `RULES_INDEX.md` with correct paths and file extensions for your agent
- Both files configured to point AI assistants to the correct rule locations
- Ready to use immediately!

#### Option C: Git Submodule (Version Tracking)

Track rule updates via git submodule:

```bash
# From your project root (choose one)
# GitLab:
git submodule add https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git .ai-rules
# GitHub:
git submodule add https://github.com/Snowflake-Labs/ai_coding_rules.git .ai-rules
cd .ai-rules
task deploy:universal DEST=..   # Deploy to parent project

# Update rules later
cd .ai-rules && git pull && task deploy:universal DEST=..
```

#### Option D: Deployment Without Task

If you don't have Task installed, use the Python deployment script directly:

```bash
# Clone the rules repository (choose one)
# GitLab:
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git /tmp/ai-rules
# GitHub:
git clone https://github.com/Snowflake-Labs/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules

# Install Python dependencies
/opt/homebrew/bin/uv sync

# Deploy using Python script (handles everything automatically)
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project

# Verify deployment
ls ~/my-project/rules/*.md | wc -l  # Should show 84
ls ~/my-project/AGENTS.md ~/my-project/RULES_INDEX.md  # Both files should exist
```

**For other formats:**

```bash
# Cursor
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent cursor --destination ~/my-project

# Copilot
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent copilot --destination ~/my-project

# Cline
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent cline --destination ~/my-project
```

**What the script does automatically:**

- Generates rules for the specified agent type
- Copies rules to the correct directory (`.cursor/rules/`, `rules/`, etc.)
- Configures `AGENTS.md` with correct paths (replaces `{rule_path}` template variable)
- Updates `RULES_INDEX.md` with correct paths and file extensions (e.g., `.mdc` for Cursor)
- Configures discovery files so AI assistants can locate rules automatically
- No manual `sed` or path editing needed!

#### Verify Setup

```bash
# Check rules are present (universal deployment)
ls rules/*.md | wc -l  # Should show 84

# Or for Cursor
ls .cursor/rules/*.mdc | wc -l  # Should show 84
```

**Success!** Your AI assistant can now access 84 specialized rules. See [AI Configuration](#ai-configuration) for IDE-specific setup.

### For Rule Maintainers (Contributing to Rules)

**This section and those following are for developers who want to modify or contribute rules.**  
If you're using the rules in your project, setup is complete. See [Troubleshooting](#troubleshooting) for support.

**Want to modify or contribute rules?** Follow this development setup:

#### Prerequisites

- **Python 3.11+** — Required for running generation scripts
- **uv** — Fast dependency management ([install guide](https://github.com/astral-sh/uv))
- **Task** — Simplified commands ([install guide](https://taskfile.dev/installation/))

#### Setup

```bash
# Clone the repository (choose one)
# GitLab:
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
# GitHub:
git clone https://github.com/Snowflake-Labs/ai_coding_rules.git

cd ai_coding_rules

# Set up Python environment
task env:deps

# Generate all rule formats
task generate:rules:all
```

#### Project Structure

See [Project Structure](#project-structure) section below for full details.

**Quick Overview:**

- `templates/` — 84 source template files (edit these)
- `discovery/` — Rule loading protocol and catalog
- `generated/` — IDE-ready outputs (auto-generated, don't edit)
- `scripts/` — Generation and deployment tools

#### Development Workflow

```bash
# 1. Edit templates
vi templates/200-python-core.md

# 2. Generate outputs
task generate:rules:all            # All formats
task generate:rules:universal      # Just universal
task generate:index         # Regenerate RULES_INDEX.md (in discovery/ dir of this repo)

# 3. Validate
task validate:ci            # Runs linting, tests, and checks

# 4. Test locally
# Copy generated/universal/ to a test project and verify

# 5. Commit
git add templates/ discovery/
git commit -m "feat: update Python core rules"
```

#### Common Tasks

```bash
# Generate specific formats
task generate:rules:cursor         # Cursor IDE format
task generate:rules:copilot        # GitHub Copilot format
task generate:rules:cline          # Cline format
task generate:rules:universal      # Universal format

# Regenerate rule index
task generate:index         # Generate RULES_INDEX.md (in discovery/ dir of this repo)

# Validate everything
task validate:ci            # Lint, test, and check staleness

# Check if outputs are stale
task generate:rules:universal:check
task generate:index:check

# Clean generated files
task maintenance:clean:generated
```

#### Verification Checklist

**After making changes:**

- [ ] Edit source files in `templates/`
- [ ] Run `task generate:rules:all` to regenerate
- [ ] Run `task generate:index` to update catalog
- [ ] Run `task validate:ci` to verify quality
- [ ] Test with actual AI assistant
- [ ] Commit `templates/`, `discovery/`, and `generated/` directories

**What NOT to commit:**

- ❌ `.venv/` or Python cache files
- ❌ IDE-specific settings (unless intentional)
- ❌ Temporary test directories

#### Testing Your Changes

```bash
# Option 1: Validate with task suite
task validate:ci

# Option 2: Manual testing with AI assistant
# Use task commands to generate and deploy to a test directory
mkdir ~/test-rules
task generate:rules:all  # Generate rules first
task deploy:universal DEST=~/test-rules  # Deploy to test location

# Point your AI assistant to ~/test-rules/ and verify behavior
```

**Success Indicators:**
- ✅ `task validate:ci` passes all checks
- ✅ `generated/universal/` contains 84 rule files
- ✅ `RULES_INDEX.md` (in test directory) lists all rules with metadata
- ✅ AI assistant can load and apply rules correctly
- ✅ No linting errors in templates

**See also:** [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed contribution guidelines.

## Understanding Rules

### What Are AI Coding Rules?

AI coding rules are structured Markdown files that guide AI assistants on how to write code, following best practices and patterns for specific technologies.

**Key Concepts:**
- **Universal Format:** Write once, use everywhere (any IDE, LLM, or agent)
- **Automatic Discovery:** AI finds relevant rules based on your task keywords
- **Dependency-Aware:** Rules load prerequisites automatically in correct order
- **Token-Efficient:** Small, focused rules (150-500 lines each) minimize context usage

### How Automatic Discovery Works

When you deploy rules to your project, AI assistants can automatically find and load the right ones:

1. **You deploy** rules to your project → `task deploy:universal DEST=~/my-project`
2. **AI reads** `AGENTS.md` (loading protocol) and `RULES_INDEX.md` (catalog) from your project root
3. **AI searches** keywords in `RULES_INDEX.md` matching your task description
4. **AI loads** relevant rules following their dependency chains automatically
5. **AI applies** rules to generate code according to best practices

**Example workflow:**
```
User: "Build a Snowflake Streamlit dashboard"

AI discovers and loads:
  1. 000-global-core (foundation - always first)
  2. 100-snowflake-core (SQL patterns - dependency)
  3. 101-snowflake-streamlit-core (Streamlit patterns)
  
AI generates code following all three rule sets.
```

### Why Smaller, Focused Rules?

This project uses **modular, topic-focused rules** instead of large monolithic files. This design significantly improves both LLM accuracy and context efficiency.

**Benefits:**
- **Better LLM Accuracy:** Clear signal-to-noise ratio, reduced conflicting guidance, precise pattern matching
- **Context Efficiency:** Load only what's needed (~300-600 tokens per rule vs ~4000+ for monoliths)
- **Easier Maintenance:** Update one focused file instead of searching through thousands of lines
- **Better Composability:** Mix and match rules for your specific tech stack

**Example:** For a Snowflake data engineering project:
- Load: `100-snowflake-core` (500 tokens) + `104-snowflake-streams-tasks` (400 tokens) + `121-snowflake-snowpipe` (2000 tokens)
- **Total: ~3400 tokens** of highly relevant, focused guidance
- Alternative: One "Data Engineering Monolith" would be 5000+ tokens with irrelevant Spark/Airflow content

## Rule Selection Decision Tree

```ascii
┌─────────────────────────────────────────────────┐
│         Start: What are you building?           │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┴─────────────┬─────────────────┬──────────────┐
    ▼                           ▼                 ▼              ▼
┌─────────┐            ┌──────────────┐   ┌─────────────┐  ┌──────────┐
│Snowflake│            │Python App    │   │Infrastructure│  │General   │
└────┬────┘            └──────┬───────┘   └──────┬──────┘  └────┬─────┘
     │                        │                   │              │
     ├─SQL/Pipeline           ├─FastAPI           ├─Docker       │
     │ └►100-snowflake-core   │ └►210-fastapi     │ └►400-docker └►000-global-core
     │                        │                   │
     ├─Streamlit              ├─Flask             ├─Shell/Bash
     │ └►101-snowflake-streamlit-core   │ └►250-python-flask       │ └►300-bash-scripting-core
     │   +101a (viz)          │                   │
     │   +101b (perf)         ├─CLI Tool          └─CI/CD
     │   +101c (security)     │ └►220-python-typer-cli         └►806-git-workflow-management
     │                        │
     ├─Notebooks/ML           └─Data Science
     │ └►109-notebooks          └►500-data-science
     │
     └─AI/ML Features
       └►114-cortex-aisql
         +114a (agents)
         +114b (search)

Loading Order (Follow Dependencies):
1. Always load 000-global-core first
2. Load domain foundation (100-snowflake, 200-python, etc.)
3. Load specialized rules based on task
4. Check Depends field and load prerequisites
```

### How the Decision Tree Works

1. **Identify your primary technology** (Snowflake, Python, Infrastructure, etc.)
2. **Select your use case** within that technology
3. **Start with the recommended base rule** 
4. **Follow the dependency chain** using the Depends metadata
5. **Add specialized rules** as needed for specific features

### Example Loading Sequences

**Snowflake Streamlit Dashboard:**

```ascii
000-global-core (foundation)
└── 100-snowflake-core (SQL patterns)
    └── 101-snowflake-streamlit-core (app basics)
        ├── 101a-streamlit-visualization (if using charts)
        └── 101b-streamlit-performance (if optimizing)
```

**Python FastAPI with Testing:**

```ascii
000-global-core (foundation)
└── 200-python-core (Python basics)
    ├── 210-python-fastapi-core (API framework)
    │   └── 210a-fastapi-security (if auth needed)
    └── 206-python-pytest (testing patterns)
```

## System-Wide Script (gen-rules.sh)

Install the `gen-rules.sh` wrapper script to deploy/generate rules from anywhere on your system.

**Pure Shell/Python implementation - no Task dependency required.**

**Installation:**

```bash
# From the ai_coding_rules directory
cp gen-rules.sh ~/bin/gen-rules
chmod +x ~/bin/gen-rules
# Ensure ~/bin is in your PATH
```

**Basic Usage:**

```bash
# Generate rules (recommended - works with any IDE/LLM)
cd /path/to/my-project
gen-rules generate universal          # Generate to current directory
gen-rules generate cursor             # Generate Cursor rules
gen-rules generate all                # Generate all formats

# Deploy rules (copies generated rules to appropriate locations)
gen-rules deploy universal            # Deploy to rules/
gen-rules deploy cursor               # Deploy to .cursor/rules/
gen-rules deploy copilot              # Deploy to .github/copilot/instructions/
gen-rules deploy cline                # Deploy to .clinerules/

# Specify destination
gen-rules generate universal ~/my-project
gen-rules deploy universal /custom/path

# Preview changes (dry run)
gen-rules generate universal --dry-run

# Check if rules are current
gen-rules generate universal --check
```

**Advanced Options:**

```bash
gen-rules --help                      # Show full usage
gen-rules --version                   # Show version
gen-rules --verbose generate cursor   # Verbose output
gen-rules --debug generate all        # Debug mode
gen-rules --project ~/my-rules generate cursor  # Override project dir

# Run validation
gen-rules validate                    # Validate all rules

# Check project status
gen-rules status                      # Show project info
```

**Features:**

- ✅ **Task-free**: Pure shell/Python implementation, no Task dependency
- ✅ Production-ready with comprehensive error handling
- ✅ Works from any directory
- ✅ Flexible configuration via flags or environment variables
- ✅ Debug support for troubleshooting
- ✅ Meaningful exit codes (0-4)
- ✅ Simple command structure: `generate`/`deploy`/`validate`/`status`

See `gen-rules --help` for complete documentation.

## Project Structure

```ascii
ai_coding_rules/
├── templates/              ← Edit these: 84 source template files
├── discovery/              ← Discovery system sources (AGENTS.md, RULES_INDEX.md)
├── generated/              ← Generated outputs (committed to git)
│   ├── universal/          ← Universal format (portable Markdown)
│   ├── cursor/rules/       ← Cursor-specific (.mdc files)
│   ├── copilot/instructions/ ← GitHub Copilot format
│   └── cline/              ← Cline format
├── scripts/                ← Generation and deployment tools
├── docs/                   ← Documentation
└── tests/                  ← Test suite
```

**Key Concepts:**
- **templates/** — Source of truth, always edit here (never in `generated/`)
- **discovery/** — AI assistant discovery guide and rule catalog
- **generated/** — IDE-ready outputs, regenerated via `task generate:rules:all`
- **scripts/** — `generate_agent_rules.py` (generation), `deploy_rules.py` (deployment)

**Workflows:**

```bash
# For users: Deploy rules
task deploy:universal DEST=~/my-project

# For contributors: Edit and regenerate
vim templates/200-python-core.md
task generate:rules:all
git add templates/ generated/ && git commit -m "feat: update Python rules"
```

## Rule Categories

The 84 rules are organized by domain using a three-digit numbering system. Each category focuses on a specific technology or practice area.

| Domain | Range | # Rules | Focus Area | Key Topics |
|--------|-------|---------|------------|------------|
| **Core Foundation** | 000-099 | 6 | Universal patterns | Operating principles, memory bank, rule governance, boilerplate template, context engineering, tool design |
| **Snowflake** | 100-199 | 38 | Data platform | SQL, Streamlit, performance, Cortex AI, security, notebooks, pipelines |
| **Python** | 200-299 | 13 | Software engineering | Core patterns, FastAPI, Flask, Typer CLI, Pydantic, pytest, Pandas |
| **Shell Scripts** | 300-399 | 6 | Automation | Bash and Zsh scripting, security, testing |
| **Containers** | 400-499 | 1 | Infrastructure | Docker best practices |
| **Data Science** | 500-599 | 1 | Analytics | ML lifecycle, feature engineering |
| **Data Governance** | 600-699 | 1 | Quality | Data quality, lineage, stewardship |
| **Business Intelligence** | 700-799 | 1 | Reporting | Business analytics, visualization |
| **Project Management** | 800-899 | 5 | Workflows | Git, changelog, README, contributing, Taskfile |
| **Demo & Synthetic Data** | 900-999 | 2 | Examples | Demo creation, data generation |

**🔍 Searchable index:** See [RULES_INDEX.md](RULES_INDEX.md) for complete rule list with keywords, dependencies, and semantic search

## Directive Language Hierarchy

The rules use a structured directive language with clear priority levels to guide both AI agents and human developers:

### Behavioral Control Directives (By Strictness)

```
├── Critical        [System Safety]      🔴 Must never violate
├── Mandatory       [Non-negotiable]     🟠 Must always follow  
├── Always          [Universal Practice] 🟡 Should be consistent
├── Requirement     [Technical Standard] 🔵 Should implement
├── Rule            [Best Practice]      🟢 Recommended pattern
└── Consider        [Optional]           ⚪ Suggestions & alternatives
```

### Informational Directives

```
├── Error           [Problem Description]  - Troubleshooting guidance
├── Exception       [Special Case]        - Override conditions
├── Forbidden       [Explicit Prohibition] - Explicitly prohibited actions
└── Note            [Additional Info]     - Cross-references and context
```

### Usage Examples

- **Critical:** `Critical: In PLAN mode, you are FORBIDDEN from using ANY file-modifying tools`
- **Mandatory:** `Mandatory: You MUST ask for explicit user confirmation of the TASK LIST`
- **Always:** `Always: Reference the most recent online official documentation`
- **Requirement:** `Requirement: Use fenced code blocks with language tags`
- **Rule:** `Rule: Act as a senior, pragmatic software engineer`
- **Consider:** `Consider: Use tables for structured information`
- **Avoid:** `Avoid: Mixing business logic and UI rendering in a single function`

This hierarchy ensures consistent interpretation across different AI models and provides clear guidance on the relative importance of each directive.

## Rule Architecture

The project uses a **universal-first architecture**: source templates are transformed into portable formats that work with any IDE, agent, or LLM. Rules are generated from a single source of truth into multiple deployment formats.

**Key concepts:**

- **Templates** in `templates/` are the source of truth (84 rule files)
- **Universal format** creates portable Markdown that works everywhere
- **IDE-specific formats** add convenience features for Cursor, Copilot, Cline
- **Automatic discovery** via AGENTS.md and RULES_INDEX.md enables intelligent rule loading

The generator (`generate_agent_rules.py`) handles format conversion, reference updates, and metadata preservation automatically. Rules preserve essential metadata (Keywords, TokenBudget, ContextTier, Depends) while stripping IDE-specific details.

**See [Architecture Documentation](docs/ARCHITECTURE.md) for complete technical details, format specifications, and design decisions.**

## AI Configuration

After deploying rules to your project, AI assistants automatically discover and load relevant rules based on your tasks.

### How Automatic Discovery Works

1. **Deploy** rules to your project: `task deploy:universal DEST=~/my-project`
2. **AI reads** `AGENTS.md` (loading protocol) and `RULES_INDEX.md` (catalog) from project root
3. **AI searches** keywords matching your task
4. **AI loads** relevant rules following dependency chains
5. **AI applies** rules to generate code

**Example:**
```
User: "Build a Snowflake Streamlit dashboard"
AI loads: 000-global-core → 100-snowflake-core → 101-snowflake-streamlit-core
```

### Manual Rule Management

**Search for rules by keyword:**

```bash
grep -i "performance" RULES_INDEX.md
```

**Check rule dependencies:**
```bash
grep "**Depends:**" rules/101-snowflake-streamlit-core.md
```

**Calculate total token budget:**
```bash
grep "**TokenBudget:**" rules/*.md | awk -F: '{sum+=$3} END {print sum}'
```

### Programmatic Rule Loading Example

```python
import re
from pathlib import Path

def load_rule_with_dependencies(rule_name, rules_dir="rules"):
    """Load a rule and all its dependencies in correct order."""
    loaded = []
    to_load = [rule_name]
    
    while to_load:
        current = to_load.pop(0)
        if current not in loaded and current != "None":
            # Read the rule file
            rule_path = Path(rules_dir) / current
            if rule_path.exists():
                content = rule_path.read_text()
                
                # Extract dependencies
                depends_match = re.search(r'\*\*Depends:\*\* (.+)', content)
                if depends_match:
                    deps = depends_match.group(1).split(', ')
                    # Add dependencies to load queue (they'll load first)
                    to_load = [f"{d}.md" for d in deps if d != "None"] + to_load
                
                loaded.append(current)
    
    return loaded  # Returns rules in dependency order

# Example usage
rules_to_load = load_rule_with_dependencies("101-snowflake-streamlit-core.md")
# Returns: ["000-global-core.md", "100-snowflake-core.md", "101-snowflake-streamlit-core.md"]
```

## Contributing

**This section and those following are for developers who want to modify or contribute rules.**  
If you're using the rules in your project, setup is complete. See [Troubleshooting](#troubleshooting) for support.

We welcome contributions! This project thrives on community input.

### How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines including:

- **Getting Started**: Fork, clone, environment setup
- **Development Workflow**: Testing, validation, code quality checks
- **Rule Authoring**: Standards, numbering scheme, governance
- **Pull Requests**: Branch strategy, conventional commits, changelog
- **Configuration Safety**: YAML, shell quoting, package management

**Quick Reference:**
```bash
# Fork and clone the repository (choose one)
# GitLab:
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
# GitHub:
git clone https://github.com/Snowflake-Labs/ai_coding_rules.git

cd ai_coding_rules

# Set up development environment
task env:deps

# Make changes, then validate
task validate:rules
task quality:lint

# Regenerate all formats
task generate:rules:all

# Submit pull request
```

For detailed workflows and examples, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Memory Bank System (Optional)

> **Note:** This is an optional advanced feature for complex, long-running projects. Skip this section if you're just getting started.

The Memory Bank is a structured documentation system that helps AI assistants maintain context across multiple sessions. Since AI assistants reset between sessions, the Memory Bank provides continuity by capturing project state, architectural decisions, and current work focus.

**Key benefits:**

- Maintains project context across development sessions
- Captures architectural decisions and technical patterns
- Tracks active work and known issues
- Enables consistent AI assistance on long-running projects

**When to use:**

- Projects spanning multiple weeks or months
- Complex architectures requiring detailed documentation
- Team collaboration where AI context sharing matters

**See [Memory Bank Documentation](docs/MEMORY_BANK.md) for complete setup and usage guide.**

## Troubleshooting

### Rules Directory Not Generated

**Problem:** Rules directory doesn't exist after running generation/deployment

**Solutions:**

1. **Verify Python Version**

```bash
python --version
# Must be 3.11 or higher
```

2. **Install Dependencies**

```bash
task env:deps
# OR without Task:
uv sync
```

3. **Check for Errors**

   - Review terminal output for error messages
   - Look for permission issues or missing dependencies

4. **Try Direct Script**

```bash
# For generation
uv run scripts/generate_agent_rules.py --agent universal --source templates --destination .

# For deployment (recommended)
uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
```

5. **Verify Project Structure**

```bash
# Check required files exist
ls scripts/generate_agent_rules.py scripts/deploy_rules.py Taskfile.yml templates/
```


### Task Command Not Found

**Problem:** `task: command not found` or `bash: task: command not found`

**Solutions:**

**Option A - Install Task (Recommended)**

```bash
# macOS
brew install go-task/tap/go-task

# Linux
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin

# Windows (PowerShell)
choco install go-task
```

**Option B - Deployment Without Task**

See [Option D: Deployment Without Task](#option-d-deployment-without-task) in Quick Start for complete instructions.

Quick example for universal rules:

```bash
cd /tmp/ai-rules
/opt/homebrew/bin/uv sync
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project
```

**Validation:**

```bash
# If Task installed successfully
task --version

# Should show: Task version: v3.x.x
```


### Python Version Conflicts

**Problem:** Wrong Python version or dependency conflicts

**Solutions:**

1. **Check Python Version**

```bash
python --version
python3 --version
# Need 3.11 or higher
```

2. **Use uv to Pin Version**

```bash
task env:python
# Creates .python-version file pinning to 3.11
```

3. **Clean and Reinstall**

```bash
task maintenance:clean:venv   # Remove virtual environment
task env:deps     # Reinstall dependencies
```

4. **Manual venv Setup (fallback)**

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows

pip install -e ".[dev]"
```


### IDE Not Recognizing Rules

**Problem:** AI assistant not using generated rules

You can force the AI assistant to load rules with simple additions to your prompt.

```
Load AGENTS.md into the context.  Review RULES_INDEX.md based on the keywords in my prompt and load appropriate rules.
```

**For Cursor:**

1. **Verify Rules Exist**

```bash
ls generated/cursor/rules/*.mdc | wc -l
# Should show 84 files
```

2. **Check Cursor Settings**

   - Open Cursor Settings (Cmd/Ctrl + ,)
   - Navigate to "Rules" or "AI" section
   - Verify rules directory is recognized

3. **Restart Cursor IDE**

   - Sometimes requires full restart to detect new rules

4. **Verify File Extension**

   - Cursor rules must use `.mdc` extension
   - Run `task generate:rules:cursor` to regenerate if needed

**For GitHub Copilot:**

1. **Verify Instructions Exist**

```bash
ls .github/instructions/*.md | wc -l
# Should show 84 files
```

2. **Check Repository Settings**
   - Instructions must be committed to repository
   - GitHub Copilot reads from remote, not local files
   - Commit and push changes: `git add .github/instructions/ && git commit && git push`

3. **Wait for Sync**
   - May take 5-10 minutes for GitHub to index new instructions
   - Try reloading VS Code after pushing

**For Universal Format (Claude, ChatGPT, etc.):**

1. **Verify Files Generated**
```bash
ls generated/universal/*.md | wc -l
# Should show 84 files
```

2. **Add to AI Context Manually**
   - **Claude Projects:** Upload `discovery/AGENTS.md`, `discovery/RULES_INDEX.md`, and relevant `generated/universal/*.md` files to project knowledge
   - **ChatGPT:** Add files to custom instructions or upload via file attachment
   - **Other LLMs:** Refer to specific tool documentation for context management

3. **Test Rule Loading**
   - Ask: "What rules are available for Snowflake development?"
   - AI should reference RULES_INDEX.md and list rules
   - If not working, verify RULES_INDEX.md is in context


### How to Verify Rules Are Working

**Test 1: Rule Discovery**
```
Prompt: "What rules are available for Snowflake development?"
Expected: AI references RULES_INDEX.md and lists 100-series rules
```

**Test 2: Rule Application**
```
Prompt: "Build a simple FastAPI endpoint following project rules"
Expected: AI follows patterns from 210-python-fastapi-core.md
```

**Test 3: Dependency Loading**
```
Prompt: "Create a Snowflake Streamlit app"
Expected: AI loads 000-global-core, 100-snowflake-core, 101-snowflake-streamlit-core
```

**Manual Verification:**
```bash
# Verify files exist
ls generated/universal/*.md | wc -l  # Should be 84

# Check discovery files (in this repo's discovery/ directory)
ls discovery/AGENTS.md discovery/RULES_INDEX.md

# After deployment, check files in project root
cat AGENTS.md | head -20
cat RULES_INDEX.md | head -20

# Test keyword search
grep -i "fastapi" RULES_INDEX.md
grep -i "snowflake" RULES_INDEX.md
```


### Permission Errors During Generation

**Problem:** Permission denied when generating rules

**Solutions:**

1. **Check Current Directory Permissions**
```bash
# Verify you can write to current directory
touch test.txt && rm test.txt
```

2. **Use Custom Destination**
```bash
# Generate to home directory
task generate:rules:universal DEST=~/ai-coding-rules-output

# Or use absolute path
task generate:rules:universal DEST=/tmp/rules-output
```

3. **Fix Repository Permissions**
```bash
# If cloned repository has wrong permissions
chmod -R u+w .
```


### Still Having Issues?

**Get Help:**
- **Check Issues:** [GitLab Issues](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git/issues)
- **Review Validation:** Run `task validate:rules` to check rule structure
- **Enable Debug Mode:** `task generate:rules:universal --verbose` for detailed output
- **Check Logs:** Review terminal output for specific error messages

**Common Fixes:**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Clear cache: `rm -rf .venv __pycache__`
- Reinstall dependencies: `task maintenance:clean:venv && task env:deps`

## Compatibility Matrix

| LLM/Tool | Reads Universal Markdown | IDE-Specific Format | Auto-Discovery | Status |
|----------|--------------------------|---------------------|----------------|--------|
| **Claude (API/Web)** | ✅ Yes | N/A | ✅ via AGENTS.md | Full Support |
| **Gemini (API/Web)** | ✅ Yes | N/A | ✅ via AGENTS.md | Full Support |
| **ChatGPT** | ✅ Yes | N/A | ✅ via AGENTS.md | Full Support |
| **GitHub Copilot** | ⚠️ Limited | ✅ `generated/copilot/instructions/` | ⚠️ Partial | Full Support |
| **Cursor** | ✅ Yes | ✅ `generated/cursor/rules/*.mdc` | ✅ Auto-attach | Full Support |
| **Cline** | ✅ Yes | ✅ `generated/cline/*.md` | ✅ Auto-process | Full Support |

**Legend:**
- **Reads Universal Markdown:** Can use `generated/universal/*.md` files without conversion
- **IDE-Specific Format:** Has optional IDE-specific format available in `generated/` directory
- **Auto-Discovery:** Supports automatic rule loading via discovery/AGENTS.md
- **Status:** Overall compatibility and support level

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues:** [GitLab Issues](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git/issues) *(Snowflake internal)*
- **Discussions:** [GitLab Discussions](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git/discussions) *(Snowflake internal)*
- **Documentation:** All rules include links to official documentation
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
