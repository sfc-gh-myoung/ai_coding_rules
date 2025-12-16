# AI Coding Rules

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/license/apache-2-0)
![Version](https://img.shields.io/badge/version-3.4.0-blue)
![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Task](https://img.shields.io/badge/Task-Taskfile-brightgreen)](https://taskfile.dev)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/sfc-gh-myoung/ai_coding_rules)

> **One universal ai coding rule set for all AI assistants, IDEs, and agents — portable, intelligent, and IDE-agnostic**

## Quick Overview

**What:** Universal AI coding rule system working with any assistant/IDE  
**Works with:** Cursor, Claude Code, GitHub Copilot, VS Code, ChatGPT, and more  
**Deploy:** 2 commands (`git clone` + `task deploy`)  
**Benefit:** 103 production-ready rules, automatic discovery, zero vendor lock-in

**Quick Checklist:**
- [ ] Prerequisites met? → [Prerequisites](#prerequisites)
- [ ] Ready to deploy? → [Quick Start](#quick-start)
- [ ] Want to understand first? → [Understanding Rules](#understanding-rules)
- [ ] Contributing rules? → [Contributing](#contributing)

## Overview

This repository provides a **universal ai coding rule system** designed to work seamlessly with any AI assistant, IDE, or development tool. Write rules once in a universal format, use them anywhere.

**What you get:** A comprehensive collection of 103 production-ready engineering rules covering Python, SQL, Snowflake, Go, Docker, Shell scripting, React, HTMX, Alpine.js, data engineering, analytics, and project governance. The rules work seamlessly with AI coding assistants including Cursor, Claude Code, GitHub Copilot, Visual Studio Code, and others.

**Important:** Some aspects of the rules are opinionated, particularly regarding naming conventions, project structure, usage of uv/uvx/ruff/Task, and documentation standards. You are **encouraged to review and adjust** the rules to align with your best practices or preferred approaches.

## Key Features

- **📚 103 Production-Ready Rules** — Comprehensive coverage across Snowflake, Python, Go, React, HTMX, Alpine.js, Docker, Shell scripting, and project management
- **🔄 Universal Format** — Write once, use everywhere: Cursor, VS Code, Claude, ChatGPT, GitHub Copilot, and more
- **🤖 Intelligent Discovery** — AI assistants automatically find and load relevant rules using semantic keyword matching
- **🎯 Dependency-Aware** — Explicit dependency chains ensure rules load in the correct order
- **⚡ Token-Efficient** — Modular, focused rules (150-500 lines) minimize context window usage
- **🔓 No Lock-In** — Standard Markdown with embedded metadata works with any tool or custom integration

This project was inspired, in part, by:

- [Cursor Rules](https://cursor.com/docs/context/rules)
- [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [how-to-add-cline-memory-bank-feature-to-your-cursor](https://forum.cursor.com/t/how-to-add-cline-memory-bank-feature-to-your-cursor/67868)
- [cline memory bank](https://docs.cline.bot/prompting/cline-memory-bank)

## Table of Contents

**For Users:**

- [Overview](#overview)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Video Tutorials](#video-tutorials)
- [Understanding Rules](#understanding-rules)
- [Rule Selection Guide](#rule-selection-decision-tree)
- [Rule Categories](#rule-categories)
- [AI Configuration](#ai-configuration)
- [Document Map](#document-map-what-to-read-first)
- [Troubleshooting](#troubleshooting)
- [License](#license)

**For Contributors:**

- [Contributing](#contributing)
- [Project Structure](#project-structure)
- [Development Commands](#development-commands)

## Prerequisites

Before getting started, ensure you have:

- **Python 3.11+** — [Download Python](https://www.python.org/downloads/)
- **Task** — Automation tool: [Installation guide](https://taskfile.dev/installation/)
- **Git** — For cloning repository: [Install Git](https://git-scm.com/downloads)
- **uv** — Python package manager: [Install uv](https://docs.astral.sh/uv/)

**Quick check:**

```bash
python --version  # Should show 3.11 or higher
task --version    # Should show Task version
git --version     # Should show Git version
```

## Document Map: What to Read First

This repository contains multiple documentation files for different audiences:

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Project overview, setup, usage | Start here (you are here) |
| **AGENTS.md** | Minimal bootstrap protocol for rule loading | AI agents: first action every response |
| **rules/000-global-core.md** | Execution protocols (MODE, validation, workflows) | AI agents: after loading foundation |
| **CONTRIBUTING.md** | Development guidelines, PR process | When contributing rules |
| **docs/ARCHITECTURE.md** | System architecture, design decisions | When understanding internals or extending |
| **docs/MEMORY_BANK.md** | Memory Bank system for long-running projects | When using Memory Bank (optional) |
| **CHANGELOG.md** | Version history, changes | When checking updates |
| **Taskfile.yml** | Build automation reference | When running tasks |

### Production-Ready Rules

| Directory | Format | Use With |
|-----------|--------|----------|
| **rules/** | Standard Markdown | Any IDE, LLM, or agent |

All rules are ready to deploy immediately—no generation step required.

**Quick Decision**:

- **Just want to use rules?** → See [Quick Start](#quick-start)
- **Want to modify rules?** → See [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)
- **Want to configure your AI?** → See [AI Configuration](#ai-configuration)
- **Want to understand the system?** → See [Architecture](docs/ARCHITECTURE.md)

## Quick Start

**Get started in 2 commands:**

```bash
# 1. Clone this repository (choose one)

# GitHub HTTPS:
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git

# GitHub SSH:
git clone git@github.com:sfc-gh-myoung/ai_coding_rules.git

cd ai_coding_rules

# 2. Deploy rules to your project
python scripts/rule_deployer.py --dest ~/my-project

# Or use task:
task deploy DEST=~/my-project

# 3. Use in your AI assistant
# Add to prompt: "Load AGENTS.md and follow guidance for rule loading with RULES_INDEX.md"
```

**That's it!** Your project now has 103 production-ready rules ready to use.

**What just happened?**

- ✅ Copied `rules/` directory (103 rules) to your project
- ✅ Copied `AGENTS.md` and `RULES_INDEX.md` for automatic AI discovery
- ✅ Ready to use immediately—no additional configuration needed!

**Next Steps:**

- ✅ Deployment complete → [Watch Video Tutorials](#video-tutorials) or [Configure Your AI](#ai-configuration)
- 🤔 Want to understand how rules work → [Understanding Rules](#understanding-rules)
- 🔧 Need different setup? → See [Deployment Options](#deployment-options)

**Alternative Paths:**

- 🛠️ **Modify or contribute** → See [For Rule Maintainers](#for-rule-maintainers-contributing-to-rules)

## Video Tutorials

Learn how to use AI Coding Rules through practical demonstrations:

| Demo | Topic | Link |
|------|-------|------|
| Demo 1 | Getting Started with AI_CODING_RULES Project | [Watch on YouTube](https://youtu.be/9lVrLegKgDg) |
| Demo 3 | Bug Fixes and Enhancements on Existing Project | [Watch on YouTube](https://youtu.be/hi5wcnLDEuI) |
| Demo 4 | Using Snowflake Cortex Code CLI with AI_CODING_RULES | [Watch on YouTube](https://youtu.be/YhYRcfLAfr4) |
| Demo 5 | Continuation: Snowflake Cortex Code CLI and AI_CODING_RULES | [Watch on YouTube](https://youtu.be/Xse0gqvgzQM) |

> **Note:** These videos are currently unlisted and accessible only via direct link.

**Quick guide:**
- **New to the project?** → Start with Demo 1
- **Working on existing code?** → See Demo 3
- **Using Snowflake Cortex?** → Watch Demos 4 & 5

### Deployment Options

**Basic Deployment (Rules + Skills):**

```bash
python scripts/rule_deployer.py --dest ~/my-project
# Or use task:
task deploy DEST=~/my-project
```

**What happens:**

- ✅ Copies `rules/` directory to `DEST/rules/`
- ✅ Copies `skills/` directory to `DEST/skills/` (excludes internal-only skills)
- ✅ Copies `AGENTS.md` and `RULES_INDEX.md` to project root
- ✅ Rules and skills ready to use immediately with any AI assistant or IDE

**Skills Exclusions:**

Both skills are internal-only and excluded from deployment (configured in `pyproject.toml`):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",   # Rule creation tool for ai_coding_rules project only
    "rule-reviewer/",  # Rule review tool for ai_coding_rules project only
]
```

**Deploy Rules Only (Skip Skills):**

```bash
python scripts/rule_deployer.py --dest ~/my-project --skip-skills
# Or use task:
task deploy:no-skills DEST=~/my-project
```

**Preview Before Deploying:**

```bash
python scripts/rule_deployer.py --dest ~/my-project --dry-run
# Or use task:
task deploy:dry DEST=~/my-project
```

**What happens:**

- ✅ Shows what would be copied without making changes
- ✅ Validates destination path exists
- ✅ Identifies potential conflicts
- ✅ Shows which skills will be excluded

### Option: Git Submodule (Version Tracking)

Track rule updates via git submodule:

```bash
# From your project root (choose one)

# GitHub:
git submodule add https://github.com/sfc-gh-myoung/ai_coding_rules.git .ai-rules

cd .ai-rules

task deploy DEST=..   # Deploy to parent project

# Update rules later
cd .ai-rules && git pull && task deploy DEST=..
```

### Option: Deployment Without Task

If you don't have Task installed, use the Python deployment script directly:

```bash
# Clone the rules repository (choose one)

# GitHub:
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git /tmp/ai-rules

cd /tmp/ai-rules

# Install Python dependencies
uv sync --all-groups

# Deploy using Python script (handles everything automatically)
uv run python scripts/rule_deployer.py --dest ~/my-project

# Verify deployment
ls ~/my-project/rules/*.md | wc -l  # Should show 103
ls ~/my-project/AGENTS.md ~/my-project/RULES_INDEX.md  # Both files should exist
```

**Success!** Your AI assistant can now access 103 specialized rules. See [AI Configuration](#ai-configuration) for IDE-specific setup.

## Understanding Rules

### What Are AI Coding Rules?

AI coding rules are structured Markdown files that guide AI assistants on how to write code, following best practices and patterns for specific technologies.

**Key Concepts:**

- **Universal Format:** Write once, use everywhere (any IDE, LLM, or agent)
- **Automatic Discovery:** AI finds relevant rules based on your task keywords
- **Dependency-Aware:** Rules load prerequisites automatically in correct order
- **Token-Efficient:** Small, focused rules (150-500 lines each) minimize context usage

### How Automatic Discovery Works

AI assistants automatically discover and load relevant rules based on your task using a three-step process:

<details>
<summary>📊 <strong>Visual Flowchart: Rule Discovery System</strong> (click to expand)</summary>

```ascii
┌─────────────────────────────────────────────────────────────────┐
│                   Rule Discovery System                         │
└─────────────────────────────────────────────────────────────────┘

  User Task                    AI Agent Actions
  ─────────                   ──────────────────
     
  📝 "Build a                 ┌──────────────────┐
   Snowflake                  │ 1. Read          │
   Streamlit                  │   AGENTS.md      │◄─── Loading Protocol
   dashboard"                 │                  │     (MODE, validation)
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 2. Search        │
                              │   RULES_INDEX.md │◄─── Keyword Match
                              │                  │     ("Streamlit")
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 3. Load Rules    │
                              │   (dependency    │◄─── Dependency Chain
                              │    order)        │     (000→100→101)
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 4. Apply Rules   │
                              │   to Task        │◄─── Code Generation
                              │                  │
                              └──────────────────┘

Example Loading Sequence:
──────────────────────────
  000-global-core.md          (Foundation - always first)
    └── 100-snowflake-core.md (SQL patterns - dependency)
          └── 101-snowflake-streamlit-core.md (Streamlit specifics)
```

</details>

**Step-by-step:**

1. **You provide a task** → "Build a Snowflake Streamlit dashboard"
2. **AI reads AGENTS.md** → Understands loading protocol (MODE, validation gates)
3. **AI searches RULES_INDEX.md** → Finds rules with "Streamlit" keyword
4. **AI loads dependencies** → Follows dependency chain (000 → 100 → 101)
5. **AI applies rules** → Generates code following loaded patterns

**Example keyword matching:**
- "Streamlit" → loads `101-snowflake-streamlit-core.md`
- "FastAPI" → loads `210-python-fastapi-core.md`
- "testing" → loads `206-python-pytest.md`

> **💡 Pro Tip: Keywords Drive Discovery**
> 
> The `Keywords` metadata in each rule enables semantic search. When you say "optimize Streamlit performance," 
> the AI searches RULES_INDEX.md for rules with keywords: "performance", "streamlit", "caching", "optimization".
> 
> **This is why well-crafted prompts matter** - specific keywords help the AI load the most relevant rules.
> See [prompts/README.md](prompts/README.md) for effective prompt patterns.

See [docs/ARCHITECTURE.md#discovery-system](docs/ARCHITECTURE.md#discovery-system) for complete technical details.

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

<details>
<summary>📊 Visual Decision Tree (expand for diagram)</summary>

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
     │   +101c (security)     │ └►220-python-typer-cli         └►803-project-git-workflow
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

</details>

### Text-Based Rule Selection Guide

**Step 1: Identify your primary technology**

- **Snowflake** → Start with `100-snowflake-core.md`
- **Python** → Start with `200-python-core.md`
- **Shell/Bash** → Start with `300-bash-scripting-core.md`
- **Docker** → Start with `400-docker-best-practices.md`
- **General** → Start with `000-global-core.md` (always load first)

**Step 2: Select your use case**

**Snowflake Projects:**
- SQL/Pipeline → `100-snowflake-core.md`
- Streamlit app → `101-snowflake-streamlit-core.md` (+ 101a for charts, 101b for performance)
- Notebooks/ML → `109-snowflake-notebooks.md`
- AI/ML features → `114-cortex-aisql.md` (+ 114a for agents, 114b for search)

**Python Projects:**
- FastAPI → `210-python-fastapi-core.md` (+ 210a for security if auth needed)
- Flask → `250-python-flask.md`
- CLI Tool → `220-python-typer-cli.md`
- Testing → `206-python-pytest.md`
- Data Science → `500-data-science.md`

**React/Frontend Projects:**
- React app → `440-react-core.md` (architecture, state management, styling)
- React + Python backend → `441-react-backend.md` (FastAPI/Flask integration, CORS, JWT)
- TypeScript → `430-typescript-core.md`
- JavaScript → `420-javascript-core.md`

**Go Projects:**
- Go app → `600-golang-core.md` (project structure, error handling, interfaces, testing, concurrency)

**Infrastructure Projects:**
- Docker → `400-docker-best-practices.md`
- Shell scripting → `300-bash-scripting-core.md`
- CI/CD → `803-project-git-workflow.md`

**Step 3: Follow the dependency chain**

1. Always load `000-global-core.md` first (foundation)
2. Load domain foundation (e.g., `100-snowflake-core` or `200-python-core`)
3. Load specialized rules based on your task
4. Check the `Depends` field in each rule to load prerequisites

**Step 4: Add specialized rules as needed**

Use `RULES_INDEX.md` to search for additional rules by keyword (testing, security, performance, etc.)

### Example Loading Sequences

**Snowflake Streamlit Dashboard:**

```
000-global-core.md (foundation)
└── 100-snowflake-core.md (SQL patterns)
    └── 101-snowflake-streamlit-core.md (app basics)
        ├── 101a-streamlit-visualization.md (if using charts)
        └── 101b-streamlit-performance.md (if optimizing)
```

**Python FastAPI with Testing:**

```
000-global-core.md (foundation)
└── 200-python-core.md (Python basics)
    ├── 210-python-fastapi-core.md (API framework)
    │   └── 210a-fastapi-security.md (if auth needed)
    └── 206-python-pytest.md (testing patterns)
```

## Example Prompts

Learn how to write effective prompts that help AI assistants automatically discover and load the right rules for your tasks.

**📝 Example Prompt Templates:** See [prompts/README.md](prompts/README.md) for:

- **Real-world prompt examples** — 4 proven patterns for different task types
- **Agent-Centric Rule Review** — Systematic prompt for reviewing rule files across any AI model
- **Keyword reference guide** — Which keywords trigger which rules
- **Best practices** — Tips for getting better results from AI assistants
- **Quick patterns** — Copy-paste templates for common scenarios

**🔍 Rule Review Prompt (template):** See [skills/rule-reviewer/PROMPT.md](skills/rule-reviewer/PROMPT.md)

**📘 Rule Review Prompt Guide (how to use):** See [docs/USING_RULE_REVIEW_PROMPT.md](docs/USING_RULE_REVIEW_PROMPT.md) for:

- **6-point scoring system** — Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness
- **Three review modes** — FULL, FOCUSED, and STALENESS for different use cases
- **Cross-model compatibility** — Tested on GPT-4o, GPT-5.1, GPT-5.2, Claude Sonnet 4.5, Claude Opus 4.5, Gemini 2.5 Pro, Gemini 3 Pro
- **Periodic review schedule** — Recommended cadence for rule maintenance

**🧰 Claude Skills (internal-only):** See [skills/](skills/) for:

- **rule-creator** (internal-only) — Create v3.0 Cursor rules with template generation and schema validation
  - Structured skill: `skills/rule-creator/SKILL.md` with 5-phase workflow
  - Excluded from deployment (for ai_coding_rules project maintenance only)
  - Trigger keywords: "create rule", "add rule", "new rule", "generate rule"

- **rule-reviewer** (internal-only) — Automate rule quality reviews (FULL/FOCUSED/STALENESS modes) and write results to `reviews/`
  - Structured skill: `skills/rule-reviewer/SKILL.md` with workflows, examples, tests, and validation
  - Excluded from deployment (for ai_coding_rules project maintenance only)
  - Trigger keywords: "review rule", "audit rule", "check rule quality", "rule staleness"
  - See [docs/USING_RULE_REVIEW_SKILL.md](docs/USING_RULE_REVIEW_SKILL.md) for usage guide

Both skills follow [Anthropic Agent Skills best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) with:
- Enhanced YAML frontmatter (version, author, tags, dependencies)
- Progressive disclosure (workflows/, examples/, tests/)
- Inline validation snippets for quick checks
- Edge case documentation and self-validation procedures

**Quick preview:**

```
Task: Fix all Ruff linting errors in Python validation scripts
Files: scripts/rule_validator.py, scripts/index_generator.py
Errors: 9 total (F841 unused variables, UP037 quoted type annotations)
```

This structured format helps AI assistants automatically load the right rules (`200-python-core`, `201-python-lint-format`) based on file types and keywords.

## Contributing

We welcome contributions! This project thrives on community input.

**Want to contribute?** See [CONTRIBUTING.md](./CONTRIBUTING.md) for complete guidelines including:

- Development environment setup
- Rule authoring guidelines and template generator usage  
- Schema validation and testing procedures
- Pull request process and code quality standards
- Configuration safety and best practices

For questions or discussions, file an issue on the repository.

## Project Structure

```ascii
ai_coding_rules/
├── rules/                  ← Production-ready rules (103 files)
├── AGENTS.md               ← Rule loading protocol for AI assistants
├── RULES_INDEX.md          ← Searchable rule catalog
├── scripts/                ← Validation and deployment tools
│   ├── index_generator.py      ← Generate RULES_INDEX.md
│   ├── rule_deployer.py        ← Deploy rules to projects
│   ├── schema_validator.py     ← Validate rule structure
│   ├── template_generator.py   ← Create new rule templates
│   ├── keyword_generator.py    ← Generate semantic keywords for rules
│   └── token_validator.py      ← Validate token budgets (single file or directory)
├── docs/                   ← Documentation
│   ├── ARCHITECTURE.md         ← System design decisions
│   └── MEMORY_BANK.md          ← Memory Bank system (optional)
├── tests/                  ← Test suite
├── schemas/                ← JSON schemas for rule validation
├── prompts/                ← User prompt templates + Rule Review prompt
└── skills/                 ← Claude Agent Skills (rule-creator, rule-reviewer)
```

**Key Concepts:**

- **rules/** — Production-ready rules, deploy directly (no generation needed)
- **AGENTS.md** — AI discovery protocol in project root
- **RULES_INDEX.md** — Searchable catalog in project root
- **scripts/** — Validation (`schema_validator.py`), deployment (`rule_deployer.py`)

**Workflows:**

```bash
# For users: Deploy rules
task deploy DEST=~/my-project

# For contributors: Edit and validate
vim rules/200-python-core.md
task rules:validate          # Validate changes
task index:generate          # Update RULES_INDEX.md
git add rules/ RULES_INDEX.md && git commit -m "feat: update Python rules"
```

## Development Commands

Run `task` to see the full categorized command list with quickstart guide.

```bash
# Quickstart (most common commands)
task quality:fix                       # Fix all code quality issues (alias: fix, qf)
task test                              # Run all pytest tests (alias for test:all)
task validate                          # Run all CI/CD checks (alias for validate:ci)
task index:generate                    # Regenerate RULES_INDEX.md
task deploy DEST=~/my-project          # Deploy rules to project

# Deployment
task deploy DEST=~/my-project          # Deploy rules to project
task deploy:dry DEST=~/my-project      # Preview deployment
task deploy:verbose DEST=~/my-project  # Deploy with verbose output
task deploy:no-skills DEST=~/my-project # Deploy rules only (skip skills)

# Rule Management
task rule:new FILENAME=100-example     # Create new rule from template
task rules:validate                    # Validate all rules against schema
task rules:validate:verbose            # Validate with detailed errors

# Index Management
task index:generate                    # Generate RULES_INDEX.md
task index:check                       # Check if index is current

# Token Management
task tokens:update                     # Update token budgets in all rules
task tokens:check                      # Check token budget accuracy (all files)
task tokens:update:file FILE=...       # Update single file token budget
task tokens:check:file FILE=...        # Check single file token budget

# Keyword Generation
task keywords:suggest FILE=...         # Suggest keywords for a rule
task keywords:update FILE=...          # Update keywords in-place
task keywords:all                      # Suggest keywords for all rules

# Quality & Testing
task quality:check                     # Run all quality checks
task quality:fix                       # Fix all quality issues (alias: fix, qf)
task quality:lint                      # Run ruff linter (check only)
task quality:format                    # Run ruff formatter (check only)
task quality:typecheck                 # Run ty type checker (aliases: type, type-check)
task quality:markdown                  # Run pymarkdownlnt Markdown linter
task test                              # Run all pytest tests (alias for test:all)
task test:coverage                     # Run tests with coverage report

# Validation & CI
task validate                          # Run all CI/CD checks (alias for validate:ci)
task preflight                         # Verify environment is ready

# Environment
task env:python                        # Pin Python 3.11 and create venv
task env:sync                          # Sync dev dependencies (fast)
task env:deps                          # Lock and sync dependencies

# Cleanup
task clean:cache                       # Remove Python cache files
task clean:venv                        # Remove virtual environment
task clean:all                         # Remove all generated files

# Status
task status                            # Show project status summary
```

## Rule Categories

The 103 rules are organized by domain using a three-digit numbering system. Each category focuses on a specific technology or practice area.

| Domain | Range | # Rules | Focus Area | Key Topics |
|--------|-------|---------|------------|------------|
| **Core Foundation** | 000-099 | 7 | Universal patterns | Operating principles, memory bank, rule governance, boilerplate template, context engineering, tool design |
| **Snowflake** | 100-199 | 39 | Data platform | SQL, Streamlit, performance, Cortex AI, security, notebooks, pipelines |
| **Python** | 200-299 | 23 | Software engineering | Core patterns, FastAPI, Flask, Typer CLI, Pydantic, pytest, Pandas, **HTMX** |
| **Shell Scripts** | 300-399 | 7 | Automation | Bash and Zsh scripting, security, testing |
| **Frontend/Containers** | 400-499 | 5 | Infrastructure & UI | Docker, JavaScript, TypeScript, React, **HTMX frontend** |
| **Frontend** | 500-599 | 1 | Client-side | HTMX frontend reference |
| **Systems/Backend Languages** | 600-699 | 1 | Backend development | **Go/Golang** core patterns, error handling, concurrency |
| **Business Intelligence** | 700-799 | 1 | Reporting | Business analytics, visualization |
| **Project Management** | 800-899 | 6 | Workflows | Git, changelog, README, contributing, Taskfile, automation |
| **Demo & Synthetic Data** | 900-999 | 5 | Examples | Demo creation, data generation, data science, data governance, business analytics |

### HTMX Rules (New in v3.1.0)

The Python domain now includes comprehensive HTMX support for building hypermedia-driven web applications:

| Rule | Focus | Description |
|------|-------|-------------|
| **221-python-htmx-core** | Foundation | Request/response lifecycle, HTTP headers, security (CSRF, XSS), HATEOAS principles |
| **221a-python-htmx-templates** | Templates | Jinja2 organization, partials, fragments, conditional rendering |
| **221b-python-htmx-flask** | Flask Integration | Flask-HTMX extension, blueprints, session management, authentication |
| **221c-python-htmx-fastapi** | FastAPI Integration | Async routes, dependency injection, Pydantic validation, background tasks |
| **221d-python-htmx-testing** | Testing | Pytest fixtures, header assertions, HTML validation, mocking strategies |
| **221e-python-htmx-patterns** | Common Patterns | CRUD, forms, infinite scroll, search, real-time updates, modals, wizards |
| **221f-python-htmx-integrations** | Frontend Libraries | Alpine.js, _hyperscript, Tailwind, Bootstrap, Chart.js integration |
| **500-frontend-htmx-core** | Frontend Reference | HTMX attributes, events, CSS transitions, debugging, browser compatibility |

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

The project uses a **production-ready rules architecture**. Rules are authored once in universal Markdown format and work everywhere without transformation.

**Key concepts:**

- **Production-ready rules** in `rules/` directory (103 files)
- **Universal Markdown format** works with any IDE, LLM, or agent
- **Automatic discovery** via `AGENTS.md` and `RULES_INDEX.md` in project root
- **Direct deployment** - no generation or transformation steps needed
- **Validation tools** ensure rules follow schema before deployment

Rules preserve essential metadata (Keywords, TokenBudget, ContextTier, Depends) while remaining readable Markdown. AI assistants use `AGENTS.md` to understand loading protocol and `RULES_INDEX.md` to discover relevant rules by keyword search.

**See [Architecture Documentation](docs/ARCHITECTURE.md) for complete technical details and design decisions.**

## AI Configuration

After deploying rules to your project, AI assistants automatically discover and load relevant rules based on your tasks. For complete details on the discovery protocol, see [docs/ARCHITECTURE.md#discovery-system](docs/ARCHITECTURE.md#discovery-system).

**Quick example:**
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

## Memory Bank System (Optional)

The Memory Bank is a structured documentation system that helps AI assistants maintain context across long-running projects. It captures project state, architectural decisions, and work focus to provide continuity across development sessions.

**See [docs/MEMORY_BANK.md](docs/MEMORY_BANK.md) for complete setup and usage guide.**

## Troubleshooting

### Rules Directory Not Generated

**Problem:** Rules directory doesn't exist after deployment

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
# For deployment
uv run scripts/rule_deployer.py --dest ~/my-project
```

5. **Verify Project Structure**

```bash
# Check required files exist
ls scripts/rule_deployer.py scripts/schema_validator.py Taskfile.yml rules/
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
uv sync --all-groups
uv run python scripts/rule_deployer.py --dest ~/my-project
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
task clean:venv   # Remove virtual environment
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

**Problem:** AI assistant not using deployed rules

You can force the AI assistant to load rules with simple additions to your prompt.

```
Load AGENTS.md into the context.  Review RULES_INDEX.md based on the keywords in my prompt and load appropriate rules.
```

**For Universal Format (Claude, ChatGPT, Cursor, etc.):**

1. **Verify Files Deployed**
```bash
ls rules/*.md | wc -l
# Should show 103 files
```

2. **Add to AI Context**
   - **Claude Projects:** Upload `AGENTS.md`, `RULES_INDEX.md`, and relevant `rules/*.md` files to project knowledge
   - **ChatGPT:** Add files to custom instructions or upload via file attachment
   - **Cursor:** Rules automatically discovered from project root
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
ls rules/*.md | wc -l  # Should be 102

# Check files in project root
cat AGENTS.md | head -20
cat RULES_INDEX.md | head -20

# Test keyword search
grep -i "fastapi" RULES_INDEX.md
grep -i "snowflake" RULES_INDEX.md
```


### Permission Errors During Deployment

**Problem:** Permission denied when deploying rules

**Solutions:**

1. **Check Current Directory Permissions**
```bash
# Verify you can write to current directory
touch test.txt && rm test.txt
```

2. **Use Custom Destination**
```bash
# Deploy to home directory
task deploy DEST=~/ai-coding-rules-output

# Or use absolute path
task deploy DEST=/tmp/rules-output
```

3. **Fix Repository Permissions**
```bash
# If cloned repository has wrong permissions
chmod -R u+w .
```


### Still Having Issues?

**Get Help:**
- **Check Issues:** [GitHub Issues](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)
- **Review Validation:** Run `task rules:validate` to check rule structure
- **Enable Debug Mode:** `task deploy:verbose DEST=~/path` for detailed output
- **Check Logs:** Review terminal output for specific error messages

**Common Fixes:**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Clear cache: `rm -rf .venv __pycache__`
- Reinstall dependencies: `task clean:venv && task env:sync`

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

**Key Points:**

- ✅ **Commercial use permitted** - Use in commercial projects and products
- ✅ **Modification allowed** - Adapt rules to your organization's needs
- ✅ **Distribution allowed** - Share modified or unmodified rules
- ✅ **Patent grant included** - Protection from patent claims
- ⚠️ **Trademark use NOT granted** - "Snowflake" and logos require separate permission
- ⚠️ **No warranty provided** - Provided "as-is" without guarantees

**Contributing:** By submitting a pull request, you agree to license your contribution under the Apache 2.0 License. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sfc-gh-myoung/ai_coding_rules/discussions)
- **Documentation:** All rules include links to official documentation
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Quick Reference

### Common Commands

**With Task:**
```bash
# Deploy/update rules
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules
task deploy DEST=~/my-project
```

**Without Task (Python script):**
```bash
# Deploy/update rules using Python script
cd /tmp/ai-rules
uv sync --all-groups
uv run python scripts/rule_deployer.py --dest ~/my-project
```

**General:**
```bash
# Check rule count
ls rules/*.md | wc -l  # Should show 103 files

# Search rules (RULES_INDEX.md is in project root after deployment)
grep -i "keyword" RULES_INDEX.md

# Find specific rule
find rules -name "*python*"
```

### Common Prompts

```
"What rules are available for [technology]?"
"Load rules for [task] development"
"Review this code for rule compliance"
"Which rule covers [specific topic]?"
"Follow rule [number] for this implementation"
```

### Key Files

| File | Purpose | Location (after deployment) |
|------|---------|----------|
| `AGENTS.md` | Rule discovery guide | **Project root** |
| `RULES_INDEX.md` | Searchable catalog | **Project root** |
| `000-global-core.md` | Foundation rules | `rules/` |
| All rule files | 103 specialized rules | `rules/` |
