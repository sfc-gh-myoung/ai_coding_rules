# Git Commands/Notes

## Add GitLab remote origin
git remote add origin git@snow.gitlab-dedicated.com:snowflakecorp/SE/sales-engineering/ai_coding_rules.git

### Update commiter emails in repo

# If needed:
brew install git-filter-repo

git filter-repo --force --commit-callback '
    # commit.author_email and commit.committer_email are bytes
    # Use the author identity as committer if committer is not a snowflake.com address
    if not commit.committer_email == (b"michael.young@snowflake.com"):
        commit.committer_name  = commit.author_name
        commit.committer_email = commit.author_email
'

git filter-repo --force \
  --commit-callback '
good_domain = b"@snowflake.com"
if not commit.committer_email.endswith(good_domain):
    commit.committer_name  = b"Michael Young"
    commit.committer_email = b"michael.young@snowflake.com"
' \
  --tag-callback '
good_domain = b"@snowflake.com"
if tag.tagger_email and not tag.tagger_email.endswith(good_domain):
    tag.tagger_name  = b"Michael Young"
    tag.tagger_email = b"michael.young@snowflake.com"
'

## Add GitHub remote repo to GitLab repo

### From your local clone that tracks GitLab as origin
git remote add github https://github.com/sfc-gh-myoung/ai_coding_rules
git remote add github git@github.com:sfc-gh-myoung/ai_coding_rules.git

git remote -v

### If the github URL is wrong, fix it (include .git to be explicit)
git remote set-url github https://github.com/sfc-gh-myoung/ai_coding_rules.git
git remote set-url github git@github.com:sfc-gh-myoung/ai_coding_rules.git

### Verify SSH works
### If prompted to trust host, accept; you should see a success message
ssh -T git@github.com

### Full mirror (branches + tags + deletions)
git push github --mirror --prune

### One-time full sync
git push github --all
git push github --tags


## Delete the local tag
git tag -d v2.2.1

## Create the tag at the current commit
git tag -a v2.2.1 -m "v2.2.1: Feature - Remove EXAMPLE_ROMPT.md to simply rule loading logic."

## Force push the tag to remote (overwrites the old one)
git push origin v2.2.1 --force


## Squash Merge
### Switch to main:
git checkout main

### Run the squash merge command:
git merge --squash feature/login

Crucial Note: This does not create a commit immediately. It takes all the changes from that branch and stages them in your "Index" (staging area), waiting for you to commit them.

### Commit the changes:
git commit -m "Add login feature (Squashed)"

task rule:all       # Regenerate all formats
task rule:check     # Verify consistency

## Release Flow

git checkout -b feat-rule-updates
git commit -m "feat: enhance Snowflake Semantic Views documentation and integration rules

- Updated the core DDL syntax and validation rules for creating Snowflake Native Semantic Views, emphasizing the `CREATE SEMANTIC VIEW` DDL syntax.
- Added comprehensive guidance for querying Semantic Views using the `SEMANTIC_VIEW()` function, including testing strategies and validation patterns.
- Introduced integration patterns for Snowflake Semantic Views with Cortex Analyst and Cortex Agent, detailing governance and development workflows.
- Updated related templates and documentation to reflect these changes, ensuring consistency and clarity across the project."
git checkout main
git merge feat-rule-updates
git tag -a v2.4.0 -m "v2.4.0: Feature: enhance Snowflake Semantic Views documentation and integration rules"
git push origin main --tags