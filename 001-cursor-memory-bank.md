**Description:** Implementing a project-level memory bank for AI assistants across LLMs and IDEs.
**AutoAttach:** true
**Type:** Auto-attach
**Version:** 2.0
**LastUpdated:** 2025-09-17

# AI Assistant Memory Bank

## Purpose
Implement a comprehensive project-level memory bank system that enables AI assistants to maintain context and effectiveness across session resets, ensuring continuity of work through structured documentation and intelligent context management.

As an AI assistant, an expert software engineer with a unique characteristic: my memory resets completely between sessions. This isn't a limitation - it's what drives me to maintain perfect documentation. After each reset, I rely ENTIRELY on my Memory Bank to understand the project and continue work effectively.

- **Requirement:** Read ALL memory bank files at the start of EVERY task - this is not optional.
- **Rule:** Memory Bank accuracy directly determines work effectiveness after session resets.

## Rule Type and Scope

- **Type:** Auto-attach
- **Scope:** Project-level memory bank system for AI assistant context management and session continuity

## Key Principles

- **Rapid Recovery:** AI must be productive within first 20 lines of reading
- **Signal Maximization:** Every line must earn its place through actionable value
- **Forward-Looking Focus:** activeContext.md contains ONLY what's next, not what's done
- **Zero Redundancy:** Each piece of information lives in exactly ONE file
- **Aggressive Pruning:** Ruthlessly remove outdated or redundant content
- **Structured Communication:** Lists, tables, and bullets over narrative prose
- **Reference Over Duplication:** Link to existing docs rather than copying content
- **Temporal Boundaries:** Clear separation between current, recent, and historical context

## 1. Memory Bank Structure

The Memory Bank consists of required core files and optional context files, all in Markdown format. Files build upon each other in a clear hierarchy:

```mermaid
flowchart TD
    PB[projectbrief.md] --> PC[productContext.md]
    PB --> SP[systemPatterns.md]
    PB --> TC[techContext.md]
    
    PC --> AC[activeContext.md]
    SP --> AC
    TC --> AC
    
    AC --> P[progress.md]
```

### Core Files (Required)
- **Rule:** `projectbrief.md`
  - Foundation document that shapes all other files
  - Created at project start if it doesn't exist
  - Defines core requirements and goals
  - Source of truth for project scope

- **Rule:** `productContext.md`
  - Why this project exists
  - Problems it solves
  - How it should work
  - User experience goals

- **Rule:** `activeContext.md`
  - Current work focus
  - Recent changes
  - Next steps
  - Active decisions and considerations

- **Rule:** `systemPatterns.md`
  - System architecture
  - Key technical decisions
  - Design patterns in use
  - Component relationships

- **Rule:** `techContext.md`
  - Technologies used
  - Development setup
  - Technical constraints
  - Dependencies

- **Rule:** `progress.md`
  - What works
  - What's left to build
  - Current status
  - Known issues

### Additional Context
- **Consider:** Create additional files/folders within memory-bank/ when they help organize:
  - Complex feature documentation
  - Integration specifications
  - API documentation
  - Testing strategies
  - Deployment procedures

## 2. Performance Targets

### File Size Budgets
- **Critical:** Each memory bank file must meet specific line limits:
  - projectbrief.md: ≤120 lines (stable, scope only)
  - productContext.md: ≤120 lines (stable, vision only)  
  - activeContext.md: ≤100 lines (current + last session only)
  - systemPatterns.md: ≤150 lines (patterns and decisions)
  - techContext.md: ≤150 lines (stack and constraints)
  - progress.md: ≤140 lines (status and compressed history)

### Context Efficiency Targets
- **Mandatory:** Total memory bank ≤ 600 lines (20% reduction from baseline)
- **Rule:** Zero redundant information across files
- **Always:** Reference external files instead of duplicating content
- **Target:** AI productivity within 20 lines of reading

### Session Recovery Performance
- **Measurement:** Time from session start to first meaningful output
- **Target:** ≤ 1 minute for complex projects, ≤ 30 seconds for familiar projects
- **Method:** Quick Start protocol in activeContext.md

## 3. Core Workflows

### Plan Mode
```mermaid
flowchart TD
    Start[Start] --> ReadFiles[Read Memory Bank]
    ReadFiles --> CheckFiles{Files Complete?}
    
    CheckFiles -->|No| Plan[Create Plan]
    Plan --> Document[Document in Chat]
    
    CheckFiles -->|Yes| Verify[Verify Context]
    Verify --> Strategy[Develop Strategy]
    Strategy --> Present[Present Approach]
```

