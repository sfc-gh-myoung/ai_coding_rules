# Using the Rule Loader Skill

**Last Updated:** 2026-03-25

The Rule Loader Skill determines which rule files to load for any user request by analyzing file extensions, directory paths, and keywords against RULES_INDEX.md. It ensures consistent, dependency-aware rule discovery across all agents and sessions, formalizing the rule-loading algorithm from AGENTS.md (Steps 1-3) into a reusable skill with progressive disclosure.


## Quick Start

### 1. Load the skill

```text
Load skills/rule-loader/SKILL.md
```

### 2. Request rule loading

```text
Use the rule-loader skill.

user_request: "Write tests for my Streamlit dashboard"
```

The skill analyzes the request and selects appropriate rules.

### 3. Check the output

On success:

```text
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
```


## Loading Modes

The skill supports different loading configurations based on context constraints.

| Mode | Token Range | When to Use |
|------|-------------|-------------|
| **Minimal** | ~3,000-5,000 | Constrained contexts, quick responses |
| **Standard** | ~8,000-12,000 | Most requests (default) |
| **Complete** | ~15,000-20,000 | Complex multi-domain tasks |

### Minimal Mode

Foundation + domain rules only. Use for simple, single-domain requests.

```text
user_request: "Fix this Python bug"
token_budget_limit: 5000
```

### Standard Mode (Default)

Foundation + domain + 1-2 activity rules. Handles most requests effectively.

```text
user_request: "Add logging to this function"
```

### Complete Mode

All matched rules including specialized rules. Use for complex cross-domain work.

```text
user_request: "Build a Streamlit dashboard with Snowflake backend and pytest tests"
context_tier_filter: all
```


## Understanding Your Results

### Output Format

The skill produces a `## Rules Loaded` section listing all selected rules with loading reasons:

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
- [Deferred: 204-python-docs-comments.md - Low tier, not required for task]
```

### Loading Reasons

| Reason | Meaning |
|--------|---------|
| `(foundation)` | Always-loaded base rule (000-global-core.md) |
| `(file extension: .py)` | Matched from file extension in request |
| `(directory: skills/)` | Matched from directory path in request |
| `(keyword: test)` | Matched keyword in RULES_INDEX.md |
| `(dependency of NNN)` | Loaded as prerequisite for another rule |
| `[Deferred: ...]` | Skipped due to token budget constraints |

### Workflow Phases

The skill executes 5 phases in order:

| Phase | Name | What Happens |
|-------|------|--------------|
| 1 | **Foundation Loading** | Always loads `000-global-core.md` (~4,050 tokens) |
| 2 | **Domain Matching** | Matches file extensions and directories to domain rules |
| 3 | **Activity Matching** | Searches RULES_INDEX.md for keyword matches |
| 4 | **Dependency Resolution** | Loads prerequisites before dependent rules |
| 5 | **Token Budget Management** | Defers low-priority rules if over budget |

### Deferral Priority

When over the token budget, rules are deferred in this order:

1. **Low tier** rules first (all of them)
2. **Medium tier** rules not directly related to task keywords
3. **High tier** rules only if critically over budget
4. **Critical tier** rules are never deferred


## Advanced Usage

### Custom Token Budget

```text
user_request: "Add a FastAPI endpoint"
token_budget_limit: 10000
```

Limits total loaded rules to 10,000 tokens. Useful for constrained contexts or targeted responses.

**Token thresholds:**
- ≤15,000: Load all matched rules
- 15,001-20,000: Warning, evaluate Low-tier deferrals
- >20,000: Mandatory deferral by priority

### Context Tier Filtering

```text
context_tier_filter: critical+high
```

Pre-filters to only consider rules at specified tiers.

| Filter | What's Included |
|--------|-----------------|
| `all` (default) | All tiers |
| `critical` | Critical only |
| `critical+high` | Critical and High |
| `critical+high+medium` | Excludes Low tier |

### Custom Rules Path

```text
rules_path: custom-rules/
```

Uses an alternate rules directory instead of the default `rules/`.


## FAQ

### What is the relationship to AGENTS.md?

AGENTS.md contains the bootstrap protocol that invokes rule-loading logic inline (Steps 1-3). This skill provides detailed workflow files for each loading phase, worked examples showing the complete selection process, and test scenarios for validating rule-loading behavior. AGENTS.md remains self-contained; this skill offers enriched reference material.

### Why was my expected rule not loaded?

Check these causes in order:

1. **No keyword match:** The keyword may not exist in RULES_INDEX.md
2. **No extension match:** Verify the extension mapping in RULES_INDEX.md Section 2
3. **Dependency missing:** A missing prerequisite skips the dependent rule
4. **Deferred for budget:** Check if it was listed in the Deferred section

### What happens if RULES_INDEX.md is not found?

The skill falls back to foundation + file-extension matching only. Keyword-based activity matching is skipped. Regenerate the index with `task index:generate`.

### What if a rule file is not found?

- **Only matched rule:** Report with options: (A) correct path, (B) proceed without, (C) cancel
- **Other rules loaded:** Note the failure, continue with remaining rules

### How are token budgets calculated?

Each rule declares a `TokenBudget` value in its metadata (e.g., `~3,500`). The skill sums these values. Agent self-regulates; there is no external enforcement.

### Token budget exceeded - what should I do?

1. Low-tier rules are deferred automatically
2. Check which rules are Critical vs Low tier in RULES_INDEX.md metadata
3. Consider using `context_tier_filter: critical+high` to pre-filter


## Reference

### Architecture

```text
User Request
│
├── Phase 1: Foundation Loading
│   └── Load 000-global-core.md (always, ~4,050 tokens)
│
├── Phase 2: Domain Matching
│   ├── Check directory paths (skills/, rules/)
│   └── Match file extensions (.py, .sql, .ts, etc.)
│
├── Phase 3: Activity Matching
│   └── Search RULES_INDEX.md for keywords
│
├── Phase 4: Dependency Resolution
│   └── Load prerequisites before dependents
│
└── Phase 5: Token Budget Management
    ├── Sum TokenBudget values
    └── Defer Low/Medium tier if over budget
