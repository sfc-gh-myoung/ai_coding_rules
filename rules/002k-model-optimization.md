# Model-Specific Rule Optimization

> **REFERENCE RULE: LOAD WHEN NEEDED**
>
> Model-specific context windows, loading budgets, and optimization strategies.
> Load when sizing rules for specific AI models or planning loading budgets.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**Keywords:** model optimization, context window, loading budget, GPT, Claude, Gemini, token limits, cost efficiency, prompt caching
**TokenBudget:** ~2550
**ContextTier:** Low
**Depends:** 002c-rule-optimization.md

## Scope

**What This Rule Covers:**
Model-specific context windows, loading budget formulas, and optimization strategies for OpenAI, Anthropic, and Google models. Includes pricing and output limits where relevant.

**When to Load This Rule:**
- Sizing rules for a specific AI model
- Planning loading budgets for different context windows
- Comparing model capabilities for rule loading
- Optimizing cost efficiency across models

## References

### Dependencies

**Must Load First:**
- **002c-rule-optimization.md** - Token budget tiers, progressive loading, and sizing guidelines

## Contract

### Inputs and Prerequisites

- Target AI model name and version
- Rule set to optimize for loading

### Mandatory

- Verify model context window from official provider documentation
- Calculate loading budget as 30-40% of context window
- Apply model-specific strategies (e.g., prompt caching for Anthropic)

### Forbidden

- Loading >40% of context window with rules
- Using outdated model specifications without verifying against current docs
- Ignoring model-specific output token limits when planning rule responses

### Execution Steps

1. Identify target model and its context window
2. Calculate loading budget (30-40% of context window)
3. Select rules that fit within the loading budget
4. Apply model-specific strategies (e.g., prompt caching for Anthropic)

### Output Format

Model optimization recommendation with:
- Target model and context window size
- Calculated loading budget (token count)
- Recommended rule selection fitting the budget
- Model-specific strategy notes

### Validation

**Success Criteria:**
- Loading budget does not exceed 40% of model context window
- Rule selection fits within calculated budget
- Model-specific strategies applied where applicable

### Error Recovery

- **Unknown model:** Use default 30% loading budget with 200K context assumption
- **Budget exceeded mid-conversation:** Stop loading additional rules, summarize context, proceed with loaded rules only
- **Model unavailable:** Fall back to nearest equivalent model in the same provider's lineup

### Post-Execution Checklist

- [ ] Model context window verified against current provider documentation
- [ ] Loading budget calculated as 30-40% of context window
- [ ] Rule selection fits within loading budget
- [ ] Model-specific strategies applied (prompt caching, reasoning effort, etc.)

## Loading Budget Formula

**Context Window is not Loading Budget**

Agents should follow this formula:

```
Loading Budget = 30-40% of context window
```

Context Budget Allocation (approximate):
- Rules loading: ~15% of context window
- Conversation history: ~30% of context window
- Output reserve: ~20% of context window
- **Available for task input: ~35% of context window**

Note: These are guidelines, not hard limits. Actual allocation depends on conversation
length, number of loaded rules, and task complexity. The ~35% available for task input
is the starting budget; as conversation grows, this shrinks.

**Model Context Windows (30-40% loading budget):**
- **GPT-4o:** 128K context, 38K-51K tokens for rules
- **GPT-5.1:** 400K context, 120K-160K tokens for rules
- **Claude Sonnet 4.5:** 200K context, 60K-80K tokens for rules
- **Gemini 3 Pro:** 1M context, 300K-400K tokens for rules

**Rule of Thumb:** If you're loading >40% of context window with rules, you're likely over-loading.

## OpenAI Models

> **Staleness Warning:** Model specifications change frequently. Before using these specs, verify against the provider's current documentation using the source links provided. Last verified: 2026-03-08.

### GPT-4o (128K context)

**Optimal Rule Size:** 2000-3500 tokens per rule
**Context Budget:** Load 10-20 rules (~25K-40K tokens total)
**Performance:** Best with focused, standard-sized rules
**Strategy:** Prioritize small and standard tiers; defer reference tier
**Avoid For:** Large rule sets, comprehensive project contexts

