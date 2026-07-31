# AI Coding Rules

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/license/apache-2-0)
![Version](https://img.shields.io/badge/version-3.8.0-blue)
[![CI](https://github.com/sfc-gh-myoung/ai_coding_rules/actions/workflows/ci.yml/badge.svg)](https://github.com/sfc-gh-myoung/ai_coding_rules/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-100%25%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/sfc-gh-myoung/ai_coding_rules)

> **One universal AI coding rule set for all AI assistants, IDEs, and agents. Portable, IDE-agnostic, built with Snowflake Cortex Code.**

## Quick Overview

**What:** Universal AI coding rule system working with any assistant/IDE  
**Works with:** Cursor, Claude Code, GitHub Copilot, VS Code, ChatGPT, and more  
**Install:** build the plugin, then install it with your assistant's plugin command  
**Benefit:** production-ready rules, automatic discovery, zero vendor lock-in

**Quick Checklist:**
- [ ] Prerequisites met? → [Prerequisites](#prerequisites)
- [ ] Ready to install? → [Quick Start](#quick-start)
- [ ] Want to understand first? → [Understanding Rules](#understanding-rules)
- [ ] Contributing rules? → [Contributing](#contributing)

## Overview

A universal AI coding rule system that works with any AI assistant, IDE, or development tool. Write rules once in a portable Markdown format and use them anywhere.

**What you get:** A library of engineering rules covering Python, SQL, Snowflake, Go, Docker, Shell scripting, React, HTMX, Alpine.js, data engineering, analytics, and project governance. The rules work with Cursor, Claude Code, GitHub Copilot, Visual Studio Code, and other AI coding assistants.

**Important:** Some rules are opinionated about naming conventions, project structure, the use of uv/uvx/ruff, and documentation standards. Review them and adjust to fit your team's practices.

## Key Features

- **194 rule files** covering Snowflake, Python, Go, React, HTMX, Alpine.js, Docker, Podman, Shell scripting, and project management.
- **Portable Markdown format** that works with Cursor, VS Code, Claude, ChatGPT, GitHub Copilot, and similar tools.
- **Automatic discovery** via semantic keyword matching (matches by meaning, not just exact text).
- **Explicit dependency chains** so rules load in the correct order.
- **Modular files** (150-500 lines) keep context-window usage low.
- **No vendor lock-in.** Plain Markdown with embedded metadata.

This project was inspired, in part, by:

- [Cursor Rules](https://cursor.com/docs/context/rules)
- [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [cline memory bank](https://docs.cline.bot/prompting/cline-memory-bank)

## Table of Contents

**For Users:**

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
- [License](#license)

**For Contributors:**

- [Contributing](#contributing)
- [Claude Agent Skills](#claude-agent-skills)
- [Development Commands](#development-commands)

## Prerequisites

Before getting started, ensure you have:

- **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
- **Git** (for cloning): [Install Git](https://git-scm.com/downloads)
- **uv** (Python package manager): [Install uv](https://docs.astral.sh/uv/)

**Quick check:**

```bash
python --version  # Should show 3.12 or higher
git --version     # Should show Git version
```

## Quick Start

**Get started in 3 steps:** clone, build the plugin, install it in your assistant.

### Clone this repository (choose one)

```bash
# GitHub HTTPS:
git clone https://github.com/sfc-gh-myoung/ai_coding_rules.git

# GitHub SSH:
git clone git@github.com:sfc-gh-myoung/ai_coding_rules.git
```

### Build the plugin

```bash
cd ai_coding_rules
uv sync --all-groups                 # Install dependencies
uv run ai-rules plugin build         # Assemble ai-coding-rules-plugin/
```

The build assembles a self-contained plugin directory:

| Component | Contents |
|-----------|----------|
| `skills/` | `rule-loader`, `show-rules` |
| `rules/` | The rule library, read by the hook when it matches a prompt |
| `hooks/` | `UserPromptSubmit` hook that performs discovery on every prompt |
| `micro_kernel_content.md` | Compact foundation injected into each prompt |
| `.cortex-plugin/plugin.json` | Manifest declaring the skills and the hook |

Validate the build before installing:

```bash
uv run ai-rules plugin verify
```

### Install the plugin

Installation is product-specific — follow your assistant's plugin documentation:

| Product | Reference |
|---------|-----------|
| CoCo CLI | [CoCo CLI plugins](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-plugins) |
| CoCo Desktop | [CoCo Desktop plugins](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/plugins) |
| Claude Code / Claude CoWork | [Claude plugins reference](https://code.claude.com/docs/en/plugins-reference) |

**Example — CoCo CLI:**

```bash
# Install from the local build
cortex plugin install ./ai-coding-rules-plugin

# Or install straight from git
cortex plugin install sfc-gh-myoung/ai_coding_rules

# Confirm it registered and is active
cortex plugin list
```

Use it without installing, for local development:

```bash
cortex --plugin-dir ./ai-coding-rules-plugin
```

Alternatively, place the built directory in `.cortex/plugins/` (CoCo) or
`.claude/plugins/` (Claude Code) inside your project to load it automatically.

> Already in a running session? Plugin changes are not picked up automatically.
> Run `/plugin reload`, or restart the assistant.
### Use in your AI assistant

Once the plugin is installed, rule discovery is automatic. On every prompt the
`UserPromptSubmit` hook scores your text against rule keywords, file extensions,
and paths, then injects a `<system-reminder>` containing the micro-kernel
foundation and the matched rule paths. The assistant reads the most relevant
rules (up to the 3-rule cap) and applies them.

There is nothing to load by hand and no per-project bootstrap file.

To see what was matched for a given prompt, invoke the bundled `$show-rules`
skill — it prints the PRE-FLIGHT gates and the rules that were cited.

**Next Steps:**

- Consider creating a `PROJECT.md` for project-specific guidance
- Understand how discovery works → [Understanding Rules](#understanding-rules)
- Modify or contribute → [Contributing](#contributing)
## Document Map: What to Read First

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Project overview, setup, usage | Start here (you are here) |
| **[rules/000-global-core.md](rules/000-global-core.md)** | Execution protocols (MODE, validation, workflows) | AI agents: after loading foundation |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Development guidelines, PR process | When contributing rules |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture, design decisions | When understanding internals or extending |
| **[docs/MEMORY_BANK.md](docs/MEMORY_BANK.md)** | Memory Bank system for long-running projects | When using Memory Bank (optional) |
| **[docs/EVALUATING_RULE_LOADER.md](docs/EVALUATING_RULE_LOADER.md)** | Rule Loading Evaluator: live-agent sanity check (pre-commit) for rule discovery + dependency loading | When changing rules, the hook, or fixtures |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history, changes | When checking updates |
| **[docs/USING_DEV_CLI.md](docs/USING_DEV_CLI.md)** | Development command reference (`ai-rules dev`) | When running tasks |

### Option: Git Submodule (Version Tracking)

Track rule updates via git submodule, then rebuild the plugin after each pull:

```bash
# From your project root
git submodule add https://github.com/sfc-gh-myoung/ai_coding_rules.git .ai-rules
cd .ai-rules && uv sync --all-groups && uv run ai-rules plugin build

# Update later
cd .ai-rules && git pull && uv run ai-rules plugin build
cortex plugin update ai-coding-rules
```

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

  User Task                    Hook + Agent Actions
  ─────────                   ──────────────────────

  📝 "Build a                 ┌──────────────────┐
   Snowflake                  │ 1. Hook fires    │◄─── UserPromptSubmit
   Streamlit                  │   on the prompt  │     (every prompt)
   dashboard"                 │                  │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 2. Score rules   │◄─── Keywords, file
                              │   deterministic  │     extensions, paths
                              │   matcher        │     ("Streamlit", .py)
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 3. Inject        │◄─── Micro-kernel +
                              │   system-        │     candidate rule
                              │   reminder       │     paths
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ 4. Agent reads   │◄─── Up to 3 rules,
                              │   and applies    │     plus required
                              │   rules          │     dependencies
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
2. **The hook fires** → `UserPromptSubmit` runs the deterministic matcher on your prompt
3. **Rules are scored** → keywords, file extensions, and paths rank candidate rules
4. **Context is injected** → a `<system-reminder>` carries the micro-kernel plus matched rule paths
5. **AI loads and applies** → reads the most relevant rules (up to 3) and their required dependencies

**Example keyword matching:**
- "Streamlit" → loads `101-snowflake-streamlit-core.md`
- "FastAPI" → loads `210-python-fastapi-core.md`
- "testing" → loads `206-python-pytest.md`

> **💡 Pro Tip: Keywords Drive Discovery**
>
> The `Keywords` metadata in each rule enables semantic search. When you say "optimize Streamlit performance,"
> the hook scores your prompt against rule keywords: "performance", "streamlit", "caching", "optimization".
>
> **This is why well-crafted prompts matter** - specific keywords help the AI load the most relevant rules.
> See [prompts/README.md](prompts/README.md) for effective prompt patterns.

See [docs/ARCHITECTURE.md → Rule Loading Workflow](docs/ARCHITECTURE.md#4-rule-loading-workflow) for complete technical details.

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
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                            Start: What are you building?                                 │
└────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                         │
        ┌────────────────┬───────────────┼───────────────┬────────────────┐
        │                │               │               │                │
        ▼                ▼               ▼               ▼                ▼
┌───────────────┐ ┌────────────┐ ┌──────────────┐ ┌─────────────┐ ┌─────────────┐
│   Snowflake   │ │ Python App │ │Infrastructure│ │   General   │ │  Frontend   │
└───────┬───────┘ └─────┬──────┘ └──────┬───────┘ └──────┬──────┘ └──────┬──────┘
        │               │               │                │               │
        ├─SQL/Pipeline  ├─FastAPI       ├─Docker         │               ├─React
        │ └►100-core    │ └►210-fastapi │ └►350-docker   └►000-global    │ └►440-react
        │               │               │                  (always       │
        ├─Streamlit     ├─Flask         ├─Shell/Bash       load first)   ├─TypeScript
        │ └►101-sis     │ └►250-flask   │ └►300-bash                     │ └►430-ts
        │  +101a,b,c    │               │                                │
        │               ├─CLI Tool      └─CI/CD                          └─JavaScript
        ├─Notebooks/ML  │ └►220-typer     └►803-git                        └►420-js
        │ └►109-nb      │
        │               └─Data Science
        └─AI/ML           └►920-analytics
          └►114-aisql
           +115-agents
           +116-search

Loading Order (Follow Dependencies):
1. Always load 000-global-core first
2. Load domain foundation (100-snowflake, 200-python, etc.)
3. Load specialized rules based on task
4. Check Depends field and load prerequisites (`required:` deps must load; `optional:` deps load when prompt benefits)
```

</details>

### Text-Based Rule Selection Guide

**Step 1: Identify your primary technology**

- **Snowflake** → Start with `100-snowflake-core.md`
- **Python** → Start with `200-python-core.md`
- **Shell/Bash** → Start with `300-bash-scripting-core.md`
- **Docker** → Start with `350-docker-core.md`
- **General** → Start with `000-global-core.md` (always load first)

**Step 2: Select your use case**

**Snowflake Projects:**
- SQL/Pipeline → `100-snowflake-core.md`
- Streamlit app → `101-snowflake-streamlit-core.md` (+ 101a for charts, 101b for performance)
- Notebooks/ML → `109-snowflake-notebooks.md`
- AI/ML features → `114-snowflake-cortex-aisql.md` (+ 115-snowflake-cortex-agents-core for agents, 116-snowflake-cortex-search for search)

**Python Projects:**
- FastAPI → `210-python-fastapi-core.md` (+ 210a for security if auth needed)
- Flask → `250-python-flask.md`
- CLI Tool → `220-python-typer-cli.md`
- Testing → `206-python-pytest.md`
- Data Science → `920-data-science-analytics.md`

**React/Frontend Projects:**
- React app → `440-react-core.md` (architecture, state management, styling)
- React + Python backend → `441-react-backend.md` (FastAPI/Flask integration, CORS, JWT)
- TypeScript → `430-typescript-core.md`
- JavaScript → `420-javascript-core.md`

**Go Projects:**
- Go app → `600-golang-core.md` (project structure, error handling, interfaces, testing, concurrency)

**Infrastructure Projects:**
- Docker → `350-docker-core.md`
- Shell scripting → `300-bash-scripting-core.md`
- CI/CD → `803-project-git-workflow.md`

**Step 3: Follow the dependency chain**

1. Always load `000-global-core.md` first (foundation)
2. Load domain foundation (e.g., `100-snowflake-core` or `200-python-core`)
3. Load specialized rules based on your task
4. Check the `Depends` field in each rule to load prerequisites (`required:` deps are mandatory; `optional:` deps are advisory)

**Step 4: Add specialized rules as needed**

Search for additional rules by keyword with `grep -ril "<keyword>" rules/` (testing, security, performance, etc.)

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

- **Real-world prompt examples**: four patterns for different task types
- **Keyword reference guide**: which keywords trigger which rules
- **Best practices**: tips for better AI results
- **Quick patterns**: copy-paste templates for common scenarios

**Quick preview:**

```
Task: Fix all Ruff linting errors in Python validation modules
Files: src/ai_rules/commands/validate.py, src/ai_rules/commands/index.py
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

## Claude Agent Skills

**This section is for developers working on the ai_coding_rules project or using project-maintenance skills in their own workflows.**

The `skills/` directory contains structured Claude Agent Skills following [Anthropic's Agent Skills best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). The skills that remain in this repository are specific to maintaining AI Coding Rules, validating rule quality, managing staged changes and release notes, and operating the repository's development workflow. Broadly reusable skills have moved to the external portable-skills repository.

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
Install the plugin and these skills are registered automatically. Alternatively, copy a skill directory into `.claude/skills/` (project or personal), or tell Claude Code to load it explicitly.

You can also use these skill by telling Claude Code to explicitly load the skill in your prompt.
- Prompt: `Load skills/<skill_name>/SKILL.md`

#### Cortex Code CLI
You can use these skills in Cortex Code CLI by running the skill add command.
- Prompt: `/skill add <project_path>/skills/<skill_name>`

You can also use these skills by telling Cortex Code CLI to explicitly load the skill in your prompt.
- Prompt: `Load skills/<skill_name>/SKILL.md`

#### Local Project Skills

These skills are intended for the ai_coding_rules project maintenance workflow:

| Skill | Purpose | Guide | Skill file |
|---|---|---|---|
| `bulk-rule-reviewer` | Review every rule under `rules/` and consolidate prioritized findings. | [docs/USING_BULK_RULE_REVIEWER_SKILL.md](docs/USING_BULK_RULE_REVIEWER_SKILL.md) | [skills/bulk-rule-reviewer/SKILL.md](skills/bulk-rule-reviewer/SKILL.md) |
| `rule-creator` | Create new rule files from templates with schema validation. | [docs/USING_RULE_CREATOR_SKILL.md](docs/USING_RULE_CREATOR_SKILL.md) | [skills/rule-creator/SKILL.md](skills/rule-creator/SKILL.md) |
| `rule-loader` | Select, load, and troubleshoot rules for agent tasks. | [docs/USING_RULE_LOADER_SKILL.md](docs/USING_RULE_LOADER_SKILL.md) | [skills/rule-loader/SKILL.md](skills/rule-loader/SKILL.md) |
| `rule-reviewer` | Review rule files for agent executability and schema quality. | [docs/USING_RULE_REVIEWER_SKILL.md](docs/USING_RULE_REVIEWER_SKILL.md) | [skills/rule-reviewer/SKILL.md](skills/rule-reviewer/SKILL.md) |
| `skill-timer` | Measure skill execution time and maintain timing baselines. | [docs/USING_SKILL_TIMER_SKILL.md](docs/USING_SKILL_TIMER_SKILL.md) | [skills/skill-timer/SKILL.md](skills/skill-timer/SKILL.md) |

## CLI Commands

The `ai-rules` CLI provides the following commands for rules management:

```bash
# Show help and all available commands
uv run ai-rules --help
```

| Command | Description |
|---------|-------------|
| `ai-rules validate` | Validate rule files against v3.5 schema |
| `ai-rules tokens` | Validate/update TokenBudget metadata; `--context-estimate` reports total per-response context |
| `ai-rules new` | Generate new rule file from v3.5 template |
| `ai-rules badges` | Update README badges (version, tests, coverage) |
| `ai-rules dev` | Development orchestration (replaces former Makefile) |
| `ai-rules plugin` | Build the distributable `ai-coding-rules-plugin/` |
| `ai-rules rule-loader` | Rule Loading Evaluator: live-agent sanity check |
| `ai-rules rule-loader keywords` | Suggest/update keywords via Snowflake Cortex (AI_COMPLETE) |

## Development Commands

Run `uv run ai-rules --help` to see the top-level commands or `uv run ai-rules dev --help` for the development sub-app. Common commands:

```bash
uv run ai-rules dev quality all --fix    # Fix all code quality issues
uv run ai-rules dev test run             # Run all pytest tests
uv run ai-rules dev validate             # Run all CI/CD checks
uv run ai-rules plugin build             # Build the distributable plugin
uv run ai-rules --debug dev validate     # Show Python tracebacks for CLI failures
```

**See [docs/USING_DEV_CLI.md](docs/USING_DEV_CLI.md) for complete development command reference.**

## Rule Categories

The rules are organized by domain using a three-digit numbering system. Each category focuses on a specific technology or practice area.

| Domain | Range | # Rules | Focus Area | Key Topics |
|--------|-------|---------|------------|------------|
| **Core Foundation** | 000-099 | 22 | Universal patterns | Operating principles, memory bank, rule governance, context engineering, tool design, skills, model optimization |
| **Snowflake** | 100-199 | 86 | Data platform | SQL, Streamlit, performance, Cortex AI, security, notebooks, pipelines, demo creation, data quality, dynamic tables, Cortex Code Agent SDK |
| **Python** | 200-299 | 44 | Software engineering | Core patterns, FastAPI, Flask, Typer CLI, Pydantic, pytest, Pandas, **HTMX**, datetime, Faker |
| **Shell/Containers** | 300-399 | 13 | Automation & Infrastructure | Bash and Zsh scripting, security, testing, Docker, **Podman** |
| **Frontend (JS/TS)** | 400-499 | 9 | Client-side frameworks | JavaScript, TypeScript, React, Alpine.js, **HTMX frontend** |
| **Frontend** | 500-599 | 3 | Client-side | HTMX frontend, browser globals |
| **Systems/Backend Languages** | 600-699 | 2 | Backend development | **Go/Golang** core patterns, advanced patterns, error handling, concurrency |
| **Reserved** | 700-799 | 0 | Future use | Reserved for future domain expansion |
| **Project Management** | 800-899 | 10 | Workflows | Git, changelog, README, contributing, CLI design, Taskfile, Makefile-rule-authoring |
| **Analytics & Governance** | 900-999 | 5 | Business intelligence | Data science, data governance, business analytics, semantic views, dbt |

**Browse rules:** see the [Rule Categories](#rule-categories) table above, or `grep -ril "<keyword>" rules/` to search by keyword.

## Directive Language Hierarchy

The rules use a structured directive language (Critical, Mandatory, Always, Requirement, Rule, Consider) with clear priority levels to guide AI agents and developers.

**See [CONTRIBUTING.md → Directive Language](CONTRIBUTING.md#directive-language) for the canonical hierarchy, informational directives, and usage examples.**

## AI Configuration

Once the plugin is installed, AI assistants discover and load relevant rules automatically on every prompt — there is nothing to deploy per project. For complete details, see [docs/ARCHITECTURE.md → Rule Loading Workflow](docs/ARCHITECTURE.md#4-rule-loading-workflow).

**Quick example:**

```
User: "Build a Snowflake Streamlit dashboard"
AI loads: 000-global-core → 100-snowflake-core → 101-snowflake-streamlit-core
```

### Manual Rule Management

**Search for rules by keyword:**

```bash
grep -ril "performance" rules/
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

### Plugin Build Produces No Rules

**Problem:** `ai-coding-rules-plugin/rules/` is empty or missing after a build

**Solutions:**

1. **Verify Python Version**

```bash
python --version
# Must be 3.12 or higher
```

1. **Install Dependencies**

```bash
uv run ai-rules dev env sync
# OR directly:
uv sync --all-groups
```

1. **Check for Errors**

   - Review terminal output for error messages
   - Look for permission issues or missing dependencies

2. **Try Direct CLI**

```bash
# Rebuild and validate the plugin
uv run ai-rules plugin build && uv run ai-rules plugin verify
```

1. **Verify Project Structure**

```bash
# Check required files exist
ls src/ai_rules/cli.py rules/
```

### Python Version Conflicts

**Problem:** Wrong Python version or dependency conflicts

**Solutions:**

1. **Check Python Version**

```bash
python --version
python3 --version
# Need 3.12 or higher
```

1. **Use uv to Pin Version**

```bash
uv run ai-rules dev env setup
# Creates .python-version file pinning to 3.12
```

1. **Clean and Reinstall**

```bash
uv run ai-rules dev clean venv --force    # Remove virtual environment
uv run ai-rules dev env sync               # Reinstall dependencies
```

1. **Manual venv Setup (fallback)**

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows

pip install -e ".[dev]"
```

### IDE Not Recognizing Rules

If an assistant is not applying rules, ask it explicitly:

```text
Run the rule-loader skill for my prompt and cite the rules you load.
```

**For Universal Format (Claude, ChatGPT, Cursor, etc.):**

1. **Confirm the plugin is active**

```bash
cortex plugin list
```

1. **Add rules to context (assistants without plugin support)**
   - **Claude Projects:** upload the relevant `rules/*.md` files to project knowledge
   - **ChatGPT:** Add files to custom instructions or upload via file attachment
   - **Cursor:** install the plugin, or load a rule explicitly in your prompt
   - **Other LLMs:** Refer to specific tool documentation for context management

2. **Test Rule Loading**
   - Ask: "What rules are available for Snowflake development?"
   - AI should cite the matched rules under RULES_LOADED
   - If not, run `/plugin reload` and confirm `cortex plugin list` shows the plugin active

### How to Verify Rules Are Working

**Test 1: Rule Discovery**

```
Prompt: "What rules are available for Snowflake development?"
Expected: AI cites 100-series Snowflake rules under RULES_LOADED
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
# Verify the rule library is present in the built plugin
ls ai-coding-rules-plugin/rules/*.md | wc -l

# Confirm the manifest and hook shipped
cat ai-coding-rules-plugin/.cortex-plugin/plugin.json
ls ai-coding-rules-plugin/hooks/
```

### Plugin Not Loading

**Problem:** The plugin is installed but rules are not being injected

**Solutions:**

1. **Confirm the plugin is registered and active**

```bash
cortex plugin list
```

1. **Validate the manifest and components**

```bash
uv run ai-rules plugin verify
```

1. **Reload the plugin runtime**

Plugin changes are not picked up by running sessions. Run `/plugin reload` in the
session, or restart the assistant.

1. **Verify the hook prerequisites**

The `UserPromptSubmit` hook is a shell script requiring `jq` and `python3` on
`PATH`. Both must be available to the process running the assistant.

### Give Specific Rules

While discovery is automatic, it is not perfect. As a conversation grows, more
of the context window is consumed and injected rule content can be displaced
during compaction.

It is good practice to name specific rules in your prompt when you know they are
relevant. If the assistant does not cite the rules you expect, stop it and ask it
to load the additional rules or re-run discovery.

### Confirming which rules loaded

If the assistant does not cite the rules you expect, invoke the `$show-rules`
skill to print the PRE-FLIGHT gates for the current prompt. That shows which
rules the hook matched and which the assistant actually read.

### Still Having Issues?

**Get Help:**
- **Check Issues:** [GitHub Issues](https://github.com/sfc-gh-myoung/ai_coding_rules/issues)
- **Review Validation:** Run `uv run ai-rules validate rules/` to check rule structure
- **Verify the Plugin:** `uv run ai-rules plugin verify` to surface a missing or undeclared build artifact, or an unparseable manifest
- **Check Logs:** Review terminal output for specific error messages

**Common Fixes:**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Clear cache: `uv run ai-rules dev clean cache`
- Reinstall dependencies: `uv run ai-rules dev clean venv --force && uv run ai-rules dev env sync`

## Author

**Michael Young** — Snowflake
- Email: michael.young@snowflake.com
- GitHub: [@sfc-gh-myoung](https://github.com/sfc-gh-myoung)

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
