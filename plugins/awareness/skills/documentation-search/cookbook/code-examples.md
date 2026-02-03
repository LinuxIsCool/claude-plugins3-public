# Purpose

Find and retrieve code examples from documentation.

## Variables

DATABASE_PATH: ${CLAUDE_PLUGIN_ROOT}/data/awareness.db

## Instructions

- Extract fenced code blocks from documentation.
- Identify language/type of each example.
- Filter by relevance to user query.

## Execution

```bash
# Using the search tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/documentation-search/tools/search_docs.py examples "hooks"

# Direct query for code examples
sqlite3 ${DATABASE_PATH} "
  SELECT
    r.url,
    json_extract(c.code_examples, '$[0].code') as example
  FROM content c
  JOIN resources r ON c.resource_id = r.id
  WHERE c.code_examples IS NOT NULL
  AND r.url LIKE '%hooks%'
  LIMIT 5;
"
```

## Example Categories

### Configuration Examples
- `plugin.json` manifest
- `hooks.json` configuration
- `settings.json` options

### Script Examples
- Hook scripts (bash, python)
- Tool implementations
- Integration scripts

### Command Examples
- CLI usage patterns
- Installation commands
- Debug commands

## Output Format

```yaml
query: "hooks"
examples_found: 40
examples:
  - source: "hooks.md"
    language: "json"
    description: "Hook configuration format"
    code: |
      {
        "PreToolUse": [{
          "matcher": "Write",
          "hooks": [{
            "type": "command",
            "command": "bash script.sh"
          }]
        }]
      }
  - source: "hooks-guide.md"
    language: "bash"
    description: "Hook validation script"
    code: |
      #!/bin/bash
      input=$(cat)
      # validation logic
```
