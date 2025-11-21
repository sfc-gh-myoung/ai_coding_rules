<!-- 
TEMPLATE NOTE: This file uses path templates for deployment flexibility
  
Template Variable: .cursor/rules
  - cursor deployment: .cursor/rules → .cursor/rules (files: *.mdc)
  - copilot deployment: .cursor/rules → .github/copilot/instructions (files: *.md)
  - cline deployment: .cursor/rules → .clinerules (files: *.md)
  - universal deployment: .cursor/rules → rules (files: *.md)

During deployment, .cursor/rules is automatically replaced with the appropriate path
for the target agent type, and file extensions are updated to match agent requirements
(.md → .mdc for Cursor). This ensures rule references point to correct locations.
-->

**Keywords:** rules index, rule discovery, semantic search, agent requested, auto-attach, rule governance, context engineering, tool design

# Rules Index

This index helps agents select the correct rule quickly through semantic keyword matching.

**Rules Location:** `.cursor/rules/`

**How to Use This Index:**
- Browse by category (000=Core, 100=Snowflake, 200=Python, 300=Shell, 400=Docker, 500-900=Domain-specific)
- Search Keywords column for semantic discovery (technologies, patterns, use cases)
- Check Depends On column for prerequisite rules
- Auto-attach rules load automatically; Agent Requested rules load on-demand
- All rules are located in `.cursor/rules/` directory

