---
name: techdebt
description: Analyse codebase for technical debt including duplicated code, dead code, unused imports and refactoring opportunities. Use when user says "find tech debt", "check for duplicates", "cleanup the code" or at the end of every coding session. Do NOT use for linting, formatting or type checking (use ruff/mypy directly).
license: MIT
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[optional: path to scan, defaults to src/ and tests/]"
metadata:
  author: Tun Shwe
  version: 1.0.0
  category: workflow-automation
  approach: problem-first
  patterns: iterative-refinement
  tags: [code-quality, technical-debt, refactoring, cleanup]
---

# Techdebt Analysis

Run this at the end of every session to find and kill duplicated code and other technical debt.

Target path: $ARGUMENTS (defaults to `src/` and `tests/` if not specified)

## Workflow

Copy this checklist and track your progress:

```
Techdebt Scan Progress:
- [ ] Step 1: Scan for duplicated code
- [ ] Step 2: Detect dead code and unused imports
- [ ] Step 3: Find inconsistent patterns
- [ ] Step 4: Generate report
```

1. **Scan for duplicated code** across the target path
2. **Detect dead code** and unused imports
3. **Find inconsistent patterns** that should be consolidated
4. **Report findings** with actionable recommendations

## Step 1: Duplicated Code Detection

Search for code duplication patterns:

- Look for functions or methods with similar logic across different modules
- Identify copy-pasted code blocks (3+ lines of near-identical code in different files)
- Find repeated patterns that could be extracted into shared utilities in `src/utils/`
- Check for duplicated Kafka producer/consumer setup code that should use shared helpers

Use grep/search to find similar function signatures, repeated string literals and duplicated error-handling blocks.

Expected output: List of duplicated code blocks with file locations and line numbers.

**Validation**: If the target path does not exist or contains no source files, report this and stop.

## Step 2: Dead Code and Unused Imports

- Run `uv run ruff check src/ tests/ --select F401,F841` to find unused imports and variables
- Search for functions and classes that are defined but never imported or called
- Look for commented-out code blocks that should be removed
- Check for TODO/FIXME/HACK comments that indicate unresolved debt

## Step 3: Inconsistent Patterns

- Check that all Kafka producers use context managers (not manual open/close)
- Verify topic names follow `{domain}.{entity}.{event}` convention
- Ensure consumer group IDs follow `{service-name}-{purpose}` convention
- Confirm all public functions have type hints and docstrings
- Check for mixed naming conventions (should be `snake_case` everywhere)
- Look for hardcoded values that should be configuration or constants

## Step 4: Refactoring Opportunities

- Identify long functions (>50 lines) that should be broken up
- Find classes with too many responsibilities (suggest splitting)
- Look for deeply nested conditionals that could be simplified
- Check for repeated error handling that could use a decorator or context manager

## Success Criteria

### Quantitative
- Triggers on 90% of tech-debt-related queries (test with 10-20 varied phrasings)
- Completes scan in under 10 tool calls
- ruff findings are always included when ruff is available

### Qualitative
- Duplicated code findings include both locations and a consolidation suggestion
- Report is actionable without follow-up questions from the user
- Consistent severity categorisation across runs

## Examples

### Example 1: End-of-session cleanup

User says: "Run a techdebt scan"

Actions:
1. Scan `src/` and `tests/` for duplicated code
2. Run ruff to find unused imports
3. Check for inconsistent patterns
4. Identify refactoring opportunities
Result: Full techdebt report with prioritised findings

### Example 2: Scoped scan

User says: "Check for tech debt in src/kafka/"

Actions:
1. Scan only `src/kafka/` for duplicated code and dead code
2. Check for inconsistent Kafka patterns (context managers, topic naming)
Result: Focused report on the Kafka module

### Example 3: Post-feature check

User says: "I just finished the payment consumer, check for any debt I introduced"

Actions:
1. Search for duplicated setup code between the new consumer and existing ones
2. Verify the new code follows project conventions
3. Check for hardcoded values that should be configurable
Result: Targeted report on recently added code

## Troubleshooting

### ruff command not found
Cause: ruff is not installed or not in the uv virtual environment.
Solution: Run `uv add --dev ruff` to install it. If uv is not configured, fall back to manual grep-based analysis.

### Too many findings to be useful
Cause: Large codebase with accumulated technical debt.
Solution: Focus on the target path if provided. Prioritise critical findings (duplicated business logic, security-related dead code) over suggestions (naming conventions).

### False positives in duplication detection
Cause: Some patterns (e.g., test setup, boilerplate) look duplicated but serve different purposes.
Solution: Use judgement to distinguish genuine duplication from necessary repetition. Note confidence level in the report.

## Output Format

Report findings in this format:

```
## Techdebt Report

### Critical (must fix)
- [file:line] Description of the issue
  Recommendation: How to fix it

### Warning (should fix)
- [file:line] Description of the issue
  Recommendation: How to fix it

### Suggestion (consider improving)
- [file:line] Description of the issue
  Recommendation: How to fix it

### Summary
- X critical issues found
- Y warnings found
- Z suggestions found
- Estimated effort: low/medium/high
```
