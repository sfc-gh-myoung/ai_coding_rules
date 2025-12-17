# Rule Optimization: Token Budgets and Performance

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** token budget, optimization, performance, rule sizing, progressive loading, context window, model limits, cost efficiency, caching, batch loading
**TokenBudget:** ~3500
**ContextTier:** High
**Depends:** rules/002-rule-governance.md, rules/000-global-core.md

## Purpose

Guidelines for optimizing rule token budgets, sizing rules appropriately, and loading rules efficiently across different AI models for maximum performance and cost efficiency.

## Rule Scope

All AI agents creating, maintaining, or loading rule files in the ai_coding_rules repository.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Token budget tiers** - Small (1000-2000), Standard (2000-3500), Large (3500-5000), Reference (5000+)
- **Optimal rule size** - 2000-3500 tokens per rule for best performance across all models
- **Progressive loading** - Load 000-global-core + domain core + 2-4 specialized rules as needed
- **TokenBudget format** - `~NUMBER` (e.g., ~1850, ~2500, ~3300) - NEVER use text labels
- **Avoid bloat** - Rules >5000 tokens should be split into multiple focused files

**Pre-Execution Checklist:**
- [ ] TokenBudget declared in metadata with `~NUMBER` format
- [ ] ContextTier matches token budget tier
- [ ] Rule size 2000-3500 tokens for optimal performance
- [ ] Rule focuses on single concept (not multiple unrelated topics)
- [ ] Dependencies minimize token budget overlap

## Contract

<inputs_prereqs>
Rule content to optimize; token count estimation; target AI model; performance requirements
</inputs_prereqs>

<mandatory>
token_validator.py; schema_validator.py; word count tools (wc); model context window knowledge
</mandatory>

<forbidden>
Using text labels for TokenBudget (small/medium/large); creating rules >7000 tokens; duplicating content across rules
</forbidden>

<steps>
1. Estimate rule token count (words x 1.33 = tokens approximately)
2. Choose appropriate TokenBudget tier based on size
3. Set ContextTier to match tier (Small=Critical/High, Standard=High/Medium, etc.)
4. Verify rule focuses on single concept
5. Run token_validator.py to confirm actual count
6. Split rule if >5000 tokens or covers multiple unrelated topics
</steps>

<output_format>
Rule file with TokenBudget and ContextTier metadata matching actual size
</output_format>

<validation>
- TokenBudget within +/-15% of actual token count (validator default threshold)
- Rule size 2000-3500 tokens (preferred) or <5000 tokens (maximum)
- ContextTier matches TokenBudget tier
- token_validator.py confirms budget accuracy
</validation>

## Rule Sizing Guidelines

### Rule Size Summary

**Token Ranges:**
- **Optimal (2000-3500):** Load normally
- **Acceptable (3500-5000):** Load when task requires
- **Caution (5000-7000):** Consider if split needed
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
3. **Sections can be loaded independently** without losing coherence
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

**Calculation:** Approximately 1.33 tokens per word, or 5-6 tokens per line as rough estimate.

> **IMPORTANT:** Token budget examples are point-in-time snapshots. Before relying on specific values for budget calculations:
> 1. Check **RULES_INDEX.md** (auto-generated, always current)
> 2. Or run: `python3 scripts/token_validator.py rules/002-rule-governance.md --detailed`
> 3. Trust declared metadata over narrative examples

## Token Budget Tiers

### ContextTier Selection Guide (Secondary Signal)

ContextTier provides fine-grained prioritization within natural language tiers:

**ContextTier Values:**
- **Critical:** Bootstrap files only - always has CRITICAL marker
- **High:** Domain cores, frequently referenced - usually has CORE RULE/FOUNDATION RULE marker
- **Medium:** Specialized rules for common tasks - no marker (can be summarized)
- **Low:** Reference documentation, examples - no marker (summarize first)

**Primary Mechanism:** Natural language markers (CRITICAL/CORE/FOUNDATION)
**Secondary Mechanism:** ContextTier metadata

See `000-global-core.md`, section "Context Window Management Protocol" for preservation hierarchy.

### Small (1000-2000 tokens)

**TokenBudget Range:** `~1000` to `~2000`
**ContextTier:** Critical or High
**Use Cases:**
- Focused utility rules
- Single-concept patterns
- Lint/format configurations
- Security constraints

**Real Examples:**
- `002-rule-governance.md` (~1850 tokens)
- `201-python-lint-format.md` (~1950 tokens)
- `221b-python-htmx-flask.md` (~1950 tokens)

**Loading:** Load based on task domain and keywords

### Standard (2000-3500 tokens)

