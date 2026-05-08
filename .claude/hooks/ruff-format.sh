#!/usr/bin/env bash
# PostToolUse hook: format Python files written or edited by Claude Code.
#
# Claude Code passes a JSON object on stdin containing the tool call. For
# Write and Edit tools the file path is at .tool_input.file_path. We extract
# it with jq, skip non-Python files, and run ruff format on the single file.
#
# This hook is a no-op if jq, uv, or ruff are unavailable, so it does not
# block the agent on machines without the toolchain.

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

input=$(cat)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file_path" ]]; then
  exit 0
fi

case "$file_path" in
  *.py) ;;
  *) exit 0 ;;
esac

if ! command -v uv >/dev/null 2>&1; then
  exit 0
fi

uv run ruff format --quiet "$file_path" >/dev/null 2>&1 || true
