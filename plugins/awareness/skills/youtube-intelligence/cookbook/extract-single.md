# Purpose

Extract transcript from a single YouTube video.

## Variables

TRANSCRIPT_OUTPUT_DIR: ${CLAUDE_PLUGIN_ROOT}/data/transcripts

## Instructions

- Use yt-dlp to download auto-generated subtitles.
- Parse VTT format to clean text.
- Cache the result for future use.

## Execution

```bash
# Extract transcript using the tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/youtube-intelligence/tools/youtube_extractor.py transcript "<VIDEO_URL>"

# Or manually with yt-dlp:
yt-dlp --skip-download --write-auto-sub --sub-lang en --sub-format vtt -o "transcript.%(ext)s" "<VIDEO_URL>"
```

## VTT Parsing

VTT files contain timestamps and duplicate lines. To parse:
1. Skip lines starting with "WEBVTT"
2. Skip lines containing "-->" (timestamps)
3. Skip empty lines
4. Deduplicate consecutive identical lines

## Output

Save transcript to: `TRANSCRIPT_OUTPUT_DIR/<video_id>.txt`

Return:
```yaml
video_id: "abc123"
title: "Video Title"
channel: "@channelname"
duration: "12:34"
transcript_path: "/path/to/transcript.txt"
transcript_length: 5432
preview: "First 200 chars of transcript..."
```
