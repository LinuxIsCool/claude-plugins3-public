# Purpose

Discover and catalog all available skills from plugins and user directories.

## Variables

USER_SKILLS_PATH: ~/.claude/skills
PLUGIN_CACHE_PATH: ~/.claude/plugins/cache

## Instructions

- Scan user skills directory for SKILL.md files.
- Scan plugin cache for skills in each plugin.
- Extract name and description from YAML frontmatter.
- Return a structured catalog.

## Execution

```bash
# Find all SKILL.md files
echo "=== User Skills ==="
find ~/.claude/skills -name "SKILL.md" 2>/dev/null | while read skill; do
  dir=$(dirname "$skill")
  name=$(basename "$dir")
  desc=$(grep -A1 "^description:" "$skill" | tail -1 | sed 's/^description: //')
  echo "- $name: $desc"
done

echo -e "\n=== Plugin Skills ==="
find ~/.claude/plugins/cache -name "SKILL.md" 2>/dev/null | while read skill; do
  # Extract plugin name from path
  plugin=$(echo "$skill" | sed 's|.*/cache/[^/]*/\([^/]*\)/.*|\1|')
  dir=$(dirname "$skill")
  name=$(basename "$dir")
  echo "- [$plugin] $name"
done
```

## Output Format

```yaml
skills:
  user_skills:
    - name: skill-name
      description: What the skill does
      path: /path/to/skill
  plugin_skills:
    - plugin: plugin-name
      name: skill-name
      description: What the skill does
```
