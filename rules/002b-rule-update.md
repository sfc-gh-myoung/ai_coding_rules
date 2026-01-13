# Rule Update and Maintenance Guide

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when updating, modifying, or maintaining existing rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.1
**LastUpdated:** 2026-01-13
**Keywords:** rule update, rule maintenance, versioning, RuleVersion, LastUpdated, semantic versioning, MAJOR, MINOR, PATCH, rule modification, keyword expansion, scope updates, metadata updates, CHANGELOG updates
**TokenBudget:** ~4500
**ContextTier:** High
**Depends:** 002-rule-governance.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Workflow and best practices for updating and maintaining existing rule files. Covers semantic versioning (MAJOR/MINOR/PATCH), LastUpdated field management, common update scenarios, and validation requirements.

**When to Load This Rule:**
- Updating existing rule files
- Modifying rule metadata (Keywords, TokenBudget, ContextTier)
- Adding content to existing rules (anti-patterns, examples, sections)
- Fixing typos, broken links, or formatting issues
- Understanding when to increment RuleVersion
- Determining MAJOR vs MINOR vs PATCH changes

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Schema requirements and standards
- **000-global-core.md** - Foundation for all rules

**Related:**
- **002a-rule-creation.md** - Creating new rules from scratch
- **002e-schema-validator-usage.md** - Validation commands and error resolution
- **002c-rule-optimization.md** - Token budget optimization
- **800-project-changelog.md** - CHANGELOG.md format and requirements

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema with validation rules
- **Semantic Versioning:** https://semver.org/spec/v2.0.0.html - Versioning specification

## Contract

### Inputs and Prerequisites

- Existing rule file to update
- Understanding of change type (content, metadata, structure)
- Access to `schema_validator.py` script
- Understanding of semantic versioning principles

### Mandatory

- Text editor
- `schema_validator.py` script
- Git for tracking changes
- Access to CHANGELOG.md

### Forbidden

- Updating rules without incrementing RuleVersion
- Updating rules without updating LastUpdated
- Skipping validation after updates
- Not documenting changes in CHANGELOG.md
- Using wrong version increment type (MAJOR when should be MINOR, etc.)

### Execution Steps

1. Read existing rule file and understand current state
2. Determine change type: MAJOR, MINOR, or PATCH (see versioning policy below)
3. Make content changes to rule file
4. Update RuleVersion according to semantic versioning
5. Update LastUpdated to current date (YYYY-MM-DD)
6. Update Keywords if adding new discoverable terms
7. Update TokenBudget if file size changed significantly
8. Validate with `schema_validator.py` (must pass with 0 CRITICAL errors)
9. Update CHANGELOG.md with change details
10. Regenerate RULES_INDEX.md with `task index:generate`

### Output Format

Updated rule file with:
- Incremented RuleVersion (vX.Y.Z format)
- Updated LastUpdated (YYYY-MM-DD format)
- Updated content
- Passing schema validation
- CHANGELOG.md entry

### Validation

**Pre-Task-Completion Checks:**
- RuleVersion incremented correctly for change type
- LastUpdated set to current date
- Keywords updated if new terms added
- TokenBudget reflects actual file size (±10%)
- schema_validator.py ready to run
- CHANGELOG.md entry prepared

**Success Criteria:**
- `schema_validator.py rules/NNN-rule.md` returns 0 CRITICAL errors
- RuleVersion follows semantic versioning (vX.Y.Z)
- LastUpdated is current date (YYYY-MM-DD)
- CHANGELOG.md has entry for this update
- RULES_INDEX.md regenerated with updated metadata

### Post-Execution Checklist

- [ ] Change type determined (MAJOR/MINOR/PATCH)
- [ ] RuleVersion incremented correctly
- [ ] LastUpdated updated to current date
- [ ] Keywords updated if new terms added
- [ ] TokenBudget updated if file size changed
- [ ] Schema validation passes (0 CRITICAL errors)
- [ ] CHANGELOG.md updated with change details
- [ ] RULES_INDEX.md regenerated
- [ ] Git commit with conventional commit message

## Rule Versioning Policy

**Requirement:** All rule modifications must update version fields according to semantic versioning principles.

### RuleVersion Semantic Versioning

**Format:** `vMAJOR.MINOR.PATCH` (e.g., v1.0.0, v2.1.3, v3.0.0)

**MAJOR (vX.0.0)** - Breaking changes requiring agent adaptation:
- Removing or renaming required sections
- Changing Contract structure fundamentally (e.g., XML to Markdown migration)
- Removing mandatory tools, commands, or dependencies
- Changing execution workflow in incompatible ways
- Schema version upgrades (v3.1 to v3.2)
- Removing keywords that agents rely on for discovery

