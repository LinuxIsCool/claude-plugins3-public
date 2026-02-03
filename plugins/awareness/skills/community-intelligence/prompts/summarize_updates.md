# Community Updates Summary Prompt

## Context

You are synthesizing recent community intelligence about Claude Code from multiple sources.

## Data Sources

<fill_in_sources_here>
```yaml
github_issues:
  - title: <issue title>
    labels: [<labels>]
    state: <open/closed>

rss_items:
  - title: <item title>
    feed: <feed name>
    date: <date>

hacker_news:
  - title: <story title>
    points: <points>
    comments: <comment count>

releases:
  - version: <version>
    date: <date>
```
</fill_in_sources_here>

## Analysis Task

Synthesize this community data into actionable insights:

### 1. What's New (Last 7 Days)
- Recent releases and their highlights
- New features or changes
- Important announcements

### 2. Community Pulse
- What topics are people discussing?
- Common questions or confusions
- Feature requests gaining traction

### 3. Known Issues
- Bugs affecting users
- Workarounds available
- Expected fixes

### 4. Actionable Recommendations
- Should the user update their Claude Code?
- Any settings to check?
- Features to try?

## Output Format

```yaml
summary:
  period: "Last 7 days"
  sources_analyzed: 4

whats_new:
  releases:
    - "v2.1.20: New hook events, bug fixes"
  announcements:
    - "MCP server improvements"

community_pulse:
  hot_topics:
    - "Hook development patterns"
    - "Plugin marketplace growth"
  common_questions:
    - "How to debug hooks?"
  trending_requests:
    - "More model options"

known_issues:
  critical: []
  moderate:
    - issue: "SessionStart timing inconsistent"
      workaround: "Add delay in hook script"
  minor:
    - "UI glitch in dark mode"

recommendations:
  should_update: true
  reason: "Bug fixes for hook timing"
  features_to_try:
    - "New PreCompact hook event"
  settings_to_check:
    - "Hook timeout values"
```
