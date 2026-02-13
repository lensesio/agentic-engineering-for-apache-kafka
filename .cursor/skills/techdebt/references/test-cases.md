# Test Cases

Test cases for validating skill triggering, functional correctness and performance. Based on Anthropic's skill testing guide.

## Triggering Tests

### Should Trigger
- "Find tech debt"
- "Check for duplicated code"
- "Run a techdebt scan"
- "Clean up the codebase"
- "Find unused imports"
- "Are there any TODO comments?"
- "Check for dead code"
- "Refactoring opportunities"
- "End of session cleanup"
- "Check for inconsistent patterns in src/"

### Should NOT Trigger
- "Run the linter"
- "Format the code with ruff"
- "Run type checking with mypy"
- "Fix the failing test"
- "Add a new feature to the consumer"

## Functional Tests

### Test 1: Full codebase scan
**Given**: Codebase with src/ and tests/ directories containing Python files.
**When**: Skill executes full techdebt scan.
**Then**:
- Duplicated code blocks are identified with file locations
- Unused imports are found (via ruff if available)
- Inconsistent patterns are flagged
- Refactoring opportunities are listed
- Report follows the defined format with severity categories

### Test 2: Scoped scan
**Given**: User specifies src/kafka/ as the target path.
**When**: Skill scans only the specified path.
**Then**: Only files in src/kafka/ are analysed.

### Test 3: Target path does not exist
**Given**: User specifies a path that does not exist.
**When**: Skill attempts to scan.
**Then**: Reports that the path does not exist and stops.

## Performance Baseline

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 5-8 | 1 |
| Failed tool calls | 0-1 | 0 |
| Tool calls | 12+ | < 10 |
| User corrections needed | 1-3 | 0 |
