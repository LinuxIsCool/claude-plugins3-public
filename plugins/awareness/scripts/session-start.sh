#!/bin/bash
# SessionStart hook - inject ecosystem awareness context
# Uses additionalContext for SessionStart events

set -euo pipefail

# Count installed plugins
PLUGIN_COUNT=$(find ~/.claude/plugins/cache -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l || echo "0")

# Count available skills
SKILL_COUNT=$(find ~/.claude/skills -name "SKILL.md" 2>/dev/null | wc -l || echo "0")

# Build context message
CONTEXT="[Awareness Plugin Active] Ecosystem: ${PLUGIN_COUNT} plugins, ${SKILL_COUNT} skills. Use /awareness:ecosystem-context for details, /awareness:documentation-search for docs, /awareness:community-intelligence for community insights."

# Output JSON with additionalContext for SessionStart
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${CONTEXT}"
  }
}
EOF
