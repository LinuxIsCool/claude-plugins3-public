# Purpose

Scan and inventory installed Claude Code plugins.

## Variables

PLUGIN_CACHE_PATH: ~/.claude/plugins/cache

## Instructions

- Scan the plugin cache directory for installed plugins.
- For each plugin, extract: name, version, components (skills, agents, hooks, commands).
- Return a structured inventory.

## Execution

```bash
# List all installed plugins
find ~/.claude/plugins/cache -mindepth 2 -maxdepth 2 -type d -exec basename {} \; 2>/dev/null | sort -u

# For detailed info, read each plugin's manifest
for plugin_dir in ~/.claude/plugins/cache/*/*; do
  if [ -f "$plugin_dir/.claude-plugin/plugin.json" ]; then
    echo "=== $(basename $plugin_dir) ==="
    cat "$plugin_dir/.claude-plugin/plugin.json" | jq -r '.name // "unknown"'
  fi
done
```

## Output Format

```yaml
plugins:
  - name: plugin-name
    version: 1.0.0
    path: /path/to/plugin
    components:
      skills: 3
      agents: 2
      hooks: 1
      commands: 4
```
