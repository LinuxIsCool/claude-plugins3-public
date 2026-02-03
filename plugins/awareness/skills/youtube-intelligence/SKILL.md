---
name: YouTube Intelligence Skill
description: This skill should be used when the user asks 'watch this video', 'summarize this YouTube video', 'extract transcript from video', 'what does IndyDevDan say about', 'find Claude Code tutorials', 'search YouTube for', or needs to extract and analyze content from YouTube videos.
---

# Purpose

Extract, analyze, and synthesize content from YouTube videos related to Claude Code and AI development.
Follow the `Instructions`, execute the `Workflow`, based on the `Cookbook`.

## Variables

ENABLE_TRANSCRIPT_EXTRACTION: true
ENABLE_CHANNEL_CRAWL: true
ENABLE_VIDEO_SEARCH: true
TRANSCRIPT_OUTPUT_DIR: ${CLAUDE_PLUGIN_ROOT}/data/transcripts
NOTABLE_CHANNELS:
  - "@indydevdan"
  - "@anthropic-ai"
  - "@AIExplained-official"

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which operation to perform.
- Always use yt-dlp for transcript extraction (no API key required).
- Parse VTT format to clean text for analysis.
- Cache transcripts to avoid redundant downloads.

### Transcript Summary

- IF: The user provides a video URL and requests a summary.
- THEN:
  - Extract transcript using `.claude/skills/youtube-intelligence/tools/youtube_extractor.py`
  - Parse VTT to clean text
  - Read the prompt template at `.claude/skills/youtube-intelligence/prompts/summarize_transcript.md`
  - Summarize the key points, actionable insights, and any code examples mentioned
- EXAMPLES:
  - "Summarize this video: https://youtube.com/watch?v=..."
  - "What's this video about? <url>"
  - "Extract and summarize the transcript"

## Workflow

1. Understand the user's request (single video, channel crawl, or search).
2. READ: `.claude/skills/youtube-intelligence/tools/youtube_extractor.py` to understand the extraction tool.
3. Follow the `Cookbook` to determine which operation to perform.
4. Execute the appropriate tool.
5. Analyze and present the extracted content.

## Cookbook

### Single Video Transcript

- IF: The user provides a specific YouTube URL AND `ENABLE_TRANSCRIPT_EXTRACTION` is true.
- THEN: Read and execute: `.claude/skills/youtube-intelligence/cookbook/extract-single.md`
- EXAMPLES:
  - "Get the transcript from https://youtube.com/watch?v=..."
  - "What does this video say? <url>"
  - "Extract transcript: <url>"

### Channel Crawl

- IF: The user wants to analyze a YouTube channel AND `ENABLE_CHANNEL_CRAWL` is true.
- THEN: Read and execute: `.claude/skills/youtube-intelligence/cookbook/crawl-channel.md`
- EXAMPLES:
  - "Crawl IndyDevDan's recent videos"
  - "Get transcripts from @anthropic-ai channel"
  - "What has this channel posted recently?"

### Video Search

- IF: The user wants to search YouTube for relevant content AND `ENABLE_VIDEO_SEARCH` is true.
- THEN: Read and execute: `.claude/skills/youtube-intelligence/cookbook/search-videos.md`
- EXAMPLES:
  - "Find Claude Code tutorial videos"
  - "Search YouTube for MCP server setup"
  - "What videos exist about Claude Code hooks?"

### Transcript Analysis

- IF: The user has a transcript and wants deeper analysis.
- THEN: Read and execute: `.claude/skills/youtube-intelligence/cookbook/analyze-transcript.md`
- EXAMPLES:
  - "What code examples are in this transcript?"
  - "Extract the key techniques mentioned"
  - "What problems does the speaker address?"

## Output Format

### Video Summary
```yaml
video:
  title: "Video Title"
  channel: "@channelname"
  url: "https://youtube.com/watch?v=..."
  duration: "12:34"
  transcript_length: 5432
summary:
  main_topic: "Brief description"
  key_points:
    - Point 1
    - Point 2
  code_examples: 3
  actionable_insights:
    - Insight 1
    - Insight 2
```

### Channel Crawl
```yaml
channel: "@channelname"
videos_analyzed: 5
total_transcript_chars: 45000
themes:
  - Theme 1
  - Theme 2
recent_videos:
  - title: "..."
    date: "2024-01-15"
```
