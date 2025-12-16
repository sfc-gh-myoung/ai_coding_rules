# Workflow: Model Slugging

## Input

- `model`: either a slug (preferred) or a raw model name

## Rules

- If `model` matches: `^[a-z0-9]+(-[a-z0-9]+)*$`, use it as `model_slug`.
- Else normalize to `model_slug`:
  - lowercase
  - replace spaces and underscores with `-`
  - remove all characters other than `a-z`, `0-9`, and `-`
  - collapse repeated `-`
  - trim leading/trailing `-`

## Examples

| Input | Output |
|-------|--------|
| `claude-sonnet45` | `claude-sonnet45` |
| `Claude Sonnet 4.5` | `claude-sonnet-45` |
| `GPT-4 Turbo` | `gpt-4-turbo` |
| `gpt_4_turbo` | `gpt-4-turbo` |
| `Claude Opus 4` | `claude-opus-4` |

## Implementation

```python
import re

def normalize_model_slug(model: str) -> str:
    """Normalize model name to slug format"""
    # Check if already valid slug
    if re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', model):
        return model
    
    # Normalize
    slug = model.lower()
    slug = re.sub(r'[\s_]+', '-', slug)  # spaces/underscores to hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)  # remove invalid chars
    slug = re.sub(r'-+', '-', slug)  # collapse repeated hyphens
    slug = slug.strip('-')  # trim leading/trailing hyphens
    
    return slug
```

## Output

- `model_slug`: normalized model identifier for use in filenames

