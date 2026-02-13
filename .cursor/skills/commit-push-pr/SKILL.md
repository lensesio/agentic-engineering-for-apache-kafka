---
name: commit-push-pr
description: Commit staged changes, push to remote and open a pull request in one step. Use when the user wants to ship code, create a PR, says "commit and push" or asks to "open a pull request". Do NOT use for rebasing, merging or resolving conflicts.
license: MIT
disable-model-invocation: true
metadata:
  author: Tun Shwe
  version: 1.0.0
  category: workflow-automation
  approach: problem-first
  patterns: sequential-workflow
  tags: [git, workflow, pull-request, automation]
---

# Commit, Push and Open a PR

Commits current changes, pushes to the remote branch and opens a pull request. Designed to be run dozens of times a day as the final step of any change.

## Workflow

Copy this checklist and track your progress:

```
Ship Progress:
- [ ] Step 1: Gather context (status, branch, diff)
- [ ] Step 2: Commit changes
- [ ] Step 3: Push to remote
- [ ] Step 4: Open pull request
```

1. **Gather context** - Check git status, current branch and diff
2. **Commit** - Generate a descriptive commit message and commit
3. **Push** - Push to remote (create the branch if needed)
4. **Open PR** - Create a pull request with a generated title and body

## Step 1: Gather Context

Before doing anything, gather the current state:

- Run `git status` to see staged and unstaged changes
- Run `git branch --show-current` to get the current branch name
- Run `git diff --cached --stat` to see what's staged
- Run `git log --oneline -5` to see recent commit style

If nothing is staged, stage all changes with `git add -A` and confirm with the user first.

**Do NOT commit to `main` or `master` directly.** If on one of those branches, create a new feature branch first.

Expected output: Current branch name, list of staged/unstaged files and recent commit messages.

**Validation**: If on main/master, create a feature branch before proceeding. If nothing is staged, confirm with the user before staging all changes.

## Step 2: Commit

Generate a commit message based on the diff:

- First line: concise summary (<72 chars), using conventional commit format
  - `feat:` for new features
  - `fix:` for bug fixes
  - `refactor:` for code restructuring
  - `test:` for adding/updating tests
  - `docs:` for documentation changes
  - `chore:` for maintenance tasks
- Blank line, then a body with more detail if the change is non-trivial
- Follow the project's existing commit message style from `git log`

```bash
git commit -m "{generated message}"
```

## Step 3: Push

Push to the remote, creating the upstream branch if it doesn't exist:

```bash
git push -u origin HEAD
```

## Step 4: Open PR

Create a pull request using the `gh` CLI:

```bash
gh pr create --title "{title}" --body "{body}"
```

**PR title**: Same as the commit summary line (or a polished version).

**PR body** should include:
- `## Summary` - 1-3 bullet points describing what changed and why
- `## Changes` - List of files modified with brief descriptions
- `## Test plan` - How to verify the changes work

If `gh` is not installed, provide the PR URL format for the user to open manually.

## Success Criteria

### Quantitative
- Triggers on 90% of commit/push/PR queries (test with 10-20 varied phrasings)
- Completes full workflow in under 6 tool calls
- 0 failed git or gh commands per run

### Qualitative
- Commit messages follow conventional commit format consistently
- PR body includes summary, changes and test plan sections
- Never commits directly to main/master without creating a branch first

## Examples

### Example 1: Standard feature commit

User says: "Ship it" or "commit and push"

Actions:
1. Review staged changes
2. Generate conventional commit message (e.g., `feat: add payment consumer`)
3. Push to feature branch
4. Open PR with summary and test plan
Result: PR created and URL returned to the user

### Example 2: Nothing staged

User says: "Commit everything and open a PR"

Actions:
1. Notice nothing is staged
2. Run `git add -A` after confirming with user
3. Commit, push and open PR
Result: All changes committed and PR opened

### Example 3: On main branch

User says: "Create a PR for these changes"

Actions:
1. Detect current branch is `main`
2. Create a new feature branch (e.g., `feature/add-payment-consumer`)
3. Commit, push and open PR against `main`
Result: Changes moved to a feature branch with PR opened

## Troubleshooting

### git push fails with divergent branches
Cause: Remote branch has commits that are not in the local branch.
Solution: Warn the user and suggest `git pull --rebase`. Never force-push without explicit user confirmation.

### gh CLI not installed
Cause: GitHub CLI is not available on the system.
Solution: Provide the manual PR URL (`https://github.com/{org}/{repo}/compare/{branch}`) for the user to open in a browser.

### gh pr create fails with "already exists"
Cause: A PR for this branch already exists.
Solution: Show the existing PR URL. Suggest the user push additional commits to the existing PR instead.

## Error Handling

- If `git push` fails due to divergent branches, warn the user and suggest `git pull --rebase`
- If `gh pr create` fails, show the error and provide a manual URL
- Never force-push without explicit user confirmation
