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
- [Deferred: 204-python-docs-comments.md - Low tier, budget exceeded at ~14,000]
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
