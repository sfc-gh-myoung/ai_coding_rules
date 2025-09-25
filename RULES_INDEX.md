**Description:** Top-level index of rule files with purpose, scope, and dependencies.
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-25

# Rules Index

This index helps agents select the correct rule quickly. Documentation files like `README.md`, `CHANGELOG.md`, and `CONTRIBUTING.md` are excluded.

| File | Type | Purpose (one line) | Scope | Depends On |
|------|------|---------------------|-------|------------|
| `000-global-core.md` | Auto-attach | Global operating contract (PLAN/ACT, safety, validation) | Universal | — |
| `001-memory-bank.md` | Auto-attach | Universal memory bank for AI context continuity | Project continuity | `000-global-core.md` |
| `002-rule-governance.md` | Auto-attach | Rule authoring governance, standards, and creation template | All rules | `000-global-core.md` |
| `100-snowflake-core.md` | Agent Requested | Foundational Snowflake practices (cost, performance, security) | Snowflake SQL & modeling | `000-global-core.md` |
| `101-snowflake-streamlit-ui.md` | Agent Requested | Streamlit UI best practices for Snowflake | Streamlit apps | `100-snowflake-core.md` |
| `102-snowflake-sql-best-practices.md` | Agent Requested | Advanced SQL authoring patterns | SQL authorship | `100-snowflake-core.md` |
| `103-snowflake-performance-tuning.md` | Agent Requested | Query profiling and warehouse tuning | Performance | `100-snowflake-core.md` |
| `104-snowflake-streams-tasks.md` | Agent Requested | Incremental pipelines with Streams + Tasks | Pipelines | `100-snowflake-core.md` |
| `105-snowflake-cost-governance.md` | Agent Requested | Cost optimization and monitors | Cost governance | `100-snowflake-core.md` |
| `106-snowflake-semantic-views.md` | Agent Requested | Semantic models and semantic views (Cortex Analyst) | Modeling | `100-snowflake-core.md` |
| `107-snowflake-security-governance.md` | Agent Requested | Masking, row access, and tagging | Security | `100-snowflake-core.md` |
| `108-snowflake-data-loading.md` | Agent Requested | Stages, COPY INTO, Snowpipe | Ingestion | `100-snowflake-core.md` |
| `109-snowflake-notebooks.md` | Agent Requested | Notebook best practices | Notebooks | `100-snowflake-core.md` |
| `110-snowflake-model-registry.md` | Agent Requested | Model lifecycle and governance | ML registry | `100-snowflake-core.md` |
| `111-snowflake-observability.md` | Agent Requested | Telemetry, logging, tracing, metrics | Observability | `100-snowflake-core.md` |
| `112-snowflake-snowcli.md` | Agent Requested | Snowflake CLI best practices with pinned uvx execution | Snowflake CLI | `100-snowflake-core.md` |
| `120-snowflake-spcs.md` | Agent Requested | Snowpark Container Services best practices | SPCS | `100-snowflake-core.md` |
| `200-python-core.md` | Agent Requested | Modern Python engineering with uv/Ruff | Python | `000-global-core.md` |
| `201-python-lint-format.md` | Agent Requested | Ruff linting/formatting policy | Linting | `200-python-core.md` |
| `202-yaml-config-best-practices.md` | Agent Requested | YAML safety and reliability | YAML/config | — |
| `203-python-project-setup.md` | Agent Requested | Packaging and setup practices | Python setup | `200-python-core.md` |
| `210-python-fastapi-core.md` | Agent Requested | FastAPI core patterns | FastAPI | `200-python-core.md` |
| `211-python-fastapi-security.md` | Agent Requested | Auth, CORS, security middleware | FastAPI security | `210-python-fastapi-core.md` |
| `212-python-fastapi-testing.md` | Agent Requested | API testing strategies | Testing | `210-python-fastapi-core.md` |
| `213-python-fastapi-deployment.md` | Agent Requested | Deployment & ASGI servers | Deployment | `210-python-fastapi-core.md` |
| `214-python-fastapi-monitoring.md` | Agent Requested | Health checks, logging, caching | Monitoring | `210-python-fastapi-core.md` |
| `220-python-typer-cli.md` | Agent Requested | Typer CLI development | CLI | `200-python-core.md` |
| `230-python-pydantic.md` | Agent Requested | Pydantic models/settings | Validation | `200-python-core.md` |
| `240-python-faker.md` | Agent Requested | Faker data generation | Test data | `200-python-core.md` |
| `250-python-flask.md` | Agent Requested | Flask best practices | Flask | `200-python-core.md` |
| `300-bash-scripting-core.md` | Agent Requested | Bash scripting fundamentals | Bash | `000-global-core.md` |
| `301-bash-security.md` | Agent Requested | Shell security best practices | Bash security | `300-bash-scripting-core.md` |
| `302-bash-testing-tooling.md` | Agent Requested | Shell testing & tooling | Bash testing | `300-bash-scripting-core.md` |
| `310-zsh-scripting-core.md` | Agent Requested | Zsh fundamentals | Zsh | `300-bash-scripting-core.md` |
| `311-zsh-advanced-features.md` | Agent Requested | Advanced Zsh patterns | Zsh advanced | `310-zsh-scripting-core.md` |
| `312-zsh-compatibility.md` | Agent Requested | Cross-shell compatibility | Zsh portability | `300-bash-scripting-core.md` |
| `500-data-science-analytics.md` | Agent Requested | DS/analytics practices | Analytics | `200-python-core.md` |
| `600-data-governance-quality.md` | Agent Requested | Data quality & governance | Governance | — |
| `700-business-analytics.md` | Agent Requested | Business reporting & visualization | BI | — |
| `800-project-changelog-rules.md` | Agent Requested | Changelog governance | Project mgmt | `000-global-core.md` |
| `801-project-readme-rules.md` | Agent Requested | README structure & standards | Docs | `000-global-core.md` |
| `805-project-contributing-rules.md` | Agent Requested | Contribution workflow standards | Contributing | `000-global-core.md` |
| `820-taskfile-automation.md` | Agent Requested | Taskfile automation practices | Automation | `202-yaml-config-best-practices.md` |
| `900-demo-creation.md` | Agent Requested | Demo creation directives | Demos | — |
| `UNIVERSAL_PROMPT.md` | Agent Requested | Universal response guidelines | Prompting | `000-global-core.md` |