### Act Mode
```mermaid
flowchart TD
    Start[Start] --> Context[Check Memory Bank]
    Context --> Update[Update Documentation]
    Update --> Rules[Update .cursor/rules if needed]
    Rules --> Execute[Execute Task]
    Execute --> Document[Document Changes]
```

## 4. File Content Guidelines

### activeContext.md (≤100 lines) - MOST CRITICAL
**Structure Required:**
1. Quick Start section (lines 1-30)
2. Current work focus (≤2 paragraphs)
3. Active decisions (blocking current work only)
4. Dependencies & blockers (current only)
5. Session change log (≤5 entries)

**DO:**
- Start with Quick Start section (primary objective, next steps, validation)
- Keep only current + last session content
- Update after every task completion
- Archive older content to history/

**DON'T:**
- Include historical accomplishments (→ progress.md)
- Duplicate setup instructions (→ reference techContext.md)
- Keep completed work details (→ archive)
- Mix current focus with historical context

### systemPatterns.md (≤150 lines)
**DO:**
- Architecture decisions with rationale
- Key design patterns currently in use
- Technology choices (why, not how)
- Integration points and relationships

**DON'T:**
- Detailed code examples (→ reference README or code)
- Setup instructions (→ techContext.md)
- Historical decisions no longer relevant
- Implementation tutorials (→ external docs)

### techContext.md (≤150 lines)
**DO:**
- Technology stack list (table format)
- Key constraints (bullet points)
- Essential commands (table format)
- Development workflow (diagram/list)

**DON'T:**
- Detailed setup tutorials (→ reference README)
- Verbose explanations (→ use bullets)
- Duplicate architecture info (→ systemPatterns.md)
- Command examples (→ reference Taskfile)

### progress.md (≤140 lines)
**DO:**
- Current state summary (high-level)
- Compressed accomplishment log (one line per item)
- Known issues list (current technical debt)
- Immediate roadmap items (next 2-3 sprints)

**DON'T:**
- Detailed historical narratives (→ archive)
- Current focus (→ activeContext.md)
- Long-term roadmap (→ reference README)
- Verbose session logs (→ compress or archive)

## 5. Documentation Updates

- **Requirement:** Memory Bank updates occur when:
  1. Discovering new project patterns
  2. After implementing significant changes
  3. When user requests with **update memory bank** (MUST review ALL files)
  4. When context needs clarification

```mermaid
flowchart TD
    Start[Update Process]
    
    subgraph Process
        P1[Review ALL Files]
        P2[Document Current State]
        P3[Clarify Next Steps]
        P4[Update .cursor/rules]
        
        P1 --> P2 --> P3 --> P4
    end
    
    Start --> Process
```

- **Always:** When triggered by **update memory bank**, review every memory bank file, even if some don't require updates. Focus particularly on activeContext.md and progress.md as they track current state.

## 4. Project Intelligence (IDE Rules)

- **Rule:** The IDE-specific rules file (e.g., `.cursor/rules`, `.vscode/ai-rules/`) serves as a learning journal for each project.
- **Rule:** Capture important patterns, preferences, and project intelligence that help work more effectively.
- **Always:** Document key insights that aren't obvious from the code alone as work progresses.

```mermaid
flowchart TD
    Start{Discover New Pattern}
    
    subgraph Learn [Learning Process]
        D1[Identify Pattern]
        D2[Validate with User]
        D3[Document in .cursor/rules]
    end
    
    subgraph Apply [Usage]
        A1[Read .cursor/rules]
        A2[Apply Learned Patterns]
        A3[Improve Future Work]
    end
    
    Start --> Learn
    Learn --> Apply
```

### What to Capture
- **Always:** Document critical implementation paths
- **Always:** Record user preferences and workflow patterns
- **Always:** Note project-specific patterns and conventions
- **Always:** Track known challenges and solutions
- **Always:** Record evolution of project decisions
- **Always:** Document tool usage patterns

- **Rule:** Format is flexible - focus on capturing valuable insights that improve work effectiveness.
- **Rule:** Treat IDE rules as a living document that grows smarter over time.

- **Critical:** After every memory reset, work begins completely fresh. The Memory Bank is the only link to previous work.
- **Requirement:** Memory Bank must be maintained with precision and clarity, as effectiveness depends entirely on its accuracy.

## References

### External Documentation
- [Cursor Documentation](https://docs.cursor.com/) - AI-powered code editor features and capabilities
- [Cursor Rules Guide](https://docs.cursor.com/en/context/rules) - Project rules and context management
- [Professional Technical Writing](https://developers.google.com/tech-writing) - Google's technical writing standards and best practices
- [Markdown Guide](https://www.markdownguide.org/) - Complete Markdown syntax and formatting reference

### Related Rules
- **Global Core**: `000-global-core.md`
- **Rules Governance**: `002-cursor-rules-governance.md`
