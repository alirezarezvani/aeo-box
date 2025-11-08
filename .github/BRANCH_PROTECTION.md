# Branch Protection Rules

This document outlines the branch protection rules that must be configured in the GitHub repository settings to enforce the AEO Box branching strategy.

## Overview

AEO Box uses a strict branching strategy to maintain code quality and stability:

```
feature/bugfix/docs/hotfix branches → dev → main
```

- **main**: Production-ready code, protected, no direct commits
- **dev**: Integration branch, protected, feature branches merge here
- **feature/bugfix/docs/hotfix branches**: Created from issues, merged to dev, auto-deleted after merge

## Required GitHub Settings

Navigate to: **Settings** → **Branches** → **Branch protection rules**

### 1. Protection Rule for `main` Branch

Click "Add rule" and configure:

#### Branch Name Pattern
```
main
```

#### Protect Matching Branches

**☑ Require a pull request before merging**
- ☑ Require approvals: `1` (minimum)
- ☑ Dismiss stale pull request approvals when new commits are pushed
- ☐ Require review from Code Owners (optional, if using CODEOWNERS file)
- ☑ Restrict who can dismiss pull request reviews (optional)

**☑ Require status checks to pass before merging**
- ☑ Require branches to be up to date before merging
- Status checks to require (add these if available):
  - `PR Branch Enforcement`
  - `tests` (if you have test workflows)
  - `lint` (if you have linting workflows)

**☑ Require conversation resolution before merging**
- Ensures all review comments are addressed

**☐ Require signed commits** (optional but recommended for production)

**☑ Require linear history**
- Prevents merge commits, keeps history clean

**☐ Require merge queue** (optional, for high-traffic repos)

**☑ Require deployments to succeed before merging** (if using GitHub deployments)

**☑ Lock branch**
- Prevents ANY pushes, including from admins
- Makes the branch read-only except via PRs

**☐ Do not allow bypassing the above settings** (recommended)
- Even admins must follow the rules

**☑ Restrict who can push to matching branches**
- Add restriction: Select specific people/teams who can push (typically none, or only CI/CD service accounts)
- Or leave empty to prevent all direct pushes

**☑ Allow force pushes** → **☐ Everyone** (DISABLE - never allow force pushes to main)

**☑ Allow deletions** → **☐** (DISABLE - prevent branch deletion)

### 2. Protection Rule for `dev` Branch

Click "Add rule" and configure:

#### Branch Name Pattern
```
dev
```

#### Protect Matching Branches

**☑ Require a pull request before merging**
- ☑ Require approvals: `1` (minimum)
- ☐ Dismiss stale pull request approvals when new commits are pushed
- ☐ Require review from Code Owners (optional)

**☑ Require status checks to pass before merging**
- ☑ Require branches to be up to date before merging
- Status checks to require:
  - `PR Branch Enforcement`
  - `tests`
  - `lint`

**☑ Require conversation resolution before merging**

**☐ Require signed commits** (optional)

**☐ Require linear history** (optional for dev, required for main)

**☐ Require merge queue** (optional)

**☐ Lock branch** (not recommended for dev - allow maintainer pushes if needed)

**☐ Do not allow bypassing the above settings**

**☑ Restrict who can push to matching branches**
- Add maintainers/core team members
- Or use rulesets to allow specific push patterns

**☑ Allow force pushes** → **☐ Everyone** (DISABLE - prevent force pushes)

**☑ Allow deletions** → **☐** (DISABLE - prevent branch deletion)

### 3. Protection Rule for Feature Branches (Optional)

This is optional but can help enforce standards on feature branches.

#### Branch Name Pattern
```
feature/*
bugfix/*
docs/*
hotfix/*
```

#### Protect Matching Branches

**☑ Require a pull request before merging**
- ☐ Require approvals: `0` (optional for feature branches)

**☑ Allow force pushes** → **☑ Everyone**
- Allow force pushes on feature branches for rebasing

**☑ Allow deletions** → **☑**
- Allow automatic deletion after merge (handled by workflow)

## Branch Protection via GitHub Rulesets (Alternative)

GitHub's newer Rulesets feature provides more granular control. If available in your plan:

