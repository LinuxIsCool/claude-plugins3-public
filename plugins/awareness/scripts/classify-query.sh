#!/bin/bash
# UserPromptSubmit hook - classify queries for awareness relevance
# Lightweight classification to detect ecosystem-related queries

set -euo pipefail

# Read input from stdin
INPUT=$(cat)

# Extract user prompt from JSON input
USER_PROMPT=$(echo "$INPUT" | jq -r '.user_prompt // ""' 2>/dev/null || echo "")

# Skip if no prompt
if [ -z "$USER_PROMPT" ]; then
  exit 0
fi

# Convert to lowercase for matching
LOWER_PROMPT=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Check for awareness-related keywords
AWARENESS_KEYWORDS="plugin|skill|hook|agent|mcp|documentation|docs|ecosystem|installed|available|configure|setup"
COMMUNITY_KEYWORDS="issue|bug|release|update|changelog|community|feedback"

CONTEXT=""

if echo "$LOWER_PROMPT" | grep -qE "$AWARENESS_KEYWORDS"; then
  CONTEXT="[Awareness hint: Query relates to Claude Code ecosystem. Consider using /awareness:ecosystem-context or /awareness:documentation-search]"
elif echo "$LOWER_PROMPT" | grep -qE "$COMMUNITY_KEYWORDS"; then
  CONTEXT="[Awareness hint: Query relates to Claude Code updates/issues. Consider using /awareness:community-intelligence]"
fi

# Only output if we have context to add
if [ -n "$CONTEXT" ]; then
  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "${CONTEXT}"
  }
}
EOF
fi

exit 0
