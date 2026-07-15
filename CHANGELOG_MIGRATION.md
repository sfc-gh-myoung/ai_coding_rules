# CHANGELOG — Rules Keyword & Schema Loader Refactor (v3.5)

## Release: `rules-keyword-schema-v3-5` (2026-07-15)

End-to-end delivery of the rules-keyword-schema-loader v5 plan
(`.snowflake/cortex/plans/rules-keyword-schema-loader-refactor-v5.md`).

### Track A — Keyword precision (data)

- Rewrote LLM keyword prompt in `src/ai_rules/commands/keywords.py` to enforce
  compound-token preference, stop-list awareness, and per-keyword rationale.
- Introduced `.workbench/config/keyword_stoplist.txt` and collision post-filter
  (`ai-rules keywords collisions` subcommand).
- Applied audited keywords in 4 batches across 194 production rules.
- **Hardening (this release):** added HARD typed triggers (`ext:`/`file:`/`dir:`)
  to 7 rules where semantically justified — `ext:.py` (`200-python-core.md`),
  `ext:.sql` (`100-snowflake-core.md`, `102-snowflake-sql-core.md`,
  `102b-snowflake-sql-procedures.md`), `file:snowflake.yml`
  (`112-snowflake-snowcli.md`), `dir:rules/` (`002-rule-governance.md`),
  `dir:skills/` (`002h-claude-code-skills.md`). Each swap kept total keyword
  count within the enforced 5-7 cap. Updated 7 fixture prompts to embed
  verbatim `kw:` tokens declared by their required rules so the
  trigger-evidence invariant holds for all 30 fixtures.

### Track B — Schema migration to v3.5 YAML frontmatter

- New schema: rules use YAML frontmatter (fenced `---` block) for `keywords`,
  `depends`, `token_budget`, `context_tier`, `schema_version`, `rule_version`,
  `last_updated`. Retired the inline `**Field:**` markdown metadata format.
- Migrated 194 production rules via `scripts/migrate_v34_to_v35.py`. Canary
  migration validated on `rules/206-python-pytest.md`.
- Extended parser/validator to accept YAML frontmatter (dual-parse window
  during rollout).
- Prose `### Dependencies` block retired; `depends:` YAML key with `required:`
  / `optional:` sub-lists is the canonical form.
- Documentation updated in `002-rule-governance.md`, `002a-rule-creation.md`,
  `002b-rule-update.md`, and `skills/rule-loader/workflows/*.md`.
- Migration reports at `.workbench/results/full_migration_report.json`.

### Track C — Rule-loader second-pass validation

- Added `skills/rule-loader/workflows/second-pass-confirmation.md` (Phase 3.5
  filter algorithm; HARD candidates exempt; top-8 SOFT cap;
  ≤4,000-token budget; no-cache invariant).
- Defined `rule-loader-manifest/v2` schema in `skills/rule-loader/SKILL.md`;
  bumped SKILL version to `2.0.0`. Additive fields:
  `candidate_rules[*].second_pass`, `deferred_rules[*].reason_type =
  second_pass_rejected`, root `second_pass_evidence`.
- Extended `src/ai_rules/rule_loader_eval/manifest.py` validator to accept
  both v1 and v2 with v2-specific invariants (HARD never filtered, required
  `second_pass_evidence`, HARD `confirmation_reason: hard-candidate-exempt`).
  Backed by 11 unit tests in `tests/test_manifest_v2.py`.
- False-positive fixture set at
  `.workbench/eval-fixtures/false_positive_fixtures.json` (6 FP + 3 HARD),
  8 unit tests in `tests/test_false_positive_fixture.py`.
- `AGENTS.md` Gate-2 manifest schema string updated `v1 → v2`.

### Phase 4 — Cutover

- Removed dual-parse inline fallback from `index.py` (dropped `RE_*` regex
  paths) and `validate.py` (dropped inline `**Field:**` branch and `##
  Metadata` header check).