**MINOR (vX.Y.0)** - Additive changes enhancing functionality:
- Adding new keywords for improved discoverability
- Expanding "When to Load This Rule" triggers
- Adding new anti-patterns, examples, or guidance sections
- Adding new optional tools or commands
- Clarifying ambiguous guidance without changing intent
- Adding new Contract subsections (non-breaking)
- Expanding scope description to be more explicit

**PATCH (vX.Y.Z)** - Non-functional corrections:
- Fixing typos, grammar, or spelling errors
- Correcting broken links or outdated URLs
- Updating external documentation references
- Formatting improvements (whitespace, markdown)
- TokenBudget adjustments to reflect actual size
- Updating examples without changing patterns

### LastUpdated Field

**Requirement:** Update `LastUpdated` to current date (YYYY-MM-DD format) for ANY content change.

**Always update LastUpdated for:**
- MAJOR version increments
- MINOR version increments
- PATCH version increments
- Metadata field updates (Keywords, TokenBudget, ContextTier)
- Any text modifications, including typo fixes

**Format:** `YYYY-MM-DD` (e.g., 2026-01-07)

### Version Update Examples

**Example 1: Adding Keywords (MINOR)**
```markdown
Before:
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** git, workflow, branching strategy

After:
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-07
**Keywords:** git, git commit, commit message, workflow, branching strategy
```

**Example 2: Fixing Typo (PATCH)**
```markdown
Before:
**RuleVersion:** v2.1.0
**LastUpdated:** 2026-01-05
Content: "Use teh validation command"

After:
**RuleVersion:** v2.1.1
**LastUpdated:** 2026-01-07
Content: "Use the validation command"
```

**Example 3: Schema Migration (MAJOR)**
```markdown
Before:
**SchemaVersion:** v3.1
**RuleVersion:** v2.5.0
**LastUpdated:** 2025-12-15

After:
**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
```

### Version Update Checklist

When modifying any rule file:
- [ ] Determine change type: MAJOR, MINOR, or PATCH
- [ ] Increment RuleVersion according to semantic versioning
- [ ] Update LastUpdated to current date (YYYY-MM-DD)
- [ ] Update CHANGELOG.md with version change details
- [ ] Run schema validator to ensure compliance
- [ ] Update RULES_INDEX.md (regenerate with `task index:generate`)

## When to Update Rules

### Update Triggers

**Update existing rule when:**
- Adding new examples or anti-patterns to existing guidance
- Expanding "When to Load This Rule" with new triggers
- Adding new keywords for improved discoverability
- Clarifying ambiguous or unclear guidance
- Fixing typos, broken links, or formatting issues
- Updating external documentation references
- Adding new optional tools or commands
- Expanding existing sections with more detail

**Create new rule instead when:**
- Topic is substantially different from existing rule
- New rule would be >10,000 tokens (split large rules)
- Existing rule would become unfocused with additions
- New content targets different ContextTier or domain
- Change would break existing rule's focused scope

### Decision Tree

```
Is the change related to existing rule's scope?
- YES: Does it enhance/clarify existing guidance?
  - YES: Update existing rule (MINOR or PATCH)
  - NO: Does it fundamentally change the approach?
    - YES: Update existing rule (MAJOR)
    - NO: Consider creating new rule
- NO: Create new rule in appropriate domain
```

## Update Workflow

### Step 1: Read Existing Rule

```bash
# Open rule file
vim rules/NNN-rule.md

# Check current version
grep "RuleVersion" rules/NNN-rule.md
grep "LastUpdated" rules/NNN-rule.md
```

### Step 2: Determine Change Type

**Ask these questions:**
1. Am I removing or fundamentally changing existing guidance? = MAJOR
2. Am I adding new content, keywords, or examples? = MINOR
3. Am I fixing typos, links, or formatting? = PATCH

**Examples:**
- Adding 5 new keywords for discoverability = MINOR
- Fixing "teh" to "the" typo = PATCH
- Removing a required section = MAJOR
- Adding new anti-pattern with example = MINOR
- Updating broken URL = PATCH
- Changing from XML to Markdown Contract = MAJOR

### Step 3: Make Content Changes

Edit the rule file with your changes. Common update scenarios:

**Adding Keywords:**
```markdown
# Before
**Keywords:** Snowflake, SQL, optimization

# After
**Keywords:** Snowflake, SQL, optimization, clustering, partitioning, query tuning
```

