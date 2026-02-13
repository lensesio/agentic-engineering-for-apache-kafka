# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Ship it"
- "Commit and push"
- "Create a PR"
- "Open a pull request"
- "Commit my changes"
- "Push this to remote"
- "Ship the code"
- "Commit everything and open a PR"
- "I'm done, create a PR"
- "Send this for review"

### Should NOT Trigger
- "Rebase my branch on main"
- "Merge the PR"
- "Resolve the merge conflict"
- "Amend the last commit"
- "Cherry-pick that commit"

## Functional Tests

### Test 1: Standard feature commit
**Given**: Feature branch with staged changes and clean git status.
**When**: Skill executes full workflow.
**Then**:
- Commit message follows conventional commit format
- Changes are pushed to remote
- PR is created with summary, changes and test plan sections
- PR URL is returned to the user

### Test 2: Nothing staged
**Given**: Unstaged changes but nothing in the staging area.
**When**: Skill checks git status.
**Then**: Prompts user for confirmation before staging all changes with git add -A.

### Test 3: On main branch
**Given**: User is on the main branch with uncommitted changes.
**When**: Skill detects the branch.
**Then**: Creates a new feature branch before committing. Never commits directly to main.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 4-6 | 1 |
| Failed git/gh calls | 0-1 | 0 |
| Tool calls | 8+ | < 6 |
| User corrections needed | 1-2 | 0 |
