# Rule Catalog

Complete catalog of all 74 rules organized by domain. For a searchable index with keywords and dependencies, see [RULES_INDEX.md](../RULES_INDEX.md) in the project root.

## Core Foundation (000-099)

- **`000-global-core.md`** — Universal operating principles and safety protocols
- **`001-memory-bank.md`** — Universal memory bank for maintaining project context across sessions
- **`002-rule-governance.md`** — Comprehensive rule authoring governance: creation standards, naming conventions, structure requirements, validation workflows, and rule creation template
- **`003-context-engineering.md`** — Context management strategies (attention budgets, context rot, progressive disclosure, compaction)
- **`004-tool-design-for-agents.md`** — Token-efficient tool design patterns (single responsibility, minimal tool sets, clear parameters)
- **discovery/AGENTS.md** — AI assistant discovery guide (automatically configured during deployment)

### Universal Rule Authoring Best Practices

The following best practices apply to all AI coding assistants and development environments:

**Structure Standards**
- Use a single `#` H1 title for each rule file
- Keep rules focused and concise (target 150-300 lines, max 500 lines)
- Split large topics into multiple composable rules
- Include clear metadata at the top with description and scope

**Content Guidelines**  
- Use explicit directive language: `Critical`, `Mandatory`, `Always`, `Requirement`, `Rule`, `Consider`, `Avoid`
- Avoid content duplication across rules; reference other files instead
- Include links to current, relevant documentation for validation
- Provide practical examples and usage patterns

**Naming & Organization**
- Use snake-case naming with `.md` extension (e.g., `my_rule_name.md`)
- Place universal rules in the canonical directory structure
- Group related rules by domain/technology (100-199 for Snowflake, 200-299 for Python, etc.)
- Use consistent 3-digit numbering for logical ordering and scalability

**Scope Management**
- Keep rule scope tightly focused on specific domains or technologies
- Prefer on-demand (Agent Requested) pattern over auto-attach for specialized rules
- Only global core rules should auto-attach universally
- Design rules to be composable and reusable across projects

**Validation & Maintenance**
- Test rules with multiple AI models and development environments
- Verify syntax, best practices, and API usage against current documentation
- Regularly update rules to reflect evolving best practices
- Remove outdated content and consolidate overlapping guidance

## Data Platform - Snowflake (100-199)

- **`100-snowflake-core.md`** — Core Snowflake guidelines (SQL, performance, security, DDL object naming conventions)
- **`101-snowflake-streamlit-core.md`** — Streamlit core: setup, navigation, state management, deployment modes (SiS vs SPCS)
- **`101a-snowflake-streamlit-visualization.md`** — Streamlit visualization: Plotly charts, maps, dashboard integration
- **`101b-snowflake-streamlit-performance.md`** — Streamlit performance: caching, optimization, data loading from Snowflake
- **`101c-snowflake-streamlit-security.md`** — Streamlit security: input validation, secrets management, best practices
- **`101d-snowflake-streamlit-testing.md`** — Streamlit testing: AppTest patterns, unit testing, debugging workflows
- **`102-snowflake-sql-demo-engineering.md`** — SQL patterns for demos and customer learning environments (educational comments, progress indicators, demo-safe idempotent patterns)
- **`102a-snowflake-sql-automation.md`** — Production SQL automation with parameterized templates and CI/CD integration (Snowflake variable syntax, environment-agnostic patterns)
- **`103-snowflake-performance-tuning.md`** — Query optimization and warehouse tuning
- **`104-snowflake-streams-tasks.md`** — Incremental data pipelines
- **`105-snowflake-cost-governance.md`** — Cost optimization and resource management
- **`106-snowflake-semantic-views.md`** — Core DDL syntax and validation rules for creating semantic views
- **`106a-snowflake-semantic-views-querying.md`** — Query patterns and testing strategies for semantic views using SEMANTIC_VIEW() function
- **`106b-snowflake-semantic-views-integration.md`** — Cortex Analyst/Agent integration, governance, and development workflows for semantic views
- **`107-snowflake-security-governance.md`** — Security policies and access control
- **`108-snowflake-data-loading.md`** — Data ingestion best practices
- **`109-snowflake-notebooks.md`** — Jupyter notebook standards (nbqa + Ruff linting, code quality, reproducibility)
- **`109a-snowflake-notebooks-tutorials.md`** — Tutorial design patterns for educational notebooks (learning objectives, checkpoints, progressive complexity, pedagogical patterns)
- **`109c-snowflake-app-deployment.md`** — Streamlit in Snowflake deployment requirements (AUTO_COMPRESS=FALSE, stage path requirements, troubleshooting TypeError errors)
- **`110-snowflake-model-registry.md`** — ML model lifecycle, versioning, and governance
- **`111-snowflake-observability.md`** — Comprehensive telemetry, logging, tracing, and metrics best practices
- **`112-snowflake-snowcli.md`** — Snowflake CLI usage best practices with pinned `uvx` execution
- **`113-snowflake-feature-store.md`** — Feature Store best practices (feature engineering, entity modeling, feature views, ML pipeline integration)
- **`114-snowflake-cortex-aisql.md`** — Cortex AISQL functions (cost, batching, governance, SQL/Snowpark examples)
- **`114a-snowflake-cortex-agents.md`** — Cortex Agents (grounding, tools, RBAC, observability)
- **`114b-snowflake-cortex-search.md`** — Cortex Search (indexing, metadata filters, hybrid retrieval)
- **`114c-snowflake-cortex-analyst.md`** — Cortex Analyst & Semantic Views (modeling, governance, prompts)
- **`114d-snowflake-cortex-rest-api.md`** — Cortex REST API (auth, retries, streaming, cost)
- **`119-snowflake-warehouse-management.md`** — Warehouse management best practices (creation, type selection CPU/GPU/High-Memory, sizing, tagging, cost governance)
- **`120-snowflake-spcs.md`** — Snowpark Container Services best practices (containerized applications, compute pools, service management)
- **`121-snowflake-snowpipe.md`** — Snowpipe and Snowpipe Streaming best practices (continuous near-real-time ingestion, auto-ingest, REST API, SDK)
- **`122-snowflake-dynamic-tables.md`** — Dynamic Tables best practices (refresh modes, lag configuration, pipeline design, performance optimization)
- **`123-snowflake-object-tagging.md`** — Object tagging best practices (governance, cost attribution, tag-based masking policies, inheritance, monitoring)
- **`124-snowflake-data-quality.md`** — Data Quality Monitoring best practices (DMFs, data profiling, expectations, scheduling, alerts, cost management)