**Adding Anti-Pattern:**
```markdown
## Anti-Patterns and Common Mistakes

### Anti-Pattern 3: New Anti-Pattern Name

**Problem:** Description of what goes wrong

**Why It Fails:** Explanation of failure mechanism

**Correct Pattern:**
\```
code example
\```

**Benefits:** Why correct pattern works
```

**Expanding Scope:**
```markdown
**When to Load This Rule:**
- Existing trigger 1
- Existing trigger 2
- New trigger 3  # Added
- New trigger 4  # Added
```

### Step 4: Update Metadata

**RuleVersion:**
```markdown
# MAJOR change (v2.5.0 to v3.0.0)
**RuleVersion:** v3.0.0

# MINOR change (v2.5.0 to v2.6.0)
**RuleVersion:** v2.6.0

# PATCH change (v2.5.0 to v2.5.1)
**RuleVersion:** v2.5.1
```

**LastUpdated:**
```markdown
# Always update to current date
**LastUpdated:** 2026-01-07
```

**Keywords (if adding new terms):**
```markdown
# Add new discoverable terms
**Keywords:** existing, terms, new-term-1, new-term-2
```

**TokenBudget (if file size changed significantly):**
```bash
# Check current token count
wc -l rules/NNN-rule.md
# Estimate: ~2 tokens per line average
# Update TokenBudget to reflect new size (±10% acceptable)
```

### Step 5: Validate Changes

```bash
# Run schema validator
uv run python scripts/schema_validator.py rules/NNN-rule.md

# Expected output:
# All validations passed!
# RESULT: PASSED

# If errors, fix and re-validate
```

### Step 6: Update CHANGELOG.md

Add entry under `## [Unreleased]` section:

```markdown
## [Unreleased]

### Changed (or Added, or Fixed)
- **docs(rules):** update NNN-rule-name (vX.Y.Z to vX.Y+1.Z)
  - Added 5 new keywords for improved discoverability
  - Expanded "When to Load" with 2 new triggers
  - Added anti-pattern example for common mistake
  - Impact: Improves rule discovery for [use case]
```

### Step 7: Regenerate RULES_INDEX.md

```bash
# Regenerate index with updated metadata
task index:generate

# Or directly:
uv run python scripts/index_generator.py
```

## Common Update Scenarios

### Scenario 1: Adding Keywords for Discoverability

**Change Type:** MINOR

**Steps:**
1. Identify missing discoverable terms from user queries or feedback
2. Add terms to Keywords metadata (maintain 5-20 range)
3. Increment MINOR version (v3.0.0 to v3.1.0)
4. Update LastUpdated to current date
5. Validate and update CHANGELOG.md

**Example:**
```markdown
# Before
**Keywords:** git, workflow, branching strategy

# After (added commit-related terms)
**Keywords:** git, git commit, commit message, workflow, branching strategy, staging
```

### Scenario 2: Expanding Scope/Triggers

**Change Type:** MINOR

**Steps:**
1. Add new triggers to "When to Load This Rule" section
2. Ensure new triggers align with existing rule scope
3. Increment MINOR version
4. Update LastUpdated
5. Validate and document in CHANGELOG.md

**Example:**
```markdown
**When to Load This Rule:**
- Existing trigger 1
- Existing trigger 2
- Writing git commit messages  # NEW
- Using Conventional Commits format  # NEW
```

### Scenario 3: Adding Anti-Patterns/Examples

**Change Type:** MINOR

**Steps:**
1. Add new anti-pattern to "Anti-Patterns and Common Mistakes" section
2. Include problem, why it fails, correct pattern, and benefits
3. Increment MINOR version
4. Update LastUpdated
5. Update TokenBudget if file grew significantly
6. Validate and document

### Scenario 4: Fixing Typos/Links

**Change Type:** PATCH

**Steps:**
1. Fix typo, broken link, or formatting issue
2. Increment PATCH version (v2.1.0 to v2.1.1)
3. Update LastUpdated
4. Validate (should still pass)
5. Document in CHANGELOG.md

**Example:**
```markdown
# Before
Content: "Use teh validation command"

# After
Content: "Use the validation command"
```

### Scenario 5: Schema Migration

**Change Type:** MAJOR

**Steps:**
1. Update SchemaVersion (v3.1 to v3.2)
2. Restructure sections per new schema requirements
3. Reset RuleVersion to vX.0.0 (increment MAJOR from previous)
4. Update LastUpdated
5. Validate with new schema
6. Document breaking changes in CHANGELOG.md

