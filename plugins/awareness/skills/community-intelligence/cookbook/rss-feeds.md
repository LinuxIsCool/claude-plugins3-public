# Purpose

Monitor RSS feeds for Claude Code releases and announcements.

## Variables

RSS_FEEDS:
  - name: anthropic_news
    url: https://www.anthropic.com/news/rss.xml
  - name: claude_blog
    url: https://www.anthropic.com/claude/rss.xml
  - name: claude_code_changelog
    url: https://code.claude.com/changelog.rss

## Instructions

- Fetch RSS feeds using feedparser or requests.
- Parse for Claude Code related items.
- Score relevance based on keywords.

## Execution

```bash
# Using the community scanner tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/community-intelligence/tools/community_scanner.py rss --days 7

# Manual feed check (if tool not available)
curl -s "https://code.claude.com/changelog.rss" | head -100
```

## Feed Analysis

### Anthropic News
- Company announcements
- Major product launches
- Research publications

### Claude Blog
- Feature deep dives
- Use case studies
- Best practices

### Claude Code Changelog
- Version releases
- Bug fixes
- New features

## Relevance Scoring

Score items based on keywords:
- High (0.8+): "claude code", "release", "update"
- Medium (0.5-0.8): "claude", "api", "tools"
- Low (<0.5): General AI news

## Output Format

```yaml
feeds_checked: 3
items_found: 30
relevant_items: 12
recent_updates:
  - title: "Claude Code v2.1.20 Released"
    feed: "claude_code_changelog"
    date: "2024-01-20"
    summary: "New hook events, bug fixes..."
    relevance: 0.95
  - title: "Introducing MCP Improvements"
    feed: "claude_blog"
    date: "2024-01-18"
    summary: "Enhanced MCP server support..."
    relevance: 0.85
```
