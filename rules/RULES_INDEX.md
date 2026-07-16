<!-- Template: Do not edit directly. Run `ai-rules index generate` to regenerate. -->
# RULES_INDEX

> **Agent note:** This is the **single discovery index** for AI agents. Grep here for
> keywords, extensions, file triggers, and directories. Generated from rule frontmatter.

Grep-optimised, keyword-only index. One line per rule.

Format: `<filename> tier=<T> [ext=<...>] [file=<...>] [dir=<...>] kw=<word1> <word2> ...`

Keywords are space-separated within the `kw=` field. Multi-word keywords use
hyphens (e.g., `prompt-engineering`). `ext=`, `file=`, `dir=` fields are
emitted only when the rule declares triggers of that kind; absent otherwise.

**Grep recipes:**

```
# Keyword search (word-boundary):
grep -iwE "KEYWORD1|KEYWORD2" rules/RULES_INDEX.md

# Extension search (field-prefix):
grep -iE "ext=.*\.py" rules/RULES_INDEX.md

# Directory search:
grep -iE "dir=.*skills/" rules/RULES_INDEX.md

# File search:
grep -iE "file=.*pyproject.toml" rules/RULES_INDEX.md
```

See `rules/.index-stats.json` for rule count, `format_version`, and generation
metadata; this file intentionally omits volatile timestamps so
`ai-rules index check` is deterministic against corpus content only.

