# Claude Code Plugin Marketplace

A collection of plugins for [Claude Code](https://claude.com/claude-code), Anthropic's official CLI tool.

## What is This?

This repository is a **plugin marketplace** — a curated collection of Claude Code plugins that extend Claude's capabilities with new skills, agents, commands, hooks, and output styles.

## Included Plugins

| Plugin | Description |
|--------|-------------|
| **hello** | Starter plugin with greeting skill, marketplace scaffolding tools, and templates |
| **logging** | Conversation logging with search, embeddings, web UI, and session management |
| **awareness** | Ecosystem intelligence — documentation search, community insights, YouTube analysis |
| **awareness-test** | Test agents for the awareness plugin's capabilities |
| **observatory** | Django-based observatory for tracking plugins, skills, agents, sessions, and knowledge |
| **writing** | Writing assistant with recursive "why" practice, research workflows, and essay tools |

## Installation

### Install the full marketplace

```bash
claude /plugins install https://github.com/LinuxIsCool/claude-plugins3-public
```

### Install individual plugins

```bash
# From the marketplace
claude /plugins install logging@linuxiscool-claude-plugins3-public
claude /plugins install awareness@linuxiscool-claude-plugins3-public
```

## Plugin Structure

Each plugin follows the standard Claude Code plugin layout:

```
plugins/
  plugin-name/
    .claude-plugin/
      plugin.json          # Plugin manifest (name, version, components)
    agents/                # Subagent definitions (.md files)
    commands/              # Slash commands (.md files)
    hooks/                 # Event hooks (PreToolUse, PostToolUse, Stop, etc.)
    output-styles/         # Output style definitions (.md files)
    skills/                # Skills with SKILL.md + cookbook/tools/prompts
      skill-name/
        SKILL.md           # Skill definition and instructions
        cookbook/           # Usage examples and recipes
        prompts/           # Prompt templates
        tools/             # Tool scripts
    .lsp.json              # Language server configurations
    .mcp.json              # MCP server configurations
```

## Creating Your Own Plugin

1. Use the **hello** plugin's `create-marketplace` skill to scaffold a new marketplace
2. Create a `plugins/your-plugin/` directory
3. Add a `.claude-plugin/plugin.json` manifest
4. Add components (skills, commands, agents, hooks, output-styles)
5. Register the plugin in `.claude-plugin/marketplace.json`

### Plugin Manifest Example

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What your plugin does",
  "skills": ["skills/my-skill"],
  "commands": ["commands/my-command.md"],
  "agents": ["agents/my-agent.md"]
}
```

## Development

### Plugin Caching

Claude Code caches plugins at install time. When developing locally, you need to update the cache after changes:

```bash
# Copy changes to cache
cp plugins/my-plugin/hooks/my_hook.py \
   ~/.claude/plugins/cache/marketplace-name/my-plugin/1.0.0/hooks/

# Or remove cache to force full reinstall
rm -rf ~/.claude/plugins/cache/marketplace-name/my-plugin/
```

### Running Plugin Services

Some plugins (like logging) include web UIs or API servers:

```bash
# Logging web UI
cd plugins/logging
python3 -m api.server &
cd web && npm run dev
```

## Contributing

1. Fork this repository
2. Create a feature branch
3. Add or modify plugins following the structure above
4. Ensure no personal data, databases, or session files are included
5. Submit a pull request

## Resources

- [Claude Code Documentation](https://claude.com/claude-code)
- [Plugin Development Guide](https://code.claude.com/docs/en/plugins)
- [Skills Documentation](https://code.claude.com/docs/en/skills)
- [Anthropic Official Skills](https://github.com/anthropics/skills)

## License

MIT
