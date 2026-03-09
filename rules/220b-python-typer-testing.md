# Python Typer CLI Testing Strategies

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Typer, CLI testing, CliRunner, ANSI escape codes, NO_COLOR, pytest, CLI integration testing, mock
**TokenBudget:** ~1450
**ContextTier:** Medium
**Depends:** 220-python-typer-cli.md, 206-python-pytest.md
**LoadTrigger:** kw:cli-testing, kw:clirunner

## Scope

**What This Rule Covers:**
Testing strategies for Typer CLI applications including CliRunner setup, ANSI escape code suppression, integration testing, and mocking external dependencies.

**When to Load This Rule:**
- Writing tests for Typer CLI commands
- Debugging ANSI escape codes in test output
- Setting up CLI integration tests
- Mocking external dependencies in CLI tests

## References

### Dependencies

**Must Load First:**
- **220-python-typer-cli.md** - Core Typer CLI patterns
- **206-python-pytest.md** - Pytest patterns

**Related:**
- **220c-python-typer-rich.md** - Rich integration (affects test output)

## Contract

### Inputs and Prerequisites

- Typer CLI application (from 220-python-typer-cli.md)
- pytest installed: `uv add --group dev pytest`

### Mandatory

- **Critical:** Configure CliRunner with `env={"NO_COLOR": "1", "TERM": "dumb"}` to disable ANSI escape codes
- **Always:** Test both success and failure scenarios
- **Rule:** Mock external dependencies and file system operations
- **Always:** Use temporary directories for file operations

### Forbidden

- Testing CLI output without disabling ANSI codes (assertions will fail)
- Testing only happy paths (must test error exit codes)

### Execution Steps

1. Create shared CliRunner fixture in conftest.py with ANSI suppression
2. Write tests for each command covering success and failure
3. Mock external dependencies (APIs, databases)
4. Use tmp_path for file system tests
5. Verify exit codes match expected values

### Output Format

pytest test files with CliRunner-based CLI tests, proper ANSI suppression, and comprehensive coverage.

### Validation

**Pre-Task-Completion Checks:**
- [ ] CliRunner configured with NO_COLOR and TERM=dumb
- [ ] All commands tested for success and failure paths
- [ ] Exit codes verified in assertions
- [ ] External dependencies mocked

**Negative Tests:**
- CliRunner without NO_COLOR (assertions should fail due to ANSI codes)
- Missing exit code test (error conditions should return non-zero)

### Design Principles

- **Clean Output:** Always suppress ANSI for reliable assertions
- **Isolation:** Mock external deps, use temp directories
- **Coverage:** Test all exit code paths

### Post-Execution Checklist

- [ ] CliRunner fixture with ANSI suppression in conftest.py
- [ ] Success and failure tests for each command
- [ ] Exit codes verified
- [ ] External dependencies mocked
- [ ] File operations use tmp_path

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: ANSI Escape Codes Breaking Test Assertions

**Problem:** Tests using CliRunner fail with cryptic assertion errors because Rich/Typer emit ANSI escape codes in output.

**Why It Fails:** Rich automatically detects terminal capabilities and adds ANSI codes. In CI or testing, these codes break string assertions:
```
AssertionError: assert "--dry-run" in "\x1b[1m-\x1b[0m\x1b[1m-dry\x1b[0m\x1b[1m-run\x1b[0m"
```

**Correct Pattern:**
```python
# BAD: No environment configuration - ANSI codes leak into output
runner = CliRunner()
result = runner.invoke(app, ["--help"])
assert "--dry-run" in result.stdout  # FAILS! Contains \x1b[1m...

# GOOD: Configure environment to disable ANSI codes
runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})
result = runner.invoke(app, ["--help"])
assert "--dry-run" in result.stdout  # Works! Clean text output
```

**Why Both Variables Are Needed:**
- `NO_COLOR=1`: Disables color output (standard convention)
- `TERM=dumb`: Disables ALL Rich formatting including bold, dim, and reset codes

Using only `NO_COLOR` still allows bold/dim formatting in Typer's Rich-formatted help text.

### Anti-Pattern 2: Testing Without Exit Code Verification

**Problem:** Tests check output text but not exit codes, missing silent failures.

**Correct Pattern:**
```python
# BAD: Only checks output
result = runner.invoke(app, ["process", "missing.txt"])
assert "Error" in result.stdout

# GOOD: Checks both output and exit code
result = runner.invoke(app, ["process", "missing.txt"])
assert result.exit_code != 0
assert "Error" in result.stdout
```

## Testing Patterns

### Shared CliRunner Fixture

```python
# conftest.py
import pytest
from typer.testing import CliRunner

@pytest.fixture
def runner() -> CliRunner:
    """CliRunner with ANSI codes disabled for clean test assertions."""
    return CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})
```

### Unit Testing Commands

```python
from myapp.cli.main import app

def test_process_command_success(runner, tmp_path):
    """Test successful file processing."""
    input_file = tmp_path / "input.txt"
    input_file.write_text("test data")

    result = runner.invoke(app, ["data", "process", str(input_file)])

    assert result.exit_code == 0
    assert "Processing" in result.stdout

def test_process_command_missing_file(runner):
    """Test error handling for missing input file."""
    result = runner.invoke(app, ["data", "process", "nonexistent.txt"])

    assert result.exit_code != 0
    assert "does not exist" in result.stdout
```

### Mocking External Dependencies

```python
from unittest.mock import patch

@patch('myapp.core.services.external_api_call')
def test_command_with_mock(mock_api, runner):
    """Test command with external dependencies."""
    mock_api.return_value = {"status": "success"}
    result = runner.invoke(app, ["data", "sync"])
    assert result.exit_code == 0
```

### Integration Testing

```python
def test_complete_pipeline(runner, tmp_path):
    """Test complete workflow end-to-end."""
    input_file = tmp_path / "input.json"
    input_file.write_text('{"test": "data"}')

    result = runner.invoke(app, ["process", str(input_file)])
    assert result.exit_code == 0
```
