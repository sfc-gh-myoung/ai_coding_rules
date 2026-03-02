# AGENTS.md Evaluation Tool

**Version:** 1.0.0  
**Purpose:** Evaluate AGENTS.md effectiveness through deterministic, reproducible tests.

## Quick Start

```bash
# Run evaluation with default model (claude-sonnet-4-5)
agent-eval run

# List saved results
agent-eval list

# Compare two result files
agent-eval compare -b <baseline.yaml> -t <target.yaml>
```

**Alternative:** If `agent-eval` is not on your PATH, use the module invocation:

```bash
uv run python -m agent_eval run
```

## Module Structure

```
src/agent_eval/
├── __init__.py          # Package metadata, version
├── __main__.py          # Entry: `python -m agent_eval`
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
agent-eval run -m claude-opus-4-5 -p 5

# Run only critical priority tests
agent-eval run -P critical

# Run specific test categories
agent-eval run -C protocol_compliance,rule_discovery

# Dry run to validate test cases
agent-eval run --dry-run

# Compare two result files
agent-eval compare -b 2026-02-05_074428_claude-opus-4-5.yaml -t 2026-02-05_074428_claude-sonnet-4-5.yaml

# Generate markdown comparison report
agent-eval report -b baseline.yaml -t current.yaml
```

## Parallel Execution

Use `-p` / `--parallel` to run tests concurrently with multiple workers:

```bash
agent-eval run -p 4
```

The progress display shows:

```
⠋ Overall Progress  ████████████░░░░░░░░░░░░  60%  6/10 | ✓ 4 | ✗ 2
⠋   TC005           ━━━━━━━━━━━━━━━━━━━━━━━━       PRE-FLIGHT Gate 1 foundati...
⠋   TC008           ━━━━━━━━━━━━━━━━━━━━━━━━       MODE declaration after AUT...
⠋   TC012           ━━━━━━━━━━━━━━━━━━━━━━━━       Task Switch detection on f...
```

- **Overall Progress**: Completion percentage, count, and pass (✓) / fail (✗) totals
- **Active tests**: Individual tasks appear when a test starts executing and disappear when complete
- Up to `N` active tests shown (where `N` is the worker count)

## Available Models

List available Cortex REST API models:

```bash
agent-eval models
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
