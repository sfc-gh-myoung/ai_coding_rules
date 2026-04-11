# Rule Optimization: Token Budgets and Performance

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.1
**LastUpdated:** 2026-03-09
**Keywords:** token budget, optimization, performance, rule sizing, progressive loading, context window, model limits, cost efficiency, caching, batch loading
**TokenBudget:** ~4350
**ContextTier:** High
**Depends:** 002-rule-governance.md, 000-global-core.md, 002k-model-optimization.md

## Scope

**What This Rule Covers:**
Guidelines for optimizing rule token budgets, sizing rules appropriately, and loading rules efficiently. Covers token budget tiers (Small: 1000-1999, Standard: 2000-3499, Large: 3500-4999, Reference: 5000+), progressive loading strategies, and performance optimization across different AI models for cost efficiency.

Note: Tier boundaries are inclusive on the lower end. A rule at exactly 2000 tokens
is Standard tier. A rule at exactly 3500 tokens is Large tier.

**When to Load This Rule:**
- Creating rules with appropriate token budgets
- Optimizing existing rules for performance
- Understanding progressive rule loading strategies
- Sizing rules for specific AI models and context windows

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Schema requirements and standards
- **000-global-core.md** - Foundation for all rules

**Related:**
- **002a-rule-creation.md** - Step-by-step rule creation workflow
- **002k-model-optimization.md** - Model-specific context windows and loading budgets

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema
- **Rules Index:** `RULES_INDEX.md` - Master index with current token budgets
- **Token Validator:** `ai-rules tokens` - CLI command for measuring actual token counts

## Contract

### Inputs and Prerequisites

- Rule content to optimize
- Token count estimation
- Target AI model
- Target response latency or context budget constraint

### Mandatory

- `ai-rules tokens` CLI command
- `ai-rules validate` CLI command
- Word count tools (wc)
- Model context window knowledge

### Forbidden

- Using text labels for TokenBudget (small/medium/large)
- Creating rules >7000 tokens without splitting
- Duplicating content across rules

### Execution Steps

1. Estimate rule token count using `uv run ai-rules tokens rules/<rule>.md`
   (manual fallback: word count × 1.33 ≈ token count)
2. Choose appropriate TokenBudget tier based on size
3. Set ContextTier to match tier (Small=Critical/High, Standard=High/Medium, etc.)
4. Verify rule focuses on single concept (all Keywords share a common domain;
   rule can be summarized in one sentence without "and" joining unrelated topics)
5. Run `ai-rules tokens` to confirm actual count
6. Split rule if >5000 tokens (review recommended) or >5500 tokens (split required),
   or if it covers multiple unrelated topics

### Output Format

Rule file with:
- TokenBudget metadata matching actual size (`~NUMBER` format)
- ContextTier aligned with token budget tier
- Focused on single concept
- Token count: 2000-3500 tokens (optimal), <5000 tokens (acceptable),
  5000-5500 (review and consider splitting), >5500 (split required)

### Validation

**Pre-Task-Completion Checks:**
- TokenBudget declared with `~NUMBER` format (no text labels)
- ContextTier matches TokenBudget tier appropriately
- Rule size calculated or estimated
- Rule focuses on single concept: all Keywords cluster around one domain,
  and the Scope section describes one coherent purpose. A rule covering "token budgets
  AND progressive loading AND model optimization" is multi-topic — split into focused rules.
- `ai-rules tokens` ready to run

**Success Criteria:**
- TokenBudget format: `~NUMBER` (e.g., ~2500)
- ContextTier matches tier: Small=Critical/High, Standard=High/Medium, etc.
- Actual token count within +/-5% of declared budget (validator default, see Variance Tolerance)
- Rule size 2000-3500 tokens (preferred) or <5000 tokens (maximum)
- `ai-rules tokens` passes without update warnings

**Negative Tests:**
- Text label TokenBudget (small/medium/large) triggers validation error
- Missing tilde prefix triggers format error
- Token variance >5% triggers auto-update (configurable via `--threshold`)
- Rule >5000 tokens triggers split review; >5500 tokens triggers mandatory
  split recommendation

**Error Recovery:**
- **`ai-rules tokens` not found:** Check `uv run ai-rules tokens` is available, fall back to word count estimate (words x 1.33)
- **Validator fails to parse rule:** Check for malformed YAML/frontmatter, validate Markdown syntax first
- **Token count wildly off:** Re-run validator, check for binary content or encoding issues

### Auto-Update Recovery