**TokenBudget Range:** `~2000` to `~3500`
**ContextTier:** High or Medium
**Use Cases:**
- Technology-specific core patterns
- Framework foundations
- Language core guidelines
- Common workflows

**Real Examples:**
- `000-global-core.md` (~3300 tokens) - Foundation
- `100-snowflake-core.md` (~2850 tokens) - Snowflake foundation
- `001-memory-bank.md` (~2850 tokens) - Context management
- `002c-advanced-rule-patterns.md` (~2900 tokens)

**Loading:** Loaded based on task domain (Python tasks -> load 200-python-core)

### Large (3500-5000 tokens)

**TokenBudget Range:** `~3500` to `~5000`
**ContextTier:** Medium or Low
**Use Cases:**
- Complex multi-step workflows
- Comprehensive domain cores
- Advanced optimization techniques
- Multi-section documentation

**Real Examples:**
- `200-python-core.md` (~4050 tokens) - Python foundation
- `115-snowflake-cortex-agents-core.md` (~4650 tokens)
- `101-snowflake-streamlit-core.md` (~3700 tokens)

**Loading:** Loaded when specifically needed for complex tasks

### Reference (5000+ tokens)

**TokenBudget Range:** `~5000` to `~7000`
**ContextTier:** Low
**Use Cases:**
- Exhaustive guides
- Complete framework documentation
- Reference documentation (loaded rarely)

**Real Examples:**
- `204-python-docs-comments.md` (~5700 tokens)
- `803-project-git-workflow.md` (~5200 tokens)
- `820-taskfile-automation.md` (~7100 tokens)

**Loading:** Loaded only when explicitly requested or for reference

### Oversized (>7000 tokens) - AVOID

**TokenBudget Range:** `>7000`
**Status:** [FAIL] **SHOULD BE SPLIT**
**Problem:** Rules >7000 tokens degrade performance and waste context budget

**Solution:** Split into multiple focused files using letter suffixes (e.g., 101a, 101b, 101c)

> **Semantic Coherence vs Token Optimization:** Never sacrifice rule coherence for token savings. A 6000-token rule covering a tightly coupled workflow is better than three 2000-token rules with circular dependencies. Split only when concepts are genuinely separable.

**Split File Naming Convention:**
- Letter suffixes indicate subtopic specialization
- Core file (no suffix) provides foundation; suffixes extend it
- Load only the suffix needed for the task (saves tokens)
- Examples:
  - `101-snowflake-streamlit-core.md` - Foundation
  - `101a-snowflake-streamlit-visualization.md` - Visualization patterns
  - `101b-snowflake-streamlit-performance.md` - Performance optimization
  - `101c-snowflake-streamlit-security.md` - Security patterns

## Model-Specific Optimization

> **Note:** Model specifications evolve rapidly. These guidelines are based on official documentation as of December 2025. Verify against current provider documentation for production deployments.

### Loading Budget Formula

**Context Window ≠ Loading Budget**

Agents should follow this formula:

```
Loading Budget = 30-40% of context window
```

Reserve remaining context for:
- User prompts and conversation history (~20-30%)
- Generated code and outputs (~20-30%)
- Safety margin for tool responses (~10-20%)

**Model Context Windows (30-40% loading budget):**
- **GPT-4o:** 128K context allows 38K-51K tokens for rules
- **GPT-5.1:** 400K context allows 120K-160K tokens for rules
- **Claude Sonnet 4.5:** 200K context allows 60K-80K tokens for rules
- **Gemini 3 Pro:** 1M context allows 300K-400K tokens for rules

**Rule of Thumb:** If you're loading >40% of context window with rules, you're likely over-loading.

### OpenAI Models

#### GPT-4o (128K context)

**Optimal Rule Size:** 2000-3500 tokens per rule
**Context Budget:** Load 10-20 rules (~25K-40K tokens total)
**Performance:** Best with focused, standard-sized rules
**Strategy:** Prioritize small and standard tiers; defer reference tier

#### GPT-5.1 (400K context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 30-80 rules (~60K-150K tokens total)
**Max Output:** 128K tokens
**Performance:** Excellent with comprehensive rule sets
**Strategy:** Can load entire rule families; leverage configurable reasoning effort for complex tasks
**Pricing:** $1.25/M input, $10.00/M output

