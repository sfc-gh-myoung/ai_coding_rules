# Rule Optimization: Token Budgets and Performance

## Metadata

**SchemaVersion:** v3.0
**Keywords:** token budget, optimization, performance, rule sizing, progressive loading, context window, model limits, cost efficiency, caching, batch loading
**TokenBudget:** ~2350
**ContextTier:** High
**Depends:** rules/002-rule-governance.md, rules/000-global-core.md

## Purpose

Guidelines for optimizing rule token budgets, sizing rules appropriately, and loading rules efficiently across different AI models for maximum performance and cost efficiency.

## Rule Scope

All AI agents creating, maintaining, or loading rule files in the ai_coding_rules repository.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Token budget tiers** - Micro (<500), Standard (500-1500), Comprehensive (1500-3000), Reference (3000-5000)
- **Optimal rule size** - <3000 tokens per rule for best performance across all models
- **Progressive loading** - Load 000-global-core + domain core + 2-4 specialized rules as needed
- **TokenBudget format** - `~NUMBER` (e.g., ~450, ~1200, ~2500) - NEVER use text labels
- **Avoid splitting** - Rules >5000 tokens should be split into multiple focused files

**Pre-Execution Checklist:**
- [ ] TokenBudget declared in metadata with `~NUMBER` format
- [ ] ContextTier matches token budget tier
- [ ] Rule size <3000 tokens for optimal performance
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
Using text labels for TokenBudget (small/medium/large); creating rules >5000 tokens; duplicating content across rules
</forbidden>

<steps>
1. Estimate rule token count (words × 1.33 ≈ tokens)
2. Choose appropriate TokenBudget tier based on size
3. Set ContextTier to match tier (Micro=Essential, Standard=Standard, etc.)
4. Verify rule focuses on single concept
5. Run token_validator.py to confirm actual count
6. Split rule if >5000 tokens or covers multiple unrelated topics
</steps>

<output_format>
Rule file with TokenBudget and ContextTier metadata matching actual size
</output_format>

<validation>
- TokenBudget within ±10% of actual token count
- Rule size <3000 tokens (preferred) or <5000 tokens (maximum)
- ContextTier matches TokenBudget tier
- token_validator.py confirms budget accuracy
</validation>

## Rule Sizing Guidelines

### Line Count Targets

| Target | Line Count | Token Budget | Use Case |
|--------|------------|--------------|----------|
| **Target** | 150-300 lines | ~500-1500 tokens | Standard rules |
| **Maximum** | 500 lines | ~3000 tokens | Complex rules |
| **Split Required** | >800 lines | >5000 tokens | Multi-concept rules |

**Focus Principle:** One rule per major concept or technology area. Reference other rules rather than duplicating content.

### TokenBudget Declaration (MANDATORY)

**Format:** `**TokenBudget:** ~[number]`

**Examples:**
- [PASS] `**TokenBudget:** ~450`
- [PASS] `**TokenBudget:** ~1200`
- [PASS] `**TokenBudget:** ~2500`
- [FAIL] `**TokenBudget:** small` (FORBIDDEN)
- [FAIL] `**TokenBudget:** medium` (FORBIDDEN)
- [FAIL] `**TokenBudget:** 1200` (missing tilde)

**Calculation:** Approximately 1.33 tokens per word, or 2 tokens per line as rough estimate.

## Token Budget Tiers

### Micro (<500 tokens)

**TokenBudget Range:** `~150` to `~400`
**ContextTier:** Critical or High
**Use Cases:**
- Core patterns loaded in every session
- Security constraints
- Basic CRUD operations
- Always-loaded foundation rules

**Examples:**
- `000-global-core.md` (~450 tokens)
- `005-security-core.md` (~300 tokens)

**Loading:** Always loaded at session start

### Standard (500-1500 tokens)

**TokenBudget Range:** `~500` to `~1200`
**ContextTier:** High or Medium
**Use Cases:**
- Technology-specific patterns
- Framework basics
- Language foundations
- Common workflows

**Examples:**
- `100-snowflake-core.md` (~800 tokens)
- `200-python-core.md` (~1000 tokens)
- `101-snowflake-streamlit-core.md` (~950 tokens)

**Loading:** Loaded based on task domain (Python tasks → load 200-python-core)

### Comprehensive (1500-3000 tokens)

**TokenBudget Range:** `~1500` to `~2500`
**ContextTier:** Medium or Low
**Use Cases:**
- Complex multi-step workflows
- Advanced optimization techniques
- Comprehensive guides
- Multi-section documentation

**Examples:**
- `002-rule-governance.md` (~1800 tokens)
- `115-model-registry.md` (~2200 tokens)
- `002a-rule-creation-guide.md` (~2900 tokens)

