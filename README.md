# Claude Code Plugin Marketplace

A curated collection of plugins for [Claude Code](https://claude.com/claude-code) — Anthropic's official CLI tool for AI-assisted development.

## Plugins

### hello
Starter plugin and marketplace scaffolding toolkit. Includes greeting skills, templates for creating new marketplaces, and examples of every plugin component type.

### logging
Full-featured conversation logging system with:
- Automatic session capture via hooks
- Semantic search with embeddings (cosine similarity)
- Web UI for browsing and searching sessions
- REST API for programmatic access
- Obsidian vault integration

### awareness
Contextual intelligence about the Claude Code ecosystem:
- Documentation search across official and community sources
- Community intelligence (GitHub issues, releases, discussions)
- YouTube transcript extraction and analysis
- Ecosystem scanning (discover installed plugins, skills, agents)

### observatory
Django-based metadata observatory for tracking:
- Plugins, skills, agents, commands, hooks, MCP servers
- Sessions and conversation history
- Knowledge graph entries
- Billing and usage tracking
- Full REST API with Django admin interface

### writing
Writing assistant with structured workflows:
- Recursive "why" practice for deepening understanding
- Research and resource gathering skills
- Essay writing with customizable output styles
- Task network methodology for organizing complex writing projects

## Quick Start

### 1. Add the marketplace

```bash
/plugin marketplace add LinuxIsCool/claude-plugins3-public
```

### 2. Install plugins

```bash
# Install individual plugins
/plugin install logging@linuxiscool-claude-plugins3-public
/plugin install awareness@linuxiscool-claude-plugins3-public
/plugin install observatory@linuxiscool-claude-plugins3-public
/plugin install writing@linuxiscool-claude-plugins3-public
```

### 3. Manage

```bash
# List installed marketplaces
/plugin marketplace list

# Update marketplace to latest
/plugin marketplace update linuxiscool-claude-plugins3-public

# Disable/enable a plugin
/plugin disable logging@linuxiscool-claude-plugins3-public
/plugin enable logging@linuxiscool-claude-plugins3-public
```

## Plugin Development

See [CLAUDE.md](./CLAUDE.md) for development guidelines, plugin structure conventions, and contribution instructions.

### Creating a New Plugin

```bash
# Use the built-in scaffolding skill
claude> /hello create-marketplace
```

This generates a complete marketplace structure with all necessary manifests and templates.

## Architecture

```
.claude-plugin/
  marketplace.json         # Registry of all plugins in this marketplace

plugins/
  hello/                   # Starter plugin + scaffolding tools
  logging/                 # Conversation logging + search + web UI
  awareness/               # Ecosystem intelligence + documentation
  awareness-test/          # Test agents for awareness capabilities
  observatory/             # Django metadata observatory
  writing/                 # Writing assistant + research workflows
```

## License

MIT
