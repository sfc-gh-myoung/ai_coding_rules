# Memory Bank System

> **Note:** This is an optional advanced feature for complex, long-running projects. Skip this section if you're just getting started with AI Coding Rules.

## Overview

The Memory Bank is a structured documentation system that helps AI assistants maintain context across multiple sessions. Since AI assistants reset between sessions, the Memory Bank provides continuity by capturing project state, architectural decisions, and current work focus.

## Key Benefits

- **Maintains project context** across development sessions
- **Captures architectural decisions** and technical patterns
- **Tracks active work** and known issues
- **Enables consistent AI assistance** on long-running projects

## When to Use

The Memory Bank is most valuable for:

- **Long-running projects** spanning multiple weeks or months
- **Complex architectures** requiring detailed documentation
- **Team collaboration** where AI context sharing matters
- **Multi-session development** where continuity is critical

## Setup

### 1. Enable Memory Bank in Your Project

Create a `.memory/` directory in your project root:

```bash
mkdir -p .memory
```

### 2. Initialize Memory Bank Structure

Create initial memory bank files:

```bash
# Project context
touch .memory/project_overview.md
touch .memory/architecture.md
touch .memory/current_focus.md

# Technical details
touch .memory/decisions.md
touch .memory/patterns.md
touch .memory/known_issues.md
```

### 3. Configure AI Assistant

Instruct your AI assistant to use Memory Bank:

```
At the start of each session, read all files in .memory/ to understand project context.
Before ending each session, update relevant .memory/ files with new decisions, patterns, or issues discovered.
```

## Memory Bank File Structure

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `project_overview.md` | High-level project description, goals, tech stack | Rarely (major changes only) |
| `architecture.md` | System architecture, component relationships | Occasionally (architectural changes) |
| `current_focus.md` | Active work, current sprint, immediate priorities | Frequently (each session) |
| `decisions.md` | Architectural Decision Records (ADRs) | Per decision |
| `patterns.md` | Code patterns, conventions, best practices | As patterns emerge |
| `known_issues.md` | Active bugs, technical debt, limitations | As issues are discovered/resolved |

## Usage Patterns

### Starting a Development Session

**Prompt your AI assistant:**

```
Load context from .memory/ directory. Summarize current project focus and any blocking issues.
```

**Expected response:**
- AI reads all Memory Bank files
- AI summarizes current state
- AI identifies what to work on next

### Ending a Development Session

**Prompt your AI assistant:**

```
Update Memory Bank with today's work:
- New architectural decisions
- Patterns discovered
- Issues encountered or resolved
- Updated focus for next session
```

**Expected response:**
- AI updates relevant `.memory/` files
- AI summarizes what was captured
- AI confirms context will persist

### Mid-Session Reference

**When AI seems to lose context:**

```
Re-read .memory/architecture.md and .memory/patterns.md to understand the system design.
```

## Example: project_overview.md

```markdown
# Project: Customer Analytics Dashboard

## Purpose
Real-time analytics dashboard for customer behavior tracking

## Tech Stack
- Frontend: React 18 + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL 15
- Deployment: Docker Compose

## Key Goals
1. Sub-second query response times
2. Support 10K concurrent users
3. 99.9% uptime SLA

## Team
- Backend: 2 developers
- Frontend: 2 developers
- DevOps: 1 engineer
```

## Example: current_focus.md

```markdown
# Current Focus (Week of 2025-01-20)

## Active Work
- Implementing real-time WebSocket updates for dashboard
- Optimizing PostgreSQL queries (target <100ms)
- Adding Redis caching layer

## Blockers
- Waiting on DevOps to provision Redis cluster
- Need design review for WebSocket message format

## Next Steps
1. Complete WebSocket integration (backend done, frontend in progress)
2. Add Redis caching once cluster is available
3. Load testing with 1K concurrent connections

## Recent Decisions
- Using Socket.io for WebSocket (easier reconnection logic)
- Redis pub/sub for WebSocket message broadcasting
- Caching query results for 30 seconds (trade-off between freshness and performance)
```

## Example: decisions.md

```markdown
# Architectural Decision Records

## ADR-001: Use Socket.io for WebSocket Communication

**Date:** 2025-01-18

**Context:** Need real-time updates for dashboard. Native WebSocket vs Socket.io.

**Decision:** Use Socket.io

**Rationale:**
- Automatic reconnection with exponential backoff
- Fallback to polling if WebSocket unavailable
- Better browser compatibility
- Rich event-based API

**Consequences:**
- Additional dependency (~50KB bundle size)
- Standardized WebSocket patterns across team

---

## ADR-002: Redis for Query Result Caching

**Date:** 2025-01-19

**Context:** PostgreSQL queries taking 200-500ms under load. Need caching layer.

**Decision:** Redis with 30-second TTL

**Rationale:**
- 30-second staleness acceptable for analytics (verified with PM)
- Redis provides <1ms cache hits
- Reduces DB load by ~80% (estimated)

**Consequences:**
- Need to provision Redis cluster (DevOps)
- Cache invalidation strategy needed for user-triggered updates
- Memory cost: ~2GB for 100K cached results
```

## Best Practices

### 1. Keep Files Focused
- Each file has a specific purpose
- Don't duplicate information across files
- Link between files when needed

### 2. Update Incrementally
- Update Memory Bank after significant decisions or discoveries
- Don't wait until end of session (risk forgetting details)
- Small, frequent updates better than large, infrequent ones

### 3. Use Consistent Formatting
- Markdown headers for structure
- Bullet points for lists
- Code blocks for examples
- Dates for time-sensitive information

### 4. Prune Regularly
- Archive resolved issues
- Remove outdated patterns
- Consolidate redundant decisions

### 5. Version Control
- Commit `.memory/` files to git
- Helps team members understand project evolution
- Enables rollback to previous context if needed

## Integration with AI Coding Rules

Memory Bank complements AI Coding Rules:

- **Rules** define HOW to write code (standards, patterns, best practices)
- **Memory Bank** captures WHAT you're building (project state, decisions, context)

**Combined workflow:**

1. **Start session:** AI loads Memory Bank (project context) + Rules (coding standards)
2. **Development:** AI follows Rules while working within project context
3. **End session:** AI updates Memory Bank with new decisions/patterns

## Troubleshooting

### Issue: AI not reading Memory Bank

**Solution:** Explicitly prompt AI to read files:
```
Read all files in .memory/ directory before proceeding.
```

### Issue: Memory Bank getting too large

**Solution:** Split into subdirectories:
```
.memory/
├── current/       # Active context (read every session)
├── archive/       # Historical context (reference as needed)
└── decisions/     # ADRs (reference by decision number)
```

### Issue: Team members out of sync

**Solution:** Add Memory Bank update to PR checklist:
```markdown
## Pull Request Checklist
- [ ] Code follows rules in rules/
- [ ] Tests pass
- [ ] Memory Bank updated (if architectural changes)
```

## Advanced: Multi-Project Memory Bank

For organizations with multiple projects:

```
~/projects/
├── project-a/
│   └── .memory/
├── project-b/
│   └── .memory/
└── .global-memory/          # Shared organizational context
    ├── team_conventions.md
    ├── infrastructure.md
    └── standards.md
```

Prompt AI to load both project-specific and global context:

```
Load context from:
1. .memory/ (project-specific)
2. ../.global-memory/ (organizational standards)
```

## Support

- **Questions:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for support channels
- **Issues:** File bug reports or feature requests on GitHub/GitLab
- **Examples:** See `.memory-examples/` directory in this repository (if available)

---

**Ready to start?** Create `.memory/` directory and begin capturing your project context.