|| File | Type | Purpose (one line) | Scope | Keywords/Hints | Depends On |
||------|------|---------------------|-------|----------------|------------|
|| `000-global-core.mdc` | Auto-attach | The core, universally-applied operating contract for a reliable and safe workflow. | Universal | PLAN mode, ACT mode, workflow, safety, confirmation, validation, surgical edits, minimal changes, mode violations, prompt engineering, task list, read-only, authorization | — |
|| `001-memory-bank.mdc` | Agent Requested | Universal memory bank principles for AI models to maintain project context and continuity. | Project continuity | memory bank, context, session recovery, project brief, active context, progress tracking, continuity, context rot, attention budget, compaction, context engineering, rapid recovery, signal maximization | `000-global-core.mdc` |
|| `002-rule-governance.mdc` | Agent Requested | Universal standards for creating and maintaining AI coding rule files across all models and editors. | All rules | rule governance, standards, semantic discovery, metadata, keywords, RULES_INDEX, system prompt altitude, right altitude, tool design, universal compatibility, template standards, Quick Start TL;DR, Investigation-First Protocol, Contract section | `000-global-core.mdc` |
|| `003-context-engineering.mdc` | Auto-attach | Comprehensive context management strategies for AI agents, covering attention budgets, context rot, and optimization techniques. | Universal context engineering | context engineering, attention budget, context rot, token efficiency, compaction, progressive disclosure, sub-agents, agentic search, system prompts, right altitude, long-horizon tasks, memory management, state tracking | `000-global-core.mdc` |
|| `004-tool-design-for-agents.mdc` | Agent Requested | Token-efficient tool design patterns for AI agents, focusing on minimal overlap, clear contracts, and promoting efficient agent behaviors. | Agent tool development | tool design, agent tools, token efficiency, tool parameters, function calling, tool overlap, tool contracts, error handling, minimal tool set, self-contained tools, LLM-friendly parameters, single responsibility | `000-global-core.mdc`, `003-context-engineering.mdc` |
|| `100-snowflake-core.mdc` | Agent Requested | Comprehensive rules for all Snowflake tasks, ensuring consistent, performant, and secure solutions. | Snowflake SQL & modeling | Snowflake, SQL, CTE, performance, cost optimization, query profile, warehouse, security, governance, stages, COPY INTO, streams, tasks, DDL fundamentals, object naming, Snowflake best practices, snowflake setup, core patterns, warehouse creation | `000-global-core.mdc` |
|| `101-snowflake-streamlit-core.mdc` | Agent Requested | Core Streamlit patterns for setup, navigation, state management, and deployment modes in Snowflake. | Streamlit apps | Streamlit, Snowflake in Streamlit, SiS, SPCS, st.connection, session state, navigation, multipage, deployment, UI, dashboard, pandas, NaN, NULL handling, streamlit app, create streamlit, debug streamlit, streamlit patterns, session management, connection management | `100-snowflake-core.mdc` |
|| `101a-snowflake-streamlit-visualization.mdc` | Agent Requested | Plotly charts, maps, and dashboard visualization patterns for Streamlit applications. | General | Streamlit charts, Plotly, st.plotly_chart, st.map, visualization, dashboard, interactive charts, map visualization, time series smoothing, data aggregation, create chart, chart types, plotly express, dashboard layout, chart configuration, visualization best practices, streamlit plotting, chart customization | `101-snowflake-streamlit-core.mdc`, `700-business-analytics.mdc` |
|| `101b-snowflake-streamlit-appendix-sql-errors.mdc` | Appendix | Comprehensive SQL error handling patterns and debugging techniques for Streamlit applications with Snowflake, extracted from 101b-streamlit-performance for detailed reference. | General | SQL error handling, SnowparkSQLException, error debugging, user inputs, complex joins, error messages, Streamlit errors, Snowflake errors, debug SQL error, fix query error, SQL exception, error troubleshooting, query failed, database error, SQL debugging patterns, exception handling, error recovery, common SQL errors | `100-snowflake-core.mdc`, `101-snowflake-streamlit-core.mdc`, `101b-snowflake-streamlit-performance.mdc` |
|| `101b-snowflake-streamlit-performance.mdc` | Agent Requested | Performance optimization, caching strategies, and data loading patterns for Streamlit applications. | General | Streamlit performance, @st.cache_data, @st.cache_resource, data loading, query optimization, SQL error handling, st.error, SnowparkSQLException, progress tracking, st.fragment, NULL handling, slow streamlit, streamlit caching, optimize streamlit, fix slow queries, fragment batch processing, NaN error, pandas NULL, KeyError, cache miss | `101-snowflake-streamlit-core.mdc`, `103-snowflake-performance-tuning.mdc` |
|| `101c-snowflake-streamlit-security.mdc` | Agent Requested | Security patterns, input validation, and secrets management for Streamlit applications. | General | Streamlit security, secrets management, st.secrets, input validation, XSS protection, SQL injection, authentication, secure streamlit, protect app, security best practices, credentials management, API keys, environment variables, secure deployment, input sanitization, RBAC streamlit, access control, security patterns | `101-snowflake-streamlit-core.mdc`, `107-snowflake-security-governance.mdc` |
|| `101d-snowflake-streamlit-testing.mdc` | Agent Requested | Testing strategies, AppTest patterns, and debugging workflows for Streamlit applications. | General | Streamlit testing, AppTest, st.testing, unit tests, debugging, test Streamlit app, pytest, test framework, test patterns, app testing, UI testing, test automation, streamlit test suite, integration testing, test coverage, debug tests, test fixtures, testing strategies | `101-snowflake-streamlit-core.mdc`, `206-python-pytest.mdc` |
|| `102-snowflake-sql-demo-engineering.mdc` | Auto-attach | SQL file patterns for Snowflake demos and customer learning environments. | Demo SQL | SQL demos, demo engineering, learning SQL, per-schema setup, teardown, grid_setup.sql, customer_load.sql, inline documentation, progress indicators, rerunnable demos, Snowflake SQL, CREATE OR REPLACE, educational SQL, demo patterns, demo data, setup scripts, demo automation, learning examples | `100-snowflake-core.mdc` |
|| `102a-snowflake-sql-automation.mdc` | Agent Requested | SQL templates and automation patterns for production Snowflake deployments. | General | SQL templates, parameterization, CI/CD, automation, production SQL, idempotent, MERGE, operations, multi-environment, infrastructure as code, Snowflake variables, production-safe, upsert, SQL automation, deployment scripts, SQL pipeline, config management, environment variables | `100-snowflake-core.mdc`, `102-snowflake-sql-demo-engineering.mdc` |
|| `103-snowflake-performance-tuning.mdc` | Agent Requested | Rules for profiling, optimizing, and fine-tuning Snowflake queries and warehouse usage. | Performance | Query profile, slow queries, performance tuning, warehouse sizing, clustering keys, search optimization, pruning, spillage, SQL optimization, Snowflake, partition pruning, QUERY_HISTORY, optimize query, fix slow query, query bottleneck, warehouse performance, micro-partitions, clustering, performance analysis | `100-snowflake-core.mdc` |
|| `104-snowflake-streams-tasks.mdc` | Agent Requested | Guidance for building robust, incremental data pipelines using Snowflake Streams and Tasks. | Pipelines | Streams, Tasks, incremental loading, CDC, change data capture, scheduled tasks, pipeline automation, MERGE patterns, SQL, Snowflake, task DAG, AFTER dependencies, Task History, create stream, create task, debug stream, task troubleshooting, stream consumption, task execution error, stream lag | `100-snowflake-core.mdc` |
|| `105-snowflake-cost-governance.mdc` | Agent Requested | Rules for managing and optimizing Snowflake costs, including resource monitors and workload right-sizing. | Cost governance | Cost optimization, resource monitors, warehouse auto-suspend, query cost, credit usage, budget alerts, spend tracking, Snowflake, SQL, CREDIT_QUOTA, WAREHOUSE_METERING_HISTORY, object tagging, monitor credits, warehouse spending, cost alerts, credit limits, budget management, resource monitor, tag enforcement | `100-snowflake-core.mdc` |
|| `106-snowflake-semantic-views-core.mdc` | Agent Requested | Core DDL syntax and validation rules for creating Snowflake Native Semantic Views using CREATE SEMANTIC VIEW. | Modeling | Snowflake, CREATE SEMANTIC VIEW, FACTS, DIMENSIONS, METRICS, TABLES, RELATIONSHIPS, PRIMARY KEY, validation rules, relationship constraints, semantic view error, InvalidRelationship, create semantic view, debug semantic view, fix semantic view, NLQ, natural language query, granularity rules, mapping syntax, SQL | `100-snowflake-core.mdc` |
|| `106a-snowflake-semantic-views-advanced.mdc` | Agent Requested | Advanced patterns for Snowflake Semantic Views including anti-patterns, validation rules, quality checks, and compliance requirements. | General | Semantic views, validation, anti-patterns, quality checks, compliance, best practices, common mistakes, validation rules, semantic model quality, semantic view pitfalls, debug semantic view, fix semantic view errors, validation failures, relationship errors, mapping errors, quality assurance, semantic view testing, validation patterns | `100-snowflake-core.mdc`, `106-snowflake-semantic-views-core.mdc` |
|| `106b-snowflake-semantic-views-querying.mdc` | Agent Requested | Query patterns and testing strategies for Snowflake Native Semantic Views using SEMANTIC_VIEW() function. | General | SEMANTIC_VIEW query, DIMENSIONS, METRICS, FACTS, WHERE clause, window functions, dimension compatibility, testing, validation, TPC-DS, performance optimization, aliases, granularity, query semantic view, semantic view results, query patterns, result processing, SEMANTIC_VIEW function, query errors, dimension filters | `106-snowflake-semantic-views.mdc` |
|| `106c-snowflake-semantic-views-integration.mdc` | Agent Requested | Integration patterns, governance, and development workflows for Snowflake Native Semantic Views with Cortex Analyst/Agent. | General | Cortex Analyst, Cortex Agent, REST API, RBAC, masking policy, row access policy, governance, Generator workflow, iterative development, synonyms, natural language queries, security, analyst integration, agent integration, semantic view security, NLQ setup, analyst API, agent tools | `106-snowflake-semantic-views.mdc`, `106a-snowflake-semantic-views-querying.mdc` |
|| `107-snowflake-security-governance.mdc` | Agent Requested | Rules for enforcing data security, access control, and data quality monitoring using Snowflake governance features. | Security | Snowflake, masking policies, row access policies, data governance, RBAC, roles, grants, secure views, security policies, access control, data security, policy troubleshooting, grant management, Data Metric Functions, DMF, least privilege, create masking policy, tagging, SQL | `100-snowflake-core.mdc` |
|| `108-snowflake-data-loading.mdc` | Agent Requested | Best practices for loading data into Snowflake using Stages and COPY INTO for bulk loading. | Ingestion | Data loading, COPY INTO, file formats, stages, Parquet, JSON, CSV, bulk loading, ON_ERROR, FILE_FORMAT, load data, external stage, internal stage, data ingestion, file upload, COPY error, loading patterns, stage files, PUT command, GET command | `100-snowflake-core.mdc` |
|| `109-snowflake-notebooks.mdc` | Agent Requested | Rules for building reproducible, secure, and maintainable Jupyter Notebooks in the Snowflake environment. | Notebooks | Snowflake notebooks, Jupyter, Python notebooks, data exploration, ML, reproducible notebooks, nbqa, notebook linting, code quality, Python, Snowflake, create notebook, debug notebook, notebook execution, notebook testing, notebook deployment, kernel management, cell execution | `100-snowflake-core.mdc`, `201-python-lint-format.mdc` |
|| `109a-snowflake-notebooks-tutorials.mdc` | Agent Requested | Tutorial and learning design patterns for Snowflake notebooks, focusing on pedagogical structure, anti-patterns, checkpoints, and progressive learning approaches. | General | tutorial design, learning notebooks, teaching patterns, anti-patterns, checkpoints, learning objectives, pedagogical design, educational content, progressive learning, Snowflake notebooks, teaching point callouts, validation gates, tutorial structure, learning design, educational notebooks, teaching methodology, tutorial best practices, notebook education | `109-snowflake-notebooks.mdc`, `500-data-science-analytics.mdc` |
|| `109c-snowflake-app-deployment.mdc` | Agent Requested | Deployment automation patterns for Snowflake applications (notebooks, Streamlit, UDFs) using staged files. | General | Snowflake deployment, Streamlit deployment, notebook deployment, PUT, CREATE STREAMLIT, CREATE NOTEBOOK, stages, deployment automation, SiS, troubleshooting, deploy app, deployment pipeline, app publishing, deployment patterns, deploy to snowflake, stage deployment, production deployment, app versioning | `100-snowflake-core.mdc`, `109-snowflake-notebooks.mdc`, `101-snowflake-streamlit-core.mdc`, `820-taskfile-automation.mdc` |
|| `110-snowflake-model-registry.mdc` | Agent Requested | Comprehensive best practices for Snowflake Model Registry, covering model lifecycle, security, versioning, and governance. | ML registry | Model registry, ML models, model versioning, model deployment, MLOps, model governance, model lifecycle, model logging, model inference, RBAC, model privileges, register model, log model, model management, ML registry, model tracking, model metadata, deploy model, model lineage | `100-snowflake-core.mdc` |
|| `111-snowflake-observability-core.mdc` | Agent Requested | Core observability foundations for Snowflake including telemetry configuration, event table management, and foundational concepts. | Observability | Observability, Snowflake Trail, telemetry configuration, event tables, LOG_LEVEL, TRACE_LEVEL, METRIC_LEVEL, SHOW PARAMETERS, OpenTelemetry, System Views vs Telemetry, monitoring, logging, tracing, debug observability, telemetry setup, event table queries, observability patterns, configure telemetry | `100-snowflake-core.mdc` |
|| `111a-snowflake-observability-logging.mdc` | Agent Requested | Logging best practices for Snowflake handlers including standard library integration, log level strategy, conditional logging patterns, and cost-conscious volume management. | General | Logging, Python logging, logger, log levels, DEBUG, INFO, WARN, ERROR, FATAL, conditional logging, sampling, tight loop logging, standard logging libraries, log volume control, cost management, setup logging, log configuration, logging best practices, log handlers | `100-snowflake-core.mdc`, `111-snowflake-observability-core.mdc` |
|| `111b-snowflake-observability-tracing.mdc` | Agent Requested | Distributed tracing and metrics collection patterns for Snowflake including custom spans, performance analysis, trace attributes, and system metrics monitoring. | General | Distributed tracing, snowflake-telemetry-python, custom spans, span attributes, trace_id, performance analysis, metrics collection, cpu_usage, memory_usage, telemetry.create_span, OpenTelemetry, nested spans, trace setup, tracing patterns, span creation, trace analysis, distributed traces, tracing best practices | `100-snowflake-core.mdc`, `111-snowflake-observability-core.mdc` |
|| `111c-snowflake-observability-monitoring.mdc` | Agent Requested | Monitoring, analysis, cost management, Snowsight interfaces, AI observability, and troubleshooting patterns for Snowflake observability. | General | Snowflake, monitoring, Snowsight, Query History, Traces & Logs, Copy History, Task History, Dynamic Tables, cost management, AI observability, Cortex AI, token tracking, troubleshooting, performance analysis, monitor queries, monitoring dashboard, observability UI, query monitoring, telemetry volume, SQL | `100-snowflake-core.mdc`, `111-snowflake-observability-core.mdc` |
|| `112-snowflake-snowcli.mdc` | Agent Requested | Guidelines and best practices for Snowflake CLI (SnowCLI) usage with reproducible, pinned execution. | Snowflake CLI | snow CLI, SnowCLI, Snowflake command line, uvx snow, CLI deployment, snowflake.yml, uvx --from snowflake-cli, pinned execution, hermetic execution, CLI commands, snow commands, CLI setup, snowflake CLI usage, CLI best practices, CLI automation, command line tools, CLI configuration, CLI deployment patterns | `100-snowflake-core.mdc` |
|| `113-snowflake-feature-store.mdc` | Agent Requested | Comprehensive best practices for Snowflake Feature Store, covering feature engineering, entity modeling, feature views, and ML pipeline integration. | Feature Store | Feature store, feature engineering, feature views, entity modeling, ML pipeline, ML features, ASOF JOIN, point-in-time correctness, Dynamic Tables, feature versioning, create features, feature catalog, feature pipeline, feature management, feature discovery, ML features, feature registry, feature lineage | `100-snowflake-core.mdc`, `110-snowflake-model-registry.mdc` |
|| `114-snowflake-cortex-aisql.mdc` | Agent Requested | Best practices for Snowflake Cortex AISQL functions with cost, performance, security, and observability guidance, including SQL and Snowpark Python examples. | AISQL | Cortex AISQL, AI_COMPLETE, AI_CLASSIFY, AI_EXTRACT, AI_SENTIMENT, AI_SUMMARIZE, embeddings, LLM functions, batching, token costs, cortex AI functions, text generation, classification, sentiment analysis, summarization, LLM SQL, cortex functions, AI function error | `100-snowflake-core.mdc`, `105-snowflake-cost-governance.mdc` |
|| `115-snowflake-cortex-agents-core.mdc` | Agent Requested | Core best practices for Snowflake Cortex Agents covering prerequisites validation, agent archetypes, tooling strategy, and configuration templates. | General | Cortex Agents, agent design, tool configuration, grounding, RBAC, multi-tool agents, planning instructions, testing, troubleshooting, semantic views, create agent, debug agent, agent not working, tool execution failed, agent error, fix agent, agent performance, agent tool integration, cortex agent configuration, UnboundedExecution | `100-snowflake-core.mdc`, `105-snowflake-cost-governance.mdc`, `106-snowflake-semantic-views.mdc`, `111-snowflake-observability-core.mdc` |
|| `115a-snowflake-cortex-agents-instructions.mdc` | Agent Requested | Planning and response instruction patterns for Snowflake Cortex Agents covering tool selection logic, orchestration patterns, and response formatting. | General | Cortex Agents, planning instructions, response instructions, tool orchestration, flagging logic, agent prompts, multi-tool orchestration, tool selection, agent prompting, instruction patterns, agent planning, tool chaining, orchestration patterns, multi-step agent, agent workflow, instruction design, tool flagging, agent response format | `100-snowflake-core.mdc`, `115-snowflake-cortex-agents-core.mdc` |
|| `115b-snowflake-cortex-agents-operations.mdc` | Agent Requested | Operational best practices for Snowflake Cortex Agents covering testing, RBAC, observability, cost management, and error troubleshooting. | General | Cortex Agents, testing, RBAC, permissions, allowlists, observability, evaluation, cost management, error troubleshooting, agent security, test agent, agent permissions, agent RBAC setup, agent monitoring, agent evaluation, agent costs, debug agent, agent logs, agent trace, agent security policies | `100-snowflake-core.mdc`, `115-snowflake-cortex-agents-core.mdc`, `111-snowflake-observability-core.mdc` |
|| `116-snowflake-cortex-search.mdc` | Agent Requested | Best practices for Snowflake Cortex Search: indexing, embeddings, filters, hybrid retrieval, agent integration, and query patterns with governance, observability, prerequisites validation, and error troubleshooting. | General | Cortex Search, vector search, embeddings, search index, RAG, semantic search, agent tools, retrieval, troubleshooting, AI_EMBED, create search service, search service error, document retrieval, cortex search setup, search index creation, hybrid search, search service debug, vector similarity | `100-snowflake-core.mdc`, `105-snowflake-cost-governance.mdc`, `111-snowflake-observability.mdc`, `114-snowflake-cortex-aisql.mdc` |
|| `117-snowflake-cortex-analyst.mdc` | Agent Requested | Best practices for Snowflake Cortex Analyst and Semantic Views, including modeling guidance, governance, agent integration, usage patterns, prerequisites validation, Semantic View Generator workflow, and error troubleshooting. | General | Cortex Analyst, semantic views, natural language queries, NL2SQL, agent tool configuration, semantic view design, Generator workflow, prerequisites validation, error troubleshooting, business metrics, analyst not working, fix analyst, debug analyst, analyst query error, semantic view validation, text to SQL, cortex analyst integration, analyst API | `100-snowflake-core.mdc`, `106-snowflake-semantic-views.mdc`, `105-snowflake-cost-governance.mdc`, `111-snowflake-observability.mdc` |
|| `118-snowflake-cortex-rest-api.mdc` | Agent Requested | Best practices for Snowflake Cortex REST API usage: auth, endpoints, retries, streaming, idempotency, rate/cost controls, and when to use REST vs AISQL. | General | Cortex REST API, API authentication, streaming responses, API retries, idempotency, rate limits, Complete endpoint, Embed endpoint, exponential backoff, REST API usage, API integration, API calls, Cortex API, API error handling, API best practices, API endpoints, authentication tokens, API retry logic | `100-snowflake-core.mdc`, `105-snowflake-cost-governance.mdc`, `111-snowflake-observability.mdc` |
|| `119-snowflake-warehouse-management.mdc` | Agent Requested | Comprehensive best practices for Snowflake virtual warehouse creation, configuration, and management including CPU/GPU/High-Memory types, GEN 2 preference, sizing, tagging, and cost governance. | Warehouse management | Warehouse management, warehouse sizing, CPU warehouse, GPU warehouse, high-memory warehouse, warehouse tagging, auto-suspend, auto-resume, GEN 2, Snowpark-Optimized, warehouse edition, resource monitors, create warehouse, warehouse configuration, warehouse types, warehouse cost, size warehouse, warehouse best practices | `100-snowflake-core.mdc`, `103-snowflake-performance-tuning.mdc`, `105-snowflake-cost-governance.mdc` |
|| `120-snowflake-spcs.mdc` | Agent Requested | Comprehensive best practices for Snowflake Snowpark Container Services (SPCS), covering containerized application deployment, management, and optimization. | SPCS | SPCS, Snowpark Container Services, containers, containerized apps, service deployment, compute pools, OCI images, image registry, health checks, GPU workloads, create service, compute pool, container deployment, SPCS setup, service spec, container troubleshooting, SPCS error, service logs | `100-snowflake-core.mdc` |
|| `121-snowflake-snowpipe.mdc` | Agent Requested | Comprehensive best practices for Snowflake Snowpipe and Snowpipe Streaming for continuous, near-real-time data ingestion including auto-ingest, REST API, and streaming architectures. | Snowpipe | Snowpipe, Snowpipe Streaming, continuous ingestion, real-time loading, auto-ingest, streaming data, micro-batching, file-based ingestion, SDK, event notifications, COPY INTO, create pipe, auto ingest, pipe setup, data ingestion, streaming load, pipe errors, continuous ingestion, pipe management, ingestion monitoring | `100-snowflake-core.mdc`, `108-snowflake-data-loading.mdc`, `104-snowflake-streams-tasks.mdc` |
|| `122-snowflake-dynamic-tables.mdc` | Agent Requested | Comprehensive best practices for Snowflake Dynamic Tables covering refresh modes, lag configuration, pipeline design, and performance optimization. | Dynamic Tables | Dynamic Tables, materialized views, incremental refresh, target lag, refresh mode, automatic pipelines, DOWNSTREAM, FULL, warehouse sizing, data freshness, create dynamic table, dynamic table lag, refresh frequency, dynamic table error, materialized view alternative, pipeline automation, lag configuration, refresh strategies | `100-snowflake-core.mdc`, `104-snowflake-streams-tasks.mdc`, `119-snowflake-warehouse-management.mdc` |
|| `123-snowflake-object-tagging.mdc` | Agent Requested | Comprehensive best practices for Snowflake object tagging covering tag fundamentals, inheritance, propagation, tag-based policies, cost attribution, and governance patterns. | Object tagging | Object tagging, tags, tag inheritance, tag-based policies, cost attribution, resource tagging, governance tags, masking policies, row access policies, tag lineage, create tags, apply tags, tag strategy, tagging best practices, tag policies, tag compliance, tag hierarchy, tag discovery, tag management | `100-snowflake-core.mdc`, `105-snowflake-cost-governance.mdc`, `107-snowflake-security-governance.mdc` |
|| `124-snowflake-data-quality-core.mdc` | Agent Requested | Core best practices for Snowflake Data Quality Monitoring covering DMF fundamentals, system DMFs, and data profiling patterns. | Data quality | Snowflake, Data quality, DMF, data metric functions, data profiling, expectations, quality checks, data validation, NULL detection, uniqueness validation, freshness monitoring, anomaly detection, automated monitoring, event tables, create DMF, quality monitoring, data expectations, DMF setup, quality rules | `100-snowflake-core.mdc`, `105-snowflake-cost-governance.mdc`, `107-snowflake-security-governance.mdc`, `600-data-governance-quality.mdc` |
|| `124a-snowflake-data-quality-custom.mdc` | Agent Requested | Custom Data Metric Functions (DMFs) and expectations patterns for Snowflake including business rule validation and quality assertions. | General | Data quality, custom DMFs, expectations, business rules, data validation, quality assertions, custom metrics, validation functions, create custom DMF, custom quality checks, business rule validation, custom expectations, quality functions, UDF for quality, validation logic, custom quality metrics, quality rules, custom validation | `100-snowflake-core.mdc`, `124-snowflake-data-quality-core.mdc` |
|| `124b-snowflake-data-quality-operations.mdc` | Agent Requested | Operational patterns for Snowflake Data Quality Monitoring including scheduling, event tables, alerts, remediation, and RBAC configuration. | General | Data quality, DMF scheduling, event tables, alerts, remediation, RBAC, privilege requirements, automated monitoring, quality alerts, schedule DMF, quality event tables, quality alerting, DMF results, quality monitoring setup, quality workflows, DMF RBAC, quality notifications, remediation workflows | `100-snowflake-core.mdc`, `124-snowflake-data-quality-core.mdc`, `111-snowflake-observability-core.mdc` |
|| `200-python-core.mdc` | Agent Requested | Core Python engineering policies for a consistent, reliable, and performant codebase using modern tools like `uv` and Ruff. | Python core | Python, uv, Ruff, pyproject.toml, dependency management, virtual environments, modern Python tooling, pytest, validation, uv run, uvx, datetime.now(UTC) | `000-global-core.mdc` |
|| `201-python-lint-format.mdc` | Agent Requested | Authoritative Python linting and formatting policy using Ruff for code quality and consistency. | Linting | Ruff, linting, formatting, code quality, style checking, uvx ruff, lint errors, ruff check, ruff format, pyproject.toml configuration | `200-python-core.mdc` |
|| `202-markup-config-validation.mdc` | Agent Requested | Markup and configuration file validation to prevent parsing errors and ensure consistency. | Config validation | YAML, configuration files, YAML syntax, parsing errors, indentation, anchors, aliases, Markdown, markdown linting, pymarkdownlnt, markup validation, TOML, environment files | — |
|| `203-python-project-setup.mdc` | Agent Requested | Python project setup and packaging best practices to avoid common build and dependency issues. | Project setup | Python packaging, project structure, setup.py, pyproject.toml, dependencies, package distribution, __init__.py, hatchling, uv, src layout | `200-python-core.mdc` |
|| `204-python-docs-comments.mdc` | Agent Requested | Python documentation, comments, and docstring standards with enforcement and common mistake prevention. | Documentation | Python docstrings, documentation, comments, pydocstyle, Ruff DOC rules, API documentation, Google style, NumPy style, PEP 257, code quality | `200-python-core.mdc`, `201-python-lint-format.mdc` |
|| `205-python-classes.mdc` | Agent Requested | Broadly accepted best practices for designing and using classes in Python, focusing on clarity, correctness, and maintainability. | Classes | Python classes, OOP, inheritance, dataclasses, @property, class design, encapsulation, composition, Protocol, ABC, type hints | `200-python-core.mdc`, `201-python-lint-format.mdc`, `204-python-docs-comments.mdc` |
|| `206-python-pytest.mdc` | Agent Requested | Broadly accepted best practices for testing Python applications using pytest: structure, fixtures, parametrization, isolation, and reliable execution. | Testing | pytest, testing, fixtures, parametrization, test isolation, mocking, test organization, coverage, AAA pattern, test markers, uv run pytest | `200-python-core.mdc`, `201-python-lint-format.mdc`, `203-python-project-setup.mdc` |
|| `210-python-fastapi-core.mdc` | Agent Requested | Comprehensive FastAPI best practices for building modern, performant, and maintainable web APIs and applications. | FastAPI | FastAPI, async, REST API, Pydantic, dependency injection, routing, request validation, response models, APIRouter, uvicorn, async def, application factory | `200-python-core.mdc` |
|| `210a-python-fastapi-security.mdc` | Agent Requested | FastAPI security patterns for authentication, authorization, CORS, and security middleware. | General | FastAPI security, authentication, OAuth2, JWT, CORS, middleware, API keys, security best practices, bcrypt, HTTPBearer, role-based access control, RBAC | `210-python-fastapi-core.mdc` |
|| `210b-python-fastapi-testing.mdc` | Agent Requested | FastAPI testing strategies with TestClient, pytest-asyncio, and comprehensive API testing patterns. | General | FastAPI testing, TestClient, pytest-asyncio, API tests, integration testing, mocking, test fixtures, AAA pattern, async testing, Python | `210-python-fastapi-core.mdc` |
|| `210c-python-fastapi-deployment.mdc` | Agent Requested | FastAPI production deployment with Docker, ASGI servers, and API documentation patterns. | General | FastAPI deployment, Uvicorn, Gunicorn, ASGI, Docker, production deployment, health checks, multi-stage build, OpenAPI, API documentation | `210-python-fastapi-core.mdc` |
|| `210d-python-fastapi-monitoring.mdc` | Agent Requested | FastAPI health checks, logging, monitoring, and performance optimization patterns. | General | FastAPI monitoring, health checks, logging, metrics, caching, Redis, observability, structured logging, health endpoints, correlation IDs | `210-python-fastapi-core.mdc` |
|| `220-python-typer-cli.mdc` | Agent Requested | Comprehensive Typer CLI development patterns covering setup, design, testing, and deployment best practices for Python command-line applications. | CLI | Typer, CLI development, command-line interface, click, argument parsing, CLI testing, typer.Argument, typer.Option, CliRunner, rich console | `200-python-core.mdc` |
|| `230-python-pydantic.mdc` | Agent Requested | Comprehensive Pydantic data validation patterns covering models, settings, serialization, and integration best practices for Python applications. | Validation | Pydantic, data validation, models, settings, BaseModel, field validation, serialization, Field, validator, model_validator, EmailStr, pydantic-settings | `200-python-core.mdc` |
|| `240-python-faker.mdc` | Agent Requested | Comprehensive Faker data generation patterns covering providers, localization, testing integration, and performance best practices for Python applications. | Data generation | Faker, test data generation, fake data, providers, localization, synthetic data, pytest fixtures, seeding, deterministic testing, Python testing | `200-python-core.mdc` |
|| `250-python-flask.mdc` | Agent Requested | Comprehensive Flask best practices for building modern, maintainable, and secure web applications following industry standards. | Flask | Flask, web development, blueprints, Flask-SQLAlchemy, templates, routing, Flask extensions, application factory, Jinja2, Flask-WTF, CSRF protection | `200-python-core.mdc` |
|| `251-python-datetime-handling.mdc` | Agent Requested | Comprehensive datetime and date handling best practices for Python, Pandas, Plotly, and Streamlit with type safety, timezone management, and performance optimization. | Datetime | datetime, pandas, timezone, datetime64, timedelta, UTC, date arithmetic, tz_localize, tz_convert, datetime.now(UTC) | `200-python-core.mdc` |
|| `252-pandas-best-practices.mdc` | Agent Requested | Comprehensive Pandas best practices for performance, vectorization, anti-patterns, and memory optimization with Streamlit and Plotly integration patterns. | Pandas | pandas, DataFrame, vectorization, SettingWithCopyWarning, memory optimization, dtypes, groupby, merge, performance, method chaining | `200-python-core.mdc` |
|| `300-bash-scripting-core.mdc` | Agent Requested | Foundation bash scripting patterns covering script structure, variables, functions, and essential error handling practices. | Bash | Bash, shell scripting, set -euo pipefail, error handling, strict mode, functions, variables, script structure, trap, exit codes, shellcheck, input validation | `000-global-core.mdc` |
|| `300a-bash-security.mdc` | Agent Requested | Bash scripting security best practices covering input validation, path security, permissions, and secure coding patterns. | General | Bash, security, input validation, command injection, path security, secure shell scripts, sanitization, permissions, privilege escalation, secrets management | `300-bash-scripting-core.mdc` |
|| `300b-bash-testing-tooling.mdc` | Agent Requested | Bash testing, debugging, and modern tooling integration including ShellCheck, CI/CD, and development workflows. | General | Bash, testing, ShellCheck, bats, shell script testing, CI/CD, debugging, static analysis, linting, test automation | `300-bash-scripting-core.mdc` |
|| `310-zsh-scripting-core.mdc` | Agent Requested | Foundation zsh scripting patterns covering unique zsh features, script structure, variables, functions, and essential practices. | Zsh | Zsh, Z shell, zsh features, arrays, functions, oh-my-zsh, emulate, setopt, parameter expansion, globbing | `300-bash-scripting-core.mdc` |
|| `310a-zsh-advanced-features.mdc` | Agent Requested | Advanced zsh features including completion system, modules, hooks, and performance optimization techniques. | General | Zsh, completion system, modules, hooks, advanced features, performance optimization, compinit, zstyle, autoload, scripting | `310-zsh-scripting-core.mdc` |
|| `310b-zsh-compatibility.mdc` | Agent Requested | Zsh compatibility strategies, bash migration patterns, and cross-shell scripting best practices for mixed environments. | General | Zsh, shell compatibility, bash vs zsh, portable scripts, cross-shell, migration, emulate, POSIX compliance, scripting, shell scripting | `300-bash-scripting-core.mdc` |
|| `400-docker-best-practices.mdc` | Agent Requested | Comprehensive Docker and Dockerfile best practices for reliable, secure, and performant container builds and runtime across dev, CI, and production. | Docker | Docker, Dockerfile, containers, multi-stage builds, layer caching, image optimization, docker-compose, BuildKit, distroless, security scanning, SBOM, non-root, healthcheck | `202-markup-config-validation.mdc` |
|| `500-data-science-analytics.mdc` | Agent Requested | Comprehensive data science and analytics rules for Snowflake, focusing on model lifecycle, ML/AI insight presentation, advanced SQL, visualization best practices, and performance optimization. | Analytics | Data science, Snowflake, pandas, Snowpark, ML, model lifecycle, feature engineering, NaN handling, model versioning, Jupyter | `200-python-core.mdc` |
|| `600-data-governance-quality.mdc` | Agent Requested | Comprehensive directives for ensuring data quality, governance, and operational reliability throughout the data lifecycle. | Governance | Data governance, data quality, lineage, metadata management, compliance, data catalog, Great Expectations, schema evolution, data observability, incident response | — |
|| `700-business-analytics.mdc` | Agent Requested | Comprehensive business analytics and reporting directives for creating business-oriented queries, dashboards, and visualizations for non-technical stakeholders with emphasis on clarity, accessibility, and ethical presentation. | BI | Business intelligence, dashboards, KPIs, reporting, visualization, stakeholder reports, metrics, Snowsight, executive dashboards, data storytelling, WCAG accessibility | — |
|| `800-project-changelog-rules.mdc` | Agent Requested | Directives for maintaining a high-signal, audit-friendly `CHANGELOG. | Changelog | CHANGELOG, changelog format, semantic versioning, release notes, conventional commits, Unreleased section, scope patterns, project governance, git workflow, version control | `000-global-core.mdc` |
|| `801-project-readme-rules.mdc` | Agent Requested | Industry-standard README. | README | README, project documentation, getting started, setup instructions, badges, Quick Start, Contributing, License, project structure, technical writing | `000-global-core.mdc` |
|| `805-project-contributing-rules.mdc` | Agent Requested | Directives for a professional contribution workflow: commits, pull requests, changelog discipline, and rule authoring standards. | Contributing | CONTRIBUTING, pull requests, code review, contribution guidelines, branching strategy, Conventional Commits, rule authoring, PR templates, project governance, git workflow | `000-global-core.mdc` |
|| `806-git-workflow-management.mdc` | Agent Requested | Git workflow best practices for GitHub and GitLab covering branching strategies, merge workflows, protected branches, and git state validation. | Git workflow | git, workflow, branching strategy, GitLab, GitHub, merge requests, pull requests, feature branches, protected branches, git validation, branch naming, PR workflow, MR workflow, Conventional Commits | `800-project-changelog-rules.mdc`, `805-project-contributing-rules.mdc` |
|| `820-taskfile-automation.mdc` | Agent Requested | Directives for creating, modifying, and maintaining project automation using `Taskfile. | Automation | Taskfile, task automation, Taskfile.yml, build automation, task runner, Task, portable tasks, error handling, categorized help, user experience, task discovery | `202-markup-config-validation.mdc` |
|| `900-demo-creation.mdc` | Agent Requested | Directives for creating realistic, deterministic, and effective demo applications, from data generation to narrative and visual clarity. | Demo | Demo creation, synthetic data, realistic demos, data generation, demo applications, narrative design, reproducible data, progressive disclosure, Streamlit, data visualization | — |
|| `901-data-generation-modeling.mdc` | Agent Requested | Data generation and dimensional modeling standards (Kimball, naming, view taxonomy, BA-first) for analytics-friendly data. | Data generation | Data modeling, naming conventions, Kimball, dimensional modeling, fact tables, dimension tables, foreign keys, view taxonomy, Business Analyst, data generation, backward compatibility, entity IDs, temporal columns, surrogate keys, SCD Type 2 | `000-global-core.mdc`, `100-snowflake-core.mdc`, `102-snowflake-sql-demo-engineering.mdc`, `600-data-governance-quality.mdc`, `700-business-analytics.mdc` |

