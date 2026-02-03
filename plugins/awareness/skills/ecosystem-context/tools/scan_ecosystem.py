#!/usr/bin/env -S uv run
"""Scan Claude Code ecosystem for plugins, skills, agents, and hooks."""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


def extract_yaml_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}

    end = content.find('---', 3)
    if end == -1:
        return {}

    frontmatter = content[3:end].strip()
    result = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result


def scan_plugins(cache_path: Path) -> list[dict]:
    """Scan plugin cache for installed plugins."""
    plugins = []

    if not cache_path.exists():
        return plugins

    # Structure: cache/marketplace/plugin/version/
    for marketplace in cache_path.iterdir():
        if not marketplace.is_dir():
            continue
        for plugin_dir in marketplace.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Find version directory (usually just one)
            for version_dir in plugin_dir.iterdir():
                if not version_dir.is_dir():
                    continue

                manifest_path = version_dir / '.claude-plugin' / 'plugin.json'
                plugin_info = {
                    'name': plugin_dir.name,
                    'marketplace': marketplace.name,
                    'path': str(version_dir),
                    'version': version_dir.name,
                    'skills': 0,
                    'agents': 0,
                    'hooks': 0,
                    'commands': 0
                }

                if manifest_path.exists():
                    try:
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                            plugin_info['name'] = manifest.get('name', plugin_dir.name)
                    except:
                        pass

                # Count components
                skills_dir = version_dir / 'skills'
                if skills_dir.exists():
                    plugin_info['skills'] = len(list(skills_dir.glob('*/SKILL.md')))

                agents_dir = version_dir / 'agents'
                if agents_dir.exists():
                    plugin_info['agents'] = len(list(agents_dir.glob('*.md')))

                hooks_file = version_dir / 'hooks' / 'hooks.json'
                if hooks_file.exists():
                    plugin_info['hooks'] = 1

                commands_dir = version_dir / 'commands'
                if commands_dir.exists():
                    plugin_info['commands'] = len(list(commands_dir.glob('*.md')))

                plugins.append(plugin_info)
                break  # Only take first version

    return plugins


def scan_skills(cache_path: Path, user_skills_path: Path) -> dict:
    """Scan for all available skills."""
    result = {'user_skills': [], 'plugin_skills': []}

    # User skills
    if user_skills_path.exists():
        for skill_md in user_skills_path.glob('*/SKILL.md'):
            skill_dir = skill_md.parent
            try:
                content = skill_md.read_text()
                fm = extract_yaml_frontmatter(content)
                result['user_skills'].append({
                    'name': fm.get('name', skill_dir.name),
                    'description': fm.get('description', ''),
                    'path': str(skill_dir)
                })
            except:
                result['user_skills'].append({
                    'name': skill_dir.name,
                    'path': str(skill_dir)
                })

    # Plugin skills
    if cache_path.exists():
        for skill_md in cache_path.glob('*/*/*/skills/*/SKILL.md'):
            skill_dir = skill_md.parent
            parts = str(skill_md).split('/')
            # Find plugin name from path
            try:
                cache_idx = parts.index('cache')
                plugin_name = parts[cache_idx + 2]  # marketplace/plugin/version
            except:
                plugin_name = 'unknown'

            try:
                content = skill_md.read_text()
                fm = extract_yaml_frontmatter(content)
                result['plugin_skills'].append({
                    'plugin': plugin_name,
                    'name': fm.get('name', skill_dir.name),
                    'description': fm.get('description', '')[:100]
                })
            except:
                result['plugin_skills'].append({
                    'plugin': plugin_name,
                    'name': skill_dir.name
                })

    return result


def scan_agents(cache_path: Path) -> list[dict]:
    """Scan for all configured agents."""
    agents = []

    if not cache_path.exists():
        return agents

    for agent_md in cache_path.glob('*/*/*/agents/*.md'):
        parts = str(agent_md).split('/')
        try:
            cache_idx = parts.index('cache')
            plugin_name = parts[cache_idx + 2]
        except:
            plugin_name = 'unknown'

        try:
            content = agent_md.read_text()
            fm = extract_yaml_frontmatter(content)
            agents.append({
                'plugin': plugin_name,
                'name': fm.get('name', agent_md.stem),
                'model': fm.get('model', 'inherit'),
                'color': fm.get('color', 'blue')
            })
        except:
            agents.append({
                'plugin': plugin_name,
                'name': agent_md.stem
            })

    return agents


def scan_hooks(cache_path: Path) -> list[dict]:
    """Scan for all hook configurations."""
    hooks = []

    if not cache_path.exists():
        return hooks

    for hooks_json in cache_path.glob('*/*/*/hooks/hooks.json'):
        parts = str(hooks_json).split('/')
        try:
            cache_idx = parts.index('cache')
            plugin_name = parts[cache_idx + 2]
        except:
            plugin_name = 'unknown'

        try:
            with open(hooks_json) as f:
                config = json.load(f)

            # Handle both formats: {hooks: {...}} and direct {...}
            hook_events = config.get('hooks', config)

            events = {}
            for event, handlers in hook_events.items():
                if isinstance(handlers, list):
                    events[event] = len(handlers)

            if events:
                hooks.append({
                    'plugin': plugin_name,
                    'events': events
                })
        except:
            pass

    return hooks


def main():
    cache_path = Path.home() / '.claude' / 'plugins' / 'cache'
    user_skills_path = Path.home() / '.claude' / 'skills'

    # Determine what to scan
    scan_type = sys.argv[1] if len(sys.argv) > 1 else 'all'

    result = {}

    if scan_type in ['all', 'plugins']:
        result['plugins'] = scan_plugins(cache_path)

    if scan_type in ['all', 'skills']:
        result['skills'] = scan_skills(cache_path, user_skills_path)

    if scan_type in ['all', 'agents']:
        result['agents'] = scan_agents(cache_path)

    if scan_type in ['all', 'hooks']:
        result['hooks'] = scan_hooks(cache_path)

    # Summary
    if scan_type == 'all':
        result['summary'] = {
            'total_plugins': len(result.get('plugins', [])),
            'total_skills': len(result.get('skills', {}).get('user_skills', [])) +
                           len(result.get('skills', {}).get('plugin_skills', [])),
            'total_agents': len(result.get('agents', [])),
            'total_hooks': sum(len(h.get('events', {})) for h in result.get('hooks', []))
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
