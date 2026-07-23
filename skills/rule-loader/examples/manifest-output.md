# Example: rule-loader discovery manifest (`rule-loader-manifest/v1`)

This is the authoritative return value of the `rule-loader` skill when it runs
inside a discovery sub-agent. It is **metadata only** — rule file *bodies* never
appear in the manifest. The main agent reads each `load_sequence[*].rule_path`
itself via `read_file` (preserving the Gate 3 read-and-apply contract).

## Minimal valid manifest — "Fix the bug in auth.py"

```json
{
  "schema_version": "rule-loader-manifest/v1",
  "loading_contract": "Each load_sequence entry with read_required=true MUST be loaded via read_file before citation. The manifest is metadata only — it does not substitute for reading rule content.",
  "request_fingerprint": "sha256:6b1f...c2a9",
  "runtime": {
    "primitive": "Task",
    "spawn_evidence": "toolu_01ABc...",
    "agent_id": "agent-7f3d2a1c"
  },
  "keywords_searched": [".py", "fix", "bug"],
  "index_evidence": [
    {
      "kind": "grep",
      "target": "rules/RULES_INDEX.md",
      "query": "grep -iwE \"ext=\\.py\" rules/RULES_INDEX.md",
      "result_summary": "200-python-core.md"
    }
  ],
  "candidate_rules": [
    {
      "rule_path": "rules/200-python-core.md",
      "rule_name": "200-python-core.md",
      "reason_type": "extension",
      "reason": "ext=.py HARD match",
      "context_tier": "High",
      "token_estimate": 2600,
      "layer": "HARD",
      "required": true
    }
  ],
  "candidate_count": 1,
  "degraded": false,
  "failures": [],
  "load_sequence": [
    {
      "order": 1,
      "rule_path": "rules/000-global-core.md",
      "rule_name": "000-global-core.md",
      "reason_type": "foundation",
      "reason": "foundation",
      "context_tier": "Critical",
      "token_estimate": 2550,
      "layer": "FOUNDATION",
      "required": true,
      "read_required": true,
      "description": "Foundational operating contract: PRE-FLIGHT gates, surgical edits, validation sequences, and communication standards for all AI agents."
    },
    {
      "order": 2,
      "rule_path": "rules/200-python-core.md",
      "rule_name": "200-python-core.md",
      "reason_type": "extension",
      "reason": "ext=.py HARD match",
      "context_tier": "High",
      "token_estimate": 2600,
      "layer": "HARD",
      "required": true,
      "read_required": true,
      "description": "Python core: toolchain detection, datetime UTC, collections.abc imports, error handling, and mandatory validation gate."
    }
  ],
  "deferred_rules": [],
  "execution_hints": {
    "expected_turns_per_fixture": 3,
    "max_output_tokens": 1000,
    "note": "Advisory only. Calibrated from opus-4-6 baseline (91 turns / 35 fixtures ≈ 2.6 turns/fixture; 19k output tokens / 35 fixtures ≈ 543 tokens/fixture)."
  }
}
```

## Token-budget deferral — "Write and document tests for my Streamlit dashboard"

Here a Low-tier rule is discovered as a candidate but deferred by the
token-budget / ContextTier cap. Note the completeness invariant: every
`candidate_rules[*].rule_path` appears in exactly one of `load_sequence` or
`deferred_rules`.

```json
{
  "schema_version": "rule-loader-manifest/v1",
  "loading_contract": "Each load_sequence entry with read_required=true MUST be loaded via read_file before citation. The manifest is metadata only — it does not substitute for reading rule content.",
  "request_fingerprint": "sha256:9d0e...11bb",
  "runtime": {
    "primitive": "Task",
    "spawn_evidence": "toolu_02XyZ...",
    "agent_id": "agent-1a2b3c4d"
  },
  "keywords_searched": ["streamlit", "test", "document", "dashboard"],
  "index_evidence": [
    {
      "kind": "grep",
      "target": "rules/RULES_INDEX.md",
      "query": "grep -iE \"streamlit|test|docs\" rules/RULES_INDEX.md",
      "result_summary": "101-snowflake-streamlit-core.md, 206-python-pytest.md, 204-python-docs.md"
    }
  ],
  "candidate_rules": [
    {
      "rule_path": "rules/101-snowflake-streamlit-core.md",
      "rule_name": "101-snowflake-streamlit-core.md",
      "reason_type": "activity_keyword",
      "reason": "keyword: Streamlit",
      "context_tier": "High",
      "token_estimate": 3000,
      "layer": "SOFT",
      "required": false
    },
    {
      "rule_path": "rules/206-python-pytest.md",
      "rule_name": "206-python-pytest.md",
      "reason_type": "activity_keyword",
      "reason": "keyword: test",
      "context_tier": "Medium",
      "token_estimate": 2400,
      "layer": "SOFT",
      "required": false
    },
    {
      "rule_path": "rules/204-python-docs.md",
      "rule_name": "204-python-docs.md",
      "reason_type": "activity_keyword",
      "reason": "keyword: document",
      "context_tier": "Low",
      "token_estimate": 2800,
      "layer": "SOFT",
      "required": false
    }
  ],
  "candidate_count": 3,
  "degraded": false,
  "failures": [],
  "load_sequence": [
    {
      "order": 1,
      "rule_path": "rules/000-global-core.md",
      "rule_name": "000-global-core.md",
      "reason_type": "foundation",
      "reason": "foundation",
      "context_tier": "Critical",
      "token_estimate": 2550,
      "layer": "FOUNDATION",
      "required": true,
      "read_required": true
    },
    {
      "order": 2,
      "rule_path": "rules/101-snowflake-streamlit-core.md",
      "rule_name": "101-snowflake-streamlit-core.md",
      "reason_type": "activity_keyword",
      "reason": "keyword: Streamlit",
      "context_tier": "High",
      "token_estimate": 3000,
      "layer": "SOFT",
      "required": false,
      "read_required": true
    },
    {
      "order": 3,
      "rule_path": "rules/206-python-pytest.md",
      "rule_name": "206-python-pytest.md",
      "reason_type": "activity_keyword",
      "reason": "keyword: test",
      "context_tier": "Medium",
      "token_estimate": 2400,
      "layer": "SOFT",
      "required": false,
      "read_required": true
    }
  ],
  "deferred_rules": [
    {
      "rule_path": "rules/204-python-docs.md",
      "rule_name": "204-python-docs.md",
      "reason_type": "context_tier_cap",
      "reason": "Deferred by token-budget management after the 3-rule domain/activity cap",
      "context_tier": "Low",
      "token_estimate": 2800,
      "layer": "SOFT",
      "deferred_because": "ContextTier Low and the domain/activity cap (3) was reached by higher-tier rules; total estimated context would exceed the configured token-budget ceiling"
    }
  ],
  "execution_hints": {
    "expected_turns_per_fixture": 3,
    "max_output_tokens": 1000,
    "note": "Advisory only. Calibrated from opus-4-6 baseline (91 turns / 35 fixtures ≈ 2.6 turns/fixture; 19k output tokens / 35 fixtures ≈ 543 tokens/fixture)."
  }
}
```

The main agent must surface the `deferred_rules[*]` entry as a Gate 3 deferral
note (e.g. `[Deferred: 204-python-docs.md — Low tier, token-budget cap]`) — it
must not silently drop token-budget deferrals.

## Not a manifest

- A Markdown table of rules is **display-only** and cannot satisfy Gate 2.
- A prose summary, a prior-session note, or a copied table is not valid Gate 2 evidence.
- Rule file **contents** must never appear in the manifest — paths and metadata only.
