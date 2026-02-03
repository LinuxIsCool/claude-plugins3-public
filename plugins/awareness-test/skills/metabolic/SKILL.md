---
name: metabolic
description: Workflow optimization and session context for Claude Code. Use when users need project catch-up, workflow recommendations, session history, or proactive suggestions based on work patterns.
argument-hint: [action] (catch-up|workflow|suggest|history)
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
---

# Metabolic Awareness

Provide workflow optimization and session context intelligence.

## Usage

```
/metabolic catch-up     - Summary of recent session activity
/metabolic workflow     - Recommended workflow for current task
/metabolic suggest      - Proactive suggestions based on context
/metabolic history      - Session history and patterns
/metabolic              - Quick status with top recommendations
```

## Action: Catch-up

When user asks for catch-up or "where was I":

1. **Scan Recent Activity**
   - Check git log for recent commits
   - Check session logs if available
   - Look at recently modified files

2. **Summarize Context**
   ```
   ## Session Catch-Up

   ### Recent Work
   - Last session: {timestamp}
   - Modified: {file_list}
   - Commits: {recent_commit_summary}

   ### Current State
   - Branch: {branch_name}
   - Uncommitted changes: {change_count}
   - Untracked files: {untracked_count}

   ### Continuation Points
   {What was in progress, next logical steps}
   ```

3. **Identify Open Loops**
   - TODO comments added recently
   - Incomplete implementations
   - Failing tests
   - Uncommitted work

## Action: Workflow

When user asks for workflow recommendations:

1. **Analyze Current Task**
   - What files are being worked on
   - What kind of task (bug fix, feature, refactor, etc.)

2. **Recommend Workflow**
   ```
   ## Recommended Workflow for {task_type}

   ### Phase 1: {phase_name}
   - {step1}
   - {step2}

   ### Relevant Tools
   - {tool}: {why_useful}

   ### Relevant Skills
   - /{skill}: {when_to_use}

   ### Best Practices
   - {practice1}
   - {practice2}
   ```

3. **Task Type Detection**

   | Pattern | Task Type | Workflow |
   |---------|-----------|----------|
   | "fix", "bug", "error" | Bug Fix | Reproduce → Debug → Fix → Test → Commit |
   | "add", "new", "feature" | Feature | Plan → Implement → Test → Document → Commit |
   | "refactor", "clean" | Refactor | Identify → Extract → Validate → Commit |
   | "test", "coverage" | Testing | Identify gaps → Write tests → Verify |
   | "docs", "readme" | Documentation | Review → Write → Validate → Commit |

## Action: Suggest

When user wants proactive suggestions:

1. **Analyze Context**
   - Project structure
   - Recent activity
   - Current session
   - Common patterns

2. **Generate Suggestions**
   ```
   ## Suggestions

   ### High Priority
   - {suggestion with rationale}

   ### Could Improve
   - {improvement opportunity}

   ### Consider
   - {optional enhancement}
   ```

3. **Suggestion Types**
   - Uncommitted work reminders
   - Test coverage opportunities
   - Documentation gaps
   - Performance concerns
   - Security considerations
   - Refactoring opportunities

## Action: History

When user asks about session history or patterns:

1. **Gather Historical Data**
   - Session log files
   - Git history
   - Tool usage patterns

2. **Present History**
   ```
   ## Session History

   ### Recent Sessions
   | Date | Duration | Focus | Key Actions |
   |------|----------|-------|-------------|
   | {date} | {time} | {area} | {summary} |

   ### Work Patterns
   - Most active: {time_of_day}
   - Focus areas: {common_directories}
   - Common workflows: {patterns}

   ### Productivity Insights
   - {insight1}
   - {insight2}
   ```

## Quick Status (Default)

If no action specified, provide quick overview:

```
[Metabolic Status]
Last session: {when}
Current task: {detected_or_unknown}
Git status: {clean/dirty with summary}

Top Recommendations:
1. {most_relevant_suggestion}
2. {second_suggestion}
```

## Integration with Other Domains

**From Introspection:**
- Current plugin/skill capabilities inform workflow recommendations
- Hook status affects available automation

**From External:**
- Community best practices inform suggestions
- Documentation patterns guide workflows

## Data Sources

### Primary Sources
- `.git/` - Commit history, branch info
- Session transcripts (if available)
- Recently modified files
- CLAUDE.md context

### Secondary Sources
- Test results
- Build outputs
- Error logs
- Configuration files

## Error Handling

If data sources unavailable:
```
[metabolic] Limited data available.

Available: {what_we_can_access}
Unavailable: {what_we_can't}

Suggestions based on available context:
- {limited_suggestion}
```

## Response Guidelines

- Be actionable, not theoretical
- Prioritize by relevance to current session
- Include specific file paths and commands
- Suggest follow-up actions
- Note confidence level when inferring

## Workflow Templates

### Bug Fix Workflow
1. Reproduce the issue
2. Locate the bug (use Grep, Read)
3. Understand the context
4. Implement fix
5. Write/update tests
6. Verify fix
7. Commit with clear message

### Feature Development Workflow
1. Understand requirements
2. Design approach (EnterPlanMode for complex)
3. Implement incrementally
4. Test as you go
5. Document changes
6. Review and refine
7. Commit with context

### Refactoring Workflow
1. Ensure test coverage exists
2. Make small, focused changes
3. Verify tests pass after each change
4. Commit frequently
5. Document intent in commits
