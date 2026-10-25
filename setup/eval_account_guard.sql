-- Filename: eval_account_guard.sql
-- Description: Stop before any change when connected to a different account than intended.
-- Prerequisites: None. Prepended to every generated file so each file is safe to run alone.
-- Creates: Nothing.
-- Parameters: __ACCOUNT__ is the intended ORGANIZATION-ACCOUNT name, or the account locator
-- (the part before the first dot) when EVAL_ACCOUNT is a locator; __ACCOUNT_EXPR__ is the
-- matching connected-account expression.
EXECUTE IMMEDIATE $$
DECLARE
  wrong_account EXCEPTION (-20002, 'Connected account is not the intended account; nothing was changed.');
BEGIN
  IF (UPPER(__ACCOUNT_EXPR__) != UPPER('__ACCOUNT__')) THEN
    RAISE wrong_account;
  END IF;
END;
$$;