If `uv run ai-rules tokens` was run without `--dry-run` and modified files unintentionally:

1. **Check git status:** `git diff rules/<rule>.md` to see what changed
2. **If only TokenBudget changed:** Verify the new value is accurate — keep it if correct
3. **If other content changed unexpectedly:** Revert with `git checkout -- rules/<rule>.md`
4. **Prevention:** Always use `--dry-run` first: `uv run ai-rules tokens --dry-run rules/<rule>.md`

### Post-Execution Checklist

- [ ] TokenBudget declared with `~NUMBER` format (no text labels)
- [ ] ContextTier matches TokenBudget tier appropriately
- [ ] Rule size 2000-3500 tokens (optimal) or <5000 tokens (preferred)
- [ ] `ai-rules tokens` confirms budget within +/-5% of actual (default threshold, use `--threshold 10` for lenient audits)
- [ ] Rule focuses on single concept (not multi-topic)
- [ ] Dependencies declared to avoid loading duplicate content
- [ ] Rule added to appropriate tier for progressive loading
- [ ] If >5500 tokens, plan created to split into multiple focused files

## Rule Sizing Guidelines

### Rule Size Summary

**Token Ranges:**
- **Optimal (2000-3500):** Load normally
- **Acceptable (3500-5000):** Load when task requires
- **Caution (5000-7000):** Evaluate split using decision tree below
- **Avoid (>7000):** Split into focused files

**Line Count Targets:**
- **Optimal:** 200-400 lines (~2000-3500 tokens) - Standard rules
- **Maximum:** 600 lines (~5000 tokens) - Complex rules
- **Split Required:** >800 lines (>5500 tokens) - Multi-concept rules

**Focus Principle:** One rule per major concept or technology area. Reference other rules rather than duplicating content.

### When to Split Rules (Decision Tree)

**Split if ANY of these conditions are true:**
1. **Token count >5500** AND rule covers multiple major concepts
2. **Rule addresses 3+ independent use cases** (even if <5500 tokens)
3. **Sections can be loaded independently** without requiring cross-references back to the parent rule for basic execution
4. **Different sections target different loading contexts** (e.g., core vs advanced patterns)

**Do NOT split if:**
- Rule is a linear workflow where steps depend on prior context
- Splitting would create circular dependencies
- Concepts are tightly coupled (e.g., error handling for a specific API)

**Split Test:** If you can't clearly name split files with distinct, non-overlapping topics, don't split.

### TokenBudget Declaration (MANDATORY)

**Format:** `**TokenBudget:** ~[number]`

**Examples:**
- [PASS] `**TokenBudget:** ~1850`
- [PASS] `**TokenBudget:** ~2500`
- [PASS] `**TokenBudget:** ~3300`
- [FAIL] `**TokenBudget:** small` (FORBIDDEN)
- [FAIL] `**TokenBudget:** medium` (FORBIDDEN)
- [FAIL] `**TokenBudget:** 1200` (missing tilde)

**Calculation:** Token estimation methods (in order of accuracy):
1. **CLI tool (recommended):** `uv run ai-rules tokens rules/<rule>.md`
2. **Word-based heuristic:** word count × 1.33 ≈ token count
3. **Character-based heuristic:** character count / 4 ≈ token count

Note: Line-based estimation is unreliable (actual tokens per line varies from 3 to 12
depending on content density). Do not use "tokens per line" for estimation.

> **IMPORTANT:** Token budget examples are point-in-time snapshots. Before relying on specific values for budget calculations:
> 1. Check **RULES_INDEX.md** (auto-generated, always current)
> 2. Or run: `uv run ai-rules tokens rules/002-rule-governance.md --detailed`
> 3. Trust declared metadata over narrative examples

## Token Budget Tiers

### ContextTier Selection Guide (Secondary Signal)

This section extends the basic ContextTier definition in `002-rule-governance.md` with detailed selection criteria and use cases.

ContextTier provides fine-grained prioritization within natural language tiers:

**ContextTier Values:**
- **Critical:** Bootstrap files only - always has CRITICAL marker
- **High:** Domain cores, frequently referenced - usually has CORE RULE/FOUNDATION RULE marker
- **Medium:** Specialized rules for common tasks - no marker (can be summarized)
- **Low:** Reference documentation, examples - no marker (summarize first)

**Primary Mechanism:** Natural language markers (CRITICAL/CORE/FOUNDATION)
**Secondary Mechanism:** ContextTier metadata

See `000-global-core.md`, section "Context Window Management Protocol" for preservation hierarchy.

