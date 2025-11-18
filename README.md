# AI Coding Rules

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/license/apache-2-0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Task](https://img.shields.io/badge/Task-Taskfile-brightgreen)](https://taskfile.dev)

> **One universal rule set for all AI assistants, IDEs, and agents — portable, intelligent, and IDE-agnostic**

## Overview

This repository provides a **universal-first rule system** designed to work seamlessly with any AI assistant, IDE, or development tool. Write rules once in a universal format, use them everywhere.

**What you get:** A comprehensive collection of 74 engineering rules covering Python, SQL, Snowflake, Docker, Shell scripting, data engineering, analytics, and project governance. The rules work seamlessly with AI coding assistants including Claude, ChatGPT, GitHub Copilot, Cursor, and others.

**Important:** Some aspects of the rules are opinionated, particularly regarding naming conventions, project structure, usage of uv/ruff/Task, and documentation standards. You are **encouraged to review and adjust** the rules to align with your best practices or preferred approaches.

## Key Features

- **📚 74 Specialized Rules** — Comprehensive coverage across Snowflake, Python, Docker, Shell scripting, and project management
- **🔄 Universal Format** — Write once, use everywhere: Cursor, VS Code, Claude, ChatGPT, GitHub Copilot, and more
- **🤖 Intelligent Discovery** — AI assistants automatically find and load relevant rules using semantic keyword matching
- **🎯 Dependency-Aware** — Explicit dependency chains ensure rules load in the correct order
- **⚡ Token-Efficient** — Modular, focused rules (150-500 lines) minimize context window usage
- **🔓 No Lock-In** — Standard Markdown with embedded metadata works with any tool or custom integration

This project was inspired, in part, by: [how-to-add-cline-memory-bank-feature-to-your-cursor](https://forum.cursor.com/t/how-to-add-cline-memory-bank-feature-to-your-cursor/67868) and [cline memory bank](https://docs.cline.bot/prompting/cline-memory-bank)

<details>
<summary><h3>Universal Format Philosophy (Click to expand)</h3></summary>

The rule system is built on a template-first architecture: 74 source templates in `templates/` generate portable rules that work with any tool, IDE, or AI assistant.

**Key Features:**
- **Any AI Assistant**: Claude, GPT, Gemini, custom agents
- **Any IDE**: Cursor, VS Code, IntelliJ, JetBrains, Vim
- **Any Tool**: CLI tools, scripts, custom integrations
- **No lock-in**: Standard Markdown with semantic metadata

**Core Principles:**

1. **Template-First Design**: Source templates in `templates/` directory → Generate to `generated/` outputs
2. **Generate Once, Use Everywhere**: Run `task rule:universal` to create portable rules
3. **Automatic Rule Discovery**: AI assistants use `AGENTS.md` and `RULES_INDEX.md` (deployed to project root) for semantic keyword matching
4. **Dependency-Aware Architecture**: Explicit dependency chains ensure correct rule loading order
5. **Token-Efficient Design**: Modular, focused rules (150-500 lines) minimize context usage
6. **Technology Coverage**: 74 specialized rules covering Snowflake, Python, Docker, Shell scripting, and project management
7. **Auto-Generated Catalog**: `RULES_INDEX.md` automatically generated from template metadata and deployed to project root

**What This Repository Provides:**

- **74 source templates** in `templates/` directory covering best practices, patterns, and governance
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

- [Overview](#overview)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Document Map](#document-map-what-to-read-first)
- [Rule Categories](#rule-categories)
- [Rule Selection Guide](#rule-selection-decision-tree)
- [AI Configuration](#ai-configuration)
- [Project Structure](#project-structure)
- [Development Commands](#development-commands)
- [Troubleshooting](#troubleshooting)
- [Compatibility Matrix](#compatibility-matrix)
- [Contributing](#contributing)
- [License](#license)

## Document Map: What to Read First

This repository contains multiple documentation files for different audiences:

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Project overview, setup, usage | Start here (you are here) |
| **docs/ONBOARDING.md** | Team onboarding guide | When setting up for your team |
| **docs/RULE_CATALOG.md** | Complete list of all 74 rules | When browsing available rules |
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
- **Just want to use rules?** → See [For Rule Consumers](#for-rule-consumers-using-the-rules)
- **Want to modify rules?** → See [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)
- **Want to configure your AI?** → See [AI Configuration](#ai-configuration)
- **Want to understand the system?** → See [Architecture](docs/ARCHITECTURE.md)

---

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

---

## Quick Start

**Choose your path:**

- 🚀 **Use rules in your project** → See [Deployment](#deployment-recommended) below
- 🛠️ **Modify or contribute** → See [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)
- 📹 **Watch first** → [Video: Overview](https://youtu.be/IhkfZwmkQyM) | [Demo](https://youtu.be/YOGxwtTWBCI)

### Deployment (Recommended)

**Get started in 3 commands:**

```bash
# 1. Clone this repository
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
cd ai_coding_rules

# 2. Deploy rules to your project
task deploy:universal DEST=~/my-project   # Works with any IDE/LLM
```

**That's it!** Your project now has 74 specialized rules ready to use.

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
# From your project root
git submodule add https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git .ai-rules
cd .ai-rules
task deploy:universal DEST=..   # Deploy to parent project

# Update rules later
cd .ai-rules && git pull && task deploy:universal DEST=..
```

#### Option D: Deployment Without Task

If you don't have Task installed, use the Python deployment script directly:

```bash
# Clone the rules repository
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules

# Install Python dependencies
/opt/homebrew/bin/uv sync

# Deploy using Python script (handles everything automatically)
/opt/homebrew/bin/uv run scripts/deploy_rules.py --agent universal --destination ~/my-project

# Verify deployment
ls ~/my-project/rules/*.md | wc -l  # Should show 74
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
ls rules/*.md | wc -l  # Should show 74

# Or for Cursor
ls .cursor/rules/*.mdc | wc -l  # Should show 74
```

**Success!** Your AI assistant can now access 74 specialized rules. See [AI Configuration](#ai-configuration) for IDE-specific setup.


### For Rule Maintainers (Contributing to Rules)

**Want to modify or contribute rules?** Follow this development setup:

#### Prerequisites

- **Python 3.11+** — Required for running generation scripts
- **uv** — Fast dependency management ([install guide](https://github.com/astral-sh/uv))
- **Task** — Simplified commands ([install guide](https://taskfile.dev/installation/))

#### Setup

```bash
# Clone the repository
git clone https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git
cd ai_coding_rules

# Set up Python environment
task deps:dev

# Generate all rule formats
task rule:all
```

#### Project Structure

See [Project Structure](#project-structure) section below for full details.

**Quick Overview:**
- `templates/` — 74 source template files (edit these)
- `discovery/` — Rule loading protocol and catalog
- `generated/` — IDE-ready outputs (auto-generated, don't edit)
- `scripts/` — Generation and deployment tools

#### Development Workflow

```bash
# 1. Edit templates
vi templates/200-python-core.md

# 2. Generate outputs
task rule:all            # All formats
task rule:universal      # Just universal
task rules:index         # Regenerate RULES_INDEX.md (in discovery/ dir of this repo)

# 3. Validate
task validate            # Runs linting, tests, and checks

# 4. Test locally
# Copy generated/universal/ to a test project and verify

# 5. Commit
git add templates/ discovery/
git commit -m "feat: update Python core rules"
```

#### Common Tasks

```bash
# Generate specific formats
task rule:cursor         # Cursor IDE format
task rule:copilot        # GitHub Copilot format
task rule:cline          # Cline format
task rule:universal      # Universal format

# Regenerate rule index
task rules:index         # Generate RULES_INDEX.md (in discovery/ dir of this repo)

# Validate everything
task validate            # Lint, test, and check staleness

# Check if outputs are stale
task rule:universal:check
task rules:index:check

# Clean generated files
task clean:rules
```

#### Verification Checklist

**After making changes:**
- [ ] Edit source files in `templates/`
- [ ] Run `task rule:all` to regenerate
- [ ] Run `task rules:index` to update catalog
- [ ] Run `task validate` to verify quality
- [ ] Test with actual AI assistant
- [ ] Commit `templates/`, `discovery/`, and `generated/` directories

**What NOT to commit:**
- ❌ `.venv/` or Python cache files
- ❌ IDE-specific settings (unless intentional)
- ❌ Temporary test directories

#### Testing Your Changes

```bash
# Option 1: Validate with task suite
task validate

# Option 2: Manual testing with AI assistant
# Copy generated/universal/ to a test project
mkdir ~/test-rules
cp -r generated/universal/* ~/test-rules/
cp discovery/AGENTS.md ~/test-rules/AGENTS.md
cp discovery/RULES_INDEX.md ~/test-rules/RULES_INDEX.md

# Point your AI assistant to ~/test-rules/ and verify behavior
```

**Success Indicators:**
- ✅ `task validate` passes all checks
- ✅ `generated/universal/` contains 74 rule files
- ✅ `RULES_INDEX.md` (in test directory) lists all rules with metadata
- ✅ AI assistant can load and apply rules correctly
- ✅ No linting errors in templates

**See also:** [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed contribution guidelines.


## Rule Selection Decision Tree

```
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
```
000-global-core (foundation)
└── 100-snowflake-core (SQL patterns)
    └── 101-snowflake-streamlit-core (app basics)
        ├── 101a-streamlit-visualization (if using charts)
        └── 101b-streamlit-performance (if optimizing)
```

**Python FastAPI with Testing:**
```
000-global-core (foundation)
└── 200-python-core (Python basics)
    ├── 210-python-fastapi-core (API framework)
    │   └── 210a-fastapi-security (if auth needed)
    └── 206-python-pytest (testing patterns)
```

## Why Smaller, Focused Rules?

This project uses **smaller, topic-focused rules** instead of large monolithic rule files. This architectural decision significantly improves both LLM accuracy and context window efficiency.

### LLM Accuracy and Comprehension

**Focused rules improve AI assistant accuracy** in several ways:

- **Clear Signal-to-Noise Ratio**: When a rule covers only Python FastAPI security (211), the LLM receives targeted, unambiguous guidance without wading through unrelated Flask or Django content.
- **Reduced Conflicting Guidance**: Smaller rules minimize the risk of contradictory advice within the same context. A 200-line FastAPI security rule is far less likely to contain conflicting patterns than a 2,000-line "web frameworks" mega-rule.
- **Precise Activation**: Agent-requested rules mean only relevant guidance loads into context. Working on Snowflake Snowpipe? You get `121-snowflake-snowpipe.md` (1,017 lines) without loading unrelated Cortex AI or SPCS guidance.
- **Better Pattern Matching**: LLMs excel at pattern recognition. Focused rules create clear patterns (e.g., "Snowpipe → auto-ingest → cloud events") that are easier to recall and apply accurately.

**Example**: Compare a 3,000-line "Snowflake Everything" rule with our modular approach:
- **Monolithic**: LLM must sift through warehouse management, Snowpipe, Cortex AI, security, and cost governance simultaneously—increasing the chance of applying warehouse sizing advice to Snowpipe (which uses serverless compute).
- **Modular**: Request `121-snowflake-snowpipe.md` and `119-snowflake-warehouse-management.md` separately. Each rule provides focused, non-conflicting guidance for its specific domain.

### Context Window Efficiency

**Context windows are precious and expensive.** Every token counts, especially with Claude, GPT-4, or Gemini models where you pay per token.

**Smaller rules optimize context usage**:

- **Load Only What's Needed**: A 300-line Pydantic rule (`230-python-pydantic.md`) uses ~600 tokens. A 2,000-line "Python Everything" rule uses ~4,000 tokens but you only need 15% of it.
- **Leave Room for Code**: With a 200k token context window, loading 10 focused rules (3,000 tokens total) leaves 197k tokens for your actual codebase, conversation history, and responses. Loading 3 monolithic rules (12,000 tokens) leaves only 188k tokens—a 4.5% reduction in usable context.
- **Avoid Token Waste**: Why load Bash scripting rules when you're working on Python? Focused rules mean you activate `200-python-core.md` (500 tokens) instead of "All Scripting Languages" (2,000 tokens).
- **Enable Rule Combinations**: Need FastAPI + Pydantic + pytest? Load `210-python-fastapi-core.md` (400 tokens) + `230-python-pydantic.md` (300 tokens) + `206-python-pytest.md` (350 tokens) = 1,050 tokens. A monolithic "Python Web Testing" rule would be 1,500+ tokens even if you only need those three topics.

**Real-world impact**: On a Snowflake data engineering project, you might need:
- `100-snowflake-core.md` (500 tokens) - foundational practices
- `104-snowflake-streams-tasks.md` (400 tokens) - incremental pipelines
- `121-snowflake-snowpipe.md` (2,000 tokens) - continuous ingestion
- `200-python-core.md` (500 tokens) - Python basics

**Total: 3,400 tokens of highly relevant, focused guidance** vs. loading a single 5,000-token "Data Engineering Monolith" that includes Spark, Airflow, and other irrelevant content.

### Practical Development Benefits

Beyond LLM performance, smaller rules provide:

- **Easier Maintenance**: Update Snowpipe best practices in one 1,000-line file instead of searching through a 5,000-line data engineering rule.
- **Better Composability**: Mix and match rules for your tech stack (FastAPI + Snowflake + pytest) without loading irrelevant content.
- **Faster Updates**: When Snowflake releases a new feature, update one focused rule instead of maintaining a massive monolith.
- **Clear Dependencies**: Rule cross-references (e.g., `121-snowflake-snowpipe.md` references `108-snowflake-data-loading.md`) make relationships explicit.
- **Reduced Cognitive Load**: Developers can review and understand a 300-line rule in minutes. A 3,000-line monolith requires hours.

### The Cost of Monolithic Rules

**What happens with large, all-encompassing rules?**

1. **Accuracy Degrades**: More content = more chances for conflicting advice = LLM confusion
2. **Token Waste**: Loading 5,000 tokens when you need 500 = 90% waste = fewer tokens for actual code
3. **Maintenance Nightmare**: Finding and updating specific guidance in 5,000 lines is error-prone
4. **Slow Iteration**: Every update requires reviewing the entire monolith for conflicts

**Our approach**: Keep individual rules under 1,000 lines (target 150-500 lines), use clear cross-references, and let users compose rule sets for their specific needs.

## System-Wide Script (gen-rules)

Install the `gen-rules` wrapper script to deploy/generate rules from anywhere on your system:

**Installation:**

```bash
# From the ai_coding_rules directory
cp scripts/gen-rules.sh ~/bin/gen-rules
chmod +x ~/bin/gen-rules
# Ensure ~/bin is in your PATH
```

**Basic Usage:**

```bash
# Deploy rules (recommended)
cd /path/to/my-project
gen-rules deploy:cursor            # Deploy to .cursor/rules/
gen-rules deploy:universal         # Deploy to rules/
gen-rules deploy:copilot           # Deploy to .github/copilot/instructions/
gen-rules deploy:cline             # Deploy to .clinerules/

# Generate for development/testing
gen-rules rule:cursor              # Generate to generated/cursor/rules/
gen-rules rule:all                 # Generate all formats

# Override destination
gen-rules deploy:universal DEST=/custom/path
```

**Advanced Options:**

```bash
gen-rules --help                   # Show full usage
gen-rules --version                # Show version
gen-rules --verbose deploy:cursor  # Verbose output
gen-rules --debug rule:all         # Debug mode
gen-rules --project ~/my-rules rule:cursor  # Override project dir
```

**Features:**
- ✅ Production-ready with comprehensive error handling
- ✅ Works from any directory
- ✅ Flexible configuration via flags or environment variables
- ✅ Debug support for troubleshooting
- ✅ Meaningful exit codes (0-4)

See `gen-rules --help` for complete documentation.

## Project Structure

```
ai_coding_rules/
├── templates/              ← Edit these: 74 source template files
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
- **generated/** — IDE-ready outputs, regenerated via `task rule:all`
- **scripts/** — `generate_agent_rules.py` (generation), `deploy_rules.py` (deployment)

**Workflows:**
```bash
# For users: Deploy rules
task deploy:universal DEST=~/my-project

# For contributors: Edit and regenerate
vim templates/200-python-core.md
task rule:all
git add templates/ generated/ && git commit -m "feat: update Python rules"
```

## Rule Categories

The 74 rules are organized by domain using a three-digit numbering system. Each category focuses on a specific technology or practice area.

| Domain | Range | # Rules | Focus Area | Key Topics |
|--------|-------|---------|------------|------------|
| **Core Foundation** | 000-099 | 6 | Universal patterns | Operating principles, memory bank, rule governance, context engineering, tool design |
| **Snowflake** | 100-199 | 35 | Data platform | SQL, Streamlit, performance, Cortex AI, security, notebooks, pipelines |
| **Python** | 200-299 | 13 | Software engineering | Core patterns, FastAPI, Flask, Typer CLI, Pydantic, pytest, Pandas |
| **Shell Scripts** | 300-399 | 6 | Automation | Bash and Zsh scripting, security, testing |
| **Containers** | 400-499 | 1 | Infrastructure | Docker best practices |
| **Data Science** | 500-599 | 1 | Analytics | ML lifecycle, feature engineering |
| **Data Governance** | 600-699 | 1 | Quality | Data quality, lineage, stewardship |
| **Business Intelligence** | 700-799 | 1 | Reporting | Business analytics, visualization |
| **Project Management** | 800-899 | 5 | Workflows | Git, changelog, README, contributing, Taskfile |
| **Demo & Synthetic Data** | 900-999 | 2 | Examples | Demo creation, data generation |

**📖 Complete listings:** See [Rule Catalog](docs/RULE_CATALOG.md) for detailed descriptions of all 74 rules

**🔍 Searchable index:** See [RULES_INDEX.md](RULES_INDEX.md) for keywords, dependencies, and semantic search

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
- **Templates** in `templates/` are the source of truth (74 rule files)
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

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Improving existing rules
- Generating new rules
- Rule validation procedures
- Code review process

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-rule`
3. Follow rule authoring guidelines in `002-rule-governance.md` section 9
4. Test your changes: `task lint` and `task rule:universal --dry-run`
5. Validate rules: `task rules:validate`
6. Submit a pull request

### Key Guidelines

- Use standard Markdown with clear section headers (`#`, `##`, `###`)
- Follow directive language: `Critical`, `Mandatory`, `Always`, `Requirement`, `Rule`, `Consider`, `Avoid`
- Keep rules focused and under 500 lines (target 150-300)
- Include current official documentation links
- Test with `task rules:validate` before submitting

**For detailed workflows and examples, see [CONTRIBUTING.md](CONTRIBUTING.md).**

### Configuration Safety Guidelines

- **YAML Safety**: Avoid Unicode characters (bullets, checkmarks) that cause parsing errors
- **Shell Quoting**: Quote arguments with special characters: `".[dev]"` not `.[dev]`
- **Taskfile Validation**: Always test with `task --list` after YAML changes
- **Python Packaging**: Ensure `__init__.py` files exist before `uv pip install -e .`

## Development Commands

### Environment Setup
```bash
# Python environment with uv (recommended)
task deps:dev              # Install development dependencies
task uv:pin               # Pin Python version and create venv

# Alternative with pip (fallback)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Code Quality & Linting
```bash
# Ruff (primary linter and formatter)
task lint                 # Check code with Ruff
task format              # Check formatting
task lint:fix            # Auto-fix linting issues
task format:fix          # Apply formatting

# Manual commands (if task unavailable)
uvx ruff check .          # Check linting
uvx ruff format --check . # Check formatting
uvx ruff format .         # Apply formatting
```

### Rule Deployment
```bash
# Deploy rules with automatic path configuration
task deploy:universal DEST=~/my-project    # For any IDE/LLM (recommended)
task deploy:cursor DEST=~/my-project       # For Cursor IDE
task deploy:copilot DEST=~/my-project      # For GitHub Copilot
task deploy:cline DEST=~/my-project        # For Cline

# Deploy to current directory (omit DEST)
cd ~/my-project
task deploy:cursor
```

### Rule Generation & Validation
```bash
# Generate IDE-specific rules (advanced - use deployment instead for projects)
task rule:cursor         # Generate Cursor rules to generated/cursor/rules/
task rule:copilot        # Generate Copilot rules to generated/copilot/instructions/
task rule:cline          # Generate Cline rules to generated/cline/
task rule:universal      # Generate Universal rules to generated/universal/
task rule:all            # Generate all IDE-specific rules (including universal)

# Optional DEST variable to change base output directory
task rule:all DEST=/custom/output

# Validate rule structure (002-rule-governance.md v2.1 compliance)
task rules:validate         # Standard validation (fails on critical errors)
task rules:validate:verbose # Show all files including clean ones
task rules:validate:strict  # Strict mode (fail on warnings too)

# Direct validation script usage
uv run python scripts/validate_agent_rules.py              # Standard validation
uv run python scripts/validate_agent_rules.py --verbose    # Verbose output
uv run python scripts/validate_agent_rules.py --fail-on-warnings  # Strict mode
uv run python scripts/validate_agent_rules.py --help       # Show all options

# Other validations
task --list              # Validate Taskfile syntax
uv run scripts/generate_agent_rules.py --source . --dry-run  # Test rule generation
```

### Utilities  
```bash
task clean_venv          # Remove virtual environment
task -l                  # List all available tasks
```

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
task deps:dev
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

See [Option C: Deployment Without Task](#option-c-deployment-without-task) in Quick Start for complete instructions.

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
task uv:pin
# Creates .python-version file pinning to 3.11
```

3. **Clean and Reinstall**
```bash
task clean_venv   # Remove virtual environment
task deps:dev     # Reinstall dependencies
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
# Should show 74 files
```

2. **Check Cursor Settings**
   - Open Cursor Settings (Cmd/Ctrl + ,)
   - Navigate to "Rules" or "AI" section
   - Verify rules directory is recognized

3. **Restart Cursor IDE**
   - Sometimes requires full restart to detect new rules

4. **Verify File Extension**
   - Cursor rules must use `.mdc` extension
   - Run `task rule:cursor` to regenerate if needed

**For GitHub Copilot:**

1. **Verify Instructions Exist**
```bash
ls .github/instructions/*.md | wc -l
# Should show 74 files
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
# Should show 74 files
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
ls generated/universal/*.md | wc -l  # Should be 74

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
task rule:universal DEST=~/ai-coding-rules-output

# Or use absolute path
task rule:universal DEST=/tmp/rules-output
```

3. **Fix Repository Permissions**
```bash
# If cloned repository has wrong permissions
chmod -R u+w .
```


### Still Having Issues?

**Get Help:**
- **Check Issues:** [GitLab Issues](https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules.git/issues)
- **Review Validation:** Run `task rules:validate` to check rule structure
- **Enable Debug Mode:** `task rule:universal --verbose` for detailed output
- **Check Logs:** Review terminal output for specific error messages

**Common Fixes:**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Clear cache: `rm -rf .venv __pycache__`
- Reinstall dependencies: `task clean_venv && task deps:dev`

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
