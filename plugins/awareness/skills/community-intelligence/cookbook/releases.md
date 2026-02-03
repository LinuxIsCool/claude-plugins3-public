# Purpose

Track Claude Code releases and version history.

## Instructions

- Check installed version via CLI.
- Query changelog for release notes.
- Compare with latest available version.

## Execution

```bash
# Check installed version
claude --version

# Using the community scanner tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/community-intelligence/tools/community_scanner.py releases

# Check changelog via web
curl -s "https://code.claude.com/docs/en/changelog.md" | head -200
```

## Version Format

Claude Code uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features
- **PATCH**: Bug fixes

## Release Cadence

Based on historical patterns:
- Major releases: ~quarterly
- Minor releases: ~monthly
- Patch releases: ~weekly

## Notable Recent Versions

| Version | Date | Highlights |
|---------|------|------------|
| 2.1.x | Jan 2026 | Hook improvements, MCP updates |
| 2.0.x | Dec 2025 | Plugin system overhaul |
| 1.x.x | 2025 | Initial public release |

## Checking for Updates

```bash
# Check if update available
claude --version

# Update Claude Code
npm update -g @anthropic/claude-code

# Or via Homebrew
brew upgrade claude-code
```

## Output Format

```yaml
current_version: "2.1.15"
latest_version: "2.1.20"
update_available: true
recent_releases:
  - version: "2.1.20"
    date: "2024-01-20"
    highlights:
      - "New PreCompact hook event"
      - "Fixed SessionStart timing"
  - version: "2.1.19"
    date: "2024-01-18"
    highlights:
      - "MCP server improvements"
      - "Bug fixes"
```