## Software Engineering - Python (200-299)

- **`200-python-core.md`** — Modern Python engineering with `uv` and Ruff (environment management, code structure, reliability)
- **`201-python-lint-format.md`** — Authoritative linting and formatting with Ruff (code quality and consistency)
- **`202-markup-config-validation.md`** — Markup and configuration file validation (YAML, TOML, environment files, Markdown linting with pymarkdownlnt)
- **`203-python-project-setup.md`** — Python project setup and packaging best practices (avoiding build issues)
- **`204-python-docs-comments.md`** — Python documentation, comments, and docstring standards with Ruff enforcement
- **`205-python-classes.md`** — Python class design and usage best practices (composition, dataclasses, properties, ABCs/Protocols)
- **`206-python-pytest.md`** — pytest testing best practices (fixtures, parametrization, isolation, markers, CI)

### FastAPI Framework (210-219)

- **`210-python-fastapi-core.md`** — FastAPI core patterns (application structure, async programming, Pydantic validation)
- **`210a-python-fastapi-security.md`** — FastAPI security patterns (authentication, authorization, CORS, middleware)
- **`210b-python-fastapi-testing.md`** — FastAPI testing strategies (TestClient, pytest-asyncio, comprehensive API testing)
- **`210c-python-fastapi-deployment.md`** — FastAPI deployment and documentation (Docker, ASGI servers, OpenAPI customization)
- **`210d-python-fastapi-monitoring.md`** — FastAPI monitoring and performance (health checks, logging, caching, observability)

### CLI Applications (220-229)

- **`220-python-typer-cli.md`** — Typer CLI development (setup, design patterns, testing, async commands, packaging)

### Data Validation & Testing (230-249)

- **`230-python-pydantic.md`** — Pydantic data validation (models, settings, serialization, FastAPI integration)
- **`240-python-faker.md`** — Faker data generation (providers, localization, testing integration, performance)

### Web Frameworks (250-259)

- **`250-python-flask.md`** — Flask web framework (application factory pattern, blueprints, security, Jinja2 templates, SQLAlchemy integration)
- **`251-python-datetime-handling.md`** — Comprehensive datetime handling for Python, Pandas, Plotly, and Streamlit (timezone management, type conversions, cross-library compatibility)
- **`252-pandas-best-practices.md`** — Pandas performance and best practices (vectorization, memory optimization, anti-patterns, Streamlit/Plotly integration)

## Software Engineering - Shell Scripts (300-399)

### Bash Scripting (300-309)

- **`300-bash-scripting-core.md`** — Foundation bash scripting patterns (script structure, variables, functions, essential error handling)
- **`300a-bash-security.md`** — Security best practices (input validation, path security, permissions, credential management)
- **`300b-bash-testing-tooling.md`** — Testing frameworks, debugging, ShellCheck integration, and CI/CD workflows

### Zsh Scripting (310-319)

- **`310-zsh-scripting-core.md`** — Foundation zsh patterns (unique features, advanced arrays, parameter expansion, globbing)
- **`310a-zsh-advanced-features.md`** — Advanced zsh capabilities (completion system, hooks, modules, performance optimization)
- **`310b-zsh-compatibility.md`** — Cross-shell compatibility (bash migration, portable scripting, mixed environments)

## Software Engineering - Containers (400-499)

- **`400-docker-best-practices.md`** — Docker and Dockerfile best practices (builds, security, supply chain, runtime, Compose)

## Data Science & Analytics (500-599)

- **`500-data-science-analytics.md`** — ML lifecycle, feature engineering, and analytics

## Data Governance (600-699)

- **`600-data-governance-quality.md`** — Data quality, lineage, and stewardship

## Business Intelligence (700-799)

- **`700-business-analytics.md`** — Business-oriented reporting and visualization

## Project Management (800-899)

- **`800-project-changelog-rules.md`** — Changelog governance using Conventional Commits
- **`801-project-readme-rules.md`** — Professional README.md structure and content standards
- **`805-project-contributing-rules.md`** — Contribution workflow and PR standards
- **`806-git-workflow-management.md`** — Git workflow best practices for GitHub and GitLab with branching strategies and merge workflows
- **`820-taskfile-automation.md`** — Project automation with Taskfile (YAML-safe task orchestration)

## Demo & Synthetic Data (900-999)

- **`900-demo-creation.md`** — Realistic demo application development
- **`901-data-generation-modeling.md`** — Comprehensive data generation and dimensional modeling standards (Kimball methodology, universal naming conventions, business-first view taxonomy, backward compatibility strategies)

---

**For searchable index with keywords and dependencies, see [RULES_INDEX.md](../RULES_INDEX.md)**

