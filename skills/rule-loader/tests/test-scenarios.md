# Rule Loader Test Scenarios

## Scenario 1: Simple Python File

**Input:** `user_request: "Fix the bug in auth.py"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
```

**Notes:** No activity keywords beyond the verb "fix" which has no specific activity rule.

---

## Scenario 2: Keyword with Dependency

**Input:** `user_request: "Write tests for my Streamlit dashboard"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
```

**Notes:** `100-snowflake-core.md` loaded as dependency of `101`, not from direct match.

---

## Scenario 3: No Extensions, No Keywords

**Input:** `user_request: "What is the project structure?"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
```

**Notes:** No file extensions, no technology keywords. Foundation only.

---

## Scenario 4: Directory-Based Rule

**Input:** `user_request: "Update the rule in rules/200-python-core.md"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/002-rule-governance.md (directory: rules/)
- rules/200-python-core.md (file extension: .py)
```

**Notes:** Mentioning `rules/` directory triggers `002-rule-governance.md`.

---

## Scenario 5: Skills Directory

**Input:** `user_request: "Create a new skill in skills/my-new-skill/"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/002h-claude-code-skills.md (directory: skills/)
```

**Notes:** Mentioning `skills/` directory triggers `002h-claude-code-skills.md`.

---

## Scenario 6: High-Risk Action (git)

**Input:** `user_request: "Commit these changes and push"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/803-project-git-workflow.md (keyword: git/commit)
```

**Notes:** `commit` and `push` are high-risk actions triggering mandatory search for git rules.

---

## Scenario 7: Multiple Extensions

**Input:** `user_request: "Create a Python script that runs this SQL query from data.sql"`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 102)
- rules/102-snowflake-sql-core.md (file extension: .sql)
```

**Notes:** Both `.py` and `.sql` extensions detected. `100` loaded as dependency of `102`.

---

## Scenario 8: Token Budget Deferral

**Input:** `user_request: "Write tests for my Streamlit dashboard with full docstrings"`
**Config:** `token_budget_limit: 14000`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
- [Deferred: 204-python-docs.md - Low tier, budget exceeded at ~14,000]
```

**Notes:** With a lower budget limit, the Low-tier docs/comments rule is deferred. The Medium-tier test rule is kept because it directly matches the primary verb.

---

## Scenario 9: Missing Rule File (Partial Load)

**Input:** `user_request: "Lint the TypeScript code"`
**Condition:** `430-typescript-core.md` does not exist on disk

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/201-python-lint-format.md (keyword: lint)
```

**Expected Gate 3:** PASSED (partial success, lint rule loaded)
**Expected warning:** "Rule load failed: 430-typescript-core.md not found"

**Notes:** Gate 3 passes because at least one rule loaded. The missing rule is noted but does not block execution.

---

## Scenario 10: Foundation Failure

**Input:** `user_request: "Any request"`
**Condition:** `000-global-core.md` does not exist on disk

**Expected output:**
```
CRITICAL ERROR: Cannot proceed - rules/000-global-core.md not accessible
```

**Notes:** No rules loaded, no further phases executed. Complete stop.

---

## Scenario 11: Multi-Technology Keyword Splitting

**Input:** `user_request: "FastAPI + HTMX + SSE in SPCS"`

**Expected grep pattern:** `grep -iE "fastapi|htmx|sse|spcs" rules/RULES_INDEX.md`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (implied .py from keyword: FastAPI)
- rules/210-python-fastapi-core.md (keyword: fastapi)
```

**Notes:** All 4 keywords must appear in the grep OR pattern. HTMX/SSE/SPCS may not match any rules in RULES_INDEX.md — note "No rules found for [keyword]" for each unmatched term.

---

## Scenario 12: Grep Zero-Result Anomaly Recovery

**Input:** `user_request: "Deploy the Python application"`
**Condition:** grep returns empty (simulated anomaly)

**Expected behavior:**
1. Re-execute grep once (transient failure recovery)
2. If still zero: Execute `read_file` fallback immediately
3. Document anomaly: "Grep returned unexpectedly empty - used fallback"

**Expected rules (after fallback):**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/820-taskfile-automation.md (keyword: deploy)
```

**Notes:** "deploy" and "python" are common keywords that should always return matches. Zero results is an anomaly requiring retry then fallback.

---

## Scenario 13: context_tier_filter Parameter

**Input:** `user_request: "Write tests for my Streamlit dashboard"`
**Config:** `context_tier_filter: critical+high`

**Expected rules:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
```

**Notes:** `206-python-pytest.md` (Medium tier) excluded by the `critical+high` filter despite matching the "test" keyword.

---

## Scenario 14: Custom rules_path

**Input:** `user_request: "Fix the bug in auth.py"`
**Config:** `rules_path: custom-rules/`

**Expected rules:**
```markdown
## Rules Loaded
- custom-rules/000-global-core.md (foundation)
- custom-rules/200-python-core.md (file extension: .py)
```

**Notes:** All paths use `custom-rules/` prefix instead of default `rules/`. Foundation loading, domain matching, and activity matching all use the custom path.

---

## Scenario 15: Circular Dependency Detection

**Condition:** Rule A depends on Rule B, Rule B depends on Rule A

**Expected behavior:**
1. Warning logged: "Circular dependency detected between A and B"
2. Cycle broken: both rules loaded once
3. No infinite loop

**Notes:** Circular dependencies should not exist in well-formed rules but must be handled gracefully if encountered.

---

## Scenario 16: Transitive Dependency Failure

**Condition:** Rule A depends on B, B depends on C, C not found

**Expected behavior:**
1. Log: "Rule load failed: C not found"
2. Log: "Skipping B - dependency C missing"
3. Log: "Skipping A - dependency B missing"

**Expected Gate 3:** PASSED if other non-dependent rules loaded successfully

**Notes:** Transitive failures cascade. If A-B-C is the only chain, Gate 3 still passes if the foundation and other matched rules loaded.
