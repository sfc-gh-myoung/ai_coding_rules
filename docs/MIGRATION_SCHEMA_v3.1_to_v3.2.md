# Schema Migration Guide: v3.1 → v3.2

**Last Updated:** 2026-01-21

**Version:** 3.2  
**Date:** 2025-01-05  
**Scope:** Rule schema format changes  
**Impact:** All 113 rule files upgraded

## Overview

Schema v3.2 represents a significant simplification and optimization of the rule format, eliminating redundant sections and improving agent comprehension. This guide documents the changes, rationale, and migration steps.

## TL;DR - What Changed

**Key Changes:**
- ✅ **Eliminated** `## Purpose` and `## Rule Scope` (separate sections)
- ✅ **Eliminated** `## Quick Start TL;DR` (redundant with Contract)
- ✅ **Added** unified `## Scope` section with structured markers
- ✅ **Moved** `## References` early (after Scope, before Contract)
- ✅ **Changed** Contract from XML tags to Markdown headers (`###`)
- ✅ **Added** `**LastUpdated:**` metadata field
- ✅ **Expanded** Keywords from 10-15 to 5-20 terms

**Migration Status:**
- All 113 rule files upgraded to v3.2
- Schema validator updated with new validation rules
- Template generator updated for v3.2 format

---

## Table of Contents

