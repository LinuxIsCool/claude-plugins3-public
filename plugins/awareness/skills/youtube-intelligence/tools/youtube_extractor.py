#!/usr/bin/env -S uv run
"""YouTube transcript extraction and channel crawling tool."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_video_info(url: str) -> dict | None:
    """Get video metadata without downloading."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting video info: {e}", file=sys.stderr)
    return None


def extract_transcript(url: str, output_dir: Path) -> dict | None:
    """Extract transcript from a YouTube video."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # First get video info
    info = get_video_info(url)
    if not info:
        return None

    video_id = info.get('id', 'unknown')
    title = info.get('title', 'Unknown')
    channel = info.get('channel', info.get('uploader', 'Unknown'))
    duration = info.get('duration_string', 'Unknown')

    # Check cache
    cache_file = output_dir / f"{video_id}.txt"
    if cache_file.exists():
        text = cache_file.read_text()
        return {
            'video_id': video_id,
            'title': title,
            'channel': channel,
            'duration': duration,
            'transcript_path': str(cache_file),
            'transcript_length': len(text),
            'cached': True,
            'preview': text[:200] + '...' if len(text) > 200 else text
        }

    # Extract subtitles
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-lang", "en",
                "--sub-format", "vtt",
                "-o", str(output_dir / "%(id)s.%(ext)s"),
                url
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Find and parse VTT file
        vtt_file = output_dir / f"{video_id}.en.vtt"
        if vtt_file.exists():
            text = parse_vtt(vtt_file)
            # Save as plain text
            cache_file.write_text(text)
            # Clean up VTT
            vtt_file.unlink()

            return {
                'video_id': video_id,
                'title': title,
                'channel': channel,
                'duration': duration,
                'transcript_path': str(cache_file),
                'transcript_length': len(text),
                'cached': False,
                'preview': text[:200] + '...' if len(text) > 200 else text
            }

    except subprocess.TimeoutExpired:
        print("Timeout extracting transcript", file=sys.stderr)
    except Exception as e:
        print(f"Error extracting transcript: {e}", file=sys.stderr)

    return None


def parse_vtt(vtt_path: Path) -> str:
    """Parse VTT subtitles into clean text."""
    lines = []
    prev_line = ""

    with open(vtt_path) as f:
        for line in f:
            line = line.strip()
            # Skip headers, timestamps, and empty lines
            if line.startswith("WEBVTT") or "-->" in line or not line:
                continue
            # Skip position/style tags
            if line.startswith('<') or line.startswith('align:'):
                continue
            # Clean inline tags
            import re
            line = re.sub(r'<[^>]+>', '', line)
            # Deduplicate
            if line and line != prev_line:
                lines.append(line)
                prev_line = line

    return " ".join(lines)


def search_videos(query: str, limit: int = 5) -> list[dict]:
    """Search YouTube for videos matching a query."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--no-download",
                f"ytsearch{limit}:{query}"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        videos = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video = json.loads(line)
                        videos.append({
                            'id': video.get('id'),
                            'title': video.get('title', ''),
                            'channel': video.get('channel', video.get('uploader', '')),
                            'duration': video.get('duration_string', ''),
                            'url': f"https://www.youtube.com/watch?v={video.get('id')}"
                        })
                    except json.JSONDecodeError:
                        continue
        return videos

    except Exception as e:
        print(f"Error searching: {e}", file=sys.stderr)
        return []


def crawl_channel(channel_url: str, limit: int = 10) -> dict:
    """Crawl a YouTube channel for recent videos."""
    # Normalize channel URL
    if not channel_url.startswith('http'):
        if channel_url.startswith('@'):
            channel_url = f"https://www.youtube.com/{channel_url}/videos"
        else:
            channel_url = f"https://www.youtube.com/@{channel_url}/videos"

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--no-download",
                "--playlist-end", str(limit),
                channel_url
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        videos = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video = json.loads(line)
                        videos.append({
                            'id': video.get('id'),
                            'title': video.get('title', ''),
                            'duration': video.get('duration_string', ''),
                            'url': f"https://www.youtube.com/watch?v={video.get('id')}"
                        })
                    except json.JSONDecodeError:
                        continue

        return {
            'channel_url': channel_url,
            'videos_found': len(videos),
            'videos': videos
        }

    except Exception as e:
        print(f"Error crawling channel: {e}", file=sys.stderr)
        return {'channel_url': channel_url, 'videos_found': 0, 'videos': [], 'error': str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: youtube_extractor.py <command> [args]")
        print("Commands:")
        print("  transcript <url>          - Extract transcript from video")
        print("  search <query> [--limit N] - Search for videos")
        print("  channel <url> [--limit N]  - Crawl channel for videos")
        print("  info <url>                - Get video info")
        sys.exit(1)

    command = sys.argv[1]

    # Determine output directory
    script_dir = Path(__file__).parent.parent
    output_dir = script_dir.parent.parent / 'data' / 'transcripts'

    if command == "transcript" and len(sys.argv) > 2:
        url = sys.argv[2]
        result = extract_transcript(url, output_dir)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({'error': 'Failed to extract transcript'}))
            sys.exit(1)

    elif command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        limit = 5
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])
        results = search_videos(query, limit)
        print(json.dumps({'query': query, 'results': len(results), 'videos': results}, indent=2))

    elif command == "channel" and len(sys.argv) > 2:
        channel = sys.argv[2]
        limit = 10
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])
        result = crawl_channel(channel, limit)
        print(json.dumps(result, indent=2))

    elif command == "info" and len(sys.argv) > 2:
        url = sys.argv[2]
        info = get_video_info(url)
        if info:
            print(json.dumps({
                'id': info.get('id'),
                'title': info.get('title'),
                'channel': info.get('channel', info.get('uploader')),
                'duration': info.get('duration_string'),
                'description': info.get('description', '')[:500]
            }, indent=2))
        else:
            print(json.dumps({'error': 'Failed to get video info'}))
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
