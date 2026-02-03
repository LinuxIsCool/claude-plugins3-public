---
name: Ecosystem Context Skill
description: This skill should be used when the user asks 'what plugins are installed', 'what skills are available', 'what agents can I use', 'show my Claude Code setup', 'what hooks are active', 'list my capabilities', or needs an overview of their Claude Code ecosystem.
---

# Purpose

Provide comprehensive awareness of the user's Claude Code ecosystem including installed plugins, available skills, configured agents, and active hooks.
Follow the `Instructions`, execute the `Workflow`, based on the `Cookbook`.

## Variables

ENABLE_PLUGIN_SCAN: true
ENABLE_SKILL_SCAN: true
ENABLE_AGENT_SCAN: true
ENABLE_HOOK_SCAN: true
PLUGIN_CACHE_PATH: ~/.claude/plugins/cache
USER_SKILLS_PATH: ~/.claude/skills
DATA_PATH: ${CLAUDE_PLUGIN_ROOT}/data

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which scan to perform.
- Always provide counts and summaries first, then details if requested.
- Use the tools in `.claude/skills/ecosystem-context/tools/` for scanning operations.

### Detailed Reports

- IF: The user requests a detailed or comprehensive report.
- THEN:
  - Execute all enabled scans sequentially.
  - Aggregate results into a unified report.
  - Save to `DATA_PATH/ecosystem.json` for caching.
- EXAMPLES:
  - "Show me everything about my Claude Code setup"
  - "Give me a complete ecosystem report"
  - "What are all my capabilities?"

## Workflow

1. Understand the user's request (plugins, skills, agents, hooks, or all).
2. READ: `.claude/skills/ecosystem-context/tools/scan_ecosystem.py` to understand the scanning tool.
3. Follow the `Cookbook` to determine which scan to perform.
4. Execute the appropriate tool or command.
5. Format and present results to the user.

## Cookbook

### Plugin Inventory

- IF: The user requests plugin information AND `ENABLE_PLUGIN_SCAN` is true.
- THEN: Read and execute: `.claude/skills/ecosystem-context/cookbook/scan-plugins.md`
- EXAMPLES:
  - "What plugins do I have installed?"
  - "List my plugins"
  - "Show plugin capabilities"

### Skill Discovery

- IF: The user requests skill information AND `ENABLE_SKILL_SCAN` is true.
- THEN: Read and execute: `.claude/skills/ecosystem-context/cookbook/scan-skills.md`
- EXAMPLES:
  - "What skills are available?"
  - "List all skills"
  - "Show me skill descriptions"

### Agent Enumeration

- IF: The user requests agent information AND `ENABLE_AGENT_SCAN` is true.
- THEN: Read and execute: `.claude/skills/ecosystem-context/cookbook/scan-agents.md`
- EXAMPLES:
  - "What agents can help me?"
  - "List available agents"
  - "Show agent capabilities"

### Hook Configuration

- IF: The user requests hook information AND `ENABLE_HOOK_SCAN` is true.
- THEN: Read and execute: `.claude/skills/ecosystem-context/cookbook/scan-hooks.md`
- EXAMPLES:
  - "What hooks are active?"
  - "Show my hook configuration"
  - "List event handlers"
