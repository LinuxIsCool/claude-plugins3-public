# Purpose

Identify and navigate to hub pages (most connected documentation).

## Hub Pages by Category

### Getting Started
| Page | Links | Best For |
|------|-------|----------|
| overview.md | 18 | First introduction |
| quickstart.md | 16 | Fast setup |
| setup.md | 18 | Detailed installation |

### Configuration
| Page | Links | Best For |
|------|-------|----------|
| settings.md | 69 | All configuration options |
| model-config.md | 7 | Model selection |

### Extension
| Page | Links | Best For |
|------|-------|----------|
| hooks.md | 40 | Event automation |
| skills.md | 20 | Custom skills |
| plugins.md | 30 | Plugin development |
| mcp.md | 21 | External integrations |
| sub-agents.md | 43 | Agent creation |

### Integration
| Page | Links | Best For |
|------|-------|----------|
| vs-code.md | 26 | VS Code setup |
| github-actions.md | 18 | CI/CD automation |

## Navigation Recommendations

### "I'm new to Claude Code"
1. Start: overview.md
2. Then: quickstart.md
3. Explore: features-overview.md

### "I want to extend Claude Code"
1. Start: plugins.md
2. Then: skills.md or hooks.md
3. Reference: plugins-reference.md

### "I want to automate workflows"
1. Start: hooks.md
2. Then: hooks-guide.md
3. Examples: github-actions.md

### "I want to integrate with tools"
1. Start: mcp.md
2. Then: third-party-integrations.md
3. Specific: vs-code.md or jetbrains.md

## Output Format

```yaml
user_goal: "extend Claude Code"
recommended_path:
  - page: "plugins.md"
    why: "Overview of plugin system"
  - page: "skills.md"
    why: "Creating custom skills"
  - page: "plugins-reference.md"
    why: "Detailed reference"
hub_pages:
  most_linked:
    - settings.md (15 incoming)
    - mcp.md (9 incoming)
  most_comprehensive:
    - settings.md (69 outgoing)
    - sub-agents.md (43 outgoing)
```