1. [Breaking Changes](#breaking-changes)
2. [Section Changes](#section-changes)
3. [Metadata Changes](#metadata-changes)
4. [Contract Format Changes](#contract-format-changes)
5. [Rationale](#rationale)
6. [Migration Steps](#migration-steps)
7. [Validation](#validation)
8. [Examples](#examples)

---

## Breaking Changes

### 1. Eliminated `## Purpose` Section

**v3.1 Format:**
```markdown
## Purpose

This rule provides guidance on...
```

**v3.2 Format:**
```markdown
(Removed - content merged into ## Scope)
```

**Rationale:**
- Purpose was redundant with Scope and H1 title
- Agents don't need separate "why this rule exists" section
- Content can be incorporated into Scope's "What This Rule Covers"

---

### 2. Eliminated `## Rule Scope` Section

**v3.1 Format:**
```markdown
## Rule Scope

This rule covers:
- Feature A
- Feature B
```

**v3.2 Format:**
```markdown
## Scope

**What This Rule Covers:**
- Feature A
- Feature B

**When to Load This Rule:**
- Scenario 1
- Scenario 2
```

**Rationale:**
- Unified Scope section with structured markers improves agent parsing
- "When to Load" helps agents make better discovery decisions
- Reduces section count while improving clarity

---

### 3. Eliminated `## Quick Start TL;DR` Section

**v3.1 Format:**
```markdown
## Quick Start TL;DR

Essential patterns:
1. Pattern A
2. Pattern B
```

**v3.2 Format:**
```markdown
(Removed - content merged into Contract → Mandatory)
```

**Rationale:**
- 80% content duplication with Contract section
- Maintenance burden (two places to update)
- Agents should read full Contract, not abbreviated version
- Essential patterns belong in Contract → Mandatory subsection

**Migration Path:**
- Move essential patterns to `### Mandatory` subsection
- Move prerequisites to `### Inputs and Prerequisites` subsection
- Delete Quick Start section entirely

---

### 4. Contract: XML Tags → Markdown Headers

**v3.1 Format:**
```markdown
## Contract

<inputs_prereqs>
- Prerequisite 1
</inputs_prereqs>

<mandatory>
- Must do A
</mandatory>
```

**v3.2 Format:**
```markdown
## Contract

### Inputs and Prerequisites
- Prerequisite 1

### Mandatory
- Must do A
```

**Rationale:**
- XML tags are not standard Markdown (universal format violation)
- Markdown headers are more readable for humans
- Agents parse Markdown headers natively
- Consistent with rest of document structure

---

### 5. References Section Moved Early

**v3.1 Placement:**
```markdown
## Metadata
## Purpose
## Rule Scope
## Contract
## References  ← Late in file
```

**v3.2 Placement:**
```markdown
## Metadata
## Scope
## References  ← Early in file (after Scope, before Contract)
## Contract
```

**Rationale:**
- Agents need dependency information before reading Contract
- Early References improves dependency discovery
- Follows "declare before use" principle
- Reduces cognitive load (know dependencies upfront)

---

## Section Changes

### New: Unified `## Scope` Section

**Structure:**
```markdown
## Scope

**What This Rule Covers:**
- Specific feature or technology aspect
- Boundaries of this rule's domain
- Related concepts included

**When to Load This Rule:**
- Scenario 1 (e.g., "When working with Snowflake Cortex Search")
- Scenario 2 (e.g., "When implementing semantic search")
- Scenario 3 (e.g., "When troubleshooting search relevance")
```

**Requirements:**
- Must appear after Metadata, before References
- Must include both markers: "What This Rule Covers" and "When to Load This Rule"
- Maximum 3 paragraphs or ~10 bullet points
- Should be concise (5-15 lines)

**Agent Impact:**
- Agents can quickly determine if rule is relevant
- "When to Load" helps with semantic discovery
- Structured markers enable reliable parsing

---

### Updated: `## References` Section

**Placement Change:**
- **Old:** After Contract (late in file)
- **New:** After Scope, before Contract (early in file)

**Structure (unchanged):**
```markdown
## References

### Dependencies
- 000-global-core.md
- 100-snowflake-core.md

### External Documentation
- [Snowflake Docs](https://docs.snowflake.com/...)
- [API Reference](https://...)

### Related Rules
- 101-snowflake-streamlit-core.md
- 103-snowflake-performance-tuning.md
```

**Rationale:**
- Agents need to know dependencies before reading Contract
- Early placement improves rule loading order
- Reduces need to scroll back to check dependencies

---

### Updated: `## Contract` Section

**Format Change:** XML tags → Markdown headers

**Required Subsections (v3.2):**
1. `### Inputs and Prerequisites`
2. `### Mandatory`
3. `### Forbidden`
4. `### Execution Steps`
5. `### Output Format`
6. `### Validation`
7. `### Post-Execution Checklist`

**Example:**
```markdown
## Contract

### Inputs and Prerequisites
- Python 3.11+
- Snowflake account with CORTEX_USER role

### Mandatory
- Always validate input parameters
- Use parameterized queries for SQL

### Forbidden
- Never hardcode credentials
- Avoid SELECT * in production queries

### Execution Steps
1. Validate prerequisites
2. Initialize connection
3. Execute query
4. Process results
5. Clean up resources

### Output Format
Return JSON with status and results:
```json
{
  "status": "success",
  "results": [...],
  "metadata": {...}
}
```

### Validation
- Check HTTP 200 status
- Verify results array is non-empty
- Validate JSON schema

### Post-Execution Checklist
- [ ] Query executed successfully
- [ ] Results validated
- [ ] Resources cleaned up
```

---

## Metadata Changes

### New Field: `**LastUpdated:**`

**Format:** `YYYY-MM-DD`

**Example:**
```markdown
**SchemaVersion:** v3.2
**RuleVersion:** v1.2.0
**LastUpdated:** 2025-01-05  ← New field
**Keywords:** snowflake, cortex, search, semantic, vector
**TokenBudget:** ~2400
**ContextTier:** High
**Depends:** 000-global-core.md, 100-snowflake-core.md
```

**Purpose:**
- Provides temporal context for troubleshooting
- Tracks maintenance history
- Helps identify when breaking changes occurred
- Complements RuleVersion with date information

**Use Cases:**
- "Was this rule updated before or after the bug was introduced?"
- "Which rules haven't been reviewed in 6+ months?"
- "What rules changed during the v3.1 → v3.2 migration?"

---

### Updated Field: `**Keywords:**`

**Change:** 10-15 terms → 5-20 terms

**Rationale:**
- More flexibility for simple vs. complex rules
- Simple rules (e.g., 300a-bash-security.md) may only need 5-8 keywords
- Complex rules (e.g., 115-snowflake-cortex-agents-core.md) may need 15-20 keywords
- Improves semantic discovery for both cases

**Example:**
```markdown
# Simple rule (5 keywords)
**Keywords:** bash, security, shellcheck, validation, best-practices

# Complex rule (18 keywords)
**Keywords:** snowflake, cortex, agents, instructions, tools, semantic-model, guardrails, conversation, context, memory, error-handling, debugging, monitoring, performance, security, best-practices, troubleshooting, operations
```

---

## Rationale

### Design Principles

**1. Agent Understanding First**
- Agents are the primary consumers of rules
- Human readability is secondary (but still important)
- Structure must be parseable and unambiguous

**2. Eliminate Redundancy**
- Quick Start duplicated Contract content (80% overlap)
- Purpose duplicated Scope and H1 title
- Maintenance burden: update multiple sections for same change

**3. Early Dependency Declaration**
- Agents need to know dependencies before reading Contract
- "Declare before use" reduces cognitive load
- Improves rule loading order and discovery

**4. Universal Format**
- Markdown headers are standard (XML tags are not)
- Consistent structure across all sections
- Works with any Markdown parser

**5. Token Efficiency**
- Eliminated ~200-400 tokens per rule (Quick Start removal)
- Unified Scope section is more concise than Purpose + Rule Scope
- Reduced duplication saves context window space

---

### Specific Change Rationale

#### Why Remove Quick Start TL;DR?

**Problem:**
- 80% content duplication with Contract
- Agents would read both sections (wasting tokens)
- Maintenance burden: update two places for same change
- No clear benefit over reading Contract directly

**Evidence:**
```markdown
# Quick Start TL;DR (v3.1)
Essential patterns:
1. Always validate input parameters
2. Use parameterized queries
3. Handle errors gracefully

# Contract → Mandatory (v3.1)
### Mandatory
- Always validate input parameters before execution
- Use parameterized queries for all SQL operations
- Implement comprehensive error handling
```

**Solution:**
- Merge essential patterns into Contract → Mandatory
- Agents read Contract once (single source of truth)
- Reduced maintenance burden

---

#### Why Move References Early?

**Problem:**
- Agents had to read entire Contract before seeing dependencies
- Couldn't determine if prerequisites were met
- Had to scroll back to check dependencies

**Solution:**
- Move References after Scope, before Contract
- Agents see dependencies immediately
- Can load prerequisite rules before reading Contract
- Follows "declare before use" principle

---

#### Why XML Tags → Markdown Headers?

**Problem:**
- XML tags are not standard Markdown
- Violates universal format principle
- Requires custom parsing logic
- Less readable for humans

**Solution:**
- Use Markdown headers (`###`) for subsections
- Standard Markdown parsers work natively
- More readable and maintainable
- Consistent with rest of document

---

## Migration Steps

### Automated Migration (Recommended)

**Step 1: Backup Current Rules**
```bash
# Create backup branch
git checkout -b backup/pre-v3.2-migration
git push origin backup/pre-v3.2-migration

# Return to main branch
git checkout main
```

**Step 2: Run Schema Validator (Identify Issues)**
```bash
# Validate all rules against v3.2 schema
python scripts/schema_validator.py rules/

# Save validation report
python scripts/schema_validator.py rules/ > migration_report.txt
```

**Step 3: Update Schema Version in All Rules**
```bash
# Update SchemaVersion field
find rules -name "*.md" -type f -exec sed -i '' 's/\*\*SchemaVersion:\*\* v3.1/\*\*SchemaVersion:\*\* v3.2/g' {} +
```

**Step 4: Validate After Migration**
```bash
# Verify all rules pass v3.2 validation
python scripts/schema_validator.py rules/

# Expected: 0 errors, 113 files validated
```

---

### Manual Migration (Per Rule)

Use this checklist for each rule file:

#### Checklist: Metadata Updates

- [ ] Update `**SchemaVersion:**` from `v3.1` to `v3.2`
- [ ] Add `**LastUpdated:**` field with current date (YYYY-MM-DD)
- [ ] Verify Keywords count is 5-20 terms
- [ ] Verify metadata field order: SchemaVersion, RuleVersion, LastUpdated, Keywords, TokenBudget, ContextTier, Depends

#### Checklist: Section Changes

- [ ] **Remove** `## Purpose` section (merge content into Scope if needed)
- [ ] **Remove** `## Rule Scope` section
- [ ] **Add** `## Scope` section with structured markers:
  - [ ] `**What This Rule Covers:**`
  - [ ] `**When to Load This Rule:**`
- [ ] **Remove** `## Quick Start TL;DR` section
  - [ ] Merge essential patterns into `### Mandatory`
  - [ ] Merge prerequisites into `### Inputs and Prerequisites`
- [ ] **Move** `## References` section to after Scope, before Contract
- [ ] **Update** `## Contract` section:
  - [ ] Replace XML tags with Markdown headers (`###`)
  - [ ] Verify all 7 required subsections present
  - [ ] Ensure subsections use `###` not `<tags>`

#### Checklist: Validation

- [ ] Run schema validator: `python scripts/schema_validator.py rules/NNN-rule.md`
- [ ] Verify 0 errors
- [ ] Check TokenBudget is within ±10% of actual
- [ ] Verify all rule references exist

---

### Example Migration

**Before (v3.1):**
```markdown
# 116-snowflake-cortex-search

## Metadata
**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** snowflake, cortex, search, semantic, vector, embeddings, similarity, retrieval, rag, llm
**TokenBudget:** ~2400
**ContextTier:** High
**Depends:** 000-global-core.md, 100-snowflake-core.md

## Purpose

This rule provides comprehensive guidance on implementing Snowflake Cortex Search...

## Rule Scope

This rule covers:
- Cortex Search service setup
- Vector embeddings and similarity search
- Query optimization

## Quick Start TL;DR

Essential patterns:
1. Always specify embedding model
2. Use appropriate distance metrics
3. Optimize chunk sizes for your use case

## Contract

<inputs_prereqs>
- Snowflake account with CORTEX_USER role
- Python 3.11+
</inputs_prereqs>

<mandatory>
- Always specify embedding model explicitly
- Use appropriate distance metrics (cosine, euclidean, dot_product)
</mandatory>

## References

### Dependencies
- 000-global-core.md
- 100-snowflake-core.md
```

**After (v3.2):**
```markdown
# 116-snowflake-cortex-search

## Metadata
**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2025-01-05
**Keywords:** snowflake, cortex, search, semantic, vector, embeddings, similarity, retrieval, rag, llm
**TokenBudget:** ~2200
**ContextTier:** High
**Depends:** 000-global-core.md, 100-snowflake-core.md

## Scope

**What This Rule Covers:**
- Snowflake Cortex Search service setup and configuration
- Vector embeddings and semantic similarity search
- Query optimization and performance tuning
- Integration with RAG (Retrieval-Augmented Generation) workflows

**When to Load This Rule:**
- When implementing semantic search in Snowflake
- When building RAG applications with Cortex
- When optimizing vector similarity queries
- When troubleshooting Cortex Search performance

## References

### Dependencies
- 000-global-core.md
- 100-snowflake-core.md

### External Documentation
- [Cortex Search Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)

### Related Rules
- 114-snowflake-cortex-aisql.md
- 115-snowflake-cortex-agents-core.md

## Contract

### Inputs and Prerequisites
- Snowflake account with CORTEX_USER role
- Python 3.11+ (for API integration)
- Understanding of vector embeddings and similarity metrics

### Mandatory
- Always specify embedding model explicitly (e.g., 'snowflake-arctic-embed-m')
- Use appropriate distance metrics (cosine, euclidean, dot_product)
- Optimize chunk sizes for your use case (typically 512-1024 tokens)
- Validate search results for relevance before returning to users

### Forbidden
- Never use SELECT * on large vector tables
- Avoid hardcoding embedding dimensions
- Don't skip result validation

### Execution Steps
1. Validate prerequisites (role, permissions)
2. Create or connect to Cortex Search service
3. Configure embedding model and distance metric
4. Execute search query with appropriate parameters
5. Validate and filter results
6. Return formatted results to caller

### Output Format
Return JSON with search results and metadata:
```json
{
  "status": "success",
  "results": [
    {
      "id": "doc_123",
      "content": "...",
      "score": 0.95,
      "metadata": {...}
    }
  ],
  "query_metadata": {
    "embedding_model": "snowflake-arctic-embed-m",
    "distance_metric": "cosine",
    "total_results": 10
  }
}
```

### Validation
- Verify HTTP 200 status from Cortex API
- Check results array is non-empty
- Validate similarity scores are in expected range (0-1 for cosine)
- Ensure metadata fields are populated

### Post-Execution Checklist
- [ ] Search query executed successfully
- [ ] Results validated for relevance
- [ ] Similarity scores within expected range
- [ ] Metadata captured for debugging
```

**Changes Summary:**
- ✅ Updated SchemaVersion: v3.1 → v3.2
- ✅ Added LastUpdated: 2025-01-05
- ✅ Removed Purpose section
- ✅ Removed Rule Scope section
- ✅ Added unified Scope section with markers
- ✅ Removed Quick Start TL;DR (merged into Mandatory)
- ✅ Moved References early (after Scope)
- ✅ Converted Contract XML tags to Markdown headers
- ✅ Updated TokenBudget: ~2400 → ~2200 (Quick Start removal saved tokens)
- ✅ Incremented RuleVersion: v1.0.0 → v1.1.0 (schema upgrade)

---

## Validation

### Schema Validator

**Run validator on single file:**
```bash
python scripts/schema_validator.py rules/116-snowflake-cortex-search.md
```

**Expected output (success):**
```
================================================================================
VALIDATION REPORT: rules/116-snowflake-cortex-search.md
================================================================================

SUMMARY:
  ❌ CRITICAL: 0
  ⚠️  HIGH: 0
  ℹ️  MEDIUM: 0
  ✓ Passed: 47 checks

================================================================================
RESULT: ✓ PASSED
================================================================================
```

**Run validator on all rules:**
```bash
python scripts/schema_validator.py rules/
```

**Expected output (all pass):**
```
Validating 113 rule files...

✓ 000-global-core.md
✓ 001-memory-bank.md
✓ 002-rule-governance.md
...
✓ 950-create-dbt-semantic-view.md

================================================================================
SUMMARY: 113 files validated
  ✓ Passed: 113
  ❌ Failed: 0
================================================================================
```

---

### Common Validation Errors

#### Error: Missing Scope Section
```
❌ CRITICAL: Scope section is required after Metadata
   Fix: Add ## Scope section with required markers
```

**Solution:**
```markdown
## Scope

**What This Rule Covers:**
- [Describe coverage]

**When to Load This Rule:**
- [Describe scenarios]
```

---

#### Error: XML Tags in Contract
```
⚠️ HIGH: Contract must NOT use XML tags (v3.2 uses Markdown headers only)
   Fix: Replace XML tags with Markdown headers (###)
```

**Solution:**
```markdown
# Before
<mandatory>
- Rule 1
</mandatory>

# After
### Mandatory
- Rule 1
```

---

#### Error: Missing LastUpdated Field
```
⚠️ HIGH: LastUpdated must be date format YYYY-MM-DD
   Fix: Add **LastUpdated:** YYYY-MM-DD with current date
```

**Solution:**
```markdown
**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2025-01-05  ← Add this field
```

---

#### Error: References Section Late in File
```
⚠️ HIGH: References must be after Scope, before Contract (early position)
   Fix: Move References section to after Scope
```

**Solution:**
Move `## References` section to appear after `## Scope` and before `## Contract`.

---

## Examples

### Simple Rule Migration

**File:** `300a-bash-security.md`

**Before (v3.1):**
```markdown
# 300a-bash-security

## Metadata
**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** bash, security, shellcheck, validation, best-practices, scripting, hardening, input-validation, privilege-escalation, command-injection
**TokenBudget:** ~800
**ContextTier:** High
**Depends:** 000-global-core.md, 300-bash-scripting-core.md

## Purpose
This rule provides security hardening guidance for Bash scripts.

## Rule Scope
- Input validation
- Command injection prevention
- Privilege management

## Quick Start TL;DR
1. Always validate user input
2. Use shellcheck for static analysis
3. Avoid eval and command substitution with user input

## Contract
<mandatory>
- Validate all user input
- Use shellcheck
</mandatory>

## References
### Dependencies
- 000-global-core.md
- 300-bash-scripting-core.md
```

**After (v3.2):**
```markdown
# 300a-bash-security

## Metadata
**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2025-01-05
**Keywords:** bash, security, shellcheck, validation, best-practices, scripting, hardening, input-validation
**TokenBudget:** ~700
**ContextTier:** High
**Depends:** 000-global-core.md, 300-bash-scripting-core.md

## Scope

**What This Rule Covers:**
- Input validation and sanitization in Bash scripts
- Command injection prevention techniques
- Privilege management and escalation prevention
- Static analysis with shellcheck

**When to Load This Rule:**
- When writing security-sensitive Bash scripts
- When accepting user input in shell scripts
- When performing security reviews of existing scripts

## References

### Dependencies
- 000-global-core.md
- 300-bash-scripting-core.md

### External Documentation
- [ShellCheck Wiki](https://www.shellcheck.net/wiki/)
- [Bash Security Best Practices](https://mywiki.wooledge.org/BashGuide/Practices)

## Contract

### Inputs and Prerequisites
- Bash 4.0+ installed
- shellcheck available for static analysis

### Mandatory
- Validate all user input before use
- Use shellcheck on all scripts
- Quote all variables to prevent word splitting
- Avoid eval and command substitution with user input

### Forbidden
- Never use eval with user input
- Don't trust environment variables without validation
- Avoid running scripts with elevated privileges unless necessary

### Execution Steps
1. Validate prerequisites (Bash version, shellcheck)
2. Review script for user input points
3. Add input validation for all user inputs
4. Run shellcheck and fix all warnings
5. Test with malicious input samples
6. Document security assumptions

### Output Format
Scripts should exit with appropriate codes:
- 0: Success
- 1: Validation failure
- 2: Security violation detected

### Validation
- shellcheck returns 0 (no warnings)
- All user inputs validated
- No eval or command substitution with untrusted data

### Post-Execution Checklist
- [ ] shellcheck passes with no warnings
- [ ] All user inputs validated
- [ ] Security review completed
- [ ] Test cases include malicious input
```

**Token Savings:** ~100 tokens (Quick Start removal, consolidated sections)

---

### Complex Rule Migration

**File:** `115-snowflake-cortex-agents-core.md`

**Changes:**
- Removed 40-line Quick Start section (merged into Contract)
- Unified Purpose + Rule Scope into Scope (saved 25 lines)
- Moved References early (improved dependency discovery)
- Converted Contract XML tags to Markdown headers
- Added LastUpdated field
- Updated TokenBudget: ~4200 → ~3900 (300 tokens saved)

**Result:** More concise, better structured, easier for agents to parse

---

## Migration Statistics

**Project-Wide Migration (v3.1 → v3.2):**
- **Files Updated:** 113 rule files
- **Commits:** 8 commits in feat/rule-schema-updates branch
- **Token Savings:** ~15,000-20,000 tokens across all rules
- **Validation:** 100% pass rate (0 errors)
- **Duration:** 5 days (Dec 23, 2025 - Jan 5, 2026)

**Breakdown by Change Type:**
- Schema version updates: 113 files
- Quick Start removal: 2 files (501, 950)
- Contract XML → Markdown: 113 files
- References moved early: 113 files
- LastUpdated added: 113 files
- Scope section unified: 113 files

---

## Troubleshooting

### Issue: Validation Fails After Migration

**Symptom:**
```
❌ CRITICAL: Scope section is required after Metadata
```

**Cause:** Forgot to add unified Scope section

**Solution:**
1. Add `## Scope` section after Metadata
2. Include both required markers:
   - `**What This Rule Covers:**`
   - `**When to Load This Rule:**`

---

### Issue: TokenBudget Variance > 10%

**Symptom:**
```
ℹ️ MEDIUM: TokenBudget ~2400 differs from actual ~2150 by 11.6%
   Fix: Update to: ~2150
```

**Cause:** Quick Start removal reduced token count significantly

**Solution:**
Update TokenBudget to match actual count:
```markdown
**TokenBudget:** ~2150
```

---

### Issue: Contract Subsections Out of Order

**Symptom:**
```
⚠️ HIGH: Contract subsections must appear in correct order
```

**Cause:** Subsections not in required order

**Solution:**
Reorder to match required sequence:
1. Inputs and Prerequisites
2. Mandatory
3. Forbidden
4. Execution Steps
5. Output Format
6. Validation
7. Post-Execution Checklist

---

## Related Documentation

- **Schema Specification:** `schemas/rule-schema.yml`
- **Schema README:** `schemas/README.md`
- **Rule Governance:** `rules/002-rule-governance.md`
- **Schema Validator Usage:** `rules/002d-schema-validator-usage.md`
- **Rule Creation Guide:** `rules/002a-rule-creation-guide.md`
- **Project CHANGELOG:** `CHANGELOG.md` (see v3.5.0 entry)

---

## Version History

| Version | Date       | Changes |
|---------|------------|---------|
| v3.2    | 2025-01-05 | Initial schema v3.2 migration guide |

---

## Feedback and Questions

If you encounter issues during migration or have questions about schema v3.2:

1. **Check validation errors:** Run `python scripts/schema_validator.py rules/NNN-rule.md`
2. **Review examples:** See [Examples](#examples) section above
3. **Consult schema docs:** `schemas/README.md` has detailed field documentation
4. **Check CHANGELOG:** `CHANGELOG.md` v3.5.0 entry has migration summary

---

## Summary

Schema v3.2 represents a significant improvement in rule structure:

**Key Benefits:**
- ✅ **Reduced redundancy** - Eliminated duplicate content (Quick Start, Purpose)
- ✅ **Improved agent parsing** - Unified Scope with structured markers
- ✅ **Better dependency discovery** - Early References placement
- ✅ **Universal format** - Markdown headers instead of XML tags
- ✅ **Token efficiency** - Saved 15,000-20,000 tokens across all rules
- ✅ **Temporal context** - LastUpdated field for troubleshooting

**Migration Success:**
- All 113 rules upgraded to v3.2
- 100% validation pass rate
- Zero breaking changes to rule content
- Improved maintainability and clarity

Schema v3.2 is now the standard for all new and updated rules.
