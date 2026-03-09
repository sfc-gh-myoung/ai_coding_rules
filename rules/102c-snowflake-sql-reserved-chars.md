# Snowflake SQL: Reserved Characters and CLI Compatibility

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** reserved characters, CLI compatibility, snow sql, snowsql, template expansion, ampersand, enable-templating, single-quote escaping, Jinja2, dbt
**TokenBudget:** ~1550
**ContextTier:** Low
**Depends:** 102-snowflake-sql-core.md

## Scope

**What This Rule Covers:**
Reserved character handling for Snowflake CLI tools including `snow sql`, `snowsql`, and dbt/Jinja contexts. Covers `&`, `<%`, `%>`, `{{`, `}}` template characters and SQL single-quote escaping.

**When to Load This Rule:**
- SQL files contain `&` characters (brand names, data values)
- Executing SQL via CLI tools (snow sql, snowsql)
- Template rendering errors mentioning undefined variables
- Working with dbt or Jinja SQL templates

## References

### Dependencies

**Must Load First:**
- **102-snowflake-sql-core.md** - SQL file patterns

## Contract

### Inputs and Prerequisites

- SQL file with potential reserved characters
- CLI tool being used for execution

### Mandatory

- Use `--enable-templating NONE` when SQL contains `&` characters
- Never corrupt data to work around CLI templating

### Forbidden

- Replacing `&` with `and` in data values
- Embedding template syntax in SQL string literals

### Execution Steps

1. Check SQL for reserved characters (`&`, `<%`, `%>`, `{{`, `}}`)
2. If present, add `--enable-templating NONE` to CLI command
3. For single quotes in data, use doubled single quotes (`''`)

### Output Format

SQL that executes correctly via CLI without template expansion errors.

### Validation

- No "template rendering error" messages
- Data values preserved exactly (no `&` to `and` substitution)

### Post-Execution Checklist

- [ ] `--enable-templating NONE` used for non-templated SQL with `&`
- [ ] Single quotes escaped as `''` in string literals
- [ ] No template syntax in SQL comments or literals

## Reserved Characters

**Characters that CLI tools interpret as template syntax:**
- **`&`** - `snow sql` LEGACY mode interprets as template variable prefix
- **`<%` `%>`** - `snowsql` interprets as variable delimiters
- **`{{` `}}`** - Jinja2, dbt interpret as template syntax

## Error Message Pattern

When `&` is present and templating is not disabled, `snow sql` produces these errors:
```
Warning: &{ ... } syntax is deprecated and will no longer be supported. Use <% ... %> syntax instead.
SQL template rendering error: 'W' is undefined
SQL template rendering error: 'Ms' is undefined
```

The text after `&` is treated as a variable name (e.g., `A&W` becomes variable `W`, `M&Ms` becomes variable `Ms`).

## The Fix: `--enable-templating NONE`

**Do NOT replace `&` with `and` in data.** That corrupts real brand names, product descriptions, and other data that legitimately contains `&`.

The correct fix is to disable client-side template expansion at the CLI layer:

```bash
# Correct: disable templating so & is passed through to Snowflake
snow sql --enable-templating NONE -c my_connection -f sql/03_seed_data.sql

# In Python wrappers, add the flag to the command builder:
cmd = [*get_snow_command(), "sql", "--enable-templating", "NONE", "-c", connection]
```

`--enable-templating NONE` should be the default for all non-templated SQL execution. Only use LEGACY or other modes when you actually need client-side variable expansion.

## Incorrect Approach (Data Substitution)

```sql
-- WRONG: Do NOT corrupt data to work around CLI templating
INSERT INTO products (name, brand) VALUES
('M and Ms Milk Chocolate 1.69oz', 'M and Ms'),  -- WRONG: corrupts brand name
('A and W Root Beer 20oz', 'A and W'),             -- WRONG: corrupts brand name
('PB and J Sandwich on White', 'Fresh');           -- WRONG: corrupts product name
```

## Correct Approach (Disable Templating)

```sql
-- CORRECT: Keep real brand names with &, execute with --enable-templating NONE
INSERT INTO products (name, brand) VALUES
('M&Ms Milk Chocolate 1.69oz', 'M&Ms'),
('A&W Root Beer 20oz', 'A&W'),
('PB&J Sandwich on White', 'Fresh');
```

## When Templating Cannot Be Disabled

For `<%` `%>` in `snowsql` or `{{` `}}` in dbt/Jinja contexts where you cannot disable templating, avoid these characters in SQL comments and string literals. Use the `--variable` flag or dbt `var()` for actual variable substitution instead of embedding template syntax in SQL.

## SQL Single-Quote Escaping

Brand names with apostrophes (e.g., Frank's RedHot) must use doubled single quotes inside SQL string literals:

```sql
-- Correct: apostrophe escaped as '' inside SQL string
INSERT INTO products (name, brand) VALUES
('Frank''s RedHot Original Cayenne Pepper Sauce 5oz', 'Frank''s RedHot');
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Data Corruption to Avoid Template Errors

**Problem:** Replacing `&` with `and` in data values instead of disabling CLI templating. This corrupts real brand names and product data.

**Correct Pattern:** Use `--enable-templating NONE` and keep data intact.

```sql
-- Wrong: corrupting data to work around CLI template expansion
INSERT INTO products (name, brand) VALUES
('M and Ms Milk Chocolate 1.69oz', 'M and Ms'),
('A and W Root Beer 20oz', 'A and W');

-- Correct: keep real brand names, execute with --enable-templating NONE
-- Run as: snow sql --enable-templating NONE -c my_connection -f seed_data.sql
INSERT INTO products (name, brand) VALUES
('M&Ms Milk Chocolate 1.69oz', 'M&Ms'),
('A&W Root Beer 20oz', 'A&W');
```

### Anti-Pattern 2: Missing Single-Quote Escaping

**Problem:** Unescaped apostrophes in string literals cause SQL syntax errors or silently truncate data.

**Correct Pattern:** Double single quotes (`''`) to escape apostrophes inside SQL strings.

```sql
-- Wrong: unescaped apostrophe breaks the SQL string
INSERT INTO products (name, brand) VALUES
('Frank's RedHot Original Cayenne Pepper Sauce 5oz', 'Frank's RedHot');

-- Correct: doubled single quotes to escape the apostrophe
INSERT INTO products (name, brand) VALUES
('Frank''s RedHot Original Cayenne Pepper Sauce 5oz', 'Frank''s RedHot');
```
