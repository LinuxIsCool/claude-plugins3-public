# Purpose

Search Hacker News for Claude Code discussions and sentiment.

## Variables

HN_API_BASE: https://hn.algolia.com/api/v1

## Instructions

- Use Algolia API (no auth required).
- Search for Claude Code related stories.
- Extract sentiment from comments.

## Execution

```bash
# Using the community scanner tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/community-intelligence/tools/community_scanner.py hacker-news "claude code"

# Direct API call
curl "https://hn.algolia.com/api/v1/search?query=claude+code&tags=story"
```

## API Endpoints

### Search Stories
```
GET /search?query=<query>&tags=story
```

### Search Comments
```
GET /search?query=<query>&tags=comment
```

### Get Item
```
GET /items/<id>
```

## Notable Claude Code Threads

| Title | Points | Comments | Key Themes |
|-------|--------|----------|------------|
| Claude 3.7 and Claude Code | 2127 | 963 | Release announcement |
| Claude Code is all you need | 851 | 504 | Productivity, workflows |
| Cowork: Claude Code for everyone | 1298 | 420 | Accessibility |

## Sentiment Extraction

When analyzing comments, categorize as:
- **Positive**: Praise, success stories, recommendations
- **Negative**: Criticism, frustrations, limitations
- **Neutral**: Questions, comparisons, technical discussions

Common themes to track:
- Productivity gains
- Learning curve
- Cost concerns
- Comparison with competitors
- Feature requests

## Output Format

```yaml
query: "claude code"
stories_found: 15
total_points: 5000
top_stories:
  - title: "Claude Code is all you need"
    points: 851
    comments: 504
    url: "https://news.ycombinator.com/item?id=..."
sentiment_summary:
  positive: 60%
  negative: 25%
  neutral: 15%
common_themes:
  - "Productivity improvements"
  - "ADHD-friendly workflow"
  - "Cost vs value debate"
```