*Source: [platform.openai.com/docs/models/gpt-4o](https://platform.openai.com/docs/models/gpt-4o)*

### GPT-5.1 (400K context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 30-80 rules (~60K-150K tokens total)
**Max Output:** 128K tokens
**Performance:** Excellent with comprehensive rule sets
**Strategy:** Can load entire rule families; leverage configurable reasoning effort for complex tasks
**Avoid For:** Cost-sensitive tasks where cheaper models suffice
**Pricing:** $1.25/M input, $10.00/M output

*Source: [platform.openai.com/docs/models/gpt-5.1](https://platform.openai.com/docs/models/gpt-5.1)*

## Anthropic Models

### Claude Sonnet 4 / Opus 4 (200K context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 15-30 rules (~40K-70K tokens total)
**Performance:** Excellent with comprehensive rules
**Strategy:** Can handle larger rule sets; use prompt caching for repeated rules (Anthropic: set `anthropic-beta: prompt-caching-2024-07-31` header; see Anthropic caching docs for details)
**Avoid For:** Tasks requiring >64K output tokens

*Source: [docs.claude.com/claude/docs/models-overview](https://docs.claude.com/claude/docs/models-overview)*

### Claude Sonnet 4.5 (200K standard / 1M beta)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 15-40 rules (~40K-80K tokens standard); 100+ rules with 1M beta
**Budget Breakdown:** 200K context - 15% rules (~30K) - 30% conversation context (~60K)
  - 20% output reserve (~40K) = ~70-80K available for task input
**Max Output:** 64K tokens
**Performance:** Excels in coding, finance, cybersecurity tasks
**Strategy:** Use prompt caching (90% cost reduction on cache hits); leverage extended context for comprehensive projects
**Avoid For:** Budget-constrained projects (higher per-token cost than Sonnet 4)
**Pricing:** $3/M input, $15/M output (standard); $6/M input, $22.50/M output (>200K)

*Source: [docs.claude.com/claude/docs/models-overview](https://docs.claude.com/claude/docs/models-overview)*

### Claude Opus 4.5 (200K context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 15-30 rules (~40K-70K tokens total)
**Max Output:** 32K tokens
**Performance:** High-level reasoning and deep analysis; best for complex technical tasks
**Strategy:** Reserve for tasks requiring sophisticated reasoning; use Sonnet 4.5 for routine tasks
**Avoid For:** Routine tasks, high-volume processing (use Sonnet 4 or Haiku instead)
**Pricing:** $15/M input, $75/M output

*Source: [docs.claude.com/claude/docs/models-overview](https://docs.claude.com/claude/docs/models-overview)*

### Prompt Caching Fallback

If prompt caching is unavailable (API does not support it, or cache was evicted):

1. **Reduce rule loading:** Load only Critical and High tier rules (skip Medium/Low)
2. **Compress conversation history:** Summarize earlier exchanges instead of passing full history
3. **Front-load critical context:** Place the most important information in the first 20% of the context
4. **Monitor token usage:** If approaching 80% of context window, proactively summarize

This fallback reduces quality slightly but prevents context overflow.

## Google Models

### Gemini 2.5 Pro (1M context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 30-100+ rules (~60K-200K tokens total)
**Performance:** Minimal constraints on rule loading
**Strategy:** Can load entire rule families; batch loading highly effective
**Avoid For:** Tasks requiring precise output formatting (less structured than GPT/Claude)

*Source: [ai.google.dev/gemini-api/docs/models#gemini-2.5-pro](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-pro)*

### Gemini 3 Pro (1M context)

**Optimal Rule Size:** 2000-5000 tokens per rule
**Context Budget:** Load 30-100+ rules (~60K-200K tokens total)
**Performance:** Best-in-class reasoning, multimodality, and coding; tops WebDev Arena (1487 Elo)
**Strategy:** Excellent for agentic coding and long-horizon planning; use Deep Think mode for problems requiring >3 reasoning steps or >5000 tokens of analysis
**Key Features:** Zero-shot generation, advanced tool use, improved multi-step workflow execution
**Avoid For:** Cost-sensitive simple tasks (use Gemini Flash for quick lookups)

*Source: [blog.google/products/gemini/gemini-3](https://blog.google/products/gemini/gemini-3/)*

## Open-Source Models

For open-source models (Llama, Mistral, DeepSeek, etc.): Apply the same 30-40% loading budget formula using the model's documented context window. Verify output token limits as these vary significantly by deployment configuration and quantization level. When context window is unknown, default to 30% of 128K (38K tokens).

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Loading Rules Without Considering Model Context

**Problem:** Loading the same number of rules regardless of model context window size.

```python
# WRONG: Same rule loading for all models
rules = load_all_rules()  # 100+ rules for 8K context model
```

**Correct Pattern:**
```python
# CORRECT: Adjust rule loading to model capacity
if model.context_size < 32000:
    rules = load_essential_rules(limit=5)
elif model.context_size < 128000:
    rules = load_priority_rules(limit=20)
else:
    rules = load_all_rules()
```

### Anti-Pattern 2: Ignoring Token Budget for Output

**Problem:** Using full context for input without reserving tokens for model output.

```python
# WRONG: Fill context completely
context = build_context(max_tokens=model.context_size)
```

**Correct Pattern:**
```python
# CORRECT: Reserve 25-30% for output
input_budget = int(model.context_size * 0.7)
context = build_context(max_tokens=input_budget)
```

### Pre-Task-Completion Checks

Before reporting work as complete, verify:

1. **Output matches request:** Re-read the original request and compare against output
2. **Model-appropriate quality:** For complex tasks (Opus), verify depth of analysis;
   for speed tasks (Haiku), verify key points are covered
3. **Context coherence:** Ensure response doesn't contradict earlier statements in conversation
4. **Token efficiency:** Verify response isn't unnecessarily verbose for the model tier