---

## Common Rule Dependency Chains

This section visualizes common rule loading patterns to help AI assistants calculate token costs and load rules in the correct order.

**Reading the Trees:**
- Indentation shows dependency relationships
- Token budgets shown in parentheses
- "Minimal/Standard/Complete" shows progressive loading strategies
- Always load parent rules before child rules

### Streamlit Dashboard Development
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    └── 101-snowflake-streamlit-core (3700 tokens)
        ├── 101a-snowflake-streamlit-visualization (3600 tokens)
        ├── 101b-snowflake-streamlit-performance (3800 tokens)
        └── 101c-snowflake-streamlit-security (2550 tokens)

Token Cost Scenarios:
• Minimal (basic app):        000 + 100 + 101      = ~6,800 tokens
• Standard (with viz):         + 101a               = ~10,400 tokens
• Performance (caching):       + 101b               = ~14,200 tokens
• Complete (production-ready): + 101c               = ~16,750 tokens
```

### Cortex Agent Development
```
000-global-core (1300 tokens)
├── 100-snowflake-core (1800 tokens)
│   ├── 106-snowflake-semantic-views-core (2800 tokens)
│   │   ├── 106a-snowflake-semantic-views-advanced (2200 tokens)
│   │   └── 106b-snowflake-semantic-views-querying (5000 tokens)
│   └── 111-snowflake-observability-core (2000 tokens)
│       ├── 111a-snowflake-observability-logging (varies)
│       └── 111c-snowflake-observability-monitoring (varies)
└── 115-snowflake-cortex-agents-core (2200 tokens)
    ├── 115a-snowflake-cortex-agents-instructions (800 tokens)
    └── 115b-snowflake-cortex-agents-operations (2400 tokens)

