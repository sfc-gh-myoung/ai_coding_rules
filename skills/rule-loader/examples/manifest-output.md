# Example: rule-loader discovery manifest (`rule-loader-matcher/v1`)

This is the authoritative return value of `match_rules.py` when it runs as the
discovery stage. It is **metadata only**: rule file *bodies* never appear in
the manifest. The main agent reads each `load_sequence[*].rule_path` itself via
`read_file` (preserving the Gate 3 read-and-apply contract).

## Minimal valid manifest: "Fix the bug in auth.py"

```json
{
  "schema_version": "rule-loader-matcher/v1",
  "candidate_rules": [
    {
      "rule_path": "rules/200-python-core.md",
      "layer": "SOFT",
      "context_tier": "High",
      "description": "Python core: toolchain detection, datetime UTC, and mandatory validation gate.",
      "token_budget": 3800
    }
  ],
  "load_sequence": [
    {
      "rule_path": "rules/000-global-core.md",
      "layer": "HARD",
      "context_tier": "Critical",
      "description": "Foundational operating contract: PRE-FLIGHT gates, surgical edits, and communication standards.",
      "token_budget": 2550
    },
    {
      "rule_path": "rules/200-python-core.md",
      "layer": "SOFT",
      "context_tier": "High",
      "description": "Python core: toolchain detection, datetime UTC, and mandatory validation gate.",
      "token_budget": 3800
    }
  ],
  "deferred_rules": [],
  "warnings": []
}
```

## Token-budget deferral: "Write and document tests for my Streamlit dashboard"

Here a Low-tier rule is discovered as a candidate but deferred by the
token-budget cap. Note the completeness invariant: every
`candidate_rules[*].rule_path` appears in exactly one of `load_sequence` or
`deferred_rules`.

```json
{
  "schema_version": "rule-loader-matcher/v1",
  "candidate_rules": [
    {
      "rule_path": "rules/101-snowflake-streamlit-core.md",
      "layer": "SOFT",
      "context_tier": "High",
      "description": "Streamlit core: setup, navigation, and state management.",
      "token_budget": 2350
    },
    {
      "rule_path": "rules/206-python-pytest.md",
      "layer": "SOFT",
      "context_tier": "Medium",
      "description": "Python pytest patterns.",
      "token_budget": 2400
    },
    {
      "rule_path": "rules/204-python-docs.md",
      "layer": "SOFT",
      "context_tier": "Low",
      "description": "Python documentation standards.",
      "token_budget": 2800
    }
  ],
  "load_sequence": [
    {
      "rule_path": "rules/000-global-core.md",
      "layer": "HARD",
      "context_tier": "Critical",
      "description": "Foundational operating contract.",
      "token_budget": 2550
    },
    {
      "rule_path": "rules/101-snowflake-streamlit-core.md",
      "layer": "SOFT",
      "context_tier": "High",
      "description": "Streamlit core: setup, navigation, and state management.",
      "token_budget": 2350
    },
    {
      "rule_path": "rules/206-python-pytest.md",
      "layer": "SOFT",
      "context_tier": "Medium",
      "description": "Python pytest patterns.",
      "token_budget": 2400
    }
  ],
  "deferred_rules": [
    {
      "rule_path": "rules/204-python-docs.md",
      "reason": "token_budget"
    }
  ],
  "warnings": []
}
```

The main agent must surface the `deferred_rules[*]` entry as a Gate 3 deferral
note (e.g. `[Deferred: 204-python-docs.md - Low tier, token-budget cap]`): it
must not silently drop token-budget deferrals.

## Not a manifest

- A Markdown table of rules is **display-only** and cannot satisfy Gate 2.
- A prose summary, a prior-session note, or a copied table is not valid Gate 2 evidence.
- Rule file **contents** must never appear in the manifest: paths and metadata only.