**Loading:** Loaded when specifically needed for complex tasks

### Reference (3000-5000 tokens)

**TokenBudget Range:** `~3000` to `~4500`
**ContextTier:** Low
**Use Cases:**
- Exhaustive guides
- Complete framework documentation
- Reference documentation (loaded rarely)

**Examples:**
- `002c-advanced-rule-patterns.md` (~4000 tokens)
- Full API reference rules

**Loading:** Loaded only when explicitly requested or for reference

### Mega (>5000 tokens) - AVOID

**TokenBudget Range:** `>5000`
**Status:** [FAIL] **SHOULD BE SPLIT**
**Problem:** Rules >5000 tokens degrade performance across all models and waste context budget

**Solution:** Split into multiple focused files (see 002-rule-governance.md split example: 9,000 tokens → 5 files of ~1,500 tokens each)

## Model-Specific Optimization

### GPT-4 / GPT-4o (128K context)

**Optimal Rule Size:** <3000 tokens per rule
**Context Budget:** Load 15-25 rules (~20K-30K tokens total)
**Performance:** Degrades with rules >3000 tokens
**Strategy:** Prioritize micro and standard rules; avoid reference tier

### Claude 4 Sonnet+ (200K context)

**Optimal Rule Size:** <5000 tokens per rule (handles larger files well)
**Context Budget:** Load 25-40 rules (~30K-50K tokens total)
**Performance:** Excellent with comprehensive rules
**Strategy:** Can handle larger rule sets; use prompt caching for repeated rules

### Gemini 2.0 Flash (1M+ context)

**Optimal Rule Size:** <5000 tokens per rule
**Context Budget:** Load 50-150+ rules (~50K-150K tokens total)
**Performance:** Minimal constraints on rule loading
**Strategy:** Can load entire rule families; batch loading highly effective

## Progressive Loading Strategy

### Critical Rules (Always Load)

Load at every session start:
- `000-global-core.md` (~450 tokens) - Foundation
- Domain core rule based on task:
  - Python tasks: `200-python-core.md` (~1000 tokens)
  - Snowflake tasks: `100-snowflake-core.md` (~800 tokens)
  - Streamlit tasks: `101-snowflake-streamlit-core.md` (~950 tokens)

**Total:** ~1,500-2,000 tokens baseline

### Standard Context (Most Tasks)

Foundation + Domain Core + 2-4 specialized rules:

**Example - Python Testing Task:**
- `000-global-core.md` (~450)
- `200-python-core.md` (~1000)
- `206-python-pytest.md` (~850)
- `201-python-lint-format.md` (~750)

**Total:** ~3,050 tokens

### Extended Context (Complex Tasks)

Foundation + Domain Core + 5-10 specialized rules:

**Example - Streamlit Dashboard with Snowflake:**
- `000-global-core.md` (~450)
- `100-snowflake-core.md` (~800)
- `101-snowflake-streamlit-core.md` (~950)
- `321-streamlit-widgets.md` (~1100)
- `322-streamlit-layout.md` (~900)
- `110-cortex-agent.md` (~1200)

**Total:** ~5,400 tokens

### Maximum Context (Comprehensive Projects)

Foundation + Multiple Domain Cores + Full rule families:

**Example - Multi-Domain Project:**
- `000-global-core.md` (~450)
- Python family (200-209): ~5,000 tokens
- Snowflake family (100-124): ~8,000 tokens
- Streamlit family (320-329): ~6,000 tokens

**Total:** ~19,450 tokens

**Note:** Only for comprehensive implementations; most tasks need <10K tokens

## Loading Pattern Examples

### Pattern 1: Incremental Loading

```markdown
# Session start
1. Load: 000-global-core (~450 tokens)
2. Identify task domain from keywords
3. Load: Domain core rule (~1000 tokens)
4. Analyze task complexity
5. Load: 2-3 most relevant specialized rules (~2000-3000 tokens)
6. Execute task
7. If errors/blockers: Load additional specialized rules as needed

Total context: ~3,500-5,500 tokens (efficient)
```

### Pattern 2: Batch Loading (Complex Task)

```markdown
# Complex multi-domain task
1. Load: 000-global-core (~450 tokens)
2. Batch load domain cores:
   - 100-snowflake-sql (~800)
   - 200-python-core (~1000)
   - 320-streamlit-core (~950)
3. Batch load specialized rules (5-8 rules): ~5000-8000 tokens
4. Execute with full context

Total context: ~8,200-11,200 tokens (comprehensive)
```

### Pattern 3: Reference Loading (Rare)

```markdown
# When documentation needed
1. Load: Standard context (~3500 tokens)
2. Load: Reference rule on-demand (~4000 tokens)
3. Extract needed information
4. Unload reference rule (optional)

Total context: ~7,500 tokens (temporary spike)
```

