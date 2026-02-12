# Prompt Evaluation Tool

**Version:** 1.0.0
**Purpose:** Evaluate and improve prompts for LLM/agent execution quality across 6 dimensions.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

> Universal prompt evaluation tool that scores prompts on actionability, completeness, token efficiency, cross-agent consistency, parsability, and context grounding, then generates improved versions optimized for any LLM or coding agent.

## Quick Overview

**What:** Analyzes prompts across 6 weighted dimensions (100-point scale) and rewrites them for better agent execution
**Works with:** Any LLM or coding agent (GPT, Claude, Gemini, Cursor, Cline, Claude Code, Gemini CLI, GitHub Copilot)
**Deploy:** `pip install` + one command
**Interfaces:** CLI, REST API, and web UI

**Quick Checklist:**

- [ ] Snowflake connection configured? See [Configuration](#configuration)
- [ ] Ready to evaluate? See [Quick Start](#quick-start)
- [ ] Want to understand scoring? See [Scoring Dimensions](#scoring-dimensions)
- [ ] Building integrations? See [REST API](#rest-api)

## Quick Start

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/) (recommended)

```bash
# Install with prompt-eval dependencies
uv pip install -e ".[prompt-eval]"

# Evaluate a prompt from a file
uv run prompt-eval eval prompt.txt

# Evaluate from stdin
echo "Write a function that parses JSON" | uv run prompt-eval eval -

# Start the web UI
uv run prompt-eval api
```

**What just happened?**

- `eval` analyzed your prompt across 6 dimensions and generated a score (0-100, letter grade A-F)
- An improved version of the prompt was generated with explanations of changes
- `api` started a local web server at `http://127.0.0.1:8000` with an interactive evaluation form

**Alternative:** If `prompt-eval` is not on your PATH, use the module invocation:

```bash
uv run python -m tools.prompt_eval eval prompt.txt
```

## Usage

### Evaluating Prompts

The `eval` command accepts a file path or `-` for stdin:

```bash
# From file
uv run prompt-eval eval my_prompt.md

# From stdin (pipe from another command)
cat system_prompt.txt | uv run prompt-eval eval -

# Skip the rewrite step (evaluation only)
uv run prompt-eval eval prompt.txt --no-rewrite

# Use a specific model
uv run prompt-eval eval prompt.txt --model openai-gpt-5

# Save results to a file
uv run prompt-eval eval prompt.txt --format json --save
```

### Output Formats

Use `--format` to control output:

| Format | Flag | Description |
|--------|------|-------------|
| Markdown | `--format markdown` | Rich terminal tables with color (default) |
| JSON | `--format json` | Machine-readable structured output |
| HTML | `--format html` | Standalone dark-theme report with progress bars |

```bash
# JSON output piped to jq
uv run prompt-eval eval prompt.txt --format json | jq '.evaluation.grade'

# Save HTML report
uv run prompt-eval eval prompt.txt --format html --save
```

Saved results go to `tools/prompt_eval/results/` with timestamped filenames.

### CLI Reference

| Command | Description |
|---------|-------------|
| `eval <source>` | Evaluate a prompt (file path or `-` for stdin) |
| `models` | List available Cortex models |
| `api` | Start the FastAPI web server |

**`eval` Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--format` | `-f` | `markdown` | Output format: markdown, json, html |
| `--model` | `-m` | `claude-sonnet-4-5` | Cortex model for analysis |
| `--connection` | `-c` | `default` | Snowflake connection name |
| `--rewrite/--no-rewrite` | `-r` | `--rewrite` | Generate improved prompt |
| `--save` | `-s` | off | Save results to file |
| `--verbose` | `-v` | off | Show detailed output |

**`api` Options:**

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--host` | `-h` | `127.0.0.1` | Host to bind to |
| `--port` | `-p` | `8000` | Port to bind to |
| `--reload` | | off | Enable auto-reload for development |

## Scoring Dimensions

Prompts are evaluated across 6 dimensions plus 1 bonus, totaling 100 points:

| Dimension | Max Points | Weight | What It Measures |
|-----------|-----------|--------|------------------|
| **Actionability** | 25 | x5 | Clear, unambiguous instructions an agent can execute without guessing |
| **Completeness** | 25 | x5 | All necessary context, constraints, and expected outputs included |
| **Token Efficiency** | 10 | x2 | Concise without redundancy; no wasted context window space |
| **Cross-Agent Consistency** | 10 | x2 | Works reliably across different LLMs and coding agents |
| **Consistency** | 10 | x2 | Internal coherence; no contradictions between sections |
| **Parsability** | 10 | x2 | Structured formatting that agents can reliably parse |
| **Context Grounding** | 10 (bonus) | x1 | References concrete files, functions, or project context |

**Grading Scale:**

| Grade | Score Range |
|-------|-------------|
| A | 90-100 |
| B | 80-89 |
| C | 70-79 |
| D | 60-69 |
| F | Below 60 |

### Design Priorities

The scoring system follows these priorities (matching the tool's own design):

1. **P1 CRITICAL:** Agent understanding and execution reliability
2. **P2 HIGH:** Rule discovery efficacy and determinism
3. **P3 HIGH:** Context window and token utilization efficiency
4. **P4 LOW:** Human developer maintainability

This means a prompt that is perfectly readable by humans but ambiguous to agents will score lower than one optimized for agent execution.

## REST API

Start the API server:

```bash
uv run prompt-eval api --port 8080
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/models` | List available models |
| `POST` | `/api/evaluate` | Evaluate a prompt |
| `GET` | `/docs` | OpenAPI (Swagger) documentation |
| `GET` | `/redoc` | ReDoc documentation |

### Evaluate a Prompt

```bash
curl -X POST http://localhost:8080/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function that validates email addresses",
    "model": "claude-sonnet-4-5",
    "rewrite": true
  }'
```

**Response structure:**

```json
{
  "evaluation": {
    "original_prompt": "...",
    "total_score": 85.0,
    "max_score": 100,
    "grade": "B",
    "dimension_scores": [
      {
        "dimension": "Actionability",
        "raw_score": 8,
        "points": 20.0,
        "max_points": 25,
        "issues": [],
        "recommendations": ["..."]
      }
    ],
    "model": "claude-sonnet-4-5",
    "timestamp": "2026-02-11T10:30:00"
  },
  "improved": {
    "improved_text": "...",
    "changes_made": ["Added explicit return type specification", "..."],
    "priority_alignment": {"P1": ["Added concrete function signature"], "P2": ["..."]},
    "explanation": "Restructured for agent execution clarity"
  }
}
```

## Web UI

The web interface provides an interactive form for evaluating prompts without the command line:

```bash
uv run prompt-eval api
# Open http://127.0.0.1:8000/ui in your browser
```

**Features:**

- Prompt textarea with monospace editing
- Model selector dropdown
- Real-time evaluation via HTMX (no page reloads)
- Score summary with color-coded grade circle
- Dimension score cards with progress bars
- Issues list with severity badges
- Improved prompt display with copy-to-clipboard
- Dark theme, responsive layout

The root URL (`/`) also serves the evaluation form.

## Module Structure

```
tools/prompt_eval/
├── __init__.py          # Package exports, version
├── __main__.py          # Entry: `python -m tools.prompt_eval`
├── cli.py               # Typer CLI (eval, models, api commands)
├── evaluator.py         # PromptEvaluator - scores across dimensions
├── rewriter.py          # PromptRewriter - generates improved prompts
├── dimensions.py        # 7 dimension definitions, patterns, weights
├── models.py            # Data models, constants, supported models
├── cortex.py            # Snowflake Cortex client (REST + SQL)
├── formatters.py        # Markdown, JSON, HTML output formatters
├── api.py               # FastAPI server with Jinja2 templates
├── py.typed             # PEP 561 marker
├── templates/
│   ├── base.html        # Layout with HTMX, nav, footer
│   ├── index.html       # Evaluation form
│   └── partials/
│       ├── results.html # Score cards, issues, improved prompt
│       ├── loading.html # Spinner animation
│       └── error.html   # Error display
├── static/
│   └── styles.css       # Dark theme stylesheet
└── results/             # Saved evaluation output (gitignored)
```

## Configuration

The tool connects to Snowflake Cortex for LLM-powered evaluation. Configure your connection in `~/.snowflake/connections.toml`:

```toml
[default]
account = "your-account.us-east-1"
token = "your-pat-token"
```

Use `--connection` to specify a named connection:

```bash
uv run prompt-eval eval prompt.txt --connection my_connection
```

**Without a Snowflake connection**, the tool falls back to pattern-matching evaluation (regex-based scoring without LLM analysis). This provides basic scoring but less nuanced feedback.

## Available Models

```bash
uv run prompt-eval models
```

| Model | Provider |
|-------|----------|
| `claude-sonnet-4-5` (default) | Anthropic |
| `claude-opus-4-5` | Anthropic |
| `claude-haiku-4-5` | Anthropic |
| `openai-gpt-5` | OpenAI |
| `openai-gpt-5-mini` | OpenAI |
| `openai-gpt-5-nano` | OpenAI |
| `llama4-maverick` | Meta |
| `llama3.1-405b` | Meta |
| `llama3.1-70b` | Meta |
| `llama3.1-8b` | Meta |
| `mistral-large2` | Mistral |
| `mistral-large` | Mistral |

Model availability varies by Snowflake region. Set `CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION'` for full access.

## Tutorial: Improving a Prompt Step by Step

This walkthrough shows how to take a vague prompt and iteratively improve it using the tool.

### Step 1: Write an Initial Prompt

Create a file called `my_prompt.txt`:

```text
Write a function that processes user data and returns the results. Make sure it handles errors and edge cases properly. The code should be well-documented.
```

### Step 2: Run the Evaluation

```bash
uv run prompt-eval eval my_prompt.txt --verbose
```

**Expected output** (truncated):

```
Score: 62.0/100.0 (D)
Issues: 4

Dimension Scores:
  Actionability      12.5 / 25   "processes" is vague - what operation?
  Completeness       12.5 / 25   Missing: input format, return type, language
  Token Efficiency    8.0 / 10   "Make sure" is filler
  Cross-Agent        10.0 / 10   No agent-specific constructs
  Consistency        10.0 / 10   No contradictions
  Parsability         7.0 / 10   No structure (headers, lists, constraints)
  Context Grounding   2.0 / 10   No file/function references
```

The tool identified that the prompt is too vague for reliable agent execution.

### Step 3: Review the Improved Version

With `--rewrite` (default), the tool generates an improved version:

```text
Write a Python function `process_user_records` that:

1. Accepts a list of dictionaries, each containing keys: "name" (str),
   "email" (str), "age" (int)
2. Validates each record:
   - "name" must be non-empty
   - "email" must contain "@" and "."
   - "age" must be between 0 and 150
3. Returns a tuple of (valid_records: list[dict], errors: list[str])
4. Include type hints and a docstring with examples

Handle edge cases:
- Empty input list: return ([], [])
- None values: add to errors list with field name
- Duplicate emails: keep first occurrence, add duplicates to errors

File: src/utils/user_processing.py
```

### Step 4: Evaluate the Improved Version

Save the improved prompt and re-evaluate:

```bash
uv run prompt-eval eval improved_prompt.txt
```

**Expected result:** Score jumps from D (62) to A (92+), with specific improvements in Actionability, Completeness, and Context Grounding.

### Key Takeaways

1. **Be specific about the operation** ("validates and filters" vs "processes")
2. **Specify input/output types** explicitly
3. **List constraints as numbered items** for parsability
4. **Include edge cases** as a separate section
5. **Reference concrete files** when possible for context grounding
6. **Avoid filler phrases** like "make sure", "should be", "properly"

## Dependencies

Install with optional dependencies:

```bash
uv pip install -e ".[prompt-eval]"
```

Required packages:

- `typer` - CLI framework
- `rich` - Terminal formatting
- `requests` - HTTP client for Cortex REST API
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `jinja2` - Template engine
- `python-multipart` - Form data parsing

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.

**Quick reference:**

```bash
uvx ruff check tools/prompt_eval/   # Lint
uv run prompt-eval eval prompt.txt   # Test CLI
uv run prompt-eval api               # Test web UI
```

## License

This project is licensed under the Apache 2.0 License. See [LICENSE](../../LICENSE) for details.