- `002i-rule-loadtrigger.md` tombstone added to `SKIP_FILES` (index.py) and
  `schemas/rule-schema.yml::excluded_files.files` (validator).
- Retired 4 obsolete workbench scripts:
  `.workbench/rule-dep-audit/check_cycles.py`, `check_dep_consistency.py`,
  `extract_inventory.py`, `fix_dep_consistency.py` (superseded by
  `check_limits.py` post-Track-B and `tests/test_track_b_ci_gates.py`).
- Manifest emission default flipped to `rule-loader-manifest/v2` in
  `skills/rule-loader/SKILL.md`.
- Test fixtures migrated to YAML frontmatter throughout `tests/cli/test_index.py`
  and `tests/cli/test_validate.py`; obsolete inline-only tests deleted.
- Refreshed Track B golden baseline
  (`.workbench/baselines/pre-track-b/RULES_INDEX.md`).

### Static-CI matrix (final)

- `uv run ai-rules validate rules/` → 0 CRITICAL, 0 HIGH
- `uv run ai-rules index check` → exit 0 (`keyword_entries` = 1350 ≥ 1200)
- `uv run ai-rules rule-loader validate` → 30 fixtures pass trigger-evidence
- `uv run pytest tests/` → **1521 passed, 0 failed**

### Known follow-up

- `rule-loader eval` precision suite (`eval_results.json` in
  `.workbench/baselines/pre-track-a/`) is still `status: deferred`. Populating
  the baseline requires a live Cortex Agent SDK run (has cost implications)
  and is deferred to a separate future session.

### Git tags

- `pre-track-a-baseline` — pre-Track-A baseline HEAD
- `pre-track-b-migration` — pre-Track-B YAML-frontmatter migration HEAD
- `track-b-complete` — Track B schema migration complete
- `track-c-complete` — Track C rule-loader second-pass complete
- `rules-keyword-schema-v3-5` — this release

---

## Schema migration v3.4 → v3.5 (2026-07-15)

