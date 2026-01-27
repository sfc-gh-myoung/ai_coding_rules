# 001 Example: Memory Bank File Templates

> **EXAMPLE FILE** - Reference implementation for `001-memory-bank.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 001-memory-bank.md
**Demonstrates:** Complete memory bank file templates with size budgets for AI context preservation
**Use When:** Setting up a new memory bank system or resetting context files
**Version:** 1.0
**Last Validated:** 2026-01-27

## Prerequisites

- [ ] Project directory exists
- [ ] `memory-bank/` directory created (or will be created)
- [ ] Understanding of project scope and goals

## Implementation

### File Organization Overview

```
memory-bank/
├── activeContext.md    (≤100 lines) - MOST CRITICAL
├── projectbrief.md     (≤120 lines) - Foundation
├── productContext.md   (≤120 lines) - Vision
├── systemPatterns.md   (≤150 lines) - Architecture
├── techContext.md      (≤150 lines) - Stack
├── progress.md         (≤140 lines) - Status
└── archive/            (overflow storage)
    └── YYYY-MM.md

TOTAL BUDGET: ≤600 lines across all files
```

## Template: activeContext.md (≤100 lines)

```markdown
# Active Context

## Quick Start
**Current Objective:** [1-2 sentence description of primary goal]

**Next 3 Steps:**
1. [Specific, actionable task with clear deliverable]
2. [Specific, actionable task with clear deliverable]
3. [Specific, actionable task with clear deliverable]

**Active Blockers:** [List blockers or "None"]

**Validation Signal:** [How to verify current objective is complete]

## Current Work Focus

[≤2 paragraphs describing current sprint/iteration focus]

## Active Decisions

[Only decisions blocking current work - remove resolved decisions]

| Decision | Options | Status |
|----------|---------|--------|
| [Decision needed] | A, B, C | Pending |

## Dependencies & Blockers

[Current blockers only - archive resolved ones]

- [ ] [Blocker 1 - owner, ETA]
- [ ] [Blocker 2 - owner, ETA]

## Session Change Log

[≤5 most recent entries - archive older ones]

| Date | Change | Impact |
|------|--------|--------|
| YYYY-MM-DD | [Change description] | [Impact] |
```

## Template: projectbrief.md (≤120 lines)

```markdown
# Project Brief

## Overview

**Project Name:** [Name]
**Version:** [Current version]
**Status:** [Active/Maintenance/Planning]

## Core Requirements

### Must Have (P0)
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

### Should Have (P1)
- [Requirement 1]
- [Requirement 2]

### Nice to Have (P2)
- [Requirement 1]

## Scope Boundaries

### In Scope
- [What this project includes]

### Out of Scope
- [What this project explicitly excludes]

## Success Criteria

- [ ] [Measurable success criterion 1]
- [ ] [Measurable success criterion 2]
- [ ] [Measurable success criterion 3]

## Key Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| Owner | [Name] | [Responsibility] |
| Tech Lead | [Name] | [Responsibility] |

## Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| [Milestone 1] | YYYY-MM-DD | [Status] |
```

## Template: productContext.md (≤120 lines)

```markdown
# Product Context

## Why This Project Exists

[2-3 paragraphs explaining the problem being solved and why it matters]

## Target Users

### Primary Users
- **[User Type 1]:** [Description, needs, goals]
- **[User Type 2]:** [Description, needs, goals]

### Secondary Users
- **[User Type 3]:** [Description, needs, goals]

## User Experience Goals

### Core Experience
- [UX goal 1 - what users should feel/accomplish]
- [UX goal 2 - what users should feel/accomplish]

### Key Workflows
1. **[Workflow name]:** [Brief description]
2. **[Workflow name]:** [Brief description]

## Business Context

### Value Proposition
[1-2 sentences on unique value]

### Key Metrics
- [Metric 1]: [Target]
- [Metric 2]: [Target]

## Competitive Context

[Brief notes on alternatives and differentiation]
```

## Template: systemPatterns.md (≤150 lines)

```markdown
# System Patterns