*Source: [platform.openai.com/docs/models/gpt-5.1](https://platform.openai.com/docs/models/gpt-5.1)*

### Anthropic Models

#### Claude Sonnet 4 / Opus 4 (200K context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 15-30 rules (~40K-70K tokens total)
**Performance:** Excellent with comprehensive rules
**Strategy:** Can handle larger rule sets; use prompt caching for repeated rules

#### Claude Sonnet 4.5 (200K standard / 1M beta)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 15-40 rules (~40K-100K tokens standard); 100+ rules with 1M beta
**Max Output:** 64K tokens
**Performance:** Excels in coding, finance, cybersecurity tasks
**Strategy:** Use prompt caching (90% cost reduction on cache hits); leverage extended context for comprehensive projects
**Pricing:** $3/M input, $15/M output (standard); $6/M input, $22.50/M output (>200K)

*Source: [docs.claude.com/claude/docs/models-overview](https://docs.claude.com/claude/docs/models-overview)*

#### Claude Opus 4.5 (200K context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 15-30 rules (~40K-70K tokens total)
**Max Output:** 32K tokens
**Performance:** High-level reasoning and deep analysis; best for complex technical tasks
**Strategy:** Reserve for tasks requiring sophisticated reasoning; use Sonnet 4.5 for routine tasks
**Pricing:** $15/M input, $75/M output

*Source: [docs.claude.com/claude/docs/models-overview](https://docs.claude.com/claude/docs/models-overview)*

### Google Models

#### Gemini 2.5 Pro (1M context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 30-100+ rules (~60K-200K tokens total)
**Performance:** Minimal constraints on rule loading
**Strategy:** Can load entire rule families; batch loading highly effective

#### Gemini 3 Pro (1M context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 30-100+ rules (~60K-200K tokens total)
**Performance:** Best-in-class reasoning, multimodality, and coding; tops WebDev Arena (1487 Elo)
**Strategy:** Excellent for agentic coding and long-horizon planning; use Deep Think mode for complex problems
**Key Features:** Zero-shot generation, advanced tool use, improved multi-step workflow execution

*Source: [blog.google/products/gemini/gemini-3](https://blog.google/products/gemini/gemini-3/)*

## Progressive Loading Strategy

### Critical Rules (Always Load)

Load at every session start:
- `000-global-core.md` (~3300 tokens) - Foundation

Then add domain core based on task:
- Python tasks: `200-python-core.md` (~4050 tokens)
- Snowflake tasks: `100-snowflake-core.md` (~2850 tokens)
- Streamlit tasks: `101-snowflake-streamlit-core.md` (~3700 tokens)

**Total:** ~6,000-7,000 tokens baseline

### Standard Context (Most Tasks)

Foundation + Domain Core + 2-3 specialized rules:

**Example - Python Testing Task:**
- `000-global-core.md` (~3300)
- `200-python-core.md` (~4050)
- `206-python-pytest.md` (~2050)
- `201-python-lint-format.md` (~1950)

**Total:** ~11,350 tokens

### Extended Context (Complex Tasks)

Foundation + Domain Core + 4-6 specialized rules:

**Example - Streamlit Dashboard with Snowflake:**
- `000-global-core.md` (~3300)
- `100-snowflake-core.md` (~2850)
- `101-snowflake-streamlit-core.md` (~3700)
- `115-snowflake-cortex-agents-core.md` (~4650)

**Total:** ~14,500 tokens

### Maximum Context (Comprehensive Projects)

Foundation + Multiple Domain Cores + Full rule families:

**Example - Multi-Domain Project:**
- `000-global-core.md` (~3300)
- Python core + 3 specialized (~10,000 tokens)
- Snowflake core + 3 specialized (~12,000 tokens)

**Total:** ~25,300 tokens

**Note:** Only for comprehensive implementations; most tasks need <15K tokens

### Deferring Rules (When to Skip)

**Defer loading a rule if:**
- Task is read-only (no modifications) AND rule is for editing patterns
- Rule's Keywords don't match any terms in the user's request
- Rule is Low tier AND you're already at 80%+ of loading budget
- Rule covers advanced features not needed for the current task

**Never defer:**
- `000-global-core.md` (always required)
- Domain core rules when modifying files of that type
- Rules explicitly requested by user

**Declaration format when deferring:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- [Deferred: 204-python-docs-comments.md - Low tier, not required for task]
```

## Loading Pattern Examples

### Pattern 1: Incremental Loading

```
# Session start
1. Load: 000-global-core (~3300 tokens)
2. Identify task domain from keywords
3. Load: Domain core rule (~2500-4000 tokens)
4. Analyze task complexity
5. Load: 2-3 most relevant specialized rules (~4000-6000 tokens)
6. Execute task
7. If errors/blockers: Load additional specialized rules as needed

Total context: ~10,000-14,000 tokens (efficient)
```

### Pattern 2: Batch Loading (Complex Task)

```
# Complex multi-domain task
1. Load: 000-global-core (~3300 tokens)
2. Batch load domain cores:
   - 100-snowflake-core (~2850)
   - 200-python-core (~4050)
3. Batch load specialized rules (3-5 rules): ~6000-10000 tokens
4. Execute with full context

Total context: ~16,000-20,000 tokens (comprehensive)
```

### Pattern 3: Reference Loading (Rare)

```
# When comprehensive documentation needed
1. Load: Standard context (~11,000 tokens)
2. Load: Reference rule on-demand (~5500 tokens)
3. Extract needed information
4. Continue with task

Total context: ~16,500 tokens (temporary spike)
```

## Token Budget Validation

### Running token_validator.py

> **WARNING:** Running without `--dry-run` will **automatically update** TokenBudget values in rule files. Use `--dry-run` to preview changes first.

```bash
# Validate single file (read-only check)
python3 scripts/token_validator.py rules/002-rule-governance.md --detailed

# Validate all rules (read-only check)
python3 scripts/token_validator.py rules/ --detailed --dry-run

# Auto-update all rules exceeding threshold
python3 scripts/token_validator.py rules/

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
wc -w rules/NNN-rule.md
# 2100 words

# Convert to tokens (multiply by ~1.33)
# 2100 x 1.33 = 2,793 tokens

# Round to nearest 50
# TokenBudget: ~2800
```

### Variance Tolerance

**Default threshold:** +/-15% (validator default, configurable via `--threshold`)

**Variance Handling:**
- **≤15% variance:** PASS - No update needed
- **>15% variance:** UPDATE - Validator auto-updates TokenBudget

**Examples:**
- Declared: `~2500`, Actual: `2650` (+6%) - PASS (within tolerance)
- Declared: `~2500`, Actual: `2950` (+18%) - UPDATE (auto-corrected to `~2950`)

**Custom threshold:** Use `--threshold 10` for stricter validation during audits.

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
1. Foundation: 000-global-core.md (~3300)
2. Domain: 200-python-core.md (~4050) based on task
3. Specialized: 206-python-pytest.md (~2050) as needed
```
**Benefits:** Efficient, focused, fast - uses 5-10% of context budget instead of 100%.

## Post-Execution Checklist

- [ ] TokenBudget declared with `~NUMBER` format (no text labels)
- [ ] ContextTier matches TokenBudget tier appropriately
- [ ] Rule size 2000-3500 tokens (optimal) or <5000 tokens (preferred)
- [ ] token_validator.py confirms budget within +/-10% of actual
- [ ] Rule focuses on single concept (not multi-topic)
- [ ] Dependencies declared to avoid loading duplicate content
- [ ] Rule added to appropriate tier for progressive loading
- [ ] If >5500 tokens, plan created to split into multiple focused files

## Validation

**Success Checks:**
- TokenBudget format: `~NUMBER` (e.g., ~2500)
- ContextTier matches tier: Small=Critical/High, Standard=High/Medium, etc.
- Actual token count within +/-15% of declared budget (validator default)
- Rule size 2000-3500 tokens (preferred) or <5000 tokens (maximum)
- token_validator.py passes without update warnings

**Negative Tests:**
- Text label TokenBudget (small/medium/large) triggers validation error
- Missing tilde prefix triggers format error
- Token variance >15% triggers auto-update (configurable via `--threshold`)
- Rule >5500 tokens triggers split recommendation

## Output Format Examples

### Example 1: Standard Rule Token Budget

```markdown
# 206-python-pytest

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** pytest, testing, fixtures, parametrization, test isolation
**TokenBudget:** ~2050
**ContextTier:** High
**Depends:** rules/200-python-core.md

# [Rule content - ~2050 tokens total]
```

### Example 2: Large Rule Token Budget

```markdown
# 115-snowflake-cortex-agents-core

**SchemaVersion:** v3.1
**Keywords:** Cortex Agents, multi-tool agents, planning instructions, testing
**TokenBudget:** ~4650
**ContextTier:** Medium
**Depends:** rules/100-snowflake-core.md

# [Rule content - ~4650 tokens total]
```

## References

### Related Rules
- **Rule Governance**: `002-rule-governance.md` - Schema requirements
- **Creation Guide**: `002a-rule-creation-guide.md` - Step-by-step rule creation workflow
- **Advanced Patterns**: `002c-advanced-rule-patterns.md` - System prompt altitude, multi-session workflows
- **Validator Usage**: `002d-schema-validator-usage.md` - Token validation commands

### Authoritative Sources
- **RULES_INDEX.md**: Contains declared TokenBudget for all rules (auto-generated, always current)
- **token_validator.py**: Validates token budgets against actual counts

### External Documentation
- **Schema Definition**: `schemas/rule-schema.yml` - Token budget validation rules