```

### File Structure

```text
skills/rule-loader/
├── SKILL.md                        # Main entrypoint (~120 lines)
├── workflows/
│   ├── foundation-loading.md       # Phase 1: Always-load foundation
│   ├── domain-matching.md          # Phase 2: File ext & directory matching
│   ├── activity-matching.md        # Phase 3: Keyword-based discovery
│   ├── dependency-resolution.md    # Phase 4: Load prerequisites
│   └── token-budget.md             # Phase 5: Budget management & deferral
├── examples/
│   ├── streamlit-dashboard.md      # Cross-domain: Streamlit + Python + test
│   ├── python-api.md               # Python + FastAPI endpoint
│   └── multi-domain.md             # Snowflake SQL + Python
└── tests/
    └── test-scenarios.md           # Input/output test cases (16 scenarios)
```

### Extension Reference

| Extension(s) | Rule |
|-------------|------|
| `.sql` | `102-snowflake-sql-core.md` |
| `.py`, `.pyi` | `200-python-core.md` |
| `.toml`, `.yaml`, `.yml` | `202-markup-config-validation.md` |
| `pyproject.toml` | `203-python-project-setup.md` |
| `.bash`, `.sh` | `300-bash-scripting-core.md` |
| `.zsh` | `310b-zsh-compatibility.md` |
| `Dockerfile`, `docker-compose.yaml` | `350-docker-core.md` |
| `.js`, `.cjs`, `.mjs` | `420-javascript-core.md` |
| `.ts` | `430-typescript-core.md` |
| `.jsx`, `.tsx` | `440-react-core.md` |
| `.go`, `go.mod` | `600-golang-core.md` |

### Integration with Other Skills

| Skill | Relationship |
|-------|--------------|
| **rule-creator** | Creates rules that rule-loader discovers |
| **rule-reviewer** | Validates rules for agent executability |
| **bulk-rule-reviewer** | Reviews all rules in the rules/ directory |

### Support

- **Skill entrypoint:** `skills/rule-loader/SKILL.md`
- **Workflow guides:** `skills/rule-loader/workflows/*.md`
- **Examples:** `skills/rule-loader/examples/*.md`
- **RULES_INDEX.md:** Authoritative source for rule discovery mappings
- **AGENTS.md:** Bootstrap protocol that invokes rule-loading (Steps 1-3)