- `000-global-core.md`: v3.10.0 → v4.0.0 (schema v3.5 migration)
- `001-memory-bank.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `002-rule-governance.md`: v3.8.0 → v4.0.0 (schema v3.5 migration)
- `002a-rule-creation.md`: v3.5.0 → v4.0.0 (schema v3.5 migration)
- `002b-rule-update.md`: v1.3.0 → v2.0.0 (schema v3.5 migration)
- `002c-rule-optimization.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `002d-advanced-rule-patterns.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `002e-schema-validator-usage.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `002f-schema-validator-advanced.md`: v1.3.0 → v2.0.0 (schema v3.5 migration)
- `002g-agent-optimization.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `002h-claude-code-skills.md`: v3.7.0 → v4.0.0 (schema v3.5 migration)
- `002j-rule-examples.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `002k-model-optimization.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `002l-skill-advanced-patterns.md`: v1.3.0 → v2.0.0 (schema v3.5 migration)
- `002m-agent-format-antipatterns.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `002n-agent-protocol-reference.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `003-context-engineering.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `003a-long-horizon-tasks.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `004-tool-design-for-agents.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `004a-tool-set-curation.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `004b-tool-output-efficiency.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `100-snowflake-core.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `100f-snowflake-connection-errors.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `101-snowflake-streamlit-core.md`: v4.3.0 → v5.0.0 (schema v3.5 migration)
- `101a-snowflake-streamlit-visualization.md`: v4.3.0 → v5.0.0 (schema v3.5 migration)
- `101b-snowflake-streamlit-performance.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `101c-snowflake-streamlit-security.md`: v4.3.0 → v5.0.0 (schema v3.5 migration)
- `101d-snowflake-streamlit-testing.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `101e-snowflake-streamlit-sql-errors.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `101f-snowflake-streamlit-deployment-errors.md`: v2.3.0 → v3.0.0 (schema v3.5 migration)
- `101g-snowflake-streamlit-fragments.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `101h-snowflake-streamlit-timeseries.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `101i-snowflake-streamlit-viz-plotly.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `101j-snowflake-streamlit-viz-pydeck.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `101k-snowflake-streamlit-viz-altair.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `101l-snowflake-streamlit-deployment.md`: v1.4.0 → v2.0.0 (schema v3.5 migration)
- `101m-snowflake-streamlit-pydeck-layers.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `101n-snowflake-streamlit-migration.md`: v1.3.0 → v2.0.0 (schema v3.5 migration)
- `102-snowflake-sql-core.md`: v1.6.0 → v2.0.0 (schema v3.5 migration)
- `102a-snowflake-sql-automation.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `102b-snowflake-sql-procedures.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `102c-snowflake-sql-reserved-chars.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `102d-snowflake-sql-cicd.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `102e-snowflake-sql-procedure-antipatterns.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `103-snowflake-performance-tuning.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `104-snowflake-streams-tasks.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `105-snowflake-cost-governance.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `106-snowflake-semantic-views-core.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `106a-snowflake-semantic-views-advanced.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `106b-snowflake-semantic-views-querying.md`: v3.5.0 → v4.0.0 (schema v3.5 migration)
- `106c-snowflake-semantic-views-integration.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `106d-snowflake-semantic-views-development.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `107-snowflake-security-governance.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `108-snowflake-data-loading.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `109-snowflake-notebooks.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `109a-snowflake-notebooks-tutorials.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `109b-snowflake-app-deployment-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `109c-snowflake-app-deployment-troubleshooting.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `109d-snowflake-notebooks-linting.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `109e-snowflake-notebook-checkpoints.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `109f-snowflake-notebook-two-approach-pattern.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `109g-snowflake-app-deployment-sql-scripts.md`: v1.3.0 → v2.0.0 (schema v3.5 migration)
- `109h-snowflake-app-deployment-taskfile.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `109i-snowflake-app-deployment-advanced.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `109j-snowflake-sis-typeerror-debugging.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `110-snowflake-model-registry.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `110a-snowflake-model-monitor.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `110b-snowflake-model-registry-operations.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `111-snowflake-observability-core.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `111a-snowflake-observability-logging.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `111b-snowflake-observability-tracing.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `111c-snowflake-observability-monitoring.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `111d-snowflake-observability-snowsight.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `112-snowflake-snowcli.md`: v3.5.0 → v4.0.0 (schema v3.5 migration)
- `113-snowflake-feature-store.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `113a-snowflake-feature-store-patterns.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `113b-snowflake-feature-store-engineering.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `114-snowflake-cortex-aisql.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `114a-snowflake-cortex-ai-transcribe.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `115-snowflake-cortex-agents-core.md`: v3.5.0 → v4.0.0 (schema v3.5 migration)
- `115a-snowflake-cortex-agents-instructions.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `115b-snowflake-cortex-agents-operations.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `115c-snowflake-cortex-agents-testing.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `115d-snowflake-cortex-agents-observability.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `116-snowflake-cortex-search.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `117-snowflake-mcp-server.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `118-snowflake-cortex-rest-api.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `118a-snowflake-cortex-rest-api-streaming.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `119-snowflake-warehouse-management.md`: v3.6.0 → v4.0.0 (schema v3.5 migration)
- `120-snowflake-spcs.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `121-snowflake-snowpipe.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `121a-snowflake-snowpipe-streaming.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `121b-snowflake-snowpipe-monitoring.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `121c-snowflake-snowpipe-troubleshooting.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `121d-snowflake-snowpipe-streaming-sdk.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `121e-snowflake-snowpipe-troubleshooting-advanced.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `121f-snowflake-snowpipe-monitoring-alerts.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `122-snowflake-dynamic-tables.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `123-snowflake-object-tagging.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `124-snowflake-data-quality-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `124a-snowflake-data-quality-custom.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `124b-snowflake-data-quality-operations.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `125-snowflake-role-introspection.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `126-snowflake-cortex-code-agent-sdk.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `130-snowflake-demo-sql.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `131-snowflake-demo-creation.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `132-snowflake-demo-modeling.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `200-python-core.md`: v4.2.0 → v5.0.0 (schema v3.5 migration)
- `200a-python-validation-gate.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `200b-python-environment-tooling.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `201-python-lint-format.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `202-markup-config-validation.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `202a-markdown-linting.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `203-python-project-setup.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `204-python-docs.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `205-python-classes.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `207-python-logging.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `210-python-fastapi-core.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `210a-python-fastapi-security.md`: v3.9.0 → v4.0.0 (schema v3.5 migration)
- `210b-python-fastapi-testing.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `210c-python-fastapi-deployment.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `210d-python-fastapi-monitoring.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `210e-python-fastapi-security-hardening.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `220-python-typer-cli.md`: v3.9.0 → v4.0.0 (schema v3.5 migration)
- `220a-python-typer-config.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `220b-python-typer-testing.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `220c-python-typer-rich.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `221-python-htmx-core.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `221a-python-htmx-templates.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `221b-python-htmx-flask.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `221c-python-htmx-fastapi.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `221d-python-htmx-testing.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `221e-python-htmx-patterns.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `221f-python-htmx-integrations.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `221g-python-htmx-sse.md`: v3.1.0 → v4.0.0 (schema v3.5 migration)
- `221h-python-htmx-fastapi-auth.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `221i-python-htmx-patterns-advanced.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `230-python-pydantic.md`: v3.10.0 → v4.0.0 (schema v3.5 migration)
- `230a-python-pydantic-settings.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `230b-python-pydantic-integration.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `240-python-faker.md`: v3.9.0 → v4.0.0 (schema v3.5 migration)
- `240a-python-faker-testing.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `240b-python-faker-advanced.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `250-python-flask.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `251-python-datetime-core.md`: v3.9.0 → v4.0.0 (schema v3.5 migration)
- `251a-python-datetime-advanced.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `251b-python-datetime-integration.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `252-python-pandas-core.md`: v3.9.0 → v4.0.0 (schema v3.5 migration)
- `252a-python-pandas-performance.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `252b-python-pandas-io-integration.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `300-bash-scripting-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `300a-bash-security.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `300b-bash-testing-tooling.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `300c-bash-security-advanced.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `300d-bash-advanced.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `310-zsh-scripting-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `310a-zsh-advanced-features.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `310b-zsh-compatibility.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `310c-zsh-compatibility-platforms.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `310d-zsh-completion-prompt.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `350-docker-core.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `351-podman-core.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `351a-podman-examples.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `420-javascript-core.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `421-javascript-alpinejs-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `421a-javascript-alpinejs-advanced.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `424-javascript-docs.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `430-typescript-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `434-typescript-docs.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `440-react-core.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `440a-react-anti-patterns.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `441-react-backend.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `500-frontend-htmx-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `501-frontend-browser-globals-collisions.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `502-frontend-revealjs-core.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `600-golang-core.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `600a-golang-patterns.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `800-project-changelog.md`: v3.4.0 → v4.0.0 (schema v3.5 migration)
- `801-project-readme.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `802-project-contributing.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `803-project-git-workflow.md`: v3.7.0 → v4.0.0 (schema v3.5 migration)
- `804-project-documentation.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `805-technical-writing-style.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `806-workbench-folder-policy.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `810-cli-design-core.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `820-taskfile-automation.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `820a-taskfile-advanced-patterns.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `821-makefile-automation.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `821a-makefile-advanced-patterns.md`: v1.1.0 → v2.0.0 (schema v3.5 migration)
- `920-data-science-analytics.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `930-data-governance-quality.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
- `940-business-analytics.md`: v3.3.0 → v4.0.0 (schema v3.5 migration)
- `950-dbt-core.md`: v1.2.0 → v2.0.0 (schema v3.5 migration)
- `951-create-dbt-semantic-view.md`: v3.2.0 → v4.0.0 (schema v3.5 migration)
