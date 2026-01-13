# Universal Memory Bank System

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** memory bank, context, session recovery, project brief, active context, progress tracking, context rot, attention budget, compaction, context engineering, rapid recovery, failure recovery, staleness detection, archive policy, signal maximization
**TokenBudget:** ~7100
**ContextTier:** Critical
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Universal principles for maintaining project context through structured memory bank documentation. Establishes patterns for context recovery across session resets, context preservation, aggressive pruning, and attention budget management. All write operations must be scoped to `memory-bank/` directory only.

**When to Load This Rule:**
- Implementing or maintaining memory bank systems
- Managing project context across session resets
- Setting up context preservation for AI agents
- Designing documentation structure for rapid recovery
- Working with `memory-bank/` directory operations

**Scope Boundary (CRITICAL):**
- **This rule governs:** Write operations to `memory-bank/` directory ONLY
- **Out of scope:** IDE/editor rule files, project files outside `memory-bank/`, IDE configuration
- **Rationale:** Agents need unambiguous write permission boundary to prevent unintended side effects

**Context Preservation:**
For overall context preservation strategy and priority order, see `000-global-core.md` section "Context Window Management Protocol" and `AGENTS.md` Bootstrap protocol. Memory bank patterns complement but do not replace the core preservation hierarchy.

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundational workflow, safety protocols, and Context Window Management Protocol

**Related:**
- **002-rule-governance.md** - Token budgets and rule sizing standards
- **003-context-engineering.md** - Comprehensive attention budget and compaction strategies

### External Documentation

**Anthropic Engineering Articles:**
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) - Context rot, attention budgets, compaction strategies, and memory management

