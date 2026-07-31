# Using the Rule Loader Skill

**Last Updated:** 2026-07-27

The Rule Loader Skill determines which rule files to load for any user request by analyzing file extensions, directory paths, and keywords against the YAML frontmatter of the rules in `rules/`. It ensures consistent, dependency-aware rule discovery across all agents and sessions.

## Examples

### Minimal Required Example

```text
Use the rule-loader skill.

user_request: "Fix this Python bug"  # Required — the request to analyze
```

### With All Optional Settings

```text
Use the rule-loader skill.

user_request: "Build a Streamlit dashboard with Snowflake backend and pytest tests"  # Required
token_budget_limit: 10000            # Optional (default: standard) — max tokens for loaded rules
context_tier_filter: critical+high   # Optional (default: all) — pre-filter by tier
rules_path: custom-rules/            # Optional (default: rules/) — alternate rules directory
```

### Minimal Mode (Constrained Context)

```text
Use the rule-loader skill.

user_request: "Fix this Python bug"  # Required
token_budget_limit: 5000             # Optional — limits to foundation + domain only
```

### Complete Mode (Multi-Domain)

```text
Use the rule-loader skill.

user_request: "Build a Streamlit dashboard with Snowflake backend and pytest tests"  # Required
context_tier_filter: all             # Optional (default: all) — includes all tiers
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

The skill produces a manifest that the agent uses internally. When diagnostic output is requested (via `$show-rules` or during eval testing), the agent renders the manifest as a PRE-FLIGHT block — Gate 1 carries the foundation citation, Gate 3 lists all selected domain/activity rules with loading reasons:

```markdown
PRE-FLIGHT:
- [x] Gate 1: Foundation rules/000-global-core.md — N lines
- [x] Gate 2: Searched: python, streamlit, test
- [x] Gate 3: +4 domain rules:
  - rules/200-python-core.md (file extension: .py) — N lines
  - rules/100-snowflake-core.md (dependency of 101) — N lines
  - rules/101-snowflake-streamlit-core.md (keyword: Streamlit) — N lines
  - rules/206-python-pytest.md (keyword: test) — N lines
  - [Deferred: 204-python-docs.md - Low tier, not required for task]

Task Switch: FIRST
```

> **Note:** PRE-FLIGHT output is not emitted by default. It appears only when explicitly requested or during eval runs.

### Loading Reasons

| Reason | Meaning |
|--------|---------|
| `(foundation)` | Foundation rule (000-global-core.md) — cited on Gate 1, not as a Gate 3 row |
| `(file extension: .py)` | Matched from file extension in request |
| `(directory: skills/)` | Matched from directory path in request |
| `(keyword: test)` | Matched keyword in a rule's frontmatter |
| `(dependency of NNN)` | Loaded as prerequisite for another rule |
| `[Deferred: ...]` | Skipped due to token budget constraints |

### Workflow Phases

The skill executes 5 phases in order:

| Phase | Name | What Happens |
|-------|------|--------------|
| 1 | **Foundation Loading** | Always loads `000-global-core.md` (~2,400 tokens) |
| 2 | **Domain Matching** | Matches file extensions and directories to domain rules |
| 3 | **Activity Matching** | Scores rule frontmatter keywords against the prompt |
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

### What is the relationship to the plugin hook?

The plugin's `UserPromptSubmit` hook runs the same matching algorithm automatically on every prompt and injects the result. This skill provides detailed workflow files for each loading phase, worked examples showing the complete selection process, and test scenarios for validating rule-loading behavior.

### Why was my expected rule not loaded?

Check these causes in order:

1. **No keyword match:** No rule declares that keyword in its frontmatter
2. **No extension match:** Use `grep -rl "<ext>" rules/` to find the authoritative rule for that extension
3. **Dependency missing:** A missing prerequisite skips the dependent rule
4. **Deferred for budget:** Check if it was listed in the Deferred section

### What happens if the `rules/` directory is not found?

The skill falls back to the injected foundation only. Confirm the plugin is installed and active with `cortex plugin list`.

### What if a rule file is not found?

- **Only matched rule:** Report with options: (A) correct path, (B) proceed without, (C) cancel
- **Other rules loaded:** Note the failure, continue with remaining rules

### How are token budgets calculated?

Each rule declares a `TokenBudget` value in its metadata (e.g., `~3,500`). The skill sums these values. Agent self-regulates; there is no external enforcement.

### Token budget exceeded - what should I do?

1. Low-tier rules are deferred automatically
2. Check which rules are Critical vs Low tier in their frontmatter `context_tier`
3. Consider using `context_tier_filter: critical+high` to pre-filter

## Reference

### Architecture

```text
User Request
│
├── Phase 1: Foundation Loading
│   └── Load 000-global-core.md (always, ~2,400 tokens)
│
├── Phase 2: Domain Matching
│   ├── Check directory paths (skills/, rules/)
│   └── Match file extensions (.py, .sql, .ts, etc.)
│
├── Phase 3: Activity Matching
│   └── Score rule frontmatter keywords
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
- **Discovery path:** the `UserPromptSubmit` hook, or the `rule-loader` skill invoked directly