## Architecture Overview

[High-level architecture description - 2-3 paragraphs max]

## Design Patterns in Use

### [Pattern Category 1]

**Pattern:** [Pattern name]
**Rationale:** [Why this pattern was chosen]
**Implementation:** [Brief implementation notes]

### [Pattern Category 2]

**Pattern:** [Pattern name]
**Rationale:** [Why this pattern was chosen]
**Implementation:** [Brief implementation notes]

## Component Relationships

```
[ASCII diagram or brief description of component relationships]
```

## Key Decisions

| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| [Decision 1] | [Choice made] | [Brief rationale] | YYYY-MM-DD |
| [Decision 2] | [Choice made] | [Brief rationale] | YYYY-MM-DD |

## Anti-Patterns to Avoid

- **[Anti-pattern 1]:** [Why to avoid]
- **[Anti-pattern 2]:** [Why to avoid]

## Integration Points

| System | Integration Type | Notes |
|--------|------------------|-------|
| [System 1] | [REST/Event/etc] | [Notes] |
```

## Template: techContext.md (≤150 lines)

```markdown
# Technical Context

## Technology Stack

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| Language | [e.g., Python] | [e.g., 3.11] | [Notes] |
| Framework | [e.g., Flask] | [e.g., 3.0] | [Notes] |
| Database | [e.g., Snowflake] | [N/A] | [Notes] |
| Cloud | [e.g., AWS] | [N/A] | [Notes] |

## Technical Constraints

- [Constraint 1 - e.g., "Must support Python 3.9+"]
- [Constraint 2 - e.g., "Max response time 200ms"]
- [Constraint 3 - e.g., "Must run in containerized environment"]

## Dependencies

### Production
- [dependency 1]: [purpose]
- [dependency 2]: [purpose]

### Development
- [dev dependency 1]: [purpose]
- [dev dependency 2]: [purpose]

## Essential Commands

```bash
# Development
[command]  # [description]

# Testing
[command]  # [description]

# Deployment
[command]  # [description]
```

## Environment Setup

[Brief setup instructions or link to detailed docs]

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| [VAR_NAME] | [Purpose] | [Default] |
```

## Template: progress.md (≤140 lines)

```markdown
# Progress

## Current State Summary

**Overall Status:** [On Track/At Risk/Blocked]
**Sprint:** [Current sprint number/name]
**Last Updated:** YYYY-MM-DD

## Recent Accomplishments

[Compressed list - 1 line per accomplishment, last 2 weeks only]

- [YYYY-MM-DD] [Accomplishment 1]
- [YYYY-MM-DD] [Accomplishment 2]
- [YYYY-MM-DD] [Accomplishment 3]

## Known Issues

[Current issues only - archive resolved ones]

| Issue | Severity | Owner | Status |
|-------|----------|-------|--------|
| [Issue 1] | High/Med/Low | [Name] | [Status] |

## Technical Debt

[Current debt items only]

- [ ] [Debt item 1 - brief description]
- [ ] [Debt item 2 - brief description]

## Immediate Roadmap

### This Sprint
- [ ] [Task 1]
- [ ] [Task 2]

### Next Sprint
- [ ] [Task 1]
- [ ] [Task 2]

### Following Sprint
- [ ] [Task 1]

## Metrics

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| [Metric 1] | [Value] | [Target] | ↑/↓/→ |
```

## Validation

After creating memory bank files:

```bash
# Check total line count (must be ≤600)
wc -l memory-bank/*.md | tail -1

# Check individual file sizes
wc -l memory-bank/activeContext.md   # ≤100
wc -l memory-bank/projectbrief.md    # ≤120
wc -l memory-bank/productContext.md  # ≤120
wc -l memory-bank/systemPatterns.md  # ≤150
wc -l memory-bank/techContext.md     # ≤150
wc -l memory-bank/progress.md        # ≤140
```

**Expected Results:**
- Total lines across all files ≤600
- Each file within its individual budget
- Quick Start section in activeContext.md contains all 4 required elements
- AI can resume work effectively using only these context files
