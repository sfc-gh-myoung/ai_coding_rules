# Rule Loader Skill

Determines which rule files to load for a given user request by analyzing file extensions, directory paths, and keywords against RULES_INDEX.md.

## Overview

This skill formalizes the rule-loading algorithm from AGENTS.md (Steps 1-3) into a reusable skill with progressive disclosure. It covers:

- **Foundation loading** - Always load 000-global-core.md
- **Domain matching** - File extension and directory-based rule selection
- **Activity matching** - Keyword-based rule discovery via RULES_INDEX.md
- **Dependency resolution** - Load prerequisites before dependent rules
- **Token budget management** - Defer low-priority rules when over budget

## Quick Start

### Step 1: Load the Skill

Use the `rule-loader` skill in your agent conversation.

### Step 2: Provide Context

```text
Use the rule-loader skill.

user_request: "Write tests for my Streamlit dashboard"
```

### Step 3: Review Output

The skill produces a `## Rules Loaded` section listing selected rules with loading reasons.

## Relationship to AGENTS.md

AGENTS.md contains the bootstrap protocol that invokes rule-loading logic inline. This skill provides:

- **Detailed workflow files** for each loading phase
- **Worked examples** showing the complete selection process
- **Test scenarios** for validating rule-loading behavior

AGENTS.md remains self-contained; this skill provides enriched reference material.

## File Structure

```
skills/rule-loader/
├── SKILL.md                        # Main entrypoint (~120 lines)
├── README.md                       # This file
├── workflows/
│   ├── foundation-loading.md       # Phase 1: Always-load foundation
│   ├── domain-matching.md          # Phase 2: File ext & directory matching
│   ├── activity-matching.md        # Phase 3: Keyword-based discovery
│   ├── dependency-resolution.md    # Phase 4: Load prerequisites
│   └── token-budget.md             # Phase 5: Budget management & deferral
├── examples/
│   ├── streamlit-dashboard.md      # Cross-domain: Streamlit + Python + test
│   ├── python-api.md               # Python + FastAPI endpoint
│   └── multi-domain.md             # Snowflake SQL + Python
└── tests/
    ├── README.md                   # Test overview
    └── test-scenarios.md           # Input/output test cases
```

## Troubleshooting

**Rules not loading as expected:**
1. Check RULES_INDEX.md for the keyword/extension mapping
2. Verify the rule file exists at the expected path
3. Check dependency chain - a missing prerequisite skips the dependent

**Token budget exceeded:**
- Low-tier rules are deferred first
- Check which rules are Critical vs Low tier in RULES_INDEX.md metadata
- Consider using `context_tier_filter` to pre-filter

**RULES_INDEX.md not found:**
- Skill falls back to foundation + file-extension matching only
- Regenerate with `task index:generate`
