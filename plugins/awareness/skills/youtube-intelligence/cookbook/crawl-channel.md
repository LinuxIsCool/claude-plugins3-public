# Purpose

Crawl a YouTube channel for recent videos and extract their transcripts.

## Variables

TRANSCRIPT_OUTPUT_DIR: ${CLAUDE_PLUGIN_ROOT}/data/transcripts
MAX_VIDEOS_PER_CHANNEL: 10

## Instructions

- List recent videos from the channel.
- Extract transcripts from each video.
- Aggregate for thematic analysis.

## Execution

```bash
# List recent videos from a channel
python3 ${CLAUDE_PLUGIN_ROOT}/skills/youtube-intelligence/tools/youtube_extractor.py channel "<CHANNEL_URL>" --limit 10

# Or manually with yt-dlp:
yt-dlp --flat-playlist --dump-json "https://www.youtube.com/@channelname/videos" | head -10
```

## Channel URL Formats

- Full URL: `https://www.youtube.com/@indydevdan/videos`
- Handle: `@indydevdan`
- Channel ID: `UC...`

## Output

```yaml
channel: "@channelname"
videos_found: 10
videos_with_transcripts: 8
total_chars: 45000
videos:
  - id: "abc123"
    title: "Video Title"
    date: "2024-01-15"
    transcript_length: 5000
  - id: "def456"
    title: "Another Video"
    date: "2024-01-10"
    transcript_length: 4500
```

## Notable Channels for Claude Code

| Channel | Handle | Focus |
|---------|--------|-------|
| IndyDevDan | @indydevdan | Claude Code tutorials, AI coding |
| Anthropic | @anthropic-ai | Official announcements |
| AI Explained | @AIExplained-official | AI tool comparisons |