### Small (1000-1999 tokens)

**TokenBudget Range:** `~1000` to `~2000`
**ContextTier:** Critical or High
**Use Cases:**
- Focused utility rules
- Single-concept patterns
- Lint/format configurations
- Security constraints

**Real Examples:**
- `001-memory-bank.md` (~1400 tokens) - Context management
- `101-snowflake-streamlit-core.md` (~1950 tokens)

**Loading:** Load based on task domain and keywords

### Standard (2000-3499 tokens)

**TokenBudget Range:** `~2000` to `~3500`
**ContextTier:** High or Medium
**Use Cases:**
- Technology-specific core patterns
- Framework foundations
- Language core guidelines
- Common workflows

**Real Examples:**
- `115-snowflake-cortex-agents-core.md` (~2500 tokens)
- `201-python-lint-format.md` (~3100 tokens)
- `221b-python-htmx-flask.md` (~3300 tokens)

**Loading:** Loaded based on task domain (Python tasks -> load 200-python-core)

### Large (3500-4999 tokens)

**TokenBudget Range:** `~3500` to `~5000`
**ContextTier:** Medium or Low
**Use Cases:**
- Complex multi-step workflows
- Comprehensive domain cores
- Advanced optimization techniques
- Multi-section documentation

**Real Examples:**
- `206-python-pytest.md` (~3600 tokens)
- `002d-advanced-rule-patterns.md` (~3700 tokens)
- `000-global-core.md` (~3800 tokens) - Foundation
- `100-snowflake-core.md` (~4350 tokens) - Snowflake foundation

**Loading:** Loaded when specifically needed for complex tasks

### Reference (5000+ tokens)

**TokenBudget Range:** `~5000` to `~7000`
**ContextTier:** Low
**Use Cases:**
- Exhaustive guides
- Complete framework documentation
- Reference documentation (loaded rarely)

**Real Examples:**
- `200-python-core.md` (~6500 tokens) - Python foundation

**Loading:** Loaded only when explicitly requested or for reference

### Oversized (>7000 tokens) - AVOID

**TokenBudget Range:** `>7000`
**Status:** [FAIL] **SHOULD BE SPLIT**
**Problem:** Rules >7000 tokens degrade performance and waste context budget

**Solution:** Split into multiple focused files using letter suffixes (e.g., 101a, 101b, 101c)

> **Semantic Coherence vs Token Optimization:** Never sacrifice rule coherence for token savings. A 6000-token rule covering a tightly coupled workflow is better than three 2000-token rules with circular dependencies. Split only when concepts are genuinely separable.

**Split File Naming Convention:**

Split files use the standard filename pattern with a single lowercase letter suffix:

**Pattern:** `<NNN>[<letter>]-<technology>-<aspect>.md`

Single-letter suffix only (a-z). Multi-character suffixes (a1, b2) are NOT allowed.

- Letter suffixes indicate subtopic specialization
- Core file (no suffix) provides foundation; suffixes extend it
- Load only the suffix needed for the task (saves tokens)
- Examples:
  - `101-snowflake-streamlit-core.md` - Foundation (no suffix)
  - `101a-snowflake-streamlit-visualization.md` - Visualization patterns
  - `101b-snowflake-streamlit-performance.md` - Performance optimization
  - `101c-snowflake-streamlit-security.md` - Security patterns

## Model-Specific Optimization

For model-specific context windows, loading budgets, and optimization strategies (OpenAI, Anthropic, Google), see **002k-model-optimization.md**.

**Quick Reference - Loading Budget Formula:**
```
Loading Budget = 30-40% of context window
```
If you're loading >40% of context window with rules, you're likely over-loading.

## Progressive Loading Strategy

### Critical Rules (Always Load)

Load at every session start:
- `000-global-core.md` (~3800 tokens) - Foundation

Then add domain core based on task:
- Python tasks: `200-python-core.md` (~6500 tokens)
- Snowflake tasks: `100-snowflake-core.md` (~4350 tokens)
- Streamlit tasks: `101-snowflake-streamlit-core.md` (~1950 tokens)

**Total:** ~6,000-10,000 tokens baseline

### Standard Context (Most Tasks)

Foundation + Domain Core + 2-3 specialized rules:

**Example - Python Testing Task:**
- `000-global-core.md` (~3800)
- `200-python-core.md` (~6500)
- `206-python-pytest.md` (~3600)
- `201-python-lint-format.md` (~3100)

