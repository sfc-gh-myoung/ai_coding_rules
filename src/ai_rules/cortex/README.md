# `ai_rules.cortex`

A small functional client for Snowflake Cortex completions. Used by
`ai-rules rule-loader keywords` (and available to any future `ai-rules` command that
needs LLM access).

## Public API

```python
from ai_rules.cortex import (
    complete,           # single prompt
    complete_batch,     # many prompts in one round trip
    verify_connection,  # smoke-test the underlying Snowflake session
    list_models,        # curated, validated model ids
    CortexResponse,     # frozen dataclass: text + request_id
    DEFAULT_MODEL,      # "claude-sonnet-4-5"
    KEYWORDS_SCHEMA,    # JSON schema for keyword extraction (structured outputs)
    SUPPORTED_MODELS,   # tuple of validated model ids
)
```

## Transports

Two transports are supported. Pass `transport=...` to either entry point.

| Transport | When to use | Structured outputs (`response_schema`) |
|-----------|-------------|----------------------------------------|
| `aisql` (default) | Production. Issues `SELECT AI_COMPLETE(...)` via `snowflake-connector-python`. Reuses your `connections.toml` auth. | Supported |
| `rest` | Fallback for environments where `AI_COMPLETE` is unavailable. Calls the `/api/v2/cortex/inference:complete` HTTP endpoint with PAT auth. | Not supported |

## Examples

### Single prompt with a JSON schema

```python
import json
from ai_rules.cortex import complete, KEYWORDS_SCHEMA

resp = complete(
    "Summarize this rule into 5-15 keywords as JSON: ...",
    response_schema=KEYWORDS_SCHEMA,
)
print(json.loads(resp.text)["keywords"])
```

### Batched prompts (one SQL statement per `chunk_size` prompts)

```python
from ai_rules.cortex import complete_batch, KEYWORDS_SCHEMA

prompts = [(rule_path, build_prompt(rule_path)) for rule_path in rules]
responses = complete_batch(
    prompts,
    response_schema=KEYWORDS_SCHEMA,
    chunk_size=20,
)
for path, resp in responses.items():
    ...
```

### Pinning a model and connection

```python
from ai_rules.cortex import complete

complete(
    "Hello, Cortex.",
    model="claude-opus-4-7",
    connection_name="snowhouse_sso",
)
```

### Letting the connector resolve the default connection

Pass `connection_name=None` (the default). The connector resolves in this
order: `SNOWFLAKE_DEFAULT_CONNECTION_NAME` env var →
`default_connection_name` in `~/.snowflake/config.toml` → the literal
connection named `"default"`.

```python
import os
os.environ["SNOWFLAKE_DEFAULT_CONNECTION_NAME"] = "snowhouse_sso"
complete("Hello, Cortex.")  # uses snowhouse_sso
```

## Defaults

| Constant | Value |
|----------|-------|
| `DEFAULT_MODEL` | `claude-sonnet-4-5` |
| `DEFAULT_TEMPERATURE` | `0.0` |
| `DEFAULT_MAX_TOKENS` | `500` |
| `DEFAULT_MAX_RETRIES` | `3` |
| `DEFAULT_BATCH_CHUNK_SIZE` | `20` |
| `DEFAULT_TIMEOUT_SECONDS` | `30.0` |

## Module layout

```
src/ai_rules/cortex/
├── __init__.py     # public re-exports
├── client.py       # complete() / complete_batch() / verify_connection() / list_models()
├── transport.py    # _complete_via_aisql() / _complete_via_rest() (private)
├── models.py       # CortexResponse, defaults, KEYWORDS_SCHEMA, SUPPORTED_MODELS
└── README.md       # this file
```
