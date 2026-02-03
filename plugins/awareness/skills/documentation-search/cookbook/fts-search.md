# Purpose

Perform full-text search across Claude Code documentation.

## Variables

DATABASE_PATH: ${CLAUDE_PLUGIN_ROOT}/data/awareness.db

## Instructions

- Use FTS5 MATCH queries for keyword search.
- Support BM25 ranking for relevance.
- Extract snippets with context.

## Execution

```bash
# Using the search tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/documentation-search/tools/search_docs.py search "hooks"

# Direct SQLite query (if tool not available)
sqlite3 ~/.claude/plugins/cache/*/awareness/*/data/awareness.db "
  SELECT url, snippet(content_fts, 1, '>>>', '<<<', '...', 32) as snippet
  FROM content_fts
  WHERE content_fts MATCH 'hooks'
  ORDER BY rank
  LIMIT 10;
"
```

## Query Syntax

### Simple Terms
```sql
MATCH 'hook'           -- Single word
MATCH 'session start'  -- Multiple words (OR)
```

### Phrase Search
```sql
MATCH '"session start"'  -- Exact phrase
```

### Boolean Operators
```sql
MATCH 'hook AND session'  -- Both terms
MATCH 'hook OR trigger'   -- Either term
MATCH 'hook NOT test'     -- Exclude term
```

### Prefix Matching
```sql
MATCH 'config*'  -- Matches configure, configuration, etc.
```

## Output Format

```yaml
query: "hooks"
results: 24
matches:
  - url: "https://code.claude.com/docs/en/hooks.md"
    title: "Hooks"
    snippet: ">>>Hooks<<< are event-driven automation scripts..."
    relevance: 0.95
  - url: "https://code.claude.com/docs/en/plugins-reference.md"
    title: "Plugins Reference"
    snippet: "Plugin >>>hooks<<< configuration in hooks.json..."
    relevance: 0.82
```
