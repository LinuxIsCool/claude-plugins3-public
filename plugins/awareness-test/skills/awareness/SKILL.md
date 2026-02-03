---
name: awareness
description: Query your Claude Code awareness system for ecosystem information, documentation search, community trends, and workflow optimization. Use when users ask about installed plugins, available capabilities, documentation, or need context about their development environment.
argument-hint: [query or "status"]
disable-model-invocation: false
user-invocable: true
---

# Awareness System

Provide contextual awareness across three domains:

## Query Processing

When the user invokes /awareness, classify their query and respond appropriately:

### Domain Detection

1. **Introspection** (self-knowledge about ecosystem)
   - "What plugins are installed?"
   - "What skills can I use?"
   - "What hooks are active?"
   - "Show my ecosystem"
   → Route to introspection analysis

2. **External** (documentation and community)
   - "How do hooks work?"
   - "Search docs for MCP"
   - "What's new in documentation?"
   - "Community trends"
   → Route to documentation search

3. **Metabolic** (workflow optimization)
   - "Catch me up on this project"
   - "Best workflow for refactoring?"
   - "What should I focus on?"
   → Route to workflow guidance

### Response Guidelines

**For Introspection queries:**
- Scan `.claude/` directories for plugins, skills, agents
- Read plugin.json files to understand capabilities
- List active hooks from settings.json
- Format as structured summary

**For External queries:**
- Search local documentation cache
- Provide relevant doc links
- Note freshness of information
- Include related topics

**For Metabolic queries:**
- Review recent session activity
- Suggest focus areas based on context
- Recommend relevant skills/tools
- Keep suggestions actionable

### Status Command

If query is "status" or empty, provide quick ecosystem overview:

```
[Awareness Status]
Plugins: {count} installed
Skills: {count} available (top: {skill1}, {skill2}, {skill3})
Hooks: {active_events}
Session: {session_info}

Recent: {recent_activity_summary}
```

## Quality Standards

- Be concise (avoid information overload)
- Include sources for claims
- Note uncertainty when present
- Suggest follow-up actions

## Files to Reference

When answering introspection queries, scan:
- `.claude/settings.json` - User configuration
- `.claude/settings.local.json` - Project configuration
- `~/.claude/plugins/` - Installed plugins
- `.claude/skills/` - Available skills
- `.claude/agents/` - Custom agents

When answering external queries:
- Check local documentation cache first
- Suggest web search for latest information
- Link to official docs when relevant
