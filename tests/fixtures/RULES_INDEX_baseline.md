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

000-global-core.md tier=Critical kw=workflow safety confirmation validation surgical-edits minimal-changes prompt-engineering task-list context-window professional-communication
001-memory-bank.md tier=Critical kw=memory-bank context session-recovery progress-tracking compaction rapid-recovery
002-rule-governance.md tier=Critical dir=rules/ kw=rule-governance schema metadata-requirements validation schema-compliance rule-structure semantic-discovery rules_index descriptive-headings design-priorities agent-optimization skill-governance
002a-rule-creation.md tier=High kw=rule-creation workflow step-by-step-guide naming-conventions metadata-setup v3.4-schema validation rule-numbering from-scratch new-rule
002b-rule-update.md tier=High kw=rule-update rule-maintenance versioning ruleversion lastupdated semantic-versioning major minor patch rule-modification keyword-expansion scope-updates metadata-updates changelog-updates
002c-rule-optimization.md tier=High kw=token-budget performance rule-sizing progressive-loading context-window model-limits cost-efficiency caching batch-loading
002d-advanced-rule-patterns.md tier=Medium kw=system-prompt-altitude investigation-first multi-session-workflows parallel-execution heuristics goldilocks-zone context-management state-management
002e-schema-validator-usage.md tier=High kw=validation-errors error-resolution exit-codes command-options output-parsing error-severity critical-errors high-warnings medium-info
002f-schema-validator-advanced.md tier=Medium kw=ci/cd-integration automation-workflow json-parsing programmatic-validation pre-commit-hooks github-actions batch-validation error-automation validation-scripts
002g-agent-optimization.md tier=High kw=llm format token efficiency understanding execution comprehension design patterns priority agent-first
002h-claude-code-skills.md tier=High dir=skills/ kw=skill skills skill.md skill-structure workflows trigger-keywords skill-authoring skill-testing skill-validation input-contracts output-contracts skill-examples yaml-frontmatter mcp-tools third-person
002i-rule-loadtrigger.md tier=Low kw=-
002j-rule-examples.md tier=Medium kw=rule-examples example-files example-schema reference-implementations example-discovery example-validation
002k-model-optimization.md tier=Low kw=model-optimization context-window loading-budget gpt claude gemini token-limits cost-efficiency prompt-caching
002l-skill-advanced-patterns.md tier=Low kw=skill-composition plan-validate-execute orchestrator-skill batch-skill visual-analysis-pattern skill-advanced-patterns visual-analysis orchestrator-worker batch-skills verifiable-outputs intermediate-validation claude-a/b-iteration skill-development toc-guidance solve-dont-punt size-heuristic
002m-agent-format-antipatterns.md tier=Medium kw=anti-pattern ascii-table arrow-character decision-tree passive-voice terminology mermaid horizontal-rule
002n-agent-protocol-reference.md tier=Medium kw=anti-patterns quality-gates task-switch rule-loading failure-modes protocol-reference term-definitions gate-compliance
003-context-engineering.md tier=Critical kw=context-engineering attention-budget context-rot token-efficiency compaction progressive-disclosure sub-agents agentic-search system-prompts right-altitude long-horizon-tasks memory-management state-tracking
003a-long-horizon-tasks.md tier=Medium kw=compaction checkpointing sub-agents structured-notes multi-session context-compression persistent-memory agent-coordination
004-tool-design-for-agents.md tier=High kw=tool-design agent-tools token-efficiency tool-parameters function-calling tool-contracts error-handling minimal-tool-set self-contained-tools llm-friendly-parameters single-responsibility
004a-tool-set-curation.md tier=Medium kw=tool-set-curation minimal-viable-tool-set tool-splitting tool-merging tool-bloat tool-boundaries
004b-tool-output-efficiency.md tier=Medium kw=tool-outputs minimal-output progressive-output context-budget verbose-output
100-snowflake-core.md tier=High ext=.sql kw=sql cte performance cost-optimization query-profile warehouse security governance stages copy-into streams tasks warehouse-creation
100f-snowflake-connection-errors.md tier=High kw=connection-error timeout connection-errors error-classification network-policy authentication vpn error-codes 08001 390114 snowflake.connector databaseerror message-analysis error-detection
101-snowflake-streamlit-core.md tier=High kw=dashboard container-runtime warehouse-runtime navigation multipage session-state config.toml theming st.connection
101a-snowflake-streamlit-visualization.md tier=High kw=st.plotly_chart st.pydeck_chart st.altair_chart dashboard interactive-charts map-visualization chart-types visualization-selection streamlit-plotting
101b-snowflake-streamlit-performance.md tier=High kw=@st.cache_data @st.cache_resource st.fragment null-handling slow-streamlit streamlit-caching optimize-streamlit fix-slow-queries fragment-batch-processing streamlit-performance app-slow loading-data caching-pattern
101c-snowflake-streamlit-security.md tier=High kw=st.secrets sql-injection authentication secure-streamlit protect-app credentials-management api-keys environment-variables secure-deployment input-sanitization rbac-streamlit access-control security-patterns container-runtime warehouse-runtime
101d-snowflake-streamlit-testing.md tier=High kw=test-streamlit-app test-framework test-patterns app-testing ui-testing streamlit-test-suite test-coverage debug-tests testing-strategies
101e-snowflake-streamlit-sql-errors.md tier=Low kw=snowparksqlexception error-messages streamlit-errors snowflake-errors debug-sql-error fix-query-error sql-exception error-troubleshooting query-failed database-error sql-debugging-patterns exception-handling common-sql-errors streamlit-error app-error fix-error
101f-snowflake-streamlit-deployment-errors.md tier=Low kw=deployment-error container-runtime warehouse-runtime eai-error compute-pool stage-upload service-startup troubleshooting runtime-error
101g-snowflake-streamlit-fragments.md tier=Medium kw=st.fragment run_every real-time-progress polling live-updates fragment-pattern auto-refresh streaming monitoring-dashboard
101h-snowflake-streamlit-timeseries.md tier=Low kw=time-series-smoothing data-aggregation resample scada-data high-frequency-data trend-analysis rolling-average ewma exponential-smoothing
101i-snowflake-streamlit-viz-plotly.md tier=Medium kw=plotly plotly-express graph-objects st.plotly_chart scatter line bar histogram heatmap box-plot violin sunburst treemap animations faceting subplots
101j-snowflake-streamlit-viz-pydeck.md tier=Medium kw=pydeck st.pydeck_chart deck.gl 3d-visualization hexagon-layer scatterplot-layer geojson-layer arc-layer heatmap-layer terrain point-cloud webgl geospatial
101k-snowflake-streamlit-viz-altair.md tier=Medium kw=altair vega-lite st.altair_chart declarative-visualization grammar-of-graphics mark_point mark_line mark_bar encoding selection interactive layered-charts
101l-snowflake-streamlit-deployment.md tier=High kw=container-runtime warehouse-runtime deployment pyproject.toml environment.yml compute-pool eai external-access-integration migration
101m-snowflake-streamlit-pydeck-layers.md tier=Low kw=pydeck-layers hexagonlayer scatterplotlayer geojsonlayer arclayer columnlayer heatmaplayer pathlayer terrainlayer pointcloudlayer multi-layer
101n-snowflake-streamlit-migration.md tier=Low kw=warehouse-runtime container-runtime in-place-upgrade live-version environment.yml pyproject.toml get_active_session st.connection runtime-migration bidirectional-migration
102-snowflake-sql-core.md tier=High ext=.sql kw=sql-files file-headers copy-into file_format create-view fully-qualified-names idempotent reserved-characters cli-compatibility on_error join ambiguous-column table-alias
102a-snowflake-sql-automation.md tier=High kw=sql-automation procedure idempotent merge operations multi-environment infrastructure-as-code snowflake-variables production-safe upsert sql-automation deployment-scripts sql-pipeline config-management environment-variables
102b-snowflake-sql-procedures.md tier=High kw=stored-procedure create-procedure udf create-function stored-procedure create-procedure create-function dollar-quoting nested-quotes execute-as execute-immediate owner caller restricted-caller sql-scripting procedure-body
102c-snowflake-sql-reserved-chars.md tier=Low kw=cli-compatibility snow-sql snowsql template-expansion ampersand enable-templating single-quote-escaping jinja2 dbt
102d-snowflake-sql-cicd.md tier=Low kw=ci/cd github-actions makefile deployment-automation environment-variables multi-environment pipeline secrets-management
102e-snowflake-sql-procedure-antipatterns.md tier=Low kw=stored-procedure-anti-patterns dollar-quoting execute-as bind-variables unqualified-names
103-snowflake-performance-tuning.md tier=High kw=optimization slow search-optimization pruning spillage sql-optimization partition-pruning query_history optimize-query fix-slow-query query-bottleneck warehouse-performance micro-partitions clustering
104-snowflake-streams-tasks.md tier=High kw=stream task cdc scheduled-tasks pipeline-automation merge-patterns task-dag after-dependencies task-history create-stream create-task debug-stream task-troubleshooting stream-consumption task-execution-error stream-lag
105-snowflake-cost-governance.md tier=High kw=cost budget billing budget-alerts spend-tracking sql credit_quota warehouse_metering_history object-tagging monitor-credits warehouse-spending cost-alerts credit-limits budget-management resource-monitor tag-enforcement
106-snowflake-semantic-views-core.md tier=High kw=semantic-view semantic-model tables relationships primary-key create-semantic-view sql yaml nlq mapping-syntax
106a-snowflake-semantic-views-advanced.md tier=High kw=semantic-view-advanced validation-rules semantic-model-quality semantic-view-pitfalls debug-semantic-view validation-failures relationship-errors
106b-snowflake-semantic-views-querying.md tier=High kw=semantic-query analyst window-functions dimension-compatibility testing validation tpc-ds semantic_view-function query-patterns
106c-snowflake-semantic-views-integration.md tier=Medium kw=semantic-integration rbac masking-policy row-access-policy cortex-analyst agent-integration semantic-view-security analyst-troubleshooting fix-analyst debug-analyst synonyms natural-language-queries
106d-snowflake-semantic-views-development.md tier=Medium kw=semantic-generator vqr verified-queries generator-workflow iterative-development yaml-semantic-model semantic-model-file onboarding-questions development-workflow verified-query-repository semantic-view-generator
107-snowflake-security-governance.md tier=High kw=rbac grant roles grants secure-views security-policies data-security policy-troubleshooting grant-management data-metric-functions dmf least-privilege create-masking-policy tagging dynamic-grant identifier
108-snowflake-data-loading.md tier=High kw=data-loading copy-into import bulk-loading on_error file_format load-data external-stage internal-stage data-ingestion file-upload copy-error loading-patterns stage-files put-command get-command
109-snowflake-notebooks.md tier=Medium kw=notebook ml reproducible-notebooks nbqa code-quality python debug-notebook notebook-execution notebook-testing notebook-deployment kernel-management cell-execution
109a-snowflake-notebooks-tutorials.md tier=High kw=notebook-tutorial checkpoints learning-objectives pedagogical-design educational-content progressive-learning snowflake-notebooks teaching-point-callouts validation-gates tutorial-structure learning-design educational-notebooks teaching-methodology notebook-education
109b-snowflake-app-deployment-core.md tier=Medium kw=app-deployment create-notebook stages sis deploy-app deployment-pipeline app-publishing deployment-patterns deploy-to-snowflake stage-deployment app-versioning automated-deployment
109c-snowflake-app-deployment-troubleshooting.md tier=Medium kw=deployment-error snowflake-deployment-troubleshooting streamlit-debugging sis-typeerror notebook-deployment-issues deployment-errors stage-file-debugging auto_compress-debugging live_version_location_uri root_location-errors-(legacy) deployment-anti-patterns diagnostic-commands cache-issues
109d-snowflake-notebooks-linting.md tier=Low kw=nbqa notebook-linting ruff code-quality notebook-formatting lint-notebooks notebook-validation
109e-snowflake-notebook-checkpoints.md tier=Low kw=notebook-checkpoint teaching-point checkpoint-validation teaching-point-callouts notebook-validation-gates progress-verification learning-checkpoints note-prefix tutorial-checkpoints
109f-snowflake-notebook-two-approach-pattern.md tier=Low kw=two-approach notebook-approach tutorial-approach approach-comparison two-approach-pattern feature-store-approach simplified-approach production-vs-learning approach-clarification tutorial-approach-selection
109g-snowflake-app-deployment-sql-scripts.md tier=Low kw=deployment-sql put-script put-command remove-command create-notebook create-streamlit upload-script stage-upload sql-deployment-templates snow-stage-copy recursive-upload
109h-snowflake-app-deployment-taskfile.md tier=Low kw=deployment-taskfile deploy-task taskfile-deployment task-automation deployment-tasks task-structure deploy-task upload-task create-task drop-task remove-task deployment-workflow
109i-snowflake-app-deployment-advanced.md tier=Low kw=multi-env-deploy deployment-rollback multi-environment-deployment deployment-rollback deployment-recovery environment-specific-deployment dev-qa-prod-deployment rollback-strategy
109j-snowflake-sis-typeerror-debugging.md tier=Medium kw=sis-typeerror typeerror-bad-argument attributeerror-streamlit sis-debugging auto_compress from-source-path live_version_location_uri root_location-mismatch-(legacy) environment.yml streamlit-version compression-debugging stage-path-mismatch
110-snowflake-model-registry.md tier=Medium kw=model-registry ml-model model-governance model-logging model-inference rbac model-privileges register-model log-model model-management ml-registry model-tracking model-metadata deploy-model model-lineage
110a-snowflake-model-monitor.md tier=Medium kw=model-monitor ml-observability model-monitor drift-detection baseline-data scoring-data ml-observability model-performance-monitoring prediction-drift schema-alignment enable_monitoring
110b-snowflake-model-registry-operations.md tier=Low kw=model-registry-operations model-cost-governance model-queries model-administration model-compliance model-audit model-maintenance resource-monitor-ml model-integration ci/cd-models notebook-models
111-snowflake-observability-core.md tier=High kw=log_level trace_level metric_level show-parameters opentelemetry system-views-vs-telemetry logging tracing debug-observability event-table-queries observability-patterns configure-telemetry
111a-snowflake-observability-logging.md tier=High kw=observability-logging debug info warn error fatal conditional-logging sampling tight-loop-logging standard-logging-libraries log-volume-control cost-management log-configuration log-handlers
111b-snowflake-observability-tracing.md tier=High kw=distributed-tracing span-attributes trace_id performance-analysis metrics-collection cpu_usage memory_usage telemetry.create_span opentelemetry nested-spans tracing-patterns span-creation trace-analysis distributed-traces
111c-snowflake-observability-monitoring.md tier=High kw=metrics copy-history task-history dynamic-tables cost-management troubleshooting performance-analysis monitor-queries telemetry-volume sql
111d-snowflake-observability-snowsight.md tier=Low kw=snowsight-monitoring ai-observability snowsight-monitoring traces-and-logs query-history-ui copy-history task-history dynamic-tables-monitoring ai-observability cortex-ai-monitoring token-tracking ai-cost-attribution llm-evaluation generative-ai-tracing
112-snowflake-snowcli.md tier=Medium file=snowflake.yml kw=snowcli snowflake-cli automation deployment-automation snowflake.yml profiles json-output pat-authentication wif-authentication project-definition connection-management stage-to-stage-copy streamlit-deploy from-deployment live-version
113-snowflake-feature-store.md tier=Medium kw=feature-store ml-features feature-views entity-modeling ml-pipeline asof-join point-in-time-correctness dynamic-tables feature-versioning create-features feature-catalog feature-pipeline feature-discovery feature-registry feature-lineage
113a-snowflake-feature-store-patterns.md tier=Low kw=feature-store-patterns feature-store-anti-patterns data-leakage point-in-time-correctness feature-versioning-mistakes non-deterministic-features feature-view-costs feature-store-governance
113b-snowflake-feature-store-engineering.md tier=Low kw=feature-engineering aggregation-features time-based-features recency-features frequency-features monetary-features velocity-features rfm-features windowed-aggregations derived-features
114-snowflake-cortex-aisql.md tier=High kw=aisql cortex-aisql cortex-aisql ai_complete ai_classify ai_extract ai_sentiment ai_summarize embeddings llm-functions batching token-costs text-generation classification sentiment-analysis summarization
114a-snowflake-cortex-ai-transcribe.md tier=Medium kw=ai_transcribe transcribe audio diarization audio-transcription to_file speaker-diarization timestamp_granularity flac mp3 ogg wav webm
115-snowflake-cortex-agents-core.md tier=High kw=agent cortex-agent cortex-agent multi-tool-agents planning-instructions testing troubleshooting semantic-views create-agent debug-agent agent-not-working tool-execution-failed agent-error fix-agent
115a-snowflake-cortex-agents-instructions.md tier=High kw=agent-instructions cortex-agents response-instructions tool-orchestration flagging-logic agent-prompts multi-tool-orchestration tool-selection agent-prompting instruction-patterns agent-planning
115b-snowflake-cortex-agents-operations.md tier=High kw=agent-operations agent-operations agent-security agent-monitoring agent-evaluation agent-costs debug-agent agent-troubleshooting agent-security-policies
115c-snowflake-cortex-agents-testing.md tier=Low kw=agent-testing agent-rbac agent-testing component-testing agent-rbac agent-permissions agent-grants cortex-agent-security test-agent agent-validation agent-role agent-access-control
115d-snowflake-cortex-agents-observability.md tier=Low kw=agent-observability agent-costs agent-observability agent-evaluation agent-cost-management agent-latency agent-health agent-errors debug-agent agent-logs agent-trace cortex-agent-troubleshooting agent-cost-tracking
116-snowflake-cortex-search.md tier=Medium kw=cortex-search embeddings search-index rag agent-tools retrieval ai_embed search-service document-retrieval hybrid-search vector-similarity
117-snowflake-mcp-server.md tier=High kw=mcp mcp-server model-context-protocol snowflake-managed-mcp-server create-mcp-server system_execute_sql cortex_analyst_message cortex_search_service_query cortex_agent_run tools/list tools/call initialize oauth security-integration rbac pat
118-snowflake-cortex-rest-api.md tier=High kw=cortex-api rest-api idempotency rate-limits complete-endpoint embed-endpoint exponential-backoff cortex-api response-format retry-logic cost-controls batch-vs-interactive
118a-snowflake-cortex-rest-api-streaming.md tier=High kw=cortex-api-streaming cortex-auth sse server-sent-events streaming-response event-stream pat oauth jwt authentication-token token-type response-format sseclient cortex-agent-sse streaming-parsing
119-snowflake-warehouse-management.md tier=High kw=high-memory-warehouse warehouse-tagging auto-suspend gen-2 snowpark-optimized warehouse-edition resource-monitors create-warehouse warehouse-configuration warehouse-types warehouse-cost size-warehouse max_query_performance_level query_throughput_multiplier system$bulk_update_wh create-adaptive-warehouse
120-snowflake-spcs.md tier=High kw=spcs compute-pools oci-images service-spec container-deployment service-logs platform-events instance-family gen_x64_g2 mem_x64_g2 current-generation gpu-l40s gpu-rtx-pro-6000
121-snowflake-snowpipe.md tier=High kw=snowpipe streaming auto-ingest rest-api file-based-ingestion event-notifications copy-into pipe-management serverless-ingestion
121a-snowflake-snowpipe-streaming.md tier=High kw=snowpipe-streaming high-performance-streaming classic-streaming row-level-ingestion low-latency-ingestion sub-second-latency real-time-ingestion streaming-architecture streaming-channels
121b-snowflake-snowpipe-monitoring.md tier=Medium kw=snowpipe-monitoring pipe-costs snowpipe-monitoring cost-management load-history pipe-usage streaming-monitoring channel-status credits-tracking performance-metrics cost-optimization metering-history monitoring-queries
121c-snowflake-snowpipe-troubleshooting.md tier=Medium kw=snowpipe-troubleshooting pipe-errors snowpipe-troubleshooting debugging error-resolution pipe-errors streaming-errors connection-failures schema-errors offset-tracking latency-issues duplicate-data authentication-errors channel-errors
121d-snowflake-snowpipe-streaming-sdk.md tier=High kw=snowpipe-streaming-sdk snowpipe-streaming-sdk java-sdk python-sdk streaming-client channel-management offset-tracking schema-evolution streaming-ingestion-code snowflakestreamingingestclient
121e-snowflake-snowpipe-troubleshooting-advanced.md tier=Low kw=snowpipe-offset snowpipe-streaming-debug snowpipe-checklist offset-tracking batch-performance data-validation debugging-checklists channel-troubleshooting exactly-once-semantics
121f-snowflake-snowpipe-monitoring-alerts.md tier=Medium kw=snowpipe-alerts pipe-alerts pipe-cost-optimization snowpipe-alerts pipe-error-alerts channel-stall-alerts cost-optimization file-size-optimization streaming-optimization alert-thresholds system$send_email monitoring-tasks performance-metrics
122-snowflake-dynamic-tables.md tier=High kw=dynamic-table incremental automatic-pipelines downstream full warehouse-sizing data-freshness dynamic-table-lag refresh-frequency pipeline-automation
123-snowflake-object-tagging.md tier=High kw=tag metadata cost-attribution resource-tagging governance-tags masking-policies row-access-policies tag-lineage tag-management
124-snowflake-data-quality-core.md tier=High kw=data-quality validation data-profiling expectations quality-checks null-detection uniqueness-validation freshness-monitoring anomaly-detection automated-monitoring event-tables create-dmf quality-monitoring data-expectations
124a-snowflake-data-quality-custom.md tier=Medium kw=custom-quality-check quality-assertions custom-metrics validation-functions create-custom-dmf custom-quality-checks business-rule-validation custom-expectations quality-functions udf-for-quality validation-logic custom-quality-metrics custom-validation
124b-snowflake-data-quality-operations.md tier=High kw=dmf-operations quality-monitoring remediation rbac privilege-requirements automated-monitoring quality-alerts schedule-dmf quality-event-tables quality-alerting dmf-results quality-workflows dmf-rbac quality-notifications remediation-workflows
125-snowflake-role-introspection.md tier=Medium kw=role introspection access account-roles database-roles show-grants role-introspection rbac python-automation error-000906 too-many-qualifiers grants-inspection programmatic-rbac
126-snowflake-cortex-code-agent-sdk.md tier=High kw=agent-sdk mcp-server mcp-servers cortex-code agent-hooks structured-output streaming-output streaming-input system-prompts agent-typescript agent-python
130-snowflake-demo-sql.md tier=High kw=demo workshop quickstart demo-sql teardown progress-indicators rerunnable-demos create-or-replace educational-sql demo-patterns setup-scripts customer-learning per-schema-isolation inline-documentation current_user identifier
131-snowflake-demo-creation.md tier=Low kw=demo-creation synthetic-data demo-creation synthetic-data realistic-demos data-generation demo-applications narrative-design reproducible-data progressive-disclosure streamlit data-visualization
132-snowflake-demo-modeling.md tier=High kw=data-modeling dimensional-model kimball naming-conventions dimensional-modeling fact-tables dimension-tables foreign-keys view-taxonomy data-generation backward-compatibility surrogate-keys
200-python-core.md tier=Critical ext=.py,.pyi file=pyproject.toml kw=python uv ruff pyproject.toml dependency-management virtual-environments pytest uv-run uvx ty type-checking mypy type-hints
200a-python-validation-gate.md tier=High kw=validate type-check lint type-checking linting formatting pytest ruff ty mypy pre-task gate syntax
200b-python-environment-tooling.md tier=High kw=venv virtual-environment uv poetry virtual-environment pip pipenv uvx tool-isolation modulenotfounderror environment-setup dependency-management
201-python-lint-format.md tier=High kw=ruff formatting code-quality style-checking lint-errors ruff-check ruff-format pyproject.toml-configuration black flake8
202-markup-config-validation.md tier=Medium ext=.yml,.yaml,.toml file=Taskfile.yml kw=yaml configuration-files yaml-syntax parsing-errors indentation anchors aliases markdown markdown-linting pymarkdownlnt toml environment-files
202a-markdown-linting.md tier=Low ext=.md kw=markdown pymarkdownlnt documentation markup-validation
203-python-project-setup.md tier=High file=pyproject.toml kw=setup bootstrap python-packaging setup.py pyproject.toml dependencies package-distribution __init__.py hatchling uv flat-layout src-layout
204-python-docs.md tier=High kw=docstring comments python-docstrings pydocstyle ruff-doc-rules google-style numpy-style pep-257 semantic-depth side-effects
205-python-classes.md tier=Medium kw=class oop dataclass python-classes inheritance dataclasses @property class-design encapsulation composition protocol abc type-hints
206-python-pytest.md tier=High kw=test coverage fixtures parametrization mocking test-organization aaa-pattern test-markers uv-run-pytest unit-test
207-python-logging.md tier=High kw=log logger python-logging handlers formatters log-levels webloghandler rich-console sse-streaming operation-id thread-safety log-hierarchy log-propagation
210-python-fastapi-core.md tier=High kw=api rest async rest-api pydantic dependency-injection routing request-validation response-models apirouter uvicorn async-def application-factory
210a-python-fastapi-security.md tier=High kw=oauth jwt rbac fastapi-security authentication oauth2 api-keys bcrypt httpbearer role-based-access-control token-refresh password-hashing
210b-python-fastapi-testing.md tier=High kw=fastapi-testing fastapi-testing testclient pytest-asyncio api-tests mocking aaa-pattern async-testing
210c-python-fastapi-deployment.md tier=High kw=fastapi-deployment fastapi-deployment uvicorn gunicorn asgi docker health-checks multi-stage-build openapi api-documentation
210d-python-fastapi-monitoring.md tier=Medium kw=fastapi-monitoring fastapi-monitoring health-checks logging metrics caching redis structured-logging health-endpoints correlation-ids
210e-python-fastapi-security-hardening.md tier=Medium kw=cors rate-limit security-headers fastapi-hardening csrf rate-limiting security-headers input-validation sql-injection xss-prevention trusted-hosts production-security
220-python-typer-cli.md tier=High kw=cli-development command-line-interface click argument-parsing typer.argument typer.option rich-console exit-codes
220a-python-typer-config.md tier=Medium kw=cli-config pydantic-settings cli-configuration pydantic-settings environment-variables cli-options
220b-python-typer-testing.md tier=Medium kw=cli-testing clirunner cli-testing ansi-escape-codes no_color cli-integration-testing mock
220c-python-typer-rich.md tier=Medium kw=rich console progress-bar console-output progress-bars live-display color-detection stderr dual-console
221-python-htmx-core.md tier=High kw=hypermedia hateoas hx-request hx-trigger partial-rendering sse websockets csrf xss http-headers swap-strategies oob-swaps response-patterns
221a-python-htmx-templates.md tier=High kw=htmx-templates jinja2 partials fragments template-composition conditional-rendering htmx-templates template-organization reusable-components template-context
221b-python-htmx-flask.md tier=Medium kw=htmx-flask flask-htmx blueprints flask-login session-management flask-routes flask-templates flask-csrf flask-extensions request-context
221c-python-htmx-fastapi.md tier=Medium kw=htmx-fastapi async dependency-injection background-tasks fastapi-templates starlette pydantic async-routes
221d-python-htmx-testing.md tier=High kw=integration-tests fixtures mocking header-validation html-assertions test-client htmx-testing
221e-python-htmx-patterns.md tier=Medium kw=crud forms validation progressive-enhancement search autocomplete inline-editing
221f-python-htmx-integrations.md tier=Low kw=alpinejs hyperscript tailwind bootstrap css-frameworks icon-libraries chartjs frontend-libraries client-side-enhancements htmx-integration javascript-frameworks
221g-python-htmx-sse.md tier=High kw=server-sent-events alpine.js eventsource real-time streaming live-updates push-notifications event-types sse-manager
221h-python-htmx-fastapi-auth.md tier=Medium kw=htmx-fastapi-auth htmx-jwt htmx-sse-fastapi htmx-csrf-fastapi jwt sse csrf starlette-wtf oauth2 server-sent-events
221i-python-htmx-patterns-advanced.md tier=Medium kw=htmx-scroll htmx-modal htmx-wizard htmx-polling infinite-scroll sse polling modals drawers wizard multi-step real-time lazy-loading
230-python-pydantic.md tier=High kw=validation basemodel data-validation models field-validation field validator model_validator emailstr
230a-python-pydantic-settings.md tier=Medium kw=env-file app-config basesettings environment-variables configuration env_file nested-settings config-precedence
230b-python-pydantic-integration.md tier=Medium kw=serialization model-dump type-adapter json-schema fastapi-integration database-orm typeadapter performance testing model_dump secretstr
240-python-faker.md tier=Low kw=test-data mock test-data-generation fake-data providers synthetic-data seeding deterministic-testing python-testing
240a-python-faker-testing.md tier=Low kw=faker-fixtures factory-boy seeded-data pytest-fixtures factory-boy seeded-testing deterministic-data pytest-xdist subfactory
240b-python-faker-advanced.md tier=Low kw=locale custom-provider faker-performance localization custom-providers baseprovider performance-optimization batch-generation caching multi-language
250-python-flask.md tier=High kw=web blueprints flask-sqlalchemy templates routing application-factory
251-python-datetime-core.md tier=High kw=datetime timezone utc timedelta tz_localize tz_convert datetime.now(utc) pd.timestamp type-conversion zoneinfo
251a-python-datetime-advanced.md tier=Medium kw=timedelta dateoffset date-arithmetic time-series datetime-arithmetic business-days calendar-math relativedelta performance downsampling resample
251b-python-datetime-integration.md tier=Medium kw=datetime-sql streamlit-datetime plotly-datetime datetime-sql parameterized-queries streamlit-date-input plotly-datetime datetime-display date-formatting sql-injection
252-python-pandas-core.md tier=High kw=dataframe vectorization settingwithcopywarning method-chaining loc iloc np.where np.select apply iterrows
252a-python-pandas-performance.md tier=Medium kw=pandas-performance groupby merge memory-optimization pandas-performance memory-optimization dtype categorical join eval query chunking sparse thread-safety multiprocessing
252b-python-pandas-io-integration.md tier=Medium kw=streamlit-pandas plotly-pandas pandas-io cache-data pandas-streamlit pandas-plotly cache_data dataframe-caching interactive-filtering csv-download aggregate-visualization data-loading
300-bash-scripting-core.md tier=High ext=.sh,.bash,.zsh kw=shell-scripting set--euo-pipefail error-handling strict-mode functions variables script-structure trap exit-codes shellcheck input-validation
300a-bash-security.md tier=High kw=bash-security shell-security bash input-validation command-injection path-security secure-shell-scripts sanitization permissions privilege-escalation secrets-management
300b-bash-testing-tooling.md tier=Medium kw=bash-testing bats shellcheck shell-script-testing ci/cd debugging static-analysis linting
300c-bash-security-advanced.md tier=Medium kw=bash-security-advanced privilege-management audit-logging bash privilege-management network-security audit-logging resource-limits url-validation security-testing parameter-expansion file-permissions
300d-bash-advanced.md tier=Medium ext=.sh,.bash kw=bash associative-arrays performance code-style shellcheck debugging documentation security parameter-expansion
310-zsh-scripting-core.md tier=Medium ext=.zsh kw=z-shell zsh-features arrays functions oh-my-zsh emulate setopt parameter-expansion globbing
310a-zsh-advanced-features.md tier=Low ext=.zsh kw=zsh-advanced modules advanced-features performance-optimization parameter-expansion globbing autoload scripting caching memoization
310b-zsh-compatibility.md tier=Low ext=.zsh kw=zsh-compatibility shell-compatibility bash-vs-zsh portable-scripts cross-shell migration emulate posix-compliance shell-detection
310c-zsh-compatibility-platforms.md tier=Low ext=.zsh kw=zsh-platform zsh-testing shell-testing multi-shell environment-detection platform-compatibility performance-benchmarking bsd-vs-gnu cross-shell-testing
310d-zsh-completion-prompt.md tier=Low ext=.zsh kw=zsh-completion zsh-prompt completion-system compinit zstyle hooks precmd preexec prompt prompt_subst vcs_info async-prompt
350-docker-core.md tier=Medium file=Dockerfile,docker-compose.yml,docker-compose.yaml kw=docker container dockerfile containers multi-stage-builds layer-caching image-optimization docker-compose buildkit distroless security-scanning sbom non-root
351-podman-core.md tier=Medium file=Containerfile,podman-compose.yml,podman-compose.yaml kw=podman buildah containerfile containers rootless-containers podman-compose pods daemonless systemd quadlet non-root security-scanning sbom
351a-podman-examples.md tier=Low kw=podman-examples containerfile-example buildah-example quadlet-example podman-build-script
420-javascript-core.md tier=High ext=.js,.jsx,.mjs,.cjs kw=javascript es2024 esm node.js jsdoc biome node:test immutability async/await functional-programming
421-javascript-alpinejs-core.md tier=Medium kw=alpine alpine.js reactivity x-data x-bind x-on x-model x-show x-if magic-properties $el $refs declarative progressive-enhancement lightweight
421a-javascript-alpinejs-advanced.md tier=Low kw=alpinejs-advanced alpine-stores alpine-plugins alpine.js stores plugins transitions x-teleport $dispatch custom-directives sse lifecycle error-recovery
424-javascript-docs.md tier=High ext=.js,.mjs kw=jsdoc comments eslint-plugin-jsdoc type-annotations
430-typescript-core.md tier=High ext=.ts,.tsx kw=typescript zod strict-mode type-inference union-types satisfies generics utility-types matt-pocock total-typescript
434-typescript-docs.md tier=High ext=.ts,.tsx kw=tsdoc comments eslint-plugin-jsdoc type-documentation
440-react-core.md tier=High ext=.jsx,.tsx kw=react next.js rsc tailwind zustand tanstack-query shadcn feature-based typescript vitest testing-library debug-hooks fix-react-error component-rendering
440a-react-anti-patterns.md tier=Medium kw=error-boundary hydration error-recovery suspense errorboundary useeffect use-client resource-exhaustion cleanup unmount abortcontroller
441-react-backend.md tier=High kw=react-backend react-backend fastapi flask python-api cors jwt authentication api-integration full-stack express-alternative fetch axios tanstack-query-backend next.js-api-routes httponly-cookies
500-frontend-htmx-core.md tier=Low kw=frontend htmx-attributes client-side events css-transitions debugging browser-compatibility hx-get hx-post hx-swap hx-trigger hx-target
501-frontend-browser-globals-collisions.md tier=High kw=browser-globals window-history htmx-history browser-globals javascript-globals window.history htmx-history alpine.js name-collisions reserved-identifiers implicit-globals historyrestore hx-push-url popstate best-practices anti-patterns
502-frontend-revealjs-core.md tier=Medium kw=reveal.js revealjs presentation slides html-presentation slide-deck code-highlighting speaker-notes markdown-slides fragments vertical-slides reveal-themes presentation-framework auto-animate
600-golang-core.md tier=High ext=.go file=go.mod kw=go golang go.mod modules error-handling interfaces goroutines channels testing go-fmt golangci-lint concurrency context defer
600a-golang-patterns.md tier=Low kw=go-http go-server go-middleware go http-server middleware graceful-shutdown timeouts database-patterns production server-configuration
800-project-changelog.md tier=Medium file=CHANGELOG.md kw=changelog changelog-format semantic-versioning release-notes conventional-commits feature-focused-entries unreleased-section scope-patterns git-workflow version-control
801-project-readme.md tier=Medium file=README.md kw=readme documentation project-documentation getting-started setup-instructions badges quick-start contributing license technical-writing author-contact maintainer
802-project-contributing.md tier=Medium file=CONTRIBUTING.md kw=pull-requests code-review contribution-guidelines branching-strategy conventional-commits rule-authoring pr-templates git-workflow
803-project-git-workflow.md tier=Medium kw=git commit commit-message feature-focused-commits branching github pull-requests feature-branches conventional-commits branch-naming
804-project-documentation.md tier=Medium file=docs/,ARCHITECTURE.md kw=docs-folder architecture.md deployment.md adr github-pages community-health-files cross-references link-maintenance documentation-organization
805-technical-writing-style.md tier=Medium ext=.md file=README.md,CONTRIBUTING.md dir=docs/ kw=writing-style voice active-voice sentence-case inclusive-language bias-free serial-comma accessibility microsoft-style
806-workbench-folder-policy.md tier=Low dir=.workbench/ kw=workbench temp scratch file-organization workflow-hygiene project-hygiene short-life in-progress baseline-scripts analyzer-output spike promotion
810-cli-design-core.md tier=Medium kw=command-line command-line-interface clig clig-dev cli-design cli-ux flags stdout isatty tty subcommands cli-help cli-config xdg dry-run machine-readable
820-taskfile-automation.md tier=Medium file=Taskfile.yml kw=deploy ci taskfile taskfile.yml task-runner task portable-tasks error-handling command-detection auto-detection cross-platform uvx
820a-taskfile-advanced-patterns.md tier=Low kw=taskfile-includes taskfile-help categorized-help categorized-help subtask-files includes ai-agent machine-readable cross-platform task-namespaces portable-tasks task-discovery
821-makefile-automation.md tier=Medium file=Makefile kw=make gnu-make make-target phony make-help portable-make make-variables uv uvx make-dependencies make-error-handling make-cleanup
821a-makefile-advanced-patterns.md tier=Low kw=makefile-includes makefile-help makefile-conditional categorized-help makefile-includes conditional-logic ifdef ifeq variable-assignment simply-expanded recursively-expanded platform-detection multi-target ai-agent make-patterns
920-data-science-analytics.md tier=High kw=data-science snowflake pandas snowpark ml model-lifecycle feature-engineering nan-handling model-versioning jupyter
930-data-governance-quality.md tier=Medium kw=data-governance data-quality lineage metadata-management compliance data-catalog great-expectations schema-evolution data-observability incident-response
940-business-analytics.md tier=High kw=dashboards kpis reporting visualization stakeholder-reports metrics snowsight executive-dashboards data-storytelling wcag-accessibility
950-dbt-core.md tier=High kw=dbt-core snowflake dbt-project-object execute-dbt-project profiles.yml workspaces snow-dbt dbt-deploy task-scheduling dbt-monitoring dbt-access-control data-transformation schema-customization generate_schema_name dbt-versioning snow://dbt
951-create-dbt-semantic-view.md tier=High kw=snowflake dbt_semantic_view materialization cortex-analyst yaml semantic-model dbt-models analytics business-intelligence data-modeling
