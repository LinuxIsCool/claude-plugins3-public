# Purpose

Analyze a transcript for key insights, code examples, and actionable techniques.

## Instructions

- Parse the transcript for structure.
- Identify code examples and technical terms.
- Extract actionable insights.
- Summarize themes.

## Analysis Categories

### Code Examples
Look for:
- File paths mentioned (`~/.claude/`, `CLAUDE.md`, etc.)
- Command examples (`claude --help`, `cc`, etc.)
- Configuration snippets (JSON, YAML)
- Programming patterns discussed

### Technical Concepts
Identify mentions of:
- Hooks (PreToolUse, SessionStart, etc.)
- Skills and commands
- Agents and subagents
- MCP servers
- Model selection (opus, sonnet, haiku)

### Workflow Patterns
Extract:
- Step-by-step processes
- Best practices mentioned
- Common pitfalls discussed
- Tips and tricks

## Analysis Prompt

When analyzing a transcript, use this structure:

```markdown
## Video Analysis: [Title]

### Main Topic
[One sentence summary]

### Key Technical Points
1. [Point 1]
2. [Point 2]
3. [Point 3]

### Code/Config Examples Mentioned
- [Example 1]
- [Example 2]

### Workflow Recommendations
- [Recommendation 1]
- [Recommendation 2]

### Quotable Insights
> "[Direct quote from transcript]"

### Related Documentation
- [Link to relevant Claude Code doc]
```

## Output

```yaml
analysis:
  main_topic: "How to create custom Claude Code hooks"
  technical_points:
    - "PreToolUse hooks can validate file writes"
    - "SessionStart hooks inject context"
    - "Prompt-based hooks use LLM reasoning"
  code_examples:
    - type: "bash"
      description: "Hook script for file validation"
    - type: "json"
      description: "hooks.json configuration"
  workflows:
    - "Test hooks with --debug flag"
    - "Use ${CLAUDE_PLUGIN_ROOT} for portable paths"
  insights:
    - "Hooks run in parallel, design for independence"
  related_docs:
    - "hooks.md"
    - "plugins-reference.md"
```
