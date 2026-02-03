---
name: introspection
description: Deep introspection into your Claude Code ecosystem. Use when users need detailed information about installed plugins, available skills, registered agents, active hooks, or configuration settings.
argument-hint: [component] (plugins|skills|agents|hooks|settings)
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
---

# Ecosystem Introspection

Provide detailed introspection into the Claude Code ecosystem.

## Usage

```
/introspection plugins    - List all installed plugins with details
/introspection skills     - Show available skills and their triggers
/introspection agents     - List registered agents and their configs
/introspection hooks      - Show active hooks by event type
/introspection settings   - Summarize configuration hierarchy
/introspection            - Full ecosystem overview
```

## Component: Plugins

When queried about plugins:

1. **Scan Plugin Locations**
   ```bash
   # User plugins
   ls ~/.claude/plugins/

   # Cached plugins
   ls ~/.claude/plugins/cache/

   # Project plugins (if exists)
   ls .claude/plugins/
   ```

2. **For Each Plugin, Extract:**
   - Name and version (from plugin.json)
   - Description
   - Components (skills, agents, hooks, commands)
   - MCP servers (if any)

3. **Format Response:**
   ```
   ## Installed Plugins ({count})

   ### {plugin_name} v{version}
   Source: {marketplace}
   Description: {description}

   Components:
   - Skills: {skill_list}
   - Agents: {agent_list}
   - Hooks: {event_list}

   ---
   ```

## Component: Skills

When queried about skills:

1. **Scan Skill Locations**
   ```bash
   # User skills
   ls ~/.claude/skills/

   # Project skills
   ls .claude/skills/

   # Plugin skills
   # (found during plugin scan)
   ```

2. **For Each Skill, Extract:**
   - Name (from frontmatter or directory)
   - Description
   - Invocation method (user/model/both)
   - Required arguments

3. **Format Response:**
   ```
   ## Available Skills ({count})

   | Skill | Description | Invocation |
   |-------|-------------|------------|
   | /{name} | {description} | {user/model/both} |
   ```

## Component: Agents

When queried about agents:

1. **Scan Agent Locations**
   ```bash
   # User agents
   ls ~/.claude/agents/

   # Project agents
   ls .claude/agents/

   # Plugin agents
   # (found during plugin scan)
   ```

2. **For Each Agent, Extract:**
   - Name
   - Description (triggering condition)
   - Model (if specified)
   - Tools (allowed/disallowed)

3. **Format Response:**
   ```
   ## Available Agents ({count})

   ### {agent_name}
   Trigger: {description}
   Model: {model or "inherit"}
   Tools: {tool_access}
   ```

## Component: Hooks

When queried about hooks:

1. **Read Hook Configuration**
   - From settings.json "hooks" section
   - From plugin.json for each plugin

2. **Group by Event Type:**
   - SessionStart
   - SessionEnd
   - PreToolUse
   - PostToolUse
   - PreCompact
   - Stop
   - etc.

3. **Format Response:**
   ```
   ## Active Hooks

   ### SessionStart ({count} handlers)
   - {plugin/source}: {action_description}

   ### PreToolUse ({count} handlers)
   Matchers:
   - Bash: {handler_description}
   - Edit|Write: {handler_description}
   ```

## Component: Settings

When queried about settings:

1. **Read Configuration Files**
   - `~/.claude/settings.json` (user)
   - `.claude/settings.json` (project)
   - `.claude/settings.local.json` (local overrides)
   - `CLAUDE.md` (instructions)

2. **Explain Hierarchy:**
   ```
   ## Configuration Hierarchy

   1. CLI flags (highest priority)
   2. Environment variables
   3. .claude/settings.local.json (git-ignored)
   4. .claude/settings.json (project, shared)
   5. ~/.claude/settings.json (user, global)

   ## Current Settings Summary

   Model: {model}
   Permissions: {permission_summary}
   Hooks: {hook_count} registered
   CLAUDE.md: {present/absent} ({word_count} words)
   ```

## Error Handling

If component not found:
```
[introspection] No {component} found.

To add {component}:
- {instructions}
```

If scan fails:
```
[introspection] Could not scan {location}: {error}

Try:
- Check directory permissions
- Verify Claude Code is properly installed
```
