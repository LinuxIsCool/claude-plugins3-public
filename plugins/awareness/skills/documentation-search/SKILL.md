---
name: Documentation Search Skill
description: This skill should be used when the user asks 'how do I configure hooks', 'what are the plugin settings', 'where is the documentation for X', 'help me understand Y feature', 'what does the docs say about', or needs to find specific Claude Code documentation.
---

# Purpose

Search and retrieve Claude Code documentation with full-text search capabilities.
Follow the `Instructions`, execute the `Workflow`, based on the `Cookbook`.

## Variables

ENABLE_FTS_SEARCH: true
ENABLE_KNOWLEDGE_GRAPH: true
ENABLE_CODE_EXAMPLES: true
DATABASE_PATH: ${CLAUDE_PLUGIN_ROOT}/data/awareness.db
DOCS_INDEX_PATH: ${CLAUDE_PLUGIN_ROOT}/data/docs-index.json

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which search to perform.
- Use FTS5 full-text search for keyword queries.
- Use knowledge graph edges for related topics.
- Include code examples when relevant.

### Documentation Navigation

- IF: The user asks how to do something specific.
- THEN:
  - Search for relevant documentation pages
  - Extract code examples from matched pages
  - Suggest related topics based on knowledge graph
- EXAMPLES:
  - "How do I create a hook?"
  - "What are the settings options?"
  - "Show me MCP server configuration"

## Workflow

1. Understand the user's documentation query.
2. READ: `.claude/skills/documentation-search/tools/search_docs.py` to understand the search tool.
3. Follow the `Cookbook` to determine which search to perform.
4. Execute the appropriate search.
5. Format and present results with links and code examples.

## Cookbook

### Full-Text Search

- IF: The user has a keyword or phrase to search AND `ENABLE_FTS_SEARCH` is true.
- THEN: Read and execute: `.claude/skills/documentation-search/cookbook/fts-search.md`
- EXAMPLES:
  - "Search docs for 'SessionStart'"
  - "Find documentation about hooks"
  - "What pages mention MCP?"

### Topic Navigation

- IF: The user wants to explore related topics AND `ENABLE_KNOWLEDGE_GRAPH` is true.
- THEN: Read and execute: `.claude/skills/documentation-search/cookbook/topic-navigation.md`
- EXAMPLES:
  - "What topics are related to plugins?"
  - "Show me the documentation map"
  - "Navigate from hooks to skills"

### Code Example Lookup

- IF: The user wants code examples AND `ENABLE_CODE_EXAMPLES` is true.
- THEN: Read and execute: `.claude/skills/documentation-search/cookbook/code-examples.md`
- EXAMPLES:
  - "Show me hook examples"
  - "What's a sample plugin.json?"
  - "Give me code for SessionStart"

### Hub Pages

- IF: The user needs an overview or starting point.
- THEN: Read and execute: `.claude/skills/documentation-search/cookbook/hub-pages.md`
- EXAMPLES:
  - "Where should I start learning about X?"
  - "What's the main page for plugins?"
  - "Overview of Claude Code features"

## Knowledge Base Statistics

| Metric | Value |
|--------|-------|
| Documentation pages | 51 |
| GitHub repositories | 10 |
| Total edges | 928 |
| Code examples | 375 |

## Hub Pages Reference

| Page | Incoming Links | Best For |
|------|----------------|----------|
| settings.md | 15 | Configuration options |
| mcp.md | 9 | MCP server integration |
| skills.md | 7 | Custom skill development |
| memory.md | 8 | Context and memory |
| plugins.md | 6 | Plugin development |
