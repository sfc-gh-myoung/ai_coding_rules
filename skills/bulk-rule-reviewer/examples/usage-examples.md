# Usage Examples — bulk-rule-reviewer

## Basic Invocation (All Rules, Full Review)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

## Filtered Review (Snowflake Rules Only)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
filter_pattern: rules/100-*.md
```

## Force Re-Review (Overwrite Existing)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
overwrite: true
```

Use `overwrite: true` to replace existing reviews. Use `skip_existing: false`
combined with `overwrite: false` (default) to create new versions with
sequential numbering (-01, -02).

## Re-Review with Sequential Numbering (Preserve History)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: false
overwrite: false
```

This creates `-01`, `-02` versions without overwriting previous reviews.

## Staleness Check Only

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
```
