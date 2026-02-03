# Purpose

Query GitHub issues for Claude Code bugs, features, and discussions.

## Variables

GITHUB_REPO: anthropics/claude-code

## Instructions

- Use gh CLI for authenticated access.
- Filter by labels, state, and date.
- Extract patterns from issue titles and labels.

## Execution

```bash
# Using the community scanner tool
python3 ${CLAUDE_PLUGIN_ROOT}/skills/community-intelligence/tools/community_scanner.py github-issues --limit 20

# Direct gh CLI commands:

# Recent open issues
gh issue list -R anthropics/claude-code --limit 20 --json title,labels,createdAt,url

# Issues by label
gh issue list -R anthropics/claude-code --label bug --limit 10 --json title,body,url

# Search issues
gh issue list -R anthropics/claude-code --search "hooks" --json title,url

# Issue details
gh issue view 123 -R anthropics/claude-code --json title,body,comments
```

## Common Labels

| Label | Description |
|-------|-------------|
| bug | Something isn't working |
| enhancement | New feature request |
| has-repro | Has reproduction steps |
| platform:macos | macOS-specific |
| platform:linux | Linux-specific |
| platform:windows | Windows-specific |
| area:tools | Tool-related issues |
| area:permissions | Permission system |

## Pattern Analysis

When analyzing issues, look for:
1. **Frequency**: How often is this reported?
2. **Severity**: Does it block work?
3. **Workaround**: Is there a known fix?
4. **Status**: Is it being worked on?

## Output Format

```yaml
source: "GitHub Issues"
repo: "anthropics/claude-code"
query: "hooks"
total_found: 15
issues:
  - number: 123
    title: "SessionStart hook not firing"
    labels: ["bug", "has-repro"]
    state: "open"
    created: "2024-01-15"
    url: "https://github.com/..."
patterns:
  - "Hook timing issues (3 reports)"
  - "macOS-specific hook bugs (2 reports)"
```
