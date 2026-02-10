# AGENTS.md Evaluation Tool

**Version:** 1.0.0  
**Purpose:** Evaluate AGENTS.md effectiveness through deterministic, reproducible tests.

## Quick Start

```bash
# From ai_coding_rules root directory:

# Run evaluation with default model (claude-sonnet-4-5)
uv run python -m tools.agent_eval run

# Or using the installed command:
uv run agent-eval run

# List saved results
uv run python -m tools.agent_eval list

# Compare two result files
uv run python -m tools.agent_eval compare -b <baseline.yaml> -t <target.yaml>
```

## Module Structure

```
tools/agent_eval/
├── __init__.py          # Package metadata, version
├── __main__.py          # Entry: `python -m tools.agent_eval`
├── cli.py               # Typer app with commands
├── evaluator.py         # Core CortexEvaluator class
├── models.py            # Data models and constants
├── parsers.py           # Response parsing (extract_fields, etc.)
├── cortex.py            # Snowflake Cortex API client
├── test_cases.yaml      # Test definitions
├── py.typed             # PEP 561 marker for type hints
└── results/             # Output directory (gitignored)
```

## CLI Commands

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--connection` | `-c` | Snowflake connection name (default: `default`) |
| `--verbose` | `-v` | Show verbose debug output |
| `--agents` | `-a` | Path to AGENTS.md file (default: `../../AGENTS.md`) |

### Commands

- **`run`** - Run automated evaluation via Snowflake Cortex
- **`models`** - List available Cortex models from Snowflake
- **`list`** - List all saved result files
- **`show`** - Show details of a single result file
- **`compare`** - Compare two result files (requires `-b` and `-t`)
- **`report`** - Generate markdown comparison report (requires `-b` and `-t`)

## Example Usage

```bash
# Run all tests with parallel workers
uv run python -m tools.agent_eval run -m claude-opus-4-5 -p 5

# Run only critical priority tests
uv run python -m tools.agent_eval run -P critical

# Run specific test categories
uv run python -m tools.agent_eval run -C protocol_compliance,rule_discovery

# Dry run to validate test cases
uv run python -m tools.agent_eval run --dry-run

# Compare two result files
uv run python -m tools.agent_eval compare -b 2026-02-05_074428_claude-opus-4-5.yaml -t 2026-02-05_074428_claude-sonnet-4-5.yaml

# Generate markdown comparison report
uv run python -m tools.agent_eval report -b baseline.yaml -t current.yaml
```

## Available Models

List available Cortex REST API models:

```bash
uv run python -m tools.agent_eval models
```

**Important:** This shows models available for the Cortex REST API (`/api/v2/cortex/inference:complete`). The SQL `COMPLETE()` function has a different (typically larger) set of models. There is no programmatic API to query REST API model availability, so the list is manually maintained.

> **Note:** Model availability varies by region. Set `CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION'` for full access.

**Recommendations:**
- **Highest quality:** `claude-sonnet-4-5`, `claude-4-sonnet`, `openai-gpt-4.1`
- **Large reasoning:** `deepseek-r1`, `llama3.1-405b`
- **Cost-effective:** `llama3.1-70b`, `mistral-large2`

See [Cortex REST API Model Availability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api#model-availability) for current availability.

## Configuration

The tool reads Snowflake connection details from `~/.snowflake/connections.toml`:

```toml
[default]
account = "your-account.us-east-1"
token = "your-pat-token"
```

## Dependencies

Install with optional dependencies:

```bash
uv pip install -e ".[agent-eval]"
```

Or ensure dev dependencies are available:

```bash
uv sync --group dev
```

## Output Format

Results are saved as YAML files in `results/` with the following structure:

- **metadata**: Model, timestamp, agents file, total duration
- **summary**: Pass rate, total/passed/failed counts
- **results**: Per-test details including:
  - `test_id`, `passed`, `score`
  - `model_response` (truncated)
  - `request_id` - Snowflake query UUID for debugging
  - `duration_seconds`

The `request_id` can be used to look up query details in Snowflake's query history.