Token Cost Scenarios:
• Minimal (agent setup):         000 + 100 + 115           = ~5,300 tokens
• Standard (with semantic views): + 106                     = ~8,100 tokens
• Advanced (instructions):        + 115a                    = ~8,900 tokens
• Production (operations):        + 115b + 111             = ~13,300 tokens
• Complete (all capabilities):    + 106a + 106b            = ~20,500 tokens
```

### Cortex Analyst Integration
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 106-snowflake-semantic-views-core (2800 tokens)
    │   ├── 106a-snowflake-semantic-views-advanced (2200 tokens)
    │   └── 106b-snowflake-semantic-views-querying (5000 tokens)
    └── 117-snowflake-cortex-analyst (3800 tokens)

Token Cost Scenarios:
• Minimal (basic analyst):    000 + 100 + 106 + 117 = ~9,700 tokens
• Standard (with queries):    + 106b                 = ~14,700 tokens
• Complete (full capability): + 106a                 = ~16,900 tokens
```

### Performance Tuning Workflow
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 103-snowflake-performance-tuning (800 tokens)
    ├── 105-snowflake-cost-governance (1150 tokens)
    └── 119-snowflake-warehouse-management (3650 tokens)

Token Cost Scenarios:
• Minimal (query optimization):  000 + 100 + 103      = ~3,900 tokens
• Standard (with warehouses):    + 119                 = ~7,550 tokens
• Complete (cost governance):    + 105                 = ~8,700 tokens
```

### Data Pipeline Development
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 104-snowflake-streams-tasks (850 tokens)
    │   └── 122-snowflake-dynamic-tables (5200 tokens)
    ├── 108-snowflake-data-loading (950 tokens)
    └── 124-snowflake-data-quality-core (6200 tokens)

Token Cost Scenarios:
• Minimal (basic CDC):           000 + 100 + 104     = ~3,950 tokens
• With dynamic tables:           + 122                = ~9,150 tokens
• With data loading:             + 108                = ~10,100 tokens
• Complete (with quality):       + 124                = ~16,300 tokens
```

