# Purpose

Identify active hook configurations from plugins.

## Variables

PLUGIN_CACHE_PATH: ~/.claude/plugins/cache

## Instructions

- Scan plugin cache for hooks.json files.
- Extract event types and matchers.
- Return a structured configuration report.

## Execution

```bash
# Find all hooks.json files
find ~/.claude/plugins/cache -name "hooks.json" 2>/dev/null | while read hooks; do
  plugin=$(echo "$hooks" | sed 's|.*/cache/[^/]*/\([^/]*\)/.*|\1|')

  echo "=== $plugin ==="
  # Extract event types
  jq -r '.hooks // . | keys[]' "$hooks" 2>/dev/null | while read event; do
    count=$(jq -r "(.hooks // .).$event | length" "$hooks" 2>/dev/null)
    echo "  $event: $count handler(s)"
  done
done
```

## Output Format

```yaml
hooks:
  - plugin: plugin-name
    events:
      PreToolUse: 2
      SessionStart: 1
      Stop: 1
```

## Event Reference

| Event | When | Common Use |
|-------|------|------------|
| PreToolUse | Before tool runs | Validation |
| PostToolUse | After tool runs | Logging |
| SessionStart | Session begins | Context injection |
| SessionEnd | Session ends | Cleanup |
| Stop | Agent stopping | Completion check |
| UserPromptSubmit | User input | Query enrichment |
| PreCompact | Before compaction | State preservation |