Navigate to: **Settings** → **Rules** → **Rulesets**

### Ruleset 1: Main Branch Protection

- **Name**: `Main Branch Protection`
- **Enforcement**: Active
- **Target branches**: `main`
- **Rules**:
  - Restrict deletions
  - Restrict force pushes
  - Require pull request before merging (1 approval)
  - Require status checks to pass
  - Block force pushes
  - Require linear history
  - Restrict who can push (nobody except via PR)

### Ruleset 2: Dev Branch Protection

- **Name**: `Dev Branch Protection`
- **Enforcement**: Active
- **Target branches**: `dev`
- **Rules**:
  - Restrict deletions
  - Restrict force pushes
  - Require pull request before merging (1 approval)
  - Require status checks to pass

### Ruleset 3: Feature Branch Naming

- **Name**: `Feature Branch Naming Convention`
- **Enforcement**: Active
- **Target branches**: All branches
- **Rules**:
  - Branch name pattern must match:
    ```
    ^(main|dev|feature/\d+-[a-z0-9-]+|bugfix/\d+-[a-z0-9-]+|docs/\d+-[a-z0-9-]+|hotfix/\d+-[a-z0-9-]+)$
    ```

## Automated Enforcement

The following GitHub Actions workflows complement these branch protection rules:

### 1. `auto-create-branch.yml`
- Automatically creates properly named branches when issues are labeled
- Naming: `{type}/{issue-number}-{short-description}`
- Types: feature, bugfix, docs, hotfix

### 2. `pr-branch-enforcement.yml`
- Validates PR targets follow the strategy:
  - Feature/bugfix/docs/hotfix → `dev` only
  - Only `dev` → `main`
- Auto-closes PRs that violate the strategy
- Posts helpful comments explaining the violation

### 3. `pr-cleanup-automation.yml`
- Auto-deletes feature branches after merge to dev
- Auto-closes linked issues when PR is merged
- Posts merge success summary

### 4. `branch-protection-check.yml`
- Monitors direct pushes to protected branches
- Creates violation issues for unauthorized pushes
- Helps identify and correct misconfigurations

## Quick Setup Checklist

Use this checklist when setting up a new repository or verifying existing settings:

- [ ] Main branch protection rule created
  - [ ] Require PR with 1 approval
  - [ ] Require status checks
  - [ ] Linear history enforced
  - [ ] Deletions disabled
  - [ ] Force pushes disabled
  - [ ] Direct pushes restricted

- [ ] Dev branch protection rule created
  - [ ] Require PR with 1 approval
  - [ ] Require status checks
  - [ ] Deletions disabled
  - [ ] Force pushes disabled

- [ ] Automation workflows active
  - [ ] `auto-create-branch.yml` enabled
  - [ ] `pr-branch-enforcement.yml` enabled
  - [ ] `pr-cleanup-automation.yml` enabled
  - [ ] `branch-protection-check.yml` enabled

- [ ] Labels configured (run: `gh label sync --file .github/labels.yml`)

- [ ] Repository settings verified
  - [ ] Default branch is `main`
  - [ ] Auto-delete head branches enabled (Settings → General)
  - [ ] Require linear history on main enabled

## Troubleshooting

### "Cannot push to protected branch"
This is expected behavior. Create a feature branch and open a PR.

### "PR auto-closed by workflow"
Check the PR target branch. Feature branches must target `dev`, not `main`.

### "Branch was not auto-deleted after merge"
- Check if the branch matches the pattern: `feature/*`, `bugfix/*`, `docs/*`, `hotfix/*`
- Verify the `pr-cleanup-automation.yml` workflow has write permissions
- Check workflow runs for errors

### "Issue was not auto-closed after PR merge"
- Ensure the PR body or title contains: `Fixes #123` or `Closes #123`
- Check the `pr-cleanup-automation.yml` workflow logs
- Verify the workflow has issues:write permission

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [AEO Box Branching Strategy](../CLAUDE.md)

## Last Updated

2025-11-08

---

**Note**: These settings must be configured manually in the GitHub repository settings. They cannot be automated via code or workflows for security reasons.