### Cortex Search Implementation
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 116-snowflake-cortex-search (4000 tokens)
    ├── 108-snowflake-data-loading (950 tokens)
    └── 115-snowflake-cortex-agents-core (2200 tokens)
        └── 115b-snowflake-cortex-agents-operations (2400 tokens)

Token Cost Scenarios:
• Minimal (search setup):        000 + 100 + 116     = ~7,100 tokens
• With document loading:         + 108                = ~8,050 tokens  
• Agent integration:             + 115                = ~10,250 tokens
• Complete (operations):         + 115b               = ~12,650 tokens
```

### SPCS Container Deployment
```
000-global-core (1300 tokens)
└── 100-snowflake-core (1800 tokens)
    ├── 120-snowflake-spcs (3550 tokens)
    ├── 119-snowflake-warehouse-management (3650 tokens)
    └── 111-snowflake-observability-core (2000 tokens)
        ├── 111a-snowflake-observability-logging (varies)
        └── 111c-snowflake-observability-monitoring (varies)

Token Cost Scenarios:
• Minimal (basic SPCS):          000 + 100 + 120     = ~6,650 tokens
• With compute pools:            + 119                = ~10,300 tokens
• Complete (observability):      + 111                = ~12,300 tokens
```

**Usage Tips:**
- Load only what you need based on task complexity
- "Minimal" scenarios cover 70-80% of typical use cases
- "Standard" adds commonly needed extensions
- "Complete" for production-ready, comprehensive implementations
- If unsure, start with Minimal and load additional rules as needed
