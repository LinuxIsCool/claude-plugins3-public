# Awareness Plugin for Claude Code

Provides contextual intelligence about your Claude Code ecosystem - documentation, community insights, and plugin capabilities.

## Installation

```bash
# Via Claude Code plugin marketplace
/plugins install awareness

# Or for development testing
claude --plugin-dir ./plugins/awareness
```

## Skills

### /awareness:ecosystem-context

Scan and inventory your installed plugins, skills, agents, and hooks.

**Example queries:**
- "What plugins do I have installed?"
- "List my skills"
- "What hooks are active?"
- "Show my Claude Code setup"

### /awareness:documentation-search

Search Claude Code documentation with full-text search and knowledge graph navigation.

**Example queries:**
- "How do I create a hook?"
- "What are the settings options?"
- "Show me MCP examples"
- "Find documentation about plugins"

### /awareness:community-intelligence

Get insights from GitHub issues, RSS feeds, and Hacker News discussions.

**Example queries:**
- "Any recent Claude Code updates?"
- "Common issues with hooks?"
- "What's the community saying about Claude Code?"
- "What version am I on?"

### /awareness:youtube-intelligence

Extract and analyze YouTube video transcripts for Claude Code tutorials.

**Example queries:**
- "Find Claude Code tutorial videos"
- "Get transcript from https://www.youtube.com/watch?v=..."
- "What has IndyDevDan posted recently?"
- "Summarize this YouTube video"

## Agent

### ecosystem-explorer

Deep exploration agent for comprehensive ecosystem analysis. Use when:
- You need thorough understanding of your Claude Code setup
- Debugging plugin or hook issues
- Comparing installed plugin features

## Data Sources

The plugin includes pre-populated data:

| Data | Description |
|------|-------------|
| Documentation index | 51 pages from code.claude.com/docs |
| Knowledge graph | 928 edges linking concepts |
| GitHub repos | 10 seed repositories analyzed |
| YouTube transcripts | 5 IndyDevDan tutorials |

## Hook Integration

The plugin injects context via hooks:

- **SessionStart**: Provides ecosystem summary at session start
- **UserPromptSubmit**: Classifies queries for skill routing

## Requirements

- Claude Code 2.1.0+
- `yt-dlp` for YouTube transcript extraction (optional)
- `gh` CLI for GitHub issue scanning (optional)

## Development

```bash
# Test individual tools
python3 skills/ecosystem-context/tools/scan_ecosystem.py plugins
python3 skills/documentation-search/tools/search_docs.py search "hooks"
python3 skills/community-intelligence/tools/community_scanner.py releases
python3 skills/youtube-intelligence/tools/youtube_extractor.py channel "@indydevdan"

# Test hook output
export CLAUDE_PLUGIN_ROOT=./plugins/awareness
bash scripts/session-start.sh
```

## Version History

- **0.1.0** (2026-01-27): Initial release with 4 skills, YouTube intelligence
