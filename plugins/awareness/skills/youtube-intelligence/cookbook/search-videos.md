# Purpose

Search YouTube for relevant videos on a topic.

## Variables

DEFAULT_SEARCH_LIMIT: 5

## Instructions

- Use yt-dlp's search feature to find videos.
- Filter for relevance (Claude Code, AI coding tools).
- Return metadata for user selection.

## Execution

```bash
# Search YouTube
python3 ${CLAUDE_PLUGIN_ROOT}/skills/youtube-intelligence/tools/youtube_extractor.py search "claude code tutorial" --limit 5

# Or manually with yt-dlp:
yt-dlp --dump-json --flat-playlist --no-download "ytsearch5:claude code tutorial 2024"
```

## Search Strategies

### Specific Tool Searches
- `"claude code hooks tutorial"`
- `"claude code mcp server"`
- `"claude code plugins guide"`

### Comparison Searches
- `"claude code vs cursor"`
- `"claude code vs github copilot"`

### Creator Searches
- `"indydevdan claude code"`
- `"anthropic claude code"`

## Output

```yaml
query: "claude code tutorial"
results: 5
videos:
  - id: "abc123"
    title: "Claude Code for Absolute Beginners"
    channel: "@indydevdan"
    duration: "15:32"
    views: 12500
    url: "https://youtube.com/watch?v=abc123"
  - id: "def456"
    title: "Advanced Claude Code Hooks"
    channel: "@techcreator"
    duration: "22:10"
    views: 8300
    url: "https://youtube.com/watch?v=def456"
```

## Filtering Tips

- Prefer videos from notable channels (see channel cookbook)
- Prefer recent videos (within 6 months)
- Prefer longer videos (10+ minutes) for tutorials
- Check view count as quality signal