**Example:**
```markdown
# Before
**SchemaVersion:** v3.1
**RuleVersion:** v2.5.0

# After
**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0  # MAJOR increment due to schema change
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Forgetting to Update RuleVersion

**Problem:** Making content changes without incrementing RuleVersion.

**Why It Fails:** Breaks version tracking; users can't tell if rule changed; violates governance; makes debugging difficult.

**Correct Pattern:**
```bash
# Always increment version for ANY change
# Before editing:
grep "RuleVersion" rules/NNN-rule.md  # Note current version

# After editing:
# Update RuleVersion based on change type (MAJOR/MINOR/PATCH)
```

**Benefits:** Clear version history; users know when rule changed; governance compliance; easier debugging.

### Anti-Pattern 2: Forgetting to Update LastUpdated

**Problem:** Updating content but leaving LastUpdated unchanged.

**Why It Fails:** Misleading date information; users think rule is stale; breaks change tracking.

**Correct Pattern:**
```markdown
# ALWAYS update LastUpdated for ANY change
**LastUpdated:** 2026-01-07  # Current date
```

**Benefits:** Accurate change tracking; users see recent updates; compliance with versioning policy.

### Anti-Pattern 3: Wrong Version Increment Type

**Problem:** Using PATCH when should be MINOR, or MINOR when should be MAJOR.

**Why It Fails:** Misleading version signals; users expect wrong level of changes; breaks semantic versioning contract.

**Correct Pattern:**
```markdown
# Adding keywords = MINOR (not PATCH)
v3.0.0 to v3.1.0  # Correct

# Removing section = MAJOR (not MINOR)
v3.1.0 to v4.0.0  # Correct

# Fixing typo = PATCH (not MINOR)
v3.1.0 to v3.1.1  # Correct
```

**Benefits:** Clear semantic signals; users understand change impact; proper version tracking.

### Anti-Pattern 4: Not Updating CHANGELOG.md

**Problem:** Making rule changes without documenting in CHANGELOG.md.

**Why It Fails:** No change history; users don't know what changed; violates project governance; hard to track evolution.

**Correct Pattern:**
```markdown
# Always add CHANGELOG.md entry
## [Unreleased]

### Changed
- **docs(rules):** update NNN-rule-name (v3.0.0 to v3.1.0)
  - Added 5 new keywords for discoverability
  - Impact: Improves rule discovery for commit workflows
```

**Benefits:** Complete change history; users see what changed; governance compliance; easier debugging.

### Anti-Pattern 5: Skipping Validation

**Problem:** Not running schema_validator.py after making changes.

**Why It Fails:** May introduce schema violations; breaks CI/CD; wastes review time; degrades rule quality.

**Correct Pattern:**
```bash
# Always validate after changes
uv run python scripts/schema_validator.py rules/NNN-rule.md

# Fix any errors before committing
# Re-validate until 0 CRITICAL errors
```

**Benefits:** Catches errors early; maintains schema compliance; smooth CI/CD; high rule quality.

## Output Format Examples

### Example 1: Keyword Addition Update

```bash
# Step 1: Read current state
grep "RuleVersion\|LastUpdated\|Keywords" rules/803-project-git-workflow.md

# Output:
# **RuleVersion:** v3.0.0
# **LastUpdated:** 2026-01-06
# **Keywords:** git, workflow, branching strategy

# Step 2: Make changes (add commit-related keywords)
vim rules/803-project-git-workflow.md

# Step 3: Update metadata
# **RuleVersion:** v3.1.0  # MINOR (added keywords)
# **LastUpdated:** 2026-01-07
# **Keywords:** git, git commit, commit message, workflow, branching strategy

# Step 4: Validate
uv run python scripts/schema_validator.py rules/803-project-git-workflow.md
# All validations passed!

# Step 5: Update CHANGELOG.md
# - **docs(rules):** expand 803 keywords for commit message discoverability

# Step 6: Regenerate index
task index:generate
```

### Example 2: Typo Fix Update

```bash
# Step 1: Fix typo
# Before: "Use teh validation command"
# After: "Use the validation command"

# Step 2: Update metadata
# **RuleVersion:** v2.1.0 to v2.1.1  # PATCH (typo fix)
# **LastUpdated:** 2026-01-07

# Step 3: Validate
uv run python scripts/schema_validator.py rules/NNN-rule.md
# All validations passed!

# Step 4: Update CHANGELOG.md
# - **fix(rules):** correct typo in NNN-rule.md (v2.1.0 to v2.1.1)

# Step 5: Regenerate index
task index:generate
```
