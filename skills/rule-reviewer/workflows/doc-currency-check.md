# Workflow: Documentation Currency Check

## Purpose

Verify that external documentation links in rules don't contain deprecation warnings that indicate stale guidance.

## Prerequisites

- Rule file loaded
- External Documentation section identified
- `web_fetch` tool available

## Inputs

- `rule_content`: Full text of rule file
- `review_date`: Current review date (for context)

## Steps

### 1. Extract Documentation Links

Parse rule for `## External Documentation` or `### External Documentation` section.

**If section not found:**
- Note: "No External Documentation section - skipping currency check"
- Return: 0 penalty, 0 links scanned

**If section found:**
- Extract all URLs (markdown links and bare URLs)
- Deduplicate

### 2. Fetch Each Link

For each URL:

```
web_fetch(url, extract_text=true)
```

**On success:**
- Store extracted text for scanning
- Record: URL, fetch status "OK", content length

**On failure:**
- Record: URL, fetch status "[error type]", skip scanning
- Continue to next URL

### 3. Scan for Deprecation Signals

For each successfully fetched page:

**Search patterns (case-insensitive):**

```python
HIGH_CONFIDENCE = [
    r'\bdeprecated\b.{0,100}\b(function|method|api|endpoint|feature|parameter)\b',
    r'\bend[- ]of[- ]life\b',
    r'\bEOL\b',
    r'\bsunset(ted|ting)?\b',
    r'\bno longer supported\b',
    r'\bremoved in (version|v)?\s*\d',
    r'\bbreaking change\b',
]

MEDIUM_CONFIDENCE = [
    r'\blegacy\b.{0,50}\b(api|method|approach)\b',
    r'\breplaced by\b',
    r'\bsuperseded by\b',
    r'\bwill be removed\b',
    r'\bscheduled for removal\b',
]
```

**For each match:**
1. Extract 200-char context window around match
2. Check false positive filters:
   - Is this in a "Migration" or "Upgrading" section? → Skip
   - Does context mention a different product? → Skip
3. If not filtered: Record signal with context

### 4. Calculate Penalty

```python
total_signals = high_confidence_count + (medium_confidence_count * 0.5)

if total_signals == 0:
    penalty = 0
elif total_signals <= 1.5:
    penalty = -0.5
elif total_signals <= 3:
    penalty = -1
else:
    penalty = -2
```

### 5. Handle Incomplete Checks

```python
links_total = len(all_urls)
links_failed = len(failed_fetches)

if links_failed / links_total > 0.5:
    # More than half failed - don't penalize
    penalty = 0
    note = "Documentation currency check incomplete (>50% fetch failures)"
```

## Output

```python
{
    "links_scanned": int,
    "links_failed": int,
    "signals_found": [
        {"url": str, "signal": str, "context": str, "confidence": "high"|"medium"}
    ],
    "penalty": float,  # 0, -0.5, -1, or -2
    "notes": [str]
}
```

## Example Output

```markdown
**Documentation Currency Check:**
- Links scanned: 4 (1 failed: timeout)
- Deprecation signals: 2

| URL | Signal | Confidence | Context |
|-----|--------|------------|---------|
| docs.streamlit.io/... | "deprecated" | High | "...`use_container_width` is deprecated, use `width='stretch'`..." |
| plotly.com/... | "will be removed" | Medium | "...legacy trace types will be removed in v6..." |

**Penalty:** -1 point

**Notes:**
- https://altair-viz.github.io/ - Timeout, unable to verify
```

## Integration with Staleness Rubric

This workflow is called during staleness scoring, after the basic link status check:

1. Check link HTTP status (existing)
2. **Run documentation currency check (new)**
3. Combine scores:
   - Base staleness score from LastUpdated + deprecated tools + patterns + broken links
   - Apply documentation currency penalty (max -2 points)
   - Floor at 2 points (1/5 minimum)
