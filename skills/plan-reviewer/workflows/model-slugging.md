# Model Slugging Workflow

## Purpose

Normalize model names to consistent slugs for output filenames.

## Slugging Rules

1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters except hyphens and numbers
4. Collapse multiple hyphens

## Common Mappings

| Input | Slug |
|-------|------|
| `Claude Sonnet 4.5` | `claude-sonnet45` |
| `Claude Opus 4.5` | `claude-opus45` |
| `GPT-5.2` | `gpt-52` |
| `GPT-4o` | `gpt-4o` |
| `Gemini 2.0 Flash` | `gemini-20-flash` |
| `Llama 3.1 70B` | `llama-31-70b` |

## Implementation

```python
import re

def slugify_model(model_name: str) -> str:
    """Convert model name to filename-safe slug"""
    slug = model_name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[\s_]+', '-', slug)        # Spaces to hyphens
    slug = re.sub(r'-+', '-', slug)            # Collapse hyphens
    slug = slug.strip('-')
    return slug
```

## Edge Cases

| Scenario | Resolution |
|----------|------------|
| Empty model name | ERROR: "model is required" |
| Already a valid slug | Use as-is |
| Unknown model format | Apply standard slugging rules |

## Next Step

Proceed to `review-execution.md`.