000-global-core.md tier=Critical kw=surgical-edits pre-flight-gates validation-command-sequence context-preservation-hierarchy foundation-operating-contract task-list-confirmation pytest
001-memory-bank.md tier=Critical kw=memory-bank context-preservation rapid-recovery-protocol aggressive-pruning activeContext.md session-initialization
002-rule-governance.md tier=Critical dir=rules/ kw=rule-schema-compliance metadata-field-requirements Contract-Markdown-subsections semantic-discovery-keywords ai-rules-validate agent-first-design-priorities
002a-rule-creation.md tier=High kw=rule-creation-workflow rule-numbering-ranges v3.4-schema-compliance Contract-Markdown-subsections rule-file-naming-convention metadata-field-setup aisql
002b-rule-update.md tier=High kw=rule-versioning RuleVersion-increment LastUpdated-field rule-modification-workflow MAJOR-MINOR-PATCH-semantics schema-migration-checklist ci/cd
002c-rule-optimization.md tier=High kw=token-budget-tiers progressive-rule-loading ai-rules-tokens-CLI rule-splitting-decision-tree context-window-budget-allocation TokenBudget-metadata-format cortex
002d-advanced-rule-patterns.md tier=Medium kw=system-prompt-altitude investigation-first-protocol multi-session-workflows anti-pattern-library-structure parallel-execution-design goldilocks-zone-heuristics fastapi
002e-schema-validator-usage.md tier=High kw=ai-rules-validate schema-v3.2-compliance severity-levels-CRITICAL-HIGH-MEDIUM exit-code-interpretation common-validation-fixes validator-command-flags ci/cd
002f-schema-validator-advanced.md tier=Medium kw=ci/cd-pipeline programmatic-parsing automated-fix-iteration pre-commit-hooks github-actions-workflow batch-validation ci/cd
002g-agent-optimization.md tier=High kw=agent-first-design ASCII-table-prohibition imperative-voice-instructions sequential-processing-model terminology-consistency-enforcement arrow-character-replacement llm
002h-claude-code-skills.md tier=High dir=skills/ kw=SKILL.md-authoring YAML-frontmatter progressive-disclosure trigger-keywords input-output-contracts third-person-description
002j-rule-examples.md tier=Medium kw=rule-examples example-schema example-schema.yml example-discovery reference-implementations example-staleness streamlit
002k-model-optimization.md tier=Low kw=context-window-sizing loading-budget-calculation GPT-4o-GPT-5.1 Claude-Sonnet-Opus Gemini-Pro prompt-caching-strategy
002l-skill-advanced-patterns.md tier=Low kw=plan-validate-execute orchestrator-worker-composition visual-analysis-pattern intermediate-validation-scripts Claude-A/B-iteration batch-failure-handling
002m-agent-format-antipatterns.md tier=Medium kw=agent-optimized-formatting ASCII-table-violations arrow-character-replacement imperative-voice-instructions visual-diagram-prohibition nested-conditional-lists mermaid
002n-agent-protocol-reference.md tier=Medium kw=agent-bootstrap-protocol PRE-FLIGHT-gate-compliance RULES_INDEX-grep-discovery ACT-authorization-recognition task-switch-detection fabricated-gate-anti-pattern cortex
003-context-engineering.md tier=Critical kw=context-window-management attention-budget context-rot-prevention progressive-disclosure-patterns agentic-search-vs-RAG context-compaction-strategies long-horizon-task-state
003a-long-horizon-tasks.md tier=Medium kw=long-horizon-tasks context-compaction persistent-memory sub-agent-delegation multi-session-continuity checkpointing-protocols fastapi
004-tool-design-for-agents.md tier=High kw=agent-tool-design single-responsibility-tools token-efficient-outputs LLM-friendly-parameters tool-boundary-overlap actionable-error-messages ci/cd
004a-tool-set-curation.md tier=Medium kw=tool-set-curation minimal-viable-tool-set tool-splitting-criteria tool-merging-criteria tool-bloat-detection tool-boundaries etl
004b-tool-output-efficiency.md tier=Medium kw=tool-output-minimization progressive-loading token-efficient-responses silent-success-pattern metadata-elimination agent-context-preservation ci/cd
100-snowflake-core.md tier=High ext=.sql kw=CTE-extraction VARIANT-parsing-optimization Streams-Tasks-incremental partition-pruning-early-filtering QUALIFY-ROW_NUMBER-deduplication Query-Profile-validation
100f-snowflake-connection-errors.md tier=High kw=connection-error-classification network-policy-violation-detection message-first-error-analysis VPN-disconnect-diagnosis snowflake.connector.errors.DatabaseError error-code-08001-ambiguity snowpark
101-snowflake-streamlit-core.md tier=High kw=Streamlit st.navigation session-state Container-Runtime config.toml-theming st.connection-snowflake TOML
101a-snowflake-streamlit-visualization.md tier=High kw=st.plotly_chart st.pydeck_chart st.altair_chart library-selection use_container_width WebGL-context-limits pandas
101b-snowflake-streamlit-performance.md tier=High kw=@st.cache_data-decorator @st.cache_resource-decorator Snowflake-column-normalization st.spinner-progress-feedback query-loop-aggregation ttl-cache-expiration pandas
101c-snowflake-streamlit-security.md tier=High kw=st.secrets SQL-injection-prevention Streamlit-authentication input-sanitization file-upload-validation container-runtime-secrets TOML
101d-snowflake-streamlit-testing.md tier=High kw=AppTest streamlit-ui-testing cache-behavior-testing mock-snowflake-session widget-interaction-testing pytest-coverage-80% TOML
101e-snowflake-streamlit-sql-errors.md tier=Low kw=SnowparkSQLException streamlit-sql-error-display error-code-display query-context-messaging st.stop-cascade-prevention empty-dataframe-warning pandas
101f-snowflake-streamlit-deployment-errors.md tier=Low kw=Streamlit-deployment Container-Runtime Warehouse-Runtime External-Access-Integration stage-upload-compression compute-pool-provisioning TOML
101g-snowflake-streamlit-fragments.md tier=Medium kw=st.fragment run_every-auto-refresh live-progress-polling session-state-persistence fragment-termination-st.stop conditional-fragment-rendering cortex
101h-snowflake-streamlit-timeseries.md tier=Low kw=time-series-smoothing pandas-resample SCADA-visualization aggregation-method-selection high-frequency-sensor-data Streamlit-chart-performance pandas
101i-snowflake-streamlit-viz-plotly.md tier=Medium kw=plotly-express graph-objects st.plotly_chart chart-animations faceting-subplots colorblind-safe-palettes pandas
101j-snowflake-streamlit-viz-pydeck.md tier=Medium kw=pydeck deck.gl-layers 3D-geospatial WebGL-context-limit ViewState-configuration hexbin-aggregation streamlit
101k-snowflake-streamlit-viz-altair.md tier=Medium kw=altair-declarative-encoding vega-lite-grammar mark_point-mark_line-mark_bar st.altair_chart interval-selection-brushing data-type-suffixes-:Q-:N-:O-:T pandas
101l-snowflake-streamlit-deployment.md tier=High kw=container-runtime warehouse-runtime pyproject.toml external-access-integration compute-pool runtime-migration TOML
101m-snowflake-streamlit-pydeck-layers.md tier=Low kw=pydeck-layer-types HexagonLayer-aggregation GeoJsonLayer-extrusion ArcLayer-flow-visualization multi-layer-composition deck.gl-accessor-syntax streamlit
101n-snowflake-streamlit-migration.md tier=Low kw=Streamlit-runtime-migration environment.yml-to-pyproject.toml get_active_session-replacement Container-Runtime-infrastructure bidirectional-runtime-swap in-place-Streamlit-upgrade TOML
102-snowflake-sql-core.md tier=High ext=.sql kw=SQL-file-headers COPY-INTO-ON_ERROR-placement CREATE-VIEW-COMMENT-syntax fully-qualified-object-names CLI-templating-reserved-characters idempotent-DDL-patterns SQL-data-transformation
102a-snowflake-sql-automation.md tier=High kw=parameterized-SQL-templates idempotent-MERGE-operations CREATE-TABLE-IF-NOT-EXISTS multi-environment-deployment CI/CD-pipeline-integration production-safe-automation ci/cd
102b-snowflake-sql-procedures.md tier=High ext=.sql kw=SQL-scripting dollar-quoting EXECUTE-AS EXECUTE-IMMEDIATE bind-variables procedure-body-quoting
102c-snowflake-sql-reserved-chars.md tier=Low kw=cli-compatibility ampersand-escaping template-expansion enable-templating-flag brand-name-preservation snow-sql-tool
102d-snowflake-sql-cicd.md tier=Low kw=Makefile-targets GitHub-Actions-workflows multi-environment-deployment Snowflake-CLI secrets-store-integration SQL-template-parameterization ci/cd
102e-snowflake-sql-procedure-antipatterns.md tier=Low kw=stored-procedure-anti-patterns dollar-quoting EXECUTE-AS SQL-injection-bind-variables fully-qualified-object-names procedure-delimiter-escaping udf
103-snowflake-performance-tuning.md tier=High kw=Query-Profile-analysis partition-pruning-optimization spillage-detection clustering-key-justification warehouse-sizing-diagnosis slow-query-investigation snowsight
104-snowflake-streams-tasks.md tier=High kw=change-data-capture stream-consumption task-dag merge-patterns task-history-monitoring stream-staleness cdc
105-snowflake-cost-governance.md tier=High kw=resource-monitor credit-quota warehouse-metering-history cost-attribution-tagging serverless-task-credits suspend-trigger etl
106-snowflake-semantic-views-core.md tier=High kw=CREATE-SEMANTIC-VIEW TABLES-PRIMARY-KEY FACTS-DIMENSIONS-METRICS RELATIONSHIPS-clause mapping-syntax-alias.physical_column SHOW-SEMANTIC-DIMENSIONS ci/cd
106a-snowflake-semantic-views-advanced.md tier=High kw=semantic-view-anti-patterns relationship-granularity physical-column-verification expression-reference-cycles template-character-restrictions semantic-view-quality-checks cortex
106b-snowflake-semantic-views-querying.md tier=High kw=SEMANTIC_VIEW-function dimension-compatibility FACTS-METRICS-mutual-exclusion window-function-metrics semantic-view-testing WHERE-clause-restrictions cortex
106c-snowflake-semantic-views-integration.md tier=Medium kw=Cortex-Analyst Cortex-Agent-grounding semantic-view-governance natural-language-query-synonyms analyst-troubleshooting policy-inheritance-base-tables ci/cd
106d-snowflake-semantic-views-development.md tier=Medium kw=semantic-view-generator verified-query-repository VQR-logical-table-naming YAML-semantic-model iterative-refinement-workflow onboarding-questions cortex
107-snowflake-security-governance.md tier=High kw=RBAC-role-hierarchy masking-policy-attachment row-access-policy-enforcement object-tagging-governance data-metric-function-scheduling least-privilege-grant-design dmf
108-snowflake-data-loading.md tier=High kw=COPY-INTO stage-management file-format-definition bulk-load-optimization VALIDATION_MODE ON_ERROR-handling COPY_HISTORY-monitoring
109-snowflake-notebooks.md tier=Medium kw=Snowflake-Notebooks reproducible-notebook-execution Snowpark-DataFrame-computation cell-naming-conventions nbqa-ruff-linting notebook-state-management pandas
109a-snowflake-notebooks-tutorials.md tier=High kw=notebook-tutorial-design learning-objectives-structure checkpoint-validation-cells anti-pattern-teaching progressive-complexity-management teaching-point-callouts pandas
109b-snowflake-app-deployment-core.md tier=Medium kw=staged-application-lifecycle five-step-deployment-workflow AUTO_COMPRESS-FALSE REMOVE-before-PUT Streamlit-ADD-LIVE-VERSION stage-as-source-of-truth ci/cd
109c-snowflake-app-deployment-troubleshooting.md tier=Medium kw=streamlit-deployment-troubleshooting sis-typeerror auto_compress-debugging stage-file-diagnostics live_version_location_uri notebook-cache-clearing deployment-permission-debugging
109d-snowflake-notebooks-linting.md tier=Low kw=nbqa notebook-linting Ruff-notebook-integration uvx-nbqa-commands notebook-cell-quality notebook-automation-targets TOML
109e-snowflake-notebook-checkpoints.md tier=Low kw=notebook-checkpoint-validation teaching-point-callouts actionable-error-messages progress-verification-gates context-before-code-pedagogy checkpoint-frequency-placement
109f-snowflake-notebook-two-approach-pattern.md tier=Low kw=two-approach-clarification notebook-approach-selection production-vs-learning-approach feature-demonstration-without-full-utilization approach-migration-guidance educational-context-justification pandas
109g-snowflake-app-deployment-sql-scripts.md tier=Low kw=PUT-AUTO_COMPRESS REMOVE-before-PUT CREATE-STREAMLIT-FROM stage-path-matching snow-stage-copy-recursive embedded-versioned-stage snowpark
109h-snowflake-app-deployment-taskfile.md tier=Low kw=Taskfile-deployment-automation five-step-deployment-workflow deployment-task-preconditions sequential-task-execution stage-file-upload-tasks notebook-streamlit-deployment snowsight
109i-snowflake-app-deployment-advanced.md tier=Low kw=multi-environment-promotion deployment-validation-gates rollback-recovery-procedures stage-backup-snapshot deployment-audit-trail environment-aware-automation streamlit
109j-snowflake-sis-typeerror-debugging.md tier=Medium kw=SiS-TypeError AUTO_COMPRESS-FALSE AttributeError-streamlit-module FROM-source-path live_version_location_uri environment.yml-streamlit-pin pandas
110-snowflake-model-registry.md tier=Medium kw=model-registry ml-model-versioning model-inference-serving model-RBAC-privileges sample-input-schema model-metadata-governance ci/cd
110a-snowflake-model-monitor.md tier=Medium kw=MODEL-MONITOR enable_monitoring drift-detection baseline-scoring-schema ml-observability monitor-refresh-interval pandas
110b-snowflake-model-registry-operations.md tier=Low kw=model-registry-operations ML-cost-governance model-version-cleanup inference-warehouse-sizing model-compliance-audit CI/CD-model-validation ci/cd
111-snowflake-observability-core.md tier=High kw=event-table-setup telemetry-level-hierarchy system-views-latency DEBUG-cost-implications SHOW-PARAMETERS-investigation OpenTelemetry-alignment snowpark
111a-snowflake-observability-logging.md tier=High kw=handler-logging log-volume-control sampling-strategy conditional-logging event-table-routing tight-loop-logging udf
111b-snowflake-observability-tracing.md tier=High kw=snowflake-telemetry-python create_span-context-manager 128-event-span-limit nested-span-hierarchy TRACE_LEVEL-configuration span-attribute-enrichment snowsight
111c-snowflake-observability-monitoring.md tier=High kw=ACCOUNT_USAGE-views telemetry-cost-optimization query-history-monitoring real-time-vs-historical-latency Snowsight-operational-dashboards cortex-token-tracking cortex
111d-snowflake-observability-snowsight.md tier=Low kw=snowsight-monitoring-interfaces cortex-ai-cost-attribution traces-and-logs-ui llm-evaluation-workflows distributed-tracing-ai-applications query-history-latency aisql
112-snowflake-snowcli.md tier=Medium file=snowflake.yml kw=snowflake.yml snowcli snowcli-uvx-pinned snowflake.yml-project stage-copy-no-auto-compress streamlit-deploy-FROM connection-profile-env CI-non-interactive-json
113-snowflake-feature-store.md tier=Medium kw=feature-store point-in-time-correctness feature-view-versioning entity-modeling ASOF-JOIN ml-lineage-integration rbac
113a-snowflake-feature-store-patterns.md tier=Low kw=ASOF-JOIN feature-view-versioning deterministic-transformations dynamic-table-refresh-costs training-data-leakage train-serve-skew
113b-snowflake-feature-store-engineering.md tier=Low kw=feature-engineering windowed-aggregations RFM-features velocity-features NULLIF-division-protection deterministic-transformations
114-snowflake-cortex-aisql.md tier=High kw=cortex-aisql llm-function-batching model-selection-strategy token-budget-control TO_FILE-stage-references CORTEX_USER-privilege-governance ai_classify
114a-snowflake-cortex-ai-transcribe.md tier=Medium kw=AI_TRANSCRIBE TO_FILE-syntax speaker-diarization audio-transcription FILE-type-reference staged-audio-formats ai_complete
115-snowflake-cortex-agents-core.md tier=High kw=cortex-agent agent-archetype tool-orchestration planning-instructions semantic-view-grounding agent-debugging aisql
115a-snowflake-cortex-agents-instructions.md tier=High kw=cortex-agent-instructions planning-instructions response-instructions agent-flagging-logic multi-tool-orchestration tool-selection-criteria cortex
115b-snowflake-cortex-agents-operations.md tier=High kw=agent-RBAC component-testing-agents agent-cost-budgets agent-plan-template agent-investigation-protocol agent-flagging-instructions aisql
115c-snowflake-cortex-agents-testing.md tier=Low kw=cortex-agent-testing agent-RBAC-grants component-integration-testing agent-tool-verification least-privilege-agent-permissions semantic-view-grants ci/cd
115d-snowflake-cortex-agents-observability.md tier=Low kw=cortex-agent-observability agent-cost-attribution AI-Observability-tracing agent-health-checks agent-troubleshooting-runbook dedicated-agent-warehouse cortex
116-snowflake-cortex-search.md tier=Medium kw=cortex-search-service document-chunking metadata-filtering search-tool-configuration SEARCH_PREVIEW-validation search-index-lifecycle ai_embed
117-snowflake-mcp-server.md tier=High kw=MCP mcp-server snowflake-managed-mcp-server CREATE-MCP-SERVER mcp-tool-invocation cortex_analyst_message-tool mcp-json-rpc-protocol mcp-server-rbac cortex
118-snowflake-cortex-rest-api.md tier=High kw=cortex-rest-api exponential-backoff-retry idempotency-keys rest-vs-aisql-decision sse-streaming-responses token-usage-monitoring aisql
118a-snowflake-cortex-rest-api-streaming.md tier=High kw=Cortex-REST-authentication server-sent-events SSE-stream-parsing Cortex-Agent-streaming PAT-token-headers response-format-detection cortex
119-snowflake-warehouse-management.md tier=High kw=virtual-warehouse-creation warehouse-sizing-strategy auto-suspend-configuration warehouse-type-selection GEN-2-warehouse adaptive-warehouse-tuning etl
120-snowflake-spcs.md tier=High kw=Snowpark-Container-Services compute-pool-instance-families OCI-image-deployment service-specification-YAML platform-events-monitoring GPU-workload-configuration flask
121-snowflake-snowpipe.md tier=High kw=snowpipe-auto-ingest file-based-ingestion cloud-event-notifications pipe-DDL serverless-compute file-sizing-optimization cdc
121a-snowflake-snowpipe-streaming.md tier=High kw=snowpipe-streaming high-performance-streaming-architecture streaming-channel-management offset-token-tracking sub-second-latency-ingestion row-level-SDK-ingestion snowpipe
121b-snowflake-snowpipe-monitoring.md tier=Medium kw=PIPE_USAGE_HISTORY Snowpipe-credit-tracking channel-status-monitoring COPY_HISTORY-Snowpipe cost-per-GB-optimization baseline-performance-metrics snowpipe
121c-snowflake-snowpipe-troubleshooting.md tier=Medium kw=snowpipe-debugging pipe-execution-failures streaming-channel-errors schema-mismatch-resolution latency-diagnosis diagnostic-queries snowpipe
121d-snowflake-snowpipe-streaming-sdk.md tier=High kw=snowpipe-streaming-sdk java-python-ingest-client channel-lifecycle-management offset-token-tracking schema-evolution-modes insertrow-error-handling snowpipe
121e-snowflake-snowpipe-troubleshooting-advanced.md tier=Low kw=snowpipe-streaming-offset exactly-once-semantics streaming-batch-optimization channel-ownership-conflicts pre-insert-validation snowpipe-debugging-checklist snowpipe
121f-snowflake-snowpipe-monitoring-alerts.md tier=Medium kw=snowpipe-alert-configuration channel-stall-detection SYSTEM$SEND_EMAIL baseline-threshold-derivation pipe-cost-per-GB file-size-100-250MB snowpipe
122-snowflake-dynamic-tables.md tier=High kw=dynamic-table refresh-mode target-lag incremental-refresh downstream-dependencies modular-pipeline-chaining cdc
123-snowflake-object-tagging.md tier=High kw=object-tagging tag-inheritance tag-based-masking ALLOWED_VALUES TAG_REFERENCES cost-attribution-tags
124-snowflake-data-quality-core.md tier=High kw=Data-Metric-Functions DMF-expectations system-DMF serverless-quality-monitoring quality-event-tables DMF-scheduling-patterns dmf
124a-snowflake-data-quality-custom.md tier=Medium kw=custom-DMF-creation business-rule-validation expectation-thresholds FLOAT-return-type parameterized-ARG_T Python-UDF-DMF dmf
124b-snowflake-data-quality-operations.md tier=High kw=DMF-scheduling quality-event-tables expectation-failures remediation-workflows EXECUTE-DATA-METRIC-FUNCTION quality-alerting dmf
125-snowflake-role-introspection.md tier=Medium kw=role-introspection account-roles-vs-database-roles SHOW-GRANTS-syntax SQL-compilation-error-000906 role-type-detection RBAC-automation rbac
126-snowflake-cortex-code-agent-sdk.md tier=High kw=cortex-code-agent-sdk agent-lifecycle-hooks canUseTool-permission-callback streaming-partial-messages multi-turn-session-management structured-output-json-schema cortex
130-snowflake-demo-sql.md tier=High kw=demo-sql per-schema-isolation rerunnable-demos progress-indicators inline-educational-comments schema-based-file-naming ci/cd
131-snowflake-demo-creation.md tier=Low kw=Faker-seeded-generation GENERATOR()-table-function offline-fallback-resilience DemoScenario-pattern narrative-aligned-correlations progressive-disclosure-UI faker
132-snowflake-demo-modeling.md tier=High kw=Kimball-dimensional-modeling fact-dimension-FK-naming view-taxonomy-prefixes synthetic-data-referential-integrity business-first-column-naming SCD-Type-2-surrogate-keys etl
200-python-core.md tier=Critical ext=.py kw=pyproject.toml toolchain-detection datetime.now(UTC) collections.abc-imports dict-list-annotations pathlib-file-operations
200a-python-validation-gate.md tier=High kw=pre-task-completion-gate ty-vs-mypy-decision zero-tolerance-validation toolchain-specific-validation-commands validation-failure-recovery-sequence pre-commit-hook-automation TOML
200b-python-environment-tooling.md tier=High kw=venv uv-run uvx poetry-run toolchain-detection ModuleNotFoundError-diagnosis fastapi
201-python-lint-format.md tier=High kw=Ruff pyproject.toml-configuration uvx-ruff pydocstyle-D-rules pre-commit-hooks zero-error-validation-gate TOML
202-markup-config-validation.md tier=Medium kw=YAML-syntax-safety configuration-file-linting TOML-validation Taskfile.yml-patterns YAML-anchors-aliases secrets-in-version-control ci/cd
202a-markdown-linting.md tier=Low kw=pymarkdownlnt markdown-linting uvx-pymarkdownlnt .pymarkdown.yml MD013-line-length markdown-automation-integration TOML
203-python-project-setup.md tier=High kw=pyproject.toml hatchling-build-backend uv-dependency-manager __init__.py-package-recognition flat-layout-src-layout editable-install TOML
204-python-docs.md tier=High kw=docstring-conventions PEP-257 Google-style-docstrings NumPy-style-docstrings Ruff-pydocstyle side-effects-documentation TOML
205-python-classes.md tier=Medium kw=dataclass-decorator composition-over-inheritance @property-decorator Protocol-structural-subtyping frozen-immutable-dataclass context-manager-resource pytest
206-python-pytest.md tier=High kw=pytest-fixtures AAA-pattern test-parametrization uv-run-pytest test-isolation flaky-test-protocol TOML
207-python-logging.md tier=High kw=hierarchical-logger-names Rich-console-bridge WebLogHandler-SSE operation-scoped-handler-attachment SUCCESS-prefix-pattern operation-ID-correlation fastapi
210-python-fastapi-core.md tier=High kw=application-factory APIRouter-modular-routing Pydantic-request-response-separation async-def-route-handlers dependency-injection-database-sessions uvicorn-ASGI-server fastapi
210a-python-fastapi-security.md tier=High kw=JWT-authentication bcrypt-password-hashing HTTPBearer-token-validation token-refresh-pairs RBAC-dependency-injection environment-secrets-validation fastapi
210b-python-fastapi-testing.md tier=High kw=TestClient-fixture dependency-overrides pytest-asyncio-configuration test-database-isolation AAA-pattern-enforcement httpx-AsyncClient TOML
210c-python-fastapi-deployment.md tier=High kw=gunicorn-uvicorn-worker multi-stage-docker-build health-check-endpoint non-root-container-user openapi-schema-customization worker-process-configuration ci/cd
210d-python-fastapi-monitoring.md tier=Medium kw=FastAPI-health-endpoints correlation-ID-middleware structured-JSON-logging Redis-caching-layer MetricsMiddleware-performance-tracking sensitive-data-sanitization fastapi
210e-python-fastapi-security-hardening.md tier=Medium kw=FastAPI-hardening CORS-middleware slowapi-rate-limiting security-headers-middleware parameterized-queries Pydantic-field-validators fastapi
220-python-typer-cli.md tier=High kw=Typer-CLI typer.Argument typer.Option exit-code-handling console-script-entry-points Rich-terminal-output TOML
220a-python-typer-config.md tier=Medium kw=Typer-CLI-configuration pydantic-settings-integration configuration-precedence-chain environment-variable-prefix CLI-option-overrides TOML-config-file-loading TOML
220b-python-typer-testing.md tier=Medium kw=CliRunner ANSI-escape-suppression Typer-command-testing exit-code-verification CLI-mock-dependencies async-command-testing pytest
220c-python-typer-rich.md tier=Medium kw=Rich-library Typer-Rich-integration shared-console-module dual-console-stdout-stderr color-detection-environment Live-progress-display pytest
221-python-htmx-core.md tier=High kw=hx-request-header-detection partial-HTML-rendering HX-Trigger-response-headers CSRF-token-injection swap-strategy-selection hypermedia-driven-navigation fastapi
221a-python-htmx-templates.md tier=High kw=Jinja2-partials HTMX-fragment-rendering template-directory-organization conditional-HTMX-detection reusable-template-macros partial-inheritance-anti-patterns fastapi
221b-python-htmx-flask.md tier=Medium kw=Flask-HTMX-extension blueprint-organization-htmx Flask-WTF-csrf-htmx Flask-Login-htmx-redirect flask-route-decorators-htmx flask-session-htmx flask
221c-python-htmx-fastapi.md tier=Medium kw=FastAPI-async-routes Jinja2Templates-FastAPI HTMX-dependency-injection BackgroundTasks-polling Pydantic-form-validation htmx-fastapi-integration fastapi
221d-python-htmx-testing.md tier=High kw=htmx-endpoint-testing HX-Request-header HX-Trigger-response-headers partial-HTML-assertions htmx_client-fixture OOB-swap-testing fastapi
221e-python-htmx-patterns.md tier=Medium kw=HTMX-CRUD server-side-form-validation search-debounce-autocomplete progressive-enhancement-fallback inline-editing-outerHTML-swap HX-Trigger-response-headers fastapi
221f-python-htmx-integrations.md tier=Low kw=Alpine.js-HTMX _hyperscript-inline-behavior CSS-framework-styling chart-library-reinitialization htmx:afterSwap-event-hooks frontend-library-lifecycle htmx
221g-python-htmx-sse.md tier=High kw=HTMX-SSE-extension Alpine.js-SSE-manager event-type-matching thread-safe-SSE-publishing EventSourceResponse SSE-connection-limits fastapi
221h-python-htmx-fastapi-auth.md tier=Medium kw=FastAPI-HTMX-authentication HX-Redirect-header SSE-streaming-FastAPI call_soon_threadsafe-queue Starlette-WTF-CSRF HTTPBearer-dependency-injection fastapi
221i-python-htmx-patterns-advanced.md tier=Medium kw=infinite-scroll SSE-polling modal-drawer multi-step-wizard revealed-trigger htmx-ext-sse fastapi
230-python-pydantic.md tier=High kw=BaseModel-inheritance Field-constraints @field_validator-decorator @model_validator-decorator ConfigDict-settings discriminated-unions TOML
230a-python-pydantic-settings.md tier=Medium kw=pydantic-settings BaseSettings environment-variable-loading SettingsConfigDict nested-settings-delimiter startup-validation fastapi
230b-python-pydantic-integration.md tier=Medium kw=model_dump-serialization TypeAdapter-batch-validation FastAPI-response_model ORM-from_attributes SecretStr-field-exclusion model_json_schema-generation fastapi
240-python-faker.md tier=Low kw=Faker-library seed_instance custom-providers deterministic-test-data unique-attribute locale-fallback TOML
240a-python-faker-testing.md tier=Low kw=faker-pytest-fixtures seed_instance-parallel Factory-Boy-SubFactory pytest-xdist-worker-seeding conftest-fixture-hierarchy unique-value-cleanup TOML
240b-python-faker-advanced.md tier=Low kw=faker-localization custom-provider BaseProvider-extension DynamicProvider-runtime streaming-generator-memory faker-caching-optimization TOML
250-python-flask.md tier=High kw=application-factory Flask-blueprints Flask-SQLAlchemy CSRF-protection Jinja2-templates Gunicorn-deployment flask
251-python-datetime-core.md tier=High kw=datetime-type-conversion timezone-localize-convert datetime.now(UTC) pd.Timestamp-compatibility date-parsing-format-specification epoch-timestamp-unit-conversion pandas
251a-python-datetime-advanced.md tier=Medium kw=timedelta-vs-dateoffset calendar-aware-arithmetic vectorized-datetime-operations business-day-calculations time-series-downsampling relativedelta-age-calculation pandas
251b-python-datetime-integration.md tier=Medium kw=parameterized-queries-datetime streamlit-date-input SQL-injection-datetime plotly-datetime-axis datetime-display-formatting allowlist-validation-SQL-keywords fastapi
252-python-pandas-core.md tier=High kw=pandas-vectorization SettingWithCopyWarning .loc-.iloc-indexing pandas-method-chaining np.where-np.select-conditional iterrows-apply-anti-patterns pandas
252a-python-pandas-performance.md tier=Medium kw=pandas-dtype-optimization categorical-data-memory groupby-aggregation-efficiency merge-validation-indicator eval-query-expressions chunked-file-processing pandas
252b-python-pandas-io-integration.md tier=Medium kw=streamlit-cache_data plotly-aggregation interactive-dataframe-filtering csv-download-button dtype-optimization-caching pandas-streamlit-plotly pandas
300-bash-scripting-core.md tier=High kw=set--euo-pipefail variable-quoting trap-cleanup-handlers shellcheck-static-analysis local-function-variables bash-script-structure taskfile
300a-bash-security.md tier=High kw=bash-input-sanitization command-injection-prevention shell-path-traversal bash-credential-storage shell-script-permissions eval-alternatives
300b-bash-testing-tooling.md tier=Medium kw=ShellCheck Bats bash-unit-testing pre-commit-hooks debug-mode-implementation CI/CD-shell-validation ci/cd
300c-bash-security-advanced.md tier=Medium kw=privilege-dropping ulimit-resource-constraints URL-validation-localhost-blocking audit-logging-security-events parameter-expansion-whitelisting malicious-payload-testing ci/cd
300d-bash-advanced.md tier=Medium kw=associative-arrays parameter-expansion shellcheck debug-mode bash-built-ins usage-documentation ci/cd
310-zsh-scripting-core.md tier=Medium kw=z-shell-scripting parameter-expansion-modifiers emulate-setopt 1-indexed-arrays extended-glob-patterns namespace-pollution-prevention
310a-zsh-advanced-features.md tier=Low kw=zsh-modules async-prompt-operations completion-caching zprof-startup-profiling glob-qualifiers parameter-expansion-back-references
310b-zsh-compatibility.md tier=Low kw=bash-vs-zsh emulate-mode array-indexing-differences POSIX-compliance shell-detection setopt-explicit ci/cd
310c-zsh-compatibility-platforms.md tier=Low kw=cross-shell-testing platform-compatibility environment-detection performance-benchmarking BSD-vs-GNU multi-shell-project-organization
310d-zsh-completion-prompt.md tier=Low kw=compinit zstyle-completion add-zsh-hook precmd-preexec vcs_info async-prompt
350-docker-core.md tier=Medium kw=multi-stage-builds image-digest-pinning non-root-container-user layer-caching-optimization SBOM-generation BuildKit-mount-cache ci/cd
351-podman-core.md tier=Medium kw=rootless-containers Containerfile-authoring Quadlet-systemd daemonless-architecture pod-orchestration Buildah-image-building SELinux-volume-labeling
351a-podman-examples.md tier=Low kw=Buildah-multi-stage Quadlet-systemd rootless-numeric-UID SBOM-generation-script Containerfile-healthcheck versioned-image-tags ini
420-javascript-core.md tier=High kw=ESM-modules immutable-array-methods node:test-runner Biome-linter JSDoc-type-annotations Object.groupBy
421-javascript-alpinejs-core.md tier=Medium kw=x-data-directive declarative-directives magic-properties Alpine.data-registration x-cloak-FOUC-prevention progressive-enhancement htmx
421a-javascript-alpinejs-advanced.md tier=Low kw=Alpine.store $dispatch-cross-component lifecycle-hooks-init-destroy x-transition-animations Alpine.js-DevTools-debugging x-effect-reactive-side-effects htmx
424-javascript-docs.md tier=High kw=JSDoc-type-annotations eslint-plugin-jsdoc @ts-check-validation @param-@returns-tags @typedef-custom-types JavaScript-API-documentation
430-typescript-core.md tier=High kw=strict-mode-enforcement Zod-runtime-validation type-inference-over-annotation enum-namespace-forbidden satisfies-operator discriminated-union-patterns
434-typescript-docs.md tier=High kw=TSDoc eslint-plugin-jsdoc TypeScript-documentation type-self-documenting semantic-documentation public-API-documentation
440-react-core.md tier=High kw=feature-based-architecture TanStack-Query RSC-server-components Zustand-client-state named-exports-components shadcn-Tailwind-patterns tsx
440a-react-anti-patterns.md tier=Medium kw=error-boundary hydration-mismatch useEffect-cleanup TanStack-Query-error use-client-directive query-cache-gcTime tsx
441-react-backend.md tier=High kw=FastAPI-React-integration httpOnly-cookie-authentication TanStack-Query-backend-communication CORS-middleware-configuration Python-first-full-stack JWT-refresh-token-rotation fastapi
500-frontend-htmx-core.md tier=Low kw=hx-get hx-swap hx-trigger htmx-lifecycle-events hypermedia-driven-UI progressive-enhancement-fallbacks htmx
501-frontend-browser-globals-collisions.md tier=High kw=browser-globals-collision window.history-shadowing htmx:historyRestore Alpine.js-component-namespacing implicit-global-prevention inline-script-scoping htmx
502-frontend-revealjs-core.md tier=Medium kw=reveal.js-6.0.0 slide-markup-hierarchy code-highlighting-data-trim plugin-registration-ESM fragments-auto-animate speaker-notes-view theme-CSS-custom-properties
600-golang-core.md tier=High kw=go.mod idiomatic-Go goroutines-channels golangci-lint table-driven-tests error-wrapping-fmt.Errorf Go
600a-golang-patterns.md tier=Low kw=http.Server-timeouts graceful-shutdown middleware-chain-composition database-connection-pooling context-aware-queries signal-handling-SIGTERM taskfile
800-project-changelog.md tier=Medium kw=CHANGELOG.md Keep-a-Changelog Conventional-Commits-style Unreleased-section changelog-entry-consolidation release-notes-workflow ci/cd
801-project-readme.md tier=Medium kw=README.md-structure quick-start-commands progressive-disclosure badge-validation clean-environment-testing author-contact-section ci/cd
802-project-contributing.md tier=Medium kw=pull-requests conventional-commits CONTRIBUTING.md changelog-discipline rule-authoring pre-commit-validation cortex
803-project-git-workflow.md tier=Medium kw=conventional-commits feature-branch-workflow conventional-branch-naming CHANGELOG.md-updates pre-commit-validation-gate pull-request-workflow cortex
804-project-documentation.md tier=Medium kw=docs-folder-structure community-health-files-placement ARCHITECTURE.md-location relative-path-cross-references ADR-folder-conventions GitHub-Pages-deployment
805-technical-writing-style.md tier=Medium kw=technical-writing-style sentence-case-headings inclusive-language active-voice-prose fenced-code-block-language-identifier descriptive-link-text
806-workbench-folder-policy.md tier=Low kw=.workbench/-folder short-life-assets promotion-protocol filesystem-hygiene workbench-mirroring gitignore-workbench
810-cli-design-core.md tier=Medium kw=clig.dev-principles TTY-detection stdout-stderr-separation destructive-operation-confirmation machine-readable-output-modes XDG-Base-Directory typer
820-taskfile-automation.md tier=Medium kw=Taskfile.yml task-runner-automation uvx-ephemeral-tools command-auto-detection cross-platform-task-portability pipefail-error-propagation ci/cd
820a-taskfile-advanced-patterns.md tier=Low kw=taskfile-includes categorized-help-output subtask-file-organization cross-platform-task-guards task-namespaces AI-agent-task-discovery ci/cd
821-makefile-automation.md tier=Medium kw=GNU-Make make-target .PHONY-declaration self-documenting-help uv-uvx-integration tool-auto-detection ci/cd
821a-makefile-advanced-patterns.md tier=Low kw=categorized-help makefile-conditionals variable-assignment-operators makefile-include-directives platform-detection AI-agent-integration ci/cd
920-data-science-analytics.md tier=High kw=snowpark-dataframe model-registry-versioning feature-engineering-leakage SHAP-explainability SQL-aggregation-over-loops pandas-NaN-handling uncertainty-quantification-intervals
930-data-governance-quality.md tier=Medium kw=expectation-suites schema-evolution metric-definitions-catalog data-drift-monitoring quality-gates-automation incident-response-procedures ci/cd
940-business-analytics.md tier=High kw=WCAG-accessibility-compliance KPI-visualization data-storytelling-narrative ethical-visualization-standards snowsight
950-dbt-core.md tier=High kw=dbt-project-object EXECUTE-DBT-PROJECT profiles.yml-snowflake snow-dbt-deploy dbt-workspaces dbt-external-access-integration ci/cd
951-create-dbt-semantic-view.md tier=High kw=dbt_semantic_view-package semantic_view-materialization cortex-analyst-integration SEMANTIC_VIEW()-function primary-key-constraints dimensions-metrics-relationships ci/cd
