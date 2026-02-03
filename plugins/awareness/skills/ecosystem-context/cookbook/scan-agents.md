# Purpose

Enumerate all configured agents from plugins.

## Variables

PLUGIN_CACHE_PATH: ~/.claude/plugins/cache

## Instructions

- Scan plugin cache for agent markdown files.
- Extract name, description, model, and color from frontmatter.
- Return a structured enumeration.

## Execution

```bash
# Find all agent definitions
find ~/.claude/plugins/cache -path "*/agents/*.md" 2>/dev/null | while read agent; do
  plugin=$(echo "$agent" | sed 's|.*/cache/[^/]*/\([^/]*\)/.*|\1|')
  name=$(basename "$agent" .md)

  # Extract frontmatter fields
  model=$(grep "^model:" "$agent" 2>/dev/null | head -1 | sed 's/model: //')
  color=$(grep "^color:" "$agent" 2>/dev/null | head -1 | sed 's/color: //')

  echo "- [$plugin] $name (model: ${model:-inherit}, color: ${color:-blue})"
done
```

## Output Format

```yaml
agents:
  - plugin: plugin-name
    name: agent-name
    model: haiku
    color: cyan
    description: What the agent does
```
