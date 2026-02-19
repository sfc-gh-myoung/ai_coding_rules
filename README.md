# AI Coding Rules

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/license/apache-2-0)
![Version](https://img.shields.io/badge/version-3.5.3-blue)
[![CI](https://github.com/sfc-gh-myoung/ai_coding_rules/actions/workflows/ci.yml/badge.svg)](https://github.com/sfc-gh-myoung/ai_coding_rules/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/sfc-gh-myoung/ai_coding_rules)

> **One universal ai coding rule set for all AI assistants, IDEs, and agents — portable, intelligent, and IDE-agnostic**

## Quick Overview

**What:** Universal AI coding rule system working with any assistant/IDE  
**Works with:** Cursor, Claude Code, GitHub Copilot, VS Code, ChatGPT, and more  
**Deploy:** 2 commands (`git clone` + `make deploy DEST=...`)  
**Benefit:** production-ready rules, automatic discovery, zero vendor lock-in

**Quick Checklist:**
- [ ] Prerequisites met? → [Prerequisites](#prerequisites)
- [ ] Ready to deploy? → [Quick Start](#quick-start)
- [ ] Want to understand first? → [Understanding Rules](#understanding-rules)
- [ ] Contributing rules? → [Contributing](#contributing)

## Overview

This repository provides a **universal ai coding rule system** designed to work seamlessly with any AI assistant, IDE, or development tool. Write rules once in a universal format, use them anywhere.

**What you get:** A comprehensive collection of production-ready engineering rules covering Python, SQL, Snowflake, Go, Docker, Shell scripting, React, HTMX, Alpine.js, data engineering, analytics, and project governance. The rules work seamlessly with AI coding assistants including Cursor, Claude Code, GitHub Copilot, Visual Studio Code, and others.

**Important:** Some aspects of the rules are opinionated, particularly regarding naming conventions, project structure, usage of uv/uvx/ruff, and documentation standards. You are **encouraged to review and adjust** the rules to align with your best practices or preferred approaches.

## Key Features

- **📚 128 Production-Ready Rules** — Comprehensive coverage across Snowflake, Python, Go, React, HTMX, Alpine.js, Docker, Podman, Shell scripting, and project management
- **🔄 Universal Format** — Write once, use everywhere: Cursor, VS Code, Claude, ChatGPT, GitHub Copilot, and more
- **🤖 Intelligent Discovery** — AI assistants automatically find and load relevant rules using semantic keyword matching (matching by meaning, not just exact text)
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
- [Claude Agent Skills](#claude-agent-skills)
- [Project Structure](#project-structure)
- [Development Commands](#development-commands)

## Prerequisites

Before getting started, ensure you have:

- **Python 3.11+** — [Download Python](https://www.python.org/downloads/)
- **Git** — For cloning repository: [Install Git](https://git-scm.com/downloads)
- **uv** — Python package manager: [Install uv](https://docs.astral.sh/uv/)

**Quick check:**

```bash
python --version  # Should show 3.11 or higher
git --version     # Should show Git version
```

## Document Map: What to Read First

This repository contains multiple documentation files for different audiences:

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Project overview, setup, usage | Start here (you are here) |
| **AGENTS.md** | Minimal bootstrap protocol for rule loading | AI agents: first action every response |
| **AGENTS_NO_MODE.md** | Simplified bootstrap without PLAN/ACT workflow | AI agents: deployed via `make deploy-no-mode DEST=...` from templates/ |
| **PROJECT.md** | Project-specific tooling and guidelines | AI agents: auto-loaded by supporting tools |
| **rules/000-global-core.md** | Execution protocols (MODE, validation, workflows) | AI agents: after loading foundation |
| **CONTRIBUTING.md** | Development guidelines, PR process | When contributing rules |
| **docs/ARCHITECTURE.md** | System architecture, design decisions | When understanding internals or extending |
| **docs/MEMORY_BANK.md** | Memory Bank system for long-running projects | When using Memory Bank (optional) |
| **CHANGELOG.md** | Version history, changes | When checking updates |
| **Makefile** | Development command targets (replaces ./dev) | When running tasks |

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

### Clone this repository (choose one)

```bash
# GitHub HTTPS:
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git

# GitHub SSH:
git clone git@github.com:sfc-gh-myoung/ai_coding_rules.git
```

### Deploy rules to your project

```bash
cd ai_coding_rules
uv sync --all-groups                     # Install dependencies
make deploy DEST=~/my-project            # Deploy rules

# Or use the CLI directly:
uv run ai-rules deploy ~/my-project
```

### Use in your AI assistant
The benefit of this project is that it uses AGENTS.md to start the rule loading process.  AGENTS.md is
automatically loaded by most agentic tools and IDEs.  If you are having issues with your tool of choice
not loading AGENTS.md, then you can add the following to your prompt:

```text
Load AGENTS.md and follow guidance for rule loading with rules/RULES_INDEX.md.
```

**That's it!** Your project now has production-ready rules ready to use.

**What just happened?**

- ✅ Copied `rules/` directory to your project
- ✅ Copied `AGENTS.md` and `rules/RULES_INDEX.md` for automatic AI discovery
- ✅ Ready to use immediately—no additional configuration needed!

**Next Steps:**

- 📝 Customize `PROJECT.md` for your project's tooling and guidelines (recommended)
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
make deploy DEST=~/my-project

# Or use the CLI directly:
uv run ai-rules deploy ~/my-project
```

**What happens:**

- ✅ Copies `rules/` directory to `DEST/rules/`
- ✅ Copies `skills/` directory to `DEST/skills/` (excludes internal-only skills)
- ✅ Copies `AGENTS.md` and `rules/RULES_INDEX.md` to project root
- ✅ Rules and skills ready to use immediately with any AI assistant or IDE

**Skills Exclusions:**

Some skills are internal-only and excluded from deployment (configured in `pyproject.toml`):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",      # Rule creation tool for ai_coding_rules project only
    "rule-reviewer/",     # Rule review tool for ai_coding_rules project only
    "bulk-rule-reviewer/" # Bulk review orchestrator for ai_coding_rules project only
]
```

**Note:** The `doc-reviewer` skill is deployed by default and can be used in target projects.

**Deploy Skills Only (Agent Configuration Directories):**

```bash
make deploy-only-skills DEST=~/.claude/skills

# Or use the CLI directly:
uv run ai-rules deploy ~/.claude/skills --only-skills
```

**What happens:**

- ✅ Copies only `skills/` directory to `DEST/skills/` (excludes internal-only skills)
- ✅ Skips rules and root files (AGENTS.md, rules/RULES_INDEX.md)
- ✅ Ideal for deploying skills to agent-specific configuration directories

**Common use cases:**

```bash
# Claude Code (Cursor/Windsurf)
make deploy-only-skills DEST=~/.claude/skills

# Cortex Code
make deploy-only-skills DEST=~/.snowflake/cortex/skills

# Custom project location
make deploy-only-skills DEST=./my-project/.ai/skills
```

**Deploy Rules Only (Skip Skills):**

```bash
make deploy-no-skills DEST=~/my-project

# Or use the CLI directly:
uv run ai-rules deploy ~/my-project --skip-skills
```

**Preview Before Deploying:**

```bash
make deploy-dry DEST=~/my-project

# Or use the CLI directly:
uv run ai-rules deploy ~/my-project --dry-run
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
uv sync --all-groups
make deploy DEST=..   # Deploy to parent project

# Update rules later
cd .ai-rules && git pull && make deploy DEST=..
```

### Option: Deployment Using CLI Directly

You can also use the `ai-rules` CLI directly:

```bash
# Clone the rules repository (choose one)

# GitHub:
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git /tmp/ai-rules

cd /tmp/ai-rules

# Install Python dependencies
uv sync --all-groups

# Deploy using CLI (handles everything automatically)
uv run ai-rules deploy ~/my-project

# Verify deployment
ls ~/my-project/rules/*.md | wc -l
ls ~/my-project/AGENTS.md ~/my-project/rules/RULES_INDEX.md  # Both files should exist
```

**Success!** Your AI assistant can now access specialized rules. See [AI Configuration](#ai-configuration) for IDE-specific setup.

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
                              │   rules/RULES_INDEX.md │◄─── Keyword Match
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
3. **AI searches rules/RULES_INDEX.md** → Finds rules with "Streamlit" keyword
4. **AI loads dependencies** → Follows dependency chain (000 → 100 → 101)
5. **AI applies rules** → Generates code following loaded patterns

**Example keyword matching:**
- "Streamlit" → loads `101-snowflake-streamlit-core.md`
- "FastAPI" → loads `210-python-fastapi-core.md`
- "testing" → loads `206-python-pytest.md`

> **💡 Pro Tip: Keywords Drive Discovery**
>
> The `Keywords` metadata in each rule enables semantic search. When you say "optimize Streamlit performance,"
> the AI searches rules/RULES_INDEX.md for rules with keywords: "performance", "streamlit", "caching", "optimization".
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

Use `rules/RULES_INDEX.md` to search for additional rules by keyword (testing, security, performance, etc.)

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
- **Keyword reference guide** — Which keywords trigger which rules
- **Best practices** — Tips for getting better results from AI assistants
- **Quick patterns** — Copy-paste templates for common scenarios

**Quick preview:**

```
Task: Fix all Ruff linting errors in Python validation modules
Files: src/ai_rules/commands/validate.py, src/ai_rules/commands/index.py
Errors: 9 total (F841 unused variables, UP037 quoted type annotations)
```

This structured format helps AI assistants automatically load the right rules (`200-python-core`, `201-python-lint-format`) based on file types and keywords.

## Claude Agent Skills

**This section is for developers working on the ai_coding_rules project or using skills in their own projects.**

The `skills/` directory contains structured Claude Agent Skills following [Anthropic's Agent Skills best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). All skills feature:

- Enhanced YAML frontmatter (version, author, tags, dependencies)
- Progressive disclosure (showing details only when needed: workflows/, examples/, tests/)
- Inline validation snippets for quick checks
- Edge case documentation and self-validation procedures

### Install Skills
There are several ways you can take advantage of these skills in your tool of choice.  The skills have been tested with Cursor, Cortex Code CLI (CoCo), and Claude Code.

#### Cursor
You can use these skills in Cursor by telling Cursor to explicitly load the skill in your prompt.
- Prompt: `Load skills/<skill_name>/SKILL.md`

#### Claude Code
You can use these skills in Claude Code by deploying the skills to the `.claude/skills` directory, either project or personal locations using the `make deploy` command or via filesystem `cp` command.

You can also use these skill by telling Claude Code to explicitly load the skill in your prompt.
- Prompt: `Load skills/<skill_name>/SKILL.md`

#### Cortex Code CLI
You can use these skills in Cortex Code CLI by running the skill add command.
- Prompt: `/skill add <project_path>/skills/<skill_name>`

You can also use these skills by telling Cortex Code CLI to explicitly load the skill in your prompt.
- Prompt: `Load skills/<skill_name>/SKILL.md`

### Deployed Skills (Available in Target Projects)

These skills are deployed by default when running `make deploy`:

**doc-reviewer** — Automate documentation quality reviews
- **Purpose:** Review documentation files for quality, completeness, and staleness
- **Modes:** FULL, FOCUSED, STALENESS
- **Scoring:** 100-point system across 6 dimensions (Clarity, Completeness, Accuracy, Structure, Consistency, Staleness)
- **Trigger keywords:** "review docs", "audit documentation", "check doc quality"
- **Usage guide:** [docs/USING_DOC_REVIEWER_SKILL.md](docs/USING_DOC_REVIEWER_SKILL.md)
- **Skill file:** [skills/doc-reviewer/SKILL.md](skills/doc-reviewer/SKILL.md)

**plan-reviewer** — Review implementation plans for agent executability
- **Purpose:** Evaluate LLM-generated plans across 8 dimensions for autonomous agent execution
- **Modes:** FULL (single plan), COMPARISON (rank multiple), META-REVIEW (consistency), DELTA (track fixes)
- **Scoring:** 100-point system with weighted dimensions (Executability 20, Completeness 20, Success Criteria 20, Scope 15, Dependencies 10, Decomposition 5, Context 5, Risk Awareness 5)
- **Verdicts:** EXCELLENT_PLAN (90-100), GOOD_PLAN (80-89), NEEDS_WORK (60-79), POOR_PLAN (40-59), INADEQUATE_PLAN (<40)
- **Trigger keywords:** "review plan", "compare plans", "plan quality", "meta-review", "plan executability"
- **Usage guide:** [docs/USING_PLAN_REVIEWER_SKILL.md](docs/USING_PLAN_REVIEWER_SKILL.md)
- **Skill file:** [skills/plan-reviewer/SKILL.md](skills/plan-reviewer/SKILL.md)

**skill-timing** — Performance measurement and timing instrumentation
- **Purpose:** Measure skill execution duration, track tokens, detect anomalies, compare against baselines
- **Features:** Wall-clock timing, checkpoints, token tracking, anomaly detection, baseline comparison
- **Output:** STDOUT summary and timing metadata appended to output files
- **Usage guide:** [docs/USING_SKILL_TIMING_SKILL.md](docs/USING_SKILL_TIMING_SKILL.md)
- **Skill file:** [skills/skill-timing/SKILL.md](skills/skill-timing/SKILL.md)

### Internal-Only Skills (Excluded from Deployment)

These skills are used only for ai_coding_rules project maintenance and are excluded from deployment:

**rule-creator** — Create new rules with template generation
- **Purpose:** Generate new rule files from templates with schema validation
- **Workflow:** 5-phase process (input validation, template generation, metadata setup, validation, file write)
- **Trigger keywords:** "create rule", "add rule", "new rule", "generate rule"
- **Usage guide:** [docs/USING_RULE_CREATOR_SKILL.md](docs/USING_RULE_CREATOR_SKILL.md)
- **Skill file:** [skills/rule-creator/SKILL.md](skills/rule-creator/SKILL.md)

**rule-reviewer** — Automate rule quality reviews
- **Purpose:** Review rule files for agent executability and quality
- **Modes:** FULL, FOCUSED, STALENESS
- **Scoring:** 100-point system across 6 dimensions (Actionability 25, Completeness 25, Consistency 15, Parsability 15, Token Efficiency 10, Staleness 10)
- **Priority Compliance Gate:** Agent Execution Test as first gate; Priority 1 violations cap scores
- **Cross-model compatibility:** Tested on GPT-4o, GPT-5.1, GPT-5.2, Claude Sonnet 4.5, Claude Opus 4.5, Gemini 2.5 Pro, Gemini 3 Pro
- **Trigger keywords:** "review rule", "audit rule", "check rule quality", "rule staleness"
- **Usage guide:** [docs/USING_RULE_REVIEW_SKILL.md](docs/USING_RULE_REVIEW_SKILL.md)
- **Skill file:** [skills/rule-reviewer/SKILL.md](skills/rule-reviewer/SKILL.md)

**bulk-rule-reviewer** — Orchestrate bulk rule reviews
- **Purpose:** Execute comprehensive reviews on all rules in `rules/` directory with consolidated priority reporting
- **Expected duration:** 1-2 hours with parallel sub-agents (default), 5-10 hours sequential
- **Parallel execution:** Launches 5 sub-agents by default, each with fresh context (eliminates drift)
- **Resume capability:** Skip existing reviews to resume after interruption
- **Output:** Individual review files + master summary report with priority tiers
- **Trigger keywords:** "bulk review rules", "review all rules", "audit rule repository"
- **Usage guide:** [docs/USING_BULK_RULE_REVIEWER_SKILL.md](docs/USING_BULK_RULE_REVIEWER_SKILL.md)
- **Skill file:** [skills/bulk-rule-reviewer/SKILL.md](skills/bulk-rule-reviewer/SKILL.md)

### Skill Deployment Configuration

Skills excluded from deployment are configured in `pyproject.toml`:

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",      # Rule creation tool for ai_coding_rules project only
    "rule-reviewer/",     # Rule review tool for ai_coding_rules project only
    "bulk-rule-reviewer/" # Bulk review orchestrator for ai_coding_rules project only
]
```

To deploy only skills (useful for agent configuration directories):

```bash
make deploy-only-skills DEST=~/.claude/skills
```

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
├── src/                    ← Python packages (CLI tools, evaluators)
│   ├── ai_rules/               ← Unified CLI: ai-rules (8 subcommands)
│   │   ├── cli.py                  ← Main CLI entry point
│   │   └── commands/               ← Subcommands: validate, index, keywords, deploy, tokens, new, badges, refs
│   ├── agent_eval/             ← AGENTS.md effectiveness evaluation CLI
│   └── prompt_eval/            ← Prompt quality evaluation CLI
├── rules/                  ← Production-ready rules (128 total)
│   └── examples/           ← Validated implementation examples (10 total)
├── AGENTS.md               ← Rule loading protocol for AI assistants
├── rules/RULES_INDEX.md          ← Searchable rule catalog
├── templates/              ← Source of truth for AGENTS.md variants
│   ├── AGENTS_MODE.md.template       ← Full PLAN/ACT protocol
│   └── AGENTS_NO_MODE.md.template    ← Simplified (no-mode) protocol
├── docs/                   ← Documentation (12 files)
│   ├── ARCHITECTURE.md         ← System design decisions
│   ├── MEMORY_BANK.md          ← Memory Bank system
│   ├── TOKEN_BUDGETS.md        ← Token budget guidelines
│   └── USING_*.md              ← Skill usage guides
├── tests/                  ← Test suite (98% coverage)
├── schemas/                ← YAML schemas for rule/example validation
├── prompts/                ← User prompt templates
├── skills/                 ← Claude Agent Skills (7 total)
│   ├── rule-reviewer/          ← Review individual rules
│   ├── bulk-rule-reviewer/     ← Review all rules at once
│   ├── doc-reviewer/           ← Review documentation
│   ├── plan-reviewer/          ← Review LLM-generated plans
│   ├── rule-creator/           ← Create new rules (internal)
│   ├── rule-loader/            ← Load rules for tasks
│   └── skill-timing/           ← Measure skill performance
└── Makefile                ← Development commands (make help for full list)
```

**Key Concepts:**

- **src/** — Python packages for CLI tools (`ai-rules`, `agent-eval`, `prompt-eval`)
- **rules/** — Production-ready rules (128 total), deploy directly (no generation needed)
- **AGENTS.md** — AI discovery protocol in project root
- **templates/** — Source of truth for AGENTS.md variants (used by `ai-rules deploy`)
- **rules/RULES_INDEX.md** — Searchable catalog in project root
- **Makefile** — Development targets (run `make help` for full list)

**Workflows:**

```bash
# For users: Deploy rules
make deploy DEST=~/my-project

# For contributors: Edit and validate
vim rules/200-python-core.md
make rules-validate           # Validate changes
make index-generate           # Update rules/RULES_INDEX.md
git add rules/ rules/RULES_INDEX.md && git commit -m "feat: update Python rules"
```

## CLI Commands

The `ai-rules` CLI provides 8 subcommands for rules management:

```bash
# Show help and all available commands
uv run ai-rules --help
```

| Command | Description |
|---------|-------------|
| `ai-rules validate` | Validate rule files against v3.2 schema |
| `ai-rules index` | Generate RULES_INDEX.md from rules/ metadata |
| `ai-rules keywords` | Suggest/update keywords using TF-IDF analysis |
| `ai-rules deploy` | Deploy rules and skills to target projects |
| `ai-rules tokens` | Validate and update TokenBudget metadata |
| `ai-rules new` | Generate new rule file from v3.2 template |
| `ai-rules badges` | Update README badges (version, tests, coverage) |
| `ai-rules refs` | Validate rule references in RULES_INDEX.md |

**Additional CLIs:**

| CLI | Description |
|-----|-------------|
| `uv run agent-eval` | Test AGENTS.md effectiveness with Cortex evaluation |
| `uv run prompt-eval` | Evaluate and improve prompt quality (6 dimensions, 100-point scale) |

## Development Commands

Run `make help` to see the full categorized command list.

```bash
# Quickstart (most common commands)
make quality-fix                        # Fix all code quality issues
make test                               # Run all pytest tests
make validate                           # Run all CI/CD checks
make index-generate                     # Regenerate rules/RULES_INDEX.md
make deploy DEST=~/my-project           # Deploy rules to project

# Deployment
make deploy DEST=~/my-project           # Deploy rules to project
make deploy-dry DEST=~/my-project       # Preview deployment
make deploy-verbose DEST=~/my-project   # Deploy with verbose output
make deploy-no-skills DEST=~/my-project # Deploy rules only (skip skills)
make deploy-no-mode DEST=~/my-project   # Deploy without PLAN/ACT workflow
make deploy-only-skills DEST=~/.claude/skills # Deploy only skills

# Split Deployment (separate directories)
make deploy-split AGENTS=~/.claude                                    # AGENTS-only
make deploy-split AGENTS=~/.claude RULES=~/.claude/rules              # Agents + rules
make deploy-split AGENTS=~/.claude RULES=~/.claude/rules SKILLS=~/.claude/skills

# Rule Management
make rule-new FILENAME=100-example      # Create new rule from template
make rules-validate                     # Validate all rules against schema
make rules-validate-verbose             # Validate with detailed errors

# Index Management
make index-generate                     # Generate rules/RULES_INDEX.md
make index-check                        # Check if index is current

# Token Management
make tokens-update                      # Update token budgets in all rules
make tokens-check                       # Check token budget accuracy
make tokens-update-file FILE=...        # Update single file token budget

# Keyword Generation
make keywords-suggest FILE=...          # Suggest keywords for a rule
make keywords-update FILE=...           # Update keywords in-place
make keywords-all                       # Suggest keywords for all rules

# Quality & Testing
make quality-check                      # Run all quality checks
make quality-fix                        # Fix all quality issues
make lint                               # Run ruff linter (check only)
make format                             # Run ruff formatter (check only)
make typecheck                          # Run ty type checker
make markdown                           # Run pymarkdownlnt Markdown linter
make test                               # Run all pytest tests
make test-cov                           # Run tests with coverage report

# Validation & CI
make validate                           # Run all CI/CD checks
make preflight                          # Verify environment is ready

# Environment
make env-python                         # Pin Python 3.11 and create venv
make env-sync                           # Sync dev dependencies (fast)
make env-deps                           # Lock and sync dependencies

# Cleanup
make clean-cache                        # Remove Python cache files
make clean-venv                         # Remove virtual environment
make clean                              # Remove all generated files

# Status
make status                             # Show project status summary
```

## Rule Categories

The rules are organized by domain using a three-digit numbering system. Each category focuses on a specific technology or practice area.

| Domain | Range | # Rules | Focus Area | Key Topics |
|--------|-------|---------|------------|------------|
| **Core Foundation** | 000-099 | 12 | Universal patterns | Operating principles, memory bank, rule governance, context engineering, tool design, skills |
| **Snowflake** | 100-199 | 58 | Data platform | SQL, Streamlit, performance, Cortex AI, security, notebooks, pipelines, demo creation |
| **Python** | 200-299 | 27 | Software engineering | Core patterns, FastAPI, Flask, Typer CLI, Pydantic, pytest, Pandas, **HTMX** |
| **Shell/Containers** | 300-399 | 9 | Automation & Infrastructure | Bash and Zsh scripting, security, testing, Docker, **Podman** |
| **Frontend (JS/TS)** | 400-499 | 3 | Client-side frameworks | JavaScript, TypeScript, React, **HTMX frontend** |
| **Frontend** | 500-599 | 2 | Client-side | HTMX frontend, browser globals |
| **Systems/Backend Languages** | 600-699 | 1 | Backend development | **Go/Golang** core patterns, error handling, concurrency |
| **Reserved** | 700-799 | 0 | Future use | Reserved for future domain expansion |
| **Project Management** | 800-899 | 5 | Workflows | Git, changelog, README, contributing, Taskfile |
| **Analytics & Governance** | 900-999 | 4 | Business intelligence | Data science, data governance, business analytics, semantic views |

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

**🔍 Searchable index:** See [rules/RULES_INDEX.md](rules/RULES_INDEX.md) for complete rule list with keywords, dependencies, and semantic search

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

## Evaluation Tools

### agent_eval — AGENTS.md Effectiveness Testing

Tests whether AI agents correctly follow the `AGENTS.md` bootstrap protocol by sending evaluation prompts through Snowflake Cortex and scoring responses against expected behaviors.

```bash
uv run agent-eval run                    # Run all evaluation tests
uv run agent-eval run --parallel         # Run tests in parallel
uv run agent-eval run -t test_name       # Run a specific test
```

**Features:** Connection verification, parallel execution with per-test progress tracking, thread-safe counters, configurable Cortex model selection. See [tools/agent_eval/README.md](tools/agent_eval/README.md) for full documentation.

### prompt_eval — Prompt Quality Evaluation

Evaluates and improves prompts for LLM/agent execution quality across 6 weighted dimensions on a 100-point scale (letter grade A–F), then generates improved versions optimized for any LLM or coding agent.

```bash
uv run prompt-eval eval prompt.txt       # Evaluate a prompt file
uv run prompt-eval eval -                # Evaluate from stdin
uv run prompt-eval eval prompt.txt --no-rewrite  # Score only, skip rewrite
uv run prompt-eval api                   # Start web UI at localhost:8000
```

**Scoring Dimensions:**

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Actionability | 25 pts | Clear, unambiguous instructions an agent can execute |
| Completeness | 25 pts | All necessary context, constraints, and outputs included |
| Token Efficiency | 10 pts | Concise without redundancy |
| Cross-Agent Consistency | 10 pts | Works reliably across different LLMs |
| Parsability | 10 pts | Structured formatting agents can parse |
| Context Grounding | 10 pts (bonus) | References concrete files, functions, or project context |

**Interfaces:** CLI, REST API, and web UI. **Output formats:** Markdown (default), JSON, HTML. See [tools/prompt_eval/README.md](tools/prompt_eval/README.md) for full documentation.

## Rule Architecture

The project uses a **production-ready rules architecture**. Rules are authored once in universal Markdown format and work everywhere without transformation.

**Key concepts:**

- **Production-ready rules** in `rules/` directory
- **Universal Markdown format** works with any IDE, LLM, or agent
- **Automatic discovery** via `AGENTS.md` and `rules/RULES_INDEX.md` in project root
- **Direct deployment** - no generation or transformation steps needed
- **Validation tools** ensure rules follow schema before deployment

Rules preserve essential metadata (Keywords, TokenBudget, ContextTier, Depends) while remaining readable Markdown. ContextTier provides secondary priority signaling; see `000-global-core.md` for primary preservation mechanism (natural language markers). AI assistants use `AGENTS.md` to understand loading protocol and `rules/RULES_INDEX.md` to discover relevant rules by keyword search.

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
grep -i "performance" rules/RULES_INDEX.md
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
make env-sync
# OR directly:
uv sync --all-groups
```

3. **Check for Errors**

   - Review terminal output for error messages
   - Look for permission issues or missing dependencies

4. **Try Direct CLI**

```bash
# For deployment
uv run ai-rules deploy ~/my-project
```

5. **Verify Project Structure**

```bash
# Check required files exist
ls src/ai_rules/cli.py Makefile rules/
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
make env-python
# Creates .python-version file pinning to 3.11
```

3. **Clean and Reinstall**

```bash
make clean-venv    # Remove virtual environment
make env-sync      # Reinstall dependencies
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
Load AGENTS.md into the context.  Review rules/RULES_INDEX.md based on the keywords in my prompt and load appropriate rules.
```

**For Universal Format (Claude, ChatGPT, Cursor, etc.):**

1. **Verify Files Deployed**
```bash
ls rules/*.md | wc -l
```

2. **Add to AI Context**
   - **Claude Projects:** Upload `AGENTS.md`, `rules/RULES_INDEX.md`, and relevant `rules/*.md` files to project knowledge
   - **ChatGPT:** Add files to custom instructions or upload via file attachment
   - **Cursor:** Rules automatically discovered from project root
   - **Other LLMs:** Refer to specific tool documentation for context management

3. **Test Rule Loading**
   - Ask: "What rules are available for Snowflake development?"
   - AI should reference rules/RULES_INDEX.md and list rules
   - If not working, verify rules/RULES_INDEX.md is in context

### How to Verify Rules Are Working

**Test 1: Rule Discovery**
```
Prompt: "What rules are available for Snowflake development?"
Expected: AI references rules/RULES_INDEX.md and lists 100-series rules
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
ls rules/*.md | wc -l

# Check files in project root
cat AGENTS.md | head -20
cat rules/RULES_INDEX.md | head -20

# Test keyword search
grep -i "fastapi" rules/RULES_INDEX.md
grep -i "snowflake" rules/RULES_INDEX.md
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
make deploy DEST=~/ai-coding-rules-output

# Or use absolute path
make deploy DEST=/tmp/rules-output
```

3. **Fix Repository Permissions**
```bash
# If cloned repository has wrong permissions
chmod -R u+w .
```

### Give Specific Rules

While the ai_coding_rules system is designed to automatically load appropriate rules based on keywords and context, it's not a perfect system. As your conversation length and iterations increase, the overall utilization of your token count in the context window will increase. This does increase the likelihood that some of AGENTS.md is potentially lost from the context during compaction.

It is considered a best practice to include specific rule names in your prompt, particularly if you know they are relevant. If the agent does not show the list of rules you expect under RULES_LOADED, stop the agent and tell it to load additional rules or reevaluate which rules are loaded.

### MODE PLAN|ACT

Most of the LLMs and agentic tools will generally do a good job of following the MODE workflow established in AGENTS.md and rules/000-global-core.md. However, some LLMs have a tendency to stay in MODE: ACT even when they should fall back to MODE: PLAN. In such cases, stop the agent and tell it to resume MODE:PLAN. You can also explicitly add MODE:PLAN or MODE:ACT to any prompt to force the agent and LLM into the correct mode.

### Still Having Issues?

**Get Help:**
- **Check Issues:** [GitHub Issues](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)
- **Review Validation:** Run `make rules-validate` to check rule structure
- **Enable Debug Mode:** `make deploy-verbose DEST=~/path` for detailed output
- **Check Logs:** Review terminal output for specific error messages

**Common Fixes:**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Clear cache: `rm -rf .venv __pycache__`
- Reinstall dependencies: `make clean-venv && make env-sync`

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

**With make:**
```bash
# Deploy/update rules
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git /tmp/ai-rules
cd /tmp/ai-rules
uv sync --all-groups
make deploy DEST=~/my-project
```

**With ai-rules CLI directly:**
```bash
# Deploy/update rules using CLI
cd /tmp/ai-rules
uv sync --all-groups
uv run ai-rules deploy ~/my-project
```

**General:**
```bash
# Check rule count
ls rules/*.md | wc -l

# Search rules (rules/RULES_INDEX.md is in project root after deployment)
grep -i "keyword" rules/RULES_INDEX.md

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
| `rules/RULES_INDEX.md` | Searchable catalog | **Project root** |
| `000-global-core.md` | Foundation rules | `rules/` |
| All rule files | Specialized rules | `rules/` |
