---
schema_version: v4.0
rule_version: v4.1.0
description: "Directives for creating realistic, deterministic demo applications: synthetic data with Faker seeding, DemoScenario configuration, narrative-aligned correlations, offline fallback resilience, and Snowflake write patterns."
last_updated: 2026-10-06
keywords:
  - kw:Faker seeded generation
  - kw:generator table function
  - kw:offline fallback resilience
  - kw:DemoScenario pattern
  - kw:narrative-aligned correlations
  - kw:progressive disclosure UI
  - kw:faker
token_budget: ~2000
context_tier: Low
depends:
  required:
    - 130-snowflake-demo-sql.md  # Demo SQL patterns
  optional:
    - 132-snowflake-demo-modeling.md  # Data modeling for demos
---
# Snowflake Demo: Creation and Synthetic Data

## Scope

**What This Rule Covers:**
Directives for realistic, deterministic demo applications. Covers synthetic data generation with Faker seeding, DemoScenario configuration, narrative-aligned correlations, offline fallback resilience, and vectorized Snowflake writes.

**When to Load This Rule:**
Load this rule when creating demo applications or proof-of-concepts, generating synthetic data for demonstrations, designing narrative-driven demos, or building reproducible demo environments.

## Contract

### Inputs and Prerequisites

- Demo narrative, target audience, and technology stack defined
- Data schema and referential integrity requirements identified
- Snowflake connection paradigm chosen: Snowpark `session` for interactive/notebook contexts; `snowflake-connector-python` for batch scripts — do not mix both in the same script

### Mandatory

**Scenario configuration:** Never hard-code record counts or an unstated date window. Use a `DemoScenario` dataclass (or equivalent) with supplied volume and date parameters in one place. A frozen clock does not imply a lookback period. If no window is supplied, describe generation requirements in prose only; omit the entire order-generator function, including stubs that raise `NotImplementedError`. Never supply runnable-looking code with a guessed window, `None` timestamp, TODO marker or invalid placeholder row. List the missing window as an implementation prerequisite. Date coverage is derived only after valid timestamps exist.

**Reproducible generation:** Seed Faker with a fixed integer (convention: `42`) via `fake.seed_instance(42)`. For time-sensitive columns, pass `reference_date` as an explicit parameter instead of calling `datetime.now()` or `CURRENT_DATE()` at generation time. Seeding guarantees reproducibility within the same library version; identical output across differing Python or Faker versions is not guaranteed. Pair seeding with a frozen reference date for time-sensitive demos.

**Batch generation:** For large datasets, yield bounded chunks or use a native generator; avoid accumulating all rows before a write. Small configured demo scenarios may fit in memory.

**Narrative-aligned correlations:** Columns representing real-world relationships (e.g., age/income, asset age/failure rate) must be correlated, not independently random. Data without realistic correlations fails demo review.

**Offline fallback:** When offline operation is required, return the same documented schema and type as the live path, or report that no valid fallback exists. Check column names, dtypes and row structure; do not claim parity without testing both paths.

**Connection paradigm:** Use Snowpark `session` for interactive and notebook contexts. Use `snowflake-connector-python` (`write_pandas`) for batch data-loading scripts. Do not mix both paradigms in the same script. Tag all writes: `ALTER SESSION SET QUERY_TAG = 'demo_data_pipeline'`.

**Write strategy:** A named or "owned target" is not proof that existing data is disposable. Do not propose overwrite as permissible until exclusive ownership, data-loss scope, and authorization are separately verified; otherwise propose a non-destructive plan. Append subsequent bounded batches only within the authorized target. Confirm the connector/session API and load outcome before claiming success.

**Error presentation:** Catch exceptions at the user boundary; present a short actionable message (e.g., `"Could not load data — check that DEMO_DB exists."`). Never expose raw stack traces to demo audiences.

```python
from dataclasses import dataclass
from faker import Faker
import pandas as pd


@dataclass
class DemoScenario:
    name: str
    reference_date: str  # e.g. "2026-10-01" -- fixed to keep demos time-stable
    customers: int = 200
    orders: int = 1000


def generate_customers(scenario: DemoScenario) -> pd.DataFrame:
    """Generate customer rows with age-income correlation."""
    fake = Faker()
    fake.seed_instance(42)
    rows = []
    for i in range(scenario.customers):
        age = fake.random_int(22, 68)
        rows.append(
            {
                "customer_id": i + 1,
                "customer_name": fake.name(),
                "age": age,
                # income correlated with age: older customers have higher baseline
                "annual_income_usd": 25000 + (age - 22) * 1800 + fake.random_int(-4000, 10000),
            }
        )
    return pd.DataFrame(rows)
```

Cache a verified live result for offline reuse only when the cache is safe and
current for the selected scenario. If the cache is absent, generate the same
documented columns and dtypes or report that no compatible offline result is
available. Test both return paths; a similar-looking DataFrame is not proof of
schema parity.

### Execution Steps

1. Verify whether a Snowflake-native solution (GENERATOR, Snowpark) meets the need before building custom infrastructure
2. Define `DemoScenario` with supplied volume parameters, fixed `reference_date`, and an explicit history window if the user specifies one; do not infer a default window from the clock
3. Implement generators with `fake.seed_instance(42)` and narrative-aligned correlations
4. If offline operation is required, add a fallback with identical column names/dtypes and test it independently; otherwise do not expand scope
5. Choose connection paradigm (session or connector-python); do not mix in the same script
6. Validate referential integrity: every FK value must exist in the parent DataFrame before writing
7. Only when separately authorized, load parent dimensions, date dimensions and facts in that order; use bounded batches when volume requires and tag the session with `QUERY_TAG`
8. When authorized, validate the actual load; test offline shape parity only when that mode is required. In design-only work, report all runtime checks unexecuted

### Validation

- Demo runs reproducibly with same `DemoScenario` and seed (within the same library version and with a fixed reference date)
- Offline fallback returns same column names, dtypes, and structure as live path
- No raw stack traces appear in demo output or UI
- Connection paradigm consistent; session and connector not mixed in same script
- Overwrite used only on first batch of an authorized disposable target
- FK integrity validated before writing to Snowflake
- Batch generation used; no single in-memory accumulation of large row sets

## References

- [Faker Documentation](https://faker.readthedocs.io/) — Synthetic data generation library
- [Snowflake GENERATOR() table function](https://docs.snowflake.com/en/sql-reference/functions/generator) — Native SQL row generation without Python
- [Snowflake Connector for Python — write_pandas](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-pandas) — Vectorized batch writes