**Total:** ~17,000 tokens

### Extended Context (Complex Tasks)

Foundation + Domain Core + 4-6 specialized rules:

**Example - Streamlit Dashboard with Snowflake:**
- `000-global-core.md` (~3800)
- `100-snowflake-core.md` (~4350)
- `101-snowflake-streamlit-core.md` (~1950)
- `115-snowflake-cortex-agents-core.md` (~2500)

**Total:** ~12,600 tokens

### Maximum Context (Comprehensive Projects)

Foundation + Multiple Domain Cores + Full rule families:

**Example - Multi-Domain Project:**
- `000-global-core.md` (~3800)
- Python core + 3 specialized (~10,000 tokens)
- Snowflake core + 3 specialized (~12,000 tokens)

**Total:** ~25,800 tokens

**Note:** Only for comprehensive implementations; most tasks need <15K tokens

### Deferring Rules (When to Skip)

**Defer loading a rule if:**
- Task is read-only (no modifications) AND rule is for editing patterns
- Rule's Keywords don't match any terms in the user's request
- Rule is Low tier AND you're already at 80%+ of loading budget
- Rule covers features not matching any keywords in the user's request

**Never defer:**
- `000-global-core.md` (always required)
- Domain core rules when modifying files of that type
- Rules explicitly requested by user

**Declaration format when deferring:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- [Deferred: 204-python-docs.md - Low tier, not required for task]
```

### Loading Approach

- **Incremental (default):** Load foundation, then domain core, then add specialized rules as task complexity demands. Load additional rules on errors or blockers. Most tasks need ~10K-14K tokens.
- **Batch (complex tasks):** Load foundation + multiple domain cores + specialized rules together for multi-domain work. Expect ~16K-20K tokens.
- **Reference (rare):** Load standard context, then add a reference rule on-demand for documentation lookups. Temporary spike to ~16K tokens.

## Token Budget Validation

### Running ai-rules tokens

> **WARNING:** Running without `--dry-run` will **automatically update** TokenBudget values in rule files. Use `--dry-run` to preview changes first.

```bash
# Validate single file (read-only check)
uv run ai-rules tokens rules/002-rule-governance.md --detailed

# Validate all rules (read-only check)
uv run ai-rules tokens rules/ --detailed --dry-run

# Auto-update all rules exceeding threshold
uv run ai-rules tokens rules/

# Output example:
# rules/002-rule-governance.md:
#   Declared: ~1850
#   Actual: 1920
#   Variance: +3.8% (within tolerance)
```

### Token Count Estimation

**Quick Estimate:**
```bash
# Word count
wc -w rules/<your-rule>.md
# 2100 words

# Convert to tokens (multiply by ~1.33)
# 2100 x 1.33 = 2,793 tokens

# Round to nearest 50
# TokenBudget: ~2800
```

### Variance Tolerance

**Default threshold:** +/-5% (validator default, configurable via `--threshold`)

**Variance Handling:**
- **≤5% variance:** PASS - No update needed
- **>5% variance:** UPDATE - Validator auto-updates TokenBudget

**Examples:**
- Declared: `~2500`, Actual: `2600` (+4%) - PASS (within tolerance)
- Declared: `~2500`, Actual: `2650` (+6%) - UPDATE (auto-corrected to `~2650`)

**Custom threshold:** Use `--threshold 10` for more lenient validation during audits.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Text Labels for TokenBudget**

```markdown
# Problem: Using text labels
**TokenBudget:** small
**TokenBudget:** medium
**TokenBudget:** large
```
**Problem:** Text labels are not parseable by validation tools and don't provide actual token counts for loading strategy decisions.

**Correct Pattern:**
```markdown
# Use numeric values with tilde prefix
**TokenBudget:** ~1850
**TokenBudget:** ~2500
**TokenBudget:** ~3300
```
**Benefits:** Parseable, enables progressive loading decisions, accurate context budget tracking.

**Anti-Pattern 2: Loading All Rules at Start**

**Problem:** Loading all 100+ rules at session start (>250K tokens)
- Wastes context budget
- Increases latency
- Reduces performance
- Unnecessary for most tasks

**Correct Pattern:** Progressive loading (~10K-20K tokens)
```
# Load only what's needed
1. Foundation: 000-global-core.md (~3800)
2. Domain: 200-python-core.md (~6500) based on task
3. Specialized: 206-python-pytest.md (~3600) as needed
```
**Benefits:** Efficient, focused, fast - uses 5-10% of context budget instead of 100%.
