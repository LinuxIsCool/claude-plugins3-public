#!/usr/bin/env -S uv run
"""Documentation search tool using FTS5 and knowledge graph."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional


def find_database() -> Path | None:
    """Find the awareness database."""
    # Check plugin data directory first
    script_dir = Path(__file__).parent.parent
    plugin_data = script_dir.parent.parent / 'data' / 'awareness.db'
    if plugin_data.exists():
        return plugin_data

    # Check research directory
    research_db = Path.home() / 'Workspace/sandbox/marketplaces/claude-plugins3/.claude/local/awareness/research/storage/experiments/awareness_prototype.db'
    if research_db.exists():
        return research_db

    return None


def search_fts(db_path: Path, query: str, limit: int = 10) -> list[dict]:
    """Full-text search using FTS5."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    results = []
    try:
        cursor = conn.execute("""
            SELECT
                r.url,
                snippet(content_fts, 1, '>>>', '<<<', '...', 32) as snippet,
                rank
            FROM content_fts
            JOIN content c ON content_fts.resource_id = c.resource_id
            JOIN resources r ON c.resource_id = r.id
            WHERE content_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        for row in cursor:
            url = row['url']
            # Extract page name from URL
            page_name = url.split('/')[-1].replace('.md', '')
            results.append({
                'url': url,
                'page': page_name,
                'snippet': row['snippet'],
                'relevance': round(1 / (1 - row['rank']), 2) if row['rank'] else 0
            })
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)

    conn.close()
    return results


def get_related(db_path: Path, page: str) -> dict:
    """Get pages related to a given page via edges."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    result = {'page': page, 'incoming': [], 'outgoing': []}

    try:
        # Outgoing links
        cursor = conn.execute("""
            SELECT DISTINCT t.url
            FROM edges e
            JOIN resources s ON e.source_id = s.id
            JOIN resources t ON e.target_id = t.id
            WHERE s.url LIKE ?
            LIMIT 20
        """, (f'%{page}%',))
        result['outgoing'] = [row['url'].split('/')[-1] for row in cursor]

        # Incoming links
        cursor = conn.execute("""
            SELECT DISTINCT s.url
            FROM edges e
            JOIN resources s ON e.source_id = s.id
            JOIN resources t ON e.target_id = t.id
            WHERE t.url LIKE ?
            LIMIT 20
        """, (f'%{page}%',))
        result['incoming'] = [row['url'].split('/')[-1] for row in cursor]

    except Exception as e:
        print(f"Related error: {e}", file=sys.stderr)

    conn.close()
    return result


def get_examples(db_path: Path, topic: str, limit: int = 5) -> list[dict]:
    """Get code examples related to a topic."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    examples = []
    try:
        cursor = conn.execute("""
            SELECT r.url, c.code_examples
            FROM content c
            JOIN resources r ON c.resource_id = r.id
            WHERE c.code_examples IS NOT NULL
            AND (r.url LIKE ? OR c.extracted_text LIKE ?)
            LIMIT ?
        """, (f'%{topic}%', f'%{topic}%', limit * 2))

        for row in cursor:
            if row['code_examples']:
                try:
                    code_list = json.loads(row['code_examples'])
                    for code in code_list[:2]:  # Max 2 per page
                        examples.append({
                            'source': row['url'].split('/')[-1],
                            'language': code.get('language', 'unknown'),
                            'code': code.get('code', '')[:500]
                        })
                        if len(examples) >= limit:
                            break
                except:
                    pass
            if len(examples) >= limit:
                break

    except Exception as e:
        print(f"Examples error: {e}", file=sys.stderr)

    conn.close()
    return examples


def get_stats(db_path: Path) -> dict:
    """Get database statistics."""
    conn = sqlite3.connect(str(db_path))

    stats = {}
    try:
        stats['total_resources'] = conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0]
        stats['total_edges'] = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        stats['with_content'] = conn.execute("SELECT COUNT(*) FROM content").fetchone()[0]

        # Count by status
        cursor = conn.execute("SELECT status, COUNT(*) FROM resources GROUP BY status")
        stats['by_status'] = dict(cursor.fetchall())

    except Exception as e:
        print(f"Stats error: {e}", file=sys.stderr)

    conn.close()
    return stats


def main():
    if len(sys.argv) < 2:
        print("Usage: search_docs.py <command> [args]")
        print("Commands:")
        print("  search <query>    - Full-text search")
        print("  related <page>    - Find related pages")
        print("  examples <topic>  - Find code examples")
        print("  stats             - Database statistics")
        sys.exit(1)

    command = sys.argv[1]
    db_path = find_database()

    if not db_path:
        print(json.dumps({'error': 'Database not found'}))
        sys.exit(1)

    if command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        results = search_fts(db_path, query, limit)
        print(json.dumps({
            'query': query,
            'results': len(results),
            'matches': results
        }, indent=2))

    elif command == "related" and len(sys.argv) > 2:
        page = sys.argv[2]
        result = get_related(db_path, page)
        print(json.dumps(result, indent=2))

    elif command == "examples" and len(sys.argv) > 2:
        topic = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        examples = get_examples(db_path, topic, limit)
        print(json.dumps({
            'topic': topic,
            'examples_found': len(examples),
            'examples': examples
        }, indent=2))

    elif command == "stats":
        stats = get_stats(db_path)
        print(json.dumps(stats, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
