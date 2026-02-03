---
name: external
description: Search Claude Code documentation, track documentation changes, and surface community insights. Use when users need help with Claude Code features, API usage, or want to know what's new.
argument-hint: [search query]
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Glob, Grep, WebFetch, WebSearch
---

# External Awareness

Provide awareness of documentation, updates, and community intelligence.

## Usage

```
/external how do hooks work    - Search documentation for hooks
/external what's new           - Recent documentation changes
/external MCP configuration    - Search for MCP setup guides
/external community trends     - What's happening in the community
```

## Query Types

### Documentation Search

When user asks "how do X work" or searches for documentation:

1. **Check Local Cache First**
   - Look in `.claude/awareness/docs/` if it exists
   - Search for relevant cached pages

2. **Search Official Documentation**
   Use WebSearch or WebFetch to search:
   - https://code.claude.com/docs/en/
   - Focus on the specific topic

3. **Format Response:**
   ```
   ## {Topic}

   {Relevant excerpt from documentation}

   Source: {url}

   Related Topics:
   - {related1}
   - {related2}

   Last checked: {timestamp}
   ```

### Documentation Changes

When user asks "what's new" or "what changed":

1. **Check Change Tracking**
   - Look for `.claude/awareness/docs/changes.json`
   - Compare current vs cached versions

2. **If No Local Tracking:**
   - Suggest checking the official changelog
   - Note inability to track changes without setup

3. **Format Response:**
   ```
   ## Documentation Updates

   Since {last_check}:

   ### New Pages
   - {page}: {summary}

   ### Modified Pages
   - {page}: {change_summary}

   ### Removed Pages
   - {page}

   Source: Change detection system
   ```

### Community Intelligence

When user asks about community, trends, or discussions:

1. **Check Community Cache**
   - Look for `.claude/awareness/community/`
   - Recent HN discussions
   - GitHub issue trends

2. **Search Recent Activity:**
   Use WebSearch to find:
   - Recent Hacker News discussions about Claude Code
   - Recent GitHub activity
   - Blog posts and announcements

3. **Format Response:**
   ```
   ## Community Pulse

   ### Trending Topics
   1. {topic} - {mention_count} mentions
   2. {topic} - {mention_count} mentions

   ### Recent Discussions
   - "{title}" on HN ({points} points)
     Summary: {brief}

   ### Sentiment
   Overall: {positive/neutral/mixed}

   Source: Community monitoring
   Last updated: {timestamp}
   ```

## Topic Reference

### Common Documentation Topics

| Topic | Documentation Path | Description |
|-------|-------------------|-------------|
| hooks | /docs/en/hooks | Lifecycle event hooks |
| skills | /docs/en/skills | Custom slash commands |
| agents | /docs/en/sub-agents | Subagent configuration |
| mcp | /docs/en/mcp | MCP server integration |
| plugins | /docs/en/plugins | Plugin development |
| settings | /docs/en/settings | Configuration options |
| iam | /docs/en/iam | Permissions and security |

### Quick Links

For common questions, provide direct links:

```
Hooks: https://code.claude.com/docs/en/hooks
Skills: https://code.claude.com/docs/en/skills
Agents: https://code.claude.com/docs/en/sub-agents
MCP: https://code.claude.com/docs/en/mcp
Plugins: https://code.claude.com/docs/en/plugins
Settings: https://code.claude.com/docs/en/settings
```

## Response Quality

### Include in Every Response:
- Source URL or cache location
- Freshness indicator (when was this checked/cached)
- Related topics for exploration
- Caveat if information might be outdated

### Avoid:
- Stale information without warning
- Speculation about undocumented features
- Mixing official docs with community speculation

## Error Handling

If documentation not found:
```
[external] Could not find documentation for "{query}".

Try:
- Check official docs: https://code.claude.com/docs/
- Search with different terms: {suggestions}
- Ask in GitHub discussions
```

If community data unavailable:
```
[external] Community monitoring not configured.

To enable:
- Set up RSS monitoring
- Configure change detection
- Run periodic community scans
```
