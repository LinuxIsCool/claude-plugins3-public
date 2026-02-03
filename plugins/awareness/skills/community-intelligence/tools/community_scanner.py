#!/usr/bin/env -S uv run
"""Community intelligence scanner for GitHub, RSS, and Hacker News."""

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from typing import Optional


def scan_github_issues(repo: str = "anthropics/claude-code", limit: int = 20, label: str = None) -> dict:
    """Scan GitHub issues using gh CLI."""
    cmd = ["gh", "issue", "list", "-R", repo, "--limit", str(limit),
           "--json", "number,title,labels,state,createdAt,url"]

    if label:
        cmd.extend(["--label", label])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            return {
                'source': 'GitHub Issues',
                'repo': repo,
                'total_found': len(issues),
                'issues': [{
                    'number': i['number'],
                    'title': i['title'],
                    'labels': [l['name'] for l in i.get('labels', [])],
                    'state': i['state'],
                    'created': i['createdAt'][:10],
                    'url': i['url']
                } for i in issues]
            }
    except Exception as e:
        return {'error': str(e)}

    return {'error': 'Failed to fetch issues'}


def scan_hacker_news(query: str, limit: int = 10) -> dict:
    """Search Hacker News via Algolia API."""
    url = f"https://hn.algolia.com/api/v1/search?query={query.replace(' ', '+')}&tags=story&hitsPerPage={limit}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            hits = data.get('hits', [])

            return {
                'source': 'Hacker News',
                'query': query,
                'stories_found': len(hits),
                'total_hits': data.get('nbHits', 0),
                'stories': [{
                    'title': h['title'],
                    'points': h.get('points', 0),
                    'comments': h.get('num_comments', 0),
                    'url': f"https://news.ycombinator.com/item?id={h['objectID']}",
                    'date': h.get('created_at', '')[:10]
                } for h in hits]
            }
    except Exception as e:
        return {'error': str(e)}


def scan_rss_feeds(days: int = 7) -> dict:
    """Check RSS feeds for recent updates."""
    feeds = [
        ('anthropic_news', 'https://www.anthropic.com/news/rss.xml'),
        ('claude_blog', 'https://www.anthropic.com/claude/rss.xml'),
    ]

    results = {
        'source': 'RSS Feeds',
        'feeds_checked': len(feeds),
        'items': []
    }

    cutoff = datetime.now() - timedelta(days=days)

    for feed_name, feed_url in feeds:
        try:
            with urllib.request.urlopen(feed_url, timeout=10) as response:
                content = response.read().decode()

                # Simple XML parsing for titles and dates
                import re
                items = re.findall(r'<item>.*?<title>([^<]+)</title>.*?</item>', content, re.DOTALL)

                for title in items[:5]:
                    # Check if Claude Code related
                    if 'claude' in title.lower():
                        results['items'].append({
                            'feed': feed_name,
                            'title': title.strip(),
                            'relevance': 0.8 if 'claude code' in title.lower() else 0.5
                        })
        except Exception as e:
            results[f'{feed_name}_error'] = str(e)

    return results


def get_releases() -> dict:
    """Get Claude Code release information."""
    result = {
        'source': 'Releases',
        'current_version': None,
        'releases': []
    }

    # Get current version
    try:
        version_result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if version_result.returncode == 0:
            result['current_version'] = version_result.stdout.strip()
    except:
        pass

    # Get recent releases from GitHub
    try:
        gh_result = subprocess.run(
            ["gh", "release", "list", "-R", "anthropics/claude-code", "--limit", "5",
             "--json", "tagName,publishedAt,name"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if gh_result.returncode == 0:
            releases = json.loads(gh_result.stdout)
            result['releases'] = [{
                'version': r['tagName'],
                'name': r['name'],
                'date': r['publishedAt'][:10]
            } for r in releases]
    except Exception as e:
        result['releases_error'] = str(e)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: community_scanner.py <command> [args]")
        print("Commands:")
        print("  github-issues [--limit N] [--label L]  - Scan GitHub issues")
        print("  hacker-news <query> [--limit N]        - Search Hacker News")
        print("  rss [--days N]                         - Check RSS feeds")
        print("  releases                               - Get release info")
        print("  all                                    - Run all scans")
        sys.exit(1)

    command = sys.argv[1]

    if command == "github-issues":
        limit = 20
        label = None
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        if "--label" in sys.argv:
            idx = sys.argv.index("--label")
            label = sys.argv[idx + 1]
        result = scan_github_issues(limit=limit, label=label)
        print(json.dumps(result, indent=2))

    elif command == "hacker-news" and len(sys.argv) > 2:
        query = sys.argv[2]
        limit = 10
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        result = scan_hacker_news(query, limit)
        print(json.dumps(result, indent=2))

    elif command == "rss":
        days = 7
        if "--days" in sys.argv:
            idx = sys.argv.index("--days")
            days = int(sys.argv[idx + 1])
        result = scan_rss_feeds(days)
        print(json.dumps(result, indent=2))

    elif command == "releases":
        result = get_releases()
        print(json.dumps(result, indent=2))

    elif command == "all":
        results = {
            'github': scan_github_issues(limit=10),
            'hacker_news': scan_hacker_news("claude code", 5),
            'rss': scan_rss_feeds(7),
            'releases': get_releases()
        }
        print(json.dumps(results, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
