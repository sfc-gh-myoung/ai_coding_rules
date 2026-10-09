# timing-finalize (v2.0.0+)

The `finalize` subcommand records work-complete semantics **server-side**.
Replaces the caller-defined `review_complete` checkpoint, which historically
fired before substantive markdown synthesis / file write and left the
largest cost block uninstrumented.

## Stages

| Stage | Required args | Records |
|---|---|---|
| `pre_write` | `--review-artifact <path>` | The moment after synthesized output exists in memory but before the on-disk write |
| `post_write` | (none beyond `--run-id`) | The moment after the on-disk write completes |

## Contract

```bash
python skills/skill-timer/scripts/skill_timer.py finalize \
    --run-id <id> \
    --stage pre_write \
    --review-artifact /path/to/review.md

# ... actually write the file ...

python skills/skill-timer/scripts/skill_timer.py finalize \
    --run-id <id> \
    --stage post_write
```

## Why both stages?

`pre_write` is the anchor used by the `post_review_gap` distribution
validator. The delta between `pre_write` and `post_write` becomes
`finalize_seconds` and quantifies on-disk write cost.

## Backward compatibility

If a `review_complete` checkpoint is recorded but no `finalize` stages exist,
skill-timer falls back to `review_complete` for the work-window denominator
and emits a deprecation WARNING. New callers should prefer `finalize`.
