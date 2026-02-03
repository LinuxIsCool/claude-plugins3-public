# Purpose

Navigate the documentation knowledge graph to find related topics.

## Variables

DATABASE_PATH: ${CLAUDE_PLUGIN_ROOT}/data/awareness.db

## Instructions

- Use edge relationships to find connected topics.
- Identify incoming links (what points here).
- Identify outgoing links (what this points to).

## Execution

```bash
# Using the search tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/documentation-search/tools/search_docs.py related "hooks.md"

# Direct SQLite query
sqlite3 ${DATABASE_PATH} "
  SELECT
    'outgoing' as direction,
    t.url as target
  FROM edges e
  JOIN resources s ON e.source_id = s.id
  JOIN resources t ON e.target_id = t.id
  WHERE s.url LIKE '%hooks.md'
  UNION ALL
  SELECT
    'incoming' as direction,
    s.url as source
  FROM edges e
  JOIN resources s ON e.source_id = s.id
  JOIN resources t ON e.target_id = t.id
  WHERE t.url LIKE '%hooks.md';
"
```

## Navigation Patterns

### From General to Specific
```
overview.md → plugins.md → hooks.md → hooks-guide.md
```

### From Feature to Implementation
```
features-overview.md → skills.md → SKILL.md format
```

### From Problem to Solution
```
troubleshooting.md → specific issue → solution doc
```

## Output Format

```yaml
page: "hooks.md"
incoming_links:  # Pages that link TO this page
  - plugins.md
  - settings.md
  - best-practices.md
outgoing_links:  # Pages this page links TO
  - hooks-guide.md
  - plugins-reference.md
  - cli-reference.md
suggested_path:
  - "Start: overview.md"
  - "Then: plugins.md"
  - "Current: hooks.md"
  - "Next: hooks-guide.md"
```