## Token Budget Validation

### Running token_validator.py

```bash
# Validate single file
python3 scripts/token_validator.py --directory rules/ --detailed

# Check specific rule
python3 scripts/token_validator.py --directory rules/ --detailed | grep "002-rule-governance"

# Output example:
# rules/002-rule-governance.md:
#   Declared: ~1500
#   Actual: 1840
#   Variance: +22.67% (within tolerance)
```

### Token Count Estimation

**Quick Estimate:**
```bash
# Word count
wc -w rules/NNN-rule.md
# 1381 words

# Convert to tokens (multiply by ~1.33)
# 1381 × 1.33 ≈ 1,837 tokens

# Round to nearest 50-100
# TokenBudget: ~1800 or ~1850
```

### Variance Tolerance

**Acceptable:** ±10% variance between declared and actual
**Warning:** >10% variance triggers review
**Critical:** >20% variance requires TokenBudget update

**Example:**
- Declared: `~1500`
- Actual: `1650` (10% over)
- Status: [PASS] Acceptable

- Declared: `~1500`
- Actual: `1900` (26.67% over)
- Status: [FAIL] Update to `~1900`

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
**TokenBudget:** ~450
**TokenBudget:** ~1200
**TokenBudget:** ~2500
```
**Benefits:** Parseable, enables progressive loading decisions, accurate context budget tracking.

---

**Anti-Pattern 2: Loading All Rules at Start**

**Problem:** Loading all 100+ rules at session start (>200K tokens)
- Wastes context budget
- Increases latency
- Reduces performance
- Unnecessary for most tasks

**Correct Pattern:** Progressive loading (~10K-30K tokens)
```python
# Load only what's needed
foundation_rules = load_rules(['000-global-core.md'])
domain_rules = load_rules(['200-python-core.md'])  # Based on task
specialized_rules = load_rules(['206-python-pytest.md', '201-python-lint-format.md'])  # As needed
```
**Benefits:** Efficient, focused, fast - uses 10-15% of context budget instead of 100%.

## Post-Execution Checklist

- [ ] TokenBudget declared with `~NUMBER` format (no text labels)
- [ ] ContextTier matches TokenBudget tier appropriately
- [ ] Rule size <3000 tokens (optimal) or <5000 tokens (maximum)
- [ ] token_validator.py confirms budget within ±10% of actual
- [ ] Rule focuses on single concept (not multi-topic)
- [ ] Dependencies declared to avoid loading duplicate content
- [ ] Rule added to appropriate tier for progressive loading
- [ ] If >5000 tokens, plan created to split into multiple focused files

## Validation

**Success Checks:**
- TokenBudget format: `~NUMBER` (e.g., ~1200)
- ContextTier matches tier: Micro→Critical/High, Standard→High/Medium, etc.
- Actual token count within ±10% of declared budget
- Rule size <3000 tokens (preferred) or <5000 tokens (maximum)
- token_validator.py passes without critical warnings

**Negative Tests:**
- Text label TokenBudget (small/medium/large) triggers validation error
- Missing tilde prefix triggers format error
- Token variance >20% triggers update warning
- Rule >5000 tokens triggers split recommendation

## Output Format Examples

### Example 1: Standard Rule Token Budget

```markdown
# 321-streamlit-validation

## Metadata

**SchemaVersion:** v3.0
**Keywords:** Streamlit, validation, forms, widgets, error handling
**TokenBudget:** ~850
**ContextTier:** Medium
**Depends:** rules/101-snowflake-streamlit-core.md

# [Rule content - ~850 tokens total]
```

### Example 2: Comprehensive Rule Token Budget

```markdown
# 002a-rule-creation-guide

**SchemaVersion:** v3.0
**Keywords:** rule creation, workflow, step-by-step guide, naming conventions
**TokenBudget:** ~2900
**ContextTier:** High
**Depends:** rules/002-rule-governance.md

# [Rule content - ~2900 tokens total]
```

## References

### Related Rules
- **Rule Governance**: `rules/002-rule-governance.md` - v3.0 schema requirements
- **Creation Guide**: `rules/002a-rule-creation-guide.md` - Step-by-step rule creation workflow
- **Advanced Patterns**: `rules/002c-advanced-rule-patterns.md` - System prompt altitude, multi-session workflows
- **Validator Usage**: `rules/002d-schema-validator-usage.md` - Token validation commands

### Tools
- **token_validator.py**: Validates token budgets against actual counts
- **schema_validator.py**: Validates v3.0 schema compliance

### External Documentation
- **Schema Definition**: `schemas/rule-schema-v3.yml` - Token budget validation rules
