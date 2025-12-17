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

Create a `memory-bank/` directory in your project root:

```bash
mkdir -p memory-bank
```

### 2. Initialize Memory Bank Structure

The recommended approach is to use the AI Coding Rules initialization protocol (see `rules/001-memory-bank.md`), but you can also create files manually:

```bash
# Core context files (as defined in rule 001-memory-bank.md)
touch memory-bank/activeContext.md
touch memory-bank/projectbrief.md
touch memory-bank/productContext.md
touch memory-bank/systemPatterns.md
touch memory-bank/techContext.md
touch memory-bank/progress.md
mkdir -p memory-bank/archive
```

### 3. Configure AI Assistant

Instruct your AI assistant to use Memory Bank:

```
At the start of each session, read all files in memory-bank/ to understand project context.
Before ending each session, update relevant memory-bank/ files with new decisions, patterns, or issues discovered.
```

## Memory Bank File Structure

The file structure follows the standard defined in `rules/001-memory-bank.md`:

| File | Purpose | Update Frequency | Size Limit |
|------|---------|-----------------|------------|
| `activeContext.md` | Current session focus, immediate next steps | Every session | ≤100 lines |
| `projectbrief.md` | Foundation reference: purpose, goals, constraints | Rarely (major changes) | ≤300 lines |
| `productContext.md` | Product vision, user value, key features | Occasionally | ≤200 lines |
| `systemPatterns.md` | Architecture decisions, design patterns | As patterns emerge | ≤400 lines |
| `techContext.md` | Technical stack, dependencies, tools | When tech changes | ≤300 lines |
| `progress.md` | Current state, roadmap, milestones | Weekly or per milestone | ≤200 lines |
| `archive/` | Historical context (subdirectory) | As needed | No limit |

> **Note:** For detailed guidance on file sizes, update triggers, and failure recovery, see `rules/001-memory-bank.md`.

## Usage Patterns

### Starting a Development Session

**Prompt your AI assistant:**

```
Load context from memory-bank/ directory. Summarize current project focus and any blocking issues.
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
- AI updates relevant `memory-bank/` files
- AI summarizes what was captured
- AI confirms context will persist

### Mid-Session Reference

**When AI seems to lose context:**

```
Re-read memory-bank/systemPatterns.md and memory-bank/techContext.md to understand the system design.
```

## Example: activeContext.md

```markdown
# Active Context (2025-01-20)

## Quick Start (Required - Lines 1-30)
**Current Objective:** Implement real-time WebSocket updates for customer dashboard

**Next 3 Steps:**
1. Complete WebSocket frontend integration (backend done, 60% frontend done)
2. Add Redis caching once cluster provisioned (blocked on DevOps)
3. Load testing with 1K concurrent connections

**Blockers:**
- Redis cluster provisioning (waiting on DevOps, requested 2025-01-18)
- WebSocket message format needs design review

**Validation Signal:** WebSocket connection successful + cache hit rate >80%

## Current Sprint (Week of 2025-01-20)
- Real-time WebSocket updates
- PostgreSQL query optimization (target: <100ms)
- Redis caching layer integration

## Recent Decisions (This Session)
- Using Socket.io for WebSocket (easier reconnection, see systemPatterns.md ADR-001)
- Redis pub/sub for broadcasting (see techContext.md)
- 30-second cache TTL (PM approved staleness for analytics)
```

## Example: projectbrief.md

```markdown
# Project Brief: Customer Analytics Dashboard

## Purpose
Real-time analytics dashboard for customer behavior tracking with sub-second response times

## Key Goals
1. Sub-second query response times (≤100ms target)
2. Support 10K concurrent users
3. 99.9% uptime SLA

## Constraints
- Budget: $50K/year infrastructure
- Timeline: MVP by Q2 2025
- Team: 5 engineers (2 backend, 2 frontend, 1 DevOps)

## Success Criteria
- Query response time: <100ms (P95)
- Concurrent users: 10K+ without degradation
- Uptime: 99.9% measured over 30 days
```

## Example: systemPatterns.md

```markdown
# System Patterns & Architecture Decisions

## ADR-001: Socket.io for WebSocket Communication

**Date:** 2025-01-18
**Status:** Accepted

**Context:** Need real-time dashboard updates. Native WebSocket vs Socket.io.

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
**Status:** Accepted

**Context:** PostgreSQL queries taking 200-500ms under load.

**Decision:** Redis with 30-second TTL

**Rationale:**
- 30-second staleness acceptable (verified with PM)
- Redis provides <1ms cache hits
- Reduces DB load by ~80% (estimated)

**Consequences:**
- Redis cluster needed (DevOps provisioning)
- Cache invalidation for user-triggered updates
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
- Commit `memory-bank/` files to git
- Helps team members understand project evolution
- Enables rollback to previous context if needed
- Consider `.gitignore` for `memory-bank/archive/` if it gets large

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
Read all files in memory-bank/ directory before proceeding.
```

### Issue: Memory Bank getting too large

**Solution:** Use the built-in archive system (see `rules/001-memory-bank.md` for archive policy):
```
memory-bank/
├── activeContext.md
├── projectbrief.md
├── productContext.md
├── systemPatterns.md
├── techContext.md
├── progress.md
└── archive/       # Historical context (auto-archived with timestamps)
```

### Issue: Team members out of sync

**Solution:** Add Memory Bank update to PR checklist:
```markdown
## Pull Request Checklist
- [ ] Code follows rules in rules/
- [ ] Tests pass
- [ ] Memory Bank updated in memory-bank/ (if architectural changes)
- [ ] activeContext.md reflects current state (if feature work)
```

## Advanced: Multi-Project Memory Bank

For organizations with multiple projects:

```
~/projects/
├── project-a/
│   └── memory-bank/
├── project-b/
│   └── memory-bank/
└── shared-memory-bank/      # Shared organizational context
    ├── team_conventions.md
    ├── infrastructure.md
    └── standards.md
```

Prompt AI to load both project-specific and global context:

```
Load context from:
1. memory-bank/ (project-specific)
2. ../shared-memory-bank/ (organizational standards)
```

## Support

- **Questions:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for support channels
- **Issues:** File bug reports or feature requests on GitHub
- **Rule Reference:** See [rules/001-memory-bank.md](../rules/001-memory-bank.md) for complete specification

---

**Ready to start?** Create `memory-bank/` directory and begin capturing your project context.

> **Tip:** Use the initialization protocol by telling your AI assistant: *"initialize memory bank"*
