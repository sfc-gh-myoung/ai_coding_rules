---
schema_version: v4.0
rule_version: v5.0.0
description: "Pytest best practices: AAA pattern, fixtures, parametrization, test isolation, uv-run-pytest, and flaky-test protocol."
last_updated: 2026-10-06
keywords:
  - kw:pytest fixtures
  - kw:AAA pattern
  - kw:test parametrization
  - kw:uv run pytest
  - kw:test isolation
  - kw:flaky test protocol
token_budget: ~1200
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
    - 200-python-core.md  # Python core patterns (uv, pytest execution)
  optional:
    - 201-python-lint-format.md  # Ruff linting and formatting for test code
    - 204-python-docs.md  # Documentation standards for test docstrings
    - 205-python-classes.md  # Class patterns for test organization
---
# Python Testing with pytest

## Scope

**What This Rule Covers:**
Focused behavioral assertions, fixtures, parametrization, isolation, selection, flaky-test diagnosis and truthful coverage/test outcomes.

**When to Load This Rule:**
When writing/reviewing pytest tests, fixtures/markers, coverage or diagnosing failures/flakiness.

## Contract

### Inputs and Prerequisites

- Existing tests/conftest/config, actual Python manager/interpreter/plugins and changed behavior.
- Safe test resources and authorization for integration/live/network/database effects.

### Mandatory

- Match established project environment/automation, using locked uv pytest here; other managers are valid when the project uses them. Never infer test-suite absence from missing config alone.
- Arrange, act and assert one coherent behavior per test. Exercise public behavior/meaningful failure cases; don't merely assert implementation line structure.
- Prefer small explicit fixtures, function scope by default and broader scopes only with safe isolation/lifecycle. Use yield/finally teardown, avoid shared mutable state and unnecessary autouse/deep chains.
- Parametrize meaningful input/boundary matrices with readable IDs. Avoid duplicate cases, arbitrary ten-case caps or mocking-count quotas; matrix size should support behavior clarity.
- Control clocks/RNG/environment/filesystem with dependency injection/tmp_path/monkeypatch and capture outputs/logs with capsys/caplog. Avoid unjustified sleeps; use bounded observable synchronization for concurrency.
- Mock external boundaries for unit tests, not private implementation details merely to force coverage. Integration tests must use appropriate real components when their semantics matter, under approved scope.
- Register markers/plugins and disclose selection/deselection. Do not invoke repeat/timeout options without the plugin or silently install it.
- Skips/xfails need concrete platform/dependency/known-defect reasons and review policy. Prefer strict xfail where unexpected pass should prompt removal; never quarantine to hide a regression or fabricate fixture reports.
- Flaky diagnosis records repeat outcomes, environment/order/concurrency evidence and cause when established. Fix race/time/resource leaks, not global extra sleeps or unexplained serial markers.
- Use precise pytest.raises/type/message assertions, no broad catch/pass. Assertions/coverage must expose meaningful branches; preserve project coverage thresholds rather than imposing generic 80/90 percentages.
- All required tests/lint/format/types must run before completion; focused passes do not replace full gates. Synthetic checks are not actual pytest execution, and failed/unavailable checks cannot become passes.

### Execution Steps

1. Read affected tests/config/conftest and current behavior; run a scoped baseline when safe.
2. Add minimal regression/boundary tests with explicit fixtures and observable expected outcomes.
3. Isolate external effects, ensure deterministic cleanup, register markers and use existing plugins/environment.
4. Run affected tests, configured Python quality checks and required full suite/coverage gates.
5. Diagnose exact failures and flakiness; retain outcomes, fix owned causes and recheck. Do not stash/reset unrelated work or lower coverage to pass.
6. Report commands/results, coverage, skips/xfails/deselected live tests and unresolved verification honestly.

### Validation

- Tests fail for the demonstrated defect and pass for intended behavior; assertions meaningful and exceptions specific.
- Fixtures independent/order-safe, resources cleaned on failure, time/random/env/filesystem controlled.
- Parametrization/markers/plugins accurate; no hidden network/cloud/database side effects.
- Full required gates and actual coverage pass without gaming thresholds; selected/deselected scope explicit.
- Flaky/skip/xfail reasons supported and reviewed; no unexplained success retry or fake runtime evidence.

## References

- [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [pytest output capture](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html)
- [pytest flaky tests](https://docs.pytest.org/en/stable/explanation/flaky.html)
- [pytest skip/xfail](https://docs.pytest.org/en/stable/how-to/skipping.html)
