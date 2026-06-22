# Parallel Execution Performance (doc-reviewer)

Sub-agent parallelization tradeoffs for doc-reviewer's 6-dimension evaluation.

## Performance targets

| Metric | Sequential | Parallel | Improvement |
|---|---|---|---|
| Execution time | ~12–15 min | ~3–4 min | 3–4× faster |
| Token cost | ~12K | ~72K | 6× higher |
| Context freshness | Degraded after dim 3 | Fresh for all | Better accuracy |
| Fault tolerance | Restart from beginning | Retry single dimension | Improved |

## Fallback behavior

If 3+ sub-agents fail, the skill automatically falls back to sequential execution.

## Full specs

Timeout handling, aggregation schema, edge cases, and rollback procedures: [`workflows/parallel-specs.md`](../workflows/parallel-specs.md).