**Technical Writing and Documentation:**
- [Technical Writing Best Practices](https://developers.google.com/tech-writing) - Google's guide for clear, effective documentation
- [Documentation Systems](https://docs.divio.com/documentation-system/) - Framework for organizing technical documentation
- [Cursor Documentation](https://cursor.com/docs) - AI-powered code editor features and capabilities
- [Cursor Rules Guide](https://cursor.com/docs) - Project rules and context management
- [Markdown Guide](https://www.markdownguide.org/) - Complete Markdown syntax and formatting reference

## Contract

### Inputs and Prerequisites

- Project context files
- Clear documentation structure
- Understanding of session reset scenarios
- Knowledge of memory bank file organization

### Mandatory

- Read-only context tools
- Documentation tools
- Structured update tools
- **CRITICAL:** ALL writes must be scoped to `memory-bank/` directory only

### Forbidden

- Tools that duplicate information across contexts
- Unstructured narrative documentation
- Writing files outside `memory-bank/` directory
- Skipping initialization check before first write

### Execution Steps

1. Initialize memory bank if needed (see Initialization Protocol in Section 4); all write operations must be scoped under `memory-bank/` only
2. Read ALL memory bank files at session start (non-optional)
3. Maintain single source of truth per information type
4. Update context when update triggers are met (see Context Update Triggers)
5. Prune outdated information aggressively (see Aggressive Pruning Rules)
6. Structure information for rapid context recovery

### Output Format

Structured documentation with:
- Clear sections
- Minimal redundancy
- Forward-looking focus
- Quick Start information in first 30 lines of activeContext.md

### Validation

**Pre-Task-Completion Checks:**
- `memory-bank/` folder exists (initialization verified)
- No writes occurred outside `memory-bank/` directory
- Context completeness check passed
- Information uniqueness verification passed
- Quick Start Requirements met (see Performance Standards)

**Success Criteria:**
- Initialization confirmed
- AI can resume work effectively using only context files
- No duplicate information exists
- All references work
- Context load completes within time targets

**Investigation Required:**
1. **Check if `memory-bank/` directory exists BEFORE any write operation** - Use list_dir to verify, run initialization if missing
2. **Read ALL existing memory bank files at session start** - Never assume context structure
3. **Never speculate about current project state** - Read activeContext.md for actual current focus
4. **Verify file sizes against budgets** - Check line counts, not just file existence
5. **Make grounded updates based on investigated context** - Don't add generic content

**Anti-Pattern:** "Based on typical projects, you probably have these memory bank files..."

**Correct Pattern:** "Let me check if memory-bank/ exists and what files are present." [runs list_dir]

### Design Principles

- **Rapid Recovery:** AI must be productive within first 20-30 lines of reading (Quick Start Requirements: objective, next 3 steps, blockers, validation)
- **Signal Maximization:** Every line must provide actionable value
- **Zero Redundancy:** Each piece of information lives in exactly one place
- **Aggressive Pruning:** Remove outdated or redundant content ruthlessly
- **Structured Communication:** Use lists, tables, and bullets over narrative prose
- **Reference Over Duplication:** Link to existing documentation rather than copying
- **Temporal Boundaries:** Separate current, recent, and historical context clearly
- **Forward Focus:** Emphasize what's next, not what's done
- **Context Rot Awareness:** As context grows, attention degrades (n² pairwise relationships) - keep context minimal
- **Attention Budget:** Treat context like limited working memory - every token depletes attention budget

### Post-Execution Checklist

- [ ] All core memory bank files exist and are within size budgets
- [ ] Initialization run before updates (or previously initialized)
- [ ] `memory-bank/` directory exists
- [ ] All writes are scoped under `memory-bank/` (no writes elsewhere)
- [ ] activeContext.md updated when update triggers met
- [ ] No information duplication across contexts
- [ ] Quick start information readily accessible in activeContext.md
- [ ] Outdated content removed or archived appropriately
- [ ] All references and links are current and functional
- [ ] Context structure follows hierarchical dependencies
- [ ] Forward-looking focus maintained (what's next vs what's done)
- [ ] Essential commands and workflows documented in techContext.md
- [ ] AI can resume work effectively using only context files

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Context Pollution Through Over-Documentation

**Problem:** Adding excessive detail to memory bank files, treating them as comprehensive logs rather than focused context.

**Why It Fails:** Causes "context rot" - as context grows, LLM attention degrades due to n² pairwise relationships. Verbose context buries critical information, slowing session recovery and reducing AI effectiveness.

**Correct Pattern:**
```markdown
# activeContext.md - GOOD (focused, actionable)
## Quick Start
- Primary: Implement user auth module
- Blocked: Waiting on API keys from DevOps
- Next: Write unit tests after unblocked

# activeContext.md - BAD (verbose, unfocused)
## Session Log
Yesterday we discussed authentication approaches. John suggested OAuth2.
We reviewed 5 different libraries. Sarah mentioned security concerns...
[50 more lines of narrative]
```

### Anti-Pattern 2: Stale Memory Without Pruning

**Problem:** Never removing completed work, resolved blockers, or outdated decisions from active context files.

**Why It Fails:** Memory bank becomes archaeological record rather than working context. AI wastes tokens processing irrelevant historical information, and outdated context can mislead current decisions.

**Correct Pattern:**
```markdown
# Maintenance workflow
1. After task completion: Remove task details, keep only outcome summary
2. Weekly: Archive per Archive Policy (see Section 3)
3. Per session: Verify activeContext.md ≤100 lines

# Before: 250 lines of accumulated context
# After pruning: 80 lines of current, actionable context
```

## Output Format Examples

```markdown
MODE: [PLAN|ACT]

## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/001-memory-bank.md (context)
- [additional rules based on task]

Analysis:
[Brief analysis of the requirement]

Task List:
1. [Specific task with clear deliverable]
2. [Another task with validation criteria]
3. [Final task with success metrics]

Implementation:
[Code/configuration changes following established patterns]

Validation:
- [x] Changes validated against requirements
- [x] Tests passing / linting clean
- [x] Documentation updated
```

## Universal Context Structure

### Core Information Types
- **Project Brief**: Foundation, scope, and requirements (stable reference)
- **Active Context**: Current work, immediate next steps, blocking issues (most critical)
- **Technical Context**: Stack, constraints, essential commands (stable reference)
- **System Patterns**: Architecture decisions and design patterns in use (evolving reference)
- **Progress Tracking**: Status, accomplishments, known issues (dynamic status)
- **Product Context**: Why project exists, problems solved, user experience goals (stable vision)

### File Organization Principles

**File Dependencies:**
- **projectbrief.md** (foundation): Informs productContext.md, systemPatterns.md, techContext.md
- **productContext.md, systemPatterns.md, techContext.md**: Inform activeContext.md
- **activeContext.md**: Informs progress.md

**File Structure:**
- **Single Purpose**: Each file serves one specific context type
- **Clear Hierarchy**: Dependencies and relationships between contexts are explicit
- **Bounded Size**: Each context file maintains specific size limits
- **Forward Focus**: Current context emphasizes what's next, not what's done

## Content Guidelines

### Core Files (Required)

#### activeContext.md (≤100 lines) - MOST CRITICAL
**Structure Required:**
1. Quick Start section (lines 1-30)
2. Current work focus (≤2 paragraphs)
3. Active decisions (blocking current work only)
4. Dependencies & blockers (current only)
5. Session change log (≤5 entries)

**Content Rules:**
- Current + last session only; archive older content
- Start with Quick Start section (primary objective, next steps, validation)
- Update when update triggers are met (see Context Update Triggers in Section 4)
- Remove completed work details (archive them)

#### projectbrief.md (≤120 lines)
- Foundation document defining core requirements and project scope
- Source of truth for project boundaries and goals
- Stable reference document (rarely changes)

#### productContext.md (≤120 lines)
- Why this project exists and problems it solves
- User experience goals and success criteria
- Business context and value proposition

#### systemPatterns.md (≤150 lines)
- System architecture and key technical decisions
- Design patterns currently in use with rationale
- Component relationships and integration points

#### techContext.md (≤150 lines)
- Technology stack (table format preferred)
- Technical constraints and dependencies
- Essential commands and development workflow
- Reference setup instructions rather than duplicating them

#### progress.md (≤140 lines)
- Current state summary and compressed accomplishments
- Known issues and technical debt (current only)
- Immediate roadmap (next 2-3 sprints maximum)

## Performance Standards

### Size Budgets (Mandatory)

All memory bank files must stay within these limits:

**File Size Budgets:**

**activeContext.md:** 100 lines max
- Priority: CRITICAL
- Content: Current + last session only
- Enforcement: Check before every commit

**projectbrief.md:** 120 lines max
- Priority: High
- Content: Stable foundation reference
- Enforcement: Check on major updates

**productContext.md:** 120 lines max
- Priority: High
- Content: Stable vision reference
- Enforcement: Check on major updates

**systemPatterns.md:** 150 lines max
- Priority: High
- Content: Architectural decisions
- Enforcement: Check when adding patterns

**techContext.md:** 150 lines max
- Priority: Medium
- Content: Technical stack reference
- Enforcement: Check on stack changes

**progress.md:** 140 lines max
- Priority: Medium
- Content: Current state + roadmap
- Enforcement: Check weekly

**Total (all files):** 600 lines max
- Priority: CRITICAL
- Enforcement: Check before every commit

**Enforcement Procedure:**
1. Check file sizes before every commit to memory bank
2. If file exceeds budget: Apply compaction rules (see Context Compaction Strategies)
3. If total exceeds 600: Archive oldest content first, then compress
4. Validation command: `wc -l memory-bank/*.md | tail -1` (total should be ≤600)

### Efficiency Targets
- **Context Load Time**: AI productive within 20 lines of reading (see Quick Start Requirements below)
- **Information Density**: Every line provides actionable value
- **Update Frequency**: Balance currency with maintenance overhead
- **Reference Accuracy**: All links and references remain current
- **Session Recovery Targets:**

**Complex Projects:** Target recovery ≤ 60 seconds
- Criteria: >4 memory bank files OR >400 total lines

**Standard Projects:** Target recovery ≤ 30 seconds
- Criteria: ≤4 files AND ≤400 lines

**Measurement:** Time from session start to first productive action (code edit or substantive response)

**Quick Start Requirements (Lines 1-30 of activeContext.md):**

Must include ALL of these elements:
- [ ] Current objective (1-2 sentences)
- [ ] Next 3 concrete steps
- [ ] Active blockers (or "None")
- [ ] Validation signal (success criteria)

**Format Example:**
```markdown
## Quick Start
**Current Objective:** [Concise statement]
**Next 3 Steps:**
1. [Specific action]
2. [Specific action]
3. [Specific action]
**Active Blockers:** [List or "None"]
**Validation Signal:** [How to verify success]
```

### Context Compaction Strategies

**Why Compaction Matters:**
From Anthropic's context engineering research, as context length increases, models experience "context rot" - diminished ability to recall specific information due to n² pairwise attention relationships. Compaction helps maintain model effectiveness.

**When to Compact:**
- Any memory bank file within 10 lines of its size budget
- activeContext.md contains content from >2 sessions
- Completed work details exceed 30 lines total
- ≥3 resolved blockers still documented in detail
- Total context >540 lines (90% of 600-line budget)

**Aggressive Pruning Rules (Mandatory):**

Apply these rules deterministically to maintain size budgets:

**Temporal Rules:**

- **Completed work details (>7 days):** Condense to 1-line summary
- **Completed work summary (>30 days):** Archive to memory-bank/archive/YYYY-MM.md
- **Resolved blocker (>14 days):** Remove entirely
- **Session logs (>14 days):** Archive to memory-bank/archive/YYYY-MM.md
- **Decision rationale (>30 days):** Keep outcome only, remove discussion

**Content Type Rules:**

- **File references for deleted project files:** Remove entirely
- **Duplicate status updates:** Keep most recent only
- **Verbose explanations (>5 lines):** Condense to bullets
- **Tool output logs after issue resolved:** Remove
- **Superseded information:** Remove immediately

**Volume Rules:**

- **Individual task details >10 lines:** Condense to 1-3 lines
- **Session change log >5 entries:** Keep most recent 5, archive rest
- **Blocker descriptions >5 lines (after resolved):** Condense to 1-2 lines

**Preservation Exceptions (Never Prune):**

- **Architectural decisions:** Keep indefinitely in systemPatterns.md
- **Core requirements:** Keep in projectbrief.md (stable reference)
- **Active blockers (unresolved):** Keep full details regardless of age
- **Current session work:** Keep full details until session ends
- **Stable references:** projectbrief.md, techContext.md, productContext.md exempt from temporal pruning

**Compaction Techniques:**

**1. Summarize Completed Work:**
```markdown
# Before Compaction (50 lines)
### Sprint 3 Details
- Implemented user authentication with bcrypt
- Created 15 unit tests for auth module
- Fixed 3 edge cases in password validation
- Updated documentation for auth API
- Reviewed PR feedback and made 8 commits
- Final merge on Jan 15th

# After Compaction (3 lines)
### Sprint 3 (Completed Jan 15)
- User authentication with bcrypt (15 tests, fully documented)
```

**2. Archive to External Files:**
- Move detailed historical context to `memory-bank/archive/YYYY-MM.md`
- Keep only summary references in active context
- Load archived details only when specifically needed

**3. Consolidate Redundant Information:**
- Merge duplicate status updates
- Remove repeated decisions already documented
- Collapse verbose explanations to bullet points

**4. Progressive Detail Decay:**
```
Current session (0-1 days old):    Full details
Last 1-2 sessions (1-7 days):      Summaries (3-5 lines per task)
Last 2-4 weeks (7-30 days):        Key decisions only (1 line each)
Older than 30 days:                Archive or remove
```

**Compaction Guidelines:**
- **Preserve:** Active objectives, unresolved blockers, key architectural decisions, recent file references
- **Remove:** Resolved issues, exploratory dead-ends, redundant tool outputs, verbose explanations
- **Compress:** Completed tasks (outcomes only), historical decisions (rationale + result), old session logs

### Staleness Detection Rules

Content is classified as **"outdated"** when it meets ANY of these criteria:

**Temporal Staleness:**
- Last modified >30 days ago (except stable references: projectbrief.md, techContext.md, productContext.md)
- References work completed >14 days ago
- Describes blockers resolved >7 days ago
- Session logs from >14 days ago
- Status updates superseded by newer information

**Content Staleness:**
- File references pointing to deleted project files
- Tool versions upgraded (old version no longer in use)
- Deprecated patterns no longer followed
- Decision discussions where final decision documented elsewhere
- Temporary workarounds replaced with permanent solutions

**Structural Staleness:**
- Duplicate information in newer sections
- Information contradicts current project state
- Section headers without content (obsolete placeholders)
- Broken cross-references

**Actions:** Apply pruning rules from "Aggressive Pruning Rules" section above.

**Stable Reference Exemptions:**
These files should NOT be pruned for temporal staleness:
- projectbrief.md (foundation document)
- techContext.md (technical stack reference)
- productContext.md (product vision)
- systemPatterns.md (architectural decisions - explicit preservation rule applies)

### Archive Policy (Single Source of Truth)

**When to Archive:**

**activeContext.md:**
- Retention: Current + last session
- Archive trigger: Content >2 sessions old
- Destination: memory-bank/archive/YYYY-MM.md

**progress.md:**
- Retention: Last 14 days
- Archive trigger: Entries >14 days old
- Destination: memory-bank/archive/YYYY-MM.md

**Other core files:**
- Retention: No routine archiving (stable reference)
- Archive trigger: N/A

**Archive Frequency:**
- **Reactive:** When file approaches size budget (within 10 lines)
- **Scheduled:** Weekly maintenance (recommended: Monday morning)
- **On-Demand:** User requests "archive old content"

**Archive File Format:**
```markdown
# Archive: YYYY-MM

## Week of YYYY-MM-DD
[Archived content with original date headers]

## Week of YYYY-MM-DD
[Next week's archived content]
```

**Archive Workflow:**
1. Create memory-bank/archive/ directory if not exists
2. Determine target archive file: memory-bank/archive/YYYY-MM.md (current year-month)
3. Open target archive file (create if doesn't exist)
4. Append content under appropriate date header
5. Remove archived content from source file
6. Validate: Source file now within size budget
7. Log: "[ARCHIVE] Moved <N> lines from <source> to archive/YYYY-MM.md"

## Maintenance Workflows

### Context Update Triggers

Update memory bank when ANY of these conditions are met:

**File Changes:**
- ≥3 files modified in a single task
- ≥50 lines of code changed across all files
- New directory created or major file structure change
- File added/removed from project

**Technical Decisions:**
- Architecture decision made (new pattern introduced)
- Technology stack change (new library, framework, or tool)
- API contract change (breaking change to interfaces)
- Design pattern adopted or deprecated

**Project State:**
- Blocker resolved or new blocker discovered
- Feature completed (named feature or task list item done)
- Release milestone reached (version increment)
- User explicitly requests: **"update memory bank"**

**Context Quality:**
- activeContext.md ≥90 lines (approaching 100-line limit)
- Information needed for current task missing from context
- Discovered pattern contradicts existing documentation
- >2 hours since last update (long session)

**Note:** When in doubt, update. Over-updating is preferable to stale context.

### Update Process

**Steps:**
1. Review ALL memory bank files
2. Document current state
3. Clarify next steps
4. Prune outdated content

### Initialization Protocol (Required Before First Use)

**Trigger Commands:**
User says:
- "initialize memory bank"
- "create memory bank structure"
- "set up memory bank"

Any of these phrasings trigger the initialization protocol. This is a **user-initiated action**. Agents should not initialize memory bank proactively without user request.

**Files and Directories Created:**

- **`memory-bank/`** - Root directory (empty directory)
- **`memory-bank/activeContext.md`** - Current session context (Template with Quick Start section)
- **`memory-bank/projectbrief.md`** - Foundation reference (Template with purpose, goals, constraints)
- **`memory-bank/productContext.md`** - Product vision (Template with user value, features)
- **`memory-bank/systemPatterns.md`** - Architecture decisions (Template with patterns section)
- **`memory-bank/techContext.md`** - Technical stack (Template with dependencies, tools)
- **`memory-bank/progress.md`** - Current state tracking (Template with status, roadmap)
- **`memory-bank/archive/`** - Historical content (empty directory, optional)

**Idempotency Rules:**
- If `memory-bank/` exists: Check for missing files only
- If file exists: DO NOT overwrite (preserve existing content)
- If file missing: Create from template
- If file exceeds budget: Apply compaction (see Context Compaction Strategies)

**Initialization Workflow:**

1. Check if memory-bank/ exists
2. If NO: Create directory, then create all template files, then validate, then complete
3. If YES: Scan for missing files
   - If missing files found: Create missing files only, then validate, then complete
   - If no missing files: Validate structure, then complete

**Error Recovery:**

**Permission denied:**
- Detection: "permission denied" in error
- Action: Report "Cannot create memory-bank/. Run `mkdir -p memory-bank` manually and retry."

**Disk full:**
- Detection: "no space" in error
- Action: Report "Insufficient disk space. Free space and retry."

**Path conflict:**
- Detection: File named 'memory-bank' exists
- Action: Report "File 'memory-bank' exists (expected directory). Rename or remove it."

**Template generation fails:**
- Detection: Write operation fails
- Action: Report "Cannot create template files. Check permissions."

**activeContext.md Template:**
```markdown
# Active Context

## Quick Start (Lines 1-30)
**Current Objective:** [To be filled]
**Next 3 Steps:**
1. [To be filled]
2. [To be filled]
3. [To be filled]

**Active Blockers:** None yet

**Validation Signal:** [Success criteria for current work]

## Current Session
[Session details to be added]

## Last Session Summary
[Previous session to be added]
```

### Update Process Steps

Pre-step: If `memory-bank/` does not exist, run initialization protocol (see above) before proceeding.

0. **Initialize If Needed**: Ensure `memory-bank/` exists and restrict writes to this directory
1. **Review All Contexts**: Check each context type for relevance
2. **Document Current State**: Capture new patterns and decisions
3. **Clarify Next Steps**: Update active context with immediate priorities
4. **Prune Outdated Content**: Remove completed, changed, or irrelevant information

**Note:** IDE rule updates are out of scope for this rule. See Section 5 for IDE integration guidance (reference only).

### Session Start Protocol

**Steps:**
1. Read ALL memory bank files
2. Check if files are complete
   - If NO: Create missing files first
   - If YES: Continue to step 3
3. Verify current context
4. Develop work strategy
5. Present approach to user

**Critical:** Read ALL memory bank files at the start of EVERY session - this is not optional.

**Precondition:** Verify the `memory-bank/` folder exists. If missing, user must run initialization (see Initialization Protocol in Section 4) before any write operation.

### Failure Recovery Procedures

#### Scenario 1: memory-bank/ Folder Missing

**Detection:**
- list_dir returns error for memory-bank/
- memory-bank/ not present in workspace root

**Recovery Steps:**
1. Log warning: "[RECOVERY] Memory bank not initialized, creating structure"
2. Run initialization protocol (see Initialization Protocol above)
3. Verify folder creation: list_dir memory-bank/
4. If initialization fails: STOP and report error to user with recovery action
5. If initialization succeeds: Proceed with normal operations

**Validation:**
- [ ] memory-bank/ exists
- [ ] Core template files created

#### Scenario 2: Context File Corrupted (Unparseable)

**Detection:**
- Read operation returns parsing error
- File contains invalid markdown or broken structure
- Metadata block incomplete or malformed

**Recovery Steps:**
1. Identify corrupted file and timestamp: YYYY-MM-DD-HHMMSS
2. Rename file: `<filename>.corrupted-YYYY-MM-DD-HHMMSS`
3. Log: "[RECOVERY] Corrupted file archived: <filename> to <filename>.corrupted-..."
4. Create new file from template with recovery notice:
   ```markdown
   # <Filename> (Recovered)

   > **Recovery Notice:** Original file corrupted on YYYY-MM-DD and archived.
   > This is a fresh start. Refer to .corrupted backup if needed.

   [Minimal required sections based on file type]
   ```
5. Notify user: "Context file recovered from corruption. Review: <filename>"
6. Continue operations with new file

**Validation:**
- [ ] Corrupted file preserved with timestamp
- [ ] New file valid and parseable
- [ ] User notified

#### Scenario 3: Context Files Inconsistent

**Detection:**
- activeContext.md references non-existent systemPatterns.md
- Cross-references point to deleted sections
- Dependency chain broken

**Recovery Steps:**
1. Scan all memory bank files for cross-references
2. Identify missing targets: list_dir + reference analysis
3. Log: "[RECOVERY] Context inconsistency detected:"
   - "Missing file: <filename> (referenced in <source>)"
   - "Broken reference: <section> in <file>"
4. For missing files:
   - Create file from template
   - Add note: "Created by recovery process due to broken reference"
5. For broken section references:
   - Log warning (may be intentional deletion)
   - Request user review
6. Continue operations, log all actions in activeContext.md session log

**Validation:**
- [ ] All referenced files exist
- [ ] Critical dependencies resolved
- [ ] User notified of inconsistencies

#### Scenario 4: File Exceeds Size Budget

**Detection:**
- File line count > size budget (see Performance Standards)
- Total context >600 lines

**Recovery Steps:**
1. Identify oversized file and current line count
2. Log: "[RECOVERY] <filename> exceeds budget: <current> lines (limit: <budget>)"
3. Apply compaction automatically:
   - Run staleness detection rules
   - Apply aggressive pruning criteria
   - Archive content >14 days old
4. Re-check line count after compaction
5. If still exceeds budget:
   - Archive oldest 50% of content (sort entries by timestamp, archive bottom half by count) to memory-bank/archive/YYYY-MM.md
   - Log: "[RECOVERY] Emergency archive: <filename> to archive/YYYY-MM.md"
6. If still exceeds after emergency archive:
   - STOP and report: "Cannot compact further, manual review required"

**Validation:**
- [ ] File within budget after recovery
- [ ] Archived content preserved
- [ ] No critical current-session info lost

#### Scenario 5: Read Operation Timeout or Network Error

**Detection:**
- File read operation times out
- Network/filesystem error prevents access

**Recovery Steps:**
1. Retry read operation 3 times with exponential backoff:
   - Attempt 1: immediate
   - Attempt 2: wait 2 seconds
   - Attempt 3: wait 5 seconds
2. If all retries fail:
   - Log: "[RECOVERY] Cannot access <filename> after 3 retries"
   - Continue with degraded context (skip this file)
   - Notify user: "Operating with incomplete context: <filename> unavailable"
3. Attempt recovery on next context update cycle

**Validation:**
- [ ] Retry mechanism prevents transient failures
- [ ] Agent continues with available context
- [ ] User notified of degraded state

#### Scenario 6: Concurrent Modifications

**Situation:** Two agents simultaneously attempt to update memory bank files.

**Detection:**
1. Before writing, record current file timestamp
2. After write operation, verify timestamp hasn't changed
3. If timestamp differs, another agent has modified the file

**Recovery Strategy:**
1. Read updated file contents
2. Merge changes if possible:
   - Append-only files: Merge both updates
   - Overwrite files: Use latest timestamp, archive conflicted version
3. If merge not possible:
   - Archive conflicted version to `memory-bank/conflicts/`
   - Log conflict with both agent IDs and timestamps
   - Continue with latest version

**Example:**
```
[CONFLICT 2026-01-06T15:30:00Z] Agent A and Agent B both modified activeContext.md
- Agent A version: Archived to memory-bank/conflicts/activeContext-agentA-20260106T153000Z.md
- Agent B version: Current (newer timestamp)
- Resolution: Manual review required
```

**Prevention:**
- Use timestamp-based conflict detection
- Implement exponential backoff for retries
- Consider file locking for critical operations

**Validation:**
- [ ] Concurrent write detection works
- [ ] Conflicts archived with clear naming
- [ ] No data loss in conflict scenarios

#### Recovery Best Practices

**Logging Requirements:**
- Always log recovery actions to activeContext.md session change log
- Format: `[RECOVERY YYYY-MM-DD HH:MM] <issue> then <action> then <outcome>`
- Include: timestamp, issue detected, action taken, outcome

**User Notification Triggers:**

- **Corruption detected:** Always notify
- **Emergency archive performed:** Always notify
- **Inconsistency detected:** Notify with details
- **Degraded operation mode:** Notify immediately
- **Transient errors (retries succeeded):** Log only, no notification

**Data Preservation:**
- NEVER delete original file before backup created
- ALWAYS use timestamped filenames for backups (.corrupted-YYYY-MM-DD-HHMMSS)
- Archive to memory-bank/archive/ or .corrupted suffix
- Preserve user data unless explicitly confirmed safe to remove

## Memory Bank Analysis
- **Precondition**: Memory bank initialized and `memory-bank/` folder exists
- **Session Status**: [New session / Continuing work]
- **Context Health**: [Complete / Missing files / Needs updates]
- **Active Focus**: [Current priority from activeContext.md]
- **Next Steps**: [Immediate actions from context]
- **Blockers**: [Any dependencies or constraints]
- **Validation**: [How to verify completion]

## Context Summary
- **Project**: [Brief description from projectbrief.md]
- **Current State**: [Status from progress.md]
- **Technical Stack**: [Key technologies from techContext.md]

## Implementation Plan
[Minimal changes based on context understanding]
```
