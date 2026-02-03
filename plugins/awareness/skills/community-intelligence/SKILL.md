---
name: Community Intelligence Skill
description: This skill should be used when the user asks 'what are people saying about Claude Code', 'any recent updates', 'common issues', 'community feedback', 'what's new', 'check GitHub issues', 'recent releases', or needs insights from community discussions.
---

# Purpose

Provide insights from Claude Code community discussions, GitHub issues, RSS feeds, and release notes.
Follow the `Instructions`, execute the `Workflow`, based on the `Cookbook`.

## Variables

ENABLE_GITHUB_ISSUES: true
ENABLE_RSS_FEEDS: true
ENABLE_HACKER_NEWS: true
ENABLE_RELEASE_TRACKING: true
GITHUB_REPO: anthropics/claude-code
RSS_FEEDS:
  - anthropic_news
  - claude_blog
  - claude_code_changelog
DATA_PATH: ${CLAUDE_PLUGIN_ROOT}/data

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which source to query.
- Use gh CLI for GitHub issue queries.
- Use RSS monitor for feed updates.
- Use HN Algolia API for discussions.

### Latest Updates

- IF: The user asks what's new or recent changes.
- THEN:
  - Check RSS feeds for recent releases
  - Check GitHub for recent closed issues
  - Read the prompt template at `.claude/skills/community-intelligence/prompts/summarize_updates.md`
  - Synthesize key changes and their impact
- EXAMPLES:
  - "What's new in Claude Code?"
  - "Any recent updates I should know about?"
  - "What changed in the last week?"

## Workflow

1. Understand the user's community query.
2. READ: `.claude/skills/community-intelligence/tools/community_scanner.py` to understand the scanning tool.
3. Follow the `Cookbook` to determine which source to query.
4. Execute the appropriate query.
5. Synthesize and present insights.

## Cookbook

### GitHub Issues

- IF: The user wants to know about bugs or feature requests AND `ENABLE_GITHUB_ISSUES` is true.
- THEN: Read and execute: `.claude/skills/community-intelligence/cookbook/github-issues.md`
- EXAMPLES:
  - "What are common Claude Code issues?"
  - "Are there any known bugs with hooks?"
  - "What features are people requesting?"

### RSS Feed Updates

- IF: The user wants release notes or announcements AND `ENABLE_RSS_FEEDS` is true.
- THEN: Read and execute: `.claude/skills/community-intelligence/cookbook/rss-feeds.md`
- EXAMPLES:
  - "What's in the latest release?"
  - "Any recent announcements?"
  - "Check the changelog"

### Hacker News Discussions

- IF: The user wants community sentiment or discussions AND `ENABLE_HACKER_NEWS` is true.
- THEN: Read and execute: `.claude/skills/community-intelligence/cookbook/hacker-news.md`
- EXAMPLES:
  - "What are people saying about Claude Code?"
  - "Any interesting HN discussions?"
  - "Community sentiment about Claude Code"

### Release Tracking

- IF: The user wants version history or release notes AND `ENABLE_RELEASE_TRACKING` is true.
- THEN: Read and execute: `.claude/skills/community-intelligence/cookbook/releases.md`
- EXAMPLES:
  - "What version am I on?"
  - "What changed in v2.1.0?"
  - "Release history"

## Community Sources

| Source | API | Auth | Rate Limit |
|--------|-----|------|------------|
| GitHub Issues | gh CLI | Yes | 5000/hr |
| Hacker News | Algolia | No | Unlimited |
| RSS Feeds | HTTP | No | None |
| Reddit | API | Yes | Blocked |

## Key Insights (Cached)

### Common Issue Categories
| Category | Count | Description |
|----------|-------|-------------|
| bug | 74 | Bugs and crashes |
| has-repro | 71 | Reproducible issues |
| platform:macos | 50 | macOS-specific |
| area:tools | 42 | Tool-related |

### Community Sentiment Patterns
- **Positive**: Automation, productivity, ADHD-friendly
- **Negative**: Non-determinism, learning curve, costs
- **Neutral**: Comparisons with other tools
